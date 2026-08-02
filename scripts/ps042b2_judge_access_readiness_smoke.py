#!/usr/bin/env python3
"""PS-042B2 static readiness contract smoke. Standard library only; no live calls."""

from __future__ import annotations

import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = "03c0f85b4d418b9c2520e6ad66e03819b1efe796"
ALLOWLIST = {
    "apps/auth-server/package.json",
    "apps/auth-server/src/account/campaign-access.ts",
    "apps/auth-server/src/db/schema.ts",
    "apps/auth-server/scripts/provision-judge-account.ts",
    "apps/auth-server/scripts/smoke-judge-access-readiness.ts",
    "apps/auth-server/scripts/smoke-judge-provisioning.ts",
    "apps/web/scripts/smoke-judge-authenticated-journey.mjs",
    "scripts/ps042b2_judge_access_readiness_smoke.py",
    "docs/deployment/judge-access.md",
    "docs/deployment/preflight-checklist.md",
    "docs/ps-042b2-judge-access-readiness-proof.md",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


provision_path = ROOT / "apps/auth-server/scripts/provision-judge-account.ts"
require(provision_path.is_file(), "provisioning script missing")
provision = provision_path.read_text(encoding="utf-8")
server = read("apps/auth-server/src/server.ts")
package = json.loads(read("apps/auth-server/package.json"))
migrations = "\n".join(path.read_text(encoding="utf-8") for path in sorted((ROOT / "apps/auth-server/drizzle").glob("*.sql")))
docs = read("docs/deployment/judge-access.md") + "\n" + read("docs/ps-042b2-judge-access-readiness-proof.md")

require("provision-judge-account" not in server, "provisioning referenced by application startup")
require("provision-judge-account" not in migrations, "provisioning referenced by migrations")
require('PROOFSTUDIO_JUDGE_PROVISIONING_APPROVED !== "true"' in provision, "exact approval gate missing")
require('["viewer", "reviewer"]' in provision, "judge roles are not bounded")
require("judge_role_refused" in provision and "owner" not in re.search(
    r"export const JUDGE_ROLES\s*=\s*(.+);", provision
).group(1), "owner/admin role is not refused")
receipt_match = re.search(r"return \{\n\s+ok: true,(.*?)\n\s+\};", provision, re.DOTALL)
require(receipt_match is not None, "sanitized receipt return missing")
receipt_code = receipt_match.group(1).lower()
for prohibited in ("database_url", "session_token", "internal_token", "credential_digest", "password_hash"):
    require(prohibited not in receipt_code, f"prohibited receipt field found: {prohibited}")

scripts = package.get("scripts", {})
for name in ("provision:judge", "smoke:judge-provisioning", "smoke:judge-access-readiness"):
    require(name in scripts, f"package script missing: {name}")
require("provision:judge" not in scripts.get("start", "") and "provision:judge" not in scripts.get("dev", ""),
        "automatic startup provisioning found")

changed = set(filter(None, git("diff", "--name-only", BASE, "--").splitlines()))
untracked: set[str] = set()
for line in git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
    if line:
        path = line[3:].split(" -> ")[-1]
        changed.add(path)
        if line.startswith("??"):
            untracked.add(path)
require(changed <= ALLOWLIST, f"changed path outside allowlist: {sorted(changed - ALLOWLIST)}")
require(not any(path.startswith("apps/auth-server/drizzle/") for path in changed), "migration file changed")
require(not any(path.endswith(("package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml")) for path in changed),
        "lockfile changed")

require(not re.search(r"PROOFSTUDIO_JUDGE_PASSWORD\s*[:=]\s*[\"'][^\"'$]", provision),
        "literal judge password found")
require("production judge account was provisioned" not in docs.lower(), "production-completion claim found")
require("render calls: 0" in docs.lower() and "provider calls: 0" in docs.lower(), "non-live counters missing")
added_text = "\n".join(
    line[1:] for line in git("diff", "--unified=0", BASE, "--").splitlines()
    if line.startswith("+") and not line.startswith("+++")
)
added_text += "\n" + "\n".join(read(path) for path in untracked if (ROOT / path).is_file())
for marker in (
    "render.com" + "/api",
    "back" + "blaze",
    "b2" + "sdk",
    "oauth" + "/authorize",
    "generative" + "language",
):
    require(marker not in added_text.lower(),
            f"live integration marker added: {marker}")

email_like = re.findall(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", docs, re.IGNORECASE)
require(not email_like, "documentation contains an email credential/example")
require(not re.search(r"(postgres(?:ql)?://)[^/\s]+:[^@\s]+@", docs, re.IGNORECASE),
        "documentation contains a database credential")

result = {
    "ok": True,
    "slice": "PS-042B2",
    "checks": {
        "explicit_operator_action": "pass",
        "approval_gate": "exact_lowercase_true",
        "roles": "viewer|reviewer",
        "sanitized_receipt": "pass",
        "package_scripts": "pass",
        "allowlist": "pass",
        "migration_changes": 0,
        "lockfile_changes": 0,
        "plaintext_judge_passwords": 0,
        "production_completion_claims": 0,
    },
    "live_operations": {
        "render_calls": 0,
        "deployments": 0,
        "paid_resource_creations": 0,
        "production_migrations": 0,
        "production_database_calls": 0,
        "production_judge_accounts_provisioned": 0,
        "external_email_sends": 0,
        "oauth_calls": 0,
        "b2_calls": 0,
        "provider_calls": 0,
        "backend_object_operations": 0,
    },
}
print(json.dumps(result, sort_keys=True))
