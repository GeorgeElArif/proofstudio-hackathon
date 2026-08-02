# PS-036 — Archive / Rehydrate / B2 Audit Vault

## 1. Status

PS-036 — Archive / Rehydrate / B2 Audit Vault is currently:

- Spec only.
- Implementation pending. No product code, frontend code, backend code,
  scripts, evidence, AGENTS.md, `.env*`, `render.yaml`, or requirements files
  are changed during this phase.

PS-036 must not be implemented, and no implementation files may be changed,
until this spec is accepted by the PM. The latest accepted base is
`accepted/proofstudio` commit
`1f6d24f526b5396a6c6e537bec7485c401a02534`.

This spec-only commit touches only this file:
`specs/53-ps-036-archive-rehydrate-b2-audit-vault.md`.

PS-036 must not call live providers, must not read or write live B2, must not
perform broad B2 scans, must not mutate any evidence, must not run the
frontend, must not stage, commit, or push, and must not print secrets during
this phase. PS-036 obeys the root `AGENTS.md` operating law and the validation
policy in `docs/validation/proofstudio-smoke-harness-v1.md`.

## 2. Purpose

PS-036 turns ProofStudio's existing archive / rehydrate / B2 evidence into a
clear, single B2 Audit Vault surface. The goal is to make Backblaze B2 feel
like the durable system of record for the verified golden run, using accepted
checked-in evidence and golden / demo fixtures, so a reviewer or judge can see
in one place:

- what was archived
- where the archive reference lives
- what hash / digest is recorded
- what can be rehydrated
- whether rehydrate used live providers
- whether B2 evidence is present
- what is locally verified versus not verified
- what remains not claimed

The B2 Audit Vault is an evidence-reading surface over what the pipeline
already recorded. It is a vault of recorded evidence, not a live B2 object
fetcher, not a browser-side B2 byte verifier, and not a legal authenticity
system. "B2 system of record" in PS-036 means Backblaze B2 is surfaced as the
durable archive behind the verified golden run; it does **not** mean "Object
Lock," "tamper-proof storage," "browser-side B2 byte verification,"
"production security," "legal authenticity," "semantic truth," or "human
authorship."

PS-036 proves only what the pipeline recorded. It does not prove semantic
truth, legal authenticity, C2PA authenticity, human authorship, Object Lock /
tamper-proof storage, browser-side B2 byte verification, public deployment
verification, or enterprise security. PS-036 does not claim live B2
availability unless a live B2 check is explicitly implemented and approved in a
later slice.

## 3. Root Cause / Product Gap

Today ProofStudio already records strong archive / rehydrate / B2 evidence,
but it is spread across many surfaces and many checked-in JSON files:

- `apps/web/src/B2EvidenceExplorer.tsx` (PS-026) shows archive URI, archive
  SHA-256, rehydrate source, and zero provider calls during rehydrate, but it
  does not frame B2 as a single audit vault of record.
- `apps/web/src/B2RehydrateComparison.tsx` (PS-029) compares golden run vs B2
  archive vs rehydrated evidence, but it is a comparison story, not a vault of
  recorded references and digests.
- `apps/web/src/ManifestVerificationPanel.tsx` (PS-028) verifies manifest
  field consistency, including the manifest hash, but it is a manifest surface,
  not an archive / B2 vault.
- `apps/web/src/JudgeEvidencePack.tsx` (PS-031) exports a portable pack, but
  it is a take-away pack, not a standing audit vault.
- `apps/web/src/ReviewApprovalWorkspace.tsx` (PS-035) is a human decision
  surface, not an archive / B2 record surface.

Each existing page shows what the pipeline did, but none of them frames
Backblaze B2 as the single durable system of record where a reviewer or judge
can read, in one place: the archive reference, the archive SHA-256 / digest,
the manifest reference / hash when present, the rehydrate source, whether
rehydrate used a live provider, the B2 evidence status, the local verification
status, an honest not-claimed / unknown status, and a clear truth-boundary
panel.

PS-036 closes that gap by adding a dedicated Archive / Rehydrate / B2 Audit
Vault surface that reuses accepted checked-in evidence as read-only inputs and
the existing B2 Evidence Explorer / B2 Rehydrate Comparison data modules
(`apps/web/src/b2Evidence.ts`, `apps/web/src/b2RehydrateComparison.ts`),
without calling providers, without reading live B2, without writing B2, and
without broad B2 scans.

## 4. User Story

As a reviewer (designer, marketer, reviewer, client, or judge), I want a
single Archive / Rehydrate / B2 Audit Vault where I can read the verified
golden run's archive reference, the recorded archive SHA-256 / digest, the
manifest reference / hash when present, what can be rehydrated, whether
rehydrate used a live provider, the B2 evidence status, and exactly what is
locally verified versus not verified — so that Backblaze B2 reads as the
durable system of record behind the run, not a hidden backend detail.

