# PS-041E2-A backend readiness proof

PS-041E2-A is built from accepted ref `origin/accepted/proofstudio` at `43f0548e6cd9ce461a2597486bf2f888721a4d1b` on branch `ps-041e2/controlled-b2-sponsor-evidence-v1`. It is the readiness and authorization-contract gate for one later controlled live-B2 sponsor evidence read. It does not access live B2, does not call any provider, does not generate or upload media, and does not write, copy, hide, delete, or mutate any B2 object.

## Files

New (untracked):

- `scripts/ps041e2_b2_evidence.py` — readiness validator with `--check-readiness`, `--validate-authorization`, `--dry-run` (fake-storage), and fail-closed `--execute` modes.
- `scripts/ps041e2_b2_readiness_smoke.py` — check-only fake-storage readiness smoke reporting actual backend counters.
- `tests/test_ps041e2_b2_evidence.py` — focused fake-storage tests covering the full readiness contract.
- `docs/ps-041e2-b2-evidence-authorization-template.json` — default-deny authorization template.
- `specs/71-ps-041e2-controlled-b2-sponsor-evidence.md` — this slice spec.
- `docs/ps-041e2-controlled-b2-sponsor-evidence-runbook.md` — operator runbook.
- `docs/ps-041e2-controlled-b2-sponsor-evidence-proof.md` — this proof document.

Modified (tracked): none.

## Backend / Auth / Web / dependency changes

None. No FastAPI route, Auth Server source, web runtime source, dependency pin, or Genblaze identity was modified. No `boto3` or alternative B2 client was installed. No browser B2 client was added. The slice reuses only the accepted `BoundedB2ImportReader`, the accepted `B2Backend` Protocol, the accepted `B2ObjectReference` structured reference, the accepted `build_candidate` / `passport_for` importer boundary, and the accepted sanitized fixture.

## Accepted B2 reader contract

The readiness validator uses the accepted `BoundedB2ImportReader` over an injected fake backend without modification:

- Alias boundary: `PROOFSTUDIO_IMPORT_BUCKET_ALIAS` (default `configured-import`).
- Root prefix: `PROOFSTUDIO_IMPORT_ROOT` (default `import-root`).
- Caps: `max_listed_objects=256`, `max_json_bytes=1_048_576`, `max_asset_bytes=134_217_728`, `max_aggregate_bytes=536_870_912`.
- TOCTOU: head-before-get and head-after-get on `(etag, size_bytes, version_id)`.
- JSON boundary: depth ≤ 32, string ≤ 8 KiB, NFC, no controls, no duplicate keys, no credential fields, no signed/credentialed/private-target URLs, aggregate ≤ 16 MiB.
- Key safety: no leading `/`, no `\`, no `..`, no `?`, no `#`, no `://`, no controls, NFC.

## Accepted hard upper bounds (immutable)

The authorization schema defines explicit immutable readiness maxima matching the accepted reader. The authorization may narrow these limits but must never enlarge them:

- maximum object count: 256
- maximum JSON object bytes: 1_048_576
- maximum media/asset object bytes: 134_217_728
- maximum aggregate bytes: 536_870_912

Excess values are rejected (never silently clamped) with the stable codes `max_object_count_exceeds_accepted_limit`, `max_object_bytes_exceeds_accepted_limit`, and `max_total_bytes_exceeds_accepted_limit`. The accepted reader additionally enforces JSON objects at no more than 1 MiB regardless of a larger media-object authorization cap. Tests cover exact maximum, maximum + 1, and extremely large integer values.

## Authorization schema

`proofstudio.ps041e2.b2_authorization.v1` carries 23 non-secret control fields, including `object_role_by_key` (explicit bounded purpose per key) and `expected_sha256_by_key` (default empty object). The template defaults to deny: `authorized=false`, empty alias/prefix/keys, empty role plan, zero caps, only `allow_metadata_reads=true`, and every denied capability fixed `false`. The template does not itself authorize a run. A later live run requires a separately created authorization document under an approved `/tmp` authorization directory, not committed.

Unknown fields, duplicate keys, missing fields, non-matching schema/purpose, non-canonical alias/prefix/keys, non-positive or over-limit caps, any enabled denied capability, and any authorization-document structural-boundary violation all reject validation with stable error codes. The document carries no credential, account ID, application-key ID, secret, endpoint URL, signed URL, or raw bucket name.

## Explicit object-role plan

