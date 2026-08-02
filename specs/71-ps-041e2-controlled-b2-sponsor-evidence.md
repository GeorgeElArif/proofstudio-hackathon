# PS-041E2 — Controlled B2 Sponsor Evidence

Status: PS-041E2-A is the accepted readiness slice. PS-041E2-B Phase-1 implements the live execute layer with injectable fake backends and proves every live gate is fail-closed; Phase-1 performs no live B2 access. Accepted base: `origin/accepted/proofstudio` (dynamic Git ref).

## 1. Scope

PS-041E2 prepares one later controlled live-B2 sponsor evidence read. PS-041E2-A is the readiness and authorization-contract gate. PS-041E2-B Phase-1 implements the production live-read executor (the 22-gate `run_live_execute` flow and the `--execute` CLI mode) but validates it entirely with injected fake backends. Neither PS-041E2-A nor PS-041E2-B Phase-1 accesses live B2, calls any provider, generates or uploads media, or writes, copies, hides, deletes, or mutates any B2 object. They make one later live read safe, bounded, repeatable, and sponsor-relevant.

PS-041E2 owns:

- the readiness authorization schema (`proofstudio.ps041e2.b2_authorization.v1`);
- the live authorization schema (`proofstudio.ps041e2.b2_live_authorization.v1`, PS-041E2-B);
- the readiness validator (`scripts/ps041e2_b2_evidence.py`);
- the live executor `run_live_execute` (PS-041E2-B Phase-1);
- the readiness smoke (`scripts/ps041e2_b2_readiness_smoke.py`);
- the execute-readiness smoke (`scripts/ps041e2_b2_execute_readiness_smoke.py`, PS-041E2-B);
- focused fake-storage tests (`tests/test_ps041e2_b2_evidence.py`);
- this spec, the operator runbook, the proof document, and the default-deny templates.

PS-041E2 does not own:

- any live B2 execution against a real B2 account, bucket, prefix, or object (PS-041E2-B Phase-1 implements the executor and validates it with fakes; the actual accepted-state live run requires a separately PM-approved slice whose commit equals `origin/accepted/proofstudio`);
- any FastAPI route change;
- any Auth Server change;
- any web runtime change;
- any dependency change;
- any Genblaze identity change;
- any PS-041E1 UI behavior change;
- any PS-041D lineage identity change;
- any PS-041C authorization change.

## 2. Accepted base

Built from `origin/accepted/proofstudio` at `43f0548e6cd9ce461a2597486bf2f888721a4d1b`. The accepted B2 boundary is defined by `src/proofstudio/api/b2_import_reader.py` (`BoundedB2ImportReader`, `B2ImportReaderConfig`, `B2Backend` Protocol), `src/proofstudio/api/imported_bundle.py` (`B2ObjectReference`), and `src/proofstudio/api/genblaze_external_adapter.py` (`build_candidate`, `passport_for`, `parse_bundle_bytes`).

## 3. Purpose

One later authorized, bounded, server-side read from a dedicated ProofStudio-controlled Backblaze B2 prefix containing one sanitized Genblaze explainer bundle compatible with the accepted PS-041D contract. The read must prove sponsor-relevant evidence without overclaiming truth, authenticity, ownership, or storage integrity.

## 4. Exact B2 boundary

The accepted boundary is reused unchanged:

- Reader: `BoundedB2ImportReader` over an injected `B2Backend` Protocol (`head`, `read_bytes`, `list`).
- Alias: server-configured via `PROOFSTUDIO_IMPORT_BUCKET_ALIAS` (default `configured-import`). No raw bucket name crosses the alias boundary.
- Root prefix: server-configured via `PROOFSTUDIO_IMPORT_ROOT` (default `import-root`). Keys are NFC relative paths under this root.
- Caps: `max_listed_objects=256`, `max_json_bytes=1_048_576`, `max_asset_bytes=134_217_728`, `max_aggregate_bytes=536_870_912`.
- Structured B2 reference fields: `{backend, bucket_alias, object_key, version_id?, size_bytes?, content_type?, etag?, sha256?, uploaded_at?, source_prefix?, manifest_hash?}`. ETag is opaque and never labeled SHA-256.
- Key safety: no leading `/`, no `\`, no `..` segment, no `?`, no `#`, no `://`, no control characters, NFC-normalized.
- TOCTOU: head-before-get and head-after-get on `(etag, size_bytes, version_id)`.
- JSON sanitization: depth ≤ 32, string ≤ 8 KiB, NFC, no control characters, no duplicate keys, no credential fields, no signed/credentialed/private-target URLs, aggregate ≤ 16 MiB.
- URL rejection: userinfo, query, fragment, unsupported schemes, loopback/private/link-local/metadata hosts are rejected at the boundary.
- Signed-URL rejection: signed transport URLs are rejected, never retained as identity.
- Fake storage injection: the readiness flow uses `FakeB2Backend` (in-process, no network).

No new B2 client is added. `boto3` is not imported and no new third-party dependency is introduced.

## 5. Authorization schema

`proofstudio.ps041e2.b2_authorization.v1` is a non-secret control document. The template lives at `docs/ps-041e2-b2-evidence-authorization-template.json`. Required fields (23):

