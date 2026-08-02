# PS-021 — Live B2 Durable Rehydrate Proof

## Status

Planned.

## Goal

Prove that a public ProofStudio Provenance Passport can be restored from a real Backblaze B2 archive after backend memory loss.

PS-020 proved the durable rehydrate foundation using a local inline archive index.

PS-021 must prove the same durable passport recovery path using a real B2 archive read, behind explicit gates.

## Product meaning

ProofStudio is not only generating media.

ProofStudio is preserving the chain of custody for AI media.

A judge should understand that a public passport is not dependent on temporary backend memory. It can be restored from archived evidence in B2.

## Hard safety boundaries

PS-021 must not fake B2 proof.

PS-021 must not fake provider output.

PS-021 must not call a media provider.

PS-021 must not create new generated media.

PS-021 must not enable B2 reads by default.

PS-021 must not make public passport recovery depend on hidden in-memory state.

PS-021 may read from B2 only when the explicit live B2 rehydrate gate is enabled.

## Required gates

The following must be false by default:

- PROOFSTUDIO_DURABLE_PASSPORT_READ_ENABLED
- PROOFSTUDIO_DURABLE_PASSPORT_B2_READ_ENABLED

A live B2 rehydrate smoke may run only when both gates are explicitly enabled.

## Required proof

The PS-021 evidence must show:

- A run archive is stored in B2.
- A durable passport index points to the B2 archive URI.
- Backend memory is cleared.
- Passport request fails or is unavailable when durable read gates are disabled.
- Passport request succeeds when durable read and B2 read gates are enabled.
- Rehydrate source is `b2_rehydrated`.
- Rehydrate completed is true.
- Provider calls made during rehydrate are zero.
- B2 read is true.
- B2 write is limited to archive/index evidence only.
- No generated media write occurs during rehydrate.

## Expected implementation shape

Prefer extending the existing PS-020 durable passport module.

Use existing archive and Genblaze/B2 helpers where possible.

Do not duplicate B2 client logic unless the existing helper surface is insufficient.

Expected files may include:

- src/proofstudio/api/durable_passport.py
- src/proofstudio/api/services.py
- scripts or docs evidence helpers if needed
- docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json
- docs/ps-021-live-b2-durable-rehydrate-proof.md

## Frontend requirement

The existing public passport Durable proof source panel should display B2 rehydrated proof honestly when the API returns it.

No major frontend redesign is required.

## Acceptance criteria

PS-021 is accepted only if:

- Backend compile passes.
- Frontend build passes.
- Diff check passes.
- Live B2 durable rehydrate smoke passes with explicit gates.
- Evidence JSON is committed.
- Proof doc is committed.
- Worktree is clean after commit.
- Branch is pushed and remote SHA verified.

## Non-goals

Do not add auth.

Do not redesign the app.

Do not change provider routing.

Do not create new generated assets.

Do not claim production-grade persistence beyond the proven B2 archive/index behavior.

Do not merge PS-022 through PS-025 into this slice.

## Next after PS-021

After PS-021, collapse PS-022 through PS-025 into one Final Submission Readiness Epic instead of continuing slow slice-by-slice execution.
