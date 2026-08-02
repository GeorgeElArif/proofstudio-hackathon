# PS-019 — Public Provenance Passport Share Page + Proof Score

## Goal

Turn ProofStudio from a proof-heavy demo into a judge-facing product moment.

PS-019 adds a public, shareable Provenance Passport page and a human-readable Proof Score so judges and future users can understand asset trust without reading JSON.

## Product thesis

ProofStudio is not just an AI media generator.

It is the chain-of-custody layer for AI-generated media:

- what was requested
- which provider/model was used
- what failed
- what fallback happened
- where the asset/proof is stored
- whether the evidence is complete
- whether the final asset can be trusted

## Public share page

Add a public route in the frontend:

- `/passport/:runId`

The page must work from the deployed Render frontend.

Minimum page content:

- ProofStudio public header
- run id
- campaign id
- status
- proof score
- trust badge
- prompt
- provider/model
- fallback status
- attempt count
- asset count
- manifest status
- B2/Genblaze proof status
- links back to Review Room context when available
- clear truth boundary

## Proof Score

Add a deterministic score from 0 to 100.

Initial scoring model:

- +15 run exists
- +10 campaign id exists
- +10 prompt exists
- +10 dry_run or run_live value explicitly known
- +10 selected provider/model known when live, or explicitly null when dry-run
- +10 attempts ledger is present or explicitly empty for dry-run
- +10 asset list is present or explicitly empty for dry-run
- +10 manifest field is present, even if null for dry-run
- +10 fallback status known
- +5 truth boundary / safety note present

Badge mapping:

- 90–100: Verified
- 70–89: Mostly verified
- 40–69: Partial evidence
- 0–39: Weak evidence

Dry-run can still score high if it honestly proves no provider call and no B2 write.

## API requirements

Prefer existing API routes first.

Use current endpoints if already sufficient:

- `/runs/{run_id}`
- `/runs/{run_id}/passport`
- `/runs/{run_id}/attempts`
- `/runs/{run_id}/assets`
- `/runs/{run_id}/manifest`

If missing, add only the minimal backend route needed.

No provider call by default.

No B2 write by default.

No fake media.

## Frontend requirements

The page must be polished enough for a judge:

- clear trust badge
- proof score card
- attempt/fallback timeline
- storage/provenance panel
- readable empty states
- responsive layout
- no raw JSON wall as the primary UI

## Demo requirement

A judge should be able to open a URL like:

`https://proofstudio-web.onrender.com/passport/<run_id>`

and understand the asset/run evidence in under 10 seconds.

## Acceptance criteria

PS-019 is accepted only if:

- branch is `ps-019/public-passport-proof-score`
- public passport route exists
- proof score is deterministic
- safe dry-run passport works
- live/provenance passport path uses real stored evidence when available
- frontend build passes
- backend smoke passes if backend code changes
- no provider call by default
- no B2 write by default
- no fake media
- no secrets
- docs updated with demo URL pattern and truth boundary

## Truth boundary

PS-019 proves a judge-facing public passport and trust score UI.

It does not prove:

- legal authenticity
- C2PA authenticity
- semantic truth of generated media
- human authorship
- paid production reliability
- authentication
- production database persistence