| field | type | constraint |
|---|---|---|
| `schema` | string | exact `proofstudio.ps041e2.b2_authorization.v1` |
| `authorized` | bool | `true` required for execute |
| `authorized_by` | string | nonempty canonical operator identity when `authorized=true` |
| `authorized_at` | ISO 8601 UTC | timezone-aware, not unreasonably in the future |
| `expires_at` | ISO 8601 UTC | timezone-aware, after `authorized_at`, within the short maximum validity window |
| `configured_alias` | string | canonical, compared byte-for-byte against independently resolved server alias |
| `allowed_bucket_name_hash` | hex64 | SHA-256 of the controlled bucket name; compared against SHA-256 of independently resolved server bucket |
| `allowed_prefix` | string | canonical (no normalization), bounded, non-root |
| `allowed_keys` | list[string] | nonempty exact object allowlist |
| `object_role_by_key` | object | explicit bounded purpose per key; key set exactly equals `allowed_keys` |
| `max_object_count` | int | > 0, ≥ `len(allowed_keys)`, ≤ accepted hard upper bound (256) |
| `max_object_bytes` | int | > 0, ≤ accepted hard upper bound (134_217_728) |
| `max_total_bytes` | int | > 0, ≥ `max_object_bytes`, ≤ accepted hard upper bound (536_870_912) |
| `allow_metadata_reads` | bool | `true` required for the readiness flow |
| `allow_json_object_reads` | bool | `true` required for the readiness flow |
| `allow_media_byte_reads` | bool | optional |
| `allow_sha256_verification` | bool | optional; if true requires nonempty `expected_sha256_by_key` |
| `allow_write` | bool | fixed `false` |
| `allow_delete` | bool | fixed `false` |
| `allow_signed_urls` | bool | fixed `false` |
| `allow_provider_calls` | bool | fixed `false` |
| `expected_sha256_by_key` | object | map of exact allowlisted key → 64 lowercase hex; default empty |
| `purpose` | string | exact `PS-041E2 controlled sponsor evidence` |

### 5.0 Explicit object-role plan

Every allowlisted object has an explicit bounded purpose. `object_role_by_key` maps each exact allowlisted key to exactly one known role. The contract:

- its key set exactly equals `allowed_keys` — no missing allowlisted key, no extra nonallowlisted key;
- every role is a known role (`stage_a_storyboard`, `stage_b0_manifest`, `stage_b1_manifest`, `stage_b2_manifest`, `stage_c_composition`, `final_delivery`, `embedded_manifest`);
- every known role is either **supported** (consumed as a JSON-read role or a media-byte role) or **reserved** (rejected at validation). The invariant `KNOWN_ROLES == SUPPORTED_ROLES | RESERVED_ROLES` is asserted at import time:
  - JSON-read roles: `stage_a_storyboard`, `stage_b0_manifest`, `stage_b1_manifest`, `stage_b2_manifest`, `stage_c_composition`;
  - media-byte roles: `final_delivery`;
  - reserved roles: `embedded_manifest` (the accepted fixture carries it as `missing=true` with no bounded JSON descriptor; PS-041E2-A rejects it with `object_role_reserved_unsupported` rather than deferring the failure to the fake backend).
- each role appears at most once (no duplicate semantic roles);
- the five required readiness roles each appear exactly once in every nonempty plan: `stage_a_storyboard`, `stage_b0_manifest`, `stage_b1_manifest`, `stage_b2_manifest`, `final_delivery`;
- optional future supporting-media roles (`stage_c_composition`) must be explicit and bounded;
- an expected digest for a media-byte role (`final_delivery`) requires `allow_media_byte_reads=true`;
- role resolution uses the explicit map only. It never relies on allowlist order and never uses a loose first `endswith()` match.

A structurally valid authorization can never reach the fake backend only to fail with `fake_backend_unknown_role`. Validation rejects reserved roles before any backend work.

The document carries no credential, account ID, application-key ID, secret, endpoint URL, signed URL, or raw bucket name. The template does not itself authorize a run. A later live run requires a separately created authorization document under an approved `/tmp` authorization directory, not committed to the repository.

Unknown fields, duplicate keys, missing fields, non-matching schema/purpose, non-canonical alias/prefix/keys, non-positive or over-limit caps, any enabled denied capability, and any authorization-document structural-boundary violation all reject validation with stable error codes.

### 5.1 Accepted hard upper bounds (immutable)

The authorization may narrow but must never enlarge these limits:

- `max_object_count` ≤ 256
- `max_object_bytes` ≤ 134_217_728
- `max_total_bytes` ≤ 536_870_912
- JSON objects are enforced at no more than 1 MiB by the accepted reader regardless of a larger media-object cap.

Excess values are rejected (never silently clamped) using the stable codes:

- `max_object_count_exceeds_accepted_limit`
- `max_object_bytes_exceeds_accepted_limit`
- `max_total_bytes_exceeds_accepted_limit`

### 5.2 Canonical alias and prefix (no silent rewriting)

