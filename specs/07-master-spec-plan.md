# ProofStudio Master Spec Plan

## 1. Product Thesis

ProofStudio is a provenance-aware AI media operations system that turns campaign briefs into verified media kits using Genblaze, Backblaze B2, and a credit-aware multi-provider AI router.

ProofStudio is not just an AI generator.

It is a system for:

- campaign intelligence
- provider fallback
- visual/audio/text asset generation
- attempt logging
- B2-backed storage
- Genblaze manifest verification
- review and approval
- export packs
- rehydration from stored manifests

## 2. Hackathon Winning Argument

ProofStudio wins by proving that generative media workflows need more than a prompt box.

Most AI media tools stop at output generation. ProofStudio shows the full production lifecycle:

1. A campaign brief becomes structured intelligence.
2. A provider router selects the best available generation provider.
3. If a provider fails because of quota, billing, auth, timeout, or model limits, ProofStudio records the failure and moves to the next provider.
4. Generated outputs are stored in Backblaze B2.
5. Genblaze writes and verifies manifests.
6. Users review, approve, reject, regenerate, compare, and export verified campaign packs.
7. The campaign can be rehydrated from B2, proving B2 is the system of record.

## 3. Core Differentiators

### 3.1 Provider Fallback Router

ProofStudio should not depend on one AI API.

The Provider Router attempts providers in priority order, based on budget mode, availability, past failures, quality, cost, and expected latency.

Provider families:

- text intelligence
- image generation
- video generation
- audio generation
- metadata generation
- review summarization

### 3.2 Attempt Ledger

Every attempt is useful.

Failures are not hidden. They become operational evidence.

Each attempt records:

- provider
- model
- job type
- request timestamp
- result timestamp
- normalized status
- raw error class
- sanitized error summary
- estimated cost
- latency
- retryability
- selected fallback reason
- output asset references if successful

### 3.3 B2 System of Record

Backblaze B2 must store:

- source briefs
- prompt packets
- generated assets
- derived assets
- manifests
- provider attempt ledgers
- review records
- export packs
- demo artifacts

B2 is not decorative. The app must be able to rehydrate campaign state from B2-backed artifacts.

### 3.4 Genblaze Manifest Layer

Genblaze is used to produce verifiable manifests for stored artifacts.

The system must be honest about what manifests prove:

- byte-level asset integrity
- recorded workflow integrity
- relationship between assets, prompts, and stored metadata

The system must not claim:

- semantic truth
- legal authenticity
- C2PA authenticity unless implemented and verified
- human authorship verification

### 3.5 Provenance Passport

Every asset should have a Provenance Passport showing:

- campaign
- source brief
- provider
- model
- prompt
- generation parameters
- B2 object URL
- SHA-256
- manifest hash
- parent and child variant lineage
- review status
- export status
- truth boundary

### 3.6 Mission Control / Flight Recorder

The app should show the live pipeline:

- brief received
- campaign intelligence generated
- prompt packet created
- provider selected
- provider failed or succeeded
- fallback selected
- asset stored in B2
- manifest written
- manifest verified
- review pending
- export ready

### 3.7 Model Audition Board

Generate or compare the same campaign prompt across providers.

Show:

- provider
- model
- output preview
- quality rating
- cost estimate
- latency
- success or failure
- B2 status
- manifest status

### 3.8 Rehydrate From B2

The user can rebuild a campaign from B2 artifacts and manifests.

This proves B2 is the durable state layer.

### 3.9 Review Room With Proof

Reviewers can approve or reject assets with reasons:

- brand mismatch
- wrong aspect ratio
- too generic
- compliance issue
- weak quality
- provider failure
- needs disclosure
- ready for export

Review records should be stored and included in export packs.

### 3.10 Export Campaign Pack

The export pack includes:

- approved assets
- prompt packet
- campaign copy
- metadata
- review summary
- provider attempt ledger
- manifest
- truth-boundary note
- disclosure note

### 3.11 Disclosure Readiness Layer

Every export should clearly explain:

- which assets are AI-generated
- which providers were used
- what was verified
- what was not verified
- where the manifest lives
- what the hashes mean

### 3.12 Credit-Aware Provider Router

The router tracks provider availability and cost:

- free-only mode
- cheap mode
- premium final mode
- sponsor demo mode

It should explain why a provider was selected or skipped.

### 3.13 Failure-As-Proof Timeline

Failures should become part of the demo:

Example:

- GMICloud failed: insufficient credits.
- Gemini image failed: quota exhausted.
- Imagen failed: paid plan required.
- Cloudflare Workers AI succeeded.
- Asset stored in B2.
- Manifest verified.

This proves production readiness.

### 3.14 Manifest Diff

Compare two asset variants:

- same prompt or different prompt
- same provider or different provider
- same campaign parent
- different hash
- different review state
- different export status

### 3.15 Provider Swap Re-run

A user can regenerate an existing asset with another provider.

Example:

- free Cloudflare version
- premium GMICloud version
- premium Imagen version

All versions stay linked in lineage.

### 3.16 Why This Provider?

The UI should explain selection decisions.

Example:

Cloudflare Workers AI was selected because GMICloud had insufficient credits and Gemini image generation was quota-blocked.

### 3.17 Cost Ledger

Track estimated cost per provider attempt:

- provider
- model
- estimated cost
- free or paid
- credits used if available
- timestamp
- campaign
- asset

## 4. Non-Goals For MVP

Do not build:

- full enterprise DAM search
- billing
- teams and permissions
- full C2PA signing
- full auth system
- advanced image editor
- legal verification claims
- fake provider success
- unverified production claims

## 5. Required Technical Shape

Frontend:

- Next.js
- campaign brief screen
- mission control screen
- model audition board
- asset detail / provenance passport
- review room
- export pack screen

Backend:

- FastAPI
- provider router
- provider wrappers
- B2 storage service
- Genblaze manifest service
- campaign state service
- export pack service

Workers / background jobs:

- provider generation jobs
- B2 upload jobs
- manifest verification jobs
- export pack jobs

Storage:

- Backblaze B2 for durable artifacts
- local temp output only for dev
- optional SQLite/Postgres later for app state, but B2 remains system of record

## 6. Current Completed Proofs

### PS-001A

Status: passed.

Proof:

- local generated PNG
- Genblaze manifest
- Backblaze B2 asset upload
- Backblaze B2 manifest upload
- manifest read-back
- hash verification true
- zero transfer failures

### PS-001B

Status: implemented but blocked.

Truth:

- GMICloud auth works
- GMICloud model validation works
- live generation blocked by insufficient credits

### PS-002

Status: passed.

Proof:

- Gemini campaign intelligence
- JSON output
- Markdown output
- B2 upload
- Genblaze manifest
- stored manifest verification
- zero transfer failures

### PS-003

Status: implemented but blocked.

Truth:

- Gemini image models are quota/free-tier blocked
- Imagen generation requires paid plan
- Developer API rejects some Enterprise-only image config fields
- visual provider router path is needed

## 7. PM / Execution Rules

ChatGPT role:

- product manager
- architect
- spec writer
- reviewer
- judge strategy
- acceptance gate

GLM 5.2 / OpenCode role:

- code executor
- refactorer
- test writer
- UI implementer
- backend implementer

User role:

- runs commands
- owns keys
- approves direction
- reviews outputs
- decides when to buy credits

Rules:

- no implementation without spec
- no commit without acceptance criteria
- no fake pass
- no committed secrets
- every provider failure must be recorded honestly
- every generated asset must go through B2 and manifest verification when possible
- every slice must map to judge value

## 8. Winning Roadmap Wave (PS-034C Replan)

PS-034C reconciles this master spec with the strongest hackathon-winning
strategy before any implementation resumes. PS-034A and PS-034B repaired the
validation architecture. PS-034C re-aligns the product plan around a marquee
judge-facing Campaign Proof Room, a multimodal proof layer, durable B2
evidence everywhere, Genblaze v0.4.0 manifest correctness, cost caps and
golden-fixture governance, a Cloudflare low-cost backbone, and a final
Devpost submission package plus a 3-minute demo video script.

The roadmap conflict between roadmap docs over what PS-035 means is resolved
here as authoritative: PS-035 is Review + Approval Workspace. Disclosure
becomes PS-037 (Disclosure + Trust Boundary Layer). PS-035 remains blocked
until PS-034C is accepted. PS-035a (Genblaze v0.4.0 Manifest Verification /
Golden-Run Manifest Correctness) should be the next implementation slice
unless the PM later changes priority.

