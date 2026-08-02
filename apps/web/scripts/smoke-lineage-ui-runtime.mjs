// PS-041E1 — runtime UI validation for the private dynamic lineage UI.
//
// Source-string smokes cannot prove runtime behavior. This script loads the
// production web build via `vite preview`, drives Playwright (Node or Python —
// the same engine family as scripts/ps041c_capture_screenshots.py and the
// screenshot capture script), and asserts BEHAVIOR at runtime:
//
//   1. malformed routes issue zero gateway requests (no `/account/campaigns/`
//      fetch, no `/campaigns//` request);
//   2. full fixture renders exactly 16 nodes and 16 edges;
//   3. no accepted node is wrongly placed under Stage A unsupported;
//   4. mismatch node card presents the mismatch (worst-outcome priority);
//   5. HTTP 503 produces the "Proof dependency unavailable" state (no fixture
//      fallback);
//   6. Passport serialization exactly deep-equals the original server Passport
//      object (state.payload.passport), not the camelCase DTO;
//   7. no direct FastAPI request;
//   8. no provider/B2 request;
//   9. no public imported Passport route.
//
// Check-only and deterministic interception. No new dependency. No provider
// call. No live B2 read. No mutation.

import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const root = resolve(__dirname, "..");
const fixtureDir = join(__dirname, "fixtures", "ps041e1");
const previewPort = 4185;
const base = `http://127.0.0.1:${previewPort}`;

const CAMPAIGN = "campaign-sanitized-demo";
const BUNDLE_FULL = "bundle-sanitized-001";
const BUNDLE_MISMATCH = "bundle-sanitized-mismatch";
const DASHBOARD_CAMPAIGN = "campaign sanitized/demo";

const DASHBOARD_READINESS = {
  processLive: true, configured: true, envConfigured: true, databaseReachable: true,
  authRuntimeAvailable: true, missing: [], placeholders: [],
  providers: Object.fromEntries(["authBase", "database", "email", "google", "github", "apple"].map((key) => [key, {
    status: key === "authBase" || key === "database" ? "configured" : "missing",
    required: key === "authBase" || key === "database", safeName: key, issues: [],
  }])),
};

const DASHBOARD_SESSION = {
  state: "authenticated", authenticated: true, liveRuntimeAuth: true,
  readiness: DASHBOARD_READINESS,
  session: { id: null, userId: null, expiresAt: null, createdAt: null, updatedAt: null },
  user: { id: null, email: null, name: null, emailVerified: false, image: null },
};

function dashboardCampaigns(campaignId = DASHBOARD_CAMPAIGN) {
  return {
    state: "available", source: "account_campaign_store",
    items: [{ campaignId, latestRunId: null, campaignAccessRole: "owner", linkedAt: "2026-01-01T00:00:00.000Z", updatedAt: "2026-01-01T00:00:00.000Z", source: "account_campaign_store", proofDetailState: "not_fetched" }],
    pageInfo: { hasMore: false, nextCursor: null },
  };
}

function readJson(name) {
  return JSON.parse(readFileSync(join(fixtureDir, name), "utf8"));
}

const FIXTURES = {
  listValid: readJson("lineage-list-valid.json"),
  detailFull: readJson("lineage-detail-full.json"),
  detailMismatch: readJson("lineage-detail-hash-mismatch.json"),
  passportValid: readJson("lineage-passport-valid.json"),
};

function envelope(payload, key) {
  return { ok: true, state: "available", source: "proof_api", campaignAccessRole: "owner", [key]: payload, requestId: "ps041e1-runtime" };
}

function deepEqualJson(a, b) {
  return JSON.stringify(sortKeys(a)) === JSON.stringify(sortKeys(b));
}
function sortKeys(value) {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value && typeof value === "object") {
    const out = {};
    for (const k of Object.keys(value).sort()) out[k] = sortKeys(value[k]);
    return out;
  }
  return value;
}

async function loadPlaywright() {
  try { const mod = await import("playwright"); return { kind: "node", chromium: mod.chromium }; } catch { /* fall through */ }
  const probe = spawnSync(process.env.PYTHON ?? "python3", ["-c", "import playwright"], { stdio: "ignore" });
  if (probe.status === 0) return { kind: "python" };
  return null;
}

