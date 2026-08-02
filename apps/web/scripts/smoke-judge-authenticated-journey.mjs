// PS-042B2 — bounded, check-only authenticated judge journey inspection.
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const read = (name) => readFileSync(resolve(name), "utf8");
const app = read("src/App.tsx");
const auth = read("src/authClient.ts");
const account = read("src/AuthAccountSurface.tsx");
const dashboardClient = read("src/dashboard/dashboardClient.ts");
const dashboardSurface = read("src/dashboard/DashboardSurface.tsx");
const privateClient = read("src/authorizedProofClient.ts");
const privatePages = read("src/PrivateProofPages.tsx");
const lineage = read("src/BundleLineage.tsx");
const publicPage = read("src/PublicPassportPage.tsx");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(app.includes("AuthAccountSurface") && account.includes("submitLogin"), "login path missing");
assert(app.includes("DashboardSurface"), "dashboard route missing");
assert(auth.includes('credentials: "include"'), "auth requests must include credentials");
assert(dashboardClient.includes('credentials: "include"') && dashboardClient.includes("/account/campaigns"), "dashboard is not account scoped");
assert(privateClient.includes('credentials: "include"'), "private gateway requests must include credentials");
assert(privateClient.includes("/account/campaigns/") && privateClient.includes("/proof-room") && privateClient.includes("/passport/"), "Proof Room/Passport gateway paths missing");
assert(privateClient.includes("/lineage") && privateClient.includes("fetchCampaignLineageBundle") && privateClient.includes("fetchCampaignLineagePassport"), "lineage gateway paths missing");
assert(!privateClient.includes("getApiBaseUrl") && !privateClient.includes("localhost:8000") && !privateClient.includes("127.0.0.1:8000"), "direct private FastAPI read found");

const browserAuthCode = [auth, account, dashboardClient, dashboardSurface, privateClient, privatePages, lineage].join("\n");
assert(!browserAuthCode.includes("PROOFSTUDIO_INTERNAL_SERVICE_TOKEN") &&
  !browserAuthCode.includes("X-ProofStudio-Internal-Token") &&
  !browserAuthCode.includes("X-ProofStudio-Import-Token"), "service/operator token found in browser code");
assert(!/\b(?:localStorage|sessionStorage)\s*[.\[]/.test(browserAuthCode), "browser-storage authentication found");
assert(privateClient.includes("response.status === 401") &&
  privateClient.includes("response.status === 404") &&
  privateClient.includes("response.status === 503") &&
  privateClient.includes("if (!response.ok)") &&
  !/from\s+[\"'][^\"']*fixtures?/.test(privateClient), "private denial handling/fallback contract missing");
assert(privatePages.includes("No fixture fallback was used"), "private denial UI does not state no fallback");
assert(auth.includes("getAuthSession") && auth.includes("submitLogout") && account.includes("submitLogout"), "session readback/logout missing");
assert(publicPage.includes("getPublicPassportRunId") && app.includes("getPublicPassportRunId"), "public credential-free journey missing");

console.log(JSON.stringify({
  ok: true,
  slice: "PS-042B2",
  smoke: "judge_authenticated_web_journey",
  checks: {
    login: "pass",
    dashboard: "pass",
    credentials_include: "pass",
    account_scoped_campaigns: "pass",
    proof_gateway: "pass",
    lineage_gateway: "pass",
    direct_private_fastapi: "absent",
    browser_service_token: "absent",
    browser_storage_auth: "absent",
    denial_fallback: "absent",
    logout_session_readback: "pass",
    public_credential_free_journey: "preserved",
  },
}));
