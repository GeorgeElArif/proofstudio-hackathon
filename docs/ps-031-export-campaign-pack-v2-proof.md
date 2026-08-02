# PS-031 — Export Campaign Pack v2 / Judge Evidence Pack — Proof

## Roadmap alignment

PS-031 follows the PS-022 master roadmap and the binding implementation
roadmap (`docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`).
Lead-in slices completed:

- PS-023 — Judge Cockpit Home
- PS-024 — Golden Demo Run Pinning
- PS-025 — Public Durable Passport Unlock
- PS-026 — B2 Evidence Explorer
- PS-027 — Genblaze Pipeline Graph
- PS-028 — Manifest Verification Panel
- PS-029 — B2 Rehydrate Comparison
- PS-030 — Failure-as-Proof Timeline

PS-030 made the whole golden workflow visible as an evidence-backed
operational timeline. PS-031 turns that proof chain into a portable,
readable judge / client pack with honest local browser exports.

## Implementation-roadmap commitment alignment

The implementation roadmap is binding: old-window out-of-the-box ideas are
implementation commitments, not notes. PS-031 implements three roadmap
sections:

- Section 6 — **Export Campaign Pack / Judge Evidence Pack** (final asset
  summary, prompt packet, provider note, attempt ledger, manifest summary,
  passport JSON, B2 archive proof, rehydrate proof, disclosure notes,
  limitations, judge/client README).
- Section 21 — **Judge Evidence Pack** (the pack as a judge-facing surface).
- The Archive / Rehydrate Lab direction called out for PS-031 / PS-043
  (the pack records the verified archive + rehydrate values; interactive
  lab work remains a later slice).

Where a roadmap field is not part of the checked-in evidence consumed by
this pack (raw prompt packet, live attempt ledger for the golden run), the
pack honestly marks the section as "not available from checked-in evidence"
instead of inventing it.

## Old-window / out-of-the-box idea implemented

The old-window idea is that a judge, client, reviewer, or operator should be
able to take the proof chain away as a usable evidence package — not just
view proof pages. PS-031 ships this as a real product surface: a
judge-facing Export Campaign Pack v2 / Judge Evidence Pack that assembles
the verified golden workflow into one readable pack and exposes honest local
browser exports (pack JSON + pack README / Markdown).

## Product surface chosen

Dedicated frontend route `/evidence-pack` + component
`apps/web/src/JudgeEvidencePack.tsx` + data module
`apps/web/src/judgeEvidencePack.ts`. Frontend-only; no new API endpoint.

## Files changed

- `apps/web/src/App.tsx` — registered `/evidence-pack` route via
  `isEvidencePackPath()` and rendered `JudgeEvidencePack`.
- `apps/web/src/JudgeCockpitHome.tsx` — added a button in the golden demo
  run panel and a dedicated tile in the Direct CTAs grid.
- `apps/web/src/FailureAsProofTimeline.tsx` — added a link to
  `/evidence-pack` (page variant CTA row).
- `apps/web/src/styles.css` — added Judge Evidence Pack styles.
- `apps/web/src/JudgeEvidencePack.tsx` — new component.
- `apps/web/src/judgeEvidencePack.ts` — new verified constants module +
  `buildJudgeEvidencePackJson()` + `buildJudgeEvidencePackMarkdown()`.
- `docs/evidence/ps-031/export-campaign-pack-v2-smoke.json` — new smoke
  evidence (written by the smoke script).
- `docs/ps-031-export-campaign-pack-v2-proof.md` — this proof doc.
- `scripts/ps031_export_campaign_pack_v2_smoke.py` — new smoke script.

No prior-slice evidence JSON was modified. No historical smoke script
(PS-019 through PS-030) was modified. No backend / API / provider / deploy
config was changed.

## Route / CTA map

| From | To | Kind |
| --- | --- | --- |
| Judge Cockpit Home (golden demo run panel + Direct CTAs tile) | `/evidence-pack` | required CTA |
| Failure-as-Proof Timeline (page CTA row) | `/evidence-pack` | required link |
| Judge Evidence Pack (page CTA row) | `/failure-timeline` | required link |
| Judge Evidence Pack (page CTA row) | `/b2-rehydrate-comparison` | required link |
| Judge Evidence Pack (page CTA row) | `/manifest-verification` | required link |
| Judge Evidence Pack (page CTA row) | `/b2-evidence` | required link |
| Judge Evidence Pack (page CTA row) | `/genblaze-pipeline` | required link |
| Judge Evidence Pack (page CTA row) | `/passport/run_89d967f9000045efa22ed4cc78cfa67f` | required link |
| Judge Evidence Pack (page CTA row) | `/` | required link |

Optional low-risk backlinks (B2RehydrateComparison, ManifestVerificationPanel,
B2EvidenceExplorer, GenblazePipelineGraph, PublicPassportPage) were not
added in PS-031 to keep the slice focused; the spec marks them optional.

## Pack sections

The component renders all 15 required sections:

