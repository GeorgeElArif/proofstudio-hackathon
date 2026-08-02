# PS-035b — Cost Caps + Golden-Fixture Governance (Proof)

Slice: PS-035b — Cost Caps + Golden-Fixture Governance
Branch: `ps-035b/cost-caps-golden-fixture-governance`
Date: 2026-07-01

## Files changed

- `scripts/ps035b_cost_caps_golden_fixture_governance_smoke.py` (new) — local/static governance + golden-fixture-freeze smoke.
- `docs/evidence/ps-035b/cost-caps-golden-fixture-governance-report.json` (new) — PS-035b evidence report (written by the smoke).
- `docs/evidence/golden-fixture-digests.json` (new) — checked-in golden-fixture digest manifest.
- `docs/ps-035b-cost-caps-golden-fixture-governance-proof.md` (new) — this proof doc.
- `scripts/smoke_lib.py` — added `docs/evidence/ps-035a/` to `HISTORICAL_PRIOR_EVIDENCE_PREFIXES`.
- `scripts/proofstudio_regression_gate.py` — added `ps-035a` to `PRIOR_EVIDENCE_PREFIXES`.
- `src/proofstudio/api/live_bridge.py` — added the authoritative default-off governance gate (`govern_live_run`, `live_runs_enabled`, `b2_writes_enabled`, `cost_cap_usd`, `fixtures_frozen`) and the B2 write gate.
- `src/proofstudio/api/services.py` — `_execute_live_and_apply` now honors `govern_live_run` before calling the live bridge.
- `.env.production.example` — documented the PS-035b default-off governance controls.
- `docs/deployment/environment.md` — documented the PS-035b governance controls and behavioral contract.
- `specs/07-master-spec-plan.md` — PS-035b status update.
- `specs/08-roadmap-slices.md` — PS-035b acceptance update.
- `docs/validation/proofstudio-smoke-harness-v1.md` — append-only PS-035b note.

No product UI, no provider code, no live B2, no frontend build, and no prior-slice evidence bytes were changed.

## Default-off governance controls

PS-035b adds four real, default-off backend governance controls plus an explicit PM/human approval flag. These are POLICY FLAGS, not secrets. They never use names containing `KEY`, `TOKEN`, or `SECRET`, and they are never printed or exposed as secrets.

- `PROOFSTUDIO_LIVE_RUNS_ENABLED=false` — live provider execution blocked by default.
- `PROOFSTUDIO_B2_WRITES_ENABLED=false` — B2 writes after a successful live run blocked by default.
- `PROOFSTUDIO_COST_CAP_USD=0.00` — local cost-cap policy gate; paid execution blocked when zero.
- `PROOFSTUDIO_FIXTURES_FROZEN=true` — golden fixtures frozen by default.
- `PROOFSTUDIO_PAID_RUN_APPROVED=false` — explicit PM/human approval required for any paid/live run.

Dry/demo runs remain fully available with these defaults. Only live provider execution, B2 writes, paid runs, and fixture mutation are gated.

## Live-run gate summary

`run_live=true` alone is no longer sufficient to execute providers. The authoritative gate is `govern_live_run(budget_mode=...)` in `src/proofstudio/api/live_bridge.py`, called at the top of `execute_live_run` before any provider is constructed or any B2 credential is read. It permits execution only when ALL of the following are true, in order:

1. `PROOFSTUDIO_LIVE_RUNS_ENABLED=true`
2. `PROOFSTUDIO_PAID_RUN_APPROVED=true`
3. `PROOFSTUDIO_COST_CAP_USD` > `0.00`
4. `budget_mode` != `free-only`

When the gate blocks, the bridge returns a `live_blocked` result with a clear `blocked_reason` and writes only the prompt packet. No provider is called and no B2 access occurs. `src/proofstudio/api/services.py::_execute_live_and_apply` honors the same gate in the service layer before the bridge is ever called, so `PROOFSTUDIO_RUN_LIVE_DEFAULT=false` is no longer a phantom-only contract — it is superseded truthfully by the enforced `PROOFSTUDIO_LIVE_RUNS_ENABLED` gate.

## B2 write gate summary

