#!/usr/bin/env python3
"""PS-037e Cloudflare Low-Cost Backbone -- smoke / validation.

This smoke validates ONLY the PS-037e slice. It is local / static by default:
it does not start a browser, does not run the frontend typecheck / build, does
not call Cloudflare, does not mutate DNS, does not create any Cloudflare
resource, does not deploy Cloudflare Pages, does not deploy Cloudflare Workers,
does not read or write any Cloudflare R2 object, does not write any Backblaze B2
object, does not call any provider, does not read or write any B2 object, does
not perform a broad B2 scan, does not call the central regression gate, and does
not recursively execute another feature smoke. Default behavior is non-mutating
local validation (``--check-only``); no evidence file is written unless
``--write-evidence`` is explicit.

Standard flags (PS-034B / PS-035D feature-smoke contract):

    --check-only      default; non-mutating local validation; writes nothing
    --write-evidence  writes only docs/evidence/ps-037e/ evidence
    --no-frontend     skip the frontend typecheck/build (always skipped; a
                      feature smoke never runs the frontend)

Truth boundary: this smoke validates that the PS-037e Cloudflare Low-Cost
Backbone layer is honest and consistent. ProofStudio proves what the pipeline
recorded. The layer is not live deployment, not production readiness, not
production security, not production compliance, not legal compliance, not uptime
guarantee, not cost guarantee, not performance guarantee, not cold-start
mitigation implementation, not DNS ownership, not Cloudflare resource
existence, not Cloudflare Pages availability, not Cloudflare Workers
availability, not Cloudflare R2 availability, not Backblaze B2 live
availability, not Object Lock, not tamper-proof, not browser-side B2 byte
verification, not semantic truth, not legal authenticity, not human authorship,
and not C2PA authenticity.

Posture contract strings preserved by this smoke: no Cloudflare API calls, no
DNS mutation, no Cloudflare resource creation, no Cloudflare Pages deployment,
no Cloudflare Workers deployment, no Cloudflare R2 live reads, no Cloudflare R2
writes, no Backblaze B2 writes, no provider calls, no live B2 reads, no B2
writes, no broad B2 scans, no recursive smokes, hidden Git flags h, line[0].

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
DATA_MODULE = APPS_WEB_SRC / "cloudflareLowCostBackbone.ts"
COMPONENT = APPS_WEB_SRC / "CloudflareLowCostBackboneLayer.tsx"
SMOKE_SELF = (
    REPO_ROOT
    / "scripts"
    / "ps037e_cloudflare_low_cost_backbone_smoke.py"
)
PROOF_DOC = (
    REPO_ROOT
    / "docs"
    / "ps-037e-cloudflare-low-cost-backbone-proof.md"
)
AGENTS_MD = REPO_ROOT / "AGENTS.md"
STYLES = APPS_WEB_SRC / "styles.css"
EVIDENCE_OUT = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "ps-037e"
    / "cloudflare-low-cost-backbone-report.json"
)

# Required core proof surfaces (spec section 10.3). Each surface that is
# present in this repo must import and render the shared Cloudflare low-cost
# backbone layer.
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


# The PS-037e implementation bundle: the canonical data module, the shared
# component, and the proof doc. Required UI / boundary strings are validated
# across this bundle.
def bundle_files() -> tuple[Path, ...]:
    return (DATA_MODULE, COMPONENT, PROOF_DOC)


# Source files scanned for Cloudflare / DNS / Cloudflare-resource /
# Cloudflare-Pages-deploy / Cloudflare-Workers-deploy / Cloudflare-R2-read /
# Cloudflare-R2-write / Backblaze-B2-write / provider-call / B2-read /
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
# context-aware overclaim scanner for PS-037e: it scans the bundle plus the
# surfaces that render the layer. It does not scan smoke guard fixtures as
# product claims.
def claim_scan_files() -> tuple[Path, ...]:
    surfaces = tuple(p for _name, p in REQUIRED_SURFACES if p.is_file())
    return (*bundle_files(), *surfaces)


# Required identity / positioning strings (spec section 21).
REQUIRED_IDENTITY_STRINGS: tuple[str, ...] = (
    "PS-037e",
    "Cloudflare Low-Cost Backbone",
    "Cloudflare",
)

# Required Cloudflare low-cost backbone concept strings (spec section 10.2 / 21).
REQUIRED_CONCEPT_STRINGS: tuple[str, ...] = (
    "low-cost backbone",
    "infrastructure posture",
    "deployment readiness evidence",
    "Cloudflare provider label",
    "Cloudflare Pages plan",
    "Cloudflare Workers plan",
    "Cloudflare R2 plan",
    "Backblaze B2 system of record",
    "B2 archive remains system of record",
    "Genblaze manifest evidence remains system of record",
    "backbone status",
    "deployment status",
    "Cloudflare resource status",
    "DNS status",
    "cost-control status",
    "cold-start mitigation status",
    "production readiness status",
    "trust boundary cross-reference",
    "multimodal proof cross-reference",
    "transcript/timestamp cross-reference",
    "voice/audio evidence cross-reference",
    "campaign intelligence cross-reference",
    "local verification",
    "live verification status",
    "disclosure boundary",
    "not claimed",
    "unknown",
    "planned",
)

# Required honest unavailable / not-claimed / planned / deferred state strings
# (spec section 10.6 / 21).
REQUIRED_DEFERRED_STATES: tuple[str, ...] = (
    "local/demo evidence",
    "live Cloudflare evidence not available",
    "Cloudflare deployment not available",
    "Cloudflare resource evidence not available",
    "DNS evidence not available",
    "production security evidence not available",
    "production compliance evidence not available",
    "cold-start mitigation deferred to PS-038",
    "production readiness deferred to PS-038",
    "final submission packaging deferred to PS-039",
)

# Required de-escalation-pair strings (spec section 10.7 / 21).
REQUIRED_DEESCALATION_PAIRS: tuple[str, ...] = (
    "proof does not equal truth",
    "Cloudflare label does not equal live Cloudflare availability",
    "backbone plan does not equal live deployment",
    "deployment readiness does not equal production readiness",
    "low-cost posture does not equal cost guarantee",
    "infrastructure posture does not equal production security",
    "Cloudflare R2 plan does not equal live R2 availability",
    "local backbone evidence does not equal live Cloudflare availability",
    "demo/golden backbone evidence does not equal production security",
)

# Required negative-boundary strings (spec section 10.8 / 21).
REQUIRED_NEGATIVE_BOUNDARY: tuple[str, ...] = (
    "not live deployment",
    "not production readiness",
    "not production security",
    "not production compliance",
    "not legal compliance",
    "not uptime guarantee",
    "not cost guarantee",
    "not performance guarantee",
    "not cold-start mitigation implementation",
    "not DNS ownership",
    "not Cloudflare resource existence",
    "not Cloudflare Pages availability",
    "not Cloudflare Workers availability",
    "not Cloudflare R2 availability",
    "not Backblaze B2 live availability",
    "not Object Lock",
    "not tamper-proof",
    "not browser-side B2 byte verification",
    "not semantic truth",
    "not legal authenticity",
    "not human authorship",
    "not C2PA authenticity",
    "not campaign performance prediction",
    "not marketing effectiveness proof",
    "not model output truth",
)

# Required posture / boundary strings preserved by this smoke (spec section 21).
REQUIRED_POSTURE_STRINGS: tuple[str, ...] = (
    "no Cloudflare API calls",
    "no DNS mutation",
    "no Cloudflare resource creation",
    "no Cloudflare Pages deployment",
    "no Cloudflare Workers deployment",
    "no Cloudflare R2 live reads",
    "no Cloudflare R2 writes",
    "no Backblaze B2 writes",
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
    ("live_deployment", (
        "deployed to cloudflare",
        "cloudflare deployment is live",
        "deployment is live",
        "production deployment live",
        "publicly deployed and verified",
        "live cloudflare deployment verified",
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
        "production security is verified",
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
    ("cold_start_mitigation_implementation", (
        "cold-start mitigation implemented",
        "cold start mitigation verified",
        "cold-start mitigation implemented and verified",
    )),
    ("dns_ownership", (
        "owns the dns",
        "dns ownership verified",
        "dns ownership confirmed",
        "we own the domain",
    )),
    ("cloudflare_resource_existence", (
        "cloudflare resource created",
        "cloudflare resource exists",
        "cloudflare resource verified",
    )),
    ("cloudflare_pages_availability", (
        "cloudflare pages available",
        "cloudflare pages deployed",
        "cloudflare pages availability verified",
        "cloudflare pages live",
    )),
    ("cloudflare_workers_availability", (
        "cloudflare workers available",
        "cloudflare workers deployed",
        "cloudflare workers availability verified",
        "cloudflare workers live",
    )),
    ("cloudflare_r2_availability", (
        "cloudflare r2 available",
        "r2 bucket created",
        "cloudflare r2 availability verified",
        "r2 is live",
    )),
    ("backblaze_b2_live_availability", (
        "live b2 availability verified",
        "live b2 verified",
        "live b2 availability confirmed",
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
# DNS, provider, or B2 behavior whatsoever. The needles are assembled from
# fragments where useful so a naive regex audit scanning THIS smoke cannot
# self-trip.
FORBIDDEN_CLOUDFLARE_CALL_NEEDLES: tuple[str, ...] = (
    "api" + "." + "cloudflare" + ".com",
    "Cloudflare" + "Client",
    "cloudflare" + "_client",
    "Cloudflare" + "API" + "Client",
    "createCloudflare" + "Client",
)

# Validation needles used to detect a newly-introduced DNS mutation path.
FORBIDDEN_DNS_MUTATION_NEEDLES: tuple[str, ...] = (
    "create" + "_dns" + "_record",
    "patch" + "_dns" + "_record",
    "dns" + ".records.create",
    "cloudflare" + "_dns",
    "mutate" + "_dns",
    "createDns" + "Record",
)

# Validation needles used to detect a newly-introduced Cloudflare resource
# creation path.
FORBIDDEN_CLOUDFLARE_RESOURCE_NEEDLES: tuple[str, ...] = (
    "create" + "_cloudflare" + "_resource",
    "provision" + "_cloudflare",
    "create" + "_zone",
    "create" + "_worker",
    "create" + "_pages" + "_project",
    "createCloudflare" + "Resource",
)

# Validation needles used to detect a newly-introduced Cloudflare Pages
# deployment path.
FORBIDDEN_PAGES_DEPLOY_NEEDLES: tuple[str, ...] = (
    "wrangler" + " pages deploy",
    "pages" + ".deploy(",
    "deploy" + "_to" + "_cloudflare" + "_pages",
    "wrangler" + " pages publish",
    "deployCloudflare" + "Pages",
)

# Validation needles used to detect a newly-introduced Cloudflare Workers
# deployment path.
FORBIDDEN_WORKERS_DEPLOY_NEEDLES: tuple[str, ...] = (
    "wrangler" + " deploy",
    "wrangler" + " publish",
    "deploy" + "_worker",
    "workers" + ".deploy(",
    "deployCloudflare" + "Worker",
)

# Validation needles used to detect a newly-introduced Cloudflare R2 live read
# path.
FORBIDDEN_R2_READ_NEEDLES: tuple[str, ...] = (
    "r2" + ".get",
    "r2" + "_get",
    "r2" + ".list",
    "list" + "_r2",
    "fetch" + "_r2",
)

# Validation needles used to detect a newly-introduced Cloudflare R2 write
# path.
FORBIDDEN_R2_WRITE_NEEDLES: tuple[str, ...] = (
    "r2" + ".put",
    "r2" + "_put",
    "put" + "_r2",
    "write" + "_to" + "_r2",
    "upload" + "_r2",
)

# Validation needles used to detect a newly-introduced Backblaze B2 write path.
FORBIDDEN_B2_WRITE_NEEDLES: tuple[str, ...] = (
    "upload" + "_to" + "_b2",
    "b2" + ".put",
    "b2Put" + "Object",
    "put" + "_b2" + "_object",
    "uploadB2" + "Object",
    "write" + "_archive" + "_to" + "_b2",
)

# Validation needles used to detect a newly-introduced live provider-call
# path.
FORBIDDEN_LIVE_CALL_NEEDLES: tuple[str, ...] = (
    "call" + "_provider",
    "fetchFrom" + "Provider",
    "requests" + ".post",
    "urlopen" + "(",
    "httpx" + ".post",
    "client" + ".post(",
)

# Validation needles used to detect a newly-introduced live B2 object read
# path.
FORBIDDEN_B2_READ_NEEDLES: tuple[str, ...] = (
    "read" + "_archive" + "_from" + "_b2",
    "b2" + ".fetch",
    "b2Get" + "Object",
    "list" + "_b2" + "_objects",
    "fetchB2" + "Object",
    "fetch" + "(",
)

# Validation needles used to detect a newly-introduced broad B2 scan path.
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
    PS-037a / PS-037b / PS-037c / PS-037d).
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
        "CLOUDFLARE_LOW_COST_BACKBONE_TITLE",
        "CLOUDFLARE_LOW_COST_BACKBONE_ITEMS",
        "CLOUDFLARE_LOW_COST_BACKBONE_DEESCALATION_PAIRS",
        "CLOUDFLARE_LOW_COST_BACKBONE_NEGATIVE_BOUNDARY",
        "CLOUDFLARE_LOW_COST_BACKBONE_PERSISTENT_STATEMENT",
        "CLOUDFLARE_LOW_COST_BACKBONE_DEFERRED_STATES",
        "CLOUDFLARE_LOW_COST_BACKBONE_MULTIMODAL_CROSS_REFERENCE",
        "CLOUDFLARE_LOW_COST_BACKBONE_TRANSCRIPT_CROSS_REFERENCE",
        "CLOUDFLARE_LOW_COST_BACKBONE_VOICE_AUDIO_CROSS_REFERENCE",
        "CLOUDFLARE_LOW_COST_BACKBONE_CAMPAIGN_INTELLIGENCE_CROSS_REFERENCE",
        "CLOUDFLARE_LOW_COST_BACKBONE_TRUST_BOUNDARY_CROSS_REFERENCE",
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
        "export function CloudflareLowCostBackboneLayer",
        '"panel"',
        '"summary"',
        "CloudflareLowCostBackboneLayerVariant",
        "cloudflareLowCostBackbone",
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
    if 'from "./cloudflareLowCostBackbone"' not in text:
        problems.append(
            "component does not import from ./cloudflareLowCostBackbone"
        )
    return (not problems, problems)


def check_required_surfaces_have_cloudflare_backbone_layer() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for name, path in REQUIRED_SURFACES:
        if not path.is_file():
            # A required surface absent from this repo is not a failure; the
            # contract only applies where the surface is present.
            continue
        text = read_text(path)
        if "CloudflareLowCostBackboneLayer" not in text:
            problems.append(
                f"{name} ({rel(path)}) does not reference "
                f"CloudflareLowCostBackboneLayer"
            )
        if "<CloudflareLowCostBackboneLayer" not in text:
            problems.append(
                f"{name} ({rel(path)}) does not render "
                f"<CloudflareLowCostBackboneLayer"
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


def check_campaign_intelligence_cross_reference() -> tuple[bool, list[str]]:
    """The layer integrates / cross-references the PS-037d Gemini Campaign
    Intelligence / Judge Narrative layer."""
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
                f"bundle missing required cloudflare backbone concept {needle!r}"
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
        "PS-037e",
        "Cloudflare Low-Cost Backbone",
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
        ".cloudflare-low-cost-backbone-layer-panel",
        ".cloudflare-low-cost-backbone-layer-summary",
    ):
        if needle not in text:
            problems.append(f"styles missing additive class {needle!r}")
    return (not problems, problems)


def check_no_cloudflare_api_calls() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_CLOUDFLARE_CALL_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden Cloudflare API call pattern "
                    f"{pattern!r}"
                )
    return (not problems, problems)


def check_no_dns_mutation() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_DNS_MUTATION_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden DNS mutation pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_cloudflare_resource_creation() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_CLOUDFLARE_RESOURCE_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden Cloudflare resource creation "
                    f"pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_cloudflare_pages_deployment() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_PAGES_DEPLOY_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden Cloudflare Pages deployment "
                    f"pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_cloudflare_workers_deployment() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_WORKERS_DEPLOY_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden Cloudflare Workers deployment "
                    f"pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_cloudflare_r2_live_reads() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_R2_READ_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden Cloudflare R2 live read "
                    f"pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_cloudflare_r2_writes() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_R2_WRITE_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden Cloudflare R2 write pattern "
                    f"{pattern!r}"
                )
    return (not problems, problems)


def check_no_backblaze_b2_writes() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in provider_b2_scan_files():
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_B2_WRITE_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden Backblaze B2 write pattern "
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
    """No tracked evidence outside docs/evidence/ps-037e/ may be left dirty."""
    problems: list[str] = []
    try:
        entries = _git_status_entries()
    except sl.HarnessError as exc:
        return False, [f"could not run git status: {exc}"]
    for _tag, path in entries:
        path = path.strip().strip('"')
        if path.startswith("docs/evidence/") and not path.startswith(
            "docs/evidence/ps-037e/"
        ):
            problems.append(
                f"prior-slice evidence left dirty by PS-037e smoke: {path}"
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
        ("cloudflare_backbone_data_module_present", check_data_module_present()),
        ("cloudflare_backbone_component_present", check_component_present()),
        ("cloudflare_backbone_layer_present", check_layer_wired()),
        (
            "required_surfaces_have_cloudflare_backbone_layer",
            check_required_surfaces_have_cloudflare_backbone_layer(),
        ),
        ("trust_boundary_cross_reference_present", check_trust_boundary_cross_reference()),
        ("multimodal_proof_cross_reference_present", check_multimodal_proof_cross_reference()),
        ("transcript_timestamp_cross_reference_present", check_transcript_timestamp_cross_reference()),
        ("voice_audio_evidence_cross_reference_present", check_voice_audio_evidence_cross_reference()),
        ("campaign_intelligence_cross_reference_present", check_campaign_intelligence_cross_reference()),
        ("identity_strings_present", check_identity_strings()),
        ("concept_strings_present", check_concept_strings()),
        ("deferred_states_present", check_deferred_states()),
        ("deescalation_pairs_present", check_deescalation_pairs()),
        ("negative_boundary_strings_present", check_negative_boundary_strings()),
        ("posture_strings_in_smoke", check_posture_strings_in_smoke()),
        ("proof_doc_present", check_proof_doc_present()),
        ("styles_present", check_styles_present()),
        ("no_cloudflare_api_calls", check_no_cloudflare_api_calls()),
        ("no_dns_mutation", check_no_dns_mutation()),
        ("no_cloudflare_resource_creation", check_no_cloudflare_resource_creation()),
        ("no_cloudflare_pages_deployment", check_no_cloudflare_pages_deployment()),
        ("no_cloudflare_workers_deployment", check_no_cloudflare_workers_deployment()),
        ("no_cloudflare_r2_live_reads", check_no_cloudflare_r2_live_reads()),
        ("no_cloudflare_r2_writes", check_no_cloudflare_r2_writes()),
        ("no_backblaze_b2_writes", check_no_backblaze_b2_writes()),
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
        "PS-037e Cloudflare Low-Cost Backbone", checks
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
        "slice_id": "ps037e",
        "cloudflare_backbone_component_present": _passed("cloudflare_backbone_component_present"),
        "cloudflare_backbone_data_module_present": _passed("cloudflare_backbone_data_module_present"),
        "cloudflare_backbone_layer_present": _passed("cloudflare_backbone_layer_present"),
        "required_surfaces_have_cloudflare_backbone_layer": _passed(
            "required_surfaces_have_cloudflare_backbone_layer"
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
        "campaign_intelligence_cross_reference_present": _passed(
            "campaign_intelligence_cross_reference_present"
        ),
        "cloudflare_label_present": "Cloudflare" in blob,
        "low_cost_backbone_present": "low-cost backbone" in blob,
        "infrastructure_posture_present": "infrastructure posture" in blob,
        "deployment_readiness_evidence_present": "deployment readiness evidence" in blob,
        "cloudflare_pages_plan_present": "Cloudflare Pages plan" in blob,
        "cloudflare_workers_plan_present": "Cloudflare Workers plan" in blob,
        "cloudflare_r2_plan_present": "Cloudflare R2 plan" in blob,
        "backblaze_b2_system_of_record_present": "Backblaze B2 system of record" in blob,
        "b2_archive_remains_system_of_record_present": "B2 archive remains system of record" in blob,
        "genblaze_manifest_evidence_remains_system_of_record_present": "Genblaze manifest evidence remains system of record" in blob,
        "backbone_status_present": "backbone status" in blob,
        "deployment_status_present": "deployment status" in blob,
        "cloudflare_resource_status_present": "Cloudflare resource status" in blob,
        "dns_status_present": "DNS status" in blob,
        "cost_control_status_present": "cost-control status" in blob,
        "cold_start_mitigation_status_present": "cold-start mitigation status" in blob,
        "production_readiness_status_present": "production readiness status" in blob,
        "local_verification_status_present": "local verification" in blob,
        "live_verification_status_present": "live verification status" in blob,
        "disclosure_boundary_present": "disclosure boundary" in blob,
        "not_claimed_status_present": "not claimed" in blob,
        "unknown_status_present": "unknown" in blob,
        "planned_status_present": "planned" in blob,
        "local_demo_evidence_present": "local/demo evidence" in blob,
        "live_cloudflare_evidence_not_available_present": "live Cloudflare evidence not available" in blob,
        "cloudflare_deployment_not_available_present": "Cloudflare deployment not available" in blob,
        "cloudflare_resource_evidence_not_available_present": "Cloudflare resource evidence not available" in blob,
        "dns_evidence_not_available_present": "DNS evidence not available" in blob,
        "production_security_evidence_not_available_present": "production security evidence not available" in blob,
        "production_compliance_evidence_not_available_present": "production compliance evidence not available" in blob,
        "cold_start_mitigation_deferred_to_ps038_present": "cold-start mitigation deferred to PS-038" in blob,
        "production_readiness_deferred_to_ps038_present": "production readiness deferred to PS-038" in blob,
        "final_submission_packaging_deferred_to_ps039_present": "final submission packaging deferred to PS-039" in blob,
        "proof_does_not_equal_truth_present": "proof does not equal truth" in blob,
        "cloudflare_label_does_not_equal_live_cloudflare_availability_present": "Cloudflare label does not equal live Cloudflare availability" in blob,
        "backbone_plan_does_not_equal_live_deployment_present": "backbone plan does not equal live deployment" in blob,
        "deployment_readiness_does_not_equal_production_readiness_present": "deployment readiness does not equal production readiness" in blob,
        "low_cost_posture_does_not_equal_cost_guarantee_present": "low-cost posture does not equal cost guarantee" in blob,
        "infrastructure_posture_does_not_equal_production_security_present": "infrastructure posture does not equal production security" in blob,
        "cloudflare_r2_plan_does_not_equal_live_r2_availability_present": "Cloudflare R2 plan does not equal live R2 availability" in blob,
        "local_backbone_evidence_does_not_equal_live_cloudflare_availability_present": "local backbone evidence does not equal live Cloudflare availability" in blob,
        "demo_golden_backbone_evidence_does_not_equal_production_security_present": "demo/golden backbone evidence does not equal production security" in blob,
        "no_live_deployment_claim": _no_claim("live_deployment"),
        "no_production_readiness_claim": _no_claim("production_readiness"),
        "no_production_security_claim": _no_claim("production_security"),
        "no_production_compliance_claim": _no_claim("production_compliance"),
        "no_legal_compliance_claim": _no_claim("legal_compliance"),
        "no_uptime_guarantee_claim": _no_claim("uptime_guarantee"),
        "no_cost_guarantee_claim": _no_claim("cost_guarantee"),
        "no_performance_guarantee_claim": _no_claim("performance_guarantee"),
        "no_cold_start_mitigation_implementation_claim": _no_claim("cold_start_mitigation_implementation"),
        "no_dns_ownership_claim": _no_claim("dns_ownership"),
        "no_cloudflare_resource_existence_claim": _no_claim("cloudflare_resource_existence"),
        "no_cloudflare_pages_availability_claim": _no_claim("cloudflare_pages_availability"),
        "no_cloudflare_workers_availability_claim": _no_claim("cloudflare_workers_availability"),
        "no_cloudflare_r2_availability_claim": _no_claim("cloudflare_r2_availability"),
        "no_backblaze_b2_live_availability_claim": _no_claim("backblaze_b2_live_availability"),
        "no_object_lock_claim": _no_claim("object_lock"),
        "no_tamper_proof_claim": _no_claim("tamper_proof"),
        "no_browser_side_b2_byte_verification_claim": _no_claim("browser_side_b2_byte_verification"),
        "no_semantic_truth_claim": _no_claim("semantic_truth"),
        "no_legal_authenticity_claim": _no_claim("legal_authenticity"),
        "no_human_authorship_claim": _no_claim("human_authorship"),
        "no_c2pa_authenticity_claim": _no_claim("c2pa_authenticity"),
        "no_campaign_performance_prediction_claim": _no_claim("campaign_performance_prediction"),
        "no_marketing_effectiveness_proof_claim": _no_claim("marketing_effectiveness_proof"),
        "no_model_output_truth_claim": _no_claim("model_output_truth"),
        "no_cloudflare_api_calls": _passed("no_cloudflare_api_calls"),
        "no_dns_mutation": _passed("no_dns_mutation"),
        "no_cloudflare_resource_creation": _passed("no_cloudflare_resource_creation"),
        "no_cloudflare_pages_deployment": _passed("no_cloudflare_pages_deployment"),
        "no_cloudflare_workers_deployment": _passed("no_cloudflare_workers_deployment"),
        "no_cloudflare_r2_live_reads": _passed("no_cloudflare_r2_live_reads"),
        "no_cloudflare_r2_writes": _passed("no_cloudflare_r2_writes"),
        "no_backblaze_b2_writes": _passed("no_backblaze_b2_writes"),
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
        "evidence_dir": "docs/evidence/ps-037e/",
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
