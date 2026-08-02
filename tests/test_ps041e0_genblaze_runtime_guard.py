"""PS-041E0 focused tests for the Genblaze runtime version guard.

These tests have two layers:

1. In-process unit tests that drive
   :mod:`proofstudio.api.genblaze_runtime` against a controlled
   ``importlib.metadata.version`` surface via monkeypatching. They never
   modify the canonical installed distributions and they never make a provider
   or live B2 call.

2. True cold-start subprocess tests that spawn a fresh Python interpreter,
   patch ``importlib.metadata.version`` BEFORE importing
   ``proofstudio.api.app``, and prove the controlled
   :class:`GenblazeRuntimeVersionError` fires before any Genblaze-dependent
   ProofStudio module is imported. These reproduce the real worker startup
   ordering guarantee.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from proofstudio.api import genblaze_runtime
from proofstudio.api.genblaze_runtime import (
    EXPECTED_VERSIONS,
    GENBLAZE_RELEASE_COMMIT,
    GENBLAZE_RELEASE_TAG,
    GenblazeRuntimeVersionError,
    assert_genblaze_runtime_versions,
    reset_cached_runtime_verification,
    verify_runtime_versions_cached,
)


TARGET = {
    "genblaze-core": "0.3.6",
    "genblaze-s3": "0.3.5",
    "genblaze-gmicloud": "0.3.5",
}


# ---------------------------------------------------------------------------
# In-process unit tests against the raw guard function.
# ---------------------------------------------------------------------------


def _patch_versions(monkeypatch, mapping):
    """Redirect the guard's ``version`` lookup to a fixed mapping.

    A value of ``None`` simulates a missing distribution.
    """

    def fake(name):
        if name not in mapping:
            raise genblaze_runtime.PackageNotFoundError(name)
        value = mapping[name]
        if value is None:
            raise genblaze_runtime.PackageNotFoundError(name)
        return value

    monkeypatch.setattr(genblaze_runtime, "version", fake)


@pytest.fixture(autouse=True)
def _reset_cache_between_tests():
    """Ensure the cached verifier never leaks state between in-process tests."""
    reset_cached_runtime_verification()
    yield
    reset_cached_runtime_verification()


def test_exact_target_versions_pass(monkeypatch):
    _patch_versions(monkeypatch, TARGET)
    installed = assert_genblaze_runtime_versions()
    assert installed == TARGET


def test_partial_upgrade_core_old_fails_closed(monkeypatch):
    bad = dict(TARGET)
    bad["genblaze-core"] = "0.3.4"
    _patch_versions(monkeypatch, bad)
    with pytest.raises(GenblazeRuntimeVersionError) as exc_info:
        assert_genblaze_runtime_versions()
    assert "genblaze-core" in str(exc_info.value)
    assert "0.3.4" in str(exc_info.value)
    assert "0.3.6" in str(exc_info.value)


def test_partial_upgrade_s3_old_fails_closed(monkeypatch):
    bad = dict(TARGET)
    bad["genblaze-s3"] = "0.3.4"
    _patch_versions(monkeypatch, bad)
    with pytest.raises(GenblazeRuntimeVersionError) as exc_info:
        assert_genblaze_runtime_versions()
    assert "genblaze-s3" in str(exc_info.value)
    assert "0.3.4" in str(exc_info.value)
    assert "0.3.5" in str(exc_info.value)


def test_partial_upgrade_gmicloud_old_fails_closed(monkeypatch):
    bad = dict(TARGET)
    bad["genblaze-gmicloud"] = "0.3.3"
    _patch_versions(monkeypatch, bad)
    with pytest.raises(GenblazeRuntimeVersionError) as exc_info:
        assert_genblaze_runtime_versions()
    assert "genblaze-gmicloud" in str(exc_info.value)
    assert "0.3.3" in str(exc_info.value)
    assert "0.3.5" in str(exc_info.value)


def test_missing_distribution_fails_closed(monkeypatch):
    bad = dict(TARGET)
    bad["genblaze-s3"] = None
    _patch_versions(monkeypatch, bad)
    with pytest.raises(GenblazeRuntimeVersionError) as exc_info:
        assert_genblaze_runtime_versions()
    message = str(exc_info.value)
    assert "genblaze-s3" in message
    assert "missing" in message


def test_unexpected_newer_version_fails_closed(monkeypatch):
    bad = dict(TARGET)
    bad["genblaze-core"] = "0.3.7"
    _patch_versions(monkeypatch, bad)
    with pytest.raises(GenblazeRuntimeVersionError) as exc_info:
        assert_genblaze_runtime_versions()
    message = str(exc_info.value)
    assert "genblaze-core" in message
    assert "0.3.7" in message
    assert "0.3.6" in message


def test_unexpected_prerelease_or_local_version_fails_closed(monkeypatch):
    for bad_value in ("0.3.6rc1", "0.3.6.dev0", "0.3.6+local"):
        bad = dict(TARGET)
        bad["genblaze-core"] = bad_value
        _patch_versions(monkeypatch, bad)
        with pytest.raises(GenblazeRuntimeVersionError) as exc_info:
            assert_genblaze_runtime_versions()
        assert bad_value in str(exc_info.value)


def test_error_contains_package_names_and_safe_versions_only(monkeypatch):
    bad = dict(TARGET)
    bad["genblaze-gmicloud"] = "0.3.9"
    _patch_versions(monkeypatch, bad)
    with pytest.raises(GenblazeRuntimeVersionError) as exc_info:
        assert_genblaze_runtime_versions()
    message = str(exc_info.value)
    assert "genblaze-gmicloud" in message
    assert "0.3.9" in message
    assert "0.3.5" in message
    assert exc_info.value.expected["genblaze-gmicloud"] == "0.3.5"
    assert exc_info.value.installed["genblaze-gmicloud"] == "0.3.9"


def test_error_contains_no_environment_credentials_or_db_urls(monkeypatch):
    bad = dict(TARGET)
    bad["genblaze-core"] = "0.3.4"
    _patch_versions(monkeypatch, bad)
    with pytest.raises(GenblazeRuntimeVersionError) as exc_info:
        assert_genblaze_runtime_versions()
    message = str(exc_info.value)
    forbidden_fragments = [
        "postgres",
        "postgresql",
        "DATABASE_URL",
        "aws_secret",
        "aws_access",
        "B2_KEY",
        "authorization",
        "bearer",
        "token",
        "/etc/",
        "/home/",
        ".env",
        "os.environ",
    ]
    lowered = message.lower()
    for fragment in forbidden_fragments:
        assert fragment.lower() not in lowered


def test_guard_makes_no_provider_or_b2_call(monkeypatch):
    import inspect

    source = inspect.getsource(genblaze_runtime)
    forbidden_imports = [
        "import boto3",
        "from boto3",
        "import requests",
        "from requests",
        "import httpx",
        "from httpx",
        "import genblaze_gmicloud",
        "from genblaze_gmicloud",
        "import genblaze_s3",
        "from genblaze_s3",
        "socket.socket",
    ]
    for fragment in forbidden_imports:
        assert fragment not in source

    import sys

    probes = {"provider_hit": False, "b2_hit": False}

    class _Probe:
        def __init__(self, *args, **kwargs):
            raise AssertionError("guard must not instantiate a provider/B2 client")

    class _ProbeModule:
        Client = _Probe

        def __getattr__(self, name):
            probes["b2_hit"] = True
            raise AssertionError(f"guard must not touch boto3 attribute {name!r}")

    monkeypatch.setitem(sys.modules, "boto3", _ProbeModule())
    _patch_versions(monkeypatch, TARGET)
    installed = assert_genblaze_runtime_versions()
    assert installed == TARGET
    assert probes["provider_hit"] is False
    assert probes["b2_hit"] is False


def test_expected_versions_match_pin_contract():
    assert EXPECTED_VERSIONS == TARGET
    assert GENBLAZE_RELEASE_TAG == "v0.7.0"
    assert GENBLAZE_RELEASE_COMMIT == "ec81e810f2643ed7ad2eb5e639d9b02470c887fd"


# ---------------------------------------------------------------------------
# Cached verifier behavior (idempotent; production startup path).
# ---------------------------------------------------------------------------


def test_cached_verifier_runs_the_underlying_check_once(monkeypatch):
    _patch_versions(monkeypatch, TARGET)
    calls = {"n": 0}
    original = genblaze_runtime.assert_genblaze_runtime_versions

    def counting(*args, **kwargs):
        calls["n"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(genblaze_runtime, "assert_genblaze_runtime_versions", counting)
    first = verify_runtime_versions_cached()
    second = verify_runtime_versions_cached()
    third = verify_runtime_versions_cached()
    assert first == TARGET
    assert second is first
    assert third is first
    assert calls["n"] == 1


def test_cached_verifier_does_not_cache_failures(monkeypatch):
    bad = dict(TARGET)
    bad["genblaze-core"] = "0.3.4"
    _patch_versions(monkeypatch, bad)
    with pytest.raises(GenblazeRuntimeVersionError):
        verify_runtime_versions_cached()
    # Cache stays empty: a subsequent good surface must be observed fresh.
    _patch_versions(monkeypatch, TARGET)
    installed = verify_runtime_versions_cached()
    assert installed == TARGET


def test_create_app_is_idempotent_and_does_not_re_invoke_the_guard(monkeypatch):
    """create_app() reuses the cached verification; it never re-invokes the
    underlying metadata check. This is the documented idempotent behavior that
    makes create_app() safe to call repeatedly."""
    import importlib

    app_module = importlib.import_module("proofstudio.api.app")
    # Populate the cache with the real installed distributions first (this is
    # the state the autouse reset cleared). After this point, the cached
    # verifier must never touch the raw guard again.
    verify_runtime_versions_cached()
    calls = {"n": 0}

    def blowing_up(*args, **kwargs):
        calls["n"] += 1
        raise GenblazeRuntimeVersionError(
            "must not be called",
            expected=TARGET,
            installed=TARGET,
        )

    monkeypatch.setattr(genblaze_runtime, "assert_genblaze_runtime_versions", blowing_up)
    application_one = app_module.create_app()
    application_two = app_module.create_app()
    assert application_one is not None
    assert application_two is not None
    assert calls["n"] == 0


# ---------------------------------------------------------------------------
# True cold-start subprocess tests.
#
# Each scenario runs in a brand-new Python interpreter that patches
# ``importlib.metadata.version`` BEFORE importing ``proofstudio.api.app``.
# The canonical distributions are never modified.
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"


def _run_cold_start(script: str) -> subprocess.CompletedProcess:
    """Run a fresh subprocess with ``src`` on PYTHONPATH and a minimal env.

    The env is rebuilt from a safe allowlist so no credentials, DB URLs,
    tokens, or private-index configuration leak into the child or into the
    captured diagnostic.
    """
    clean_env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": str(SRC_DIR),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "LC_ALL": "C.UTF-8",
        "LANG": "C.UTF-8",
    }
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(script)],
        capture_output=True,
        text=True,
        timeout=90,
        env=clean_env,
    )


_COLD_START_HEADER = """
import importlib.metadata as _md
from importlib.metadata import PackageNotFoundError
import json, sys

