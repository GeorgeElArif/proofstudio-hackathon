# ProofStudio Roadmap Slices

## Roadmap Principle

Every slice must have:

- spec reference
- goal
- implementation owner
- acceptance criteria
- failure conditions
- judge value
- commit gate

No random coding.

## Wave 0 — Spec Repair And Project Control

### S0-001 Master Spec Plan

Status: this file set.

Goal:

Define the complete product, architecture, out-of-box ideas, truth boundaries, and execution rules.

Acceptance:

- specs/07-master-spec-plan.md exists
- all current proofs are summarized
- all out-of-box ideas are preserved
- execution rules are explicit

Judge value:

Keeps the product coherent and prevents random demo drift.

### S0-002 Roadmap Slice Ledger

Status: this file.

Goal:

Define all major slices from current state to submission.

Acceptance:

- specs/08-roadmap-slices.md exists
- waves are ordered
- each slice has clear purpose

Judge value:

Shows serious execution discipline.

### S0-003 Provider Router Contract Spec

File:

- specs/09-provider-router-contract.md

Goal:

Define provider interfaces, fallback rules, budget modes, and normalized errors.

### S0-004 Attempt Ledger Contract Spec

File:

- specs/10-attempt-ledger-contract.md

Goal:

Define the attempt ledger schema and storage rules.

### S0-005 Winning Demo Acceptance Spec

File:

- specs/11-winning-demo-acceptance.md

Goal:

Define what the final demo must show to be considered submission-ready.

## Wave 1 — Provider Router Foundation

### P1-001 Provider Result Contract

Goal:

Create typed provider result and provider error objects.

Acceptance:

- provider result supports success and failure
- normalized status enum exists
- raw error is sanitized
- no provider-specific leaking into app UI

Judge value:

Production readiness.

### P1-002 Provider Attempt Ledger

Goal:

Record every provider attempt.

Acceptance:

- each attempt has provider, model, status, latency, cost estimate, fallback reason
- ledger serializes to JSON
- ledger can be stored in B2

Judge value:

Failure-as-proof timeline.

### P1-003 Budget Mode Config

Goal:

Add budget modes:

- free-only
- cheap
- premium-final
- sponsor-demo

Acceptance:

- each provider declares supported modes
- router respects mode
- skipped providers are recorded with reason

Judge value:

Cost-aware production workflow.

### P1-004 ProviderRouter Core

Goal:

Attempt providers in ranked order until success or exhaustion.

Acceptance:

- stops on first valid success
- continues on retryable failure
- records all skipped and failed attempts
- returns final asset or final failure report

Judge value:

Resilient multi-provider media operations.

### P1-005 Mock Provider For Tests

Goal:

Create deterministic local providers for tests.

Acceptance:

- mock success provider
- mock quota failure provider
- mock billing required provider
- mock timeout provider

Judge value:

Production-readiness and testability.

### P1-006 B2 Attempt Ledger Storage

Goal:

Store provider attempt ledger in B2 and include it in Genblaze manifest.

Acceptance:

- attempt ledger asset uploaded to B2
- manifest includes ledger
- stored manifest verifies

Judge value:

B2 system of record.

## Wave 2 — Free / Cheap Provider Proofs

### P2-001 Cloudflare Workers AI Provider

Goal:

Add Cloudflare image generation provider.

Acceptance:

- uses env vars
- generates image if account supports it
- uploads output to B2
- writes manifest
- records failure honestly if blocked

Judge value:

Free/cheap visual path.

### P2-002 Pollinations Provider

Goal:

Add no-key fallback provider.

Acceptance:

- generates image from prompt
- stores image in B2
- stores provider note explaining fallback status
- marks output as emergency fallback, not premium provider

Judge value:

Resilience.

### P2-003 Stability Provider Stub

Goal:

Add provider wrapper ready for Stability API key.

Acceptance:

- env var supported
- skipped cleanly if missing
- records skipped reason

Judge value:

Future premium upgrade path.

### P2-004 Runware Provider Stub

Goal:

Add provider wrapper ready for Runware API key.

Acceptance:

- env var supported
- skipped cleanly if missing
- records skipped reason

Judge value:

Cheap variant generation path.

### P2-005 Gemini Text Provider Wrapper

Goal:

Wrap existing Gemini campaign intelligence into provider contract.

Acceptance:

- Gemini Flash produces structured JSON
- failure maps to normalized error
- output stored in B2

Judge value:

Existing PS-002 becomes part of app architecture.

