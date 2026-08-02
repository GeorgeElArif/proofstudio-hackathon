import { readFile } from "node:fs/promises";
import type { IncomingMessage, ServerResponse } from "node:http";
import { join } from "node:path";
import { Readable } from "node:stream";

import { loadAuthRuntimeEnv } from "../src/env.js";
import {
  isAllowedCorsOrigin,
  isAuthFacingPath,
  resolveAuthServerBinding,
  toWebRequest,
  writeWebResponse,
} from "../src/server.js";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

function expectInvalidPort(value: string): void {
  let refused = false;
  try {
    resolveAuthServerBinding({
      PORT: value,
      PROOFSTUDIO_AUTH_SERVER_PORT: "8787",
    });
  } catch {
    refused = true;
  }
  assert(refused, `invalid PORT must be refused: ${JSON.stringify(value)}`);
}

class SyntheticServerResponse {
  statusCode = 200;
  readonly headers = new Map<string, string | string[] | number>();
  body = Buffer.alloc(0);

  setHeader(name: string, value: string | readonly string[] | number): this {
    this.headers.set(name.toLowerCase(), Array.isArray(value) ? [...value] : value as string | number);
    return this;
  }

  end(chunk?: Uint8Array | string): this {
    this.body = chunk === undefined ? Buffer.alloc(0) : Buffer.from(chunk);
    return this;
  }
}

function syntheticRequest(
  url: string,
  method: string,
  body: Buffer = Buffer.alloc(0),
  headers: Record<string, string> = {},
): IncomingMessage {
  const request = Readable.from(body) as unknown as IncomingMessage;
  request.url = url;
  request.method = method;
  request.headers = { host: "auth.test", ...headers };
  return request;
}

const portWins = resolveAuthServerBinding({
  PORT: "4321",
  PROOFSTUDIO_AUTH_SERVER_PORT: "9876",
});
assert(portWins.port === 4321, "PORT must win over PROOFSTUDIO_AUTH_SERVER_PORT");
assert(
  resolveAuthServerBinding({ PROOFSTUDIO_AUTH_SERVER_PORT: "9876" }).port === 9876,
  "PROOFSTUDIO_AUTH_SERVER_PORT must win over the local default",
);
assert(resolveAuthServerBinding({}).port === 8787, "the local port default must remain 8787");
for (const invalid of ["", "abc", "1x", "0", "-1", "1.5", "65536", "999999999999999999999"]) {
  expectInvalidPort(invalid);
}

assert(
  resolveAuthServerBinding({ PROOFSTUDIO_ENV: "production" }).host === "0.0.0.0",
  "production must default to 0.0.0.0",
);
assert(
  resolveAuthServerBinding({ PROOFSTUDIO_ENV: "development" }).host === "127.0.0.1",
  "non-production must default to 127.0.0.1",
);
assert(
  resolveAuthServerBinding({
    PROOFSTUDIO_ENV: "production",
    PROOFSTUDIO_AUTH_SERVER_HOST: "10.20.30.40",
  }).host === "10.20.30.40",
  "an explicit auth-server host must win",
);

const forwardedBytes = Buffer.from([0, 1, 2, 3, 254, 255]);
const forwarded = toWebRequest(
  syntheticRequest(
    "/auth/sign-in/email?next=%2Faccount%2Fcampaigns&mode=test",
    "POST",
    forwardedBytes,
    {
      "content-type": "application/octet-stream",
      cookie: "proofstudio_session=synthetic-cookie",
      origin: "https://web.example.test",
    },
  ),
);
assert(forwarded.method === "POST", "request method must be preserved");
assert(
  new URL(forwarded.url).search === "?next=%2Faccount%2Fcampaigns&mode=test",
  "query string must be preserved",
);
assert(forwarded.headers.get("content-type") === "application/octet-stream", "content type must be forwarded");
assert(forwarded.headers.get("cookie") === "proofstudio_session=synthetic-cookie", "cookie must be forwarded");
assert(forwarded.headers.get("origin") === "https://web.example.test", "origin must be forwarded");
assert(
  Buffer.from(await forwarded.arrayBuffer()).equals(forwardedBytes),
  "request body bytes must be preserved",
);