Every allowlisted object has an explicit bounded purpose. `object_role_by_key` maps each exact allowlisted key to exactly one known role. The plan key set exactly equals `allowed_keys`. The five required readiness roles (`stage_a_storyboard`, `stage_b0_manifest`, `stage_b1_manifest`, `stage_b2_manifest`, `final_delivery`) each appear exactly once. No duplicate roles. Role resolution uses the explicit map only — it never relies on allowlist order and never uses a loose first `endswith()` match. Tests prove missing required roles, duplicate roles, unknown roles, unconsumed allowlisted keys, and extra nonallowlisted keys all reject.

## Supported/reserved role invariant

Every known role has exactly one explicit bounded consumption mode or is explicitly reserved. The module-level invariant `KNOWN_ROLES == SUPPORTED_ROLES | RESERVED_ROLES` (with `SUPPORTED_ROLES == JSON_READ_ROLES | MEDIA_BYTE_ROLES`) is asserted at import time and tested explicitly. JSON-read roles (`stage_a_storyboard`, `stage_b0_manifest`, `stage_b1_manifest`, `stage_b2_manifest`, `stage_c_composition`) consume one validated JSON snapshot each. Media-byte roles (`final_delivery`) consume bytes only through the bounded asset reader. `embedded_manifest` is reserved: the accepted fixture carries it as `missing=true` with no bounded JSON descriptor, so PS-041E2-A rejects any plan that uses it with `object_role_reserved_unsupported` during authorization validation. A structurally valid authorization can therefore never reach the fake backend only to fail with `fake_backend_unknown_role`.

## Head-metadata caps enforced before any byte read (PS-041E2-A v2)

The initial exact-key observation is a metadata prelight. For every allowlisted object, before any byte read, the readiness flow enforces:

- the metadata returned by `head()` is a mapping (`object_metadata_invalid`);
- `size_bytes` is an integer, excluding `bool` (`object_size_invalid`);
- `size_bytes >= 0` (`object_size_invalid`);
- `size_bytes <= min(max_object_bytes, ACCEPTED_MAX_MEDIA_OBJECT_BYTES)` (`object_exceeds_authorization_cap` / `object_exceeds_accepted_cap`);
- the sum of declared sizes is `<= min(max_total_bytes, ACCEPTED_MAX_AGGREGATE_BYTES)` (`declared_inventory_exceeds_authorization_total` / `declared_inventory_exceeds_accepted_total`).

These caps apply even when `allow_media_byte_reads=false`. An oversized declared final delivery still rejects during the metadata preflight. No silent clamping is ever performed. Any preflight failure aborts before any `read_bytes` call. Focused tests prove oversized metadata-only final delivery rejects; total declared inventory overflow rejects; exact per-object and aggregate caps pass; negative, boolean, string and missing size values reject; and no read occurs after a metadata preflight failure.

## Normalized media/backend failures (PS-041E2-A v2)

`_bounded_asset_read` normalizes every failure to a stable `AuthorizationError` code. No raw exception text, path, bucket name, or object key ever escapes through the error channel. Focused tests prove:

- object removed after pre-head → `backend_read_failed`;
- backend `OSError` during read → `backend_read_failed`;
- non-bytes backend response → `backend_response_not_bytes`;
- malformed size in head → `object_size_invalid`;
- missing post-head → `approved_object_disappeared_after_read`;
- unexpected backend failure → `backend_read_failed`;
- no credential or raw bucket content in diagnostics.

## No inline fallback

When constructing the fake B2-backed `ImportBundleRequest`, every required descriptor consumes its exact authorized B2 key. Its `inline_json` is removed unconditionally and its `b2_reference` is set to the exact authorized key. There is no inline fallback: a missing required role/key rejects, a duplicate role rejects, and an unconsumed allowlisted key rejects. Media-only authorization (no required JSON roles) rejects at validation before any backend import. Tests prove no successful candidate contains required-role `inline_json` after B2 binding.

## Canonical alias and prefix

`configured_alias` must be a nonempty bounded NFC string with no leading or trailing whitespace, no slash, no backslash, no control characters, and no URL syntax. `allowed_prefix` must be canonical: no leading slash, no trailing slash, no surrounding whitespace, not empty or root, no repeated empty components, no `..`, no backslash, no query, no fragment, no URL syntax, no control characters, NFC. The authorized prefix used by the reader must byte-for-byte equal the authorization value; no stripping or normalization is applied. Tests prove `/prefix`, `prefix/`, and ` prefix ` reject.

## Controlled malformed-input errors

Every authorization structure is bounded before semantic validation. An iterative walk enforces: bounded nesting depth (≤ 32), bounded total list/dict items (≤ 4096), bounded string length (≤ 8 KiB), bounded key length (≤ 256 chars), no control characters, and NFC strings. Every `allowed_keys` item is validated to be a string before duplicate detection. No malformed authorization may escape as `TypeError`, `RecursionError`, `UnicodeError`, `OSError`, `MemoryError`, or raw `JSONDecodeError`. All parser and structure failures normalize to stable `AuthorizationError` codes.

