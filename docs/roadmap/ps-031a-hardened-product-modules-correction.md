# PS-031A — Hardened Product Modules Roadmap Correction

Current as of: 2026-06-29

## PM Decision

PS-031A is a small roadmap correction.

It does not renumber accepted slices.

It clarifies how PS-032 onward should be interpreted and implemented.

The goal is to avoid building duplicate pages for overlapping old-window and new out-of-the-box ideas.

ProofStudio must become a working product that designers, marketers, reviewers, clients, and judges can use and enjoy.

It must not become a shallow MVP or a collection of disconnected proof pages.

## Binding Product Standard

ProofStudio is an AI media operations cockpit.

It should help real creative and marketing teams:

- generate campaign media
- understand which provider/model was used
- see why routing decisions happened
- preserve attempts, evidence, and proof
- review and approve assets
- export a usable client/judge pack
- explain disclosure boundaries
- rehydrate historical proof from B2
- understand what is verified and what is not claimed
- manage campaigns from a polished dashboard
- understand the product through a simple modern public website

Every future slice must improve at least one real user workflow.

## No Duplicate Feature Pages

Do not build one page per idea if the ideas solve the same user job.

From PS-032 onward, similar ideas must be merged into hardened product modules.

A hardened module must have:

- a clear user job
- product surface or API behavior
- linked evidence
- truth boundary
- smoke validation
- proof doc
- no fake claims
- no decorative-only UI

## Hardened Product Modules

### 1. Judge Evidence Pack / Export Pack

Already started by PS-031.

Merges:

- Export Campaign Pack
- Judge Evidence Pack
- Proof View / Audit Pack
- Passport export
- disclosure notes
- final submission evidence-pack pieces

User job:

A designer, marketer, client, or judge can take away a readable proof bundle.

### 2. Operations Cockpit / Flight Recorder

Main future slice:

- PS-032 — Operations Cockpit / Flight Recorder v2

Merges:

- Mission Control
- Flight Recorder
- Failure-as-Proof Timeline
- Failure Theater
- Evidence Graph
- pipeline lifecycle view

User job:

A creative operator can see what happened from brief to export without reading raw JSON.

### 3. Provider Decision Intelligence

Main future slice:

- PS-033 — Provider Decision Intelligence

Merges:

- Credit-Aware Provider Router
- Provider Budget Modes
- Cost and Time Ledger
- Why This Provider
- Emergency No-Key Mode
- quota/paid/free risk explanation

User job:

A marketer can understand why ProofStudio chose a provider, what it costs or risks, and what fallback path exists.

### 4. Lineage + Comparison Lab

Main future slice:

- PS-034 — Lineage + Comparison Lab

Merges:

- Model Audition Board
- Manifest Diff
- Provider Swap Re-run
- Variant Family Tree

User job:

A designer can compare candidates, variants, provider swaps, and manifest differences in one coherent workspace.

### 5. Review + Approval Workspace

Main future slice:

- PS-035 — Review + Approval Workspace

Merges:

- Review Room
- Team Review Comments
- Approval Ledger
- reviewer next actions
- export readiness

User job:

A team can approve, reject, comment, and prepare final assets for export.

### 6. Archive / Rehydrate / B2 Audit Vault

Main future slice:

- PS-036 — Archive / Rehydrate / B2 Audit Vault

Merges:

- Rehydrate from B2
- Archive / Rehydrate Lab
- B2 Audit Vault
- approved artifact layout
- browser-side B2 byte verification stretch
- Object Lock stretch

User job:

A client or reviewer can trust B2 as the durable system of record and inspect archived proof.

### 7. Disclosure + Trust Boundary Layer

Main future slice:

- PS-037 — Disclosure + Trust Boundary Layer

Merges:

- Disclosure Readiness Layer
- truth boundary
- non-claims
- C2PA-only-if-real boundary
- signed passport export stretch

User job:

A marketer can prepare honest AI-use disclosure without overclaiming authenticity.

### 8. Production Readiness + Submission Hardening

Main future slices:

- PS-038 — Production Readiness + Demo Mode
- PS-039 — Final Submission Pack

Merges:

- public deployment
- demo mode and seed data
- input/error/security posture
- README hardening
- provider/model inventory
- architecture diagram
- screenshots
- three-minute demo script

User job:

Judges and real users can access, run, understand, and evaluate the project safely.

### 9. Product Dashboard + Marketing Website Experience

Reserved future slice:

- PS-040 — Product Dashboard + Marketing Website Experience

Merges:

- application dashboard
- modern public website
- designer/marketer onboarding
- product introduction
- SEO optimization
- AEO optimization
- app navigation polish
- screenshot-ready product storytelling
- award-level UI/UX design direction

User job:

A designer, marketer, client, or judge can understand ProofStudio quickly, enter the app confidently, and feel the value without needing a technical explanation.

Dashboard requirements:

- campaign overview
- recent runs
- proof status
- provider/model status
- review status
- export readiness
- evidence warnings
- quick actions
- dashboard cards for key workflows
- polished UI/UX
- designer/marketer-friendly language
- no fake data unless clearly marked as demo seed data

Marketing website requirements:

- simple modern product story
- clear headline and value proposition
- problem / solution
- workflow explanation
- B2 + Genblaze proof story
- designers and marketers as primary users
- judges and clients as secondary users
- screenshots or demo panels
- CTA to dashboard/app/demo
- SEO metadata
- AEO-friendly FAQ / answer-style sections
- honest truth boundary
- no overclaiming

Planning/build approach:

- Antigravity and Claude Opus 4.6 may be used for planning the dashboard and website.
- Gemini 3.5 Pro may be used for implementation.
- A world-class implementation prompt should be created when this slice begins.
- Do not begin PS-040 until dashboard options, app information architecture, website sections, content strategy, SEO/AEO requirements, and existing route constraints are defined.

## Roadmap Numbering Rule

Do not renumber already accepted roadmap slices.

Use PS-031A as the correction layer.

Future specs should reference this addendum when deciding how to merge overlapping ideas.

If an older roadmap item appears to conflict with this correction, follow this correction unless the user explicitly says otherwise.

## Updated Interpretation From PS-032 Onward

- PS-032 should implement Operations Cockpit / Flight Recorder v2.
- PS-033 should implement Provider Decision Intelligence.
- PS-034 should implement Lineage + Comparison Lab.
- PS-035 should implement Review + Approval Workspace.
- PS-036 should implement Archive / Rehydrate / B2 Audit Vault.
- PS-037 should implement Disclosure + Trust Boundary Layer.
- PS-038 should implement Production Readiness + Demo Mode.
- PS-039 should implement Final Submission Pack.
- PS-040 should implement Product Dashboard + Marketing Website Experience.

PS-041 through PS-043 are not deleted.

They become reserve numbers for:

- real blockers
- hardening gaps
- stretch implementation
- judge feedback fixes
- production polish if needed

## Non-Negotiable Product Rule

Every future feature must be judged by this question:

Would a designer, marketer, reviewer, client, or hackathon judge understand and feel value from this?

If the answer is no, do not build it.

## Design Quality Rule

ProofStudio should feel like a serious creative-operations product.

Future UI work must optimize for:

- clarity
- trust
- speed to understand
- modern visual quality
- useful information hierarchy
- designer/marketer language
- judge demo clarity
- responsive layout
- accessibility basics
- no decorative-only complexity

## SEO / AEO Rule

The marketing website must support both SEO and AEO.

SEO requirements:

- strong page title
- meta description
- structured headings
- clear internal links
- concise product positioning
- keyword-aware but not spammy copy
- screenshot/demo alt text where applicable

AEO requirements:

- answer-style sections
- clear FAQ
- direct definitions
- "what is ProofStudio" answer
- "who is ProofStudio for" answer
- "how does ProofStudio use B2 and Genblaze" answer
- "what does ProofStudio verify and not verify" answer
- concise summaries suitable for AI answer engines

## Truth Boundary

This correction does not authorize overclaiming.

Do not claim:

- legal authenticity
- semantic truth
- human authorship
- C2PA authenticity
- Object Lock / tamper-proof storage
- browser-side B2 byte verification
- public deployment verification
- enterprise security

unless each item is actually implemented and validated.

## PS-034C Reconciliation Note (2026-07-01)

PS-034C (Winning Roadmap + Master Spec Replan) reconciles this PS-031A
correction with the post-PS-034B roadmap. This note records how the two fit
together.

- PS-031A numbering remains authoritative unless later superseded. This
  document is the reference state for the roadmap going forward.
- PS-034C adds a winning roadmap wave on top of the PS-031A hardened product
  modules; it does not renumber accepted slices.
- No accepted slice is dropped. Every accepted built slice PS-023 through
  PS-034B is preserved by the PS-034C replan.
- Campaign Proof Room and the multimodal proof layer are added as future
  slices (PS-038a and the PS-037a/PS-037b/PS-037c/PS-037d/PS-037e family).
  These are documentation-only commitments in PS-034C; they are not
  implemented in PS-034C.
- The PS-035 numbering conflict is resolved: PS-035 is Review + Approval
  Workspace, and Disclosure becomes PS-037 — Disclosure + Trust Boundary
  Layer. PS-035 remains blocked until PS-034C is accepted.
- PS-035a (Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest
  Correctness) is blocking and should be the next implementation slice unless
  the PM later changes priority. The golden run currently has a null
  `manifest_uri` / `manifest_hash` / `genblaze_version` gap that PS-035a
  closes.
- PS-040 (Product Dashboard + Marketing Website Experience) is delayed/
  optional. It should not compete with submission-critical slices for spend or
  time.
- PS-041 through PS-043 are reserve numbers for hardening, stretch, and fixes,
  exactly as this correction already stated.

This reconciliation does not authorize overclaiming. The truth boundary above
still applies in full.

