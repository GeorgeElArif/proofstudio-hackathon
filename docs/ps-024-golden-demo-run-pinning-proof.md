# PS-024 — Golden Demo Run Pinning

## Status

Implemented. Canonical demo manifest created with verified durable evidence
values from PS-021. Passport pinning is **honestly blocked**: no verified run
currently resolves on the public deployment. PS-024 smoke passes (11/11
checks). PS-023 smoke still passes. Frontend typecheck and build pass.

### Root-cause patch (validation vocabulary alignment)

An earlier WSL gate failed because the homepage blocked-state check expected
the literal phrase **"golden demo"**, but `JudgeCockpitHome` did not yet carry
that phrase. This was validation vocabulary drift plus a small product-copy
clarity gap — not a product failure. The patch aligns both sides:

- **Product copy.** `JudgeCockpitHome.tsx` now has a dedicated "Golden demo
  run" section (`#golden-demo-run`) using the canonical phrase. The copy stays
  honest: public Provenance Passport pinning is blocked until a verified
  public durable passport run exists; verified durable evidence exists from
  PS-021; no fake `/passport/run_…` link is pinned; no `public_passport_url`
  is invented.
- **Canonical PS-024 smoke now owns the homepage blocked-state wording
  check.** `check_homepage_honest` in
  `scripts/ps024_golden_demo_run_pinning_smoke.py` requires the homepage to
  contain: `golden demo`, `verified durable evidence`, `provenance passport`,
  `run_id`, and a `blocked` or `planned` marker (in addition to the existing
  "no hard-coded pinned href" rule). This keeps the validator and the product
  copy locked to the same vocabulary so the drift cannot silently recur.

## Purpose

Pin one canonical judge-facing demo run across ProofStudio so a judge can open
the strongest available run/passport/evidence without guessing IDs.

## Discovery process

PS-024 requires discovery from existing evidence before pinning anything. The
following source files were inspected in full:

### Source evidence files inspected

| File | What it provides |
|------|-----------------|
| `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json` | **Strongest evidence.** Verified run_id, campaign_id, real B2 archive URI + SHA-256, `durable_source: b2_rehydrated`, `provider_calls_during_rehydrate: 0`, `no_live_provider_call_during_rehydrate: true`. |
| `docs/evidence/ps-019/live-public-passport-smoke-summary.json` | Verified public passport URL pattern + a live passport URL that was valid at smoke time (ephemeral in-memory run). |
| `docs/evidence/ps-019/local-passport-smoke-summary.json` | Local passport smoke (in-memory run). |
| `docs/evidence/ps-020/durable-passport-foundation-smoke.json` | Durable foundation local rehydrate (durable_source: local_rehydrated). |
| `docs/ps-021-live-b2-durable-rehydrate-proof.md` | PS-021 proof narrative. |
| `docs/ps-019-public-passport-proof-score-proof.md` | PS-019 proof narrative. |
| `docs/ps-020-durable-passport-b2-rehydrate-proof.md` | PS-020 proof narrative. |
| `docs/submission/judge-evidence-pack.md` | Judge evidence pack. |
| `README.md` | Project README with PS-018B + PS-019 deployment info. |
| `apps/web/src/JudgeCockpitHome.tsx` | PS-023 judge cockpit home. |
| `apps/web/src/App.tsx` | Client-side router. |
| `apps/web/src/PublicPassportPage.tsx` | Public passport route component (PS-019). |

### Priority evaluation

The spec defines a 7-point priority for selecting the strongest canonical demo
source:

| # | Criterion | Result | Source |
|---|-----------|--------|--------|
| 1 | Public passport route works | **Yes** — route pattern `/passport/<run_id>` is implemented and was verified live (PS-019). | PS-019 |
| 2 | Proof score exists | **Conditional** — deterministic UI-local computation over a live passport response; no pinned score without a pinned passport response. | PS-019 |
| 3 | B2 archive URI exists | **Yes** | PS-021 |
| 4 | B2 readback proof exists | **Yes** (`b2_archive_read: true`) | PS-021 |
| 5 | Rehydrate proof exists | **Yes** (`durable_source: b2_rehydrated`, `rehydrate_completed: true`) | PS-021 |
| 6 | Provider calls during rehydrate equals zero | **Yes** (`provider_calls_during_rehydrate: 0`) | PS-021 |
| 7 | Truth boundary exists | **Yes** | PS-019/PS-021 |

