import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import ts from "typescript";

const data = await readFile(new URL("../src/dashboard/dashboardData.ts", import.meta.url), "utf8");
const client = await readFile(new URL("../src/dashboard/dashboardClient.ts", import.meta.url), "utf8");
const ui = await readFile(new URL("../src/dashboard/DashboardSurface.tsx", import.meta.url), "utf8");
const parserSource = await readFile(new URL("../src/dashboard/dashboardCampaignPayload.ts", import.meta.url), "utf8");
const parserJavaScript = ts.transpileModule(parserSource, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 },
}).outputText;
const parserModule = await import(`data:text/javascript;base64,${Buffer.from(parserJavaScript).toString("base64")}`);
const { parseAccountCampaignListPayload } = parserModule;

assert.match(data, /account_campaign_store/);
for (const state of ["unauthenticated", "unavailable", "available_empty", "available", "error"]) assert.match(data, new RegExp(state));
assert.match(client, /\/account\/campaigns/);
assert.match(client, /credentials: "include"/);
assert.doesNotMatch(client + ui, /localStorage|sessionStorage/);
assert.match(ui, /does not imply legal ownership or authorship/);
assert.match(ui, /href="\/account">Sign in/);
assert.match(ui, /checked_in_fixture.*is not account-owned and is not inserted into the real account campaign list/i);
assert.doesNotMatch(ui, /Missing source — account campaign ownership\/list/);
assert.doesNotMatch(ui, /Why this is unavailable/);
assert.match(ui, /Available · 0 mappings/);
assert.match(ui, /checked_in_fixture · not account-linked/);
for (const label of [
  "Why sign-in is required", "About this empty list", "About access and proof details",
  "Why this source is unavailable", "Why this request failed",
]) assert.match(ui, new RegExp(label));

const validItem = {
  campaignId: "campaign-a",
  latestRunId: "run-a",
  campaignAccessRole: "owner",
  linkedAt: "2026-07-14T08:00:00.000Z",
  updatedAt: "2026-07-14T09:00:00.000Z",
  source: "account_campaign_store",
  proofDetailState: "not_fetched",
};
const validPayload = {
  state: "available",
  source: "account_campaign_store",
  items: [validItem],
  pageInfo: { hasMore: false, nextCursor: null },
};
assert.deepEqual(parseAccountCampaignListPayload(validPayload)?.items, [validItem]);

const malformedPayloads = [
  { ...validPayload, state: "unavailable" },
  { ...validPayload, source: "checked_in_fixture" },
  { ...validPayload, items: [{ ...validItem, campaignId: "  " }] },
  { ...validPayload, items: [{ ...validItem, latestRunId: "" }] },
  { ...validPayload, items: [{ ...validItem, campaignAccessRole: "admin" }] },
  { ...validPayload, items: [{ ...validItem, source: "proof_api" }] },
  { ...validPayload, items: [{ ...validItem, proofDetailState: "available" }] },
  { ...validPayload, items: [{ ...validItem, linkedAt: "not-a-timestamp" }] },
  { ...validPayload, items: [{ ...validItem, updatedAt: "2026-99-99" }] },
  { ...validPayload, pageInfo: null },
  { ...validPayload, pageInfo: { hasMore: "false", nextCursor: null } },
  { ...validPayload, pageInfo: { hasMore: false, nextCursor: 4 } },
];
for (const payload of malformedPayloads) {
  assert.equal(parseAccountCampaignListPayload(payload), null, "malformed payload must be rejected without partial rows");
}
assert.match(client, /state: "error", realAccountCampaigns: \[\], message: "The account campaign response was invalid and was not displayed\."/);
assert.doesNotMatch(client, /console\.(?:log|info|warn|error)/);

console.log(JSON.stringify({ ok: true, slice: "PS-041B", checks: {
  source: "pass", states: "pass", credentials: "pass", fixture_separation: "pass",
  runtime_payload_validation: "pass", malformed_payload_safe_error: "pass",
} }));