PS-035 (Review + Approval Workspace) is implemented on this branch as a local /
demo-only human decision surface: a dedicated `/review-approval-workspace`
route (distinct from the legacy `/review` Review Room) renders a reviewable
item from accepted local / golden / demo data, its asset / media summary, the
proof the pipeline already captured, the four review states, reviewer decision
controls, a rationale / notes capture, and a local / in-session review ledger.
Approval records the reviewer's workflow decision; it does not prove semantic
truth, legal authenticity, C2PA authenticity, human authorship, Object Lock /
tamper-proof storage, or production security. The workspace reads no B2
object, calls no provider, and performs no browser-side B2 byte verification.
Spec: `specs/51-ps-035-review-approval-workspace.md`.

The PS-031A hardened product-modules correction
(`docs/roadmap/ps-031a-hardened-product-modules-correction.md`) remains
authoritative unless later superseded. No accepted built slice PS-023 through
PS-034B is dropped by this replan.

### 8.1 Campaign Proof Room

Campaign Proof Room is the marquee future judge-facing surface. It is the
single room that shows a judge the full provenance story end to end: brief,
provider routing, attempts, failure-as-proof, generated asset, Backblaze B2
archive, Genblaze manifest, provenance passport, manifest verification, B2
rehydrate, review decision, and export/disclosure notes.

Campaign Proof Room ties provenance, B2 evidence, rehydration, failure-as-proof,
and lineage together for a judge in one room. It is added as a future slice
(PS-038a) so the roadmap has a single marquee surface instead of many
disconnected proof pages.

Campaign Proof Room is a future implementation slice. PS-034C only documents
the plan; it does not implement Campaign Proof Room.

### 8.2 Multimodal Proof Layer

The current plan treats proof as images only. The winning strategy needs a
multimodal proof layer: image + voiceover/audio + transcript under a single
campaign/passport/manifest. A proof must be able to carry more than one
modality against one pipeline run.

The multimodal proof layer is added as a future slice (PS-037a). It defines a
multimodal passport schema and adapters so image, voiceover/audio, and
transcript artifacts all share one campaign identity, one manifest, and one
provenance chain.

The multimodal proof layer is a future implementation slice. PS-034C only
documents the plan; it does not implement it.

### 8.3 AssemblyAI Transcript/Timestamp Evidence

AssemblyAI transcript/timestamp evidence is added as a future implementation
slice (PS-037b). Word-level timestamps become first-class provenance evidence
inside the multimodal passport, so a judge can see exactly which words were
spoken at which timestamp in the voiceover/audio artifact.

AssemblyAI transcript/timestamp evidence is a future implementation slice.
PS-034C only documents the plan; it does not call AssemblyAI or any provider.

### 8.4 Hume or ElevenLabs Voiceover Artifact

A polished voiceover artifact per campaign is added as a future implementation
slice (PS-037c). The strategy is to choose one polished voiceover provider
(Hume or ElevenLabs) rather than ship both, so the roadmap does not block on
two voice providers. Voiceover artifacts are stored in B2 and carried in the
multimodal passport.

Hume or ElevenLabs voiceover artifact is a future implementation slice.
PS-034C only documents the plan; it does not call Hume, ElevenLabs, or any
provider.

### 8.5 Gemini/Google Credit Strategy for Campaign Intelligence

Gemini/Google credit strategy covers campaign intelligence, captions,
summaries, model-comparison explanations, and the judge-facing narrative. The
existing Gemini campaign intelligence path (PS-002) becomes part of a broader
Gemini campaign intelligence slice (PS-037d) that produces the judge-facing
narrative: a plain-language explanation of what the pipeline produced, which
providers/models were used, why routing decisions happened, and what is and is
not claimed.

Gemini/Google credit strategy is a future implementation slice. PS-034C only
documents the plan; it does not call Gemini or spend any Google credit.

### 8.6 Cloudflare Low-Cost Backbone Strategy

Cloudflare is the low-cost backbone for cheap, durable, fast delivery of
assets and the public surface. Cloudflare Workers AI is already a free/cheap
provider path in the router. The Cloudflare backbone slice (PS-037e) extends
that into a delivery backbone so assets and the public surface are served
cheaply and durably.

