# PS-034C — Winning Roadmap + Master Spec Replan

Status: Spec only.
Base branch: `ps-034c/winning-roadmap-master-spec-replan`
Date: 2026-07-01

## 1. Status

PS-034C is currently:

- Spec only.
- Implementation/docs edits pending.

PS-034C must not be implemented, and no documentation edits may begin, until
this spec is accepted.

PS-034C depends on PS-034A and PS-034B being accepted. PS-034A created the
central validation harness (`scripts/smoke_lib.py`,
`scripts/proofstudio_regression_gate.py`, the validation doc, and the
PS-034A evidence report). PS-034B retrofitted the historical feature smokes
(PS-023 through PS-034) so they are safe to run directly. The latest accepted
slice is PS-034B commit `aa20c82`.

PS-034C is documentation/spec/roadmap only. It does not touch validation
architecture, product code, backend, providers, or deployment.

PS-035 remains blocked until PS-034C is accepted.

## 2. Purpose

PS-034C reconciles the master spec, roadmap, one-pager, and slice ordering
with the strongest hackathon-winning strategy before any implementation
resumes.

PS-034A and PS-034B repaired the validation architecture. PS-034C now
re-aligns the product plan around the winning strategy: a marquee judge-facing
Campaign Proof Room, a multimodal proof layer (image + voiceover/audio +
transcript under one campaign/passport), AssemblyAI transcript/timestamp
evidence, a Hume or ElevenLabs voiceover artifact, Gemini/Google campaign
intelligence, a Cloudflare low-cost backbone, B2-everywhere evidence, Genblaze
v0.4.0 SHA-256 manifest correctness, cost caps and golden-fixture governance,
Render/hosting cold-start mitigation and paid-upgrade timing, and a final
Devpost submission package plus a 3-minute demo video script.

After PS-034C, the master spec, roadmap, and slice ordering must reflect that
winning strategy, the built slices PS-023 through PS-034B must remain, and the
next implementation slice must be unblocked and clearly defined.

## 3. Why PS-034C Exists

- The validation architecture is now repaired by PS-034A/PS-034B, so product
  planning can resume safely on top of a stable gate.
- The product roadmap must be corrected before PS-035 resumes, because PS-035
  should no longer be built against the pre-PS-034C roadmap.
- There is a PS-035 numbering conflict between roadmap docs. Two roadmap
  sources disagree on what PS-035 is. PS-034C resolves that conflict with one
  authoritative numbering.
- The roadmap is missing a multimodal proof layer strategy. The current plan
  treats proof as images only. The winning strategy needs image + voiceover/
  audio + transcript under a single campaign/passport.
- The roadmap is missing Campaign Proof Room as the marquee future
  judge-facing surface that ties provenance, B2 evidence, rehydration,
  failure-as-proof, and lineage together for a judge in one room.
- The roadmap is missing Genblaze v0.4.0 SHA-256 manifest requirements. The
  golden run currently has a Genblaze gap: `manifest_uri` and `manifest_hash`
  are null. That gap must become a blocking future slice.
- The roadmap is missing cost/golden-fixture governance: no cost caps, no
  golden-fixture reuse rule, no rule that every paid/live run becomes a
  reusable golden fixture.
- The roadmap is missing a Devpost/demo plan: no final submission package
  milestone and no 3-minute demo video script milestone.

PS-034C is the slice that closes all of those gaps in documentation only,
without writing or shipping any of the underlying product features.

## 4. Scope

PS-034C is documentation/spec/roadmap only.

In scope:

- master spec replan
- one-pager refresh
- roadmap reconciliation
- PS-031A correction reconciliation (declare the PS-031A roadmap correction
  authoritative unless later superseded)
- a new winning roadmap wave (the future slice list that implements the
  winning strategy)
- a PS-034C proof doc
- a PS-034C evidence report
- an optional doc-contract smoke if useful
- this spec

Out of scope: everything that is not documentation/spec/roadmap/evidence/
smoke. That includes all product UI, all backend, all providers, all
deployment config, all requirements/dependency pin changes, all live provider
calls, and all prior-slice evidence rewrites.

## 5. Non-goals

PS-034C must not:

- do not write or change product UI code
- do not write or change backend/provider code
- do not write or change deployment code
- do not change requirements or dependency pins in this slice
  (no `requirements*.txt`, no `pyproject.toml`, no lockfile changes)
- do not make any live provider calls
- do not read B2
- do not rewrite evidence for prior slices
- do not implement Campaign Proof Room
- do not implement Genblaze v0.4.0 manifest correctness
- do not implement AssemblyAI / Hume / ElevenLabs / Gemini provider work
- do not implement PS-035

