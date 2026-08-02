# ProofStudio Winning Implementation Roadmap

Current as of: 2026-06-29
PS-034C reconciliation applied: 2026-07-01

## PS-034C Roadmap Conflict Resolution (Authoritative)

This roadmap previously conflicted with the PS-031A hardened product-modules
correction over what PS-035 means. Earlier prose in this document called
PS-035 the "Disclosure Readiness Layer", while the PS-031A correction called
PS-035 the "Review + Approval Workspace". PS-034C resolves this with one
authoritative identity:

- The PS-031A correction (`docs/roadmap/ps-031a-hardened-product-modules-correction.md`)
  remains authoritative unless later superseded.
- PS-035 is Review + Approval Workspace.
- Disclosure becomes PS-037 — Disclosure + Trust Boundary Layer.
- PS-035 remains blocked until PS-034C is accepted.
- PS-035a (Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest
  Correctness) should be the next implementation slice unless the PM later
  changes priority.

The conflicting section headings below (PS-035 — Disclosure Readiness Layer
and PS-037 — Review Room Comments + Approval Ledger) are superseded by this
reconciliation and by the post-PS-034C roadmap ledger in
`specs/08-roadmap-slices.md` Wave 8. They are retained for history, but their
numbering is no longer authoritative. The authoritative post-PS-034C ordering
is:

- PS-034C — Winning Roadmap + Master Spec Replan
- PS-035 — Review + Approval Workspace
- PS-035a — Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest
  Correctness (blocking)
- PS-035b — Cost Caps + Golden-Fixture Governance
- PS-036 — Archive / Rehydrate / B2 Audit Vault
- PS-037 — Disclosure + Trust Boundary Layer
- PS-037a — Multimodal Proof Layer
- PS-037b — AssemblyAI Transcript/Timestamp Evidence
- PS-037c — Hume or ElevenLabs Voiceover Artifact
- PS-037d — Gemini Campaign Intelligence / Judge Narrative
- PS-037e — Cloudflare Low-Cost Backbone
- PS-038 — Production Readiness + Demo Mode
- PS-038a — Campaign Proof Room (marquee)
- PS-039 — Final Submission Pack
- PS-039a — Devpost Submission Package + 3-Minute Demo Script
- PS-040 — Product Dashboard + Marketing Website (delayed/optional)
- PS-041 through PS-043 — reserve hardening / stretch / fix slices

No accepted built slice PS-023 through PS-034B is dropped by this replan.

## PM Decision

The old-window out-of-the-box ideas are not being preserved as notes.

They are now implementation commitments.

Every major idea must become a real product slice with:

- user-facing surface or API behavior
- evidence contract
- smoke script
- proof doc
- truth boundary
- no fake proof
- no overclaiming

## Product Identity

ProofStudio is not another AI image generator.

ProofStudio is an AI media operations cockpit.

It proves the production workflow behind AI media:

Brief
-> Provider Router
-> Provider / model attempts
-> Failure / fallback ledger
-> Generated asset
-> Backblaze B2 archive
-> Genblaze manifest
-> Provenance Passport
-> Manifest Verification
-> B2 Rehydrate
-> Review
-> Export / Judge Evidence Pack

## Winning Standard

A hackathon-winning ProofStudio must feel like a real working product, not a shallow MVP.

Required qualities:

- judges can understand the product without reading raw JSON
- developers can run it locally
- the app has a reliable golden path
- B2 is the durable system of record
- Genblaze manifests are central to proof
- provider routing and fallback are visible
- rehydrate works without provider rerun for the verified golden run
- evidence surfaces link together
- exports/review/disclosure feel operational
- limitations are explicit
- nothing is faked

## Truth Boundary

ProofStudio proves what the pipeline did.

It does not prove:

- semantic truth
- legal authenticity
- human authorship
- C2PA authenticity unless implemented
- Object Lock / tamper-proof storage unless implemented
- enterprise security unless implemented
- public deployment success unless verified
- browser-side B2 byte verification unless implemented

## Old-Window Ideas — Implementation Commitments

### 1. Provenance Passport

Status:

Partially implemented through current passport/public passport work.

Must continue toward a full passport that includes:

- campaign identity
- run identity
- prompt packet
- provider/model
- params
- attempt ledger
- selected asset
- rejected/failed/skipped attempts when present
- asset hashes
- B2 object keys / URIs
- Genblaze manifest URI
- archive URI
- archive SHA-256
- rehydrate proof
- review state
- disclosure recommendation
- truth boundary
- public verification link when available

Implementation commitment:

Extend in later slices through Review Room, Export Pack, Disclosure Layer, and Final Submission Pack.

