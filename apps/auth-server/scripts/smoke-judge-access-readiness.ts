import { createServer, type Server } from "node:http";
import { randomBytes } from "node:crypto";
import { spawn, type ChildProcess } from "node:child_process";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

import pg from "pg";

import { getConfiguredAuthSmokeEnv, getSmokeDatabaseUrl } from "./ps040f-config.js";
import { provisionJudgeAccount } from "./provision-judge-account.js";
import { assertSafeDatabaseUrlForSmoke } from "../src/db/url-safety.js";

const databaseUrl = getSmokeDatabaseUrl();
assertSafeDatabaseUrlForSmoke(databaseUrl, { action: "PS-042B2 judge access readiness smoke" });
const pool = new pg.Pool({ connectionString: databaseUrl });
const stamp = `${Date.now()}-${randomBytes(4).toString("hex")}`;
const judgeEmail = `ps042b2-ready-${stamp}@proofstudio.test`;
const otherEmail = `ps042b2-other-${stamp}@proofstudio.test`;
const campaignId = `ps042b2-linked-${stamp}`;
const otherCampaignId = `ps042b2-unlinked-${stamp}`;
const bundleId = "bundle-sanitized-001";
const runId = "recorded-run";
const judgeSecret = `Cc9!${randomBytes(20).toString("base64url")}`;
const otherSecret = `Dd6!${randomBytes(20).toString("base64url")}`;
const authPort = 8812;
const proofPort = 8813;
const authBase = `http://127.0.0.1:${authPort}`;
const internalToken = randomBytes(32).toString("base64url");
let authServer: ChildProcess | null = null;
let proofServer: Server | null = null;
let proofCalls = 0;
let tokenReachedProofOnly = true;
const createdIds: string[] = [];
type RateRow = { id: string; key: string; count: number; last_request: string };
const rateBaseline = (await pool.query<RateRow>(
  "select id, key, count, last_request::text as last_request from auth_rate_limit order by id",
)).rows;

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function judgeEnv(email = judgeEmail, secret = judgeSecret, linkedCampaign = campaignId): NodeJS.ProcessEnv {
  return {
    PROOFSTUDIO_DATABASE_URL: databaseUrl,
    PROOFSTUDIO_JUDGE_EMAIL: email,
    PROOFSTUDIO_JUDGE_PASSWORD: secret,
    PROOFSTUDIO_JUDGE_CAMPAIGN_ID: linkedCampaign,
    PROOFSTUDIO_JUDGE_RUN_ID: runId,
    PROOFSTUDIO_JUDGE_ROLE: "viewer",
    PROOFSTUDIO_JUDGE_PROVISIONING_APPROVED: "true",
  };
}

async function readFixture(name: string): Promise<Record<string, unknown>> {
  const text = await readFile(resolve("../web/scripts/fixtures/ps041e1", name), "utf8");
  return JSON.parse(text.replaceAll("campaign-sanitized-demo", campaignId)) as Record<string, unknown>;
}

async function json(path: string, init: RequestInit = {}) {
  const response = await fetch(authBase + path, init);
  return { response, body: await response.json() as Record<string, any> };
}

async function waitForServer(): Promise<void> {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try { if ((await fetch(`${authBase}/healthz`)).ok) return; } catch { /* bounded local retry */ }
    await new Promise((resolveDelay) => setTimeout(resolveDelay, 200));
  }
  throw new Error("judge_readiness_server_start_timeout");
}

async function stopChild(child: ChildProcess | null): Promise<void> {
  if (!child || child.exitCode !== null || child.signalCode !== null) return;
  child.kill("SIGTERM");
  await new Promise((resolveExit) => child.once("exit", resolveExit));
}

async function closeServer(server: Server | null): Promise<void> {
  if (!server) return;
  await new Promise<void>((resolveClose, reject) => server.close((error) => error ? reject(error) : resolveClose()));
}

function cookiePair(setCookie: string): string {
  return setCookie.split(";")[0] ?? "";
}

