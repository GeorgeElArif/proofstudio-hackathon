# PS-038 — Production Readiness + Demo Mode — Proof

## 1. What PS-038 adds

PS-038 adds a reusable **Production Readiness + Demo Mode** layer — a demo-mode
/ readiness-posture / cold-start-mitigation inspection layer rendered
additively on every core proof surface. It makes the demo path, the readiness
posture, the local/static fallback, the golden evidence fallback, the
checked-in evidence fallback, the live dependency boundaries, the cold-start
mitigation plan, and the readiness checklist explicit, inspectable, and
truth-bounded in one consistent place, so a judge, customer, or demo reviewer
can read what demo mode is, whether demo mode is active or planned, whether the
demo uses local/golden/checked-in evidence, whether live dependencies are
required for the judge demo, and what the layer proves and does not prove.

It is a demo-path-and-readiness-posture-over-recorded-proof layer. It is
**not** a live deployment, **not** a production readiness claim, **not** a
production security system, **not** a production compliance system, **not** an
uptime guarantee, **not** a cost guarantee, **not** a performance guarantee,
**not** a cold-start performance guarantee, **not** a load test, **not** a
vulnerability scan, **not** a penetration test, **not** an incident-response
readiness system, **not** an SLO/SLA system, **not** a data retention
compliance system, **not** a privacy compliance system, **not** a Cloudflare
deployment, **not** a DNS change, and **not** a new backend endpoint.

## 2. Files changed

New files:

- `apps/web/src/productionReadinessDemoMode.ts` — the canonical Production
  Readiness + Demo Mode data module.
- `apps/web/src/ProductionReadinessDemoModeLayer.tsx` — the shared component
  (`variant="panel"` / `variant="summary"`).
- `scripts/ps038_production_readiness_demo_mode_smoke.py` — the PS-038 feature
  smoke (local / static, non-mutating by default).
- `docs/ps-038-production-readiness-demo-mode-proof.md` — this proof doc.
- `docs/evidence/ps-038/production-readiness-demo-mode-report.json` — the
  evidence report (written only when `--write-evidence` is explicit).

Additive edits (existing files, additive only):

- `apps/web/src/styles.css` — only the additive
  `.production-readiness-demo-mode-layer*` classes.
- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/B2EvidenceExplorer.tsx`
- `apps/web/src/ManifestVerificationPanel.tsx`
- `apps/web/src/B2RehydrateComparison.tsx`
- `apps/web/src/B2AuditVault.tsx`
- `apps/web/src/ReviewApprovalWorkspace.tsx`
- `apps/web/src/JudgeEvidencePack.tsx`
- `apps/web/src/PublicPassportPage.tsx`

No other files were changed. No `AGENTS.md`, no `render.yaml`, no `.env*`, no
requirements files, no `scripts/proofstudio_regression_gate.py`, no
`scripts/smoke_lib.py`, no spec / validation docs, and no prior-slice evidence
were touched.

## 3. How the Production Readiness + Demo Mode layer works

The layer has two parts:

1. **`productionReadinessDemoMode.ts`** — the single shared data module. It
   exposes the canonical set of demo / readiness concepts (demo mode, readiness
   posture, production readiness status, demo mode status, local demo status,
   judge demo status, local/static fallback, golden evidence fallback,
   checked-in evidence fallback, live dependency status, provider dependency
   status, B2 dependency status, Cloudflare dependency status, deployment
   evidence status, production security evidence status, production compliance
   evidence status, cold-start mitigation status, startup health status,
   cost-control status, provider fallback status, failure-mode status,
   export/offline evidence status, demo path evidence, readiness checklist
   evidence, local verification, live verification status, disclosure
   boundary), the cross-references, the honest unavailable / not-claimed /
   planned / ready-for-local-demo states, the de-escalation pairs, the negative
   boundary strings, and the persistent boundary statement. It reads only
   accepted local / golden / demo data and existing accepted data modules.

2. **`ProductionReadinessDemoModeLayer.tsx`** — the shared component. It reads
   only from the data module and renders a compact summary variant
   (`variant="summary"`) or an expanded readiness-posture / readiness-checklist
   panel (`variant="panel"`).

The layer is rendered additively on the nine required core proof surfaces
(Judge Cockpit Home, B2 Evidence Explorer, Manifest Verification Panel, B2
Rehydrate Comparison, B2 Audit Vault, Review + Approval Workspace, Judge
Evidence Pack, Public Provenance Passport, Review Room), alongside the existing
`TrustBoundaryLayer` (PS-037), `MultimodalProofLayer` (PS-037a),
`TranscriptTimestampEvidenceLayer` (PS-037b),
`VoiceAudioEvidenceChoiceLayer` (PS-037c),
`CampaignIntelligenceJudgeNarrativeLayer` (PS-037d), and
`CloudflareLowCostBackboneLayer` (PS-037e).

## 4. Why demo mode does not equal production readiness

Demo mode is a judge-facing posture label for local / golden / checked-in demo
evidence only. Naming demo mode does not imply a live deployment, a production
readiness claim, a production security claim, a production compliance claim, an
uptime guarantee, a cost guarantee, a performance guarantee, a cold-start
performance guarantee, or any correctness guarantee. The layer surfaces this
de-escalation pair verbatim: "demo mode does not equal production readiness."

## 5. Why the production readiness layer label does not equal a production readiness claim

The production readiness layer label names the layer's scope (demo / readiness
posture inspection); it does not assert that production readiness has been
achieved. No production readiness evidence is checked into accepted data, so
the layer surfaces an honest "production readiness evidence not available"
state and a "deferred to later production work" state. The layer surfaces this
de-escalation pair verbatim: "production readiness layer does not equal
production readiness claim."

## 6. Why the readiness checklist does not equal production security

The readiness checklist is a framing artifact that lists the demo / readiness
posture items; it is not a security audit, a vulnerability scan, or a
penetration test. The layer surfaces this de-escalation pair verbatim:
"readiness checklist does not equal production security."

## 7. Why local demo mode does not equal live deployment

Local demo mode runs entirely over accepted local / golden / checked-in data.
No live deployment exists in accepted evidence, so the layer surfaces an honest
"production deployment not available" state. The layer surfaces this
de-escalation pair verbatim: "local demo mode does not equal live deployment."

## 8. Why the cold-start mitigation plan does not equal a measured performance guarantee

PS-038 owns the cold-start mitigation **plan** only. The implementation and the
measurement remain later / out-of-scope work. No cold-start measurement is
checked into accepted evidence, so the layer surfaces an honest "cold-start
measurement not available" state and a "cold-start mitigation planned" state.
The layer surfaces this de-escalation pair verbatim: "cold-start mitigation
plan does not equal measured performance guarantee."

## 9. Why the low-cost demo posture does not equal cost guarantee

The low-cost demo posture is a framing choice (local / static by default, no
paid live dependency); it is not a billing commitment, a spend guarantee, or a
price lock. The layer surfaces this de-escalation pair verbatim: "low-cost demo
posture does not equal cost guarantee."

## 10. Why local fallback does not equal live provider availability

Local fallback means the demo falls back to local / static evidence when live
dependencies are unavailable. It does not prove that any live provider is
reachable. The layer surfaces an honest "live provider evidence not available"
state. The layer surfaces this de-escalation pair verbatim: "local fallback
does not equal live provider availability."

## 11. Why checked-in evidence does not equal live B2 availability

Checked-in evidence is recorded-only golden / demo fixture data; it is not a
live B2 object read. The layer surfaces an honest "live B2 evidence not
available" state. The layer surfaces this de-escalation pair verbatim:
"checked-in evidence does not equal live B2 availability."

## 12. Why the Cloudflare dependency posture does not equal live Cloudflare availability

Cloudflare is named for dependency posture labeling only. No live Cloudflare
API call, DNS mutation, Cloudflare resource creation, Cloudflare Pages
deployment, Cloudflare Workers deployment, Cloudflare R2 live read, or
Cloudflare R2 write occurs. The layer surfaces an honest "live Cloudflare
evidence not available" state. The layer surfaces this de-escalation pair
verbatim: "Cloudflare dependency posture does not equal live Cloudflare
availability."

## 13. Local / static default

The layer is purely client-side by default: it makes no Cloudflare API call,
mutates no DNS, creates no Cloudflare resource, deploys no Cloudflare Pages,
deploys no Cloudflare Workers, performs no Cloudflare R2 live read, performs no
Cloudflare R2 write, performs no Backblaze B2 write, calls no provider, calls
no model, reads no B2 object, performs no browser-side B2 byte verification,
performs no broad B2 scan, and writes no B2 object. It only reads accepted
local / golden / demo data and existing accepted data modules.

## 14. No deployment / env / secrets / render / requirements changes

PS-038 makes no deployment changes, no env/secrets changes, no render.yaml
changes, and no requirements/dependency changes. The smoke enforces
`no_deployment_changes`, `no_env_secrets_changes`, `no_render_yaml_changes`,
and `no_requirements_dependency_changes`.

## 15. No live Cloudflare / API / DNS / resource / deploy / R2 / B2 / provider / model behavior

PS-038 performs no Cloudflare API call, no DNS mutation, no Cloudflare resource
creation, no Cloudflare Pages deployment, no Cloudflare Workers deployment, no
Cloudflare R2 live read, no Cloudflare R2 write, no Backblaze B2 write, no
provider call, no model call, no live B2 read, no B2 write, and no broad B2
scan. The smoke enforces every corresponding `no_*` boolean.

## 16. Backblaze B2 and Genblaze manifest remain checked-in systems of record

Backblaze B2 remains the durable proof/archive system of record. The Genblaze
manifest evidence remains the system of record. The Production Readiness +
Demo Mode layer only cross-references these recorded systems of record; it does
not displace them and does not perform any live B2 / manifest behavior.

## 17. PS-037 / PS-037a / PS-037b / PS-037c / PS-037d / PS-037e preservation / cross-reference

The Production Readiness + Demo Mode layer renders alongside the PS-037
Disclosure + Trust Boundary Layer, the PS-037a Multimodal Proof Layer, the
PS-037b Transcript/Timestamp Evidence layer, the PS-037c Voice/Audio Evidence
Provider Choice layer, the PS-037d Gemini Campaign Intelligence / Judge
Narrative layer, and the PS-037e Cloudflare Low-Cost Backbone layer. It reuses
the shared disclosure concepts and cross-references each predecessor layer; it
never contradicts or weakens any of those contracts. No PS-037 / PS-037a /
PS-037b / PS-037c / PS-037d / PS-037e contract file was weakened.

## 18. Validation commands and results

```
python scripts/ps038_production_readiness_demo_mode_smoke.py --check-only --no-frontend
python scripts/ps038_production_readiness_demo_mode_smoke.py --write-evidence --no-frontend
python scripts/proofstudio_regression_gate.py --current ps038 --no-frontend --report-out /tmp/proofstudio-ps038-regression-report.json
cd apps/web && npx tsc --noEmit
```

The hidden Git flags check uses `git ls-files -v` and `line[0]`; it fails on
marker `h` or `S`. `git diff --check` is clean. Prior evidence outside
`docs/evidence/ps-038/` is unchanged.

## 19. Truth boundary / negative claims

ProofStudio proves what the pipeline recorded for the demo path and readiness
posture. Proof does not equal truth. Demo mode does not equal production
readiness. The production readiness layer label does not equal a production
readiness claim. A readiness checklist does not equal production security.
Local demo mode does not equal live deployment. A cold-start mitigation plan
does not equal a measured performance guarantee. A low-cost demo posture does
not equal cost guarantee. Local fallback does not equal live provider
availability. Checked-in evidence does not equal live B2 availability. A
Cloudflare dependency posture does not equal live Cloudflare availability.
Demo/golden readiness evidence does not equal production compliance.

The layer is not production readiness, not production security, not production
compliance, not legal compliance, not live deployment, not Cloudflare
deployment, not Cloudflare availability, not Backblaze B2 live availability,
not provider availability, not model availability, not uptime guarantee, not
cost guarantee, not performance guarantee, not cold-start performance
guarantee, not load-test coverage, not vulnerability scan coverage, not
penetration test coverage, not incident response readiness, not SLO/SLA
guarantee, not data retention compliance, not privacy compliance, not Object
Lock, not tamper-proof, not browser-side B2 byte verification, not semantic
truth, not legal authenticity, not human authorship, not C2PA authenticity,
not campaign performance prediction, not marketing effectiveness proof, and
not model output truth.
