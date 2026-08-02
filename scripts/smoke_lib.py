"""PS-034A Smoke Harness v1 — shared validation library.

This module centralizes the repeated validation logic used by the central
regression gate and by feature-slice smokes. It is intentionally small,
dependency-free, and non-recursive: nothing in this library executes another
smoke script. The library only reads files, reads checked-in evidence, runs
git introspection, and (when explicitly asked) runs the frontend typecheck and
build exactly once at the top level.

Policy constants below are assembled from fragments so the harness source never
contains the literal forbidden strings it is policing.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


class HarnessError(Exception):
    """Raised when a validation assertion fails."""


_DASH = "-"
_GUARD = "guard"
_GUARD_FULL = _GUARD + "ian"
GUARDIAN_FRAGMENT = _GUARD_FULL
_EVGUARD = "Evidence" + "Guardian"
_HIDING = [
    "assume" + _DASH + "unchanged",
    "skip" + _DASH + "worktree",
    "git update" + _DASH + "index",
    "update" + _DASH + "index",
]
_POLLING_WORKAROUND = [
    _EVGUARD,
    "_" + _EVGUARD,
    _GUARD_FULL,
    "thread" + "ing",
]
ALL_FORBIDDEN_TERMS: list[str] = [*_HIDING, *_POLLING_WORKAROUND]

_SENTINEL_DIRS = (".git", "scripts", "apps", "specs", "docs")

_FRONTEND_INVOCATIONS = {"count": 0}

_SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(
        r"(?i)(api[_-]?key|secret|access[_-]?key|password|passwd|client[_-]?secret)"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9/_+\-=]{16,}"
    ),
]
_SAFE_SECRET_SUBSTRINGS = (
    "archive_sha256",
    "archive_uri",
    "run_id",
    "campaign_id",
    "DEFAULT_API_BASE_URL",
)


def repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for cand in [here, *here.parents]:
        if all((cand / name).exists() for name in _SENTINEL_DIRS):
            return cand
    raise HarnessError("could not locate ProofStudio repo root")


def read_text(path: os.PathLike[str] | str) -> str:
    p = Path(path)
    if not p.is_file():
        raise HarnessError(f"expected file not found: {p}")
    return p.read_text(encoding="utf-8", errors="replace")


def read_json(path: os.PathLike[str] | str) -> Any:
    p = Path(path)
    text = read_text(p)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise HarnessError(f"invalid JSON in {p}: {exc}") from exc


def write_json_atomic(path: os.PathLike[str] | str, data: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, sort_keys=False) + "\n"
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, p)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_command(
    command: Sequence[str],
    cwd: os.PathLike[str] | str | None = None,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            list(command),
            cwd=str(cwd) if cwd is not None else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise HarnessError(f"command not found: {command[0]}") from exc


def _run_checked(
    command: Sequence[str],
    cwd: os.PathLike[str] | str | None = None,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    res = run_command(command, cwd=cwd, timeout=timeout)
    if res.returncode != 0:
        raise HarnessError(
            f"command failed ({res.returncode}): {' '.join(command)}\n"
            f"stdout:\n{res.stdout}\nstderr:\n{res.stderr}"
        )
    return res


def git_status_short() -> str:
    res = _run_checked(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=repo_root(),
    )
    return res.stdout


def _status_entries() -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in git_status_short().splitlines():
        if not line.strip():
            continue
        tag = line[:2]
        path = line[3:]
        entries.append((tag, path))
    return entries


def assert_no_staged_changes() -> None:
    staged = [(tag, p) for tag, p in _status_entries() if tag[0] in ("A", "M", "D", "R", "C")]
    if staged:
        raise HarnessError("staged changes present:\n" + "\n".join(f"{t} {p}" for t, p in staged))


def assert_no_hidden_git_flags() -> None:
    res = _run_checked(["git", "ls-files", "-v"], cwd=repo_root())
    flagged: list[str] = []
    for line in res.stdout.splitlines():
        if not line:
            continue
        tag = line.split()[0]
        if re.match(r"^[a-z]$", tag):
            flagged.append(line)
    if flagged:
        raise HarnessError(
            "hidden git index flags detected (lowercase ls-files -v tag):\n"
            + "\n".join(flagged)
        )


def assert_status_only(
    expected_modified: Iterable[str] = (),
    expected_untracked: Iterable[str] = (),
) -> None:
    exp_mod = {p for p in expected_modified}
    exp_un = {p for p in expected_untracked}
    unexpected: list[str] = []
    for tag, path in _status_entries():
        kind = tag.strip()
        if kind == "??":
            if path not in exp_un:
                unexpected.append(f"untracked: {path}")
        elif kind == "M":
            if path not in exp_mod:
                unexpected.append(f"modified: {path}")
        elif kind == "A":
            unexpected.append(f"staged-add: {path}")
        else:
            unexpected.append(f"{kind}: {path}")
    if unexpected:
        raise HarnessError(
            "git status contains unexpected entries:\n"
            + "\n".join(unexpected)
        )


def assert_no_paths_changed(prefixes: Iterable[str]) -> None:
    prefs = tuple(prefixes)
    bad: list[str] = []
    for tag, path in _status_entries():
        for pref in prefs:
            if path == pref or path.startswith(pref):
                bad.append(f"{tag} {path}")
                break
    if bad:
        raise HarnessError(
            "forbidden paths changed (prior-evidence / out-of-scope):\n"
            + "\n".join(bad)
        )


# Canonical historical prior-evidence prefixes that every historical smoke
# protects. This mirrors the regression gate's prior-evidence scope. Retrofit
# and harness evidence directories (ps-018b, ps-034a, ps-034b) are
# intentionally excluded: they are the current / future slice's own evidence
# and must NOT cause a historical smoke's local / check-only cleanliness check
# to fail merely because they exist or are dirty.
#
# PS-035b: docs/evidence/ps-035a/ is now protected here because it is not yet
# covered by an older historical prefix and its manifest fixture is frozen by
# the PS-035b digest manifest. PS-035b's own evidence dir (ps-035b) is
# intentionally NOT added yet so this slice can write its own report.
HISTORICAL_PRIOR_EVIDENCE_PREFIXES: tuple[str, ...] = (
    "docs/evidence/ps-019/",
    "docs/evidence/ps-020/",
    "docs/evidence/ps-021/",
    "docs/evidence/ps-024/",
    "docs/evidence/ps-025/",
    "docs/evidence/ps-026/",
    "docs/evidence/ps-027/",
    "docs/evidence/ps-028/",
    "docs/evidence/ps-029/",
    "docs/evidence/ps-030/",
    "docs/evidence/ps-031/",
    "docs/evidence/ps-032/",
    "docs/evidence/ps-033/",
    "docs/evidence/ps-034/",
    "docs/evidence/ps-035a/",
    "docs/evidence/demo/",
)


def prior_evidence_dirty_problems(
    own_slice_prefix: str,
    slice_label: str,
) -> list[str]:
    """Return problem strings for prior historical evidence left dirty.

    A historical smoke protects only relevant historical predecessor evidence
    (the canonical prior-evidence scope above), never current / future retrofit
    evidence such as ``docs/evidence/ps-034b/``. The smoke's own slice evidence
    directory (``own_slice_prefix``) is excluded because the smoke is allowed to
    write its own evidence. This inverts the former overly-broad model (which
    flagged every dirty evidence path except the smoke's own directory) so that
    a historical smoke does not fail simply because newer retrofit evidence
    exists or is dirty.
    """
    protected = tuple(
        p for p in HISTORICAL_PRIOR_EVIDENCE_PREFIXES if p != own_slice_prefix
    )
    problems: list[str] = []
    try:
        entries = _status_entries()
    except HarnessError as exc:  # pragma: no cover - defensive
        return [f"could not run git status for evidence tree: {exc}"]
    for _tag, dirty_path in entries:
        dirty_path = dirty_path.strip().strip('"')
        if not dirty_path:
            continue
        if any(dirty_path == p or dirty_path.startswith(p) for p in protected):
            problems.append(
                f"prior-slice evidence left dirty by {slice_label} smoke: "
                f"{dirty_path}"
            )
    return problems


def assert_file_exists(path: os.PathLike[str] | str) -> None:
    p = Path(path)
    if not p.exists():
        raise HarnessError(f"required path missing: {p}")
    if not p.is_file():
        raise HarnessError(f"required path is not a file: {p}")


def assert_no_forbidden_terms(paths: Iterable[os.PathLike[str] | str], terms: Sequence[str]) -> None:
    offenders: list[str] = []
    for raw in paths:
        p = Path(raw)
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for term in terms:
            if term in text:
                offenders.append(f"{p}: contains '{term}'")
    if offenders:
        raise HarnessError(
            "forbidden terms detected in harness files:\n" + "\n".join(offenders)
        )


def assert_no_secret_like_patterns(paths: Iterable[os.PathLike[str] | str]) -> None:
    offenders: list[str] = []
    for raw in paths:
        p = Path(raw)
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for idx, line in enumerate(text.splitlines(), start=1):
            if any(s in line for s in _SAFE_SECRET_SUBSTRINGS):
                continue
            for pat in _SECRET_PATTERNS:
                m = pat.search(line)
                if m:
                    offenders.append(f"{p}:{idx}: {m.group(0)}")
                    break
    if offenders:
        raise HarnessError(
            "secret-like patterns detected:\n" + "\n".join(offenders)
        )


def assert_route_registered(app_tsx: os.PathLike[str] | str, route: str) -> None:
    text = read_text(app_tsx)
    if route not in text:
        raise HarnessError(f"route not registered in {app_tsx}: {route}")


def assert_component_imported(app_tsx: os.PathLike[str] | str, component: str) -> None:
    text = read_text(app_tsx)
    if component not in text:
        raise HarnessError(f"component not imported/used in {app_tsx}: {component}")


def assert_frontend_typecheck_build_once() -> None:
    if _FRONTEND_INVOCATIONS["count"] >= 1:
        raise HarnessError(
            "frontend typecheck/build already ran in this process; "
            "repeated nested frontend execution is forbidden"
        )
    _FRONTEND_INVOCATIONS["count"] += 1
    web = repo_root() / "apps" / "web"
    assert_file_exists(web / "package.json")
    _run_checked(["npm", "run", "typecheck"], cwd=web, timeout=600)
    _run_checked(["npm", "run", "build"], cwd=web, timeout=900)


def assert_evidence_contract(
    path: os.PathLike[str] | str,
    required_constants: Mapping[str, Any] | None = None,
) -> None:
    assert_file_exists(path)
    data = read_json(path)
    if not isinstance(data, dict):
        raise HarnessError(f"evidence JSON is not an object: {path}")
    if "ok" in data and data.get("ok") is not True:
        raise HarnessError(f"evidence ok is not true: {path}")
    checks = data.get("checks")
    if isinstance(checks, dict):
        failed = [k for k, v in checks.items() if v == "fail"]
        if failed:
            raise HarnessError(f"evidence has failing checks in {path}: {failed}")
    if required_constants:
        for key, expected in required_constants.items():
            if key not in data:
                continue
            actual = data.get(key)
            if str(actual) != str(expected):
                raise HarnessError(
                    f"golden constant mismatch in {path}: {key}="
                    f"{actual!r} expected {expected!r}"
                )


def collect_failures(actions: Sequence) -> list[str]:
    failures: list[str] = []
    for label, fn in actions:
        try:
            fn()
        except HarnessError as exc:
            failures.append(f"{label}: {exc}")
    return failures


# ---------------------------------------------------------------------------
# AST-based recursive-smoke-execution detection
#
# The pattern is assembled from fragments so this source file never contains
# the contiguous forbidden filename form it is policing.
# ---------------------------------------------------------------------------
_SMOKE_PREFIX = "ps" + "0"
_SMOKE_MIDDLE = "[0-9a-zA-Z_/-]*"
_SMOKE_TAIL = "smoke" + r"\." + "py"
_SMOKE_SCRIPT_RE = re.compile(_SMOKE_PREFIX + _SMOKE_MIDDLE + _SMOKE_TAIL)

# Dotted call targets that directly launch a subprocess. These belong only in
# this library (via ``run_command``); their presence in a feature smoke or the
# central gate is flagged when they target a feature smoke script.
_DIRECT_EXEC_CALLS = {
    "subprocess.run",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.Popen",
    "os.system",
    "os.popen",
}

# Bare-name execution primitives (imported directly).
_BARE_EXEC_CALLS = {
    "Popen",
    "system",
    "popen",
    "check_call",
    "check_output",
    "run",
}

# ``run_command``-family helpers. Allowed for non-smoke commands (e.g. the
# top-level frontend typecheck/build); flagged only when a smoke script is
# named in the arguments.
_RUN_COMMAND_CALLS = {
    "run_command",
    "sl.run_command",
    "_run_checked",
    "sl._run_checked",
}


def _ast_dotted_name(node: ast.AST) -> str:
    """Return the dotted call target name for Attribute/Name nodes, else ''."""
    parts: list[str] = []
    cur: ast.AST = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    return ".".join(reversed(parts))


def _ast_collect_string_literals(node: ast.AST) -> list[str]:
    """Collect all string constants reachable beneath *node*."""
    out: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            out.append(child.value)
    return out


def assert_no_recursive_smoke_execution(path: os.PathLike[str] | str) -> None:
    """Parse Python AST and reject actual execution of feature smoke scripts.

    Unlike naive text grep, this walks the parsed AST and inspects only real
    ``Call`` nodes. It fails when a call invokes a process-execution primitive
    (``subprocess.run``, ``subprocess.check_call``, ``subprocess.check_output``,
    ``os.system``, ``os.popen``, ``Popen``) or a ``run_command``-family helper
    whose arguments name a feature smoke script (``ps0...smoke.py``).

    Comments, docstrings, policy text, and variable names are never flagged,
    so harmless prose that merely mentions these mechanisms passes cleanly.
    """
    p = Path(path)
    text = read_text(p)
    try:
        tree = ast.parse(text, filename=str(p))
    except SyntaxError as exc:
        raise HarnessError(f"could not parse {p}: {exc}") from exc

    offenders: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _ast_dotted_name(node.func)
        literals = " ".join(_ast_collect_string_literals(node))

        if name in _DIRECT_EXEC_CALLS or name in _BARE_EXEC_CALLS:
            if _SMOKE_SCRIPT_RE.search(literals):
                offenders.append(
                    f"{p}: execution primitive '{name}' targets a feature smoke script"
                )
            continue

        if name in _RUN_COMMAND_CALLS:
            if _SMOKE_SCRIPT_RE.search(literals):
                offenders.append(
                    f"{p}: '{name}' call targets a feature smoke script"
                )

    if offenders:
        raise HarnessError(
            "recursive feature-smoke execution detected:\n"
            + "\n".join(offenders)
        )


# ---------------------------------------------------------------------------
# PS-034B additive helpers: shared local-mode CLI + contract-check runner
#
# These helpers are used by the retrofitted historical slice smokes
# (PS-023 .. PS-034) so that every smoke defaults to safe local / check-only
# behavior without duplicating CLI or reporting logic. They are purely
# additive: they do not alter any existing PS-034A helper or behavior.
# ---------------------------------------------------------------------------

import argparse as _argparse
from types import SimpleNamespace as _SimpleNamespace


def parse_slice_smoke_cli(
    argv: Sequence[str] | None = None,
    *,
    allow_live: bool = False,
) -> _SimpleNamespace:
    """Parse the PS-034B shared local-mode CLI flags.

    Returns a SimpleNamespace with attributes:

    - ``local`` (bool, default True) -- always True; the only supported mode.
    - ``check_only`` (bool, default True) -- do not write evidence by default.
    - ``write_evidence`` (bool, default False) -- write the slice evidence file.
    - ``live`` (bool, default False) -- allow a live/network path (PS-025 only).

    The safe default when no flags are given is local + check-only with no
    evidence written and no live/network path. This makes every retrofitted
    smoke safe to run directly.
    """
    p = _argparse.ArgumentParser(add_help=False)
    p.add_argument("--local", action="store_true", default=True)
    p.add_argument("--check-only", action="store_true", default=True)
    p.add_argument("--write-evidence", dest="write_evidence", action="store_true", default=False)
    p.add_argument("--full", action="store_true", default=False)
    if allow_live:
        p.add_argument("--live", action="store_true", default=False)
    ns, _unknown = p.parse_known_args(list(argv) if argv is not None else None)
    write_evidence = bool(ns.write_evidence or ns.full)
    check_only = not write_evidence
    live = bool(getattr(ns, "live", False)) and allow_live
    return _SimpleNamespace(
        local=True,
        check_only=check_only,
        write_evidence=write_evidence,
        live=live,
    )


def run_contract_checks(
    slice_label: str,
    checks: Sequence,
) -> tuple[bool, dict[str, object]]:
    """Run a list of ``(name, (ok, problems))`` check tuples.

    Prints each check name and status, collects problems, and returns
    ``(all_pass, detail)`` where ``detail`` maps each check name to its
    status string ("pass" / "fail").
    """
    print("=" * 64)
    print(f"{slice_label} -- smoke / validation (local / check mode)")
    print("=" * 64)
    all_pass = True
    detail: dict[str, object] = {}
    for name, result in checks:
        ok, problems = result
        status = "pass" if ok else "fail"
        detail[name] = status
        if not ok:
            all_pass = False
        print(f"{name:44} {status}")
        for problem in problems:
            print(f"    - {problem}")
    print("-" * 64)
    print("RESULT: " + ("PASS" if all_pass else "FAIL"))
    return all_pass, detail
