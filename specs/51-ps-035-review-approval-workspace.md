# PS-035 — Review + Approval Workspace

## 1. Status

PS-035 — Review + Approval Workspace is currently:

- Spec only.
- Implementation pending. No product code, frontend code, backend code,
  scripts, evidence, AGENTS.md, `.env*`, `render.yaml`, or requirements files
  are changed during this phase.

PS-035 must not be implemented, and no implementation files may be changed,
until this spec is accepted by the PM. The latest accepted base is
`accepted/proofstudio` commit
`964cc404fe1fa6a0f046b5130aa01b2425a1d7df`.

This spec-only commit touches only this file:
`specs/51-ps-035-review-approval-workspace.md`.

PS-035 must not call live providers, must not read or write live B2, must not
mutate any evidence, must not run the frontend, must not stage, commit, or
push, and must not print secrets during this phase. PS-035 obeys the root
`AGENTS.md` operating law and the validation policy in
`docs/validation/proofstudio-smoke-harness-v1.md`.

## 2. Purpose

PS-035 adds a clear human review and approval workspace for ProofStudio's
existing generated media / provenance pipeline. The goal is to make the
product feel less like "generated files plus evidence" and more like an
operations workspace where a human can:

- review assets
- inspect existing proof
- approve / reject items
- explain why a decision was made
- understand what evidence exists before export or a demo presentation

The review workspace is a human decision surface, not a legal authenticity
system. "Approval" in PS-035 means *approved by this workflow / demo UI*; it
does **not** mean "legally verified," "factually true," "human-authored,"
"C2PA-authentic," "tamper-proof," or "production-secure."

PS-035 proves what the pipeline did. It does not prove semantic truth, legal
authenticity, C2PA authenticity, human authorship, Object Lock / tamper-proof
storage, browser-side B2 byte verification, public deployment verification,
or enterprise security.

## 3. Product Problem

Today ProofStudio surfaces proof across many disconnected pages (B2 Evidence
Explorer, Genblaze Pipeline Graph, Manifest Verification Panel, B2 Rehydrate
Comparison, Failure-as-Proof Timeline, Judge Evidence Pack, Operations
Cockpit, Provider Decision Intelligence, Lineage + Comparison Lab). Each page
shows what the pipeline did, but none of them gives a reviewer one place to
*make a decision* on an asset and record the reason.

The closest existing surface is the legacy PS-013 / PS-014 Review Room at
`/review`, which is a live operator flow (create campaign -> create run ->
fetch evidence) over the FastAPI demo contract. It is not an approval
workspace: it has no reviewer decision controls, no recorded rationale, no
approval ledger, and no review-state lifecycle. The Provenance Passport
already exposes a read-only `review_room_summary` block
(`one_sentence_summary`, `risk_flags`, `reviewer_next_actions`), but that is a
summary, not a decision surface.

A reviewer / client / judge today cannot, in one place:

- see a reviewable item from accepted local / demo data
- see the asset / media summary
- see the proof / evidence status already captured by the pipeline
- set a review state (pending review, approved, rejected, needs changes)
- record the reason for the decision
- read a clear boundary statement of what approval does and does not mean

PS-035 closes that gap by adding a dedicated review + approval workspace that
reuses existing accepted data paths and existing checked-in proof, without
calling providers and without reading live B2.

## 4. User Story

As a reviewer (designer, marketer, reviewer, client, or judge), I want a
single workspace where I can look at a reviewable item from the accepted
golden run, see what proof the pipeline already captured for it, make an
approve / reject / needs-changes decision, record my reason, and understand
exactly what that decision does and does not prove — so that the product
behaves like an operations workspace, not just a folder of generated files
and evidence.

As a demo presenter, I want that workspace to be useful in a three-minute
hackathon demo: clear title, at least one reviewable item, decision controls,
recorded rationale, proof status, and an honest boundary message — all
working offline from local / golden / demo fixtures, with no live provider
calls and no live B2 reads.