As a demo presenter, I want that vault to be useful in a three-minute
hackathon demo: a clear title that names the vault, the archive reference and
SHA-256 front and center, the manifest hash when present, the rehydrate source
and zero-provider-call proof, the B2 evidence status, the local verification
status, an honest not-claimed / unknown panel, and a persistent
truth-boundary panel — all working offline from accepted local / golden /
demo fixtures, with no live provider calls, no live B2 reads, no B2 writes,
and no broad B2 scans.

## 5. Current Accepted Base

The current accepted base for PS-036 is:

- branch: `accepted/proofstudio`
- commit: `1f6d24f526b5396a6c6e537bec7485c401a02534`
- remote: `origin/accepted/proofstudio` is at the same commit
- this is the post-PS-035 / post-PS-035e accepted state: the root `AGENTS.md`
  operating law is already in place (PS-035D); the accepted-base-pointer-drift
  guard is in place (PS-035E); the central regression gate is non-mutating by
  default from PS-035C; the golden-fixture digest freeze is in place from
  PS-035B; the golden-run manifest carries a real non-null `manifest_uri` and
  a real 64-hex `manifest_hash` from PS-035A; the Review + Approval Workspace
  is in place from PS-035.

PS-036 must start from `origin/accepted/proofstudio`, not from `main`.

Relevant accepted facts at this base that PS-036 reuses as read-only inputs
(PS-036 must not mutate these and must not change their values):

- the central regression gate
  (`scripts/proofstudio_regression_gate.py`) supports `--current`,
  `--frontend`, `--no-frontend`, `--check-only`, `--report-out`, and
  `--write-report` (PS-035C accepted)
- the gate is non-mutating by default for any current slice that is not
  PS-034A (PS-035C accepted)
- the root `AGENTS.md` operating law exists at the repository root
  (PS-035D accepted)
- the accepted-base-pointer-drift guard exists (PS-035E accepted)
- the golden-fixture digest freeze exists at
  `docs/evidence/golden-fixture-digests.json` (PS-035B accepted)
- the golden-run manifest carries a real non-null `manifest_uri` and a real
  64-hex `manifest_hash` (PS-035A accepted)
- the golden run canonical constants are fixed inputs (see section 12)
- the B2 Evidence Explorer data module `apps/web/src/b2Evidence.ts` and the
  B2 Rehydrate Comparison data module `apps/web/src/b2RehydrateComparison.ts`
  already expose the verified golden B2 archive / rehydrate constants
- the accepted evidence files listed in section 12.1 already record the
  verified durable values PS-036 must surface

## 6. Scope

PS-036 is a product slice. It adds a dedicated Archive / Rehydrate / B2 Audit
Vault surface. It is local / static by default: it must work without live
provider calls, without live B2 reads, without B2 writes, and without broad
B2 scans, by using accepted local / golden / demo fixtures and existing
accepted data paths / data modules.

PS-036 must:

1. Add a dedicated Archive / Rehydrate / B2 Audit Vault route / page /
   surface using existing app conventions (client-side route guard in
   `apps/web/src/App.tsx`, a PascalCase component, and a camelCase data module
   — see section 8).
2. Frame Backblaze B2 as the durable system of record for the verified golden
   run, using accepted checked-in evidence and golden / demo fixtures.
3. Show the archive reference (the recorded B2 archive URI) for the golden
   run.
4. Show the archive SHA-256 / digest recorded for the archive reference.
5. Show the manifest reference / hash when present; if no manifest reference /
   hash is present in accepted data, show an honest "not available" state and
   do not fabricate one.
6. Show what can be rehydrated (rehydrate source / durable source).
7. Show whether rehydrate used live providers (provider calls during
   rehydrate, no live provider call during rehydrate).
8. Show the B2 evidence status (present / absent over accepted evidence).
9. Show the local verification status (what is locally verified vs not
   verified).
10. Show an honest not-claimed / unknown status panel.
11. Show a clear, persistent truth-boundary panel (see section 11).
12. Be demo-friendly and judge-friendly: useful in a three-minute demo, no
    generic AI hype copy, no unsupported claims.
13. Work without provider calls, without live B2 reads, without B2 writes,
    and without broad B2 scans, by using accepted local / golden / demo
    fixtures or existing accepted data paths.
14. Not mutate any prior evidence. Any PS-036-owned evidence lives only under
    `docs/evidence/ps-036/`.

## 7. Non-goals

PS-036 must not:

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
- do not read B2 (no live B2 reads)
- do not write B2 (no B2 writes)
- do not perform broad B2 scans
- do not claim browser-side B2 byte verification unless implemented and
  verified
- do not claim live B2 availability unless a live B2 check is explicitly
  implemented and approved
- do not stage, commit, or push unless explicitly instructed after validation
- do not imply legal authenticity
- do not imply semantic truth
- do not imply human authorship
- do not imply C2PA authenticity unless implemented and verified
- do not imply Object Lock / tamper-proof storage unless implemented and
  verified