PS-021 satisfies criteria 3–7 fully and is the strongest durable evidence
source. However, criteria 1–2 cannot be combined into a **working pinned
public passport URL** for the PS-021 run, because:

- The PS-021 run (`run_89d967f9000045efa22ed4cc78cfa67f`) was created during a
  **local smoke test** and is not present in the public backend's in-memory
  store.
- The public deployment's durable read gates
  (`PROOFSTUDIO_DURABLE_PASSPORT_READ_ENABLED` and
  `PROOFSTUDIO_DURABLE_PASSPORT_B2_READ_ENABLED`) both **default to false**
  (`durable_read_enabled_default: false`, `durable_b2_read_enabled_default:
  false` in the PS-021 evidence). Without these gates explicitly enabled,
  `GET /runs/<run_id>/passport` returns 404 for any run not in memory.
- The PS-019 live run (`run_b852f08667bf4178b931d8466be1b2c8`) had a working
  passport URL **at smoke time only**. The public backend store is in-memory,
  so that run is no longer guaranteed to exist after a backend restart. It has
  no B2 archive evidence.

### Decision

**No verified run_id with a currently-working public passport URL exists.**
Passport pinning is **honestly blocked**.

Per the spec's non-negotiable rule, PS-024 does not invent a run ID, campaign
ID, passport URL, manifest URI, proof score, or archive proof. Instead:

- A canonical demo manifest records all verified durable evidence values from
  PS-021.
- `public_passport_url` is null with a clear reason.
- The homepage CTA is updated to reflect the honest blocked state and to
  reduce friction by linking to the verified PS-021 durable proof.

### Evidence discrepancy noted (not fixed)

The PS-021 proof doc text (`docs/ps-021-live-b2-durable-rehydrate-proof.md`)
and the PS-023 proof doc reference values from an earlier PS-021 run
(`run_9567ddc8…`, archive sha256 `21c5805c…`). The machine-generated evidence
JSON (`docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json`) contains
the final canonical values (`run_89d967f9…`, archive sha256 `a6ade0a6…`).
The PS-024 spec's "Current Proven Base" section confirms the evidence JSON
values are canonical (archive SHA-256 `a6ade0a6…` + matching archive URI).
PS-024 uses the **evidence JSON** as the single source of truth. The proof
doc text discrepancy is a pre-existing documentation issue in PS-021/PS-023
and is not modified by PS-024.

## Canonical demo manifest

Created at `docs/evidence/demo/golden-demo-run.json`.

### Verified values (from PS-021 evidence JSON)

| Field | Value | Source |
|-------|-------|--------|
| `demo_id` | `golden-demo-run-ps-024` | PS-024 (identifier only) |
| `source_slice` | `PS-021` | strongest durable evidence source |
| `run_id` | `run_89d967f9000045efa22ed4cc78cfa67f` | PS-021 evidence JSON |
| `campaign_id` | `camp_bea5161faa6244079d2ee01ce445c259` | PS-021 evidence JSON |
| `public_app_url` | `https://proofstudio-web.onrender.com` | PS-018B (README) |
| `public_api_url` | `https://proofstudio.onrender.com` | PS-018B (README) |
| `archive_uri` | `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json` | PS-021 evidence JSON |
| `archive_sha256` | `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141` | PS-021 evidence JSON |
| `rehydrate_source` | `b2_rehydrated` | PS-021 evidence JSON (`durable_source`) |
| `provider_calls_during_rehydrate` | `0` | PS-021 evidence JSON |
| `no_live_provider_call_during_rehydrate` | `true` | PS-021 evidence JSON |
| `truth_boundary` | (truth boundary text) | PS-023 verbatim |

