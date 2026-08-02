# PS-023 — Judge Cockpit Home

## Status

Specification slice.

## Purpose

Turn the public homepage into a judge-first cockpit that explains ProofStudio in under 10 seconds and routes judges directly to the strongest proof surfaces.

This is not a generic marketing homepage. It is the front door for hackathon evaluation.

## Current Proven Base

PS-022 locked the master winning roadmap.

Current proven project state includes:

- public frontend URL
- public API URL
- public deployment smoke evidence
- public Provenance Passport route
- Proof Score
- durable passport rehydrate foundation
- live B2 durable rehydrate proof
- B2 archive write/read proof
- `b2_object_content` archive storage mode
- no provider call during B2 rehydrate
- submission docs already present under `docs/submission/`

## Problem

ProofStudio has deep proof, but judges may not discover it quickly enough.

The homepage must make the value obvious immediately:

- ProofStudio is not another AI generator.
- ProofStudio is an AI media operations system of record.
- B2 and Genblaze are central to the workflow.
- Provenance Passport is the judge/client-facing proof object.

## User

Primary user for this slice:

- hackathon judge

Secondary users:

- creator team
- marketing agency
- client/legal reviewer
- AI ops engineer

## Required Homepage Sections

### 1. Hero

Must include:

- product name: ProofStudio
- one-line thesis: AI media operations with durable proof.
- short explanation focused on creator/marketing teams
- primary CTA: Open Judge Demo
- secondary CTA: View Provenance Passport

Hero must not claim:

- legal authenticity
- semantic truth
- C2PA verification
- human authorship
- enterprise-grade security

### 2. Golden Proof Path

Must show the workflow:

`Brief -> ProviderRouter -> Genblaze Pipeline -> Generated Asset -> B2 Storage -> Manifest -> Archive -> Rehydrate -> Provenance Passport`

This can be visual cards, timeline, or diagram.

### 3. Judge Proof Cards

Must show four cards mapped to judging criteria:

- Real-world Utility
- Production Readiness
- B2 Storage + Data Orchestration
- Use of Genblaze

Each card must say what ProofStudio already proves or exposes.

### 4. B2 Evidence Card

Must show B2 as a system-of-record layer.

Required copy points:

- assets
- manifests
- archives
- evidence JSON
- rehydrate from B2 archive content

Must avoid fake live claims unless backed by pinned proof.

### 5. Genblaze Pipeline Card

Must show Genblaze as orchestration/provenance infrastructure.

Required copy points:

- media pipeline
- provider workflow
- manifest verification
- SHA-256 provenance evidence

### 6. Provenance Passport Preview

Must preview what a passport contains:

- provider/model
- attempt timeline
- asset evidence
- manifest verification
- B2 archive proof
- truth boundary

### 7. Truth Boundary

Must include a permanent truth boundary section:

ProofStudio proves what this pipeline did. It does not prove semantic truth, legal authenticity, C2PA authenticity, or human authorship.

### 8. Direct CTAs

Homepage must include links/buttons to available proof surfaces.

Expected CTAs:

- Open Judge Demo
- View Provenance Passport
- View Evidence Pack
- Read Submission Notes
- Open GitHub/README if available in existing repo config

If a target route/file is not implemented, it must be clearly marked as planned or disabled. Do not create broken links.

## Allowed Files

GLM implementation may inspect the repo first before editing.

Expected likely files:

- `apps/web/`
- frontend page/component files discovered by inspection
- possible frontend README/proof doc
- optional smoke script for homepage links

Do not assume framework paths. Inspect before editing.

## Required Proof Doc

Create:

- `docs/ps-023-judge-cockpit-home-proof.md`

Proof doc must include:

- files changed
- public/local route tested
- screenshots path if screenshots are created
- CTA target list
- truth boundary confirmation
- no overclaim confirmation

## Required Smoke / Validation

At minimum, validation must prove:

- frontend builds or lints if existing scripts support it
- homepage route exists locally or statically
- required copy appears in source/build output
- no forbidden overclaim language appears
- no broken internal CTAs are introduced, or unavailable CTAs are disabled/marked planned
- secret scan passes

## Forbidden Claims

Reject immediately if homepage says or implies:

- ProofStudio proves the image is true
- ProofStudio proves legal authenticity
- ProofStudio proves human authorship
- ProofStudio is C2PA verified
- production security/auth/multi-user support exists unless actually implemented
- Object Lock/tamper-proof storage exists unless actually implemented

## Acceptance Criteria

PS-023 is accepted only if:

1. Homepage clearly explains ProofStudio in under 10 seconds.
2. B2 and Genblaze are visible above or near the first proof section.
3. The golden proof path is visible.
4. CTAs route judges to implemented proof surfaces or are honestly marked planned.
5. Truth boundary is visible.
6. No unproven claims are introduced.
7. Build/lint/smoke validation passes.
8. Proof doc is created.
9. Working tree contains only allowed PS-023 files before commit.

## Failure Conditions

Fail the slice if:

- homepage is generic SaaS fluff
- B2/Genblaze are hidden below the fold
- CTAs are broken
- copy overclaims authenticity/truth/security
- frontend build breaks
- proof doc is missing
- unrelated files are changed

## Next Slice After PS-023

PS-024 — Golden Demo Run Pinning.
