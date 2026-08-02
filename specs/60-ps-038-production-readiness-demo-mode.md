# PS-038 — Production Readiness + Demo Mode

## 1. Status

PS-038 — Production Readiness + Demo Mode is currently:

- Spec only.
- Implementation pending. No product code, frontend code, backend code,
  scripts, evidence, AGENTS.md, `.env*`, `render.yaml`, or requirements files
  are changed during this phase.

PS-038 must not be implemented, and no implementation files may be changed,
until this spec is accepted by the PM. The authoritative accepted base is the
dynamic Git ref `origin/accepted/proofstudio`, never a hardcoded commit hash.
At the time of this spec the ref resolves to commit
`3e0c896375947c1d9668204333c12218a6f52981` (the post-PS-037e accepted state).
The ref is the authority; the commit hash is recorded for traceability only
and must not be treated as a hardcoded base.

This spec-only commit touches only this file:
`specs/60-ps-038-production-readiness-demo-mode.md`.

PS-038 must not deploy ProofStudio, must not make any Cloudflare API call, must
not mutate DNS, must not create any Cloudflare resource, must not deploy
Cloudflare Pages, must not deploy Cloudflare Workers, must not perform
Cloudflare R2 live reads, must not perform Cloudflare R2 writes, must not
perform Backblaze B2 writes, must not call any live provider, must not call
any model, must not read or write live B2, must not perform broad B2 scans,
must not change `.env*` / `render.yaml` / requirements / deployment config,
must not mutate any evidence, must not run the frontend, must not run the
backend, must not stage, commit, or push, and must not print secrets during
this phase. PS-038 obeys the root `AGENTS.md` operating law and the validation
policy in `docs/validation/proofstudio-smoke-harness-v1.md`.

PS-038 defines a Production Readiness + Demo Mode layer for judge-facing demo
reliability, readiness posture, local/demo fallback clarity, live dependency
boundaries, and cold-start mitigation evidence/planning. It does not claim
actual production readiness. It does not deploy ProofStudio. It does not change
env/secrets/deployment config. It does not call live providers or models. It
does not call Cloudflare. It does not read/write live B2. It does not create
production security/compliance guarantees.

## 2. Purpose

PS-038 defines a reusable Production Readiness + Demo Mode layer that explains
how ProofStudio can be shown reliably in a judge demo using explicit demo-mode
posture, local/static fallback states, live dependency boundaries, cold-start
mitigation planning, and readiness checklist evidence — while preserving
strict truth boundaries around production readiness, production security,
production compliance, legal compliance, uptime, cost, performance, live
providers, B2, Cloudflare, and deployment. The layer reads only what the
pipeline already recorded (B2 / archive / rehydrate evidence, Genblaze /
manifest evidence, the PS-037 Disclosure + Trust Boundary, the PS-037a
Multimodal Proof Layer, the PS-037b AssemblyAI Transcript/Timestamp Evidence
layer, the PS-037c Voice/Audio Evidence Provider Choice layer, the PS-037d
Gemini Campaign Intelligence / Judge Narrative layer, and the PS-037e
Cloudflare Low-Cost Backbone layer) and renders a consistent production
readiness + demo mode / readiness posture view that makes the demo path,
local fallback, live dependency posture, cold-start mitigation plan, and
readiness checklist inspectable for judges, customers, and demo reviewers.

PS-038 makes the demo path, local fallback, live dependency posture,
cold-start mitigation plan, and readiness checklist explicit, inspectable, and
truth-bounded before the final submission packaging slice (PS-039). The layer
answers, in one consistent place, the basic demo / readiness questions a judge
or demo reviewer asks:

- what demo mode is
- whether demo mode is active or planned
- whether demo mode uses local/golden/checked-in evidence
- whether live dependencies are required for the judge demo
- whether live providers are required
- whether live B2 reads/writes are required
- whether live Cloudflare is required
- whether Cloudflare deployment exists
- whether deployment evidence exists
- whether production readiness evidence exists
- whether production security evidence exists
- whether production compliance evidence exists
- whether cold-start mitigation is planned, implemented, measured, or
  unavailable
- whether startup health evidence exists
- whether cost-control evidence exists
- whether provider fallback evidence exists
- whether failure-mode evidence exists
- whether export/offline evidence exists
- what the app can demo locally/static
- what still requires later production deployment work
- what this layer proves and does not prove

The layer is a demo-mode / readiness-posture / cold-start-mitigation
inspection layer over already-recorded or honestly-unavailable data, not a
live deployment, not a production readiness claim, not a production security
system, not a production compliance system, not an uptime guarantee, not a
cost guarantee, not a performance guarantee, not a cold-start performance
guarantee, not a load test, not a vulnerability scan, not a penetration test,
not an incident-response readiness system, not an SLO/SLA system, not a data
retention compliance system, not a privacy compliance system, not a
Cloudflare API integration, not a DNS change, not a Cloudflare resource
creation, not a Cloudflare Pages deployment, not a Cloudflare Workers
deployment, not a Cloudflare R2 live read, not a Cloudflare R2 write, not a
Backblaze B2 write, not a live B2 read, not a B2 write, not a broad B2 scan,
not a provider call, and not a model call. It makes the existing demo /
readiness framing consistent and judge-safe, and it states honestly what
ProofStudio proves and what ProofStudio does not prove for production
readiness, demo mode, and cold-start mitigation.

PS-038 proves what the pipeline recorded. The layer does not prove live
deployment, production readiness, production security, production compliance,
legal compliance, uptime guarantee, cost guarantee, performance guarantee,
cold-start performance guarantee, load-test coverage, vulnerability scan
coverage, penetration test coverage, incident response readiness, SLO/SLA
guarantee, data retention compliance, privacy compliance, Cloudflare
deployment, Cloudflare availability, Backblaze B2 live availability, provider
availability, model availability, Object Lock, tamper-proof storage,
browser-side B2 byte verification, semantic truth, legal authenticity, human
authorship, C2PA authenticity, campaign performance prediction, marketing
effectiveness proof, or model output truth.

Demo mode may use local/static/checked-in/golden evidence only. The
implementation must default to local/static behavior. No live provider/API/
B2/Cloudflare/model behavior may occur unless a later PM-approved slice
explicitly enables it with env gates, cost controls, rollback, and evidence
boundaries. Naming "demo mode" or "production readiness" as a layer label
does not imply a live deployment, a production readiness claim, a production
security claim, a production compliance claim, an uptime guarantee, a cost
guarantee, a performance guarantee, a cold-start performance guarantee, or any
correctness guarantee. The production readiness layer label does not equal a
production readiness claim. Demo mode does not equal production readiness.
Local demo mode does not equal live deployment. A readiness checklist does not
equal production security. A cold-start mitigation plan does not equal a
measured performance guarantee. A low-cost demo posture does not equal a cost
guarantee. Local fallback does not equal live provider availability.
Checked-in evidence does not equal live B2 availability. A Cloudflare
dependency posture does not equal live Cloudflare availability. Demo/golden
readiness evidence does not equal production compliance.

## 3. Root Cause / Product Gap

ProofStudio already records a deep proof stack: B2 archive + rehydrate evidence
(PS-010, PS-020, PS-021, PS-026, PS-029, PS-036), Genblaze manifest evidence
(PS-028), the Disclosure + Trust Boundary (PS-037), the Multimodal Proof Layer
(PS-037a), the AssemblyAI Transcript/Timestamp Evidence layer (PS-037b), the
Voice/Audio Evidence Provider Choice layer (PS-037c), the Gemini Campaign
Intelligence / Judge Narrative layer (PS-037d), and the Cloudflare Low-Cost
Backbone layer (PS-037e). Each layer is honest about what it proves and what
it does not prove.

Those layers are honest, but none of them makes the demo path, demo-mode
posture, local/static fallback, live dependency boundaries, cold-start
mitigation plan, startup health, cost-control posture, provider fallback,
failure-mode evidence, export/offline evidence, or readiness checklist
explicit in a single inspectable place. There is no place where a judge or
demo reviewer can read what demo mode is, whether demo mode is active or
planned, whether demo mode uses local/golden/checked-in evidence, whether
live dependencies are required for the judge demo, whether live providers are
required, whether live B2 reads/writes are required, whether live Cloudflare
is required, whether Cloudflare deployment exists, whether deployment evidence
exists, whether production readiness evidence exists, whether production
security evidence exists, whether production compliance evidence exists,
whether cold-start mitigation is planned / implemented / measured /
unavailable, whether startup health evidence exists, whether cost-control
evidence exists, whether provider fallback evidence exists, whether
failure-mode evidence exists, whether export/offline evidence exists, what the
app can demo locally/static, what still requires later production deployment
work, and what the demo / readiness posture proves and does not prove. The gap
this creates is judge-safety at the demo / readiness / cold-start boundary,
compounded by the risk of readiness-word overclaim and the risk of mistaking
"demo mode" / "production readiness layer" / "readiness checklist" language
for a production readiness claim, a production security claim, a production
compliance claim, an uptime guarantee, a cost guarantee, a performance
guarantee, or a cold-start performance guarantee. Today:

- no accepted slice records a demo mode plan, a readiness posture view, a
  local/static fallback statement, a golden evidence fallback statement, a
  checked-in evidence fallback statement, a live dependency status, a provider
  dependency status, a B2 dependency status, a Cloudflare dependency status, a
  deployment evidence status, a production security evidence status, a
  production compliance evidence status, a cold-start mitigation plan, a
  startup health status, a cost-control status, a provider fallback status, a
  failure-mode status, an export/offline evidence status, a demo path
  evidence layer, a readiness checklist evidence layer, or a set of honest
  "production deployment not available" / "production readiness evidence not
  available" / "production security evidence not available" / "production
  compliance evidence not available" / "live provider evidence not available"
  / "live B2 evidence not available" / "live Cloudflare evidence not
  available" / "cold-start measurement not available" / "ready for local
  demo" / "planned" / "not claimed" / "unknown" readiness states in a single
  inspectable place.
- a judge reading a proof surface today cannot tell whether the proof stack
  can be shown in a reliable local demo, whether demo mode is active or only
  planned, whether the demo depends on live providers / live B2 / live
  Cloudflare, whether any production deployment exists, whether production
  readiness / production security / production compliance / cold-start
  mitigation / startup health / cost-control / provider fallback /
  failure-mode / export-offline evidence exists, or what the demo / readiness
  posture proves and does not prove. A "production readiness" layer name that
  appears without a clear disclosure boundary looks like a production
  readiness claim; a "demo mode" word that appears without a clear boundary
  looks like a deployment; a "readiness checklist" that appears without a
  clear boundary looks like production security; a "cold-start mitigation
  plan" that appears without a clear boundary looks like a measured
  performance guarantee.

PS-038 closes that gap by adding one shared Production Readiness + Demo Mode
layer — a canonical data module plus a shared component — that the core proof
surfaces render additively. The layer reads only accepted local / golden /
demo evidence and the existing accepted data modules, or exposes explicit
honest "production deployment not available" / "production readiness evidence
not available" / "production security evidence not available" / "production
compliance evidence not available" / "live provider evidence not available" /
"live B2 evidence not available" / "live Cloudflare evidence not available" /
"cold-start measurement not available" / "cold-start mitigation planned" /
"ready for local demo" / "not claimed" / "unknown" / "planned" states. It
does not invent a live deployment, a production readiness claim, a production
security claim, a production compliance claim, a legal compliance claim, an
uptime guarantee, a cost guarantee, a performance guarantee, a cold-start
performance guarantee, a load-test coverage claim, a vulnerability scan
coverage claim, a penetration test coverage claim, an incident response
readiness claim, an SLO/SLA guarantee, a data retention compliance claim, a
privacy compliance claim, a Cloudflare deployment, a Cloudflare availability,
a Backblaze B2 live availability, a provider availability, a model
availability, an Object Lock, a tamper-proof storage, a browser-side B2 byte
verification, a semantic truth, a legal authenticity, a human authorship, a
C2PA authenticity, a campaign performance prediction, a marketing
effectiveness proof, or a model output truth. It is local / static by default:
it adds no deployment changes, no env/secrets changes, no render.yaml changes,
no requirements/dependency changes, no Cloudflare API calls, no DNS mutation,
no Cloudflare resource creation, no Cloudflare Pages deployment, no Cloudflare
Workers deployment, no Cloudflare R2 live reads, no Cloudflare R2 writes, no
Backblaze B2 writes, no provider calls, no model calls, no live B2 reads, no
B2 writes, no broad B2 scans, no new backend, and no new paid service
dependency.

Demo mode is named as a judge-facing posture label for local / golden /
checked-in demo evidence only. Naming demo mode does not imply a live
deployment, a production readiness claim, a production security claim, a
production compliance claim, an uptime guarantee, a cost guarantee, a
performance guarantee, a cold-start performance guarantee, or any correctness
guarantee. The production readiness layer label does not equal a production
readiness claim. The implementation must default to local/static behavior. No
live provider/API/B2/Cloudflare/model behavior may occur unless a later
PM-approved slice explicitly enables it with env gates, cost controls,
rollback, and evidence boundaries. The implementation phase relies on
checked-in local / golden / demo evidence or explicit unavailable states, and
must not require live provider credentials, live model credentials, live B2
credentials, or live Cloudflare credentials.

## 4. User Story

As a reviewer (designer, marketer, reviewer, client, or judge), I want one
honest, consistent Production Readiness + Demo Mode / readiness-posture view,
so that on any core proof surface I can immediately read: what demo mode is;
whether demo mode is active or planned; whether demo mode uses local/golden/
checked-in evidence; whether live dependencies are required for the judge
demo; whether live providers are required; whether live B2 reads/writes are
required; whether live Cloudflare is required; whether Cloudflare deployment
exists; whether deployment evidence exists; whether production readiness
evidence exists; whether production security evidence exists; whether
production compliance evidence exists; whether cold-start mitigation is
planned, implemented, measured, or unavailable; whether startup health
evidence exists; whether cost-control evidence exists; whether provider
fallback evidence exists; whether failure-mode evidence exists; whether
export/offline evidence exists; what the app can demo locally/static; what
still requires later production deployment work; what this layer proves and
does not prove; and whether live deployment, production readiness, production
security, production compliance, legal compliance, uptime guarantee, cost
guarantee, performance guarantee, cold-start performance guarantee, load-test
coverage, vulnerability scan coverage, penetration test coverage, incident
response readiness, SLO/SLA guarantee, data retention compliance, privacy
compliance, Cloudflare deployment, Cloudflare availability, Backblaze B2 live
availability, provider availability, model availability, Object Lock,
tamper-proof storage, browser-side B2 byte verification, semantic truth,
legal authenticity, human authorship, C2PA authenticity, campaign performance
prediction, marketing effectiveness proof, or model output truth is claimed —
and so I never mistake a demo mode label for a live deployment, a production
readiness layer for a production readiness claim, a readiness checklist for
production security, a cold-start mitigation plan for a measured performance
guarantee, a low-cost demo posture for a cost guarantee, local fallback for
live provider availability, checked-in evidence for live B2 availability, a
Cloudflare dependency posture for live Cloudflare availability, or
demo/golden readiness evidence for production compliance.

As a customer, I want the demo path and readiness posture stated honestly in
a single place that says what the demo / readiness layer proves, what it does
not prove, what is ready for local demo, what is planned, what is not
available, what is not claimed, and whether any live deployment exists.

As a demo presenter, I want a reusable Production Readiness + Demo Mode layer
that is useful in a three-minute hackathon demo: a compact demo / readiness
posture summary that lists the demo mode status, the readiness posture, the
local/static fallback, the live dependency boundaries, the cold-start
mitigation plan, and the honest "production deployment not available" /
"production readiness evidence not available" / "production security evidence
not available" / "production compliance evidence not available" / "live
provider evidence not available" / "live B2 evidence not available" / "live
Cloudflare evidence not available" / "cold-start measurement not available" /
"cold-start mitigation planned" / "ready for local demo" / "planned" /
"unknown" / "not claimed" states, plus an expanded readiness-posture /
readiness-checklist panel that states, verbatim, what the demo / readiness
layer proves, what it does not prove, what is unavailable, what is not
claimed, what is planned, what is ready for local demo, and what the shared
disclosure boundary is — all working offline from accepted local / golden /
demo fixtures, with no deployment changes, no env/secrets changes, no
render.yaml changes, no requirements/dependency changes, no Cloudflare API
calls, no DNS mutation, no Cloudflare resource creation, no Cloudflare Pages
deployment, no Cloudflare Workers deployment, no Cloudflare R2 live reads, no
Cloudflare R2 writes, no Backblaze B2 writes, no provider calls, no model
calls, no live B2 reads, no B2 writes, and no broad B2 scans.