## Time and operator validation

`authorized_at` and `expires_at` must be timezone-aware ISO-8601 values expressed in UTC (`Z` or `+00:00`). Date-only, timezone-naive, and non-UTC offsets are rejected. `expires_at` must be strictly after `authorized_at`. The authorization window must not exceed 24 hours. `authorized_at` must not be unreasonably in the future. When `authorized=true`, `authorized_by` must be a nonempty bounded canonical string. All failures use stable safe error codes.

## Server-binding validation

Pure testable helpers compare the authorization values against independent server-side values:

- `compare_server_alias(authorized_alias, server_alias)` — exact, constant-time comparison of UTF-8 bytes; returns only `alias_match` or `alias_mismatch`.
- `compare_bucket_identity(authorized_hash, server_bucket_identity)` — computes SHA-256 of the server bucket identity and compares in constant time; the bucket name is never printed or returned; returns only `bucket_match` or `bucket_identity_mismatch`.

The dry-run injects a separate fake server alias and fake bucket identity rather than deriving them from the authorization document. Tests cover exact match, mismatch, and absence of the raw bucket name in diagnostics.

## Read-permission flags honored before backend access

The readiness flow fails closed before any backend operation unless the required permissions are enabled:

- `allow_metadata_reads=false` → zero head calls and controlled rejection (`metadata_reads_required`).
- `allow_json_object_reads=false` → zero JSON reads and no `build_candidate` path (`json_reads_required`).
- `allow_media_byte_reads=false` → zero media byte reads.

Operations are never performed first and rejected afterward. Actual backend counters are instrumented and reported.

## Validated snapshot reuse (one backend read per JSON object)

Each authorized JSON object is read exactly once through the accepted `BoundedB2ImportReader`. The accepted reader performs head-before, size check, `read_bytes`, head-after TOCTOU and (when the `B2ObjectReference` carries `sha256`) hash verification. The exact bytes served are digested and bound to the retained parsed snapshot. The guarded candidate reader asserts the key is authorized, asserts the key was validated, returns a deep copy of the stored parsed value, and counts snapshot-consumer calls separately from backend reads. The candidate and idempotency reconstruction consume the same validated snapshot and cause zero extra backend reads.

Required results, proven by focused tests:

- one backend JSON read operation per unique approved JSON object;
- candidate and idempotency reconstruction cause zero extra backend reads;
- the digest marked `matched` is for the exact bytes used by candidate import;
- mutation after hash verification cannot substitute different imported bytes.

## Hash evidence semantics

A newly calculated digest is never labeled `verified`. The schema carries independently expected per-object SHA-256 values in `expected_sha256_by_key` (default empty object). Keys must be exact members of `allowed_keys`; values must be 64-char lowercase hex. `allow_sha256_verification=true` requires at least one expected digest; `allow_sha256_verification=false` with a nonempty expected map is rejected (strict rule). Each verified object digest is compared against its expected digest using constant-time comparison:

- exact match records `matched`;
- mismatch records `mismatch` and triggers abort A15 (`unexpected_hash_mismatch`);
- keys without an expected digest record `observed` (JSON) or `computed` (media), never `verified`.

Every expected SHA-256 entry is consumed by an actual read. An expected digest for a JSON key requires that JSON key to be read. An expected digest for a media key requires `allow_media_byte_reads=true`; otherwise validation rejects with `expected_media_hash_requires_media_reads`. No expected digest may remain unchecked after a successful run; an unconsumed expected digest rejects. The expected SHA-256 is also placed onto the `B2ObjectReference` used by the accepted reader as defense in depth. Media bytes are never included in evidence output.

## Actual backend operation counters

The readiness flow reports counters derived directly from the instrumented `FakeB2Backend`: `head_calls_total`, `read_calls_total`, `unique_json_objects_read`, `unique_media_objects_read`, `snapshot_consumer_calls`, `list_calls`, `write_attempts`, `delete_attempts`, `signed_url_attempts`, and `total_bytes_read`. The expected default five-object readiness run reports four unique JSON objects, zero media reads by default, four backend read operations after snapshot caching, and eight snapshot-consumer calls (four objects × two builds). A unique-object count is never labelled as the number of backend read operations. Focused tests compare every reported value to the instrumented backend lists.

## Missing and unauthorized object handling

The fake backend is injectable into the readiness flow. Truthful tests cover:

