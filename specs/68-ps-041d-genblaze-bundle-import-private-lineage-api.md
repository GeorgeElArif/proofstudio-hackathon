# PS-041D — Genblaze Bundle Import + Private Lineage API

Status: implementation slice. Backend only. Accepted base: `origin/accepted/proofstudio` at `78ee403f9da01571e5ebe88c96c7ee0635f54cf3`.

## 1. Pinned compatibility contract

The only official source contract is `backblaze-labs/genblaze-gen-media-multi-provider-sample` commit `2e31577b7a9d5a7b0309d814f2d0282088b33fe8`, MIT, copyright 2026 Backblaze, Inc. Parsing targets `genblaze-core==0.3.4`, storage abstraction compatibility targets `genblaze-s3==0.3.4`, the pipeline slug is `genblaze-gen-media-multi-provider-sample`, and supported imported Manifests are schema 1.5. Provider packages are neither required nor loaded.

The fixed stages are:

- A: standalone `chat()` result manually stored as storyboard JSON. It has no Genblaze Run, Manifest, recorded hash, or durable A→B relation.
- B0: separate Pipeline Run and reference-image lineage root.
- B1: separate Pipeline Run whose `run.parent_run_id` records B0. Scene association is positional/inferred.
- B2: separate Pipeline Run whose one `run.parent_run_id` records B1. Scene grouping is positional/inferred. External inputs may have expiring signed transport URLs and may omit SHA-256.
- C: external ffmpeg composition, never a Run. The B2 Manifest may be embedded best-effort, with no composition sidecar. The final object convention is `explainers/<b2-run-id>/final.mp4`.

Manifest 1.5 records `parent_run_id` but excludes it from the canonical manifest hash. Every normalized parent edge therefore has `evidence_class=recorded` and `hash_covered=false`.

## 2. Authority and trust boundary

Auth Postgres continues to own identity, sessions, and account↔campaign access only. FastAPI owns imported proof. Import is a server/operator mutation, while readback uses PS-041C authorization: authenticated account, active campaign mapping, and exact FastAPI campaign scope. Provider, model, source ID, parent ID, and B2 key are evidence, never authorization.

`PROOFSTUDIO_IMPORT_OPERATOR_TOKEN` is separate from `PROOFSTUDIO_INTERNAL_SERVICE_TOKEN`. The operator token uses `X-ProofStudio-Import-Token`, is at least 24 characters, rejects surrounding whitespace and placeholders, compares in constant time, fails closed, and never appears in readiness or browser gateway configuration. Production must inject it using server secret management. It creates no Auth Postgres column or migration.

ProofStudio reports what the imported pipeline record states. It does not establish truth, legal authenticity, human authorship, quality, or remote-byte integrity unless a byte check is explicitly recorded.

## 3. Canonical bundle index

The sole envelope is `proofstudio.genblaze_bundle.v1`:

```json
{
  "bundle_schema": "proofstudio.genblaze_bundle.v1",
  "source_type": "genblaze_multi_provider_sample",
  "source_slug": "genblaze-gen-media-multi-provider-sample",
  "source_revision": "2e31577b7a9d5a7b0309d814f2d0282088b33fe8",
  "objects": [],
  "relationships": []
}
```

Object roles are `stage_a_storyboard`, `stage_b0_manifest`, `stage_b1_manifest`, `stage_b2_manifest`, `stage_c_composition`, `final_delivery`, and `embedded_manifest`. A present descriptor contains exactly one controlled content source: sanitized inline JSON or a server-resolved `B2ObjectReference`. A descriptor may instead explicitly record missing evidence. Credentials, authorization headers, cookies, keys, session tokens, archives, local absolute paths, arbitrary fetch URLs, and browser bucket authority are forbidden.

Relationships contain controlled kind, source, target or missing-source identity, `recorded|inferred`, optional bounded locator/limitation, and hash coverage. The adapter never upgrades inferred evidence.

## 4. Bounds and parsing

- Bundle index: 1 MiB.
- Storyboard or individual Manifest JSON: 1 MiB.
- Aggregate parsed JSON: 16 MiB.
- Object descriptors: 256.
- Relationships: 64.
- Nesting: 32.
- General string: 8 KiB.
- Provider/model/source ID: 256 characters.
- Caption/notice: 4 KiB.

Before normalization the boundary rejects invalid UTF-8, duplicate JSON keys, non-NFC/control-bearing strings, depth and count overflow, unknown envelope schema/fields, and compression/archive input. Stable error codes do not reflect bodies or internal state.

## 5. Normalized model