### 2. Mission Control / Flight Recorder

Status:

Partially covered by Judge Cockpit and Genblaze Pipeline Graph.

Must become a real operations cockpit.

Implementation commitment:

PS-032 — Mission Control / Flight Recorder v2.

Must include:

- brief
- routing
- attempt status
- skipped/failed/disabled/fallback states if present
- B2 storage
- manifest write
- passport creation
- verification surfaces
- future pipeline.jsonl model

### 3. Model Audition Arena

Status:

Not yet implemented.

Implementation commitment:

PS-033 — Model Audition Arena.

Must include:

- provider/model candidates
- status
- latency
- known/unknown cost
- selected/rejected state
- linked evidence
- no fake provider candidates

### 4. Rehydrate From B2

Status:

Implemented as proof through PS-021 and surfaced through PS-029.

Implementation commitment:

Continue to use as a core winning proof spine in Export Pack, Audit Pack, and Final Submission.

Required proof fields:

- rehydrate_source = b2_rehydrated
- provider_calls_during_rehydrate = 0
- no_live_provider_call_during_rehydrate = true

### 5. Review Room With Proof

Status:

Basic Review Room existed earlier, but not enough as final product.

Implementation commitment:

PS-037 — Review Room Comments + Approval Ledger.

Must include:

- approve/reject
- reviewer notes
- audit trail
- linked passport
- linked manifest verification
- linked B2 archive
- export readiness

### 6. Export Campaign Pack / Judge Evidence Pack

Status:

Not yet implemented enough.

Implementation commitment:

PS-031 — Export Campaign Pack v2 / Judge Evidence Pack.

Must include:

- final asset summary
- prompt packet
- provider note
- attempt ledger
- manifest summary
- passport JSON
- B2 archive proof
- rehydrate proof
- disclosure notes
- limitations
- judge/client README

### 7. Disclosure Readiness Layer

Status:

Not yet implemented enough.

Implementation commitment:

PS-035 — Disclosure Readiness Layer.

Must include:

- plain-language disclosure notes
- channel-ready copy
- known facts
- unknown facts
- non-claimed facts
- not legal advice
- no C2PA claim unless implemented

### 8. Credit-Aware Provider Router

Status:

Router exists, credit-aware explanation not enough.

Implementation commitment:

PS-036 — Credit / Cost / Why This Provider.

Must include:

- budget mode
- provider availability
- known/unknown cost
- quota risk
- why provider was selected
- fallback policy explanation

### 9. Provider Budget Modes

Status:

Not fully productized.

Implementation commitment:

PS-036.

Budget modes:

- free-only
- balanced
- quality-first
- fastest
- fallback-only
- demo-safe

### 10. Cost and Time Ledger

Status:

Not yet implemented enough.

Implementation commitment:

PS-036.

Must show:

- estimated cost
- known/unknown cost state
- provider credit risk
- latency
- storage footprint
- export pack size where available

### 11. Failure-as-Proof Timeline

Status:

Next slice.

Implementation commitment:

PS-030 — Failure-as-Proof Timeline.

Must include:

- evidence-backed timeline
- Failure-as-Proof section
- no-provider-rerun proof
- where real failures/retries/fallbacks would appear
- no fake actual failure claims

### 12. Manifest Diff

Status:

Not yet implemented.

Implementation commitment:

PS-034 — Variant Family Tree + Manifest Diff.

Must include:

- changed prompt
- changed provider/model
- changed params
- changed asset hash
- changed B2 URI
- changed manifest URI
- changed review/export state

### 13. Provider Swap Re-run

Status:

Not yet implemented.

Implementation commitment:

PS-039 — Provider Swap Re-run.

Must include:

- original run
- swapped provider/model run
- manifest comparison
- lineage
- no fake provider calls

### 14. Why This Provider?

Status:

Not yet implemented enough.

Implementation commitment:

PS-036.

Must explain provider choice based on:

- availability
- budget mode
- output compatibility
- fallback policy
- quota risk
- disabled/blocked provider status if present

### 15. Proof View / Audit Pack

Status:

Partially covered through current evidence surfaces.

Implementation commitment:

PS-031 and PS-043.

Must include:

- compressed judge/client proof chain
- run identity
- provider/model
- attempt ledger
- B2 archive
- Genblaze manifest
- passport
- manifest verification
- rehydrate comparison
- review state
- disclosure
- export pack

### 16. Emergency No-Key Mode

Status:

Implemented earlier through Pollinations fallback.

Implementation commitment:

Keep it visible and honest in router/provider surfaces.