PS-034C only edits documentation, specs, roadmap, a proof doc, an evidence
report, and optionally a doc-contract smoke. Nothing else.

## 6. Allowed files for PS-034C implementation

PS-034C implementation may touch only:

- `specs/46-ps-034c-winning-roadmap-master-spec-replan.md`
- `specs/07-master-spec-plan.md`
- `specs/01-product-one-pager.md`
- `specs/08-roadmap-slices.md`
- `docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`
- `docs/roadmap/ps-031a-hardened-product-modules-correction.md`
- `docs/ps-034c-winning-roadmap-master-spec-replan-proof.md`
- `docs/evidence/ps-034c/winning-roadmap-master-spec-replan-report.json`
- `scripts/ps034c_winning_roadmap_master_spec_replan_smoke.py` only if added
  as a doc-contract smoke
- `docs/validation/proofstudio-smoke-harness-v1.md` only to append a PS-034C
  note if necessary

No other files may be modified.

## 7. Forbidden files

PS-034C must not touch:

- `apps/web/**`
- `apps/api/**`
- `src/**`
- `workers/**`
- `packages/**`
- `render.yaml`
- `.env*`
- `requirements*.txt`
- `pyproject.toml`
- `scripts/proofstudio_regression_gate.py`
- PS-034A evidence (`docs/evidence/ps-034a/**`)
- PS-034B evidence (`docs/evidence/ps-034b/**`)
- historical evidence under `docs/evidence/ps-023` through `docs/evidence/ps-034`
- `docs/evidence/demo/golden-demo-run.json`
- product/backend/provider/deployment files of any kind

## 8. Required documentation edits

The implementation phase of PS-034C must perform the following edits:

1. Declare the PS-031A roadmap correction authoritative unless later
   superseded. The PS-031A correction is the hardened product-modules
   correction and must be the reference state for the roadmap going forward.
2. Resolve the PS-035 numbering conflict. Pick one authoritative PS-035
   identity and propagate it across the master spec plan, the roadmap
   slices doc, and the winning roadmap doc.
3. Preserve all accepted built slices PS-023 through PS-034B. No accepted
   built slice may be silently dropped. Any unbuilt slice may be dropped only
   if it is clearly useless, redundant, risky, or lower priority, and the
   reason must be recorded.
4. Add Campaign Proof Room as the marquee future judge-facing surface. It is
   the single room that shows a judge the full provenance story end to end.
5. Add a multimodal proof layer: image + voiceover/audio + transcript under
   one campaign/passport. A proof must be able to carry more than one modality
   against one pipeline run.
6. Add AssemblyAI transcript/timestamp evidence as a future slice. Word-level
   timestamps become first-class provenance evidence.
7. Add Hume or ElevenLabs voiceover artifact as a future slice, choosing one
   polished artifact rather than both unless later justified. Do not block the
   roadmap on shipping both voice providers.
8. Add Gemini/Google credit strategy for campaign intelligence, captions,
   summaries, model comparison explanations, and the judge-facing narrative.
9. Add a Cloudflare low-cost backbone strategy for cheap, durable, fast
   delivery of assets and the public surface.
10. Add a B2-everywhere evidence strategy: B2 is the durable evidence layer
    across campaigns, rehydration, and demo mode.
11. Add Genblaze v0.4.0 SHA-256 manifest requirements and golden-run manifest
    correctness as a blocking future slice. The golden run must carry a real
    `manifest_uri` and `manifest_hash`, not nulls.
12. Add cost caps and golden-fixture governance: explicit caps, explicit
    reuse rule for paid runs, explicit local/dry-run default.
13. Add Render/hosting cold-start mitigation and paid-upgrade timing so the
    public demo does not fail on a cold free tier at judging time.
14. Add the final Devpost submission package and the 3-minute demo video
    script milestones as explicit roadmap deliverables.
15. Keep PS-035 blocked until PS-034C is accepted.
16. State that PS-035a Genblaze manifest correctness should be the next
    implementation slice after PS-034C unless the PM later changes priority.

## 9. Proposed roadmap after PS-034C

The roadmap table below is the proposed post-PS-034C ordering. Each row lists
why it matters for judging, its scope, its dependency, its validation proof,
and a decision (keep / add / expand / delay / reserve).