`configured_alias` must be a nonempty bounded NFC string with no leading or trailing whitespace, no slash, no backslash, no control characters, and no URL syntax. `allowed_prefix` must be canonical: no leading slash, no trailing slash, no surrounding whitespace, not empty or root, no repeated empty components, no `..`, no backslash, no query, no fragment, no URL syntax, no control characters, NFC. The authorized prefix used by the reader must byte-for-byte equal the authorization value; no stripping or normalization is applied.

### 5.3 Time and operator validation

`authorized_at` and `expires_at` must be timezone-aware ISO-8601 values expressed in UTC (`Z` or `+00:00`). Date-only, timezone-naive, and non-UTC offsets are rejected. `expires_at` must be strictly after `authorized_at`. The authorization window must not exceed 24 hours. `authorized_at` must not be unreasonably in the future. When `authorized=true`, `authorized_by` must be a nonempty bounded canonical string.

## 6. Credential separation

Credentials are never passed through CLI arguments. Credentials are never stored in authorization JSON. Credentials are configured only through the established local server-side environment mechanism (`B2_KEY_ID`, `B2_APP_KEY`, `B2_BUCKET`, `B2_REGION`). The readiness validator never reads, prints, or logs credential-bearing environment files (`.env.local`, `.env.save`) or credential variable values. The validator rejects known environment-file basenames and non-`.json` paths before any read. The least-privilege application-key requirement is documented in the runbook: the key must be restricted to the intended bucket and prefix and read-only capability.

## 7. Exact alias / prefix / object allowlist

The authorization binds an exact canonical configured alias, a canonical bounded prefix, and an exact object allowlist. Every allowlisted key must be inside the approved prefix. Root and empty prefixes are rejected. Count and byte caps are explicit, positive, and within the accepted hard upper bounds. The readiness flow compares the authorized alias against an independently injected server alias, and compares the authorized bucket hash against the SHA-256 of an independently injected server bucket identity. Mismatch returns only a safe stable code (`alias_mismatch`, `bucket_identity_mismatch`); the raw bucket name is never printed or returned.

## 8. Read-permission flags honored before backend access

The readiness flow is metadata-default. `allow_json_object_reads` and `allow_media_byte_reads` default `false`. The flow fails closed before any backend operation unless the required metadata and JSON permissions are enabled:

- `allow_metadata_reads=false` → zero head calls and controlled rejection before any backend operation.
- `allow_json_object_reads=false` → zero JSON reads and no `build_candidate` path that indirectly reads JSON.
- `allow_media_byte_reads=false` → zero media byte reads.

Operations are never performed first and rejected afterward. Actual backend operation counters are instrumented and reported. Each authorized JSON object is read exactly once through the accepted `BoundedB2ImportReader`; the validated parsed snapshot is retained and deep-copied for both the candidate and the idempotency reconstruction, causing zero extra backend reads. The guarded candidate reader asserts the key is authorized, asserts the key was validated, returns a deep copy of the stored parsed value, and counts snapshot-consumer calls separately from backend reads. The fake backend explicitly fails and counts any forbidden write/delete/signed-URL operation.

Reported counters derived directly from the instrumented backend include: `head_calls_total`, `read_calls_total`, `unique_json_objects_read`, `unique_media_objects_read`, `snapshot_consumer_calls`, `list_calls`, `write_attempts`, `delete_attempts`, `signed_url_attempts`, and `total_bytes_read`. A unique-object count is never labelled as the number of backend read operations. The expected default five-object readiness run distinguishes four unique JSON objects, zero media reads by default, and exactly four backend read operations after snapshot caching.

## 9. Hash evidence semantics

A newly calculated digest is never labeled `verified`. The schema carries independently expected per-object SHA-256 values in `expected_sha256_by_key`. Keys must be exact members of `allowed_keys`; values must be 64-char lowercase hex. `allow_sha256_verification=true` requires at least one expected digest; `allow_sha256_verification=false` with a nonempty map is rejected (strict rule). Each verified object digest is compared against its expected digest using constant-time comparison:

- exact match records `matched`;
- mismatch records `mismatch` and triggers abort A15 (`unexpected_hash_mismatch`);
- keys without an expected digest record `observed` (JSON) or `computed` (media), never `verified`.

Every expected SHA-256 entry must be consumed by an actual read. An expected digest for a JSON key requires that JSON key to be read. An expected digest for a media key requires `allow_media_byte_reads=true`. No expected digest may remain unchecked after a successful run. Each hash result records `key`, `role`, `status` (`matched` / `observed` / `computed` / `mismatch`) and `sha256`. A computed digest alone is never verification.

The digest labelled `matched` is the digest of the exact bytes parsed into the snapshot that `build_candidate` consumed. Where practical, the expected SHA-256 is placed onto the `B2ObjectReference` used by the accepted reader as defense in depth; the reader verifies it before returning the parsed value. Mutation after hash verification cannot substitute different imported bytes because the snapshot is immutable and only deep copies are handed out.

Media bytes are never included in evidence output.

## 10. TOCTOU before/after observations

The accepted reader performs head-before-get and head-after-get on `(etag, size_bytes, version_id)` for each JSON read. The readiness flow additionally stores the initial `(etag, size_bytes, version_id)` tuple for every allowlisted object before any read and, after all authorized reads and candidate construction, heads every exact object again and compares the full tuple. Any difference — including a missing final object — aborts with `object_changed_during_evidence_run`. `observation_stable=true` only when every before/after tuple exactly matches. There is no missing-only shortcut and no broad listing. The final observation covers both JSON and media objects.

