# PS-035b — Cost Caps + Golden-Fixture Governance

Status: Spec only.
Base branch: `ps-035b/cost-caps-golden-fixture-governance`
Date: 2026-07-01

This spec-only commit touches only one file:
`specs/48-ps-035b-cost-caps-golden-fixture-governance.md`. No implementation
files, no requirements, no evidence, no smoke scripts, no `smoke_lib`, no
regression gate, no env files, no proof docs, and no B2 access are changed or
performed during this phase.

## 1. Status

PS-035b is currently:

- Spec only.
- Implementation pending.

PS-035b must not be implemented, and no implementation files may be changed,
until this spec is accepted.

PS-035b is the next blocking governance slice after PS-035a. It exists to put a
real, default-off cost-cap and golden-fixture governance layer in place before
any new paid, multimodal, or provider-expansion work is permitted. The latest
accepted slice is PS-035a commit `105cd91`.

This spec-only phase writes only this file. PS-035b must not call live
providers, must not read or write live B2, must not call any provider, and must
not print secrets.

## 2. Purpose

PS-035b introduces a real governance contract and a golden-fixture freeze
contract before any further paid/multimodal/provider expansion. Today
ProofStudio has documentation and smoke checks that assert safe defaults, but
no single backend-enforced gate that blocks live runs, paid providers, or B2
writes by default, and no frozen digest manifest that future slices must verify
before acceptance.

PS-035b closes that gap by defining:

- a cost-cap and live-run governance contract (default-off live runs,
  default-off B2 writes, a `0.00` cost cap, an explicit human/PM approval
  requirement for any paid/live run);
- a golden-fixture freeze contract (a checked-in digest manifest that future
  slices verify before acceptance); and
- a local/static smoke validation model that proves the governance gates and
  the freeze are in place without ever calling a provider or touching live B2.

After PS-035b, no new paid/multimodal/provider-expansion slice may be accepted
until it honors the governance contract and verifies the frozen golden
fixtures.

## 3. Why PS-035b Exists

- There is no central cost-cap or governance layer today. Safe defaults are
  documented and smoke-checked but are not unified into one enforceable,
  default-off backend gate.
- `PROOFSTUDIO_RUN_LIVE_DEFAULT=false` is documented and smoke-checked (for
  example in `.env.production.example`, `docs/deployment/environment.md`, and
  the PS-017/PS-018 smoke scripts), but it is not read by backend code under
  `src/**`. A documented default is not an enforced gate.
- `RunCreate.run_live` defaults `False` and `dry_run` defaults `True` (see
  `src/proofstudio/api/models.py`), but there is no unified paid/live approval
  gate that decides whether a live or paid run may execute at all.
- `budget_mode="free-only"` exists (for example as a default in
  `src/proofstudio/providers/types.py`) but is not enforced before live
  provider calls. A non-free/paid provider is not blocked when
  `budget_mode="free-only"`.
- B2 reads are gated by default-off durable passport flags (PS-019/PS-021/PS-025
  contract). B2 reads remain default-off, but B2 writes happen after successful
  live provider runs without a dedicated default-off B2 write gate.
- Golden demo and PS-035a manifest fixture hashes are checked by existing
  smokes, but there is no fixture-freeze policy: no single checked-in digest
  manifest that future slices must verify before acceptance.
- `docs/evidence/ps-035a/` is not yet protected by PS-034A/PS-034B historical
  evidence prefix lists, so a frozen digest manifest is the durable protection
  path forward.
- The regression gate currently reports no-provider/no-broad-B2-read assurance
  without PS-035b-specific measured governance. There is no measured field that
  says live runs are disabled by default, B2 writes are disabled by default, or
  the golden fixtures are frozen and matching.

PS-035b is the slice that establishes a real, default-off governance contract
and a golden-fixture freeze, validated by local/static smoke, without calling
providers or touching live B2.

## 4. Current Discovery Facts

Environment / governance state:

- `PROOFSTUDIO_RUN_LIVE_DEFAULT=false` appears in `.env.production.example`,
  `docs/deployment/environment.md`, `docs/deployment/render.md`, and the
  PS-017/PS-018 smoke scripts. It is documented and smoke-checked.
- There is no read of `PROOFSTUDIO_RUN_LIVE_DEFAULT` in any backend code under
  `src/**`. The documented default is not an enforced backend gate.
