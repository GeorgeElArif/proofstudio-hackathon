# PS-036 — Archive / Rehydrate / B2 Audit Vault — Proof

## 1. Status

PS-036 — Archive / Rehydrate / B2 Audit Vault is implemented. This proof doc
records what the slice adds, what evidence it reads, the exact truth-boundary
copy surfaced, and the validation that passed. PS-036 obeys the root
`AGENTS.md` operating law and the validation policy in
`docs/validation/proofstudio-smoke-harness-v1.md`.

PS-036 starts from `origin/accepted/proofstudio` (not `main`). It does not call
any provider, does not read live B2, does not write B2, does not perform a
broad B2 scan, does not mutate any prior evidence, and does not print secrets.

## 2. What PS-036 adds

A dedicated Archive / Rehydrate / B2 Audit Vault surface that frames Backblaze
B2 as the durable system of record for the verified golden run, using accepted
checked-in evidence only.

Implementation files (this slice only):

- `apps/web/src/b2AuditVault.ts` — the camelCase data module. Reuses the
  verified golden B2 archive / rehydrate constants from
  `apps/web/src/b2Evidence.ts` (PS-026) read-only and adds the manifest
  reference / hash sourced verbatim from the PS-024 golden manifest.
- `apps/web/src/B2AuditVault.tsx` — the PascalCase vault component. Accepts
  the existing `variant="page"` convention.
- `apps/web/src/App.tsx` — registers the `/b2-audit-vault` route guard
  (`isB2AuditVaultPath()`) and renders `<B2AuditVault variant="page" />`.
- `apps/web/src/JudgeCockpitHome.tsx` — adds a nav link to the vault.
- `scripts/ps036_archive_rehydrate_b2_audit_vault_smoke.py` — the PS-036
  feature smoke (local / non-mutating by default).
- `docs/ps-036-archive-rehydrate-b2-audit-vault-proof.md` — this proof doc.
- `docs/evidence/ps-036/archive-rehydrate-b2-audit-vault-report.json` — the
  only evidence PS-036 may write, and only when `--write-evidence` is explicit.

No backend (`src/**`), provider wrapper, B2 client, B2 storage path,
`AGENTS.md`, `.env*`, `render.yaml`, requirements file,
`scripts/proofstudio_regression_gate.py`, or `scripts/smoke_lib.py` is touched.
No CSS file is touched: the vault reuses the existing shared component classes.

## 3. Route / component / data module

- Route: `/b2-audit-vault` (client-side guard `isB2AuditVaultPath()` in
  `apps/web/src/App.tsx`).
- Component: `B2AuditVault` (`apps/web/src/B2AuditVault.tsx`), rendered as
  `<B2AuditVault variant="page" />`.
- Data module: `b2AuditVault` (`apps/web/src/b2AuditVault.ts`).
- Nav link: "Open B2 Audit Vault" on the Judge Cockpit Home golden demo run
  CTA row.

## 4. Evidence sources used (read-only)

All vault records are sourced verbatim from accepted checked-in evidence:

- `docs/evidence/demo/golden-demo-run.json` (PS-024 golden manifest)
- `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json` (PS-021)
- `docs/evidence/ps-026/b2-evidence-explorer-smoke.json` (PS-026)
- `docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json` (PS-029)
- `docs/evidence/ps-035a/manifest-fixture.json` (PS-035A manifest fixture)
- `apps/web/src/b2Evidence.ts` (PS-026 verified golden constants, read-only reuse)

Golden-run canonical constants reused (read-only):