## 5. Current Accepted Base

The current accepted base for PS-038 is:

- branch: `accepted/proofstudio`
- ref: `origin/accepted/proofstudio` (the authoritative source of truth; the
  ref is the authority, not any hardcoded commit hash)
- commit the ref resolves to at the time of this spec:
  `3e0c896375947c1d9668204333c12218a6f52981`
- this is the post-PS-037e accepted state: the Disclosure + Trust Boundary
  Layer from PS-037 is in place (`apps/web/src/trustBoundary.ts` +
  `apps/web/src/TrustBoundaryLayer.tsx`); the Multimodal Proof Layer from
  PS-037a is in place (`apps/web/src/multimodalProof.ts` +
  `apps/web/src/MultimodalProofLayer.tsx`); the AssemblyAI
  Transcript/Timestamp Evidence layer from PS-037b is in place
  (`apps/web/src/assemblyAITranscriptEvidence.ts` +
  `apps/web/src/TranscriptTimestampEvidenceLayer.tsx`); the Voice/Audio
  Evidence Provider Choice layer from PS-037c is in place
  (`apps/web/src/voiceAudioEvidenceChoice.ts` +
  `apps/web/src/VoiceAudioEvidenceChoiceLayer.tsx`); the Gemini Campaign
  Intelligence / Judge Narrative layer from PS-037d is in place
  (`apps/web/src/geminiCampaignIntelligence.ts` +
  `apps/web/src/CampaignIntelligenceJudgeNarrativeLayer.tsx`); the Cloudflare
  Low-Cost Backbone layer from PS-037e is in place
  (`apps/web/src/cloudflareLowCostBackbone.ts` +
  `apps/web/src/CloudflareLowCostBackboneLayer.tsx`); the Archive / Rehydrate
  / B2 Audit Vault is in place from PS-036; the Review + Approval Workspace is
  in place from PS-035; the root `AGENTS.md` operating law is in place
  (PS-035D); the accepted-base-pointer-drift guard is in place (PS-035E); the
  central regression gate is non-mutating by default from PS-035C; the
  golden-fixture digest freeze is in place from PS-035B; the golden-run
  manifest carries a real non-null `manifest_uri` and a real 64-hex
  `manifest_hash` from PS-035A.

PS-038 must start from `origin/accepted/proofstudio`, not from `main`.

Relevant accepted facts at this base that PS-038 builds on (PS-038 must not
mutate these and must not change their values):

- the central regression gate (`scripts/proofstudio_regression_gate.py`)
  supports `--current`, `--frontend`, `--no-frontend`, `--check-only`,
  `--report-out`, and `--write-report` (PS-035C accepted)
- the gate is non-mutating by default for any current slice that is not
  PS-034A (PS-035C accepted)
- the root `AGENTS.md` operating law exists at the repository root (PS-035D
  accepted), including the rule that hidden Git flags `h` and `S` must be
  checked explicitly by reading `git ls-files -v` and failing when `line[0]`
  is `h` or `S`
- the accepted-base-pointer-drift guard exists (PS-035E accepted)
- the golden-fixture digest freeze exists at
  `docs/evidence/golden-fixture-digests.json` (PS-035B accepted)
- the golden-run manifest carries a real non-null `manifest_uri` and a real
  64-hex `manifest_hash` (PS-035A accepted), and the golden demo manifest at
  `docs/evidence/demo/golden-demo-run.json` carries `archive_uri`,
  `archive_sha256`, `manifest_uri`, `manifest_hash`, `rehydrate_source`, and
  an honest `unavailable_fields` map for values that are not present
- the PS-037 Disclosure + Trust Boundary Layer exists and is rendered on the
  core proof surfaces; PS-038 integrates with it and does not weaken it
- the PS-037a Multimodal Proof Layer exists and is rendered on the core proof
  surfaces; PS-038 cross-references PS-037a and does not weaken it
- the PS-037b AssemblyAI Transcript/Timestamp Evidence layer exists and is
  rendered on the core proof surfaces; PS-038 cross-references PS-037b and
  does not weaken it
- the PS-037c Voice/Audio Evidence Provider Choice layer exists and is
  rendered on the core proof surfaces; PS-038 cross-references PS-037c and
  does not weaken it
- the PS-037d Gemini Campaign Intelligence / Judge Narrative layer exists and
  is rendered on the core proof surfaces; PS-038 cross-references PS-037d and
  does not weaken it
- the PS-037e Cloudflare Low-Cost Backbone layer exists and is rendered on
  the core proof surfaces; PS-038 cross-references PS-037e and does not
  weaken it
- the existing shared component classes (`.trust-boundary`,
  `.trust-boundary-layer*`, the multimodal proof layer classes, the
  transcript/timestamp evidence layer classes, the voice/audio evidence
  provider choice layer classes, the campaign-intelligence / judge-narrative
  layer classes, the cloudflare-low-cost-backbone layer classes, pills,
  cards, `JsonExpander`) already exist in `apps/web/src/styles.css`

## 6. Scope

PS-038 is a product slice. It adds a reusable Production Readiness + Demo
Mode layer (a shared data module plus a shared component) and renders it
additively on the core proof surfaces. It is local / static by default: it
must work without deployment changes, without env/secrets changes, without
render.yaml changes, without requirements/dependency changes, without
Cloudflare API calls, without DNS mutation, without Cloudflare resource
creation, without Cloudflare Pages deployment, without Cloudflare Workers
deployment, without Cloudflare R2 live reads, without Cloudflare R2 writes,
without Backblaze B2 writes, without provider calls, without model calls,
without live B2 reads, without B2 writes, and without broad B2 scans, by
reading accepted local / golden / demo fixtures and existing accepted data
modules, or by surfacing explicit honest "production deployment not
available" / "production readiness evidence not available" / "production
security evidence not available" / "production compliance evidence not
available" / "live provider evidence not available" / "live B2 evidence not
available" / "live Cloudflare evidence not available" / "cold-start
measurement not available" / "cold-start mitigation planned" / "ready for
local demo" / "planned" / "not claimed" / "unknown" states.

PS-038 owns the demo-mode / readiness-posture / cold-start-mitigation
evidence and planning layer only. It must:

1. Add a shared, canonical Production Readiness + Demo Mode data module
   (`apps/web/src/productionReadinessDemoMode.ts`, or the project's accepted
   equivalent) that exposes one consistent set of demo / readiness concepts,
   the demo mode plan, the readiness posture, the local/static fallback, the
   golden evidence fallback, the checked-in evidence fallback, the live
   dependency status, the provider dependency status, the B2 dependency
   status, the Cloudflare dependency status, the deployment evidence status,
   the production security evidence status, the production compliance
   evidence status, the cold-start mitigation status, the startup health
   status, the cost-control status, the provider fallback status, the
   failure-mode status, the export/offline evidence status, the demo path
   evidence, the readiness checklist evidence, honest "production deployment
   not available" / "production readiness evidence not available" /
   "production security evidence not available" / "production compliance
   evidence not available" / "live provider evidence not available" / "live
   B2 evidence not available" / "live Cloudflare evidence not available" /
   "cold-start measurement not available" / "cold-start mitigation planned"
   / "ready for local demo" / "planned" / "not claimed" / "unknown" states,
   and deferred / unavailable later-slice states for every core proof surface.
2. Add a shared Production Readiness + Demo Mode component
   (`apps/web/src/ProductionReadinessDemoModeLayer.tsx`, or the project's
   accepted equivalent) that renders the layer, including an optional compact
   demo / readiness posture summary and an expanded readiness-posture /
   readiness-checklist panel pattern, reading only from
   `apps/web/src/productionReadinessDemoMode.ts`.
3. Render the Production Readiness + Demo Mode layer additively on the
   required core proof surfaces (section 10.3) that are present in this repo
   so the demo / readiness / cold-start-mitigation framing is consistent
   everywhere the demo path / readiness posture is shown.
4. State, for the demo path / readiness posture / cold-start mitigation,
   "what ProofStudio proves" and "what ProofStudio does not prove."
5. Surface the canonical Production Readiness + Demo Mode concepts
   (section 10.2): Production Readiness + Demo Mode, demo mode, readiness
   posture, production readiness status, demo mode status, local demo status,
   judge demo status, local/static fallback, golden evidence fallback,
   checked-in evidence fallback, live dependency status, provider dependency
   status, B2 dependency status, Cloudflare dependency status, deployment
   evidence status, production security evidence status, production
   compliance evidence status, cold-start mitigation status, startup health
   status, cost-control status, provider fallback status, failure-mode
   status, export/offline evidence status, demo path evidence, readiness
   checklist evidence, local verification, live verification status,
   disclosure boundary, not claimed, unknown, planned, ready for local demo,
   local/demo evidence, production deployment not available, production
   readiness evidence not available, production security evidence not
   available, production compliance evidence not available, live provider
   evidence not available, live B2 evidence not available, live Cloudflare
   evidence not available, cold-start measurement not available, cold-start
   mitigation planned, and final submission packaging deferred to PS-039.
6. Surface the honest unavailable / not-claimed / planned states
   (section 10.6) verbatim so no reviewer mistakes an absent demo / readiness
   / cold-start value for a hidden proof, and no reviewer mistakes a demo
   mode label, a production readiness layer label, or a readiness checklist
   for a live deployment, a production readiness claim, a production security
   claim, a production compliance claim, a cost guarantee, an uptime
   guarantee, a performance guarantee, or a cold-start performance guarantee.
7. Surface the canonical Production Readiness + Demo Mode de-escalation
   pairs (section 10.7) verbatim so no judge mistakes a strong-sounding demo
   mode label, production readiness layer label, readiness checklist,
   cold-start mitigation plan, local fallback, checked-in evidence, Cloudflare
   dependency posture, or low-cost demo posture for a stronger guarantee.
8. Surface the canonical Production Readiness + Demo Mode negative boundary
   strings (section 10.8) verbatim.
9. Integrate with the PS-037 TrustBoundaryLayer (render alongside it; reuse
   the shared disclosure concepts; do not duplicate or weaken the PS-037
   boundary).
10. Integrate / cross-reference with the PS-037a MultimodalProofLayer (render
    alongside it; surface an honest multimodal proof cross-reference; do not
    duplicate or weaken the PS-037a layer).
11. Integrate / cross-reference with the PS-037b TranscriptTimestampEvidenceLayer
    (render alongside it; surface an honest transcript/timestamp
    cross-reference; do not duplicate or weaken the PS-037b layer).
12. Integrate / cross-reference with the PS-037c VoiceAudioEvidenceChoiceLayer
    (render alongside it; surface an honest voice/audio evidence
    cross-reference; do not duplicate or weaken the PS-037c layer).
13. Integrate / cross-reference with the PS-037d
    CampaignIntelligenceJudgeNarrativeLayer (render alongside it; surface an
    honest campaign intelligence cross-reference; do not duplicate or weaken
    the PS-037d layer).
14. Integrate / cross-reference with the PS-037e CloudflareLowCostBackboneLayer
    (render alongside it; surface an honest Cloudflare low-cost backbone
    cross-reference; do not duplicate or weaken the PS-037e layer).
15. Preserve the existing per-surface artifact / boundary panels; the shared
    Production Readiness + Demo Mode layer complements them. PS-038 must not
    delete or weaken any existing per-surface non-claim, per-surface artifact
    record, the PS-037 disclosure contract, the PS-037a multimodal proof
    contract, the PS-037b transcript/timestamp contract, the PS-037c
    voice/audio evidence provider choice contract, the PS-037d campaign
    intelligence / judge narrative contract, or the PS-037e Cloudflare
    low-cost backbone contract.
16. Be demo-friendly and judge-friendly: useful in a three-minute demo, no
    generic readiness hype copy, no unsupported claims, no faked live
    deployment, no faked production readiness, no faked production security,
    no faked production compliance, no faked cost guarantee, no faked uptime
    guarantee, no faked performance guarantee, no faked cold-start performance
    guarantee, no faked load-test coverage, no faked vulnerability scan
    coverage, no faked penetration test coverage, no faked incident response
    readiness, no faked SLO/SLA guarantee, no faked data retention compliance,
    no faked privacy compliance.
17. Work without deployment changes, without env/secrets changes, without
    render.yaml changes, without requirements/dependency changes, without
    Cloudflare API calls, without DNS mutation, without Cloudflare resource
    creation, without Cloudflare Pages deployment, without Cloudflare Workers
    deployment, without Cloudflare R2 live reads, without Cloudflare R2
    writes, without Backblaze B2 writes, without provider calls, without
    model calls, without live B2 reads, without B2 writes, and without broad
    B2 scans, by using accepted local / golden / demo data or existing
    accepted data paths.
18. Not mutate any prior evidence. Any PS-038-owned evidence lives only under
    `docs/evidence/ps-038/`.
19. Not change the golden run canonical constants, the historical contracts
    the regression gate verifies, any provider / B2 / model behavior, the
    PS-037 disclosure contract, the PS-037a multimodal proof contract, the
    PS-037b transcript/timestamp contract, the PS-037c voice/audio evidence
    provider choice contract, the PS-037d campaign intelligence / judge
    narrative contract, or the PS-037e Cloudflare low-cost backbone contract.

## 7. Non-goals

PS-038 must not:

- do not implement product code during the spec-only phase
- do not make any deployment change (no deployment changes)
- do not make any env/secrets change (no env/secrets changes)
- do not make any `render.yaml` change (no render.yaml changes)
- do not make any requirements/dependency change (no requirements/dependency
  changes)
- do not make any Cloudflare API call (no Cloudflare API calls)
- do not mutate DNS (no DNS mutation)
- do not create any Cloudflare resource (no Cloudflare resource creation)
- do not deploy Cloudflare Pages (no Cloudflare Pages deployment)
- do not deploy Cloudflare Workers (no Cloudflare Workers deployment)
- do not perform Cloudflare R2 live reads (no Cloudflare R2 live reads)
- do not perform Cloudflare R2 writes (no Cloudflare R2 writes)
- do not perform Backblaze B2 writes (no Backblaze B2 writes)
- do not make any live provider call (no provider calls)
- do not make any model call (no model calls)
- do not read live B2 (no live B2 reads)
- do not write B2 (no B2 writes)
- do not perform broad B2 scans (no broad B2 scans)
- do not implement live production deployment
- do not implement the later or out-of-scope capabilities:
  - production readiness, production security, production compliance, legal
    compliance, uptime guarantee, cost guarantee, performance guarantee,
    cold-start performance guarantee, load-test coverage, vulnerability scan
    coverage, penetration test coverage, incident response readiness, SLO/SLA
    guarantee, data retention compliance, privacy compliance, DNS ownership,
    Object Lock, tamper-proof storage, or browser-side B2 byte verification
    (PS-038 must only reserve honest "not claimed" / "planned" / "unknown"
    states for these; it must not fake them)
  - CI, billing, deployment, auth, teams, permissions, or a full enterprise DAM