Cloudflare backbone is a future implementation slice. PS-034C only documents
the plan; it does not configure Cloudflare.

### 8.7 B2-Everywhere Evidence Strategy

Backblaze B2 is the durable evidence layer across campaigns, rehydration, and
demo mode. B2 is not decorative: the app must be able to rehydrate campaign
state from B2-backed artifacts. B2-everywhere means source briefs, prompt
packets, generated assets, derived assets, manifests, provider attempt
ledgers, review records, export packs, and demo artifacts all live in B2.

B2-everywhere is preserved as a core winning proof spine through PS-036
(Archive / Rehydrate / B2 Audit Vault) and Demo Mode in PS-038.

### 8.8 Genblaze v0.4.0 SHA-256 Manifest Requirements

Genblaze is used to produce verifiable manifests for stored artifacts. The
golden run must lock Genblaze v0.4.0 and must carry a real `manifest_uri` and
a real `manifest_hash`, not nulls.

Today the golden run has a Genblaze gap: `manifest_uri` and `manifest_hash`
are null, and `genblaze_version` is null. That gap is documented and closed by
a blocking future slice.

The system must be honest about what manifests prove (byte-level asset
integrity, recorded workflow integrity, relationship between assets, prompts,
and stored metadata) and must not claim semantic truth, legal authenticity,
C2PA authenticity, human authorship, Object Lock/tamper-proof storage, or
production security unless those are actually implemented.

### 8.9 Golden-Run Manifest Correctness as Blocking Future Slice

Golden-run manifest correctness is a blocking future slice (PS-035a: Genblaze
v0.4.0 Manifest Verification / Golden-Run Manifest Correctness). Manifest
correctness is core provenance: the golden run must carry a real
`manifest_uri` and a real `manifest_hash`, pinned to Genblaze v0.4.0. Until
PS-035a closes that gap, the golden-run manifest correctness story is
incomplete and must not be claimed as done.

PS-035a is blocking because the current golden run has a null manifest gap.

PS-035a has now been implemented (2026-07-01) as Genblaze manifest correctness
with exact published pins. The requested v0.4.0 target was probed unavailable
on the configured index at implementation time, so the published-version
fallback (`genblaze-core==0.3.4`, `genblaze-s3==0.3.4`,
`genblaze-gmicloud==0.3.2`) was selected and recorded honestly. The golden run
now carries a real non-null `manifest_uri` (a checked-in local fixture path,
not a live B2 URL), a real 64-hex `manifest_hash`, the exact recorded Genblaze
versions actually installed, and an independent SHA-256 recompute over the
checked-in fixture equals the golden `manifest_hash`. No v0.4.0 claim is made.
Manifest correctness remains mandatory; if v0.4.0 becomes available later, a
follow-up may re-pin to the primary path and re-verify.

### 8.10 Cost Caps and Golden-Fixture Governance

Cost caps and golden-fixture governance are locked into the roadmap by
PS-035b. The locked cost rules are:

- no paid video generation until the core demo is stable
- no repeated live provider runs during UI development
- every paid/live run becomes a reusable golden fixture
- local/dry-run fixtures for frontend and smoke tests
- provider adapters behind the router (no direct provider calls in UI paths)
- visible Demo Mode: B2 rehydrated evidence, no live spend at judging time
- billing alerts and low quotas configured before any paid keys are used
- no provider keys in frontend code
- never commit `.env`, `.env.save`, tokens, or generated secrets

PS-035b has now been implemented (2026-07-01) as a real, default-off
governance contract plus a golden-fixture digest freeze. The four governance
controls are `PROOFSTUDIO_LIVE_RUNS_ENABLED=false`,
`PROOFSTUDIO_B2_WRITES_ENABLED=false`, `PROOFSTUDIO_COST_CAP_USD=0.00`, and
`PROOFSTUDIO_FIXTURES_FROZEN=true` (plus an explicit
`PROOFSTUDIO_PAID_RUN_APPROVED=false` PM/human approval gate). They are policy
flags, not secrets, and never use names containing `KEY`, `TOKEN`, or
`SECRET`. The backend (`src/proofstudio/api/live_bridge.py` and
`src/proofstudio/api/services.py`) enforces the gate: `run_live=true` alone is
no longer sufficient to execute providers. A checked-in digest manifest
(`docs/evidence/golden-fixture-digests.json`) records SHA-256 digests for the
golden demo run and the PS-035a manifest fixture; future slices must verify
these digests before acceptance. The freeze proves byte equality to recorded
digests only; it is not tamper-proof, not Object Lock, and not production
immutability. The cost cap is a local policy gate, not a real billing API
integration and not production multi-user budget accounting. PS-035b validated
with local/static smoke only: no live provider call, no live B2 read, no live
B2 write.