### P2-006 GMICloud Provider Wrapper

Goal:

Turn PS-001B script into a router-compatible provider.

Acceptance:

- validates model
- detects insufficient credits
- records billing failure
- succeeds after credits are added

Judge value:

Sponsor-aligned premium provider path.

## Wave 3 — Backend MVP

### B3-001 FastAPI Setup

Goal:

Create backend app.

Acceptance:

- health endpoint
- config loading
- no secrets in repo
- requirements updated

### B3-002 Campaign Model

Goal:

Represent campaign brief, prompt packet, assets, attempts, review states.

Acceptance:

- JSON serializable
- B2 artifact references supported

### B3-003 Generation Job Endpoint

Goal:

API endpoint to start a generation job.

Acceptance:

- accepts campaign brief and budget mode
- triggers provider router
- returns job/result summary

### B3-004 Provider Attempt Endpoint

Goal:

Retrieve attempt ledger.

Acceptance:

- returns all attempts
- supports successful and failed attempts

### B3-005 Asset Manifest Endpoint

Goal:

Retrieve asset manifest/provenance details.

Acceptance:

- returns B2 object refs
- returns manifest hash
- returns SHA-256

### B3-006 Export Pack Endpoint

Goal:

Create export pack.

Acceptance:

- includes approved assets
- includes manifests
- includes attempt ledger
- includes disclosure note

### B3-007 Rehydrate From B2 Endpoint

Goal:

Rebuild campaign state from B2 artifacts and manifest.

Acceptance:

- no local-only dependency
- campaign can be reconstructed from stored artifacts

## Wave 4 — Frontend MVP

### F4-001 Next.js App Shell

Goal:

Create app shell.

Acceptance:

- modern premium UI
- responsive layout
- nav between screens

### F4-002 Campaign Brief Screen

Goal:

Input campaign brief and budget mode.

Acceptance:

- submits to backend
- shows selected mode
- validates required fields

### F4-003 Mission Control Screen

Goal:

Show pipeline timeline.

Acceptance:

- provider attempts visible
- failures visible
- success visible
- B2 and Genblaze steps visible

### F4-004 Model Audition Board

Goal:

Compare provider outputs and failures.

Acceptance:

- cards for each provider
- output previews
- cost/latency/status
- B2/manifest status

### F4-005 Asset Detail / Provenance Passport

Goal:

Show full asset proof.

Acceptance:

- provider
- model
- prompt
- SHA-256
- B2 object URL
- manifest hash
- lineage
- truth boundary

### F4-006 Review Room

Goal:

Approve/reject generated assets.

Acceptance:

- reviewer decision
- rejection reasons
- review summary stored

### F4-007 Export Pack Screen

Goal:

Prepare final downloadable campaign pack.

Acceptance:

- selected approved assets
- manifest
- disclosure note
- attempt ledger
- export action

## Wave 5 — Demo Polish

### D5-001 Demo Seed Data

Goal:

Create deterministic campaign demo.

Acceptance:

- works without all providers
- shows fallback behavior
- can be rerun

### D5-002 Screenshot-Quality UI Pass

Goal:

Make the UI look premium enough for judges.

Acceptance:

- desktop screenshot
- tablet screenshot
- mobile screenshot
- no generic template feel

### D5-003 Failure-As-Proof Timeline Polish

Goal:

Make provider failures a strength.

Acceptance:

- clean failure messages
- fallback explanation
- no scary stack traces

### D5-004 Manifest Diff Visual

Goal:

Compare variants.

Acceptance:

- two assets can be compared
- hashes and providers differ clearly
- parent/child relation visible

### D5-005 Provider Swap Re-run

Goal:

Regenerate an asset with another provider.

Acceptance:

- new child asset created
- lineage preserved
- attempt recorded

### D5-006 Export Zip Polish

Goal:

Final export pack is judge-ready.

Acceptance:

- zip includes all required files
- README inside export explains proof

## Wave 6 — Premium Final Providers

### PF6-001 Add GMICloud Credits

Goal:

Rerun PS-001B and integrate into router.

Acceptance:

- GMICloud creates asset
- B2 upload succeeds
- manifest verifies

### PF6-002 Test Cloudflare vs GMICloud Quality

Goal:

Use Model Audition Board for final provider choice.

Acceptance:

- compare outputs
- record cost and quality

### PF6-003 Add Stability Or Runware Credits

Goal:

Cheap high-quality variants.

Acceptance:

- at least one paid cheap provider works if selected

### PF6-004 Add Gemini / Vertex / Imagen If Worth It

Goal:

Use Google paid path only if quality/value justifies it.

Acceptance:

- generated asset stored in B2
- manifest verifies
- provider cost recorded

### PF6-005 Add ElevenLabs Voiceover If Useful

Goal:

Optional audio proof.

Acceptance:

- generated voiceover stored in B2
- manifest verifies
- used in demo only if it improves submission

## Wave 7 — Submission Package

### SUB7-001 Final README

Acceptance:

- setup
- architecture
- provider strategy
- truth boundaries
- demo instructions

### SUB7-002 Architecture Diagram

Acceptance:

- shows B2
- shows Genblaze
- shows provider router
- shows UI/backend

### SUB7-003 Devpost Writeup

Acceptance:

- explains real-world utility
- explains production readiness
- explains B2 and Genblaze usage
- explains provider fallback

### SUB7-004 3-Minute Demo Script

Acceptance:

- strong story
- no overclaims
- visible proof
- clean ending

### SUB7-005 Recorded Demo

Acceptance:

- under 3 minutes
- shows brief to export
- shows fallback
- shows B2/manifest proof

### SUB7-006 Final Checklist

Acceptance:

- repo clean
- secrets removed
- demo works
- links work
- submission complete

## Wave 8 — PS-034C-Governed Winning Roadmap (Authoritative Post-Replan)

This wave is the authoritative post-PS-034C ordering from the current accepted
state (PS-023 through PS-034B) to the Devpost submission. It supersedes any
conflicting slice numbering in earlier roadmap prose for PS-035 onward. The
PS-031A hardened product-modules correction remains authoritative unless later
superseded. No accepted built slice is dropped by this replan.

### Roadmap conflict resolution

Two roadmap sources previously disagreed on what PS-035 is (Disclosure
Readiness Layer vs. Review + Approval Workspace). PS-034C resolves this with
one authoritative identity:

- PS-035 is Review + Approval Workspace.
- Disclosure becomes PS-037 — Disclosure + Trust Boundary Layer.
- PS-035 remains blocked until PS-034C is accepted.
- PS-035a (Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest
  Correctness) should be the next implementation slice unless the PM later
  changes priority.

### PS-034C — Winning Roadmap + Master Spec Replan

Spec: `specs/46-ps-034c-winning-roadmap-master-spec-replan.md`

Goal:

Align the master spec, one-pager, roadmap, and slice ordering with the
strongest hackathon-winning strategy before any implementation resumes. Docs/
spec/roadmap/evidence only.

Acceptance:

- master spec, one-pager, roadmap slices, winning roadmap doc, and PS-031A
  correction doc are reconciled
- the PS-035 numbering conflict is resolved with one authoritative identity
- Campaign Proof Room, multimodal proof layer, AssemblyAI transcript evidence,
  Hume or ElevenLabs voiceover artifact, Gemini campaign intelligence /
  judge narrative, Cloudflare low-cost backbone, B2-everywhere evidence,
  Genblaze v0.4.0 manifest correctness, cost caps and golden-fixture
  governance, Render cold-start mitigation, and the Devpost submission
  package plus 3-minute demo script are all added as roadmap items
- truth boundary is preserved verbatim
- PS-034C doc-contract smoke passes
- no product/backend/provider/deployment files change

Judge value:

Keeps the whole product plan coherent around the winning strategy before build
resumes.

### PS-035 — Review + Approval Workspace

Spec: `specs/51-ps-035-review-approval-workspace.md`

Goal:

A team can approve, reject, comment, and prepare final assets for export, with
every decision recorded in an approval ledger linked to passport, manifest, and
B2 archive.

Acceptance:

- approve/reject state
- reviewer notes/comments
- audit trail
- linked passport/evidence
- export readiness

Dependency: PS-034C accepted. (PS-035 remains blocked until PS-034C is
accepted.)

