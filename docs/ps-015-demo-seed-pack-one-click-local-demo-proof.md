# PS-015 Demo Seed Pack + One-Click Local Demo — Proof

## Status

**Complete (safe default path).** PS-015 adds a repeatable, safe local demo layer
on top of PS-014: a deterministic demo seed pack and a one-click helper that
seeds a demo campaign, creates a safe dry-run, proves the default path calls no
live provider and no B2, and prints the Review Room + API docs URLs. Default
acceptance never requires live provider spend.

## Files added by this slice

- Seed pack: `examples/ps015/demo-seed-pack.json`
- One-click helper: `scripts/ps015_one_click_local_demo.py`
- Smoke: `scripts/ps015_demo_seed_pack_one_click_smoke.py`
- This proof doc: `docs/ps-015-demo-seed-pack-one-click-local-demo-proof.md`

No backend files were changed. Historical proof scripts (PS-004 .. PS-014) were
not modified.

## Seed pack

- Path: `examples/ps015/demo-seed-pack.json`
- Holds deterministic demo inputs only. It carries `slice`, `demo_name`,
  `campaign` (name, brief, audience, channels, tone, creative_constraints),
  `safe_run` (`run_live: false`), `optional_live_run`
  (`run_live: true`, `requires_explicit_opt_in: true`), an ordered
  `reviewer_script`, a `truth_boundary`, and `created_for`.
- It contains **no fake image URLs, no fake manifest URIs, no fake B2 URLs, no
  fake hashes, no fake provider/model claims, and no secrets.**

## One-click helper

- Path: `scripts/ps015_one_click_local_demo.py`

### Safe default behavior

1. Confirms it is running inside the ProofStudio repo.
2. Confirms Python imports work with the `src` layout.
3. Loads `examples/ps015/demo-seed-pack.json`.
4. Imports the FastAPI app (`proofstudio.api.app:app`).
5. Uses `TestClient` to create a demo campaign from the seed pack.
6. Creates a safe dry-run with `run_live=false`.
7. Fetches run / attempts / assets / manifest / passport.
8. Confirms the default path called no live provider (sentinel on
   `services.execute_live_run`).
9. Confirms the default path called no B2 (sentinels on
   `archive.store_run_archive_with_genblaze` and `archive.read_archive_from_b2`).
10. Writes `/tmp/proofstudio-ps-015/one-click-local-demo-summary.json`.
11. Writes `/tmp/proofstudio-ps-015/one-click-local-demo-transcript.json`.
12. Prints the Review Room URL, API docs URL, backend command, frontend command,
    created campaign id, created run id, summary path, and transcript path.

## Exact default command

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python scripts/ps015_one_click_local_demo.py
```

This runs the safe default (no provider, no B2, no fake media, no fake manifest).

The smoke equivalent:

```bash
python scripts/ps015_demo_seed_pack_one_click_smoke.py
```

## Optional live command (explicit opt-in only)

Live mode is **never** the default. It is enabled only with an explicit flag or
environment variable:

```bash
PROOFSTUDIO_PS015_LIVE=1 python scripts/ps015_one_click_local_demo.py
# or
python scripts/ps015_one_click_local_demo.py --live
```

When live mode is enabled:

- a clear warning is printed: **Live mode may call external providers and B2.**
- the helper creates a `run_live=true` run against the real provider/B2 chain
- it records whether the live run completed / failed / blocked
- it never fakes success, never fakes media, and never fakes a manifest

Default acceptance never requires live provider spend.

## Exact two-terminal manual fallback

If you prefer to drive the Review Room by hand instead of the one-click helper:

### Terminal 1 — FastAPI backend

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
uvicorn proofstudio.api.app:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 — Review Room frontend

```bash
cd /home/proofstudio-work/proofstudio/apps/web
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

### Open

- Review Room: http://127.0.0.1:5173
- API health: http://127.0.0.1:8000/health
- API docs (Swagger): http://127.0.0.1:8000/docs

