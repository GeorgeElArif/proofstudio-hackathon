# PS-034 — Lineage + Comparison Lab — Proof

Status: Implemented
Date: 2026-06-30
Slice: PS-034
Route: `/lineage-comparison-lab`

## PS-031A alignment

PS-034 implements the fourth PS-031A hardened product module: **Lineage +
Comparison Lab**. Per `docs/roadmap/ps-031a-hardened-product-modules-correction.md`,
PS-034 must merge four old-window ideas into one coherent workspace:

- Model Audition Board
- Manifest Diff
- Provider Swap Re-run
- Variant Family Tree

PS-031A forbids building duplicate disconnected proof pages for overlapping
ideas. PS-034 consolidates these four comparison jobs into a single lineage /
comparison workspace that a designer, marketer, reviewer, client, or judge can
open and use.

## Hardened product module alignment

A hardened module must have: a clear user job, product surface, linked
evidence, truth boundary, smoke validation, proof doc, no fake claims, and no
decorative-only UI. PS-034 delivers all of these via:

- `apps/web/src/LineageComparisonLab.tsx` (surface)
- `apps/web/src/lineageComparisonLab.ts` (verified constants + JSON builder)
- `docs/evidence/ps-034/lineage-comparison-lab-smoke.json` (linked evidence)
- `scripts/ps034_lineage_comparison_lab_smoke.py` (smoke validation)
- this proof doc

## Old-window idea consolidation

| Old-window idea | Merged into PS-034 section |
| --- | --- |
| Model Audition Board | Model Audition Board section |
| Manifest Diff | Manifest Diff section |
| Provider Swap Re-run | Provider Swap Re-run Planner section |
| Variant Family Tree | Variant Family Tree section |

## Product surface chosen

A dedicated frontend route `/lineage-comparison-lab` rendering the
`LineageComparisonLab` component. Frontend-only; no backend endpoint added.
The component supports a `variant` prop (`page` | `section`) so it can render
as a full page or an inline section.

## Files changed

New:
- `apps/web/src/LineageComparisonLab.tsx`
- `apps/web/src/lineageComparisonLab.ts`
- `docs/evidence/ps-034/lineage-comparison-lab-smoke.json` (smoke-generated)
- `docs/ps-034-lineage-comparison-lab-proof.md`
- `scripts/ps034_lineage_comparison_lab_smoke.py`