Status (2026-07-02): Implemented as a local / demo-only human decision surface.
A dedicated `/review-approval-workspace` route (distinct from the legacy
`/review` Review Room) renders a reviewable item from accepted local / golden /
demo data, its asset / media summary, the proof the pipeline already captured
(provenance passport, manifest verification, B2 evidence, rehydrate, export
pack), the four review states (`pending_review`, `approved`, `rejected`,
`needs_changes`), reviewer decision controls (state, reason category, rationale,
notes, reviewer label), and a local / in-session review ledger. The workspace
reads no B2 object, calls no provider, and performs no browser-side B2 byte
verification. Approval records the reviewer's workflow decision; it does not
prove semantic truth, legal authenticity, C2PA authenticity, human authorship,
Object Lock / tamper-proof storage, or production security. The ledger is local
/ in-session and is not durable, tamper-proof, replicated, or
production-multi-user. PS-035 ships a feature smoke
(`scripts/ps035_review_approval_workspace_smoke.py`) that is local / static by
default, writes only `docs/evidence/ps-035/`, and never calls a provider, reads
or writes B2, runs the frontend, or recursively executes another smoke.

Judge value:

Reviewers and clients can trust the approval trail.

### PS-035a — Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest Correctness (Blocking)

Goal:

Close the golden-run `manifest_uri` / `manifest_hash` null gap. Pin the golden
run to Genblaze v0.4.0 and require a real `manifest_uri` and a real
`manifest_hash`, not nulls.

Acceptance:

- Genblaze v0.4.0 SHA-256 manifest verification
- golden-run manifest correctness: `manifest_uri` and `manifest_hash` are real,
  not null; `genblaze_version` is pinned
- manifest verification smoke + golden-run manifest correctness check pass

Dependency: PS-034C accepted. This is the blocking next slice unless the PM
later changes priority.

Status (2026-07-01): Implemented as Genblaze manifest correctness with exact
published pins. The requested v0.4.0 target was probed unavailable on the
configured index, so the published-version fallback
(`genblaze-core==0.3.4`, `genblaze-s3==0.3.4`, `genblaze-gmicloud==0.3.2`) was
selected and recorded honestly. The golden run now carries real non-null
manifest fields backed by a checked-in local fixture (not a live B2 URL), with
an independent SHA-256 recompute equal to the golden `manifest_hash`. No
v0.4.0 claim is made.

Judge value:

Manifest correctness is core provenance.

### PS-035b — Cost Caps + Golden-Fixture Governance

Goal:

Protect budget and make paid runs reusable, so the demo is repeatable without
spend.

Acceptance:

- explicit cost caps
- explicit golden-fixture reuse rule (every paid/live run becomes a reusable
  golden fixture)
- local/dry-run default for frontend and smoke tests
- provider adapters behind the router
- billing alerts and low quotas configured before paid keys are used
- no provider keys in frontend code
- never commit `.env`, `.env.save`, tokens, or generated secrets

Dependency: PS-035a accepted.

Implementation (2026-07-01): PS-035b is implemented as a real, default-off
backend governance contract plus a golden-fixture digest freeze. The four
governance controls (`PROOFSTUDIO_LIVE_RUNS_ENABLED=false`,
`PROOFSTUDIO_B2_WRITES_ENABLED=false`, `PROOFSTUDIO_COST_CAP_USD=0.00`,
`PROOFSTUDIO_FIXTURES_FROZEN=true`) plus an explicit PM/human approval gate
(`PROOFSTUDIO_PAID_RUN_APPROVED=false`) are enforced in
`src/proofstudio/api/live_bridge.py` and `src/proofstudio/api/services.py`:
`run_live=true` alone no longer executes providers. A checked-in digest
manifest (`docs/evidence/golden-fixture-digests.json`) records SHA-256 digests
for the golden demo run and the PS-035a manifest fixture, which future slices
must verify before acceptance. PS-035a evidence is now protected by the
historical prior-evidence prefix lists. Validation is local/static only (no
live provider call, no live B2 read, no live B2 write). The freeze proves byte
equality to recorded digests only; it is not tamper-proof, not Object Lock, and
not production immutability.

Judge value:

Repeatable, low-spend demo and production-grade cost discipline.

### PS-035C — Non-Mutating Regression Gate Mode

Spec: `specs/49-ps-035c-non-mutating-regression-gate-mode.md`

Goal:

Make the central regression gate non-mutating by default so running the gate for
any later slice no longer overwrites the tracked historical PS-034A evidence
file (`docs/evidence/ps-034a/smoke-harness-v1-report.json`) as a side effect.

Acceptance:

- `--check-only`, `--report-out <path>`, and `--write-report` are supported;
  `--current`, `--frontend`, and `--no-frontend` remain supported.
- the default write mode for every slice (including PS-034A) is check-only; no
  report file is written unless `--report-out` or `--write-report` is supplied.
- `--write-report` is rejected for any non-PS034A current slice; conflicting
  write modes error before writing any file.