- do not edit product code under `src/**`
- do not edit frontend code under `apps/**`
- do not edit scripts under `scripts/**`
- do not edit evidence under `docs/evidence/**`
- do not edit `AGENTS.md`
- do not edit `.env*`
- do not edit `render.yaml`
- do not edit requirements files
- do not run the frontend
- do not run the backend
- do not claim live deployment
- do not claim production readiness
- do not claim production security
- do not claim production compliance
- do not claim legal compliance
- do not claim uptime guarantee
- do not claim cost guarantee
- do not claim performance guarantee
- do not claim cold-start performance guarantee
- do not claim load-test coverage
- do not claim vulnerability scan coverage
- do not claim penetration test coverage
- do not claim incident response readiness
- do not claim SLO/SLA guarantee
- do not claim data retention compliance
- do not claim privacy compliance
- do not claim Cloudflare deployment
- do not claim Cloudflare availability
- do not claim Backblaze B2 live availability
- do not claim provider availability
- do not claim model availability
- do not claim cold-start mitigation implementation unless actually implemented
  and validated
- do not claim Object Lock / tamper-proof storage unless implemented and
  verified
- do not claim browser-side B2 byte verification unless implemented and
  verified
- do not claim semantic truth
- do not claim legal authenticity
- do not claim human authorship
- do not claim C2PA authenticity unless implemented and verified
- do not claim campaign performance prediction
- do not claim marketing effectiveness proof
- do not claim model output truth
- do not delete or weaken any existing per-surface truth-boundary panel,
  non-claim, artifact record, the PS-037 disclosure contract, the PS-037a
  multimodal proof contract, the PS-037b transcript/timestamp contract, the
  PS-037c voice/audio evidence provider choice contract, the PS-037d campaign
  intelligence / judge narrative contract, or the PS-037e Cloudflare low-cost
  backbone contract
- do not add a new backend, a new Cloudflare client, a new provider wrapper, a
  new model client, a new B2 client, a new B2 write path, a new broad B2 scan
  path, a new env variable, a new paid service dependency, or any deployment
  change
- do not change the golden run canonical constants
- do not change the historical contracts the regression gate verifies
- do not change the PS-037 disclosure contract
- do not change the PS-037a multimodal proof contract
- do not change the PS-037b transcript/timestamp contract
- do not change the PS-037c voice/audio evidence provider choice contract
- do not change the PS-037d campaign intelligence / judge narrative contract
- do not change the PS-037e Cloudflare low-cost backbone contract
- do not introduce a control name containing `KEY`, `TOKEN`, or `SECRET`
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not run recursive smokes
- do not use generic readiness hype copy or unsupported claims
- do not create duplicate context-blind overclaim scanners in chat/spec
  guidance; the PS-038 smoke and its evidence report are the source of truth
  for slice overclaim validation; do not scan smoke guard fixtures as product
  claims

PS-038 only edits this spec file in the spec-only phase.
Implementation-phase candidate files are listed in section 8.

## 8. Implementation Candidate Files

The following are implementation-phase candidates only, clearly marked as
implementation-phase only. They are **not** for this spec-only commit. They are
listed so the implementation phase has a grounded file plan that follows
existing app conventions (each surface has a PascalCase `.tsx` component, a
camelCase `.ts` data module, a smoke script, and an evidence directory).

Shared layer (new files):
- `apps/web/src/productionReadinessDemoMode.ts` (new) — the canonical
  camelCase Production Readiness + Demo Mode data module. Exposes the single
  shared set of demo / readiness concepts, the demo mode plan, the readiness
  posture, the local/static fallback, the golden evidence fallback, the
  checked-in evidence fallback, the live dependency status, the provider
  dependency status, the B2 dependency status, the Cloudflare dependency
  status, the deployment evidence status, the production security evidence
  status, the production compliance evidence status, the cold-start mitigation
  status, the startup health status, the cost-control status, the provider
  fallback status, the failure-mode status, the export/offline evidence
  status, the demo path evidence, the readiness checklist evidence, the
  cross-references (B2 / manifest / rehydrate / trust boundary / multimodal
  proof / transcript/timestamp / voice/audio / campaign intelligence /
  cloudflare low-cost backbone), honest "production deployment not available"
  / "production readiness evidence not available" / "production security
  evidence not available" / "production compliance evidence not available" /
  "live provider evidence not available" / "live B2 evidence not available" /
  "live Cloudflare evidence not available" / "cold-start measurement not
  available" / "cold-start mitigation planned" / "ready for local demo" /
  "planned" / "not claimed" / "unknown" states, deferred later-slice states,
  de-escalation pairs, negative boundary strings, and not-claimed / unknown /
  planned status used by every core proof surface. Same convention as
  `cloudflareLowCostBackbone.ts`, `geminiCampaignIntelligence.ts`,
  `voiceAudioEvidenceChoice.ts`, `assemblyAITranscriptEvidence.ts`,
  `multimodalProof.ts`, `trustBoundary.ts`, `b2Evidence.ts`,
  `b2RehydrateComparison.ts`, `judgeEvidencePack.ts`, etc. Demo mode and the
  production readiness layer label are named for judge-facing posture labeling
  only; the module must not contain a live provider call, a live model call, a
  Cloudflare API call, a live B2 read, or a deployment change.
- `apps/web/src/ProductionReadinessDemoModeLayer.tsx` (new) — the shared
  Production Readiness + Demo Mode component. Accepts the existing `variant`
  convention (for example `variant="panel"` for an expanded readiness-posture
  / readiness-checklist panel and `variant="summary"` / `variant="badge"` for
  a compact demo / readiness posture summary), reads only from
  `apps/web/src/productionReadinessDemoMode.ts`, and renders the Production
  Readiness + Demo Mode layer with no deployment changes, no env/secrets
  changes, no render.yaml changes, no requirements/dependency changes, no
  Cloudflare API calls, no DNS mutation, no Cloudflare resource creation, no
  Cloudflare Pages deployment, no Cloudflare Workers deployment, no Cloudflare
  R2 live reads, no Cloudflare R2 writes, no Backblaze B2 writes, no provider
  calls, no model calls, and no live B2 reads. Rendered alongside the existing
  `TrustBoundaryLayer` (PS-037), `MultimodalProofLayer` (PS-037a),
  `TranscriptTimestampEvidenceLayer` (PS-037b),
  `VoiceAudioEvidenceChoiceLayer` (PS-037c),
  `CampaignIntelligenceJudgeNarrativeLayer` (PS-037d), and
  `CloudflareLowCostBackboneLayer` (PS-037e).

Additive use on core proof surfaces (existing files, edited additively only):
- `apps/web/src/JudgeCockpitHome.tsx` (PS-023) — render the Production
  Readiness + Demo Mode layer on the home surface.
- `apps/web/src/B2EvidenceExplorer.tsx` (PS-026) — render the Production
  Readiness + Demo Mode layer (B2 evidence cross-reference).
- `apps/web/src/B2RehydrateComparison.tsx` (PS-029) — render the Production
  Readiness + Demo Mode layer (rehydrate evidence cross-reference).
- `apps/web/src/ManifestVerificationPanel.tsx` (PS-028) — render the
  Production Readiness + Demo Mode layer (manifest evidence cross-reference).
- `apps/web/src/B2AuditVault.tsx` (PS-036) — render the Production Readiness +
  Demo Mode layer (B2 / rehydrate evidence cross-reference audit).
- `apps/web/src/ReviewApprovalWorkspace.tsx` (PS-035) — render the Production
  Readiness + Demo Mode layer (the reviewable artifact's demo / readiness
  posture).
- `apps/web/src/JudgeEvidencePack.tsx` (PS-031) — render the Production
  Readiness + Demo Mode layer (export-pack demo / readiness posture summary).
- `apps/web/src/PublicPassportPage.tsx` (PS-019) — render the Production
  Readiness + Demo Mode layer (provenance passport demo path / readiness
  posture).
- `apps/web/src/App.tsx` (PS-013 / PS-014) — render the Production Readiness +
  Demo Mode layer on the Review Room, complementing the existing asset /
  manifest / evidence panels, the PS-037 disclosure layer, the PS-037a
  multimodal proof layer, the PS-037b transcript/timestamp evidence layer, the
  PS-037c voice/audio evidence provider choice layer, the PS-037d campaign
  intelligence / judge narrative layer, and the PS-037e Cloudflare low-cost
  backbone layer.

Additive styles (existing file, additive classes only):
- `apps/web/src/styles.css` — add only the classes needed for the Production
  Readiness + Demo Mode layer (demo-mode pills, readiness-posture pills,
  production-readiness-status rows, demo-mode-status rows, local-demo-status
  rows, judge-demo-status rows, local-static-fallback rows,
  golden-evidence-fallback rows, checked-in-evidence-fallback rows,
  live-dependency-status pills, provider-dependency-status pills,
  b2-dependency-status pills, cloudflare-dependency-status pills,
  deployment-evidence-status pills, production-security-evidence-status pills,
  production-compliance-evidence-status pills, cold-start-mitigation-status
  pills, startup-health-status pills, cost-control-status pills,
  provider-fallback-status pills, failure-mode-status pills,
  export-offline-evidence-status pills, demo-path-evidence rows,
  readiness-checklist-evidence rows, cross-reference pills, unavailable /
  not-claimed / planned / unknown / ready-for-local-demo pills). No global
  style rewrite. PS-038 must not remove or weaken the existing
  `.trust-boundary-layer*` classes from PS-037, the multimodal proof layer
  classes from PS-037a, the transcript/timestamp evidence layer classes from
  PS-037b, the voice/audio evidence provider choice layer classes from
  PS-037c, the campaign-intelligence / judge-narrative layer classes from
  PS-037d, or the cloudflare-low-cost-backbone layer classes from PS-037e.

Backend (`src/proofstudio`) — none:
- PS-038 is a frontend-only Production Readiness + Demo Mode layer over
  existing accepted data. No backend change is expected. If any read-only
  reuse of an accepted data path is needed, it must reuse the existing
  accepted data paths under `src/proofstudio/api/` and
  `src/proofstudio/provenance/` without calling Cloudflare, without calling
  any provider, without calling any model, without reading live B2, without
  mutating DNS, and without creating any Cloudflare resource. No new provider
  wiring, no model client, no Cloudflare client, no new B2 client, no new B2
  write path, no new broad B2 scan path. If no backend change is needed, none
  is made.

Smoke (scripts):
- `scripts/ps038_production_readiness_demo_mode_smoke.py` (new) — the PS-038
  feature smoke. Must reuse `scripts/smoke_lib.py` for shared validation logic
  and must implement its own explicit `h` / `S` hidden-Git-flags checker (see
  section 14). Local / static only.

Spec / docs:
- `specs/07-master-spec-plan.md` — implementation-phase cross-reference only
  (register PS-038 acceptance). Must not change any historical item or golden
  constant.
- `specs/08-roadmap-slices.md` — implementation-phase status update only.
- `docs/validation/proofstudio-smoke-harness-v1.md` — implementation-phase
  PS-038 note only, additive, must not weaken any existing PS-034A / PS-035C
  contract.
- `docs/ps-038-production-readiness-demo-mode-proof.md` (new) — the PS-038
  proof doc.

Evidence:
- `docs/evidence/ps-038/production-readiness-demo-mode-report.json` (new) —
  the only evidence PS-038 may write, and only when `--write-evidence` is
  explicit.

Any edit to `src/proofstudio/**` during implementation requires the backend
change to remain read-only over accepted data and to make no Cloudflare API
call, no provider call, no model call, no live B2 read, no DNS mutation, and
no Cloudflare resource creation.

## 9. Forbidden files Unless PM-approved Later

PS-038 implementation must not touch without explicit PM approval:

- `AGENTS.md`
- `.env*`
- `render.yaml`
- requirements files
- `docs/evidence/**` paths other than `docs/evidence/ps-038/**`
- any prior-slice evidence prefix (for example `docs/evidence/ps-037e/**`,
  `docs/evidence/ps-037d/**`, `docs/evidence/ps-037c/**`,
  `docs/evidence/ps-037b/**`, `docs/evidence/ps-037a/**`,
  `docs/evidence/ps-037/**`, `docs/evidence/ps-036/**`,
  `docs/evidence/ps-035/**`, `docs/evidence/ps-031/**`,
  `docs/evidence/ps-029/**`, `docs/evidence/ps-026/**`,
  `docs/evidence/ps-021/**`, `docs/evidence/demo/golden-demo-run.json`,
  `docs/evidence/golden-fixture-digests.json`)
- `scripts/proofstudio_regression_gate.py` (the central gate is not owned by
  PS-038)
- `scripts/smoke_lib.py` (shared library; PS-038 must not mutate shared
  validation behavior)
- any provider wrapper under `src/proofstudio/providers/**` (PS-038 owns no
  live provider behavior)
- any model client / model wrapper (PS-038 makes no model calls)
- any B2 client / storage write path (PS-038 performs no live B2 read, no B2
  write, and no broad B2 scan)
- any Cloudflare client / live Cloudflare integration path (PS-038 names
  Cloudflare for dependency posture labeling only; no live Cloudflare API
  call, no DNS mutation, no Cloudflare resource creation, no Cloudflare Pages
  deployment, no Cloudflare Workers deployment, no Cloudflare R2 live read,
  and no Cloudflare R2 write is allowed unless a later PM-approved slice
  explicitly enables it with env gates, cost controls, rollback, and evidence
  boundaries)
- any DNS mutation path (PS-038 performs no DNS mutation)
- any deployment config path (PS-038 makes no deployment change)
- the PS-037 disclosure contract files (`apps/web/src/trustBoundary.ts`,
  `apps/web/src/TrustBoundaryLayer.tsx`) except for additive integration; any
  change that weakens or duplicates the PS-037 boundary is forbidden
- the PS-037a multimodal proof contract files
  (`apps/web/src/multimodalProof.ts`, `apps/web/src/MultimodalProofLayer.tsx`)
  except for additive cross-reference; any change that weakens, duplicates, or
  removes the PS-037a contract is forbidden
- the PS-037b transcript/timestamp contract files
  (`apps/web/src/assemblyAITranscriptEvidence.ts`,
  `apps/web/src/TranscriptTimestampEvidenceLayer.tsx`) except for additive
  cross-reference; any change that weakens, duplicates, or removes the PS-037b
  contract is forbidden
- the PS-037c voice/audio evidence provider choice contract files
  (`apps/web/src/voiceAudioEvidenceChoice.ts`,
  `apps/web/src/VoiceAudioEvidenceChoiceLayer.tsx`) except for additive
  cross-reference; any change that weakens, duplicates, or removes the PS-037c
  contract is forbidden
- the PS-037d campaign intelligence / judge narrative contract files
  (`apps/web/src/geminiCampaignIntelligence.ts`,
  `apps/web/src/CampaignIntelligenceJudgeNarrativeLayer.tsx`) except for
  additive cross-reference; any change that weakens, duplicates, or removes
  the PS-037d contract is forbidden
- the PS-037e Cloudflare low-cost backbone contract files
  (`apps/web/src/cloudflareLowCostBackbone.ts`,
  `apps/web/src/CloudflareLowCostBackboneLayer.tsx`) except for additive
  cross-reference; any change that weakens, duplicates, or removes the PS-037e
  contract is forbidden

The only implementation-phase files allowed without PM approval are those in
section 8. Any other path requires explicit PM approval.

## 10. Production Readiness + Demo Mode Product Contract

PS-038 defines the following contract for the Production Readiness + Demo Mode
layer.

### 10.1 Layer identity

- It is a reusable Production Readiness + Demo Mode layer, not a live
  deployment, not a production readiness claim, not a production security
  system, not a production compliance system, not an uptime guarantee, not a
  cost guarantee, not a performance guarantee, not a cold-start performance
  guarantee, not a load test, not a vulnerability scan, not a penetration
  test, not an incident-response readiness system, not an SLO/SLA system, not
  a data retention compliance system, not a privacy compliance system, not a
  DNS change, not a Cloudflare resource creation, not a new route, and not a
  new backend endpoint.
- It is demo-path-and-readiness-posture-over-recorded-proof by design: it
  reads what the pipeline already recorded and renders a consistent demo mode
  / readiness posture / cold-start mitigation plan. It is not a live
  deployment, not a hosting system, not a deployment engine, and not a
  production readiness engine.
