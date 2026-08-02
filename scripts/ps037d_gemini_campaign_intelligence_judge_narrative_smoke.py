#!/usr/bin/env python3
"""PS-037d Gemini Campaign Intelligence / Judge Narrative -- smoke / validation.

This smoke validates ONLY the PS-037d slice. It is local / static by default:
it does not start a browser, does not run the frontend typecheck / build, does
not call Gemini, does not call any model, does not call any provider, does not
read or write any B2 object, does not perform a broad B2 scan, does not call
the central regression gate, and does not recursively execute another feature
smoke. Default behavior is non-mutating local validation (``--check-only``); no
evidence file is written unless ``--write-evidence`` is explicit.

Standard flags (PS-034B / PS-035D feature-smoke contract):

    --check-only      default; non-mutating local validation; writes nothing
    --write-evidence  writes only docs/evidence/ps-037d/ evidence
    --no-frontend     skip the frontend typecheck/build (always skipped; a
                      feature smoke never runs the frontend)

Truth boundary: this smoke validates that the PS-037d Gemini Campaign
Intelligence / Judge Narrative Layer is honest and consistent. ProofStudio
proves what the pipeline recorded. The layer is not model output truth, not
semantic truth, not legal authenticity, not human authorship, not C2PA
authenticity, not Object Lock, not tamper-proof, not browser-side B2 byte
verification, not live B2 availability, not live Gemini availability, not
production security, not production compliance, not legal review, not
chain-of-custody guarantee, not campaign performance prediction, not marketing
effectiveness proof, not business outcome guarantee, not conversion lift, not
revenue impact, not audience targeting accuracy, not ad compliance approval,
not identity verification, not biometric identification, not deepfake detection,
not content moderation, not OCR correctness, not transcript correctness, not
timestamp correctness, not voice authenticity, not speaker identity, and not
emotion truth.

Posture contract strings preserved by this smoke: no Gemini API calls, no
provider calls, no live B2 reads, no B2 writes, no broad B2 scans, no recursive
smokes, hidden Git flags h, line[0].

Exit code is 0 only when every check passes.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke_lib as sl  # noqa: E402

REPO_ROOT = sl.repo_root()
APPS_WEB_SRC = REPO_ROOT / "apps" / "web" / "src"
DATA_MODULE = APPS_WEB_SRC / "geminiCampaignIntelligence.ts"
COMPONENT = APPS_WEB_SRC / "CampaignIntelligenceJudgeNarrativeLayer.tsx"
SMOKE_SELF = (
    REPO_ROOT
    / "scripts"
    / "ps037d_gemini_campaign_intelligence_judge_narrative_smoke.py"
)
PROOF_DOC = (
    REPO_ROOT
    / "docs"
    / "ps-037d-gemini-campaign-intelligence-judge-narrative-proof.md"
)
AGENTS_MD = REPO_ROOT / "AGENTS.md"
STYLES = APPS_WEB_SRC / "styles.css"
EVIDENCE_OUT = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "ps-037d"
    / "gemini-campaign-intelligence-judge-narrative-report.json"
)

# Required core proof surfaces (spec section 10.3). Each surface that is
# present in this repo must import and render the shared campaign intelligence
# / judge narrative layer.
REQUIRED_SURFACES: tuple[tuple[str, Path], ...] = (
    ("Judge Cockpit Home", APPS_WEB_SRC / "JudgeCockpitHome.tsx"),
    ("B2 Evidence Explorer", APPS_WEB_SRC / "B2EvidenceExplorer.tsx"),
    ("Manifest Verification Panel", APPS_WEB_SRC / "ManifestVerificationPanel.tsx"),
    ("B2 Rehydrate Comparison", APPS_WEB_SRC / "B2RehydrateComparison.tsx"),
    ("Archive / Rehydrate / B2 Audit Vault", APPS_WEB_SRC / "B2AuditVault.tsx"),
    ("Review + Approval Workspace", APPS_WEB_SRC / "ReviewApprovalWorkspace.tsx"),
    ("Judge Evidence Pack", APPS_WEB_SRC / "JudgeEvidencePack.tsx"),
    ("Public Provenance Passport", APPS_WEB_SRC / "PublicPassportPage.tsx"),
    ("Review Room", APPS_WEB_SRC / "App.tsx"),
)


# The PS-037d implementation bundle: the canonical data module, the shared
# component, and the proof doc. Required UI / boundary strings are validated
# across this bundle.
def bundle_files() -> tuple[Path, ...]:
    return (DATA_MODULE, COMPONENT, PROOF_DOC)


# Source files scanned for Gemini / model / provider-call / B2-read /
# B2-write / broad-B2-scan code patterns. Includes every surface the layer is
# rendered on so a newly-introduced live path cannot hide behind an additive
# render.
def provider_b2_scan_files() -> tuple[Path, ...]:
    surfaces = tuple(p for _name, p in REQUIRED_SURFACES if p.is_file())
    return (DATA_MODULE, COMPONENT, *surfaces)


# Files scanned for the bad lowercase-only hidden-flag command literal.
# Includes the smoke itself: the literal must never appear contiguously in any
# changed file, and the smoke builds the search needle from fragments so it
# does not self-trip.
def bad_literal_scan_files() -> tuple[Path, ...]:
    surfaces = tuple(p for _name, p in REQUIRED_SURFACES if p.is_file())
    return (*bundle_files(), *surfaces, SMOKE_SELF)


# Files scanned for forbidden affirmative overclaims. This is the ONLY
# context-aware overclaim scanner for PS-037d: it scans the bundle plus the
# surfaces that render the layer. It does not scan smoke guard fixtures as
# product claims.
def claim_scan_files() -> tuple[Path, ...]:
    surfaces = tuple(p for _name, p in REQUIRED_SURFACES if p.is_file())
    return (*bundle_files(), *surfaces)


# Required identity / positioning strings (spec section 21).
REQUIRED_IDENTITY_STRINGS: tuple[str, ...] = (
    "PS-037d",
    "Gemini Campaign Intelligence / Judge Narrative",
    "Gemini",
)

# Required campaign intelligence / judge narrative concept strings (spec section
# 10.2 / 21).
REQUIRED_CONCEPT_STRINGS: tuple[str, ...] = (
    "campaign intelligence",
    "judge narrative",
    "campaign proof narrative",
    "campaign evidence summary",
    "Gemini provider label",
    "model output reference",
    "model output digest",
    "model output status",
    "campaign intelligence status",
    "judge narrative status",
    "narrative source evidence",
    "narrative source evidence references",
    "proof stack summary",
    "B2 evidence cross-reference",
    "manifest evidence cross-reference",
    "rehydrate evidence cross-reference",
    "trust boundary cross-reference",
    "multimodal proof cross-reference",
    "transcript/timestamp cross-reference",
    "voice/audio evidence cross-reference",
    "provider activity status",
    "local verification",
    "live verification status",
    "disclosure boundary",
    "not claimed",
    "unknown",
    "local/demo evidence",
)

# Required honest unavailable / not-claimed / deferred state strings (spec
# section 10.6 / 21).
REQUIRED_DEFERRED_STATES: tuple[str, ...] = (
    "local/demo evidence",
    "live provider evidence not available",
    "Gemini evidence not available",
    "model output not available",
    "campaign intelligence not available",
    "judge narrative not available",
    "campaign performance prediction not claimed",
    "marketing effectiveness proof not claimed",
    "business outcome guarantee not claimed",
    "conversion lift not claimed",
    "revenue impact not claimed",
    "audience targeting accuracy not claimed",
    "ad compliance approval not claimed",
    "model output truth not claimed",
    "semantic truth not claimed",
    "legal authenticity not claimed",
    "voice authenticity not claimed",
    "speaker identity not claimed",
    "biometric identification not claimed",
    "emotion truth not claimed",
    "deepfake detection not claimed",
    "content moderation not claimed",
    "transcript correctness not claimed",
    "timestamp correctness not claimed",
)

# Required de-escalation-pair strings (spec section 10.7 / 21).
REQUIRED_DEESCALATION_PAIRS: tuple[str, ...] = (
    "proof does not equal truth",
    "Gemini label does not equal live Gemini availability",
    "model output does not equal semantic truth",
    "judge narrative does not equal legal authenticity",
    "campaign intelligence does not equal campaign performance",
    "campaign narrative does not equal marketing effectiveness",
    "local campaign intelligence does not equal live Gemini availability",
    "demo/golden campaign narrative does not equal production security",
)

# Required negative-boundary strings (spec section 10.8 / 21).
REQUIRED_NEGATIVE_BOUNDARY: tuple[str, ...] = (
    "not model output truth",
    "not semantic truth",
    "not legal authenticity",
    "not human authorship",
    "not C2PA authenticity",
    "not Object Lock",
    "not tamper-proof",
    "not browser-side B2 byte verification",
    "not live B2 availability",
    "not live Gemini availability",
    "not production security",
    "not production compliance",
    "not legal review",
    "not chain-of-custody guarantee",
    "not campaign performance prediction",
    "not marketing effectiveness proof",
    "not business outcome guarantee",
    "not conversion lift",
    "not revenue impact",
    "not audience targeting accuracy",
    "not ad compliance approval",
    "not identity verification",
    "not biometric identification",
    "not deepfake detection",
    "not content moderation",
    "not OCR correctness",
    "not transcript correctness",
    "not timestamp correctness",
    "not voice authenticity",
    "not speaker identity",
    "not emotion truth",
)

# Required posture / boundary strings preserved by this smoke (spec section 21).
REQUIRED_POSTURE_STRINGS: tuple[str, ...] = (
    "no Gemini API calls",
    "no provider calls",
    "no live B2 reads",
    "no B2 writes",
    "no broad B2 scans",
    "no recursive smokes",
    "hidden Git flags h",
    "line[0]",
)

# AGENTS.md operating-law strings that must remain intact so the h/S hidden
# Git flag rule is not weakened to a lowercase-only check.
AGENTS_HS_RULE_STRINGS: tuple[str, ...] = (
    "hidden Git flags h and S",
    "fail when line[0] is h or S",
)
AGENTS_RED_LINE_STRINGS: tuple[str, ...] = (
    "do not claim legal authenticity",
    "do not claim Object Lock",
    "do not claim C2PA",
    "do not claim enterprise security",
)

# Per-category forbidden affirmative overclaim phrases. Each is matched
# case-insensitively against a line; if the surrounding paragraph does not
# carry a non-claim context marker, the line is flagged. A category's
# ``no_X_claim`` boolean is true only when no such affirmative overclaim is
# present.
CLAIM_CATEGORY_PHRASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("model_output_truth", (
        "proves model output truth",
        "model output truth verified",
        "model output truth proven",
        "model output is true",
    )),
    ("semantic_truth", (
        "proves semantic truth",
        "is semantic truth",
        "semantic truth verified",
        "semantic truth proven",
        "semantic truth is proven",
    )),
    ("legal_authenticity", (
        "proves legal authenticity",
        "is legal authenticity",
        "legal authenticity verified",
        "legal authenticity proven",
    )),
    ("human_authorship", (
        "proves human authorship",
        "is human authorship",
        "human authorship verified",
        "human authorship proven",
    )),
    ("c2pa_authenticity", (
        "proves c2pa authenticity",
        "is c2pa authenticity",
        "c2pa authenticity verified",
        "c2pa proven",
        "c2pa verified",
    )),
    ("object_lock", (
        "proves object lock",
        "object lock is enabled",
        "object lock enabled",
        "object lock verified",
    )),
    ("tamper_proof", (
        "proves tamper-proof",
        "tamper-proof storage is enabled",
        "tamper-proof verified",
    )),
    ("browser_side_b2_byte_verification", (
        "browser verified the b2 bytes",
        "browser fetched and hashed the b2 object",
        "browser-side b2 byte verification succeeded",
    )),
    ("live_b2_availability", (
        "live b2 availability verified",
        "live b2 verified",
        "live b2 availability confirmed",
    )),
    ("live_gemini_availability", (
        "live gemini availability verified",
        "live gemini verified",
        "live gemini availability confirmed",
        "gemini is available",
        "gemini availability confirmed",
    )),
    ("production_security", (
        "production security verified",
        "production security proven",
        "production security is verified",
        "enterprise-grade security",
    )),
    ("production_compliance", (
        "production compliance verified",
        "production compliance proven",
        "production compliance confirmed",
    )),
    ("legal_review", (
        "legal review completed",
        "legal review verified",
        "legal review passed",
        "proves legal review",
    )),
    ("chain_of_custody_guarantee", (
        "chain of custody guaranteed",
        "chain-of-custody guarantee verified",
        "proves chain of custody",
    )),
    ("campaign_performance_prediction", (
        "predicts campaign performance",
        "campaign performance predicted",
        "campaign performance prediction verified",
        "campaign performance prediction confirmed",
    )),
    ("marketing_effectiveness_proof", (
        "proves marketing effectiveness",
        "marketing effectiveness proven",
        "marketing effectiveness verified",
        "marketing effectiveness confirmed",
    )),
    ("business_outcome_guarantee", (
        "guarantees business outcome",
        "business outcome guaranteed",
        "business outcome guarantee verified",
    )),
    ("conversion_lift", (
        "proves conversion lift",
        "conversion lift measured",
        "conversion lift verified",
        "conversion lift confirmed",
    )),
    ("revenue_impact", (
        "proves revenue impact",
        "revenue impact verified",
        "revenue impact confirmed",
        "revenue impact proven",
    )),
    ("audience_targeting_accuracy", (
        "proves audience targeting accuracy",
        "audience targeting accuracy verified",
        "audience targeting accuracy confirmed",
    )),
    ("ad_compliance_approval", (
        "ad compliance approved",
        "ad compliance approval verified",
        "ad compliance approval confirmed",
        "proves ad compliance approval",
    )),
    ("identity_verification", (
        "proves identity verification",
        "identity verification verified",
        "identity verification proven",
        "identity is verified",
        "identity verification confirmed",
    )),
    ("biometric_identification", (
        "proves biometric identification",
        "biometric identification verified",
        "biometric identification proven",
        "biometric identified",
    )),
    ("deepfake_detection", (
        "proves deepfake detection",
        "deepfake detection verified",
        "deepfakes detected",
        "deepfake detected",
    )),
    ("content_moderation", (
        "proves content moderation",
        "content moderation verified",
        "content moderated",
        "content policy verified",
    )),
    ("ocr_correctness", (
        "proves ocr correctness",
        "ocr correctness verified",
        "ocr correctness proven",
    )),
    ("transcript_correctness", (
        "proves transcript correctness",
        "transcript correctness verified",
        "transcript correctness proven",
    )),
    ("timestamp_correctness", (
        "proves timestamp correctness",
        "timestamp correctness verified",
        "timestamp correctness proven",
    )),
    ("voice_authenticity", (
        "proves voice authenticity",
        "voice authenticity verified",
        "voice authenticity proven",
        "voice is authentic",
    )),
    ("speaker_identity", (
        "proves speaker identity",
        "speaker identity verified",
        "speaker identity proven",
        "speaker identity confirmed",
        "speaker is identified",
    )),
    ("emotion_truth", (
        "proves emotion truth",
        "emotion truth verified",
        "emotion truth proven",
    )),
)

CONTEXT_MARKERS_RE = re.compile(
    r"does not|do not|must not|\bnot\b|non-claim|non-claims|forbidden|"
    r"reject|rejected|avoid|without overclaim|unless actually implemented|"
    r"only inside non-claim|limitation|limitations|no affirmative|"
    r"unavailable|blocked|honestly|no live|no_new|no_fake|pending|planned|"
    r"did not fetch|does not claim|did not claim|without|none claimed|"
    r"would appear|if captured|no actual|no fake|not implemented|"
    r"is not implemented|not a certification|not legal advice|"
    r"it is not|it did not|does not equal|not equal",
    re.IGNORECASE,
)
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")

SECRET_SUBSTRINGS: tuple[str, ...] = (
    "B2_APP_KEY=",
    "CLOUDFLARE_API_TOKEN=",
    "GEMINI_API_KEY=",
    "GMI_API_KEY=",
    "ELEVENLABS_API_KEY=",
    "HUME_API_KEY=",
    "ASSEMBLYAI_API_KEY=",
    "Bearer ",
    "AKIA",
    "AWS_SECRET_ACCESS_KEY",
)
SECRET_KEY_RE = re.compile(r"(?<![A-Za-z])sk-[A-Za-z0-9]")

# Validation needles used to detect a newly-introduced live Gemini API call
# path in the scanned app source. These are SCANNER NEEDLES (string
# constants), not executable calls: this smoke performs no network, provider,
# model, or B2 behavior whatsoever. The needles are assembled from fragments
# where useful so a naive regex audit scanning THIS smoke cannot self-trip.
FORBIDDEN_GEMINI_CALL_NEEDLES: tuple[str, ...] = (
    "generativelanguage" + "." + "googleapis" + ".com",
    "gemini" + "." + "googleapis" + ".com",
    "aiplatform" + "." + "googleapis" + ".com",
    "Google" + "GenerativeAI",
    "Generative" + "Model",
    "genai" + ".GenerativeModel",
    "genera" + "te_content",
    "gemini" + "_client",
    "Gemini" + "Client",
)

# Validation needles used to detect a newly-introduced live provider-call
# path. Scanner needles only; no executable behavior.
FORBIDDEN_LIVE_CALL_NEEDLES: tuple[str, ...] = (
    "call_provider",
    "fetchFromProvider",
    "requests" + ".post",
    "urlopen" + "(",
    "httpx" + ".post",
    "client.post(",
)

# Validation needles used to detect a newly-introduced broad B2 object read
# path. Scanner needles only; no executable behavior.
FORBIDDEN_B2_READ_NEEDLES: tuple[str, ...] = (
    "read_archive_from_b2",
    "b2.fetch",
    "b2GetObject",
    "list_b2_objects",
    "fetchB2Object",
    "fetch" + "(",
)

# Validation needles used to detect a newly-introduced B2 object write path.
FORBIDDEN_B2_WRITE_NEEDLES: tuple[str, ...] = (
    "upload_to_b2",
    "b2.put",
    "b2PutObject",
    "put_b2_object",
    "uploadB2Object",
    "write_archive_to_b2",
)

# Validation needles used to detect a newly-introduced broad B2 scan path.
FORBIDDEN_B2_SCAN_NEEDLES: tuple[str, ...] = (
    "list_all_b2_objects",
    "scan_b2_bucket",
    "listObjectsV2",
    "b2_list_buckets",
    "enumerate_b2_prefix",
)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return sl.read_text(path)


def _paragraph_range(lines: list[str], index: int) -> tuple[int, int]:
    start = index
    while start > 0 and lines[start - 1].strip():
        start -= 1
    end = index + 1
    while end < len(lines) and lines[end].strip():
        end += 1
    return start, end


def _line_has_nonclaim_context(lines: list[str], index: int) -> bool:
    start, end = _paragraph_range(lines, index)
    window = "\n".join(lines[start:end])
    return bool(CONTEXT_MARKERS_RE.search(window))


def _scan_affirmative(
    paths: tuple[Path, ...],
    phrases: tuple[str, ...],
) -> list[str]:
    """Return problem strings for forbidden affirmative claims.

    A phrase is flagged only when the surrounding paragraph lacks a non-claim
    context marker (mirrors PS-031 / PS-034 / PS-035 / PS-036 / PS-037 /
    PS-037a / PS-037b / PS-037c).
    """
    problems: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        lines = read_text(path).splitlines()
        in_fence = False
        for i, line in enumerate(lines):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            line_lower = line.lower()
            hit = False
            for phrase in phrases:
                if phrase in line_lower:
                    hit = True
                    break
            if not hit:
                continue
            if _line_has_nonclaim_context(lines, i):
                continue
            problems.append(
                f"{rel(path)}:{i + 1}: affirmative claim with no non-claim "
                f"context -> {line.strip()!r}"
            )
    return problems


def _git_status_entries() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for line in sl.git_status_short().splitlines():
        if not line.strip():
            continue
        tag = line[:2]
        path = line[3:]
        out.append((tag, path))
    return out


def _bundle_blob() -> str:
    blob = ""
    for path in bundle_files():
        if path.is_file():
            blob += "\n" + read_text(path)
    return blob


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_data_module_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not DATA_MODULE.is_file():
        return False, [f"missing data module {rel(DATA_MODULE)}"]
    text = read_text(DATA_MODULE)
    for needle in (
        "GEMINI_CAMPAIGN_INTELLIGENCE_TITLE",
        "GEMINI_CAMPAIGN_INTELLIGENCE_ITEMS",
        "GEMINI_CAMPAIGN_INTELLIGENCE_DEESCALATION_PAIRS",
        "GEMINI_CAMPAIGN_INTELLIGENCE_NEGATIVE_BOUNDARY",
        "GEMINI_CAMPAIGN_INTELLIGENCE_PERSISTENT_STATEMENT",
        "GEMINI_CAMPAIGN_INTELLIGENCE_DEFERRED_STATES",
        "GEMINI_CAMPAIGN_INTELLIGENCE_MULTIMODAL_CROSS_REFERENCE",
        "GEMINI_CAMPAIGN_INTELLIGENCE_TRANSCRIPT_CROSS_REFERENCE",
        "GEMINI_CAMPAIGN_INTELLIGENCE_VOICE_AUDIO_CROSS_REFERENCE",
        "GEMINI_CAMPAIGN_INTELLIGENCE_TRUST_BOUNDARY_CROSS_REFERENCE",
    ):
        if needle not in text:
            problems.append(f"data module missing {needle!r}")
    return (not problems, problems)


def check_component_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not COMPONENT.is_file():
        return False, [f"missing component {rel(COMPONENT)}"]
    text = read_text(COMPONENT)
    for needle in (
        "export function CampaignIntelligenceJudgeNarrativeLayer",
        '"panel"',
        '"summary"',
        "CampaignIntelligenceJudgeNarrativeLayerVariant",
        "geminiCampaignIntelligence",
    ):
        if needle not in text:
            problems.append(f"component missing reference to {needle!r}")
    return (not problems, problems)


def check_layer_wired() -> tuple[bool, list[str]]:
    """The component reads only from the data module (no provider / B2)."""
    problems: list[str] = []
    if not COMPONENT.is_file():
        return False, [f"missing component {rel(COMPONENT)}"]
    text = read_text(COMPONENT)
    if 'from "./geminiCampaignIntelligence"' not in text:
        problems.append(
            "component does not import from ./geminiCampaignIntelligence"
        )
    return (not problems, problems)


def check_required_surfaces_have_campaign_intelligence_layer() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for name, path in REQUIRED_SURFACES:
        if not path.is_file():
            # A required surface absent from this repo is not a failure; the
            # contract only applies where the surface is present.
            continue
        text = read_text(path)
        if "CampaignIntelligenceJudgeNarrativeLayer" not in text:
            problems.append(
                f"{name} ({rel(path)}) does not reference "
                f"CampaignIntelligenceJudgeNarrativeLayer"
            )
        if "<CampaignIntelligenceJudgeNarrativeLayer" not in text:
            problems.append(
                f"{name} ({rel(path)}) does not render "
                f"<CampaignIntelligenceJudgeNarrativeLayer"
            )
    return (not problems, problems)


def check_trust_boundary_cross_reference() -> tuple[bool, list[str]]:
    """The layer integrates / cross-references the PS-037 Disclosure + Trust
    Boundary Layer."""
    problems: list[str] = []
    blob = _bundle_blob()
    if "PS-037" not in blob:
        problems.append("bundle missing PS-037 cross-reference")
    if "Trust Boundary" not in blob:
        problems.append("bundle missing Trust Boundary cross-reference")
    if "trust boundary cross-reference" not in blob.lower():
        problems.append(
            "bundle missing trust boundary cross-reference indicator"
        )
    return (not problems, problems)


def check_multimodal_proof_cross_reference() -> tuple[bool, list[str]]:
    """The layer integrates / cross-references the PS-037a Multimodal Proof
    Layer."""
    problems: list[str] = []
    blob = _bundle_blob()
    if "PS-037a" not in blob:
        problems.append("bundle missing PS-037a cross-reference")
    if "Multimodal Proof Layer" not in blob:
        problems.append("bundle missing Multimodal Proof Layer cross-reference")
    if "MULTIMODAL_PROOF_MANIFEST" not in read_text(DATA_MODULE):
        problems.append(
            "data module does not import MULTIMODAL_PROOF_* cross-reference"
        )
    return (not problems, problems)


def check_transcript_timestamp_cross_reference() -> tuple[bool, list[str]]:
    """The layer integrates / cross-references the PS-037b Transcript/Timestamp
    Evidence layer."""
    problems: list[str] = []
    blob = _bundle_blob()
    if "PS-037b" not in blob:
        problems.append("bundle missing PS-037b cross-reference")
    if "Transcript/Timestamp" not in blob:
        problems.append(
            "bundle missing Transcript/Timestamp cross-reference"
        )
    if "transcript/timestamp cross-reference" not in blob:
        problems.append(
            "bundle missing transcript/timestamp cross-reference indicator"
        )
    return (not problems, problems)


def check_voice_audio_evidence_cross_reference() -> tuple[bool, list[str]]:
    """The layer integrates / cross-references the PS-037c Voice/Audio Evidence
    Provider Choice layer."""
    problems: list[str] = []
    blob = _bundle_blob()
    if "PS-037c" not in blob:
        problems.append("bundle missing PS-037c cross-reference")
    if "Voice/Audio Evidence Provider Choice" not in blob:
        problems.append(
            "bundle missing Voice/Audio Evidence Provider Choice cross-reference"
        )
    if "voice/audio evidence cross-reference" not in blob:
        problems.append(
            "bundle missing voice/audio evidence cross-reference indicator"
        )
    return (not problems, problems)


def check_identity_strings() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = _bundle_blob()
    for needle in REQUIRED_IDENTITY_STRINGS:
        if needle not in blob:
            problems.append(f"bundle missing required identity string {needle!r}")
    return (not problems, problems)


def check_concept_strings() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = _bundle_blob()
    for needle in REQUIRED_CONCEPT_STRINGS:
        if needle not in blob:
            problems.append(
                f"bundle missing required campaign intelligence concept {needle!r}"
            )
    return (not problems, problems)


def check_deferred_states() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = _bundle_blob()
    for needle in REQUIRED_DEFERRED_STATES:
        if needle not in blob:
            problems.append(
                f"bundle missing required deferred / unavailable / not-claimed "
                f"state {needle!r}"
            )
    return (not problems, problems)


def check_deescalation_pairs() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = _bundle_blob()
    for needle in REQUIRED_DEESCALATION_PAIRS:
        if needle not in blob:
            problems.append(f"bundle missing required de-escalation pair {needle!r}")
    return (not problems, problems)


def check_negative_boundary_strings() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = _bundle_blob()
    for needle in REQUIRED_NEGATIVE_BOUNDARY:
        if needle not in blob:
            problems.append(f"bundle missing required negative boundary string {needle!r}")
    return (not problems, problems)


def check_posture_strings_in_smoke() -> tuple[bool, list[str]]:
    """Required posture / boundary strings must be preserved by this smoke."""
    problems: list[str] = []
    text = read_text(SMOKE_SELF)
    for needle in REQUIRED_POSTURE_STRINGS:
        if needle not in text:
            problems.append(f"smoke missing required posture string {needle!r}")
    return (not problems, problems)


def check_proof_doc_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not PROOF_DOC.is_file():
        return False, [f"missing proof doc {rel(PROOF_DOC)}"]
    text = read_text(PROOF_DOC)
    for needle in (
        "PS-037d",
        "Gemini Campaign Intelligence / Judge Narrative",
    ):
        if needle not in text:
            problems.append(f"proof doc missing {needle!r}")
    return (not problems, problems)


def check_styles_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not STYLES.is_file():
        return False, [f"missing {rel(STYLES)}"]
    text = read_text(STYLES)
    for needle in (
        ".campaign-intelligence-judge-narrative-layer-panel",
        ".campaign-intelligence-judge-narrative-layer-summary",
    ):
        if needle not in text:
            problems.append(f"styles missing additive class {needle!r}")
    return (not problems, problems)


def check_no_gemini_api_calls() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_GEMINI_CALL_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden Gemini API call pattern "
                    f"{pattern!r}"
                )
    return (not problems, problems)


def check_no_provider_calls() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_LIVE_CALL_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden provider-call pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_b2_reads() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_B2_READ_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden B2 read pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_b2_writes() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_B2_WRITE_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden B2 write pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_b2_scans() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_B2_SCAN_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden broad B2 scan pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_recursive_smokes() -> tuple[bool, list[str]]:
    problems: list[str] = []
    try:
        sl.assert_no_recursive_smoke_execution(SMOKE_SELF)
    except sl.HarnessError as exc:
        problems.append(str(exc))
    return (not problems, problems)


def check_no_bad_hidden_flag_literal() -> tuple[bool, list[str]]:
    """The bad lowercase-only hidden-flag command literal must be absent.

    The search needle is assembled from fragments so the smoke itself never
    contains the contiguous forbidden literal and therefore does not self-trip.
    """
    needle = "gr" + "ep" + " -" + "E " + "'^" + "[a-z]" + "'"
    problems: list[str] = []
    for path in bad_literal_scan_files():
        if not path.is_file():
            continue
        if needle in read_text(path):
            problems.append(
                f"{rel(path)}: contains the forbidden lowercase-only "
                f"hidden-flag command literal"
            )
    return (not problems, problems)


def _hidden_flag_hits() -> tuple[list[str], list[str]]:
    """Return (h_hits, S_hits) from ``git ls-files -v``.

    This is the explicit h/S checker required by the operating law: it reads
    ``git ls-files -v`` and flags a line when ``line[0]`` is ``h`` (assume
    unchanged) or ``S`` (skip-worktree, uppercase). A lowercase-only marker
    check is not sufficient because it misses uppercase ``S`` skip-worktree.
    This intentionally does NOT reuse the shared lowercase-only marker check.
    """
    res = sl.run_command(["git", "ls-files", "-v"], cwd=REPO_ROOT)
    h_hits: list[str] = []
    s_hits: list[str] = []
    for line in res.stdout.splitlines():
        if not line:
            continue
        first = line[0]
        if first == "h":
            h_hits.append(line)
        elif first == "S":
            s_hits.append(line)
    return h_hits, s_hits


def check_hidden_git_flags_h() -> tuple[bool, list[str]]:
    h_hits, _ = _hidden_flag_hits()
    return (not h_hits, h_hits)


def check_hidden_git_flags_S() -> tuple[bool, list[str]]:
    _, s_hits = _hidden_flag_hits()
    return (not s_hits, s_hits)


def _claim_problems_for(category: str) -> list[str]:
    for cat, phrases in CLAIM_CATEGORY_PHRASES:
        if cat == category:
            return _scan_affirmative(claim_scan_files(), phrases)
    return []


def check_no_forbidden_overclaims() -> tuple[bool, list[str]]:
    all_phrases = tuple(p for _cat, phrases in CLAIM_CATEGORY_PHRASES for p in phrases)
    problems = _scan_affirmative(claim_scan_files(), all_phrases)
    return (not problems, problems)


def check_truth_boundary_preserved() -> tuple[bool, list[str]]:
    """AGENTS.md h/S rule + red lines intact, boundary copy + neg strings present."""
    problems: list[str] = []
    if not AGENTS_MD.is_file():
        return False, [f"missing {rel(AGENTS_MD)}"]
    text = read_text(AGENTS_MD)
    for needle in AGENTS_HS_RULE_STRINGS:
        if needle not in text:
            problems.append(f"AGENTS.md missing h/S rule string {needle!r}")
    for needle in AGENTS_RED_LINE_STRINGS:
        if needle not in text:
            problems.append(f"AGENTS.md missing red line {needle!r}")
    blob = _bundle_blob()
    if "ProofStudio proves what the pipeline recorded" not in blob:
        problems.append("bundle missing persistent positioning statement")
    for needle in REQUIRED_NEGATIVE_BOUNDARY:
        if needle not in blob:
            problems.append(f"bundle missing negative boundary string {needle!r}")
    return (not problems, problems)


def check_secrets_absent() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in claim_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for needle in SECRET_SUBSTRINGS:
            if needle in text:
                idx = text.find(needle)
                line_no = text.count("\n", 0, idx) + 1
                problems.append(f"{rel(path)}:{line_no}: secret literal {needle!r}")
        for m in SECRET_KEY_RE.finditer(text):
            idx = m.start()
            line_no = text.count("\n", 0, idx) + 1
            problems.append(f"{rel(path)}:{line_no}: secret literal {m.group(0)!r}")
    return (not problems, problems)


def check_git_diff_check_clean() -> tuple[bool, list[str]]:
    res = sl.run_command(["git", "diff", "--check"], cwd=REPO_ROOT)
    problems: list[str] = []
    output = (res.stdout or "").strip()
    if res.returncode != 0 or output:
        text = output or f"git diff --check exited {res.returncode}"
        problems.append(f"git diff --check not clean: {text}")
    return (not problems, problems)


def check_prior_evidence_clean() -> tuple[bool, list[str]]:
    """No tracked evidence outside docs/evidence/ps-037d/ may be left dirty."""
    problems: list[str] = []
    try:
        entries = _git_status_entries()
    except sl.HarnessError as exc:
        return False, [f"could not run git status: {exc}"]
    for _tag, path in entries:
        path = path.strip().strip('"')
        if path.startswith("docs/evidence/") and not path.startswith(
            "docs/evidence/ps-037d/"
        ):
            problems.append(
                f"prior-slice evidence left dirty by PS-037d smoke: {path}"
            )
    return (not problems, problems)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None) -> tuple[bool, bool, bool]:
    """Return (write_evidence, check_only, no_frontend).

    Default is non-mutating local validation: check_only=True,
    write_evidence=False, no_frontend=True.
    """
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--check-only", action="store_true", default=True)
    p.add_argument(
        "--write-evidence",
        dest="write_evidence",
        action="store_true",
        default=False,
    )
    p.add_argument(
        "--no-frontend",
        dest="no_frontend",
        action="store_true",
        default=True,
    )
    ns, _unknown = p.parse_known_args(list(argv) if argv is not None else None)
    write_evidence = bool(ns.write_evidence)
    check_only = not write_evidence
    return write_evidence, check_only, bool(ns.no_frontend)


def run(argv: list[str] | None = None) -> int:
    write_evidence, _check_only, _no_frontend = parse_args(argv)

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("campaign_intelligence_data_module_present", check_data_module_present()),
        ("campaign_intelligence_component_present", check_component_present()),
        ("campaign_intelligence_layer_present", check_layer_wired()),
        (
            "required_surfaces_have_campaign_intelligence_layer",
            check_required_surfaces_have_campaign_intelligence_layer(),
        ),
        ("trust_boundary_cross_reference_present", check_trust_boundary_cross_reference()),
        ("multimodal_proof_cross_reference_present", check_multimodal_proof_cross_reference()),
        ("transcript_timestamp_cross_reference_present", check_transcript_timestamp_cross_reference()),
        ("voice_audio_evidence_cross_reference_present", check_voice_audio_evidence_cross_reference()),
        ("identity_strings_present", check_identity_strings()),
        ("concept_strings_present", check_concept_strings()),
        ("deferred_states_present", check_deferred_states()),
        ("deescalation_pairs_present", check_deescalation_pairs()),
        ("negative_boundary_strings_present", check_negative_boundary_strings()),
        ("posture_strings_in_smoke", check_posture_strings_in_smoke()),
        ("proof_doc_present", check_proof_doc_present()),
        ("styles_present", check_styles_present()),
        ("no_gemini_api_calls", check_no_gemini_api_calls()),
        ("no_provider_calls", check_no_provider_calls()),
        ("no_live_b2_reads", check_no_b2_reads()),
        ("no_b2_writes", check_no_b2_writes()),
        ("no_broad_b2_scans", check_no_b2_scans()),
        ("no_recursive_smokes", check_no_recursive_smokes()),
        ("no_bad_hidden_flag_literal", check_no_bad_hidden_flag_literal()),
        ("no_hidden_git_flags_h", check_hidden_git_flags_h()),
        ("no_hidden_git_flags_S", check_hidden_git_flags_S()),
        ("truth_boundary_preserved", check_truth_boundary_preserved()),
        ("no_forbidden_overclaims", check_no_forbidden_overclaims()),
        ("secrets_absent", check_secrets_absent()),
        ("git_diff_check_clean", check_git_diff_check_clean()),
        ("prior_evidence_clean", check_prior_evidence_clean()),
    ]

    all_pass, detail = sl.run_contract_checks(
        "PS-037d Gemini Campaign Intelligence / Judge Narrative", checks
    )

    failures: list[str] = []
    for _name, (ok, problems) in checks:
        if not ok:
            failures.extend(problems)

    def _passed(name: str) -> bool:
        return detail.get(name) == "pass"

    blob = _bundle_blob()

    # Granular no_X_claim booleans, derived per category from the affirmative
    # overclaim scan. True only when no forbidden affirmative claim of that
    # category is present.
    def _no_claim(category: str) -> bool:
        return not _claim_problems_for(category)

    report: dict = {
        "ok": bool(all_pass),
        "slice_id": "ps037d",
        "campaign_intelligence_component_present": _passed("campaign_intelligence_component_present"),
        "campaign_intelligence_data_module_present": _passed("campaign_intelligence_data_module_present"),
        "campaign_intelligence_layer_present": _passed("campaign_intelligence_layer_present"),
        "required_surfaces_have_campaign_intelligence_layer": _passed(
            "required_surfaces_have_campaign_intelligence_layer"
        ),
        "trust_boundary_cross_reference_present": _passed(
            "trust_boundary_cross_reference_present"
        ),
        "multimodal_proof_cross_reference_present": _passed(
            "multimodal_proof_cross_reference_present"
        ),
        "transcript_timestamp_cross_reference_present": _passed(
            "transcript_timestamp_cross_reference_present"
        ),
        "voice_audio_evidence_cross_reference_present": _passed(
            "voice_audio_evidence_cross_reference_present"
        ),
        "gemini_label_present": "Gemini" in blob,
        "campaign_intelligence_present": "campaign intelligence" in blob,
        "judge_narrative_present": "judge narrative" in blob,
        "campaign_proof_narrative_present": "campaign proof narrative" in blob,
        "campaign_evidence_summary_present": "campaign evidence summary" in blob,
        "gemini_provider_label_present": "Gemini provider label" in blob,
        "model_output_reference_present_or_honestly_unavailable": "model output reference" in blob,
        "model_output_digest_present_or_honestly_unavailable": "model output digest" in blob,
        "model_output_status_present": "model output status" in blob,
        "campaign_intelligence_status_present": "campaign intelligence status" in blob,
        "judge_narrative_status_present": "judge narrative status" in blob,
        "narrative_source_evidence_present": "narrative source evidence" in blob,
        "narrative_source_evidence_references_present": "narrative source evidence references" in blob,
        "proof_stack_summary_present": "proof stack summary" in blob,
        "b2_evidence_cross_reference_present": "B2 evidence cross-reference" in blob,
        "manifest_evidence_cross_reference_present": "manifest evidence cross-reference" in blob,
        "rehydrate_evidence_cross_reference_present": "rehydrate evidence cross-reference" in blob,
        "provider_activity_status_present": "provider activity status" in blob,
        "local_verification_status_present": "local verification" in blob,
        "live_verification_status_present": "live verification status" in blob,
        "disclosure_boundary_present": "disclosure boundary" in blob,
        "not_claimed_status_present": "not claimed" in blob,
        "unknown_status_present": "unknown" in blob,
        "local_demo_evidence_present": "local/demo evidence" in blob,
        "live_provider_evidence_not_available_present": "live provider evidence not available" in blob,
        "gemini_evidence_not_available_present": "Gemini evidence not available" in blob,
        "model_output_not_available_present": "model output not available" in blob,
        "campaign_intelligence_not_available_present": "campaign intelligence not available" in blob,
        "judge_narrative_not_available_present": "judge narrative not available" in blob,
        "proof_does_not_equal_truth_present": "proof does not equal truth" in blob,
        "gemini_label_does_not_equal_live_gemini_availability_present": "Gemini label does not equal live Gemini availability" in blob,
        "model_output_does_not_equal_semantic_truth_present": "model output does not equal semantic truth" in blob,
        "judge_narrative_does_not_equal_legal_authenticity_present": "judge narrative does not equal legal authenticity" in blob,
        "campaign_intelligence_does_not_equal_campaign_performance_present": "campaign intelligence does not equal campaign performance" in blob,
        "campaign_narrative_does_not_equal_marketing_effectiveness_present": "campaign narrative does not equal marketing effectiveness" in blob,
        "local_campaign_intelligence_does_not_equal_live_gemini_availability_present": "local campaign intelligence does not equal live Gemini availability" in blob,
        "demo_golden_campaign_narrative_does_not_equal_production_security_present": "demo/golden campaign narrative does not equal production security" in blob,
        "no_model_output_truth_claim": _no_claim("model_output_truth"),
        "no_semantic_truth_claim": _no_claim("semantic_truth"),
        "no_legal_authenticity_claim": _no_claim("legal_authenticity"),
        "no_human_authorship_claim": _no_claim("human_authorship"),
        "no_c2pa_authenticity_claim": _no_claim("c2pa_authenticity"),
        "no_object_lock_claim": _no_claim("object_lock"),
        "no_tamper_proof_claim": _no_claim("tamper_proof"),
        "no_browser_side_b2_byte_verification_claim": _no_claim("browser_side_b2_byte_verification"),
        "no_live_b2_availability_claim": _no_claim("live_b2_availability"),
        "no_live_gemini_availability_claim": _no_claim("live_gemini_availability"),
        "no_production_security_claim": _no_claim("production_security"),
        "no_production_compliance_claim": _no_claim("production_compliance"),
        "no_legal_review_claim": _no_claim("legal_review"),
        "no_chain_of_custody_guarantee_claim": _no_claim("chain_of_custody_guarantee"),
        "no_campaign_performance_prediction_claim": _no_claim("campaign_performance_prediction"),
        "no_marketing_effectiveness_proof_claim": _no_claim("marketing_effectiveness_proof"),
        "no_business_outcome_guarantee_claim": _no_claim("business_outcome_guarantee"),
        "no_conversion_lift_claim": _no_claim("conversion_lift"),
        "no_revenue_impact_claim": _no_claim("revenue_impact"),
        "no_audience_targeting_accuracy_claim": _no_claim("audience_targeting_accuracy"),
        "no_ad_compliance_approval_claim": _no_claim("ad_compliance_approval"),
        "no_identity_verification_claim": _no_claim("identity_verification"),
        "no_biometric_identification_claim": _no_claim("biometric_identification"),
        "no_deepfake_detection_claim": _no_claim("deepfake_detection"),
        "no_content_moderation_claim": _no_claim("content_moderation"),
        "no_ocr_correctness_claim": _no_claim("ocr_correctness"),
        "no_transcript_correctness_claim": _no_claim("transcript_correctness"),
        "no_timestamp_correctness_claim": _no_claim("timestamp_correctness"),
        "no_voice_authenticity_claim": _no_claim("voice_authenticity"),
        "no_speaker_identity_claim": _no_claim("speaker_identity"),
        "no_emotion_truth_claim": _no_claim("emotion_truth"),
        "no_gemini_api_calls": _passed("no_gemini_api_calls"),
        "no_provider_calls": _passed("no_provider_calls"),
        "no_live_b2_reads": _passed("no_live_b2_reads"),
        "no_b2_writes": _passed("no_b2_writes"),
        "no_broad_b2_scans": _passed("no_broad_b2_scans"),
        "no_recursive_smokes": _passed("no_recursive_smokes"),
        "no_hidden_git_flags_h": _passed("no_hidden_git_flags_h"),
        "no_hidden_git_flags_S": _passed("no_hidden_git_flags_S"),
        "no_forbidden_overclaims": _passed("no_forbidden_overclaims"),
        "prior_evidence_clean": _passed("prior_evidence_clean"),
        "failures": failures,
        "checks": detail,
        "checks_count": len(checks),
        "evidence_dir": "docs/evidence/ps-037d/",
        "data_source": "accepted local / golden / demo data (read-only)",
        "checked_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }

    # Keep ok strictly bound to failures so the schema rule holds: ok is true
    # only when every measured field is truthful and no failure is present.
    report["ok"] = bool(all_pass and not failures)

    if write_evidence:
        EVIDENCE_OUT.parent.mkdir(parents=True, exist_ok=True)
        sl.write_json_atomic(EVIDENCE_OUT, report)
        print(f"evidence: {rel(EVIDENCE_OUT)}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(run())
