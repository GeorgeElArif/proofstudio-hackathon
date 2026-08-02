# PS-032 — Operations Cockpit / Flight Recorder v2 — Proof

## PS-031A alignment

PS-032 is the first hardened product module defined by the PS-031A roadmap
correction (`docs/roadmap/ps-031a-hardened-product-modules-correction.md`).
PS-031A says:

> PS-032 should implement Operations Cockpit / Flight Recorder v2.

PS-031A merges Mission Control, Flight Recorder, Failure-as-Proof Timeline,
Failure Theater, Evidence Graph, and the pipeline lifecycle view into this
single hardened module. The user job is: a creative operator can see what
happened from brief to export without reading raw JSON.

PS-032 does not renumber any accepted roadmap slice and follows both the PS-022
master roadmap and the binding implementation roadmap
(`docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`).

## Hardened product module alignment

PS-031A requires every hardened module to carry: a clear user job, product
surface or API behavior, linked evidence, truth boundary, smoke validation,
proof doc, no fake claims, and no decorative-only UI.

PS-032 satisfies each:

- **User job:** a designer, marketer, reviewer, client, or judge can open one
  cockpit and answer what campaign/run this is, what happened first/next/last,
  which evidence is checked-in, which evidence points to B2, which points to
  Genblaze manifest verification, whether rehydrate called providers again,
  where failures/retries/fallbacks would appear, what is ready for
  review/export, and what is still pending or not claimed.
- **Product surface:** dedicated `/operations-cockpit` route + component.
- **Linked evidence:** nine checked-in evidence sources plus the
  implementation roadmap and the PS-031A correction.
- **Truth boundary:** allowed / forbidden claim boundary rendered in the UI.
- **Smoke validation:** `scripts/ps032_operations_cockpit_flight_recorder_smoke.py`.
- **Proof doc:** this file.
- **No fake claims:** Failure Theater slot carries the exact line
  `No fake failures are claimed.` and `For the verified golden run, rehydrate
  uses B2-backed evidence with zero provider calls.`
- **No decorative-only UI:** every section maps to checked-in evidence or an
  honest pending / non-claim marker.

## Old-window idea consolidation

PS-032 consolidates six old-window / out-of-the-box ideas that previously would
have been separate disconnected pages:

1. Mission Control
2. Flight Recorder
3. Failure-as-Proof Timeline (carried forward from PS-030)
4. Failure Theater
5. Evidence Graph
6. Pipeline lifecycle view

Rather than building six pages, PS-032 builds one operating cockpit that
renders each idea as a section of the same surface, all sourced from the same
verified golden evidence chain.

## Product surface chosen

Dedicated frontend route `/operations-cockpit` + component
`apps/web/src/OperationsCockpit.tsx` + data module
`apps/web/src/operationsCockpit.ts`. Frontend-only; no new API endpoint.

## Files changed

- `apps/web/src/App.tsx` — registered `/operations-cockpit` route via
  `isOperationsCockpitPath()` and rendered `OperationsCockpit`.
- `apps/web/src/JudgeCockpitHome.tsx` — added a button in the golden demo run
  panel and a dedicated tile in the Direct CTAs grid.
- `apps/web/src/JudgeEvidencePack.tsx` — added a link to
  `/operations-cockpit` (page variant CTA row).
- `apps/web/src/FailureAsProofTimeline.tsx` — added a link to
  `/operations-cockpit` (page variant CTA row).
- `apps/web/src/B2RehydrateComparison.tsx` — optional low-risk backlink to
  `/operations-cockpit` (page variant CTA row).
- `apps/web/src/ManifestVerificationPanel.tsx` — optional low-risk backlink to
  `/operations-cockpit` (page variant CTA row).
- `apps/web/src/B2EvidenceExplorer.tsx` — optional low-risk backlink to
  `/operations-cockpit` (page variant CTA row).
- `apps/web/src/GenblazePipelineGraph.tsx` — optional low-risk backlink to
  `/operations-cockpit` (page variant CTA row).