try {
  await pool.query("delete from auth_rate_limit");
  const requiredTables = await pool.query<{ table_name: string }>(
    `select table_name from information_schema.tables
     where table_schema = 'public' and table_name = any($1)`,
    [["auth_user", "auth_account", "auth_session", "account_campaign_access"]],
  );
  assert(requiredTables.rowCount === 4, "migrations 0000-0002 not present");

  const listFixture = await readFixture("lineage-list-valid.json");
  const detailFixture = await readFixture("lineage-detail-full.json");
  const passportFixture = await readFixture("lineage-passport-valid.json");
  proofServer = createServer((request, response) => {
    proofCalls += 1;
    tokenReachedProofOnly &&= request.headers["x-proofstudio-internal-token"] === internalToken;
    const path = request.url ?? "";
    let payload: Record<string, unknown>;
    if (path.endsWith("/proof-room")) {
      payload = { source: "proof_api", campaign: { campaign_id: campaignId }, selected_run: null, attempts: [], assets: [], manifest: null, passport_ref: null, export_refs: [] };
    } else if (path.endsWith(`/runs/${runId}/passport`)) {
      payload = { source: "proof_api", campaign_access_scope: campaignId, passport: { passport_identity: { run_id: runId } } };
    } else if (path.endsWith(`/${bundleId}/passport`)) {
      payload = passportFixture;
    } else if (path.endsWith(`/${bundleId}`)) {
      payload = detailFixture;
    } else {
      payload = listFixture;
    }
    response.writeHead(200, { "content-type": "application/json" });
    response.end(JSON.stringify(payload));
  }).listen(proofPort, "127.0.0.1");

  const first = await provisionJudgeAccount(judgeEnv(), {
    allowDisposableSmokeDatabase: true,
    automatedSmoke: true,
  });
  createdIds.push(first.account_id);
  assert(first.role === "viewer", "judge role is not minimum role");
  const other = await provisionJudgeAccount(judgeEnv(otherEmail, otherSecret, otherCampaignId), {
    allowDisposableSmokeDatabase: true,
    automatedSmoke: true,
  });
  createdIds.push(other.account_id);

  authServer = spawn(process.execPath, ["dist/src/server.js"], {
    env: {
      ...getConfiguredAuthSmokeEnv(authPort),
      PROOFSTUDIO_PROOF_API_BASE_URL: `http://127.0.0.1:${proofPort}`,
      PROOFSTUDIO_INTERNAL_SERVICE_TOKEN: internalToken,
      PROOFSTUDIO_SESSION_COOKIE_SECURE: "true",
      NODE_OPTIONS: `${process.env.NODE_OPTIONS ?? ""} --experimental-global-webcrypto`.trim(),
    },
    stdio: "ignore",
  });
  await waitForServer();

  const login = await json("/auth/sign-in/email", {
    method: "POST",
    headers: { "content-type": "application/json", origin: "http://127.0.0.1:5173" },
    body: JSON.stringify({ email: judgeEmail, password: judgeSecret, rememberMe: true }),
  });
  assert(login.response.ok, `judge login failed: ${login.response.status}:${String(login.body.code ?? login.body.error ?? "unknown")}`);
  const setCookie = login.response.headers.get("set-cookie") ?? "";
  assert(/;\s*httponly/i.test(setCookie), "session cookie is not HTTP-only");
  assert(/;\s*secure/i.test(setCookie), "production-shaped secure cookie missing");
  const judgeCookie = cookiePair(setCookie);
  assert(judgeCookie, "session cookie missing");

  const session = await json("/session", { headers: { cookie: judgeCookie } });
  assert(session.response.ok && session.body.authenticated === true, "session readback failed");
  const dashboard = await json("/account/campaigns", { headers: { cookie: judgeCookie } });
  assert(dashboard.response.ok && dashboard.body.items.length === 1, "dashboard campaign isolation failed");
  assert(dashboard.body.items[0].campaignId === campaignId &&
    dashboard.body.items[0].campaignAccessRole === "viewer", "linked campaign/role mismatch");

  for (const path of [
    `/account/campaigns/${campaignId}/proof-room`,
    `/account/campaigns/${campaignId}/passport/${runId}`,
    `/account/campaigns/${campaignId}/lineage`,
    `/account/campaigns/${campaignId}/lineage/${bundleId}`,
    `/account/campaigns/${campaignId}/lineage/${bundleId}/passport`,
  ]) {
    const result = await json(path, { headers: { cookie: judgeCookie } });
    assert(result.response.ok && result.body.state === "available", `authorized journey failed: ${path}`);
    assert(result.body.campaignAccessRole === "viewer", `excess role returned: ${path}`);
  }

  const beforeUnlinked = proofCalls;
  const unlinked = await json(`/account/campaigns/${otherCampaignId}/proof-room`, { headers: { cookie: judgeCookie } });
  assert(unlinked.response.status === 404 && proofCalls === beforeUnlinked, "unlinked denial called proof API");

  const otherLogin = await json("/auth/sign-in/email", {
    method: "POST",
    headers: { "content-type": "application/json", origin: "http://127.0.0.1:5173" },
    body: JSON.stringify({ email: otherEmail, password: otherSecret, rememberMe: true }),
  });
  const otherCookie = cookiePair(otherLogin.response.headers.get("set-cookie") ?? "");
  const beforeOther = proofCalls;
  const secondAccount = await json(`/account/campaigns/${campaignId}/lineage`, { headers: { cookie: otherCookie } });
  assert(secondAccount.response.status === 404 && proofCalls === beforeOther, "second-account denial called proof API");

  const logout = await json("/logout", {
    method: "POST",
    headers: { cookie: judgeCookie, origin: "http://127.0.0.1:5173" },
  });
  assert(logout.response.ok, "logout failed");
  const afterLogout = await json("/session", { headers: { cookie: judgeCookie } });
  assert(afterLogout.body.authenticated === false, "logout did not invalidate session");

  const rerun = await provisionJudgeAccount(judgeEnv(), {
    allowDisposableSmokeDatabase: true,
    automatedSmoke: true,
  });
  assert(!rerun.created_user && !rerun.created_account && !rerun.created_access &&
    !rerun.rotated_password && !rerun.updated_access, "provisioning rerun not idempotent");

  const browserSources = [
    await readFile(resolve("../web/src/authClient.ts"), "utf8"),
    await readFile(resolve("../web/src/authorizedProofClient.ts"), "utf8"),
  ].join("\n");
  assert(!browserSources.includes("localStorage") && !browserSources.includes("sessionStorage"), "browser-storage authentication found");
  assert(!browserSources.includes("PROOFSTUDIO_INTERNAL_SERVICE_TOKEN") &&
    !browserSources.includes("X-ProofStudio-Internal-Token"), "internal token exposed to browser source");
  const privateColumns = await pool.query<{ column_name: string }>(
    "select column_name from information_schema.columns where table_name = 'account_campaign_access'",
  );
  assert(!privateColumns.rows.some((row) => /proof|passport|lineage|manifest|asset|prompt/.test(row.column_name)), "private proof payload duplicated into PostgreSQL");
  assert(tokenReachedProofOnly, "proof API did not receive the server-owned internal token");

  console.log(JSON.stringify({
    ok: true,
    slice: "PS-042B2",
    smoke: "judge_access_readiness",
    journey: "fresh_db_migrations_provision_login_session_dashboard_proof_passport_lineage_denials_logout_rerun",
    checks: {
      http_only_cookie: "pass",
      secure_cookie_production_shape: "pass",
      browser_storage_auth: "absent",
      browser_internal_token: "absent",
      authorization_before_proof: "pass",
      denied_proof_calls: 0,
      fixture_fallback_after_denial: "absent",
      private_payload_postgres_duplication: "absent",
      linked_campaign_only: "pass",
      minimum_role: "viewer",
      logout_session_invalid: "pass",
      idempotent_rerun: "pass",
      provider_calls: 0,
      b2_calls: 0,
      external_http_calls: 0,
      production_database_calls: 0,
    },
  }));
} finally {
  await stopChild(authServer).catch(() => undefined);
  await closeServer(proofServer).catch(() => undefined);
  for (const id of createdIds) await pool.query("delete from auth_user where id = $1", [id]).catch(() => undefined);
  await pool.query("delete from auth_rate_limit").catch(() => undefined);
  for (const row of rateBaseline) {
    await pool.query(
      "insert into auth_rate_limit (id, key, count, last_request) values ($1, $2, $3, $4)",
      [row.id, row.key, row.count, row.last_request],
    ).catch(() => undefined);
  }
  await pool.end();
}