Cost caps and golden-fixture governance is implemented by PS-035b on this
branch. PS-034C originally documented the rules only; PS-035b adds the
default-off governance controls, golden-fixture digest manifest, and local
validation contract.

### 8.10.1 Non-Mutating Regression Gate (PS-035C)

PS-035C (Non-Mutating Regression Gate Mode) is a validation-harness slice that
fixes a validation-harness root-cause bug, not a product bug. The central
regression gate previously had a hardcoded tracked report path and wrote
`docs/evidence/ps-034a/smoke-harness-v1-report.json` unconditionally, so running
the gate for any later slice mutated tracked historical PS-034A evidence as a
side effect.

PS-035C (2026-07-01) makes the central gate non-mutating by default. The gate
accepts `--check-only` (the default for every slice, including PS-034A; no
report file is written), `--report-out <path>` (write only the requested path;
the canonical PS-034A report is never touched), and `--write-report` (write the
canonical tracked PS-034A report; only allowed with `--current ps034a` and
rejected for any non-PS034A current slice). Conflicting write modes error
before writing. The PS-034A smoke passes `--write-report` explicitly when it
regenerates canonical PS-034A evidence. Future slices can run the central gate
as part of their validation without manually restoring the PS-034A evidence
afterward. PS-035C is local/static only: no provider calls, no B2 reads, no B2
writes, and no frontend unless explicitly requested. PS-035C fixes validation
mutation only; it does not prove product correctness, production security, B2
immutability, tamper-proof storage, real billing API integration, or billing
behavior.

### 8.10.2 Root AGENTS.md Operating Law (PS-035D)

PS-035D (Root AGENTS.md Operating Rules) adds a concise root-level `AGENTS.md`
operating law at the repository root so future GLM / OpenCode / Codex / agent
sessions inherit the accepted-base branch rule, the non-mutating regression
gate, the feature-smoke scope rules, the no-hidden-Git rule, the truth
boundary, and the canonical commands before any PS-035 product work. It is an
operating-rules guard, not a product slice and not a duplicate roadmap: it
links `specs/07-master-spec-plan.md` and `specs/08-roadmap-slices.md` rather
than copying them. PS-035D is local/static only (no provider calls, no B2
reads, no B2 writes, no frontend run) and does not change any historical claim
or golden constant. Spec: `specs/50-ps-035d-root-agents-operating-rules.md`.

### 8.11 Render/Hosting Cold-Start Mitigation and Paid-Upgrade Timing

Render free tier can cold-start at judging time. The roadmap must include
cold-start mitigation and a clear paid-upgrade timing rule: do not pay for a
hosting upgrade until the demo is stable and close to submission, but plan the
upgrade so it happens before judging rather than during it. This is handled
inside PS-038 (Production Readiness + Demo Mode) and PS-044 (Devpost Package +
3-Minute Demo Script).

### 8.12 Devpost Submission Package and 3-Minute Demo Video Script

The final Devpost submission package (PS-044) and the 3-minute demo video
script (PS-044) are explicit roadmap deliverables. The demo video script must
show brief to export, show fallback, show B2/manifest proof, stay under three
minutes, avoid overclaims, and end cleanly.

### 8.13 Truth Boundary (Authoritative)

ProofStudio proves what the pipeline did.

It does not prove semantic truth, legal authenticity, C2PA authenticity, human
authorship, Object Lock/tamper-proof storage, browser-side B2 byte
verification, or production security unless those are actually implemented.

PS-034C preserves this boundary verbatim across the master spec, the one-pager,
and the roadmap. Any roadmap row that risks overclaim (for example multimodal
proof or campaign intelligence) is worded as proving what the pipeline
produced, not as proving what the content means or who authored it.

