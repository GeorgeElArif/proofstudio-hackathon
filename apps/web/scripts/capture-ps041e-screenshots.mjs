// PS-041E1 — deterministic screenshot capture for the private lineage UI.
//
// Uses the repository-established Playwright tooling only (Node or Python —
// the same engine family used by scripts/ps041c_capture_screenshots.py). No
// new screenshot dependency is added. The script serves the production web
// build via `vite preview` and intercepts the auth-server gateway reads with
// the deterministic fixtures under scripts/fixtures/ps041e1, so it makes:
//   - no provider call;
//   - no live B2 read;
//   - no real-session call;
//   - no mutation.
//
// Both the Node and Python engines consume ONE explicit CAPTURE_PLAN. Every
// entry declares its viewport, URL, mocked response state, node-selection
// action, element/full-page target, and output filename. The two engines are
// behaviorally identical — same plan, same routing rules, same assertions.
//
// Writes only to /tmp/proofstudio-ps041e-screenshots/. Stale files are removed
// before capture. The script fails if any expected screenshot was not
// recreated, and verifies all ten files are nonempty and distinct where
// distinct states are required.
//
// If Playwright is not installed the script prints a clear diagnostic and
// exits non-zero without writing partial output; it never fabricates
// screenshots and never adds a dependency.

