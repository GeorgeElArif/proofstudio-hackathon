# PS-022 — Master Winning Roadmap

## Status

Specification slice.

## Purpose

Lock ProofStudio’s remaining build plan into a judge-focused, spec-driven roadmap.

This document exists to prevent random feature building. Every future slice must improve the product against the Backblaze Generative AI Media Hackathon requirements and judging criteria:

1. Real-world Utility
2. Production Readiness
3. B2 Storage + Data Orchestration
4. Use of Genblaze

## Current Proven State

As of PS-021, ProofStudio has already proven:

* Public deployment exists and has been smoke-tested.
* Public frontend and API URLs exist.
* Safe public dry-run exists.
* Review Room / public Provenance Passport path exists.
* Proof Score exists.
* Durable passport rehydrate foundation exists.
* Live B2 durable rehydrate proof exists.
* B2 archive write/read proof exists.
* Archive storage mode `b2_object_content` is proven.
* Rehydrate without provider rerun is proven.
* Historical proof scripts remain protected.
* Truth boundary is part of the product.

PS-021 accepted proof:

* Branch: `ps-021/live-b2-durable-rehydrate-proof`
* Commit: `2294e180f5a8462fa4922c9529e4463b61d0729e`
* Archive SHA-256: `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
* Archive URI: `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json`

## Product Thesis

ProofStudio is AI media operations with durable proof.

Most AI media apps stop at generation. ProofStudio focuses on the production layer after generation:

`Brief -> ProviderRouter -> Genblaze Pipeline -> Generated Asset -> B2 Storage -> Manifest -> Archive -> Rehydrate -> Provenance Passport -> Judge/Client Review`

ProofStudio does not claim that media is semantically true, legally authentic, C2PA-certified, or human-authored.

ProofStudio proves what this pipeline did:

* which campaign/run was created
* which provider/model was used
* which attempts succeeded or failed
* which generated assets were captured
* which manifests and hashes were recorded
* which B2 archive was written and read back
* whether evidence can be rehydrated without rerunning providers
* what the proof does and does not claim

## Winning Position

ProofStudio should not compete as another image generator.

ProofStudio should compete as:

**The system of record for generative media teams.**

Judge-facing sentence:

**ProofStudio helps creator and marketing teams generate AI media without losing the operational proof trail: every run is routed across providers, stored in Backblaze B2, verified with Genblaze manifests, rehydratable from durable evidence, and reviewable through a Provenance Passport.**

## Build Law

A future slice is valid only if it satisfies at least one of these conditions:

1. Makes B2 usage more visible, durable, or useful.
2. Makes Genblaze usage more visible, orchestrated, or useful.
3. Makes the judge demo easier to understand.
4. Makes the public app more reliable.
5. Makes the submission pack more complete.
6. Makes the product more useful for creator, marketing, agency, or reviewer workflows.
7. Improves proof integrity without overclaiming.

A future slice is rejected if it:

* fakes media
* fakes B2 proof
* fakes Genblaze proof
* hides provider failure
* overclaims legal authenticity, semantic truth, C2PA authenticity, or human authorship
* adds UI that cannot be backed by real data or a clearly marked demo/seed mode
* burns live provider calls unnecessarily
* changes historical proof scripts without explicit slice permission
* creates untestable claims

## Master Roadmap

### Phase 1 — Lock the Judge Narrative

#### PS-023 — Judge Cockpit Home

Goal: Make the public landing page explain ProofStudio in under 10 seconds.

Required elements:

* product thesis
* golden path diagram
* CTA to Judge Demo
* CTA to Provenance Passport
* CTA to Evidence Pack
* public status badges

Acceptance:

* public frontend loads
* CTAs resolve
* copy does not overclaim
* page makes B2 and Genblaze visible immediately

Judging impact:

* Real-world Utility
* Production Readiness
* B2 Storage + Data Orchestration
* Use of Genblaze

#### PS-024 — Golden Demo Run Pinning

Goal: Pin one canonical demo run used across homepage, passport, evidence pack, README, and demo video.

Required elements:

* canonical run ID
* campaign ID
* passport URL
* archive URI
* archive SHA-256
* manifest URI/hash when available
* proof score
* rehydrate status

Acceptance:

* one command verifies all canonical IDs
* public UI opens the pinned run
* no stale links

Judging impact:

* demo clarity
* production readiness

#### PS-025 — Judge Mode

Goal: Give judges a safe, deterministic test path.

Required elements:

* clear “Judge Mode” banner
* no surprise live provider spend
* safe dry-run path
* seeded/replayed proof path
* live proof path clearly marked when available

Acceptance:

* judge can test without credentials
* public route explains which data is live, seeded, or rehydrated

Judging impact:

* production readiness
* real-world utility

---

### Phase 2 — Make B2 and Genblaze Undeniable

#### PS-026 — B2 Evidence Explorer

Goal: Make B2 object storage visible inside the product.

Required elements:

* archive URI
* asset URI
* manifest URI
* archive SHA-256
* readback status
* storage mode
* copy buttons

Acceptance:

* panel renders for canonical run
* no secret values exposed
* B2 evidence matches JSON proof

Judging impact:

* B2 Storage + Data Orchestration

#### PS-027 — Genblaze Pipeline Graph

Goal: Show Genblaze as a real media pipeline, not a hidden library.

Required elements:

* brief/input stage
* provider routing stage
* generation attempt stage
* manifest stage
* B2 storage stage
* passport/review stage

Acceptance:

* graph renders from real or canonical run data
* no decorative-only pipeline claims

Judging impact:

* Use of Genblaze
* demo clarity

#### PS-028 — Manifest Verification Panel

Goal: Make manifest verification understandable to non-technical judges.

Required elements:

* manifest URI
* manifest hash
* verified status
* asset count
* what verification means
* what verification does not mean

Acceptance:

* panel uses actual passport/manifest fields
* truth boundary appears near verification

Judging impact:

* Use of Genblaze
* production readiness

#### PS-029 — B2 Rehydrate Comparison

Goal: Show original run evidence beside rehydrated evidence.

Required elements:

* original run ID
* rehydrated run ID or rehydrated source
* archive SHA-256
* provider calls during rehydrate
* equality/match checks

Acceptance:

* UI or proof doc shows rehydrate without provider rerun
* provider call count is zero

Judging impact:

* B2 Storage + Data Orchestration
* production readiness

---

### Phase 3 — Turn Proof Into a Product

#### PS-030 — Failure-as-Proof Timeline

Goal: Treat failed provider attempts as useful operational evidence.

Required elements:

* provider attempted
* model attempted
* normalized status
* fallback reason
* sanitized error
* next provider or final state

Acceptance:

* failed/blocked states display honestly
* errors are sanitized
* no compact attempts replace full ledgers

Judging impact:

* production readiness

#### PS-031 — Proof Score v2

Goal: Make Proof Score explainable and deterministic.

Required score components:

* attempt ledger completeness
* B2 archive write/read
* manifest presence/verification
* rehydrate proof
* provider rerun avoided
* truth boundary present

Acceptance:

* score has breakdown, not just a number
* score is deterministic for the same run

Judging impact:

* real-world utility
* production readiness

#### PS-032 — Timeline Replay

Goal: Animate the proof chain in the public app.

Required sequence:

`Brief -> Provider Attempt -> Asset -> Genblaze Manifest -> B2 Archive -> Rehydrate -> Passport`

Acceptance:

* replay works on canonical run
* finishes in under 20 seconds
* no fake status transitions

Judging impact:

* demo clarity
* Use of Genblaze
* B2 Storage + Data Orchestration

#### PS-033 — Evidence Bundle Export

Goal: Export a client/judge evidence bundle.

Required bundle files:

* passport JSON
* archive JSON
* manifest JSON or manifest reference
* attempt ledger
* proof summary markdown
* truth boundary text

Acceptance:

* export is deterministic
* no secrets
* bundle can be regenerated from canonical run

Judging impact:

* real-world utility
* production readiness

---

### Phase 4 — Submission Readiness

#### PS-034 — Provider and Model Inventory Page

Goal: Make provider/model usage easy for judges to verify.

Required elements:

* active providers
* active models
* fallback providers
* blocked providers, if any
* why blocked states are honest
* what providers are planned but not claimed

Acceptance:

* public/doc page exists
* matches actual code and evidence

Judging impact:

* submission requirement
* production readiness

#### PS-035 — Submission Compliance Wall

Goal: Show all Devpost requirements in one place.

Required elements:

* working app URL
* API URL
* GitHub repo
* setup instructions
* provider/model list
* B2 usage explanation
* Genblaze usage explanation
* demo video placeholder or final URL
* truth boundary

Acceptance:

* no missing required submission item
* no unverified claims

Judging impact:

* submission quality

#### PS-036 — README Grand Prize Rewrite

Goal: Rewrite README for judges, not developers only.

Required sections:

* what ProofStudio is
* why it matters
* golden path
* B2 usage
* Genblaze usage
* providers/models
* public URLs
* local setup
* demo workflow
* smoke tests
* evidence pack
* truth boundary
* known limitations

Acceptance:

* README can stand alone for judging
* links resolve
* no stale “Sprint 0” status remains

Judging impact:

* all criteria

#### PS-037 — Demo Video Script and Recording Runbook

Goal: Make the demo video tight and judge-first.

Required structure:

* 0:00-0:20 problem
* 0:20-0:45 product
* 0:45-1:25 live/golden run
* 1:25-1:55 B2 rehydrate
* 1:55-2:30 Provenance Passport
* 2:30-2:55 why B2 and Genblaze matter
* under 3 minutes

Acceptance:

* script avoids unproven claims
* screen path uses public app and canonical run

Judging impact:

* demo quality

#### PS-038 — Genblaze Feedback Prize Draft

Goal: Prepare a serious feedback issue for the Genblaze repo.

Required elements:

* what worked
* what was missing
* what would improve developer experience
* concrete examples from ProofStudio
* no complaint without actionable suggestion

Acceptance:

* issue draft exists
* feedback is specific and respectful

Judging impact:

* feedback prize opportunity
* sponsor alignment

#### PS-039 — Final Public Smoke Freeze

Goal: Final pre-submission validation.

Required checks:

* public frontend
* public API
* health/version
* CORS
* Judge Mode
* canonical passport
* B2 evidence panel
* Genblaze pipeline graph
* evidence bundle
* README links
* submission docs

Acceptance:

* one script writes final summary JSON
* final tree is clean
* public URLs are verified

Judging impact:

* production readiness
* submission readiness

---

## The Best 33 Hardened Out-of-Box Ideas

These ideas are approved because they are judge-visible, buildable, and tied to the actual ProofStudio product.

### 1. Judge Cockpit Home

A homepage designed for judges, not generic marketing.

Acceptance:

* public route loads
* explains ProofStudio in under 10 seconds
* links to demo, passport, evidence, and submission docs

### 2. Golden Demo Run

One canonical run used everywhere.

Acceptance:

* run ID, passport URL, archive URI, and hash are pinned
* no broken or inconsistent demo paths

### 3. Judge Mode

A safe mode for evaluation.

Acceptance:

* public judge path works without credentials
* live/seeded/rehydrated states are clearly labeled

### 4. B2 Evidence Explorer

A UI panel exposing B2 proof.

Acceptance:

* archive URI, SHA-256, storage mode, and readback status are visible

### 5. Genblaze Pipeline Graph

A visual graph of the media pipeline.

Acceptance:

* graph maps to real pipeline stages
* Genblaze is visible as orchestration, not branding

### 6. Manifest Verification Panel

A readable panel for manifest verification.

Acceptance:

* manifest URI/hash/status visible
* truth boundary nearby

### 7. B2 Rehydrate Comparison

Compare original evidence to rehydrated evidence.

Acceptance:

* provider calls during rehydrate equals zero
* archive hash matches

### 8. Failure-as-Proof Timeline

Provider failures become timeline evidence.

Acceptance:

* provider/model/status/fallback reason shown
* sanitized errors only

### 9. Proof Score v2

Explainable score, not magic score.

Acceptance:

* score breakdown is deterministic
* storage, manifest, attempts, rehydrate, and truth boundary are represented

### 10. Timeline Replay

Animated proof chain for the demo.

Acceptance:

* replay uses canonical run data
* finishes in under 20 seconds

### 11. Evidence Bundle Export

Downloadable proof pack.

Acceptance:

* includes passport, archive, manifest/reference, attempts, summary, truth boundary

### 12. Provider and Model Inventory Page

Public provider/model compliance page.

Acceptance:

* matches code and proof
* blocked providers are marked honestly

### 13. Submission Compliance Wall

A page/checklist showing Devpost readiness.

Acceptance:

* all required submission materials listed with status

### 14. README Grand Prize Rewrite

README rewritten for judges.

Acceptance:

* no stale status
* setup and demo are clear

### 15. Demo Video Script

A tight sub-3-minute script.

Acceptance:

* screen path is exact
* no unproven claims

### 16. Final Public Smoke Freeze

One final public validation.

Acceptance:

* smoke writes final JSON proof
* public app/API/passport/evidence paths pass

### 17. Truth Boundary Card

A permanent product card explaining non-claims.

Acceptance:

* says ProofStudio does not prove semantic truth, legal authenticity, C2PA authenticity, or human authorship

### 18. Raw JSON Toggle

Let technical judges inspect raw proof.

Acceptance:

* JSON is available but not the default experience

### 19. Copy Evidence Buttons

Copy run ID, archive URI, hash, and manifest URI.

Acceptance:

* buttons copy exact values from current run

### 20. Client Review Summary

Plain-English summary for non-technical reviewers.

Acceptance:

* one paragraph generated from passport fields
* no legal overclaim

### 21. Run Health Panel

Operational status for a run.

Acceptance:

* status, attempts, assets, manifest, archive, rehydrate state visible

### 22. Environment Readiness Checker

Checks missing keys without printing secrets.

Acceptance:

* reports present/missing only
* no secret values exposed

### 23. Safe Live Mode Guard

Live provider/B2 actions require explicit env flag.

Acceptance:

* no accidental live spend
* blocked state is honest

### 24. Archive Schema Version

Version the archive contract.

Acceptance:

* archive schema version appears in JSON
* validator rejects unsupported versions

### 25. Passport Schema Version

Version the passport contract.

Acceptance:

* passport schema version appears in JSON
* frontend handles expected version

### 26. Public API Contract Page

Simple docs for health/version/passport/demo endpoints.

Acceptance:

* public API behavior documented
* matches actual endpoints

### 27. Proof Pack Stored Back to B2

Exported evidence bundle can be stored in B2.

Acceptance:

* bundle URI and hash recorded
* no secrets in bundle

### 28. Campaign Brief Intake

A small real-world campaign intake form.

Acceptance:

* audience, goal, channel, format, prompt captured
* appears in passport campaign snapshot

### 29. Asset Evidence Cards

Each generated asset gets a proof card.

Acceptance:

* provider/model/hash/storage reference visible

### 30. Reviewer Decision Checklist

Human reviewer checklist.

Acceptance:

* “acceptable for client review” is human decision, not AI truth claim

### 31. Genblaze Feedback Issue Draft

Bonus prize strategy.

Acceptance:

* feedback is specific, actionable, based on actual implementation

### 32. Limitations Page

Production honesty page.

Acceptance:

* clearly states what is implemented and what is not

### 33. Submission Lock Gate

Final gate before Devpost submit.

Acceptance:

* dirty tree rejected
* public URLs verified
* docs complete
* video URL present
* provider/model list present
* B2 and Genblaze explanations present

---

## Rejected Ideas

These are intentionally not in the roadmap yet:

* C2PA verification, because it is not implemented.
* Legal authenticity claims, because ProofStudio does not prove legal authenticity.
* Human authorship claims, because the app proves pipeline activity, not authorship.
* Tamper-proof/Object Lock claims, unless actually implemented.
* Multi-user auth/security claims, unless actually implemented.
* Cost optimization dashboards, unless real measurements are captured.
* Video/audio generation claims, unless real provider proof exists.
* Enterprise compliance claims, unless backed by implementation.
* “AI detector” features, because they distract from the hackathon’s B2/Genblaze scoring.
* Fancy UI animations that do not expose proof.

## Required Slice Discipline

Every future slice must have:

1. spec file
2. branch
3. allowed files list
4. failure conditions
5. smoke or docs validation
6. evidence JSON when runtime behavior is involved
7. no secret scan
8. historical script protection when applicable
9. final proof doc
10. clean commit

## Next Slice

After PS-022 is committed, build:

`PS-023 — Judge Cockpit Home`

Reason:

The proof engine is strong. The current highest risk is that judges do not understand the product quickly enough. The next slice must make the public app judge-first.