- one exact allowlisted key missing from the backend → `approved_object_missing` before import;
- an attempt to head/read a key not in authorization → `key_not_allowlisted` before any backend operation;
- media-only authorization (no required JSON roles) → rejects at validation before backend import;
- missing storyboard / B0 / B1 / B2 Manifest / final_delivery role → rejects at validation;
- duplicate role → rejects at validation;
- unconsumed allowlisted key → rejects at validation;
- an approved key not consumed by the declared object plan → rejects;
- unknown fake JSON key does not return `b"{}"` (the fake backend rejects);
- independently configured alias differs → `alias_mismatch`;
- independently resolved bucket hash differs → `bucket_identity_mismatch`.

No test relies on a later unrelated bundle-validation failure.

## Authorization file path safety

No mode may accidentally read `.env.local`, `.env.save`, or another credential-bearing file. Before reading, the validator rejects known environment-file basenames, requires a `.json` suffix, rejects symlinks, requires a regular file, and enforces the 64 KiB document bound. Tests prove forbidden files are rejected before any read call. The rejected path is never printed.

## Default-deny controls

Every write/delete/signed-URL/provider capability is fixed `false`. Validation rejects any enabled denied capability with `denied_capability_enabled:<field>`. Count and byte caps must be positive and within the accepted hard upper bounds. `allow_json_object_reads` and `allow_media_byte_reads` default `false`.

## Execute-mode gates (PS-041E2-B Phase-1: implemented; fail-closed unless local HEAD == current remote refs/heads/accepted/proofstudio)

PS-041E2-B Phase-1 implements the live execute layer. The `run_live_execute` flow and the CLI `--execute` mode are wired through real Git state (including the current remote `refs/heads/accepted/proofstudio` resolved via a bounded `git ls-remote`), explicit server configuration (canonical alias, import root, bucket identity, region — no implicit defaults), an injectable `EnvAccessBoundary`-backed credential provider that reads only the established server-side environment variables, the accepted `build_backblaze_backend` backend factory, and a fresh in-process `ProofStudioService` for the accepted PS-041D import + readback + passport boundary. Gates 1–20 are pure and non-networking. Gate 21 performs exactly one bounded `git ls-remote` lookup of the current `refs/heads/accepted/proofstudio`; tests inject the remote resolver and perform no network. Gate 22 is the explicit confirmation flag. No B2 credential value is read before every authorization and Git binding check passes. No B2 client is constructed before all 22 gates pass. No list, write, delete, signed-URL, or provider method is ever invoked.

Phase-1 itself performs no live B2 access in any test or smoke. The 22 gates are now implemented (the constant name `FUTURE_EXECUTE_GATES` is preserved for backward compatibility with the accepted PS-041E2-A contract; `LIVE_EXECUTE_GATES` is an alias of the same single-source-of-truth constant). Gate 21 requires local HEAD, local `origin/accepted/proofstudio`, and the current remote `refs/heads/accepted/proofstudio` to all agree. The future live run performs Git remote binding before B2 credential access. Because the PS-041E2-B implementation commit is not yet officially accepted, every CLI `--execute` invocation from a feature branch (or with a stale local accepted ref) fails closed at gate 21 with exit code 2 before any client construction.

The PM-review focused tests extend the original 47 Phase-1 cases (L1–L47) with M1–M33 cases plus corrected N1–N30 cases that cover every PM-review blocker:

- M1 true key-only environment-access boundary: secret-presence true and false without value retrieval; every pre-gate failure produces zero secret-value reads; alias/root/bucket/region reads do not expose secret values; gate 22 completion precedes the first `B2_KEY_ID` / `B2_APP_KEY` value read; the boundary never monkeypatches `os._Environ`.
- M2 explicit alias/import-root/bucket/region required (no `configured-import` default); the real resolver returns empty fields and presence=false when env vars are unset.
- M3 root-prefix mismatch (canonical_prefix != import_root) rejects; byte-for-byte equality passes.
- M4 stale local accepted ref rejects via remoteAccepted_ref_mismatch.
- M5 remote accepted mismatch rejects.
- M6 remote lookup failure (empty / malformed) rejects.
- M7 exact local and remote match passes.
- M8 arbitrary live evidence base rejected by the validator.
- M9 symlink output base rejected.
- M10 stale partial directory refused (not recursively deleted); caller-controlled marker survives.
- M11–M17 cleanup after each post-gate failure class (credential retrieval, backend construction, first HEAD, JSON GET, candidate construction, evidence writing, security scanning).
- M18 real security scanner detects every fake secret/value category (credential assignment, signed URL query, auth header, db url with credentials, unexpected http(s) url, raw bucket identity, object byte sentinel); never serializes sensitive comparison values.
- M19 no final directory on security failure.
- M20 final directory appears only after all 20 LIVE_EVIDENCE_FILES are complete and regular non-symlink files.
- M21 `cleanup_verified=true` in finalized authorization-summary and execution-summary.
- M22 S3-like real-adapter operation counts are exact (head + get_range); no full-object GET fallback.
- M23 no hidden HEAD inside `read_bytes`.
- M24 no `get_range` support rejects before reading.
- M25 bounded-range returns exact declared length; mismatches reject.
- M26 `version_id` never fabricated from `storage_class` or a constant.
- M27 fake execution reports `live_b2_calls=0`, `real_backend_factory_used=false`.
- M28 SDK invocations are not claimed as HTTP attempts; fake execution carries
  zero HTTP attempts even when exercising the real-mode report branch.
