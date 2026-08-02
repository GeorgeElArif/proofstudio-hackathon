import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const contract = readFileSync(resolve("src/dashboard/dashboardData.ts"), "utf8");
const client = readFileSync(resolve("src/dashboard/dashboardClient.ts"), "utf8");

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

for (const label of [
  "auth_session",
  "proof_api",
  "checked_in_fixture",
  "demo_fixture",
  "unavailable",
  "not_implemented",
]) {
  assert(contract.includes(`"${label}"`), `dashboard contract should include ${label}`);
}

for (const entity of [
  "DashboardSessionState",
  "DashboardCampaignSummary",
  "DashboardProofLayerStatus",
  "DashboardAction",
  "DashboardDataSourceLabel",
  "DashboardUnavailableReason",
]) {
  assert(contract.includes(entity), `dashboard contract should export ${entity}`);
}

assert(
  contract.includes("accountOwned: false"),
  "campaign summaries should not be representable as account-owned in PS-041A",
);
assert(
  client.includes("ACCOUNT_CAMPAIGN_LIST_NOT_IMPLEMENTED_SOURCE"),
  "dashboard client should source the campaign list from the not-implemented label",
);
assert(
  client.includes("realAccountCampaigns: []"),
  "dashboard client should not return real account campaign rows",
);
assert(
  client.includes("getAuthSession()"),
  "dashboard client should use server session readback",
);
assert(
  !client.includes("localStorage") && !client.includes("sessionStorage"),
  "dashboard client must not use browser storage for auth state",
);
assert(
  !client.includes("authenticated: true"),
  "dashboard client must not force an authenticated state",
);

console.log("PS-041A dashboard contract smoke passed.");
