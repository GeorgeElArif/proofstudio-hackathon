# PS-035a — Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest Correctness

Status: Spec only.
Base branch: `ps-035a/genblaze-v040-manifest-correctness`
Date: 2026-07-01

## 1. Status

PS-035a is currently:

- Spec only.
- Implementation pending.

PS-035a must not be implemented, and no implementation files may be changed,
until this spec is accepted.

PS-035a is the next blocking implementation slice after PS-034C. PS-034C
declared PS-035a (Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest
Correctness) the next implementation slice after PS-034C unless the PM later
changed priority. The latest accepted slice is PS-034C commit `7af3c8f`.

This spec-only commit touches only this file:
`specs/47-ps-035a-genblaze-v040-manifest-correctness.md`. No implementation
files are changed during this phase.

## 2. Purpose

PS-035a closes the canonical golden-run Genblaze manifest correctness gap
before any downstream multimodal, Campaign Proof Room, or future proof
surface slices are built on top of it.

The canonical golden run currently carries `manifest_uri: null`,
`manifest_hash: null`, no `manifest_sha256`, and no `genblaze_version`. That
is a core provenance gap: the golden run cannot honestly claim Genblaze
manifest correctness while those fields are null.

PS-035a pins Genblaze to exact, available versions per the two-path
dependency pin contract (section 12), supplies a real, reproducible,
checked-in manifest fixture by default, recomputes the manifest SHA-256
independently, fills in the golden-run manifest fields with real evidence,
and migrates the PS-024 smoke from the old null-manifest contract to a
real-manifest contract.

After PS-035a, every downstream surface may rely on the golden run carrying
real manifest evidence instead of nulls.

## 3. Why PS-035a Exists

- PS-034C identified PS-035a as the next blocking correctness slice, because
  golden-run manifest correctness is core provenance and the current golden
  run has a manifest null gap.
- The canonical golden run currently has null manifest fields:
  `manifest_uri: null`, `manifest_hash: null`, no `manifest_sha256`, and no
  `genblaze_version`.
- Genblaze dependencies are unpinned. The current `apps/api/requirements.txt`
  pins nothing: the strings are bare `genblaze-core`, `genblaze-s3`, and
  `genblaze-gmicloud`.
- Current installed Genblaze packages in the venv are 0.3.x, not 0.4.0.
- PS-024 smoke currently enforces the old null-manifest contract on the
  golden run. Any migration to a real manifest contract must update that
  smoke in lockstep, otherwise the smoke and the golden evidence will
  contradict each other.
- ProofStudio must not build new proof surfaces on top of missing manifest
  evidence. The multimodal layer, Campaign Proof Room, and all future
  proof-passport work must read real manifest fields, not nulls.

PS-035a is the slice that closes that gap with real, reproducible, checked-in
manifest fixture evidence, without doing live B2 reads/writes by default and
without making live provider calls.

## 4. Current Discovery Facts

Canonical golden run (`docs/evidence/demo/golden-demo-run.json`) currently
records:

- run id: `run_89d967f9000045efa22ed4cc78cfa67f`
- campaign id: `camp_bea5161faa6244079d2ee01ce445c259`
- archive SHA-256: `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
- `manifest_uri: null`
- `manifest_hash: null`
- no `manifest_sha256`
- no `genblaze_version`

Dependency state:

- current `apps/api/requirements.txt` strings are bare `genblaze-core`,
  `genblaze-s3`, `genblaze-gmicloud` (unpinned)
- current venv discovered 0.3.x packages, not 0.4.0
- no Python lockfile exists

A real Genblaze integration already exists in
`src/proofstudio/provenance/genblaze_store.py`, so the manifest-correctness
work is integration plus evidence work, not a from-scratch provider build.

## 5. Package Availability Repair

A readiness probe for PS-035a checked the configured package index and found
Genblaze 0.4.0 unavailable. `pip index versions` showed the latest visible
versions as:

- `genblaze-core`: `0.3.4`
- `genblaze-s3`: `0.3.4`
- `genblaze-gmicloud`: `0.3.2`

No `0.4.0` was visible for any of the three packages. The currently
installed versions are `genblaze-core==0.3.2`, `genblaze-s3==0.3.2`, and
`genblaze-gmicloud==0.3.1`.

Because of this, PS-035a must not pin packages that are unavailable on the
configured index. PS-035a must not claim v0.4.0 verification unless v0.4.0 is
actually published, installed, and validated against the existing
`src/proofstudio/provenance/genblaze_store.py` integration.

The branch name `ps-035a/genblaze-v040-manifest-correctness` and this file
name `47-ps-035a-genblaze-v040-manifest-correctness.md` may retain `v040` as
historical planning language. The implemented proof language — requirements
pins, evidence report, golden-run fields, and proof doc — must reflect the
actual installed and pinned versions, not an assumed v0.4.0.

Accordingly, the dependency pin contract (section 12), the manifest
correctness contract (section 11), the PS-024 migration contract (section
13), the evidence model (section 14), the validation plan (section 15), and
the acceptance criteria (section 18) all follow a two-path, truth-first model
described below.

## 6. Scope

PS-035a implementation should:

1. Pin Genblaze dependency requirements to exact, available versions per the
   two-path dependency pin contract (section 12). Do not pin unavailable
   packages.
2. Create or check in a local manifest fixture by default
   (`docs/evidence/ps-035a/manifest-fixture.json` or equivalent checked-in
   fixture). The default path is local/checked-in. Live B2 upload or a live
   Genblaze run requires later explicit PM approval.
3. Require non-null `manifest_uri` on the canonical golden run.
4. Require non-null `manifest_hash` or `manifest_sha256` on the canonical
   golden run.
5. Require 64-hex SHA-256 format for `manifest_hash`/`manifest_sha256`.
6. Require the canonical golden run to record the exact Genblaze package
   versions actually used to produce/verify the checked-in manifest fixture,
   via a `genblaze_version` scalar or a `genblaze_versions` mapping. Do not
   record `"0.4.0"` unless v0.4.0 is actually installed and used.
7. Independently recompute SHA-256 over the checked-in manifest fixture bytes
   and require it to equal the golden-run `manifest_hash`/`manifest_sha256`.
8. Update the canonical golden run only with real, reproducible manifest
   fixture evidence. Do not invent a manifest URI or hash.
9. Update PS-024 smoke from the old null-manifest contract to the real-
   manifest contract (non-null fields, SHA-256 format, exact recorded
   Genblaze versions), preserving all other golden identity fields.
10. Add a PS-035a smoke (`scripts/ps035a_genblaze_manifest_correctness_smoke.py`)
    and a PS-035a evidence report
    (`docs/evidence/ps-035a/genblaze-manifest-correctness-report.json`).
11. Add a PS-035a proof doc
    (`docs/ps-035a-genblaze-v040-manifest-correctness-proof.md`) that names
    the work truthfully (e.g. "Genblaze manifest correctness with exact
    published pins" when the fallback path is used), not "v0.4.0 proof."
12. Preserve the truth boundary and avoid overclaims. A checked-in fixture
    proves reproducible local manifest-hash correctness, not live B2 Object
    Lock, not tamper-proof storage, and not semantic truth.

## 7. Non-goals

PS-035a must not:

- do not change product UI
- do not change the PS-028 manifest panel unless later explicitly approved
- do not make provider calls
- do not do live B2 read/write by default (no live B2 read/write by default)
- do not do broad B2 reads
- do not do live Genblaze/B2 upload unless explicitly PM-approved later
- do not implement Campaign Proof Room
- do not implement multimodal proof
- do not edit `scripts/proofstudio_regression_gate.py`
- do not edit `scripts/smoke_lib.py`
- do not edit PS-021 smoke unless later explicitly approved
- do not invent a manifest URI or hash
- do not claim C2PA authenticity, human authorship, legal authenticity,
  Object Lock, tamper-proof storage, browser-side B2 byte verification, or
  production security

PS-035a only edits the dependency pin, the canonical golden run, the PS-024
smoke, a PS-035a smoke, PS-035a evidence, a PS-035a proof doc, the smoke
harness doc note, the master spec plan, and the roadmap slices doc. Nothing
else.

## 8. Spec-only allowed file

This spec-only commit touches only:

- `specs/47-ps-035a-genblaze-v040-manifest-correctness.md`

No other files are changed during the spec-only phase.

## 9. Recommended implementation allowed files

The following are implementation-phase candidates, not for this spec-only
commit:

- `apps/api/requirements.txt`
- `docs/evidence/demo/golden-demo-run.json`
- `scripts/ps024_golden_demo_run_pinning_smoke.py`
- `scripts/ps035a_genblaze_manifest_correctness_smoke.py`
- `docs/evidence/ps-035a/genblaze-manifest-correctness-report.json`
- `docs/evidence/ps-035a/manifest-fixture.json` or equivalent checked-in fixture
- `docs/ps-035a-genblaze-v040-manifest-correctness-proof.md`
- `docs/validation/proofstudio-smoke-harness-v1.md` append-only PS-035a note
- `specs/07-master-spec-plan.md`
- `specs/08-roadmap-slices.md`

Any source helper edit under `src/**` must be PM-gated and allowed only if
the installed Genblaze API compatibility requires it.

## 10. Forbidden files unless explicitly PM-approved later

PS-035a implementation must not touch:

- `apps/web/**`
- `src/**`
- `workers/**`
- `packages/**`
- `render.yaml`
- `.env*`
- `scripts/proofstudio_regression_gate.py`
- `scripts/smoke_lib.py`
- `scripts/ps021_live_b2_durable_rehydrate_smoke.py`
- prior-slice evidence under `docs/evidence/ps-021`, `ps-024`, `ps-027`,
  `ps-028`, `ps-029`, `ps-034a`, `ps-034b`, `ps-034c`
- any historical evidence not explicitly whitelisted

## 11. Manifest correctness contract

The canonical golden run must eventually include:

- `manifest_uri`: non-empty string
- `manifest_hash`: 64-hex SHA-256 string, or `manifest_sha256`: 64-hex SHA-256
  string
- `genblaze_version` or `genblaze_versions`: the exact Genblaze package
  versions actually used to produce and verify the checked-in manifest
  fixture. This may be a scalar only when v0.4.0 is actually installed and
  used; otherwise it must be an exact package-to-version mapping for the
  chosen pin path, e.g. `{"genblaze-core": "0.3.4", "genblaze-s3": "0.3.4",
  "genblaze-gmicloud": "0.3.2"}` on the published-version fallback. It must
  never record a version that is not actually installed.
- source provenance for the manifest fixture (where the fixture came from,
  how it was produced, and whether or not it came from a live B2 upload)
- in-memory manifest verification result, if available
- stored manifest verification result, if available
- independent SHA-256 recompute over the checked-in fixture bytes, equal to
  the recorded golden `manifest_hash`/`manifest_sha256`

If the manifest fixture is not produced by a live B2 upload, the docs must
state that clearly. Do not imply live B2 manifest storage unless it actually
happened.

## 12. Dependency pin contract

PS-035a implementation must follow a two-path, truth-first dependency pin
contract in `apps/api/requirements.txt`. It must not pin packages that are
unavailable on the configured index.

Primary path (v0.4.0):

- Use `genblaze-core==0.4.0`, `genblaze-s3==0.4.0`,
  `genblaze-gmicloud==0.4.0` only if all three packages are available,
  installable, and API-compatible with the existing
  `src/proofstudio/provenance/genblaze_store.py` integration at
  implementation time.

Fallback path (published-version pins):

- If v0.4.0 remains unavailable, PS-035a may pin the latest published
  compatible versions visible in the readiness probe:
  - `genblaze-core==0.3.4`
  - `genblaze-s3==0.3.4`
  - `genblaze-gmicloud==0.3.2`
- Implementation must verify those exact installed versions with
  `importlib.metadata.version(...)` for each package, asserting each equals
  the pinned value.
- Implementation must document that this is the published-version fallback,
  not v0.4.0.
- Any proof/evidence/docs must call it "Genblaze manifest correctness with
  exact published pins" (or equivalent), not "v0.4.0 proof."

Stop condition:

- If the fallback pins fail to install or the API is incompatible with the
  existing integration, implementation must stop and report the exact
  blocker. Do not silently substitute a different version. A source helper
  edit under `src/**` to accommodate an API difference is only allowed with
  explicit PM approval (see section 9).

In both paths, all three Genblaze packages must be pinned to exact versions
(no bare, unpinned package names), and the installed versions must be
validated through `importlib.metadata.version(...)`.

## 13. PS-024 migration contract

The PS-024 smoke migration must:

- remove the old null-manifest assertion (the assertion that
  `manifest_uri` and `manifest_hash` are null)
- require real non-null manifest fields on the canonical golden run
- require SHA-256 64-hex format for `manifest_hash`/`manifest_sha256`
- require the exact recorded Genblaze package versions on the golden run to
  match the installed/pinned versions from the chosen dependency pin path
  (section 12)
- preserve all existing golden run identity fields (run id, campaign id,
  archive URI, archive SHA-256, etc.)
- preserve archive URI and archive SHA-256 unless the PM explicitly approves
  a new golden run
- do not mutate unrelated evidence

## 14. Evidence model

The PS-035a evidence report JSON
(`docs/evidence/ps-035a/genblaze-manifest-correctness-report.json`) should
include:

- `ok`
- `slice_id: ps035a`
- `checked_at`
- `target_version_requested`
- `target_version_available`
- `version_fallback_used`
- `pinned_genblaze_versions`
- `installed_genblaze_versions`
- `version_claim_truthful`
- `requirements_pinned`
- `golden_run_id_preserved`
- `golden_campaign_id_preserved`
- `archive_sha256_preserved`
- `manifest_uri_non_null`
- `manifest_hash_non_null`
- `manifest_hash_sha256_format`
- `genblaze_versions_recorded`
- `manifest_fixture_present`
- `manifest_fixture_sha256_recomputed`
- `manifest_fixture_hash_matches_golden`
- `in_memory_manifest_verify`
- `stored_manifest_verify`
- `ps024_smoke_migrated`
- `no_live_provider_call`
- `no_broad_b2_read`
- `truth_boundary_preserved`
- `no_forbidden_overclaims`
- `no_forbidden_file_changes`
- `failures`

`target_version_requested` records the version PS-035a originally planned for
(`0.4.0`). `target_version_available` records whether `0.4.0` was visible on
the configured index at implementation time. `version_fallback_used` is true
when the published-version fallback pins were used instead of v0.4.0.
`pinned_genblaze_versions` and `installed_genblaze_versions` record the exact
package-to-version maps. `version_claim_truthful` is true only when no
artifact claims a Genblaze version that is not actually installed and used.

## 15. Required validation plan

PS-035a implementation must be validated with:

- a static required-string check over the spec/proof/docs
- a package availability check: `pip index versions` evidence (or a
  documented local equivalent) showing whether `0.4.0` is visible for all
  three Genblaze packages, recorded in the evidence report
- a requirements pin check for the chosen dependency pin path: either
  (`genblaze-core==0.4.0`, `genblaze-s3==0.4.0`, `genblaze-gmicloud==0.4.0`)
  on the primary path, or
  (`genblaze-core==0.3.4`, `genblaze-s3==0.3.4`, `genblaze-gmicloud==0.3.2`)
  on the fallback path
- an installed package version check with `importlib.metadata.version(...)`,
  asserting installed versions equal the pinned versions for the chosen path
- a proof-doc claim check: if the fallback path is used, the proof docs and
  evidence must not claim v0.4.0; `version_claim_truthful` must be true
- a golden-demo-run JSON schema check
- a SHA-256 64-hex check on `manifest_hash`/`manifest_sha256`
- an independent hash recompute over the manifest fixture bytes, equal to the
  recorded golden hash
- the PS-024 smoke pass (now migrated to the real-manifest contract)
- the PS-035a smoke pass
- a no-forbidden-file-changes check (none of section 10 may appear in the
  diff)
- no prior evidence mutation except the whitelisted golden-demo-run and the
  new PS-035a evidence
- the PS-034A smoke still passes (in safe local mode, no evidence mutation)
- the PS-034B smoke still passes (in safe local mode, no evidence mutation)
- a no-hidden-Git-flags check:
  ```
  git ls-files -v | grep -E '^[a-z]'
  ```
  must return nothing both before and after validation
- `git diff --check` returns clean

## 16. Truth boundary

ProofStudio proves what the pipeline did.

It does not prove semantic truth, legal authenticity, C2PA authenticity,
human authorship, Object Lock/tamper-proof storage, browser-side B2 byte
verification, or production security unless those are actually implemented.

A checked-in manifest fixture proves reproducible local manifest-hash
correctness, not live B2 Object Lock, not tamper-proof storage, and not
semantic truth.

PS-035a must preserve this boundary verbatim across the proof doc, evidence
report, golden run, and PS-024 smoke. No PS-035a artifact may imply live B2
manifest storage, Object Lock, or tamper-proof storage unless a later
PM-approved slice actually performs a live B2 upload and records it honestly.

## 17. Risks

PS-035a must record the following risks with mitigations:

- fake manifest proof
  - mitigation: require a checked-in fixture, independent SHA-256 recompute,
    and source provenance; reject any invented manifest URI/hash
- checked-in golden evidence changed without real provenance
  - mitigation: golden-demo-run edits must be limited to the manifest fields,
    must preserve all identity fields, and must be backed by the checked-in
    fixture plus the recomputed hash
- Genblaze v0.4.0 package unavailable
  - mitigation: follow the two-path dependency pin contract (section 12); if
    v0.4.0 is unavailable, use the published-version fallback pins and name
    them truthfully; if the fallback also fails, stop and report
- Genblaze API mismatch between 0.3.x and 0.4.0
  - mitigation: any `src/**` edit for API compatibility is PM-gated; if the
    API differs and no PM approval exists, stop and report
- dependency pin breakage
  - mitigation: pin all three packages to exact versions; validate with
    `importlib.metadata.version(...)`; do not leave any package unpinned
- B2/live credential dependency
  - mitigation: default path is local/checked-in fixture; live B2 upload or
    live Genblaze run requires later explicit PM approval; do not read B2
    broadly
- overclaim drift
  - mitigation: preserve the truth boundary verbatim; never imply live B2
    Object Lock, tamper-proof storage, or semantic truth
- version-claim drift (claiming v0.4.0 while running 0.3.x)
  - mitigation: record exact installed versions; set
    `version_claim_truthful` from real installed versions; no evidence may
    claim v0.4.0 unless v0.4.0 is actually installed and used
- downstream surfaces reading old (null) fields
  - mitigation: migrate PS-024 smoke in lockstep; update golden run with real
    fields; record the exact Genblaze versions so downstream surfaces can
    branch on the real versions
- demo fragility
  - mitigation: keep the default path local/checked-in; do not require live
    providers or live B2 for the demo to pass

## 18. Acceptance criteria

PS-035a is accepted only when:

- the PS-035a spec exists (this document, accepted)
- package availability reality is documented (section 5 records the readiness
  probe and the unavailable v0.4.0)
- the implementation uses v0.4.0 only if all three Genblaze packages are
  available, installable, and API-compatible at implementation time
- if v0.4.0 remains unavailable, the exact published fallback pins
  (`genblaze-core==0.3.4`, `genblaze-s3==0.3.4`, `genblaze-gmicloud==0.3.2`)
  are allowed
- any fallback is named truthfully (e.g. "Genblaze manifest correctness with
  exact published pins") and recorded in evidence
- No evidence may claim v0.4.0 unless v0.4.0 is actually installed and used
- the manifest fixture strategy is documented (local/checked-in by default;
  live B2 upload requires later PM approval)
- live B2 is not required by default
- the golden-run manifest contract is explicit (non-null `manifest_uri`,
  non-null 64-hex `manifest_hash`/`manifest_sha256`, exact recorded
  Genblaze versions, independent recompute), and manifest correctness remains
  mandatory regardless of version path
- the PS-024 migration is explicit (remove null assertion, require real
  fields, preserve identity)
- the evidence report schema is defined (section 14)
- the truth boundary is preserved (section 16)
- no implementation files are changed during the spec-only phase
- commit and push are required before acceptance

## 19. Rollback

Rollback of the PS-035a spec-only phase is a single revert of the PS-035a
spec commit, because only this spec file is changed in this phase.

Future implementation rollback must restore `golden-demo-run.json` and the
PS-024 smoke if the manifest migration fails. Specifically, if PS-035a
implementation turns out to break the golden evidence or the PS-024 smoke,
rollback must restore:

- `docs/evidence/demo/golden-demo-run.json` to its pre-PS-035a state
  (with `manifest_uri: null`, `manifest_hash: null`, no `manifest_sha256`,
  no `genblaze_version`)
- `scripts/ps024_golden_demo_run_pinning_smoke.py` to its pre-PS-035a state
  (the null-manifest contract)
- `apps/api/requirements.txt` to its pre-PS-035a state (or to a PM-approved
  fallback pin)

Because PS-035a is intentionally scoped to dependency pin, golden evidence,
PS-024 smoke, PS-035a smoke, PS-035a evidence, a PS-035a proof doc, a smoke
harness note, the master spec plan, and the roadmap slices doc, rollback is
isolated, reversible, and does not require touching product UI, backend,
providers, or deployment config.