- M29 actual accepted-service `import_created=True` on first call.
- M30 actual idempotent re-import through the same service.
- M31 actual private lineage readback via `ProofStudioService.get_imported_bundle`.
- M32 actual Passport readback via `ProofStudioService.get_imported_passport`.
- M33 no raw exception, credential, bucket, endpoint or object bytes in diagnostics; no live backend constructed in any PM-review test.

The corrected PM-review blocker cases (N1–N30) extend the M-series with adversarial coverage of the corrected environment boundary, scan, cleanup, Git-state, server-binding, and partial-directory hardening:

- N1–N6 exact credential values in the fail-closed scan via `SensitiveScanContext`: bare B2 key id, bare B2 application key, bare credential under an unrelated JSON property, bare credential inside ordinary prose, bare credential with no `B2_` / `secret` marker, and the scan context drops every sensitive reference after scanning. The sensitive comparison values are never serialized.
- N7–N10 no quarantine of credential-bearing evidence: after a planted credential leak, no final directory exists, no `.partial-*` directory exists, no `.quarantine-*` directory containing the evidence exists; regular partial files are best-effort overwritten, logically unlinked and the directory removed, leaving no payload at the controlled evidence path without claiming physical-media erasure. A recursive scan of the evidence root finds none of the planted value; an optional sanitized failure summary carries only a stable error code; `_secure_remove_partial` never renames to `.quarantine-*`.
- N11–N20 real Git state fails closed: status command failure does NOT become `tree_clean=true`; status timeout does NOT become `tree_clean=true`; branch command failure yields empty branch; accepted-ref lookup failure yields empty accepted commit; clean status success yields `tree_clean=true`; dirty status success yields `tree_clean=false`; detached HEAD (literal `HEAD` or a hex commit returned by some git versions) is normalized to the exact `(detached)` marker; the exact implementation branch is normalized unchanged; a malformed commit rejects; `_run_git_command` never prints raw subprocess stderr.
- N21–N23 independent server-root evidence: `server-binding.json` carries `authorized_prefix`, `configured_import_root`, `import_root_comparison_code`, `import_root_matches_prefix` derived from independent observations; mismatched import root cannot emit a successful match result; no `report.canonical_prefix == report.canonical_prefix` tautology.
- N24–N29 partial directory + scanning hardening: symlink evidence file is rejected before reading via `lstat`; symlink partial directory is rejected; symlink at any path component under the controlled root is rejected; unexpected file is rejected before finalization; non-regular file (FIFO) is flagged; partial directory is created with owner-only mode `0o700`; `expected_files` flagging during the final scan.
- N30 accepted executor controls preserved: exact five-role plan; exact-key HEAD/GET only; no LIST; bounded-range-only reads; real operation counters; exact snapshot/hash binding; accepted `ProofStudioService` import; idempotent re-import; private lineage readback; private Passport readback; atomic final rename; truthful `live_b2_calls`; zero provider/write/delete/signed-URL capability.

The corrected PM-review Phase-1 focused tests (P1–P14) cover the defects corrected in the second PM-review pass:

- P1/P2 pinned genblaze-s3 ObjectMetadata shape without version_id: the exact pinned dataclass (key/size/last_modified/etag/content_type/storage_class/metadata — NO version_id) passes `_normalize_head`; no version ID is fabricated; dictionary fakes with a genuine version_id continue to work.
- P3 last_modified normalization: naive datetime assumed UTC; timezone-aware converted to UTC; ISO-string normalized; None returns None; malformed rejects; a last_modified change between observations rejects.
- P4 optional genuine version_id remains compared; the canonical observation identity is the four-tuple (etag, size_bytes, version_id_or_none, last_modified_or_none).
- P5 valid post-gate secret reads produce clean cleanup evidence; the explicit fields `no_pre_gate_secret_value_reads`, `pre_gate_secret_value_read_count`, `post_gate_secret_value_read_count`, `post_gate_secret_names_match`, `secret_read_order_valid`, `cleanup_secret_reads_verified` are present.
- P6 pre-gate / duplicate / missing / unexpected secret reads reject cleanup verification.
- P7/P8 all summary rewrites occur before the final scan; zero writes after the final scan (proved via the test-only write monitor).
- P9 a credential inserted during a late summary rewrite is caught by the strict final scan; post-scan mutation cannot be finalized.
- P10/P11 unreadable files and invalid UTF-8 reject; no final directory after any scanner failure; invalid UTF-8 containing a fake credential byte sequence rejects before the credential is matched.
- P12 evidence size caps: oversized per-file and aggregate overflow reject; the normal 20-file set is within both caps.
- P13 the real CLI `--execute` invokes `_validate_evidence_base` before any filesystem write; arbitrary `--evidence-out` values are rejected.
- P14 docs contain no stale payload-quarantine claim; evidence records `version_id_observed=false` when the backend does not supply version_id; the ambiguous `env_access_clean` field is gone.