| Slice | Title | Why it matters for judging | Scope | Dependency | Validation proof | Decision |
|---|---|---|---|---|---|---|
| PS-034C | Winning Roadmap + Master Spec Replan | Aligns the whole product plan with the winning strategy before build resumes | Docs/spec/roadmap/evidence only | PS-034B accepted | PS-034C doc-contract smoke + static required-string check | add |
| PS-035 | Review + Approval Workspace | Lets a judge step through provenance and approve/reject with a recorded decision | Review workspace UI + decision ledger | PS-034C accepted | Review-room contract smoke | keep |
| PS-035a | Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest Correctness | Closes the golden-run `manifest_uri`/`manifest_hash` null gap; manifest correctness is core provenance | Manifest SHA-256 verification + golden-run manifest fix | PS-034C accepted | Manifest verification smoke + golden-run manifest correctness check | add (blocking) |
| PS-035b | Cost Caps + Golden-Fixture Governance | Protects budget and makes paid runs reusable, so the demo is repeatable without spend | Caps, fixture reuse rule, dry-run default | PS-035a accepted | Cost/governance contract smoke | add |
| PS-036 | Archive / Rehydrate / B2 Audit Vault | Durable evidence across runs; rehydration is a winning provenance story | Archive + rehydrate + B2 audit | PS-035b accepted | B2 rehydrate smoke | keep |
| PS-037 | Disclosure + Trust Boundary Layer | Prevents overclaim; states exactly what ProofStudio proves | Disclosure surface + trust boundary | PS-036 accepted | Disclosure contract smoke | keep |
| PS-037a | Multimodal Proof Layer | One campaign/passport carries image + voiceover/audio + transcript | Multimodal passport schema + adapters | PS-037 accepted | Multimodal contract smoke | add |
| PS-037b | AssemblyAI Transcript/Timestamp Evidence | Word-level timestamps become first-class provenance | AssemblyAI adapter + transcript evidence | PS-037a accepted | Transcript evidence smoke | add |
| PS-037c | Hume or ElevenLabs Voiceover Artifact | One polished voiceover artifact per campaign (choose one, not both) | Voiceover adapter + artifact | PS-037a accepted | Voiceover artifact smoke | add |
| PS-037d | Gemini Campaign Intelligence / Judge Narrative | Captions, summaries, model comparison explanations, judge narrative | Gemini adapter + narrative builder | PS-037 accepted | Gemini narrative smoke | add |
| PS-037e | Cloudflare Low-Cost Backbone | Cheap durable delivery of assets and public surface | Cloudflare backbone wiring | PS-035b accepted | Backbone delivery smoke | add |
| PS-038 | Production Readiness + Demo Mode | Demo Mode rehydrates B2 evidence with no live provider spend | Demo mode + production hardening | PS-037 series accepted | Demo-mode smoke | keep |
| PS-038a | Campaign Proof Room | Marquee judge-facing room tying provenance, B2, rehydration, failure-as-proof, lineage | Campaign proof room UI + integration | PS-038 accepted | Campaign proof room smoke | add (marquee) |
| PS-039 | Final Submission Pack | Bundles the full evidence pack for submission | Submission pack builder | PS-038a accepted | Submission pack smoke | keep |
| PS-039a | Devpost Submission Package + 3-Minute Demo Script | Final Devpost deliverable and the video script a judge actually watches | Devpost package + demo script | PS-039 accepted | Submission package smoke | add |
| PS-040 | Product Dashboard + Marketing Website | Marketing/dashboard surface; not required to win, lower priority | Dashboard + marketing site | PS-039a accepted | Dashboard smoke | delay/optional |
| PS-041–PS-043 | reserve hardening / stretch / fix slices | Reserve capacity for late hardening, stretch, and fixes | reserved | as needed | as needed | reserve |

Decisions summary:

- PS-035 through PS-039a are required for the winning submission.
- PS-035a is blocking because golden-run manifest correctness is core
  provenance and the current golden run has a null manifest gap.
- PS-040 is delayed/optional because it does not help a judge decide and
  should not compete with submission-critical slices for spend or time.
- PS-041 through PS-043 are reserved for hardening, stretch, and fixes so the
  roadmap has slack instead of inventing new numbers late.

## 10. Cost strategy to lock

PS-034C must lock the following cost rules into the roadmap and master spec:

- no paid video generation until the core demo is stable
- no repeated live provider runs during UI development
- every paid/live run becomes a reusable golden fixture
- local/dry-run fixtures for frontend and smoke tests
- provider adapters behind the router (no direct provider calls in UI paths)
- visible Demo Mode: B2 rehydrated evidence, no live spend at judging time
- billing alerts and low quotas configured before any paid keys are used
- no provider keys in frontend code
- never commit `.env`, `.env.save`, tokens, or generated secrets

