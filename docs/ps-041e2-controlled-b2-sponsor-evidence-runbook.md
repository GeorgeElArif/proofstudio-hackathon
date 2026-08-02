# PS-041E2 — Controlled B2 Sponsor Evidence Operator Runbook

This runbook tells the operator how to prepare and execute one controlled live-B2 sponsor evidence read. PS-041E2-B Phase-1 implements the live executor. The fake-backend tests and smokes perform zero live B2 access; the only path that may touch live B2 is the real CLI `--execute` mode after every gate has passed and only when the local HEAD equals the current remote `refs/heads/accepted/proofstudio`. Read this entire document before touching any credential.

## Hard rules

- Never paste credentials into chat, email, tickets, or commit messages.
- Never put credentials in Git. No `.env`, `.env.local`, `.env.save`, or real authorization JSON is committed.
- Never include credentials in the authorization JSON. The authorization schema (`proofstudio.ps041e2.b2_authorization.v1`) carries only non-secret controls. There is no credential field, account ID, application-key ID, secret, endpoint URL, or signed URL in the schema.
- Configure credentials only through the established local server-side environment mechanism (`B2_KEY_ID`, `B2_APP_KEY`, `B2_BUCKET`, `B2_REGION`). Never pass credentials through CLI arguments.
- Verify the application key is restricted to the intended bucket and prefix and read-only capability before starting.
- Remove or unset credentials immediately after execution. Verify no process, container, or temporary credential file remains.

## Accepted hard upper bounds (immutable)

The authorization may narrow but must never enlarge these limits. Excess values are rejected with stable codes; they are never silently clamped.

| cap | accepted maximum | rejection code when exceeded |
|---|---|---|
| `max_object_count` | 256 | `max_object_count_exceeds_accepted_limit` |
| `max_object_bytes` | 134_217_728 (128 MiB) | `max_object_bytes_exceeds_accepted_limit` |
| `max_total_bytes` | 536_870_912 (512 MiB) | `max_total_bytes_exceeds_accepted_limit` |

The accepted reader additionally enforces JSON objects at no more than 1 MiB regardless of a larger media-object authorization cap.

## Readiness validation (PS-041E2-A)

Run readiness checks before any live read:

```
PYTHONPATH=src python scripts/ps041e2_b2_evidence.py --check-readiness
```

Validate one authorization document:

```
PYTHONPATH=src python scripts/ps041e2_b2_evidence.py --validate-authorization /tmp/my-authorization.json
```

Run the fake-storage readiness smoke:

```
PYTHONPATH=src python scripts/ps041e2_b2_readiness_smoke.py
```

All three must succeed before any live read is considered.

## Authorization file path safety

The validator refuses to read credential-bearing files. Before any read it rejects:

- known environment-file basenames (`.env`, `.env.local`, `.env.save`, `.env.production`, `.env.development`, `.env.test`, `.env.staging`, `.env.example`, `credentials`, `credentials.json`);
- any basename that does not end in `.json`;
- symbolic links;
- non-regular files (directories, sockets, pipes);
- files exceeding the 64 KiB document bound.

The rejected path is never printed. Put the authorization document under an approved `/tmp` authorization directory, never at a repository path other than the exact committed template.

## Creating an authorization document

Copy the template:

```
cp docs/ps-041e2-b2-evidence-authorization-template.json /tmp/proofstudio-ps041e2-auth.json
```

Fill in the fields:

1. Set `authorized: true` only when a PM has approved the specific evidence run.
2. Set `authorized_by` to a canonical operator identity (nonempty, NFC, no surrounding whitespace).
3. Set `authorized_at` and `expires_at` (ISO 8601, UTC only — use `Z` or `+00:00`). The window between them must not exceed 24 hours. `authorized_at` must not be in the future beyond small clock skew.
4. Set `configured_alias` to the exact canonical server-configured `PROOFSTUDIO_IMPORT_BUCKET_ALIAS` value (do not paste the raw bucket name). The value must be byte-for-byte identical to the server alias; no whitespace stripping is applied.
5. Set `allowed_bucket_name_hash` to `sha256` of the controlled bucket name (64 lowercase hex). The validator compares this hash against the SHA-256 of the independently resolved server bucket name; the raw bucket name is never printed.
6. Set `allowed_prefix` to the exact canonical bounded prefix containing only the evidence objects (for example `proofstudio-hackathon/ps041e2/<evidence-run-id>`). The prefix must be canonical: no leading or trailing slash, no surrounding whitespace, no `..`, no backslash, no query, no fragment, no URL syntax, no control characters, NFC. The validator does not normalize the value — it must already be canonical.
7. Set `allowed_keys` to the exact object keys to be read. Every key must be inside the prefix. Every item must be a string. No `..`, no leading slash, no query, no fragment, no scheme, no controls.
8. Set `object_role_by_key` to an explicit map of each exact allowlisted key to exactly one known role. The key set must exactly equal `allowed_keys`. Each of the five required readiness roles (`stage_a_storyboard`, `stage_b0_manifest`, `stage_b1_manifest`, `stage_b2_manifest`, `final_delivery`) must appear exactly once. No duplicate roles. Role resolution uses this map only — never allowlist order, never a loose suffix match.
9. Set `max_object_count`, `max_object_bytes`, and `max_total_bytes` to explicit positive caps within the accepted hard upper bounds above.
10. Set `allow_metadata_reads: true`. Set `allow_json_object_reads: true` (the readiness flow requires both). Leave `allow_media_byte_reads` and `allow_sha256_verification` as needed.
11. If `allow_sha256_verification: true`, populate `expected_sha256_by_key` with at least one entry mapping an exact allowlisted key to its 64-char lowercase hex SHA-256. If `allow_sha256_verification: false`, `expected_sha256_by_key` must be empty. An expected digest for a media key requires `allow_media_byte_reads: true`.
12. Every denied capability (`allow_write`, `allow_delete`, `allow_signed_urls`, `allow_provider_calls`) must remain `false`.
13. Keep `purpose` exactly `PS-041E2 controlled sponsor evidence`.

Validate the filled document before proceeding:

```
PYTHONPATH=src python scripts/ps041e2_b2_evidence.py --validate-authorization /tmp/proofstudio-ps041e2-auth.json
```

## Read-permission flags honored before backend access

The readiness flow fails closed before any backend operation unless the required permissions are enabled. Setting any of these to `false` does not silently downgrade the run; it aborts before any head, read, or `build_candidate` call.

- `allow_metadata_reads=false` → zero head calls, aborts with `metadata_reads_required`.
- `allow_json_object_reads=false` → zero JSON reads, aborts with `json_reads_required`.
- `allow_media_byte_reads=false` → zero media byte reads.

## Hash evidence semantics

A newly calculated digest is never labeled `verified`. When `allow_sha256_verification=true`, the flow compares each object digest against its `expected_sha256_by_key` entry:

- exact match records `matched`;
- mismatch records `mismatch` and aborts with `unexpected_hash_mismatch`;
- keys without an expected digest record `observed` (JSON) or `computed` (media).

Every expected digest must be consumed by an actual read; an unconsumed expected digest rejects. An expected digest for a media key requires `allow_media_byte_reads: true`. The digest labelled `matched` is the digest of the exact bytes parsed into the snapshot that the candidate consumed. A computed digest alone is not verification. Media bytes are never included in evidence output.

## Validated snapshot reuse

Each authorized JSON object is read exactly once through the accepted `BoundedB2ImportReader`. The validated parsed snapshot is retained and deep-copied for both the candidate and the idempotency reconstruction. Zero extra backend reads occur during candidate or idempotency construction. The guarded candidate reader asserts the key is authorized and was validated, returns a deep copy, and counts consumer calls separately from backend reads.

## Actual backend operation counters

The readiness flow reports counters derived directly from the instrumented backend: `head_calls_total`, `read_calls_total`, `unique_json_objects_read`, `unique_media_objects_read`, `snapshot_consumer_calls`, `list_calls`, `write_attempts`, `delete_attempts`, `signed_url_attempts`, and `total_bytes_read`. The default five-object readiness run reports four unique JSON objects, zero media reads, and exactly four backend read operations after snapshot caching. A unique-object count is never labelled as the number of backend read operations.

## Execute mode (PS-041E2-B Phase-1: implemented; fail-closed unless local HEAD == current remote refs/heads/accepted/proofstudio)

PS-041E2-B Phase-1 implements the live execute layer. The `--execute <authorization-path>` CLI mode additionally requires `--confirm-controlled-live-read`. Without that exact flag the executor fails before any client construction. It also requires:

- repository branch is the PS-041E2-B implementation branch (`ps-041e2b/authorized-read-only-b2-evidence-run-v1`) or a detached HEAD;
- working tree clean;
- local HEAD equals `authorization.execution_commit`;
- local HEAD equals the local `origin/accepted/proofstudio`;
- local HEAD equals the **current remote** `refs/heads/accepted/proofstudio` (resolved via a bounded `git ls-remote`; fail-closed when the remote cannot be reached);
- authorization file under the approved `/tmp/proofstudio-ps041e2-authorizations/` directory;
- evidence output directory is confined to exactly `/tmp/proofstudio-ps041e2-live-evidence` (the CLI accepts `--evidence-out` for backward compatibility but ignores it for execute mode and always uses the confined root);
- explicit server-side B2 configuration is present (canonical alias, import root, bucket identity, region — no implicit `configured-import` default);
- the authorized `allowed_prefix` byte-for-byte equals the independently configured `PROOFSTUDIO_IMPORT_ROOT`;
- alias matches independently configured alias;
- bucket hash matches independently configured bucket name;
- exact prefix and object plan;
- all 22 gates pass.

For the actual accepted-state live run, the PS-041E2-B implementation commit must already be officially accepted (local HEAD must equal the current remote `refs/heads/accepted/proofstudio`). No live execution is allowed from an unaccepted feature commit, and no live execution is allowed when the local `origin/accepted/proofstudio` ref is stale relative to the remote. From any feature branch the executor fails closed at gate 21 with exit code 2 before any client construction.

### True key-only environment-access boundary

The real CLI execute path constructs an injectable `EnvAccessBoundary` (`RealEnvAccessBoundary`) before any pre-gate check runs. The boundary snapshots `os.environ.keys()` once at construction time and exposes three methods: `read_non_secret(name)` (for the four non-secret configuration fields), `secret_name_present(name)` (KEY-MEMBERSHIP only; inspects the snapshot and never invokes `get` / `__getitem__` for `B2_KEY_ID` / `B2_APP_KEY`), and `read_secret_after_gates(name)` (raises `secret_value_read_before_gate_completion` until the executor calls `mark_gates_completed` immediately after gate 22). The boundary does NOT monkeypatch `os._Environ` globally. The previous `EnvAccessSpy` monkeypatch approach — whose patched `__contains__` invoked the original `__getitem__`, silently materializing secret values while hiding the access — has been removed.

The `CredentialProvider` is the only component permitted to read secret values; it reads them via `read_secret_after_gates`. No B2 credential value is read before every authorization and Git binding check passes. No B2 client is constructed before all 22 gates pass.

The pre-gate server-config resolver uses KEY-MEMBERSHIP checks only via `secret_name_present`. The four explicit configuration fields (`PROOFSTUDIO_IMPORT_BUCKET_ALIAS`, `PROOFSTUDIO_IMPORT_ROOT`, `B2_BUCKET`, `B2_REGION`) are non-secret and may be read pre-gate. There is no implicit default for any of them; missing any of the four rejects at gate 17 with `server_side_configuration_missing` before credential retrieval or backend construction.

### Corrected network boundary

Gates 1–20 are pure and non-networking. Gate 21 performs exactly one bounded `git ls-remote` lookup of the current `refs/heads/accepted/proofstudio`. Tests inject the remote resolver and perform no network. The future live run performs Git remote binding before B2 credential access.

### Atomic finalization (12-step order)

The final run directory does not exist until every success artifact is complete. The executor performs the following exact order:

1. create a validated partial directory (rejects pre-existing final, rejects pre-existing partial rather than recursively deleting an unverified caller-controlled path, rejects symlink bases, requires the resolved parent under `/tmp`);
2. write every provisional evidence artifact (with `cleanup_verified=false`);
3. destroy the backend/client and release credential references;
4. complete `cleanup-verification.txt` (never rewritten after this step);
5. run the initial classified security scan over the partial directory;
6. write `classified-security-scan.txt` and `known-limitations.txt`;
7. set `cleanup_verified=true` on the in-memory report;
8. rewrite `authorization-summary.json` and `execution-summary.json` with `cleanup_verified=true`;
9. verify all `LIVE_EVIDENCE_FILES` exist and are regular non-symlink files;
10. run the strict final security scan over all exact finalized bytes;
11. make no further file-content change;
12. retain the final scan result only in the in-memory `LiveExecuteReport`;
13. atomically rename partial to final as the last filesystem operation.