const responseHeaders = new Headers({ "content-type": "application/octet-stream" });
responseHeaders.append("set-cookie", "first=synthetic; Path=/; HttpOnly");
responseHeaders.append("set-cookie", "second=synthetic; Path=/; HttpOnly");
const target = new SyntheticServerResponse();
await writeWebResponse(
  new Response(forwardedBytes, { status: 207, headers: responseHeaders }),
  syntheticRequest("/auth/callback?state=synthetic", "GET"),
  target as unknown as ServerResponse,
);
assert(target.statusCode === 207, "Better Auth response status must be preserved");
assert(target.body.equals(forwardedBytes), "Better Auth response body bytes must be preserved");
assert(target.headers.get("content-type") === "application/octet-stream", "response content type must be preserved");
assert(target.headers.get("cache-control") === "no-store", "auth response must be no-store");
assert(target.headers.get("pragma") === "no-cache", "auth response must disable legacy caches");
const setCookies = target.headers.get("set-cookie");
assert(Array.isArray(setCookies) && setCookies.length === 2, "multiple Set-Cookie headers must be preserved");

for (const path of ["/auth/sign-in/email", "/session", "/logout", "/account/campaigns", "/healthz", "/readyz"]) {
  assert(isAuthFacingPath(path), `auth-facing route must be classified for no-store: ${path}`);
}
assert(!isAuthFacingPath("/assets/app.js"), "immutable frontend assets must not be classified as auth-facing");

const exactCorsEnv = loadAuthRuntimeEnv({
  PROOFSTUDIO_PUBLIC_WEB_URL: "https://web.example.test",
  PROOFSTUDIO_CORS_ORIGINS: "https://review.example.test,*",
});
assert(isAllowedCorsOrigin("https://web.example.test", exactCorsEnv), "public web origin must be allowed exactly");
assert(isAllowedCorsOrigin("https://review.example.test", exactCorsEnv), "configured origin must be allowed exactly");
assert(!isAllowedCorsOrigin("https://other.example.test", exactCorsEnv), "unconfigured origin must be refused");
assert(!isAllowedCorsOrigin("http://localhost:5173", exactCorsEnv), "production-shaped localhost origin must be refused");
assert(!isAllowedCorsOrigin("http://127.0.0.1:5173", exactCorsEnv), "production-shaped 127.0.0.1 origin must be refused");
assert(!isAllowedCorsOrigin("*", exactCorsEnv), "wildcard CORS must be refused");

const localCorsEnv = loadAuthRuntimeEnv({
  PROOFSTUDIO_PUBLIC_WEB_URL: "http://127.0.0.1:5173",
});
assert(isAllowedCorsOrigin("http://127.0.0.1:5173", localCorsEnv), "configured local public web origin must be allowed");
assert(isAllowedCorsOrigin("http://localhost:5173", localCorsEnv), "alternate localhost origin must be allowed for local-shaped configuration");

const serverSource = await readFile(join(process.cwd(), "src/server.ts"), "utf8");
const boundarySource = await readFile(join(process.cwd(), "src/auth/boundary.ts"), "utf8");
const blueprintSource = await readFile(join(process.cwd(), "..", "..", "render.yaml"), "utf8");
assert(
  /if \(isAuthFacingPath\(url\.pathname\)\) \{\s*applyNoStore\(response\);/s.test(serverSource),
  "every auth-facing server route must receive no-store headers before dispatch",
);
assert(/trustedOrigins:\s*\[env\.publicWebUrl,\s*\.\.\.env\.corsAllowedOrigins\]/s.test(boundarySource), "Better Auth must retain exact trusted origins");
assert(!/disable(?:CSRF|Origin)\w*\s*:\s*true/i.test(boundarySource), "Better Auth CSRF/origin checks must not be disabled");
assert(!/trustedOrigins\s*:\s*\[\s*["']\*["']\s*\]/.test(boundarySource), "Better Auth trusted origins must not be wildcarded");
assert(!/PROOFSTUDIO_SESSION_COOKIE_DOMAIN/.test(blueprintSource), "the production Blueprint must not enable cross-subdomain cookies");

console.log("PS-042B1 auth production-topology smoke passed.");
console.log("external_http_calls=0 provider_calls=0 b2_calls=0 production_database_calls=0");