### 8.14 Winning Product Presentation Architecture (PS-038b)

PS-038b — Winning Product Presentation Architecture is a docs/spec/roadmap
alignment slice that corrects the post-proof-core sequence and records the
product presentation + productization architecture before PS-039 implementation
begins. Spec: `specs/62-ps-038b-winning-product-presentation-architecture.md`.

Final Submission Pack is not next. Before final submission, ProofStudio needs:

- Brand Identity + 3D Marketing Website + Demo Automation Shell
- Auth + Account System
- World-Class User Dashboard
- Deployment / Domain / Production Demo Hardening
- Final Submission Pack
- Devpost Package + 3-Minute Demo Script

Corrected future sequence:

- PS-038b — Winning Product Presentation Architecture (docs only)
- PS-039 — Brand Identity + 3D Marketing Website + Demo Automation Shell
- PS-040 — Auth + Account System
- PS-041 — World-Class User Dashboard
- PS-042 — Deployment / Domain / Production Demo Hardening
- PS-043 — Final Submission Pack
- PS-044 — Devpost Package + 3-Minute Demo Script

PS-038b records the 3D website strategy (Next.js 16 + React 19 + TypeScript,
Tailwind CSS v4, Three.js + React Three Fiber + Drei, GSAP ScrollTrigger +
Lenis, Framer Motion, Canvas/image-sequence, GLB/glTF, reduced-motion fallback,
mobile/tablet/desktop), the cinematic proof metaphor (Proof Core / Evidence Orb
/ Campaign Record reassembling into the Campaign Proof Room), the brand
identity direction (serious premium media proof system, near-black charcoal
base, Backblaze-inspired orange used rarely as warmth, electric proof
blue/cyan for verification, muted green for verified, amber for warning, red
only for destructive/error), the dashboard architecture (shadcn/ui + Radix UI
primitives, TanStack Query v5, TanStack Table v8, React Hook Form + Zod,
Recharts first / ECharts if needed, Supabase Postgres, Drizzle ORM, Better
Auth primary / Supabase Auth backup), the auth/account architecture (Google
OAuth, Apple OAuth, GitHub OAuth, email/password signup, username login, email
verification before activation, block disposable/temp email domains, validate
domain/MX/deliverability, do not reject legitimate custom/company domains),
the agent/model operating plan, and the CodeRabbit review gate.

PS-038b records strategy only. It does not implement the 3D website, auth, the
dashboard, or deployment. The CodeRabbit review gate is a recorded later
post-build review layer; CodeRabbit is an extra review layer, not a replacement
for local gates (it does not replace the feature smoke, the central regression
gate, the frontend typecheck, the hidden Git flag check, the git diff check, or
PM acceptance). PS-038b does not claim production readiness, does not claim
production security, does not claim production compliance, does not claim
OAuth/auth is implemented, does not claim the dashboard is implemented, does
not claim deployment/domain is done, and does not claim CodeRabbit has reviewed
the project. PS-038b preserves every prior truth boundary from PS-037 through
PS-038a verbatim and does not change any golden run canonical constant.

### 8.15 Website/Dashboard Build Authority + Visual Rebuild Contract (PS-039a)

PS-039a — Website/Dashboard Build Authority + Visual Rebuild Contract is a
docs/spec alignment only slice that records the corrected build authority and
visual/product acceptance contract before PS-039 is rebuilt. Spec:
`specs/64-ps-039a-website-dashboard-build-authority-visual-rebuild-contract.md`.

Current accepted base for PS-039a:
`origin/accepted/proofstudio @ 4ee42823d25fba670b9c2367882d86bc2c62f389`.

The rejected GLM-built PS-039 implementation failed visual/product gate. It
must not be staged, must not be committed, must not be accepted, must not be
repaired by GLM, and must not be restored from discarded working tree. Root
cause: GLM optimized for static proof strings, cards, and safety checks, but
failed the intended product surface: a cinematic premium winning-project
presentation layer.

