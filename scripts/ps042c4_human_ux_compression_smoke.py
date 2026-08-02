#!/usr/bin/env python3
"""PS-042C4 human UX compression and mobile repair source smoke."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps/web/src"

HOME = WEB / "PS039CinematicSite.tsx"
JUDGE = WEB / "JudgeCockpitHome.tsx"
QUICK = WEB / "JudgeQuickStart.tsx"
PASSPORT = WEB / "PublicPassportPage.tsx"
PROOF_ROOM = WEB / "CampaignProofRoom.tsx"
OVERLAY = WEB / "PublicDeploymentVerificationOverlay.tsx"
PUBLIC_VERIFICATION = WEB / "publicDeploymentVerification.ts"
STYLES = WEB / "styles.css"
LIVE_API_URL = "https://proofstudio-api.onrender.com"
REQUIRED_COMMIT = "53b456d85593c87ad83da33782d7e157ebbd0f24"
REQUIRED_BRANCH = "ps-042c0/free-render-staging-v1"

EXPECTED_SCOPE = {
    "apps/web/src/App.tsx",
    "apps/web/src/CampaignProofRoom.tsx",
    "apps/web/src/JudgeCockpitHome.tsx",
    "apps/web/src/JudgeQuickStart.tsx",
    "apps/web/src/PS039CinematicSite.tsx",
    "apps/web/src/PublicDeploymentVerificationOverlay.tsx",
    "apps/web/src/PublicPassportPage.tsx",
    "apps/web/src/styles.css",
    "scripts/ps042c4_human_ux_compression_smoke.py",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )


home = read(HOME)
judge = read(JUDGE)
quick = read(QUICK)
passport = read(PASSPORT)
proof_room = read(PROOF_ROOM)
overlay = read(OVERLAY)
public_verification = read(PUBLIC_VERIFICATION)
styles = read(STYLES)

# Slice markers and homepage first-fold contract.
assert "PS-042C4" in home
assert "PS-042C4" in passport
assert "PS-042C4" in proof_room
assert "PS-042C4" in judge
assert "PS-042C4 — Human UX compression and mobile repair" in styles
assert "Inspect how an AI media run was created, stored, and verified." in home
assert "View the verified demo" in home
assert 'href="/passport/run_89d967f9000045efa22ed4cc78cfa67f"' in home
assert "How it works" in home
assert 'href="/judge-cockpit"' in home
assert 'preload="none"' in home

# The readable desktop message is authored before the visual object, and the
# public header exposes exactly the three approved destinations.
homepage_component = home[home.index("export function PS039CinematicSite") :]
assert homepage_component.index("<SceneCopy") < homepage_component.index(
    "<HeroAssetStage",
)
site_header = home[
    home.index("function SiteHeader") : home.index("function MobileLayerUnfolding")
]
assert re.findall(r'href="([^"#]+)"', site_header) == [
    "/judge-cockpit",
    "/passport/run_89d967f9000045efa22ed4cc78cfa67f",
    "/campaign-proof-room",
]
for label in ("Judge View", "Verified Demo", "Proof Room"):
    assert label in site_header, label
for forbidden in ("Dashboard", ">Demo<", "Website"):
    assert forbidden not in site_header, forbidden

# The landing page has one short four-stage explanation and one final Campaign
# Proof Room CTA; the preview itself does not repeat the invitation.
home_flow = home[
    home.index("function HomeProofFlow") : home.index("function CampaignRoomPreview")
]
for stage in ("Generate", "Archive", "Rehydrate", "Verify"):
    assert stage in home_flow, stage
assert home_flow.count("[\"") == 4
campaign_preview = home[
    home.index("function CampaignRoomPreview") : home.index("function TruthBoundarySection")
]
assert 'href="/campaign-proof-room"' not in campaign_preview
final_cta = home[home.index("function FinalCta") : home.index("function DemoControls")]
assert home.count('className="ps039-final-cta"') == 1
assert final_cta.count('"/campaign-proof-room"') == 1
assert final_cta.count("View the Campaign Proof Room") == 1

# Judge CTA must precede the three-step block in source order.
assert quick.index("judge-quick-start-actions") < quick.index(
    "judge-quick-start-steps",
)
assert "View the verified demo" in quick
assert "See the proof map" in quick
assert "Live demo ready" in quick
assert judge.count("judge-evidence-directory") >= 1
for destination in (
    "Provenance Passport",
    "Campaign Proof Room",
    "B2 Evidence",
    "Manifest Verification",
    "Operations Cockpit",
    "Judge Evidence Pack",
):
    assert destination in judge

# Passport starts with the human summary and follows it with concrete proof.
passport_summary_start = passport.index("passport-human-summary")
passport_details_start = passport.index("<details", passport_summary_start)
passport_first_fold_source = passport[passport_summary_start:passport_details_start]
for marker in (
    "Verified demo record",
    "See what happened to this AI media run.",
    "Follow the recorded generation, storage, and verification trail.",
    "Run recorded",
    "Archive verified",
    "Private records protected",
    "Explore the evidence",
    "Back to Judge View",
    "Recorded",
    "Archived in B2",
    "Rehydrated",
    "Verified",
    "Archive hash matched",
    "Provider calls during rehydrate:",
    "Public Passport:",
    "Private route:",
):
    assert marker in passport_first_fold_source, marker
inspection_actions = (
    "Inspect manifest",
    "Inspect rehydrate proof",
    "Inspect Passport details",
    "Inspect authorization evidence",
)
assert passport_first_fold_source.count('className="proof-fact-action"') == 4
for action in inspection_actions:
    assert action in passport_first_fold_source, action
for forbidden in (
    "Proof Score",
    "Mostly verified",
    "70 / 100",
    "run_id",
    "campaign_id",
    "API:",
):
    assert forbidden not in passport_first_fold_source, forbidden

passport_directory_start = passport.index('id="passport-evidence-directory"')
passport_technical_start = passport.index('id="full-technical-passport-record"')
passport_directory = passport[passport_directory_start:passport_technical_start]
assert passport_directory.count('className="evidence-directory-card"') <= 6
assert passport_directory.count('className="evidence-directory-card"') == 6
for destination in (
    "Manifest verification",
    "B2 archive evidence",
    "Rehydrate comparison",
    "Provider decisions",
    "Lineage",
    "Full technical Passport",
):
    assert destination in passport_directory, destination
for sentence in re.findall(r"<p>(.*?)</p>", passport_directory, flags=re.DOTALL):
    assert len(re.findall(r"[\w’'-]+", sentence)) <= 18, sentence

assert "<summary>Explore the evidence directory</summary>" in passport
assert "<summary>Full technical Passport record</summary>" in passport
assert "<summary>Evidence completeness details</summary>" in passport
assert 'id="full-technical-passport-record"\n            open' not in passport
passport_active_page = passport[passport.index("export function PublicPassportPage") :]
for old_inline_path in (
    "<B2EvidenceExplorer",
    "<MultimodalProofLayer",
    "<TranscriptTimestampEvidenceLayer",
    "<VoiceAudioEvidenceChoiceLayer",
    "<CampaignIntelligenceJudgeNarrativeLayer",
    "<CloudflareLowCostBackboneLayer",
    "<ProductionReadinessDemoModeLayer",
    "<TrustBoundaryLayer",
):
    assert old_inline_path not in passport_active_page, old_inline_path

# Proof Room live branch starts with the guided summary and compact directory.
compact_campaign_start = proof_room.index("function CompactCampaignProofRoom")
compact_campaign_end = proof_room.index("export function CampaignProofRoom")
compact_campaign = proof_room[compact_campaign_start:compact_campaign_end]
proof_summary_start = compact_campaign.index("campaign-human-summary")
proof_details_start = compact_campaign.index("<details", proof_summary_start)
proof_first_fold_source = compact_campaign[proof_summary_start:proof_details_start]
for marker in (
    "Campaign proof",
    "One campaign. One inspectable record.",
    "See what was recorded, what can be verified, and what is not claimed.",
    "What happened",
    "What is verified",
    "What is not claimed",
    "View the verified demo",
    "View detailed evidence",
):
    assert marker in proof_first_fold_source, marker
for forbidden in ("run_id", "campaign_id", "archive URI", "SHA-256"):
    assert forbidden not in proof_first_fold_source, forbidden

campaign_directory_start = compact_campaign.index('id="campaign-evidence-directory"')
campaign_technical_start = compact_campaign.index(
    'id="full-technical-campaign-record"',
)
campaign_directory = compact_campaign[
    campaign_directory_start:campaign_technical_start
]
assert campaign_directory.count('className="evidence-directory-card"') <= 6
assert campaign_directory.count('className="evidence-directory-card"') == 6
for destination in (
    "Provenance Passport",
    "Manifest verification",
    "B2 archive evidence",
    "Rehydrate comparison",
    "Operations cockpit",
    "Judge evidence pack",
):
    assert destination in campaign_directory, destination
for sentence in re.findall(r"<p>(.*?)</p>", campaign_directory, flags=re.DOTALL):
    assert len(re.findall(r"[\w’'-]+", sentence)) <= 18, sentence

assert "<summary>View detailed campaign evidence</summary>" in compact_campaign
assert "<summary>Full technical campaign record</summary>" in compact_campaign
assert 'id="full-technical-campaign-record"\n        open' not in compact_campaign
assert "campaign-detailed-evidence-content" not in compact_campaign
for old_inline_path in (
    "<MultimodalProofLayer",
    "<TranscriptTimestampEvidenceLayer",
    "<VoiceAudioEvidenceChoiceLayer",
    "<CampaignIntelligenceJudgeNarrativeLayer",
    "<CloudflareLowCostBackboneLayer",
    "<ProductionReadinessDemoModeLayer",
    "<TrustBoundaryLayer",
):
    assert old_inline_path not in compact_campaign, old_inline_path
assert (
    proof_room.index("return <CompactCampaignProofRoom />;")
    < proof_room.index("campaign-detailed-evidence-content")
)

# Deployment wording and the non-negotiable truth boundary.
assert "<dt>API revision</dt>" in overlay
assert "<dt>deployed commit</dt>" not in overlay
assert LIVE_API_URL in public_verification
assert "getApiBaseUrl()" in passport
assert "VITE_PROOFSTUDIO_API_BASE_URL" not in passport
assert "http://127.0.0.1:8000" not in passport_active_page
assert "http://127.0.0.1:8000" not in compact_campaign
truth_boundary = (
    "ProofStudio proves what the pipeline recorded. Proof does not equal truth."
)
assert truth_boundary in passport
assert truth_boundary in proof_room
assert "ProofStudio proves what the pipeline recorded." in quick
assert "Proof does not equal" in quick

# Primary demo wording stays consistent across the public entry points.
assert "View the verified demo" in home
assert "View the verified demo" in quick
assert "View the verified demo" in compact_campaign
assert "Open the verified demo" not in home
assert "Open the verified demo" not in quick
assert "Open the verified demo" not in compact_campaign

# Protected sources and evidence remain untouched.
changed_status = git("status", "--porcelain=v1", "--untracked-files=all").splitlines()
changed_paths = {
    line[3:].split(" -> ")[-1]
    for line in changed_status
    if len(line) >= 4
}
assert changed_paths == EXPECTED_SCOPE, (
    f"unexpected patch scope: {sorted(changed_paths)}; "
    f"expected: {sorted(EXPECTED_SCOPE)}"
)

protected_prefixes = (
    "docs/evidence/",
    "specs/",
    "apps/api/",
    "src/proofstudio/api/",
)
protected_exact = {
    "docs/evidence/demo/golden-demo-run.json",
    "docs/evidence/golden-fixture-digests.json",
    "package.json",
    "package-lock.json",
    "apps/web/package.json",
    "apps/web/package-lock.json",
}
for changed in changed_paths:
    assert changed not in protected_exact, changed
    assert not changed.startswith(protected_prefixes), changed
    assert not changed.endswith(("package.json", "package-lock.json")), changed
    assert not changed.endswith((".lock", ".lockfile")), changed
assert not git("status", "--porcelain=v1", "--", "docs/evidence").strip()
assert not git("diff", "--name-only", "--", "docs/evidence").strip()
assert not git("diff", "--name-only", "--", "specs", "apps/api", "src/proofstudio/api").strip()
assert not git(
    "diff",
    "--name-only",
    "--",
    "package.json",
    "package-lock.json",
    "apps/web/package.json",
    "apps/web/package-lock.json",
).strip()
assert git("rev-parse", "HEAD").strip() == REQUIRED_COMMIT
assert git("rev-parse", f"origin/{REQUIRED_BRANCH}").strip() == REQUIRED_COMMIT

print("PS042C4_SOURCE_MARKERS=PASS")
print("PS042C4_HOMEPAGE_FIRST_FOLD=PASS")
print("PS042C4_JUDGE_CTA_ORDER=PASS")
print("PS042C4_PASSPORT_DISCLOSURE=PASS")
print("PS042C4_PROOF_ROOM_DISCLOSURE=PASS")
print("PS042C4_CONCRETE_PROOF=PASS")
print("PS042C4_EVIDENCE_DIRECTORY=PASS")
print("PS042C4_LIVE_API_AUDIT_CONFIG=PASS")
print("PS042C4_API_REVISION_LABEL=PASS")
print("PS042C4_TRUTH_BOUNDARY=PASS")
print("PS042C4_PROTECTED_HISTORY=PASS")
print("PS042C4_APPROVED_PUBLIC_NAV=PASS")
print("PS042C4_INSPECTION_ACTIONS=PASS")
print("PS042C4_CTA_CONSISTENCY=PASS")
print("PS042C4_REQUIRED_GIT_STATE=PASS")
print("PS042C4_PATCH_SCOPE=" + json.dumps(sorted(changed_paths)))