1. Pack identity
2. Campaign / run identity
3. Final asset / archive summary
4. Prompt / generation evidence summary
5. Provider / model / attempt ledger summary
6. B2 archive evidence
7. Genblaze manifest evidence
8. B2 rehydrate proof
9. Failure-as-Proof summary
10. Public passport link
11. Review / approval status
12. Disclosure readiness notes
13. Truth boundary
14. Limitations
15. Next actions for judge / client

Sections 4 and 5 honestly mark themselves as "not available from checked-in
evidence" because the raw prompt packet and the live attempt ledger for the
golden run are not part of the checked-in evidence consumed by PS-031. The
durable rehydrate ledger fact (`provider_calls_during_rehydrate = 0`) is
still surfaced in section 5.

## Pack JSON shape

`buildJudgeEvidencePackJson(generatedAt)` returns the exported pack JSON.
Required keys (all present):

- `pack_id` (deterministic: `pack_ps031_<golden_run_id>`)
- `pack_version` (`2.0.0`)
- `generated_from` (honest local-export provenance string)
- `generated_at` (the only dynamic field; the smoke does not assert on it)
- `campaign_id`
- `run_id`
- `archive_uri`
- `archive_sha256`
- `rehydrate_source` (`b2_rehydrated`)
- `provider_calls_during_rehydrate` (`0`)
- `no_live_provider_call_during_rehydrate` (`true`)
- `source_evidence` (8 sources)
- `route_map` (7 routes)
- `proof_chain` (8 steps)
- `failure_as_proof_summary`
- `disclosure_notes`
- `truth_boundary`
- `limitations`
- `public_deployment_pending` (`true`)

`pack_id` is deterministic (not a UUID / random id) so the same golden run
always yields the same pack_id and the smoke is free of brittle expectations.

## README / Markdown export behavior

`buildJudgeEvidencePackMarkdown(generatedAt)` returns the README text. It
includes:

- title: `ProofStudio Judge Evidence Pack`
- run_id
- campaign_id
- what the pack proves
- what it does not prove
- B2 archive URI
- archive SHA-256
- rehydrate proof
- zero provider calls during rehydrate
- proof surface links
- disclosure notes
- limitations
- public deployment pending

Both exports are produced by a browser-side `Blob` + anchor download (see
`triggerBrowserDownload` in `JudgeEvidencePack.tsx`). Copy-to-clipboard
actions are also exposed; if the clipboard API is unavailable the action
does not fake success.

Honest export labels are surfaced verbatim in the UI:

- Local browser export.
- Generated from checked-in ProofStudio evidence.
- Does not fetch B2 bytes.
- Does not include raw media bytes.
- Not a zip export (zip generation is not implemented in PS-031).

## Source evidence list

- `docs/evidence/demo/golden-demo-run.json` (PS-024 golden manifest)
- `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json` (PS-021)
- `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json` (PS-025)
- `docs/evidence/ps-026/b2-evidence-explorer-smoke.json` (PS-026)
- `docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json` (PS-027)
- `docs/evidence/ps-028/manifest-verification-panel-smoke.json` (PS-028)
- `docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json` (PS-029)
- `docs/evidence/ps-030/failure-as-proof-timeline-smoke.json` (PS-030)
- `docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`

## Proof chain explanation

The pack exposes the proof chain as 8 ordered steps:

1. Pack identity established (local browser export)
2. Golden run identity pinned (checked-in evidence)
3. B2 archive recorded (durable B2 archive proof)
4. Genblaze manifest captured (Genblaze manifest evidence)
5. Public passport contract unlocked locally (local public passport contract proof)
6. Rehydrate proven durable without provider rerun (B2 rehydrate proof)
7. Failure-as-Proof carried into the pack (checked-in evidence)
8. Public deployment pending remains explicit (public deployment pending)

Every step cites the checked-in evidence that backs it. The chain makes the
operational trail readable top-to-bottom inside the pack while the route map
lets a judge step out into any underlying surface.

## Failure-as-Proof carryover

The pack carries PS-030's Failure-as-Proof summary forward as a dedicated
section. It states that operational events are auditable workflow evidence,
that the timeline shows where captured failures / retries / fallbacks would
appear, that the verified golden run currently proves durable B2 rehydrate
with zero provider calls, that no actual failure or fallback is claimed
unless evidence proves it, and that for the verified golden run rehydrate
uses B2-backed evidence with zero provider calls. No fake failures are
claimed.

## Disclosure Readiness carryover

The Disclosure Readiness Layer is a PS-035 commitment. PS-031 carries it
forward as the "Disclosure readiness notes" section: plain-language
disclosure, known facts, unknown / not-claimed facts, the channel-ready
copy planned for PS-035, and the explicit "not legal advice / not a
certification" note. The pack is a proof summary, not a channel-ready
disclosure asset.

## No-zip-claim confirmation

Zip generation is NOT implemented in PS-031. The pack does not claim a zip
export. The UI labels the export as "Not a zip export (zip generation is
not implemented in PS-031)" and the smoke's `no_zip_claim` check rejects any
affirmative zip claim outside a non-claim context.

## No-raw-media-byte-claim confirmation

