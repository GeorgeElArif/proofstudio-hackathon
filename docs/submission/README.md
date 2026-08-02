# ProofStudio — Submission Pack

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


This is the **judge-ready submission pack** for ProofStudio. It packages the
working local product and its prior proof slices into a single, reviewable
story: what the product is, who it is for, how to run it, how the demo works,
and how it uses Backblaze B2 and the Genblaze pipeline.

> PS-015 one-click helper and the two-terminal local demo. No public app URL is
> claimed here until one exists. See
> [`submission-checklist.md`](./submission-checklist.md) for what is ready and
> what is still pending.

## Read these in order

1. **[Judge Evidence Pack](./judge-evidence-pack.md)** — the one-stop summary:
   product, audience, problem, workflow, architecture, endpoints, commands,
   proof scripts, B2/Genblaze evidence, limitations.
2. **[Demo Video Script](./demo-video-script.md)** — a ~3-minute narrated demo
   script with an exact timeline (Hook → Product → Safe Demo Setup → Live Proof
   Flow → Provenance Passport → Why It Wins).
3. **[Recording Runbook](./recording-runbook.md)** — exact commands, browser
   URLs, what to show / not show, and fallback plans for recording the demo.
4. **[Provider & Model Inventory](./provider-model-inventory.md)** — only the
   providers/models actually implemented or proven, plus the ones blocked or
   optional.
5. **[B2 + Genblaze Usage](./b2-genblaze-usage.md)** — how Backblaze B2 and the
   Genblaze pipeline are used for storage, manifests, archive/rehydrate, and
   provenance evidence, with prior proof-slice references.
6. **[Judging Criteria Mapping](./judging-criteria-mapping.md)** — how
   ProofStudio maps to real-world utility, production readiness, B2 storage/data
   orchestration, and Genblaze use.
7. **[Submission Checklist](./submission-checklist.md)** — required submission
   items, local proof already available, and what is still pending.

## Quick start (local, safe)

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python scripts/ps015_one_click_local_demo.py
```

This seeds a demo campaign and a **safe dry-run** (no provider, no B2, no fake
media). The full two-terminal Review Room demo is in the
[Recording Runbook](./recording-runbook.md).

## Truth boundary

This pack proves ProofStudio has a judge-ready submission evidence pack and demo
script grounded in the current local product and prior proof slices
(PS-001A through PS-015). It does **not** prove public deployment, production
availability, authentication, production persistence, background job
reliability, legal authenticity, C2PA authenticity, semantic truth, or human
authorship.