### Demo sequence

1. Confirm the API Status card reports the backend online.
2. Create a campaign (or use the seeded campaign id from the one-click helper).
3. Click **Create Safe Dry Run** and inspect the honest no-media state.
4. Inspect attempts / assets / manifest / passport panels.
5. Optionally enable Live mode (explicit opt-in) and click **Create Live Proof
   Run**; show live evidence or an honest failure/block.
6. Always end on the Truth Boundary footer.

You can also print this runbook directly:

```bash
python scripts/ps015_one_click_local_demo.py --print-runbook
```

Other optional helper flags:

- `--check-ports` — report whether the backend/frontend ports are in use
- `--serve` — start backend + frontend locally (safe; never live by default)

## Generated summary and transcript

One-click helper writes:

- `/tmp/proofstudio-ps-015/one-click-local-demo-summary.json`
- `/tmp/proofstudio-ps-015/one-click-local-demo-transcript.json`

Smoke writes:

- `/tmp/proofstudio-ps-015/demo-seed-pack-one-click-summary.json`
- `/tmp/proofstudio-ps-015/demo-seed-pack-one-click-transcript.json`

## Default no-provider / no-B2 proof

The default (safe dry-run) path installs sentinels over
`proofstudio.api.services.execute_live_run`,
`proofstudio.api.archive.store_run_archive_with_genblaze`, and
`proofstudio.api.archive.read_archive_from_b2` before creating the run. If the
default path were ever to reach a live provider or B2, the sentinel raises and
the demo fails loudly. The default smoke asserts the provider call count and the
B2 call count are both `0`. This is recorded in the summary fields:

- `default_no_live_provider_call: true`
- `default_no_b2_call: true`

## No-fake-evidence proof

- The seed pack is scanned for fake image URLs, fake manifest URIs, fake B2
  URLs, sha256-length fake hashes, and fake provider/model claims; none are
  present.
- The default dry-run produces zero assets, a manifest that reports
  `ready: false`, and a passport that reports `generated_media_present: false`.
- The helper never fabricates media or a manifest; it records the honest
  no-media / no-manifest state and the sentinel proof above.
- The smoke asserts `no_fake_media` and `no_fake_manifest` are both true.

## Demo recording checklist

- [ ] Run `python scripts/ps015_one_click_local_demo.py` and capture the printed
      Review Room + API docs URLs, campaign id, run id, and summary path.
- [ ] Start the two-terminal stack (or `--serve`) and open the Review Room.
- [ ] Show the API Status card reporting the backend online.
- [ ] Create a campaign / safe dry-run in the UI and narrate the honest
      no-media / no-manifest state.
- [ ] Walk through Attempt Timeline → Assets → Manifest → Provenance Passport.
- [ ] (Optional) Enable live mode explicitly and run a live proof; show the live
      evidence or an honest failure/block.
- [ ] End on the Truth Boundary footer.

## Limitations

- The helper uses the FastAPI `TestClient` in-process for the default path; it
  does not require a running uvicorn server for the safe dry-run.
- `--serve` starts local processes but is a convenience, not a production
  process manager.
- Live mode depends on real provider/B2 credentials being configured; without
  them a live run will honestly fail or block.
- No backend changes were made; all existing PS-012 contracts are preserved.

## Next milestone recommendation

PS-016: package the local demo into a single shareable artifact (e.g. a
deterministic demo bundle / one-click launcher with recorded transcript
export), and add an optional recorded-demo replay path that rehydrates a real
archive into the Review Room so reviewers can inspect completed evidence
without a live provider call.

## Truth Boundary

PS-015 proves ProofStudio has a deterministic local demo seed pack and a safe
one-click helper for preparing a local Review Room demo. It does **not** prove
public deployment, production availability, authentication, production
persistence, background job reliability, legal authenticity, C2PA authenticity,
semantic truth, or human authorship.