- None of `PROOFSTUDIO_LIVE_RUNS_ENABLED`, `PROOFSTUDIO_B2_WRITES_ENABLED`,
  `PROOFSTUDIO_COST_CAP_USD`, or `PROOFSTUDIO_FIXTURES_FROZEN` exist anywhere
  in the repo today (no code, no docs, no env template, no smoke).
- There is no central cost-cap or governance layer today.

API / run model state (`src/proofstudio/api/models.py`):

- `RunCreate.dry_run` defaults `True`.
- `RunCreate.run_live` defaults `False`.
- There is no unified paid/live approval gate that decides whether a live or
  paid run may execute at all.

Provider / budget state:

- `budget_mode="free-only"` exists as a default (for example in
  `src/proofstudio/providers/types.py`).
- `budget_mode="free-only"` is not enforced before live provider calls. A
  paid/non-free provider is not blocked when `budget_mode="free-only"`.

B2 state:

- B2 reads are gated by default-off durable passport flags (PS-019/PS-021/PS-025
  contract). B2 reads remain default-off.
- B2 writes happen after successful live provider runs without a dedicated
  default-off B2 write gate.

Fixture / evidence state:

- `docs/evidence/demo/golden-demo-run.json` exists and its hash is checked by
  existing smokes.
- `docs/evidence/ps-035a/manifest-fixture.json` exists and its hash is checked
  by the PS-035a smoke.
- There is no fixture-freeze policy: no single checked-in digest manifest that
  future slices must verify before acceptance.
- `docs/evidence/ps-035a/` is not yet protected by PS-034A/PS-034B historical
  evidence prefix lists.

Regression gate state:

- The regression gate currently reports no-provider/no-broad-B2-read assurance
  without PS-035b-specific measured governance. There is no measured field for
  `live_runs_disabled_by_default`, `b2_writes_disabled_by_default`,
  `golden_fixture_digests_match`, or `ps035a_evidence_protected`.

## 5. Scope

PS-035b is a governance and golden-fixture-freeze slice. It adds a real
governance contract before any new paid/multimodal/provider expansion. It is
local/static-only and must not touch the network for providers or B2.

PS-035b must:

1. Add a real governance contract before any new paid/multimodal/provider
   expansion.
2. Define default-off controls (see section 10): live runs disabled by default,
   B2 writes disabled by default, a `0.00` cost cap, and frozen fixtures.
3. Require an explicit PM/human approval before any paid/live run executes.
4. Require that any approved paid/live run is either promoted into a reusable
   golden fixture or recorded as intentionally non-promoted with reason.
5. Block live provider execution unless live runs are explicitly enabled.
6. Block B2 writes unless B2 writes are explicitly enabled.
7. Block paid/non-free providers when `budget_mode="free-only"` or when the cost
   cap is `0.00`.
8. Introduce a checked-in golden-fixture digest manifest (recommended path:
   `docs/evidence/golden-fixture-digests.json`) recording SHA-256 digests for
   the golden demo run and the PS-035a manifest fixture, and require future
   slices to verify these digests before acceptance.
9. Require demo mode to reuse checked-in golden fixtures and to not call
   providers or B2 by default.
10. Preserve the truth boundary (section 17) and avoid overclaims. The freeze
    proves byte equality to recorded digests only; it is not tamper-proof, not
    Object Lock, not legal authenticity, and not production immutability.
11. Define local/static smoke validation only (section 16). PS-035b must not
    call providers and must not read or write live B2.
12. Preserve PS-034A/PS-034B harness constraints. The PS-034A and PS-034B
    smokes must still pass after the PS-035b commit, in safe local mode with no
    evidence mutation.

## 6. Non-goals

PS-035b must not:

- do not call live providers
- do not read or write live B2 (no live B2 read, no live B2 write)
- do not do broad B2 reads
- do not claim B2 Object Lock, tamper-proof storage, or production immutability
- do not claim real billing API integration
- do not claim production multi-user budget accounting
- do not implement Campaign Proof Room
- do not implement multimodal proof
- do not implement a new provider
- do not change product UI
- do not require any control name containing `KEY`, `TOKEN`, or `SECRET`
- do not treat the governance control names as secrets
- do not print secrets
- do not claim C2PA authenticity, human authorship, legal authenticity,
  browser-side B2 byte verification, or production security
