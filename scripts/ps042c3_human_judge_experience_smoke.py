#!/usr/bin/env python3
"""PS-042C3 human-first judge experience source smoke."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HOME = ROOT / "apps/web/src/JudgeCockpitHome.tsx"
QUICK = ROOT / "apps/web/src/JudgeQuickStart.tsx"
OVERLAY = ROOT / "apps/web/src/PublicDeploymentVerificationOverlay.tsx"
STYLES = ROOT / "apps/web/src/styles.css"

home = HOME.read_text(encoding="utf-8")
quick = QUICK.read_text(encoding="utf-8")
overlay = OVERLAY.read_text(encoding="utf-8")
styles = STYLES.read_text(encoding="utf-8")

assert "Proof you can inspect, not just trust." in quick
assert "Open the verified demo" in quick
assert "See the proof map" in quick
assert "Live demo ready" in quick
assert "No login required" in quick
assert quick.count("judge-quick-start-step") >= 1

assert "Demo verified and ready" in overlay
assert "View technical verification" in overlay
assert "current public API deployment verified" in overlay
assert "historical PS-025 state preserved" in overlay

assert home.count("<JudgeQuickStart ") == 1
assert home.count("<PublicDeploymentVerificationOverlay />") == 1
assert home.count("Explore full technical evidence") == 1
assert 'className="judge-technical-details"' in home

for historical_phrase in (
    "Golden Proof Path",
    "Golden demo run",
    "View Provenance Passport",
    "ProofStudio proves what this pipeline did.",
):
    assert historical_phrase in home, historical_phrase

assert "PS-042C3 — Human-first judge experience" in styles
assert "@media (max-width: 760px)" in styles

print("PS042C3_HUMAN_HIERARCHY=PASS")
print("PS042C3_TECHNICAL_DISCLOSURE=PASS")
print("PS042C3_HISTORICAL_CONTENT_PRESERVED=PASS")
print("PS042C3_MOBILE_LAYOUT_CONTRACT=PASS")
