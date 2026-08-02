import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { pathToFileURL } from "node:url";
import { Readable } from "node:stream";

import { createAuthBoundaryRuntime } from "./auth/boundary.js";
import { createAuthDatabase } from "./db/client.js";
import { getAuthRuntimeReadiness, loadAuthRuntimeEnv, type AuthRuntimeEnv } from "./env.js";
import { buildHealthPayload } from "./routes/health.js";

const env = loadAuthRuntimeEnv();

export type AuthServerBinding = {
  port: number;
  host: string;
};

function parsePort(rawValue: string, variableName: string): number {
  if (!/^[0-9]+$/.test(rawValue)) {
    throw new Error(`${variableName} must be an integer from 1 through 65535`);
  }
  const parsed = Number(rawValue);
  if (!Number.isSafeInteger(parsed) || parsed < 1 || parsed > 65535) {
    throw new Error(`${variableName} must be an integer from 1 through 65535`);
  }
  return parsed;
}

export function resolveAuthServerBinding(runtimeEnv: NodeJS.ProcessEnv = process.env): AuthServerBinding {
  const selectedPort =
    runtimeEnv.PORT !== undefined
      ? { name: "PORT", value: runtimeEnv.PORT }
      : runtimeEnv.PROOFSTUDIO_AUTH_SERVER_PORT !== undefined
        ? { name: "PROOFSTUDIO_AUTH_SERVER_PORT", value: runtimeEnv.PROOFSTUDIO_AUTH_SERVER_PORT }
        : { name: "default port", value: "8787" };
  const explicitHost = runtimeEnv.PROOFSTUDIO_AUTH_SERVER_HOST?.trim();
  const production = runtimeEnv.PROOFSTUDIO_ENV?.trim().toLowerCase() === "production";

  return {
    port: parsePort(selectedPort.value, selectedPort.name),
    host: explicitHost || (production ? "0.0.0.0" : "127.0.0.1"),
  };
}

async function checkDatabaseReachable(): Promise<{ reachable: boolean | null; error?: string }> {
  const envOnlyReadiness = getAuthRuntimeReadiness(env);
  if (!envOnlyReadiness.envConfigured) {
    return { reachable: null };
  }

  const database = createAuthDatabase(env.databaseUrl);
  try {
    await database.checkReady();
    return { reachable: true };
  } catch {
    return { reachable: false, error: "database_unreachable" };
  } finally {
    await database.close();
  }
}

function copyResponseHeaders(source: Response, target: ServerResponse): void {
  source.headers.forEach((value, key) => {
    if (key.toLowerCase() !== "set-cookie") {
      target.setHeader(key, value);
    }
  });
  const setCookies = (
    source.headers as Headers & { getSetCookie?: () => string[] }
  ).getSetCookie?.() ?? [];
  if (setCookies.length > 0) {
    target.setHeader("set-cookie", setCookies);
  }
}

function isLocalDevOrigin(origin: string): boolean {
  try {
    const parsed = new URL(origin);
    return (
      (parsed.hostname === "127.0.0.1" || parsed.hostname === "localhost") &&
      (parsed.protocol === "http:" || parsed.protocol === "https:")
    );
  } catch {
    return false;
  }
}

export function isAllowedCorsOrigin(origin: string, runtimeEnv: AuthRuntimeEnv = env): boolean {
  if (origin === "*") {
    return false;
  }
  const allowLocalDev =
    runtimeEnv.publicWebUrl === "" || isLocalDevOrigin(runtimeEnv.publicWebUrl);
  return (
    origin === runtimeEnv.publicWebUrl ||
    runtimeEnv.corsAllowedOrigins.filter((candidate) => candidate !== "*").includes(origin) ||
    (allowLocalDev && isLocalDevOrigin(origin))
  );
}

function applyCors(request: IncomingMessage, response: ServerResponse): void {
  const origin = request.headers.origin;
  if (!origin || Array.isArray(origin) || !isAllowedCorsOrigin(origin)) {
    return;
  }

  response.setHeader("access-control-allow-origin", origin);
  response.setHeader("access-control-allow-credentials", "true");
  response.setHeader("access-control-allow-methods", "GET,POST,OPTIONS");
  response.setHeader("access-control-allow-headers", "content-type,authorization");
  response.setHeader("vary", "origin");
}

export async function writeWebResponse(
  webResponse: Response,
  request: IncomingMessage,
  response: ServerResponse,
): Promise<void> {
  response.statusCode = webResponse.status;
  copyResponseHeaders(webResponse, response);
  applyCors(request, response);
  applyNoStore(response);
  const body = await webResponse.arrayBuffer();
  response.end(Buffer.from(body));
}

function writeJson(request: IncomingMessage, response: ServerResponse, status: number, payload: unknown): void {
  applyCors(request, response);
  response.writeHead(status, { "content-type": "application/json" });
  response.end(JSON.stringify(payload));
}

export function toWebRequest(request: IncomingMessage): Request {
  const url = new URL(request.url ?? "/", `http://${request.headers.host ?? "localhost"}`);
  const headers = new Headers();

  for (const [key, value] of Object.entries(request.headers)) {
    if (Array.isArray(value)) {
      for (const item of value) {
        headers.append(key, item);
      }
    } else if (value !== undefined) {
      headers.set(key, value);
    }
  }

  const method = request.method ?? "GET";
  if (method === "GET" || method === "HEAD") {
    return new Request(url, { method, headers });
  }

  return new Request(url, {
    method,
    headers,
    body: Readable.toWeb(request) as RequestInit["body"],
    duplex: "half",
  } as RequestInit & { duplex: "half" });
}