- It is purely client-side by default: it makes no Cloudflare API call,
  mutates no DNS, creates no Cloudflare resource, deploys no Cloudflare Pages,
  deploys no Cloudflare Workers, performs no Cloudflare R2 live read, performs
  no Cloudflare R2 write, performs no Backblaze B2 write, calls no provider,
  calls no model, reads no B2 object, exposes no arbitrary `run_id` input,
  performs no browser-side B2 byte verification, performs no broad B2 scan,
  writes no B2 object, and changes no deployment / env / render.yaml /
  requirements config.
- It is sourced from accepted local / golden / demo data and existing accepted
  data modules only, or from explicit honest "production deployment not
  available" / "production readiness evidence not available" / "production
  security evidence not available" / "production compliance evidence not
  available" / "live provider evidence not available" / "live B2 evidence not
  available" / "live Cloudflare evidence not available" / "cold-start
  measurement not available" / "cold-start mitigation planned" / "ready for
  local demo" / "planned" / "not claimed" / "unknown" states.
- It makes the demo / readiness / cold-start-mitigation framing consistent on
  every core proof surface. It does not invent new live deployments, new
  production readiness claims, new production security claims, new production
  compliance claims, new legal compliance claims, new uptime guarantees, new
  cost guarantees, new performance guarantees, new cold-start performance
  guarantees, new load-test coverage, new vulnerability scan coverage, new
  penetration test coverage, new incident response readiness, new SLO/SLA
  guarantees, new data retention compliance, new privacy compliance, new
  Cloudflare deployments, new Cloudflare availability, new Backblaze B2 live
  availability, new provider availability, or new model availability; it
  states the existing recorded demo / readiness posture consistently and
  honestly, and it states honest "production deployment not available" /
  "production readiness evidence not available" / "production security
  evidence not available" / "production compliance evidence not available" /
  "live provider evidence not available" / "live B2 evidence not available" /
  "live Cloudflare evidence not available" / "cold-start measurement not
  available" / "cold-start mitigation planned" / "ready for local demo" /
  "planned" / "not claimed" / "unknown" states where no evidence exists.
- Demo mode is named as a judge-facing posture label for local / golden /
  checked-in demo evidence only. Naming demo mode does not imply a live
  deployment, a production readiness claim, a production security claim, a
  production compliance claim, an uptime guarantee, a cost guarantee, a
  performance guarantee, a cold-start performance guarantee, or any
  correctness guarantee. Demo mode does not equal production readiness. Local
  demo mode does not equal live deployment.
- The production readiness layer label does not equal a production readiness
  claim. The readiness checklist does not equal production security. The
  cold-start mitigation plan does not equal a measured performance guarantee.
  The low-cost demo posture does not equal a cost guarantee. Local fallback
  does not equal live provider availability. Checked-in evidence does not
  equal live B2 availability. The Cloudflare dependency posture does not equal
  live Cloudflare availability. Demo/golden readiness evidence does not equal
  production compliance.
- It integrates with the PS-037 Disclosure + Trust Boundary Layer: it renders
  alongside `TrustBoundaryLayer` and reuses the shared disclosure concepts,
  and must not duplicate or weaken the PS-037 boundary.
- It integrates / cross-references the PS-037a Multimodal Proof Layer: it
  renders alongside `MultimodalProofLayer` and surfaces an honest multimodal
  proof cross-reference, and must not duplicate or weaken the PS-037a
  contract.
- It integrates / cross-references the PS-037b Transcript/Timestamp Evidence
  layer: it renders alongside `TranscriptTimestampEvidenceLayer` and surfaces
  an honest transcript/timestamp cross-reference, and must not duplicate or
  weaken the PS-037b contract.
- It integrates / cross-references the PS-037c Voice/Audio Evidence Provider
  Choice layer: it renders alongside `VoiceAudioEvidenceChoiceLayer` and
  surfaces an honest voice/audio evidence cross-reference, and must not
  duplicate or weaken the PS-037c contract.
- It integrates / cross-references the PS-037d Gemini Campaign Intelligence /
  Judge Narrative layer: it renders alongside
  `CampaignIntelligenceJudgeNarrativeLayer` and surfaces an honest campaign
  intelligence cross-reference, and must not duplicate or weaken the PS-037d
  contract.
- It integrates / cross-references the PS-037e Cloudflare Low-Cost Backbone
  layer: it renders alongside `CloudflareLowCostBackboneLayer` and surfaces an
  honest Cloudflare low-cost backbone cross-reference, and must not duplicate
  or weaken the PS-037e contract.

### 10.2 Required Production Readiness + Demo Mode concepts

The layer must surface these canonical Production Readiness + Demo Mode
concepts, each as a clearly labeled item:

- `Production Readiness + Demo Mode` — the reusable demo / readiness layer
  label.
- `demo mode` — the judge-facing demo mode posture. Demo mode does not equal
  production readiness.
- `readiness posture` — the judge-facing readiness posture view. Readiness
  posture does not equal production readiness.
- `production readiness status` — the honest status of production readiness
  (deferred to later production work / production readiness evidence not
  available / not claimed / unknown).
- `demo mode status` — the honest status of demo mode (active / planned /
  local_demo / unknown).
- `local demo status` — the honest status of the local demo (ready for local
  demo / planned / unknown). Ready for local demo is the default posture.
- `judge demo status` — the honest status of the judge demo path (ready for
  local demo / local_demo / unknown).
- `local/static fallback` — whether the demo falls back to local / static
  evidence when live dependencies are unavailable (the default posture).
- `golden evidence fallback` — whether the demo falls back to golden demo
  evidence (the default posture).
- `checked-in evidence fallback` — whether the demo falls back to checked-in
  evidence (the default posture).
- `live dependency status` — the honest status of live dependency
  requirements for the judge demo (none required by default / live provider
  evidence not available / live B2 evidence not available / live Cloudflare
  evidence not available / unknown).
- `provider dependency status` — the honest status of live provider
  dependency for the judge demo (not required for local demo by default /
  live provider evidence not available / unknown).
- `B2 dependency status` — the honest status of live B2 dependency for the
  judge demo (not required for local demo by default / live B2 evidence not
  available / unknown).
- `Cloudflare dependency status` — the honest status of live Cloudflare
  dependency for the judge demo (not required for local demo by default /
  live Cloudflare evidence not available / unknown).
- `deployment evidence status` — the honest status of deployment evidence
  (production deployment not available / not claimed / unknown).
- `production security evidence status` — the honest status of production
  security evidence (production security evidence not available / not claimed
  / unknown).
- `production compliance evidence status` — the honest status of production
  compliance evidence (production compliance evidence not available / not
  claimed / unknown).
- `cold-start mitigation status` — the honest status of cold-start mitigation
  (cold-start mitigation planned / cold-start measurement not available /
  unknown). Cold-start mitigation plan does not equal measured performance
  guarantee.
- `startup health status` — the honest status of startup health evidence
  (planned / not available / unknown).
- `cost-control status` — the honest status of cost control (planned / not
  available / unknown). Low-cost demo posture does not equal cost guarantee.
- `provider fallback status` — the honest status of provider fallback
  evidence (planned / local_demo / not available / unknown).
- `failure-mode status` — the honest status of failure-mode evidence
  (planned / local_demo / not available / unknown).
- `export/offline evidence status` — the honest status of export / offline
  evidence (planned / local_demo / not available / unknown).
- `demo path evidence` — the evidence of the local demo path (ready for local
  demo / local_demo / unknown).
- `readiness checklist evidence` — the readiness checklist evidence framing.
  Readiness checklist does not equal production security.
- `local verification` — whether evidence is locally verified against
  checked-in / accepted data.
- `live verification status` — whether a live check is in scope (local /
  check-only by default; live provider evidence not available / live B2
  evidence not available / live Cloudflare evidence not available by default).
- `disclosure boundary` — the demo / readiness disclosure boundary, sourced
  from / consistent with PS-037.
- `not claimed` — the honest set of things ProofStudio does not claim for the
  demo / readiness layer.
- `unknown` — what remains unknown or not surfaced for the demo / readiness
  layer.
- `planned` — what is planned but not yet live for the demo / readiness layer.
- `ready for local demo` — the honest default posture that the app can be
  demoed locally / statically from checked-in evidence.
- `local/demo evidence` — whether the demo / readiness evidence is local /
  demo / golden fixture evidence (the default posture).
- `production deployment not available` — the honest default state that no
  production deployment is available.
- `production readiness evidence not available` — the honest default state
  that no production readiness evidence is available.
- `production security evidence not available` — the honest default state
  that no production security evidence is available.
- `production compliance evidence not available` — the honest default state
  that no production compliance evidence is available.
- `live provider evidence not available` — the honest default state that no
  live provider evidence is available.
- `live B2 evidence not available` — the honest default state that no live B2
  evidence is available.
- `live Cloudflare evidence not available` — the honest default state that no
  live Cloudflare evidence is available.
- `cold-start measurement not available` — the honest default state that no
  cold-start measurement is available. The cold-start mitigation plan does not
  equal a measured performance guarantee.
- `cold-start mitigation planned` — the honest default state that cold-start
  mitigation is planned (PS-038 owns the plan; the implementation and
  measurement remain later / out-of-scope work).
- `final submission packaging deferred to PS-039` — the honest deferred state
  for final submission packaging.

If a concept does not apply, the layer must show an honest "production
deployment not available" / "production readiness evidence not available" /
"production security evidence not available" / "production compliance evidence
not available" / "live provider evidence not available" / "live B2 evidence
not available" / "live Cloudflare evidence not available" / "cold-start
measurement not available" / "cold-start mitigation planned" / "ready for
local demo" / "planned" / "not claimed" / "unknown" state and must not
fabricate a value.

### 10.3 Required surfaces

The Production Readiness + Demo Mode layer must be rendered (additively) on
at least these required core proof surfaces, so
`required_surfaces_have_production_readiness_demo_mode_layer` is truthful:

- Judge Cockpit Home (`apps/web/src/JudgeCockpitHome.tsx`, path `/`)
- B2 Evidence Explorer (`apps/web/src/B2EvidenceExplorer.tsx`, path
  `/b2-evidence`)
- Manifest Verification Panel (`apps/web/src/ManifestVerificationPanel.tsx`,
  path `/manifest-verification`)
- B2 Rehydrate Comparison (`apps/web/src/B2RehydrateComparison.tsx`, path
  `/b2-rehydrate-comparison`)
- Archive / Rehydrate / B2 Audit Vault (`apps/web/src/B2AuditVault.tsx`, path
  `/b2-audit-vault`)
- Review + Approval Workspace (`apps/web/src/ReviewApprovalWorkspace.tsx`,
  path `/review-approval-workspace`)
- Judge Evidence Pack (`apps/web/src/JudgeEvidencePack.tsx`, path
  `/evidence-pack`)
- Public Provenance Passport (`apps/web/src/PublicPassportPage.tsx`, path
  `/passport/:id`)
- Review Room (`apps/web/src/App.tsx`, path `/review`)

Additional accepted surfaces (Genblaze Pipeline Graph, Failure-as-Proof
Timeline, Operations Cockpit, Provider Decision Intelligence, Lineage +
Comparison Lab) may render the layer but are not required for the minimum
contract. The smoke validates presence only on surfaces that are present in
this repo (section 14).

### 10.4 Local / live evidence honesty

The layer must distinguish clearly between:

- local demo / readiness evidence (the demo mode plan, the readiness posture,
  the local/static fallback, the golden evidence fallback, the checked-in
  evidence fallback, the live dependency status / provider dependency status /
  B2 dependency status / Cloudflare dependency status / deployment evidence
  status / production security evidence status / production compliance
  evidence status / cold-start mitigation status / startup health status /
  cost-control status / provider fallback status / failure-mode status /
  export/offline evidence status / demo path evidence / readiness checklist
  evidence recorded or reserved in accepted checked-in data)
- live evidence (none, by default — PS-038 makes no Cloudflare API call, no
  DNS mutation, no Cloudflare resource creation, no Cloudflare Pages
  deployment, no Cloudflare Workers deployment, no Cloudflare R2 live read, no
  Cloudflare R2 write, no Backblaze B2 write, no provider call, no model call,
  and no live B2 read)
- demo / golden evidence (the golden demo run, which is local / golden, not
  production)

A reviewer reading the layer must never mistake a demo mode label for a live
deployment, a production readiness layer for a production readiness claim, a
readiness checklist for production security, a cold-start mitigation plan for
a measured performance guarantee, a low-cost demo posture for a cost
guarantee, local fallback for live provider availability, checked-in evidence
for live B2 availability, a Cloudflare dependency posture for live Cloudflare
availability, or demo/golden readiness evidence for production compliance.

### 10.5 Deployment / readiness honesty

The layer must never fabricate a live deployment, a production deployment, a
production readiness evidence value, a production security evidence value, a
production compliance evidence value, a cold-start measurement, a startup
health evidence value, a cost-control evidence value, a Cloudflare
availability, a Backblaze B2 live availability, a provider availability, or a
model availability. Where no production deployment / production readiness /
production security / production compliance / live provider / live B2 / live
Cloudflare / cold-start measurement / startup health / cost-control evidence
exists in accepted data, the layer must surface honest "production deployment
not available", "production readiness evidence not available", "production
security evidence not available", "production compliance evidence not
available", "live provider evidence not available", "live B2 evidence not
available", "live Cloudflare evidence not available", and "cold-start
measurement not available" states. The demo mode and production readiness
layer labels must be honestly local / plan-only by default. Demo mode does not
equal production readiness. The production readiness layer label does not
equal a production readiness claim. The readiness checklist does not equal
production security. The cold-start mitigation plan does not equal a measured
performance guarantee. The low-cost demo posture does not equal cost
guarantee. Local fallback does not equal live provider availability.
Checked-in evidence does not equal live B2 availability. The Cloudflare
dependency posture does not equal live Cloudflare availability. Demo/golden
readiness evidence does not equal production compliance.

### 10.6 Required unavailable / not-claimed / planned states (verbatim)

The layer must surface, honestly, these unavailable / not-claimed / planned /
ready-for-local-demo states verbatim. These are non-claim states: they state
what is not available, not claimed, planned, ready for local demo, or
unknown, and must never be read as a hidden proof:

- local/demo evidence
- ready for local demo
- production deployment not available
- production readiness evidence not available
- production security evidence not available
- production compliance evidence not available
- live provider evidence not available
- live B2 evidence not available
- live Cloudflare evidence not available
- cold-start measurement not available
- cold-start mitigation planned
- final submission packaging deferred to PS-039
- not claimed
- unknown
- planned

PS-038 must not fake a live deployment, a production deployment, a production
readiness, a production security, a production compliance, a legal
compliance, an uptime guarantee, a cost guarantee, a performance guarantee, a
cold-start performance guarantee, a cold-start measurement, a load-test
coverage, a vulnerability scan coverage, a penetration test coverage, an
incident response readiness, an SLO/SLA guarantee, a data retention
compliance, a privacy compliance, a Cloudflare deployment, a Cloudflare
availability, a Backblaze B2 live availability, a provider availability, a
model availability, an Object Lock, a tamper-proof storage, or a
browser-side B2 byte verification. The honest unavailable / not-claimed /
planned / ready-for-local-demo / unknown states are the only acceptable
representation of those concepts when no accepted evidence exists.

### 10.7 Required de-escalation pairs (verbatim)

The layer must surface these Production Readiness + Demo Mode de-escalation
pairs verbatim so a judge never mistakes a strong-sounding demo mode label,
production readiness layer label, readiness checklist, cold-start mitigation
plan, local fallback, checked-in evidence, Cloudflare dependency posture, or
low-cost demo posture for a stronger guarantee:

- proof does not equal truth
- demo mode does not equal production readiness
- production readiness layer does not equal production readiness claim
- readiness checklist does not equal production security
- local demo mode does not equal live deployment
- cold-start mitigation plan does not equal measured performance guarantee
- low-cost demo posture does not equal cost guarantee
- local fallback does not equal live provider availability
- checked-in evidence does not equal live B2 availability
- Cloudflare dependency posture does not equal live Cloudflare availability
- demo/golden readiness evidence does not equal production compliance

### 10.8 Required negative boundary strings (verbatim)

The layer must surface these negative boundary strings verbatim:

- not production readiness
- not production security
- not production compliance
- not legal compliance
- not live deployment
- not Cloudflare deployment
- not Cloudflare availability
- not Backblaze B2 live availability
- not provider availability
- not model availability
- not uptime guarantee
- not cost guarantee
- not performance guarantee
- not cold-start performance guarantee
- not load-test coverage
- not vulnerability scan coverage
- not penetration test coverage
- not incident response readiness
- not SLO/SLA guarantee
- not data retention compliance
- not privacy compliance
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not semantic truth
- not legal authenticity
- not human authorship
- not C2PA authenticity
- not campaign performance prediction
- not marketing effectiveness proof
- not model output truth

### 10.9 Boundary honesty

The layer must not imply that any ProofStudio demo mode, readiness posture,
production readiness status, demo mode status, local demo status, judge demo
status, local/static fallback, golden evidence fallback, checked-in evidence
fallback, live dependency status, provider dependency status, B2 dependency
status, Cloudflare dependency status, deployment evidence status, production
security evidence status, production compliance evidence status, cold-start
mitigation status, startup health status, cost-control status, provider
fallback status, failure-mode status, export/offline evidence status, demo
path evidence, or readiness checklist evidence proves anything beyond what the
pipeline recorded. In particular it must not imply that those concepts prove
live deployment, production deployment, production readiness, production
security, production compliance, legal compliance, uptime guarantee, cost
guarantee, performance guarantee, cold-start performance guarantee,
cold-start measurement, load-test coverage, vulnerability scan coverage,
penetration test coverage, incident response readiness, SLO/SLA guarantee,
data retention compliance, privacy compliance, Cloudflare deployment,
Cloudflare availability, Backblaze B2 live availability, provider
availability, model availability, Object Lock, tamper-proof storage,
browser-side B2 byte verification, semantic truth, legal authenticity, human
authorship, C2PA authenticity, campaign performance prediction, marketing
effectiveness proof, or model output truth.

## 11. UI/UX Contract

The Production Readiness + Demo Mode layer UI must include:

- A clear title: "Production Readiness + Demo Mode" (or an equivalent clear
  title), with a positioning line that ProofStudio proves what the pipeline
  recorded for the demo path and readiness posture, that this is a
  demo-path-and-readiness-posture-over-recorded-proof layer, and that demo
  mode and the production readiness layer label are judge-facing posture
  labels for local / golden / checked-in demo evidence only (demo mode does
  not equal production readiness; the production readiness layer label does
  not equal a production readiness claim).
- A compact demo / readiness posture summary variant (for example
  `variant="summary"` or `variant="badge"`) that lists, in one compact block,
  the demo mode status, the local demo status, the judge demo status, the
  readiness posture, the local/static fallback, the live dependency status,
  the cold-start mitigation status, and the honest "production deployment not
  available" / "production readiness evidence not available" / "ready for
  local demo" / "planned" / "not claimed" / "unknown" states, suitable for
  surfaces where space is constrained.
- An expanded readiness-posture / readiness-checklist panel variant (for
  example `variant="panel"`) that states, in full, the Production Readiness +
  Demo Mode contract.
- A demo mode block that shows: Production Readiness + Demo Mode, demo mode,
  readiness posture, production readiness status, demo mode status, local
  demo status, judge demo status, and the demo mode posture and its honest
  "ready for local demo" / "planned" / "local/demo evidence" / "unknown"
  states.
- A local fallback block that shows: local/static fallback, golden evidence
  fallback, checked-in evidence fallback, local verification, live
  verification status, local/demo evidence, and the honest unavailable /
  not claimed / planned / unknown states where no value exists.
- A live dependency block that shows: live dependency status, provider
  dependency status, B2 dependency status, Cloudflare dependency status, and
  the honest "live provider evidence not available" / "live B2 evidence not
  available" / "live Cloudflare evidence not available" states.
- A readiness evidence block that shows: deployment evidence status,
  production security evidence status, production compliance evidence status,
  cold-start mitigation status, startup health status, cost-control status,
  provider fallback status, failure-mode status, export/offline evidence
  status, demo path evidence, and readiness checklist evidence, with the
  honest "production deployment not available" / "production readiness
  evidence not available" / "production security evidence not available" /
  "production compliance evidence not available" / "cold-start measurement
  not available" / "cold-start mitigation planned" / "planned" / "not
  claimed" / "unknown" states where no value exists.
- A cross-reference block that shows: trust boundary cross-reference,
  multimodal proof cross-reference, transcript/timestamp cross-reference,
  voice/audio evidence cross-reference, campaign intelligence
  cross-reference, and Cloudflare low-cost backbone cross-reference.
- A "not claimed" section listing, verbatim, what the demo / readiness layer
  does not prove (section 10.8), the honest unavailable / not-claimed /
  planned / ready-for-local-demo states (section 10.6).
- The de-escalation pairs (section 10.7), surfaced verbatim.
- The negative boundary strings (section 10.8), surfaced verbatim.
- Integration with the PS-037 Disclosure + Trust Boundary Layer: the
  Production Readiness + Demo Mode layer renders alongside
  `TrustBoundaryLayer`, reuses the shared disclosure concepts, and never
  contradicts the PS-037 boundary.
- Integration / cross-reference with the PS-037a Multimodal Proof Layer, the
  PS-037b Transcript/Timestamp Evidence layer, the PS-037c Voice/Audio
  Evidence Provider Choice layer, the PS-037d Gemini Campaign Intelligence /
  Judge Narrative layer, and the PS-037e Cloudflare Low-Cost Backbone layer:
  the Production Readiness + Demo Mode layer renders alongside those layers,
  cross-references them honestly, and never contradicts or weakens their
  contracts.
- A persistent demo / readiness boundary statement that states verbatim (or
  equivalent):

  > ProofStudio proves what the pipeline recorded for the demo path and
  > readiness posture. Proof does not equal truth. Demo mode does not equal
  > production readiness. The production readiness layer label does not equal
  > a production readiness claim. A readiness checklist does not equal
  > production security. Local demo mode does not equal live deployment. A
  > cold-start mitigation plan does not equal a measured performance
  > guarantee. A low-cost demo posture does not equal cost guarantee. Local
  > fallback does not equal live provider availability. Checked-in evidence
  > does not equal live B2 availability. A Cloudflare dependency posture does
  > not equal live Cloudflare availability. Demo/golden readiness evidence
  > does not equal production compliance.

UI / UX constraints:

- Must be useful in a three-minute hackathon demo: open any core proof surface
  -> read the compact demo / readiness posture summary -> read the demo mode
  status and the readiness posture -> expand the readiness-posture /
  readiness-checklist panel -> read what the demo / readiness layer proves ->
  read what it does not prove -> read the unavailable / not-claimed / planned
  states -> read the de-escalation pairs -> read the negative boundary
  strings.
- Must render the same demo / readiness / cold-start-mitigation framing on
  every required surface (section 10.3).
- Must not introduce generic readiness hype copy.
- Must not add unsupported claims.
- Must not fabricate live deployments, production deployments, production
  readiness, production security, production compliance, legal compliance,
  uptime guarantees, cost guarantees, performance guarantees, cold-start
  performance guarantees, cold-start measurements, load-test coverage,
  vulnerability scan coverage, penetration test coverage, incident response
  readiness, SLO/SLA guarantees, data retention compliance, privacy
  compliance, Cloudflare deployments, Cloudflare availability, Backblaze B2
  live availability, provider availability, model availability, or any
  provider output that is not in accepted data.
- Must follow the existing component conventions (`variant`, pills, cards,
  `JsonExpander`, the `.trust-boundary`, `.trust-boundary-layer*`, multimodal
  proof layer, transcript/timestamp evidence layer, voice/audio evidence
  provider choice layer, campaign-intelligence / judge-narrative layer, and
  cloudflare-low-cost-backbone layer styles) used by the other surfaces.
- Must not delete or weaken any existing per-surface truth-boundary panel,
  per-surface artifact record, the PS-037 disclosure layer, the PS-037a
  multimodal proof layer, the PS-037b transcript/timestamp evidence layer, the
  PS-037c voice/audio evidence provider choice layer, the PS-037d campaign
  intelligence / judge narrative layer, or the PS-037e Cloudflare low-cost
  backbone layer; the Production Readiness + Demo Mode layer is additive.

## 12. Data Contract

### 12.1 Source data (read-only inputs)

PS-038 reads accepted local / golden / demo data and existing accepted data
modules as immutable inputs. It must not mutate these and must not change
their canonical values. Acceptable read-only sources:

- `apps/web/src/trustBoundary.ts` (PS-037) — reuse the shared disclosure
  concepts; do not duplicate or weaken them
- `apps/web/src/multimodalProof.ts` (PS-037a) — reuse / cross-reference the
  multimodal proof; do not duplicate, weaken, or remove it
- `apps/web/src/assemblyAITranscriptEvidence.ts` (PS-037b) — reuse /
  cross-reference the transcript/timestamp evidence; do not duplicate, weaken,
  or remove it
- `apps/web/src/voiceAudioEvidenceChoice.ts` (PS-037c) — reuse /
  cross-reference the voice/audio evidence provider choice; do not duplicate,
  weaken, or remove it
- `apps/web/src/geminiCampaignIntelligence.ts` (PS-037d) — reuse /
  cross-reference the campaign intelligence / judge narrative; do not
  duplicate, weaken, or remove it
- `apps/web/src/cloudflareLowCostBackbone.ts` (PS-037e) — reuse /
  cross-reference the Cloudflare low-cost backbone posture; do not duplicate,
  weaken, or remove it
- `apps/web/src/b2Evidence.ts` (PS-026) — archive URI, archive SHA-256,
  rehydrate source, provider-call counts
- `apps/web/src/b2RehydrateComparison.ts` (PS-029) — rehydrate evidence
- `apps/web/src/manifestVerification.ts` (PS-028) — `manifest_uri`,
  `manifest_hash`
- `apps/web/src/b2AuditVault.ts` (PS-036)
- `apps/web/src/failureAsProofTimeline.ts` (PS-030)
- `apps/web/src/judgeEvidencePack.ts` (PS-031) — final asset / archive summary
- `apps/web/src/operationsCockpit.ts` (PS-032)
- `apps/web/src/providerDecisionIntelligence.ts` (PS-033)
- `apps/web/src/lineageComparisonLab.ts` (PS-034)
- `apps/web/src/reviewApprovalWorkspace.ts` (PS-035)
- `apps/web/src/api.ts` (passport / trust_boundary shape exposed by the
  Provenance Passport)
- `docs/evidence/demo/golden-demo-run.json` — `archive_uri`, `archive_sha256`,
  `manifest_uri`, `manifest_hash`, `rehydrate_source`,
  `provider_calls_during_rehydrate`, and the honest `unavailable_fields` map
- `docs/evidence/golden-fixture-digests.json`

Where no accepted demo / readiness / cold-start mitigation evidence exists,
PS-038 must surface explicit honest "production deployment not available" /
"production readiness evidence not available" / "production security evidence
not available" / "production compliance evidence not available" / "live
provider evidence not available" / "live B2 evidence not available" / "live
Cloudflare evidence not available" / "cold-start measurement not available" /
"cold-start mitigation planned" / "ready for local demo" / "planned" / "not
claimed" / "unknown" states and must not fabricate values. PS-038 must not
change the golden run canonical constants. The canonical constants are owned
by their respective accepted slices.

### 12.2 Production Readiness + Demo Mode item shape

A Production Readiness + Demo Mode item is derived from accepted data and
must expose:

- `production_readiness_demo_mode` (the reusable demo / readiness layer
  framing)
- `demo_mode` (the judge-facing demo mode framing)
- `readiness_posture` (the judge-facing readiness posture)
- `production_readiness_status` (one of `deferred_to_later_production_work`,
  `not_available`, `not_claimed`, `unknown`)
- `demo_mode_status` (one of `active`, `planned`, `local_demo`, `unknown`)
- `local_demo_status` (one of `ready_for_local_demo`, `planned`, `unknown`)
- `judge_demo_status` (one of `ready_for_local_demo`, `local_demo`,
  `unknown`)
- `local_static_fallback` (honest indicator; the default posture)
- `golden_evidence_fallback` (honest indicator; the default posture)
- `checked_in_evidence_fallback` (honest indicator; the default posture)
- `live_dependency_status` (one of `none_required_for_local_demo`,
  `not_available`, `unknown`)
- `provider_dependency_status` (one of `not_required_for_local_demo`,
  `not_available`, `unknown`)
- `b2_dependency_status` (one of `not_required_for_local_demo`,
  `not_available`, `unknown`)
- `cloudflare_dependency_status` (one of `not_required_for_local_demo`,
  `not_available`, `unknown`)
- `deployment_evidence_status` (one of `production_deployment_not_available`,
  `not_available`, `not_claimed`, `unknown`)
- `production_security_evidence_status` (one of `not_available`,
  `not_claimed`, `unknown`)
- `production_compliance_evidence_status` (one of `not_available`,
  `not_claimed`, `unknown`)
- `cold_start_mitigation_status` (one of `planned`, `not_available`,
  `unknown`)
- `startup_health_status` (one of `planned`, `not_available`, `unknown`)
- `cost_control_status` (one of `planned`, `not_available`, `unknown`)
- `provider_fallback_status` (one of `planned`, `local_demo`,
  `not_available`, `unknown`)
- `failure_mode_status` (one of `planned`, `local_demo`, `not_available`,
  `unknown`)
- `export_offline_evidence_status` (one of `planned`, `local_demo`,
  `not_available`, `unknown`)
- `demo_path_evidence` (one of `ready_for_local_demo`, `local_demo`,
  `unknown`)
- `readiness_checklist_evidence` (the readiness checklist framing)
- `trust_boundary_cross_reference` (honest indicator)
- `multimodal_proof_cross_reference` (honest indicator)
- `transcript_timestamp_cross_reference` (honest indicator)
- `voice_audio_evidence_cross_reference` (honest indicator)
- `campaign_intelligence_cross_reference` (honest indicator)
- `cloudflare_backbone_cross_reference` (honest indicator)
- `local_verification` (locally verified against accepted checked-in data)
- `live_verification_status` (local / check-only by default; live provider
  evidence not available / live B2 evidence not available / live Cloudflare
  evidence not available by default)
- `disclosure_boundary` (sourced from / consistent with PS-037)
- `label` (the human-readable label, matching the verbatim strings in
  section 21)
- `value` (the evidence value, honest about local / recorded-only /
  unavailable / not claimed / planned / unknown)
- `applicable` (boolean; false when the concept honestly does not apply)
- `state` (one of `recorded`, `locally_verified`, `recorded_only`,
  `not_verified`, `not_available`, `not_claimed`, `planned`, `unknown`,
  `deferred_to_later_slice`)

### 12.3 Evidence report schema rule

The PS-038 evidence report must follow the harness schema rule: boolean
fields remain booleans and detail / list fields use explicit detail names. A
field whose name implies a boolean success flag must remain a boolean. List
fields must use explicit detail names such as `_ids`, `_details`, or
`_failures` (see section 13).

## 13. Evidence Contract

PS-038 owns exactly one evidence directory: `docs/evidence/ps-038/`.

- A feature smoke may write only its own evidence, and only when
  `--write-evidence` is explicit. The default PS-038 smoke behavior is
  non-mutating local validation.
- PS-038 must not write any file outside `docs/evidence/ps-038/`.
- PS-038 must not mutate any prior-slice evidence (every prior evidence prefix
  is guarded by `scripts/smoke_lib.py` and
  `scripts/proofstudio_regression_gate.py`), including the PS-037 evidence
  under `docs/evidence/ps-037/`, the PS-037a evidence under
  `docs/evidence/ps-037a/`, the PS-037b evidence under
  `docs/evidence/ps-037b/`, the PS-037c evidence under
  `docs/evidence/ps-037c/`, the PS-037d evidence under
  `docs/evidence/ps-037d/`, and the PS-037e evidence under
  `docs/evidence/ps-037e/`.
- The PS-038 evidence file is
  `docs/evidence/ps-038/production-readiness-demo-mode-report.json`.