The pack does NOT include raw media bytes. The B2 archive content is a JSON
run archive (passport / attempt ledger / asset metadata), not the generated
media. The UI labels the export as "Does not include raw media bytes" and
the smoke's `no_raw_media_byte_claim` check rejects any affirmative
raw-media-byte claim outside a non-claim context.

## No-provider-call confirmation

PS-031 source files contain no provider-call pattern. The pack performs no
network call to any provider; the local browser export is computed entirely
from checked-in constants. The smoke's `no_provider_call` check passes.

## No-broad-B2-read confirmation

PS-031 source files contain no B2 object read pattern. The pack records the
archive URI and SHA-256 from checked-in evidence; it did not fetch the B2
object in the browser. The smoke's `no_broad_b2_read` check also confirms
an arbitrary run id still returns 404 through the public durable passport
path, so no broad durable read is introduced.

## No-prior-slice-evidence-mutation confirmation

PS-031 owns only `docs/evidence/ps-031/`. The smoke snapshots the byte
content of every other evidence file before invoking any regression smoke
and restores the exact bytes afterward (try/finally). Historical smoke
scripts PS-019 through PS-030 were not modified. The smoke's
`no_prior_slice_evidence_modified` check passes.

## Truth boundary confirmation

The pack carries the canonical truth boundary text plus an allowed /
forbidden claim boundary. Allowed claims:

- Checked-in evidence records B2 rehydrate proof for the golden run.
- Checked-in evidence records zero provider calls during rehydrate.
- Checked-in evidence agrees on the archive URI and SHA-256.
- The pack is generated from local checked-in ProofStudio evidence.
- The browser export gives judges a portable proof summary.
- The pack helps reviewers understand workflow provenance and limitations.

Forbidden claims (stated as non-claims so the context-aware scanners do not
flag the boundary terms):

- The pack does not prove semantic truth of the media.
- The pack does not prove legal authenticity.
- The pack does not prove human authorship.
- The pack does not prove C2PA authenticity.
- The pack does not prove Object Lock or tamper-proof storage.
- The pack did not fetch and hash the B2 object in the browser.
- The pack does not include raw media bytes.
- The pack does not produce a zip export (zip generation is not implemented).
- Public deployment has not been verified (it remains pending).
- The pack is not a certification and is not legal advice.

## Validation commands

```bash
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python scripts/ps031_export_campaign_pack_v2_smoke.py
cd apps/web && npm run typecheck && npm run build && cd ../..
git diff --check -- apps/web/src/App.tsx apps/web/src/JudgeCockpitHome.tsx \
  apps/web/src/FailureAsProofTimeline.tsx apps/web/src/styles.css \
  apps/web/src/JudgeEvidencePack.tsx apps/web/src/judgeEvidencePack.ts
git status --short --branch --untracked-files=all
```

The smoke invokes the PS-030 / PS-029 / PS-028 / PS-027 / PS-026 / PS-025 /
PS-024 / PS-023 regressions internally under byte-snapshot / restore
protection plus `--assume-unchanged` index handling for the tracked
unlink-prone evidence (ps-027 / ps-028 / ps-029 / ps-030).

## Smoke result

The PS-031 smoke writes
`docs/evidence/ps-031/export-campaign-pack-v2-smoke.json` with `ok: true`
when every check passes, including:

- `evidence_pack_surface_verified`
- `json_export_available`
- `markdown_export_available`
- `pack_identity_verified`
- `pack_sections_verified`
- `route_map_verified`
- `proof_chain_verified`
- `failure_as_proof_summary_visible`
- `disclosure_notes_visible`
- `truth_boundary_present`
- `limitations_present`
- `source_ps021_evidence` … `source_ps030_evidence`
- `source_implementation_roadmap`
- `frontend_surface_verified`
- `api_surface_verified`
- `no_provider_call`
- `no_broad_b2_read`
- `no_raw_media_byte_claim`
- `no_zip_claim_unless_implemented`
- `no_prior_slice_evidence_modified`
- `public_deployment_pending`

The latest run's `checks` map is in the evidence JSON.

## Limitations

- The pack is generated locally in the browser. It is not signed by a
  server and is not a notarized artifact.
- The pack does not include raw media bytes. The B2 archive content is a
  JSON run archive, not the generated media.
- The pack does not produce a zip export. Zip generation is not implemented
  in PS-031.
- The pack did not fetch and hash the B2 object in the browser. The archive
  SHA-256 is the value recorded by PS-021, not a value the browser
  recomputed.
- The pack does not prove semantic truth, legal authenticity, C2PA
  authenticity, or human authorship.
- The pack does not prove Object Lock or tamper-proof storage.
- The public deployment is not verified. The local contract is verified;
  the public Render deployment remains pending.
- The pack does not include the golden run's live provider / model / attempt
  ledger or raw prompt packet; those are not part of the checked-in
  evidence consumed by this pack.
- Optional low-risk backlinks from B2RehydrateComparison,
  ManifestVerificationPanel, B2EvidenceExplorer, GenblazePipelineGraph, and
  PublicPassportPage were not added in PS-031; the spec marks them optional.
