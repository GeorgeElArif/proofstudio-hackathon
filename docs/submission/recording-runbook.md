# ProofStudio — Recording Runbook

<!-- PS-018B_CURRENT_PUBLIC_DEPLOYMENT_START -->
## Current public deployment status — PS-018B

PS-018B supersedes the earlier PS-018 pre-deployment state.

- Public app URL: `https://proofstudio-web.onrender.com`
- Public API URL: `https://proofstudio.onrender.com`
- Live URL smoke: passed.
- Public URL verified: true.
- API health/version: verified.
- Frontend load: verified.
- CORS preflight from the deployed frontend origin: verified.
- Safe public dry-run: verified with no provider call and no B2/Genblaze write.

Evidence:

- `docs/ps-018b-render-deployment-public-url-verification-proof.md`
- `docs/evidence/ps-018b/live-url-smoke-summary.json`
- `docs/evidence/ps-018b/live-url-smoke-transcript.json`
- `docs/evidence/ps-018b/safe-public-dry-run-semantic.json`
<!-- PS-018B_CURRENT_PUBLIC_DEPLOYMENT_END -->


Exact commands and on-screen plan for recording the ~3-minute demo. The default
path is **safe** (no provider, no B2, no fake media). The live proof segment is
explicit opt-in only.

> screenshots or video are assumed to already exist — capture them live during a
> recording session.

## Prerequisites

- The ProofStudio repo checked out at `/home/proofstudio-work/proofstudio`.
- A Python virtualenv at `.venv/` with FastAPI/uvicorn/httpx installed.
- Node 24 / npm available for the frontend.
- (Optional, for the live proof segment only) configured provider + B2
  credentials. The default recording never requires these.

## One-click demo helper (safe default)

Run this first to confirm the stack is healthy and to seed a demo campaign +
safe dry-run:

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python scripts/ps015_one_click_local_demo.py
```

The helper prints the Review Room URL, API docs URL, the created campaign id and
run id, and writes a local demo summary/transcript to `/tmp/proofstudio-ps-015/`.
It calls **no live provider and no B2** on the default path.

You can also print this runbook from the helper:

```bash
python scripts/ps015_one_click_local_demo.py --print-runbook
```

## Two-terminal stack (for the on-screen demo)

### Terminal 1 — FastAPI backend

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
uvicorn proofstudio.api.app:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 — Review Room frontend

```bash
cd apps/web
npm run dev -- --host 127.0.0.1 --port 5173
```

## Browser URLs

- **Review Room UI:** http://127.0.0.1:5173
- **Backend health:** http://127.0.0.1:8000/health
- **Backend docs (Swagger):** http://127.0.0.1:8000/docs

## What to show on screen

1. The one-click helper output (Review Room URL, API docs URL, campaign/run ids).
2. The Review Room with the **API Status card** reporting the backend online.
3. A **campaign** (seeded or created in the UI).
4. A **safe dry-run** and its honest no-media / no-manifest state across all
   panels (Attempts, Assets, Manifest, Provenance Passport).
5. The explicit **Live mode** toggle and warning, then **Create Live Proof Run**.
6. The **attempt ledger** (success, or honest failure/block with a sanitized
   reason) and any generated asset metadata / manifest evidence.
7. The **Provenance Passport** (generation summary, manifest verification,
   archive/rehydration, trust boundary, reviewer next actions).
8. Always end on the **Truth Boundary** footer.

## What NOT to show on screen

- Do not show the terminal scrollback of API keys, tokens, or `.env` contents.
- Do not show real presigned B2 URLs that may carry query-string signatures.
- Do not show provider dashboards or billing consoles.
- Do not claim a public/deployed app URL — there is none yet.
- Do not present placeholder images as generated output. The UI never substitutes
  a placeholder for real media; if a live image cannot load, it falls back to
  metadata only.

## Fallback plan if the live provider fails

If the explicit live proof run fails or is blocked:

- Show the honest `live_failed` / `live_blocked` state and the sanitized reason.
- Explain that **failed and skipped attempts are preserved as evidence** in the
  attempt ledger.
- Pivot to the **recorded prior live evidence** from earlier proof slices (see
  [`provider-model-inventory.md`](./provider-model-inventory.md) and
  [`b2-genblaze-usage.md`](./b2-genblaze-usage.md)), which contain real
  manifest hashes and asset SHA-256s from successful runs.
- Never narrate a fake success. The truth boundary is part of the product.

## Fallback plan if the frontend is unavailable

If the Review Room UI cannot start (e.g. Node/npm issue):

- Drive the same product flow through the **FastAPI docs** at
  http://127.0.0.1:8000/docs (Swagger UI) and/or the one-click helper, which
  exercises the full contract in-process (campaign → safe dry-run → readbacks →
  passport).
- Run `python scripts/ps015_one_click_local_demo.py` and show its printed
  summary and the `/tmp/proofstudio-ps-015/` transcript as the demo artifact.
- The backend contract and provenance passport are fully exercisable without the
  browser.

## Final recording checklist

- [ ] `python scripts/ps015_one_click_local_demo.py` ran clean (safe default).
- [ ] Backend reachable at http://127.0.0.1:8000/health.
- [ ] Review Room reachable at http://127.0.0.1:5173; API Status card online.
- [ ] Recorded the safe dry-run + honest no-media state.
- [ ] Recorded the explicit live mode warning + live proof segment (or honest
      failure/block).
- [ ] Recorded the Provenance Passport and the Truth Boundary footer.
- [ ] No secrets, tokens, or signed URLs visible on screen.
- [ ] No public app URL claimed.
- [ ] Final video is about 3 minutes.
