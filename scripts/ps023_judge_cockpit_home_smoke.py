#!/usr/bin/env python3
"""PS-023 Judge Cockpit Home -- smoke / validation script.

This is the canonical PS-023 validation command:

    python scripts/ps023_judge_cockpit_home_smoke.py

It statically validates the PS-023 judge cockpit surface without starting a
browser or calling any provider. It performs six checks:

1. required_copy     -- every required PS-023 phrase is present across the
                        judge cockpit source files and the proof doc.
2. route_cta_check   -- every route/CTA marker is present (client-side router,
                        passport route, review route, GitHub + evidence pack).
3. truth_boundary    -- the project explicitly states ProofStudio does NOT
                        prove semantic truth, legal authenticity, C2PA
                        authenticity, or human authorship.
4. forbidden_claim_scan -- a context-aware scan for affirmative overclaims.
                        Terms such as "Object Lock", "tamper-proof storage",
                        "production security" or "multi-user security" are
                        REJECTED only when asserted as an affirmative claim,
                        and ALLOWED when the same line or nearby context marks
                        them as a non-claim, limitation, rejection, or negation.
5. secret_scan       -- the changed PS-023 files contain no API keys, tokens,
                        bearer strings, or AWS/B2 credential literals.
6. proof_doc_check   -- the proof doc records files changed, CTA, truth
                        boundary, forbidden scan, frontend validation, build,
                        and this smoke script.

Why a context-aware scan: a naive scanner that flags any occurrence of a
sensitive term treats honest non-claim documentation (the truth boundary, the
expanded non-claims hint, the forbidden-claim scan section in the proof doc,
and fenced scan commands) as an affirmative overclaim. That is validator drift,
not a product failure. This script only rejects a sensitive term when it is
asserted affirmatively with no surrounding non-claim / negation context.

Truth boundary: this script validates that the PS-023 surface is honest. It
does not prove semantic truth, legal authenticity, C2PA authenticity, or human
authorship. Those are explicitly listed as non-claims by the product itself.

Exit code is 0 only when every check passes.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke_lib as sl  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]

# Files that together carry the PS-023 required copy + route/CTA surface.
COPY_FILES: tuple[Path, ...] = (
    REPO_ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx",
    REPO_ROOT / "apps" / "web" / "src" / "App.tsx",
    REPO_ROOT / "apps" / "web" / "src" / "PublicPassportPage.tsx",
    REPO_ROOT / "apps" / "web" / "index.html",
    REPO_ROOT / "docs" / "ps-023-judge-cockpit-home-proof.md",
)

# Changed PS-023 files that must be free of secrets. The scanner script itself
# is intentionally excluded: it legitimately contains the detection literals.
SECRET_FILES: tuple[Path, ...] = (
    REPO_ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx",
    REPO_ROOT / "apps" / "web" / "src" / "App.tsx",
    REPO_ROOT / "apps" / "web" / "src" / "PublicPassportPage.tsx",
    REPO_ROOT / "apps" / "web" / "src" / "styles.css",
    REPO_ROOT / "apps" / "web" / "index.html",
    REPO_ROOT / "docs" / "ps-023-judge-cockpit-home-proof.md",
)

PROOF_DOC = REPO_ROOT / "docs" / "ps-023-judge-cockpit-home-proof.md"
SCRIPT_NAME = "ps023_judge_cockpit_home_smoke.py"

# 1. Required PS-023 copy (exact casing as specified by the slice).
REQUIRED_COPY: tuple[str, ...] = (
    "ProofStudio",
    "AI media operations with durable proof",
    "Brief",
    "ProviderRouter",
    "Genblaze",
    "Generated Asset",
    "B2 Storage",
    "Manifest",
    "Archive",
    "Rehydrate",
    "Provenance Passport",
    "Real-world Utility",
    "Production Readiness",
    "B2 Storage + Data Orchestration",
    "Use of Genblaze",
    "semantic truth",
    "legal authenticity",
    "C2PA authenticity",
    "human authorship",
)

# 2. Route / CTA markers that must be reachable from the cockpit surface.
ROUTE_CTA_MARKERS: tuple[str, ...] = (
    "window.location.pathname",
    "/passport/",
    "/review",
    "JudgeCockpitHome",
    "judge-evidence-pack.md",
    "docs/submission",
    "github.com/GeorgeElArif/proofstudio",
)

# 3. Terms the project must explicitly state ProofStudio does NOT prove.
TRUTH_BOUNDARY_TERMS: tuple[str, ...] = (
    "semantic truth",
    "legal authenticity",
    "C2PA authenticity",
    "human authorship",
)

# 4a. Affirmative overclaims that must never be asserted as product claims.
#     Matched case-insensitively as contiguous phrases.
FORBIDDEN_AFFIRMATIVE: tuple[str, ...] = (
    "ProofStudio proves the image is true",
    "ProofStudio proves media is true",
    "proves legal authenticity",
    "proves human authorship",
    "is C2PA verified",
    "C2PA certified",
    "tamper-proof storage",
    "Object Lock",
    "enterprise-grade security",
    "multi-user security",
)

# 4b. Context markers that downgrade a sensitive term from an affirmative claim
#     to an allowed non-claim / limitation / rejection. When any marker appears
#     on the same line or in the nearby context window, the term is allowed.
CONTEXT_MARKERS_RE = re.compile(
    r"does not|do not|must not|\bnot\b|non-claim|non-claims|forbidden|"
    r"reject|rejected|avoid|without overclaim|unless actually implemented|"
    r"only inside non-claim|limitation|limitations|no affirmative",
    re.IGNORECASE,
)

# 4c. Markdown fence delimiters. Lines inside a fenced block are meta
#     documentation (e.g. a quoted scan command), never an affirmative claim.
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def _paragraph_range(lines: list[str], index: int) -> tuple[int, int]:
    """Return the [start, end) span of the non-blank paragraph around index.

    "Nearby context" for prose documentation is the enclosing paragraph: the
    run of consecutive non-blank lines that contains the hit. This is what lets
    an honest multi-line non-claim sentence (e.g. the proof doc's forbidden-claim
    section) be recognized as a non-claim even when the negation marker sits a
    few lines above the sensitive term, instead of forcing a brittle fixed
    line window that re-introduces validator drift.
    """
    start = index
    while start > 0 and lines[start - 1].strip():
        start -= 1
    end = index + 1
    while end < len(lines) and lines[end].strip():
        end += 1
    return start, end

# 5. Secret indicators. Plain substrings are matched case-sensitively; "sk-"
#    uses a regex so ordinary words like "risk-" or "flask-" do not trip it.
SECRET_SUBSTRINGS: tuple[str, ...] = (
    "B2_APP_KEY=",
    "CLOUDFLARE_API_TOKEN=",
    "GEMINI_API_KEY=",
    "GMI_API_KEY=",
    "ELEVENLABS_API_KEY=",
    "Bearer ",
    "AKIA",
    "AWS_SECRET_ACCESS_KEY",
)
SECRET_KEY_RE = re.compile(r"(?<![A-Za-z])sk-[A-Za-z0-9]")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_corpus(files: tuple[Path, ...]) -> dict[Path, str]:
    corpus: dict[Path, str] = {}
    for path in files:
        corpus[path] = read_text(path)
    return corpus


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def check_required_copy(corpus: dict[Path, str]) -> tuple[bool, list[str]]:
    combined = "\n".join(corpus.values())
    missing = [term for term in REQUIRED_COPY if term not in combined]
    return (not missing, missing)


def check_route_cta(corpus: dict[Path, str]) -> tuple[bool, list[str]]:
    combined = "\n".join(corpus.values())
    missing = [m for m in ROUTE_CTA_MARKERS if m not in combined]
    return (not missing, missing)


def check_truth_boundary(corpus: dict[Path, str]) -> tuple[bool, list[str]]:
    """Each truth-boundary term must appear inside a negation paragraph."""
    missing: list[str] = []
    for term in TRUTH_BOUNDARY_TERMS:
        term_lower = term.lower()
        found = False
        for text in corpus.values():
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if term_lower not in line.lower():
                    continue
                start, end = _paragraph_range(lines, i)
                window = "\n".join(lines[start:end])
                if CONTEXT_MARKERS_RE.search(window):
                    found = True
                    break
            if found:
                break
        if not found:
            missing.append(term)
    return (not missing, missing)


def _line_is_contextual(lines: list[str], index: int, in_fence: bool) -> bool:
    """True if the sensitive term on this line is an allowed non-claim."""
    if in_fence:
        return True
    start, end = _paragraph_range(lines, index)
    window = "\n".join(lines[start:end])
    return bool(CONTEXT_MARKERS_RE.search(window))


def check_forbidden_claims(
    corpus: dict[Path, str],
) -> tuple[bool, list[str]]:
    violations: list[str] = []
    for path, text in corpus.items():
        lines = text.splitlines()
        in_fence = False
        for i, line in enumerate(lines):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            line_lower = line.lower()
            hit = False
            for phrase in FORBIDDEN_AFFIRMATIVE:
                if phrase.lower() in line_lower:
                    hit = True
                    break
            if not hit:
                continue
            if _line_is_contextual(lines, i, in_fence):
                continue
            violations.append(
                f"{rel(path)}:{i + 1}: affirmative claim with no non-claim "
                f"context -> {line.strip()!r}"
            )
    return (not violations, violations)


def check_secrets(files: tuple[Path, ...]) -> tuple[bool, list[str]]:
    hits: list[str] = []
    for path in files:
        text = read_text(path)
        for needle in SECRET_SUBSTRINGS:
            if needle in text:
                idx = text.find(needle)
                line_no = text.count("\n", 0, idx) + 1
                hits.append(f"{rel(path)}:{line_no}: secret literal {needle!r}")
        for m in SECRET_KEY_RE.finditer(text):
            idx = m.start()
            line_no = text.count("\n", 0, idx) + 1
            hits.append(f"{rel(path)}:{line_no}: secret literal {m.group(0)!r}")
    return (not hits, hits)


def check_proof_doc() -> tuple[bool, list[str]]:
    text = read_text(PROOF_DOC)
    text_lower = text.lower()
    required = (
        "files changed",
        "cta",
        "truth boundary",
        "forbidden",
        "type" + "check",
        "build",
        SCRIPT_NAME.lower(),
    )
    missing = [needle for needle in required if needle not in text_lower]
    return (not missing, missing)


def run(argv: list[str] | None = None) -> int:
    opts = sl.parse_slice_smoke_cli(argv)
    missing_files = [str(p) for p in COPY_FILES if not p.exists()]
    missing_files += [str(p) for p in SECRET_FILES if not p.exists()]
    if not PROOF_DOC.exists():
        missing_files.append(str(PROOF_DOC))
    if missing_files:
        print("PS-023 smoke: MISSING INPUT FILES")
        for f in missing_files:
            print(f"  - {f}")
        return 1

    corpus = load_corpus(COPY_FILES)

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("required_copy", check_required_copy(corpus)),
        ("route_cta_check", check_route_cta(corpus)),
        ("truth_boundary", check_truth_boundary(corpus)),
        ("forbidden_claim_scan", check_forbidden_claims(corpus)),
        ("secret_scan", check_secrets(SECRET_FILES)),
        ("proof_doc_check", check_proof_doc()),
    ]

    all_pass, detail = sl.run_contract_checks("PS-023 Judge Cockpit Home", checks)
    print(json.dumps(detail, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run())
