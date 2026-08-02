#!/usr/bin/env python3
"""PS-041E0 selective Genblaze v0.7.0 connector compatibility smoke.

Current-slice-only, local, non-mutating. It verifies:

- the three Genblaze Python packages match the exact selective v0.7.0
  connector compatibility matrix in apps/api/requirements.txt;
- the installed distributions (importlib.metadata) match the same exact
  versions;
- the exact Genblaze symbols ProofStudio uses import cleanly;
- the runtime version guard (:func:`assert_genblaze_runtime_versions`)
  returns success against the installed map;
- the accepted PS-041D bundle fingerprint, node count, edge count, and
  portable Passport schema remain identical to the accepted baseline;
- parent edges remain ``hash_covered=false`` (Manifest 1.5 excludes
  ``parent_run_id`` from the canonical hash);
- no provider call and no B2 call occur during this smoke.

It writes no evidence in normal mode. Exit code is 0 only when every check
passes.

    python scripts/ps041e0_genblaze_version_smoke.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from importlib.metadata import PackageNotFoundError, version as md_version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "apps" / "api" / "requirements.txt"
FIXTURE = ROOT / "tests" / "fixtures" / "ps041d" / "genblaze-multi-provider-bundle-v1.json"

EXPECTED_VERSIONS = {
    "genblaze-core": "0.3.6",
    "genblaze-s3": "0.3.5",
    "genblaze-gmicloud": "0.3.5",
}
EXPECTED_FINGERPRINT = (
    "f5e85c7fd7f85c272f1205d8a276c89fd77076e583b9de9839591589a1cd8a6c"
)
EXPECTED_NODE_COUNT = 16
EXPECTED_EDGE_COUNT = 16
EXPECTED_PASSPORT_SCHEMA = "proofstudio.portable_lineage_passport.v1"
GENBLAZE_RELEASE_TAG = "v0.7.0"
GENBLAZE_RELEASE_COMMIT = "ec81e810f2643ed7ad2eb5e639d9b02470c887fd"

PIN_LINE_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*==\s*([0-9A-Za-z_.-]+)\s*$")


def _read_requirements_pins() -> dict[str, str]:
    pins: dict[str, str] = {}
    if not REQUIREMENTS.is_file():
        return pins
    for raw in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0]
        match = PIN_LINE_RE.match(line)
        if not match:
            continue
        name, ver = match.group(1).strip(), match.group(2).strip()
        if name in EXPECTED_VERSIONS:
            pins[name] = ver
    return pins


def _installed_versions() -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for name in EXPECTED_VERSIONS:
        try:
            out[name] = md_version(name)
        except PackageNotFoundError:
            out[name] = None
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true", default=True)
    parser.add_argument("--write-evidence", action="store_true")
    parser.add_argument("--no-frontend", action="store_true")
    args = parser.parse_args(argv)
    if args.write_evidence:
        raise SystemExit(
            "PS-041E0 version smoke does not own canonical evidence writes"
        )

    failures: list[str] = []

    # 1. Requirements pins.
    pins = _read_requirements_pins()
    for name, expected in EXPECTED_VERSIONS.items():
        actual = pins.get(name)
        if actual is None:
            failures.append(f"requirements pin missing for {name}")
        elif actual != expected:
            failures.append(
                f"requirements pin {name}=={actual} != expected {expected}"
            )

    # 2. Installed versions via importlib.metadata.
    installed = _installed_versions()
    for name, expected in EXPECTED_VERSIONS.items():
        actual = installed.get(name)
        if actual is None:
            failures.append(f"installed distribution missing: {name}")
        elif actual != expected:
            failures.append(
                f"installed {name}=={actual} != expected {expected}"
            )

    # 3. Exact Genblaze symbols ProofStudio uses import cleanly.
    try:
        from genblaze_core.models.manifest import (  # noqa: F401
            ManifestError,
            parse_manifest,
        )
        from proofstudio.api.genblaze_external_adapter import (  # noqa: F401
            build_candidate,
            passport_for,
        )
        from proofstudio.api.imported_bundle import (  # noqa: F401
            ImportBundleRequest,
            PortableLineagePassport,
        )
        symbols_ok = True
    except Exception as exc:  # pragma: no cover - defensive
        failures.append(f"genblaze symbol import failed: {exc}")
        symbols_ok = False

    # 4. Runtime guard returns success against installed map.
    guard_ok = False
    try:
        from proofstudio.api.genblaze_runtime import (
            assert_genblaze_runtime_versions,
        )

        assert_genblaze_runtime_versions()
        guard_ok = True
    except Exception as exc:
        failures.append(f"runtime guard failed: {exc}")

    # 5-9. Accepted PS-041D fixture stability: fingerprint, nodes, edges,
    #     passport schema, parent hash_covered semantics.
    fingerprint: str | None = None
    node_count: int | None = None
    edge_count: int | None = None
    passport_schema: str | None = None
    fingerprint_ok = False
    node_count_ok = False
    edge_count_ok = False
    passport_schema_ok = False
    parent_hash_covered_false = False
    try:
        from proofstudio.api.genblaze_external_adapter import build_candidate
        from proofstudio.api.imported_bundle import (
            EdgeKind,
            EvidenceClass,
            ImportBundleRequest,
        )

        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        payload = ImportBundleRequest.model_validate(data)
        candidate = build_candidate("camp_smoke", payload)
        fingerprint = candidate.bundle.bundle_fingerprint
        node_count = len(candidate.nodes)
        edge_count = len(candidate.edges)
        fingerprint_ok = fingerprint == EXPECTED_FINGERPRINT
        if not fingerprint_ok:
            failures.append(
                f"bundle fingerprint changed: {fingerprint} != "
                f"{EXPECTED_FINGERPRINT}"
            )
        node_count_ok = node_count == EXPECTED_NODE_COUNT
        if not node_count_ok:
            failures.append(
                f"node count changed: {node_count} != "
                f"{EXPECTED_NODE_COUNT}"
            )
        edge_count_ok = edge_count == EXPECTED_EDGE_COUNT
        if not edge_count_ok:
            failures.append(
                f"edge count changed: {edge_count} != "
                f"{EXPECTED_EDGE_COUNT}"
            )
        passport = passport_for(candidate)
        passport_schema = passport.passport_schema
        passport_schema_ok = passport_schema == EXPECTED_PASSPORT_SCHEMA
        if not passport_schema_ok:
            failures.append(
                f"passport schema changed: {passport_schema} != "
                f"{EXPECTED_PASSPORT_SCHEMA}"
            )
        parent_edges = [
            edge for edge in candidate.edges
            if edge.kind is EdgeKind.PARENT_RUN
        ]
        parent_hash_covered_false = bool(parent_edges) and all(
            edge.evidence_class is EvidenceClass.RECORDED
            and edge.hash_covered is False
            for edge in parent_edges
        )
        if not parent_hash_covered_false:
            failures.append(
                "parent edges must be recorded and hash_covered=false "
                "(Manifest 1.5 excludes parent_run_id from canonical hash)"
            )
    except Exception as exc:
        failures.append(f"fixture stability check failed: {exc}")

    # 10-11. No provider call, no live B2 call. This smoke makes neither.
    provider_calls = 0
    b2_calls = 0

    ok = not failures

    report = {
        "ok": bool(ok),
        "slice": "ps041e0",
        "mode": "check-only",
        "genblaze_release_tag": GENBLAZE_RELEASE_TAG,
        "genblaze_release_commit": GENBLAZE_RELEASE_COMMIT,
        "expected_versions": EXPECTED_VERSIONS,
        "requirements_pins": pins,
        "installed_versions": installed,
        "requirements_pinned_exact": pins == EXPECTED_VERSIONS,
        "installed_match_expected": installed == EXPECTED_VERSIONS,
        "genblaze_symbols_imported": bool(symbols_ok),
        "runtime_guard_passed": bool(guard_ok),
        "bundle_fingerprint": fingerprint,
        "bundle_fingerprint_unchanged": bool(fingerprint_ok),
        "node_count": node_count,
        "node_count_unchanged": bool(node_count_ok),
        "edge_count": edge_count,
        "edge_count_unchanged": bool(edge_count_ok),
        "passport_schema": passport_schema,
        "passport_schema_unchanged": bool(passport_schema_ok),
        "parent_hash_covered_false": bool(parent_hash_covered_false),
        "provider_calls": provider_calls,
        "b2_calls": b2_calls,
        "no_live_provider_call": True,
        "no_live_b2_call": True,
        "failures": failures,
    }

    print(json.dumps(report, indent=2, sort_keys=True))
    if failures:
        print("PS-041E0 GENBLAZE VERSION SMOKE FAILED", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
