# PS-034C — Winning Roadmap + Master Spec Replan — Proof

Status: Spec only / docs only.
Slice: PS-034C
Date: 2026-07-01
Base branch: `ps-034c/winning-roadmap-master-spec-replan`
Spec: `specs/46-ps-034c-winning-roadmap-master-spec-replan.md`

PS-034C is documentation/spec/roadmap only. It does not touch validation
architecture, product code, backend, providers, deployment, requirements, or
dependencies. It does not call providers, does not read B2, and does not
implement Campaign Proof Room, Genblaze v0.4.0 manifest correctness, the
multimodal proof layer, or any future implementation slice.

## 1. Files Changed

PS-034C changed only the following files:

- `specs/46-ps-034c-winning-roadmap-master-spec-replan.md` (this slice's spec)
- `specs/07-master-spec-plan.md` (master spec replan — added the winning
  roadmap wave sections)
- `specs/01-product-one-pager.md` (one-pager refresh)
- `specs/08-roadmap-slices.md` (Wave 8 PS-034C-governed roadmap ledger)
- `docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`
  (PS-035 conflict resolution + superseded-section reconciliation)
- `docs/roadmap/ps-031a-hardened-product-modules-correction.md`
  (PS-034C reconciliation note appended)
- `docs/ps-034c-winning-roadmap-master-spec-replan-proof.md` (this proof doc)
- `docs/evidence/ps-034c/winning-roadmap-master-spec-replan-report.json`
  (PS-034C doc-contract smoke report)
- `scripts/ps034c_winning_roadmap_master_spec_replan_smoke.py` (PS-034C
  doc-contract smoke)
- `docs/validation/proofstudio-smoke-harness-v1.md` (PS-034C note appended;
  PS-034A/PS-034B required lines preserved)

No other files were changed. No product, backend, provider, deployment,
requirements, or `.env*` files were touched. No prior-slice evidence
(PS-034A, PS-034B, PS-023 through PS-034, `docs/evidence/demo/golden-demo-run.json`)
was modified. `scripts/proofstudio_regression_gate.py` was not modified.

## 2. Roadmap Conflict Resolution

Two roadmap sources previously disagreed on what PS-035 is:

- The winning roadmap doc (`docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`)
  called PS-035 the "Disclosure Readiness Layer".
- The PS-031A correction called PS-035 the "Review + Approval Workspace".

PS-034C resolves this with one authoritative identity, propagated across the
master spec, the roadmap slices doc, and the winning roadmap doc:

- The PS-031A correction remains authoritative unless later superseded.
- PS-035 is Review + Approval Workspace.
- Disclosure becomes PS-037 — Disclosure + Trust Boundary Layer.
- PS-035 remains blocked until PS-034C is accepted.
- PS-035a (Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest
  Correctness) should be the next implementation slice unless the PM later
  changes priority.

The conflicting section headings in the winning roadmap doc are retained for
history but explicitly marked SUPERSEDED, with pointers to the authoritative
post-PS-034C ordering.

## 3. Built Slice Preservation Statement

No accepted built slice is dropped by PS-034C. The accepted built slices
PS-023 through PS-034B remain in place and are the foundation for the
post-PS-034C roadmap wave:

- PS-023 — Judge Cockpit Home
- PS-024 — Golden Demo Run Pinning
- PS-025 — Public Durable Passport Unlock
- PS-026 — B2 Evidence Explorer
- PS-027 — Genblaze Pipeline Graph
- PS-028 — Manifest Verification Panel
- PS-029 — B2 Rehydrate Comparison
- PS-030 — Failure-as-Proof Timeline
- PS-031 — Export Campaign Pack v2 / Judge Evidence Pack
- PS-032 — Operations Cockpit / Flight Recorder v2
- PS-033 — Provider Decision Intelligence
- PS-034 — Lineage + Comparison Lab
- PS-034A — Smoke Harness v1 (validation architecture repair)
- PS-034B — Historical Smoke Local-Mode Retrofit

Any unbuilt slice may be dropped or delayed only with a recorded reason. The
only delayed/optional slice in the new wave is PS-040 (Product Dashboard +
Marketing Website), which does not directly help a judge decide.

## 4. New Roadmap Ledger

The post-PS-034C roadmap ledger (authoritative, from current accepted state to
Devpost):

| Slice | Title | Status |
|---|---|---|
| PS-034C | Winning Roadmap + Master Spec Replan | docs only (this slice) |
| PS-035 | Review + Approval Workspace | blocked until PS-034C accepted |
| PS-035a | Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest Correctness | blocking; next implementation slice unless PM changes priority |
| PS-035b | Cost Caps + Golden-Fixture Governance | add |
| PS-036 | Archive / Rehydrate / B2 Audit Vault | keep |
| PS-037 | Disclosure + Trust Boundary Layer | keep |
| PS-037a | Multimodal Proof Layer | add |
| PS-037b | AssemblyAI Transcript/Timestamp Evidence | add |
| PS-037c | Hume or ElevenLabs Voiceover Artifact | add |
| PS-037d | Gemini Campaign Intelligence / Judge Narrative | add |
| PS-037e | Cloudflare Low-Cost Backbone | add |
| PS-038 | Production Readiness + Demo Mode | keep |
| PS-038a | Campaign Proof Room | add (marquee) |
| PS-039 | Final Submission Pack | keep |
| PS-039a | Devpost Submission Package + 3-Minute Demo Script | add |
| PS-040 | Product Dashboard + Marketing Website | delay/optional |
| PS-041–PS-043 | reserve hardening / stretch / fix slices | reserve |

Decisions:

- PS-035 through PS-039a are required for the winning submission.
- PS-035a is blocking because golden-run manifest correctness is core
  provenance and the current golden run has a null manifest gap.
- PS-040 is delayed/optional because it does not help a judge decide.
- PS-041 through PS-043 are reserved for hardening, stretch, and fixes.

## 5. Genblaze v0.4.0 / Golden-Run Manifest Correctness Plan

Genblaze is used to produce verifiable SHA-256 manifests for stored artifacts.
The golden run must lock Genblaze v0.4.0 and must carry a real `manifest_uri`
and a real `manifest_hash`, not nulls.

Today the golden run has a Genblaze gap: `manifest_uri`, `manifest_hash`, and
`genblaze_version` are all null. This was confirmed during PS-034C (the golden
run file was read, not modified).

PS-035a (Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest
Correctness) closes that gap:

- pin the golden run to Genblaze v0.4.0
- require a real `manifest_uri` (not null)
- require a real `manifest_hash` (not null)
- require `genblaze_version` pinned (not null)
- manifest verification smoke + golden-run manifest correctness check pass

PS-035a is blocking. Until it lands, golden-run manifest correctness must not
be claimed as done. PS-034C only documents the requirement; it does not
implement it.

Risk: Genblaze version drift. If the golden run is not locked to Genblaze
v0.4.0, the manifest correctness story breaks.

## 6. Cost Cap / Golden-Fixture Plan

PS-035b (Cost Caps + Golden-Fixture Governance) locks the following cost rules
into the roadmap:

- no paid video generation until the core demo is stable
- no repeated live provider runs during UI development
- every paid/live run becomes a reusable golden fixture
- local/dry-run fixtures for frontend and smoke tests
- provider adapters behind the router (no direct provider calls in UI paths)
- visible Demo Mode: B2 rehydrated evidence, no live spend at judging time
- billing alerts and low quotas configured before any paid keys are used
- no provider keys in frontend code
- never commit `.env`, `.env.save`, tokens, or generated secrets

Render/hosting cold-start mitigation and paid-upgrade timing are handled in
PS-038 and PS-039a: do not pay for a hosting upgrade until the demo is stable
and close to submission, but plan the upgrade so it happens before judging
rather than during it.

PS-034C only documents these rules; it does not change billing, budgets, or
dependency pins.

## 7. Campaign Proof Room and Multimodal Proof Plan

### Campaign Proof Room (PS-038a, marquee)

Campaign Proof Room is the marquee future judge-facing surface. It is the
single room that shows a judge the full provenance story end to end: brief,
provider routing, attempts, failure-as-proof, generated asset, Backblaze B2
archive, Genblaze manifest, provenance passport, manifest verification, B2
rehydrate, review decision, and export/disclosure notes.

It ties provenance, B2 evidence, rehydration, failure-as-proof, and lineage
together in one room so the roadmap has a single marquee surface instead of
many disconnected proof pages. It is a future implementation slice (PS-038a);
PS-034C only documents the plan.

### Multimodal Proof Layer (PS-037a)

The current plan treats proof as images only. The winning strategy needs a
multimodal proof layer: image + voiceover/audio + transcript under a single
campaign/passport/manifest. PS-037a defines the multimodal passport schema and
adapters so image, voiceover/audio, and transcript artifacts share one
campaign identity, one manifest, and one provenance chain. It is a future
implementation slice; PS-034C only documents the plan.

Supporting future slices:

- PS-037b — AssemblyAI Transcript/Timestamp Evidence (word-level timestamps as
  first-class provenance).
- PS-037c — Hume or ElevenLabs Voiceover Artifact (choose one polished
  provider, not both, unless later justified).
- PS-037d — Gemini Campaign Intelligence / Judge Narrative (captions,
  summaries, model-comparison explanations, judge-facing narrative).
- PS-037e — Cloudflare Low-Cost Backbone (cheap, durable, fast delivery of
  assets and the public surface).

None of these are implemented in PS-034C. PS-034C documents them only.

## 8. Truth-Boundary Preservation

ProofStudio proves what the pipeline did.

It does not prove semantic truth, legal authenticity, C2PA authenticity, human
authorship, Object Lock/tamper-proof storage, browser-side B2 byte
verification, or production security unless those are actually implemented.

PS-034C preserves this boundary verbatim across the master spec, the one-pager,
and the roadmap. Any roadmap row that risks overclaim (for example multimodal
proof or campaign intelligence) is worded as proving what the pipeline
produced, not as proving what the content means or who authored it.

The PS-034C doc-contract smoke explicitly checks that none of the following
appear as positive claims in the changed docs:

- production secure
- C2PA authentic
- human authorship proven
- Object Lock enabled
- tamper-proof storage
- browser-side B2 byte verification

(These terms may still appear as explicit non-claims inside the truth
boundary, which is correct and required.)

## 9. Non-Goals

PS-034C must not and does not:

- write or change product UI code
- write or change backend/provider code
- write or change deployment code
- change requirements or dependency pins (no `requirements*.txt`, no
  `pyproject.toml`, no lockfile changes)
- make any live provider calls
- read B2
- rewrite evidence for prior slices
- implement Campaign Proof Room
- implement Genblaze v0.4.0 manifest correctness
- implement AssemblyAI / Hume / ElevenLabs / Gemini provider work
- implement PS-035
- implement PS-035a
- call the central regression gate
- mutate PS-034A, PS-034B, or historical evidence
- mutate `docs/evidence/demo/golden-demo-run.json`
- remove or rewrite the PS-034A required validation sentence
  "Historical smoke local-mode retrofit is deferred to PS-034B."

## 10. Validation Evidence

PS-034C is validated by a dedicated doc-contract smoke:

- `scripts/ps034c_winning_roadmap_master_spec_replan_smoke.py`

It is local/static only. It:

- reads docs/specs only
- does not call providers
- does not read B2
- does not run frontend
- does not run backend
- does not call the central regression gate
- does not mutate prior evidence
- writes only `docs/evidence/ps-034c/winning-roadmap-master-spec-replan-report.json`

The smoke verifies:

- all required files exist
- the PS-035 conflict is resolved
- the PS-031A correction is declared authoritative
- PS-035 is Review + Approval Workspace
- Disclosure is PS-037
- PS-035a is Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest
  Correctness
- PS-035 remains blocked until PS-034C is accepted
- Campaign Proof Room appears in required docs
- the multimodal proof layer appears in required docs
- AssemblyAI Transcript/Timestamp Evidence appears
- Hume or ElevenLabs Voiceover Artifact appears
- Gemini Campaign Intelligence / Judge Narrative appears
- Cloudflare Low-Cost Backbone appears
- Cost Caps + Golden-Fixture Governance appears
- Devpost Submission Package + 3-Minute Demo Script appears
- the truth boundary appears
- no forbidden overclaims appear as positive claims
- no forbidden implementation files were changed

The PS-034C evidence report is at
`docs/evidence/ps-034c/winning-roadmap-master-spec-replan-report.json`.

Additional regression protection: `scripts/ps034a_smoke_harness_v1_smoke.py`
and `scripts/ps034b_historical_smoke_local_mode_retrofit_smoke.py` still pass
unchanged, and `git ls-files -v` shows no hidden git flags.

## 11. Risks

Recorded per the PS-034C spec:

- too many slices: the new roadmap wave is large and could diffuse focus
- scope creep: documentation work can expand into unplanned doc rewrites
- paid provider dependency: the winning strategy depends on paid providers
  (AssemblyAI, Hume or ElevenLabs, Gemini), which adds spend and key risk
- demo fragility: a live or cold demo can fail in front of a judge
- overclaim risk: multimodal proof and campaign intelligence must stay inside
  the truth boundary
- Genblaze version drift: the golden run must lock Genblaze v0.4.0 or the
  manifest correctness story breaks
- deployment/cold-start risk: the free Render tier can cold-start at judging
  time
- evidence/report drift: docs and evidence can drift out of sync if the
  roadmap is updated without updating the report
- judge confusion: too many surfaces can confuse a judge; Campaign Proof Room
  must be the single marquee surface

## 12. Rollback

Rollback of PS-034C is a single revert of the PS-034C docs/evidence commit.
Because PS-034C only edits documentation, specs, roadmap, a proof doc, an
evidence report, and a doc-contract smoke, rollback is low-risk, isolated, and
reversible. It leaves the accepted PS-034A and PS-034B validation architecture
fully intact and requires no change to the central regression gate or to
PS-034A/PS-034B evidence.