Media byte reads use a bounded asset read with the full sequence: pre-read head; reject missing; reject declared size above authorization `max_object_bytes`; reject declared size above the accepted 128 MiB maximum; reserve the declared size against the aggregate-byte budget; read no more than the exact approved limit; reject truncation or length mismatch; hash the exact returned bytes; post-read head; compare etag, size_bytes and version_id; abort on any difference; update the shared aggregate-byte counter. The fake backend rejects oversized reads and never silently returns a truncated body.

### 10.1 Head-metadata caps enforced before any byte read (PS-041E2-A v2)

The initial exact-key observation is a metadata preflight. For every allowlisted object, before any byte read, the readiness flow requires:

- the metadata returned by `head()` is a mapping (`object_metadata_invalid`);
- `size_bytes` is an integer, excluding `bool` (`object_size_invalid`);
- `size_bytes >= 0` (`object_size_invalid`);
- `size_bytes <= min(max_object_bytes, ACCEPTED_MAX_MEDIA_OBJECT_BYTES)` (`object_exceeds_authorization_cap` / `object_exceeds_accepted_cap`);
- the sum of declared sizes is `<= min(max_total_bytes, ACCEPTED_MAX_AGGREGATE_BYTES)` (`declared_inventory_exceeds_authorization_total` / `declared_inventory_exceeds_accepted_total`).

These caps apply even when `allow_media_byte_reads=false`. An oversized declared final delivery still rejects during the metadata preflight. No silent clamping is ever performed. Any preflight failure aborts before any `read_bytes` call, any candidate construction, and any `build_candidate` invocation.

### 10.2 Normalized media/backend failures

`_bounded_asset_read` normalizes every failure to a stable `AuthorizationError` code. No raw exception text, path, bucket name, or object key ever escapes through the error channel:

- malformed pre-head metadata → `object_metadata_invalid` / `object_size_invalid`;
- backend head exception → `backend_head_failed`;
- object disappearance between pre-head and read → `backend_read_failed`;
- `OSError` during read → `backend_read_failed`;
- non-bytes backend response → `backend_response_not_bytes`;
- malformed post-head metadata → `object_metadata_invalid` / `object_changed_during_evidence_run`;
- object disappearance between read and post-head → `approved_object_disappeared_after_read`;
- length mismatch (truncation or substitution) → `media_length_mismatch`;
- oversized backend response → `media_object_exceeds_approved_limit`;
- unexpected backend failure → `backend_read_failed`.

## 11. Abort conditions

The validator aborts before or during access on any of the following:

- A1 authorization absent, malformed, expired, or on a forbidden path;
- A2 alias mismatch (compared against the independently resolved server alias);
- A3 bucket identity mismatch (compared against the SHA-256 of the independently resolved server bucket);
- A4 prefix is not canonical (empty, root, leading/trailing slash, surrounding whitespace, unsafe);
- A5 object count exceeds the accepted hard cap;
- A6 an object is outside the approved prefix;
- A7 a key was not explicitly allowlisted (rejected before any backend call);
- A8 an object exceeds the per-object byte cap;
- A9 total bytes exceed the accepted hard cap;
- A10 a credential, token, authorization header, or signed URL appears in output;
- A11 a write/delete/copy operation is attempted;
- A12 production, customer, personal, or unexpected data is observed;
- A13 JSON is malformed or violates accepted nesting/size boundaries;
- A14 a provider call occurs;
- A15 an unexpected hash mismatch occurs (an `expected_sha256_by_key` mismatch is not authorized);
- A16 object metadata changes between before/after observations;
- A17 source schema differs from the approved schema;
- A18 a browser receives a raw B2 URL or credential-bearing field;
- A19 repository branch/commit/tree state differs;
- A20 evidence output fails its final secret scan.

No abort broadens the read to diagnose the bucket.

## 12. Output sanitization

Sanitized evidence output (only under `/tmp/proofstudio-ps041e2-live-evidence/`) may include: authorization summary, execution state, approved object inventory, normalized B2 references, JSON boundary results, hash results (`matched`/`mismatch`/`observed`/`computed`), observation stability, import result, idempotency result, private lineage summary, private passport summary, UI runtime validation, provider/B2 operation counters, cleanup verification, security scan, and known limitations.

Never included: credentials, application key IDs, secrets, raw authorization headers, endpoint URLs, signed URLs, raw bucket names, raw authorization file paths, raw provider prompts, personal data, production data, arbitrary object bytes, unredacted exception objects, or media bytes.

## 13. Authorization file path safety

No mode may accidentally read `.env.local`, `.env.save`, or another credential-bearing environment file. Before reading:

- reject known environment-file basenames (`.env`, `.env.local`, `.env.save`, `.env.production`, `.env.development`, `.env.test`, `.env.staging`, `.env.example`, `credentials`, `credentials.json`);
- require a `.json` suffix;
- reject symlinks;
- require a regular file;
- enforce the document size bound (64 KiB).