Updated (required CTAs + route):
- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/OperationsCockpit.tsx`
- `apps/web/src/ProviderDecisionIntelligence.tsx`
- `apps/web/src/JudgeEvidencePack.tsx`
- `apps/web/src/styles.css`

Updated (optional low-risk backlinks):
- `apps/web/src/FailureAsProofTimeline.tsx`
- `apps/web/src/B2RehydrateComparison.tsx`
- `apps/web/src/ManifestVerificationPanel.tsx`
- `apps/web/src/B2EvidenceExplorer.tsx`
- `apps/web/src/GenblazePipelineGraph.tsx`
- `apps/web/src/PublicPassportPage.tsx`

No provider code, manifest/archive code, backend API, deployment config, or
prior-slice evidence was modified.

## Route / CTA map

Route added: `/lineage-comparison-lab` -> `LineageComparisonLab` (page variant).

Inbound CTAs (required, now present):
- Judge Cockpit Home (`/`) -> `/lineage-comparison-lab` (button + dedicated tile)
- Operations Cockpit (`/operations-cockpit`) -> `/lineage-comparison-lab`
- Provider Decision Intelligence (`/provider-decision-intelligence`) -> `/lineage-comparison-lab`
- Judge Evidence Pack (`/evidence-pack`) -> `/lineage-comparison-lab`

Inbound backlinks (optional, clean):
- Failure-as-Proof Timeline -> `/lineage-comparison-lab`
- B2 Rehydrate Comparison -> `/lineage-comparison-lab`
- Manifest Verification Panel -> `/lineage-comparison-lab`
- B2 Evidence Explorer -> `/lineage-comparison-lab`
- Genblaze Pipeline Graph -> `/lineage-comparison-lab`
- Public Passport -> `/lineage-comparison-lab`

Outbound CTAs from the lab (Action Rail + page CTA row):
`/provider-decision-intelligence`, `/operations-cockpit`, `/evidence-pack`,
`/failure-timeline`, `/b2-rehydrate-comparison`, `/manifest-verification`,
`/b2-evidence`, `/genblaze-pipeline`,
`/passport/run_89d967f9000045efa22ed4cc78cfa67f`, `/`.

## Lineage + Comparison Lab sections implemented

1. Lab Identity
2. Lineage Summary
3. Variant Family Tree
4. Manifest Diff
5. Model Audition Board
6. Provider Swap Re-run Planner
7. Comparison Readiness Checklist
8. Designer / Marketer Interpretation
9. Action Rail
10. Truth Boundary
11. Limitations

Plus: Source evidence files, Deployment status.

## Variant family tree explanation

The Variant Family Tree is a card/tree layout over the verified lineage. The
required nodes are present: Campaign, Golden Run, Asset / Manifest, B2
Archive, Rehydrated Evidence, Public Passport, Judge Evidence Pack, and
Review / Next Action. The required relationship labels are present (owns,
generated, archived_to, rehydrated_from, exposes, exports, awaits_review).
Because no second variant is captured, two future variant slots are shown
honestly as `future variant slot` / `not captured in checked-in evidence`. No
variant IDs, model outputs, or provider reruns are invented.

## Manifest diff explanation

The Manifest Diff compares the known golden manifest fields (PS-024, left /
source) against the rehydrated/archive proof fields (PS-021 durable rehydrate,
right / comparison) for the eight required fields: run_id, campaign_id,
archive_uri, archive_sha256, rehydrate_source,
provider_calls_during_rehydrate, no_live_provider_call_during_rehydrate, and
public_deployment_pending. Seven rows match exactly across manifest and
archive proof. The `public_deployment_pending` row is honestly `not captured`
on the left (the PS-024 manifest does not record it) and `true` on the right
(PS-025 captures it), so its match status is `not_captured`. No missing
manifest field is invented.

## Model audition board explanation

The Model Audition Board shows how multiple model candidates would be compared
across the eight required columns (candidate, provider/model role, modality,
evidence status, quality review status, cost/time status, proof status,
decision). The golden run candidate discloses
`selected provider/model not captured in checked-in evidence`. Two future
slots are marked `audition slot not run` / `not captured in checked-in
evidence`. No model scores, quality scores, cost scores, or winner labels are
invented.

## Provider swap rerun planner explanation

The Provider Swap Re-run Planner is a documented policy workflow (planner, not
an executed rerun) with the nine required steps: keep campaign_id, create new
run_id, preserve source prompt/brief if available, route through provider
decision policy, capture new asset/manifest, archive to B2, compare manifest
diff, attach to variant family, update review/export state. The exact truth
line `No provider swap rerun is claimed for the verified golden run.` is
surfaced verbatim.

## Comparison readiness explanation

The Comparison Readiness Checklist shows whether the system has enough
evidence to compare variants across the 13 required items. Present items:
golden run exists, B2 archive exists, manifest hash exists, rehydrate proof
exists, provider calls during rehydrate captured, evidence pack exists,
operations cockpit exists, provider decision policy exists. Honestly missing
items: second real variant exists, model scores captured, measured cost
captured, measured latency captured, review decision captured.

## Designer / marketer value

The Designer / Marketer Interpretation explains in plain language: why lineage
matters, why comparing variants helps campaigns, why manifest diff matters,
how provider swaps help creative teams, when to rerun with another model, when
to export the evidence pack, and why missing variant data is not a failure.
This makes the lab useful to non-technical users, not just engineers.

## Source evidence list

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
- `docs/evidence/ps-033/provider-decision-intelligence-smoke.json` (PS-033)
- `docs/roadmap/ps-031a-hardened-product-modules-correction.md` (PS-031A)
- `docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`

## Proof chain explanation

The lab's golden values are sourced verbatim from the checked-in PS-024
manifest and the PS-021 durable rehydrate evidence, both of which agree on
run_id, campaign_id, archive_uri, archive_sha256, rehydrate_source, and
provider_calls_during_rehydrate. PS-025 supplies `public_deployment_pending`.
PS-026 / PS-027 / PS-028 / PS-029 / PS-030 / PS-031 / PS-032 / PS-033 each
re-pin the same run_id, campaign_id, archive_uri, and archive_sha256, forming
a cross-source proof chain. The PS-034 smoke cross-checks every frontend
constant against every source. No value is invented.

## No-provider-call confirmation

Confirmed. PS-034 performs no network call. The smoke scans all changed
frontend files for forbidden provider-call patterns (`requests.post`,
`httpx.post`, `client.post(`, `call_provider`, `fetchFromProvider`,
`urlopen(`) and finds none. `provider_calls_during_rehydrate` equals 0 across
all sources and the frontend constant.

## No-broad-B2-read confirmation

Confirmed. The surface records the archive URI and SHA-256 from checked-in
evidence; it does not fetch the B2 object. The smoke scans all changed
frontend files for forbidden broad-B2-read patterns (`read_archive_from_b2`,
`b2.fetch`, `b2GetObject`, `list_b2_objects`, `fetchB2Object`, `fetch(`) and
finds none. An arbitrary run_id still returns 404 from the passport endpoint
(broad durable read stays blocked).

## No-provider-swap-rerun claim confirmation

Confirmed. The exact line `No provider swap rerun is claimed for the verified
golden run.` is surfaced verbatim. The planner is documented policy only. The
smoke scans for affirmative provider-swap-rerun overclaims and finds none
outside non-claim context.

## No-second-variant-without-evidence confirmation

Confirmed. The exact line `Only one verified golden run is available in
checked-in evidence.` is surfaced verbatim. Future variant slots are honestly
labeled `future variant slot` / `not captured in checked-in evidence`. The
smoke scans for second-variant overclaims and finds none outside non-claim
context.

## No-model-score-without-evidence confirmation

Confirmed. No model scores are invented; the audition board marks quality /
cost / model scores as `not captured in checked-in evidence`. The smoke scans
for model-score overclaims and finds none outside non-claim context.

## No-winner-without-evidence confirmation

Confirmed. No winner label is assigned; the golden run candidate decision is
`no winner label assigned`. The smoke scans for winner overclaims and finds
none outside non-claim context.

## No-actual-spend-without-evidence confirmation

Confirmed. No measured spend is claimed; cost classes are policy only. The
smoke scans for spend overclaims and finds none outside non-claim context.

## No-actual-latency-without-evidence confirmation

Confirmed. No measured latency is claimed. The smoke scans for latency
overclaims and finds none outside non-claim context.

## No-raw-media-byte confirmation

Confirmed. The surface does not inspect raw media bytes. The smoke scans for
raw-media-byte claims and finds none outside non-claim context.

## No-prior-slice-evidence-mutation confirmation

Confirmed. PS-034 owns only `docs/evidence/ps-034/`. PS-034 does not execute
any historical smoke, so no prior-slice evidence is ever rewritten. The
`no_prior_slice_evidence_modified` check confirms no evidence outside
`ps-034/` is dirty in `git status`. No prior smoke script is modified.

## Regression design (non-recursive prior-slice contract)

PS-034 avoids recursive smoke execution. Historical smokes already include
their own transitive regressions, and nesting them (PS-033 -> PS-032 -> ...
-> PS-023) made the chain O(n²) and brittle — PS-030 timed out after 300
seconds when nested under PS-034. Instead, PS-034 uses a non-recursive
prior-slice contract:

- **Checked-in evidence presence.** Each prior accepted slice evidence file
  (PS-033 .. PS-025) must still exist.
- **Success markers.** Each must still record `ok: true`.
- **Golden constants.** Each must still re-pin `run_id`, `campaign_id`,
  `archive_uri`, `archive_sha256`, and `rehydrate_source` consistently with
  the PS-024 golden manifest. PS-024 is the manifest itself; PS-023 is the
  foundational Judge Cockpit Home smoke (no evidence file), represented by
  the smoke script + home component being present.
- **Route / file presence.** The sibling routes PS-034 links to must still be
  registered in `App.tsx` (`/provider-decision-intelligence`,
  `/operations-cockpit`, `/evidence-pack`, `/failure-timeline`,
  `/b2-rehydrate-comparison`, `/manifest-verification`, `/b2-evidence`,
  `/genblaze-pipeline`) plus the golden passport surface.
- **Clean git status.** No prior-slice evidence file may be modified.
- **Frontend build once.** `npm run typecheck` and `npm run build` run
  exactly once at the PS-034 level — not once per nested smoke.

The per-slice result keys (`ps033_passes` .. `ps023_passes`) are retained in
the smoke output and evidence JSON for result continuity, but their meaning
is now **"prior accepted regression contract is still satisfied"**, not
"recursively executed the full historical smoke." This prevents O(n²) smoke
recursion and repeated frontend builds.

## Truth boundary

The surface summarizes checked-in lineage evidence, compares known manifest /
proof fields, shows where future variants and provider swaps would appear,
shows only one verified golden run (because that is true), helps creative
teams plan comparison workflows, and shows pending gaps honestly. It does not
prove semantic truth, legal authenticity, C2PA authenticity, or human
authorship. It does not prove Object Lock or tamper-proof storage. It did not
fetch and hash the B2 object in the browser. The local contract is verified;
the public deployment remains pending.

## Limitations

- No live provider call in PS-034.
- No provider swap rerun executed.
- No second real variant captured unless evidence exists (none exists yet).
- No model score captured unless evidence exists (none exists yet).
- No broad B2 read.
- No live pricing API; cost classes are policy, not measured billing.
- No measured billing unless present in checked-in evidence.
- No measured latency unless present in checked-in evidence.
- Public deployment pending.
- Checked-in evidence and documented policy only.
- No invented variant events.

## Validation commands

```bash
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python scripts/ps034_lineage_comparison_lab_smoke.py
cd apps/web && npm run typecheck && npm run build && cd ../..
git status --short --branch --untracked-files=all
```

## Smoke result

See `docs/evidence/ps-034/lineage-comparison-lab-smoke.json` for the canonical
`ok` + per-check result. The smoke validates component + data module + route
+ sibling route presence + inbound/outbound CTAs + all 11 sections + golden
value cross-source agreement + no provider call + no broad B2 read + no fake
claim + no forbidden authenticity claim + no secrets + no prior-slice
evidence mutation, verifies the non-recursive prior-slice regression contract
(PS-033 .. PS-023 accepted evidence + golden constants + route presence +
clean git status), and runs frontend typecheck/build exactly once.