All Phase-1 tests use injected fakes: the in-process `FakeB2Backend` (or an S3-like fake with `head`/`get_range`/`get` and no `read_bytes`), an injected fake `GitState`, fake `ServerConfig` (with explicit alias/import_root/bucket_identity/region), fake `CredentialProvider` (counts calls; returns inert strings), a fake `BackendFactory`, a fake `RemoteRefResolver`, an injectable `EnvAccessBoundary`, and a fresh in-process `ProofStudioService`. No test imports `genblaze_s3` or `boto3`. No test reads real credential values. No test accesses the network.

## TOCTOU controls

The readiness flow stores the initial `(etag, size_bytes, version_id_or_none, last_modified_or_none)` four-tuple for every allowlisted object before any read. The accepted reader additionally performs head-before-get and head-after-get on `(etag, size_bytes, version_id)` for each JSON read (the reader's own observation tuple is the accepted three-field set; the executor's canonical identity extends this with `last_modified_iso`). Media byte reads use a bounded asset read with pre-read head, per-object cap, aggregate budget, length match, hash and post-read head comparison using the full four-field identity. After all authorized reads and candidate construction the readiness flow heads every exact object again and compares the full four-tuple. Any difference — including a missing final object — aborts with `object_changed_during_evidence_run`. `observation_stable=true` only when every before/after tuple exactly matches. There is no missing-only shortcut and no broad listing. The final observation covers both JSON and media objects. The pinned genblaze-s3 `ObjectMetadata` does not expose `version_id`; that absence is represented as `None` in the identity (never fabricated) and recorded as `version_id_observed=false` in the evidence.

Focused tests cover media object at exact cap, cap + 1, aggregate overflow, body shorter/longer than declared size, ETag change after read, size change after read, version change after read, expected media hash match and mismatch.

## Abort conditions

Twenty abort conditions (A1–A20) are documented in the spec and surfaced by `--check-readiness`. No abort broadens the read to diagnose the bucket.## Output sanitization

The readiness output carries only stable counts, schema identifiers, hash digests, bundle/lineage identifiers, and comparison codes (`alias_match`/`bucket_match`). It never carries credentials, application key IDs, secrets, raw authorization headers, endpoint URLs, signed URLs, raw bucket names, raw authorization file paths, raw provider prompts, personal data, production data, arbitrary object bytes, unredacted exception objects, or media bytes. Authorization errors carry only a stable error code.

## Cleanup contract

The readiness flow holds no credentials and leaves no temporary credential files. The future live run will unset credentials from the execution environment and prove no retained credential state.

## Fake-storage test result

The focused test suite covers: valid authorization; accepted hard maxima and max+1/extreme rejection; canonical alias and prefix rejection; non-string and nonhashable allowlist values rejecting before duplicate detection; bounded nested authorization parsing; no raw exception escape; timezone-aware timestamp validation; execute-mode denial; authorized-by validation; canonical key safety; count/byte overflow; unknown/missing field and wrong schema/purpose; denied-capability enforcement; bucket hash validation; actual server-alias match and mismatch; actual bucket-identity match and mismatch with no raw bucket name in diagnostics; metadata-read false giving zero backend operations; JSON-read false giving zero JSON reads; media-read false giving zero media reads; real missing allowlisted object rejection before import; unauthorized key rejected before backend call; expected-hash match, mismatch, and edge cases; hash result never labelled `verified`; authorization file path safety; TOCTOU metadata change; accepted-reader SHA mismatch; idempotent import; zero provider/write/delete/list/signed-URL; forbidden-operation counting in the fake backend; output sanitization; no raw bucket name in diagnostics; cleanup verification; and CLI surface checks.

