#!/usr/bin/env python3
"""PS-038a Campaign Proof Room -- smoke / validation.

This smoke validates ONLY the PS-038a slice. It is local / static by default:
it does not start a browser, does not run the frontend typecheck / build, does
not call Cloudflare, does not mutate DNS, does not create any Cloudflare
resource, does not deploy Cloudflare Pages, does not deploy Cloudflare Workers,
does not read or write any Cloudflare R2 object, does not write any Backblaze B2
object, does not call any provider, does not call any model, does not read or
write any B2 object, does not perform a broad B2 scan, does not make any
deployment change, does not make any env/secrets change, does not make any
render.yaml change, does not make any requirements/dependency change, does not
call the central regression gate, and does not recursively execute another
feature smoke. Default behavior is non-mutating local validation
(``--check-only``); no evidence file is written unless ``--write-evidence`` is
explicit.

Standard flags (PS-034B / PS-035D feature-smoke contract):

    --check-only      default; non-mutating local validation; writes nothing
    --write-evidence  writes only docs/evidence/ps-038a/ evidence
    --no-frontend     skip the frontend typecheck/build (always skipped; a
                      feature smoke never runs the frontend)

Truth boundary: this smoke validates that the PS-038a Campaign Proof Room is
honest and consistent. ProofStudio proves what the pipeline recorded for the
campaign. The Campaign Proof Room is not campaign performance proof, not
marketing effectiveness proof, not business outcome guarantee, not semantic
truth, not legal authenticity, not legal approval, not human authorship, not
C2PA authenticity, not production readiness, not production security, not
production compliance, not legal compliance, not live deployment, not provider
availability, not model availability, not Backblaze B2 live availability, not
Cloudflare availability, not uptime guarantee, not cost guarantee, not
performance guarantee, not cold-start performance guarantee, not Object Lock,
not tamper-proof, not browser-side B2 byte verification, not content moderation
correctness, not transcript correctness, not emotion truth, not speaker
identity, not biometric identity, and not model output truth.

Posture contract strings preserved by this smoke: no deployment changes, no
env/secrets changes, no render.yaml changes, no requirements/dependency changes,
no Cloudflare API calls, no DNS mutation, no Cloudflare resource creation, no
Cloudflare Pages deployment, no Cloudflare Workers deployment, no Cloudflare R2
live reads, no Cloudflare R2 writes, no Backblaze B2 writes, no provider calls,
no model calls, no live B2 reads, no B2 writes, no broad B2 scans, no recursive
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
DATA_MODULE = APPS_WEB_SRC / "campaignProofRoom.ts"
COMPONENT = APPS_WEB_SRC / "CampaignProofRoom.tsx"
APP_TSX = APPS_WEB_SRC / "App.tsx"
JUDGE_HOME = APPS_WEB_SRC / "JudgeCockpitHome.tsx"
SMOKE_SELF = (
    REPO_ROOT
    / "scripts"
    / "ps038a_campaign_proof_room_smoke.py"
)
PROOF_DOC = (
    REPO_ROOT
    / "docs"
    / "ps-038a-campaign-proof-room-proof.md"
)
AGENTS_MD = REPO_ROOT / "AGENTS.md"
STYLES = APPS_WEB_SRC / "styles.css"
RENDER_YAML = REPO_ROOT / "render.yaml"
ENV_FILES: tuple[Path, ...] = (
    REPO_ROOT / ".env",
    REPO_ROOT / ".env.local",
    REPO_ROOT / ".env.example",
)
REQUIREMENTS_FILES: tuple[Path, ...] = (
    REPO_ROOT / "requirements.txt",
    REPO_ROOT / "apps" / "api" / "requirements.txt",
)
EVIDENCE_OUT = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "ps-038a"
    / "campaign-proof-room-report.json"
)

# Existing accepted layer component files PS-038a must preserve (render
# alongside / cross-reference). The Campaign Proof Room component renders each
# of these; the smoke validates they remain present.
LAYER_COMPONENTS: tuple[tuple[str, Path], ...] = (
    ("PS-037 Trust Boundary", APPS_WEB_SRC / "TrustBoundaryLayer.tsx"),
    ("PS-037a Multimodal Proof", APPS_WEB_SRC / "MultimodalProofLayer.tsx"),
    ("PS-037b Transcript/Timestamp", APPS_WEB_SRC / "TranscriptTimestampEvidenceLayer.tsx"),
    ("PS-037c Voice/Audio Evidence", APPS_WEB_SRC / "VoiceAudioEvidenceChoiceLayer.tsx"),
    ("PS-037d Campaign Intelligence", APPS_WEB_SRC / "CampaignIntelligenceJudgeNarrativeLayer.tsx"),
    ("PS-037e Cloudflare Low-Cost Backbone", APPS_WEB_SRC / "CloudflareLowCostBackboneLayer.tsx"),
    ("PS-038 Production Readiness + Demo Mode", APPS_WEB_SRC / "ProductionReadinessDemoModeLayer.tsx"),
)


# The PS-038a implementation bundle: the canonical data module, the shared
# page component, and the proof doc. Required UI / boundary strings are
# validated across this bundle.
def bundle_files() -> tuple[Path, ...]:
    return (DATA_MODULE, COMPONENT, PROOF_DOC)


# Source files scanned for Cloudflare / DNS / Cloudflare-resource /
# Cloudflare-Pages-deploy / Cloudflare-Workers-deploy / Cloudflare-R2-read /
# Cloudflare-R2-write / Backblaze-B2-write / provider-call / model-call /
# B2-read / B2-write / broad-B2-scan code patterns. Includes the app files
# PS-038a touched so a newly-introduced live path cannot hide behind an
# additive render.
def provider_b2_scan_files() -> tuple[Path, ...]:
    return (DATA_MODULE, COMPONENT, APP_TSX, JUDGE_HOME)


# Files scanned for the bad lowercase-only hidden-flag command literal.
# Includes the smoke itself: the literal must never appear contiguously in any
# changed file, and the smoke builds the search needle from fragments so it
# does not self-trip.
def bad_literal_scan_files() -> tuple[Path, ...]:
    return (*bundle_files(), APP_TSX, JUDGE_HOME, SMOKE_SELF)


# Files scanned for forbidden affirmative overclaims. This is the ONLY
# context-aware overclaim scanner for PS-038a: it scans the bundle plus the app
# files PS-038a touched. It does not scan smoke guard fixtures as product
# claims.
def claim_scan_files() -> tuple[Path, ...]:
    return (*bundle_files(), APP_TSX, JUDGE_HOME)


# Required identity / positioning strings (spec section 21).
REQUIRED_IDENTITY_STRINGS: tuple[str, ...] = (
    "PS-038a",
    "Campaign Proof Room",
)

# Required Campaign Proof Room concept strings (spec section 10.2 / 21).
REQUIRED_CONCEPT_STRINGS: tuple[str, ...] = (
    "Campaign Proof Room",
    "campaign-level proof",
    "campaign evidence room",
    "judge-facing campaign room",
    "guided campaign proof trail",
    "recorded campaign artifact",
    "campaign artifact evidence",
    "campaign proof summary",
    "proof trail",
    "proof timeline",
    "evidence map",
    "inspection path",
    "judge demo path",
    "creator/marketing workflow utility",
    "campaign artifact reference",
    "campaign artifact digest",
    "campaign manifest evidence",
    "campaign archive evidence",
    "campaign rehydrate evidence",
    "campaign review evidence",
    "campaign approval evidence",
    "export pack evidence",
    "provenance passport evidence",
    "B2 evidence",
    "Genblaze manifest evidence",
    "rehydrate comparison evidence",
    "multimodal artifact evidence",
    "transcript/timestamp evidence",
    "voice/audio evidence",
    "campaign intelligence evidence",
    "Cloudflare backbone posture",
    "production readiness demo mode posture",
    "readiness posture",
    "demo mode posture",
    "local/static evidence",
    "checked-in evidence",
    "local verification",
    "live verification status",
    "disclosure boundary",
)

# Required honest unavailable / not-claimed / planned / deferred / proof-
# available / proof-unavailable state strings (spec section 10.6 / 21).
REQUIRED_DEFERRED_STATES: tuple[str, ...] = (
    "recorded proof",
    "local/static demo evidence",
    "checked-in campaign evidence",
    "proof available",
    "proof unavailable",
    "not claimed",
    "unknown",
    "planned",
    "deferred",
    "final submission packaging deferred to PS-039",
)

# Required de-escalation-pair strings (spec section 10.7 / 21).
REQUIRED_DEESCALATION_PAIRS: tuple[str, ...] = (
    "proof does not equal truth",
    "Campaign Proof Room does not equal campaign performance proof",
    "campaign narrative does not equal marketing effectiveness proof",
    "campaign intelligence evidence does not equal business outcome guarantee",
    "campaign artifact evidence does not equal legal authenticity",
    "local campaign evidence does not equal live provider availability",
    "checked-in campaign evidence does not equal live B2 availability",
    "Cloudflare backbone posture does not equal live Cloudflare availability",
    "demo mode posture does not equal production readiness",
    "review approval evidence does not equal legal approval",
    "provenance passport evidence does not equal C2PA authenticity",
    "manifest evidence does not equal semantic truth",
    "transcript/timestamp evidence does not equal transcript correctness",
    "voice/audio evidence does not equal speaker identity",
)

# Required negative-boundary strings (spec section 10.8 / 21).
REQUIRED_NEGATIVE_BOUNDARY: tuple[str, ...] = (
    "not campaign performance proof",
    "not marketing effectiveness proof",
    "not business outcome guarantee",
    "not semantic truth",
    "not legal authenticity",
    "not legal approval",
    "not human authorship",
    "not C2PA authenticity",
    "not production readiness",
    "not production security",
    "not production compliance",
    "not legal compliance",
    "not live deployment",
    "not provider availability",
    "not model availability",
    "not Backblaze B2 live availability",
    "not Cloudflare availability",
    "not uptime guarantee",
    "not cost guarantee",
    "not performance guarantee",
    "not cold-start performance guarantee",
    "not Object Lock",
    "not tamper-proof",
    "not browser-side B2 byte verification",
    "not content moderation correctness",
    "not transcript correctness",
    "not emotion truth",
    "not speaker identity",
    "not biometric identity",
    "not model output truth",
)

# Required posture / boundary strings preserved by this smoke (spec section 21).
REQUIRED_POSTURE_STRINGS: tuple[str, ...] = (
    "no deployment changes",
    "no env/secrets changes",
    "no render.yaml changes",
    "no requirements/dependency changes",
    "no Cloudflare API calls",
    "no DNS mutation",
    "no Cloudflare resource creation",
    "no Cloudflare Pages deployment",
    "no Cloudflare Workers deployment",
    "no Cloudflare R2 live reads",
    "no Cloudflare R2 writes",
    "no Backblaze B2 writes",
    "no provider calls",
    "no model calls",
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
    ("campaign_performance_proof", (
        "campaign performance proven",
        "campaign performance verified",
        "campaign performance confirmed",
        "proves campaign performance",
        "campaign performance is proven",
    )),
    ("marketing_effectiveness_proof", (
        "marketing effectiveness proven",
        "marketing effectiveness verified",
        "marketing effectiveness confirmed",
        "proves marketing effectiveness",
        "marketing effectiveness is proven",
    )),
    ("business_outcome_guarantee", (
        "business outcome guaranteed",
        "business outcome guarantee verified",
        "business outcome guarantee confirmed",
        "guarantees business outcome",
        "proves business outcome",
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
    ("legal_approval", (
        "legal approval proven",
        "legal approval verified",
        "legal approval confirmed",
        "proves legal approval",
        "legally approved",
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
    ("production_readiness", (
        "production readiness verified",
        "production ready",
        "production readiness proven",
        "production readiness confirmed",
        "is production-ready",
    )),
    ("production_security", (
        "production security verified",
        "production security proven",
        "enterprise-grade security",
    )),
    ("production_compliance", (
        "production compliance verified",
        "production compliance proven",
        "production compliance confirmed",
    )),
    ("legal_compliance", (
        "legal compliance verified",
        "legally compliant",
        "legal compliance proven",
    )),
    ("live_deployment", (
        "deployed to cloudflare",
        "deployment is live",
        "production deployment live",
        "publicly deployed and verified",
        "live cloudflare deployment verified",
    )),
    ("provider_availability", (
        "provider availability verified",
        "provider is available",
        "provider availability confirmed",
    )),
    ("model_availability", (
        "model availability verified",
        "model is available",
        "model availability confirmed",
    )),
    ("backblaze_b2_live_availability", (
        "live b2 availability verified",
        "live b2 verified",
        "live b2 availability confirmed",
    )),
    ("cloudflare_availability", (
        "cloudflare is available",
        "cloudflare availability verified",
        "cloudflare availability confirmed",
    )),
    ("uptime_guarantee", (
        "uptime guaranteed",
        "uptime guarantee verified",
        "guarantees uptime",
        "sla guaranteed",
    )),
    ("cost_guarantee", (
        "cost guaranteed",
        "cost guarantee verified",
        "guarantees cost",
        "cost is guaranteed",
    )),
    ("performance_guarantee", (
        "performance guaranteed",
        "performance guarantee verified",
        "guarantees performance",
    )),
    ("cold_start_performance_guarantee", (
        "cold-start performance guaranteed",
        "cold start performance verified",
        "cold-start performance guarantee confirmed",
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
    ("content_moderation_correctness", (
        "content moderation correctness verified",
        "content moderation correctness proven",
        "content moderation is correct",
    )),
    ("transcript_correctness", (
        "transcript correctness verified",
        "transcript correctness proven",
        "transcript is correct",
        "transcript verified as correct",
    )),
    ("emotion_truth", (
        "proves emotion truth",
        "emotion truth verified",
        "emotion truth proven",
        "emotion is true",
    )),
    ("speaker_identity", (
        "proves speaker identity",
        "speaker identity verified",
        "speaker identity confirmed",
        "identifies the speaker",
    )),
    ("biometric_identity", (
        "proves biometric identity",
        "biometric identity verified",
        "biometric identity confirmed",
        "identifies the biometric",
    )),
    ("model_output_truth", (
        "proves model output truth",
        "model output truth verified",
        "model output truth proven",
        "model output is true",
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
    "CF_API_TOKEN=",
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

# Validation needles used to detect a newly-introduced live Cloudflare API
# call path in the scanned app source. These are SCANNER NEEDLES (string
# constants), not executable calls: this smoke performs no network, Cloudflare,
# DNS, provider, model, or B2 behavior whatsoever. The needles are assembled
# from fragments where helpful so a naive regex audit scanning THIS smoke cannot
# self-trip.
FORBIDDEN_CLOUDFLARE_CALL_NEEDLES: tuple[str, ...] = (
    "api" + "." + "cloudflare" + ".com",
    "Cloudflare" + "Client",
    "cloudflare" + "_client",
    "Cloudflare" + "API" + "Client",
    "createCloudflare" + "Client",
)

FORBIDDEN_DNS_MUTATION_NEEDLES: tuple[str, ...] = (
    "create" + "_dns" + "_record",
    "patch" + "_dns" + "_record",
    "dns" + ".records.create",
    "cloudflare" + "_dns",
    "mutate" + "_dns",
    "createDns" + "Record",
)

FORBIDDEN_CLOUDFLARE_RESOURCE_NEEDLES: tuple[str, ...] = (
    "create" + "_cloudflare" + "_resource",
    "provision" + "_cloudflare",
    "create" + "_zone",
    "create" + "_worker",
    "create" + "_pages" + "_project",
    "createCloudflare" + "Resource",
)

FORBIDDEN_PAGES_DEPLOY_NEEDLES: tuple[str, ...] = (
    "wrangler" + " pages deploy",
    "pages" + ".deploy(",
    "deploy" + "_to" + "_cloudflare" + "_pages",
    "wrangler" + " pages publish",
    "deployCloudflare" + "Pages",
)

FORBIDDEN_WORKERS_DEPLOY_NEEDLES: tuple[str, ...] = (
    "wrangler" + " deploy",
    "wrangler" + " publish",
    "deploy" + "_worker",
    "workers" + ".deploy(",
    "deployCloudflare" + "Worker",
)

FORBIDDEN_R2_READ_NEEDLES: tuple[str, ...] = (
    "r2" + ".get",
    "r2" + "_get",
    "r2" + ".list",
    "list" + "_r2",
    "fetch" + "_r2",
)

FORBIDDEN_R2_WRITE_NEEDLES: tuple[str, ...] = (
    "r2" + ".put",
    "r2" + "_put",
    "put" + "_r2",
    "write" + "_to" + "_r2",
    "upload" + "_r2",
)

FORBIDDEN_B2_WRITE_NEEDLES: tuple[str, ...] = (
    "upload" + "_to" + "_b2",
    "b2" + ".put",
    "b2Put" + "Object",
    "put" + "_b2" + "_object",
    "uploadB2" + "Object",
    "write" + "_archive" + "_to" + "_b2",
)

FORBIDDEN_LIVE_CALL_NEEDLES: tuple[str, ...] = (
    "call" + "_provider",
    "fetchFrom" + "Provider",
    "requests" + ".post",
    "urlopen" + "(",
    "httpx" + ".post",
    "client" + ".post(",
)

FORBIDDEN_MODEL_CALL_NEEDLES: tuple[str, ...] = (
    "call" + "_model",
    "fetchFrom" + "Model",
    "generate" + "_content" + "(",
    "chat" + ".completions" + ".create",
    "model" + ".generate",
)

FORBIDDEN_B2_READ_NEEDLES: tuple[str, ...] = (
    "read" + "_archive" + "_from" + "_b2",
    "b2" + ".fetch",
    "b2Get" + "Object",
    "list" + "_b2" + "_objects",
    "fetchB2" + "Object",
)

FORBIDDEN_B2_SCAN_NEEDLES: tuple[str, ...] = (
    "list" + "_all" + "_b2" + "_objects",
    "scan" + "_b2" + "_bucket",
    "listObjects" + "V2",
    "b2" + "_list" + "_buckets",
    "enumerate" + "_b2" + "_prefix",
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
    PS-037a / PS-037b / PS-037c / PS-037d / PS-037e / PS-038).
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
        "CAMPAIGN_PROOF_ROOM_TITLE",
        "CAMPAIGN_PROOF_ROOM_ITEMS",
        "CAMPAIGN_PROOF_ROOM_DEESCALATION_PAIRS",
        "CAMPAIGN_PROOF_ROOM_NEGATIVE_BOUNDARY",
        "CAMPAIGN_PROOF_ROOM_PERSISTENT_STATEMENT",
        "CAMPAIGN_PROOF_ROOM_DEFERRED_STATES",
        "CAMPAIGN_PROOF_ROOM_MULTIMODAL_CROSS_REFERENCE",
        "CAMPAIGN_PROOF_ROOM_TRANSCRIPT_CROSS_REFERENCE",
        "CAMPAIGN_PROOF_ROOM_VOICE_AUDIO_CROSS_REFERENCE",
        "CAMPAIGN_PROOF_ROOM_CAMPAIGN_INTELLIGENCE_CROSS_REFERENCE",
        "CAMPAIGN_PROOF_ROOM_CLOUDFLARE_BACKBONE_CROSS_REFERENCE",
        "CAMPAIGN_PROOF_ROOM_PRODUCTION_READINESS_DEMO_MODE_CROSS_REFERENCE",
        "CAMPAIGN_PROOF_ROOM_TRUST_BOUNDARY_CROSS_REFERENCE",
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
        "export function CampaignProofRoom",
        '"page"',
        '"summary"',
        "CampaignProofRoomVariant",
        "campaignProofRoom",
    ):
        if needle not in text:
            problems.append(f"component missing reference to {needle!r}")
    return (not problems, problems)


def check_route_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not APP_TSX.is_file():
        return False, [f"missing {rel(APP_TSX)}"]
    text = read_text(APP_TSX)
    for needle in (
        "isCampaignProofRoomPath",
        "/campaign-proof-room",
        "<CampaignProofRoom variant=\"page\" />",
    ):
        if needle not in text:
            problems.append(f"App.tsx missing route contract string {needle!r}")
    # Dispatch must precede passport/review fallbacks (call sites in App()).
    dispatch_idx = text.find("if (isCampaignProofRoomPath())")
    passport_idx = text.find("if (publicPassportRunId)")
    review_idx = text.find("if (isReviewRoomPath()) return <ReviewRoom")
    if dispatch_idx < 0:
        problems.append("App.tsx missing CampaignProofRoom dispatch line")
    elif passport_idx >= 0 and dispatch_idx > passport_idx:
        problems.append(
            "CampaignProofRoom dispatch must precede the passport fallback"
        )
    elif review_idx >= 0 and dispatch_idx > review_idx:
        problems.append(
            "CampaignProofRoom dispatch must precede the review fallback"
        )
    return (not problems, problems)


def check_navigation_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not JUDGE_HOME.is_file():
        return False, [f"missing {rel(JUDGE_HOME)}"]
    text = read_text(JUDGE_HOME)
    if "/campaign-proof-room" not in text:
        problems.append("JudgeCockpitHome missing /campaign-proof-room link")
    if "Campaign Proof Room" not in text:
        problems.append("JudgeCockpitHome missing Campaign Proof Room label")
    if "href=\"/campaign-proof-room\"" not in text:
        problems.append("JudgeCockpitHome missing campaign-proof-room href")
    return (not problems, problems)


def check_layer_wired() -> tuple[bool, list[str]]:
    """The component reads only from the data module (no provider / B2)."""
    problems: list[str] = []
    if not COMPONENT.is_file():
        return False, [f"missing component {rel(COMPONENT)}"]
    text = read_text(COMPONENT)
    if 'from "./campaignProofRoom"' not in text:
        problems.append(
            "component does not import from ./campaignProofRoom"
        )
    return (not problems, problems)


def check_required_surfaces_preserve_layers() -> tuple[bool, list[str]]:
    """The accepted proof layer component files remain present and the Campaign
    Proof Room renders alongside each one."""
    problems: list[str] = []
    for name, path in LAYER_COMPONENTS:
        if not path.is_file():
            problems.append(
                f"accepted layer component missing: {name} ({rel(path)})"
            )
    if COMPONENT.is_file():
        text = read_text(COMPONENT)
        for name, _path in LAYER_COMPONENTS:
            comp = _path.stem
            if f"<{comp}" not in text:
                problems.append(
                    f"CampaignProofRoom does not render <{comp}> ({name})"
                )
    return (not problems, problems)


def check_trust_boundary_cross_reference() -> tuple[bool, list[str]]:
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
    problems: list[str] = []
    blob = _bundle_blob()
    if "PS-037a" not in blob:
        problems.append("bundle missing PS-037a cross-reference")
    if "Multimodal Proof Layer" not in blob:
        problems.append("bundle missing Multimodal Proof Layer cross-reference")
    if "multimodal proof cross-reference" not in blob:
        problems.append(
            "bundle missing multimodal proof cross-reference indicator"
        )
    if "MULTIMODAL_PROOF_MANIFEST" not in read_text(DATA_MODULE):
        problems.append(
            "data module does not import MULTIMODAL_PROOF_* cross-reference"
        )
    return (not problems, problems)


def check_transcript_timestamp_cross_reference() -> tuple[bool, list[str]]:
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


def check_campaign_intelligence_cross_reference() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = _bundle_blob()
    if "PS-037d" not in blob:
        problems.append("bundle missing PS-037d cross-reference")
    if "Campaign Intelligence" not in blob:
        problems.append(
            "bundle missing Campaign Intelligence cross-reference"
        )
    if "campaign intelligence cross-reference" not in blob:
        problems.append(
            "bundle missing campaign intelligence cross-reference indicator"
        )
    return (not problems, problems)


def check_cloudflare_backbone_cross_reference() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = _bundle_blob()
    if "PS-037e" not in blob:
        problems.append("bundle missing PS-037e cross-reference")
    if "Cloudflare Low-Cost Backbone" not in blob:
        problems.append(
            "bundle missing Cloudflare Low-Cost Backbone cross-reference"
        )
    if "Cloudflare low-cost backbone cross-reference" not in blob:
        problems.append(
            "bundle missing Cloudflare low-cost backbone cross-reference indicator"
        )
    return (not problems, problems)


def check_production_readiness_demo_mode_cross_reference() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = _bundle_blob()
    if "PS-038" not in blob:
        problems.append("bundle missing PS-038 cross-reference")
    if "Production Readiness + Demo Mode" not in blob:
        problems.append(
            "bundle missing Production Readiness + Demo Mode cross-reference"
        )
    if "production readiness demo mode cross-reference" not in blob:
        problems.append(
            "bundle missing production readiness demo mode cross-reference indicator"
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
                f"bundle missing required Campaign Proof Room concept "
                f"{needle!r}"
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
        "PS-038a",
        "Campaign Proof Room",
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
        ".campaign-proof-room-page",
        ".campaign-proof-room-summary",
    ):
        if needle not in text:
            problems.append(f"styles missing additive class {needle!r}")
    return (not problems, problems)


def _path_dirty(path: Path) -> bool:
    res = sl.run_command(
        ["git", "status", "--short", "--", str(path.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
    )
    return bool((res.stdout or "").strip())


def check_no_deployment_changes() -> tuple[bool, list[str]]:
    problems: list[str] = []
    try:
        entries = _git_status_entries()
    except sl.HarnessError as exc:
        return False, [f"could not run git status: {exc}"]
    for _tag, path in entries:
        path = path.strip().strip('"')
        if path == "render.yaml" or path.endswith("/render.yaml"):
            problems.append(f"deployment config left dirty: {path}")
    if RENDER_YAML.is_file() and _path_dirty(RENDER_YAML):
        problems.append(f"deployment config left dirty: {rel(RENDER_YAML)}")
    return (not problems, problems)


def check_no_env_secrets_changes() -> tuple[bool, list[str]]:
    problems: list[str] = []
    try:
        entries = _git_status_entries()
    except sl.HarnessError as exc:
        return False, [f"could not run git status: {exc}"]
    for _tag, path in entries:
        clean = path.strip().strip('"')
        if clean.startswith(".env"):
            problems.append(f"env/secrets file left dirty: {clean}")
    for env in ENV_FILES:
        if env.is_file() and _path_dirty(env):
            problems.append(f"env/secrets file left dirty: {rel(env)}")
    return (not problems, problems)


def check_no_render_yaml_changes() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if RENDER_YAML.is_file() and _path_dirty(RENDER_YAML):
        problems.append(f"render.yaml left dirty: {rel(RENDER_YAML)}")
    try:
        entries = _git_status_entries()
    except sl.HarnessError as exc:
        return False, [f"could not run git status: {exc}"]
    for _tag, path in entries:
        clean = path.strip().strip('"')
        if clean.endswith("render.yaml"):
            problems.append(f"render.yaml left dirty: {clean}")
    return (not problems, problems)


def check_no_requirements_dependency_changes() -> tuple[bool, list[str]]:
    problems: list[str] = []
    try:
        entries = _git_status_entries()
    except sl.HarnessError as exc:
        return False, [f"could not run git status: {exc}"]
    for _tag, path in entries:
        clean = path.strip().strip('"')
        if clean.endswith("requirements.txt"):
            problems.append(f"requirements file left dirty: {clean}")
        if clean.endswith("package.json") or clean.endswith("package-lock.json"):
            problems.append(f"dependency manifest left dirty: {clean}")
    for req in REQUIREMENTS_FILES:
        if req.is_file() and _path_dirty(req):
            problems.append(f"requirements file left dirty: {rel(req)}")
    return (not problems, problems)


def _scan_needles(
    paths: tuple[Path, ...],
    needles: tuple[str, ...],
    label: str,
) -> list[str]:
    problems: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in needles:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden {label} pattern {pattern!r}"
                )
    return problems


def check_no_cloudflare_api_calls() -> tuple[bool, list[str]]:
    return (
        not _scan_needles(
            provider_b2_scan_files(), FORBIDDEN_CLOUDFLARE_CALL_NEEDLES,
            "Cloudflare API call",
        ),
        _scan_needles(
            provider_b2_scan_files(), FORBIDDEN_CLOUDFLARE_CALL_NEEDLES,
            "Cloudflare API call",
        ),
    )


def check_no_dns_mutation() -> tuple[bool, list[str]]:
    p = _scan_needles(provider_b2_scan_files(), FORBIDDEN_DNS_MUTATION_NEEDLES, "DNS mutation")
    return (not p, p)


def check_no_cloudflare_resource_creation() -> tuple[bool, list[str]]:
    p = _scan_needles(provider_b2_scan_files(), FORBIDDEN_CLOUDFLARE_RESOURCE_NEEDLES, "Cloudflare resource creation")
    return (not p, p)


def check_no_cloudflare_pages_deployment() -> tuple[bool, list[str]]:
    p = _scan_needles(provider_b2_scan_files(), FORBIDDEN_PAGES_DEPLOY_NEEDLES, "Cloudflare Pages deployment")
    return (not p, p)


def check_no_cloudflare_workers_deployment() -> tuple[bool, list[str]]:
    p = _scan_needles(provider_b2_scan_files(), FORBIDDEN_WORKERS_DEPLOY_NEEDLES, "Cloudflare Workers deployment")
    return (not p, p)


def check_no_cloudflare_r2_live_reads() -> tuple[bool, list[str]]:
    p = _scan_needles(provider_b2_scan_files(), FORBIDDEN_R2_READ_NEEDLES, "Cloudflare R2 live read")
    return (not p, p)


def check_no_cloudflare_r2_writes() -> tuple[bool, list[str]]:
    p = _scan_needles(provider_b2_scan_files(), FORBIDDEN_R2_WRITE_NEEDLES, "Cloudflare R2 write")
    return (not p, p)


def check_no_backblaze_b2_writes() -> tuple[bool, list[str]]:
    p = _scan_needles(provider_b2_scan_files(), FORBIDDEN_B2_WRITE_NEEDLES, "Backblaze B2 write")
    return (not p, p)


def check_no_provider_calls() -> tuple[bool, list[str]]:
    p = _scan_needles(provider_b2_scan_files(), FORBIDDEN_LIVE_CALL_NEEDLES, "provider-call")
    return (not p, p)


def check_no_model_calls() -> tuple[bool, list[str]]:
    p = _scan_needles(provider_b2_scan_files(), FORBIDDEN_MODEL_CALL_NEEDLES, "model-call")
    return (not p, p)


def check_no_b2_reads() -> tuple[bool, list[str]]:
    p = _scan_needles(provider_b2_scan_files(), FORBIDDEN_B2_READ_NEEDLES, "B2 read")
    return (not p, p)


def check_no_b2_writes() -> tuple[bool, list[str]]:
    p = _scan_needles(provider_b2_scan_files(), FORBIDDEN_B2_WRITE_NEEDLES, "B2 write")
    return (not p, p)


def check_no_b2_scans() -> tuple[bool, list[str]]:
    p = _scan_needles(provider_b2_scan_files(), FORBIDDEN_B2_SCAN_NEEDLES, "broad B2 scan")
    return (not p, p)


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
    """No tracked evidence outside docs/evidence/ps-038a/ may be left dirty."""
    problems: list[str] = []
    try:
        entries = _git_status_entries()
    except sl.HarnessError as exc:
        return False, [f"could not run git status: {exc}"]
    for _tag, path in entries:
        path = path.strip().strip('"')
        if path.startswith("docs/evidence/") and not path.startswith(
            "docs/evidence/ps-038a/"
        ):
            problems.append(
                f"prior-slice evidence left dirty by PS-038a smoke: {path}"
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
        ("campaign_proof_room_data_module_present", check_data_module_present()),
        ("campaign_proof_room_component_present", check_component_present()),
        ("campaign_proof_room_route_present", check_route_present()),
        ("campaign_proof_room_navigation_present", check_navigation_present()),
        ("campaign_proof_room_layer_wired", check_layer_wired()),
        (
            "required_surfaces_preserve_layers",
            check_required_surfaces_preserve_layers(),
        ),
        ("trust_boundary_cross_reference_present", check_trust_boundary_cross_reference()),
        ("multimodal_proof_cross_reference_present", check_multimodal_proof_cross_reference()),
        ("transcript_timestamp_cross_reference_present", check_transcript_timestamp_cross_reference()),
        ("voice_audio_evidence_cross_reference_present", check_voice_audio_evidence_cross_reference()),
        ("campaign_intelligence_cross_reference_present", check_campaign_intelligence_cross_reference()),
        ("cloudflare_backbone_cross_reference_present", check_cloudflare_backbone_cross_reference()),
        ("production_readiness_demo_mode_cross_reference_present", check_production_readiness_demo_mode_cross_reference()),
        ("identity_strings_present", check_identity_strings()),
        ("concept_strings_present", check_concept_strings()),
        ("deferred_states_present", check_deferred_states()),
        ("deescalation_pairs_present", check_deescalation_pairs()),
        ("negative_boundary_strings_present", check_negative_boundary_strings()),
        ("posture_strings_in_smoke", check_posture_strings_in_smoke()),
        ("proof_doc_present", check_proof_doc_present()),
        ("styles_present", check_styles_present()),
        ("no_deployment_changes", check_no_deployment_changes()),
        ("no_env_secrets_changes", check_no_env_secrets_changes()),
        ("no_render_yaml_changes", check_no_render_yaml_changes()),
        ("no_requirements_dependency_changes", check_no_requirements_dependency_changes()),
        ("no_cloudflare_api_calls", check_no_cloudflare_api_calls()),
        ("no_dns_mutation", check_no_dns_mutation()),
        ("no_cloudflare_resource_creation", check_no_cloudflare_resource_creation()),
        ("no_cloudflare_pages_deployment", check_no_cloudflare_pages_deployment()),
        ("no_cloudflare_workers_deployment", check_no_cloudflare_workers_deployment()),
        ("no_cloudflare_r2_live_reads", check_no_cloudflare_r2_live_reads()),
        ("no_cloudflare_r2_writes", check_no_cloudflare_r2_writes()),
        ("no_backblaze_b2_writes", check_no_backblaze_b2_writes()),
        ("no_provider_calls", check_no_provider_calls()),
        ("no_model_calls", check_no_model_calls()),
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
        "PS-038a Campaign Proof Room", checks
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

    # Concept-string presence booleans, derived from the bundle blob.
    def _present(needle: str) -> bool:
        return needle in blob

    report: dict = {
        "ok": bool(all_pass),
        "slice_id": "ps038a",
        "campaign_proof_room_data_module_present": _passed("campaign_proof_room_data_module_present"),
        "campaign_proof_room_component_present": _passed("campaign_proof_room_component_present"),
        "campaign_proof_room_route_present": _passed("campaign_proof_room_route_present"),
        "campaign_proof_room_navigation_present": _passed("campaign_proof_room_navigation_present"),
        "campaign_level_proof_present": _present("campaign-level proof"),
        "campaign_evidence_room_present": _present("campaign evidence room"),
        "judge_facing_campaign_room_present": _present("judge-facing campaign room"),
        "guided_campaign_proof_trail_present": _present("guided campaign proof trail"),
        "recorded_campaign_artifact_present": _present("recorded campaign artifact"),
        "campaign_artifact_evidence_present": _present("campaign artifact evidence"),
        "campaign_proof_summary_present": _present("campaign proof summary"),
        "proof_trail_present": _present("proof trail"),
        "proof_timeline_present": _present("proof timeline"),
        "evidence_map_present": _present("evidence map"),
        "inspection_path_present": _present("inspection path"),
        "judge_demo_path_present": _present("judge demo path"),
        "creator_marketing_workflow_utility_present": _present("creator/marketing workflow utility"),
        "campaign_artifact_reference_present": _present("campaign artifact reference"),
        "campaign_artifact_digest_present": _present("campaign artifact digest"),
        "campaign_manifest_evidence_present": _present("campaign manifest evidence"),
        "campaign_archive_evidence_present": _present("campaign archive evidence"),
        "campaign_rehydrate_evidence_present": _present("campaign rehydrate evidence"),
        "campaign_review_evidence_present": _present("campaign review evidence"),
        "campaign_approval_evidence_present": _present("campaign approval evidence"),
        "export_pack_evidence_present": _present("export pack evidence"),
        "provenance_passport_evidence_present": _present("provenance passport evidence"),
        "b2_evidence_present": _present("B2 evidence"),
        "genblaze_manifest_evidence_present": _present("Genblaze manifest evidence"),
        "rehydrate_comparison_evidence_present": _present("rehydrate comparison evidence"),
        "multimodal_artifact_evidence_present": _present("multimodal artifact evidence"),
        "transcript_timestamp_evidence_present": _present("transcript/timestamp evidence"),
        "voice_audio_evidence_present": _present("voice/audio evidence"),
        "campaign_intelligence_evidence_present": _present("campaign intelligence evidence"),
        "cloudflare_backbone_posture_present": _present("Cloudflare backbone posture"),
        "production_readiness_demo_mode_posture_present": _present("production readiness demo mode posture"),
        "readiness_posture_present": _present("readiness posture"),
        "demo_mode_posture_present": _present("demo mode posture"),
        "local_static_evidence_present": _present("local/static evidence"),
        "checked_in_evidence_present": _present("checked-in evidence"),
        "local_verification_status_present": _present("local verification"),
        "live_verification_status_present": _present("live verification status"),
        "proof_available_status_present": _present("proof available"),
        "proof_unavailable_status_present": _present("proof unavailable"),
        "not_claimed_status_present": _present("not claimed"),
        "unknown_status_present": _present("unknown"),
        "planned_status_present": _present("planned"),
        "deferred_status_present": _present("deferred"),
        "disclosure_boundary_present": _present("disclosure boundary"),
        "final_submission_packaging_deferred_to_ps039_present": _present("final submission packaging deferred to PS-039"),
        "proof_does_not_equal_truth_present": _present("proof does not equal truth"),
        "campaign_proof_room_does_not_equal_campaign_performance_proof_present": _present("Campaign Proof Room does not equal campaign performance proof"),
        "campaign_narrative_does_not_equal_marketing_effectiveness_proof_present": _present("campaign narrative does not equal marketing effectiveness proof"),
        "campaign_intelligence_evidence_does_not_equal_business_outcome_guarantee_present": _present("campaign intelligence evidence does not equal business outcome guarantee"),
        "campaign_artifact_evidence_does_not_equal_legal_authenticity_present": _present("campaign artifact evidence does not equal legal authenticity"),
        "local_campaign_evidence_does_not_equal_live_provider_availability_present": _present("local campaign evidence does not equal live provider availability"),
        "checked_in_campaign_evidence_does_not_equal_live_b2_availability_present": _present("checked-in campaign evidence does not equal live B2 availability"),
        "cloudflare_backbone_posture_does_not_equal_live_cloudflare_availability_present": _present("Cloudflare backbone posture does not equal live Cloudflare availability"),
        "demo_mode_posture_does_not_equal_production_readiness_present": _present("demo mode posture does not equal production readiness"),
        "review_approval_evidence_does_not_equal_legal_approval_present": _present("review approval evidence does not equal legal approval"),
        "provenance_passport_evidence_does_not_equal_c2pa_authenticity_present": _present("provenance passport evidence does not equal C2PA authenticity"),
        "manifest_evidence_does_not_equal_semantic_truth_present": _present("manifest evidence does not equal semantic truth"),
        "transcript_timestamp_evidence_does_not_equal_transcript_correctness_present": _present("transcript/timestamp evidence does not equal transcript correctness"),
        "voice_audio_evidence_does_not_equal_speaker_identity_present": _present("voice/audio evidence does not equal speaker identity"),
        "no_campaign_performance_proof_claim": _no_claim("campaign_performance_proof"),
        "no_marketing_effectiveness_proof_claim": _no_claim("marketing_effectiveness_proof"),
        "no_business_outcome_guarantee_claim": _no_claim("business_outcome_guarantee"),
        "no_semantic_truth_claim": _no_claim("semantic_truth"),
        "no_legal_authenticity_claim": _no_claim("legal_authenticity"),
        "no_legal_approval_claim": _no_claim("legal_approval"),
        "no_human_authorship_claim": _no_claim("human_authorship"),
        "no_c2pa_authenticity_claim": _no_claim("c2pa_authenticity"),
        "no_production_readiness_claim": _no_claim("production_readiness"),
        "no_production_security_claim": _no_claim("production_security"),
        "no_production_compliance_claim": _no_claim("production_compliance"),
        "no_legal_compliance_claim": _no_claim("legal_compliance"),
        "no_live_deployment_claim": _no_claim("live_deployment"),
        "no_provider_availability_claim": _no_claim("provider_availability"),
        "no_model_availability_claim": _no_claim("model_availability"),
        "no_backblaze_b2_live_availability_claim": _no_claim("backblaze_b2_live_availability"),
        "no_cloudflare_availability_claim": _no_claim("cloudflare_availability"),
        "no_uptime_guarantee_claim": _no_claim("uptime_guarantee"),
        "no_cost_guarantee_claim": _no_claim("cost_guarantee"),
        "no_performance_guarantee_claim": _no_claim("performance_guarantee"),
        "no_cold_start_performance_guarantee_claim": _no_claim("cold_start_performance_guarantee"),
        "no_object_lock_claim": _no_claim("object_lock"),
        "no_tamper_proof_claim": _no_claim("tamper_proof"),
        "no_browser_side_b2_byte_verification_claim": _no_claim("browser_side_b2_byte_verification"),
        "no_content_moderation_correctness_claim": _no_claim("content_moderation_correctness"),
        "no_transcript_correctness_claim": _no_claim("transcript_correctness"),
        "no_emotion_truth_claim": _no_claim("emotion_truth"),
        "no_speaker_identity_claim": _no_claim("speaker_identity"),
        "no_biometric_identity_claim": _no_claim("biometric_identity"),
        "no_model_output_truth_claim": _no_claim("model_output_truth"),
        "no_deployment_changes": _passed("no_deployment_changes"),
        "no_env_secrets_changes": _passed("no_env_secrets_changes"),
        "no_render_yaml_changes": _passed("no_render_yaml_changes"),
        "no_requirements_dependency_changes": _passed("no_requirements_dependency_changes"),
        "no_cloudflare_api_calls": _passed("no_cloudflare_api_calls"),
        "no_dns_mutation": _passed("no_dns_mutation"),
        "no_cloudflare_resource_creation": _passed("no_cloudflare_resource_creation"),
        "no_cloudflare_pages_deployment": _passed("no_cloudflare_pages_deployment"),
        "no_cloudflare_workers_deployment": _passed("no_cloudflare_workers_deployment"),
        "no_cloudflare_r2_live_reads": _passed("no_cloudflare_r2_live_reads"),
        "no_cloudflare_r2_writes": _passed("no_cloudflare_r2_writes"),
        "no_backblaze_b2_writes": _passed("no_backblaze_b2_writes"),
        "no_provider_calls": _passed("no_provider_calls"),
        "no_model_calls": _passed("no_model_calls"),
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
        "evidence_dir": "docs/evidence/ps-038a/",
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
