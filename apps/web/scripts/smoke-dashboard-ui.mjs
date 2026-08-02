import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const app = readFileSync(resolve("src/App.tsx"), "utf8");
const surface = readFileSync(resolve("src/dashboard/DashboardSurface.tsx"), "utf8");
const client = readFileSync(resolve("src/dashboard/dashboardClient.ts"), "utf8");
const styles = readFileSync(resolve("src/styles.css"), "utf8");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(app.includes('from "./dashboard/DashboardSurface"'), "App should import DashboardSurface");
assert(app.includes('path === "/dashboard"'), "App should register /dashboard");
assert(app.includes("<DashboardSurface />"), "App should render DashboardSurface for /dashboard");

assert(
  surface.includes("ProofStudio proves what the pipeline recorded. Proof does not equal truth."),
  "dashboard should render the required trust boundary",
);
assert(client.includes("ACCOUNT_CAMPAIGN_STORE_SOURCE"), "real campaign list should use account_campaign_store");
assert(client.includes("CHECKED_IN_GOLDEN_FIXTURE_SOURCE"), "golden entry should remain checked_in_fixture");
assert(client.includes("realAccountCampaigns: []"), "dashboard should not return fake campaign rows");
assert(!client.includes("authenticated: true"), "dashboard should not force an authenticated state");
for (const metric of ["rev" + "enue", "M" + "RR", "A" + "RR", "conversion", "active " + "users", "growth"]) {
  assert(!surface.includes(metric), `dashboard should not render ${metric} metrics`);
}

assert(
  surface.includes('src="/ps039/proof-object-sealed-poster.jpg"') &&
    surface.includes('alt="Sealed golden ProofStudio evidence capsule"') &&
    existsSync(resolve("public/ps039/proof-object-sealed-poster.jpg")),
  "dashboard should use the committed, accessible PS-039 branded poster",
);
assert(surface.includes('className="dashboard-media-fallback"'), "branded media should have a CSS fallback");

for (const label of ["Session", "Proof runtime", "Account campaigns"]) {
  assert(surface.includes(`>${label}<`), `compact source strip should include ${label}`);
}
assert(surface.includes('aria-label="Compact source state"'), "source strip should expose a structural label");
const sourceStrip = surface.slice(surface.indexOf("function SourceStrip"), surface.indexOf("function getLayer"));
assert((sourceStrip.match(/<article>/g) ?? []).length === 3, "source strip should contain exactly three compact states");

assert(surface.includes('role="tablist"'), "evidence pipeline should expose a tablist");
assert(surface.includes('role="tab"'), "evidence stages should be semantic tab controls");
assert(surface.includes('role="tabpanel"'), "selected evidence detail should be a tab panel");
assert(surface.includes("aria-selected={stage.key === selectedKey}"), "stage controls should expose selected state");
assert(surface.includes("aria-expanded={stage.key === selectedKey}"), "mobile stepper controls should expose expanded state");
assert(surface.includes('useState(defaultStage)'), "evidence stage selection should use local React state");
assert(!surface.includes("localStorage") && !surface.includes("sessionStorage"), "stage state should not persist to browser storage");
for (const stage of ["Capture / Campaign", "Manifest / Genblaze", "Archive / B2", "Rehydrate", "Review", "Export / Passport"]) {
  assert(surface.includes(stage), `evidence pipeline should include ${stage}`);
}

assert(surface.includes('<details className="dashboard-disclosure dashboard-source-ledger"'), "full source detail should use native progressive disclosure");
assert(surface.includes("The source map, compressed"), "source integrity should be a compact summary");
assert(surface.includes("Account campaign references"), "dashboard should render the real account campaign state surface");
assert(surface.includes("Account campaign storage is available. No campaigns are currently linked to this account."), "dashboard should retain an honest available-empty state");
assert(!surface.includes("Missing source — account campaign ownership/list"), "populated dashboard must not label the account campaign source as missing");
assert(!surface.includes("Why this is unavailable"), "dashboard must not use the obsolete state-agnostic disclosure label");
for (const label of [
  "Why sign-in is required", "About this empty list", "About access and proof details",
  "Why this source is unavailable", "Why this request failed",
]) {
  assert(surface.includes(label), `campaign disclosure should include the state-specific label: ${label}`);
}
assert(surface.includes("Available · 0 mappings"), "available-empty source integrity should report an available source with zero mappings");
assert(surface.includes("Sign-in required"), "unauthenticated source integrity should require sign-in");
assert(surface.includes("Request failed"), "request error should remain distinct from source unavailability");
assert(surface.includes("checked_in_fixture · not account-linked"), "fixture source should remain separate from account campaign rows");
assert(surface.includes('<details className="dashboard-disclosure dashboard-empty-disclosure"'), "campaign limitation should use native disclosure");
assert(surface.includes('<details className="dashboard-disclosure dashboard-more-tools"'), "secondary commands should use native disclosure");
assert(surface.includes('className="dashboard-command-grid"'), "dashboard should render four primary command actions");
const primaryCommands = surface.slice(surface.indexOf("const primary = ["), surface.indexOf("const secondary = ["));
assert((primaryCommands.match(/^\s*\["/gm) ?? []).length === 4, "dashboard should expose exactly four primary commands");

assert(surface.includes('<details className="dashboard-mobile-menu"'), "mobile navigation should use an expandable menu");
assert(!surface.includes("dashboard-sidebar"), "dashboard should not render the old horizontal-scroll sidebar rail");
assert(styles.includes("overflow-x: clip"), "dashboard should prevent page-level horizontal overflow");
assert(styles.includes("@media (max-width: 340px)"), "dashboard should include narrow reflow rules");

for (const href of [
  "/campaign-proof-room", "/b2-evidence", "/genblaze-pipeline", "/b2-rehydrate-comparison",
  "/review-approval-workspace", "/evidence-pack", "/account/session", "/demo", "/review",
]) {
  assert(client.includes(href) || surface.includes(href), `dashboard should preserve launcher ${href}`);
}
assert(client.includes("/passport/"), "dashboard should preserve the golden passport route");

console.log("PS-041A dashboard UI smoke passed.");