Focused PS-041E2-A v2 regression cases additionally cover: successful five-object explicit role plan; no required `inline_json` survives B2 binding; media-only authorization rejects before backend import; missing/duplicate/unconsumed/unknown role rejection; one backend JSON read per JSON object; zero backend rereads during candidate/idempotency construction; matched bytes equal imported snapshot; changed object between verification and import rejects; expected media digest cannot remain unchecked; media per-object overflow (cap and cap+1); media aggregate overflow; media body shorter/longer than declared size; media metadata TOCTOU (etag/size/version change after read); expected media hash match and mismatch; actual counters equal backend instrumentation; unknown fake JSON key does not return `b"{}"`; fake backend oversized read rejects (never truncates); full observation stability compares every object; and no raw exception, credential or bucket name in diagnostics. All tests use fake/injected storage. No test accesses the network.

## Readiness-smoke result

The readiness smoke runs one bounded fake-storage evidence flow end-to-end with independently injected server alias and bucket identity. It reports actual backend operation counters (`head_calls_total`, `read_calls_total`, `unique_json_objects_read`, `unique_media_objects_read`, `snapshot_consumer_calls`, `list_calls`, `write_attempts`, `delete_attempts`, `signed_url_attempts`, `total_bytes_read`), confirms `alias_match` and `bucket_match`, confirms hash result statuses are in `{matched, observed, computed, mismatch}` (never `verified`), confirms the explicit role plan, confirms accepted hard upper bounds are respected, confirms import idempotency and full observation stability, and produces the structured JSON block defined in the readiness contract. The default five-object readiness run reports four unique JSON objects, zero media reads, four backend read operations, and eight snapshot-consumer calls.

## Provider / live-B2 / write / delete / list result

Zero provider calls, zero live B2 calls, zero B2 writes, zero B2 deletes, zero broad B2 listings, and zero signed URLs across tests, smoke, and validator modes.

## Security scan

Owned files and generated evidence are scanned for credential markers (`B2_APPLICATION_KEY`, `B2_APPLICATION_KEY_ID`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `Authorization`, `Bearer`, `X-Amz-`, signed URL, presigned, endpoint URL, `DATABASE_URL`, password, secret, token, cookie, production email, raw prompt, `http://`, `https://`).

The final classified security-scan claim distinguishes **expected marker references** (which legitimately appear in source, tests, docs, and the authorization-template field names) from **actual secret-bearing values**. The final claim is:

- expected marker references were classified separately (these are documented field names, sanitizer token lists, and explicit prohibitions; they are not credentials);
- zero credential assignments or values;
- zero bearer tokens;
- zero signed/presigned URLs;
- zero credential-bearing DB URLs;
- zero raw bucket names in diagnostics (the fake server bucket identity constant is treated as a marker reference, not a raw production bucket name);
- zero environment-file contents.

The scan does **not** claim zero marker-token occurrences; markers are intentionally referenced by the sanitizer token list and by prohibition documentation.

## Sponsor-claim boundary

The evidence may support only bounded claims: one authorized server-side read; only allowlisted objects observed; normalized B2 references without credentials or signed URLs; approved JSON passed the accepted defensive boundary; idempotent import; private lineage UI rendered recorded B2-backed evidence; zero provider calls; zero writes/deletes/listings; recorded object digests matched, mismatched, or were observed/computed according to the actual result. A computed digest alone is not verification. The evidence must not claim universal authenticity, verified truth, legal ownership, human authorship, immutable storage, Object Lock (unless separately proven), tamper-proof storage, production compliance, complete evidence, universal byte verification, or public disclosure readiness.

## Known limitations

- PS-041E2-A does not execute any live read. PS-041E2-B Phase-1 implements the live executor and validates it entirely with injected fake backends; it does not perform any live B2 access in tests or smokes.
- The CLI `--execute` mode refuses to run unless the local HEAD equals the current remote `refs/heads/accepted/proofstudio`. From an unaccepted feature commit (or with a stale local accepted ref) it fails closed before any client construction.
- Authorization expiry is checked against the system clock; clock skew affects the check (a 60-second future tolerance is allowed).
- The authorization document is a control document only; it does not itself enforce server-side bucket policy or application-key capability. The operator must verify the application key is restricted to the intended bucket/prefix and read-only.
- Process-local import idempotency is reused from PS-041D; restart/multi-worker durability is not claimed.
- Hash verification records `matched` against an independently expected digest, or `observed`/`computed` when no expected digest is provided; it does not prove remote storage integrity, Object Lock, or tamper-proof storage.
- The readiness flow uses the accepted sanitized fixture with an injected fake backend; the accepted-state live run uses a separately approved sanitized fixture bundle whose exact keys are allowlisted.
- Partial directory cleanup is best-effort logical removal (overwrite + unlink); **physical media erasure is not claimed** on SSD, copy-on-write or journaled filesystems.

