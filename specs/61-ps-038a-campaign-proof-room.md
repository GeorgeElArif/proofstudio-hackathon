# PS-038a — Campaign Proof Room

## 1. Status

PS-038a — Campaign Proof Room is currently:

- Spec only.
- Implementation pending. No product code, frontend code, backend code,
  scripts, evidence, AGENTS.md, `.env*`, `render.yaml`, or requirements files
  are changed during this phase.

PS-038a must not be implemented, and no implementation files may be changed,
until this spec is accepted by the PM. The authoritative accepted base is the
dynamic Git ref `origin/accepted/proofstudio`, never a hardcoded commit hash.
At the time of this spec the ref resolves to commit
`de428e51c855b2de3c5a0ef6ce3421360058bbd8` (the post-PS-038 accepted state).
The ref is the authority; the commit hash is recorded for traceability only
and must not be treated as a hardcoded base.

This spec-only commit touches only this file:
`specs/61-ps-038a-campaign-proof-room.md`.

PS-038a must not deploy ProofStudio, must not make any Cloudflare API call, must
not mutate DNS, must not create any Cloudflare resource, must not deploy
Cloudflare Pages, must not deploy Cloudflare Workers, must not perform
Cloudflare R2 live reads, must not perform Cloudflare R2 writes, must not
perform Backblaze B2 writes, must not call any live provider, must not call
any model, must not read or write live B2, must not perform broad B2 scans,
must not change `.env*` / `render.yaml` / requirements / deployment config,
must not mutate any evidence, must not run the frontend, must not run the
backend, must not stage, commit, or push, and must not print secrets during
this phase. PS-038a obeys the root `AGENTS.md` operating law and the validation
policy in `docs/validation/proofstudio-smoke-harness-v1.md`.

PS-038a defines a marquee Campaign Proof Room: a judge-facing guided evidence
room that assembles the existing accepted ProofStudio proof layers into one
campaign-level story. It is a navigation, evidence, and narrative surface over
recorded proof. It is not a new generation pipeline. It is not a new
provider/model integration. It is not campaign performance proof. It is not
marketing effectiveness proof. It is not semantic truth. It is not legal
authenticity. It is not production readiness. It does not deploy ProofStudio.
It does not change env/secrets/deployment config. It does not call live
providers or models. It does not call Cloudflare. It does not read/write live
B2.

## 2. Purpose

PS-038a defines a reusable Campaign Proof Room — a judge-facing campaign-level
command room for one proof-backed campaign — that guides a judge through the
campaign artifact, the recorded proof trail, the provenance passport, the
review/approval state, the B2 archive/rehydrate evidence, the manifest
verification evidence, the multimodal proof, the transcript/timestamp evidence,
the voice/audio evidence choices, the campaign intelligence / judge narrative,
the Cloudflare/backbone posture, the production-readiness / demo-mode posture,
the export evidence, and the truth boundaries. The room reads only what the
pipeline already recorded (B2 / archive / rehydrate evidence, Genblaze /
manifest evidence, the PS-037 Disclosure + Trust Boundary, the PS-037a
Multimodal Proof Layer, the PS-037b AssemblyAI Transcript/Timestamp Evidence
layer, the PS-037c Voice/Audio Evidence Provider Choice layer, the PS-037d
Gemini Campaign Intelligence / Judge Narrative layer, the PS-037e Cloudflare
Low-Cost Backbone layer, and the PS-038 Production Readiness + Demo Mode layer)
and renders one consistent campaign-level proof / evidence map / proof trail /
proof timeline / inspection path / judge demo path that makes a single
campaign's recorded proof, available evidence, unavailable evidence, and
truth boundary inspectable for judges, customers, and demo reviewers.

PS-038a makes the campaign-level proof, the campaign evidence room, the
judge-facing campaign room, the guided campaign proof trail, the recorded
campaign artifact, the campaign proof summary, the proof trail, the proof
timeline, the evidence map, the inspection path, and the judge demo path
explicit and inspectable in one place, before the final submission packaging
slice (PS-039). The room answers, in one consistent place, the basic
campaign-level questions a judge or demo reviewer asks:

- what campaign artifact was made
- what proof exists for the campaign artifact
- what evidence can be inspected for the campaign artifact
- what evidence remains unavailable or not claimed for the campaign artifact
- how B2 / Genblaze / rehydrate / manifest / provider evidence fit together
  for the campaign
- how demo / readiness posture fits the campaign demo
- what the system proves and does not prove for the campaign
- how the product creates real-world utility for creator/marketing teams
- what proof is available and what proof is unavailable
- what is planned, deferred, not claimed, or unknown

The room is a navigation / evidence / narrative surface over already-recorded
or honestly-unavailable data, not a new generation pipeline, not a new
provider/model integration, not a campaign performance proof, not a marketing
effectiveness proof, not a business outcome guarantee, not a semantic truth,
not a legal authenticity, not a legal approval, not a human authorship, not a
C2PA authenticity, not a production readiness claim, not a production security
claim, not a production compliance claim, not a legal compliance claim, not a
live deployment, not a provider availability claim, not a model availability
claim, not a Backblaze B2 live availability claim, not a Cloudflare
availability claim, not an uptime guarantee, not a cost guarantee, not a
performance guarantee, not a cold-start performance guarantee, not an Object
Lock, not a tamper-proof storage, not a browser-side B2 byte verification, not
a content moderation correctness claim, not a transcript correctness claim,
not an emotion truth, not a speaker identity, not a biometric identity, not a
model output truth, not a Cloudflare API call, not a DNS mutation, not a
Cloudflare resource creation, not a Cloudflare Pages deployment, not a
Cloudflare Workers deployment, not a Cloudflare R2 live read, not a Cloudflare
R2 write, not a Backblaze B2 write, not a live B2 read, not a B2 write, not a
broad B2 scan, not a provider call, and not a model call. It makes the existing
campaign-level proof framing consistent and judge-safe, and it states honestly
what ProofStudio proves and what ProofStudio does not prove for a campaign.

PS-038a proves what the pipeline recorded. The room does not prove campaign
performance, marketing effectiveness, business outcome, semantic truth, legal
authenticity, legal approval, human authorship, C2PA authenticity, production
readiness, production security, production compliance, legal compliance, live
deployment, provider availability, model availability, Backblaze B2 live
availability, Cloudflare availability, uptime guarantee, cost guarantee,
performance guarantee, cold-start performance guarantee, Object Lock,
tamper-proof storage, browser-side B2 byte verification, content moderation
correctness, transcript correctness, emotion truth, speaker identity,
biometric identity, or model output truth.

The room reads accepted local / static / golden / checked-in / demo data and
existing accepted data modules only, or exposes explicit honest "proof
available" / "proof unavailable" / "not claimed" / "unknown" / "planned" /
"deferred" / "local verification" / "live verification not available" / "live
provider evidence not available" / "live B2 evidence not available" / "live
Cloudflare evidence not available" states. Naming "Campaign Proof Room",
"campaign-level proof", "campaign evidence room", "judge-facing campaign
room", "guided campaign proof trail", "campaign proof summary", "campaign
narrative", or "campaign intelligence evidence" does not imply a campaign
performance proof, a marketing effectiveness proof, a business outcome
guarantee, a semantic truth, a legal authenticity, a legal approval, a human
authorship, a C2PA authenticity, a production readiness claim, a production
security claim, a production compliance claim, an uptime guarantee, a cost
guarantee, a performance guarantee, a cold-start performance guarantee, an
Object Lock, a tamper-proof storage, a browser-side B2 byte verification, a
content moderation correctness, a transcript correctness, an emotion truth, a
speaker identity, a biometric identity, or a model output truth. The Campaign
Proof Room does not equal campaign performance proof. Campaign narrative does
not equal marketing effectiveness proof. Campaign intelligence evidence does
not equal business outcome guarantee. Campaign artifact evidence does not
equal legal authenticity. Local campaign evidence does not equal live provider
availability. Checked-in campaign evidence does not equal live B2 availability.
Cloudflare backbone posture does not equal live Cloudflare availability. Demo
mode posture does not equal production readiness. Review approval evidence does
not equal legal approval. Provenance passport evidence does not equal C2PA
authenticity. Manifest evidence does not equal semantic truth.
Transcript/timestamp evidence does not equal transcript correctness. Voice/
audio evidence does not equal speaker identity. Proof does not equal truth.

## 3. Root Cause / Product Gap

ProofStudio now records a deep proof stack and exposes it across many honest
surfaces: the Disclosure + Trust Boundary (PS-037), the Multimodal Proof Layer
(PS-037a), the AssemblyAI Transcript/Timestamp Evidence layer (PS-037b), the
Voice/Audio Evidence Provider Choice layer (PS-037c), the Gemini Campaign
Intelligence / Judge Narrative layer (PS-037d), the Cloudflare Low-Cost
Backbone layer (PS-037e), the Production Readiness + Demo Mode layer (PS-038),
B2 archive + rehydrate evidence (PS-010, PS-020, PS-021, PS-026, PS-029,
PS-036), Genblaze manifest evidence (PS-028), the Review + Approval Workspace
(PS-035), the Judge Evidence Pack / Export Pack (PS-031), the Public Provenance
Passport (PS-019/PS-025), the Manifest Verification Panel (PS-028), the B2
Evidence Explorer (PS-026), the B2 Rehydrate Comparison (PS-029), the Archive /
Rehydrate / B2 Audit Vault (PS-036), and the Judge Cockpit Home (PS-023). Each
layer is honest about what it proves and what it does not prove.

Those layers are honest, but none of them assembles the campaign-level story in
one judge-facing place. There is no campaign-level command room where a judge
or demo reviewer can read, in one guided proof trail: what campaign artifact
was made; what proof exists for that campaign artifact; what evidence can be
inspected; what evidence remains unavailable or not claimed; how B2 / Genblaze
/ rehydrate / manifest / provider evidence fit together for the campaign; how
demo / readiness posture fits the campaign demo; what the system proves and
does not prove for the campaign; how the product creates real-world utility for
creator/marketing teams; what proof is available and what proof is unavailable;
what is planned, deferred, not claimed, or unknown. The gap this creates is
judge-safety at the campaign boundary: a judge landing on the product today has
to assemble the campaign story by hopping between many separate surfaces, and
risks mistaking a campaign narrative word, a campaign intelligence label, a
"proof room" name, or a checked-in campaign artifact for a campaign performance
proof, a marketing effectiveness proof, a business outcome guarantee, a legal
authenticity, a legal approval, a C2PA authenticity, a semantic truth, a
production readiness claim, or a live deployment. Today:

- no accepted slice records a campaign-level proof room, a campaign evidence
  room, a judge-facing campaign room, a guided campaign proof trail, a
  recorded campaign artifact view, a campaign artifact evidence summary, a
  campaign proof summary, a campaign proof trail, a campaign proof timeline, a
  campaign evidence map, a campaign inspection path, a campaign judge demo
  path, a campaign artifact reference, a campaign artifact digest, a campaign
  manifest evidence cross-reference, a campaign archive evidence
  cross-reference, a campaign rehydrate evidence cross-reference, a campaign
  review evidence cross-reference, a campaign approval evidence
  cross-reference, a campaign export pack evidence cross-reference, a campaign
  provenance passport evidence cross-reference, a campaign B2 evidence
  cross-reference, a campaign Genblaze manifest evidence cross-reference, a
  campaign rehydrate comparison evidence cross-reference, a campaign
  multimodal artifact evidence cross-reference, a campaign transcript/
  timestamp evidence cross-reference, a campaign voice/audio evidence
  cross-reference, a campaign intelligence evidence cross-reference, a
  Cloudflare backbone posture cross-reference, a production readiness demo
  mode posture cross-reference, a creator/marketing workflow utility framing,
  or a set of honest "proof available" / "proof unavailable" / "not claimed" /
  "unknown" / "planned" / "deferred" / "local verification" / "live
  verification not available" / "live provider evidence not available" / "live
  B2 evidence not available" / "live Cloudflare evidence not available"
  campaign-level states in a single inspectable place.
- a judge reading the product today cannot, in one place, see what campaign
  artifact was made, what proof exists, what can be inspected, what is
  unavailable or not claimed, how B2 / Genblaze / rehydrate / manifest /
  provider evidence fit together for the campaign, how demo / readiness posture
  fits the campaign demo, and what the system proves and does not prove for the
  campaign. A "Campaign Proof Room" name that appears without a clear
  disclosure boundary looks like a campaign performance proof; a "campaign
  narrative" that appears without a clear boundary looks like a marketing
  effectiveness proof; a "campaign intelligence" label that appears without a
  clear boundary looks like a business outcome guarantee; a "proof trail" that
  appears without a clear boundary looks like legal authenticity; a "campaign
  artifact evidence" phrase that appears without a clear boundary looks like
  human authorship or C2PA authenticity.

PS-038a closes that gap by adding one Campaign Proof Room — a campaign-level
data module plus a campaign-level page component on its own route, plus an
additive campaign-room CTA/link from the Judge Cockpit Home and/or accepted app
navigation — that the proof surfaces cross-reference additively. The room reads
only accepted local / static / golden / checked-in / demo evidence and the
existing accepted data modules, or exposes explicit honest "proof available" /
"proof unavailable" / "not claimed" / "unknown" / "planned" / "deferred" /
"local verification" / "live verification not available" / "live provider
evidence not available" / "live B2 evidence not available" / "live Cloudflare
evidence not available" states. It does not invent a new generation pipeline, a
new provider/model integration, a campaign performance proof, a marketing
effectiveness proof, a business outcome guarantee, a semantic truth, a legal
authenticity, a legal approval, a human authorship, a C2PA authenticity, a
production readiness claim, a production security claim, a production
compliance claim, a legal compliance claim, a live deployment, a provider
availability, a model availability, a Backblaze B2 live availability, a
Cloudflare availability, an uptime guarantee, a cost guarantee, a performance
guarantee, a cold-start performance guarantee, an Object Lock, a tamper-proof
storage, a browser-side B2 byte verification, a content moderation
correctness, a transcript correctness, an emotion truth, a speaker identity, a
biometric identity, or a model output truth. It is local / static by default:
it adds no deployment changes, no env/secrets changes, no render.yaml changes,
no requirements/dependency changes, no Cloudflare API calls, no DNS mutation,
no Cloudflare resource creation, no Cloudflare Pages deployment, no Cloudflare
Workers deployment, no Cloudflare R2 live reads, no Cloudflare R2 writes, no
Backblaze B2 writes, no provider calls, no model calls, no live B2 reads, no
B2 writes, no broad B2 scans, no new backend, and no new paid service
dependency.