- do not claim public deployment verification unless deployed and tested
- do not claim enterprise security
- do not claim actual spend / latency / quota unless captured
- do not claim provider failures / reruns / variants unless evidenced
- do not invent archive references, digests, manifest hashes, or rehydrate
  values that are not present in accepted evidence
- do not build CI, billing, deployment, auth, teams, permissions, or a full
  enterprise DAM
- do not change the golden run canonical constants
- do not change the historical contracts the regression gate verifies
- do not introduce a control name containing `KEY`, `TOKEN`, or `SECRET`
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not run recursive smokes
- do not use generic AI hype copy or unsupported claims

PS-036 only edits this spec file in the spec-only phase. Implementation-phase
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
  `isB2AuditVaultPath()` and render `<B2AuditVault variant="page" />` for the
  path `/b2-audit-vault` (preferred) or `/archive-rehydrate-b2-audit-vault`
  (acceptable alternative). The existing `/b2-evidence`,
  `/b2-rehydrate-comparison`, and `/manifest-verification` routes stay
  unchanged.
- `apps/web/src/B2AuditVault.tsx` (new) — the vault component. Accepts the
  existing `variant="page"` convention used by every other surface component.
- `apps/web/src/b2AuditVault.ts` (new) — the camelCase data module that reads
  accepted local / golden / demo data and reuses the existing
  `apps/web/src/b2Evidence.ts` and `apps/web/src/b2RehydrateComparison.ts`
  constants read-only (same convention as `b2Evidence.ts`,
  `b2RehydrateComparison.ts`, `operationsCockpit.ts`, etc.).
- `apps/web/src/JudgeCockpitHome.tsx` — add a nav link to the new vault so it
  is reachable from the home surface.
- `apps/web/src/styles.css` — add only the classes needed for the vault
  (vault header, archive reference + digest rows, manifest row, rehydrate /
  provider-call rows, B2 evidence status, local verification status,
  not-claimed / unknown panel, truth-boundary panel). No global style rewrite.

Backend (src/proofstudio) — optional / read-only reuse only:
- PS-036 is primarily a frontend surface over existing accepted data. If a
  read-only archive / rehydrate evidence read path is needed, it must reuse
  the existing accepted data paths under `src/proofstudio/api/` and
  `src/proofstudio/provenance/` without calling providers and without reading
  live B2. No new provider wiring, no new B2 client, no new B2 write path, no
  new broad B2 scan path. If no backend change is needed, none is made.

Smoke (scripts):
- `scripts/ps036_archive_rehydrate_b2_audit_vault_smoke.py` (new) — the PS-036
  feature smoke. Must reuse `scripts/smoke_lib.py` for shared validation logic
  and must implement its own explicit `h` / `S` hidden-Git-flags checker (see
  section 14). Local / static only.

Spec / docs:
- `specs/07-master-spec-plan.md` — implementation-phase cross-reference only
  (register PS-036 acceptance). Must not change any historical item or golden
  constant.
- `specs/08-roadmap-slices.md` — implementation-phase status update only.
- `docs/validation/proofstudio-smoke-harness-v1.md` — implementation-phase
  PS-036 note only, additive, must not weaken any existing PS-034A / PS-035C
  contract.
- `docs/ps-036-archive-rehydrate-b2-audit-vault-proof.md` (new) — the PS-036
  proof doc.

Evidence:
- `docs/evidence/ps-036/archive-rehydrate-b2-audit-vault-report.json` (new) —
  the only evidence PS-036 may write, and only when `--write-evidence` is
  explicit.

Any edit to `src/proofstudio/**` during implementation requires the backend
change to remain read-only over accepted data and to make no provider call and
no live B2 read.

## 9. Forbidden Files Unless PM-approved Later

PS-036 implementation must not touch without explicit PM approval:

- `AGENTS.md`
- `.env*`
- `render.yaml`
- requirements files
- `docs/evidence/**` paths other than `docs/evidence/ps-036/**`
- any prior-slice evidence prefix (for example `docs/evidence/ps-021/**`,
  `docs/evidence/ps-026/**`, `docs/evidence/ps-029/**`,
  `docs/evidence/ps-031/**`, `docs/evidence/ps-035/**`,
  `docs/evidence/ps-035a/**`, `docs/evidence/ps-035b/**`,
  `docs/evidence/demo/golden-demo-run.json`,
  `docs/evidence/golden-fixture-digests.json`)
- `scripts/proofstudio_regression_gate.py` (the central gate is not owned by
  PS-036)
- `scripts/smoke_lib.py` (shared library; PS-036 must not mutate shared
  validation behavior)
- any provider wrapper under `src/proofstudio/providers/**` (PS-036 owns no
  provider behavior)
- any B2 client / storage write path (PS-036 performs no live B2 read, no B2
  write, and no broad B2 scan)

The only implementation-phase files allowed without PM approval are those in
section 8. Any other path requires explicit PM approval.

## 10. Archive / Rehydrate / B2 Audit Vault Product Contract

PS-036 defines the following contract for the Archive / Rehydrate / B2 Audit
Vault.