- do not claim semantic truth

PS-035b only edits this spec file in the spec-only phase. Implementation-phase
candidates are listed in section 8.

## 7. Spec-only allowed file

This spec-only commit touches only:

- `specs/48-ps-035b-cost-caps-golden-fixture-governance.md`

No other files are changed during the spec-only phase. No implementation files,
no requirements, no evidence, no smoke scripts, no `smoke_lib`, no regression
gate, no env files, and no proof docs are changed.

## 8. Recommended implementation allowed files

The following are implementation-phase candidates only, clearly marked as
implementation-phase only. They are not for this spec-only commit:

- `scripts/ps035b_cost_caps_golden_fixture_governance_smoke.py`
- `docs/evidence/ps-035b/cost-caps-golden-fixture-governance-report.json`
- `docs/evidence/golden-fixture-digests.json`
- `docs/ps-035b-cost-caps-golden-fixture-governance-proof.md`
- `scripts/smoke_lib.py`
- `scripts/proofstudio_regression_gate.py`
- `src/proofstudio/api/live_bridge.py`
- `src/proofstudio/api/services.py`
- `.env.production.example`
- `docs/deployment/environment.md` if it exists
- `specs/07-master-spec-plan.md`
- `specs/08-roadmap-slices.md`
- `docs/validation/proofstudio-smoke-harness-v1.md`

Any edit to backend code under `src/**` (for example `live_bridge.py` or
`services.py`) is the implementation phase actually enforcing the governance
gate. It must remain default-off, must not call providers, and must not touch
live B2 as part of PS-035b validation.

Any edit to `.env.production.example` or `docs/deployment/environment.md` is the
implementation phase documenting the new default-off controls. It must not
introduce names containing `KEY`, `TOKEN`, or `SECRET`, and must not print or
expose secrets.

Any edit to `scripts/smoke_lib.py` or `scripts/proofstudio_regression_gate.py`
is the implementation phase adding the PS-035b measured fields and must preserve
PS-034A/PS-034B harness constraints (safe local mode, no evidence mutation, no
provider calls, no live B2).

## 9. Forbidden files unless PM-approved later

PS-035b implementation must not touch:

- `apps/web/**` (unless the frontend secret-safety scan requires a minimal,
  PM-approved change)
- `workers/**`
- `packages/**`
- `render.yaml`
- prior-slice evidence under `docs/evidence/ps-018b`, `ps-019`, `ps-020`,
  `ps-021`, `ps-024`, `ps-025`, `ps-026`, `ps-027`, `ps-028`, `ps-029`,
  `ps-030`, `ps-031`, `ps-032`, `ps-033`, `ps-034`, `ps-034a`, `ps-034b`,
  `ps-034c`, `ps-035a`
- the canonical `docs/evidence/demo/golden-demo-run.json` (its digest is
  recorded, not its bytes changed) unless a later PM-approved slice explicitly
  re-pins the golden run
- any historical evidence not explicitly whitelisted
- any live provider credential or live B2 credential file

The golden fixtures are recorded into the digest manifest; PS-035b must not
mutate the fixture bytes themselves.

## 10. Cost-cap and live-run governance contract

PS-035b defines the following intended default-off controls for implementation.
These are policy/governance flags, not secrets. They must not be treated as
secrets, must not require names containing `KEY`, `TOKEN`, or `SECRET`, and must
not be printed or exposed.

- `PROOFSTUDIO_LIVE_RUNS_ENABLED=false`
- `PROOFSTUDIO_B2_WRITES_ENABLED=false`
- `PROOFSTUDIO_COST_CAP_USD=0.00`
- `PROOFSTUDIO_FIXTURES_FROZEN=true`

Behavioral contract:

- Live provider execution is blocked unless live runs are explicitly enabled
  (`PROOFSTUDIO_LIVE_RUNS_ENABLED=false` by default).
- B2 writes are blocked unless B2 writes are explicitly enabled
  (`PROOFSTUDIO_B2_WRITES_ENABLED=false` by default).
- Paid/non-free providers are blocked when `budget_mode="free-only"` or when the
  cost cap is `0.00` (`PROOFSTUDIO_COST_CAP_USD=0.00` by default). The
  `budget_mode_free_only_blocks_paid` gate must be enforced before any live
  provider call.