The PS-038 evidence report must carry these boolean fields (booleans as
booleans; `failures` as a list):

- `ok` (boolean; true only when every measured field is truthful and no
  forbidden overclaim or forbidden file change is present)
- `slice_id`: `ps038`
- `production_readiness_demo_mode_component_present` (boolean;
  `ProductionReadinessDemoModeLayer` component exists)
- `production_readiness_demo_mode_data_module_present` (boolean;
  `productionReadinessDemoMode.ts` exists)
- `production_readiness_demo_mode_layer_present` (boolean; the shared layer is
  wired in)
- `required_surfaces_have_production_readiness_demo_mode_layer` (boolean; the
  required surfaces in section 10.3 that are present in this repo render the
  layer)
- `trust_boundary_cross_reference_present` (boolean; the layer integrates /
  cross-references the PS-037 Disclosure + Trust Boundary Layer)
- `multimodal_proof_cross_reference_present` (boolean; the layer integrates /
  cross-references the PS-037a Multimodal Proof Layer)
- `transcript_timestamp_cross_reference_present` (boolean; the layer
  integrates / cross-references the PS-037b Transcript/Timestamp Evidence
  layer)
- `voice_audio_evidence_cross_reference_present` (boolean; the layer
  integrates / cross-references the PS-037c Voice/Audio Evidence Provider
  Choice layer)
- `campaign_intelligence_cross_reference_present` (boolean; the layer
  integrates / cross-references the PS-037d Gemini Campaign Intelligence /
  Judge Narrative layer)
- `cloudflare_backbone_cross_reference_present` (boolean; the layer
  integrates / cross-references the PS-037e Cloudflare Low-Cost Backbone
  layer)
- `demo_mode_present` (boolean)
- `readiness_posture_present` (boolean)
- `production_readiness_status_present` (boolean)
- `demo_mode_status_present` (boolean)
- `local_demo_status_present` (boolean)
- `judge_demo_status_present` (boolean)
- `local_static_fallback_present` (boolean)
- `golden_evidence_fallback_present` (boolean)
- `checked_in_evidence_fallback_present` (boolean)
- `live_dependency_status_present` (boolean)
- `provider_dependency_status_present` (boolean)
- `b2_dependency_status_present` (boolean)
- `cloudflare_dependency_status_present` (boolean)
- `deployment_evidence_status_present` (boolean)
- `production_security_evidence_status_present` (boolean)
- `production_compliance_evidence_status_present` (boolean)
- `cold_start_mitigation_status_present` (boolean)
- `startup_health_status_present` (boolean)
- `cost_control_status_present` (boolean)
- `provider_fallback_status_present` (boolean)
- `failure_mode_status_present` (boolean)
- `export_offline_evidence_status_present` (boolean)
- `demo_path_evidence_present` (boolean)
- `readiness_checklist_evidence_present` (boolean)
- `local_verification_status_present` (boolean)
- `live_verification_status_present` (boolean)
- `disclosure_boundary_present` (boolean)
- `not_claimed_status_present` (boolean)
- `unknown_status_present` (boolean)
- `planned_status_present` (boolean)
- `ready_for_local_demo_status_present` (boolean)
- `local_demo_evidence_present` (boolean)
- `production_deployment_not_available_present` (boolean)
- `production_readiness_evidence_not_available_present` (boolean)
- `production_security_evidence_not_available_present` (boolean)
- `production_compliance_evidence_not_available_present` (boolean)
- `live_provider_evidence_not_available_present` (boolean)
- `live_b2_evidence_not_available_present` (boolean)
- `live_cloudflare_evidence_not_available_present` (boolean)
- `cold_start_measurement_not_available_present` (boolean)
- `cold_start_mitigation_planned_present` (boolean)
- `final_submission_packaging_deferred_to_ps039_present` (boolean)
- `proof_does_not_equal_truth_present` (boolean)
- `demo_mode_does_not_equal_production_readiness_present` (boolean)
- `production_readiness_layer_does_not_equal_production_readiness_claim_present`
  (boolean)
- `readiness_checklist_does_not_equal_production_security_present` (boolean)
- `local_demo_mode_does_not_equal_live_deployment_present` (boolean)
- `cold_start_mitigation_plan_does_not_equal_measured_performance_guarantee_present`
  (boolean)
- `low_cost_demo_posture_does_not_equal_cost_guarantee_present` (boolean)
- `local_fallback_does_not_equal_live_provider_availability_present` (boolean)
- `checked_in_evidence_does_not_equal_live_b2_availability_present` (boolean)
- `cloudflare_dependency_posture_does_not_equal_live_cloudflare_availability_present`
  (boolean)
- `demo_golden_readiness_evidence_does_not_equal_production_compliance_present`
  (boolean)
- `no_production_readiness_claim` (boolean)
- `no_production_security_claim` (boolean)
- `no_production_compliance_claim` (boolean)
- `no_legal_compliance_claim` (boolean)
- `no_live_deployment_claim` (boolean)
- `no_cloudflare_deployment_claim` (boolean)
- `no_cloudflare_availability_claim` (boolean)
- `no_backblaze_b2_live_availability_claim` (boolean)
- `no_provider_availability_claim` (boolean)
- `no_model_availability_claim` (boolean)
- `no_uptime_guarantee_claim` (boolean)
- `no_cost_guarantee_claim` (boolean)
- `no_performance_guarantee_claim` (boolean)
- `no_cold_start_performance_guarantee_claim` (boolean)
- `no_load_test_coverage_claim` (boolean)
- `no_vulnerability_scan_coverage_claim` (boolean)
- `no_penetration_test_coverage_claim` (boolean)
- `no_incident_response_readiness_claim` (boolean)
- `no_slo_sla_guarantee_claim` (boolean)
- `no_data_retention_compliance_claim` (boolean)
- `no_privacy_compliance_claim` (boolean)
- `no_object_lock_claim` (boolean)
- `no_tamper_proof_claim` (boolean)
- `no_browser_side_b2_byte_verification_claim` (boolean)
- `no_semantic_truth_claim` (boolean)
- `no_legal_authenticity_claim` (boolean)
- `no_human_authorship_claim` (boolean)
- `no_c2pa_authenticity_claim` (boolean)
- `no_campaign_performance_prediction_claim` (boolean)
- `no_marketing_effectiveness_proof_claim` (boolean)
- `no_model_output_truth_claim` (boolean)
- `no_deployment_changes` (boolean)
- `no_env_secrets_changes` (boolean)
- `no_render_yaml_changes` (boolean)
- `no_requirements_dependency_changes` (boolean)
- `no_cloudflare_api_calls` (boolean)
- `no_dns_mutation` (boolean)
- `no_cloudflare_resource_creation` (boolean)
- `no_cloudflare_pages_deployment` (boolean)
- `no_cloudflare_workers_deployment` (boolean)
- `no_cloudflare_r2_live_reads` (boolean)
- `no_cloudflare_r2_writes` (boolean)
- `no_backblaze_b2_writes` (boolean)
- `no_provider_calls` (boolean)
- `no_model_calls` (boolean)
- `no_live_b2_reads` (boolean)
- `no_b2_writes` (boolean)
- `no_broad_b2_scans` (boolean)
- `no_recursive_smokes` (boolean)
- `no_hidden_git_flags_h` (boolean)
- `no_hidden_git_flags_S` (boolean)
- `no_forbidden_overclaims` (boolean)
- `prior_evidence_clean` (boolean)
- `failures` (list; empty on success)

`ok` must be `false` if `failures` is non-empty. Boolean fields must remain
booleans; list / detail fields must use explicit detail names. This evidence
file is created only in the implementation phase and only when
`--write-evidence` is explicit.

## 14. Smoke / Validation Contract

PS-038 ships one feature smoke:
`scripts/ps038_production_readiness_demo_mode_smoke.py`.

The PS-038 feature smoke must:

- validate only the PS-038 slice (no recursive smokes; must never launch
  another feature smoke as a subprocess; must never call the central
  regression gate)
- read checked-in prior evidence and accepted data modules as immutable inputs
- write only its own evidence file
  `docs/evidence/ps-038/production-readiness-demo-mode-report.json`, and only
  when `--write-evidence` is explicit
- never call Cloudflare (no Cloudflare API calls)
- never mutate DNS (no DNS mutation)
- never create Cloudflare resources (no Cloudflare resource creation)
- never deploy Cloudflare Pages (no Cloudflare Pages deployment)
- never deploy Cloudflare Workers (no Cloudflare Workers deployment)
- never perform Cloudflare R2 live reads (no Cloudflare R2 live reads)
- never perform Cloudflare R2 writes (no Cloudflare R2 writes)
- never perform Backblaze B2 writes (no Backblaze B2 writes)
- never call any provider (no provider calls)
- never call any model (no model calls)
- never read arbitrary B2 objects (no live B2 reads)
- never write B2 (no B2 writes)
- never perform broad B2 scans
- never make any deployment change (no deployment changes)
- never make any env/secrets change (no env/secrets changes)
- never make any `render.yaml` change (no render.yaml changes)
- never make any requirements/dependency change (no requirements/dependency
  changes)
- never run the frontend typecheck / build (that belongs to the central gate)
- reuse `scripts/smoke_lib.py` for shared validation logic
- validate the shared `ProductionReadinessDemoModeLayer` component is present
- validate the shared `productionReadinessDemoMode.ts` data module is present
- validate the Production Readiness + Demo Mode layer is rendered on the
  required proof surfaces that are present in this repo (section 10.3)
- validate the layer integrates / cross-references the PS-037 Trust Boundary
  (`trust_boundary_cross_reference_present`)
- validate the layer integrates / cross-references the PS-037a Multimodal
  Proof Layer (`multimodal_proof_cross_reference_present`)
- validate the layer integrates / cross-references the PS-037b Transcript/
  Timestamp Evidence layer
  (`transcript_timestamp_cross_reference_present`)
- validate the layer integrates / cross-references the PS-037c Voice/Audio
  Evidence Provider Choice layer
  (`voice_audio_evidence_cross_reference_present`)
- validate the layer integrates / cross-references the PS-037d Gemini Campaign
  Intelligence / Judge Narrative layer
  (`campaign_intelligence_cross_reference_present`)
- validate the layer integrates / cross-references the PS-037e Cloudflare
  Low-Cost Backbone layer (`cloudflare_backbone_cross_reference_present`)
- validate the required Production Readiness + Demo Mode UI strings
  (section 21) are present
- validate the required negative boundary strings (section 21) are present
- validate the deferred / unavailable / not-claimed / planned /
  ready-for-local-demo states (section 10.6) are present and honest
- validate no deployment changes are introduced
- validate no env/secrets changes are introduced
- validate no render.yaml changes are introduced
- validate no requirements/dependency changes are introduced
- validate no Cloudflare API calls are introduced
- validate no DNS mutation is introduced
- validate no Cloudflare resource creation is introduced
- validate no Cloudflare Pages deployment is introduced
- validate no Cloudflare Workers deployment is introduced
- validate no Cloudflare R2 live reads are introduced
- validate no Cloudflare R2 writes are introduced
- validate no Backblaze B2 writes are introduced
- validate no provider calls are introduced
- validate no model calls are introduced
- validate no live B2 reads are introduced
- validate no B2 writes are introduced
- validate no broad B2 scans are introduced
- validate no forbidden overclaims are introduced
- validate no recursive smokes (the smoke must not launch another feature
  smoke)
- validate no hidden Git flags `h` or `S` with an explicit h/S checker that
  reads `git ls-files -v` and fails when `line[0]` is `h` or `S` (a
  lowercase-only marker check is not sufficient because it misses uppercase
  `S` skip-worktree)
- validate the bad lowercase-only hidden-flag command literal is absent from
  the PS-038 changed files, without the smoke or this spec reproducing that
  literal
- validate prior evidence is unchanged
- validate `git diff --check` is clean
- do not scan smoke guard fixtures as product claims (the future PS-038 smoke
  and its evidence report are the source of truth for slice overclaim
  validation; smoke guard fixtures are not product claims)

The PS-038 feature smoke must support these standard flags:

- `--check-only` (default: non-mutating local validation; no evidence file is
  written)
- `--write-evidence` (write only `docs/evidence/ps-038/` evidence)
- `--no-frontend`

Default PS-038 smoke behavior is non-mutating local validation
(`--check-only`).

The smoke must not contain the bad lowercase-only hidden-flag marker check
and must not rely on a lowercase-only marker check. The hidden-Git-flags check
must be the explicit `h` / `S` checker over `git ls-files -v`, and must record
`no_hidden_git_flags_h` and `no_hidden_git_flags_S` as separate booleans.

PS-038 smoke performs no Cloudflare API calls, no DNS mutation, no Cloudflare
resource creation, no Cloudflare Pages deployment, no Cloudflare Workers
deployment, no Cloudflare R2 live reads, no Cloudflare R2 writes, no Backblaze
B2 writes, no provider calls, no model calls, no live B2 reads, no B2 writes,
no broad B2 scans, no deployment changes, no env/secrets changes, no
render.yaml changes, and no requirements/dependency changes.

The PS-038 smoke must not create duplicate context-blind overclaim scanners.
The smoke and its evidence report are the source of truth for PS-038
overclaim validation. The smoke must not scan smoke guard fixtures as product
claims.

## 15. Regression Gate Contract

The central regression gate remains the single cross-slice release-readiness
gate and is non-mutating by default. PS-038 does not own or modify the central
gate.

Normal future PS-038 release validation command:

```
python scripts/proofstudio_regression_gate.py --current ps038 --frontend --report-out /tmp/proofstudio-release-report.json
```

Contract-only gate (no frontend):

```
python scripts/proofstudio_regression_gate.py --current ps038 --no-frontend --report-out /tmp/proofstudio-ps038-regression-report.json
```

- The gate runs `npm run typecheck` and `npm run build` in `apps/web` exactly
  once per invocation, and only when `--frontend` is passed. PS-038 feature
  smoke must never trigger nested frontend builds.
- The gate must not write the canonical PS-034A report. `--write-report` is
  rejected for `--current ps038` (PS-035C accepted behavior; only PS-034A may
  regenerate the canonical report).
- Running the gate for `ps038` must leave all prior-slice evidence unchanged,
  including the PS-037, PS-037a, PS-037b, PS-037c, PS-037d, and PS-037e
  evidence.
- No recursive smokes: the gate never executes a feature smoke.

Canonical PS-034A regeneration (unchanged, owned by PS-034A only):

```
python scripts/proofstudio_regression_gate.py --current ps034a --write-report
```

## 16. Truth Boundary

ProofStudio proves what the pipeline recorded. The Production Readiness + Demo
Mode layer is a demo-path-and-readiness-posture-over-recorded-proof surface
that makes the recorded demo mode posture, local fallback, live dependency
posture, cold-start mitigation plan, and readiness checklist explicit and
consistent on every core proof surface. It is not a live deployment, not a
production deployment, not a DNS change system, not a Cloudflare resource
creator, not a Cloudflare Pages deployment system, not a Cloudflare Workers
deployment system, not a Cloudflare R2 live reader, not a Cloudflare R2
writer, not a Backblaze B2 writer, not a live B2 verifier, not a truth system,
not a semantic-truth system, not a model-output-truth system, not a production
readiness system, not a production security system, not a production
compliance system, not a legal compliance system, not an uptime guarantee
system, not a cost guarantee system, not a performance guarantee system, not a
cold-start performance guarantee system, not a load test, not a vulnerability
scan, not a penetration test, not an incident-response readiness system, not
an SLO/SLA system, not a data retention compliance system, not a privacy
compliance system, not a campaign performance predictor, not a marketing
effectiveness scorer, and not an identity / biometric / authenticity system.

The layer must preserve these truth-boundary red lines verbatim across the
spec, the UI, and any evidence report:

- do not claim live deployment
- do not claim production deployment
- do not claim production readiness
- do not claim production security
- do not claim production compliance
- do not claim legal compliance
- do not claim uptime guarantee
- do not claim cost guarantee
- do not claim performance guarantee
- do not claim cold-start performance guarantee
- do not claim cold-start mitigation implementation unless implemented and
  validated