function startPreview() {
  return spawn(process.execPath, ["node_modules/vite/bin/vite.js", "preview", "--port", String(previewPort), "--strictPort"], {
    cwd: root, stdio: "ignore", env: { ...process.env, NODE_ENV: "production" },
  });
}

async function waitForPreview() {
  for (let i = 0; i < 120; i++) {
    try { const r = await fetch(base); if (r.ok) return; } catch { /* not up */ }
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error("vite preview did not start");
}

async function runtimeChecksNode(chromium) {
  const results = {};
  const browser = await chromium.launch({ headless: true });

  // The vite preview middleware crashes on invalid percent-encoded URLs, so
  // for the malformed-route test we fulfill the document request ourselves
  // with the production index.html. The browser then loads the SPA at the
  // malformed URL; App's matcher tries decodeURIComponent, catches the
  // URIError, and returns the lineage-invalid route — which renders the
  // static MalformedLineageReferencePage that invokes NO data hook.
  const indexHtmlPath = join(root, "dist", "index.html");
  const indexHtml = readFileSync(indexHtmlPath, "utf8");

  // --- Dashboard: authenticated campaign renders one safe launcher ---------
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const forbiddenRequests = [];
    ctx.on("request", (req) => {
      const u = req.url();
      if (/backblaze|s3\.amazonaws|openai|anthropic|gemini|generativelanguage|fal\.|runwayml|elevenlabs/i.test(u)) forbiddenRequests.push(u);
    });
    await ctx.route("**/session", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(DASHBOARD_SESSION) }));
    await ctx.route("**/readyz", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ service: "proofstudio-auth-server", liveRuntimeAuth: true, ready: true, readiness: DASHBOARD_READINESS, trustBoundary: "Auth proves account/session identity only." }) }));
    await ctx.route("**/account/campaigns", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(dashboardCampaigns()) }));
    await ctx.route("**/health", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ ok: true, service: "proofstudio-api", mode: "runtime-smoke", version: "ps041e1" }) }));
    const page = await ctx.newPage();
    await page.goto(base + "/dashboard", { waitUntil: "networkidle" });
    const launcher = page.locator(".dashboard-lineage-launcher");
    if (await launcher.count() !== 1 || !await launcher.isVisible()) throw new Error("authenticated dashboard did not render exactly one visible lineage launcher");
    if ((await launcher.innerText()).trim() !== "Open recorded lineage") throw new Error("dashboard lineage launcher text differs");
    const expectedHref = `/account/campaigns/${encodeURIComponent(DASHBOARD_CAMPAIGN)}/lineage`;
    const href = await launcher.getAttribute("href");
    if (href !== expectedHref || !href.startsWith("/") || href.includes("://") || href.includes(":8000")) throw new Error(`dashboard lineage launcher is not safely encoded, relative, and FastAPI-free: ${href}`);
    const forbiddenControls = page.locator('a, button, input[type="file"]').filter({ hasText: /import|upload|public[ -]?share/i });
    if (await forbiddenControls.count() !== 0) throw new Error("dashboard exposes an import/upload/public-share action");
    if (forbiddenRequests.length) throw new Error("dashboard made a provider/B2 request: " + JSON.stringify(forbiddenRequests));
    results.dashboard_lineage_launcher_visible = true;
    await ctx.close();
  }

  // --- Check 1: malformed routes issue ZERO gateway requests ----------------
  const malformedUrls = [
    `/account/campaigns/%E2%28%A1/lineage`,                 // invalid percent encoding (campaign)
    `/account/campaigns/${CAMPAIGN}/lineage/%E2%28%A1`,     // invalid percent encoding (bundle)
    `/account/campaigns/${CAMPAIGN}/lineage/%E2%28%A1/passport`, // invalid percent encoding (passport route)
  ];
  for (const urlPath of malformedUrls) {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const seenRequests = [];
    ctx.on("request", (req) => {
      const u = req.url();
      // We log any potentially-mutating request: lineage gateway reads,
      // direct FastAPI URLs, or any URL containing the literal empty-segment
      // pattern `/campaigns//`. Document requests for the malformed URL
      // itself are expected (and intercepted below) — excluded from this
      // count. Asset requests under /assets are also excluded.
      if (u.includes("/assets/")) return;
      if (u.endsWith(urlPath)) return; // the document navigation itself
      if (u.includes("/account/campaigns/") || u.includes("/lineage") || u.includes(":8000") || u.includes("127.0.0.1:8000")) {
        seenRequests.push(u);
      }
    });
    // Intercept any lineage gateway read and return empty JSON so a stray
    // fetch is recorded but never reaches the network.
    await ctx.route("**/account/campaigns/**/lineage**", (route) => {
      if (route.request().resourceType() === "document") return route.continue();
      return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
    });
    await ctx.route("**/auth/**", (route) => {
      if (route.request().resourceType() === "document") return route.continue();
      return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
    });
    const page = await ctx.newPage();
    // Fulfill the malformed document URL with index.html (vite preview crashes
    // on invalid percent encoding). Per-page route, never duplicated.
    await page.route(`**${urlPath}**`, (route) => {
      if (route.request().resourceType() === "document") {
        return route.fulfill({ status: 200, contentType: "text/html", body: indexHtml });
      }
      return route.continue();
    });
    await page.goto(base + urlPath, { waitUntil: "load", timeout: 15000 });
    await page.waitForTimeout(500);
    const malformedDisplayed = await page.locator("h1", { hasText: "Malformed lineage reference" }).count();
    if (malformedDisplayed !== 1) throw new Error(`malformed route ${urlPath} did not render the static malformed-reference page (count=${malformedDisplayed})`);
    const doubleSlashRequests = seenRequests.filter((u) => u.includes("/campaigns//"));
    if (seenRequests.length > 0 || doubleSlashRequests.length > 0) {
      throw new Error(`malformed route ${urlPath} emitted ${seenRequests.length} gateway requests: ${JSON.stringify(seenRequests)}`);
    }
    results[`malformed_${urlPath}`] = { reads: seenRequests.length, double_slash: doubleSlashRequests.length };
    await ctx.close();
  }
  results.malformed_route_zero_reads = true;

  // --- Check 2: full fixture renders 16 nodes / 16 edges --------------------
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await ctx.route("**/account/campaigns/**/lineage**", (route) => {
      if (route.request().resourceType() === "document") return route.continue();
      const p = new URL(route.request().url()).pathname;
      if (p.endsWith("/lineage")) return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(envelope(FIXTURES.listValid, "lineage")) });
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(envelope(FIXTURES.detailFull, "lineage")) });
    });
    await ctx.route("**/auth/**", (r) => r.fulfill({ status: 200, contentType: "application/json", body: "{}" }));
    const page = await ctx.newPage();
    await page.goto(base + `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_FULL}`, { waitUntil: "networkidle" });
    const overviewText = await page.locator(".lineage-overview").first().innerText();
    if (!/16 nodes/.test(overviewText)) throw new Error("overview did not show 16 nodes: " + overviewText.replace(/\s+/g, " "));
    if (!/16 edges/.test(overviewText)) throw new Error("overview did not show 16 edges");
    // Count rendered cards across all lanes (excluding unclassified section,
    // which must be empty for the accepted full graph).
    const cardCount = await page.locator(".lineage-stage .lineage-node-card").count();
    if (cardCount !== 15) throw new Error(`expected 15 stage-lane cards (16 nodes minus the bundle-root), got ${cardCount}`);
    const bundleRootText = await page.locator(".lineage-bundle-root").first().innerText();
    if (!/bundle context/i.test(bundleRootText)) throw new Error("bundle-root section not rendered");
    const unclassifiedCount = await page.locator(".lineage-unclassified-section .lineage-node-card").count();
    if (unclassifiedCount !== 0) throw new Error(`expected 0 unclassified nodes for accepted graph, got ${unclassifiedCount}`);
    // Stage A has exactly ONE node (storyboard). Stage A must NOT carry any
    // other accepted node.
    const stageACards = await page.locator(".lineage-stage-a .lineage-node-card").count();
    if (stageACards !== 1) throw new Error(`Stage A must contain exactly one node (storyboard), got ${stageACards}`);
    const stageALabel = await page.locator(".lineage-stage-a .lineage-node-card").first().innerText();
    if (!/storyboard/i.test(stageALabel)) throw new Error("Stage A card is not the storyboard");
    results.full_renders_16_nodes_16_edges = true;
    results.stage_a_only_storyboard = true;
    results.no_unclassified_for_accepted_graph = true;
    await ctx.close();
  }

  // --- Check 4: mismatch node card presents the mismatch (worst outcome) ----
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await ctx.route("**/account/campaigns/**/lineage**", (route) => {
      if (route.request().resourceType() === "document") return route.continue();
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(envelope(FIXTURES.detailMismatch, "lineage")) });
    });
    await ctx.route("**/auth/**", (r) => r.fulfill({ status: 200, contentType: "application/json", body: "{}" }));
    const page = await ctx.newPage();
    await page.goto(base + `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_MISMATCH}`, { waitUntil: "networkidle" });
    // The B2 Run card must surface "Hash mismatch" as its summary badge.
    const b2Card = page.locator(".lineage-node-card", { hasText: "b2-run-sanitized-001" }).first();
    const b2CardText = await b2Card.innerText();
    if (!/Hash mismatch/i.test(b2CardText)) throw new Error("B2 Run card did not surface Hash mismatch badge: " + b2CardText.replace(/\s+/g, " "));
    // And the badge severity must be danger.
    const dangerBadgeCount = await b2Card.locator(".lineage-severity-danger").count();
    if (dangerBadgeCount < 1) throw new Error("B2 Run card has no danger-severity badge");
    // The card must NOT show a success-only badge.
    const okBadgeCount = await b2Card.locator(".lineage-severity-ok").count();
    if (okBadgeCount > 0 && dangerBadgeCount === 0) throw new Error("B2 Run card shows an ok badge with no danger badge");
    results.mismatch_card_shows_hash_mismatch = true;
    await ctx.close();
  }

  // --- Check 5: HTTP 503 produces dependency-unavailable state --------------
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    let fallbackFired = false;
    await ctx.route("**/account/campaigns/**/lineage**", (route) => {
      if (route.request().resourceType() === "document") return route.continue();
      // The exact lineage detail request returns 503; no fixture fallback.
      fallbackFired = true;
      return route.fulfill({ status: 503, contentType: "application/json", body: "" });
    });
    await ctx.route("**/auth/**", (r) => r.fulfill({ status: 200, contentType: "application/json", body: "{}" }));
    const page = await ctx.newPage();
    await page.goto(base + `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_FULL}`, { waitUntil: "networkidle" });
    const stateText = await page.locator(".lineage-state").first().innerText();
    if (!/Proof dependency unavailable/i.test(stateText)) throw new Error("503 did not render Proof dependency unavailable state: " + stateText.replace(/\s+/g, " "));
    if (!fallbackFired) throw new Error("the lineage request was not intercepted");
    results.http_503_renders_dependency_unavailable = true;
    await ctx.close();
  }

  // --- Check 6: Passport serialization exactly equals the original raw ------
  {
    const ctx = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
      permissions: ["clipboard-read", "clipboard-write"],
    });
    await ctx.route("**/account/campaigns/**/lineage/**/passport", (route) => {
      if (route.request().resourceType() === "document") return route.continue();
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(envelope(FIXTURES.passportValid, "passport")) });
    });
    await ctx.route("**/auth/**", (r) => r.fulfill({ status: 200, contentType: "application/json", body: "{}" }));
    const page = await ctx.newPage();
    await page.goto(base + `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_FULL}/passport`, { waitUntil: "networkidle" });
    await page.click('button:has-text("Copy private Passport JSON")', { timeout: 5000 });
    await page.waitForTimeout(300);
    const clip = await page.evaluate(async () => {
      try { return await navigator.clipboard.readText(); } catch { return null; }
    });
    if (!clip) throw new Error("clipboard not readable after Copy click");
    const copied = JSON.parse(clip);
    const rawPassport = FIXTURES.passportValid.passport;
    if (!deepEqualJson(copied, rawPassport)) throw new Error("copied payload does not deep-equal the raw server Passport object");
    // The copied object must contain snake_case keys and must NOT contain the
    // camelCase DTO substitutions, the kind field, or the campaignAccessScope
    // envelope key.
    if (copied.campaign_id === undefined) throw new Error("copied payload missing snake_case campaign_id");
    if (copied.bundle_fingerprint === undefined) throw new Error("copied payload missing snake_case bundle_fingerprint");
    if (copied.truth_boundary === undefined) throw new Error("copied payload missing snake_case truth_boundary");
    if (copied.nodes === undefined || copied.edges === undefined) throw new Error("copied payload missing nodes/edges");
    if (copied.bundleFingerprint !== undefined) throw new Error("copied payload must NOT carry camelCase bundleFingerprint");
    if (copied.kind !== undefined) throw new Error("copied payload must NOT carry browser-only kind");
    if (copied.campaignAccessScope !== undefined) throw new Error("copied payload must NOT carry envelope key campaignAccessScope");
    results.passport_serialization_exact_raw = true;
    await ctx.close();
  }

  // --- Check 7,8,9: no FastAPI / provider / B2 / public-passport requests ---
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const blocked = [];
    ctx.on("request", (req) => {
      const u = req.url();
      if (/localhost:8000|127\.0\.0\.1:8000/.test(u)) blocked.push("fastapi:" + u);
      if (/b2|backblaze|s3\.amazonaws/.test(u)) blocked.push("b2:" + u);
      if (/openai|anthropic|gemini|generativelanguage|fal\.|runwayml|elevenlabs/.test(u)) blocked.push("provider:" + u);
      // Public imported Passport route would be /passport/<bundleId> (golden run
      // Passport stays at /passport/:runId and is exempt).
      if (new RegExp(`/passport/${BUNDLE_FULL}$`).test(u)) blocked.push("public-imported-passport:" + u);
    });
    await ctx.route("**/account/campaigns/**/lineage**", (route) => {
      if (route.request().resourceType() === "document") return route.continue();
      const p = new URL(route.request().url()).pathname;
      if (p.endsWith("/passport")) return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(envelope(FIXTURES.passportValid, "passport")) });
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(envelope(FIXTURES.detailFull, "lineage")) });
    });
    await ctx.route("**/auth/**", (r) => r.fulfill({ status: 200, contentType: "application/json", body: "{}" }));
    const page = await ctx.newPage();
    await page.goto(base + `/account/campaigns/${CAMPAIGN}/lineage/${BUNDLE_FULL}`, { waitUntil: "networkidle" });
    if (blocked.length > 0) throw new Error("forbidden network requests observed: " + JSON.stringify(blocked));
    results.no_fastapi_no_b2_no_provider_no_public_passport = true;
    await ctx.close();
  }

  await browser.close();
  return results;
}