### Null / unavailable fields

| Field | Value | Reason |
|-------|-------|--------|
| `public_passport_url` | `null` | The PS-021 verified run was created during a local smoke and is not present in the public backend's in-memory store. The public deployment's durable read gates default to false, so `/passport/<run_id>` returns 404 for this run. No passport URL is invented. |
| `manifest_uri` | `null` | Not captured in the PS-021 durable rehydrate smoke evidence. The PS-021 archive is a full run archive, not a Genblaze manifest. |
| `manifest_hash` | `null` | Not captured in the PS-021 durable rehydrate smoke evidence. |
| `proof_score` | `null` | Proof Score is a deterministic UI-local computation over a live passport API response (PS-019). No pinned passport response is fetchable on the public deployment, so no pinned score is recorded. Inventing a score would violate the non-negotiable rule. |

## CTA target map

Every CTA targets either an implemented client route, a verified external doc,
or an honest blocked/planned state. No broken links were introduced.

| CTA | Target | Status |
|-----|--------|--------|
| Open Judge Demo (hero + CTA grid) | `/review` | **implemented** (PS-013/PS-014 Review Room) |
| View Provenance Passport (hero) | disabled until a `run_id` is entered; PS-024 honestly blocked | route **implemented** (PS-019); pinning **blocked** (PS-024) |
| Open Passport (by run id) | `/passport/<run_id>` once a valid id is pasted | **implemented** (PS-019) |
| View Verified Durable Evidence | GitHub: `docs/ps-021-live-b2-durable-rehydrate-proof.md` | **verified** (PS-021 proof on main) |
| View Evidence Pack | GitHub: `docs/submission/judge-evidence-pack.md` | **repo doc** (existing) |
| Read Submission Notes | GitHub: `docs/submission/` | **repo doc** (existing) |
| Open GitHub / README | `https://github.com/GeorgeElArif/proofstudio` | **configured `origin` remote** |

No `/demo` or `/demo/golden` route was added. Passport pinning is blocked, so
a dedicated demo route would only duplicate the homepage without adding value.
A direct pinned homepage CTA is cleaner and lower-risk, as the spec allows.

## No-fake-proof confirmation

PS-024 does not invent any run ID, campaign ID, passport URL, manifest URI,
proof score, or archive proof. Every non-null value in the manifest is traced
to a source evidence file. The four null fields are explicitly recorded with
reasons in `unavailable_fields`. The homepage does not hard-code a pinned
passport link. The smoke script validates all of these statically.

## Truth boundary confirmation

The canonical demo manifest and the homepage both carry the truth boundary:

> ProofStudio proves what this pipeline did. It does not prove semantic truth,
> legal authenticity, C2PA authenticity, or human authorship.

The manifest records this as the `truth_boundary` field. The homepage renders
it verbatim in the `#truth-boundary` section (PS-023 constant
`TRUTH_BOUNDARY_TEXT`). No truth boundary was removed or weakened.

## Smoke / validation script (canonical command)

```bash
python scripts/ps024_golden_demo_run_pinning_smoke.py
```

This is the canonical PS-024 validation command. It performs eleven static
checks and exits non-zero on any failure:

1. `manifest_exists` — the canonical demo manifest exists.
2. `pinned_values_match` — every non-null manifest value is traceable to a
   source evidence file.
3. `no_invented_ids` — run_id/campaign_id appear in evidence; passport URL
   and proof score are null.
4. `homepage_honest` — homepage carries the canonical PS-024 blocked-state
   wording for the golden demo run (`golden demo`, `verified durable
   evidence`, `provenance passport`, `run_id`, and a `blocked`/`planned`
   marker) and contains no hard-coded pinned passport href.