B2 writes after a successful live provider run require `PROOFSTUDIO_B2_WRITES_ENABLED=true`. The gate (`b2_writes_enabled()`) is checked in `execute_live_run` immediately before the Genblaze/B2 upload. When blocked, the real local image produced by the provider is preserved (recorded as `local_image`), the run is marked `live_failed` with a clear error, and no B2 write occurs. B2 reads remain disabled by default under the existing PS-019/PS-021/PS-025 durable passport contract; PS-035b adds no live B2 read path.

## Cost cap / free-only summary

`cost_cap_usd()` reads `PROOFSTUDIO_COST_CAP_USD` and defaults to `0.00`. The governance gate blocks paid/non-free execution when the cap is zero. `budget_mode="free-only"` (the default) also blocks paid/non-free execution before any live provider call. A non-zero cap and a non-`free-only` budget mode are both required in addition to the live-runs-enabled and PM-approval flags.

## Golden fixture digest manifest summary

A checked-in digest manifest at `docs/evidence/golden-fixture-digests.json` records SHA-256 digests for the two canonical golden fixtures:

- `docs/evidence/demo/golden-demo-run.json`
- `docs/evidence/ps-035a/manifest-fixture.json`

The manifest is checked in (not generated at runtime from the files it guards). The PS-035b smoke recomputes the SHA-256 over the current fixture bytes and requires equality to the recorded digests. The fixture bytes themselves were NOT mutated. Future slices must verify these digests before acceptance.

## PS-035a evidence protection summary

`docs/evidence/ps-035a/` was added to `HISTORICAL_PRIOR_EVIDENCE_PREFIXES` in `scripts/smoke_lib.py` and to `PRIOR_EVIDENCE_PREFIXES` in `scripts/proofstudio_regression_gate.py`, because PS-035a evidence was not previously covered by the PS-034A/PS-034B historical evidence prefix lists. The frozen digest manifest additionally covers the PS-035a manifest fixture. PS-035b's own evidence dir (`docs/evidence/ps-035b/`) was intentionally NOT added as prior evidence in this slice, so the PS-035b smoke can write its own report without blocking itself.

## No live provider/B2 execution by default

With the PS-035b defaults in place:

- no live provider call is made by default
- no live B2 read is made by default
- no live B2 write is made by default
- demo/dry-run runs use checked-in golden fixtures and never contact providers or B2

The PS-035b smoke is local/static only: it reads checked-in files, runs git introspection, and writes only its own report. It performs no provider call, no live B2 read, and no live B2 write.

## Validation results

Pre-commit validation performed for PS-035b:

- `py_compile` of the PS-035b smoke and touched backend modules: pass.
- PS-035b smoke: pass (all measured fields true, `failures` empty).
- Golden fixture digest recomputation: both fixtures recompute to their recorded SHA-256 digests.
- Changed-files allowlist: only the PS-035b allowed files appear in the working tree.
- Prior fixture bytes unchanged: `docs/evidence/demo/golden-demo-run.json` and `docs/evidence/ps-035a/manifest-fixture.json` were not mutated.
- Hidden Git index flags: none.
- `git diff --check`: clean.
- Central regression gate: pass before commit.

Development-scope note: while the tree is dirty for a source-modifying slice, older standalone slice smokes with frozen path allowlists may reject legitimate PS-035b working-tree changes. PS-035b does not claim those standalone smokes passed in the dirty working tree. The authoritative acceptance gate is the PS-035b smoke, digest verification, prior-evidence protection, changed-file allowlist, central regression gate, clean final status, and pushed commit.

## Truth Boundary

ProofStudio proves what the pipeline did.

It does not prove semantic truth, legal authenticity, C2PA authenticity, human authorship, Object Lock/tamper-proof storage, browser-side B2 byte verification, production security, real billing API integration, or production multi-user budget accounting unless those are actually implemented.

The golden-fixture freeze proves byte equality to recorded digests only. It is not tamper-proof, not Object Lock, not legal authenticity, and not production immutability. The cost cap is a local policy gate, not a real billing API integration and not production multi-user budget accounting.

PS-035b makes no claim of B2 Object Lock, tamper-proof storage, real billing API integration, or production multi-user budget accounting.

## Non-goals

PS-035b did not call live providers, did not read or write live B2, did not implement Campaign Proof Room or multimodal proof, did not add a new provider, did not change product UI, and did not mutate the PS-035a golden fixture bytes or the canonical golden demo bytes. PS-035b makes no claim of tamper-proof storage, Object Lock, real billing API integration, production multi-user budget accounting, or production security, and did not weaken PS-034A/PS-034B harness constraints.