_real_version = _md.version
_target = {
    "genblaze-core": "0.3.6",
    "genblaze-s3": "0.3.5",
    "genblaze-gmicloud": "0.3.5",
}

def _make_version(surface):
    def _v(name):
        if name in surface:
            value = surface[name]
            if value is None:
                raise PackageNotFoundError(name)
            return value
        return _real_version(name)
    return _v

def _diagnose():
    return {
        "services_imported": "proofstudio.api.services" in sys.modules,
        "ext_adapter_imported": (
            "proofstudio.api.genblaze_external_adapter" in sys.modules
        ),
        "store_imported": "proofstudio.api.store" in sys.modules,
        "any_provider_imported": any(
            m.startswith("proofstudio.providers") for m in sys.modules
        ),
        "boto3_imported": "boto3" in sys.modules,
        "genblaze_core_imported": any(
            m == "genblaze_core" or m.startswith("genblaze_core.")
            for m in sys.modules
        ),
        "app_module_imported": "proofstudio.api.app" in sys.modules,
        "app_constructed": False,
    }
"""

_SUCCESS_FOOTER = """
try:
    import proofstudio.api  # ensures full package + app module initialization
    _appmod = sys.modules.get("proofstudio.api.app")
except Exception as _e:
    print("RESULT:" + json.dumps({
        "ok": False,
        "error_type": type(_e).__name__,
        "diagnose": _diagnose(),
        "message": str(_e),
    }))
    raise SystemExit(0)