## 5. Current Accepted Base

The current accepted base for PS-035 is:

- branch: `accepted/proofstudio`
- commit: `964cc404fe1fa6a0f046b5130aa01b2425a1d7df`
- remote: `origin/accepted/proofstudio` is at the same commit
- this is the post-PS-035D accepted state (root `AGENTS.md` operating law is
  already in place; the central regression gate is already non-mutating by
  default from PS-035C; the golden-fixture digest freeze is in place from
  PS-035B; the golden-run manifest correctness is in place from PS-035A)

PS-035 must start from `origin/accepted/proofstudio`, not from `main`.

Relevant accepted facts at this base that PS-035 reuses (these are read-only
inputs; PS-035 must not mutate them and must not change their values):

- the central regression gate
  (`scripts/proofstudio_regression_gate.py`) supports `--current`,
  `--frontend`, `--no-frontend`, `--check-only`, `--report-out`, and
  `--write-report` (PS-035C accepted)
- the gate is non-mutating by default for non-PS034A current slices
  (PS-035C accepted)
- the root `AGENTS.md` operating law exists at the repository root
  (PS-035D accepted)
- the golden-fixture digest freeze exists at
  `docs/evidence/golden-fixture-digests.json` (PS-035B accepted)
- the golden-run manifest carries a real non-null `manifest_uri` and a real
  64-hex `manifest_hash` (PS-035A accepted)
- the golden run canonical constants are fixed inputs (see section 12)
- the Provenance Passport already exposes a `review_room_summary` block

## 6. Scope

PS-035 is a product slice. It adds a dedicated review + approval workspace
surface. It is local / static by default: it must work without live provider
calls and without live B2 reads by using local / golden / demo fixtures or
existing accepted data paths.

PS-035 must:

1. Add a dedicated review + approval workspace route / page / surface using
   existing app conventions (client-side route guard in
   `apps/web/src/App.tsx`, a PascalCase component, and a kebab-case data
   module — see section 8).
2. Show at least one reviewable item / card / row sourced from accepted
   local / demo data (the golden run and its checked-in evidence).
3. Show an asset / media summary for each reviewable item.
4. Show the proof / evidence status already captured by the pipeline for each
   item (provenance passport link, manifest verification status, B2 archive /
   rehydrate evidence, failure / proof timeline link, and export-pack link,
   depending on what exists in accepted data).
5. Expose review states. The required review states are exactly:
   - `pending_review`
   - `approved`
   - `rejected`
   - `needs_changes`
6. Allow a reviewer to set a decision state and record a rationale / note for
   each decision.
7. Show why a reviewer made a decision (recorded reason text + a selectable
   reason taxonomy derived from the existing master spec review reasons:
   `brand_mismatch`, `wrong_aspect_ratio`, `too_generic`, `compliance_issue`,
   `weak_quality`, `provider_failure`, `needs_disclosure`,
   `ready_for_export`).
8. Maintain an in-session / local review ledger of decisions keyed by
   reviewable item id (see section 12). Persistence is local only in this
   slice unless a later slice explicitly owns durable review storage; PS-035
   does not claim durable, tamper-proof, or production-multi-user storage.
9. Show a clear, persistent boundary message (see section 11) stating that
   approval records the reviewer's workflow decision and does not prove
   semantic truth, legal authenticity, C2PA authenticity, human authorship,
   Object Lock / tamper-proof storage, or production security.
10. Be demo-friendly and judge-friendly: useful in a three-minute demo, no
    generic AI hype copy, no unsupported claims.
11. Work without provider calls and without B2 reads by using local / golden /
    demo fixtures or existing accepted data paths.
12. Not mutate any prior evidence. Any PS-035-owned evidence lives only under
    `docs/evidence/ps-035/`.

## 7. Non-goals

PS-035 must not:

- do not implement product code during the spec-only phase
- do not edit product code under `src/**`
- do not edit frontend code under `apps/**`
- do not edit scripts under `scripts/**`
- do not edit evidence under `docs/evidence/**`
- do not edit `AGENTS.md`
- do not edit `.env*`
- do not edit `render.yaml`
- do not edit requirements files
- do not run the frontend
- do not call any provider
- do not read B2
- do not write B2
- do not stage, commit, or push unless explicitly instructed after validation
- do not imply legal authenticity
- do not imply semantic truth
- do not imply human authorship
- do not imply C2PA authenticity unless implemented and verified
- do not imply Object Lock / tamper-proof storage unless implemented and
  verified
- do not claim browser-side B2 byte verification unless implemented and
  verified
- do not claim public deployment verification unless deployed and tested
- do not claim enterprise security
- do not claim actual spend / latency / quota unless captured
- do not claim provider failures / reruns / variants unless evidenced
- do not invent reviewable items, assets, manifest hashes, or B2 archive
  references that are not present in accepted evidence
- do not build CI, billing, deployment, auth, teams, permissions, or a full
  enterprise DAM
- do not change the golden run canonical constants
- do not change the historical contracts the regression gate verifies
- do not introduce a control name containing `KEY`, `TOKEN`, or `SECRET`
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not run recursive smokes
- do not use generic AI hype copy or unsupported claims

PS-035 only edits this spec file in the spec-only phase. Implementation-phase
candidate files are listed in section 8.

## 8. Implementation Candidate Files

The following are implementation-phase candidates only, clearly marked as
implementation-phase only. They are **not** for this spec-only commit. They
are listed so the implementation phase has a grounded file plan that follows
existing app conventions (each surface has a kebab-case route path, a
PascalCase `.tsx` component, a camelCase `.ts` data module, a smoke script,
and an evidence directory).

Frontend (apps/web):
- `apps/web/src/App.tsx` — register the new route guard
  `isReviewApprovalWorkspacePath()` and render
  `<ReviewApprovalWorkspace variant="page" />` for the path
  `/review-approval-workspace` (or equivalent kebab-case path). The legacy
  `/review` Review Room stays unchanged.
- `apps/web/src/ReviewApprovalWorkspace.tsx` (new) — the workspace component.
  Accepts the existing `variant="page"` convention used by every other surface
  component.
- `apps/web/src/reviewApprovalWorkspace.ts` (new) — the kebab/camel-case data
  module that reads accepted local / golden / demo data (same convention as
  `judgeEvidencePack.ts`, `operationsCockpit.ts`, etc.).
- `apps/web/src/JudgeCockpitHome.tsx` — add a nav link to the new workspace so
  it is reachable from the home surface.
- `apps/web/src/styles.css` — add only the classes needed for the workspace
  (review cards, decision pills, ledger table, boundary footer). No global
  style rewrite.

Backend (src/proofstudio) — optional / read-only reuse only:
- PS-035 is primarily a frontend surface over existing accepted data. If a
  read-only review-state read path is needed, it must reuse the existing
  accepted data paths under `src/proofstudio/api/` and `src/proofstudio/
  provenance/` without calling providers and without reading live B2. No new
  provider wiring, no new B2 client, no new billing path. If no backend
  change is needed, none is made.

Smoke (scripts):
- `scripts/ps035_review_approval_workspace_smoke.py` (new) — the PS-035
  feature smoke. Must reuse `scripts/smoke_lib.py`. Local / static only.

Spec / docs:
- `specs/07-master-spec-plan.md` — implementation-phase cross-reference only
  (register PS-035 acceptance). Must not change any historical item or golden
  constant.
- `specs/08-roadmap-slices.md` — implementation-phase status update only.
- `docs/validation/proofstudio-smoke-harness-v1.md` — implementation-phase
  PS-035 note only, additive, must not weaken any existing PS-034A / PS-035C
  contract.

Evidence:
- `docs/evidence/ps-035/review-approval-workspace-smoke.json` (new) — the only
  evidence PS-035 may write, and only when `--write-evidence` is explicit.