- check-only leaves `git status` clean except PS-035C implementation files and
  leaves the SHA-256 digest of the canonical PS-034A report unchanged.
- `--report-out /tmp/...` writes only the requested out-of-tree path and does
  not dirty tracked evidence.
- the PS-034A smoke passes `--write-report` explicitly when regenerating
  canonical PS-034A evidence.
- PS-035C smoke passes; validation is local/static only (no provider call, no
  B2 read, no B2 write, no frontend unless requested).

Dependency: PS-035b accepted.

Implementation (2026-07-01): PS-035C is implemented as a non-mutating gate mode
in `scripts/proofstudio_regression_gate.py` plus a local/static PS-035C smoke.
The canonical tracked PS-034A report bytes are unchanged from the pre-PS-035C
baseline. PS-035C fixes validation mutation only; it does not prove product
correctness, production security, B2 immutability, tamper-proof storage, real
billing API integration, or billing behavior.

Judge value:

Future-slice validation no longer dirties tracked historical PS-034A evidence,
removing a manual-restore workaround and keeping release-readiness evidence
honest.

### PS-035D — Root AGENTS.md Operating Rules

Spec: `specs/50-ps-035d-root-agents-operating-rules.md`

Goal:

Add a concise root-level `AGENTS.md` operating law so future GLM / OpenCode /
Codex / agent sessions inherit the accepted-base branch rule, the non-mutating
regression gate, the feature-smoke scope rules, the no-hidden-Git rule, the
truth boundary, and the canonical commands before any PS-035 product work. It
links the roadmap; it does not duplicate it.

Acceptance:

- root `AGENTS.md` exists and contains every required string in PS-035D section 11
- `AGENTS.md` is concise and links (not copies) the roadmap docs
- forbidden files (`src/**`, `apps/**`, `scripts/**`, `docs/evidence/**`,
  `.env*`, `render.yaml`, requirements) are unchanged
- no evidence mutation; hidden Git flags h/S check clean; `git diff --check` clean
- local/static only (no provider calls, no B2 reads, no B2 writes, no frontend run)

Dependency: PS-035C accepted. PS-035D does not renumber any accepted slice and
does not change the PS-035 Review + Approval Workspace scope.

Judge value:

Inheritable operating discipline so the review workspace opens on a repo whose
rules are already bound, not negotiated per session.

### PS-036 — Archive / Rehydrate / B2 Audit Vault

Goal:

Durable evidence across runs. Archive, rehydrate, and B2 audit layout so B2 is
the durable system of record and rehydration is a winning provenance story.

Acceptance:

- archive + rehydrate + B2 audit
- approved proof layout visible
- rehydrate proof (no live provider call during rehydrate)
- no Object Lock / tamper-proof claim unless implemented

Dependency: PS-035b accepted.

Judge value:

B2 system of record proven end to end.

### PS-037 — Disclosure + Trust Boundary Layer

Goal:

Prevent overclaim and state exactly what ProofStudio proves. Plain-language
disclosure notes, known/unknown/non-claimed sections, truth boundary.

Acceptance:

- disclosure surface + trust boundary
- channel-ready disclosure visible
- not legal advice
- no C2PA claim unless implemented

Dependency: PS-036 accepted.

Judge value:

Honest, judge-trustworthy disclosure.

### PS-037a — Multimodal Proof Layer

Goal:

One campaign/passport carries image + voiceover/audio + transcript. A proof can
carry more than one modality against one pipeline run.

Acceptance:

- multimodal passport schema
- adapters for image + voiceover/audio + transcript under one campaign
- multimodal contract smoke passes

Dependency: PS-037 accepted.

Judge value:

Multimodal provenance under one manifest.

### PS-037b — AssemblyAI Transcript/Timestamp Evidence

Goal:

Word-level timestamps become first-class provenance evidence inside the
multimodal passport.

Acceptance:

- AssemblyAI adapter + transcript evidence
- transcript/timestamp evidence visible
- transcript evidence smoke passes

Dependency: PS-037a accepted.

Judge value:

Timestamp-level transcript provenance.

### PS-037c — Hume or ElevenLabs Voiceover Artifact

Goal:

One polished voiceover artifact per campaign (choose one provider, not both,
unless later justified). Voiceover artifact stored in B2 and carried in the
multimodal passport.

Acceptance:

- voiceover adapter + artifact (Hume or ElevenLabs, one)
- voiceover artifact smoke passes
- do not block the roadmap on shipping both voice providers