Corrected build authority: ChatGPT GPT-5.5 Thinking is PM / release
gatekeeper; Codex GPT-5.5 in VS Code is repo builder for PS-039 website and
PS-041 dashboard; Claude 4.6 in Antigravity remains Awwwards Creative Director
/ visual critic; Gemini 3.1 Pro remains large-context researcher / multimodal
reviewer; Gemini 3.5 Flash remains fast variant generator; CodeRabbit remains
later post-build PR/static review layer only; GLM is excluded from PS-039
website and PS-041 dashboard build/repair work.

PS-039a records process and strategy only. It has no implementation code, no
deployment changes, no env/secrets changes, no provider calls, no model calls,
no B2 reads/writes, and no Cloudflare API/DNS/resource/deploy/R2 behavior. It
does not claim implementation exists, does not claim production readiness,
does not claim production security, does not claim production compliance, does
not claim OAuth/auth is implemented, does not claim dashboard is implemented,
does not claim deployment/domain is done, and does not claim CodeRabbit has
reviewed the project.

## 9. Post-PS-034C Roadmap Ledger

The roadmap after PS-034C is the authoritative ordering from the current
accepted state to Devpost submission. The full table lives in
`specs/08-roadmap-slices.md` and in
`docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`. In
summary:

- PS-034C — Winning Roadmap + Master Spec Replan (this replan)
- PS-035 — Review + Approval Workspace (blocked until PS-034C accepted)
- PS-035a — Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest
  Correctness (blocking; should be next implementation slice unless PM
  changes priority)
- PS-035b — Cost Caps + Golden-Fixture Governance
- PS-036 — Archive / Rehydrate / B2 Audit Vault
- PS-037 — Disclosure + Trust Boundary Layer
- PS-037a — Multimodal Proof Layer
- PS-037b — AssemblyAI Transcript/Timestamp Evidence
- PS-037c — Hume or ElevenLabs Voiceover Artifact
- PS-037d — Gemini Campaign Intelligence / Judge Narrative
- PS-037e — Cloudflare Low-Cost Backbone
- PS-038 — Production Readiness + Demo Mode
- PS-038a — Campaign Proof Room (marquee)
- PS-038b — Winning Product Presentation Architecture (docs/spec/roadmap
  alignment; corrects the post-proof-core sequence and records the
  presentation + productization architecture)
- PS-039 — Brand Identity + 3D Marketing Website + Demo Automation Shell
- PS-039a — Website/Dashboard Build Authority + Visual Rebuild Contract
  (docs/spec alignment only; records rejected GLM-built PS-039 implementation
  and corrected build authority before PS-039 rebuild)
- PS-040 — Auth + Account System
- PS-041 — World-Class User Dashboard
- PS-042 — Deployment / Domain / Production Demo Hardening
- PS-043 — Final Submission Pack
- PS-044 — Devpost Package + 3-Minute Demo Script

Note (PS-038b): the historical pre-PS-038b ledger listed PS-039 as Final
Submission Pack, an earlier historical Devpost/demo-script identifier that is
now folded into PS-044, and PS-040 (Product Dashboard + Marketing Website) as
delayed/optional. PS-038b corrects this: the presentation + productization
layer (brand / 3D website, auth, dashboard, deployment hardening) is now
required and is sequenced before the Final Submission Pack.
From PS-039a onward, PS-039a means Website/Dashboard Build Authority + Visual Rebuild Contract only.
PS-038b preserves the accepted history (PS-001 through PS-038a) and does not
rewrite unrelated historical slices.

Decisions:

- PS-035 through PS-038a are accepted.
- PS-038b corrects the post-PS-038a sequence: Final Submission Pack is not
  next; the brand/3D website, auth, dashboard, and deployment hardening slices
  are required before final submission.
- PS-035a was blocking because golden-run manifest correctness is core
  provenance and the golden run previously had a null manifest gap; it is now
  accepted (see 8.9).
- PS-039 through PS-044 are required for the winning submission under the
  PS-038b-corrected sequence.
- PS-039a records that the rejected GLM-built PS-039 implementation failed
  visual/product gate and must not be staged, committed, accepted, repaired by
  GLM, or restored from discarded working tree.
- After PS-039a is accepted, Codex GPT-5.5 in VS Code rebuilds PS-039 from
  accepted base under PM/human screenshot review.
- The PS-031A correction remains authoritative unless later superseded.
- No accepted built slice PS-023 through PS-038a is dropped by this replan.