- A live/paid run must require explicit PM/human approval before execution. The
  measured field `paid_run_requires_explicit_approval` must be true.
- Any approved paid/live run must be promoted into a reusable golden fixture or
  recorded as intentionally non-promoted with reason.
- These controls must be honored in addition to, not instead of, the existing
  `run_live`/`dry_run` defaults and the `PROOFSTUDIO_RUN_LIVE_DEFAULT`
  documentation. PS-035b must make `run_live_default` honored in backend, not
  only documented.
- PS-035b must not call live providers and must not read or write live B2 while
  validating these gates. The validation is local/static only.

The implementation must report `live_runs_disabled_by_default`,
`run_live_default_honored`, `paid_run_requires_explicit_approval`,
`cost_cap_default_zero`, `budget_mode_free_only_blocks_paid`, and
`b2_writes_disabled_by_default` as measured fields.

## 11. Demo mode vs live mode contract

- Demo mode must reuse checked-in golden fixtures and must not call providers or
  B2 by default. The measured field `demo_mode_uses_fixtures` must be true.
- Demo mode must not require live providers or live B2 to succeed.
- Live mode is opt-in only. It requires `PROOFSTUDIO_LIVE_RUNS_ENABLED` to be
  explicitly enabled, an explicit PM/human approval for any paid/live run, and
  must respect `budget_mode="free-only"` and the cost cap.
- Provider calls are blocked by default. The measured field
  `provider_calls_blocked_by_default` must be true.

PS-035b validation must run in demo/local mode only.

## 12. B2 read/write guard contract

- B2 reads remain disabled by default (default-off durable passport flags,
  PS-019/PS-021/PS-025 contract). The measured field
  `b2_reads_remain_disabled_by_default` must be true.
- B2 writes are disabled by default (`PROOFSTUDIO_B2_WRITES_ENABLED=false`). The
  measured field `b2_writes_disabled_by_default` must be true.
- PS-035b must perform no live B2 read and no live B2 write during validation.
- PS-035b must not claim B2 Object Lock, tamper-proof storage, or production
  immutability.

## 13. Golden-fixture freeze contract

PS-035b introduces a checked-in digest manifest. Recommended file:

- `docs/evidence/golden-fixture-digests.json`

The manifest must record SHA-256 digests for:

- `docs/evidence/demo/golden-demo-run.json`
- `docs/evidence/ps-035a/manifest-fixture.json`

Contract:

- `PROOFSTUDIO_FIXTURES_FROZEN=true` by default.
- Future slices must verify these digests before acceptance. The measured field
  `golden_fixture_digests_match` must be true.
- The freeze proves byte equality to recorded digests only.
- It must not be described as tamper-proof, Object Lock, legal authenticity, or
  production immutability. It is not tamper-proof.
- The manifest must be checked in, not generated at runtime from the files it
  guards (a recorded digest that the smoke recomputes and compares against).
- The manifest must include the measured fields `golden_demo_digest_recorded`
  and `ps035a_manifest_fixture_digest_recorded`.
- The manifest must enable `ps035a_evidence_protected`: PS-035a evidence is
  protected by digest freeze because it is not yet covered by the PS-034A/PS-034B
  historical evidence prefix lists.

## 14. Provider-key and frontend secret-safety contract

- PS-035b must not introduce any control name containing `KEY`, `TOKEN`, or
  `SECRET`. The four governance controls are policy flags, not secrets.
- PS-035b must not treat the governance control names as secrets and must not
  print or expose them as secrets.
- No provider keys may be referenced from frontend code. The measured field
  `no_provider_keys_in_frontend` must be true.
- `.env`, `.env.save`, and token-like files must remain gitignored. The measured
  field `env_files_gitignored` must be true.
- PS-035b must not print secrets.

## 15. Evidence model

The future PS-035b evidence report JSON
(`docs/evidence/ps-035b/cost-caps-golden-fixture-governance-report.json`) must
include at least:

- `ok`
- `slice_id: ps035b`
- `checked_at`
- `live_runs_disabled_by_default`
- `run_live_default_honored`
- `paid_run_requires_explicit_approval`
- `cost_cap_default_zero`
- `budget_mode_free_only_blocks_paid`
- `b2_writes_disabled_by_default`
- `b2_reads_remain_disabled_by_default`
- `demo_mode_uses_fixtures`
- `provider_calls_blocked_by_default`
- `golden_fixture_digest_manifest_present`
- `golden_demo_digest_recorded`
- `ps035a_manifest_fixture_digest_recorded`
- `golden_fixture_digests_match`
- `ps035a_evidence_protected`
- `no_provider_keys_in_frontend`
- `env_files_gitignored`
- `no_live_provider_call`
- `no_live_b2_read`
- `no_live_b2_write`
- `truth_boundary_preserved`
- `no_forbidden_overclaims`
- `no_forbidden_file_changes`
- `failures`

`ok` is true only when every measured field is truthful and no forbidden
overclaim or forbidden file change is present. `failures` is a list of human-
readable failure strings and must be empty on acceptance.

## 16. Required validation plan

PS-035b implementation must be validated with local/static validation only:

- py_compile of the new PS-035b smoke.
- the PS-035b smoke pass.
- the PS-035a smoke still passes.
- the PS-024 smoke still passes.
- the PS-034A smoke still passes after the commit.
- the PS-034B smoke still passes after the commit.
- golden fixture digest recomputation: recompute SHA-256 over
  `docs/evidence/demo/golden-demo-run.json` and
  `docs/evidence/ps-035a/manifest-fixture.json` and require equality to the
  recorded digests in `docs/evidence/golden-fixture-digests.json`.
- frontend secret-reference scan: no provider keys referenced from frontend
  code.
- env/gitignore protection for `.env`, `.env.save`, and token-like files.
- no executable provider/B2 calls in the PS-035b smoke (static proof: the smoke
  must not perform a live provider call, no live B2 read, no live B2 write).
- no false tamper-proof/Object Lock/billing-integration claims (no forbidden
  overclaims).
- changed-files allowlist: only the files in section 8 may appear in the diff.
- a no-hidden-Git-flags check:
  ```
  git ls-files -v | grep -E '^[a-z]'
  ```
  must return nothing both before and after validation.
- `git diff --check` returns clean.

## 17. Truth boundary

ProofStudio proves what the pipeline did.

It does not prove semantic truth, legal authenticity, C2PA authenticity, human
authorship, Object Lock or tamper-proof storage, browser-side B2 byte
verification, production security, real billing API integration, or production
multi-user budget accounting unless those are actually implemented.

The golden-fixture freeze proves byte equality to recorded digests only. It is
not tamper-proof, not Object Lock, not legal authenticity, and not production
immutability. The cost cap is a local policy gate, not a real billing API
integration and not production multi-user budget accounting.

PS-035b must preserve this boundary verbatim across the proof doc, evidence
report, digest manifest, and smoke. No PS-035b artifact may imply live B2
Object Lock, tamper-proof storage, real billing API integration, production
multi-user budget accounting, or production security.

## 18. Risks

PS-035b must record the following risks with mitigations:

- documented-but-unenforced defaults
  - risk: `PROOFSTUDIO_RUN_LIVE_DEFAULT=false` is documented/smoke-checked but
    not read by backend; a future change could execute a live/paid run without a
    real gate.
  - mitigation: PS-035b adds backend-enforced default-off controls and reports
    `live_runs_disabled_by_default`, `run_live_default_honored`, and
    `b2_writes_disabled_by_default` as measured fields.
- paid provider slipping past `budget_mode="free-only"`
  - risk: a paid/non-free provider is not blocked today when
    `budget_mode="free-only"`.
  - mitigation: PS-035b enforces `budget_mode_free_only_blocks_paid` and the
    `0.00` cost cap before any live provider call.
- B2 write without a default-off gate
  - risk: B2 writes happen after successful live provider runs without a
    dedicated default-off B2 write gate.
  - mitigation: PS-035b adds `PROOFSTUDIO_B2_WRITES_ENABLED=false` and reports
    `b2_writes_disabled_by_default`; PS-035b validation performs no live B2
    write.
- golden fixture drift
  - risk: golden demo or PS-035a manifest fixture bytes change without a freeze
    noticing.
  - mitigation: PS-035b records digests in
    `docs/evidence/golden-fixture-digests.json`, requires
    `golden_fixture_digests_match`, and future slices must verify the digests
    before acceptance.