export function isAuthFacingPath(pathname: string): boolean {
  return (
    pathname.startsWith("/auth/") ||
    pathname === "/session" ||
    pathname === "/logout" ||
    pathname.startsWith("/account/") ||
    pathname === "/healthz" ||
    pathname === "/readyz"
  );
}

function applyNoStore(response: ServerResponse): void {
  response.setHeader("cache-control", "no-store");
  response.setHeader("pragma", "no-cache");
}

const authBoundary = createAuthBoundaryRuntime(env, (databaseReachable, databaseError) =>
  getAuthRuntimeReadiness(env, databaseReachable, databaseError),
);

const server = createServer((request, response) => {
  void (async () => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host ?? "localhost"}`);
    if (isAuthFacingPath(url.pathname)) {
      applyNoStore(response);
    }

    if (request.method === "OPTIONS") {
      response.statusCode = 204;
      applyCors(request, response);
      response.end();
      return;
    }

    if (url.pathname === "/healthz") {
      const readiness = authBoundary.getReadiness(null);
      const payload = buildHealthPayload(readiness, readiness.authRuntimeAvailable);
      writeJson(request, response, 200, payload);
      return;
    }

    if (url.pathname === "/readyz") {
      const database = await checkDatabaseReachable();
      const readiness = authBoundary.getReadiness(database.reachable, database.error);
      const payload = buildHealthPayload(readiness, readiness.authRuntimeAvailable);
      writeJson(request, response, payload.ready ? 200 : 503, payload);
      return;
    }

    if (url.pathname === "/session" || url.pathname === "/auth/session") {
      await writeWebResponse(await authBoundary.handleSessionReadback(toWebRequest(request)), request, response);
      return;
    }

    if (url.pathname === "/logout") {
      await writeWebResponse(await authBoundary.handleLogoutRequest(toWebRequest(request)), request, response);
      return;
    }

    if (url.pathname === "/account/campaigns" && request.method === "GET") {
      await writeWebResponse(await authBoundary.handleAccountCampaigns(toWebRequest(request)), request, response);
      return;
    }

    const proofRoomMatch = url.pathname.match(/^\/account\/campaigns\/([^/]+)\/proof-room$/);
    if (proofRoomMatch && request.method === "GET") {
      let campaignId = "";
      try { campaignId = decodeURIComponent(proofRoomMatch[1]); } catch { /* rejected by boundary */ }
      await writeWebResponse(await authBoundary.handlePrivateProofRoom(toWebRequest(request), campaignId), request, response);
      return;
    }

    const passportMatch = url.pathname.match(/^\/account\/campaigns\/([^/]+)\/passport\/([^/]+)$/);
    if (passportMatch && request.method === "GET") {
      let campaignId = "";
      let runId = "";
      try {
        campaignId = decodeURIComponent(passportMatch[1]);
        runId = decodeURIComponent(passportMatch[2]);
      } catch { /* rejected by boundary */ }
      await writeWebResponse(await authBoundary.handlePrivatePassport(toWebRequest(request), campaignId, runId), request, response);
      return;
    }

    const lineagePassportMatch = url.pathname.match(/^\/account\/campaigns\/([^/]+)\/lineage\/([^/]+)\/passport$/);
    if (lineagePassportMatch && request.method === "GET") {
      let campaignId = ""; let bundleId = "";
      try { campaignId = decodeURIComponent(lineagePassportMatch[1]); bundleId = decodeURIComponent(lineagePassportMatch[2]); } catch { /* rejected */ }
      await writeWebResponse(await authBoundary.handlePrivateLineagePassport(toWebRequest(request), campaignId, bundleId), request, response);
      return;
    }

    const lineageBundleMatch = url.pathname.match(/^\/account\/campaigns\/([^/]+)\/lineage\/([^/]+)$/);
    if (lineageBundleMatch && request.method === "GET") {
      let campaignId = ""; let bundleId = "";
      try { campaignId = decodeURIComponent(lineageBundleMatch[1]); bundleId = decodeURIComponent(lineageBundleMatch[2]); } catch { /* rejected */ }
      await writeWebResponse(await authBoundary.handlePrivateLineage(toWebRequest(request), campaignId, bundleId), request, response);
      return;
    }

    const lineageListMatch = url.pathname.match(/^\/account\/campaigns\/([^/]+)\/lineage$/);
    if (lineageListMatch && request.method === "GET") {
      let campaignId = "";
      try { campaignId = decodeURIComponent(lineageListMatch[1]); } catch { /* rejected */ }
      await writeWebResponse(await authBoundary.handlePrivateLineage(toWebRequest(request), campaignId), request, response);
      return;
    }

    if (url.pathname.startsWith("/auth/")) {
      await writeWebResponse(await authBoundary.handleAuthRequest(toWebRequest(request)), request, response);
      return;
    }

    writeJson(request, response, 404, { error: "not_found" });
  })().catch(() => {
    writeJson(request, response, 500, { error: "internal_error" });
  });
});

export function startAuthServer(runtimeEnv: NodeJS.ProcessEnv = process.env): void {
  const { port, host } = resolveAuthServerBinding(runtimeEnv);
  server.listen(port, host, () => {
    console.log(`proofstudio-auth-server listening on http://${host}:${port}`);
  });
}

process.on("SIGTERM", () => {
  server.close(() => {
    void authBoundary.close().finally(() => {
      process.exit(0);
    });
  });
});

const entrypoint = process.argv[1];
if (entrypoint && import.meta.url === pathToFileURL(entrypoint).href) {
  startAuthServer();
}