- `apps/web/src/styles.css` — added Operations Cockpit styles.
- `apps/web/src/OperationsCockpit.tsx` — new component.
- `apps/web/src/operationsCockpit.ts` — new verified constants module +
  `buildOperationsCockpitJson()`.
- `docs/evidence/ps-032/operations-cockpit-flight-recorder-v2-smoke.json` — new
  smoke evidence (written by the smoke script).
- `docs/ps-032-operations-cockpit-flight-recorder-v2-proof.md` — this proof doc.
- `scripts/ps032_operations_cockpit_flight_recorder_smoke.py` — new smoke script.

No prior-slice evidence JSON was modified. No historical smoke script (PS-019
through PS-031) was modified. No backend / API / provider / deploy config was
changed.

## Route / CTA map

| From | To | Kind |
| --- | --- | --- |
| Judge Cockpit Home (golden demo run panel + Direct CTAs tile) | `/operations-cockpit` | required CTA |
| Judge Evidence Pack (page CTA row) | `/operations-cockpit` | required link |
| Failure-as-Proof Timeline (page CTA row) | `/operations-cockpit` | required link |
| Operations Cockpit (page CTA row) | `/` | required link |
| Operations Cockpit (page CTA row) | `/evidence-pack` | required link |
| Operations Cockpit (page CTA row) | `/failure-timeline` | required link |
| Operations Cockpit (action rail + CTA row) | `/b2-rehydrate-comparison` | required link |
| Operations Cockpit (action rail + CTA row) | `/manifest-verification` | required link |
| Operations Cockpit (action rail + CTA row) | `/b2-evidence` | required link |
| Operations Cockpit (action rail + CTA row) | `/genblaze-pipeline` | required link |
| Operations Cockpit (action rail + CTA row) | `/passport/run_89d967f9000045efa22ed4cc78cfa67f` | required link |
| B2 Rehydrate Comparison (page CTA row) | `/operations-cockpit` | optional backlink |
| Manifest Verification Panel (page CTA row) | `/operations-cockpit` | optional backlink |
| B2 Evidence Explorer (page CTA row) | `/operations-cockpit` | optional backlink |
| Genblaze Pipeline Graph (page CTA row) | `/operations-cockpit` | optional backlink |

## Cockpit sections implemented

The component renders all 10 required sections:

1. Cockpit identity (`Operations Cockpit`, `Flight Recorder`, `PS-032`,
   run_id, campaign_id, public deployment pending).
2. Run status summary (campaign/run identity, archive status, manifest status,
   rehydrate status, provider call status during rehydrate, evidence pack
   status, review/export readiness, pending public deployment).
3. Operational phase map (10 phases).
4. Flight Recorder timeline (10 ordered events).
5. Evidence graph (12 nodes + 10 edges).
6. Failure Theater slot.
7. Action rail (8 routes).
8. Designer / marketer next actions (7 actions).
9. Truth boundary (allowed + forbidden claims).
10. Limitations (7 honesty markers).

## Phase map explanation

The phase map renders the run as 10 phases, each carrying a title, status,
truth class, evidence source, and next route or action:

1. Campaign brief (inferred product explanation)
2. Provider routing / orchestration (inferred product explanation)
3. Media generation attempt (inferred product explanation)
4. Asset and manifest capture (Genblaze manifest evidence)
5. Backblaze B2 archive (B2 archive reference)
6. Genblaze manifest verification (Genblaze manifest evidence)
7. B2 rehydrate (rehydrate proof)
8. Failure-as-Proof / retry visibility (inferred product explanation)
9. Judge Evidence Pack export (local export contract)
10. Review / next action (public deployment pending)

Phases that would require the golden run's live attempt ledger or raw prompt
packet (which are not part of checked-in evidence) are honestly marked as
inferred product explanation rather than checked-in evidence. The smoke's
`required_phases_exist` and `truth_classes_exist` checks validate all 10 phases
and all 7 required truth classes are present.

## Flight recorder explanation

The flight recorder renders 10 ordered events, each carrying a sequence
number, title, event type, status, evidence anchor, route link when available,
and a truth class.

The checked-in evidence does NOT carry real wall-clock timestamps for these
operational events. To stay honest, each event records a `timestampHonesty`
label instead of an invented timestamp:

- `source evidence order`
- `checked-in evidence order`
- `not timestamped in checked-in evidence`

The smoke's `event_sequence_exists` check validates each event carries a seq
number, and the `timestamp_honesty_exists` check validates the honesty labels
are present and that no event invents an ISO-style timestamp.

## Evidence graph explanation

The evidence graph is an accessible card / column representation (no graph
library required). It carries 12 required nodes and 10 required edges so a
reviewer can read the campaign → run → router → pipeline → asset → archive →
verification → rehydrate → passport → pack → review chain at a glance.

Required nodes: Campaign, Run, Provider Router, Genblaze Pipeline,
Asset / Manifest, B2 Archive, Manifest Verification, B2 Rehydrate,
Failure-as-Proof Timeline, Judge Evidence Pack, Public Passport,
Review / Next Action.

Required edges: Campaign → Run, Run → Provider Router, Provider Router →
Genblaze Pipeline, Genblaze Pipeline → Asset / Manifest, Asset / Manifest →
B2 Archive, Asset / Manifest → Manifest Verification, B2 Archive → B2
Rehydrate, B2 Rehydrate → Public Passport, Failure-as-Proof Timeline → Judge
Evidence Pack, Judge Evidence Pack → Review / Next Action.

The smoke's `required_nodes_exist` and `required_edges_exist` checks validate
every node and edge by resolving node labels to ids and matching edge tuples.

## Failure Theater slot explanation

The Failure Theater slot shows where captured failures, retries, and fallbacks
would appear if future evidence captured them. It carries the two exact
required lines verbatim:

- `No fake failures are claimed.`
- `For the verified golden run, rehydrate uses B2-backed evidence with zero provider calls.`

No provider failure is invented. The smoke's `no_fake_failures_line`,
`zero_provider_calls_line`, and `no_fake_failure_claim` checks validate this.

## Designer / marketer value

The cockpit is built for non-technical users. The Designer / marketer next
actions section lists: review asset proof, open evidence pack, inspect
rehydrate proof, verify manifest, prepare client handoff, understand
disclosure boundary, and continue to review/approval workspace when available
(PS-035 commitment). Every action maps to a concrete proof surface or an
honest pending marker.

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
- `docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`
- `docs/roadmap/ps-031a-hardened-product-modules-correction.md` (PS-031A)

## Proof chain explanation

The cockpit cross-references nine checked-in evidence sources plus the
implementation roadmap and the PS-031A correction. Each golden value (run_id,
campaign_id, archive URI, archive SHA-256, rehydrate source,
provider_calls_during_rehydrate, no_live_provider_call_during_rehydrate) is
validated to agree across PS-021 / PS-024 / PS-025 / PS-026 / PS-027 / PS-028 /
PS-029 / PS-030 / PS-031 AND match the frontend constants. The cockpit is a
superset summary of the existing proof chain, not a new proof claim.

## No-provider-call confirmation

PS-032 source files contain no provider-call pattern. The cockpit performs no
network call to any provider; every value is computed from checked-in
constants. The smoke's `no_provider_call` check scans all changed source files
for `call_provider`, `fetchFromProvider`, `requests.post`, `urlopen`,
`httpx.post`, and `client.post(` patterns and passes.

## No-broad-B2-read confirmation

PS-032 source files contain no B2 object read pattern. The cockpit records the
archive URI and SHA-256 from checked-in evidence; it did not fetch the B2
object in the browser. The smoke's `no_broad_b2_read` check scans for
`read_archive_from_b2`, `b2.fetch`, `b2GetObject`, `list_b2_objects`,
`fetchB2Object`, and `fetch(` patterns and passes. It also confirms an
arbitrary run id still returns 404 through the public durable passport path,
so no broad durable read is introduced.

## No-fake-failure confirmation

The cockpit does not claim any actual provider failure, fallback, retry, or
outage occurred for the golden run. The Failure Theater slot carries the exact
line `No fake failures are claimed.` The smoke's `no_fake_failure_claim` check
scans for affirmative fake-failure phrases outside non-claim contexts and
passes.

## No-raw-media-byte confirmation

