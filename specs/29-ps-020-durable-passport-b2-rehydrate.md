# PS-020 — Durable Passport / B2 Source-of-Truth Rehydrate

## Goal

Remove PS-019's biggest weakness: public passport links currently depend on in-memory backend state.

PS-020 makes Provenance Passports durable by introducing a B2-backed source-of-truth rehydrate path.

A judge-facing passport URL should not become useless just because the backend restarts.

## Product thesis

ProofStudio is the chain-of-custody layer for AI-generated media.

That only becomes credible if the proof trail survives app memory loss.

PS-020 turns B2 into the durable proof source:

- run identity
- campaign snapshot
- provider attempt ledger
- asset metadata
- manifest reference
- passport evidence
- truth boundary

## Target user-facing behavior

A user or judge opens:

`https://proofstudio-web.onrender.com/passport/<run_id>`

If the run still exists in memory:

- return the normal in-memory passport.

If the run is missing from memory but durable proof exists in B2:

- rehydrate the passport from B2-backed evidence.
- show a clear source label:
  - `in_memory`
  - `b2_rehydrated`
  - `missing`

If neither exists:

- return an honest missing-state response.
- do not fake proof.

## Durable index requirement

A direct `/passport/<run_id>` URL needs a lookup path.

PS-020 should add a durable run index object when durable evidence is written.

Target index concept:

`proofstudio/index/runs/<run_id>.json`

Minimum fields:

- run_id
- campaign_id
- manifest_uri
- passport_uri, if available
- created_at
- proofstudio_schema_version
- source
- truth_boundary

This index lets the API find durable evidence by run_id after memory loss.

## API behavior

Prefer extending the existing passport route instead of adding a new public route:

`GET /runs/{run_id}/passport`

Expected behavior:

1. Try current in-memory store.
2. If found, build current passport as before.
3. If not found and durable lookup is enabled:
   - find B2 index by run_id
   - load durable manifest/passport evidence
   - return a rehydrated passport
4. If not found:
   - return a structured missing response or controlled 404 with clear reason.

## Safety gates

No live provider call by default.

No B2 write unless explicitly running a durable write path.

No B2 read unless explicitly enabled by environment/config or explicit test flag.

No fake media.

No fake manifest verification.

No fake passport.

No secrets in docs, code, or evidence.

## Implementation constraints

PS-020 must inspect existing archive/B2/Genblaze helpers before implementing.

Do not invent a second storage system.

Reuse existing PS-010 archive/rehydrate code where possible.

Keep public frontend behavior honest:

- if passport is rehydrated, show it
- if passport is missing, explain why
- if persistence is not configured, say so
- never present missing evidence as verified

## Frontend requirement

The PS-019 public passport page must show the passport source.

Minimum source states:

- in-memory passport
- B2 rehydrated passport
- missing/unavailable

The page should explain why B2-backed proof matters:

"Proof survives backend restart because B2 is the source of truth."

## Acceptance criteria

PS-020 is accepted only if:

- branch is `ps-020/durable-passport-b2-rehydrate`
- existing archive/B2/Genblaze helper code is inspected before implementation
- durable run index design is documented
- rehydrate behavior is deterministic
- safe default path does not call provider
- safe default path does not write B2
- B2 read/write behavior is explicitly gated
- in-memory passport still works
- missing passport response is honest
- frontend shows passport source state
- local smoke proves missing/in-memory behavior
- live/B2 smoke is only run behind an explicit live flag
- docs and evidence are updated
- frontend build passes
- backend smoke passes
- no secrets

## Winning-project reason

This slice changes ProofStudio from a live demo into a durable proof system.

Without PS-020:

- the passport page is impressive but fragile.

With PS-020:

- B2 becomes the long-term chain-of-custody source.
- the demo story becomes stronger:
  "Even if the app restarts, the proof survives."

## Truth boundary

PS-020 proves durable proof rehydrate behavior.

It does not prove:

- legal authenticity
- C2PA authenticity
- semantic truth of generated media
- human authorship
- paid production reliability
- authentication
- enterprise-grade access control