If any scan finds a real leak, the partial directory is best-effort overwritten and logically unlinked so no credential-bearing evidence is retained; no payload-bearing quarantine is ever retained. Physical media erasure is not claimed on SSD, copy-on-write or journaled filesystems — the overwrite is a logical best-effort step and does not guarantee the underlying storage medium has zeroed the bytes. An optional sanitized failure summary (stable error code only) may be written next to the removed partial directory.

### Real fail-closed security scan

The classified security scan detects real credential-bearing values, never just marker words. It scans every candidate evidence file for:

- exact credential values supplied only in-memory to the scan (object byte sentinels, raw bucket identity);
- credential assignments (`key=value` for credential-like field names with an 8+ char value);
- signed/presigned URL query parameters (`?X-Amz-`, `?Expires=`, `?Signature=`, `?X-Goog-`, Azure-style `?sv=`, etc.);
- Authorization / Bearer / AWS4-HMAC-SHA256 / Basic header values;
- credential-bearing database URLs (`scheme://user:pass@host`);
- unexpected `http://` or `https://` URLs;
- raw object-byte sentinels (the exact bytes served by B2);
- raw bucket identity.

The sensitive comparison values are NEVER serialized into the scan output; the report carries only file names, token names and per-category counts. Any real leak prevents atomic finalization: regular files in the partial directory are best-effort overwritten, then logically unlinked and the directory removed, so no payload remains at the controlled evidence path; no payload-bearing quarantine is retained, and physical erasure is not claimed. Every evidence file must be a regular non-symlink UTF-8 text file within documented per-file and aggregate byte caps; invalid UTF-8, unreadable files, short reads and oversized files prevent finalization with stable error codes (`evidence_file_invalid_utf8`, `evidence_file_unreadable`, `evidence_file_too_large`, `evidence_aggregate_too_large`).

### Cleanup on every path

After the credential provider has been called, every outcome destroys the backend, releases inner backend/client references and credential references, and best-effort overwrites regular partial files before logical unlink and directory removal. No payload remains at the controlled evidence path; no payload-bearing quarantine is retained, and physical media erasure is not claimed. An optional separately generated sanitized failure summary may contain only a stable error code. No raw object bytes are retained; no raw exception text, bucket name, endpoint, or object key escapes through the error channel. Failures from the credential provider, backend factory, client construction, HEAD, GET, fixture loading, candidate creation, import service, evidence writing, security scanning, and the final rename are all normalized to stable codes. Ordinary failures cannot broaden B2 access.

### Exact real-adapter counters

The controlled read path uses the accepted ``ExactKeyReadAdapter``
(``proofstudio.provenance.genblaze_store``) which wraps the pinned
``S3StorageBackend`` and issues ONLY low-level ``HeadObject`` and ranged
``GetObject`` calls through the boto3 client. It never runs the lazy
bucket-region preflight, so the controlled read produces exactly zero
``head_bucket`` calls and exactly zero regional probes. The
``GuardedLiveBackend`` adapter then enforces the corrected read contract:

- **true exact-key read path**: every head dispatches to the adapter's
  ``head_object`` and every bounded read to the adapter's ``get_range``;
  the lazy bucket-region preflight never runs (zero ``head_bucket``, zero
  regional probes);
- **no hidden HEAD inside ``read_bytes``**: the adapter reuses metadata from the immediately preceding counted ``head()``; if no preceding head exists the read rejects with ``backend_read_requires_preceding_head``;
- **no full-object GET fallback**: when the underlying backend has no native ``read_bytes`` (i.e. the accepted S3 backend or the S3-like test fake), the adapter requires a ``get_range`` method; absent ``get_range`` rejects with ``backend_get_range_unsupported`` before any byte is read;
- **exact byte length**: the returned byte length must equal the declared approved size carried by the preceding head; mismatches reject with ``media_length_mismatch``;
- **no fabricated version_id**: the head normalization never fabricates a ``version_id`` from ``storage_class`` or a constant; the pinned backend's absent version ID is represented as ``None``;
- **SDK versus HTTP counters**: SDK invocations are counted separately from
  actual HTTP attempts. A successful response contributes exactly ``1 +
  ResponseMetadata.RetryAttempts``; missing, negative, boolean or non-integer
  retry metadata rejects with a stable code;