Any edit to `src/proofstudio/**` during implementation requires the backend
change to remain read-only over accepted data and to make no provider call and
no live B2 read.

## 9. Forbidden Files Unless PM-approved Later

PS-035 implementation must not touch without explicit PM approval:

- `AGENTS.md`
- `.env*`
- `render.yaml`
- requirements files
- `docs/evidence/**` paths other than `docs/evidence/ps-035/**`
- any prior-slice evidence prefix (for example `docs/evidence/ps-034a/**`,
  `docs/evidence/ps-035a/**`, `docs/evidence/ps-035b/**`,
  `docs/evidence/ps-035c/**`, `docs/evidence/golden-fixture-digests.json`)
- `scripts/proofstudio_regression_gate.py` (the central gate is not owned by
  PS-035)
- any provider wrapper under `src/proofstudio/providers/**` (PS-035 owns no
  provider behavior)
- any B2 client / storage write path (PS-035 performs no live B2 read or
  write)

The only implementation-phase files allowed without PM approval are those in
section 8. Any other path requires explicit PM approval.

## 10. Review + Approval Workspace Contract

PS-035 defines the following contract for the review + approval workspace.

### 10.1 Surface identity

- It is a dedicated workspace surface, distinct from the legacy `/review`
  Review Room (which stays as the live operator flow).
- It is purely client-side by default: it reads no B2 object, calls no
  provider, exposes no arbitrary `run_id` input for live execution, and
  performs no browser-side B2 byte verification.
- It is sourced from accepted local / golden / demo data and existing
  accepted data paths only.

### 10.2 Review state lifecycle

The required review states are exactly these four, each with a stable machine
value:

- `pending_review` (human label: "Pending Review")
- `approved` (human label: "Approved")
- `rejected` (human label: "Rejected")
- `needs_changes` (human label: "Needs Changes")

Every reviewable item starts in `pending_review` until a reviewer sets a
decision. The UI must show the current state of every item at all times.

### 10.3 Decision + rationale

For each decision the workspace must capture:

- reviewable item id (derived from accepted data; see section 12)
- decision state (one of the four values above)
- decision rationale / note (free text, reviewer-authored)
- optional reason category (one of the master-spec review reasons:
  `brand_mismatch`, `wrong_aspect_ratio`, `too_generic`, `compliance_issue`,
  `weak_quality`, `provider_failure`, `needs_disclosure`,
  `ready_for_export`)
- reviewer label (free text, optional; PS-035 does not implement auth or
  identity verification)
- recorded timestamp (local clock; not a tamper-evident or synchronized clock)

### 10.4 Review ledger

Decisions are recorded in a local review ledger keyed by reviewable item id.
The ledger is a list of decision records. In this slice the ledger is local /
in-session by default; a later slice may own durable review storage. PS-035
must not claim the ledger is durable, tamper-proof, replicated, or
production-multi-user.

### 10.5 Proof linkage

For each reviewable item the workspace must show, as read-only links /
summaries drawn from existing accepted data (whichever exist for that item):

- provenance passport link / summary
- manifest verification status
- B2 archive / rehydrate evidence status
- failure / proof timeline link
- export pack link

If a particular proof artifact does not exist for an item, the UI must show an
honest "not available" state and must not fabricate a link or a verified
status.

### 10.6 Boundary honesty

The workspace must not imply that approval proves anything beyond the
reviewer's workflow decision. The boundary message in section 11 is mandatory
and persistent.

## 11. UI/UX Contract

The review + approval workspace UI must include:

- A clear title: "Review + Approval Workspace" (or an equivalent clear title).
- A list / grid of at least one reviewable item / card / row from accepted
  local / demo data. At minimum, the golden-run asset is a reviewable item.
- For each item, an asset / media summary (asset id, kind, provider / model,
  media type, size, sha256, and url when present in accepted data).
- For each item, a proof / evidence status block (the read-only proof links /
  summaries from section 10.5).
