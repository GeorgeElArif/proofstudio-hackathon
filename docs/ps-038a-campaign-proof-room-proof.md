# PS-038a — Campaign Proof Room — Proof

## 1. What PS-038a adds

PS-038a adds a **Campaign Proof Room**: a judge-facing campaign-level command
room for one proof-backed campaign. It is a navigation, evidence, and narrative
surface over already-recorded proof — not a new generation pipeline, not a new
provider/model integration, not a new backend endpoint, and not a live
deployment.

It assembles the existing accepted ProofStudio proof layers into one
campaign-level story so a judge or demo reviewer can, in one place, read:

- what campaign artifact was made
- what proof exists for the campaign artifact
- what evidence can be inspected
- what evidence remains unavailable or not claimed
- how B2 / Genblaze / rehydrate / manifest / provider evidence fit together
  for the campaign
- how demo / readiness posture fits the campaign demo
- what the system proves and does not prove for the campaign
- how the product creates real-world utility for creator/marketing teams
- what proof is available and what proof is unavailable
- what is planned, deferred, not claimed, or unknown

The room reads only accepted local / static / golden / demo data and existing
accepted data modules. It is local / static by default. It makes no Cloudflare
API call, mutates no DNS, creates no Cloudflare resource, deploys no Cloudflare
Pages, deploys no Cloudflare Workers, performs no Cloudflare R2 live read,
performs no Cloudflare R2 write, performs no Backblaze B2 write, calls no
provider, calls no model, reads no B2 object, performs no browser-side B2 byte
verification, performs no broad B2 scan, and writes no B2 object.

## 2. Files changed

New files:

- `apps/web/src/campaignProofRoom.ts` — the canonical Campaign Proof Room data
  module. Exposes the single shared set of campaign-level concepts, the
  honest "proof available" / "proof unavailable" / "not claimed" / "unknown" /
  "planned" / "deferred" states, the cross-references (PS-037 / PS-037a /
  PS-037b / PS-037c / PS-037d / PS-037e / PS-038), the de-escalation pairs,
  the negative boundary strings, and the final submission packaging deferred
  to PS-039 state.
- `apps/web/src/CampaignProofRoom.tsx` — the Campaign Proof Room page
  component. Accepts the `variant` convention (`variant="page"` for the full
  campaign-level command room; `variant="summary"` for a compact campaign
  proof summary), reads only from `campaignProofRoom.ts`, and renders the
  campaign proof summary, the guided campaign proof trail, the proof timeline,
  the evidence map, the inspection path, the judge demo path, the
  creator/marketing workflow utility, the cross-references, the honest
  unavailable / not-claimed / planned / deferred states, the negative
  boundary, the de-escalation pairs, and the persistent campaign truth
  boundary.
- `scripts/ps038a_campaign_proof_room_smoke.py` — the PS-038a feature smoke.
  Validates only the PS-038a slice. Local / static by default; supports
  `--check-only` (default), `--write-evidence`, and `--no-frontend`.
- `docs/ps-038a-campaign-proof-room-proof.md` — this proof doc.

Modified files (additive only):

- `apps/web/src/App.tsx` — adds the `isCampaignProofRoomPath()` route helper
  and dispatches `<CampaignProofRoom variant="page" />` before the passport /
  review fallbacks.
- `apps/web/src/JudgeCockpitHome.tsx` — adds an additive campaign-room CTA
  link (`<a className="btn btn-primary" href="/campaign-proof-room">`) in the
  navigation block.
- `apps/web/src/styles.css` — adds only the additive Campaign Proof Room
  classes. No existing layer class is removed or weakened.

Evidence (written only by the smoke when `--write-evidence` is explicit):

- `docs/evidence/ps-038a/campaign-proof-room-report.json`

## 3. How the Campaign Proof Room works