5. `archive_match` — archive URI/hash match PS-021 evidence exactly.
6. `rehydrate_match` — rehydrate fields match PS-021 evidence exactly.
7. `truth_boundary` — manifest and homepage carry the truth boundary.
8. `forbidden_claims` — context-aware scan; no affirmative overclaim.
9. `secret_scan` — no secrets in changed files.
10. `route_markers` — no existing route/CTA marker removed (PS-023 compat).
11. `ps023_callable` — PS-023 smoke script is present.

## Validation commands run

| Command | Result |
|---------|--------|
| `python scripts/ps024_golden_demo_run_pinning_smoke.py` | **PASS** (11/11) |
| `python scripts/ps023_judge_cockpit_home_smoke.py` | **PASS** (6/6) |
| `npm run typecheck` (apps/web) | **pass** (`tsc --noEmit`, no errors) |
| `npm run build` (apps/web) | **pass** (34 modules, `dist/` written) |
| `git diff --check` | **pass** (exit 0; no whitespace errors) |

Forbidden-claim scan (context-aware, exit 1 = no matches):

```
rg -n -i "ProofStudio (proves|is|provides|offers|supports) (semantic truth|legal authenticity|human authorship|c2pa|production security|enterprise|multi-user|object lock|tamper-proof)" apps/web/src docs/ps-024-golden-demo-run-pinning-proof.md docs/evidence/demo/golden-demo-run.json
```

Secret scan: clean. No API keys, tokens, bearer strings, or AWS/B2 credential
literals in any changed file.

## Files changed

All changes are confined to the PS-024 scope. No unrelated files were touched.
No historical proof scripts (ps004–ps023), provider code, API backend code, or
deployment config were modified.

- `docs/evidence/demo/golden-demo-run.json` — **new**. Canonical demo manifest
  recording verified durable evidence from PS-021 with null+reason for blocked
  fields.
- `apps/web/src/JudgeCockpitHome.tsx` — updated. Hero passport CTA title,
  passport preview hint, passport CTA tile pill/description, and a new "View
  Verified Durable Evidence" CTA tile linking to the PS-021 proof. No routes
  changed; no truth boundary removed.
- `docs/ps-024-golden-demo-run-pinning-proof.md` — **new**. This proof doc.
- `scripts/ps024_golden_demo_run_pinning_smoke.py` — **new**. Canonical PS-024
  validation script.

## Limitations / risks

- **Passport pinning is blocked, not resolved.** A future slice must enable
  durable reads on the public backend (or persist a verified run to the public
  in-memory store + B2) before the homepage can pin a working
  `/passport/<run_id>` link. The manifest records everything needed to wire
  that up once the gates are enabled.
- **No `/demo` route was added.** The spec allows a direct pinned homepage CTA
  as a cleaner alternative. Since pinning is blocked, a demo route would add
  risk without value.
- **Pre-existing evidence discrepancy.** The PS-021 proof doc text references
  values from an earlier run (`run_9567ddc8…` / sha `21c5805c…`) that differ
  from the canonical evidence JSON (`run_89d967f9…` / sha `a6ade0a6…`). PS-024
  uses the evidence JSON as the source of truth (confirmed by the PS-024 spec
  "Current Proven Base" section). The proof doc text discrepancy is not fixed
  by PS-024 to avoid modifying historical artifacts.
- **External GitHub links** (`View Verified Durable Evidence`, `View Evidence
  Pack`, `Read Submission Notes`, `Open GitHub`) point at the configured
  `origin` remote on `main`. These are honest references to existing repo
  paths. The canonical manifest JSON is new in this branch and will only be
  reachable on GitHub after merge.
- **No backend-driven content.** The homepage is static copy grounded in prior
  proof docs and the manifest; it does not fetch live evidence. Live evidence
  remains on `/review` and `/passport/<run_id>`.

## Working tree

Only PS-024 files were changed. No commit, push, or stage was performed.

```
apps/web/src/JudgeCockpitHome.tsx                    (modified)
docs/evidence/demo/golden-demo-run.json              (new)
docs/ps-024-golden-demo-run-pinning-proof.md         (new)
scripts/ps024_golden_demo_run_pinning_smoke.py       (new)
```
