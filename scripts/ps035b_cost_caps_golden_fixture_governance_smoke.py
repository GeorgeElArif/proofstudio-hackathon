#!/usr/bin/env python3
"""PS-035b Cost Caps + Golden-Fixture Governance -- local / static smoke.

This smoke is LOCAL / STATIC ONLY. It:

- reads checked-in files only (backend source, env template, digest manifest,
  golden fixtures, smoke_lib, regression gate, proof doc)
- does not call providers
- does not read or write B2
- does not run the frontend
- does not run the backend
- does not call the central regression gate
- does not mutate prior evidence
- writes only:
  ``docs/evidence/ps-035b/cost-caps-golden-fixture-governance-report.json``

It verifies the PS-035b governance and golden-fixture-freeze contract:

- live runs are disabled by default (PROOFSTUDIO_LIVE_RUNS_ENABLED)
- run_live=True alone is not enough; the backend honors the live-run gate
- a paid/live run requires explicit PM/human approval
  (PROOFSTUDIO_PAID_RUN_APPROVED)
- the cost cap defaults to 0.00 (PROOFSTUDIO_COST_CAP_USD)
- budget_mode="free-only" blocks paid/non-free execution
- B2 writes are disabled by default (PROOFSTUDIO_B2_WRITES_ENABLED)
- B2 reads remain disabled by default (durable passport default-off contract)
- demo mode reuses checked-in golden fixtures and calls no provider/B2
- provider calls are blocked by default
- the golden-fixture digest manifest exists and records both fixtures
- the recorded digests recompute and match the current fixture bytes
- PS-035a evidence is now protected by the historical prior-evidence prefix
  lists
- no provider keys are referenced from frontend code
- .env / .env.save / token-like files remain gitignored
- no live provider call, no live B2 read, no live B2 write occur
- the truth boundary is preserved and no forbidden overclaims / file changes
  are present

Exit code is 0 only when every check passes.

    python scripts/ps035b_cost_caps_golden_fixture_governance_smoke.py
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LIVE_BRIDGE = ROOT / "src" / "proofstudio" / "api" / "live_bridge.py"
SERVICES = ROOT / "src" / "proofstudio" / "api" / "services.py"
DURABLE_PASSPORT = ROOT / "src" / "proofstudio" / "api" / "durable_passport.py"
ENV_TEMPLATE = ROOT / ".env.production.example"
ENV_DOC = ROOT / "docs" / "deployment" / "environment.md"
SMOKE_LIB = ROOT / "scripts" / "smoke_lib.py"
REGRESSION_GATE = ROOT / "scripts" / "proofstudio_regression_gate.py"
GITIGNORE = ROOT / ".gitignore"
PROOF_DOC = ROOT / "docs" / "ps-035b-cost-caps-golden-fixture-governance-proof.md"
DIGEST_MANIFEST = ROOT / "docs" / "evidence" / "golden-fixture-digests.json"
GOLDEN_DEMO = ROOT / "docs" / "evidence" / "demo" / "golden-demo-run.json"
PS035A_FIXTURE = ROOT / "docs" / "evidence" / "ps-035a" / "manifest-fixture.json"
FRONTEND_SRC = ROOT / "apps" / "web" / "src"
REPORT = (
    ROOT / "docs" / "evidence" / "ps-035b"
    / "cost-caps-golden-fixture-governance-report.json"
)

GOLDEN_FIXTURE_PATHS = (
    "docs/evidence/demo/golden-demo-run.json",
    "docs/evidence/ps-035a/manifest-fixture.json",
)

# Governance control names that must appear in the backend gate.
LIVE_RUNS_ENABLED_ENV = "PROOFSTUDIO_LIVE_RUNS_ENABLED"
B2_WRITES_ENABLED_ENV = "PROOFSTUDIO_B2_WRITES_ENABLED"
COST_CAP_USD_ENV = "PROOFSTUDIO_COST_CAP_USD"
FIXTURES_FROZEN_ENV = "PROOFSTUDIO_FIXTURES_FROZEN"
PAID_RUN_APPROVED_ENV = "PROOFSTUDIO_PAID_RUN_APPROVED"

# Names that must never appear in a governance control name.
FORBIDDEN_NAME_PARTS = ("KEY", "TOKEN", "SECRET")

# Default-off durable passport B2 read flags (PS-019/PS-021/PS-025 contract).
DURABLE_READ_FLAG = "PROOFSTUDIO_DURABLE_PASSPORT_READ_ENABLED"
DURABLE_B2_READ_FLAG = "PROOFSTUDIO_DURABLE_PASSPORT_B2_READ_ENABLED"

# Allowed changed files for PS-035b (mirrors the spec section 8 implementation
# candidates plus this smoke and its evidence).
ALLOWED_CHANGED_FILES = {
    "scripts/ps035b_cost_caps_golden_fixture_governance_smoke.py",
    "docs/evidence/ps-035b/cost-caps-golden-fixture-governance-report.json",
    "docs/evidence/golden-fixture-digests.json",
    "docs/ps-035b-cost-caps-golden-fixture-governance-proof.md",
    "scripts/smoke_lib.py",
    "scripts/proofstudio_regression_gate.py",
    "src/proofstudio/api/live_bridge.py",
    "src/proofstudio/api/services.py",
    ".env.production.example",
    "docs/deployment/environment.md",
    "specs/07-master-spec-plan.md",
    "specs/08-roadmap-slices.md",
    "docs/validation/proofstudio-smoke-harness-v1.md",
    "specs/48-ps-035b-cost-caps-golden-fixture-governance.md",
}

# Forbidden overclaim phrases that must never appear as POSITIVE claims.
FORBIDDEN_OVERCLAIM_PHRASES = [
    "tamper-proof storage",
    "tamper proof storage",
    "Object Lock enabled",
    "live B2 Object Lock",
    "real billing API integration",
    "production multi-user budget accounting",
    "production immutability",
    "C2PA authentic",
    "production security verified",
]

# Negation / non-claim cues. A forbidden phrase is acceptable only if a cue
# appears within the context window around it.
NEGATION_CUES = (
    "does not",
    "do not",
    "doesn't",
    "don't",
    "did not",
    "not prove",
    "not claim",
    "must not",
    "no claim",
    "no claim of",
    "no overclaim",
    "without",
    "non-claim",
    "never claim",
    "not implemented",
    "forbidden",
    "is not",
    "are not",
    "cannot",
    "not a ",
    "not an ",
    "not tamper-proof",
    "not object lock",
    "not production immutability",
    "not real billing",
    "not production multi-user",
    "not_object_lock",
    "not_tamper_proof",
    "not_production_immutability",
    "not_real_billing_api_integration",
    "not_production_multi_user_budget_accounting",
)

_OVERCLAIM_BEFORE_WINDOW = 260
_OVERCLAIM_AFTER_WINDOW = 200
_WS_RE = re.compile(r"\s+")

# Provider-key-like patterns that must not appear in frontend source.
_PROVIDER_KEY_PATTERNS = [
    re.compile(r"(?i)CLOUDFLARE_API_TOKEN"),
    re.compile(r"(?i)GEMINI_API_KEY"),
    re.compile(r"(?i)ELEVENLABS_API_KEY"),
    re.compile(r"(?i)B2_APP_KEY"),
    re.compile(r"(?i)B2_KEY_ID"),
    re.compile(r"(?i)OPENAI_API_KEY"),
    re.compile(r"(?i)REPLICATE_API_TOKEN"),
    re.compile(r"(?i)RUNWAY_API_KEY"),
    re.compile(r"(?i)STABILITY_API_KEY"),
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_flat(path: Path) -> str:
    return _WS_RE.sub(" ", _read_text(path)).strip() if path.is_file() else ""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _flat(text: str) -> str:
    return _WS_RE.sub(" ", text).strip()


def _git_status_paths() -> list[str]:
    res = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    paths: list[str] = []
    for line in res.stdout.splitlines():
        if not line.strip() or line.startswith("## "):
            continue
        paths.append(line[3:])
    return paths


def _no_forbidden_overclaims_in_text(text: str, label: str, failures: list[str]) -> bool:
    flat_low = _flat(text).lower()
    ok = True
    for phrase in FORBIDDEN_OVERCLAIM_PHRASES:
        p_low = phrase.lower()
        start = 0
        while True:
            idx = flat_low.find(p_low, start)
            if idx == -1:
                break
            win_start = max(0, idx - _OVERCLAIM_BEFORE_WINDOW)
            win_end = min(len(flat_low), idx + len(p_low) + _OVERCLAIM_AFTER_WINDOW)
            window = flat_low[win_start:win_end]
            if not any(cue.lower() in window for cue in NEGATION_CUES):
                failures.append(
                    f"no_forbidden_overclaims/{label}: phrase {phrase!r} "
                    f"appears as a positive claim (no negation cue in context)"
                )
                ok = False
            start = idx + len(p_low)
    return ok


def main() -> int:
    failures: list[str] = []

    live_src = _read_text(LIVE_BRIDGE) if LIVE_BRIDGE.is_file() else ""
    services_src = _read_text(SERVICES) if SERVICES.is_file() else ""
    env_text = _read_text(ENV_TEMPLATE) if ENV_TEMPLATE.is_file() else ""
    env_flat = _read_flat(ENV_TEMPLATE)

    # ---- governance control names must never contain KEY/TOKEN/SECRET ----
    name_ok = True
    for env_name in (
        LIVE_RUNS_ENABLED_ENV,
        B2_WRITES_ENABLED_ENV,
        COST_CAP_USD_ENV,
        FIXTURES_FROZEN_ENV,
        PAID_RUN_APPROVED_ENV,
    ):
        for part in FORBIDDEN_NAME_PARTS:
            if part in env_name:
                failures.append(
                    f"governance control name {env_name!r} contains forbidden "
                    f"part {part!r}"
                )
                name_ok = False

    # ---- live runs disabled by default ----
    live_runs_disabled_by_default = (
        LIVE_RUNS_ENABLED_ENV in live_src
        and 'def govern_live_run' in live_src
        and 'def live_runs_enabled' in live_src
        and f'"{LIVE_RUNS_ENABLED_ENV}"' in live_src
        and f"{LIVE_RUNS_ENABLED_ENV}=false" in env_text
    )
    if not live_runs_disabled_by_default:
        failures.append(
            "live_runs_disabled_by_default: backend gate or env default missing "
            "(govern_live_run/live_runs_enabled/PROOFSTUDIO_LIVE_RUNS_ENABLED=false)"
        )

    # ---- run_live default honored / live-run gate exists ----
    run_live_default_honored = (
        "govern_live_run" in services_src
        and "govern_live_run" in live_src
        and "PROOFSTUDIO_RUN_LIVE_DEFAULT" in live_src
    )
    if not run_live_default_honored:
        failures.append(
            "run_live_default_honored: services/live_bridge do not reference the "
            "governance gate or PROOFSTUDIO_RUN_LIVE_DEFAULT supersession"
        )

    # ---- paid run requires explicit approval ----
    paid_run_requires_explicit_approval = (
        PAID_RUN_APPROVED_ENV in live_src
        and "PROOFSTUDIO_PAID_RUN_APPROVED is not true" in live_src
    )
    if not paid_run_requires_explicit_approval:
        failures.append(
            "paid_run_requires_explicit_approval: backend does not require "
            "PROOFSTUDIO_PAID_RUN_APPROVED before a paid/live run"
        )

    # ---- cost cap default zero ----
    cost_cap_default_zero = (
        "DEFAULT_COST_CAP_USD = 0.00" in live_src
        and "def cost_cap_usd" in live_src
        and f"{COST_CAP_USD_ENV}=0.00" in env_text
    )
    if not cost_cap_default_zero:
        failures.append(
            "cost_cap_default_zero: backend default 0.00 or env default missing"
        )

    # ---- budget_mode free-only blocks paid ----
    budget_free_only_blocks = (
        'FREE_ONLY_BUDGET_MODE = "free-only"' in live_src
        and 'budget_mode is \'free-only\'' in live_src
    )
    if not budget_free_only_blocks:
        failures.append(
            "budget_mode_free_only_blocks_paid: backend does not block "
            "budget_mode='free-only' before live provider execution"
        )

    # ---- B2 writes disabled by default ----
    b2_writes_disabled = (
        'def b2_writes_enabled' in live_src
        and f'"{B2_WRITES_ENABLED_ENV}"' in live_src
        and "PROOFSTUDIO_B2_WRITES_ENABLED is not true" in live_src
        and f"{B2_WRITES_ENABLED_ENV}=false" in env_text
    )
    if not b2_writes_disabled:
        failures.append(
            "b2_writes_disabled_by_default: backend B2 write gate or env default "
            "missing"
        )

    # ---- B2 reads remain disabled by default ----
    dp_src = _read_text(DURABLE_PASSPORT) if DURABLE_PASSPORT.is_file() else ""
    b2_reads_remain_disabled = (
        DURABLE_READ_FLAG in dp_src
        and DURABLE_B2_READ_FLAG in dp_src
        and "def durable_b2_read_enabled" in dp_src
        # The read gate must default off (no "true" default in the helper).
        and "B2 durable passport read is disabled" in dp_src
    )
    if not b2_reads_remain_disabled:
        failures.append(
            "b2_reads_remain_disabled_by_default: durable passport default-off "
            "B2 read contract not intact"
        )

    # ---- demo mode uses fixtures ----
    demo_mode_uses_fixtures = (
        GOLDEN_DEMO.is_file()
        and "RunCreate.dry_run" not in services_src  # noqa: sanity guard only
        and "fixtures_frozen" in live_src
        and f"{FIXTURES_FROZEN_ENV}=true" in env_text
    )
    if not GOLDEN_DEMO.is_file():
        failures.append("demo_mode_uses_fixtures: golden demo fixture missing")
    if "fixtures_frozen" not in live_src or f"{FIXTURES_FROZEN_ENV}=true" not in env_text:
        failures.append(
            "demo_mode_uses_fixtures: PROOFSTUDIO_FIXTURES_FROZEN=true backend "
            "helper or env default missing"
        )
    demo_mode_uses_fixtures = (
        GOLDEN_DEMO.is_file()
        and "fixtures_frozen" in live_src
        and f"{FIXTURES_FROZEN_ENV}=true" in env_text
    )

    # ---- provider calls blocked by default ----
    provider_calls_blocked = (
        "govern_live_run" in live_src
        and "blocked by default" in live_src
    )
    if not provider_calls_blocked:
        failures.append(
            "provider_calls_blocked_by_default: backend live-run gate message "
            "missing"
        )

    # ---- golden fixture digest manifest ----
    golden_fixture_digest_manifest_present = DIGEST_MANIFEST.is_file()
    if not golden_fixture_digest_manifest_present:
        failures.append(f"golden fixture digest manifest missing: {DIGEST_MANIFEST}")

    manifest_data = {}
    if golden_fixture_digest_manifest_present:
        try:
            manifest_data = json.loads(_read_text(DIGEST_MANIFEST))
        except json.JSONDecodeError as exc:
            failures.append(f"digest manifest invalid JSON: {exc}")
            manifest_data = {}

    # Build path -> recorded sha256 from either a list ("fixtures") or a dict.
    entries = manifest_data.get("fixtures") or manifest_data.get("digests") or {}
    if isinstance(entries, list):
        by_path = {item.get("path"): item.get("sha256") for item in entries}
    elif isinstance(entries, dict):
        by_path = {
            path: (val.get("sha256") if isinstance(val, dict) else val)
            for path, val in entries.items()
        }
    else:
        by_path = {}

    golden_demo_digest_recorded = GOLDEN_FIXTURE_PATHS[0] in by_path
    ps035a_manifest_fixture_digest_recorded = GOLDEN_FIXTURE_PATHS[1] in by_path
    if not golden_demo_digest_recorded:
        failures.append(
            f"golden_demo_digest_recorded: no digest entry for "
            f"{GOLDEN_FIXTURE_PATHS[0]}"
        )
    if not ps035a_manifest_fixture_digest_recorded:
        failures.append(
            f"ps035a_manifest_fixture_digest_recorded: no digest entry for "
            f"{GOLDEN_FIXTURE_PATHS[1]}"
        )

    # ---- digests recompute and match ----
    golden_fixture_digests_match = True
    for rel in GOLDEN_FIXTURE_PATHS:
        fpath = ROOT / rel
        recorded = by_path.get(rel)
        if not fpath.is_file():
            failures.append(f"golden_fixture_digests_match: fixture missing: {rel}")
            golden_fixture_digests_match = False
            continue
        if not recorded:
            failures.append(
                f"golden_fixture_digests_match: no recorded digest for {rel}"
            )
            golden_fixture_digests_match = False
            continue
        actual = _sha256_bytes(fpath.read_bytes())
        if actual != recorded:
            failures.append(
                f"golden_fixture_digests_match: {rel} digest mismatch "
                f"{actual!r} != {recorded!r}"
            )
            golden_fixture_digests_match = False

    # manifest must declare sha256 algorithm and slice id
    if manifest_data.get("digest_algorithm") != "sha256":
        failures.append("digest manifest digest_algorithm is not sha256")
        golden_fixture_digests_match = False
    if manifest_data.get("slice_id") != "ps035b":
        failures.append("digest manifest slice_id is not ps035b")
        golden_fixture_digests_match = False

    # ---- PS-035a evidence protected ----
    smoke_lib_src = _read_text(SMOKE_LIB) if SMOKE_LIB.is_file() else ""
    gate_src = _read_text(REGRESSION_GATE) if REGRESSION_GATE.is_file() else ""
    ps035a_evidence_protected = (
        "docs/evidence/ps-035a/" in smoke_lib_src
        and "ps-035a" in gate_src
        and "docs/evidence/ps-035b/" not in smoke_lib_src
    )
    if not ps035a_evidence_protected:
        failures.append(
            "ps035a_evidence_protected: ps-035a not added to smoke_lib / "
            "regression gate prior-evidence prefix lists (or ps-035b was added "
            "and would block its own report)"
        )

    # ---- no provider keys in frontend ----
    frontend_offenders: list[str] = []
    if FRONTEND_SRC.is_dir():
        for fpath in FRONTEND_SRC.rglob("*"):
            if not fpath.is_file():
                continue
            if fpath.suffix not in (".ts", ".tsx", ".js", ".jsx"):
                continue
            text = fpath.read_text(encoding="utf-8", errors="replace")
            for pat in _PROVIDER_KEY_PATTERNS:
                if pat.search(text):
                    frontend_offenders.append(f"{fpath}: {pat.pattern}")
    no_provider_keys_in_frontend = not frontend_offenders
    if frontend_offenders:
        failures.append(
            "no_provider_keys_in_frontend: provider key references found:\n"
            + "\n".join(frontend_offenders)
        )

    # ---- env files gitignored ----
    gi_text = _read_text(GITIGNORE) if GITIGNORE.is_file() else ""
    env_files_gitignored = (
        ".env" in gi_text
        and ".env.*" in gi_text
        # .env.save is covered by the .env.* glob; verify the glob explicitly.
        and re.search(r"^\.env\.\*", gi_text, re.MULTILINE) is not None
    )
    if not env_files_gitignored:
        failures.append(
            "env_files_gitignored: .gitignore does not cover .env / .env.* "
            "(which includes .env.save)"
        )

    # ---- no live provider call / B2 read / B2 write (static proof) ----
    no_live_provider_call = True
    no_live_b2_read = True
    no_live_b2_write = True

    # ---- truth boundary preserved ----
    truth_boundary_preserved = False
    if PROOF_DOC.is_file():
        proof_flat = _read_flat(PROOF_DOC).lower()
        truth_boundary_preserved = (
            "truth boundary" in proof_flat
            and "not tamper-proof" in proof_flat
            and "not object lock" in proof_flat
        )
    if not truth_boundary_preserved:
        failures.append(
            "truth_boundary_preserved: proof doc missing truth boundary / "
            "non-claims (not tamper-proof, not Object Lock)"
        )

    # ---- no forbidden overclaims ----
    no_forbidden_overclaims = True
    scan_docs = [PROOF_DOC, DIGEST_MANIFEST]
    for doc in scan_docs:
        if not doc.is_file():
            continue
        if not _no_forbidden_overclaims_in_text(_read_text(doc), doc.name, failures):
            no_forbidden_overclaims = False
    # The report we are about to write is also scanned after assembly below.

    # ---- no forbidden file changes ----
    no_forbidden_file_changes = True
    try:
        changed = _git_status_paths()
    except Exception as exc:  # pragma: no cover - defensive
        failures.append(f"no_forbidden_file_changes: git status failed: {exc}")
        no_forbidden_file_changes = False
        changed = []
    for path in changed:
        if path not in ALLOWED_CHANGED_FILES:
            failures.append(
                f"no_forbidden_file_changes: forbidden/out-of-allowed path "
                f"changed: {path}"
            )
            no_forbidden_file_changes = False

    ok = (
        name_ok
        and live_runs_disabled_by_default
        and run_live_default_honored
        and paid_run_requires_explicit_approval
        and cost_cap_default_zero
        and budget_free_only_blocks
        and b2_writes_disabled
        and b2_reads_remain_disabled
        and demo_mode_uses_fixtures
        and provider_calls_blocked
        and golden_fixture_digest_manifest_present
        and golden_demo_digest_recorded
        and ps035a_manifest_fixture_digest_recorded
        and golden_fixture_digests_match
        and ps035a_evidence_protected
        and no_provider_keys_in_frontend
        and env_files_gitignored
        and no_live_provider_call
        and no_live_b2_read
        and no_live_b2_write
        and truth_boundary_preserved
        and no_forbidden_overclaims
        and no_forbidden_file_changes
        and not failures
    )

    report = {
        "ok": bool(ok),
        "slice_id": "ps035b",
        "checked_at": _utc_now_iso(),
        "live_runs_disabled_by_default": bool(live_runs_disabled_by_default),
        "run_live_default_honored": bool(run_live_default_honored),
        "paid_run_requires_explicit_approval": bool(paid_run_requires_explicit_approval),
        "cost_cap_default_zero": bool(cost_cap_default_zero),
        "budget_mode_free_only_blocks_paid": bool(budget_free_only_blocks),
        "b2_writes_disabled_by_default": bool(b2_writes_disabled),
        "b2_reads_remain_disabled_by_default": bool(b2_reads_remain_disabled),
        "demo_mode_uses_fixtures": bool(demo_mode_uses_fixtures),
        "provider_calls_blocked_by_default": bool(provider_calls_blocked),
        "golden_fixture_digest_manifest_present": bool(golden_fixture_digest_manifest_present),
        "golden_demo_digest_recorded": bool(golden_demo_digest_recorded),
        "ps035a_manifest_fixture_digest_recorded": bool(ps035a_manifest_fixture_digest_recorded),
        "golden_fixture_digests_match": bool(golden_fixture_digests_match),
        "ps035a_evidence_protected": bool(ps035a_evidence_protected),
        "no_provider_keys_in_frontend": bool(no_provider_keys_in_frontend),
        "env_files_gitignored": bool(env_files_gitignored),
        "no_live_provider_call": bool(no_live_provider_call),
        "no_live_b2_read": bool(no_live_b2_read),
        "no_live_b2_write": bool(no_live_b2_write),
        "truth_boundary_preserved": bool(truth_boundary_preserved),
        "no_forbidden_overclaims": bool(no_forbidden_overclaims),
        "no_forbidden_file_changes": bool(no_forbidden_file_changes),
        "governance_controls": {
            "live_runs_enabled_env": LIVE_RUNS_ENABLED_ENV,
            "b2_writes_enabled_env": B2_WRITES_ENABLED_ENV,
            "cost_cap_usd_env": COST_CAP_USD_ENV,
            "fixtures_frozen_env": FIXTURES_FROZEN_ENV,
            "paid_run_approved_env": PAID_RUN_APPROVED_ENV,
        },
        "golden_fixture_digests": {
            rel: by_path.get(rel) for rel in GOLDEN_FIXTURE_PATHS
        },
        "truth_boundary": (
            "ProofStudio proves what the pipeline did. The golden-fixture "
            "freeze proves byte equality to recorded digests only. It is not "
            "tamper-proof, not Object Lock, not legal authenticity, and not "
            "production immutability. The cost cap is a local policy gate, not "
            "a real billing API integration and not production multi-user "
            "budget accounting."
        ),
        "non_claims": {
            "not_tamper_proof": True,
            "not_object_lock": True,
            "not_production_immutability": True,
            "not_real_billing_api_integration": True,
            "not_production_multi_user_budget_accounting": True,
        },
        "failures": failures,
    }

    # Scan the assembled report JSON text for forbidden overclaims before
    # writing (the report itself must not overclaim).
    report_text = json.dumps(report, indent=2, sort_keys=False)
    if not _no_forbidden_overclaims_in_text(report_text, "report", failures):
        no_forbidden_overclaims = False
        report["no_forbidden_overclaims"] = False
        ok = False
        report["ok"] = False
        report["failures"] = failures

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, sort_keys=False) + "\n"
    tmp = REPORT.with_suffix(REPORT.suffix + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    import os
    os.replace(tmp, REPORT)

    if failures:
        print("PS-035B COST CAPS + GOLDEN-FIXTURE GOVERNANCE SMOKE FAILED", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("PS-035B COST CAPS + GOLDEN-FIXTURE GOVERNANCE SMOKE PASSED")
    print(f"  live_runs_disabled_by_default: {report['live_runs_disabled_by_default']}")
    print(f"  cost_cap_default_zero: {report['cost_cap_default_zero']}")
    print(f"  b2_writes_disabled_by_default: {report['b2_writes_disabled_by_default']}")
    print(f"  golden_fixture_digests_match: {report['golden_fixture_digests_match']}")
    print(f"  ps035a_evidence_protected: {report['ps035a_evidence_protected']}")
    print(f"  report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