The rejected path is never printed. For future live execute mode, the authorization file must resolve under an approved `/tmp` authorization directory. For repository template validation, only the exact committed template path is allowed.

## 14. Cleanup

Credentials are removed/unset from the execution environment immediately after execution. The cleanup verification proves no process, container, or temporary credential file remains.

## 15. Evidence claims

The evidence may support only claims such as:

- ProofStudio performed one authorized, bounded, server-side read from Backblaze B2.
- Only exact allowlisted objects were observed.
- B2 references were normalized without exposing credentials or signed URLs.
- Approved JSON objects passed the same defensive import boundary as inline bundles.
- The imported record was idempotent.
- The private lineage UI rendered the recorded B2-backed evidence.
- No provider call occurred during the evidence run.
- No B2 write, delete, or broad listing occurred.
- Recorded object digests matched, mismatched, or were observed/computed according to the actual result. A computed digest alone is not verification.

## 16. Prohibited claims

The evidence must not claim universal authenticity, verified truth, legal ownership, human authorship, immutable storage, Object Lock (unless separately proven), tamper-proof storage, production compliance, complete evidence, universal byte verification, or public disclosure readiness.

## 17. Execute mode (PS-041E2-B Phase-1: implemented; fail-closed unless local HEAD == current remote refs/heads/accepted/proofstudio)

PS-041E2-B Phase-1 implements the live execute layer. The `--execute <authorization-path>` CLI mode now resolves a real `GitState` (including the current remote `refs/heads/accepted/proofstudio` via a bounded `git ls-remote`), an explicit `ServerConfig` (canonical alias, import root, bucket identity, region — no implicit defaults), an injectable `EnvAccessBoundary`-backed `CredentialProvider`, and the accepted `build_backblaze_backend` backend factory, then invokes `run_live_execute`. Gates 1–20 are pure and non-networking. Gate 21 performs exactly one bounded Git remote-ref lookup (`git ls-remote`); tests inject the remote resolver and perform no network. Gate 22 is the explicit confirmation flag. The credential provider and backend factory are only invoked after all 22 gates pass. No list, write, delete, signed-URL, or provider method is ever invoked at any point.

The CLI execute path always confines the evidence output root to exactly `/tmp/proofstudio-ps041e2-live-evidence`; a custom `--evidence-out` is accepted for backward compatibility but ignored for execute mode. A custom evidence directory is available only through direct dependency injection in tests.

However, **Phase-1 itself performs no live B2 access in any test or smoke**. The fake-backend tests and smokes use injected fakes. The only path that may touch live B2 is the real CLI `--execute` mode after every gate has passed and only when the local HEAD equals the current remote `refs/heads/accepted/proofstudio`. From any feature branch, or when the local accepted ref is stale relative to the remote, `--execute` fails closed at gate 21 with exit code 2 before any client construction. No credential is read. No backend is constructed. No evidence is written. The accepted-state live run requires a separately PM-approved slice whose commit equals the current remote `refs/heads/accepted/proofstudio`.

The canonical execution-gate contract is the single source-of-truth constant `FUTURE_EXECUTE_GATES` in `scripts/ps041e2_b2_evidence.py` (`FUTURE_EXECUTE_GATES_COUNT = LIVE_EXECUTE_GATES_COUNT = 22`). The same constant is consumed by `_execute_gates()`, the `--check-readiness` summary, the `--execute` mode stderr output, focused tests, the execute-readiness smoke, this spec, the runbook, the proof document, and the `execution-gates.json` evidence artifact. No separately maintained list may drift from this constant.

### 17.1 True key-only environment-access boundary

The real CLI execute path constructs an `EnvAccessBoundary` (`RealEnvAccessBoundary`) before any pre-gate check runs. The boundary snapshots `os.environ.keys()` exactly once at construction time and exposes three distinct methods:

- `read_non_secret(name)` — for the four non-secret configuration names (`PROOFSTUDIO_IMPORT_BUCKET_ALIAS`, `PROOFSTUDIO_IMPORT_ROOT`, `B2_BUCKET`, `B2_REGION`); hard-rejects if called on `B2_KEY_ID` / `B2_APP_KEY`;
- `secret_name_present(name)` — KEY-MEMBERSHIP ONLY; inspects the captured key-set snapshot and NEVER invokes `get` / `__getitem__` for `B2_KEY_ID` or `B2_APP_KEY`;
- `read_secret_after_gates(name)` — the only method that returns a secret value; raises `AuthorizationError("secret_value_read_before_gate_completion")` until the executor calls `mark_gates_completed`.

The `CredentialProvider` is the only component permitted to read secret values; it reads them through `read_secret_after_gates`. The executor calls `mark_gates_completed` immediately after gate 22 passes and before invoking the `CredentialProvider`. The boundary does NOT monkeypatch `os._Environ` globally; the previous `EnvAccessSpy` monkeypatch approach (whose patched `__contains__` invoked the original `__getitem__`, silently materializing secret values while hiding the access) has been removed. The four non-secret configuration fields may be read pre-gate. There is no implicit default for any of them; missing any of the four rejects at gate 17 with `server_side_configuration_missing` before credential retrieval or backend construction.