Must be labeled:

Emergency no-key fallback.

Not equivalent to paid/provider production mode.

Never faked.

## Added PM Out-of-the-Box Ideas — Implementation Commitments

### 17. B2 Audit Vault

Implementation commitment:

PS-038 — B2 Audit Vault.

Must define and surface an audit-ready B2 layout:

campaigns/{campaign_id}/approved/{run_id}/asset.*
campaigns/{campaign_id}/approved/{run_id}/manifest.json
campaigns/{campaign_id}/approved/{run_id}/passport.json
campaigns/{campaign_id}/approved/{run_id}/review-log.jsonl
campaigns/{campaign_id}/approved/{run_id}/campaign-pack.zip

Object Lock is stretch only.

No tamper-proof claim unless implemented.

### 18. Variant Family Tree

Implementation commitment:

PS-034.

Must show lineage:

Campaign Brief
-> Run A
   -> Candidate A1 rejected
   -> Candidate A2 approved
      -> Variant A2.1 cropped 9:16
      -> Variant A2.2 captioned
      -> Export Pack v1 locked

### 19. Failure Theater

Implementation commitment:

PS-030.

Must show:

- captured failures if real
- skipped providers if real
- disabled providers if real
- quota blocks if real
- where future failures would appear
- no fake failures

### 20. Evidence Graph

Implementation commitment:

Fold into PS-032 and PS-043.

Must connect:

- campaign
- run
- prompt packet
- provider attempt
- asset
- B2 object
- Genblaze manifest
- passport
- review decision
- export pack

### 21. Judge Evidence Pack

Implementation commitment:

PS-031.

Must answer:

- what was generated
- which provider/model produced it
- where it is stored
- what Genblaze verifies
- whether it rehydrates from B2
- whether providers were called again
- what is not claimed
- how a reviewer/client can use it

### 22. Production Readiness Layer

Implementation commitment:

PS-040, PS-041, PS-042.

Must include:

- persistent run registry
- restart-safe inspection
- safe demo mode
- local seed data
- public deployment
- env validation
- error sanitization
- safe CORS posture
- input bounds
- secret hygiene
- no leaked provider keys
- repeatable setup

### 23. Signed Passport Export

Stretch implementation commitment.

Only claim if implemented.

Target:

- checksummed passport bundle
- signed metadata if feasible
- no legal authenticity claim

### 24. C2PA Integration

Stretch implementation commitment.

Only claim if real integration exists.

No fake C2PA claim.

### 25. B2 Event / Webhook Notification Layer

Stretch implementation commitment.

Future target:

- B2 event notification
- archive-created event
- manifest-indexed event
- review/export event
- evidence graph update

No live event claim unless implemented.

### 26. Browser-Side B2 Byte Verification

Stretch implementation commitment.

Future target:

- fetch B2 object
- hash in browser
- compare to manifest/archive SHA

No claim unless implemented.


### 27. Team Review Comments

Implementation commitment:

PS-037 — Review Room Comments + Approval Ledger.

Must include:

- reviewer comments
- approve/reject state
- reviewer identity if available
- timestamp or deterministic local evidence timestamp
- linked asset/passport/manifest
- export readiness status

No multi-user/auth claim unless implemented.

### 28. Archive / Rehydrate Lab

Implementation commitment:

Already partially implemented through PS-029.

Continue through PS-031 and PS-043.

Must include:

- archive URI
- archive SHA-256
- read/rehydrate source
- original vs restored proof comparison
- no provider call badge
- truth boundary

## Current Accepted Modern Slices

- PS-023 — Judge Cockpit Home
- PS-024 — Golden Demo Run Pinning
- PS-025 — Public Durable Passport Unlock
- PS-026 — B2 Evidence Explorer
- PS-027 — Genblaze Pipeline Graph
- PS-028 — Manifest Verification Panel
- PS-029 — B2 Rehydrate Comparison

## Implementation Roadmap From Here

### PS-030 — Failure-as-Proof Timeline

Implements:

- Failure-as-Proof Timeline
- Failure Theater
- no-provider-rerun story
- visible production workflow timeline

Acceptance:

- route exists
- timeline visible
- no fake actual failures
- no-provider-rerun proof visible
- truth boundary visible
- PS-029 through PS-023 regressions pass

### PS-031 — Export Campaign Pack v2 / Judge Evidence Pack

Implements:

- Export Campaign Pack
- Judge Evidence Pack
- Proof View / Audit Pack foundation

Acceptance:

- pack surface or generated local pack exists
- includes proof summary
- includes manifest/passport/B2/rehydrate/disclosure sections
- no fake downloads if not implemented
- evidence JSON and smoke pass