## Final PM-review correction evidence (Q1–Q16)

The final PM-review focused tests (Q1–Q16) cover the last hidden-preflight,
client-close, descriptor-safe scanning and fail-closed evidence-permission
defects:

- Q1 pinned Genblaze lazy-preflight proof: the pinned genblaze-s3 0.3.5
  `for_backblaze(preflight=False)` defers bucket-region verification to the
  first I/O call. A fully instrumented fake boto3 client (no network, no
  real boto client) proves construction issues zero `head_bucket`; the
  first `head()` and `get_range()` each trigger exactly one `head_bucket`.
- Q2 modeled 403 regional-probe path: the fake boto client returns a 403
  for `head_bucket`; the public `head()` path then creates additional
  probe clients (regional discovery). No-network; proves regional probes
  are reachable on the public path — the motivation for the exact-key
  adapter.
- Q3/Q4 exact-key adapter produces zero `head_bucket` and zero regional
  probes across any number of head/get_range calls (the lazy preflight
  never runs).
- Q5/Q6 SDK invocation counters increment exactly while HTTP-attempt counters
  are derived independently from `1 + RetryAttempts`; HeadBucket/probe HTTP
  attempts stay zero and there is no list/write/delete path.
- Retry cases 0/1/2 yield 1/2/3 attempts; missing, negative, boolean and string
  retry metadata reject with stable codes. A mixed-retry aggregate proves
  `live_b2_calls` increases beyond the zero-retry total of 22.
- Adversarial ranged bodies prove every `read` has an integer size, at most
  `requested_length + 1` bytes are collected, short and oversized bodies
  reject, `ContentLength`/`ContentRange` are exact, and `close()` runs once on
  success and every failure including read/close failures.
- Factory tests prove raw-backend cleanup on adapter/version/compatibility
  failure, adapter-owner cleanup on wrapper failure, stable cleanup-failure
  normalization, and no premature close after successful ownership transfer.
- Q6c/Q6d locally rejected reads and zero-length local reads do not
  fabricate ranged GetObject counts.
- Q7 underlying client closed exactly once; idempotent on repeated
  destroy().
- Q8 close failure raises `backend_close_failed`, leaves
  inner_close_succeeded False, raw exception text never escapes.
- Q8a a backend lacking `close()` rejects with
  `backend_close_unsupported`.
- Q8b close failure during a live run blocks final success-directory
  publication.
- Q9 descriptor no-follow scan rejects symlink evidence files, including a
  symlink replacement between validation and descriptor opening; no-follow
  open failure and nonregular descriptors reject fail closed.
- Q10 descriptor read detects same-inode size mutation between the bounded
  read and the second fstat (evidence_file_replaced); a path-swap
  replacement race is defeated by the bound descriptor (attacker content
  never read).
- Q10b size growth after the bounded read rejects at the EOF check.
- Q10c short read rejects.
- Q11 partial + base directory mode is exactly 0o700, owner == euid.
- Q11b chmod failure rejects with `evidence_permissions_unverified` (no
  best-effort swallow).
- Q11c mode mismatch rejects with `evidence_permissions_unverified`.
- Q11d/Q11f the final directory remains owner-only after atomic rename, and
  a detected post-rename mode race removes the unverified final directory.
- Q12 failure summary created exclusively with mode 0o600; pre-existing
  regular files, symlinks and exclusive-create races are never overwritten
  or followed; uncontrolled basenames are omitted.
- Q13 `_run_git_command` binds the ProofStudio root derived from the
  script location when invoked from another repository or outside any
  repository; callers cannot override the Git cwd.
- Q14 docs contain no guaranteed-physical-secure-erasure overclaim.
- Q15 `operation-counts.json` and `execution-summary.json` carry the separate
  `*_sdk_calls` and `*_http_attempts` counters, close evidence, and the
  controlled-read invariant.
- Q16 ExactKeyReadAdapter version guard asserts the pinned 0.3.5; a
  backend lacking `_client`/`_bucket` rejects with
  `backend_attributes_unavailable`.

All tests remain fake/injected and perform no network or real B2 access.

## Corrected secure-removal contract

The partial directory cleanup is best-effort logical removal (overwrite +
unlink); **physical media erasure is not claimed** on SSD, copy-on-write
or journaled filesystems. Wear leveling, copy-on-write snapshots,
journaling and deduplication may retain stale blocks the logical
overwrite cannot reach. No guaranteed physical secure erasure is claimed.

## Truth boundary

ProofStudio proves what the pipeline recorded. Proof does not equal truth. No claim is made that live B2 execution has occurred. Phase-1 implements the executor and validates it entirely with injected fake backends; the accepted-state live run is a separately PM-approved operation.