- PS-035a evidence unprotected by prefix lists
  - risk: `docs/evidence/ps-035a/` is not yet covered by PS-034A/PS-034B
    historical evidence prefix lists.
  - mitigation: the digest manifest covers the PS-035a manifest fixture and
    reports `ps035a_evidence_protected`.
- overclaim drift
  - risk: a future artifact describes the freeze as tamper-proof/Object Lock,
    or the cost cap as a real billing API integration.
  - mitigation: preserve the truth boundary verbatim; the freeze is not
    tamper-proof; report `no_forbidden_overclaims`.
- secret-safety drift
  - risk: a future control name contains `KEY`/`TOKEN`/`SECRET` or provider keys
    leak into frontend.
  - mitigation: control names must not contain `KEY`/`TOKEN`/`SECRET`; report
    `no_provider_keys_in_frontend` and `env_files_gitignored`.
- harness regression
  - risk: PS-035b changes break the PS-034A/PS-034B harness.
  - mitigation: PS-035b must preserve PS-034A/PS-034B harness constraints; both
    smokes must still pass after the commit in safe local mode.
- demo fragility
  - risk: demo mode requires live providers or live B2 to succeed.
  - mitigation: demo mode reuses checked-in golden fixtures and must not call
    providers or B2 by default.

## 19. Acceptance criteria

PS-035b is accepted only when:

- the PS-035b spec exists (this document, accepted)
- a real governance contract is defined and intended to be backend-enforced:
  `PROOFSTUDIO_LIVE_RUNS_ENABLED=false`,
  `PROOFSTUDIO_B2_WRITES_ENABLED=false`, `PROOFSTUDIO_COST_CAP_USD=0.00`,
  `PROOFSTUDIO_FIXTURES_FROZEN=true`
- live provider execution is blocked unless live runs are explicitly enabled
- B2 writes are blocked unless B2 writes are explicitly enabled
- paid/non-free providers are blocked when `budget_mode="free-only"` or cost cap
  is `0.00`
- a live/paid run requires explicit PM/human approval before execution
- any approved paid/live run is promoted into a reusable golden fixture or
  recorded as intentionally non-promoted with reason
- demo mode reuses checked-in golden fixtures and does not call providers or B2
  by default
- a checked-in digest manifest exists at
  `docs/evidence/golden-fixture-digests.json` recording SHA-256 digests for the
  golden demo run and the PS-035a manifest fixture
- future slices must verify these digests before acceptance
- the freeze proves byte equality to recorded digests only and is described as
  not tamper-proof
- the evidence report schema is defined (section 15)
- the validation plan is local/static only (section 16) and includes
  `no live provider call`, `no live B2 read`, `no live B2 write`
- the truth boundary is preserved (section 17)
- PS-035b makes no claim of B2 Object Lock, tamper-proof storage, real billing
  API integration, or production multi-user budget accounting
- PS-035b preserves PS-034A/PS-034B harness constraints
- no implementation files are changed during the spec-only phase
- commit and push are required before acceptance

## 20. Rollback

Rollback of the PS-035b spec-only phase is a single revert of the PS-035b spec
commit, because only this spec file is changed in this phase.

Future implementation rollback must restore the pre-PS-035b state of the edited
files in section 8 and remove the new digest manifest and PS-035b evidence if
the governance gate or the freeze breaks the harness. Specifically, if PS-035b
implementation turns out to break the PS-034A/PS-034B harness or the golden
fixtures, rollback must restore:

- `scripts/smoke_lib.py` to its pre-PS-035b state
- `scripts/proofstudio_regression_gate.py` to its pre-PS-035b state
- `src/proofstudio/api/live_bridge.py` to its pre-PS-035b state
- `src/proofstudio/api/services.py` to its pre-PS-035b state
- `.env.production.example` and `docs/deployment/environment.md` to their
  pre-PS-035b state
- remove `docs/evidence/golden-fixture-digests.json`,
  `docs/evidence/ps-035b/cost-caps-golden-fixture-governance-report.json`, and
  `docs/ps-035b-cost-caps-golden-fixture-governance-proof.md`

Because PS-035b is intentionally scoped to a default-off governance contract, a
golden-fixture digest manifest, a PS-035b smoke, PS-035b evidence, a PS-035b
proof doc, the smoke harness/regression-gate measured fields, the env docs, the
master spec plan, and the roadmap slices doc, rollback is isolated, reversible,
and does not require touching product UI, providers, or deployment topology.
