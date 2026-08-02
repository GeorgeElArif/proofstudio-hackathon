# PS-035a — Genblaze Manifest Correctness with Exact Published Pins

Status: Implemented (pending commit / acceptance).
Slice: PS-035a — Genblaze Manifest Verification / Golden-Run Manifest
Correctness (the requested v0.4.0 target was probed unavailable; this proof
uses the published-pin fallback and does not claim v0.4.0).
Date: 2026-07-01

> Note on naming: the branch and this proof file retain `v040` as historical
> planning language. The implemented proof is named truthfully below: it is
> **Genblaze manifest correctness with exact published pins**, not a v0.4.0
> proof. The requested target version was v0.4.0; that version was probed
> unavailable on the configured index at implementation time, so the
> published-version fallback was used and named honestly.

## 1. Files Changed

PS-035a touched only these files (all within the spec's recommended
implementation scope):

- `apps/api/requirements.txt` — Genblaze lines pinned to exact published versions.
- `docs/evidence/ps-035a/manifest-fixture.json` — new checked-in local manifest fixture.
- `docs/evidence/demo/golden-demo-run.json` — manifest fields filled with real evidence.
- `scripts/ps024_golden_demo_run_pinning_smoke.py` — migrated from the null-manifest contract to the real-manifest contract.
- `scripts/ps035a_genblaze_manifest_correctness_smoke.py` — new local/static PS-035a smoke.
- `docs/evidence/ps-035a/genblaze-manifest-correctness-report.json` — new PS-035a evidence report.
- `docs/ps-035a-genblaze-v040-manifest-correctness-proof.md` — this proof doc.
- `docs/validation/proofstudio-smoke-harness-v1.md` — append-only PS-035a note.
- `specs/07-master-spec-plan.md` — PS-035a status note (no PS-034A/PS-034B validation lines disturbed).
- `specs/08-roadmap-slices.md` — PS-035a status note.

No product UI, backend source, deployment config, `.env*`, central regression
gate, shared smoke library, PS-021 smoke, or prior-slice evidence was changed.
No `src/**` edit was needed (the fallback pins are API-compatible with the
existing `src/proofstudio/provenance/genblaze_store.py` integration).

## 2. Selected Version Path

**Selected path: published-version fallback** (not the primary v0.4.0 path).

A fresh package availability probe ran at implementation time:

```
python -m pip index versions genblaze-core
python -m pip index versions genblaze-s3
python -m pip index versions genblaze-gmicloud
```

The probe results on the configured index:

| Package             | Latest visible | v0.4.0 visible (probed unavailable)? |
|---------------------|----------------|-----------------|
| `genblaze-core`     | 0.3.4          | no              |
| `genblaze-s3`       | 0.3.4          | no              |
| `genblaze-gmicloud` | 0.3.2          | no              |

## 3. Why v0.4.0 Was Not Used

The requested target version was v0.4.0. Per the two-path dependency pin
contract (PS-035a spec section 12), the primary v0.4.0 path is usable only
when all three Genblaze packages are available, installable, and API-compatible
at implementation time. v0.4.0 was probed unavailable for all three packages on
the configured index, so the primary path could not be used truthfully. PS-035a
must not claim v0.4.0 verification unless v0.4.0 is actually published,
installed, and used, so the published-version fallback was selected and named
honestly as "Genblaze manifest correctness with exact published pins".

## 4. Exact Pinned Versions

`apps/api/requirements.txt` now pins the Genblaze packages to exact published
versions (no bare, unpinned package names remain):

- `genblaze-core==0.3.4`
- `genblaze-s3==0.3.4`
- `genblaze-gmicloud==0.3.2`

## 5. Installed Versions

The selected pins were installed into the project venv and verified with
`importlib.metadata.version(...)`:

| Package             | Pinned | Installed |
|---------------------|--------|-----------|
| `genblaze-core`     | 0.3.4  | 0.3.4     |
| `genblaze-s3`       | 0.3.4  | 0.3.4     |
| `genblaze-gmicloud` | 0.3.2  | 0.3.2     |

Installed versions match the chosen pins exactly. The existing
`src/proofstudio/provenance/genblaze_store.py` integration imports cleanly
against the fallback pins (`Asset`, `Pipeline.ingest`, `ObjectStorageSink`,
`S3StorageBackend`), so the fallback pins are API-compatible and no `src/**`
patch was required.

## 6. Manifest Fixture Source

The manifest fixture is a **checked-in local repo-relative file**:

`docs/evidence/ps-035a/manifest-fixture.json`

It is hand-authored and deterministic. It records the canonical golden-run
identity (run id, campaign id, archive SHA-256), the selected published-version
fallback pins, the installed versions, the local source scope, and the truth
boundary. The fixture is not produced by a live B2 upload. There is no live B2
manifest storage, no live Genblaze run, and no fake public B2 URL. The manifest
URI recorded on the golden run is the checked-in local fixture path, made
explicit so no artifact implies live B2 manifest storage.