### 17.2 Strengthened accepted-commit binding

Gate 21 resolves and compares local HEAD, the local `origin/accepted/proofstudio`, and the current remote `refs/heads/accepted/proofstudio`. All three must agree before any credential is read. The remote resolver uses a bounded `git ls-remote` subprocess with a timeout; it fails closed (returns empty string) when the remote cannot be reached, the ref does not exist, or the returned value is not a 40-hex commit. The remote binding closes the stale-local-ref loophole.

### 17.3 Atomic finalization (13-step order)

The final run directory does not exist until every success artifact is complete AND the strict final scan has passed over the exact finalized bytes. The executor performs: (1) create a validated partial directory; (2) write every provisional evidence artifact; (3) destroy the backend/client and release credential references; (4) complete `cleanup-verification.txt` (never rewritten); (5) run the initial classified security scan; (6) write `classified-security-scan.txt` and `known-limitations.txt`; (7) set `cleanup_verified=true` on the in-memory report; (8) rewrite `authorization-summary.json` and `execution-summary.json`; (9) verify all `LIVE_EVIDENCE_FILES` exist and are regular non-symlink files; (10) run the strict final security scan over all exact finalized bytes; (11) make no further file-content change; (12) retain the final scan result only in the in-memory `LiveExecuteReport`; (13) atomically rename partial to final as the last filesystem operation. No evidence file is modified after the final scan; the final scan result is never written to an evidence file merely to record that the scan passed.

### 17.4 Real fail-closed security scan

The classified security scan detects real credential-bearing values, never just marker words: exact credential values supplied only in-memory to the scan (object byte sentinels, raw bucket identity); credential assignments; signed/presigned URL query parameters; Authorization/Bearer header values; credential-bearing database URLs; unexpected `http://` or `https://` URLs; raw object-byte sentinels; raw bucket identity. The sensitive comparison values are NEVER serialized into the scan output; the report carries only file names, token names and per-category counts. Any real leak prevents atomic finalization.

### 17.5 Cleanup on every post-gate path

After the credential provider has been called, every outcome destroys the backend, releases inner backend/client references and credential references, and best-effort overwrites regular partial files before logical unlink and directory removal. No payload remains at the controlled evidence path; no payload-bearing quarantine is retained, and physical-media erasure is not claimed. An optional separately generated sanitized failure summary may be written next to the removed partial directory and contains only a stable error code (no source evidence). No raw object bytes are retained; no raw exception text, bucket name, endpoint, or object key escapes through the error channel. Failures from the credential provider, backend factory, client construction, HEAD, GET, fixture loading, candidate creation, import service, evidence writing, security scanning, and the final rename are all normalized to stable codes. Ordinary failures cannot broaden B2 access.

### 17.6 Exact real-adapter counters

The controlled read path uses the accepted ``ExactKeyReadAdapter``
(``proofstudio.provenance.genblaze_store``) which wraps the pinned
``S3StorageBackend`` and issues ONLY low-level ``HeadObject`` and ranged
``GetObject`` calls through the boto3 client. The pinned genblaze-s3
0.3.5 public ``head()`` / ``get_range()`` methods each call
``_ensure_region_verified()`` which calls ``head_bucket`` (and, on the
modeled B2 403 non-redirect path, may trigger parallel regional probes).
The ``ExactKeyReadAdapter`` bypasses that lazy preflight entirely, so the
controlled read path produces exactly zero ``head_bucket`` calls and
exactly zero regional probes. The ``GuardedLiveBackend`` adapter enforces
the corrected read contract: no hidden HEAD inside ``read_bytes`` (reuses
the immediately preceding counted head metadata); no full-object GET
fallback (``get_range`` is mandatory for the accepted live adapter; absent
``get_range`` rejects with ``backend_get_range_unsupported`` before any
byte is read); exact byte length must equal the declared approved size;
``version_id`` is never fabricated from ``storage_class`` or a constant.

SDK invocations and actual HTTP attempts are tracked separately:
``head_object_sdk_calls``, ``ranged_get_object_sdk_calls``,
``head_object_http_attempts``, ``ranged_get_object_http_attempts``,
``head_bucket_http_attempts`` and ``regional_probe_http_attempts``. Each
successful SDK response must contain mapping-shaped ``ResponseMetadata`` with
a non-negative, non-boolean integer ``RetryAttempts``; its actual attempts are
``1 + RetryAttempts``. Missing or malformed metadata rejects with stable codes.
The no-preflight counters remain zero. ``live_b2_calls`` is the sum of the four
HTTP-attempt counters, never an SDK-call count.

Ranged GET responses must be mappings with a non-negative integer
``ContentLength`` exactly equal to the requested length. When present,
``ContentRange`` must describe the exact requested offset/end interval. The
body must expose ``read(n)`` and ``close()``. Reads are bounded to an absolute
collection maximum of ``requested_length + 1``; exact length succeeds, short
data rejects with ``get_object_length_mismatch``, and one extra byte rejects
with ``get_object_range_exceeded``. No unbounded ``read()`` is permitted and
the body is closed exactly once in ``finally`` on every success/failure path.

### 17.7 Underlying client close exactly once

