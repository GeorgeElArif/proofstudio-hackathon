#!/usr/bin/env python3
"""PS-042B1 local Render Blueprint and same-origin gateway contract smoke.

This check uses only the Python standard library. It parses the committed
Blueprint subset itself so duplicate mapping keys fail instead of being
silently overwritten. It performs no HTTP, provider, B2, Render, or database
operation and writes no evidence.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "render.yaml"


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
                        extra_indent = lines[index][0]
                        extra, index = parse_block(index, extra_indent)
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


def by_key(entries: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for entry in entries:
        require(isinstance(entry, dict), f"{key} entry must be a mapping")
        name = entry.get(key)
        require(isinstance(name, str) and name not in result, f"duplicate or missing {key}: {name!r}")
        result[name] = entry
    return result


def env_by_key(service: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return by_key(service.get("envVars", []), "key")


def require_service_reference(entry: dict[str, Any], name: str, env_var_key: str) -> None:
    require(
        entry.get("fromService") == {"type": "web", "name": name, "envVarKey": env_var_key},
        f"invalid service reference for {entry.get('key')}",
    )


def changed_paths() -> set[str]:
    output = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=ROOT, text=True
    )
    return {line[3:] for line in output.splitlines() if line.strip()}


def main() -> int:
    text = BLUEPRINT.read_text(encoding="utf-8")
    blueprint = parse_blueprint(text)
    require(text.count("\n    routes:\n") == 1, "static site must contain exactly one routes mapping")
    require(blueprint.get("previews") == {"generation": "off"}, "Blueprint previews must use current generation: off fields")

    services = by_key(blueprint.get("services", []), "name")
    databases = by_key(blueprint.get("databases", []), "name")
    require(set(services) == {"proofstudio-api", "proofstudio-auth", "proofstudio-web"}, "exactly three named services are required")
    require(set(databases) == {"proofstudio-db"}, "exactly one named PostgreSQL resource is required")

    api = services["proofstudio-api"]
    auth = services["proofstudio-auth"]
    web = services["proofstudio-web"]
    require(api.get("type") == "web" and api.get("runtime") == "python", "FastAPI must be a Python web service")
    require(auth.get("type") == "web" and auth.get("runtime") == "node", "auth must be a Node web service")
    require(web.get("type") == "web" and web.get("runtime") == "static", "web must use current static runtime fields")
    for service in (api, auth):
        require(service.get("region") == "oregon", "dynamic services must share the database region")
        require(service.get("plan") == "starter", "judge-facing dynamic services must be always-on starter instances")
        require(service.get("autoDeployTrigger") == "off", "automatic deployment is outside PS-042B1")
    require(web.get("autoDeployTrigger") == "off", "automatic static deployment is outside PS-042B1")

    require(api.get("healthCheckPath") == "/health", "FastAPI health check must use /health")
    require(auth.get("healthCheckPath") == "/readyz", "auth health check must use readiness")
    require(auth.get("preDeployCommand") == "npm run drizzle:migrate", "auth migrations must run as a pre-deploy gate")
    require(auth.get("buildCommand") == "npm ci --include=dev && npm run build", "auth build must install the locked dev toolchain and compile")
    require(auth.get("startCommand") == "npm run start", "auth start command mismatch")
    require(web.get("rootDir") == "apps/web" and web.get("staticPublishPath") == "dist", "static build roots mismatch")

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
    require(
        [(route.get("source"), route.get("destination")) for route in routes] == expected_routes,
        "same-origin auth rewrites must be exact and precede the SPA fallback",
    )
    require(all(route.get("type") == "rewrite" for route in routes), "all static routes must preserve the browser-visible origin")
    auth_paths = [source for source, _ in expected_routes[:-1]]
    headers = web.get("headers", [])
    require(
        [(item.get("path"), item.get("name"), item.get("value")) for item in headers]
        == [(path, "Cache-Control", "no-store") for path in auth_paths],
        "every auth-facing static path must carry Cache-Control: no-store",
    )

    api_env = env_by_key(api)
    auth_env = env_by_key(auth)
    web_env = env_by_key(web)
    for flag in (
        "PROOFSTUDIO_RUN_LIVE_DEFAULT",
        "PROOFSTUDIO_LIVE_RUNS_ENABLED",
        "PROOFSTUDIO_B2_WRITES_ENABLED",
        "PROOFSTUDIO_PAID_RUN_APPROVED",
    ):
        require(api_env.get(flag, {}).get("value") == "false", f"{flag} must remain default-off")
    require(auth_env.get("PROOFSTUDIO_AUTH_SECRET", {}).get("generateValue") is True, "auth secret must be generated")
    require(auth_env.get("PROOFSTUDIO_INTERNAL_SERVICE_TOKEN", {}).get("generateValue") is True, "internal token must be generated once")
    require_service_reference(api_env["PROOFSTUDIO_INTERNAL_SERVICE_TOKEN"], "proofstudio-auth", "PROOFSTUDIO_INTERNAL_SERVICE_TOKEN")
    require_service_reference(auth_env["PROOFSTUDIO_APP_BASE_URL"], "proofstudio-web", "RENDER_EXTERNAL_URL")
    require_service_reference(auth_env["PROOFSTUDIO_PUBLIC_WEB_URL"], "proofstudio-web", "RENDER_EXTERNAL_URL")
    require_service_reference(auth_env["PROOFSTUDIO_CORS_ORIGINS"], "proofstudio-web", "RENDER_EXTERNAL_URL")
    require_service_reference(auth_env["PROOFSTUDIO_PROOF_API_BASE_URL"], "proofstudio-api", "RENDER_EXTERNAL_URL")
    require(auth_env.get("PROOFSTUDIO_SESSION_COOKIE_SECURE", {}).get("value") == "true", "production session cookie must be secure")
    require("PROOFSTUDIO_SESSION_COOKIE_DOMAIN" not in auth_env, "cross-subdomain cookies are forbidden")
    require_service_reference(web_env["VITE_PROOFSTUDIO_AUTH_BASE_URL"], "proofstudio-web", "RENDER_EXTERNAL_URL")

    database = databases["proofstudio-db"]
    require(database.get("region") == "oregon", "database region mismatch")
    require(database.get("plan") == "basic-256mb", "managed database plan mismatch")
    require(database.get("postgresMajorVersion") == "18", "PostgreSQL major version must be explicit")
    require(database.get("ipAllowList") == [], "database public inbound access must be blocked")
    require(auth_env.get("PROOFSTUDIO_DATABASE_URL", {}).get("fromDatabase") == {"name": "proofstudio-db", "property": "connectionString"}, "auth must use the managed database connection")

    web_package = json.loads((ROOT / "apps/web/package.json").read_text(encoding="utf-8"))
    require(web_package["scripts"].get("smoke:production-auth-gateway") == "node scripts/smoke-production-auth-gateway.mjs", "web smoke script registration mismatch")
    env_template = (ROOT / ".env.production.example").read_text(encoding="utf-8")
    require("PROOFSTUDIO_SESSION_COOKIE_DOMAIN=" not in env_template, "environment template must not suggest cross-subdomain cookies")
    require(
        "PROOFSTUDIO_APP_BASE_URL=https://replace-with-web-host" in env_template,
        "environment template must use the browser-visible public web origin for auth",
    )
    require(
        "PROOFSTUDIO_APP_BASE_URL=https://replace-with-auth-host" not in env_template,
        "environment template must not point auth directly at the auth service",
    )
    require("VITE_PROOFSTUDIO_AUTH_BASE_URL=https://replace-with-web-host" in env_template, "environment template must document same-origin auth")
    auth_topology_smoke = (
        ROOT / "apps/auth-server/scripts/smoke-production-topology.ts"
    ).read_text(encoding="utf-8")
    require(
        'assert(!isAllowedCorsOrigin("http://localhost:5173", exactCorsEnv)' in auth_topology_smoke,
        "auth production-topology smoke must deny production-shaped localhost",
    )
    require(
        'assert(!isAllowedCorsOrigin("http://127.0.0.1:5173", exactCorsEnv)' in auth_topology_smoke,
        "auth production-topology smoke must deny production-shaped 127.0.0.1",
    )

    allowed = {
        "render.yaml", ".env.production.example", "apps/auth-server/package.json",
        "apps/auth-server/src/server.ts", "apps/auth-server/scripts/smoke-production-topology.ts",
        "apps/web/package.json", "apps/web/src/authClient.ts",
        "apps/web/scripts/smoke-production-auth-gateway.mjs",
        "scripts/ps042b1_render_blueprint_smoke.py", "docs/deployment/render.md",
        "docs/deployment/environment.md", "docs/deployment/cors-and-security.md",
        "docs/deployment/preflight-checklist.md",
        "docs/ps-042b1-production-topology-auth-gateway-proof.md",
    }
    changed = changed_paths()
    require(changed <= allowed, f"changed paths outside PS-042B1 allowlist: {sorted(changed - allowed)}")
    require(not any(path.endswith(("package-lock.json", "npm-shrinkwrap.json")) for path in changed), "lockfile changed")

    boundary = (ROOT / "apps/auth-server/src/auth/boundary.ts").read_text(encoding="utf-8")
    runtime_redaction_findings = re.findall(r"\b(accessToken|refreshToken|idToken):\s*\"(access_token|refresh_token|id_token)\"", boundary)
    require(len(runtime_redaction_findings) == 3, "expected three schema/redaction-shaped runtime classifications")
    changed_text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in sorted(changed) if (ROOT / path).is_file())
    forbidden_secret_shapes = [
        r"AKIA[0-9A-Z]{16}", r"sk-[A-Za-z0-9]{32,}",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    ]
    require(not any(re.search(pattern, changed_text) for pattern in forbidden_secret_shapes), "unclassified credential material found")

    print("PASS: PS-042B1 Render Blueprint and same-origin auth gateway")
    print("resources=4 services=3 databases=1 static_route_mappings=1 ordered_routes=7")
    print("classified_runtime_findings=3 classification=schema_field_mapping credential_findings=0")
    print("external_http_calls=0 render_calls=0 provider_calls=0 b2_calls=0 production_database_calls=0")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SmokeFailure as error:
        raise SystemExit(f"FAIL: {error}") from error