The Campaign Proof Room is named as a judge-facing campaign-level evidence /
navigation / narrative surface over recorded proof only. Naming the Campaign
Proof Room does not imply a campaign performance proof, a marketing
effectiveness proof, a business outcome guarantee, a semantic truth, a legal
authenticity, a legal approval, a human authorship, a C2PA authenticity, a
production readiness claim, a production security claim, a production
compliance claim, an uptime guarantee, a cost guarantee, a performance
guarantee, a cold-start performance guarantee, an Object Lock, a tamper-proof
storage, a browser-side B2 byte verification, a content moderation
correctness, a transcript correctness, an emotion truth, a speaker identity, a
biometric identity, or a model output truth. The implementation must default
to local/static behavior. No live provider/API/B2/Cloudflare/model behavior may
occur unless a later PM-approved slice explicitly enables it with env gates,
cost controls, rollback, and evidence boundaries. The implementation phase
relies on checked-in local / static / golden / demo evidence or explicit
unavailable states, and must not require live provider credentials, live model
credentials, live B2 credentials, or live Cloudflare credentials.

## 4. User Story

As a reviewer (designer, marketer, reviewer, client, or judge), I want one
honest, consistent Campaign Proof Room — a campaign-level command room for one
proof-backed campaign — so that in one place I can immediately read: what
campaign artifact was made; what proof exists for the campaign artifact; what
evidence can be inspected; what evidence remains unavailable or not claimed;
how B2 / Genblaze / rehydrate / manifest / provider evidence fit together for
the campaign; how demo / readiness posture fits the campaign demo; what the
system proves and does not prove for the campaign; how the product creates
real-world utility for creator/marketing teams; what proof is available and
what proof is unavailable; what is planned, deferred, not claimed, or unknown;
and whether campaign performance proof, marketing effectiveness proof,
business outcome guarantee, semantic truth, legal authenticity, legal
approval, human authorship, C2PA authenticity, production readiness, production
security, production compliance, legal compliance, live deployment, provider
availability, model availability, Backblaze B2 live availability, Cloudflare
availability, uptime guarantee, cost guarantee, performance guarantee,
cold-start performance guarantee, Object Lock, tamper-proof storage,
browser-side B2 byte verification, content moderation correctness, transcript
correctness, emotion truth, speaker identity, biometric identity, or model
output truth is claimed — and so I never mistake a Campaign Proof Room for a
campaign performance proof, a campaign narrative for a marketing effectiveness
proof, a campaign intelligence label for a business outcome guarantee, a proof
trail for legal authenticity, a campaign artifact evidence phrase for human
authorship or C2PA authenticity, local campaign evidence for live provider
availability, checked-in campaign evidence for live B2 availability, a
Cloudflare backbone posture for live Cloudflare availability, a demo mode
posture for production readiness, a review approval record for legal approval,
a provenance passport for C2PA authenticity, manifest evidence for semantic
truth, transcript/timestamp evidence for transcript correctness, or voice/
audio evidence for speaker identity.

As a creator or marketing team member, I want one campaign-level room that
shows how the recorded proof, the available evidence, the unavailable
evidence, the provenance passport, the review/approval state, the B2 archive /
rehydrate evidence, the manifest verification, the multimodal proof, the
transcript/timestamp evidence, the voice/audio evidence, the campaign
intelligence / judge narrative, the Cloudflare backbone posture, and the
demo / readiness posture fit together for a real campaign artifact — so the
product creates real-world utility for creator/marketing workflow without
overclaiming campaign performance, marketing effectiveness, or business
outcome.

As a demo presenter, I want a reusable Campaign Proof Room that is useful in a
three-minute hackathon demo: a compact campaign proof summary that lists the
recorded campaign artifact, the proof available, the proof unavailable, the
inspection path, the judge demo path, the campaign proof trail, the campaign
proof timeline, the evidence map, and the honest "proof available" / "proof
unavailable" / "not claimed" / "unknown" / "planned" / "deferred" / "local
verification" / "live verification not available" states, plus an expanded
guided campaign proof trail / evidence map that states, verbatim, what the
Campaign Proof Room proves, what it does not prove, what is unavailable, what
is not claimed, what is planned, what is deferred, what the inspection path
is, what the judge demo path is, and what the shared disclosure boundary is —
all working offline from accepted local / static / golden / demo fixtures,
with no deployment changes, no env/secrets changes, no render.yaml changes, no
requirements/dependency changes, no Cloudflare API calls, no DNS mutation, no
Cloudflare resource creation, no Cloudflare Pages deployment, no Cloudflare
Workers deployment, no Cloudflare R2 live reads, no Cloudflare R2 writes, no
Backblaze B2 writes, no provider calls, no model calls, no live B2 reads, no
B2 writes, and no broad B2 scans.

## 5. Current Accepted Base

The current accepted base for PS-038a is:

- branch: `accepted/proofstudio`
- ref: `origin/accepted/proofstudio` (the authoritative source of truth; the
  ref is the authority, not any hardcoded commit hash)
- commit the ref resolves to at the time of this spec:
  `de428e51c855b2de3c5a0ef6ce3421360058bbd8`
- this is the post-PS-038 accepted state: the Disclosure + Trust Boundary
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
  `apps/web/src/CloudflareLowCostBackboneLayer.tsx`); the Production
  Readiness + Demo Mode layer from PS-038 is in place
  (`apps/web/src/productionReadinessDemoMode.ts` +
  `apps/web/src/ProductionReadinessDemoModeLayer.tsx`); the Archive / Rehydrate
  / B2 Audit Vault is in place from PS-036; the Review + Approval Workspace is
  in place from PS-035; the root `AGENTS.md` operating law is in place
  (PS-035D); the accepted-base-pointer-drift guard is in place (PS-035E); the
  central regression gate is non-mutating by default from PS-035C; the
  golden-fixture digest freeze is in place from PS-035B; the golden-run
  manifest carries a real non-null `manifest_uri` and a real 64-hex
  `manifest_hash` from PS-035A.

PS-038a must start from `origin/accepted/proofstudio`, not from `main`.

