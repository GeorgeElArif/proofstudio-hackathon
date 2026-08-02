#!/usr/bin/env python3
"""PS-042C2 current public API deployment verification overlay smoke."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RECEIPT = (
    ROOT
    / "docs"
    / "evidence"
    / "ps-042c2"
    / "public-api-deployment-verification.json"
)

DATA_SOURCE = ROOT / "apps" / "web" / "src" / "publicDeploymentVerification.ts"
OVERLAY = (
    ROOT
    / "apps"
    / "web"
    / "src"
    / "PublicDeploymentVerificationOverlay.tsx"
)
HOME = ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx"
PASSPORT = ROOT / "apps" / "web" / "src" / "PublicPassportPage.tsx"

EXPECTED_COMMIT = "37cef3def9c14b64b917ef054058c7cb6dfb1e73"
EXPECTED_RUN = "run_89d967f9000045efa22ed4cc78cfa67f"
EXPECTED_CAMPAIGN = "camp_bea5161faa6244079d2ee01ce445c259"
EXPECTED_ARCHIVE = (
    "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141"
)

HISTORICAL_BLOBS = {
    "docs/evidence/ps-025/public-durable-passport-unlock-smoke.json":
        "912963b844a6c54ca0f881b960d6b6bc42ea2afc",
    "docs/evidence/demo/golden-demo-run.json":
        "e560ff8a18ec9cf1c6d82847ef0714ffa2602d6b",
    "docs/evidence/golden-fixture-digests.json":
        "97a751f495cb3052c70cffa9b9c4f10849b435dd",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


receipt = json.loads(read_text(RECEIPT))

assert receipt["ok"] is True
assert receipt["slice"] == "ps042c2"
assert receipt["api_commit"] == EXPECTED_COMMIT
assert receipt["health"]["status"] == 200
assert receipt["public_passport"]["status"] == 200
assert receipt["public_passport"]["run_id"] == EXPECTED_RUN
assert receipt["public_passport"]["campaign_id"] == EXPECTED_CAMPAIGN
assert receipt["public_passport"]["archive_sha256"] == EXPECTED_ARCHIVE
assert receipt["public_passport"]["provider_calls_during_rehydrate"] == 0
assert receipt["private_run"] == {
    "status": 401,
    "code": "internal_auth_required",
}
assert receipt["credentials_used"] is False
assert receipt["current_public_api_deployment_verified"] is True

historical = receipt["historical_ps025_capture_state"]
assert historical["public_deployment_pending"] is True
assert historical["preserved"] is True

data_source = read_text(DATA_SOURCE)
overlay_source = read_text(OVERLAY)
home_source = read_text(HOME)
passport_source = read_text(PASSPORT)

for literal in (
    EXPECTED_COMMIT,
    EXPECTED_RUN,
    EXPECTED_CAMPAIGN,
    EXPECTED_ARCHIVE,
    "healthStatus: 200",
    "passportStatus: 200",
    "privateRunStatus: 401",
    "credentialsUsed: false",
):
    assert literal in data_source, literal

assert "current public API deployment verified" in overlay_source
assert "historical PS-025 state preserved" in overlay_source
assert "PublicDeploymentVerificationOverlay" in home_source
assert "PublicDeploymentVerificationOverlay" in passport_source

for stale_phrase in (
    "the public deployment remains planned until",
    "public deploy planned",
):
    assert stale_phrase not in home_source.lower(), stale_phrase

for relative, expected_blob in HISTORICAL_BLOBS.items():
    actual_blob = subprocess.check_output(
        ["git", "hash-object", relative],
        cwd=ROOT,
        text=True,
    ).strip()
    assert actual_blob == expected_blob, {
        "file": relative,
        "expected": expected_blob,
        "actual": actual_blob,
    }

print(
    json.dumps(
        {
            "ok": True,
            "slice": "ps042c2",
            "api_commit": EXPECTED_COMMIT,
            "health_status": 200,
            "passport_status": 200,
            "private_run_status": 401,
            "provider_calls_during_rehydrate": 0,
            "credentials_used": False,
            "historical_ps025_evidence_preserved": True,
            "judge_cockpit_overlay": True,
            "public_passport_overlay": True,
        },
        sort_keys=True,
    )
)

print("PS042C2_RECEIPT_CONTRACT=PASS")
print("PS042C2_HISTORICAL_EVIDENCE_IMMUTABLE=PASS")
print("PS042C2_PUBLIC_DEPLOYMENT_OVERLAY_SMOKE=PASS")