### 10.1 Surface identity

- It is a dedicated vault surface, distinct from the B2 Evidence Explorer
  (PS-026), the B2 Rehydrate Comparison (PS-029), and the Manifest
  Verification Panel (PS-028). Those surfaces stay unchanged.
- It is purely client-side by default: it reads no B2 object, calls no
  provider, exposes no arbitrary `run_id` input for live execution, performs
  no browser-side B2 byte verification, and performs no broad B2 scan.
- It is sourced from accepted local / golden / demo data and existing accepted
  data paths / data modules only.
- It frames Backblaze B2 as the durable system of record for the verified
  golden run.

### 10.2 Required vault records

For the verified golden run the vault must show at least these records, each
sourced verbatim from accepted evidence (see section 12):

- `archive_reference` — the recorded B2 archive URI (the archive reference)
- `archive_sha256` — the archive SHA-256 / digest recorded for the archive
  reference
- `manifest_reference` / `manifest_hash` — the manifest reference / hash when
  present; if absent in accepted data, an honest "not available" state
- `rehydrate_source` — what can be rehydrated / the durable source
- `provider_calls_during_rehydrate` — whether rehydrate used live providers
  (count)
- `no_live_provider_call_during_rehydrate` — whether no live provider call
  happened during rehydrate (boolean)
- `b2_evidence_status` — whether B2 evidence is present over accepted evidence
- `local_verification_status` — what is locally verified versus not verified
- `not_claimed_status` — the honest not-claimed / unknown status

If a particular record does not exist in accepted data, the UI must show an
honest "not available" / "not verified" state and must not fabricate a value.

### 10.3 Verification honesty

The vault must distinguish clearly between:

- what is locally verified against accepted checked-in evidence (archive URI,
  archive SHA-256, rehydrate source, provider-call count, manifest hash when
  present)
- what is not verified (live B2 availability, browser-side B2 byte
  verification, Object Lock / tamper-proof storage, public deployment)
- what is not claimed (semantic truth, legal authenticity, C2PA
  authenticity, human authorship, production security)

### 10.4 Boundary honesty

The vault must not imply that B2 as system of record proves anything beyond
what the pipeline recorded. The truth-boundary panel in section 11 is
mandatory and persistent.

## 11. UI/UX Contract

The Archive / Rehydrate / B2 Audit Vault UI must include:

- A clear title: "Archive / Rehydrate / B2 Audit Vault" (or an equivalent
  clear title), with a "Backblaze B2 system of record" positioning line.
- A vault header / hero that frames B2 as the durable system of record behind
  the verified golden run, sourced from accepted checked-in evidence.
- An archive reference record: the recorded B2 archive URI, shown verbatim,
  with an explicit "archive reference" label.
- An archive SHA-256 / digest record: the recorded archive SHA-256, shown
  verbatim, with an explicit "archive sha256" label.
- A manifest record: the manifest reference / hash when present, shown
  verbatim, with an explicit "manifest hash" label; if absent, an honest
  "not available" state.
- A rehydrate record: the rehydrate source, with an explicit "rehydrate
  source" label.
- A provider-call record: `provider_calls_during_rehydrate` and
  `no_live_provider_call_during_rehydrate`, with explicit "provider calls
  during rehydrate" and "no live provider call during rehydrate" labels.
- A B2 evidence status record: whether B2 evidence is present over accepted
  evidence, with an explicit "B2 evidence status" framing.
- A local verification status record: what is locally verified versus not
  verified, with an explicit "local verification" framing and an explicit
  "not live B2 verification" note.
- A not-claimed / unknown status panel.
- A clear, persistent truth-boundary panel that states verbatim (or
  equivalent):

  > The B2 Audit Vault shows what the pipeline recorded: the archive
  > reference, archive SHA-256, manifest hash when present, rehydrate source,
  > and zero provider calls during rehydrate. It is not live B2 verification.
  > It is not Object Lock. It is not tamper-proof. It is not production
  > security. It is not legal authenticity. It is not semantic truth.

- A way back to the home surface (consistent with every other surface, e.g. a
  link to `/`), plus cross-links to the B2 Evidence Explorer, the B2 Rehydrate
  Comparison, the Manifest Verification Panel, and the golden Provenance
  Passport (no broken internal links).

UI / UX constraints:

- Must be useful in a three-minute hackathon demo: open vault -> read archive
  reference + SHA-256 -> read manifest hash when present -> read rehydrate
  source + zero provider calls -> read B2 evidence status -> read local
  verification status -> read the not-claimed panel -> read the truth-boundary
  panel.
- Must not introduce generic AI hype copy.
- Must not add unsupported claims.
- Must not fabricate archive references, digests, manifest hashes, or verified
  statuses that are not in accepted data.
- Must follow the existing component convention (`variant="page"`) and the
  existing styles / pills / cards / `JsonExpander` patterns used by the other
  surfaces.

## 12. Data Contract