Dependency: PS-037a accepted.

Judge value:

Polished multimodal campaign with voiceover.

### PS-037d — Gemini Campaign Intelligence / Judge Narrative

Goal:

Captions, summaries, model-comparison explanations, and the judge-facing
narrative. Gemini/Google credit strategy for campaign intelligence.

Acceptance:

- Gemini adapter + narrative builder
- judge-facing narrative visible
- Gemini narrative smoke passes

Dependency: PS-037 accepted.

Judge value:

A judge gets a plain-language narrative of what the pipeline produced.

### PS-037e — Cloudflare Low-Cost Backbone

Goal:

Cheap, durable, fast delivery of assets and the public surface via Cloudflare.

Acceptance:

- Cloudflare backbone wiring
- backbone delivery smoke passes

Dependency: PS-035b accepted.

Judge value:

Low-cost, durable, fast delivery.

### PS-038 — Production Readiness + Demo Mode

Goal:

Demo Mode rehydrates B2 evidence with no live provider spend. Production
hardening including Render/hosting cold-start mitigation and paid-upgrade
timing so the public demo does not fail on a cold free tier at judging time.

Acceptance:

- demo mode + production hardening
- demo-mode smoke passes
- cold-start mitigation plan + paid-upgrade timing

Dependency: PS-037 series accepted.

Judge value:

Reliable, honest demo at judging time.

### PS-038a — Campaign Proof Room (Marquee)

Goal:

The marquee judge-facing room tying provenance, B2, rehydration, failure-as-
proof, and lineage together for a judge in one room.

Acceptance:

- campaign proof room UI + integration
- campaign proof room smoke passes
- single marquee surface, not many disconnected proof pages

Dependency: PS-038 accepted.

Judge value:

The single surface a judge uses to understand ProofStudio.

### PS-038b — Winning Product Presentation Architecture

Spec: `specs/62-ps-038b-winning-product-presentation-architecture.md`

Goal:

Correct the post-proof-core sequence and record the product presentation +
productization architecture (brand identity direction, 3D marketing website
strategy, dashboard architecture, auth/account architecture, deployment
roadmap, agent/model operating plan, and CodeRabbit post-build review gate)
into the repo before PS-039 implementation begins. Docs/spec/roadmap
alignment only.

Roadmap correction: Final Submission Pack is not next. Before final
submission, ProofStudio needs Brand Identity + 3D Marketing Website + Demo
Automation Shell, Auth + Account System, World-Class User Dashboard, and
Deployment / Domain / Production Demo Hardening.

Corrected future sequence:

- PS-038b — Winning Product Presentation Architecture (docs only)
- PS-039 — Brand Identity + 3D Marketing Website + Demo Automation Shell
- PS-040 — Auth + Account System
- PS-041 — World-Class User Dashboard
- PS-042 — Deployment / Domain / Production Demo Hardening
- PS-043 — Final Submission Pack
- PS-044 — Devpost Package + 3-Minute Demo Script

Acceptance:

- spec + master spec + roadmap slices reflect PS-038b and the corrected
  sequence, without rewriting unrelated historical slices and without
  weakening any truth boundary from PS-037 through PS-038a
- the 3D website, brand, dashboard, auth, deployment, and CodeRabbit
  architectures are recorded but not implemented
- no implementation code, no app files, no scripts, no evidence mutation, no
  env/secrets changes, no deployment changes, no provider calls, no model
  calls, no B2 reads/writes, no Cloudflare API/DNS/resource/deploy/R2 behavior
- does not claim production readiness, does not claim production security,
  does not claim production compliance, does not claim OAuth/auth is
  implemented, does not claim the dashboard is implemented, does not claim
  deployment/domain is done, does not claim CodeRabbit has reviewed the
  project
- no hidden Git flags `h`/`S`; `git diff --check` clean; no stage/commit/push

Dependency: PS-038a accepted.

Status (2026-07-03): Docs/spec/roadmap alignment only. Records strategy;
implements nothing. The CodeRabbit review gate is a recorded later post-build
review layer; CodeRabbit is an extra review layer, not a replacement for local
gates (it does not replace the feature smoke, the central regression gate, the
frontend typecheck, the hidden Git flag check, the git diff check, or PM
acceptance).

Judge value:

Keeps the presentation + productization layer coherent and spec-first so the
brand, 3D website, auth, dashboard, and deployment slices do not drift.

### PS-039 — Brand Identity + 3D Marketing Website + Demo Automation Shell