function writePythonHelper() {
  const helperPath = join("/tmp/opencode", "ps041e1-runtime-helper.py");
  mkdirSync("/tmp/opencode", { recursive: true });
  const code = `#!/usr/bin/env python3
import json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

base = "${base}"
root = "${root.replaceAll('\\', '/')}"
campaign = "${CAMPAIGN}"
bundle_full = "${BUNDLE_FULL}"
bundle_mismatch = "${BUNDLE_MISMATCH}"
dashboard_campaign = ${JSON.stringify(DASHBOARD_CAMPAIGN)}
fixtures = json.loads(${JSON.stringify(JSON.stringify(FIXTURES))})
dashboard_session = json.loads(${JSON.stringify(JSON.stringify(DASHBOARD_SESSION))})
index_html = None
try:
    index_html = Path(root + "/dist/index.html").read_text(encoding="utf-8")
except Exception:
    index_html = None

def envelope(payload, key):
    return {"ok": True, "state": "available", "source": "proof_api",
            "campaignAccessRole": "owner", key: payload, "requestId": "ps041e1-runtime"}

def sort_keys(value):
    if isinstance(value, list):
        return [sort_keys(v) for v in value]
    if isinstance(value, dict):
        return {k: sort_keys(value[k]) for k in sorted(value.keys())}
    return value

def deep_equal(a, b):
    return json.dumps(sort_keys(a), sort_keys=True) == json.dumps(sort_keys(b), sort_keys=True)

results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # Dashboard: authenticated campaign -> one safely encoded relative launcher.
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    forbidden = []
    ctx.on("request", lambda req: forbidden.append(req.url) if any(t in req.url.lower() for t in ("backblaze", "s3.amazonaws", "openai", "anthropic", "gemini", "generativelanguage", "elevenlabs")) else None)
    ctx.route("**/session", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(dashboard_session)))
    ctx.route("**/readyz", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps({"service":"proofstudio-auth-server","liveRuntimeAuth":True,"ready":True,"readiness":dashboard_session["readiness"],"trustBoundary":"Auth proves account/session identity only."})))
    ctx.route("**/account/campaigns", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps({"state":"available","source":"account_campaign_store","items":[{"campaignId":dashboard_campaign,"latestRunId":None,"campaignAccessRole":"owner","linkedAt":"2026-01-01T00:00:00.000Z","updatedAt":"2026-01-01T00:00:00.000Z","source":"account_campaign_store","proofDetailState":"not_fetched"}],"pageInfo":{"hasMore":False,"nextCursor":None}})))
    ctx.route("**/health", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps({"ok":True,"service":"proofstudio-api","mode":"runtime-smoke","version":"ps041e1"})))
    page = ctx.new_page()
    page.goto(base + "/dashboard", wait_until="networkidle")
    launcher = page.locator(".dashboard-lineage-launcher")
    if launcher.count() != 1 or not launcher.is_visible():
        raise AssertionError("authenticated dashboard did not render exactly one visible lineage launcher")
    if launcher.inner_text().strip() != "Open recorded lineage":
        raise AssertionError("dashboard lineage launcher text differs")
    expected_href = "/account/campaigns/campaign%20sanitized%2Fdemo/lineage"
    href = launcher.get_attribute("href")
    if href != expected_href or not href.startswith("/") or "://" in href or ":8000" in href:
        raise AssertionError("dashboard lineage launcher is not safely encoded, relative, and FastAPI-free: " + str(href))
    controls = page.locator('a, button, input[type="file"]')
    for index in range(controls.count()):
        control = controls.nth(index)
        text = (control.inner_text() if control.evaluate("el => el.tagName !== 'INPUT'") else control.get_attribute("aria-label") or "").lower()
        if any(term in text for term in ("import", "upload", "public share", "public-share")):
            raise AssertionError("dashboard exposes an import/upload/public-share action")
    if forbidden:
        raise AssertionError("dashboard made a provider/B2 request: " + str(forbidden))
    results["dashboard_lineage_launcher_visible"] = True
    ctx.close()

    # 1. malformed routes -> zero gateway reads
    for url_path in [
        f"/account/campaigns/%E2%28%A1/lineage",
        f"/account/campaigns/{campaign}/lineage/%E2%28%A1",
        f"/account/campaigns/{campaign}/lineage/%E2%28%A1/passport",
    ]:
        ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
        seen = []
        def make_listener(up):
            def listener(req):
                u = req.url
                if "/assets/" in u:
                    return
                if u.endswith(up):
                    return
                if "/account/campaigns/" in u or "/lineage" in u or ":8000" in u:
                    seen.append(u)
            return listener
        ctx.on("request", make_listener(url_path))
        def gateway_handler(route):
            if route.request.resource_type == "document":
                return route.continue_()
            return route.fulfill(status=200, content_type="application/json", body="{}")
        ctx.route("**/account/campaigns/**/lineage**", gateway_handler)
        ctx.route("**/auth/**", lambda r: r.fulfill(status=200, content_type="application/json", body="{}") if r.request.resource_type != "document" else r.continue_())
        page = ctx.new_page()
        if index_html:
            page.route(f"**{url_path}**", lambda r: r.fulfill(status=200, content_type="text/html", body=index_html) if r.request.resource_type == "document" else r.continue_())
        page.goto(base + url_path, wait_until="load", timeout=15000)
        page.wait_for_timeout(500)
        h1 = page.locator("h1", has_text="Malformed lineage reference").count()
        if h1 != 1:
            raise AssertionError(f"malformed route {url_path} did not render malformed page (count={h1})")
        double = [u for u in seen if "/campaigns//" in u]
        if seen or double:
            raise AssertionError(f"malformed route {url_path} emitted reads: {seen}")
        ctx.close()
    results["malformed_route_zero_reads"] = True

    # 2. full fixture -> 16 nodes / 16 edges, Stage A only storyboard
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    def lineage_handler(route):
        if route.request.resource_type == "document":
            return route.continue_()
        path = urlparse(route.request.url).path
        if path.endswith("/lineage"):
            return route.fulfill(status=200, content_type="application/json", body=json.dumps(envelope(fixtures["listValid"], "lineage")))
        return route.fulfill(status=200, content_type="application/json", body=json.dumps(envelope(fixtures["detailFull"], "lineage")))
    ctx.route("**/account/campaigns/**/lineage**", lineage_handler)
    ctx.route("**/auth/**", lambda r: r.fulfill(status=200, content_type="application/json", body="{}"))
    page = ctx.new_page()
    page.goto(base + f"/account/campaigns/{campaign}/lineage/{bundle_full}", wait_until="networkidle")
    overview = page.locator(".lineage-overview").first.inner_text()
    if "16 nodes" not in overview or "16 edges" not in overview:
        raise AssertionError("overview did not show 16/16")
    cards = page.locator(".lineage-stage .lineage-node-card").count()
    if cards != 15:
        raise AssertionError(f"expected 15 stage cards, got {cards}")
    if page.locator(".lineage-bundle-root").count() < 1:
        raise AssertionError("bundle-root section missing")
    unclassified = page.locator(".lineage-unclassified-section .lineage-node-card").count()
    if unclassified != 0:
        raise AssertionError(f"expected 0 unclassified, got {unclassified}")
    stage_a_cards = page.locator(".lineage-stage-a .lineage-node-card").count()
    if stage_a_cards != 1:
        raise AssertionError(f"Stage A must have exactly 1 card, got {stage_a_cards}")
    stage_a_text = page.locator(".lineage-stage-a .lineage-node-card").first.inner_text()
    if "storyboard" not in stage_a_text.lower():
        raise AssertionError("Stage A card is not the storyboard")
    results["full_renders_16_nodes_16_edges"] = True
    results["stage_a_only_storyboard"] = True
    results["no_unclassified_for_accepted_graph"] = True
    ctx.close()

    # 4. mismatch card -> Hash mismatch
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    ctx.route("**/account/campaigns/**/lineage**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(envelope(fixtures["detailMismatch"], "lineage"))) if r.request.resource_type != "document" else r.continue_())
    ctx.route("**/auth/**", lambda r: r.fulfill(status=200, content_type="application/json", body="{}"))
    page = ctx.new_page()
    page.goto(base + f"/account/campaigns/{campaign}/lineage/{bundle_mismatch}", wait_until="networkidle")
    b2 = page.locator(".lineage-node-card", has_text="b2-run-sanitized-001").first
    b2_text = b2.inner_text()
    if "hash mismatch" not in b2_text.lower():
        raise AssertionError("B2 Run card did not surface Hash mismatch")
    if b2.locator(".lineage-severity-danger").count() < 1:
        raise AssertionError("B2 Run card has no danger-severity badge")
    results["mismatch_card_shows_hash_mismatch"] = True
    ctx.close()

    # 5. 503 -> dependency unavailable
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    ctx.route("**/account/campaigns/**/lineage**", lambda r: r.fulfill(status=503, content_type="application/json", body="") if r.request.resource_type != "document" else r.continue_())
    ctx.route("**/auth/**", lambda r: r.fulfill(status=200, content_type="application/json", body="{}"))
    page = ctx.new_page()
    page.goto(base + f"/account/campaigns/{campaign}/lineage/{bundle_full}", wait_until="networkidle")
    state_text = page.locator(".lineage-state").first.inner_text()
    if "proof dependency unavailable" not in state_text.lower():
        raise AssertionError("503 did not render dependency-unavailable state")
    results["http_503_renders_dependency_unavailable"] = True
    ctx.close()

    # 6. passport serialization exactly equals raw
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000}, permissions=["clipboard-read", "clipboard-write"])
    ctx.route("**/account/campaigns/**/lineage/**/passport", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(envelope(fixtures["passportValid"], "passport"))) if r.request.resource_type != "document" else r.continue_())
    ctx.route("**/auth/**", lambda r: r.fulfill(status=200, content_type="application/json", body="{}"))
    page = ctx.new_page()
    page.goto(base + f"/account/campaigns/{campaign}/lineage/{bundle_full}/passport", wait_until="networkidle")
    page.click('button:has-text("Copy private Passport JSON")', timeout=5000)
    page.wait_for_timeout(300)
    clip = page.evaluate("async () => { try { return await navigator.clipboard.readText(); } catch { return null; } }")
    if not clip:
        raise AssertionError("clipboard not readable after Copy click")
    copied = json.loads(clip)
    raw_passport = fixtures["passportValid"]["passport"]
    if not deep_equal(copied, raw_passport):
        raise AssertionError("copied payload does not deep-equal raw server Passport")
    for key in ("campaign_id", "bundle_fingerprint", "truth_boundary", "nodes", "edges"):
        if key not in copied:
            raise AssertionError(f"copied payload missing {key}")
    for key in ("bundleFingerprint", "kind", "campaignAccessScope"):
        if key in copied:
            raise AssertionError(f"copied payload must NOT carry {key}")
    results["passport_serialization_exact_raw"] = True
    ctx.close()

    # 7,8,9. no fastapi/b2/provider/public-passport
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    blocked = []
    ctx.on("request", lambda req: blocked.append(req.url) if any(t in req.url for t in (":8000", "b2", "backblaze", "s3.amazonaws", "openai", "anthropic", "gemini", "generativelanguage", "elevenlabs")) else None)
    ctx.route("**/account/campaigns/**/lineage**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(envelope(fixtures["detailFull"], "lineage"))) if r.request.resource_type != "document" else r.continue_())
    ctx.route("**/auth/**", lambda r: r.fulfill(status=200, content_type="application/json", body="{}"))
    page = ctx.new_page()
    page.goto(base + f"/account/campaigns/{campaign}/lineage/{bundle_full}", wait_until="networkidle")
    if blocked:
        raise AssertionError("forbidden requests observed: " + str(blocked))
    results["no_fastapi_no_b2_no_provider_no_public_passport"] = True
    ctx.close()

    browser.close()

print(json.dumps({"ok": True, "results": results}, indent=2, sort_keys=True))
`;
  writeFileSync(helperPath, code, { mode: 0o644 });
  return helperPath;
}