Campaign is mandatory scope on every record and is not a node. Node kinds are exactly `import_bundle`, `standalone_artifact`, `genblaze_run`, `manifest`, `asset`, and `external_composition`. Steps remain bounded, ordered summaries nested under `genblaze_run` and are not graph nodes.

Edge kinds are exactly `parent_run`, `generated_asset`, `external_input`, `storyboard_for`, `scene_member`, `composition_input`, `composed_output`, `manifest_for`, and `embedded_manifest`. Edges carry deterministic ID, campaign, bundle, kind, source, target or missing source, recorded/inferred class, `hash_covered`, check outcome, locator, and bounded limitations. Unknown parents remain dangling recorded edges; no node is fabricated.

Allowed endpoint-kind pairs are validated. V1 rejects self-parenting, cycles, duplicate edges/source IDs, cross-campaign edges, and multiple parents. Display ordering is deterministic. It never infers lineage from timestamp, provider/model match, prefix, or ID resemblance. Positional scene links require the bundle’s explicit convention.

## 6. Defensive Genblaze adapter

The adapter delegates only recognized Manifest parsing to installed `genblaze_core.models.manifest.parse_manifest`. It accepts only 1.5, preserves bounded provider/model and ordered step summaries, discards raw prompts/provider payloads/Manifest JSON, and never dynamically imports or executes provider values. Manifest checks distinguish canonical hash equality from declared output hashes; neither fetches remote assets.

Stage A becomes `standalone_artifact`; B0/B1/B2 become distinct `genblaze_run` nodes plus Manifest observations; C becomes `external_composition`. Recorded Manifest parents create non-hash-covered edges. Output assets contain safe metadata only. Composition and embedded-manifest claims exist only when descriptors record them; missing evidence remains missing/not checked.

## 7. URL and B2 policy

Imported URL fields reject userinfo, query strings, fragments, unsupported schemes, and loopback/private/link-local/metadata hosts. No URL is fetched, logged, returned, or fingerprinted. Signed transport URLs are rejected at the boundary rather than retained as identity.

Durable B2 references are `{backend:"b2_s3", bucket_alias, object_key, version_id?, size_bytes?, content_type?, etag?, sha256?, uploaded_at?, source_prefix?, manifest_hash?}`. The alias is server configured. Keys are NFC relative paths under an allowlisted root, with no leading slash, backslash, `..`, scheme, query, fragment, or controls. ETag is opaque and never labeled SHA-256.

The optional B2 reader is disabled by default and accepts an injected `genblaze-s3`-compatible backend. It supports only bounded list under one root, head, JSON get, and optional byte hash verification. It uses head-before-get and optional head-after-get consistency observation, list/JSON/asset/aggregate byte caps, and no signed URL. Every returned JSON object is then subjected to the same depth, string, NFC, control-character, credential-field, URL, aggregate-size, and role-specific strict parsing boundary as inline JSON. Tests use a fake backend; standard validation performs no live B2 operation and imports no boto3 directly. V1 exposes no reader timeout setting because the injected backend contract cannot enforce one.

## 8. Checks and truth vocabulary

The safe outcomes are `recorded`, `parsed`, `hash_present`, `hash_verified`, `hash_mismatch`, `manifest_hash_verified`, `manifest_output_hashes_declared`, `manifest_invalid`, `object_missing`, `relationship_recorded`, `relationship_inferred`, `unsupported_schema`, `partial_bundle`, `unavailable`, and `not_checked`.

`manifest_hash_verified` means canonical payload equality under supported schema only, and does not mean the Genblaze hash covers `parent_run_id`. `hash_verified` requires checked bytes. `hash_present` reports a stated digest only. A storage reference without a read is recorded reference evidence only. Composition notices are workflow records, not guarantees.

## 9. Fingerprint, idempotency, conflict, atomicity

`ps041d.fingerprint.v1` hashes normalized source type/slug, object role/source ID/importer-computed content fingerprint, normalized B2 key/version, and sorted relationship kind/from/to/evidence. Inline and read JSON use deterministic canonical sanitized JSON fingerprints computed by ProofStudio. Descriptor `content_fingerprint` values describe normalized content only. For recognized Genblaze Manifests, the Run and Manifest node `content_fingerprint` is the normalized Manifest content fingerprint and includes recorded `run.parent_run_id` because Manifest 1.5 excludes it from the canonical Manifest hash. A verified Genblaze canonical hash remains safe evidence and a `manifest_hash_verified` check, but is not the sole Run/Manifest content fingerprint. If a Manifest canonical hash is absent or mismatched, importer-computed normalized content remains authoritative and the mismatch remains distinct. A descriptor `content_sha256` is recorded evidence only, never verified unless bytes are actually checked, and never affects canonical bundle identity, bundle ID, node IDs, edge IDs, or normalized content identity; changing only that unchecked declaration is an idempotent no-op, while changing normalized content with the same upstream ID is a safe 409 conflict. Metadata-only B2 references use normalized key/version identity and make no byte-verification claim. It excludes campaign, import time, object/relationship ordering, transport/signed URLs, prompts, and importer diagnostics. Node/edge/bundle IDs are deterministic SHA-256-derived IDs; no import UUID is used.