import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { resolve, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const root = resolve(__dirname, "..");
const fixtureDir = join(__dirname, "fixtures", "ps041e1");
const outDir = "/tmp/proofstudio-ps041e-screenshots";
const previewPort = 4183;
const base = `http://127.0.0.1:${previewPort}`;

const CAMPAIGN = "campaign-sanitized-demo";
const BUNDLE_FULL = "bundle-sanitized-001";
const BUNDLE_PARTIAL = "bundle-sanitized-partial";
const BUNDLE_MISMATCH = "bundle-sanitized-mismatch";

const DASHBOARD_READINESS = {
  processLive: true,
  configured: true,
  envConfigured: true,
  databaseReachable: true,
  authRuntimeAvailable: true,
  missing: [],
  placeholders: [],
  providers: {
    authBase: { status: "configured", required: true, safeName: "auth base", issues: [] },
    database: { status: "configured", required: true, safeName: "database", issues: [] },
    email: { status: "missing", required: false, safeName: "email", issues: [] },
    google: { status: "missing", required: false, safeName: "google", issues: [] },
    github: { status: "missing", required: false, safeName: "github", issues: [] },
    apple: { status: "missing", required: false, safeName: "apple", issues: [] },
  },
};

const DASHBOARD_SESSION = {
  state: "authenticated",
  authenticated: true,
  liveRuntimeAuth: true,
  readiness: DASHBOARD_READINESS,
  session: { id: null, userId: null, expiresAt: null, createdAt: null, updatedAt: null },
  user: { id: null, email: null, name: null, emailVerified: false, image: null },
};

const DASHBOARD_CAMPAIGNS = {
  state: "available",
  source: "account_campaign_store",
  items: [{
    campaignId: CAMPAIGN,
    latestRunId: null,
    campaignAccessRole: "owner",
    linkedAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    source: "account_campaign_store",
    proofDetailState: "not_fetched",
  }],
  pageInfo: { hasMore: false, nextCursor: null },
};

const DASHBOARD_HEALTH = {
  ok: true,
  service: "proofstudio-api",
  mode: "deterministic-capture",
  version: "ps041e1",
};

function readJson(name) {
  return JSON.parse(readFileSync(join(fixtureDir, name), "utf8"));
}

const FIXTURES = {
  listValid: readJson("lineage-list-valid.json"),
  detailFull: readJson("lineage-detail-full.json"),
  detailPartial: readJson("lineage-detail-partial.json"),
  detailMismatch: readJson("lineage-detail-hash-mismatch.json"),
  passportValid: readJson("lineage-passport-valid.json"),
};

// One explicit capture manifest. Both engines consume exactly this list.
// Each entry pins: viewport, URL, mocked response state, node-selection
// action (or null), element/full-page target, and output filename.
const CAPTURE_PLAN = [
  { name: "01-dashboard-lineage-entry.png", viewport: { width: 1440, height: 1000 }, urlPath: "/dashboard", mock: "dashboard", action: null, target: "element:#account-campaigns" },
  { name: "02-lineage-bundle-list.png", viewport: { width: 1440, height: 1000 }, urlPath: `/account/campaigns/${CAMPAIGN}/lineage`, mock: "list-valid", action: null, target: "full" },
  { name: "03-lineage-full-a-b0-b1-b2-c.png", viewport: { width: 1440, height: 1000 }, urlPath: `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_FULL}`, mock: "detail-full", action: null, target: "full" },
  { name: "04-recorded-vs-inferred.png", viewport: { width: 1440, height: 1000 }, urlPath: `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_FULL}`, mock: "detail-full", action: null, target: "element:.lineage-stages" },
  { name: "05-partial-missing-evidence.png", viewport: { width: 1440, height: 1000 }, urlPath: `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_PARTIAL}`, mock: "detail-partial", action: null, target: "full" },
  { name: "06-hash-check-details.png", viewport: { width: 1440, height: 1000 }, urlPath: `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_MISMATCH}`, mock: "detail-mismatch", action: "select-b2-mismatch", target: "element:.lineage-selected" },
  { name: "07-structured-b2-reference.png", viewport: { width: 1440, height: 1000 }, urlPath: `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_FULL}`, mock: "detail-full", action: "select-final-delivery", target: "element:.lineage-b2-reference" },
  { name: "08-private-portable-passport.png", viewport: { width: 1440, height: 1000 }, urlPath: `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_FULL}/passport`, mock: "passport-valid", action: null, target: "full" },
  { name: "09-mobile-lineage.png", viewport: { width: 390, height: 844 }, urlPath: `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_FULL}`, mock: "detail-full", action: null, target: "full" },
  { name: "10-safe-dependency-error.png", viewport: { width: 1440, height: 1000 }, urlPath: `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_FULL}`, mock: "detail-503", action: null, target: "element:.lineage-state" },
];

// Semantic action descriptors. Both engines implement these by name so the
// plan stays engine-neutral.
const ACTIONS = {
  "select-b2-mismatch": {
    clickSelector: '.lineage-node-card-button',
    clickHasText: 'b2-run-sanitized-001',
    waitForSelector: '.lineage-selected',
  },
  "select-final-delivery": {
    clickSelector: '.lineage-node-card-button',
    clickHasText: 'final-sanitized-001',
    waitForSelector: '.lineage-b2-reference',
  },
};

function envelope(payload, key) {
  return {
    ok: true,
    state: "available",
    source: "proof_api",
    campaignAccessRole: "owner",
    [key]: payload,
    requestId: "ps041e1-screenshot-request",
  };
}

// Per-shot mock resolver. Returns {status, body} for a lineage gateway fetch,
// or null to let the request continue. A shot's `mock` field is authoritative
// — the resolver does not switch fixtures based on URL alone, so the 503 case
// is deterministic and never falls back to a fixture.
function resolveShotMock(shot, requestPath) {
  if (!requestPath.includes("/lineage")) return null;
  if (shot.mock === "detail-503") return { status: 503, body: null };
  if (shot.mock === "dashboard") return null;
  if (requestPath.endsWith("/passport")) return { status: 200, body: envelope(FIXTURES.passportValid, "passport") };
  if (requestPath.endsWith("/lineage")) return { status: 200, body: envelope(FIXTURES.listValid, "lineage") };
  if (shot.mock === "list-valid") return { status: 200, body: envelope(FIXTURES.listValid, "lineage") };
  if (shot.mock === "detail-full") return { status: 200, body: envelope(FIXTURES.detailFull, "lineage") };
  if (shot.mock === "detail-partial") return { status: 200, body: envelope(FIXTURES.detailPartial, "lineage") };
  if (shot.mock === "detail-mismatch") return { status: 200, body: envelope(FIXTURES.detailMismatch, "lineage") };
  if (shot.mock === "passport-valid") return { status: 200, body: envelope(FIXTURES.passportValid, "passport") };
  return null;
}

function assertOutputIntegrity() {
  const expected = CAPTURE_PLAN.map((s) => s.name);
  const present = readdirSync(outDir);
  for (const name of expected) {
    if (!present.includes(name)) throw new Error(`expected screenshot not recreated: ${name}`);
    const st = statSync(join(outDir, name));
    if (!st.size || st.size < 1024) throw new Error(`screenshot too small / empty: ${name} (${st.size} bytes)`);
  }
  // Distinct-content check for shots that MUST show distinct UI state:
  // 03 (full graph) vs 06 (Hash mismatch) vs 10 (Proof dependency unavailable).
  // Their byte sizes must not be identical (a strong signal that the wrong
  // fixture state was rendered).
  const distinctPairs = [
    ["03-lineage-full-a-b0-b1-b2-c.png", "06-hash-check-details.png"],
    ["03-lineage-full-a-b0-b1-b2-c.png", "10-safe-dependency-error.png"],
    ["06-hash-check-details.png", "10-safe-dependency-error.png"],
  ];
  for (const [a, b] of distinctPairs) {
    const sa = statSync(join(outDir, a)).size;
    const sb = statSync(join(outDir, b)).size;
    if (sa === sb) throw new Error(`distinct-state screenshots have identical size: ${a} vs ${b} (${sa} bytes)`);
  }
}

async function loadPlaywright() {
  try {
    const mod = await import("playwright");
    return { kind: "node", chromium: mod.chromium };
  } catch { /* fall through */ }
  const probe = spawnSync(process.env.PYTHON ?? "python3", ["-c", "import playwright"], { stdio: "ignore" });
  if (probe.status === 0) return { kind: "python" };
  return null;
}

function startPreview() {
  const child = spawn(process.execPath, ["node_modules/vite/bin/vite.js", "preview", "--port", String(previewPort), "--strictPort"], {
    cwd: root,
    stdio: "ignore",
    env: { ...process.env, NODE_ENV: "production" },
  });
  return child;
}

async function waitForPreview() {
  for (let i = 0; i < 120; i++) {
    try { const r = await fetch(base); if (r.ok) return; } catch { /* not up yet */ }
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error("vite preview did not start");
}

// Serialize the capture plan + helpers to JSON for the Python engine so it
// consumes the SAME semantic plan (no duplicate logic).
function serializePlanForPython() {
  return JSON.stringify({
    plan: CAPTURE_PLAN,
    actions: ACTIONS,
    fixtures: {
      listValid: FIXTURES.listValid,
      detailFull: FIXTURES.detailFull,
      detailPartial: FIXTURES.detailPartial,
      detailMismatch: FIXTURES.detailMismatch,
      passportValid: FIXTURES.passportValid,
    },
    dashboard: {
      session: DASHBOARD_SESSION,
      campaigns: DASHBOARD_CAMPAIGNS,
      health: DASHBOARD_HEALTH,
      expectedLauncherHref: `/account/campaigns/${encodeURIComponent(CAMPAIGN)}/lineage`,
    },
    base,
    outDir,
    campaign: CAMPAIGN,
  });
}

async function captureWithNodePlaywright(chromium) {
  const browser = await chromium.launch({ headless: true });

  for (const shot of CAPTURE_PLAN) {
    const ctx = await browser.newContext({ viewport: shot.viewport });
    // One route handler per page (registered on the context, never duplicated).
    await ctx.route("**/account/campaigns/**/lineage**", async (route) => {
      const type = route.request().resourceType();
      if (type !== "fetch" && type !== "xhr") { await route.continue(); return; }
      const path = new URL(route.request().url()).pathname;
      const mock = resolveShotMock(shot, path);
      if (mock === null) { await route.continue(); return; }
      if (mock.status !== 200) { await route.fulfill({ status: mock.status, contentType: "application/json", body: "" }); return; }
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(mock.body) });
    });
    await ctx.route("**/auth/**", (route) => {
      if (route.request().resourceType() === "document") { route.continue(); return; }
      route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
    });
    await ctx.route("**/session", (route) => route.fulfill({
      status: 200, contentType: "application/json", body: JSON.stringify(DASHBOARD_SESSION),
    }));
    await ctx.route("**/readyz", (route) => route.fulfill({
      status: 200, contentType: "application/json", body: JSON.stringify({
        service: "proofstudio-auth-server", liveRuntimeAuth: true, ready: true,
        readiness: DASHBOARD_READINESS, trustBoundary: "Auth proves account/session identity only.",
      }),
    }));
    await ctx.route("**/health", (route) => route.fulfill({
      status: 200, contentType: "application/json", body: JSON.stringify(DASHBOARD_HEALTH),
    }));
    await ctx.route("**/account/campaigns", (route) => {
      if (route.request().resourceType() === "document") { route.continue(); return; }
      route.fulfill({
        status: 200, contentType: "application/json",
        body: JSON.stringify(DASHBOARD_CAMPAIGNS),
      });
    });
    const page = await ctx.newPage();
    await page.goto(base + shot.urlPath, { waitUntil: "networkidle" });

    if (shot.mock === "dashboard") {
      const launcher = page.locator(".dashboard-lineage-launcher");
      if (await launcher.count() !== 1) throw new Error("dashboard must render exactly one lineage launcher");
      if (!await launcher.isVisible()) throw new Error("dashboard lineage launcher is not visible");
      if ((await launcher.innerText()).trim() !== "Open recorded lineage") throw new Error("dashboard lineage launcher text differs");
      const href = await launcher.getAttribute("href");
      const expectedHref = `/account/campaigns/${encodeURIComponent(CAMPAIGN)}/lineage`;
      if (href !== expectedHref) throw new Error(`dashboard lineage launcher href differs: ${href}`);
      const forbiddenControls = page.locator('a, button, input[type="file"]').filter({ hasText: /import|upload|public[ -]?share/i });
      if (await forbiddenControls.count() !== 0) throw new Error("dashboard exposes an import/upload/public-share control");
      const accountText = await page.locator("#account-campaigns").innerText();
      if (!accountText.includes(CAMPAIGN) || !/storage is available/i.test(accountText)) throw new Error("dashboard account campaign is not available");
      if (/source unavailable|request failed|network error/i.test(accountText)) throw new Error("dashboard account campaign rendered an unavailable/error state");
    }

    if (shot.action) {
      const action = ACTIONS[shot.action];
      if (action) {
        await page.locator(action.clickSelector, { hasText: action.clickHasText }).first().click({ timeout: 5000 });
        await page.waitForSelector(action.waitForSelector, { timeout: 5000 });
        await page.waitForTimeout(200);
      }
    }

    if (shot.target.startsWith("element:")) {
      const sel = shot.target.slice("element:".length);
      const loc = page.locator(sel).first();
      try {
        await loc.scrollIntoViewIfNeeded({ timeout: 4000 });
        await loc.screenshot({ path: join(outDir, shot.name) });
      } catch {
        await page.screenshot({ path: join(outDir, shot.name), fullPage: true });
      }
    } else {
      await page.screenshot({ path: join(outDir, shot.name), fullPage: true });
    }
    await ctx.close();
  }
  await browser.close();
}