- do not claim cold-start measurement
- do not claim load-test coverage
- do not claim vulnerability scan coverage
- do not claim penetration test coverage
- do not claim incident response readiness
- do not claim SLO/SLA guarantee
- do not claim data retention compliance
- do not claim privacy compliance
- do not claim DNS ownership
- do not claim Cloudflare deployment
- do not claim Cloudflare resource existence
- do not claim Cloudflare Pages availability
- do not claim Cloudflare Workers availability
- do not claim Cloudflare R2 availability
- do not claim Cloudflare availability
- do not claim Backblaze B2 live availability
- do not claim provider availability
- do not claim model availability
- do not claim semantic truth
- do not claim legal authenticity
- do not claim human authorship
- do not claim C2PA unless implemented and verified
- do not claim Object Lock / tamper-proof storage unless implemented and
  verified
- do not claim browser-side B2 byte verification unless implemented and
  verified
- do not claim live B2 availability unless a live B2 check is explicitly
  implemented and approved
- do not claim public deployment verification unless deployed and tested
- do not claim enterprise security
- do not claim actual spend / latency / quota unless captured
- do not claim provider failures / reruns / variants unless evidenced
- do not claim campaign performance prediction
- do not claim marketing effectiveness proof
- do not claim model output truth

PS-038 does not prove live deployment, production deployment, production
readiness, production security, production compliance, legal compliance,
uptime guarantee, cost guarantee, performance guarantee, cold-start
performance guarantee, cold-start measurement, load-test coverage,
vulnerability scan coverage, penetration test coverage, incident response
readiness, SLO/SLA guarantee, data retention compliance, privacy compliance,
DNS ownership, Cloudflare deployment, Cloudflare resource existence,
Cloudflare Pages availability, Cloudflare Workers availability, Cloudflare R2
availability, Cloudflare availability, Backblaze B2 live availability,
provider availability, model availability, B2 immutability, Object Lock,
tamper-proof storage, browser-side B2 byte verification, live B2
availability, semantic truth, legal authenticity, human authorship, C2PA
authenticity, campaign performance, marketing effectiveness, or model output
truth. No PS-038 artifact may imply any of these. The Production Readiness +
Demo Mode layer states what the pipeline already recorded; it does not deploy
ProofStudio, it does not mutate DNS, it does not create Cloudflare resources,
it does not call Cloudflare, it does not call any provider, it does not call
any model, it does not read live B2, it does not write B2, it does not perform
broad B2 scans, and it does not change deployment / env / render.yaml /
requirements config.

## 17. Later-slice Boundaries

PS-038 must not implement, fake, or claim the later provider-specific slices
or out-of-scope capabilities. The boundaries are:

- live production deployment — out of scope for PS-038. PS-038 names demo mode
  and the production readiness layer as judge-facing posture labels for local
  / golden / checked-in demo evidence only. A live production deployment path
  may only be enabled by a later PM-approved slice with env gates, cost
  controls, rollback, and evidence boundaries. PS-038 must only reserve an
  honest "production deployment not available" state.
- final submission packaging — out of scope for PS-038. PS-038 must only
  reserve an honest "final submission packaging deferred to PS-039" state.
- cold-start mitigation implementation / measurement — PS-038 owns the plan
  only. PS-038 must reserve an honest "cold-start mitigation planned" state
  for the plan and a "cold-start measurement not available" state for the
  measurement. The cold-start mitigation plan does not equal a measured
  performance guarantee. The implementation and measurement remain later /
  out-of-scope work.
- startup health evidence — out of scope for PS-038 beyond an honest "planned"
  state.
- cost control — out of scope for PS-038 beyond an honest "planned" state. The
  low-cost demo posture does not equal a cost guarantee.
- provider fallback / failure-mode / export-offline evidence — PS-038 surfaces
  honest "planned" / "local_demo" / "not available" states; it does not
  implement live provider fallback behavior, live failure-mode handling, or
  live export/offline packaging beyond accepted checked-in evidence.
- DNS mutation — out of scope for PS-038. PS-038 must only reserve an honest
  "not claimed" / "unknown" state.
- Cloudflare resource creation — out of scope for PS-038. PS-038 must only
  reserve an honest "live Cloudflare evidence not available" state.
- Cloudflare Pages deployment — out of scope for PS-038.
- Cloudflare Workers deployment — out of scope for PS-038.
- Cloudflare R2 live reads — out of scope for PS-038. PS-038 must only reserve
  an honest "live Cloudflare evidence not available" state; the Cloudflare
  dependency posture does not equal live Cloudflare availability.
- Cloudflare R2 writes — out of scope for PS-038.
- Backblaze B2 writes — out of scope for PS-038. Backblaze B2 remains the
  durable proof/archive system of record.
- production readiness — out of scope for PS-038. PS-038 must only reserve an
  honest "production readiness evidence not available" state. The production
  readiness layer label does not equal a production readiness claim.
- production security — out of scope for PS-038. PS-038 must only reserve an
  honest "production security evidence not available" state. The readiness
  checklist does not equal production security.
- production compliance — out of scope for PS-038. PS-038 must only reserve an
  honest "production compliance evidence not available" state.
- legal compliance — out of scope for PS-038. PS-038 must not claim it.
- uptime guarantee — out of scope for PS-038. PS-038 must not claim it.
- cost guarantee — out of scope for PS-038. PS-038 must not claim it.
- performance guarantee — out of scope for PS-038. PS-038 must not claim it.
- cold-start performance guarantee — out of scope for PS-038. PS-038 must not
  claim it.
- load-test coverage / vulnerability scan coverage / penetration test
  coverage / incident response readiness / SLO/SLA guarantee / data retention
  compliance / privacy compliance — out of scope. PS-038 must only reserve
  honest "not claimed" / "unknown" states for these.
- semantic truth verification — out of scope for PS-038. PS-038 must not claim
  it.
- legal authenticity — out of scope for PS-038. PS-038 must not claim it.
- human authorship — out of scope for PS-038. PS-038 must not claim it.
- C2PA authenticity — out of scope for PS-038. PS-038 must not claim it.
- Object Lock / tamper-proof storage / browser-side B2 byte verification — out
  of scope. PS-038 must only reserve honest "not claimed" states for these.
- campaign performance prediction / marketing effectiveness proof / model
  output truth — out of scope. PS-038 must only reserve honest "not claimed"
  states for these.

PS-038 may reserve fields and honest "production deployment not available" /
"production readiness evidence not available" / "production security evidence
not available" / "production compliance evidence not available" / "live
provider evidence not available" / "live B2 evidence not available" / "live
Cloudflare evidence not available" / "cold-start measurement not available" /
"cold-start mitigation planned" / "ready for local demo" / "planned" / "not
claimed" / "unknown" states for those later-slice / out-of-scope areas, but
must not fake live deployments, production deployments, production readiness,
production security, production compliance, legal compliance, uptime
guarantees, cost guarantees, performance guarantees, cold-start performance
guarantees, cold-start measurements, load-test coverage, vulnerability scan
coverage, penetration test coverage, incident response readiness, SLO/SLA
guarantees, data retention compliance, privacy compliance, Cloudflare
deployments, Cloudflare availability, Backblaze B2 live availability,
provider availability, model availability, or any provider output.

## 18. Risks

PS-038 must record the following risks with mitigations:

- overclaim risk
  - risk: a reviewer misreads the Production Readiness + Demo Mode layer or
    its copy as a forbidden overclaim — i.e. as claiming live deployment,
    production deployment, production readiness, production security,
    production compliance, legal compliance, uptime guarantee, cost guarantee,
    performance guarantee, cold-start performance guarantee, cold-start
    measurement, load-test coverage, vulnerability scan coverage, penetration
    test coverage, incident response readiness, SLO/SLA guarantee, data
    retention compliance, privacy compliance, Cloudflare deployment,
    Cloudflare availability, Backblaze B2 live availability, provider
    availability, model availability, Object Lock, tamper-proof storage,
    browser-side B2 byte verification, semantic truth, legal authenticity,
    human authorship, C2PA authenticity, campaign performance prediction,
    marketing effectiveness proof, or model output truth. ProofStudio does not
    claim any of these.
  - mitigation: the persistent demo / readiness boundary statement
    (section 11) is mandatory; the truth-boundary red lines (section 16) are
    preserved verbatim; the de-escalation pairs (section 10.7) and negative
    boundary strings (section 10.8) are surfaced verbatim; the evidence
    report carries `no_forbidden_overclaims`.
- demo-mode / readiness-word overclaim risk
  - risk: a "demo mode", "production readiness", "readiness posture",
    "readiness checklist", or "cold-start mitigation plan" word is misread as
    a live deployment claim, a production readiness claim, a production
    security claim, a production compliance claim, a cost guarantee, an uptime
    guarantee, a performance guarantee, or a cold-start performance guarantee.
  - mitigation: the de-escalation pairs in section 10.7 are surfaced verbatim
    (demo mode does not equal production readiness; production readiness
    layer does not equal production readiness claim; readiness checklist does
    not equal production security; local demo mode does not equal live
    deployment; cold-start mitigation plan does not equal measured performance
    guarantee; low-cost demo posture does not equal cost guarantee; local
    fallback does not equal live provider availability; checked-in evidence
    does not equal live B2 availability; Cloudflare dependency posture does
    not equal live Cloudflare availability; demo/golden readiness evidence
    does not equal production compliance); the negative boundary strings in
    section 10.8 are surfaced verbatim.
- faking-deployment / faking-readiness risk
  - risk: a live deployment, a production deployment, a production readiness
    evidence value, a production security evidence value, a production
    compliance evidence value, a cold-start measurement, a startup health
    evidence value, a cost-control evidence value, a Cloudflare deployment, a
    Cloudflare availability, a Backblaze B2 live availability, a provider
    availability, or a model availability is silently represented as present
    when it is not, or is silently omitted so it looks hidden.
  - mitigation: the unavailable / not-claimed / planned /
    ready-for-local-demo states (section 10.6) are surfaced verbatim and
    honestly; the deployment / readiness honesty (section 10.5) is mandatory;
    the smoke validates their presence; PS-038 never produces those outputs
    unless they exist in accepted data.
- de-escalation-gap risk
  - risk: a judge mistakes a demo mode label for a live deployment, a
    production readiness layer for a production readiness claim, a readiness
    checklist for production security, a cold-start mitigation plan for a
    measured performance guarantee, a low-cost demo posture for a cost
    guarantee, local fallback for live provider availability, checked-in
    evidence for live B2 availability, a Cloudflare dependency posture for
    live Cloudflare availability, or demo/golden readiness evidence for
    production compliance.
  - mitigation: the de-escalation pairs in section 10.7 are surfaced verbatim.
- PS-037 / PS-037a / PS-037b / PS-037c / PS-037d / PS-037e weakening risk
  - risk: the Production Readiness + Demo Mode layer duplicates,
    contradicts, weakens, or removes the PS-037 Disclosure + Trust Boundary
    Layer, the PS-037a Multimodal Proof Layer, the PS-037b Transcript/
    Timestamp Evidence layer, the PS-037c Voice/Audio Evidence Provider Choice
    layer, the PS-037d Gemini Campaign Intelligence / Judge Narrative layer,
    or the PS-037e Cloudflare Low-Cost Backbone layer.
  - mitigation: the Production Readiness + Demo Mode layer renders alongside
    `TrustBoundaryLayer`, `MultimodalProofLayer`,
    `TranscriptTimestampEvidenceLayer`, `VoiceAudioEvidenceChoiceLayer`,
    `CampaignIntelligenceJudgeNarrativeLayer`, and
    `CloudflareLowCostBackboneLayer`, reuses the shared disclosure concepts,
    cross-references PS-037a, PS-037b, PS-037c, PS-037d, and PS-037e, and
    never contradicts the PS-037 boundary or removes the PS-037a / PS-037b /
    PS-037c / PS-037d / PS-037e contracts; PS-038 does not edit the PS-037,
    PS-037a, PS-037b, PS-037c, PS-037d, or PS-037e contract files except
    additively (section 9).
- deployment-config / env / render.yaml / requirements drift risk
  - risk: the layer or its smoke silently changes deployment config,
    `.env*`, `render.yaml`, or requirements, which would break the
    demo-mode-as-local-static posture and the truth boundary.
  - mitigation: PS-038 makes no deployment changes, no env/secrets changes,
    no render.yaml changes, and no requirements/dependency changes; the smoke
    enforces `no_deployment_changes`, `no_env_secrets_changes`,
    `no_render_yaml_changes`, and `no_requirements_dependency_changes`.
- live-B2-read / DNS-mutation / provider-call / model-call risk
  - risk: the layer triggers a live B2 read, a broad B2 scan, a Cloudflare
    API call, a DNS mutation, a Cloudflare resource creation, a Cloudflare
    Pages deployment, a Cloudflare Workers deployment, a Cloudflare R2 live
    read, a Cloudflare R2 write, a Backblaze B2 write, a provider call, or a
    model call.
  - mitigation: the layer is purely client-side over accepted data; the smoke
    enforces `no_cloudflare_api_calls`, `no_dns_mutation`,
    `no_cloudflare_resource_creation`, `no_cloudflare_pages_deployment`,
    `no_cloudflare_workers_deployment`, `no_cloudflare_r2_live_reads`,
    `no_cloudflare_r2_writes`, `no_backblaze_b2_writes`, `no_provider_calls`,
    `no_model_calls`, `no_live_b2_reads`, `no_b2_writes`,
    `no_broad_b2_scans`.
- evidence-mutation risk
  - risk: the PS-038 smoke or the central gate run overwrites prior-slice
    evidence, including PS-037, PS-037a, PS-037b, PS-037c, PS-037d, and
    PS-037e evidence.
  - mitigation: PS-038 writes only `docs/evidence/ps-038/`; the gate is
    non-mutating by default; prior evidence prefixes are guarded.
- hidden-Git-flags risk
  - risk: a session uses `assume-unchanged`, `skip-worktree`, or
    `git update-index` / `update-index` to mask a dirty tree, including the
    uppercase `S` skip-worktree flag that a lowercase-only marker check misses.
  - mitigation: the operating law forbids these verbatim; the smoke uses the
    explicit `h` / `S` checker over `git ls-files -v` and fails on `line[0]`
    being `h` or `S`, recording `no_hidden_git_flags_h` and
    `no_hidden_git_flags_S` as separate booleans.
- scope-creep risk
  - risk: PS-038 expands into live production deployment, DNS mutation,
    Cloudflare resource creation, Cloudflare Pages deployment, Cloudflare
    Workers deployment, Cloudflare R2 live reads, Cloudflare R2 writes,
    Backblaze B2 writes, provider calls, model calls, live B2 reads, B2
    writes, broad B2 scans, production readiness, production security,
    production compliance, legal compliance, uptime guarantee, cost guarantee,
    performance guarantee, cold-start performance guarantee, cold-start
    measurement, load-test coverage, vulnerability scan coverage, penetration
    test coverage, incident response readiness, SLO/SLA guarantee, data
    retention compliance, privacy compliance, CI, billing, deployment, auth,
    teams, permissions, a full enterprise DAM, a new backend, or a live B2
    fetcher.
  - mitigation: section 7 lists these as non-goals; section 9 forbids the
    relevant paths; section 17 fixes the later-slice / out-of-scope
    boundaries.
- recursive-smoke risk
  - risk: the PS-038 smoke launches another feature smoke or calls the central
    gate.
  - mitigation: the smoke must never launch another feature smoke as a
    subprocess and must never call the central regression gate; the central
    gate is the only cross-slice validator.
- duplicate-scanner risk
  - risk: PS-038 adds duplicate context-blind overclaim scanners in chat/spec
    guidance that treat smoke guard fixtures as product claims.
  - mitigation: PS-038 does not create duplicate context-blind overclaim
    scanners; the PS-038 smoke and its evidence report are the source of truth
    for slice overclaim validation; smoke guard fixtures are not scanned as
    product claims.

## 19. Acceptance Criteria