## 7. Golden-Run Fields Updated

`docs/evidence/demo/golden-demo-run.json` was updated to carry real manifest
evidence while preserving every golden identity field:

Preserved unchanged:

- `run_id` = `run_89d967f9000045efa22ed4cc78cfa67f`
- `campaign_id` = `camp_bea5161faa6244079d2ee01ce445c259`
- `archive_uri`
- `archive_sha256` = `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
- existing rehydrate/provider-call truth fields

Added / updated:

- `manifest_uri` = `docs/evidence/ps-035a/manifest-fixture.json` (checked-in local fixture path)
- `manifest_hash` = `438fabca46481a232373067eedb6d0e3a684c8ed513410dfe2047e3b4950022f`
- `manifest_sha256` = same 64-hex value (matches `manifest_hash`)
- `manifest_source_scope` = `checked-in-local-fixture`
- `manifest_provenance_note` — states the fixture is local, not a live B2 URL
- `genblaze_versions` — exact package-to-version mapping actually installed

The stale `unavailable_fields` entries for `manifest_uri` and `manifest_hash`
were removed (those fields are no longer unavailable). The legitimately-null
`public_passport_url` and `proof_score` unavailable-field entries were
preserved; PS-035a does not overclaim live B2 manifest storage.

## 8. PS-024 Migration

`scripts/ps024_golden_demo_run_pinning_smoke.py` was migrated from the old
null-manifest contract to the real-manifest contract:

- Removed the old assertion that `manifest_uri` and `manifest_hash` are null.
- Added a new `manifest_contract` check requiring:
  - `manifest_uri` is a non-empty string
  - `manifest_hash` is 64-hex SHA-256
  - `manifest_sha256` (if present) is 64-hex and matches `manifest_hash`
  - the golden `genblaze_versions` match the exact requirements pins
  - the checked-in fixture bytes recompute to the golden `manifest_hash`
- Preserved all golden identity fields (run id, campaign id, archive SHA-256,
  rehydrate/provider-call truth fields, homepage honesty, route markers, etc.).

The PS-024 smoke remains local / check-only: no provider calls and no B2
reads/writes.

## 9. Hash Recompute Proof

The golden `manifest_hash` is the independent SHA-256 over the exact bytes of
the checked-in fixture file:

```
SHA-256(docs/evidence/ps-035a/manifest-fixture.json)
  = 438fabca46481a232373067eedb6d0e3a684c8ed513410dfe2047e3b4950022f
```

Both the PS-035a smoke and the PS-024 `manifest_contract` check recompute this
hash independently and require it to equal the golden `manifest_hash`. The
fixture hash is stable and deterministic (the fixture contains no volatile
field such as a timestamp).

## 10. No Live Provider / No Live B2 by Default

PS-035a is local / static only by default:

- no provider calls
- no live B2 read or write
- no broad B2 read
- no frontend build
- no backend server
- no central regression gate call

A live B2 upload or live Genblaze run would require later explicit PM approval
and is out of scope for this slice. The manifest fixture proves reproducible
local manifest-hash correctness only.

## 11. Truth Boundary

ProofStudio proves what the pipeline did. It does not prove semantic truth,
legal authenticity, C2PA authenticity, or human authorship. A checked-in
manifest fixture proves reproducible local manifest-hash correctness, not live
B2 Object Lock, not tamper-proof storage, and not semantic truth. No PS-035a
artifact implies live B2 manifest storage, Object Lock, tamper-proof storage,
or production security unless a later PM-approved slice actually performs a
live B2 upload and records it honestly.

## 12. Non-Goals

PS-035a did not:

- change product UI
- change the PS-028 manifest panel
- make provider calls
- do live B2 read/write by default
- do broad B2 reads
- implement Campaign Proof Room
- implement multimodal proof
- edit the central regression gate, shared smoke library, or PS-021 smoke
- invent a manifest URI or hash
- claim C2PA authenticity, human authorship, legal authenticity, Object Lock,
  tamper-proof storage, browser-side B2 byte verification, or production
  security
- claim v0.4.0 verification (v0.4.0 remains unavailable)

## 13. Validation Results

- `python -m py_compile` over both smoke scripts: clean.
- PS-035a smoke (`scripts/ps035a_genblaze_manifest_correctness_smoke.py`): PASS
  (report written to `docs/evidence/ps-035a/genblaze-manifest-correctness-report.json`).
- PS-024 smoke (`scripts/ps024_golden_demo_run_pinning_smoke.py --local --check-only`): PASS.
- No forbidden file changes; all changed files are within the allowed PS-035a set.
- No hidden Git index flags; `git diff --check` clean.

The PS-035a evidence report records `version_claim_truthful: true`,
`version_fallback_used: true`, and every required manifest-correctness field as
true.