The room is a single page component on route `/campaign-proof-room`. It reads
only from `apps/web/src/campaignProofRoom.ts`, which in turn reuses read-only
accepted constants from `apps/web/src/b2Evidence.ts` (PS-026, traced to the
golden demo manifest and PS-021 durable rehydrate evidence) and
`apps/web/src/multimodalProof.ts` (PS-035A manifest reference / hash).

The room renders, in one guided order:

1. A **campaign proof summary** block — the recorded campaign artifact, the
   campaign artifact reference (archive URI), the campaign artifact digest
   (archive SHA-256), the proof available / proof unavailable status, the
   inspection path, and the judge demo path.
2. A **guided campaign proof trail** — eight steps walking a judge through the
   recorded campaign artifact, the campaign proof summary, the proof trail,
   the proof timeline, the evidence map, the inspection path, the judge demo
   path, and the not-claimed / unavailable / deferred states.
3. A **proof timeline** — the recorded proof events (brief -> provider router
   -> Genblaze pipeline -> generated asset -> B2 archive -> rehydrate ->
   manifest -> passport -> review/approval -> export pack).
4. An **evidence map** — every campaign evidence concept with its honest
   state.
5. An **inspection path** — deep-links into every proof surface.
6. A **judge demo path** — the recommended three-minute judge demo flow.
7. A **creator/marketing workflow utility** block.
8. A **cross-references** block — explicit cross-reference statements with
   PS-037, PS-037a, PS-037b, PS-037c, PS-037d, PS-037e, and PS-038.
9. The honest **unavailable / not-claimed / planned / deferred states**.
10. The **negative boundary** strings and the **de-escalation pairs**.
11. The **concepts** checklist.
12. The persistent **campaign truth boundary** statement.

The room renders alongside each accepted proof layer
(`MultimodalProofLayer`, `TranscriptTimestampEvidenceLayer`,
`VoiceAudioEvidenceChoiceLayer`, `CampaignIntelligenceJudgeNarrativeLayer`,
`CloudflareLowCostBackboneLayer`, `ProductionReadinessDemoModeLayer`, and
`TrustBoundaryLayer`) so every existing contract stays canonical. The room
cross-references each layer; it never duplicates, weakens, or removes a layer
contract.

## 4. Why the Campaign Proof Room does not equal campaign performance proof

The Campaign Proof Room is a navigation / evidence / narrative surface over
recorded proof. It states what the pipeline already recorded for one
proof-backed campaign. It does not measure, predict, or prove campaign
performance. No campaign performance metric (reach, conversions, ROI,
engagement, attribution) is checked into accepted data, so the room surfaces
an honest "proof unavailable" / "not claimed" state for campaign performance
rather than fabricating one. Naming the Campaign Proof Room does not imply a
campaign performance proof. The Campaign Proof Room does not equal campaign
performance proof.

## 5. Why campaign narrative does not equal marketing effectiveness proof

The room surfaces a campaign narrative framing (the guided campaign proof trail
and the creator/marketing workflow utility). That narrative describes what was
recorded and what is unavailable; it does not measure marketing effectiveness.
No marketing effectiveness measurement is checked into accepted data. Campaign
narrative does not equal marketing effectiveness proof.

## 6. Why campaign intelligence evidence does not equal business outcome guarantee

The room cross-references the PS-037d Gemini Campaign Intelligence / Judge
Narrative layer as recorded / checked-in framing only. It does not measure,
predict, or guarantee a business outcome. Campaign intelligence evidence does
not equal business outcome guarantee. Creator/marketing workflow utility does
not equal business outcome guarantee.

## 7. Why campaign artifact evidence does not equal legal authenticity

The room surfaces the recorded campaign artifact, its archive reference, and
its archive digest. A recorded artifact reference and a SHA-256 digest prove
that the pipeline recorded this artifact; they do not prove legal
authenticity. Campaign artifact evidence does not equal legal authenticity.

## 8. Why local campaign evidence does not equal live provider availability

The room reads only local / static / golden / demo evidence. It makes no live
provider call. The fact that campaign evidence is present locally does not
mean any provider is currently available. Local campaign evidence does not
equal live provider availability.