## 11. Truth boundary

ProofStudio proves what the pipeline did.

It does not prove semantic truth, legal authenticity, C2PA authenticity, human
authorship, Object Lock/tamper-proof storage, browser-side B2 byte
verification, or production security unless those are actually implemented.

PS-034C must preserve this boundary verbatim across the master spec, the
one-pager, and the roadmap. Any roadmap row that risks overclaim (for example
multimodal proof or campaign intelligence) must be worded as proving what the
pipeline produced, not as proving what the content means or who authored it.

## 12. Acceptance criteria

PS-034C is accepted only when:

- the PS-034C spec exists (this document, accepted)
- the required docs are updated: master spec plan, one-pager, roadmap slices,
  winning roadmap doc, PS-031A correction doc
- the PS-035 numbering conflict is resolved with one authoritative identity
- all winning strategy items from section 8 are included in the updated docs
- all built slices PS-023 through PS-034B are preserved unless explicitly
  justified in writing
- Genblaze v0.4.0 manifest correctness is added as a blocking future slice
  (PS-035a)
- no product/code/deployment files are changed
- no prior evidence is changed (PS-034A, PS-034B, and `docs/evidence/ps-023`
  through `docs/evidence/ps-034`, and `docs/evidence/demo/golden-demo-run.json`
  remain untouched)
- the PS-034C proof doc exists at
  `docs/ps-034c-winning-roadmap-master-spec-replan-proof.md`
- the PS-034C evidence report exists at
  `docs/evidence/ps-034c/winning-roadmap-master-spec-replan-report.json`
- an optional PS-034C doc-contract smoke passes if added
- the final git status contains only allowed PS-034C files (see section 6)
- commit and push are required before acceptance

## 13. Validation plan

The PS-034C implementation must be validated with:

- a static required-string check over the changed docs (the winning-strategy
  terms from section 8 must each appear in the updated docs)
- a no-forbidden-file-changes check (none of section 7 may appear in the diff)
- a no-prior-evidence-changed check (PS-034A, PS-034B, and historical evidence
  must remain unchanged)
- a no-hidden-Git-flags check:
  ```
  git ls-files -v | grep -E '^[a-z]'
  ```
  must return nothing both before and after validation
- an optional PS-034C doc-contract smoke if added
- the PS-034A smoke still passes:
  ```
  python scripts/ps034a_smoke_harness_v1_smoke.py
  ```
  This must not mutate PS-034A evidence.
- the PS-034B smoke still passes (run in safe local/check mode)
- a final git status check confirming only allowed PS-034C files are present

Important: Do NOT require `python scripts/proofstudio_regression_gate.py --current ps034c` unless you verify it does not mutate PS-034A evidence or existing evidence. Prefer a PS-034C doc-contract smoke for this slice.

Rationale: the central regression gate writes to a fixed report path tied to
its `--current` argument. Running it for `ps034c` is only safe if the gate is
first updated in a later PM-approved slice to avoid overwriting PS-034A or
existing evidence. For PS-034C, a dedicated doc-contract smoke is safer and
sufficient.

## 14. Risks

PS-034C must record the following risks:

- too many slices: the new roadmap wave is large and could diffuse focus
- scope creep: documentation work can expand into unplanned doc rewrites
- paid provider dependency: the winning strategy depends on paid providers
  (AssemblyAI, Hume or ElevenLabs, Gemini) which adds spend and key risk
- demo fragility: a live or cold demo can fail in front of a judge
- overclaim risk: multimodal proof and campaign intelligence must stay inside
  the truth boundary from section 11
- Genblaze version drift: the golden run must lock Genblaze v0.4.0 or the
  manifest correctness story breaks
- deployment/cold-start risk: the free Render tier can cold-start at judging
  time
- evidence/report drift: docs and evidence can drift out of sync if the
  roadmap is updated without updating the report
- judge confusion: too many surfaces can confuse a judge; Campaign Proof Room
  must be the single marquee surface

## 15. Rollback

Rollback of PS-034C is a single revert of the PS-034C docs/evidence commit.

Rollback must:

- leave the accepted PS-034A and PS-034B validation architecture fully intact
- not require any change to the central regression gate
- not require any change to PS-034A or PS-034B evidence
- restore the master spec, one-pager, roadmap, and PS-031A correction doc to
  their pre-PS-034C state (the known baseline)

Because PS-034C only edits documentation, specs, roadmap, a proof doc, an
evidence report, and optionally a doc-contract smoke, and does not touch
product, backend, provider, deployment, or validation-architecture files,
rollback is low-risk, isolated, and reversible.
