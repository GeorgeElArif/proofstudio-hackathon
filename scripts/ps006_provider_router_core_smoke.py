#!/usr/bin/env python3
"""
PS-006: ProviderRouter Core deterministic smoke test.

What this proves:
- The reusable ProviderRouter runs providers in priority order.
- It stops on the first success and preserves every attempt (success, failure,
  and skip) in a JSON-serializable attempt ledger.
- It falls back correctly after failures and disabled providers.
- It returns ok=False with full failure evidence when all providers fail.
- It never fakes success and never creates fake generated image assets.

This smoke script performs NO network calls and requires NO API keys, NO B2,
NO Cloudflare, NO Pollinations, NO Gemini, NO GMICloud. It exercises the
deterministic router core using the fake providers in
``proofstudio.providers.fakes``.

Outputs:
- /tmp/proofstudio-ps-006/provider-router-core-summary.json
- /tmp/proofstudio-ps-006/provider-router-core-attempts.json

Exit code is non-zero if any scenario fails or outputs cannot be serialized.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from proofstudio.providers.fakes import (  # noqa: E402
    AlwaysFailProvider,
    AlwaysSucceedProvider,
    DisabledProvider,
)
from proofstudio.providers.router import ProviderRouter  # noqa: E402
from proofstudio.providers.types import (  # noqa: E402
    NS_OK,
    NS_PROVIDER_DOWN,
    NS_SKIPPED_DISABLED,
    ProviderJob,
)

OUTPUT_DIR = Path("/tmp/proofstudio-ps-006")
SUMMARY_PATH = OUTPUT_DIR / "provider-router-core-summary.json"
ATTEMPTS_PATH = OUTPUT_DIR / "provider-router-core-attempts.json"

JOB_TYPE = "image_generation"
SUCCESS_PROVIDER_ID = AlwaysSucceedProvider().provider_id
FAIL_PROVIDER_ID = AlwaysFailProvider().provider_id
DISABLED_PROVIDER_ID = DisabledProvider().provider_id

# Canonical acceptance-gate keys. Every scenario below must map to exactly one
# of these keys so downstream tooling has stable, predictable dict access.
SCENARIO_KEYS = ("scenario_a", "scenario_b", "scenario_c", "scenario_d")

# Full required attempt-ledger schema per specs/14-ps-006-provider-router-core.md
# section 7. Every record in the attempts JSON must carry every field below.
REQUIRED_ATTEMPT_FIELDS = (
    "attempt_id",
    "attempt_index",
    "provider",
    "model",
    "api_method",
    "job_type",
    "status",
    "normalized_status",
    "started_at",
    "finished_at",
    "latency_ms",
    "retryable",
    "fallback_allowed",
    "skip_reason",
    "raw_error_type",
    "sanitized_error_message",
    "estimated_cost",
    "free_or_paid",
    "output_asset_refs",
    "notes",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_job() -> ProviderJob:
    return ProviderJob(
        job_type=JOB_TYPE,
        prompt="PS-006 deterministic router-core smoke (no real generation).",
        budget_mode="free-only",
        campaign_id="proofstudio-launch",
    )


def assert_equal(label: str, got: Any, expected: Any) -> list[str]:
    if got == expected:
        return []
    return [
        f"{label}: expected {expected!r}, got {got!r}",
    ]


def assert_true(label: str, got: Any) -> list[str]:
    return assert_equal(label, bool(got), True)


def assert_false(label: str, got: Any) -> list[str]:
    return assert_equal(label, bool(got), False)


def attempts_json_serializable(attempts: list[dict]) -> bool:
    try:
        json.dumps(attempts)
    except (TypeError, ValueError) as exc:
        print(f"  FAIL attempts not JSON serializable: {exc}", file=sys.stderr)
        return False
    return True


def attempt_produced_real_media(attempts: list[dict]) -> bool:
    for attempt in attempts:
        for ref in attempt.get("output_asset_refs", []):
            if ref.get("produced_real_media") is True:
                return True
            if ref.get("kind") not in (None, "synthetic_success_marker"):
                return True
            if any(
                ref.get(key)
                for key in ("local_path", "sha256", "b2_url", "bytes_ref")
            ):
                return True
    return False


def run_scenario(
    key: str,
    label: str,
    providers: list,
    expectations: Callable[[dict], list[str]],
) -> dict[str, Any]:
    """Run a single router scenario.

    Returns a dict carrying both the compact human-readable summary (for the
    ``summary.scenarios`` block) and the full attempt ledger records sourced
    directly from the real :class:`ProviderResult` objects. The full records are
    produced by ``ProviderAttempt.to_dict()`` exactly as the router emitted
    them; they are never manually invented or trimmed here.
    """
    router = ProviderRouter(providers=providers)
    result = router.route(make_job())
    result_dict = result.to_dict()

    # Full attempt ledger records come straight from the router result. These
    # are the authoritative records written to the attempts JSON.
    full_attempts: list[dict[str, Any]] = [attempt.to_dict() for attempt in result.attempts]

    errors: list[str] = []
    errors.extend(expectations(result_dict))

    if not attempts_json_serializable(full_attempts):
        errors.append("attempts must be JSON serializable")

    if attempt_produced_real_media(full_attempts):
        errors.append("no fake generated media asset may be produced")

    try:
        json.dumps(result_dict)
    except (TypeError, ValueError) as exc:
        errors.append(f"result must be JSON serializable: {exc}")

    passed = not errors

    # Compact display attempts are for human readability inside the summary
    # only. They are NOT what gets written to provider-router-core-attempts.json.
    compact = {
        "key": key,
        "label": label,
        "passed": passed,
        "ok": result_dict["ok"],
        "final_status": result_dict["final_status"],
        "final_normalized_status": result_dict["final_normalized_status"],
        "selected_provider": result_dict["selected_provider"],
        "selected_model": result_dict["selected_model"],
        "selected_attempt_index": result_dict["selected_attempt_index"],
        "fallback_used": result_dict["fallback_used"],
        "attempt_count": result_dict["attempt_count"],
        "stopped_reason": result_dict["stopped_reason"],
        "provider_chain": [type(p).provider_id for p in providers],
        "attempts": [
            {
                "attempt_index": a["attempt_index"],
                "provider": a["provider"],
                "model": a["model"],
                "status": a["status"],
                "normalized_status": a["normalized_status"],
                "retryable": a["retryable"],
                "fallback_allowed": a["fallback_allowed"],
                "latency_ms": a["latency_ms"],
                "skip_reason": a["skip_reason"],
                "sanitized_error_message": a["sanitized_error_message"],
            }
            for a in full_attempts
        ],
        "errors": errors,
    }

    status_line = "PASS" if passed else "FAIL"
    print(f"[{status_line}] {key} ({label}): ok={result_dict['ok']} "
          f"attempts={result_dict['attempt_count']} "
          f"selected={result_dict['selected_provider']} "
          f"fallback_used={result_dict['fallback_used']}")
    for err in errors:
        print(f"   - {err}")

    return {
        "compact": compact,
        "full_attempts": full_attempts,
    }


def expect_scenario_a(result: dict) -> list[str]:
    errors: list[str] = []
    errors += assert_true("ok", result["ok"])
    errors += assert_equal("attempt_count", result["attempt_count"], 1)
    errors += assert_equal("selected_provider", result["selected_provider"], SUCCESS_PROVIDER_ID)
    errors += assert_equal("selected_attempt_index", result["selected_attempt_index"], 0)
    errors += assert_false("fallback_used", result["fallback_used"])
    errors += assert_equal("final_normalized_status", result["final_normalized_status"], NS_OK)
    return errors


def expect_scenario_b(result: dict) -> list[str]:
    errors: list[str] = []
    errors += assert_true("ok", result["ok"])
    errors += assert_equal("attempt_count", result["attempt_count"], 2)
    errors += assert_equal("selected_provider", result["selected_provider"], SUCCESS_PROVIDER_ID)
    errors += assert_equal("selected_attempt_index", result["selected_attempt_index"], 1)
    errors += assert_true("fallback_used", result["fallback_used"])
    errors += assert_equal("final_normalized_status", result["final_normalized_status"], NS_OK)

    first = result["attempts"][0]
    if first["status"] != "failed":
        errors.append(f"attempt[0].status: expected 'failed', got {first['status']!r}")
    if first["provider"] != FAIL_PROVIDER_ID:
        errors.append(
            f"attempt[0].provider: expected {FAIL_PROVIDER_ID!r}, got {first['provider']!r}"
        )
    if first["normalized_status"] == NS_OK:
        errors.append("failed attempt must not be normalized as OK")
    return errors


def expect_scenario_c(result: dict) -> list[str]:
    errors: list[str] = []
    errors += assert_true("ok", result["ok"])
    errors += assert_equal("attempt_count", result["attempt_count"], 2)
    errors += assert_equal("selected_provider", result["selected_provider"], SUCCESS_PROVIDER_ID)
    errors += assert_equal("selected_attempt_index", result["selected_attempt_index"], 1)
    errors += assert_true("fallback_used", result["fallback_used"])

    first = result["attempts"][0]
    if first["status"] != "skipped":
        errors.append(f"attempt[0].status: expected 'skipped', got {first['status']!r}")
    if first["provider"] != DISABLED_PROVIDER_ID:
        errors.append(
            f"attempt[0].provider: expected {DISABLED_PROVIDER_ID!r}, got {first['provider']!r}"
        )
    if first["normalized_status"] != NS_SKIPPED_DISABLED:
        errors.append(
            "attempt[0].normalized_status: expected "
            f"{NS_SKIPPED_DISABLED!r}, got {first['normalized_status']!r}"
        )
    return errors


def expect_scenario_d(result: dict) -> list[str]:
    errors: list[str] = []
    errors += assert_false("ok", result["ok"])
    errors += assert_equal("attempt_count", result["attempt_count"], 2)
    errors += assert_equal("selected_provider", result["selected_provider"], None)
    errors += assert_equal("selected_model", result["selected_model"], None)
    errors += assert_equal("selected_attempt_index", result["selected_attempt_index"], None)
    errors += assert_equal("final_normalized_status", result["final_normalized_status"], NS_PROVIDER_DOWN)

    for index, attempt in enumerate(result["attempts"]):
        if attempt["status"] != "failed":
            errors.append(
                f"attempt[{index}].status: expected 'failed', got {attempt['status']!r}"
            )
        if attempt["normalized_status"] == NS_OK:
            errors.append(f"attempt[{index}] must not be normalized as OK")
        if attempt["output_asset_refs"]:
            errors.append(
                f"attempt[{index}] must have no output_asset_refs on failure"
            )
    if result["output_asset_refs"]:
        errors.append("all-fail result must carry no output_asset_refs")
    return errors


def validate_full_attempt_schema(
    attempts_by_scenario: dict[str, list[dict[str, Any]]],
) -> list[str]:
    """Validate that every attempt ledger record carries all required fields.

    Required fields are defined by specs/14-ps-006-provider-router-core.md
    section 7. This runs BEFORE any PASS is written; if it returns any errors
    the smoke run must fail.
    """
    errors: list[str] = []

    missing_keys = [k for k in SCENARIO_KEYS if k not in attempts_by_scenario]
    if missing_keys:
        errors.append(
            f"attempts_by_scenario missing keys: {missing_keys}"
        )

    for key in SCENARIO_KEYS:
        attempts = attempts_by_scenario.get(key)
        if attempts is None:
            continue
        if not isinstance(attempts, list):
            errors.append(f"{key}: attempts must be a list, got {type(attempts).__name__}")
            continue
        for index, attempt in enumerate(attempts):
            if not isinstance(attempt, dict):
                errors.append(
                    f"{key}[{index}]: attempt must be a dict, got {type(attempt).__name__}"
                )
                continue
            for field_name in REQUIRED_ATTEMPT_FIELDS:
                if field_name not in attempt:
                    errors.append(
                        f"{key}[{index}]: missing required field {field_name!r}"
                    )
    return errors


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    runs = [
        run_scenario(
            "scenario_a",
            "A_first_succeeds",
            [AlwaysSucceedProvider()],
            expect_scenario_a,
        ),
        run_scenario(
            "scenario_b",
            "B_first_fails_second_succeeds",
            [AlwaysFailProvider(), AlwaysSucceedProvider()],
            expect_scenario_b,
        ),
        run_scenario(
            "scenario_c",
            "C_disabled_then_success",
            [DisabledProvider(), AlwaysSucceedProvider()],
            expect_scenario_c,
        ),
        run_scenario(
            "scenario_d",
            "D_all_fail",
            [AlwaysFailProvider(), AlwaysFailProvider()],
            expect_scenario_d,
        ),
    ]

    # summary.scenarios keyed by canonical acceptance-gate keys.
    scenarios_summary: dict[str, dict[str, Any]] = {}
    # attempts JSON keyed by the same canonical keys, each value a list of full
    # attempt ledger records sourced from the real ProviderResult objects.
    attempts_by_scenario: dict[str, list[dict[str, Any]]] = {}
    for key, run in zip(SCENARIO_KEYS, runs):
        scenarios_summary[key] = run["compact"]
        attempts_by_scenario[key] = run["full_attempts"]

    # Behavioral PASS gates first; schema gate is additional and must also pass.
    behavior_passed = all(s["passed"] for s in scenarios_summary.values())
    schema_errors = validate_full_attempt_schema(attempts_by_scenario)

    all_passed = behavior_passed and not schema_errors

    summary = {
        "slice": "PS-006",
        "ok": all_passed,
        "proof": (
            "PS-006 ProviderRouter Core deterministic smoke. Router preserves "
            "every attempt, stops on first success, falls back on failure and "
            "disabled providers, and returns ok=false with evidence when all "
            "providers fail. No network, no keys, no fake media."
        ),
        "scenarios": scenarios_summary,
        "scenario_count": len(runs),
        "passed_count": sum(1 for s in scenarios_summary.values() if s["passed"]),
        "failed_count": sum(1 for s in scenarios_summary.values() if not s["passed"]),
        "schema_errors": schema_errors,
        "outputs": {
            "summary": str(SUMMARY_PATH),
            "attempts": str(ATTEMPTS_PATH),
        },
        "truth_boundary": (
            "This proves deterministic router-core behavior only. It does not "
            "prove any provider executed, any asset was generated, or any "
            "manifest exists. No B2 upload occurs in this slice."
        ),
        "written_at": now_iso(),
    }

    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    ATTEMPTS_PATH.write_text(
        json.dumps(attempts_by_scenario, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print(f"summary:  {SUMMARY_PATH}")
    print(f"attempts: {ATTEMPTS_PATH}")
    print(f"overall:  {'PASS' if all_passed else 'FAIL'} "
          f"({summary['passed_count']}/{summary['scenario_count']} scenarios)")
    for err in schema_errors:
        print(f"   - SCHEMA ERROR: {err}", file=sys.stderr)

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