Goal:

Build the serious premium brand identity and the 3D marketing website, plus the
demo automation shell. Cinematic proof story using the ProofStudio visual
metaphor (Proof Core / Evidence Orb / Campaign Record reassembling into the
Campaign Proof Room).

Stack direction (recorded by PS-038b): Next.js 16 + React 19 + TypeScript,
Tailwind CSS v4, Three.js + React Three Fiber + Drei, GSAP ScrollTrigger +
Lenis, Framer Motion, Canvas/image-sequence, GLB/glTF, reduced-motion
fallback, mobile/tablet/desktop variants, performance budgets + lazy loading.
No fake production/security/performance claims.

Acceptance:

- brand identity + 3D marketing website + demo automation shell
- brand site smoke passes
- the site is local/demo-first and does not overclaim

Dependency: PS-038b accepted. Must be spec-first, then implementation. Must
not include auth/dashboard/deployment unless explicitly approved.

Judge value:

A serious premium presentation surface that makes the proof story cinematic
and judge-winning.

### PS-039a — Website/Dashboard Build Authority + Visual Rebuild Contract

Spec:
`specs/64-ps-039a-website-dashboard-build-authority-visual-rebuild-contract.md`

Goal:

Record the corrected build authority and visual/product acceptance contract
inside the repo before PS-039 is rebuilt. Docs/spec alignment only.

Context:

The rejected GLM-built PS-039 implementation failed visual/product gate. It
must not be staged, must not be committed, must not be accepted, must not be
repaired by GLM, and must not be restored from discarded working tree. Root
cause: GLM optimized for static proof strings, cards, and safety checks, but
failed the intended product surface: a cinematic premium winning-project
presentation layer.

Corrected model/tool team:

- ChatGPT GPT-5.5 Thinking: PM / release gatekeeper
- Codex GPT-5.5 in VS Code: repo builder for PS-039 website and PS-041 dashboard
- Claude 4.6 in Antigravity: Awwwards Creative Director / visual critic
- Gemini 3.1 Pro: large-context researcher / multimodal reviewer
- Gemini 3.5 Flash: fast variant generator
- CodeRabbit: later post-build PR/static review layer only
- GLM is excluded from PS-039 website and PS-041 dashboard build/repair work

Acceptance:

- spec + master spec + roadmap slices reflect PS-039a without implementation
  code
- rejected GLM-built PS-039 implementation is recorded as rejected and blocked
  from staging, commit, acceptance, GLM repair, or restoration from discarded
  working tree
- PS-039 website target is recorded as a winning-project presentation layer,
  cinematic 3D marketing site, deep near-black premium atmosphere,
  Apple/Awwwards-level typography and hierarchy, sticky full-screen
  Canvas/image-sequence, scroll-synchronized story beats, Proof Core /
  Evidence Orb / Campaign Record, Campaign Proof Room, reduced-motion
  fallback, and desktop/tablet/mobile layouts
- PS-039 hard rejection list includes dense technical docs page and flat
  evidence-card layout
- PS-041 dashboard target is recorded as a calm, clear, fast tool interface,
  understandable in under 10 seconds, where the UI should point toward the
  data, not compete with it
- no implementation code, no app files, no scripts, no evidence mutation, no
  env/secrets changes, no deployment changes, no provider calls, no model
  calls, no B2 reads/writes, no Cloudflare API/DNS/resource/deploy/R2 behavior
- does not claim implementation exists, does not claim production readiness,
  does not claim production security, does not claim production compliance,
  does not claim OAuth/auth is implemented, does not claim dashboard is
  implemented, does not claim deployment/domain is done, does not claim
  CodeRabbit has reviewed the project
- no hidden Git flags `h`/`S`; `git diff --check` clean; no stage/commit/push

Dependency: PS-039 spec accepted; prior rejected PS-039 implementation
discarded. Must be accepted before the PS-039 rebuild.

Judge value:

Prevents a visually failed implementation from re-entering the repo and locks
the winning website/dashboard standard before rebuild.

### PS-040 — Auth + Account System

Spec:
`specs/65-ps-040-auth-account-system.md`

Status note (2026-07-07): PS-040A records the auth architecture/env/schema
contract before runtime implementation. It implements no runtime auth, no
login/signup UI, no auth endpoints, no migrations, no dependency installs, and
no secrets.

Goal:

Real auth + account system. Google OAuth, Apple OAuth, GitHub OAuth,
email/password signup, username login, email verification before activation,
block disposable/temp email domains, validate email/MX/deliverability, do not
reject legitimate custom/company domains, configurable allowlist/blocklist,
RBAC/account model, rate limiting for auth-sensitive endpoints, server-side
validation, audit hooks for important account actions.

Acceptance:

- OAuth (Google/Apple/GitHub) + email/password + username login
- email verification before activation; disposable/temp email blocking; email
  domain/MX/deliverability validation
- auth/account smoke passes
- does not claim enterprise security or production compliance

Dependency: PS-039 accepted.

Judge value:

Real accounts behind the proof system.

### PS-041 — World-Class User Dashboard

Goal:

A calm, clear, data-first dashboard understandable in under 10 seconds.
Campaign list, proof status, Campaign Proof Room launcher, passport launcher,
B2/Genblaze/rehydrate status, review status, export actions, account/profile,
and full loading/empty/error/success states.

Stack direction (recorded by PS-038b): Next.js 16 + React 19 + TypeScript,
Tailwind CSS v4, shadcn/ui + Radix UI primitives, TanStack Query v5, TanStack
Table v8, React Hook Form + Zod, Recharts first / ECharts only if
heavy/high-frequency data requires it, Supabase Postgres, Drizzle ORM, Better
Auth primary / Supabase Auth backup.

Acceptance:

- dashboard with campaign list, proof status, launchers, status panels, export
  actions, account/profile, and loading/empty/error/success states
- dashboard smoke passes
- does not overclaim proof or security

Dependency: PS-040 accepted.

Judge value:

A working surface a creator/marketing team uses day to day.

### PS-042 — Deployment / Domain / Production Demo Hardening

Goal:

Deploy to a real domain and harden the production demo (cold-start mitigation,
paid-upgrade timing, public demo reliability).

Acceptance:

- production deployment + domain + cold-start mitigation
- deployment smoke passes
- does not claim more uptime/performance than measured

Dependency: PS-041 accepted.

Judge value:

A reliable, honest public demo at judging time.

### PS-043 — Final Submission Pack

Goal:

Bundle the full evidence pack for submission.

Acceptance:

- submission pack builder
- submission pack smoke passes

Dependency: PS-042 accepted.

Judge value:

Submission-ready evidence bundle.

### PS-044 — Devpost Package + 3-Minute Demo Script

Goal:

Final Devpost deliverable and the video script a judge actually watches.

Acceptance:

- Devpost package + demo script
- submission package smoke passes
- demo script under 3 minutes, no overclaims, brief to export, shows fallback,
  shows B2/manifest proof, clean ending

Dependency: PS-043 accepted.

Judge value:

The final judge-facing deliverable.

Note (PS-038b): the historical pre-PS-038b roadmap listed PS-039 as Final
Submission Pack, an earlier historical Devpost/demo-script identifier that is
now folded into PS-044, and PS-040 (Product Dashboard + Marketing Website) as
delayed/optional. PS-038b corrects this: the presentation + productization
layer is now required and is sequenced before the Final Submission Pack.
From PS-039a onward, PS-039a means Website/Dashboard Build Authority + Visual Rebuild Contract only.
PS-038b preserves accepted history and does not rewrite unrelated historical
slices.

## Wave 8 — Decisions Summary

- PS-035 through PS-038a are accepted.
- PS-038b corrects the post-PS-038a sequence: Final Submission Pack is not
  next; the brand/3D website, auth, dashboard, and deployment hardening slices
  are required before final submission.
- PS-038b through PS-044 are the corrected path to submission:
  PS-038b (docs) -> PS-039 (Brand Identity + 3D Marketing Website + Demo
  Automation Shell spec) -> PS-039a (Website/Dashboard Build Authority +
  Visual Rebuild Contract) -> PS-039 rebuild -> PS-040 (Auth + Account System)
  -> PS-041 (World-Class User Dashboard) -> PS-042 (Deployment / Domain /
  Production Demo Hardening) -> PS-043 (Final Submission Pack) -> PS-044
  (Devpost Package + 3-Minute Demo Script).
- PS-039a records that the rejected GLM-built PS-039 implementation failed
  visual/product gate and that Codex GPT-5.5 in VS Code owns the PS-039
  website and PS-041 dashboard rebuild/build work.
- PS-035a was blocking because golden-run manifest correctness is core
  provenance; it is now accepted.
- The PS-031A correction remains authoritative unless later superseded.
- No accepted built slice PS-023 through PS-038a is dropped by this replan.