``GuardedLiveBackend.destroy()`` closes the underlying client exactly once
before clearing the inner reference. The close state is surfaced as
``inner_close_attempted``, ``inner_close_succeeded`` and
``inner_close_call_count``. ``cleanup_verified`` may be True only when
``inner_close_succeeded`` is True. A close failure is normalized to
``AuthorizationError("backend_close_failed")`` (raw exception text never
escapes) and prevents final success-directory publication. A backend
lacking ``close()`` rejects with ``backend_close_unsupported``. The
accepted clientless fake exposes an explicit counting ``close()`` rather
than relying on an implicit exception. Repeated
``destroy()`` calls are idempotent (no double close).

### 17.8 Descriptor-safe evidence reading

Evidence file reading is descriptor-based and no-follow. Each evidence
file is opened with ``O_RDONLY | O_NOFOLLOW`` (``O_CLOEXEC`` where
available); the descriptor is ``fstat``-ed, required to be a regular file
owned by the current effective UID, size-capped per-file and aggregate,
read exactly the declared bounded size, immediately EOF-verified,
``fstat``-ed again, and the device/inode/mode/size compared. Stable error
codes: ``evidence_file_symlink``, ``evidence_file_replaced``,
``evidence_file_unreadable``, ``evidence_file_invalid_utf8``,
``evidence_file_too_large``, ``evidence_aggregate_too_large``. Paths and
raw exception text are never included in diagnostics.

### 17.9 Fail-closed directory permissions

The live evidence base and partial directory must be owned by the current
effective UID and have mode exactly ``0o700``. ``chmod`` is applied when
newly created and re-verified after; a ``chmod`` failure rejects with
``evidence_permissions_unverified``; a mode mismatch rejects with
``evidence_permissions_unverified``; an ownership mismatch rejects with
``evidence_owner_mismatch``. There is no best-effort ``except OSError:
pass`` swallow in permission enforcement. The final directory must remain
owner-only after the atomic rename.

### 17.10 Safe failure-summary write

The sanitized failure summary is created with ``os.open`` using
``O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW`` and mode ``0o600``, with a
bounded deterministic UTF-8 payload and ``fsync`` before close. A
pre-existing regular file or symlink is never overwritten or followed;
when safe exclusive creation cannot be established the summary is silently
omitted.

### 17.11 Corrected secure-removal contract

The partial directory cleanup is best-effort logical removal: every
regular file is best-effort overwritten with zeros before unlinking, then
the directory tree is removed. No payload is retained at the controlled
evidence path. **Physical media erasure is not claimed** on SSD,
copy-on-write or journaled filesystems. No guaranteed physical secure
erasure is claimed.

### 17.12 ProofStudio Git cwd binding

Every local Git command and every ``git ls-remote`` invocation is pinned
to the ProofStudio repository root derived from the script's resolved
location (``Path(__file__).resolve().parent.parent``). The executor never
depends on the shell's current working directory: invoking from another
Git repository, or from outside any repository, still binds the
ProofStudio repository. A wrong-repository state cannot authorize the run.

### 17.13 Truthful `live_b2_calls` semantics

`live_b2_calls` is zero for fake execution and for real execution equals
``head_object_http_attempts + ranged_get_object_http_attempts +
head_bucket_http_attempts + regional_probe_http_attempts``. For the accepted
zero-retry five-object plan the SDK/attempt counts are 18/18 HEAD and 4/4 GET,
so `live_b2_calls == 22`; injected retries increase it truthfully.
`real_backend_factory_used` distinguishes the two paths. For fake
execution: `live_b2_calls == 0`, `real_backend_factory_used == false`. For
real execution: `real_backend_factory_used == true`, `live_b2_calls > 0`
after a successful five-object run. The hard-coded `"live_b2_calls": 0`
from earlier drafts has been removed from every real-execution output
path.

### 17.13a Factory construction ownership

Once the raw backend is constructed the factory closes the currently owned
resource exactly once on every adapter/version/compatibility/wrapper failure.
Ownership transfers to the adapter only after successful adapter construction
and to the returned guard only after successful wrapper construction. Cleanup
failure is normalized to ``backend_factory_cleanup_failed``; garbage
collection and raw exception text are never relied upon.

### 17.14 Accepted import + readback service

The live run uses the accepted PS-041D `ProofStudioService` to construct the candidate from the validated snapshots, import it through `import_genblaze_bundle` (capturing the real created/idempotent result), re-import through the same service to prove idempotency, retrieve the stored private lineage bundle through `get_imported_bundle`, retrieve the portable Passport through `get_imported_passport`, and derive summaries from those retrieved results. `import_created` is set from the actual import result, never hard-coded.

## 18. No provider calls / no writes / no broad listing / no public B2 route

The readiness flow records zero provider calls, zero B2 writes, zero B2 deletes, zero broad listings, and zero signed URLs. No public B2 route is exposed. No browser B2 client is added.

## 19. Truth boundary

ProofStudio proves what the pipeline recorded. Proof does not equal truth.

## 20. PS-041E2-B Phase-1 live executor

