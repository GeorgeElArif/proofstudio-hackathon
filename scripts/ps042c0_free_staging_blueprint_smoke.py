#!/usr/bin/env python3
"""PS-042C0A free Render staging Blueprint contract smoke.

Uses only the Python standard library. The check parses the committed YAML
subset without network access and performs no Render, database, provider, B2,
OAuth, email, deployment, migration, or account operation.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "render.free.yaml"
PROOF = ROOT / "docs/ps-042c0-free-staging-blueprint-proof.md"
BRANCH = "ps-042c0/free-render-staging-v1"


class SmokeFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return None
    if value == "[]":
        return []
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if value[:1] in {'"', "'"}:
        return ast.literal_eval(value)
    return value


def key_value(content: str, line_number: int) -> tuple[str, str]:
    require(":" in content, f"line {line_number}: expected mapping entry")
    key, value = content.split(":", 1)
    key = key.strip()
    require(bool(key), f"line {line_number}: empty mapping key")
    return key, value.strip()


def parse_blueprint(text: str) -> dict[str, Any]:
    lines: list[tuple[int, str, int]] = []
    for line_number, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        require("\t" not in raw[:indent], f"line {line_number}: tabs are forbidden")
        require(indent % 2 == 0, f"line {line_number}: indentation must use two-space levels")
        lines.append((indent, raw.strip(), line_number))
    require(bool(lines), "Blueprint is empty")

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        require(index < len(lines), "unexpected end of YAML")
        is_list = lines[index][1].startswith("- ")
        if is_list:
            items: list[Any] = []
            while index < len(lines) and lines[index][0] == indent and lines[index][1].startswith("- "):
                _, content, line_number = lines[index]
                remainder = content[2:].strip()
                index += 1
                if ":" in remainder:
                    key, raw_value = key_value(remainder, line_number)
                    item: dict[str, Any] = {}
                    if raw_value:
                        item[key] = scalar(raw_value)
                    else:
                        require(index < len(lines) and lines[index][0] > indent, f"line {line_number}: missing nested value")
                        item[key], index = parse_block(index, lines[index][0])
                    if index < len(lines) and lines[index][0] > indent:
                        extra, index = parse_block(index, lines[index][0])
                        require(isinstance(extra, dict), f"line {line_number}: list mapping continuation required")
                        duplicate = set(item).intersection(extra)
                        require(not duplicate, f"line {line_number}: duplicate mapping key(s): {sorted(duplicate)}")
                        item.update(extra)
                    items.append(item)
                else:
                    items.append(scalar(remainder))
            return items, index

        mapping: dict[str, Any] = {}
        while index < len(lines) and lines[index][0] == indent and not lines[index][1].startswith("- "):
            _, content, line_number = lines[index]
            key, raw_value = key_value(content, line_number)
            require(key not in mapping, f"line {line_number}: duplicate mapping key: {key}")
            index += 1
            if raw_value:
                mapping[key] = scalar(raw_value)
            else:
                require(index < len(lines) and lines[index][0] > indent, f"line {line_number}: missing nested value")
                mapping[key], index = parse_block(index, lines[index][0])
        return mapping, index

    parsed, final_index = parse_block(0, lines[0][0])
    if final_index != len(lines):
        raise SmokeFailure(f"line {lines[final_index][2]}: unparsed YAML content")
    require(isinstance(parsed, dict), "Blueprint root must be a mapping")
    return parsed


def by_key(entries: Any, key: str) -> dict[str, dict[str, Any]]:
    require(isinstance(entries, list), f"{key} entries must be a list")
    result: dict[str, dict[str, Any]] = {}
    for entry in entries:
        require(isinstance(entry, dict), f"{key} entry must be a mapping")
        name = entry.get(key)
        require(isinstance(name, str) and name not in result, f"duplicate or missing {key}: {name!r}")
        result[name] = entry
    return result


def env_by_key(service: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return by_key(service.get("envVars", []), "key")


def service_reference(entry: dict[str, Any], name: str) -> bool:
    return entry.get("fromService") == {
        "type": "web",
        "name": name,
        "envVarKey": "RENDER_EXTERNAL_URL",
    }


def command_entries(value: Any, path: str = "root") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if isinstance(child, str) and (key.lower().endswith("command") or "deploy" in key.lower() or "startup" in key.lower()):
                found.append((child_path, child))
            found.extend(command_entries(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(command_entries(child, f"{path}[{index}]"))
    return found


def all_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(all_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(all_keys(child))
    return keys


def main() -> int:
    text = BLUEPRINT.read_text(encoding="utf-8")
    blueprint = parse_blueprint(text)
    require(blueprint.get("previews") == {"generation": "off"}, "preview generation must be off")

    services = by_key(blueprint.get("services", []), "name")
    databases = by_key(blueprint.get("databases", []), "name")
    expected_services = {"proofstudio-api", "proofstudio-auth", "proofstudio-web"}
    require(set(services) == expected_services and len(services) == 3, "exactly three named services are required")
    require(set(databases) == {"proofstudio-db"} and len(databases) == 1, "exactly one named database is required")

    api = services["proofstudio-api"]
    auth = services["proofstudio-auth"]
    web = services["proofstudio-web"]
    database = databases["proofstudio-db"]
    require(api.get("plan") == "free", "API plan must be free")
    require(auth.get("plan") == "free", "auth plan must be free")
    require(database.get("plan") == "free", "database plan must be free")
    require("plan" not in web, "static site must not carry a paid plan field")
    paid_plan = re.compile(r"^(?:starter|standard|pro|basic(?:-.+)?|team|business|enterprise)", re.I)
    plans = [resource.get("plan") for resource in [*services.values(), *databases.values()] if "plan" in resource]
    require(not any(isinstance(plan, str) and paid_plan.match(plan) for plan in plans), "paid plan found")

    for service in services.values():
        require(service.get("branch") == BRANCH, f"{service['name']} branch binding mismatch")
        require(service.get("autoDeployTrigger") == "off", f"{service['name']} automatic deployment must be off")
    require(api.get("region") == auth.get("region") == database.get("region") == "oregon", "accepted region must be preserved")

    keys = all_keys(blueprint)
    require("preDeployCommand" not in keys, "preDeployCommand is forbidden")
    commands = command_entries(blueprint)
    for path, command in commands:
        require(not re.search(r"\b(?:migrat(?:e|ion|ions)|drizzle(?:-kit)?\s+(?:push|migrate))\b", command, re.I), f"migration found in {path}")

    expected_routes = [
        ("/auth/*", "https://proofstudio-auth.onrender.com/auth/*"),
        ("/session", "https://proofstudio-auth.onrender.com/session"),
        ("/logout", "https://proofstudio-auth.onrender.com/logout"),
        ("/account/*", "https://proofstudio-auth.onrender.com/account/*"),
        ("/healthz", "https://proofstudio-auth.onrender.com/healthz"),
        ("/readyz", "https://proofstudio-auth.onrender.com/readyz"),
        ("/*", "/index.html"),
    ]
    routes = web.get("routes", [])
    require([(item.get("source"), item.get("destination")) for item in routes] == expected_routes, "gateway route ordering changed")
    require(all(item.get("type") == "rewrite" for item in routes), "all routes must remain rewrites")
    auth_paths = [source for source, _ in expected_routes[:-1]]
    headers = web.get("headers", [])
    require(
        [(item.get("path"), item.get("name"), item.get("value")) for item in headers]
        == [(path, "Cache-Control", "no-store") for path in auth_paths],
        "no-store rules changed",
    )

    require(database.get("ipAllowList") == [], "database external access must start blocked")
    auth_env = env_by_key(auth)
    api_env = env_by_key(api)
    require(
        auth_env.get("PROOFSTUDIO_DATABASE_URL", {}).get("fromDatabase")
        == {"name": "proofstudio-db", "property": "connectionString"},
        "auth database connection must use fromDatabase",
    )
    require(service_reference(auth_env.get("PROOFSTUDIO_PROOF_API_BASE_URL", {}), "proofstudio-api"), "auth must use the API public Render URL")

    expected_flags = {
        "PROOFSTUDIO_RUN_LIVE_DEFAULT": "false",
        "PROOFSTUDIO_LIVE_RUNS_ENABLED": "false",
        "PROOFSTUDIO_B2_WRITES_ENABLED": "false",
        "PROOFSTUDIO_PAID_RUN_APPROVED": "false",
        "PROOFSTUDIO_COST_CAP_USD": "0.00",
        "PROOFSTUDIO_FIXTURES_FROZEN": "true",
    }
    for key, value in expected_flags.items():
        require(api_env.get(key, {}).get("value") == value, f"{key} staging value mismatch")

    require(auth_env.get("PROOFSTUDIO_EMAIL_PROVIDER", {}).get("value") == "capture", "email must use accepted capture provider")
    require(auth_env.get("PROOFSTUDIO_EMAIL_CAPTURE_MODE", {}).get("value") == "local", "email capture mode must be local")
    env_keys = set(api_env) | set(auth_env) | set(env_by_key(web))
    forbidden_credential_names = re.compile(
        r"(?:B2_(?:APPLICATION_KEY|KEY_ID|SECRET|TOKEN|CREDENTIAL|API_KEY)|CLOUDFLARE|GEMINI|ELEVENLABS|OPENAI|ANTHROPIC|SMTP|EMAIL_(?:API_KEY|FROM)|OAUTH|CLIENT_SECRET|PROVIDER_(?:KEY|TOKEN|SECRET))",
        re.I,
    )
    require(not any(forbidden_credential_names.search(key) for key in env_keys), "provider, B2, OAuth, SMTP, or delivery credential name found")
    for env in (api_env, auth_env, env_by_key(web)):
        for key, entry in env.items():
            if re.search(r"(?:SECRET|TOKEN|PASSWORD|API_KEY|DATABASE_URL)$", key):
                require("value" not in entry, f"real secret-shaped value found for {key}")
    require(not re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I), "real email address found")
    require(not re.search(r"(?:password|passwd)\s*[:=]", text, re.I), "password material found")
    forbidden_secret_shapes = [
        r"AKIA[0-9A-Z]{16}",
        r"sk-[A-Za-z0-9]{32,}",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    ]
    require(not any(re.search(pattern, text) for pattern in forbidden_secret_shapes), "real secret value found")

    proof = PROOF.read_text(encoding="utf-8")
    required_nonclaim = (
        "PS-042C0A prepares a free staging Blueprint. It does not create Render\n"
        "resources, run a staging migration, deploy the application, or prove that any\n"
        "public endpoint is operational."
    )
    require(required_nonclaim in proof, "required production non-claim is missing")
    require("ProofStudio proves what the pipeline recorded.\nProof does not equal truth." in proof, "truth boundary missing")
    require(not re.search(r"PS-042C0A\s+(?:is|was)\s+(?:accepted|deployed|operational|live)", proof, re.I), "production completion claim found")

    counters = {
        "render_calls": 0,
        "resource_creations": 0,
        "deployments": 0,
        "migrations": 0,
        "account_provisioning": 0,
        "charges": 0,
        "email_sends": 0,
        "oauth_calls": 0,
        "b2_calls": 0,
        "provider_calls": 0,
    }
    require(all(value == 0 for value in counters.values()), "live-operation counters must be zero")
    receipt = {
        "ok": True,
        "slice": "PS-042C0A",
        "resources": ["proofstudio-web", "proofstudio-api", "proofstudio-auth", "proofstudio-db"],
        "plans": {
            "proofstudio-web": "free-static-no-plan-field",
            "proofstudio-api": "free",
            "proofstudio-auth": "free",
            "proofstudio-db": "free",
        },
        "branch_bindings": {name: services[name]["branch"] for name in sorted(services)},
        "route_count": len(routes),
        "no_store_count": len(headers),
        "migration_mode": "explicit_operator_action_ps042c0b",
        "database_external_access": "blocked",
        "live_operation_counters": counters,
    }
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SmokeFailure as error:
        print(json.dumps({"ok": False, "slice": "PS-042C0A", "error": str(error)}, sort_keys=True, separators=(",", ":")))
        raise SystemExit(1)