- Reviewer decision controls for each item: set the state to one of the four
  review states, and a field to enter the decision rationale / note.
- An optional reason-category selector using the master-spec reason taxonomy.
- The current decision state shown as a visible pill / badge on every item at
  all times.
- The recorded rationale / note shown on the item after a decision is made.
- A local review ledger view (table / list) of all decisions made in the
  session, so a reviewer / judge can read the approval trail.
- A clear, persistent boundary message that states verbatim (or equivalent):

  > Approval records the reviewer's workflow decision; it does not prove
  > semantic truth, legal authenticity, C2PA authenticity, human authorship,
  > Object Lock / tamper-proof storage, or production security.

- A way back to the home surface (consistent with every other surface, e.g. a
  link to `/`).

UI / UX constraints:

- Must be useful in a three-minute hackathon demo: open workspace -> see a
  reviewable item -> see its proof status -> approve / reject with a reason ->
  read the approval trail -> read the boundary message.
- Must not introduce generic AI hype copy.
- Must not add unsupported claims.
- Must not fabricate media, manifest hashes, archive URIs, or verified
  statuses that are not in accepted data.
- Must follow the existing component convention (`variant="page"`) and the
  existing styles / pills / cards / `JsonExpander` patterns used by the other
  surfaces.

## 12. Data Contract

### 12.1 Source data (read-only inputs)

PS-035 reads accepted local / golden / demo data as immutable inputs. It must
not mutate these and must not change their canonical values. The golden-run
canonical constants PS-035 reuses are the accepted fixed inputs:

- run_id: `run_89d967f9000045efa22ed4cc78cfa67f`
- campaign_id: `camp_bea5161faa6244079d2ee01ce445c259`
- archive_uri: `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json`
- archive_sha256: `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
- rehydrate_source: `b2_rehydrated`
- provider_calls_during_rehydrate: `0`
- no_live_provider_call_during_rehydrate: `true`
- public_deployment_pending: `true`

If the implementation phase discovers a different accepted golden value in
`docs/evidence/demo/golden-demo-run.json` or
`docs/evidence/golden-fixture-digests.json`, it must use the accepted value
and must not invent a new one.

Acceptable source files for reviewable-item data include (read-only):

- `docs/evidence/demo/golden-demo-run.json`
- the accepted per-slice evidence under `docs/evidence/ps-021/**` through
  `docs/evidence/ps-034/**`
- the existing Provenance Passport `review_room_summary` block already
  produced by accepted paths

### 12.2 Reviewable item shape

A reviewable item is derived from accepted data and must expose:

- `item_id` (stable; derived from asset id / run id in accepted data)
- `asset_summary` (kind, provider, model, media type, size, sha256, url when
  present)
- `initial_state` (always `pending_review` for a fresh session)
- `proof_status` (passport / manifest / archive-rehydrate / failure-timeline /
  export-pack status, each "available" or "not_available")

### 12.3 Decision record shape

A decision record (PS-035-owned local data) must be JSON-serializable and
include:

- `item_id`
- `decision_state` (one of `pending_review`, `approved`, `rejected`,
  `needs_changes`)
- `reason_category` (one of the master-spec reasons or `null`)
- `rationale` (string, reviewer-authored)
- `reviewer_label` (string or `null`)
- `recorded_at` (ISO-8601 local timestamp)

### 12.4 Evidence report schema rule

The PS-035 evidence report must follow the harness schema rule: boolean fields
remain booleans and detail / list fields use explicit detail names. A field
whose name implies a boolean success flag must remain a boolean. List fields
must use explicit detail names such as `_ids`, `_details`, or `_failures` (see
section 13).

## 13. Evidence Contract

PS-035 owns exactly one evidence directory: `docs/evidence/ps-035/`.

- A feature smoke may write only its own evidence, and only when
  `--write-evidence` is explicit. The default PS-035 smoke behavior is
  non-mutating local validation.
- PS-035 must not write any file outside `docs/evidence/ps-035/`.
- PS-035 must not mutate any prior-slice evidence (every prior evidence prefix
  is guarded by `scripts/smoke_lib.py` and
  `scripts/proofstudio_regression_gate.py`).
- Any PS-035-owned evidence file must live under `docs/evidence/ps-035/`, for
  example `docs/evidence/ps-035/review-approval-workspace-smoke.json`.

The PS-035 evidence report should carry measured fields such as:

- `ok` (boolean; true only when every measured field is truthful and no
  forbidden overclaim or forbidden file change is present)
- `slice_id: ps035`
- `checked_at`
- `route_registered` (boolean; the `/review-approval-workspace` route guard +
  component render are present in `apps/web/src/App.tsx`)
- `component_present` (boolean; `ReviewApprovalWorkspace` component exists)
- `data_module_present` (boolean)
- `nav_link_present` (boolean)
- `review_states_defined` (boolean; all four states present)
- `boundary_message_present` (boolean)
- `no_provider_calls` (boolean)
- `no_b2_reads` (boolean)
- `no_b2_writes` (boolean)
- `prior_evidence_clean` (boolean)
- `no_hidden_git_flags_h` (boolean)
- `no_hidden_git_flags_S` (boolean)
- `git_diff_check_clean` (boolean)
- `truth_boundary_preserved` (boolean)
- `no_forbidden_overclaims` (boolean)
- `failures` (list; empty on success)

`ok` must be `false` if `failures` is non-empty. Boolean fields must remain
booleans; list / detail fields must use explicit detail names. This evidence
file is created only in the implementation phase and only when
`--write-evidence` is explicit.


### Verbatim implementation/audit contract strings

The PS-035 implementation and smoke validation must preserve these exact strings
so the review workspace contract is deterministic and not dependent on
close-enough wording:

- notes
- B2 evidence
- does not prove legal authenticity
- does not prove C2PA authenticity
- does not prove human authorship
- does not prove Object Lock
- does not prove production security
- no broad B2 reads
- hidden Git flags h and S
- do not claim Object Lock / tamper-proof storage unless implemented and verified
- do not claim browser-side B2 byte verification unless implemented and verified
- do not claim actual spend/latency/quota unless captured
- do not claim provider failures/reruns/variants unless evidenced

## 14. Smoke / Validation Contract

PS-035 ships one feature smoke: `scripts/ps035_review_approval_workspace_smoke.py`.

The PS-035 feature smoke must:

- validate only the PS-035 slice (no recursive smokes; must never launch
  another feature smoke as a subprocess)
- read checked-in prior evidence as immutable inputs
- write only its own evidence file under `docs/evidence/ps-035/`, and only when
  `--write-evidence` is explicit
- never call a provider
- never read arbitrary B2 objects
- never run the frontend typecheck / build (that belongs to the central gate)
- reuse `scripts/smoke_lib.py` for shared validation logic
- verify the route is registered in `apps/web/src/App.tsx`
- verify the `ReviewApprovalWorkspace` component exists
- verify the four review states are defined
- verify the boundary message is present
- verify no hidden Git flags `h` or `S` with an explicit h/S checker that
  reads `git ls-files -v` and fails when `line[0]` is `h` or `S` (a
  lowercase-only marker check is not sufficient because it misses uppercase
  `S` skip-worktree)
- verify `git diff --check` is clean
- verify prior evidence is unchanged
- verify no forbidden overclaims are introduced

The PS-035 feature smoke must support these standard flags:

- `--check-only` (default: non-mutating local validation; no evidence file is
  written)
- `--write-evidence` (write only `docs/evidence/ps-035/` evidence)
- `--no-frontend`

Default PS-035 smoke behavior is non-mutating local validation
(`--check-only`).

The smoke must not contain the bad lowercase-only hidden-flag grep command
lowercase-only marker check and must not rely on a lowercase-only marker check.
The hidden-Git-flags check must be the explicit `h` / `S` checker.

PS-035 smoke performs no provider calls, no B2 reads, and no B2 writes.

## 15. Regression Gate Contract

The central regression gate remains the single cross-slice release-readiness
gate and is non-mutating by default. PS-035 does not own or modify the central
gate.

Normal PS-035 release validation command:

```
python scripts/proofstudio_regression_gate.py --current ps035 --frontend --report-out /tmp/proofstudio-release-report.json
```

Contract-only gate (no frontend):

```
python scripts/proofstudio_regression_gate.py --current ps035 --no-frontend
```

- The gate runs `npm run typecheck` and `npm run build` in `apps/web` exactly
  once per invocation, and only when `--frontend` is passed. PS-035 feature
  smoke must never trigger nested frontend builds.
- The gate must not write the canonical PS-034A report. `--write-report` is
  rejected for `--current ps035` (PS-035C accepted behavior).
- Running the gate for `ps035` must leave all prior-slice evidence unchanged.
- No recursive smokes: the gate never executes a feature smoke.

Canonical PS-034A regeneration (unchanged, owned by PS-034A only):

```
python scripts/proofstudio_regression_gate.py --current ps034a --write-report
```

## 16. Truth Boundary

ProofStudio proves what the pipeline did. The review + approval workspace is a
human decision surface, not a legal authenticity system.

PS-035 approval means "approved by this workflow / demo UI." It does not mean
legally verified, factually true, human-authored, C2PA-authentic,
tamper-proof, or production-secure.

PS-035 must preserve these truth-boundary red lines verbatim across the spec,
the UI, and any evidence report:

- do not claim legal authenticity
- do not claim semantic truth
- do not claim human authorship
- do not claim C2PA unless implemented and verified
- do not claim Object Lock / tamper-proof storage unless implemented and
  verified
- do not claim browser-side B2 byte verification unless implemented and
  verified
- do not claim public deployment verification unless deployed and tested
- do not claim enterprise security
- do not claim actual spend / latency / quota unless captured
- do not claim provider failures / reruns / variants unless evidenced

PS-035 does not prove product correctness, production security, B2
immutability, tamper-proof storage, real billing API integration, billing
behavior, CI enforcement, or deployment readiness. No PS-035 artifact may
imply any of these.

The review ledger is local / in-session in this slice. PS-035 must not claim
the ledger is durable, tamper-proof, replicated, audited, or
production-multi-user.

## 17. Risks

PS-035 must record the following risks with mitigations:

- overclaim risk
  - risk: the workspace or its copy implies approval proves legal
    authenticity, semantic truth, human authorship, C2PA authenticity, Object
    Lock / tamper-proof storage, or production security.
  - mitigation: the persistent boundary message (section 11) is mandatory; the
    truth-boundary red lines (section 16) are preserved verbatim; the evidence
    report carries `no_forbidden_overclaims`.
- invented-evidence risk
  - risk: the workspace fabricates an asset, manifest hash, archive URI, or
    verified status not present in accepted data.
  - mitigation: all reviewable-item data is sourced read-only from accepted
    local / golden / demo data; missing proof artifacts show an honest
    "not available" state.
- evidence-mutation risk
  - risk: the PS-035 smoke or the central gate run overwrites prior-slice
    evidence.
  - mitigation: PS-035 writes only `docs/evidence/ps-035/`; the gate is
    non-mutating by default; prior evidence prefixes are guarded.
- live-call risk
  - risk: the workspace triggers a provider call or a live B2 read.
  - mitigation: the workspace is purely client-side over accepted data; the
    smoke enforces `no_provider_calls`, `no_b2_reads`, `no_b2_writes`.
- hidden-Git-flags risk
  - risk: a session uses `assume-unchanged`, `skip-worktree`, or
    `git update-index` / `update-index` to mask a dirty tree.
  - mitigation: the operating law forbids these verbatim; the smoke uses the
    explicit `h` / `S` checker over `git ls-files -v` and fails on `line[0]`
    being `h` or `S`.
- scope-creep risk
  - risk: PS-035 expands into CI, billing, deployment, auth, teams,
    permissions, or a full DAM.
  - mitigation: section 7 lists these as non-goals; section 9 forbids the
    relevant paths.
- durability-misunderstanding risk
  - risk: a reviewer or judge assumes the local review ledger is durable /
    tamper-proof.
  - mitigation: section 10 and section 16 state plainly that the ledger is
    local / in-session in this slice and is not tamper-proof.
- recursive-smoke risk
  - risk: the PS-035 smoke launches another feature smoke.
  - mitigation: the smoke must never launch another feature smoke as a
    subprocess; the central gate is the only cross-slice validator.

## 18. Acceptance Criteria

PS-035 (spec-only phase) is accepted only when:

- this spec exists at `specs/51-ps-035-review-approval-workspace.md`
- only this spec file is changed in the spec-only phase
- the branch `ps-035/review-approval-workspace` starts from
  `origin/accepted/proofstudio` at commit
  `964cc404fe1fa6a0f046b5130aa01b2425a1d7df` (the merge-base equals that
  commit)
- the product scope is clear and does not expand into CI, billing, deployment,
  provider calls, or B2 live reads
- the review states (`pending_review`, `approved`, `rejected`,
  `needs_changes`) are specified
- the proof / evidence display contract (section 10.5, section 11, section 12)
  is specified
- the decision rationale / note capture is specified
- the truth boundary (section 16) is explicit and the boundary message is
  specified
- the implementation candidate files (section 8) are listed, but no
  implementation is done in this phase
- the validation plan uses the PS-035 feature smoke plus the central
  regression gate (sections 14 and 15)
- no evidence mutation occurs in this phase
- no hidden Git flags `h` or `S` are present (verified by the explicit h/S
  checker over `git ls-files -v`)
- `git diff --check` is clean
- no staging, commit, or push occurs until PM approval

Implementation-phase acceptance (for reference, not this phase) additionally
requires: the route is registered; the component + data module exist; the nav
link exists; the four review states and the boundary message are present; the
PS-035 smoke passes in `--check-only` (default) and writes only
`docs/evidence/ps-035/**` under `--write-evidence`; the central gate passes
for `--current ps035`; no provider call, no B2 read, no B2 write occurs; prior
evidence is unchanged; no forbidden overclaim is introduced.

## 19. Rollback

Rollback of the PS-035 spec-only phase is a single revert of this spec commit,
because only `specs/51-ps-035-review-approval-workspace.md` is changed in this
phase.

Future implementation rollback must restore the pre-PS-035 state of the edited
files in section 8. Specifically:

- remove the `/review-approval-workspace` route guard and render from
  `apps/web/src/App.tsx`
- remove `apps/web/src/ReviewApprovalWorkspace.tsx`
- remove `apps/web/src/reviewApprovalWorkspace.ts`
- revert `apps/web/src/JudgeCockpitHome.tsx` (nav link) and
  `apps/web/src/styles.css` (workspace classes) to pre-PS-035 state
- remove `scripts/ps035_review_approval_workspace_smoke.py`
- remove `docs/evidence/ps-035/` if it was added
- revert the additive cross-references in `specs/07-master-spec-plan.md`,
  `specs/08-roadmap-slices.md`, and
  `docs/validation/proofstudio-smoke-harness-v1.md` to pre-PS-035 state

Rollback of PS-035 must not touch any evidence under `docs/evidence/**` other
than `docs/evidence/ps-035/`, must not touch the central gate
(`scripts/proofstudio_regression_gate.py`), `scripts/smoke_lib.py`, `AGENTS.md`,
`.env*`, `render.yaml`, requirements files, any provider wrapper, or any B2
storage path. Rollback is isolated and reversible because PS-035 is a
self-contained workspace surface over existing accepted data; it does not
change provider behavior, B2 behavior, billing behavior, or deployment
topology.