### PS-032 — Mission Control / Flight Recorder v2

Implements:

- Mission Control / Flight Recorder
- Evidence Graph foundation
- pipeline lifecycle view

Acceptance:

- lifecycle stages visible
- evidence links visible
- future pipeline.jsonl model documented or implemented
- no fake live monitoring claim

### PS-033 — Model Audition Arena

Implements:

- Model Audition Board

Acceptance:

- candidate comparison visible
- provider/model/status/latency/cost fields visible
- selected/rejected logic visible
- no fake provider candidates

### PS-034 — Variant Family Tree + Manifest Diff

Implements:

- Variant Family Tree
- Manifest Diff

Acceptance:

- lineage visible
- diff fields visible
- hashes/URIs/params compared
- no fake variants

### PS-035 — Disclosure Readiness Layer

> SUPERSEDED by PS-034C reconciliation. Under the authoritative post-PS-034C
> numbering, PS-035 is Review + Approval Workspace, and Disclosure becomes
> PS-037 — Disclosure + Trust Boundary Layer. The intent of this section
> (Disclosure Readiness Layer) is preserved and moved to PS-037. See the
> PS-034C Roadmap Conflict Resolution block at the top of this document and
> Wave 8 in `specs/08-roadmap-slices.md`.

Implements:

- Disclosure Readiness Layer

Acceptance:

- channel-ready disclosure visible
- known/unknown/non-claimed sections
- not legal advice
- no C2PA claim unless implemented

### PS-036 — Credit / Cost / Why This Provider

Implements:

- Credit-Aware Provider Router surface
- Provider Budget Modes
- Cost and Time Ledger
- Why This Provider

Acceptance:

- budget mode visible
- cost/latency/availability visible
- provider rationale visible
- no fake exact cost unless known

### PS-037 — Review Room Comments + Approval Ledger

> SUPERSEDED by PS-034C reconciliation. Under the authoritative post-PS-034C
> numbering, the Review + Approval Workspace intent lives in PS-035 (Review +
> Approval Workspace), and PS-037 is Disclosure + Trust Boundary Layer. See
> the PS-034C Roadmap Conflict Resolution block at the top of this document
> and Wave 8 in `specs/08-roadmap-slices.md`.

Implements:

- Review Room With Proof

Acceptance:

- approve/reject state
- notes/comments
- audit trail
- linked passport/evidence
- export readiness

### PS-038 — B2 Audit Vault

Implements:

- B2 Audit Vault

Acceptance:

- approved proof layout visible
- B2 prefix model visible
- artifact index visible
- no Object Lock claim unless implemented

### PS-039 — Provider Swap Re-run

Implements:

- Provider Swap Re-run

Acceptance:

- original vs swapped run model
- provider/model comparison
- manifest comparison
- no fake provider call

### PS-040 — Persistent Run Registry / Restart-Safe Inspection

Implements:

- Persistent Run Store
- Run Registry
- restart-safe inspection

Acceptance:

- local durable registry
- run lookup
- proof state reconstruction
- survives process restart

### PS-041 — Public Deployment + Demo Mode Hardening

Implements:

- Deployment
- Demo Mode + Seed Data

Acceptance:

- public app URL
- seed demo path
- safe live toggle
- env validation
- no leaked secrets

### PS-042 — Security / Input / Error Hardening

Implements:

- Auth/basic security posture where feasible
- input bounds
- error sanitization
- safe CORS
- rate-limit posture

Acceptance:

- unsafe inputs bounded
- errors sanitized
- secrets not exposed
- honest security boundary

### PS-043 — Final Submission Pack / Demo Script / README Hardening

Implements:

- Final Submission Pack

Acceptance:

- README
- provider/model list
- Backblaze + Genblaze explanation
- architecture diagram
- screenshots
- 3-minute demo script
- truth boundary
- final limitations

## What We Will Not Do

We will not turn these ideas into a dead document.

Each idea above has a slice assignment.

If a slice is skipped, it must be because of a real blocker, and the blocker must be documented.

## PM Operating Rules

- The roadmap is implementation-driven, not inspiration-driven.
- Every slice must build part of the product.
- No decorative UI without evidence.
- No fake proof.
- No fake provider calls.
- No fake B2 reads.
- No fake failures.
- No fake public deployment claims.
- Canonical smoke validates product contract.
- Final gates must not add brittle duplicate semantic scanners.
- Every slice needs:
  - spec
  - implementation
  - smoke
  - evidence JSON
  - proof doc
  - regression protection
  - exact commit gate
