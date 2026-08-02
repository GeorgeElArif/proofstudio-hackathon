# Winning Demo Acceptance Spec

## 1. Demo Goal

The final demo must prove that ProofStudio is a real AI media operations system, not a thin wrapper around one model.

The judge should understand:

- what problem exists
- why single-provider AI media workflows are fragile
- how ProofStudio handles provider failure
- how B2 acts as the system of record
- how Genblaze verifies the workflow artifacts
- how teams review and export a verified media kit

## 2. Required Demo Story

The demo should show:

1. Open ProofStudio dashboard.
2. Create or load a campaign brief.
3. Generate campaign intelligence.
4. Show Gemini-generated prompt pack.
5. Start visual generation.
6. Show Provider Router attempts.
7. Show at least one failed/skipped provider and one successful provider.
8. Store output in B2.
9. Verify Genblaze manifest.
10. Open Provenance Passport.
11. Review asset.
12. Export campaign pack.
13. Rehydrate campaign or show B2-backed source of truth.

## 3. Required Screens

The final UI must include:

- Dashboard
- Campaign Brief
- Mission Control / Flight Recorder
- Model Audition Board
- Asset Detail / Provenance Passport
- Review Room
- Export Pack
- optional Rehydrate view

## 4. Required Proof Artifacts

The demo must show or reference:

- B2 object URL or object reference
- manifest URI
- manifest hash
- asset SHA-256
- provider attempt ledger
- prompt packet
- export pack
- truth boundary note

## 5. Required Out-of-Box Moments

At least four of these must be visible:

- Failure-as-Proof Timeline
- Why This Provider?
- Model Audition Board
- Provenance Passport
- Manifest Diff
- Provider Swap Re-run
- Cost Ledger
- Rehydrate from B2
- Disclosure Readiness Layer

## 6. Submission Truth Boundaries

The demo may claim:

- ProofStudio records workflow history.
- ProofStudio stores artifacts in B2.
- ProofStudio verifies byte-level integrity with hashes/manifests.
- ProofStudio shows provider attempts and fallback behavior.
- ProofStudio can export a campaign pack with provenance notes.

The demo must not claim:

- ProofStudio proves semantic truth.
- ProofStudio proves legal authenticity.
- ProofStudio proves human authorship.
- ProofStudio provides C2PA authenticity unless C2PA is implemented and verified.
- Blocked providers generated assets.
- Paid providers worked if they did not.

## 7. Winning Bar

A submission-ready demo must satisfy:

- one full campaign flow works
- one generated or fallback visual asset exists
- asset is stored in B2
- Genblaze manifest verifies
- provider attempt ledger exists
- at least one fallback is visible
- export pack exists
- UI is polished enough for screenshots
- demo video can be recorded in under 3 minutes
- repo can be understood by judges

## 8. Current Gap List

Still needed:

- Provider Router implementation
- Cloudflare Workers AI provider proof
- Pollinations fallback proof
- FastAPI backend
- Next.js frontend
- campaign state model
- Mission Control UI
- Provenance Passport UI
- Model Audition Board UI
- Review Room UI
- Export Pack generation
- Rehydrate from B2
- final README
- final architecture diagram
- final Devpost writeup
- final demo video

## 9. Commit Gate For Future Slices

No slice can be accepted unless:

- code compiles
- tests or smoke command pass
- no secrets are committed
- working tree is clean after commit
- acceptance criteria are met
- failures are documented honestly
- B2/Genblaze claims are backed by actual run output