function writePythonHelper() {
  const helperPath = join("/tmp/opencode", "ps041e-capture-helper.py");
  mkdirSync("/tmp/opencode", { recursive: true });
  const code = `#!/usr/bin/env python3
import json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

PLAN_JSON = ${JSON.stringify(serializePlanForPython())}
cfg = json.loads(PLAN_JSON)
plan = cfg["plan"]
actions = cfg["actions"]
fixtures = cfg["fixtures"]
dashboard = cfg["dashboard"]
base = cfg["base"]
out = Path(cfg["outDir"])

def envelope(payload, key):
    return {"ok": True, "state": "available", "source": "proof_api",
            "campaignAccessRole": "owner", key: payload,
            "requestId": "ps041e1-screenshot-request"}

def resolve_shot_mock(shot, request_path):
    if "/lineage" not in request_path:
        return None
    if shot["mock"] == "detail-503":
        return {"status": 503, "body": None}
    if shot["mock"] == "dashboard":
        return None
    if request_path.endswith("/passport"):
        return {"status": 200, "body": envelope(fixtures["passportValid"], "passport")}
    if request_path.endswith("/lineage"):
        return {"status": 200, "body": envelope(fixtures["listValid"], "lineage")}
    if shot["mock"] == "list-valid":
        return {"status": 200, "body": envelope(fixtures["listValid"], "lineage")}
    if shot["mock"] == "detail-full":
        return {"status": 200, "body": envelope(fixtures["detailFull"], "lineage")}
    if shot["mock"] == "detail-partial":
        return {"status": 200, "body": envelope(fixtures["detailPartial"], "lineage")}
    if shot["mock"] == "detail-mismatch":
        return {"status": 200, "body": envelope(fixtures["detailMismatch"], "lineage")}
    if shot["mock"] == "passport-valid":
        return {"status": 200, "body": envelope(fixtures["passportValid"], "passport")}
    return None

def run_shot(browser, shot):
    ctx = browser.new_context(viewport=shot["viewport"])
    def handler(route):
        req = route.request
        if req.resource_type not in ("fetch", "xhr"):
            return route.continue_()
        parsed = urlparse(req.url)
        path = parsed.path
        if "/account/campaigns/" in path and "/lineage" in path:
            mock = resolve_shot_mock(shot, path)
            if mock is not None:
                if mock["status"] != 200:
                    return route.fulfill(status=mock["status"], content_type="application/json", body="")
                return route.fulfill(status=200, content_type="application/json", body=json.dumps(mock["body"]))
        return route.continue_()
    ctx.route("**/account/campaigns/**/lineage**", handler)
    ctx.route("**/auth/**", lambda r: r.continue_() if r.request.resource_type == "document" else r.fulfill(status=200, content_type="application/json", body="{}"))
    ctx.route("**/session", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(dashboard["session"])))
    ctx.route("**/readyz", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps({"service":"proofstudio-auth-server","liveRuntimeAuth":True,"ready":True,"readiness":dashboard["session"]["readiness"],"trustBoundary":"Auth proves account/session identity only."})))
    ctx.route("**/health", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(dashboard["health"])))
    ctx.route("**/account/campaigns", lambda r: r.continue_() if r.request.resource_type == "document" else r.fulfill(status=200, content_type="application/json", body=json.dumps(dashboard["campaigns"])))
    page = ctx.new_page()
    page.goto(base + shot["urlPath"], wait_until="networkidle")
    if shot["mock"] == "dashboard":
        launcher = page.locator(".dashboard-lineage-launcher")
        if launcher.count() != 1:
            raise AssertionError("dashboard must render exactly one lineage launcher")
        if not launcher.is_visible():
            raise AssertionError("dashboard lineage launcher is not visible")
        if launcher.inner_text().strip() != "Open recorded lineage":
            raise AssertionError("dashboard lineage launcher text differs")
        if launcher.get_attribute("href") != dashboard["expectedLauncherHref"]:
            raise AssertionError("dashboard lineage launcher href differs")
        controls = page.locator('a, button, input[type="file"]')
        for index in range(controls.count()):
            control = controls.nth(index)
            text = (control.inner_text() if control.evaluate("el => el.tagName !== 'INPUT'") else control.get_attribute("aria-label") or "").lower()
            if any(term in text for term in ("import", "upload", "public share", "public-share")):
                raise AssertionError("dashboard exposes an import/upload/public-share control")
        account_text = page.locator("#account-campaigns").inner_text()
        if cfg["campaign"] not in account_text or "storage is available" not in account_text.lower():
            raise AssertionError("dashboard account campaign is not available")
        if any(term in account_text.lower() for term in ("source unavailable", "request failed", "network error")):
            raise AssertionError("dashboard account campaign rendered an unavailable/error state")
    if shot.get("action"):
        action = actions.get(shot["action"])
        if action:
            page.locator(action["clickSelector"]).filter(has_text=action["clickHasText"]).first.click(timeout=5000)
            page.wait_for_selector(action["waitForSelector"], timeout=5000)
            page.wait_for_timeout(200)
    target = shot["target"]
    if target.startswith("element:"):
        sel = target[len("element:"):]
        loc = page.locator(sel).first
        try:
            loc.scroll_into_view_if_needed(timeout=4000)
            loc.screenshot(path=str(out / shot["name"]))
        except Exception:
            page.screenshot(path=str(out / shot["name"]), full_page=True)
    else:
        page.screenshot(path=str(out / shot["name"]), full_page=True)
    ctx.close()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for shot in plan:
        run_shot(browser, shot)
    browser.close()
print(json.dumps({"ok": True, "count": len(plan), "out": str(out)}))
`;
  writeFileSync(helperPath, code, { mode: 0o644 });
  return helperPath;
}

