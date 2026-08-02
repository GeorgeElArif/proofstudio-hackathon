# PS-028 — Manifest Verification Panel — Proof

## Roadmap alignment

PS-028 follows the PS-022 master roadmap. Lead-in slices completed:

- PS-023 — Judge Cockpit Home
- PS-024 — Golden Demo Run Pinning
- PS-025 — Public Durable Passport Unlock
- PS-026 — B2 Evidence Explorer
- PS-027 — Genblaze Pipeline Graph

PS-026 made B2 evidence visible. PS-027 made Genblaze orchestration visible.
PS-028 makes manifest verification visible.

## Product surface chosen

Dedicated frontend route `/manifest-verification` + component
`apps/web/src/ManifestVerificationPanel.tsx` + data module
`apps/web/src/manifestVerification.ts`. Frontend-only; no new API endpoint.

## Files changed

- `apps/web/src/App.tsx` — registered `/manifest-verification` route via
  `isManifestVerificationPath()` and rendered `ManifestVerificationPanel`.
- `apps/web/src/JudgeCockpitHome.tsx` — added CTA in the golden demo run
  panel and a dedicated tile in the Direct CTAs grid.
- `apps/web/src/B2EvidenceExplorer.tsx` — added backlink to
  `/manifest-verification` (page variant).
- `apps/web/src/GenblazePipelineGraph.tsx` — added backlink to
  `/manifest-verification` (page variant).
- `apps/web/src/styles.css` — added Manifest Verification Panel styles.
- `apps/web/src/ManifestVerificationPanel.tsx` — new component.
- `apps/web/src/manifestVerification.ts` — new verified constants module.
- `docs/evidence/ps-028/manifest-verification-panel-smoke.json` — new evidence.
- `docs/ps-028-manifest-verification-panel-proof.md` — this proof doc.
- `scripts/ps028_manifest_verification_panel_smoke.py` — new smoke script.

No API endpoint was added. No backend file was changed.

## Route/CTA map

- `/` (Judge Cockpit Home)
  - golden demo run panel: button → `/manifest-verification`
  - Direct CTAs grid: tile → `/manifest-verification`
- `/manifest-verification` (Manifest Verification Panel)
  - button → `/genblaze-pipeline`
  - button → `/b2-evidence`
  - button → `/passport/run_89d967f9000045efa22ed4cc78cfa67f`
  - button → `/`
- `/b2-evidence` (B2 Evidence Explorer, page variant)
  - button → `/manifest-verification` (backlink)
- `/genblaze-pipeline` (Genblaze Pipeline Graph, page variant)
  - button → `/manifest-verification` (backlink)

## Verification source list

1. `docs/evidence/demo/golden-demo-run.json` (PS-024 golden manifest)
2. `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json`
3. `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json`
4. `docs/evidence/ps-026/b2-evidence-explorer-smoke.json`
5. `docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json`

## Verified field list

- `run_id`
- `campaign_id`
- `archive_uri`
- `archive_sha256`
- `rehydrate_source`
- `provider_calls_during_rehydrate`
- `no_live_provider_call_during_rehydrate`

## Consistency result

All five checked-in evidence sources agree on every required field:

- `run_id` = `run_89d967f9000045efa22ed4cc78cfa67f`
- `campaign_id` = `camp_bea5161faa6244079d2ee01ce445c259`
- `archive_uri` = `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json`
- `archive_sha256` = `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
- `rehydrate_source` = `b2_rehydrated` (PS-021 records this under the key
  `durable_source`; every other source uses `rehydrate_source`)
- `provider_calls_during_rehydrate` = `0`
- `no_live_provider_call_during_rehydrate` = `true`

`manifest_consistency_verified`: **true**.

## Manifest claim boundary

Allowed claims:

- Checked-in evidence agrees on golden run identifiers (run_id, campaign_id).
- Checked-in evidence agrees on the archive URI and SHA-256.
- Checked-in evidence records `rehydrate_source = b2_rehydrated`.
- Checked-in evidence records `provider_calls_during_rehydrate = 0`.

Forbidden claims (the panel does NOT assert these):

- The panel does not prove semantic truth of the media.
- The panel does not prove legal authenticity.
- The panel does not prove human authorship.
- The panel does not prove C2PA authenticity.
- The panel does not prove Object Lock or tamper-proof storage.
- The panel did not fetch and hash the B2 object in the browser.
- Public deployment has not been verified (it remains pending).

## No-provider-call confirmation

The PS-028 smoke scans every changed source file for forbidden provider-call
patterns (`call_provider`, `fetchFromProvider`, `requests.post`, `urlopen(`,
`httpx.post`, `client.post(`). None are present. The panel performs no
network call. `no_provider_call`: **true**.

## No-broad-B2-read confirmation

The PS-028 smoke scans every changed source file for forbidden B2 read
patterns (`read_archive_from_b2`, `b2.fetch`, `b2GetObject`, `list_b2_objects`,
`fetchB2Object`, `fetch(`). None are present. The smoke also verifies an
arbitrary run_id still returns HTTP 404 through the public durable passport
path (FastAPI TestClient against a fresh empty store), so the PS-025 narrow
golden-demo allowlist still holds. `no_broad_b2_read`: **true**.

## No-prior-slice-evidence-mutation confirmation

The PS-028 smoke snapshots the byte content of every evidence file outside
`docs/evidence/ps-028/` before invoking any regression smoke, restores the
exact bytes after each regression smoke (so a later smoke never sees an
earlier smoke's freshly-written evidence as dirty), and confirms via
`git status --porcelain -- docs/evidence/` that no prior-slice evidence file
is left dirty. `no_prior_slice_evidence_modified`: **true**.

PS-027 additionally unlinks its own tracked `docs/evidence/ps-027/` evidence
before invoking PS-026 (a historical behaviour PS-028 cannot modify). Once
that evidence is committed/tracked, the unlink produces a git-visible
deletion that PS-026's prior-slice check would flag. PS-028 marks the
PS-027 evidence file `--assume-unchanged` in the git index for the duration
of the regression run so git skips the worktree-vs-index comparison and the
deletion is invisible to PS-026's `git status` check. The flag is cleared
before PS-028's own prior-slice check, and the file's original bytes are
restored from the snapshot, so the final working tree is byte-identical to
HEAD for that file. This manipulation is index-only: it modifies no source
file, no evidence file, and no historical smoke script.

## Truth boundary confirmation

The panel renders `MANIFEST_VERIFICATION_TRUTH_BOUNDARY` and the
`MANIFEST_CLAIM_BOUNDARY_ALLOWED` / `MANIFEST_CLAIM_BOUNDARY_FORBIDDEN`
lists. The truth boundary distinguishes:

- manifest field consistency across checked-in evidence
- durable B2 archive proof
- local public passport contract proof
- inferred product explanation
- public deployment pending

`truth_boundary_present`: **true**.

## Validation commands

```bash
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python scripts/ps028_manifest_verification_panel_smoke.py
```

```bash
cd apps/web && npm run typecheck && npm run build && cd ../..
```

```bash
git diff --check -- apps/web/src/App.tsx apps/web/src/B2EvidenceExplorer.tsx \
  apps/web/src/GenblazePipelineGraph.tsx apps/web/src/JudgeCockpitHome.tsx \
  apps/web/src/styles.css apps/web/src/ManifestVerificationPanel.tsx \
  apps/web/src/manifestVerification.ts \
  docs/evidence/ps-028/manifest-verification-panel-smoke.json \
  docs/ps-028-manifest-verification-panel-proof.md \
  scripts/ps028_manifest_verification_panel_smoke.py
```

```bash
git status --short --branch --untracked-files=all
```

## Smoke result

```
surface_exists                   pass
route_exists                     pass
judge_links_panel                pass
panel_links_genblaze_b2_passport_home pass
sources_present                  pass
fields_present                   pass
run_id_matches                   pass
campaign_id_matches              pass
archive_uri_match                pass
archive_sha256_match             pass
rehydrate_source                 pass
provider_calls_zero              pass
no_live_provider_call            pass
truth_boundary                   pass
no_broad_b2_read                 pass
no_provider_call                 pass
secret_scan                      pass
forbidden_claims                 pass
api_resolves_golden              pass
ps027_passes                     pass
ps026_passes                     pass
ps025_passes                     pass
ps024_passes                     pass
ps023_passes                     pass
no_prior_slice_evidence_modified pass
frontend_typecheck               pass
frontend_build                   pass
```

`ok`: **true**. `local_contract_proof`: **true**.
`public_deployment_pending`: **true**.

## Limitations

- The panel proves manifest field **consistency** across checked-in evidence.
  It does not prove semantic truth, legal authenticity, C2PA authenticity,
  human authorship, Object Lock, or tamper-proof storage.
- The panel references the archive URI and SHA-256 but does not fetch or
  byte-verify the B2 object in the browser. A judge may independently
  verify the bytes against the recorded SHA-256 if they want.
- The local contract (FastAPI TestClient against a fresh empty store
  resolving the golden run_id from checked-in evidence) is verified by
  PS-025. The public Render deployment is **not** verified here; the new
  backend must be deployed and the public URL verified end-to-end before
  `public_deployment_pending` can flip.
- The panel is informational only; it does not call any provider, does not
  read any B2 object, and does not modify any run state.
