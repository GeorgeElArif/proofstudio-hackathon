#!/usr/bin/env python3
"""PS-034C Winning Roadmap + Master Spec Replan -- doc-contract smoke.

This smoke is LOCAL / STATIC ONLY. It:

- reads docs / specs only
- does not call providers
- does not read B2
- does not run the frontend
- does not run the backend
- does not call the central regression gate
- does not mutate prior evidence
- writes only:
  ``docs/evidence/ps-034c/winning-roadmap-master-spec-replan-report.json``

It verifies that the PS-034C documentation replan is complete and internally
consistent:

- all required files exist
- the PS-035 numbering conflict is resolved
- the PS-031A correction is declared authoritative
- PS-035 is Review + Approval Workspace
- Disclosure is PS-037
- PS-035a is Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest
  Correctness
- PS-035 remains blocked until PS-034C is accepted
- Campaign Proof Room appears in required docs
- the multimodal proof layer appears in required docs
- AssemblyAI Transcript/Timestamp Evidence appears
- Hume or ElevenLabs Voiceover Artifact appears
- Gemini Campaign Intelligence / Judge Narrative appears
- Cloudflare Low-Cost Backbone appears
- Cost Caps + Golden-Fixture Governance appears
- Devpost Submission Package + 3-Minute Demo Script appears
- the truth boundary appears
- no forbidden overclaims appear as positive claims
- no forbidden implementation files were changed

Exit code is 0 only when every check passes.

    python scripts/ps034c_winning_roadmap_master_spec_replan_smoke.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "specs"
DOCS = ROOT / "docs"
REPORT = (
    DOCS / "evidence" / "ps-034c"
    / "winning-roadmap-master-spec-replan-report.json"
)

# Required files for PS-034C.
SPEC_FILE = SPECS / "46-ps-034c-winning-roadmap-master-spec-replan.md"
MASTER_SPEC = SPECS / "07-master-spec-plan.md"
ONE_PAGER = SPECS / "01-product-one-pager.md"
ROADMAP_SLICES = SPECS / "08-roadmap-slices.md"
WINNING_ROADMAP = (
    DOCS / "roadmap"
    / "proofstudio-winning-implementation-roadmap-2026-06-29.md"
)
PS031A_CORRECTION = (
    DOCS / "roadmap" / "ps-031a-hardened-product-modules-correction.md"
)
PROOF_DOC = DOCS / "ps-034c-winning-roadmap-master-spec-replan-proof.md"
VALIDATION_DOC = DOCS / "validation" / "proofstudio-smoke-harness-v1.md"

REQUIRED_FILES = [
    SPEC_FILE,
    MASTER_SPEC,
    ONE_PAGER,
    ROADMAP_SLICES,
    WINNING_ROADMAP,
    PS031A_CORRECTION,
    PROOF_DOC,
]

# Docs scanned for required winning-strategy terms and for the truth boundary.
CONTENT_DOCS = [
    MASTER_SPEC,
    ONE_PAGER,
    ROADMAP_SLICES,
    WINNING_ROADMAP,
    PS031A_CORRECTION,
]

# Docs scanned for overclaim risk. Meta-docs that merely describe the check
# (the proof doc, the smoke script, this report) are intentionally excluded so
# the literal forbidden-phrase list does not flag itself.
OVERCLAIM_SCAN_DOCS = [
    MASTER_SPEC,
    ONE_PAGER,
    ROADMAP_SLICES,
    WINNING_ROADMAP,
    PS031A_CORRECTION,
]

# Forbidden overclaim phrases that must never appear as POSITIVE claims.
# Each line containing such a phrase must carry a negation / non-claim cue.
FORBIDDEN_OVERCLAIM_PHRASES = [
    "production secure",
    "C2PA authentic",
    "human authorship proven",
    "Object Lock enabled",
    "tamper-proof storage",
    "browser-side B2 byte verification",
]

# Negation / non-claim cues. A forbidden phrase is acceptable only if a cue
# appears within the context window around it (i.e. the phrase is stated as a
# non-claim, not asserted as a capability). "stretch" is included because it is
# this project's canonical marker for an unimplemented stretch goal (never a
# positive claim). Broad words that could mask a real overclaim (e.g. "future",
# "honest") are intentionally excluded.
NEGATION_CUES = (
    "does not",
    "do not",
    "doesn't",
    "don't",
    "not prove",
    "not claim",
    "must not",
    "no claim",
    "no overclaim",
    "no fake",
    "without",
    "unless",
    "non-claim",
    "non-claimed",
    "never claim",
    "not implemented",
    "not yet implemented",
    "forbidden",
    "no c2pa",
    "no object lock",
    "no tamper-proof",
    "no browser-side",
    "only claim if",
    "only if implemented",
    "only if real",
    "not legal",
    "not authorized",
    "do not claim",
    "must not be claimed",
    "is not",
    "are not",
    "cannot",
    "can't",
    "must not claim",
    "not authorized to",
    "stretch",
)

# Forbidden implementation file patterns. None of these may appear in the
# PS-034C diff.
FORBIDDEN_PATH_PATTERNS = [
    re.compile(r"^apps/web/"),
    re.compile(r"^apps/api/"),
    re.compile(r"^src/"),
    re.compile(r"^workers/"),
    re.compile(r"^packages/"),
    re.compile(r"^render\.yaml$"),
    re.compile(r"^\.env"),
    re.compile(r"^requirements.*\.txt$"),
    re.compile(r"^pyproject\.toml$"),
    re.compile(r"^scripts/proofstudio_regression_gate\.py$"),
    re.compile(r"^docs/evidence/ps-034a/"),
    re.compile(r"^docs/evidence/ps-034b/"),
    re.compile(r"^docs/evidence/ps-023/"),
    re.compile(r"^docs/evidence/ps-024/"),
    re.compile(r"^docs/evidence/ps-025/"),
    re.compile(r"^docs/evidence/ps-026/"),
    re.compile(r"^docs/evidence/ps-027/"),
    re.compile(r"^docs/evidence/ps-028/"),
    re.compile(r"^docs/evidence/ps-029/"),
    re.compile(r"^docs/evidence/ps-030/"),
    re.compile(r"^docs/evidence/ps-031/"),
    re.compile(r"^docs/evidence/ps-032/"),
    re.compile(r"^docs/evidence/ps-033/"),
    re.compile(r"^docs/evidence/ps-034/"),
    re.compile(r"^docs/evidence/demo/golden-demo-run\.json$"),
]

# The PS-034A required validation sentence must still be present verbatim.
PS034A_REQUIRED_LINE = (
    "Historical smoke local-mode retrofit is deferred to PS-034B."
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_WS_RE = re.compile(r"\s+")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _flat(text: str) -> str:
    """Collapse all runs of whitespace (including newlines) to single spaces.

    Markdown paragraphs in the docs wrap forbidden/required phrases across
    multiple physical lines. Substring and overclaim checks operate on this
    normalized form so wrapping does not produce false negatives or positives.
    """
    return _WS_RE.sub(" ", text).strip()


def _read_flat(path: Path) -> str:
    return _flat(_read(path)) if path.is_file() else ""


def _check_files_exist(failures: list[str]) -> bool:
    ok = True
    for p in REQUIRED_FILES:
        if not p.is_file():
            failures.append(f"required_file_missing: {p}")
            ok = False
    return ok


def _require_in(
    failures: list[str],
    label: str,
    doc: Path,
    needle: str,
) -> bool:
    text = _read_flat(doc)
    if needle not in text:
        failures.append(f"{label}: missing {needle!r} in {doc.name}")
        return False
    return True


def _require_all(
    failures: list[str],
    label: str,
    requirements: list[tuple[Path, str]],
) -> bool:
    ok = True
    for doc, needle in requirements:
        if not _require_in(failures, label, doc, needle):
            ok = False
    return ok


def _check_roadmap_conflict_resolved(failures: list[str]) -> bool:
    return _require_all(
        failures,
        "roadmap_conflict_resolved",
        [
            (MASTER_SPEC, "PS-035 is Review + Approval Workspace"),
            (MASTER_SPEC, "Disclosure becomes PS-037"),
            (ROADMAP_SLICES, "PS-035 is Review + Approval Workspace"),
            (WINNING_ROADMAP, "PS-035 is Review + Approval Workspace"),
            (WINNING_ROADMAP, "Disclosure becomes PS-037"),
        ],
    )


def _check_ps031a_authoritative(failures: list[str]) -> bool:
    return _require_all(
        failures,
        "ps031a_authoritative",
        [
            (WINNING_ROADMAP, "PS-031A"),
            (WINNING_ROADMAP, "authoritative"),
            (PS031A_CORRECTION, "PS-034C"),
            (PS031A_CORRECTION, "authoritative"),
            (MASTER_SPEC, "authoritative"),
        ],
    )


def _check_ps035_review_workspace(failures: list[str]) -> bool:
    return _require_all(
        failures,
        "ps035_review_workspace",
        [
            (MASTER_SPEC, "Review + Approval Workspace"),
            (ROADMAP_SLICES, "Review + Approval Workspace"),
            (WINNING_ROADMAP, "Review + Approval Workspace"),
        ],
    )


def _check_ps037_disclosure_layer(failures: list[str]) -> bool:
    return _require_all(
        failures,
        "ps037_disclosure_layer",
        [
            (MASTER_SPEC, "Disclosure + Trust Boundary Layer"),
            (ROADMAP_SLICES, "Disclosure + Trust Boundary Layer"),
            (WINNING_ROADMAP, "Disclosure + Trust Boundary Layer"),
        ],
    )


def _check_ps035a_genblaze_manifest_correctness(failures: list[str]) -> bool:
    needle = (
        "Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest "
        "Correctness"
    )
    return _require_all(
        failures,
        "ps035a_genblaze_manifest_correctness",
        [
            (MASTER_SPEC, needle),
            (ROADMAP_SLICES, needle),
            (WINNING_ROADMAP, needle),
            (PROOF_DOC, needle),
        ],
    )


def _check_ps035_blocked(failures: list[str]) -> bool:
    return _require_all(
        failures,
        "ps035_blocked_until_ps034c_accepted",
        [
            (MASTER_SPEC, "PS-035 remains blocked until PS-034C is accepted"),
            (ROADMAP_SLICES, "PS-035 remains blocked until PS-034C is accepted"),
            (WINNING_ROADMAP, "PS-035 remains blocked until PS-034C is accepted"),
        ],
    )


def _check_term_present(
    failures: list[str],
    label: str,
    needle: str,
    docs: list[Path],
) -> bool:
    """Needle must appear in at least one of the given docs (flat text)."""
    for doc in docs:
        if needle in _read_flat(doc):
            return True
    failures.append(
        f"{label}: {needle!r} not found in any of "
        f"{[d.name for d in docs]}"
    )
    return False


def _check_campaign_proof_room(failures: list[str]) -> bool:
    return _check_term_present(
        failures,
        "campaign_proof_room_present",
        "Campaign Proof Room",
        [MASTER_SPEC, ONE_PAGER, ROADMAP_SLICES, WINNING_ROADMAP, PROOF_DOC],
    )


def _check_multimodal_proof(failures: list[str]) -> bool:
    return _check_term_present(
        failures,
        "multimodal_proof_present",
        "multimodal proof layer",
        [MASTER_SPEC, ONE_PAGER, ROADMAP_SLICES, PROOF_DOC],
    )


def _check_assemblyai(failures: list[str]) -> bool:
    return _check_term_present(
        failures,
        "assemblyai_transcript_present",
        "AssemblyAI Transcript/Timestamp Evidence",
        [MASTER_SPEC, ROADMAP_SLICES, PROOF_DOC],
    )


def _check_voiceover(failures: list[str]) -> bool:
    return _check_term_present(
        failures,
        "voiceover_artifact_present",
        "Hume or ElevenLabs Voiceover Artifact",
        [MASTER_SPEC, ROADMAP_SLICES, PROOF_DOC],
    )


def _check_gemini(failures: list[str]) -> bool:
    return _check_term_present(
        failures,
        "gemini_strategy_present",
        "Gemini Campaign Intelligence / Judge Narrative",
        [MASTER_SPEC, ROADMAP_SLICES, PROOF_DOC],
    )


def _check_cloudflare(failures: list[str]) -> bool:
    return _check_term_present(
        failures,
        "cloudflare_backbone_present",
        "Cloudflare Low-Cost Backbone",
        [MASTER_SPEC, ROADMAP_SLICES, PROOF_DOC],
    )


def _check_cost_caps(failures: list[str]) -> bool:
    return _check_term_present(
        failures,
        "cost_caps_present",
        "Cost Caps + Golden-Fixture Governance",
        [MASTER_SPEC, ROADMAP_SLICES, PROOF_DOC],
    )


def _check_devpost_demo(failures: list[str]) -> bool:
    return _check_term_present(
        failures,
        "devpost_demo_present",
        "Devpost Submission Package + 3-Minute Demo Script",
        [MASTER_SPEC, ROADMAP_SLICES, PROOF_DOC],
    )


def _check_truth_boundary(failures: list[str]) -> bool:
    return _check_term_present(
        failures,
        "truth_boundary_present",
        "Truth Boundary",
        [MASTER_SPEC, ONE_PAGER, WINNING_ROADMAP, PROOF_DOC],
    )


def _check_ps034a_required_line(failures: list[str]) -> bool:
    text = _read_flat(VALIDATION_DOC)
    if PS034A_REQUIRED_LINE not in text:
        failures.append(
            "ps034a_required_line_preserved: missing exact sentence "
            f"{PS034A_REQUIRED_LINE!r} in {VALIDATION_DOC.name}"
        )
        return False
    return True


# Context window (in characters) around a forbidden phrase that must contain a
# negation / non-claim cue. Generous enough to capture the negation cue that
# opens a wrapped markdown paragraph (e.g. "It does not prove ...") or the
# "unless implemented" that closes it.
_OVERCLAIM_BEFORE_WINDOW = 260
_OVERCLAIM_AFTER_WINDOW = 200


def _check_no_forbidden_overclaims(failures: list[str]) -> bool:
    """Forbid overclaim phrases as POSITIVE claims.

    Operates on whitespace-normalized text so wrapped paragraphs are handled.
    A forbidden phrase is acceptable only if a negation / non-claim cue appears
    within a context window around it (for example "does not prove", "must not
    claim", or "unless implemented"). A standalone positive assertion
    (e.g. "ProofStudio provides tamper-proof storage") has no such cue nearby
    and is flagged.
    """
    ok = True
    for doc in OVERCLAIM_SCAN_DOCS:
        if not doc.is_file():
            continue
        flat = _read_flat(doc).lower()
        for phrase in FORBIDDEN_OVERCLAIM_PHRASES:
            p_low = phrase.lower()
            start = 0
            while True:
                idx = flat.find(p_low, start)
                if idx == -1:
                    break
                win_start = max(0, idx - _OVERCLAIM_BEFORE_WINDOW)
                win_end = min(len(flat), idx + len(p_low) + _OVERCLAIM_AFTER_WINDOW)
                window = flat[win_start:win_end]
                if not any(cue in window for cue in NEGATION_CUES):
                    failures.append(
                        f"no_forbidden_overclaims/{doc.name}: phrase "
                        f"{phrase!r} appears as a positive claim "
                        f"(no negation cue in context): "
                        f"{flat[max(0, idx - 80):idx + len(p_low) + 80].strip()!r}"
                    )
                    ok = False
                start = idx + len(p_low)
    return ok


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


def _check_no_forbidden_file_changes(failures: list[str]) -> bool:
    ok = True
    try:
        paths = _git_status_paths()
    except Exception as exc:  # pragma: no cover - defensive
        failures.append(f"no_forbidden_file_changes: git status failed: {exc}")
        return False
    for path in paths:
        for pat in FORBIDDEN_PATH_PATTERNS:
            if pat.search(path):
                failures.append(
                    f"no_forbidden_file_changes: forbidden path changed: "
                    f"{path}"
                )
                ok = False
                break
    return ok


def main() -> int:
    failures: list[str] = []
    files_checked: list[str] = [str(p.relative_to(ROOT)) for p in REQUIRED_FILES]

    files_exist = _check_files_exist(failures)

    roadmap_conflict_resolved = _check_roadmap_conflict_resolved(failures)
    ps031a_authoritative = _check_ps031a_authoritative(failures)
    ps035_review_workspace = _check_ps035_review_workspace(failures)
    ps037_disclosure_layer = _check_ps037_disclosure_layer(failures)
    ps035a_genblaze_manifest_correctness = (
        _check_ps035a_genblaze_manifest_correctness(failures)
    )
    ps035_blocked = _check_ps035_blocked(failures)
    campaign_proof_room_present = _check_campaign_proof_room(failures)
    multimodal_proof_present = _check_multimodal_proof(failures)
    assemblyai_transcript_present = _check_assemblyai(failures)
    voiceover_artifact_present = _check_voiceover(failures)
    gemini_strategy_present = _check_gemini(failures)
    cloudflare_backbone_present = _check_cloudflare(failures)
    cost_caps_present = _check_cost_caps(failures)
    devpost_demo_present = _check_devpost_demo(failures)
    truth_boundary_present = _check_truth_boundary(failures)
    ps034a_required_line_preserved = _check_ps034a_required_line(failures)
    no_forbidden_overclaims = _check_no_forbidden_overclaims(failures)
    no_forbidden_file_changes = _check_no_forbidden_file_changes(failures)

    ok = (
        files_exist
        and roadmap_conflict_resolved
        and ps031a_authoritative
        and ps035_review_workspace
        and ps037_disclosure_layer
        and ps035a_genblaze_manifest_correctness
        and ps035_blocked
        and campaign_proof_room_present
        and multimodal_proof_present
        and assemblyai_transcript_present
        and voiceover_artifact_present
        and gemini_strategy_present
        and cloudflare_backbone_present
        and cost_caps_present
        and devpost_demo_present
        and truth_boundary_present
        and ps034a_required_line_preserved
        and no_forbidden_overclaims
        and no_forbidden_file_changes
        and not failures
    )

    report = {
        "ok": bool(ok),
        "slice_id": "ps034c",
        "checked_at": _utc_now_iso(),
        "files_checked": files_checked,
        "roadmap_conflict_resolved": bool(roadmap_conflict_resolved),
        "ps031a_authoritative": bool(ps031a_authoritative),
        "ps035_review_workspace": bool(ps035_review_workspace),
        "ps037_disclosure_layer": bool(ps037_disclosure_layer),
        "ps035a_genblaze_manifest_correctness": bool(
            ps035a_genblaze_manifest_correctness
        ),
        "ps035_blocked_until_ps034c_accepted": bool(ps035_blocked),
        "campaign_proof_room_present": bool(campaign_proof_room_present),
        "multimodal_proof_present": bool(multimodal_proof_present),
        "assemblyai_transcript_present": bool(assemblyai_transcript_present),
        "voiceover_artifact_present": bool(voiceover_artifact_present),
        "gemini_strategy_present": bool(gemini_strategy_present),
        "cloudflare_backbone_present": bool(cloudflare_backbone_present),
        "cost_caps_present": bool(cost_caps_present),
        "devpost_demo_present": bool(devpost_demo_present),
        "truth_boundary_preserved": bool(truth_boundary_present),
        "truth_boundary_present": bool(truth_boundary_present),
        "ps034a_required_line_preserved": bool(ps034a_required_line_preserved),
        "no_forbidden_overclaims": bool(no_forbidden_overclaims),
        "no_forbidden_file_changes": bool(no_forbidden_file_changes),
        "forbidden_overclaim_phrases": list(FORBIDDEN_OVERCLAIM_PHRASES),
        "failures": failures,
    }

    if "truth_boundary_preserved" not in report:
        failures.append(
            "truth_boundary_preserved: required report field is missing"
        )
        ok = False
    elif report.get("truth_boundary_preserved") is not True:
        failures.append(
            "truth_boundary_preserved: required report field is not true"
        )
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
        print("PS-034C DOC-CONTRACT SMOKE FAILED", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("PS-034C DOC-CONTRACT SMOKE PASSED")
    print(f"  files_checked: {len(files_checked)}")
    print(f"  roadmap_conflict_resolved: {roadmap_conflict_resolved}")
    print(f"  ps035a_genblaze_manifest_correctness: "
          f"{ps035a_genblaze_manifest_correctness}")
    print(f"  no_forbidden_overclaims: {no_forbidden_overclaims}")
    print(f"  no_forbidden_file_changes: {no_forbidden_file_changes}")
    print(f"  report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