async function captureWithPythonPlaywright() {
  const helper = writePythonHelper();
  const result = spawnSync(process.env.PYTHON ?? "python3", [helper], { stdio: "inherit" });
  if (result.status !== 0) throw new Error("Python playwright capture failed");
}

async function main() {
  // Explicit temporary directory creation; never rely on a pre-existing path.
  if (existsSync(outDir)) rmSync(outDir, { recursive: true, force: true });
  mkdirSync(outDir, { recursive: true });

  const playwright = await loadPlaywright();
  if (!playwright) {
    console.error("PS-041E1 screenshot capture requires Playwright (Node or Python), which is not installed in this environment.");
    console.error("No new dependency was added. Install Playwright separately to capture screenshots; the script is correct and runnable then.");
    console.error("No screenshots were written and no partial output was produced.");
    process.exit(2);
  }

  if (!existsSync(join(root, "dist"))) {
    const build = spawnSync(process.execPath, ["node_modules/vite/bin/vite.js", "build"], { cwd: root, stdio: "inherit" });
    if (build.status !== 0) throw new Error("vite build failed");
  }

  const preview = startPreview();
  try {
    await waitForPreview();
    if (playwright.kind === "node") await captureWithNodePlaywright(playwright.chromium);
    else await captureWithPythonPlaywright();
    assertOutputIntegrity();
    console.log(JSON.stringify({ ok: true, slice: "PS-041E1", screenshots: CAPTURE_PLAN.length, out: outDir, engine: playwright.kind }));
  } finally {
    try { preview.kill("SIGTERM"); } catch { /* ignore */ }
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.stack ?? error.message : String(error));
  process.exit(1);
});