PS-038 (spec-only phase) is accepted only when:

- this spec exists at
  `specs/60-ps-038-production-readiness-demo-mode.md`
- only this spec file is changed in the spec-only phase
- the branch `ps-038/production-readiness-demo-mode` starts from
  `origin/accepted/proofstudio` at commit
  `3e0c896375947c1d9668204333c12218a6f52981` (the merge-base equals that
  commit)
- the product scope is clear and owns the demo-mode / readiness-posture /
  cold-start-mitigation evidence and planning layer only; it does not expand
  into live production deployment, DNS mutation, Cloudflare resource creation,
  Cloudflare Pages deployment, Cloudflare Workers deployment, Cloudflare R2
  live reads, Cloudflare R2 writes, Backblaze B2 writes, provider calls, model
  calls, live B2 reads, B2 writes, broad B2 scans, production readiness,
  production security, production compliance, legal compliance, uptime
  guarantee, cost guarantee, performance guarantee, cold-start performance
  guarantee, cold-start measurement, load-test coverage, vulnerability scan
  coverage, penetration test coverage, incident response readiness, SLO/SLA
  guarantee, data retention compliance, privacy compliance, DNS ownership,
  Cloudflare resource existence, Cloudflare Pages availability, Cloudflare
  Workers availability, Cloudflare R2 availability, Cloudflare availability,
  Backblaze B2 live availability, provider availability, model availability,
  Object Lock, tamper-proof storage, browser-side B2 byte verification,
  semantic truth, legal authenticity, human authorship, C2PA authenticity,
  campaign performance prediction, marketing effectiveness proof, or model
  output truth
- the required Production Readiness + Demo Mode concepts (section 10.2) and
  the required surfaces (section 10.3) are specified
- the unavailable / not-claimed / planned / ready-for-local-demo states
  (section 10.6), the de-escalation pairs (section 10.7), and the negative
  boundary strings (section 10.8) are specified verbatim
- the UI / UX contract (section 11) and the persistent demo / readiness
  boundary statement are specified
- the data contract (section 12) reuses accepted checked-in evidence as
  read-only inputs and surfaces honest unavailable / not-claimed / planned /
  ready-for-local-demo / unknown states where no evidence exists
- the truth boundary (section 16) is explicit and the boundary copy is
  specified
- the later-slice boundaries (section 17) are fixed
- the implementation candidate files (section 8) are listed, but no
  implementation is done in this phase
- the validation plan uses the PS-038 feature smoke plus the central
  regression gate (sections 14 and 15)
- no evidence mutation occurs in this phase
- no hidden Git flags `h` or `S` are present (verified by the explicit h/S
  checker over `git ls-files -v`)
- `git diff --check` is clean
- no staging, commit, or push occurs until PM approval
- `AGENTS.md`, `specs/07-master-spec-plan.md`, and
  `specs/08-roadmap-slices.md` are not changed in this phase

Implementation-phase acceptance (for reference, not this phase) additionally
requires: the shared `ProductionReadinessDemoModeLayer` component +
`productionReadinessDemoMode.ts` data module exist; the Production Readiness +
Demo Mode layer is rendered on the required surfaces present in this repo
(section 10.3); the layer integrates / cross-references the PS-037a Multimodal
Proof Layer, the PS-037b Transcript/Timestamp Evidence layer, the PS-037c
Voice/Audio Evidence Provider Choice layer, the PS-037d Gemini Campaign
Intelligence / Judge Narrative layer, and the PS-037e Cloudflare Low-Cost
Backbone layer and preserves the PS-037 TrustBoundaryLayer; the required
Production Readiness + Demo Mode concepts, unavailable / not-claimed / planned
/ ready-for-local-demo states, de-escalation pairs, and negative boundary
strings are present; the PS-038 smoke passes in `--check-only` (default) and
writes only `docs/evidence/ps-038/**` under `--write-evidence`; the central
gate passes for `--current ps038`; no deployment change, no env/secrets change,
no render.yaml change, no requirements/dependency change, no Cloudflare API
call, no DNS mutation, no Cloudflare resource creation, no Cloudflare Pages
deployment, no Cloudflare Workers deployment, no Cloudflare R2 live read, no
Cloudflare R2 write, no Backblaze B2 write, no provider call, no model call,
no live B2 read, no B2 write, no broad B2 scan occurs; prior evidence is
unchanged, including PS-037, PS-037a, PS-037b, PS-037c, PS-037d, and PS-037e
evidence; no forbidden overclaim is introduced; the PS-037 disclosure
boundary, the PS-037a multimodal proof contract, the PS-037b transcript/
timestamp contract, the PS-037c voice/audio evidence provider choice contract,
the PS-037d campaign intelligence / judge narrative contract, and the PS-037e
Cloudflare low-cost backbone contract are not weakened.

## 20. Rollback

Rollback of the PS-038 spec-only phase is a single revert of this spec commit,
because only `specs/60-ps-038-production-readiness-demo-mode.md` is changed in
this phase.

Future implementation rollback must restore the pre-PS-038 state of the edited
files in section 8. Specifically:

- remove `apps/web/src/productionReadinessDemoMode.ts`
- remove `apps/web/src/ProductionReadinessDemoModeLayer.tsx`
- revert the additive production-readiness-demo-mode renders in
  `apps/web/src/JudgeCockpitHome.tsx`,
  `apps/web/src/B2EvidenceExplorer.tsx`,
  `apps/web/src/B2RehydrateComparison.tsx`,
  `apps/web/src/ManifestVerificationPanel.tsx`,
  `apps/web/src/B2AuditVault.tsx`,
  `apps/web/src/ReviewApprovalWorkspace.tsx`,
  `apps/web/src/JudgeEvidencePack.tsx`,
  `apps/web/src/PublicPassportPage.tsx`, and
  `apps/web/src/App.tsx` to pre-PS-038 state
- revert the additive production-readiness-demo-mode classes in
  `apps/web/src/styles.css` to pre-PS-038 state
- remove `scripts/ps038_production_readiness_demo_mode_smoke.py`
- remove `docs/ps-038-production-readiness-demo-mode-proof.md`
- remove `docs/evidence/ps-038/` if it was added
- revert the additive cross-references in `specs/07-master-spec-plan.md`,
  `specs/08-roadmap-slices.md`, and
  `docs/validation/proofstudio-smoke-harness-v1.md` to pre-PS-038 state

Rollback of PS-038 must not touch any evidence under `docs/evidence/**` other
than `docs/evidence/ps-038/`, must not touch the central gate
(`scripts/proofstudio_regression_gate.py`), `scripts/smoke_lib.py`,
`AGENTS.md`, `.env*`, `render.yaml`, requirements files, any provider wrapper,
any model client, any Cloudflare client, any B2 storage path, any DNS mutation
path, any deployment config path, the PS-037 disclosure contract, the PS-037a
multimodal proof contract, the PS-037b transcript/timestamp contract, the
PS-037c voice/audio evidence provider choice contract, the PS-037d campaign
intelligence / judge narrative contract, or the PS-037e Cloudflare low-cost
backbone contract. Rollback is isolated and reversible because PS-038 is a
self-contained Production Readiness + Demo Mode layer over existing accepted
data; it does not change provider behavior, model behavior, Cloudflare
behavior, DNS behavior, B2 behavior, billing behavior, deployment topology,
the PS-037 boundary, the PS-037a contract, the PS-037b contract, the PS-037c
contract, the PS-037d contract, or the PS-037e contract.

## 21. Verbatim implementation/audit contract strings

The PS-038 implementation, the Production Readiness + Demo Mode layer UI, the
PS-038 smoke, and the PS-038 evidence report must preserve the following
exact strings so the Production Readiness + Demo Mode contract is
deterministic and auditable. Any future PM audit must check these exact
strings; do not rely on close-enough wording. No surprise audit checks: any
exact string a future PM audit should check is listed here.

The required identity / positioning strings are:

- PS-038
- Production Readiness + Demo Mode

The required concept strings are:

- demo mode
- readiness posture
- production readiness status
- demo mode status
- local demo status
- judge demo status
- local/static fallback
- golden evidence fallback
- checked-in evidence fallback
- live dependency status
- provider dependency status
- B2 dependency status
- Cloudflare dependency status
- deployment evidence status
- production security evidence status
- production compliance evidence status
- cold-start mitigation status
- startup health status
- cost-control status
- provider fallback status
- failure-mode status
- export/offline evidence status
- demo path evidence
- readiness checklist evidence
- local verification
- live verification status
- disclosure boundary

The required honest status / state strings are:

- not claimed
- unknown
- planned
- ready for local demo
- local/demo evidence
- production deployment not available
- production readiness evidence not available
- production security evidence not available
- production compliance evidence not available
- live provider evidence not available
- live B2 evidence not available
- live Cloudflare evidence not available
- cold-start measurement not available
- cold-start mitigation planned
- final submission packaging deferred to PS-039

The required de-escalation-pair strings are:

- proof does not equal truth
- demo mode does not equal production readiness
- production readiness layer does not equal production readiness claim
- readiness checklist does not equal production security
- local demo mode does not equal live deployment
- cold-start mitigation plan does not equal measured performance guarantee
- low-cost demo posture does not equal cost guarantee
- local fallback does not equal live provider availability
- checked-in evidence does not equal live B2 availability
- Cloudflare dependency posture does not equal live Cloudflare availability
- demo/golden readiness evidence does not equal production compliance

The required negative-boundary strings are:

- not production readiness
- not production security
- not production compliance
- not legal compliance
- not live deployment
- not Cloudflare deployment
- not Cloudflare availability
- not Backblaze B2 live availability
- not provider availability
- not model availability
- not uptime guarantee
- not cost guarantee
- not performance guarantee
- not cold-start performance guarantee
- not load-test coverage
- not vulnerability scan coverage
- not penetration test coverage
- not incident response readiness
- not SLO/SLA guarantee
- not data retention compliance
- not privacy compliance
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not semantic truth
- not legal authenticity
- not human authorship
- not C2PA authenticity
- not campaign performance prediction
- not marketing effectiveness proof
- not model output truth

The required posture / boundary strings are:

- no deployment changes
- no env/secrets changes
- no render.yaml changes
- no requirements/dependency changes
- no Cloudflare API calls
- no DNS mutation
- no Cloudflare resource creation
- no Cloudflare Pages deployment
- no Cloudflare Workers deployment
- no Cloudflare R2 live reads
- no Cloudflare R2 writes
- no Backblaze B2 writes
- no provider calls
- no model calls
- no live B2 reads
- no B2 writes
- no broad B2 scans
- no recursive smokes
- hidden Git flags h
- line[0]

The required evidence-report boolean keys are:

- `ok`
- `slice_id: ps038`
- `production_readiness_demo_mode_component_present`
- `production_readiness_demo_mode_data_module_present`
- `production_readiness_demo_mode_layer_present`
- `required_surfaces_have_production_readiness_demo_mode_layer`
- `trust_boundary_cross_reference_present`
- `multimodal_proof_cross_reference_present`
- `transcript_timestamp_cross_reference_present`
- `voice_audio_evidence_cross_reference_present`
- `campaign_intelligence_cross_reference_present`
- `cloudflare_backbone_cross_reference_present`
- `demo_mode_present`
- `readiness_posture_present`
- `production_readiness_status_present`
- `demo_mode_status_present`
- `local_demo_status_present`
- `judge_demo_status_present`
- `local_static_fallback_present`
- `golden_evidence_fallback_present`
- `checked_in_evidence_fallback_present`
- `live_dependency_status_present`
- `provider_dependency_status_present`
- `b2_dependency_status_present`
- `cloudflare_dependency_status_present`
- `deployment_evidence_status_present`
- `production_security_evidence_status_present`
- `production_compliance_evidence_status_present`
- `cold_start_mitigation_status_present`
- `startup_health_status_present`
- `cost_control_status_present`
- `provider_fallback_status_present`
- `failure_mode_status_present`
- `export_offline_evidence_status_present`
- `demo_path_evidence_present`
- `readiness_checklist_evidence_present`
- `local_verification_status_present`
- `live_verification_status_present`
- `disclosure_boundary_present`
- `not_claimed_status_present`
- `unknown_status_present`
- `planned_status_present`
- `ready_for_local_demo_status_present`
- `local_demo_evidence_present`
- `production_deployment_not_available_present`
- `production_readiness_evidence_not_available_present`
- `production_security_evidence_not_available_present`
- `production_compliance_evidence_not_available_present`
- `live_provider_evidence_not_available_present`
- `live_b2_evidence_not_available_present`
- `live_cloudflare_evidence_not_available_present`
- `cold_start_measurement_not_available_present`
- `cold_start_mitigation_planned_present`
- `final_submission_packaging_deferred_to_ps039_present`
- `proof_does_not_equal_truth_present`
- `demo_mode_does_not_equal_production_readiness_present`
- `production_readiness_layer_does_not_equal_production_readiness_claim_present`
- `readiness_checklist_does_not_equal_production_security_present`
- `local_demo_mode_does_not_equal_live_deployment_present`
- `cold_start_mitigation_plan_does_not_equal_measured_performance_guarantee_present`
- `low_cost_demo_posture_does_not_equal_cost_guarantee_present`
- `local_fallback_does_not_equal_live_provider_availability_present`
- `checked_in_evidence_does_not_equal_live_b2_availability_present`
- `cloudflare_dependency_posture_does_not_equal_live_cloudflare_availability_present`
- `demo_golden_readiness_evidence_does_not_equal_production_compliance_present`
- `no_production_readiness_claim`
- `no_production_security_claim`
- `no_production_compliance_claim`
- `no_legal_compliance_claim`
- `no_live_deployment_claim`
- `no_cloudflare_deployment_claim`
- `no_cloudflare_availability_claim`
- `no_backblaze_b2_live_availability_claim`
- `no_provider_availability_claim`
- `no_model_availability_claim`
- `no_uptime_guarantee_claim`
- `no_cost_guarantee_claim`
- `no_performance_guarantee_claim`
- `no_cold_start_performance_guarantee_claim`
- `no_load_test_coverage_claim`
- `no_vulnerability_scan_coverage_claim`
- `no_penetration_test_coverage_claim`
- `no_incident_response_readiness_claim`
- `no_slo_sla_guarantee_claim`
- `no_data_retention_compliance_claim`
- `no_privacy_compliance_claim`
- `no_object_lock_claim`
- `no_tamper_proof_claim`
- `no_browser_side_b2_byte_verification_claim`
- `no_semantic_truth_claim`
- `no_legal_authenticity_claim`
- `no_human_authorship_claim`
- `no_c2pa_authenticity_claim`
- `no_campaign_performance_prediction_claim`
- `no_marketing_effectiveness_proof_claim`
- `no_model_output_truth_claim`
- `no_deployment_changes`
- `no_env_secrets_changes`
- `no_render_yaml_changes`
- `no_requirements_dependency_changes`
- `no_cloudflare_api_calls`
- `no_dns_mutation`
- `no_cloudflare_resource_creation`
- `no_cloudflare_pages_deployment`
- `no_cloudflare_workers_deployment`
- `no_cloudflare_r2_live_reads`
- `no_cloudflare_r2_writes`
- `no_backblaze_b2_writes`
- `no_provider_calls`
- `no_model_calls`
- `no_live_b2_reads`
- `no_b2_writes`
- `no_broad_b2_scans`
- `no_recursive_smokes`
- `no_hidden_git_flags_h`
- `no_hidden_git_flags_S`
- `no_forbidden_overclaims`
- `prior_evidence_clean`
- `failures`

The required regression-gate and smoke contract commands and paths are:

- `python scripts/proofstudio_regression_gate.py --current ps038 --frontend --report-out /tmp/proofstudio-release-report.json`
- `python scripts/proofstudio_regression_gate.py --current ps038 --no-frontend --report-out /tmp/proofstudio-ps038-regression-report.json`
- `scripts/ps038_production_readiness_demo_mode_smoke.py`
- `docs/evidence/ps-038/production-readiness-demo-mode-report.json`
- `docs/ps-038-production-readiness-demo-mode-proof.md`