### 12.1 Source data (read-only inputs)

PS-036 reads accepted local / golden / demo data as immutable inputs. It must
not mutate these and must not change their canonical values. The golden-run
canonical constants PS-036 reuses are the accepted fixed inputs:

- run_id: `run_89d967f9000045efa22ed4cc78cfa67f`
- campaign_id: `camp_bea5161faa6244079d2ee01ce445c259`
- archive_reference (archive_uri):
  `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json`
- archive_sha256:
  `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
- manifest_reference (manifest_uri): `docs/evidence/ps-035a/manifest-fixture.json`
- manifest_hash:
  `438fabca46481a232373067eedb6d0e3a684c8ed513410dfe2047e3b4950022f`
- rehydrate_source: `b2_rehydrated`
- provider_calls_during_rehydrate: `0`
- no_live_provider_call_during_rehydrate: `true`
- public_deployment_pending: `true`

If the implementation phase discovers a different accepted golden value in
`docs/evidence/demo/golden-demo-run.json` or
`docs/evidence/golden-fixture-digests.json`, it must use the accepted value
and must not invent a new one.

Acceptable source files for vault records (read-only):

- `docs/evidence/demo/golden-demo-run.json`
- `docs/evidence/golden-fixture-digests.json`
- `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json`
- `docs/evidence/ps-026/b2-evidence-explorer-smoke.json`
- `docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json`
- `docs/evidence/ps-031/export-campaign-pack-v2-smoke.json`
- `docs/evidence/ps-035/review-approval-workspace-report.json`
- the existing B2 Evidence Explorer data module `apps/web/src/b2Evidence.ts`
  and the existing B2 Rehydrate Comparison data module
  `apps/web/src/b2RehydrateComparison.ts` (read-only reuse)

### 12.2 Vault record shape

A vault record is derived from accepted data and must expose:

- `record_key` (stable; one of the keys in section 10.2)
- `value` (the accepted value, verbatim)
- `available` (boolean; false when the record is honestly not present in
  accepted data)
- `source_paths` (the accepted evidence files this value is read from)
- `verification` (one of `locally_verified`, `not_verified`, `not_claimed`)

### 12.3 Evidence report schema rule

The PS-036 evidence report must follow the harness schema rule: boolean fields
remain booleans and detail / list fields use explicit detail names. A field
whose name implies a boolean success flag must remain a boolean. List fields
must use explicit detail names such as `_ids`, `_details`, or `_failures` (see
section 13).

## 13. Evidence Contract

PS-036 owns exactly one evidence directory: `docs/evidence/ps-036/`.

- A feature smoke may write only its own evidence, and only when
  `--write-evidence` is explicit. The default PS-036 smoke behavior is
  non-mutating local validation.
- PS-036 must not write any file outside `docs/evidence/ps-036/`.
- PS-036 must not mutate any prior-slice evidence (every prior evidence prefix
  is guarded by `scripts/smoke_lib.py` and
  `scripts/proofstudio_regression_gate.py`).
- The PS-036 evidence file is
  `docs/evidence/ps-036/archive-rehydrate-b2-audit-vault-report.json`.

The PS-036 evidence report must carry these boolean fields (booleans as
booleans; `failures` as a list):

- `ok` (boolean; true only when every measured field is truthful and no
  forbidden overclaim or forbidden file change is present)
- `slice_id`: `ps036`
- `route_present` (boolean; the `/b2-audit-vault` route guard + component
  render are present in `apps/web/src/App.tsx`)
- `vault_component_present` (boolean; `B2AuditVault` component exists)
- `vault_data_module_present` (boolean; `b2AuditVault.ts` exists)
- `archive_reference_present` (boolean)
- `archive_sha256_present` (boolean)
- `manifest_hash_present_or_honestly_unavailable` (boolean)
- `rehydrate_source_present` (boolean)
- `provider_calls_during_rehydrate_present` (boolean)
- `no_live_provider_call_during_rehydrate_present` (boolean)
- `b2_evidence_status_present` (boolean)
- `local_verification_status_present` (boolean)
- `not_claimed_status_present` (boolean)
- `boundary_copy_present` (boolean)
- `no_provider_calls` (boolean)
- `no_live_b2_reads` (boolean)
- `no_b2_writes` (boolean)
- `no_broad_b2_scans` (boolean)
- `no_recursive_smokes` (boolean)
- `no_hidden_git_flags_h` (boolean)
- `no_hidden_git_flags_S` (boolean)
- `truth_boundary_preserved` (boolean)
- `no_forbidden_overclaims` (boolean)
- `prior_evidence_clean` (boolean)
- `failures` (list; empty on success)

`ok` must be `false` if `failures` is non-empty. Boolean fields must remain
booleans; list / detail fields must use explicit detail names. This evidence
file is created only in the implementation phase and only when
`--write-evidence` is explicit.

### Verbatim implementation/audit contract strings

The PS-036 implementation and smoke validation must preserve these exact
strings so the B2 Audit Vault contract is deterministic and not dependent on
close-enough wording:

- Archive / Rehydrate / B2 Audit Vault
- B2 system of record
- archive reference
- archive sha256
- manifest hash
- rehydrate source
- provider calls during rehydrate
- no live provider call during rehydrate
- local verification
- not live B2 verification
- not Object Lock
- not tamper-proof
- not production security
- not legal authenticity
- not semantic truth
- notes
- B2 evidence
- no broad B2 reads
- hidden Git flags h and S
- do not claim Object Lock / tamper-proof storage unless implemented and verified
- do not claim browser-side B2 byte verification unless implemented and verified
- do not claim actual spend/latency/quota unless captured
- do not claim provider failures/reruns/variants unless evidenced

## 14. Smoke / Validation Contract

PS-036 ships one feature smoke:
`scripts/ps036_archive_rehydrate_b2_audit_vault_smoke.py`.

The PS-036 feature smoke must:

- validate only the PS-036 slice (no recursive smokes; must never launch
  another feature smoke as a subprocess; must never call the central
  regression gate)
- read checked-in prior evidence as immutable inputs
- write only its own evidence file
  `docs/evidence/ps-036/archive-rehydrate-b2-audit-vault-report.json`, and only
  when `--write-evidence` is explicit
- never call a provider
- never read arbitrary B2 objects (no live B2 reads)
- never write B2 (no B2 writes)
- never perform broad B2 scans
- never run the frontend typecheck / build (that belongs to the central gate)
- reuse `scripts/smoke_lib.py` for shared validation logic
- validate the route is registered in `apps/web/src/App.tsx`
- validate the `B2AuditVault` component is present
- validate the `b2AuditVault.ts` data module is present
- validate the required vault UI strings (section 20) are present
- validate the required golden / demo constants match accepted evidence
  (run_id, campaign_id, archive reference, archive SHA-256, rehydrate source,
  provider_calls_during_rehydrate, no_live_provider_call_during_rehydrate, and
  manifest hash when present)
- validate no provider calls are introduced
- validate no live B2 reads are introduced
- validate no B2 writes are introduced
- validate no broad B2 scans are introduced
- validate no forbidden overclaims are introduced
- validate no recursive smokes (the smoke must not launch another feature
  smoke)
- validate no hidden Git flags `h` or `S` with an explicit h/S checker that
  reads `git ls-files -v` and fails when `line[0]` is `h` or `S` (a
  lowercase-only marker check is not sufficient because it misses uppercase
  `S` skip-worktree)
- validate the bad lowercase-only hidden-flag command literal is absent from
  the PS-036 changed files, without the smoke or this spec reproducing that
  literal
- validate prior evidence is unchanged
- validate `git diff --check` is clean

The PS-036 feature smoke must support these standard flags:

- `--check-only` (default: non-mutating local validation; no evidence file is
  written)
- `--write-evidence` (write only `docs/evidence/ps-036/` evidence)
- `--no-frontend`

Default PS-036 smoke behavior is non-mutating local validation
(`--check-only`).

The smoke must not contain the bad lowercase-only hidden-flag marker check and
must not rely on a lowercase-only marker check. The hidden-Git-flags check
must be the explicit `h` / `S` checker over `git ls-files -v`, and must record
`no_hidden_git_flags_h` and `no_hidden_git_flags_S` as separate booleans.

PS-036 smoke performs no provider calls, no live B2 reads, no B2 writes, and
no broad B2 scans.

## 15. Regression Gate Contract

The central regression gate remains the single cross-slice release-readiness
gate and is non-mutating by default. PS-036 does not own or modify the central
gate.

Normal PS-036 release validation command:

```
python scripts/proofstudio_regression_gate.py --current ps036 --frontend --report-out /tmp/proofstudio-release-report.json
```

Contract-only gate (no frontend):

```
python scripts/proofstudio_regression_gate.py --current ps036 --no-frontend --report-out /tmp/proofstudio-ps036-regression-report.json
```

- The gate runs `npm run typecheck` and `npm run build` in `apps/web` exactly
  once per invocation, and only when `--frontend` is passed. PS-036 feature
  smoke must never trigger nested frontend builds.
- The gate must not write the canonical PS-034A report. `--write-report` is
  rejected for `--current ps036` (PS-035C accepted behavior; only PS-034A may
  regenerate the canonical report).
- Running the gate for `ps036` must leave all prior-slice evidence unchanged.
- No recursive smokes: the gate never executes a feature smoke.

Canonical PS-034A regeneration (unchanged, owned by PS-034A only):

```
python scripts/proofstudio_regression_gate.py --current ps034a --write-report
```

## 16. Truth Boundary

ProofStudio proves what the pipeline did. The Archive / Rehydrate / B2 Audit
Vault is an evidence-reading surface over recorded B2 / archive / rehydrate
evidence, not a legal authenticity system and not a live B2 verifier.

"B2 system of record" in PS-036 means Backblaze B2 is surfaced as the durable
archive behind the verified golden run. It does not mean Object Lock,
tamper-proof storage, browser-side B2 byte verification, production security,
live B2 availability, legal authenticity, semantic truth, or human authorship.

PS-036 must preserve these truth-boundary red lines verbatim across the spec,
the UI, and any evidence report:

- do not claim legal authenticity
- do not claim semantic truth
- do not claim human authorship
- do not claim C2PA unless implemented and verified
- do not claim Object Lock / tamper-proof storage unless implemented and
  verified
- do not claim browser-side B2 byte verification unless implemented and
  verified
- do not claim live B2 availability unless a live B2 check is explicitly
  implemented and approved
- do not claim public deployment verification unless deployed and tested
- do not claim enterprise security
- do not claim actual spend / latency / quota unless captured
- do not claim provider failures / reruns / variants unless evidenced

PS-036 does not prove product correctness, production security, B2
immutability, Object Lock, tamper-proof storage, browser-side B2 byte
verification, live B2 availability, real billing API integration, billing
behavior, CI enforcement, or deployment readiness. No PS-036 artifact may
imply any of these. The vault records the digests and references the pipeline
already captured; it does not re-fetch or re-hash live B2 bytes.

## 17. Risks

PS-036 must record the following risks with mitigations:

- overclaim risk
  - risk: the vault or its copy implies B2 as system of record proves Object
    Lock, tamper-proof storage, browser-side B2 byte verification, live B2
    availability, legal authenticity, semantic truth, human authorship, C2PA
    authenticity, or production security.
  - mitigation: the persistent truth-boundary panel (section 11) is
    mandatory; the truth-boundary red lines (section 16) are preserved
    verbatim; the evidence report carries `no_forbidden_overclaims`.
- invented-evidence risk
  - risk: the vault fabricates an archive reference, digest, manifest hash, or
    verified status not present in accepted data.
  - mitigation: all vault records are sourced read-only from accepted local /
    golden / demo data; missing records show an honest "not available" /
    "not verified" state.
- live-B2-read risk
  - risk: the vault triggers a live B2 read or a broad B2 scan.
  - mitigation: the vault is purely client-side over accepted data; the smoke
    enforces `no_live_b2_reads`, `no_b2_writes`, `no_broad_b2_scans`.
- evidence-mutation risk
  - risk: the PS-036 smoke or the central gate run overwrites prior-slice
    evidence.
  - mitigation: PS-036 writes only `docs/evidence/ps-036/`; the gate is
    non-mutating by default; prior evidence prefixes are guarded.
- hidden-Git-flags risk
  - risk: a session uses `assume-unchanged`, `skip-worktree`, or
    `git update-index` / `update-index` to mask a dirty tree, including the
    uppercase `S` skip-worktree flag that a lowercase-only marker check
    misses.
  - mitigation: the operating law forbids these verbatim; the smoke uses the
    explicit `h` / `S` checker over `git ls-files -v` and fails on `line[0]`
    being `h` or `S`, recording `no_hidden_git_flags_h` and
    `no_hidden_git_flags_S` as separate booleans.
- scope-creep risk
  - risk: PS-036 expands into CI, billing, deployment, auth, teams,
    permissions, a full enterprise DAM, or a live B2 fetcher.
  - mitigation: section 7 lists these as non-goals; section 9 forbids the
    relevant paths.
- recursive-smoke risk
  - risk: the PS-036 smoke launches another feature smoke or calls the central
    gate.
  - mitigation: the smoke must never launch another feature smoke as a
    subprocess and must never call the central regression gate; the central
    gate is the only cross-slice validator.
- manifest-hash-availability risk
  - risk: the vault asserts a manifest hash when none is recorded, or silently
    drops the manifest record when one is recorded.
  - mitigation: the vault surfaces the manifest reference / hash when present
    and otherwise shows an honest "not available" state; the evidence report
    carries `manifest_hash_present_or_honestly_unavailable`.

## 18. Acceptance Criteria

PS-036 (spec-only phase) is accepted only when:

- this spec exists at `specs/53-ps-036-archive-rehydrate-b2-audit-vault.md`
- only this spec file is changed in the spec-only phase
- the branch `ps-036/archive-rehydrate-b2-audit-vault` starts from
  `origin/accepted/proofstudio` at commit
  `1f6d24f526b5396a6c6e537bec7485c401a02534` (the merge-base equals that
  commit)
- the product scope is clear and does not expand into CI, billing, deployment,
  provider calls, live B2 reads, B2 writes, or broad B2 scans
- the required vault records (section 10.2) are specified
- the UI / UX contract (section 11) and the truth-boundary panel are
  specified
- the data contract (section 12) reuses accepted checked-in evidence as
  read-only inputs
- the truth boundary (section 16) is explicit and the boundary copy is
  specified
- the implementation candidate files (section 8) are listed, but no
  implementation is done in this phase
- the validation plan uses the PS-036 feature smoke plus the central
  regression gate (sections 14 and 15)
- no evidence mutation occurs in this phase
- no hidden Git flags `h` or `S` are present (verified by the explicit h/S
  checker over `git ls-files -v`)
- `git diff --check` is clean
- no staging, commit, or push occurs until PM approval
- `AGENTS.md`, `specs/07-master-spec-plan.md`, and `specs/08-roadmap-slices.md`
  are not changed in this phase

Implementation-phase acceptance (for reference, not this phase) additionally
requires: the route is registered; the `B2AuditVault` component + `b2AuditVault.ts`
data module exist; the nav link exists; the required vault records and the
truth-boundary panel are present; the PS-036 smoke passes in `--check-only`
(default) and writes only `docs/evidence/ps-036/**` under `--write-evidence`;
the central gate passes for `--current ps036`; no provider call, no live B2
read, no B2 write, no broad B2 scan occurs; prior evidence is unchanged; no
forbidden overclaim is introduced.

## 19. Rollback

Rollback of the PS-036 spec-only phase is a single revert of this spec commit,
because only `specs/53-ps-036-archive-rehydrate-b2-audit-vault.md` is changed
in this phase.

Future implementation rollback must restore the pre-PS-036 state of the edited
files in section 8. Specifically:

- remove the `/b2-audit-vault` (or `/archive-rehydrate-b2-audit-vault`) route
  guard and render from `apps/web/src/App.tsx`
- remove `apps/web/src/B2AuditVault.tsx`
- remove `apps/web/src/b2AuditVault.ts`
- revert `apps/web/src/JudgeCockpitHome.tsx` (nav link) and
  `apps/web/src/styles.css` (vault classes) to pre-PS-036 state
- remove `scripts/ps036_archive_rehydrate_b2_audit_vault_smoke.py`
- remove `docs/ps-036-archive-rehydrate-b2-audit-vault-proof.md`
- remove `docs/evidence/ps-036/` if it was added
- revert the additive cross-references in `specs/07-master-spec-plan.md`,
  `specs/08-roadmap-slices.md`, and
  `docs/validation/proofstudio-smoke-harness-v1.md` to pre-PS-036 state

Rollback of PS-036 must not touch any evidence under `docs/evidence/**` other
than `docs/evidence/ps-036/`, must not touch the central gate
(`scripts/proofstudio_regression_gate.py`), `scripts/smoke_lib.py`,
`AGENTS.md`, `.env*`, `render.yaml`, requirements files, any provider wrapper,
or any B2 storage path. Rollback is isolated and reversible because PS-036 is
a self-contained vault surface over existing accepted data; it does not change
provider behavior, B2 behavior, billing behavior, or deployment topology.

## 20. Verbatim implementation/audit contract strings

The PS-036 implementation, the B2 Audit Vault UI, and the PS-036 smoke must
preserve the following exact strings so the vault contract is deterministic
and auditable. The required UI / positioning strings are:

- Archive / Rehydrate / B2 Audit Vault
- B2 system of record
- archive reference
- archive sha256
- manifest hash
- rehydrate source
- provider calls during rehydrate
- no live provider call during rehydrate
- local verification
- not live B2 verification
- not Object Lock
- not tamper-proof
- not production security
- not legal authenticity
- not semantic truth

The required audit / boundary contract strings are:

- notes
- B2 evidence
- no broad B2 reads
- hidden Git flags h and S
- do not claim Object Lock / tamper-proof storage unless implemented and verified
- do not claim browser-side B2 byte verification unless implemented and verified
- do not claim actual spend/latency/quota unless captured
- do not claim provider failures/reruns/variants unless evidenced

The required regression-gate and smoke contract commands are:

- `python scripts/proofstudio_regression_gate.py --current ps036 --frontend --report-out /tmp/proofstudio-release-report.json`
- `python scripts/proofstudio_regression_gate.py --current ps036 --no-frontend --report-out /tmp/proofstudio-ps036-regression-report.json`
- `scripts/ps036_archive_rehydrate_b2_audit_vault_smoke.py`
- `docs/evidence/ps-036/archive-rehydrate-b2-audit-vault-report.json`

The required evidence-report boolean keys are:

- `ok`
- `slice_id: ps036`
- `route_present`
- `vault_component_present`
- `vault_data_module_present`
- `archive_reference_present`
- `archive_sha256_present`
- `manifest_hash_present_or_honestly_unavailable`
- `rehydrate_source_present`
- `provider_calls_during_rehydrate_present`
- `no_live_provider_call_during_rehydrate_present`
- `b2_evidence_status_present`
- `local_verification_status_present`
- `not_claimed_status_present`
- `boundary_copy_present`
- `no_provider_calls`
- `no_live_b2_reads`
- `no_b2_writes`
- `no_broad_b2_scans`
- `no_recursive_smokes`
- `no_hidden_git_flags_h`
- `no_hidden_git_flags_S`
- `truth_boundary_preserved`
- `no_forbidden_overclaims`
- `prior_evidence_clean`
- `failures`