Relevant accepted facts at this base that PS-038a builds on (PS-038a must not
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
  core proof surfaces; PS-038a integrates with it and does not weaken it
- the PS-037a Multimodal Proof Layer exists and is rendered on the core proof
  surfaces; PS-038a cross-references PS-037a and does not weaken it
- the PS-037b AssemblyAI Transcript/Timestamp Evidence layer exists and is
  rendered on the core proof surfaces; PS-038a cross-references PS-037b and
  does not weaken it
- the PS-037c Voice/Audio Evidence Provider Choice layer exists and is
  rendered on the core proof surfaces; PS-038a cross-references PS-037c and
  does not weaken it
- the PS-037d Gemini Campaign Intelligence / Judge Narrative layer exists and
  is rendered on the core proof surfaces; PS-038a cross-references PS-037d and
  does not weaken it
- the PS-037e Cloudflare Low-Cost Backbone layer exists and is rendered on the
  core proof surfaces; PS-038a cross-references PS-037e and does not weaken it
- the PS-038 Production Readiness + Demo Mode layer exists and is rendered on
  the core proof surfaces; PS-038a cross-references PS-038 and does not weaken
  it
- the existing shared component classes (`.trust-boundary`,
  `.trust-boundary-layer*`, the multimodal proof layer classes, the
  transcript/timestamp evidence layer classes, the voice/audio evidence
  provider choice layer classes, the campaign-intelligence / judge-narrative
  layer classes, the cloudflare-low-cost-backbone layer classes, the
  production-readiness-demo-mode layer classes, pills, cards, `JsonExpander`)
  already exist in `apps/web/src/styles.css`
- the client-side route shell lives in `apps/web/src/App.tsx`: each surface is
  gated by an `is<Path>Path()` helper that reads `window.location.pathname`
  and is dispatched in the `App()` function (which returns
  `<Component variant="page" />`), and the Judge Cockpit Home
  (`apps/web/src/JudgeCockpitHome.tsx`, path `/`) exposes the navigation block
  of `<a className="btn" href="/route" title="...">` links to every surface

## 6. Scope

PS-038a is a product slice. It adds a Campaign Proof Room (a campaign-level
data module plus a campaign-level page component on its own route) and links
to it additively from the Judge Cockpit Home and/or accepted app navigation.
It is local / static by default: it must work without deployment changes,
without env/secrets changes, without render.yaml changes, without
requirements/dependency changes, without Cloudflare API calls, without DNS
mutation, without Cloudflare resource creation, without Cloudflare Pages
deployment, without Cloudflare Workers deployment, without Cloudflare R2 live
reads, without Cloudflare R2 writes, without Backblaze B2 writes, without
provider calls, without model calls, without live B2 reads, without B2
writes, and without broad B2 scans, by reading accepted local / static /
golden / demo fixtures and existing accepted data modules, or by surfacing
explicit honest "proof available" / "proof unavailable" / "not claimed" /
"unknown" / "planned" / "deferred" / "local verification" / "live
verification not available" / "live provider evidence not available" / "live
B2 evidence not available" / "live Cloudflare evidence not available" states.

PS-038a owns presentation, routing, campaign-level aggregation, judge
guidance, proof navigation, and evidence narrative only. It must:

1. Add a shared, canonical Campaign Proof Room data module
   (`apps/web/src/campaignProofRoom.ts`, or the project's accepted equivalent)
   that exposes one consistent set of campaign-level concepts — the Campaign
   Proof Room, the campaign-level proof, the campaign evidence room, the
   judge-facing campaign room, the guided campaign proof trail, the recorded
   campaign artifact, the campaign artifact evidence, the campaign proof
   summary, the proof trail, the proof timeline, the evidence map, the
   inspection path, the judge demo path, the creator/marketing workflow
   utility framing, the campaign artifact reference, the campaign artifact
   digest, the campaign manifest evidence, the campaign archive evidence, the
   campaign rehydrate evidence, the campaign review evidence, the campaign
   approval evidence, the export pack evidence, the provenance passport
   evidence, the B2 evidence, the Genblaze manifest evidence, the rehydrate
   comparison evidence, the multimodal artifact evidence, the transcript/
   timestamp evidence, the voice/audio evidence, the campaign intelligence
   evidence, the Cloudflare backbone posture, the production readiness demo
   mode posture, the readiness posture, the demo mode posture, the local/
   static evidence, the checked-in evidence, the local verification, the live
   verification status, honest "proof available" / "proof unavailable" / "not
   claimed" / "unknown" / "planned" / "deferred" / "live verification not
   available" / "live provider evidence not available" / "live B2 evidence
   not available" / "live Cloudflare evidence not available" states, the
   cross-references (trust boundary / multimodal proof / transcript/
   timestamp / voice/audio / campaign intelligence / cloudflare backbone /
   production readiness demo mode), deferred later-slice states, the
   de-escalation pairs, the negative boundary strings, and the final
   submission packaging deferred to PS-039 state.
2. Add a Campaign Proof Room page component (`apps/web/src/CampaignProofRoom.tsx`,
   or the project's accepted equivalent) that renders the room, including a
   campaign proof summary, a guided campaign proof trail, a proof timeline, an
   evidence map, an inspection path, a judge demo path, and a campaign truth
   boundary panel, reading only from `apps/web/src/campaignProofRoom.ts`.
3. Register the Campaign Proof Room route `/campaign-proof-room` in the
   client-side route shell (`apps/web/src/App.tsx`) using the accepted
   `is<Path>Path()` + `window.location.pathname` convention, dispatched in the
   `App()` function before the passport / review / default fallbacks, returning
   `<CampaignProofRoom variant="page" />`.
4. Add an additive campaign-room CTA/link from the Judge Cockpit Home
   (`apps/web/src/JudgeCockpitHome.tsx`) and/or the accepted app navigation,
   following the existing `<a className="btn" href="/campaign-proof-room"
   title="...">` convention.
5. Optionally add compact links from the proof surfaces back to the campaign
   room if consistent with existing conventions; any such link must be
   additive and must not weaken an existing surface.
6. State, for the campaign-level proof, "what ProofStudio proves" and "what
   ProofStudio does not prove."
7. Surface the canonical Campaign Proof Room concepts (section 10.2) verbatim.
8. Surface the honest unavailable / not-claimed / planned / deferred states
   (section 10.6) verbatim so no reviewer mistakes an absent campaign value
   for a hidden proof, and no reviewer mistakes a Campaign Proof Room, a
   campaign narrative, a campaign intelligence label, a proof trail, or a
   campaign artifact evidence phrase for a campaign performance proof, a
   marketing effectiveness proof, a business outcome guarantee, a legal
   authenticity, a legal approval, a human authorship, a C2PA authenticity, a
   production readiness claim, a production security claim, a production
   compliance claim, a cost guarantee, an uptime guarantee, a performance
   guarantee, or a cold-start performance guarantee.
9. Surface the canonical Campaign Proof Room de-escalation pairs (section 10.7)
   verbatim so no judge mistakes a strong-sounding Campaign Proof Room,
   campaign-level proof, campaign evidence room, judge-facing campaign room,
   guided campaign proof trail, campaign narrative, campaign intelligence
   evidence, campaign artifact evidence, local campaign evidence, checked-in
   campaign evidence, Cloudflare backbone posture, demo mode posture, review
   approval evidence, provenance passport evidence, manifest evidence,
   transcript/timestamp evidence, or voice/audio evidence for a stronger
   guarantee.
10. Surface the canonical Campaign Proof Room negative boundary strings
    (section 10.8) verbatim.
11. Integrate with the PS-037 TrustBoundaryLayer (render alongside it / link to
    it; reuse the shared disclosure concepts; do not duplicate or weaken the
    PS-037 boundary).
12. Integrate / cross-reference with the PS-037a MultimodalProofLayer (surface
    an honest multimodal artifact evidence cross-reference; do not duplicate or
    weaken the PS-037a layer).
13. Integrate / cross-reference with the PS-037b TranscriptTimestampEvidenceLayer
    (surface an honest transcript/timestamp evidence cross-reference; do not
    duplicate or weaken the PS-037b layer).
14. Integrate / cross-reference with the PS-037c VoiceAudioEvidenceChoiceLayer
    (surface an honest voice/audio evidence cross-reference; do not duplicate or
    weaken the PS-037c layer).
15. Integrate / cross-reference with the PS-037d
    CampaignIntelligenceJudgeNarrativeLayer (surface an honest campaign
    intelligence evidence cross-reference; do not duplicate or weaken the
    PS-037d layer).
16. Integrate / cross-reference with the PS-037e CloudflareLowCostBackboneLayer
    (surface an honest Cloudflare backbone posture cross-reference; do not
    duplicate or weaken the PS-037e layer).
17. Integrate / cross-reference with the PS-038 ProductionReadinessDemoModeLayer
    (surface an honest production readiness demo mode posture cross-reference;
    do not duplicate or weaken the PS-038 layer).
18. Preserve the existing per-surface artifact / boundary panels; the Campaign
    Proof Room complements them and links to them. PS-038a must not delete or
    weaken any existing per-surface non-claim, per-surface artifact record, the
    PS-037 disclosure contract, the PS-037a multimodal proof contract, the
    PS-037b transcript/timestamp contract, the PS-037c voice/audio evidence
    provider choice contract, the PS-037d campaign intelligence / judge
    narrative contract, the PS-037e Cloudflare low-cost backbone contract, or
    the PS-038 production readiness + demo mode contract.
19. Be demo-friendly and judge-friendly: useful in a three-minute demo, no
    generic campaign hype copy, no unsupported claims, no faked live
    deployment, no faked campaign performance proof, no faked marketing
    effectiveness proof, no faked business outcome guarantee, no faked
    production readiness, no faked production security, no faked production
    compliance, no faked cost guarantee, no faked uptime guarantee, no faked
    performance guarantee, no faked cold-start performance guarantee, no faked
    legal authenticity, no faked legal approval, no faked human authorship, no
    faked C2PA authenticity, no faked Object Lock, no faked tamper-proof
    storage, no faked browser-side B2 byte verification, no faked content
    moderation correctness, no faked transcript correctness, no faked emotion
    truth, no faked speaker identity, no faked biometric identity, no faked
    model output truth.
20. Work without deployment changes, without env/secrets changes, without
    render.yaml changes, without requirements/dependency changes, without
    Cloudflare API calls, without DNS mutation, without Cloudflare resource
    creation, without Cloudflare Pages deployment, without Cloudflare Workers
    deployment, without Cloudflare R2 live reads, without Cloudflare R2
    writes, without Backblaze B2 writes, without provider calls, without
    model calls, without live B2 reads, without B2 writes, and without broad
    B2 scans, by using accepted local / static / golden / demo data or
    existing accepted data paths.
21. Not mutate any prior evidence. Any PS-038a-owned evidence lives only under
    `docs/evidence/ps-038a/`.
22. Not change the golden run canonical constants, the historical contracts
    the regression gate verifies, any provider / B2 / model behavior, the
    PS-037 disclosure contract, the PS-037a multimodal proof contract, the
    PS-037b transcript/timestamp contract, the PS-037c voice/audio evidence
    provider choice contract, the PS-037d campaign intelligence / judge
    narrative contract, the PS-037e Cloudflare low-cost backbone contract, or
    the PS-038 production readiness + demo mode contract.

## 7. Non-goals

PS-038a must not:

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
- do not implement a new generation pipeline
- do not implement a new provider/model integration
- do not implement live production deployment
- do not implement the later or out-of-scope capabilities:
  - campaign performance measurement, marketing effectiveness measurement,
    business outcome guarantee, semantic truth, legal authenticity, legal
    approval, human authorship, C2PA authenticity, production readiness,
    production security, production compliance, legal compliance, live
    deployment, provider availability, model availability, Backblaze B2 live
    availability, Cloudflare availability, uptime guarantee, cost guarantee,
    performance guarantee, cold-start performance guarantee, DNS ownership,
    Object Lock, tamper-proof storage, browser-side B2 byte verification,
    content moderation correctness, transcript correctness, emotion truth,
    speaker identity, biometric identity, model output truth (PS-038a must
    only reserve honest "not claimed" / "unknown" / "planned" / "deferred"
    states for these; it must not fake them)
  - final submission packaging (deferred to PS-039)
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
- do not claim campaign performance proof
- do not claim marketing effectiveness proof
- do not claim business outcome guarantee
- do not claim semantic truth
- do not claim legal authenticity
- do not claim legal approval
- do not claim human authorship
- do not claim C2PA authenticity
- do not claim production readiness
- do not claim production security
- do not claim production compliance
- do not claim legal compliance
- do not claim live deployment
- do not claim provider availability
- do not claim model availability
- do not claim Backblaze B2 live availability
- do not claim Cloudflare availability
- do not claim uptime guarantee
- do not claim cost guarantee
- do not claim performance guarantee
- do not claim cold-start performance guarantee
- do not claim Object Lock / tamper-proof storage unless implemented and
  verified
- do not claim browser-side B2 byte verification unless implemented and
  verified
- do not claim content moderation correctness
- do not claim transcript correctness
- do not claim emotion truth
- do not claim speaker identity
- do not claim biometric identity
- do not claim model output truth
- do not delete or weaken any existing per-surface truth-boundary panel,
  non-claim, artifact record, the PS-037 disclosure contract, the PS-037a
  multimodal proof contract, the PS-037b transcript/timestamp contract, the
  PS-037c voice/audio evidence provider choice contract, the PS-037d campaign
  intelligence / judge narrative contract, the PS-037e Cloudflare low-cost
  backbone contract, or the PS-038 production readiness + demo mode contract
- do not add a new backend, a new generation pipeline, a new provider/model
  integration, a new Cloudflare client, a new provider wrapper, a new model
  client, a new B2 client, a new B2 write path, a new broad B2 scan path, a
  new env variable, a new paid service dependency, or any deployment change
- do not change the golden run canonical constants
- do not change the historical contracts the regression gate verifies
- do not change the PS-037 disclosure contract
- do not change the PS-037a multimodal proof contract
- do not change the PS-037b transcript/timestamp contract
- do not change the PS-037c voice/audio evidence provider choice contract
- do not change the PS-037d campaign intelligence / judge narrative contract
- do not change the PS-037e Cloudflare low-cost backbone contract
- do not change the PS-038 production readiness + demo mode contract
- do not introduce a control name containing `KEY`, `TOKEN`, or `SECRET`
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not run recursive smokes
- do not use generic campaign hype copy or unsupported claims
- do not create duplicate context-blind overclaim scanners in chat/spec
  guidance; the future PS-038a smoke and its evidence report are the source of
  truth for slice overclaim validation; do not scan smoke guard fixtures as
  product claims

PS-038a only edits this spec file in the spec-only phase.
Implementation-phase candidate files are listed in section 8.

## 8. Implementation Candidate Files

The following are implementation-phase candidates only, clearly marked as
implementation-phase only. They are **not** for this spec-only commit. They are
listed so the implementation phase has a grounded file plan that follows
existing app conventions (each surface has a PascalCase `.tsx` component, a
camelCase `.ts` data module, a route in `App.tsx`, a navigation link in
`JudgeCockpitHome.tsx`, a smoke script, and an evidence directory).

Campaign Proof Room (new files):
- `apps/web/src/campaignProofRoom.ts` (new) — the canonical camelCase Campaign
  Proof Room data module. Exposes the single shared set of campaign-level
  concepts — the Campaign Proof Room, the campaign-level proof, the campaign
  evidence room, the judge-facing campaign room, the guided campaign proof
  trail, the recorded campaign artifact, the campaign artifact evidence, the
  campaign proof summary, the proof trail, the proof timeline, the evidence
  map, the inspection path, the judge demo path, the creator/marketing
  workflow utility framing, the campaign artifact reference, the campaign
  artifact digest, the campaign manifest evidence, the campaign archive
  evidence, the campaign rehydrate evidence, the campaign review evidence, the
  campaign approval evidence, the export pack evidence, the provenance
  passport evidence, the B2 evidence, the Genblaze manifest evidence, the
  rehydrate comparison evidence, the multimodal artifact evidence, the
  transcript/timestamp evidence, the voice/audio evidence, the campaign
  intelligence evidence, the Cloudflare backbone posture, the production
  readiness demo mode posture, the readiness posture, the demo mode posture,
  the local/static evidence, the checked-in evidence, the local verification,
  the live verification status, honest "proof available" / "proof unavailable"
  / "not claimed" / "unknown" / "planned" / "deferred" / "live verification
  not available" / "live provider evidence not available" / "live B2 evidence
  not available" / "live Cloudflare evidence not available" states, the
  cross-references (trust boundary / multimodal proof / transcript/timestamp /
  voice/audio / campaign intelligence / cloudflare backbone / production
  readiness demo mode), deferred later-slice states (final submission
  packaging deferred to PS-039), de-escalation pairs, negative boundary
  strings, and not-claimed / unknown / planned / deferred status. Same
  convention as `productionReadinessDemoMode.ts`, `cloudflareLowCostBackbone.ts`,
  `geminiCampaignIntelligence.ts`, `voiceAudioEvidenceChoice.ts`,
  `assemblyAITranscriptEvidence.ts`, `multimodalProof.ts`, `trustBoundary.ts`,
  `b2Evidence.ts`, `b2RehydrateComparison.ts`, `judgeEvidencePack.ts`, etc.
  The module must not contain a live provider call, a live model call, a
  Cloudflare API call, a live B2 read, a B2 write, a broad B2 scan, a DNS
  mutation, or a deployment change.
- `apps/web/src/CampaignProofRoom.tsx` (new) — the Campaign Proof Room page
  component. Accepts the existing `variant` convention (`variant="page"` for
  the full campaign-level command room; the data module may also support a
  `variant="summary"` / `variant="badge"` compact campaign proof summary if
  reused inline elsewhere), reads only from `apps/web/src/campaignProofRoom.ts`,
  and renders the Campaign Proof Room with no deployment changes, no
  env/secrets changes, no render.yaml changes, no requirements/dependency
  changes, no Cloudflare API calls, no DNS mutation, no Cloudflare resource
  creation, no Cloudflare Pages deployment, no Cloudflare Workers deployment,
  no Cloudflare R2 live reads, no Cloudflare R2 writes, no Backblaze B2
  writes, no provider calls, no model calls, no live B2 reads, no B2 writes,
  and no broad B2 scans.

Route + navigation (existing files, edited additively only):
- `apps/web/src/App.tsx` (PS-013 / PS-014 / PS-023 route shell) — add an
  `isCampaignProofRoomPath()` helper that reads `window.location.pathname` and
  returns true for `/campaign-proof-room` and `/campaign-proof-room/*`, and add
  a dispatch line `if (isCampaignProofRoomPath()) return <CampaignProofRoom
  variant="page" />;` in the `App()` function before the passport / review /
  default fallbacks. Follow the exact convention of the other
  `is<Path>Path()` + `<Component variant="page" />` dispatch lines.
- `apps/web/src/JudgeCockpitHome.tsx` (PS-023) — add an additive campaign-room
  CTA/link in the navigation block, following the existing `<a className="btn"
  href="/campaign-proof-room" title="Open the Campaign Proof Room (PS-038a)">`
  convention. Optionally, additional compact links from other proof surfaces
  back to the campaign room may be added if consistent with existing
  conventions; any such link must be additive and must not weaken an existing
  surface.

Additive styles (existing file, additive classes only):
- `apps/web/src/styles.css` — add only the classes needed for the Campaign
  Proof Room (campaign-proof-room container, campaign-proof-summary block,
  campaign-proof-trail rows, proof-timeline rows, evidence-map rows,
  inspection-path rows, judge-demo-path rows, campaign-artifact-reference
  rows, campaign-artifact-digest rows, cross-reference pills, proof-available
  / proof-unavailable / not-claimed / planned / deferred / unknown pills). No
  global style rewrite. PS-038a must not remove or weaken the existing
  `.trust-boundary-layer*` classes from PS-037, the multimodal proof layer
  classes from PS-037a, the transcript/timestamp evidence layer classes from
  PS-037b, the voice/audio evidence provider choice layer classes from
  PS-037c, the campaign-intelligence / judge-narrative layer classes from
  PS-037d, the cloudflare-low-cost-backbone layer classes from PS-037e, or the
  production-readiness-demo-mode layer classes from PS-038.

Backend (`src/proofstudio`) — none:
- PS-038a is a frontend-only Campaign Proof Room over existing accepted data.
  No backend change is expected. If any read-only reuse of an accepted data
  path is needed, it must reuse the existing accepted data paths under
  `src/proofstudio/api/` and `src/proofstudio/provenance/` without calling
  Cloudflare, without calling any provider, without calling any model, without
  reading live B2, without mutating DNS, and without creating any Cloudflare
  resource. No new provider wiring, no model client, no Cloudflare client, no
  new B2 client, no new B2 write path, no new broad B2 scan path, no new
  generation pipeline. If no backend change is needed, none is made.

Smoke (scripts):
- `scripts/ps038a_campaign_proof_room_smoke.py` (new) — the PS-038a feature
  smoke. Must reuse `scripts/smoke_lib.py` for shared validation logic and
  must implement its own explicit `h` / `S` hidden-Git-flags checker (see
  section 14). Local / static only.

Spec / docs:
- `specs/07-master-spec-plan.md` — implementation-phase cross-reference only
  (register PS-038a acceptance). Must not change any historical item or golden
  constant.
- `specs/08-roadmap-slices.md` — implementation-phase status update only.
- `docs/validation/proofstudio-smoke-harness-v1.md` — implementation-phase
  PS-038a note only, additive, must not weaken any existing PS-034A / PS-035C
  contract.
- `docs/ps-038a-campaign-proof-room-proof.md` (new) — the PS-038a proof doc.

Evidence:
- `docs/evidence/ps-038a/campaign-proof-room-report.json` (new) — the only
  evidence PS-038a may write, and only when `--write-evidence` is explicit.

Any edit to `src/proofstudio/**` during implementation requires the backend
change to remain read-only over accepted data and to make no Cloudflare API
call, no provider call, no model call, no live B2 read, no DNS mutation, and
no Cloudflare resource creation.

## 9. Forbidden files Unless PM-approved Later

PS-038a implementation must not touch without explicit PM approval:

- `AGENTS.md`
- `.env*`
- `render.yaml`
- requirements files
- `docs/evidence/**` paths other than `docs/evidence/ps-038a/**`
- any prior-slice evidence prefix (for example `docs/evidence/ps-038/**`,
  `docs/evidence/ps-037e/**`, `docs/evidence/ps-037d/**`,
  `docs/evidence/ps-037c/**`, `docs/evidence/ps-037b/**`,
  `docs/evidence/ps-037a/**`, `docs/evidence/ps-037/**`,
  `docs/evidence/ps-036/**`, `docs/evidence/ps-035/**`,
  `docs/evidence/ps-031/**`, `docs/evidence/ps-029/**`,
  `docs/evidence/ps-026/**`, `docs/evidence/ps-021/**`,
  `docs/evidence/demo/golden-demo-run.json`,
  `docs/evidence/golden-fixture-digests.json`)
- `scripts/proofstudio_regression_gate.py` (the central gate is not owned by
  PS-038a)
- `scripts/smoke_lib.py` (shared library; PS-038a must not mutate shared
  validation behavior)
- any provider wrapper under `src/proofstudio/providers/**` (PS-038a owns no
  live provider behavior)
- any model client / model wrapper (PS-038a makes no model calls)
- any B2 client / storage write path (PS-038a performs no live B2 read, no B2
  write, and no broad B2 scan)
- any Cloudflare client / live Cloudflare integration path (PS-038a names
  Cloudflare for backbone posture labeling only; no live Cloudflare API call,
  no DNS mutation, no Cloudflare resource creation, no Cloudflare Pages
  deployment, no Cloudflare Workers deployment, no Cloudflare R2 live read,
  and no Cloudflare R2 write is allowed unless a later PM-approved slice
  explicitly enables it with env gates, cost controls, rollback, and evidence
  boundaries)
- any DNS mutation path (PS-038a performs no DNS mutation)
- any deployment config path (PS-038a makes no deployment change)
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
- the PS-038 production readiness + demo mode contract files
  (`apps/web/src/productionReadinessDemoMode.ts`,
  `apps/web/src/ProductionReadinessDemoModeLayer.tsx`) except for additive
  cross-reference; any change that weakens, duplicates, or removes the PS-038
  contract is forbidden

The only implementation-phase files allowed without PM approval are those in
section 8. Any other path requires explicit PM approval.

## 10. Campaign Proof Room Product Contract

PS-038a defines the following contract for the Campaign Proof Room.

### 10.1 Layer identity

- It is a reusable Campaign Proof Room — a judge-facing campaign-level
  command room for one proof-backed campaign — not a new generation pipeline,
  not a new provider/model integration, not a campaign performance proof, not
  a marketing effectiveness proof, not a business outcome guarantee, not a
  semantic truth, not a legal authenticity, not a legal approval, not a human
  authorship, not a C2PA authenticity, not a production readiness claim, not
  a production security claim, not a production compliance claim, not a legal
  compliance claim, not a live deployment, not a DNS change, not a Cloudflare
  resource creation, not a new backend endpoint, and not a new generation
  behavior.
- It is campaign-proof-over-recorded-proof by design: it reads what the
  pipeline already recorded and renders a consistent campaign-level proof
  trail / evidence map / proof timeline / inspection path / judge demo path.
  It is not a generation engine, not a provider integration, not a model
  integration, and not a campaign performance engine.
- It is purely client-side by default: it makes no Cloudflare API call,
  mutates no DNS, creates no Cloudflare resource, deploys no Cloudflare Pages,
  deploys no Cloudflare Workers, performs no Cloudflare R2 live read, performs
  no Cloudflare R2 write, performs no Backblaze B2 write, calls no provider,
  calls no model, reads no B2 object, exposes no arbitrary `run_id` input,
  performs no browser-side B2 byte verification, performs no broad B2 scan,
  writes no B2 object, and changes no deployment / env / render.yaml /
  requirements config.
- It is sourced from accepted local / static / golden / demo data and existing
  accepted data modules only, or from explicit honest "proof available" /
  "proof unavailable" / "not claimed" / "unknown" / "planned" / "deferred" /
  "local verification" / "live verification not available" / "live provider
  evidence not available" / "live B2 evidence not available" / "live
  Cloudflare evidence not available" states.
- It makes the campaign-level proof framing consistent and inspectable. It
  does not invent a new generation pipeline, a new provider/model integration,
  a campaign performance proof, a marketing effectiveness proof, a business
  outcome guarantee, a semantic truth, a legal authenticity, a legal approval,
  a human authorship, a C2PA authenticity, a production readiness claim, a
  production security claim, a production compliance claim, a legal compliance
  claim, a live deployment, a provider availability, a model availability, a
  Backblaze B2 live availability, a Cloudflare availability, an uptime
  guarantee, a cost guarantee, a performance guarantee, a cold-start
  performance guarantee, an Object Lock, a tamper-proof storage, a
  browser-side B2 byte verification, a content moderation correctness, a
  transcript correctness, an emotion truth, a speaker identity, a biometric
  identity, or a model output truth; it states the existing recorded
  campaign-level proof consistently and honestly, and it states honest "proof
  available" / "proof unavailable" / "not claimed" / "unknown" / "planned" /
  "deferred" / "live verification not available" / "live provider evidence
  not available" / "live B2 evidence not available" / "live Cloudflare
  evidence not available" states where no evidence exists.
- The Campaign Proof Room is named as a judge-facing campaign-level evidence /
  navigation / narrative surface over recorded proof only. Naming the Campaign
  Proof Room does not imply a campaign performance proof, a marketing
  effectiveness proof, a business outcome guarantee, a semantic truth, a legal
  authenticity, a legal approval, a human authorship, a C2PA authenticity, a
  production readiness claim, a production security claim, a production
  compliance claim, an uptime guarantee, a cost guarantee, a performance
  guarantee, a cold-start performance guarantee, an Object Lock, a
  tamper-proof storage, a browser-side B2 byte verification, a content
  moderation correctness, a transcript correctness, an emotion truth, a
  speaker identity, a biometric identity, or a model output truth. The
  Campaign Proof Room does not equal campaign performance proof. Campaign
  narrative does not equal marketing effectiveness proof. Campaign
  intelligence evidence does not equal business outcome guarantee. Campaign
  artifact evidence does not equal legal authenticity. Local campaign evidence
  does not equal live provider availability. Checked-in campaign evidence does
  not equal live B2 availability. Cloudflare backbone posture does not equal
  live Cloudflare availability. Demo mode posture does not equal production
  readiness. Review approval evidence does not equal legal approval. Provenance
  passport evidence does not equal C2PA authenticity. Manifest evidence does
  not equal semantic truth. Transcript/timestamp evidence does not equal
  transcript correctness. Voice/audio evidence does not equal speaker
  identity. Proof does not equal truth.
- It integrates with the PS-037 Disclosure + Trust Boundary Layer: it renders
  alongside / links to `TrustBoundaryLayer` and reuses the shared disclosure
  concepts, and must not duplicate or weaken the PS-037 boundary.
- It integrates / cross-references the PS-037a Multimodal Proof Layer: it
  surfaces an honest multimodal artifact evidence cross-reference, and must
  not duplicate or weaken the PS-037a contract.
- It integrates / cross-references the PS-037b Transcript/Timestamp Evidence
  layer: it surfaces an honest transcript/timestamp evidence cross-reference,
  and must not duplicate or weaken the PS-037b contract.
- It integrates / cross-references the PS-037c Voice/Audio Evidence Provider
  Choice layer: it surfaces an honest voice/audio evidence cross-reference,
  and must not duplicate or weaken the PS-037c contract.
- It integrates / cross-references the PS-037d Gemini Campaign Intelligence /
  Judge Narrative layer: it surfaces an honest campaign intelligence evidence
  cross-reference, and must not duplicate or weaken the PS-037d contract.
- It integrates / cross-references the PS-037e Cloudflare Low-Cost Backbone
  layer: it surfaces an honest Cloudflare backbone posture cross-reference,
  and must not duplicate or weaken the PS-037e contract.
- It integrates / cross-references the PS-038 Production Readiness + Demo Mode
  layer: it surfaces an honest production readiness demo mode posture
  cross-reference, and must not duplicate or weaken the PS-038 contract.

### 10.2 Required Campaign Proof Room concepts

The room must surface these canonical Campaign Proof Room concepts, each as a
clearly labeled item:

- `Campaign Proof Room` — the reusable campaign-level command room label.
- `campaign-level proof` — the campaign-level proof framing. Campaign-level
  proof does not equal campaign performance proof.
- `campaign evidence room` — the campaign-level evidence room framing.
- `judge-facing campaign room` — the judge-facing campaign room framing.
- `guided campaign proof trail` — the guided campaign proof trail framing.
- `recorded campaign artifact` — the recorded campaign artifact framing.
- `campaign artifact evidence` — the campaign artifact evidence framing.
  Campaign artifact evidence does not equal legal authenticity.
- `campaign proof summary` — the compact campaign proof summary framing.
- `proof trail` — the proof trail framing. Proof trail does not equal legal
  authenticity.
- `proof timeline` — the proof timeline framing.
- `evidence map` — the evidence map framing.
- `inspection path` — the inspection path framing for the judge.
- `judge demo path` — the judge demo path framing.
- `creator/marketing workflow utility` — the creator/marketing workflow
  utility framing. Creator/marketing workflow utility does not equal business
  outcome guarantee.
- `campaign artifact reference` — the campaign artifact reference (archive URI
  / asset reference when present in accepted data; honest "proof unavailable"
  / "not claimed" state otherwise).
- `campaign artifact digest` — the campaign artifact digest (archive SHA-256 /
  manifest hash when present in accepted data; honest "proof unavailable" /
  "not claimed" state otherwise).
- `campaign manifest evidence` — the campaign manifest evidence
  cross-reference (PS-028). Manifest evidence does not equal semantic truth.
- `campaign archive evidence` — the campaign archive evidence cross-reference
  (B2 archive / PS-036).
- `campaign rehydrate evidence` — the campaign rehydrate evidence
  cross-reference (PS-029 / PS-036).
- `campaign review evidence` — the campaign review evidence cross-reference
  (PS-035).
- `campaign approval evidence` — the campaign approval evidence
  cross-reference (PS-035). Review approval evidence does not equal legal
  approval.
- `export pack evidence` — the export pack evidence cross-reference (PS-031).
- `provenance passport evidence` — the provenance passport evidence
  cross-reference (PS-019 / PS-025). Provenance passport evidence does not
  equal C2PA authenticity.
- `B2 evidence` — the B2 evidence cross-reference (PS-026 / PS-036).
- `Genblaze manifest evidence` — the Genblaze manifest evidence
  cross-reference (PS-027 / PS-028).
- `rehydrate comparison evidence` — the rehydrate comparison evidence
  cross-reference (PS-029).
- `multimodal artifact evidence` — the multimodal artifact evidence
  cross-reference (PS-037a).
- `transcript/timestamp evidence` — the transcript/timestamp evidence
  cross-reference (PS-037b). Transcript/timestamp evidence does not equal
  transcript correctness.
- `voice/audio evidence` — the voice/audio evidence cross-reference
  (PS-037c). Voice/audio evidence does not equal speaker identity.
- `campaign intelligence evidence` — the campaign intelligence evidence
  cross-reference (PS-037d). Campaign intelligence evidence does not equal
  business outcome guarantee.
- `Cloudflare backbone posture` — the Cloudflare backbone posture
  cross-reference (PS-037e). Cloudflare backbone posture does not equal live
  Cloudflare availability.
- `production readiness demo mode posture` — the production readiness demo
  mode posture cross-reference (PS-038).
- `readiness posture` — the readiness posture (cross-referenced from PS-038).
- `demo mode posture` — the demo mode posture (cross-referenced from PS-038).
  Demo mode posture does not equal production readiness.
- `local/static evidence` — whether the campaign evidence is local / static /
  golden / demo fixture evidence (the default posture).
- `checked-in evidence` — whether the campaign evidence is checked-in
  evidence. Checked-in campaign evidence does not equal live B2 availability.
- `local verification` — whether evidence is locally verified against
  checked-in / accepted data.
- `live verification status` — whether a live check is in scope (local /
  check-only by default; live verification not available / live provider
  evidence not available / live B2 evidence not available / live Cloudflare
  evidence not available by default).
- `disclosure boundary` — the campaign disclosure boundary, sourced from /
  consistent with PS-037.
- `proof available` — the honest state that recorded proof is available.
- `proof unavailable` — the honest state that recorded proof is not available.
- `not claimed` — the honest set of things ProofStudio does not claim for the
  campaign.
- `unknown` — what remains unknown or not surfaced for the campaign.
- `planned` — what is planned but not yet live for the campaign.
- `deferred` — what is deferred to a later slice for the campaign.
- `final submission packaging deferred to PS-039` — the honest deferred state
  for final submission packaging.

If a concept does not apply, the room must show an honest "proof unavailable"
/ "not claimed" / "unknown" / "planned" / "deferred" / "live verification not
available" / "live provider evidence not available" / "live B2 evidence not
available" / "live Cloudflare evidence not available" state and must not
fabricate a value.

### 10.3 Required route + navigation

The Campaign Proof Room must be reachable (additively):

- Route `/campaign-proof-room` registered in `apps/web/src/App.tsx` via the
  accepted `isCampaignProofRoomPath()` + `window.location.pathname` convention,
  dispatched in the `App()` function before the passport / review / default
  fallbacks, returning `<CampaignProofRoom variant="page" />`. If the
  implementation chooses a route, this route must be present.
- An additive campaign-room CTA/link from the Judge Cockpit Home
  (`apps/web/src/JudgeCockpitHome.tsx`) and/or the accepted app navigation,
  following the existing `<a className="btn" href="/campaign-proof-room"
  title="...">` convention. If the implementation chooses route navigation,
  this navigation link must be present.
- Optional compact links from proof surfaces back to the campaign room if
  consistent with existing conventions; any such link must be additive and
  must not weaken an existing surface.

### 10.4 Local / live evidence honesty

The room must distinguish clearly between:

- local campaign evidence (the recorded campaign artifact, the proof trail,
  the proof timeline, the evidence map, the inspection path, the judge demo
  path, the campaign artifact reference, the campaign artifact digest, the
  campaign manifest evidence, the campaign archive evidence, the campaign
  rehydrate evidence, the campaign review evidence, the campaign approval
  evidence, the export pack evidence, the provenance passport evidence, the
  B2 evidence, the Genblaze manifest evidence, the rehydrate comparison
  evidence, the multimodal artifact evidence, the transcript/timestamp
  evidence, the voice/audio evidence, the campaign intelligence evidence, the
  Cloudflare backbone posture, the production readiness demo mode posture, the
  readiness posture, and the demo mode posture recorded or reserved in
  accepted checked-in data)
- live evidence (none, by default — PS-038a makes no Cloudflare API call, no
  DNS mutation, no Cloudflare resource creation, no Cloudflare Pages
  deployment, no Cloudflare Workers deployment, no Cloudflare R2 live read, no
  Cloudflare R2 write, no Backblaze B2 write, no provider call, no model call,
  no live B2 read, and no broad B2 scan)
- demo / golden evidence (the golden demo run, which is local / golden, not
  production)

A reviewer reading the room must never mistake a Campaign Proof Room for a
campaign performance proof, a campaign narrative for a marketing effectiveness
proof, a campaign intelligence label for a business outcome guarantee, a proof
trail for legal authenticity, a campaign artifact evidence phrase for human
authorship or C2PA authenticity, local campaign evidence for live provider
availability, checked-in campaign evidence for live B2 availability, a
Cloudflare backbone posture for live Cloudflare availability, a demo mode
posture for production readiness, a review approval record for legal approval,
a provenance passport for C2PA authenticity, manifest evidence for semantic
truth, transcript/timestamp evidence for transcript correctness, or voice/
audio evidence for speaker identity.

### 10.5 Campaign / proof honesty

The room must never fabricate a campaign performance proof, a marketing
effectiveness proof, a business outcome guarantee, a semantic truth, a legal
authenticity, a legal approval, a human authorship, a C2PA authenticity, a
production readiness claim, a production security claim, a production
compliance claim, a legal compliance claim, a live deployment, a provider
availability, a model availability, a Backblaze B2 live availability, a
Cloudflare availability, an uptime guarantee, a cost guarantee, a performance
guarantee, a cold-start performance guarantee, an Object Lock, a tamper-proof
storage, a browser-side B2 byte verification, a content moderation
correctness, a transcript correctness, an emotion truth, a speaker identity, a
biometric identity, or a model output truth. Where no accepted campaign
evidence exists, the room must surface honest "proof unavailable", "not
claimed", "unknown", "planned", "deferred", "live verification not
available", "live provider evidence not available", "live B2 evidence not
available", and "live Cloudflare evidence not available" states. The Campaign
Proof Room label and the campaign-level proof framing must be honestly local /
recorded-only by default. The Campaign Proof Room does not equal campaign
performance proof. Campaign narrative does not equal marketing effectiveness
proof. Campaign intelligence evidence does not equal business outcome
guarantee. Campaign artifact evidence does not equal legal authenticity. Local
campaign evidence does not equal live provider availability. Checked-in
campaign evidence does not equal live B2 availability. Cloudflare backbone
posture does not equal live Cloudflare availability. Demo mode posture does
not equal production readiness. Review approval evidence does not equal legal
approval. Provenance passport evidence does not equal C2PA authenticity.
Manifest evidence does not equal semantic truth. Transcript/timestamp evidence
does not equal transcript correctness. Voice/audio evidence does not equal
speaker identity.

### 10.6 Required unavailable / not-claimed / planned / deferred states (verbatim)

The room must surface, honestly, these unavailable / not-claimed / planned /
deferred / proof-available / proof-unavailable states verbatim. These are
non-claim states: they state what is available, unavailable, not claimed,
planned, deferred, or unknown, and must never be read as a hidden proof:

- recorded proof
- local/static demo evidence
- checked-in campaign evidence
- proof available
- proof unavailable
- not claimed
- unknown
- planned
- deferred
- local verification
- live verification not available
- live provider evidence not available
- live B2 evidence not available
- live Cloudflare evidence not available
- final submission packaging deferred to PS-039

PS-038a must not fake a campaign performance proof, a marketing effectiveness
proof, a business outcome guarantee, a semantic truth, a legal authenticity, a
legal approval, a human authorship, a C2PA authenticity, a production
readiness claim, a production security claim, a production compliance claim, a
legal compliance claim, a live deployment, a provider availability, a model
availability, a Backblaze B2 live availability, a Cloudflare availability, an
uptime guarantee, a cost guarantee, a performance guarantee, a cold-start
performance guarantee, an Object Lock, a tamper-proof storage, a
browser-side B2 byte verification, a content moderation correctness, a
transcript correctness, an emotion truth, a speaker identity, a biometric
identity, or a model output truth. The honest unavailable / not-claimed /
planned / deferred / proof-available / proof-unavailable / unknown states are
the only acceptable representation of those concepts when no accepted evidence
exists.

### 10.7 Required de-escalation pairs (verbatim)

The room must surface these Campaign Proof Room de-escalation pairs verbatim
so a judge never mistakes a strong-sounding Campaign Proof Room, campaign-level
proof, campaign evidence room, judge-facing campaign room, guided campaign
proof trail, campaign narrative, campaign intelligence evidence, campaign
artifact evidence, local campaign evidence, checked-in campaign evidence,
Cloudflare backbone posture, demo mode posture, review approval evidence,
provenance passport evidence, manifest evidence, transcript/timestamp
evidence, or voice/audio evidence for a stronger guarantee:

- proof does not equal truth
- Campaign Proof Room does not equal campaign performance proof
- campaign narrative does not equal marketing effectiveness proof
- campaign intelligence evidence does not equal business outcome guarantee
- campaign artifact evidence does not equal legal authenticity
- local campaign evidence does not equal live provider availability
- checked-in campaign evidence does not equal live B2 availability
- Cloudflare backbone posture does not equal live Cloudflare availability
- demo mode posture does not equal production readiness
- review approval evidence does not equal legal approval
- provenance passport evidence does not equal C2PA authenticity
- manifest evidence does not equal semantic truth
- transcript/timestamp evidence does not equal transcript correctness
- voice/audio evidence does not equal speaker identity

### 10.8 Required negative boundary strings (verbatim)

The room must surface these negative boundary strings verbatim:

- not campaign performance proof
- not marketing effectiveness proof
- not business outcome guarantee
- not semantic truth
- not legal authenticity
- not legal approval
- not human authorship
- not C2PA authenticity
- not production readiness
- not production security
- not production compliance
- not legal compliance
- not live deployment
- not provider availability
- not model availability
- not Backblaze B2 live availability
- not Cloudflare availability
- not uptime guarantee
- not cost guarantee
- not performance guarantee
- not cold-start performance guarantee
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not content moderation correctness
- not transcript correctness
- not emotion truth
- not speaker identity
- not biometric identity
- not model output truth

### 10.9 Boundary honesty

The room must not imply that any Campaign Proof Room, campaign-level proof,
campaign evidence room, judge-facing campaign room, guided campaign proof
trail, recorded campaign artifact, campaign artifact evidence, campaign proof
summary, proof trail, proof timeline, evidence map, inspection path, judge
demo path, creator/marketing workflow utility, campaign artifact reference,
campaign artifact digest, campaign manifest evidence, campaign archive
evidence, campaign rehydrate evidence, campaign review evidence, campaign
approval evidence, export pack evidence, provenance passport evidence, B2
evidence, Genblaze manifest evidence, rehydrate comparison evidence,
multimodal artifact evidence, transcript/timestamp evidence, voice/audio
evidence, campaign intelligence evidence, Cloudflare backbone posture,
production readiness demo mode posture, readiness posture, or demo mode
posture proves anything beyond what the pipeline recorded. In particular it
must not imply that those concepts prove campaign performance, marketing
effectiveness, business outcome, semantic truth, legal authenticity, legal
approval, human authorship, C2PA authenticity, production readiness,
production security, production compliance, legal compliance, live deployment,
provider availability, model availability, Backblaze B2 live availability,
Cloudflare availability, uptime guarantee, cost guarantee, performance
guarantee, cold-start performance guarantee, Object Lock, tamper-proof
storage, browser-side B2 byte verification, content moderation correctness,
transcript correctness, emotion truth, speaker identity, biometric identity,
or model output truth.

## 11. UI/UX Contract

The Campaign Proof Room UI must include:

- A clear title: "Campaign Proof Room" (or an equivalent clear title), with a
  positioning line that ProofStudio proves what the pipeline recorded for the
  campaign-level proof, that this is a navigation / evidence / narrative
  surface over recorded proof, and that the Campaign Proof Room is a
  judge-facing campaign-level command room for one proof-backed campaign
  (Campaign Proof Room does not equal campaign performance proof; campaign
  narrative does not equal marketing effectiveness proof).
- A compact campaign proof summary block that lists, in one compact block, the
  recorded campaign artifact, the campaign artifact reference, the campaign
  artifact digest, the proof available / proof unavailable status, the
  inspection path, the judge demo path, and the honest "proof available" /
  "proof unavailable" / "not claimed" / "unknown" / "planned" / "deferred"
  states, suitable for the top of the room.
- A guided campaign proof trail that walks the judge through the campaign
  artifact, the proof trail, the proof timeline, the evidence map, the
  inspection path, and the judge demo path, in a readable order.
- A proof timeline that orders the recorded proof events for the campaign
  (brief -> provider router -> Genblaze pipeline -> generated asset -> B2
  archive -> rehydrate -> manifest -> passport -> review/approval -> export
  pack), reading only accepted local / static / golden / demo data.
- An evidence map that lists, for the campaign, the campaign manifest
  evidence, the campaign archive evidence, the campaign rehydrate evidence,
  the campaign review evidence, the campaign approval evidence, the export
  pack evidence, the provenance passport evidence, the B2 evidence, the
  Genblaze manifest evidence, the rehydrate comparison evidence, the
  multimodal artifact evidence, the transcript/timestamp evidence, the voice/
  audio evidence, the campaign intelligence evidence, the Cloudflare backbone
  posture, the production readiness demo mode posture, the readiness posture,
  the demo mode posture, the local/static evidence, the checked-in evidence,
  the local verification, and the live verification status, each with an
  honest "proof available" / "proof unavailable" / "not claimed" / "unknown"
  / "planned" / "deferred" / "local verification" / "live verification not
  available" / "live provider evidence not available" / "live B2 evidence not
  available" / "live Cloudflare evidence not available" state.
- An inspection path that lists the links / deep-links into the proof surfaces
  (Judge Cockpit Home, B2 Evidence Explorer, B2 Rehydrate Comparison, Manifest
  Verification Panel, Archive / Rehydrate / B2 Audit Vault, Review + Approval
  Workspace, Judge Evidence Pack / Export Pack, Public Provenance Passport,
  Review Room, and the PS-037 / PS-037a / PS-037b / PS-037c / PS-037d /
  PS-037e / PS-038 layers) so a judge can inspect each piece of evidence.
- A judge demo path that states, in order, the recommended three-minute judge
  demo flow through the campaign room.
- A creator/marketing workflow utility block that states, honestly, how the
  recorded proof creates real-world utility for creator/marketing teams
  without claiming campaign performance, marketing effectiveness, or business
  outcome.
- A cross-reference block that shows: trust boundary cross-reference,
  multimodal proof cross-reference, transcript/timestamp cross-reference,
  voice/audio evidence cross-reference, campaign intelligence cross-reference,
  Cloudflare low-cost backbone cross-reference, and production readiness +
  demo mode cross-reference.
- A "not claimed" section listing, verbatim, what the Campaign Proof Room does
  not prove (section 10.8), the honest unavailable / not-claimed / planned /
  deferred / proof-available / proof-unavailable states (section 10.6).
- The de-escalation pairs (section 10.7), surfaced verbatim.
- The negative boundary strings (section 10.8), surfaced verbatim.
- Integration with the PS-037 Disclosure + Trust Boundary Layer: the Campaign
  Proof Room renders alongside / links to `TrustBoundaryLayer`, reuses the
  shared disclosure concepts, and never contradicts the PS-037 boundary.
- Integration / cross-reference with the PS-037a Multimodal Proof Layer, the
  PS-037b Transcript/Timestamp Evidence layer, the PS-037c Voice/Audio
  Evidence Provider Choice layer, the PS-037d Gemini Campaign Intelligence /
  Judge Narrative layer, the PS-037e Cloudflare Low-Cost Backbone layer, and
  the PS-038 Production Readiness + Demo Mode layer: the Campaign Proof Room
  cross-references them honestly, and never contradicts or weakens their
  contracts.
- A persistent campaign truth-boundary statement that states verbatim (or
  equivalent):

  > ProofStudio proves what the pipeline recorded for the campaign. Proof does
  > not equal truth. The Campaign Proof Room does not equal campaign
  > performance proof. Campaign narrative does not equal marketing
  > effectiveness proof. Campaign intelligence evidence does not equal business
  > outcome guarantee. Campaign artifact evidence does not equal legal
  > authenticity. Local campaign evidence does not equal live provider
  > availability. Checked-in campaign evidence does not equal live B2
  > availability. Cloudflare backbone posture does not equal live Cloudflare
  > availability. Demo mode posture does not equal production readiness.
  > Review approval evidence does not equal legal approval. Provenance passport
  > evidence does not equal C2PA authenticity. Manifest evidence does not equal
  > semantic truth. Transcript/timestamp evidence does not equal transcript
  > correctness. Voice/audio evidence does not equal speaker identity.

UI / UX constraints:

- Must be useful in a three-minute hackathon demo: open the Campaign Proof Room
  -> read the campaign proof summary -> read the recorded campaign artifact ->
  follow the guided campaign proof trail -> read the proof timeline -> read
  the evidence map -> follow the inspection path -> read the judge demo path ->
  read what the campaign room proves -> read what it does not prove -> read
  the unavailable / not-claimed / planned / deferred states -> read the
  de-escalation pairs -> read the negative boundary strings.
- Must render the same campaign-level proof framing on the room and on any
  surface that cross-references the room.
- Must not introduce generic campaign hype copy.
- Must not add unsupported claims.
- Must not fabricate campaign performance proof, marketing effectiveness
  proof, business outcome guarantee, semantic truth, legal authenticity, legal
  approval, human authorship, C2PA authenticity, production readiness,
  production security, production compliance, legal compliance, live
  deployment, provider availability, model availability, Backblaze B2 live
  availability, Cloudflare availability, uptime guarantee, cost guarantee,
  performance guarantee, cold-start performance guarantee, Object Lock,
  tamper-proof storage, browser-side B2 byte verification, content moderation
  correctness, transcript correctness, emotion truth, speaker identity,
  biometric identity, model output truth, or any provider output that is not
  in accepted data.
- Must follow the existing component conventions (`variant`, pills, cards,
  `JsonExpander`, the `.trust-boundary`, `.trust-boundary-layer*`, multimodal
  proof layer, transcript/timestamp evidence layer, voice/audio evidence
  provider choice layer, campaign-intelligence / judge-narrative layer,
  cloudflare-low-cost-backbone layer, and production-readiness-demo-mode layer
  styles) used by the other surfaces.
- Must not delete or weaken any existing per-surface truth-boundary panel,
  per-surface artifact record, the PS-037 disclosure layer, the PS-037a
  multimodal proof layer, the PS-037b transcript/timestamp evidence layer, the
  PS-037c voice/audio evidence provider choice layer, the PS-037d campaign
  intelligence / judge narrative layer, the PS-037e Cloudflare low-cost
  backbone layer, or the PS-038 production readiness + demo mode layer; the
  Campaign Proof Room is additive.

## 12. Data Contract

### 12.1 Source data (read-only inputs)

PS-038a reads accepted local / static / golden / demo data and existing
accepted data modules as immutable inputs. It must not mutate these and must
not change their canonical values. Acceptable read-only sources:

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
- `apps/web/src/productionReadinessDemoMode.ts` (PS-038) — reuse /
  cross-reference the production readiness + demo mode posture; do not
  duplicate, weaken, or remove it
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

Where no accepted campaign evidence exists, PS-038a must surface explicit
honest "proof unavailable" / "not claimed" / "unknown" / "planned" /
"deferred" / "local verification" / "live verification not available" / "live
provider evidence not available" / "live B2 evidence not available" / "live
Cloudflare evidence not available" states and must not fabricate values.
PS-038a must not change the golden run canonical constants. The canonical
constants are owned by their respective accepted slices.

### 12.2 Campaign Proof Room item shape

A Campaign Proof Room item is derived from accepted data and must expose:

- `campaign_proof_room` (the reusable campaign-level command room framing)
- `campaign_level_proof` (the campaign-level proof framing)
- `campaign_evidence_room` (the campaign evidence room framing)
- `judge_facing_campaign_room` (the judge-facing campaign room framing)
- `guided_campaign_proof_trail` (the guided campaign proof trail framing)
- `recorded_campaign_artifact` (the recorded campaign artifact)
- `campaign_artifact_evidence` (the campaign artifact evidence)
- `campaign_proof_summary` (the campaign proof summary)
- `proof_trail` (the proof trail)
- `proof_timeline` (the proof timeline)
- `evidence_map` (the evidence map)
- `inspection_path` (the inspection path)
- `judge_demo_path` (the judge demo path)
- `creator_marketing_workflow_utility` (the creator/marketing workflow utility
  framing)
- `campaign_artifact_reference` (the campaign artifact reference, honest
  about present / unavailable)
- `campaign_artifact_digest` (the campaign artifact digest, honest about
  present / unavailable)
- `campaign_manifest_evidence` (cross-reference; honest indicator)
- `campaign_archive_evidence` (cross-reference; honest indicator)
- `campaign_rehydrate_evidence` (cross-reference; honest indicator)
- `campaign_review_evidence` (cross-reference; honest indicator)
- `campaign_approval_evidence` (cross-reference; honest indicator)
- `export_pack_evidence` (cross-reference; honest indicator)
- `provenance_passport_evidence` (cross-reference; honest indicator)
- `b2_evidence` (cross-reference; honest indicator)
- `genblaze_manifest_evidence` (cross-reference; honest indicator)
- `rehydrate_comparison_evidence` (cross-reference; honest indicator)
- `multimodal_artifact_evidence` (cross-reference; honest indicator)
- `transcript_timestamp_evidence` (cross-reference; honest indicator)
- `voice_audio_evidence` (cross-reference; honest indicator)
- `campaign_intelligence_evidence` (cross-reference; honest indicator)
- `cloudflare_backbone_posture` (cross-reference; honest indicator)
- `production_readiness_demo_mode_posture` (cross-reference; honest indicator)
- `readiness_posture` (cross-reference; honest indicator)
- `demo_mode_posture` (cross-reference; honest indicator)
- `local_static_evidence` (honest indicator; the default posture)
- `checked_in_evidence` (honest indicator; the default posture)
- `local_verification` (locally verified against accepted checked-in data)
- `live_verification_status` (local / check-only by default; live verification
  not available / live provider evidence not available / live B2 evidence not
  available / live Cloudflare evidence not available by default)
- `disclosure_boundary` (sourced from / consistent with PS-037)
- `label` (the human-readable label, matching the verbatim strings in
  section 21)
- `value` (the evidence value, honest about local / recorded-only /
  unavailable / not claimed / planned / deferred / unknown)
- `applicable` (boolean; false when the concept honestly does not apply)
- `state` (one of `recorded`, `locally_verified`, `recorded_only`,
  `not_verified`, `proof_available`, `proof_unavailable`, `not_available`,
  `not_claimed`, `planned`, `deferred`, `unknown`)

### 12.3 Evidence report schema rule

The PS-038a evidence report must follow the harness schema rule: boolean
fields remain booleans and detail / list fields use explicit detail names. A
field whose name implies a boolean success flag must remain a boolean. List
fields must use explicit detail names such as `_ids`, `_details`, or
`_failures` (see section 13).

## 13. Evidence Contract

PS-038a owns exactly one evidence directory: `docs/evidence/ps-038a/`.

- A feature smoke may write only its own evidence, and only when
  `--write-evidence` is explicit. The default PS-038a smoke behavior is
  non-mutating local validation.
- PS-038a must not write any file outside `docs/evidence/ps-038a/`.
- PS-038a must not mutate any prior-slice evidence (every prior evidence prefix
  is guarded by `scripts/smoke_lib.py` and
  `scripts/proofstudio_regression_gate.py`), including the PS-038 evidence
  under `docs/evidence/ps-038/`, the PS-037 evidence under
  `docs/evidence/ps-037/`, the PS-037a evidence under
  `docs/evidence/ps-037a/`, the PS-037b evidence under
  `docs/evidence/ps-037b/`, the PS-037c evidence under
  `docs/evidence/ps-037c/`, the PS-037d evidence under
  `docs/evidence/ps-037d/`, and the PS-037e evidence under
  `docs/evidence/ps-037e/`.
- The PS-038a evidence file is
  `docs/evidence/ps-038a/campaign-proof-room-report.json`.

The PS-038a evidence report must carry these boolean fields (booleans as
booleans; `failures` as a list):

- `ok` (boolean; true only when every measured field is truthful and no
  forbidden overclaim or forbidden file change is present)
- `slice_id`: `ps038a`
- `campaign_proof_room_data_module_present` (boolean; `campaignProofRoom.ts`
  exists)
- `campaign_proof_room_component_present` (boolean; `CampaignProofRoom.tsx`
  exists)
- `campaign_proof_room_route_present` (boolean; `/campaign-proof-room` is
  registered in `App.tsx` if the implementation chooses a route)
- `campaign_proof_room_navigation_present` (boolean; a CTA/link from the
  Judge Cockpit Home or accepted app navigation is present if the
  implementation chooses route navigation)
- `campaign_level_proof_present` (boolean)
- `campaign_evidence_room_present` (boolean)
- `judge_facing_campaign_room_present` (boolean)
- `guided_campaign_proof_trail_present` (boolean)
- `recorded_campaign_artifact_present` (boolean)
- `campaign_artifact_evidence_present` (boolean)
- `campaign_proof_summary_present` (boolean)
- `proof_trail_present` (boolean)
- `proof_timeline_present` (boolean)
- `evidence_map_present` (boolean)
- `inspection_path_present` (boolean)
- `judge_demo_path_present` (boolean)
- `creator_marketing_workflow_utility_present` (boolean)
- `campaign_artifact_reference_present` (boolean)
- `campaign_artifact_digest_present` (boolean)
- `campaign_manifest_evidence_present` (boolean)
- `campaign_archive_evidence_present` (boolean)
- `campaign_rehydrate_evidence_present` (boolean)
- `campaign_review_evidence_present` (boolean)
- `campaign_approval_evidence_present` (boolean)
- `export_pack_evidence_present` (boolean)
- `provenance_passport_evidence_present` (boolean)
- `b2_evidence_present` (boolean)
- `genblaze_manifest_evidence_present` (boolean)
- `rehydrate_comparison_evidence_present` (boolean)
- `multimodal_artifact_evidence_present` (boolean)
- `transcript_timestamp_evidence_present` (boolean)
- `voice_audio_evidence_present` (boolean)
- `campaign_intelligence_evidence_present` (boolean)
- `cloudflare_backbone_posture_present` (boolean)
- `production_readiness_demo_mode_posture_present` (boolean)
- `readiness_posture_present` (boolean)
- `demo_mode_posture_present` (boolean)
- `local_static_evidence_present` (boolean)
- `checked_in_evidence_present` (boolean)
- `local_verification_status_present` (boolean)
- `live_verification_status_present` (boolean)
- `proof_available_status_present` (boolean)
- `proof_unavailable_status_present` (boolean)
- `not_claimed_status_present` (boolean)
- `unknown_status_present` (boolean)
- `planned_status_present` (boolean)
- `deferred_status_present` (boolean)
- `disclosure_boundary_present` (boolean)
- `final_submission_packaging_deferred_to_ps039_present` (boolean)
- `proof_does_not_equal_truth_present` (boolean)
- `campaign_proof_room_does_not_equal_campaign_performance_proof_present`
  (boolean)
- `campaign_narrative_does_not_equal_marketing_effectiveness_proof_present`
  (boolean)
- `campaign_intelligence_evidence_does_not_equal_business_outcome_guarantee_present`
  (boolean)
- `campaign_artifact_evidence_does_not_equal_legal_authenticity_present`
  (boolean)
- `local_campaign_evidence_does_not_equal_live_provider_availability_present`
  (boolean)
- `checked_in_campaign_evidence_does_not_equal_live_b2_availability_present`
  (boolean)
- `cloudflare_backbone_posture_does_not_equal_live_cloudflare_availability_present`
  (boolean)
- `demo_mode_posture_does_not_equal_production_readiness_present` (boolean)
- `review_approval_evidence_does_not_equal_legal_approval_present` (boolean)
- `provenance_passport_evidence_does_not_equal_c2pa_authenticity_present`
  (boolean)
- `manifest_evidence_does_not_equal_semantic_truth_present` (boolean)
- `transcript_timestamp_evidence_does_not_equal_transcript_correctness_present`
  (boolean)
- `voice_audio_evidence_does_not_equal_speaker_identity_present` (boolean)
- `no_campaign_performance_proof_claim` (boolean)
- `no_marketing_effectiveness_proof_claim` (boolean)
- `no_business_outcome_guarantee_claim` (boolean)
- `no_semantic_truth_claim` (boolean)
- `no_legal_authenticity_claim` (boolean)
- `no_legal_approval_claim` (boolean)
- `no_human_authorship_claim` (boolean)
- `no_c2pa_authenticity_claim` (boolean)
- `no_production_readiness_claim` (boolean)
- `no_production_security_claim` (boolean)
- `no_production_compliance_claim` (boolean)
- `no_legal_compliance_claim` (boolean)
- `no_live_deployment_claim` (boolean)
- `no_provider_availability_claim` (boolean)
- `no_model_availability_claim` (boolean)
- `no_backblaze_b2_live_availability_claim` (boolean)
- `no_cloudflare_availability_claim` (boolean)
- `no_uptime_guarantee_claim` (boolean)
- `no_cost_guarantee_claim` (boolean)
- `no_performance_guarantee_claim` (boolean)
- `no_cold_start_performance_guarantee_claim` (boolean)
- `no_object_lock_claim` (boolean)
- `no_tamper_proof_claim` (boolean)
- `no_browser_side_b2_byte_verification_claim` (boolean)
- `no_content_moderation_correctness_claim` (boolean)
- `no_transcript_correctness_claim` (boolean)
- `no_emotion_truth_claim` (boolean)
- `no_speaker_identity_claim` (boolean)
- `no_biometric_identity_claim` (boolean)
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

PS-038a ships one feature smoke:
`scripts/ps038a_campaign_proof_room_smoke.py`.

The PS-038a feature smoke must:

- validate only the PS-038a slice (no recursive smokes; must never launch
  another feature smoke as a subprocess; must never call the central
  regression gate)
- read checked-in prior evidence and accepted data modules as immutable inputs
- write only its own evidence file
  `docs/evidence/ps-038a/campaign-proof-room-report.json`, and only
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
- validate the `campaignProofRoom.ts` data module is present
- validate the `CampaignProofRoom.tsx` component is present
- validate route `/campaign-proof-room` is present if the implementation
  chooses a route
- validate a CTA/link from the Judge Cockpit Home or accepted app navigation
  is present if the implementation chooses route navigation
- validate the required proof / demo / readiness surfaces preserve existing
  layers (PS-037 / PS-037a / PS-037b / PS-037c / PS-037d / PS-037e / PS-038)
- validate the room integrates / cross-references the PS-037 Trust Boundary
- validate the room integrates / cross-references the PS-037a Multimodal Proof
  Layer
- validate the room integrates / cross-references the PS-037b Transcript/
  Timestamp Evidence layer
- validate the room integrates / cross-references the PS-037c Voice/Audio
  Evidence Provider Choice layer
- validate the room integrates / cross-references the PS-037d Gemini Campaign
  Intelligence / Judge Narrative layer
- validate the room integrates / cross-references the PS-037e Cloudflare
  Low-Cost Backbone layer
- validate the room integrates / cross-references the PS-038 Production
  Readiness + Demo Mode layer
- validate the required Campaign Proof Room UI strings (section 21) are present
- validate the required negative boundary strings (section 21) are present
- validate the unavailable / not-claimed / planned / deferred / proof-available
  / proof-unavailable states (section 10.6) are present and honest
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
  the PS-038a changed files, without the smoke or this spec reproducing that
  literal
- validate prior evidence is unchanged
- validate `git diff --check` is clean
- do not scan smoke guard fixtures as product claims (the future PS-038a smoke
  and its evidence report are the source of truth for slice overclaim
  validation; smoke guard fixtures are not product claims)

The PS-038a feature smoke must support these standard flags:

- `--check-only` (default: non-mutating local validation; no evidence file is
  written)
- `--write-evidence` (write only `docs/evidence/ps-038a/` evidence)
- `--no-frontend`

Default PS-038a smoke behavior is non-mutating local validation
(`--check-only`).

The smoke must not contain the bad lowercase-only hidden-flag marker check
and must not rely on a lowercase-only marker check. The hidden-Git-flags check
must be the explicit `h` / `S` checker over `git ls-files -v`, and must record
`no_hidden_git_flags_h` and `no_hidden_git_flags_S` as separate booleans.

PS-038a smoke performs no Cloudflare API calls, no DNS mutation, no Cloudflare
resource creation, no Cloudflare Pages deployment, no Cloudflare Workers
deployment, no Cloudflare R2 live reads, no Cloudflare R2 writes, no Backblaze
B2 writes, no provider calls, no model calls, no live B2 reads, no B2 writes,
no broad B2 scans, no deployment changes, no env/secrets changes, no
render.yaml changes, and no requirements/dependency changes.

The PS-038a smoke must not create duplicate context-blind overclaim scanners.
The smoke and its evidence report are the source of truth for PS-038a
overclaim validation. The smoke must not scan smoke guard fixtures as product
claims.

## 15. Regression Gate Contract

The central regression gate remains the single cross-slice release-readiness
gate and is non-mutating by default. PS-038a does not own or modify the
central gate.

Normal future PS-038a release validation command:

```
python scripts/proofstudio_regression_gate.py --current ps038a --frontend --report-out /tmp/proofstudio-release-report.json
```

Contract-only gate (no frontend):

```
python scripts/proofstudio_regression_gate.py --current ps038a --no-frontend --report-out /tmp/proofstudio-ps038a-regression-report.json
```

- The gate runs `npm run typecheck` and `npm run build` in `apps/web` exactly
  once per invocation, and only when `--frontend` is passed. PS-038a feature
  smoke must never trigger nested frontend builds.
- The gate must not write the canonical PS-034A report. `--write-report` is
  rejected for `--current ps038a` (PS-035C accepted behavior; only PS-034A may
  regenerate the canonical report).
- Running the gate for `ps038a` must leave all prior-slice evidence unchanged,
  including the PS-038, PS-037, PS-037a, PS-037b, PS-037c, PS-037d, and
  PS-037e evidence.
- No recursive smokes: the gate never executes a feature smoke.

Canonical PS-034A regeneration (unchanged, owned by PS-034A only):

```
python scripts/proofstudio_regression_gate.py --current ps034a --write-report
```

## 16. Truth Boundary

ProofStudio proves what the pipeline recorded. The Campaign Proof Room is a
campaign-proof-over-recorded-proof surface that makes the recorded campaign
artifact, the proof trail, the proof timeline, the evidence map, the
inspection path, and the judge demo path explicit and consistent for one
proof-backed campaign. It is not a new generation pipeline, not a new
provider/model integration, not a campaign performance proof, not a marketing
effectiveness proof, not a business outcome guarantee, not a semantic truth,
not a legal authenticity, not a legal approval, not a human authorship, not a
C2PA authenticity, not a production readiness claim, not a production security
claim, not a production compliance claim, not a legal compliance claim, not a
live deployment, not a DNS change system, not a Cloudflare resource creator,
not a Cloudflare Pages deployment system, not a Cloudflare Workers deployment
system, not a Cloudflare R2 live reader, not a Cloudflare R2 writer, not a
Backblaze B2 writer, not a live B2 verifier, not a truth system, not a
semantic-truth system, not a model-output-truth system, not a content
moderation correctness system, not a transcript correctness system, not an
emotion truth system, not a speaker identity system, not a biometric identity
system, and not an identity / authenticity system.

The room must preserve these truth-boundary red lines verbatim across the
spec, the UI, and any evidence report:

- do not claim campaign performance proof
- do not claim marketing effectiveness proof
- do not claim business outcome guarantee
- do not claim semantic truth
- do not claim legal authenticity
- do not claim legal approval
- do not claim human authorship
- do not claim C2PA unless implemented and verified
- do not claim production readiness
- do not claim production security
- do not claim production compliance
- do not claim legal compliance
- do not claim live deployment
- do not claim production deployment
- do not claim provider availability
- do not claim model availability
- do not claim Backblaze B2 live availability
- do not claim Cloudflare availability
- do not claim Cloudflare deployment
- do not claim Cloudflare resource existence
- do not claim Cloudflare Pages availability
- do not claim Cloudflare Workers availability
- do not claim Cloudflare R2 availability
- do not claim uptime guarantee
- do not claim cost guarantee
- do not claim performance guarantee
- do not claim cold-start performance guarantee
- do not claim DNS ownership
- do not claim Object Lock / tamper-proof storage unless implemented and
  verified
- do not claim browser-side B2 byte verification unless implemented and
  verified
- do not claim live B2 availability unless a live B2 check is explicitly
  implemented and approved
- do not claim content moderation correctness
- do not claim transcript correctness
- do not claim emotion truth
- do not claim speaker identity
- do not claim biometric identity
- do not claim model output truth
- do not claim public deployment verification unless deployed and tested
- do not claim enterprise security
- do not claim actual spend / latency / quota unless captured
- do not claim provider failures / reruns / variants unless evidenced

PS-038a does not prove campaign performance, marketing effectiveness,
business outcome, semantic truth, legal authenticity, legal approval, human
authorship, C2PA authenticity, production readiness, production security,
production compliance, legal compliance, live deployment, production
deployment, provider availability, model availability, Backblaze B2 live
availability, Cloudflare availability, Cloudflare deployment, Cloudflare
resource existence, Cloudflare Pages availability, Cloudflare Workers
availability, Cloudflare R2 availability, uptime guarantee, cost guarantee,
performance guarantee, cold-start performance guarantee, DNS ownership, B2
immutability, Object Lock, tamper-proof storage, browser-side B2 byte
verification, live B2 availability, content moderation correctness,
transcript correctness, emotion truth, speaker identity, biometric identity,
or model output truth. No PS-038a artifact may imply any of these. The
Campaign Proof Room states what the pipeline already recorded; it does not
deploy ProofStudio, it does not run a generation pipeline, it does not mutate
DNS, it does not create Cloudflare resources, it does not call Cloudflare, it
does not call any provider, it does not call any model, it does not read live
B2, it does not write B2, it does not perform broad B2 scans, and it does not
change deployment / env / render.yaml / requirements config.

## 17. Later-slice Boundaries

PS-038a must not implement, fake, or claim the later slices or out-of-scope
capabilities. The boundaries are:

- final submission packaging — out of scope for PS-038a. PS-038a must only
  reserve an honest "final submission packaging deferred to PS-039" state.
- new generation pipeline / new provider-model integration — out of scope for
  PS-038a. PS-038a assembles existing recorded proof; it does not generate,
  rerun, or integrate a new provider/model.
- campaign performance measurement — out of scope for PS-038a. PS-038a must
  only reserve an honest "not claimed" / "unknown" state. The Campaign Proof
  Room does not equal campaign performance proof.
- marketing effectiveness measurement — out of scope for PS-038a. PS-038a
  must only reserve an honest "not claimed" / "unknown" state. Campaign
  narrative does not equal marketing effectiveness proof.
- business outcome guarantee — out of scope for PS-038a. PS-038a must only
  reserve an honest "not claimed" / "unknown" state. Campaign intelligence
  evidence does not equal business outcome guarantee. Creator/marketing
  workflow utility does not equal business outcome guarantee.
- live production deployment — out of scope for PS-038a. PS-038a must only
  reserve an honest "live deployment not available" / "not claimed" state.
- DNS mutation — out of scope for PS-038a. PS-038a must only reserve an honest
  "not claimed" / "unknown" state.
- Cloudflare resource creation / Pages deployment / Workers deployment / R2
  live reads / R2 writes — out of scope for PS-038a. PS-038a must only reserve
  an honest "live Cloudflare evidence not available" state. The Cloudflare
  backbone posture does not equal live Cloudflare availability.
- Backblaze B2 writes / live B2 reads / broad B2 scans — out of scope for
  PS-038a. Backblaze B2 remains the durable proof/archive system of record.
  Checked-in campaign evidence does not equal live B2 availability.
- production readiness / production security / production compliance / legal
  compliance — out of scope for PS-038a. PS-038a must only reserve honest
  "not claimed" / "unknown" states. Demo mode posture does not equal
  production readiness.
- uptime guarantee / cost guarantee / performance guarantee / cold-start
  performance guarantee — out of scope for PS-038a. PS-038a must not claim
  them.
- semantic truth verification — out of scope for PS-038a. PS-038a must not
  claim it. Manifest evidence does not equal semantic truth.
- legal authenticity / legal approval — out of scope for PS-038a. PS-038a must
  not claim them. Campaign artifact evidence does not equal legal
  authenticity. Review approval evidence does not equal legal approval.
- human authorship — out of scope for PS-038a. PS-038a must not claim it.
- C2PA authenticity — out of scope for PS-038a. PS-038a must not claim it.
  Provenance passport evidence does not equal C2PA authenticity.
- Object Lock / tamper-proof storage / browser-side B2 byte verification — out
  of scope. PS-038a must only reserve honest "not claimed" states for these.
- content moderation correctness / transcript correctness — out of scope.
  PS-038a must not claim them. Transcript/timestamp evidence does not equal
  transcript correctness.
- emotion truth / speaker identity / biometric identity — out of scope.
  PS-038a must not claim them. Voice/audio evidence does not equal speaker
  identity.
- model output truth — out of scope. PS-038a must not claim it.

PS-038a may reserve fields and honest "proof available" / "proof unavailable"
/ "not claimed" / "unknown" / "planned" / "deferred" / "local verification" /
"live verification not available" / "live provider evidence not available" /
"live B2 evidence not available" / "live Cloudflare evidence not available"
states for those later-slice / out-of-scope areas, but must not fake campaign
performance proofs, marketing effectiveness proofs, business outcome
guarantees, live deployments, production deployments, production readiness,
production security, production compliance, legal compliance, legal
authenticity, legal approval, human authorship, C2PA authenticity, semantic
truth, uptime guarantees, cost guarantees, performance guarantees, cold-start
performance guarantees, Cloudflare deployments, Cloudflare availability,
Backblaze B2 live availability, provider availability, model availability,
Object Lock, tamper-proof storage, browser-side B2 byte verification, content
moderation correctness, transcript correctness, emotion truth, speaker
identity, biometric identity, model output truth, or any provider output.

## 18. Risks

PS-038a must record the following risks with mitigations:

- overclaim risk
  - risk: a reviewer misreads the Campaign Proof Room or its copy as a
    forbidden overclaim — i.e. as claiming campaign performance proof,
    marketing effectiveness proof, business outcome guarantee, semantic truth,
    legal authenticity, legal approval, human authorship, C2PA authenticity,
    production readiness, production security, production compliance, legal
    compliance, live deployment, provider availability, model availability,
    Backblaze B2 live availability, Cloudflare availability, uptime guarantee,
    cost guarantee, performance guarantee, cold-start performance guarantee,
    Object Lock, tamper-proof storage, browser-side B2 byte verification,
    content moderation correctness, transcript correctness, emotion truth,
    speaker identity, biometric identity, or model output truth. ProofStudio
    does not claim any of these.
  - mitigation: the persistent campaign truth-boundary statement (section 11)
    is mandatory; the truth-boundary red lines (section 16) are preserved
    verbatim; the de-escalation pairs (section 10.7) and negative boundary
    strings (section 10.8) are surfaced verbatim; the evidence report carries
    `no_forbidden_overclaims`.
- campaign-word overclaim risk
  - risk: a "Campaign Proof Room", "campaign-level proof", "campaign evidence
    room", "judge-facing campaign room", "guided campaign proof trail",
    "campaign narrative", "campaign intelligence", "proof trail", or "campaign
    artifact evidence" word is misread as a campaign performance proof, a
    marketing effectiveness proof, a business outcome guarantee, a legal
    authenticity, a legal approval, a human authorship, a C2PA authenticity, a
    production readiness claim, a cost guarantee, an uptime guarantee, a
    performance guarantee, or a cold-start performance guarantee.
  - mitigation: the de-escalation pairs in section 10.7 are surfaced verbatim
    (Campaign Proof Room does not equal campaign performance proof; campaign
    narrative does not equal marketing effectiveness proof; campaign
    intelligence evidence does not equal business outcome guarantee; campaign
    artifact evidence does not equal legal authenticity; local campaign
    evidence does not equal live provider availability; checked-in campaign
    evidence does not equal live B2 availability; Cloudflare backbone posture
    does not equal live Cloudflare availability; demo mode posture does not
    equal production readiness; review approval evidence does not equal legal
    approval; provenance passport evidence does not equal C2PA authenticity;
    manifest evidence does not equal semantic truth; transcript/timestamp
    evidence does not equal transcript correctness; voice/audio evidence does
    not equal speaker identity); the negative boundary strings in section 10.8
    are surfaced verbatim.
- faking-campaign-proof / faking-evidence risk
  - risk: a campaign performance proof, a marketing effectiveness proof, a
    business outcome guarantee, a campaign artifact digest, a campaign
    artifact reference, a campaign intelligence output, a transcript, a
    voice/audio identity, a Cloudflare availability, a Backblaze B2 live
    availability, a provider availability, or a model availability is silently
    represented as present when it is not, or is silently omitted so it looks
    hidden.
  - mitigation: the unavailable / not-claimed / planned / deferred /
    proof-available / proof-unavailable states (section 10.6) are surfaced
    verbatim and honestly; the campaign / proof honesty (section 10.5) is
    mandatory; the smoke validates their presence; PS-038a never produces
    those outputs unless they exist in accepted data.
- de-escalation-gap risk
  - risk: a judge mistakes a Campaign Proof Room for a campaign performance
    proof, a campaign narrative for a marketing effectiveness proof, a
    campaign intelligence label for a business outcome guarantee, a proof
    trail for legal authenticity, a campaign artifact evidence phrase for
    human authorship or C2PA authenticity, local campaign evidence for live
    provider availability, checked-in campaign evidence for live B2
    availability, a Cloudflare backbone posture for live Cloudflare
    availability, a demo mode posture for production readiness, a review
    approval record for legal approval, a provenance passport for C2PA
    authenticity, manifest evidence for semantic truth, transcript/timestamp
    evidence for transcript correctness, or voice/audio evidence for speaker
    identity.
  - mitigation: the de-escalation pairs in section 10.7 are surfaced verbatim.
- PS-037 / PS-037a / PS-037b / PS-037c / PS-037d / PS-037e / PS-038 weakening
  risk
  - risk: the Campaign Proof Room duplicates, contradicts, weakens, or removes
    the PS-037 Disclosure + Trust Boundary Layer, the PS-037a Multimodal Proof
    Layer, the PS-037b Transcript/Timestamp Evidence layer, the PS-037c
    Voice/Audio Evidence Provider Choice layer, the PS-037d Gemini Campaign
    Intelligence / Judge Narrative layer, the PS-037e Cloudflare Low-Cost
    Backbone layer, or the PS-038 Production Readiness + Demo Mode layer.
  - mitigation: the Campaign Proof Room renders alongside / links to
    `TrustBoundaryLayer`, `MultimodalProofLayer`,
    `TranscriptTimestampEvidenceLayer`, `VoiceAudioEvidenceChoiceLayer`,
    `CampaignIntelligenceJudgeNarrativeLayer`,
    `CloudflareLowCostBackboneLayer`, and
    `ProductionReadinessDemoModeLayer`, reuses the shared disclosure concepts,
    cross-references PS-037a, PS-037b, PS-037c, PS-037d, PS-037e, and PS-038,
    and never contradicts the PS-037 boundary or removes the PS-037a /
    PS-037b / PS-037c / PS-037d / PS-037e / PS-038 contracts; PS-038a does not
    edit the PS-037, PS-037a, PS-037b, PS-037c, PS-037d, PS-037e, or PS-038
    contract files except additively (section 9).
- deployment-config / env / render.yaml / requirements drift risk
  - risk: the room or its smoke silently changes deployment config, `.env*`,
    `render.yaml`, or requirements, which would break the campaign-room-as-
    local-static posture and the truth boundary.
  - mitigation: PS-038a makes no deployment changes, no env/secrets changes,
    no render.yaml changes, and no requirements/dependency changes; the smoke
    enforces `no_deployment_changes`, `no_env_secrets_changes`,
    `no_render_yaml_changes`, and `no_requirements_dependency_changes`.
- live-B2-read / DNS-mutation / provider-call / model-call / Cloudflare risk
  - risk: the room triggers a live B2 read, a broad B2 scan, a Cloudflare API
    call, a DNS mutation, a Cloudflare resource creation, a Cloudflare Pages
    deployment, a Cloudflare Workers deployment, a Cloudflare R2 live read, a
    Cloudflare R2 write, a Backblaze B2 write, a provider call, or a model
    call.
  - mitigation: the room is purely client-side over accepted data; the smoke
    enforces `no_cloudflare_api_calls`, `no_dns_mutation`,
    `no_cloudflare_resource_creation`, `no_cloudflare_pages_deployment`,
    `no_cloudflare_workers_deployment`, `no_cloudflare_r2_live_reads`,
    `no_cloudflare_r2_writes`, `no_backblaze_b2_writes`, `no_provider_calls`,
    `no_model_calls`, `no_live_b2_reads`, `no_b2_writes`,
    `no_broad_b2_scans`.
- evidence-mutation risk
  - risk: the PS-038a smoke or the central gate run overwrites prior-slice
    evidence, including PS-038, PS-037, PS-037a, PS-037b, PS-037c, PS-037d,
    and PS-037e evidence.
  - mitigation: PS-038a writes only `docs/evidence/ps-038a/`; the gate is
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
  - risk: PS-038a expands into a new generation pipeline, a new provider/model
    integration, live production deployment, DNS mutation, Cloudflare resource
    creation, Cloudflare Pages deployment, Cloudflare Workers deployment,
    Cloudflare R2 live reads, Cloudflare R2 writes, Backblaze B2 writes,
    provider calls, model calls, live B2 reads, B2 writes, broad B2 scans,
    campaign performance measurement, marketing effectiveness measurement,
    business outcome guarantee, production readiness, production security,
    production compliance, legal compliance, uptime guarantee, cost guarantee,
    performance guarantee, cold-start performance guarantee, Object Lock,
    tamper-proof storage, browser-side B2 byte verification, content
    moderation correctness, transcript correctness, emotion truth, speaker
    identity, biometric identity, model output truth, CI, billing, deployment,
    auth, teams, permissions, a full enterprise DAM, a new backend, or a live
    B2 fetcher.
  - mitigation: section 7 lists these as non-goals; section 9 forbids the
    relevant paths; section 17 fixes the later-slice / out-of-scope
    boundaries.
- recursive-smoke risk
  - risk: the PS-038a smoke launches another feature smoke or calls the
    central gate.
  - mitigation: the smoke must never launch another feature smoke as a
    subprocess and must never call the central regression gate; the central
    gate is the only cross-slice validator.
- duplicate-scanner risk
  - risk: PS-038a adds duplicate context-blind overclaim scanners in chat/spec
    guidance that treat smoke guard fixtures as product claims.
  - mitigation: PS-038a does not create duplicate context-blind overclaim
    scanners; the PS-038a smoke and its evidence report are the source of
    truth for slice overclaim validation; smoke guard fixtures are not scanned
    as product claims.

## 19. Acceptance Criteria

PS-038a (spec-only phase) is accepted only when:

- this spec exists at
  `specs/61-ps-038a-campaign-proof-room.md`
- only this spec file is changed in the spec-only phase
- the branch `ps-038a/campaign-proof-room` starts from
  `origin/accepted/proofstudio` at commit
  `de428e51c855b2de3c5a0ef6ce3421360058bbd8` (the merge-base equals that
  commit)
- the product scope is clear and owns presentation, routing, campaign-level
  aggregation, judge guidance, proof navigation, and evidence narrative only;
  it does not expand into a new generation pipeline, a new provider/model
  integration, live production deployment, DNS mutation, Cloudflare resource
  creation, Cloudflare Pages deployment, Cloudflare Workers deployment,
  Cloudflare R2 live reads, Cloudflare R2 writes, Backblaze B2 writes,
  provider calls, model calls, live B2 reads, B2 writes, broad B2 scans,
  campaign performance measurement, marketing effectiveness measurement,
  business outcome guarantee, production readiness, production security,
  production compliance, legal compliance, uptime guarantee, cost guarantee,
  performance guarantee, cold-start performance guarantee, DNS ownership,
  Cloudflare resource existence, Cloudflare Pages availability, Cloudflare
  Workers availability, Cloudflare R2 availability, Cloudflare availability,
  Backblaze B2 live availability, provider availability, model availability,
  Object Lock, tamper-proof storage, browser-side B2 byte verification,
  semantic truth, legal authenticity, legal approval, human authorship, C2PA
  authenticity, content moderation correctness, transcript correctness,
  emotion truth, speaker identity, biometric identity, or model output truth
- the required Campaign Proof Room concepts (section 10.2), the route +
  navigation (section 10.3) are specified
- the unavailable / not-claimed / planned / deferred / proof-available /
  proof-unavailable states (section 10.6), the de-escalation pairs
  (section 10.7), and the negative boundary strings (section 10.8) are
  specified verbatim
- the UI / UX contract (section 11) and the persistent campaign truth-boundary
  statement are specified
- the data contract (section 12) reuses accepted checked-in evidence as
  read-only inputs and surfaces honest unavailable / not-claimed / planned /
  deferred / proof-available / proof-unavailable / unknown states where no
  evidence exists
- the truth boundary (section 16) is explicit and the boundary copy is
  specified
- the later-slice boundaries (section 17) are fixed
- the implementation candidate files (section 8) are listed, but no
  implementation is done in this phase
- the validation plan uses the PS-038a feature smoke plus the central
  regression gate (sections 14 and 15)
- no evidence mutation occurs in this phase
- no hidden Git flags `h` or `S` are present (verified by the explicit h/S
  checker over `git ls-files -v`)
- `git diff --check` is clean
- no staging, commit, or push occurs until PM approval
- `AGENTS.md`, `specs/07-master-spec-plan.md`, and
  `specs/08-roadmap-slices.md` are not changed in this phase

Implementation-phase acceptance (for reference, not this phase) additionally
requires: the shared `CampaignProofRoom.tsx` component +
`campaignProofRoom.ts` data module exist; the Campaign Proof Room route
`/campaign-proof-room` is registered in `App.tsx` if the implementation
chooses a route; a campaign-room CTA/link from the Judge Cockpit Home or
accepted app navigation is present if the implementation chooses route
navigation; the room integrates / cross-references the PS-037a Multimodal
Proof Layer, the PS-037b Transcript/Timestamp Evidence layer, the PS-037c
Voice/Audio Evidence Provider Choice layer, the PS-037d Gemini Campaign
Intelligence / Judge Narrative layer, the PS-037e Cloudflare Low-Cost Backbone
layer, and the PS-038 Production Readiness + Demo Mode layer and preserves the
PS-037 TrustBoundaryLayer; the required Campaign Proof Room concepts,
unavailable / not-claimed / planned / deferred / proof-available /
proof-unavailable states, de-escalation pairs, and negative boundary strings
are present; the PS-038a smoke passes in `--check-only` (default) and writes
only `docs/evidence/ps-038a/**` under `--write-evidence`; the central gate
passes for `--current ps038a`; no deployment change, no env/secrets change, no
render.yaml change, no requirements/dependency change, no Cloudflare API
call, no DNS mutation, no Cloudflare resource creation, no Cloudflare Pages
deployment, no Cloudflare Workers deployment, no Cloudflare R2 live read, no
Cloudflare R2 write, no Backblaze B2 write, no provider call, no model call,
no live B2 read, no B2 write, no broad B2 scan occurs; prior evidence is
unchanged, including PS-038, PS-037, PS-037a, PS-037b, PS-037c, PS-037d, and
PS-037e evidence; no forbidden overclaim is introduced; the PS-037 disclosure
boundary, the PS-037a multimodal proof contract, the PS-037b transcript/
timestamp contract, the PS-037c voice/audio evidence provider choice contract,
the PS-037d campaign intelligence / judge narrative contract, the PS-037e
Cloudflare low-cost backbone contract, and the PS-038 production readiness +
demo mode contract are not weakened.

## 20. Rollback

Rollback of the PS-038a spec-only phase is a single revert of this spec
commit, because only `specs/61-ps-038a-campaign-proof-room.md` is changed in
this phase.

Future implementation rollback must restore the pre-PS-038a state of the
edited files in section 8. Specifically:

- remove `apps/web/src/campaignProofRoom.ts`
- remove `apps/web/src/CampaignProofRoom.tsx`
- revert the additive `isCampaignProofRoomPath()` helper and dispatch line in
  `apps/web/src/App.tsx` to pre-PS-038a state
- revert the additive campaign-room CTA/link in
  `apps/web/src/JudgeCockpitHome.tsx` to pre-PS-038a state
- revert any additive compact links from proof surfaces back to the campaign
  room to pre-PS-038a state
- revert the additive campaign-proof-room classes in
  `apps/web/src/styles.css` to pre-PS-038a state
- remove `scripts/ps038a_campaign_proof_room_smoke.py`
- remove `docs/ps-038a-campaign-proof-room-proof.md`
- remove `docs/evidence/ps-038a/` if it was added
- revert the additive cross-references in `specs/07-master-spec-plan.md`,
  `specs/08-roadmap-slices.md`, and
  `docs/validation/proofstudio-smoke-harness-v1.md` to pre-PS-038a state

Rollback of PS-038a must not touch any evidence under `docs/evidence/**` other
than `docs/evidence/ps-038a/`, must not touch the central gate
(`scripts/proofstudio_regression_gate.py`), `scripts/smoke_lib.py`,
`AGENTS.md`, `.env*`, `render.yaml`, requirements files, any provider wrapper,
any model client, any Cloudflare client, any B2 storage path, any DNS mutation
path, any deployment config path, the PS-037 disclosure contract, the PS-037a
multimodal proof contract, the PS-037b transcript/timestamp contract, the
PS-037c voice/audio evidence provider choice contract, the PS-037d campaign
intelligence / judge narrative contract, the PS-037e Cloudflare low-cost
backbone contract, or the PS-038 production readiness + demo mode contract.
Rollback is isolated and reversible because PS-038a is a self-contained
Campaign Proof Room over existing accepted data; it does not change provider
behavior, model behavior, generation behavior, Cloudflare behavior, DNS
behavior, B2 behavior, billing behavior, deployment topology, the PS-037
boundary, the PS-037a contract, the PS-037b contract, the PS-037c contract,
the PS-037d contract, the PS-037e contract, or the PS-038 contract.

## 21. Verbatim implementation/audit contract strings

The PS-038a implementation, the Campaign Proof Room UI, the PS-038a smoke,
and the PS-038a evidence report must preserve the following exact strings so
the Campaign Proof Room contract is deterministic and auditable. Any future PM
audit must check these exact strings; do not rely on close-enough wording. No
surprise audit checks: any exact string a future PM audit should check is
listed here.

The required identity / positioning strings are:

- PS-038a
- Campaign Proof Room

The required concept strings are:

- campaign-level proof
- campaign evidence room
- judge-facing campaign room
- guided campaign proof trail
- recorded campaign artifact
- campaign artifact evidence
- campaign proof summary
- proof trail
- proof timeline
- evidence map
- inspection path
- judge demo path
- creator/marketing workflow utility
- campaign artifact reference
- campaign artifact digest
- campaign manifest evidence
- campaign archive evidence
- campaign rehydrate evidence
- campaign review evidence
- campaign approval evidence
- export pack evidence
- provenance passport evidence
- B2 evidence
- Genblaze manifest evidence
- rehydrate comparison evidence
- multimodal artifact evidence
- transcript/timestamp evidence
- voice/audio evidence
- campaign intelligence evidence
- Cloudflare backbone posture
- production readiness demo mode posture
- readiness posture
- demo mode posture
- local/static evidence
- checked-in evidence
- local verification
- live verification status
- disclosure boundary

The required honest status / state strings are:

- recorded proof
- local/static demo evidence
- checked-in campaign evidence
- proof available
- proof unavailable
- not claimed
- unknown
- planned
- deferred
- final submission packaging deferred to PS-039

The required de-escalation-pair strings are:

- proof does not equal truth
- Campaign Proof Room does not equal campaign performance proof
- campaign narrative does not equal marketing effectiveness proof
- campaign intelligence evidence does not equal business outcome guarantee
- campaign artifact evidence does not equal legal authenticity
- local campaign evidence does not equal live provider availability
- checked-in campaign evidence does not equal live B2 availability
- Cloudflare backbone posture does not equal live Cloudflare availability
- demo mode posture does not equal production readiness
- review approval evidence does not equal legal approval
- provenance passport evidence does not equal C2PA authenticity
- manifest evidence does not equal semantic truth
- transcript/timestamp evidence does not equal transcript correctness
- voice/audio evidence does not equal speaker identity

The required negative-boundary strings are:

- not campaign performance proof
- not marketing effectiveness proof
- not business outcome guarantee
- not semantic truth
- not legal authenticity
- not legal approval
- not human authorship
- not C2PA authenticity
- not production readiness
- not production security
- not production compliance
- not legal compliance
- not live deployment
- not provider availability
- not model availability
- not Backblaze B2 live availability
- not Cloudflare availability
- not uptime guarantee
- not cost guarantee
- not performance guarantee
- not cold-start performance guarantee
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not content moderation correctness
- not transcript correctness
- not emotion truth
- not speaker identity
- not biometric identity
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
- `slice_id: ps038a`
- `campaign_proof_room_data_module_present`
- `campaign_proof_room_component_present`
- `campaign_proof_room_route_present`
- `campaign_proof_room_navigation_present`
- `campaign_level_proof_present`
- `campaign_evidence_room_present`
- `judge_facing_campaign_room_present`
- `guided_campaign_proof_trail_present`
- `recorded_campaign_artifact_present`
- `campaign_artifact_evidence_present`
- `campaign_proof_summary_present`
- `proof_trail_present`
- `proof_timeline_present`
- `evidence_map_present`
- `inspection_path_present`
- `judge_demo_path_present`
- `creator_marketing_workflow_utility_present`
- `campaign_artifact_reference_present`
- `campaign_artifact_digest_present`
- `campaign_manifest_evidence_present`
- `campaign_archive_evidence_present`
- `campaign_rehydrate_evidence_present`
- `campaign_review_evidence_present`
- `campaign_approval_evidence_present`
- `export_pack_evidence_present`
- `provenance_passport_evidence_present`
- `b2_evidence_present`
- `genblaze_manifest_evidence_present`
- `rehydrate_comparison_evidence_present`
- `multimodal_artifact_evidence_present`
- `transcript_timestamp_evidence_present`
- `voice_audio_evidence_present`
- `campaign_intelligence_evidence_present`
- `cloudflare_backbone_posture_present`
- `production_readiness_demo_mode_posture_present`
- `readiness_posture_present`
- `demo_mode_posture_present`
- `local_static_evidence_present`
- `checked_in_evidence_present`
- `local_verification_status_present`
- `live_verification_status_present`
- `proof_available_status_present`
- `proof_unavailable_status_present`
- `not_claimed_status_present`
- `unknown_status_present`
- `planned_status_present`
- `deferred_status_present`
- `disclosure_boundary_present`
- `final_submission_packaging_deferred_to_ps039_present`
- `proof_does_not_equal_truth_present`
- `campaign_proof_room_does_not_equal_campaign_performance_proof_present`
- `campaign_narrative_does_not_equal_marketing_effectiveness_proof_present`
- `campaign_intelligence_evidence_does_not_equal_business_outcome_guarantee_present`
- `campaign_artifact_evidence_does_not_equal_legal_authenticity_present`
- `local_campaign_evidence_does_not_equal_live_provider_availability_present`
- `checked_in_campaign_evidence_does_not_equal_live_b2_availability_present`
- `cloudflare_backbone_posture_does_not_equal_live_cloudflare_availability_present`
- `demo_mode_posture_does_not_equal_production_readiness_present`
- `review_approval_evidence_does_not_equal_legal_approval_present`
- `provenance_passport_evidence_does_not_equal_c2pa_authenticity_present`
- `manifest_evidence_does_not_equal_semantic_truth_present`
- `transcript_timestamp_evidence_does_not_equal_transcript_correctness_present`
- `voice_audio_evidence_does_not_equal_speaker_identity_present`
- `no_campaign_performance_proof_claim`
- `no_marketing_effectiveness_proof_claim`
- `no_business_outcome_guarantee_claim`
- `no_semantic_truth_claim`
- `no_legal_authenticity_claim`
- `no_legal_approval_claim`
- `no_human_authorship_claim`
- `no_c2pa_authenticity_claim`
- `no_production_readiness_claim`
- `no_production_security_claim`
- `no_production_compliance_claim`
- `no_legal_compliance_claim`
- `no_live_deployment_claim`
- `no_provider_availability_claim`
- `no_model_availability_claim`
- `no_backblaze_b2_live_availability_claim`
- `no_cloudflare_availability_claim`
- `no_uptime_guarantee_claim`
- `no_cost_guarantee_claim`
- `no_performance_guarantee_claim`
- `no_cold_start_performance_guarantee_claim`
- `no_object_lock_claim`
- `no_tamper_proof_claim`
- `no_browser_side_b2_byte_verification_claim`
- `no_content_moderation_correctness_claim`
- `no_transcript_correctness_claim`
- `no_emotion_truth_claim`
- `no_speaker_identity_claim`
- `no_biometric_identity_claim`
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

- `python scripts/proofstudio_regression_gate.py --current ps038a --frontend --report-out /tmp/proofstudio-release-report.json`
- `python scripts/proofstudio_regression_gate.py --current ps038a --no-frontend --report-out /tmp/proofstudio-ps038a-regression-report.json`
- `scripts/ps038a_campaign_proof_room_smoke.py`
- `docs/evidence/ps-038a/campaign-proof-room-report.json`
- `docs/ps-038a-campaign-proof-room-proof.md`