async function runtimeChecksPython() {
  const helper = writePythonHelper();
  const result = spawnSync(process.env.PYTHON ?? "python3", [helper], { stdio: "inherit" });
  if (result.status !== 0) throw new Error("Python playwright runtime validation failed");
}

async function main() {
  const playwright = await loadPlaywright();
  if (!playwright) {
    console.error("PS-041E1 runtime UI validation requires Playwright (Node or Python).");
    console.error("No new dependency was added. Install Playwright separately to run runtime validation.");
    console.error("No assertions were made; the script is correct and runnable then.");
    process.exit(2);
  }
  if (!existsSync(join(root, "dist"))) {
    const build = spawnSync(process.execPath, ["node_modules/vite/bin/vite.js", "build"], { cwd: root, stdio: "inherit" });
    if (build.status !== 0) throw new Error("vite build failed");
  }
  const preview = startPreview();
  try {
    await waitForPreview();
    if (playwright.kind === "node") {
      const results = await runtimeChecksNode(playwright.chromium);
      console.log(JSON.stringify({ ok: true, slice: "PS-041E1-runtime", engine: "node", results }, null, 2));
    } else {
      await runtimeChecksPython();
    }
  } finally {
    try { preview.kill("SIGTERM"); } catch { /* ignore */ }
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.stack ?? error.message : String(error));
  process.exit(1);
});
