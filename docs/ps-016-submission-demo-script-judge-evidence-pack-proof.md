# PS-016 Submission Demo Script + Judge Evidence Pack — Proof

## Status

**Complete (docs-only + smoke).** PS-016 packages the working local product and
its prior proof slices (PS-001A through PS-015) into a judge-ready submission
evidence pack: a demo video script, an exact recording runbook, a judge evidence
pack, an honest provider/model inventory, a B2 + Genblaze usage doc, a judging
criteria mapping, and a submission checklist — validated by a non-network smoke.

This slice adds **no product features**. It is docs + smoke only. Backend changes
are not allowed for PS-016; none were made.

## Files created

- `docs/submission/README.md` — judge/reviewer entry point.
- `docs/submission/demo-video-script.md` — ~3-minute narrated demo script.
- `docs/submission/recording-runbook.md` — exact commands + on-screen plan.
- `docs/submission/judge-evidence-pack.md` — one-stop judge summary.
- `docs/submission/provider-model-inventory.md` — honest provider/model list.
- `docs/submission/b2-genblaze-usage.md` — B2 + Genblaze usage + proof refs.
- `docs/submission/judging-criteria-mapping.md` — four-criteria mapping.
- `docs/submission/submission-checklist.md` — required/pending items.
- `scripts/ps016_submission_evidence_pack_smoke.py` — submission pack smoke.
- `docs/ps-016-submission-demo-script-judge-evidence-pack-proof.md` — this file.

Allowed modified files:

- `README.md` — added a short submission section pointing at `docs/submission/`.
- `apps/web/README.md` — added a short pointer to the submission pack.

## What the pack covers

- **Product:** ProofStudio, a provenance-aware AI media operations Review Room.
- **Audience:** creator, marketing, agency, and production teams.
- **Problem:** teams lose the evidence trail behind AI-generated media.
- **Demo flow:** safe dry-run → explicit live proof run → evidence → Provenance
  Passport → truth boundary, scripted for ~3 minutes.
- **Setup/run commands:** the one-click helper and the two-terminal stack.
- **Provider/model inventory:** only what is implemented/proven, with blocked
  and optional providers clearly separated.
- **Backblaze B2 usage:** assets, manifests, run archives, rehydrate-from-B2.
- **Genblaze usage:** manifest write/verify as provenance evidence.
- **Judging criteria mapping:** real-world utility, production readiness, B2
  storage/data orchestration, Genblaze use.
- **Evidence and limitations:** grounded in prior proof docs; public deployment,
  persistence, and auth marked pending.

## Source-of-truth assumptions

- All B2/Genblaze/provider claims are drawn from the existing proof docs under
  `docs/` (PS-001A, PS-002, PS-004, PS-005, PS-007, PS-009, PS-010, PS-011, and
  PS-012 through PS-015). Concrete manifest URIs, manifest hashes, and asset
  SHA-256 values are referenced via those docs, not re-invented here.
- Public deployment does not exist; the pack marks it pending and points at the
  local PS-015 one-click demo path.

## Public requirements covered

- Working app URL — documented as **pending**; local Review Room demo is working.
- Repo access — the repository with source, specs, docs, and proof scripts.
- Setup instructions — recording runbook + `apps/web/README.md` + `README.md`.
- Providers/models list — `provider-model-inventory.md`.
- B2 and Genblaze explanation — `b2-genblaze-usage.md`.
- Demo video (~3 minutes) — script ready; recording pending.

## Local proof commands

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"

python -m py_compile scripts/ps016_submission_evidence_pack_smoke.py
python scripts/ps016_submission_evidence_pack_smoke.py

cd apps/web && npm run build
```

The smoke writes:

- `/tmp/proofstudio-ps-016/submission-evidence-pack-summary.json`
- `/tmp/proofstudio-ps-016/submission-evidence-pack-transcript.json`

The smoke makes **no live provider calls and no B2 calls**. It verifies the docs,
the exact commands, the no-invented-evidence rules, the no-secret rule, that the
backend (`src/`) is unchanged, that historical proof scripts are untouched, and
that the frontend production build still passes.

## No fake evidence statement

This pack introduces **no fake evidence**. Specifically it does not invent:

- screenshots or captured image files presented as existing;
- generated asset/media URLs;
- B2 object URLs;
- manifest hashes;
- a public app URL (deployment is marked pending);
- provider/model success for providers that are not actually implemented
  (optional providers are explicitly listed as not implemented).

The smoke scans `docs/submission/*` for these fabricated-artifact patterns and
fails if any are found. The word "fake" itself is not banned — the docs are
allowed to say "no fake evidence."

## Limitations

- Public deployment, production persistence, and authentication are **not** done.
- The default demo path is a safe dry-run; live provider runs are explicit opt-in
  and may fail/block based on credits/quotas.
- Some visual providers are blocked (GMI Cloud credits, Gemini/Imagen quota).
- No screenshots or recorded video exist yet; they must be captured following the
  recording runbook.
- The smoke validates docs/contract/build/source; it does not drive a browser.

## Next milestone recommendation

Deploy the Review Room + FastAPI app behind a stable public URL (the hackathon
"working app URL"), record the ~3-minute demo following the runbook, and add
production persistence (Postgres/SQLite) with the B2 archive as the system of
record. Authentication is a natural follow-on.

## Truth boundary

PS-016 proves ProofStudio has a judge-ready submission evidence pack and demo
script grounded in the current local product and prior proof slices. It does
**not** prove public deployment, final Devpost submission, production
availability, authentication, production persistence, background job reliability,
legal authenticity, C2PA authenticity, semantic truth, or human authorship.