- run_id: `run_89d967f9000045efa22ed4cc78cfa67f`
- campaign_id: `camp_bea5161faa6244079d2ee01ce445c259`
- archive reference (archive_uri): the recorded Backblaze B2 archive URI
- archive sha256: `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
- manifest reference (manifest_uri): `docs/evidence/ps-035a/manifest-fixture.json`
- manifest hash: `438fabca46481a232373067eedb6d0e3a684c8ed513410dfe2047e3b4950022f`
  (the independent SHA-256 recomputed over the exact bytes of the PS-035A
  manifest fixture)
- rehydrate source: `b2_rehydrated`
- provider calls during rehydrate: `0`
- no live provider call during rehydrate: `true`
- public deployment pending: `true`

## 5. Vault records surfaced

Each record exposes `record_key`, `value`, `available`, `source_paths`, and
`verification`:

- `archive_reference` — the recorded B2 archive URI (locally verified)
- `archive_sha256` — the recorded archive SHA-256 (locally verified)
- `manifest_reference` — the manifest URI (locally verified)
- `manifest_hash` — the recorded manifest SHA-256 (locally verified; present)
- `rehydrate_source` — `b2_rehydrated` (locally verified)
- `provider_calls_during_rehydrate` — `0` (locally verified)
- `no_live_provider_call_during_rehydrate` — `true` (locally verified)
- `b2_evidence_status` — `present` (locally verified)

The manifest record IS present in accepted evidence (PS-024 / PS-035A), so the
vault shows it verbatim. If a future vault sourced from evidence with no
manifest record, it would show an honest "not available" state and would never
fabricate a value.

## 6. Exact truth-boundary copy added

The persistent truth-boundary panel (spec section 11, verbatim):

> The B2 Audit Vault shows what the pipeline recorded: the archive reference,
> archive SHA-256, manifest hash when present, rehydrate source, and zero
> provider calls during rehydrate. It is not live B2 verification. It is not
> Object Lock. It is not tamper-proof. It is not production security. It is not
> legal authenticity. It is not semantic truth.

The not-claimed / unknown panel surfaces: not live B2 verification, not Object
Lock, not tamper-proof, not production security, not legal authenticity, not
semantic truth.

## 7. Audit contract (notes)

Audit contract anchors surfaced by the vault and enforced by the smoke:

- notes
- B2 evidence
- no broad B2 reads
- hidden Git flags h and S
- do not claim Object Lock / tamper-proof storage unless implemented and verified
- do not claim browser-side B2 byte verification unless implemented and verified
- do not claim actual spend/latency/quota unless captured
- do not claim provider failures/reruns/variants unless evidenced

## 8. Truth boundary

ProofStudio proves what the pipeline recorded. The Archive / Rehydrate / B2
Audit Vault is an evidence-reading surface over recorded B2 / archive /
rehydrate evidence, not a legal authenticity system and not a live B2 verifier.

"B2 system of record" in PS-036 means Backblaze B2 is surfaced as the durable
archive behind the verified golden run. It does not mean Object Lock,
tamper-proof storage, browser-side B2 byte verification, production security,
live B2 availability, legal authenticity, semantic truth, or human authorship.

PS-036 does not prove product correctness, production security, B2
immutability, Object Lock, tamper-proof storage, browser-side B2 byte
verification, live B2 availability, real billing API integration, billing
behavior, CI enforcement, or deployment readiness. The vault records the
digests and references the pipeline already captured; it does not re-fetch or
re-hash live B2 bytes.

## 9. Validation

PS-036 ships one feature smoke:
`scripts/ps036_archive_rehydrate_b2_audit_vault_smoke.py`.

- Default behavior is non-mutating local validation (`--check-only`).
- `--write-evidence` writes only
  `docs/evidence/ps-036/archive-rehydrate-b2-audit-vault-report.json`.
- The smoke validates only PS-036; it never launches another feature smoke and
  never calls the central regression gate.
- The smoke uses its own explicit h/S checker over `git ls-files -v` and fails
  when `line[0]` is `h` or `S` (a lowercase-only marker check is not sufficient
  because it misses uppercase `S` skip-worktree).
- The smoke performs no provider call, no live B2 read, no B2 write, and no
  broad B2 scan.

Central regression gate (non-mutating, contract-only):

```
python scripts/proofstudio_regression_gate.py --current ps036 --no-frontend --report-out /tmp/proofstudio-ps036-regression-report.json
```