Phase-1 implements the live executor and validates it entirely with injected fake backends. It performs no live B2 access. The implementation reuses the accepted server-side B2 backend `proofstudio.provenance.genblaze_store.build_backblaze_backend` (which wraps `genblaze_s3.backend.S3StorageBackend.for_backblaze`) without modification. The executor's narrow adapter is `GuardedLiveBackend` in `scripts/ps041e2_b2_evidence.py`, which exposes the accepted `B2Backend` Protocol with operation counting and forbidden-method enforcement.

### 20.1 Live authorization schema

`proofstudio.ps041e2.b2_live_authorization.v1` is a strict superset of the readiness schema. It adds two live-specific fields:

| field | type | constraint |
|---|---|---|
| `evidence_run_id` | string | canonical path-safe lowercase identifier, 1-64 chars, no leading/trailing/repeat dash |
| `execution_commit` | string | lowercase hex40 git commit SHA |

All readiness fields carry their existing constraints and the live schema additionally requires `authorized=true`, `authorized_by` nonempty canonical, `allow_metadata_reads=true`, `allow_json_object_reads=true`, and an unexpired authorization window. The committed template (`docs/ps-041e2-b-live-authorization-template.json`) defaults to deny and does not itself authorize a run. Live authorization files must resolve only under `/tmp/proofstudio-ps041e2-authorizations/`.

### 20.2 Implemented 22-gate executor

The executor implements all 22 gates from `FUTURE_EXECUTE_GATES` before constructing the guarded live backend. The gates cover: exact live schema; `authorized=true`; canonical operator; UTC authorization time; unexpired authorization; 24-hour validity window; canonical evidence-run identifier; exact configured alias; independently resolved bucket identity hash; canonical non-root prefix; exact allowlisted keys; explicit object-role plan; hard count/per-object/aggregate caps; metadata-read permission; required JSON-read permission; optional media-read permission; expected-hash contract; all prohibited capabilities false; required server-side configuration present; clean repository and exact accepted commit; explicit controlled-live-read confirmation; output location, sanitization, and cleanup readiness.

Gate evaluation is structured as: gates 1–20 are pure and non-networking; gate 21 performs exactly one bounded `git ls-remote` lookup of the current `refs/heads/accepted/proofstudio`; gate 22 is the explicit confirmation flag. No B2 credential value is read before every authorization and Git binding check passes. No B2 client is constructed before all 22 gates pass. The backend factory is only called after the credential provider returns. The 32-step operation order is exact and has no fallback to inline JSON, listing, prefix traversal, URL fetch, signed URL, alternate alias/prefix, or broader-scope retry. Tests inject the remote resolver and perform no network.

### 20.3 Credential handling

Credentials are never accepted through CLI arguments, never stored in authorization JSON, never printed. The executor retrieves credentials only through the established server-side environment mechanism (`B2_KEY_ID`, `B2_APP_KEY`, `B2_BUCKET`, `B2_REGION`). No B2 credential value is read before every authorization and Git binding check passes. The pre-gate server-config resolver uses KEY-MEMBERSHIP checks only via the injectable `EnvAccessBoundary` (`secret_name_present` inspects a captured key-set snapshot and never invokes `get` / `__getitem__` for the two secret names). The `CredentialProvider` is the only component permitted to read secret values; it reads them via `read_secret_after_gates`, which raises immediately until the executor calls `mark_gates_completed` (immediately after gate 22). Credential locals are released by the cleanup step. The exact credential values are held for the minimum scan interval only (via a narrow `SensitiveScanContext`) and dropped immediately after the fail-closed scan completes. The credential-provider stub used by tests exposes only call counts; it never reads environment values.

### 20.4 Atomic evidence output

Evidence is written first to `/tmp/proofstudio-ps041e2-live-evidence/.partial-<evidence_run_id>/` and atomically renamed to `/tmp/proofstudio-ps041e2-live-evidence/<evidence_run_id>/` as the last operation of a successful run. The output root is confined to exactly `/tmp/proofstudio-ps041e2-live-evidence` for real execution; the validator rejects symlink bases and symlink components, requires the resolved parent under `/tmp`, refuses an existing final run directory, and refuses a pre-existing partial directory rather than recursively deleting an unverified caller-controlled path. The atomic rename happens only after the 13-step finalization order completes, including the initial classified scan, the strict final scan over all exact finalized bytes, and the all-20-files-present verification. No evidence file is modified after the final scan. On failure no success summary is written; the in-memory `LiveExecuteReport.errors` list returns the stable error code; regular partial files are best-effort overwritten before logical unlink and directory removal, leaving no payload at the controlled evidence path without claiming physical-media erasure; no payload-bearing quarantine, object bytes, raw exceptions, or credential state are retained there.

### 20.5 Accepted-state live run boundary

Phase-1 implements and validates the executor. The actual accepted-state live run is a separate PM-approved operation that requires the PS-041E2-B implementation commit to be officially accepted such that local HEAD equals the current remote `refs/heads/accepted/proofstudio`. Until then, every `--execute` invocation fails closed at gate 21.

## 21. PS-041E2-B Phase-1 truth boundary

ProofStudio proves what the pipeline recorded. Proof does not equal truth. Phase-1 does not perform any live B2 access. No claim is made that live B2 execution has occurred.