- **strict ranged response**: ``ContentLength`` must equal the requested
  length and any ``ContentRange`` must match the exact requested interval.
  ``StreamingBody.read(n)`` is used only with a size, at most
  ``requested_length + 1`` bytes are collected, and the body is closed once
  in ``finally``. Short, oversized, read-failing, and close-failing responses
  reject with stable codes;
- **zero hidden operations**: ``head_bucket_http_attempts`` and
  ``regional_probe_http_attempts`` are always zero on the controlled path;
  ``list_calls``, ``write_attempts``, ``delete_attempts`` and
  ``signed_url_attempts`` are always zero.

### Underlying client close exactly once

The ``GuardedLiveBackend.destroy()`` method closes the underlying client
exactly once before clearing the inner reference:

- ``inner_close_attempted`` is True after the first ``destroy()``;
- ``inner_close_succeeded`` is True only when close succeeded;
- ``inner_close_call_count`` counts close attempts (1 after the first
  destroy, still 1 after a repeated idempotent destroy);
- a close failure raises ``AuthorizationError("backend_close_failed")``
  without exposing raw exception text — a close failure prevents final
  success-directory publication;
- every backend lacking ``close()`` rejects with
  ``backend_close_unsupported``; the accepted clientless fake exposes an
  explicit counting ``close()`` rather than relying on an implicit exception;
- ``cleanup_verified`` may be True only when ``inner_close_succeeded`` is
  True.

### Corrected secure-removal contract

The partial directory cleanup is best-effort logical removal: every
regular file is best-effort overwritten with zeros before unlinking, then
the directory tree is removed. No payload is retained at the controlled
evidence path. **Physical media erasure is not claimed** on SSD,
copy-on-write or journaled filesystems — wear leveling, copy-on-write
snapshots, journaling and deduplication may retain stale blocks that the
logical overwrite cannot reach.

### Truthful `live_b2_calls` semantics

`live_b2_calls` is zero for fake execution. For real execution it is the sum
of actual HTTP attempts, never the number of SDK invocations:

- fake execution: `live_b2_calls == 0`, `real_backend_factory_used == false`;
- real execution: ``live_b2_calls == head_object_http_attempts +
  ranged_get_object_http_attempts + head_bucket_http_attempts +
  regional_probe_http_attempts``. A zero-retry five-object plan is 18 HEAD
  SDK calls / 18 HEAD attempts and 4 GET SDK calls / 4 GET attempts, totaling
  22; retries increase only the attempt counts and total.

### Factory construction ownership

After raw backend construction, the factory always owns one closeable
resource. Ownership moves to the exact-key adapter only after adapter
construction succeeds, then to the returned guard only after wrapper
construction succeeds. Any intervening version, compatibility, adapter, or
wrapper failure closes the current owner exactly once; cleanup failure becomes
``backend_factory_cleanup_failed`` and raw exception text never escapes.

### Accepted import + readback service

The live run uses the accepted PS-041D `ProofStudioService` to:

1. construct the candidate from the validated snapshots via `build_candidate`;
2. import it through `ProofStudioService.import_genblaze_bundle` and capture the real created/idempotent result;
3. re-import through the same service and prove idempotency (`import_idempotent`);
4. retrieve the stored private lineage bundle through `ProofStudioService.get_imported_bundle`;
5. retrieve the portable Passport through `ProofStudioService.get_imported_passport`;
6. derive summaries from those retrieved results.

`import_created` is set from the actual import result, never hard-coded.

The 22 implemented live gates are the canonical constant `FUTURE_EXECUTE_GATES` in `scripts/ps041e2_b2_evidence.py` (`FUTURE_EXECUTE_GATES_COUNT = LIVE_EXECUTE_GATES_COUNT = 22`). The same constant is consumed by `_execute_gates()`, the `--check-readiness` summary, the `--execute` mode stderr output, focused tests, the execute-readiness smoke, the spec, this runbook, the proof document, and the `execution-gates.json` evidence artifact. No separately maintained list may drift from this constant.

The implemented live execute mode requires all of the following (22 gates) before constructing a live storage client:

1. live authorization document exists and parses defensively under an approved `/tmp` authorization directory;
2. schema exact match;
3. `authorized=true`;
4. `authorized_by` is a nonempty canonical operator identity;
5. authorization not expired and within the short maximum validity window;
6. exact configured alias match against the independently resolved server alias;
7. exact bucket identity match against the SHA-256 of the independently resolved server bucket;
8. exact canonical prefix match against the independently configured import root (byte-for-byte equality, no normalization);
9. exact object allowlist (count and byte caps > 0 and within accepted upper bounds);
10. explicit object-role plan (key set equals `allowed_keys`, required roles exactly once, no reserved roles);
11. metadata reads allowed;
12. JSON reads allowed;
13. `write=false`;
14. `delete=false`;
15. signed URLs `false`;
16. provider calls `false`;
17. required server-side B2 configuration present (canonical alias, import root, bucket identity, region all nonempty AND the secret credential env vars present via membership-only check; checked without printing values);
18. no credential passed through CLI arguments;
19. no credential stored in authorization JSON;
20. repository tree clean;
21. branch and HEAD match the accepted PS-041E2 execution commit AND the current remote `refs/heads/accepted/proofstudio`;
22. `--confirm-controlled-live-read` flag present.

## Execute-readiness smoke (PS-041E2-B Phase-1)

Run the fake-backend execute-readiness smoke to confirm every implemented live gate and the 32-step operation order:

```
PYTHONPATH=src python scripts/ps041e2_b2_execute_readiness_smoke.py
```

This smoke injects a `FakeB2Backend`-returning backend factory and a fake git/server/credential provider. It never constructs a real `S3StorageBackend.for_backblaze` client, never reads credential values, and never accesses the network. It reports the exact backend operation counters, including `head_calls_total`, `read_calls_total`, `list_calls` (zero), `write_attempts` (zero), `delete_attempts` (zero), `signed_url_attempts` (zero), and `provider_calls` (zero).

## Head-metadata caps enforced before any byte read (PS-041E2-A v2)

The initial exact-key observation is a metadata preflight. For every allowlisted object, before any byte read, the readiness flow enforces:

- the metadata returned by `head()` is a mapping (`object_metadata_invalid`);
- `size_bytes` is an integer, excluding `bool` (`object_size_invalid`);
- `size_bytes >= 0` (`object_size_invalid`);
- `size_bytes <= min(max_object_bytes, ACCEPTED_MAX_MEDIA_OBJECT_BYTES)` (`object_exceeds_authorization_cap` / `object_exceeds_accepted_cap`);
- the sum of declared sizes is `<= min(max_total_bytes, ACCEPTED_MAX_AGGREGATE_BYTES)` (`declared_inventory_exceeds_authorization_total` / `declared_inventory_exceeds_accepted_total`).

These caps apply even when `allow_media_byte_reads=false`. An oversized declared final delivery still rejects during the metadata preflight. No silent clamping is ever performed. Any preflight failure aborts before any byte read.

## Normalized media/backend failures

`_bounded_asset_read` normalizes every failure to a stable `AuthorizationError` code. No raw exception text, path, bucket name, or object key ever escapes through the error channel. The stable codes are: `object_metadata_invalid`, `object_size_invalid`, `object_exceeds_authorization_cap`, `object_exceeds_accepted_cap`, `backend_head_failed`, `backend_read_failed`, `backend_response_not_bytes`, `approved_object_disappeared_after_read`, `media_length_mismatch`, `media_object_exceeds_approved_limit`, `object_changed_during_evidence_run`.

## Sanitized evidence output

The later live run may output only sanitized files under `/tmp/proofstudio-ps041e2-live-evidence/`. Never include credentials, application key IDs, secrets, raw authorization headers, endpoint URLs, signed URLs, raw bucket names, raw authorization file paths, raw provider prompts, personal data, production data, arbitrary object bytes, unredacted exception objects, or media bytes. Only hashes and bounded metadata may be retained.

## Rollback / abort

At any abort condition the validator exits nonzero before constructing a live storage client. No partial evidence is written. Remove the temporary authorization document from `/tmp` and unset any credential from the execution environment. The repository is not mutated.

## Truth boundary

ProofStudio proves what the pipeline recorded. Proof does not equal truth. The evidence must not claim universal authenticity, verified truth, legal ownership, human authorship, immutable storage, Object Lock (unless separately proven), tamper-proof storage, production compliance, complete evidence, universal byte verification, or public disclosure readiness.