The cockpit does not inspect or read raw media bytes. The B2 archive content is
a JSON run archive, not the generated media. The smoke's
`no_raw_media_byte_claim` check scans for affirmative raw-media-byte phrases
outside non-claim contexts and passes.

## No-prior-slice-evidence-mutation confirmation

PS-032 owns only `docs/evidence/ps-032/`. The smoke snapshots the byte content
of every other evidence file before invoking any regression smoke and restores
the exact bytes afterward (try/finally). Historical smoke scripts PS-019
through PS-031 were not modified. Tracked unlink-prone evidence (ps-027 /
ps-028 / ps-029 / ps-030 / ps-031) is marked `--assume-unchanged` during each
regression run so git status stays clean. The smoke's
`no_prior_slice_evidence_modified` check passes.

## Truth boundary

The cockpit carries the canonical truth boundary text plus an allowed /
forbidden claim boundary.

Allowed claims:

- The cockpit summarizes checked-in evidence for the golden run.
- The cockpit links to B2 archive evidence (archive URI and SHA-256).
- The cockpit links to Genblaze manifest evidence (cross-source consistency).
- The cockpit shows zero provider calls during rehydrate.
- The cockpit helps reviewers understand workflow provenance and limitations.
- The cockpit shows pending product gaps honestly (public deployment pending).

Forbidden claims (stated as non-claims so the context-aware scanners do not
flag the boundary terms):

- The cockpit does not prove semantic truth of the media.
- The cockpit does not prove legal authenticity.
- The cockpit does not prove human authorship.
- The cockpit does not prove C2PA authenticity.
- The cockpit does not prove Object Lock or tamper-proof storage.
- The cockpit did not fetch and hash the B2 object in the browser.
- The cockpit does not perform browser-side B2 byte verification.
- Public deployment has not been verified (it remains pending).
- The cockpit does not claim enterprise security.

## Limitations

- No live provider call in PS-032: the cockpit performs no network call.
- No broad B2 read: the cockpit records the archive URI and SHA-256 from
  checked-in evidence; it did not fetch the B2 object.
- No browser-side B2 byte verification: the archive SHA-256 is the value
  recorded by PS-021, not a value the browser recomputed.
- No raw media byte inspection: the B2 archive content is a JSON run archive,
  not the generated media.
- Public deployment pending: the local contract is verified; the public Render
  deployment remains pending.
- Checked-in evidence only: the cockpit surfaces the golden run's checked-in
  evidence, not a live operational feed.
- No invented failure events: the Failure Theater slot shows where captured
  failures would appear; none are claimed for the golden run.

## Validation commands

```bash
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python scripts/ps032_operations_cockpit_flight_recorder_smoke.py
cd apps/web && npm run typecheck && npm run build && cd ../..
git status --short --branch --untracked-files=all
```

The smoke invokes the PS-031 / PS-030 / PS-029 / PS-028 / PS-027 / PS-026 /
PS-025 / PS-024 / PS-023 regressions internally under byte-snapshot / restore
protection plus `--assume-unchanged` index handling for the tracked
unlink-prone evidence (ps-027 / ps-028 / ps-029 / ps-030 / ps-031).

## Smoke result

The PS-032 smoke writes
`docs/evidence/ps-032/operations-cockpit-flight-recorder-v2-smoke.json` with
`ok: true` when every check passes, including:

- `operations_cockpit_surface_verified`
- `cockpit_identity_visible`
- `run_status_summary_visible`
- `phase_map_verified`
- `flight_recorder_verified`
- `evidence_graph_verified`
- `failure_theater_slot_visible`
- `designer_marketer_next_actions_visible`
- `action_rail_verified`
- `truth_boundary_present`
- `limitations_present`
- `source_ps021_evidence` … `source_ps031_evidence`
- `source_ps031a_roadmap_correction`
- `frontend_surface_verified`
- `api_surface_verified`
- `no_provider_call`
- `no_broad_b2_read`
- `no_raw_media_byte_claim`
- `no_fake_failure_claim`
- `no_prior_slice_evidence_modified`
- `public_deployment_pending`

The latest run's `checks` map is in the evidence JSON.