try:
    _fastapi_app = getattr(_appmod, "app", None)
    _constructed = _fastapi_app is not None
    _routes = (
        sorted({getattr(r, "path", None) for r in _fastapi_app.routes})
        if _constructed
        else []
    )
except Exception:
    _constructed = False
    _routes = []
_diag = _diagnose()
_diag["app_constructed"] = _constructed
print("RESULT:" + json.dumps({
    "ok": True,
    "routes": _routes,
    "diagnose": _diag,
}))
"""

_FAILURE_FOOTER = """
try:
    import proofstudio.api  # triggers guard via package initializer
except Exception as _e:
    _diag = _diagnose()
    print("RESULT:" + json.dumps({
        "ok": False,
        "error_type": type(_e).__name__,
        "message": str(_e),
        "diagnose": _diag,
    }))
    raise SystemExit(0)
print("RESULT:" + json.dumps({
    "ok": True,
    "error": "expected failure but import succeeded",
    "diagnose": _diagnose(),
}))
"""

_FORBIDDEN_DIAGNOSTIC_FRAGMENTS = [
    "postgres",
    "postgresql",
    "DATABASE_URL",
    "aws_secret",
    "aws_access",
    "B2_KEY",
    "authorization",
    "bearer",
    "/etc/",
    "/home/",
    ".env",
    "os.environ",
    "secret_access_key",
    "account_id",
    "<traceback",  # rendered form would only appear if a real traceback leaked
]


def _assert_clean_failure(result: subprocess.CompletedProcess, scenario: str):
    """Common assertions for every cold-start failure scenario."""
    assert result.returncode == 0, (
        f"{scenario}: subprocess exited {result.returncode}; "
        f"stderr tail:\n{result.stderr[-800:]}"
    )
    # No Python traceback must leak to stderr.
    assert "Traceback (most recent call last)" not in result.stderr, (
        f"{scenario}: stack trace leaked to stderr:\n{result.stderr}"
    )
    payload = _extract_payload(result.stdout, scenario)
    assert payload["ok"] is False, (
        f"{scenario}: expected controlled failure, got {payload}"
    )
    assert payload["error_type"] == "GenblazeRuntimeVersionError", (
        f"{scenario}: expected GenblazeRuntimeVersionError, got "
        f"{payload['error_type']}"
    )
    diagnose = payload["diagnose"]
    assert diagnose["services_imported"] is False, (
        f"{scenario}: proofstudio.api.services was imported on failure"
    )
    assert diagnose["ext_adapter_imported"] is False, (
        f"{scenario}: proofstudio.api.genblaze_external_adapter was imported"
    )
    assert diagnose["store_imported"] is False, (
        f"{scenario}: proofstudio.api.store was imported on failure"
    )
    assert diagnose["any_provider_imported"] is False, (
        f"{scenario}: a provider module was imported on failure"
    )
    assert diagnose["boto3_imported"] is False, (
        f"{scenario}: boto3 was imported on failure"
    )
    assert diagnose["genblaze_core_imported"] is False, (
        f"{scenario}: genblaze_core was imported on failure"
    )
    assert diagnose["app_module_imported"] is False, (
        f"{scenario}: proofstudio.api.app module was imported on failure"
    )
    assert diagnose["app_constructed"] is False, (
        f"{scenario}: a FastAPI app was constructed on failure"
    )
    message = payload["message"]
    lowered = message.lower()
    for fragment in _FORBIDDEN_DIAGNOSTIC_FRAGMENTS:
        assert fragment.lower() not in lowered, (
            f"{scenario}: forbidden fragment {fragment!r} in diagnostic: "
            f"{message!r}"
        )
    # The combined stdout+stderr must also be free of credential/path echoes.
    combined = (result.stdout + "\n" + result.stderr).lower()
    for fragment in _FORBIDDEN_DIAGNOSTIC_FRAGMENTS:
        assert fragment.lower() not in combined, (
            f"{scenario}: forbidden fragment {fragment!r} in captured output"
        )
    return payload


def _extract_payload(stdout: str, scenario: str) -> dict:
    marker = "RESULT:"
    line = next((ln for ln in stdout.splitlines() if ln.startswith(marker)), None)
    assert line is not None, f"{scenario}: no RESULT line in stdout:\n{stdout}"
    return json.loads(line[len(marker):])


def test_cold_start_exact_versions_import_and_serve_routes():
    script = (
        _COLD_START_HEADER
        + "\n_md.version = _make_version(_target)\n"
        + _SUCCESS_FOOTER
    )
    result = _run_cold_start(script)
    assert result.returncode == 0, result.stderr
    assert "Traceback (most recent call last)" not in result.stderr
    payload = _extract_payload(result.stdout, "exact-versions")
    assert payload["ok"] is True, payload
    routes = payload["routes"]
    assert "/health" in routes
    assert "/version" in routes
    assert "/campaigns" in routes
    assert "/runs" in routes
    diagnose = payload["diagnose"]
    assert diagnose["app_constructed"] is True


def test_cold_start_missing_core_fails_closed_before_dependent_imports():
    surface = dict(TARGET)
    surface["genblaze-core"] = None
    script = (
        _COLD_START_HEADER
        + f"\n_md.version = _make_version({surface!r})\n"
        + _FAILURE_FOOTER
    )
    payload = _assert_clean_failure(_run_cold_start(script), "missing-core")
    assert "genblaze-core" in payload["message"]
    assert "missing" in payload["message"].lower()


def test_cold_start_missing_s3_fails_closed_before_dependent_imports():
    surface = dict(TARGET)
    surface["genblaze-s3"] = None
    script = (
        _COLD_START_HEADER
        + f"\n_md.version = _make_version({surface!r})\n"
        + _FAILURE_FOOTER
    )
    payload = _assert_clean_failure(_run_cold_start(script), "missing-s3")
    assert "genblaze-s3" in payload["message"]


def test_cold_start_missing_gmicloud_fails_closed_before_dependent_imports():
    surface = dict(TARGET)
    surface["genblaze-gmicloud"] = None
    script = (
        _COLD_START_HEADER
        + f"\n_md.version = _make_version({surface!r})\n"
        + _FAILURE_FOOTER
    )
    payload = _assert_clean_failure(_run_cold_start(script), "missing-gmicloud")
    assert "genblaze-gmicloud" in payload["message"]


def test_cold_start_old_core_fails_closed_before_dependent_imports():
    surface = dict(TARGET)
    surface["genblaze-core"] = "0.3.4"
    script = (
        _COLD_START_HEADER
        + f"\n_md.version = _make_version({surface!r})\n"
        + _FAILURE_FOOTER
    )
    payload = _assert_clean_failure(_run_cold_start(script), "old-core")
    assert "genblaze-core" in payload["message"]
    assert "0.3.4" in payload["message"]
    assert "0.3.6" in payload["message"]


def test_cold_start_old_s3_fails_closed_before_dependent_imports():
    surface = dict(TARGET)
    surface["genblaze-s3"] = "0.3.4"
    script = (
        _COLD_START_HEADER
        + f"\n_md.version = _make_version({surface!r})\n"
        + _FAILURE_FOOTER
    )
    payload = _assert_clean_failure(_run_cold_start(script), "old-s3")
    assert "genblaze-s3" in payload["message"]
    assert "0.3.4" in payload["message"]
    assert "0.3.5" in payload["message"]


def test_cold_start_old_gmicloud_fails_closed_before_dependent_imports():
    surface = dict(TARGET)
    surface["genblaze-gmicloud"] = "0.3.3"
    script = (
        _COLD_START_HEADER
        + f"\n_md.version = _make_version({surface!r})\n"
        + _FAILURE_FOOTER
    )
    payload = _assert_clean_failure(_run_cold_start(script), "old-gmicloud")
    assert "genblaze-gmicloud" in payload["message"]
    assert "0.3.3" in payload["message"]
    assert "0.3.5" in payload["message"]


@pytest.mark.parametrize(
    "bad_versions",
    [
        {"genblaze-core": "0.3.7"},
        {"genblaze-s3": "0.3.6"},
        {"genblaze-gmicloud": "0.3.6"},
        {"genblaze-core": "0.3.6rc1"},
        {"genblaze-core": "0.3.6.dev0"},
        {"genblaze-core": "0.3.6+local"},
        {"genblaze-core": "1!0.3.6"},
    ],
)
def test_cold_start_unexpected_newer_or_prerelease_fails_closed(bad_versions):
    surface = dict(TARGET)
    surface.update(bad_versions)
    script = (
        _COLD_START_HEADER
        + f"\n_md.version = _make_version({surface!r})\n"
        + _FAILURE_FOOTER
    )
    _assert_clean_failure(_run_cold_start(script), f"unexpected:{bad_versions}")