The store uniquely binds fingerprint→campaign and indexes every normalized external descriptor, Genblaze Run, generated Asset, and other supplied node identity as typed `(source_type, source_id) → (source_conflict_fingerprint, campaign_id)` evidence. The descriptor source-conflict fingerprint is `sha256_json({"role": role, "normalized_content_fingerprint": descriptor_content_fingerprint})`, stored under `("object", source_id)`. The Run source-conflict fingerprint is `sha256_json({"stage": stage, "normalized_manifest_fingerprint": manifest_content_fingerprint})`, stored under `("genblaze_run", run_id)`. Roles and stages are not added to the key; they are bound inside the indexed value. Therefore one source ID cannot silently change semantic descriptor role, and one Run ID cannot silently change B0/B1/B2 stage, even when normalized content is otherwise identical. The importer-generated synthetic bundle source string is excluded. Exact and reordered re-import are readback no-ops. Same typed source/content/classification/campaign is allowed; same source ID with different role, same Run ID with different stage, same Run ID with contradictory recorded parent lineage, same typed source/different content, typed source/other campaign, same fingerprint/other campaign, golden namespace collision, and cross-campaign mutation are safe 409 conflicts. Explicitly missing but internally consistent evidence may commit as `partial_bundle`. Parse/read/validation failure commits nothing, and cleanup removes all typed source bindings for its campaign.

The candidate is fully built outside one `RLock`. Inside the lock the store rechecks campaign, source conflicts, campaign binding, golden namespace, and campaign boundaries; builds copy-on-write dictionaries; then swaps all bundle/node/edge/index maps. Injected pre-commit failure exposes nothing and deterministic retry succeeds.

Atomicity, idempotency, and indexes are process-local. They do not survive restart and are not multi-worker safe. Production persistence is future work; this slice adds no database migration or graph database.

## 10. Private routes

Operator mutation:

- `POST /internal/operator/campaigns/{campaign_id}/genblaze-bundles`
- 201 create, 200 no-op, 400 malformed/limits, 401 operator auth, 404 missing campaign, 409 conflict, 413 size, 503 optional B2 unavailable.

PS-041C service-token reads:

- `GET /internal/campaigns/{campaign_id}/import-bundles`
- `GET /internal/campaigns/{campaign_id}/import-bundles/{bundle_id}`
- `GET /internal/campaigns/{campaign_id}/import-bundles/{bundle_id}/passport`

Auth-server real-session gateways:

- `GET /account/campaigns/{campaignId}/lineage`
- `GET /account/campaigns/{campaignId}/lineage/{bundleId}`
- `GET /account/campaigns/{campaignId}/lineage/{bundleId}/passport`

The gateway derives account identity from Better Auth, checks active `proof.read` mapping before calling FastAPI, allows owner/reviewer/viewer read, rejects caller identity and evidence query scopes, recursively bounds and exact-key-validates every bundle, node, edge, run/step summary, check, limitation, structured B2 reference, detail, and private Passport, contains redirects, and maps absent/revoked/cross-account to uniform 404 and dependency failures to safe 503. Nested enums, hashes, safe metadata, campaign/bundle scope, and detail node/edge membership must agree; any malformed nested value rejects the entire upstream response without returning a partial payload. It exposes no mutation.

## 11. Portable private Passport and public boundary

`proofstudio.portable_lineage_passport.v1` contains canonical campaign/bundle/fingerprint/source fields, deterministic normalized nodes and edges, recorded/inferred classes, safe Manifest checks/hashes, structured B2 references, final composition relationship, missing states, limitations, and the truth-boundary statement. It never contains raw upstream JSON, source prompts, signed URLs, credentials, or paths.

Imported Passports remain private. Existing exact-ID golden public Passport, publication, sharing, and golden surfaces are unchanged. Imported lookup never falls through to the fixture.

## 12. Validation and PS-041E handoff

The sanitized checked-in fixture is pinned-contract-derived, not production observation. Focused parser/service/fake-B2/route tests, current-slice smoke, and real-session auth smoke run with no provider and no live B2. Central regression remains non-mutating and PS-034A evidence must remain unchanged.

PS-041E owns dynamic lineage UI, visual evidence, screenshots, sponsor presentation, and any public presentation decision. PS-041D adds no web UI source.
