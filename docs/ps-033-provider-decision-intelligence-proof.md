# PS-033 — Provider Decision Intelligence — Proof

Status: Spec implementation slice.
Date: 2026-06-30
Slice: PS-033
Route: `/provider-decision-intelligence`

## PS-031A Alignment

PS-033 implements the third PS-031A hardened product module:
**Provider Decision Intelligence**.

`docs/roadmap/ps-031a-hardened-product-modules-correction.md` section 3 ("Provider
Decision Intelligence") says PS-033 merges:

- Credit-Aware Provider Router
- Provider Budget Modes
- Cost and Time Ledger
- Why This Provider
- Emergency No-Key Mode
- quota / paid / free risk explanation

PS-033 does not renumber accepted slices. It references PS-031A explicitly in
the surface, the data module, and this proof doc.

## Hardened Product Module Alignment

PS-033 is a real provider decision surface, not a decorative provider matrix.
It has a clear user job (a marketer / designer / reviewer / client / judge can
understand why a provider was chosen, what it costs or risks, and what the
fallback path is), a product surface (`/provider-decision-intelligence`),
linked evidence (PS-021 through PS-032 plus the documented provider inventory
and the PS-005 / PS-006 router proofs), a truth boundary, smoke validation,
this proof doc, no fake claims, and no decorative-only UI.

## Old-Window Idea Consolidation

PS-033 consolidates the following roadmap (winning implementation roadmap
`docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`)
old-window ideas into one hardened module:

- #8 Credit-Aware Provider Router
- #9 Provider Budget Modes
- #10 Cost and Time Ledger
- #14 Why This Provider?
- #16 Emergency No-Key Mode
- quota / paid / free risk explanation (called out in PS-031A section 3)

These were previously committed to "PS-036 — Credit / Cost / Why This
Provider" in the old roadmap. PS-031A re-routes them into PS-033. PS-033 does
not create one page per idea; it merges them into one decision surface.

## Product Surface Chosen

A dedicated frontend route `/provider-decision-intelligence` rendered by
`apps/web/src/ProviderDecisionIntelligence.tsx`, backed by the verified data
module `apps/web/src/providerDecisionIntelligence.ts`. The component exposes a
`variant` prop (`page` | `section`) so it can also render inline in other
surfaces. It is frontend-only: it performs no network call, calls no provider,
and reads no B2 object.

## API Endpoint

No backend API endpoint was added. The surface reads only checked-in evidence
and documented routing policy. The smoke verifies the existing PS-025 local
contract (FastAPI TestClient resolving the golden run_id from checked-in
evidence) still resolves, and that an arbitrary run_id still 404s. The public
deployment remains pending.

## Files Changed

New:
- `apps/web/src/ProviderDecisionIntelligence.tsx` (component)
- `apps/web/src/providerDecisionIntelligence.ts` (data module)
- `docs/evidence/ps-033/provider-decision-intelligence-smoke.json` (evidence)
- `docs/ps-033-provider-decision-intelligence-proof.md` (this proof)
- `scripts/ps033_provider_decision_intelligence_smoke.py` (smoke)

Updated (CTAs + route + styles):
- `apps/web/src/App.tsx` (route + import + path helper)
- `apps/web/src/JudgeCockpitHome.tsx` (golden demo panel CTA + Direct CTAs tile)
- `apps/web/src/OperationsCockpit.tsx` (page-variant CTA)
- `apps/web/src/JudgeEvidencePack.tsx` (page-variant CTA)
- `apps/web/src/styles.css` (PS-033 styles)

No prior-slice evidence, no prior smoke script, no provider code, no
deployment config, and no backend API file was modified.

## Route / CTA Map

| From | To | Kind |
|------|----|------|
| Judge Cockpit Home (`/`) | `/provider-decision-intelligence` | golden demo panel + Direct CTAs tile |
| Operations Cockpit (`/operations-cockpit`) | `/provider-decision-intelligence` | page-variant CTA |
| Judge Evidence Pack (`/evidence-pack`) | `/provider-decision-intelligence` | page-variant CTA |
| Provider Decision Intelligence | `/` | back link |
| Provider Decision Intelligence | `/operations-cockpit` | action rail |
| Provider Decision Intelligence | `/evidence-pack` | action rail |
| Provider Decision Intelligence | `/failure-timeline` | action rail |
| Provider Decision Intelligence | `/b2-rehydrate-comparison` | action rail |
| Provider Decision Intelligence | `/manifest-verification` | action rail |
| Provider Decision Intelligence | `/b2-evidence` | action rail |
| Provider Decision Intelligence | `/genblaze-pipeline` | action rail |
| Provider Decision Intelligence | `/passport/run_89d967f9000045efa22ed4cc78cfa67f` | action rail |

Optional backlinks (Failure-as-Proof Timeline, B2 Rehydrate Comparison,
Manifest Verification Panel, B2 Evidence Explorer, Genblaze Pipeline Graph,
Public Passport) were left untouched in this slice to keep the change minimal
and low-risk; the required CTAs (Judge Cockpit, Operations Cockpit, Evidence
Pack) and the Provider Decision Intelligence back-links are all present.

## Provider Decision Sections Implemented

1. Provider Decision Identity
2. Decision Summary
3. Provider Option Matrix
4. Budget Modes
5. Why This Provider
6. Cost and Time Ledger
7. Emergency No-Key Mode
8. Provider Failure / Fallback Policy
9. Designer / Marketer Interpretation
10. Action Rail
11. Truth Boundary
12. Limitations

All twelve section headings are rendered and verified by the smoke.

## Provider Option Matrix Explanation

The matrix is limited to providers supported by existing code, docs, or
evidence (sourced from `docs/submission/provider-model-inventory.md`,
`docs/ps-005-pollinations-fallback-proof.md`, and
`src/proofstudio/providers/{router,types}.py`). Each row carries provider
name, model or role, modality or output type, key requirement, budget class,
fallback role, evidence status, risk notes, and a truth class. The smoke
verifies each documented provider token used in the matrix appears in the
documented inventory (no invented provider).

Rows:

- Cloudflare Workers AI (`@cf/bytedance/stable-diffusion-xl-lightning`) — image primary, paid key, documented provider option (PS-004/007/009/010/011).
- Pollinations (`pollinations-image-default`) — image no-key fallback, documented provider option (PS-005).
- Google Gemini (campaign intelligence) — strategy layer, documented provider option (PS-002).
- GMI Cloud — visual generation attempted, blocked by credits (PS-001B, 402).
- Google Gemini / Imagen visual — attempted, quota / paid blocked (PS-003, 429).
- Luma — skipped (card required).
- ElevenLabs / OpenAI / Runway / Stability Audio / NVIDIA NIM — optional later, not implemented.

HONESTY: none of these is claimed as the golden run's selected provider. The
selected provider is marked "not captured in checked-in evidence" because the
PS-021 durable rehydrate smoke records the archive URI / SHA-256 / rehydrate
facts but not the selected provider, selected model, or attempt ledger.

## Budget Modes Explanation

PS-033 presents four budget modes as ROUTING POLICIES, not live billing facts:
`free_safe`, `balanced`, `quality_max`, `emergency_no_key`. Each mode carries
goal, preferred route behavior, fallback behavior, key / payment dependency,
risk, what is measured, and what is not measured yet. The surface labels them
as policy ("Budget modes are routing policies, not live billing facts"). No
actual billing cost is claimed unless measured evidence exists. The golden
run's recorded budget_mode literal is not captured in the durable rehydrate
evidence consumed here.

## Why This Provider Explanation

A human-readable panel answering: why this route is acceptable for the golden
chain (PS-021 proved rehydrate from B2 with zero provider calls; PS-024..PS-032
agree on identity / archive); what evidence backs the decision (checked-in
rehydrate facts + documented provider inventory + ProviderRouter core); what is
not known (selected provider / model / budget mode / attempt count / fallback
count / measured cost / latency / quota are NOT captured); how the system
behaves if a provider key is unavailable (documented router fallback chain to
the no-key path); and how emergency no-key mode differs from quality mode.

## Cost and Time Ledger Explanation

The ledger separates captured values, not-captured values, and future
measurement fields. Required fields are present: provider, model_or_role,
attempt_count, fallback_count, provider_calls_during_rehydrate,
estimated_cost_class, measured_cost, measured_latency, evidence_source,
truth_class. For the golden run, only `provider_calls_during_rehydrate = 0` is
captured. measured_cost and measured_latency show the literal "not captured in
checked-in evidence". No price, spend, latency, quota, or token usage is
invented. The smoke asserts measured_cost / measured_latency are not numeric
currency / latency values.

## Emergency No-Key Mode Explanation

Explains when the mode is useful (missing key / provider failure / disabled /
quota exhausted), how it protects demos and onboarding (documented router
fallback to Pollinations so a demo does not dead-end), the quality tradeoffs
(documented as not a premium final visual provider), the evidence / code
support (PS-005 + ProviderRouter core), and what is not verified for the
golden run (production no-key generation is NOT validated; the golden run's
selected provider / any fallback are not captured). PS-033 does not claim
no-key generation works in production unless validated.

## Fallback Policy Explanation

One policy row per required condition: key missing, quota exhausted, provider
timeout, provider unavailable, moderation / safety block, paid provider
skipped, fallback to no-key mode. Each maps to the documented ProviderRouter
normalized-status vocabulary (SKIPPED_MISSING_KEY, QUOTA_OR_BILLING_BLOCKED,
TIMEOUT, PROVIDER_DOWN, SAFETY_BLOCKED, SKIPPED_DISABLED). The surface carries
the explicit line: "No real provider failure / retry / fallback event is
claimed for the golden run unless checked-in evidence proves it." No actual
failure / retry / fallback is claimed for the golden run.

## Designer / Marketer Value

Plain-language explanations for: best quality mode (quality_max), cheapest safe
mode (free_safe), emergency demo mode (emergency_no_key), why provider choice
affects review, why proof matters for client handoff, and when to export the
evidence pack. This makes the surface useful to non-technical users without
overclaiming.

## Source Evidence List

- `docs/evidence/demo/golden-demo-run.json` (PS-024 golden manifest)
- `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json` (PS-021)
- `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json` (PS-025)
- `docs/evidence/ps-026/b2-evidence-explorer-smoke.json` (PS-026)
- `docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json` (PS-027)
- `docs/evidence/ps-028/manifest-verification-panel-smoke.json` (PS-028)
- `docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json` (PS-029)
- `docs/evidence/ps-030/failure-as-proof-timeline-smoke.json` (PS-030)
- `docs/evidence/ps-031/export-campaign-pack-v2-smoke.json` (PS-031)
- `docs/evidence/ps-032/operations-cockpit-flight-recorder-v2-smoke.json` (PS-032)
- `docs/roadmap/ps-031a-hardened-product-modules-correction.md` (PS-031A)
- `docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`
- `docs/submission/provider-model-inventory.md` (documented provider options)
- `docs/ps-005-pollinations-fallback-proof.md` (no-key fallback)
- `docs/ps-006-provider-router-core-proof.md` (router policy)

## Proof Chain Explanation

The surface cross-references the golden run identity and rehydrate facts from
PS-021 (live B2 durable rehydrate smoke) and the PS-024 golden manifest, both
of which are traced forward through PS-025 (narrow public passport unlock),
PS-026 (B2 Evidence Explorer), PS-027 (Genblaze Pipeline Graph), PS-028
(Manifest Verification Panel), PS-029 (B2 Rehydrate Comparison), PS-030
(Failure-as-Proof Timeline), PS-031 (Judge Evidence Pack), and PS-032
(Operations Cockpit). Every source agrees on run_id, campaign_id, archive URI,
archive SHA-256, rehydrate_source = `b2_rehydrated`,
provider_calls_during_rehydrate = 0, and
no_live_provider_call_during_rehydrate = true. The provider option facts come
from the documented provider inventory and the PS-005 / PS-006 router proofs.

## No-Provider-Call Confirmation

PS-033 source files contain no provider-call code patterns
(`call_provider`, `fetchFromProvider`, `requests.post`, `urlopen(`, `httpx.post`,
`client.post(`). The surface performs no network call. The smoke's
`no_provider_call` check passes.

## No-Broad-B2-Read Confirmation

PS-033 source files contain no broad B2 read patterns (`read_archive_from_b2`,
`b2.fetch`, `b2GetObject`, `list_b2_objects`, `fetchB2Object`, `fetch(`). An
arbitrary run_id still returns 404 through the public durable passport path.
The smoke's `no_broad_b2_read` check passes.

## No-Fake-Provider-Failure Confirmation

No fake actual provider failure / retry / fallback / outage claim is made
outside a non-claim context. The fallback policy section is explicitly policy.
The surface carries the line "No real provider failure / retry / fallback
event is claimed for the golden run unless checked-in evidence proves it." The
smoke's `no_fake_failure_claim` check passes.

## No-Raw-Media-Byte Confirmation

No raw media byte inspection claim is made. The smoke's
`no_raw_media_byte_claim` check passes.

## No-Actual-Spend-Without-Evidence Confirmation

No actual spend / measured cost for the golden run is claimed. measured_cost
rows carry the literal "not captured in checked-in evidence". Budget classes
are policy. The smoke's `no_actual_spend_claim_without_evidence` check passes.

## No-Actual-Latency-Without-Evidence Confirmation

No actual latency for the golden run is claimed. measured_latency rows carry
the literal "not captured in checked-in evidence". The smoke's
`no_actual_latency_claim_without_evidence` check passes.

## No-Quota-Status-Without-Evidence Confirmation

No actual quota status / quota remaining / token usage for the golden run is
claimed. The smoke's `no_quota_status_claim_without_evidence` check passes.

## No-Prior-Slice-Evidence-Mutation Confirmation

PS-033 owns only `docs/evidence/ps-033/`. The smoke snapshots every evidence
file outside `ps-033/` before invoking any regression smoke and restores the
exact bytes afterward (try/finally). Tracked evidence that historical smokes
unlink before deeper regressions (PS-027 / PS-028 / PS-029 / PS-030 / PS-031 /
PS-032) is marked `--assume-unchanged` for the duration of each regression run
and restored + unflagged afterward. The smoke's
`no_prior_slice_evidence_modified` check passes.

## Truth Boundary

The surface summarizes checked-in evidence and documented routing policy,
explains provider decision tradeoffs, shows cost / budget classes as policy
unless measured evidence exists, shows zero provider calls during rehydrate,
helps marketers understand routing choices, and shows pending gaps honestly.
It does not prove semantic truth, legal authenticity, C2PA authenticity, or
human authorship. It does not prove Object Lock or tamper-proof storage. It did
not fetch and hash the B2 object in the browser. Public deployment remains
pending. It does not claim enterprise security.

## Limitations

- No live provider call in PS-033.
- No broad B2 read.
- No live pricing API; cost classes are policy, not measured billing.
- No measured billing unless present in checked-in evidence (measured cost /
  latency not captured for the golden run).
- No measured latency unless present in checked-in evidence.
- No quota inspection; quota status is not captured and not claimed.
- Public deployment pending.
- Checked-in evidence and documented policy only.
- No invented provider failure events.
- Selected provider / model / budget mode / attempt count / fallback count for
  the golden run are not captured in the durable rehydrate evidence consumed
  here and are not invented.

## Validation Commands

```
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python scripts/ps033_provider_decision_intelligence_smoke.py
cd apps/web && npm run typecheck && npm run build && cd ../..
```

Python whitespace check applies to all changed files. The smoke leaves the
working tree clean except for PS-033 files.

## Smoke Result

See `docs/evidence/ps-033/provider-decision-intelligence-smoke.json` (`ok: true`
when all checks pass). The smoke validates all 90 required checks including the
PS-032 through PS-023 regressions (through snapshot/restore protection) and the
frontend typecheck/build.
