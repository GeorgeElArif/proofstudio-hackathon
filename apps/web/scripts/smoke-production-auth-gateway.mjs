import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import ts from "typescript";

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const authClientPath = resolve("src/authClient.ts");
const authClient = readFileSync(authClientPath, "utf8");
const authorizedProofClient = readFileSync(resolve("src/authorizedProofClient.ts"), "utf8");
const dashboardClient = readFileSync(resolve("src/dashboard/dashboardClient.ts"), "utf8");
const dashboardData = readFileSync(resolve("src/dashboard/dashboardData.ts"), "utf8");
const privateSurfaces = `${authorizedProofClient}\n${dashboardClient}\n${dashboardData}`;

const compiled = ts.transpileModule(authClient, {
  compilerOptions: {
    target: ts.ScriptTarget.ES2022,
    module: ts.ModuleKind.ESNext,
  },
  fileName: authClientPath,
}).outputText;
const moduleUrl = `data:text/javascript;base64,${Buffer.from(compiled).toString("base64")}`;
const { resolveAuthBaseUrl } = await import(moduleUrl);

assert(
  resolveAuthBaseUrl("https://auth.example.test///", true, "https://web.example.test") ===
    "https://auth.example.test",
  "explicit configured auth base must win and normalize trailing slashes",
);
assert(
  resolveAuthBaseUrl("   ", true, "https://web.example.test///") === "https://web.example.test",
  "production browser fallback must use the normalized current origin",
);
assert(
  resolveAuthBaseUrl(undefined, false, "https://web.example.test") === "http://127.0.0.1:8787",
  "non-production must preserve the local auth-server fallback",
);
let protocolRelativeRefused = false;
try {
  resolveAuthBaseUrl("//auth.example.test", true, "https://web.example.test");
} catch {
  protocolRelativeRefused = true;
}
assert(protocolRelativeRefused, "protocol-relative auth base URLs must be refused");

for (const source of [authClient, authorizedProofClient, dashboardClient]) {
  let searchFrom = 0;
  while (true) {
    const fetchAt = source.indexOf("fetch(`${getAuthBaseUrl()}", searchFrom);
    if (fetchAt === -1) break;
    const requestBlock = source.slice(fetchAt, fetchAt + 420);
    assert(requestBlock.includes('credentials: "include"'), "every auth fetch must include cookie credentials");
    searchFrom = fetchAt + 1;
  }
}

assert(!/\blocalStorage\b|\bsessionStorage\b/.test(authClient + authorizedProofClient), "browser storage authentication is forbidden");
assert(!/PROOFSTUDIO_INTERNAL_SERVICE_TOKEN/.test(authClient + privateSurfaces), "browser code must not construct the internal service token");
assert(!/getApiBaseUrl|VITE_PROOFSTUDIO_API_BASE_URL/.test(authorizedProofClient), "private reads must not target FastAPI directly");
assert(
  /if \(response\.status === 401\) return \{ state: "unauthenticated" \};/.test(authorizedProofClient) &&
    /if \(!response\.ok\) return \{ state: "error" \};/.test(authorizedProofClient),
  "authorization denial must terminate without a private-proof fallback",
);
assert(
  /response\.status === 401[^\n]*realAccountCampaigns: \[\]/.test(dashboardClient) &&
    /checked_in_fixture[\s\S]*not an authenticated account campaign/.test(dashboardData),
  "account denial must return an empty real-account list and keep fixtures explicitly separate",
);
assert(!/fetch\s*\(\s*["']https?:\/\/proofstudio-api/.test(privateSurfaces), "no private FastAPI URL may be constructed");

console.log("PS-042B1 web production auth-gateway smoke passed.");
console.log("external_http_calls=0 browser_storage_auth=0 internal_service_tokens=0 private_fastapi_reads=0");