## 9. Why checked-in campaign evidence does not equal live B2 availability

The room cross-references checked-in B2 / archive / rehydrate evidence
recorded by PS-021 / PS-026 / PS-029 / PS-036. The checked-in evidence proves
the pipeline recorded this durable archive; it does not mean the B2 object is
reachable live from this room. Checked-in campaign evidence does not equal live
B2 availability.

## 10. Why Cloudflare backbone posture does not equal live Cloudflare availability

The room cross-references the PS-037e Cloudflare Low-Cost Backbone layer. It
names Cloudflare for backbone posture labeling only. It makes no Cloudflare
API call, performs no Cloudflare R2 live read, and creates no Cloudflare
resource. Cloudflare backbone posture does not equal live Cloudflare
availability.

## 11. Why demo mode posture does not equal production readiness

The room cross-references the PS-038 Production Readiness + Demo Mode layer.
The demo mode posture is a local / demo posture label; it does not mean the
system is production ready. Demo mode posture does not equal production
readiness.

## 12. Why review approval evidence does not equal legal approval

The room cross-references the PS-035 Review + Approval Workspace. A review /
approval record records a reviewer's workflow decision; it does not prove legal
approval. Review approval evidence does not equal legal approval.

## 13. Why provenance passport evidence does not equal C2PA authenticity

The room cross-references the PS-019 / PS-025 Public Provenance Passport. The
passport is a recorded provenance object; it is not a C2PA manifest and is not
verified as C2PA authenticity. Provenance passport evidence does not equal
C2PA authenticity.

## 14. Why manifest evidence does not equal semantic truth

The room cross-references the PS-028 / PS-035A manifest evidence. A manifest
hash proves the manifest bytes agree across checked-in sources; it does not
prove the content is semantically true. Manifest evidence does not equal
semantic truth.

## 15. Why transcript/timestamp evidence does not equal transcript correctness

The room cross-references the PS-037b Transcript/Timestamp Evidence layer.
Transcript/timestamp evidence records that a transcript/timestamp framing
exists; it does not prove the transcript is correct.
Transcript/timestamp evidence does not equal transcript correctness.

## 16. Why voice/audio evidence does not equal speaker identity

The room cross-references the PS-037c Voice/Audio Evidence Provider Choice
layer. Voice/audio evidence records a provider choice and a framing; it does
not identify a speaker. Voice/audio evidence does not equal speaker identity.

## 17. Local / static default

The room is local / static by default. It works without deployment changes,
without env/secrets changes, without render.yaml changes, without
requirements/dependency changes, without Cloudflare API calls, without DNS
mutation, without Cloudflare resource creation, without Cloudflare Pages
deployment, without Cloudflare Workers deployment, without Cloudflare R2 live
reads, without Cloudflare R2 writes, without Backblaze B2 writes, without
provider calls, without model calls, without live B2 reads, without B2 writes,
and without broad B2 scans.

## 18. No deployment / env / secrets / render / requirements changes

PS-038a makes no deployment changes, no env/secrets changes, no render.yaml
changes, and no requirements/dependency changes. The smoke enforces
`no_deployment_changes`, `no_env_secrets_changes`, `no_render_yaml_changes`,
and `no_requirements_dependency_changes`.

## 19. No live Cloudflare / API / DNS / resource / deploy / R2 / B2 / provider /
model behavior

PS-038a makes no Cloudflare API call, mutates no DNS, creates no Cloudflare
resource, deploys no Cloudflare Pages, deploys no Cloudflare Workers, performs
no Cloudflare R2 live read, performs no Cloudflare R2 write, performs no
Backblaze B2 write, calls no provider, calls no model, reads no live B2 object,
writes no B2 object, and performs no broad B2 scan. The smoke enforces every
one of these as a boolean.

## 20. Backblaze B2 and Genblaze manifest remain checked-in systems of record

Backblaze B2 remains the durable proof / archive system of record
(PS-010 / PS-021 / PS-026 / PS-036). Genblaze remains the manifest system of
record (PS-027 / PS-028). PS-038a only cross-references their checked-in
evidence; it does not call them live, does not write to them, and does not
claim they are live-available. Checked-in campaign evidence does not equal live
B2 availability.

## 21. PS-037 / PS-037a / PS-037b / PS-037c / PS-037d / PS-037e / PS-038
preservation / cross-reference

The Campaign Proof Room renders alongside and cross-references every accepted
proof layer:

- PS-037 Disclosure + Trust Boundary — renders alongside `TrustBoundaryLayer`,
  reuses the shared disclosure concepts, never contradicts the PS-037 boundary.
- PS-037a Multimodal Proof Layer — surfaces an honest multimodal artifact
  evidence cross-reference (manifest reference / manifest hash reused from
  PS-035A via PS-037a).
- PS-037b AssemblyAI Transcript/Timestamp Evidence layer — surfaces an honest
  transcript/timestamp evidence cross-reference.
- PS-037c Voice/Audio Evidence Provider Choice layer — surfaces an honest
  voice/audio evidence cross-reference.
- PS-037d Gemini Campaign Intelligence / Judge Narrative layer — surfaces an
  honest campaign intelligence evidence cross-reference.
- PS-037e Cloudflare Low-Cost Backbone layer — surfaces an honest Cloudflare
  backbone posture cross-reference.
- PS-038 Production Readiness + Demo Mode layer — surfaces an honest production
  readiness demo mode posture cross-reference.

PS-038a does not edit the PS-037, PS-037a, PS-037b, PS-037c, PS-037d, PS-037e,
or PS-038 contract files. No existing layer class is removed or weakened.

## 22. Validation commands and results

1. `python scripts/ps038a_campaign_proof_room_smoke.py --check-only --no-frontend`
2. `python scripts/ps038a_campaign_proof_room_smoke.py --write-evidence --no-frontend`
3. `python scripts/proofstudio_regression_gate.py --current ps038a --no-frontend --report-out /tmp/proofstudio-ps038a-regression-report.json`
4. `cd apps/web && npx tsc --noEmit`
5. Hidden Git flags check: `git ls-files -v`, fail when `line[0]` is `h` or `S`.
6. `git diff --check`
7. Prior evidence outside `docs/evidence/ps-038a/` is unchanged.

The PS-038a evidence report is written only when `--write-evidence` is
explicit, at `docs/evidence/ps-038a/campaign-proof-room-report.json`.

## 23. Truth boundary / negative claims

ProofStudio proves what the pipeline recorded for the campaign. Proof does not
equal truth. The Campaign Proof Room does not equal campaign performance proof.
Campaign narrative does not equal marketing effectiveness proof. Campaign
intelligence evidence does not equal business outcome guarantee. Campaign
artifact evidence does not equal legal authenticity. Local campaign evidence
does not equal live provider availability. Checked-in campaign evidence does
not equal live B2 availability. Cloudflare backbone posture does not equal live
Cloudflare availability. Demo mode posture does not equal production readiness.
Review approval evidence does not equal legal approval. Provenance passport
evidence does not equal C2PA authenticity. Manifest evidence does not equal
semantic truth. Transcript/timestamp evidence does not equal transcript
correctness. Voice/audio evidence does not equal speaker identity.

The room does not claim: campaign performance proof, marketing effectiveness
proof, business outcome guarantee, semantic truth, legal authenticity, legal
approval, human authorship, C2PA authenticity, production readiness, production
security, production compliance, legal compliance, live deployment, provider
availability, model availability, Backblaze B2 live availability, Cloudflare
availability, uptime guarantee, cost guarantee, performance guarantee,
cold-start performance guarantee, Object Lock, tamper-proof storage,
browser-side B2 byte verification, content moderation correctness, transcript
correctness, emotion truth, speaker identity, biometric identity, or model
output truth. Final submission packaging is deferred to PS-039.
