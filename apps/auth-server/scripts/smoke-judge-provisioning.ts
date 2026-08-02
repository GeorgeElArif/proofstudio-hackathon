import { randomBytes } from "node:crypto";
import { spawn, type ChildProcess } from "node:child_process";

import pg from "pg";

import { getConfiguredAuthSmokeEnv, getSmokeDatabaseUrl } from "./ps040f-config.js";
import { provisionJudgeAccount } from "./provision-judge-account.js";
import { assertSafeDatabaseUrlForSmoke } from "../src/db/url-safety.js";

const databaseUrl = getSmokeDatabaseUrl();
assertSafeDatabaseUrlForSmoke(databaseUrl, { action: "PS-042B2 judge provisioning smoke" });
const pool = new pg.Pool({ connectionString: databaseUrl });
const stamp = `${Date.now()}-${randomBytes(4).toString("hex")}`;
const email = `ps042b2-judge-${stamp}@proofstudio.test`;
const campaignId = `ps042b2-campaign-${stamp}`;
const runId = `ps042c1-run-${stamp}`;
const firstSecret = `Aa7!${randomBytes(20).toString("base64url")}`;
const secondSecret = `Bb8!${randomBytes(20).toString("base64url")}`;
const internalToken = randomBytes(32).toString("base64url");
const port = 8802;
const base = `http://127.0.0.1:${port}`;
let server: ChildProcess | null = null;
type RateRow = { id: string; key: string; count: number; last_request: string };
const rateBaseline = (await pool.query<RateRow>(
  "select id, key, count, last_request::text as last_request from auth_rate_limit order by id",
)).rows;

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

async function expectRefusal(env: NodeJS.ProcessEnv, expected: string): Promise<void> {
  try {
    await provisionJudgeAccount(env, { allowDisposableSmokeDatabase: true, automatedSmoke: true });
  } catch (error) {
    assert(error instanceof Error && error.message.includes(expected), `unexpected refusal: ${expected}`);
    return;
  }
  throw new Error(`expected refusal: ${expected}`);
}

function envFor(overrides: NodeJS.ProcessEnv = {}): NodeJS.ProcessEnv {
  return {
    PROOFSTUDIO_DATABASE_URL: databaseUrl,
    PROOFSTUDIO_JUDGE_EMAIL: email,
    PROOFSTUDIO_JUDGE_PASSWORD: firstSecret,
    PROOFSTUDIO_JUDGE_CAMPAIGN_ID: campaignId,
    PROOFSTUDIO_JUDGE_RUN_ID: runId,
    PROOFSTUDIO_JUDGE_ROLE: "viewer",
    PROOFSTUDIO_JUDGE_PROVISIONING_APPROVED: "true",
    ...overrides,
  };
}

async function request(path: string, init: RequestInit = {}) {
  const response = await fetch(base + path, init);
  return { response, body: await response.json() as Record<string, unknown> };
}

async function waitForServer(): Promise<void> {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try { if ((await fetch(`${base}/healthz`)).ok) return; } catch { /* bounded local retry */ }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  throw new Error("judge_smoke_server_start_timeout");
}

async function login(secret: string): Promise<{ ok: boolean; cookie: string; status: number; reason: string }> {
  const result = await request("/auth/sign-in/email", {
    method: "POST",
    headers: { "content-type": "application/json", origin: "http://127.0.0.1:5173" },
    body: JSON.stringify({ email, password: secret, rememberMe: true }),
  });
  return {
    ok: result.response.ok,
    cookie: result.response.headers.get("set-cookie")?.split(";")[0] ?? "",
    status: result.response.status,
    reason: String(result.body.reason ?? result.body.code ?? result.body.error ?? "unknown"),
  };
}

let accountId: string | null = null;
try {
  await pool.query("delete from auth_rate_limit");
  const baseline = await pool.query<{ count: string }>(
    "select count(*)::text as count from auth_user where email_normalized = $1",
    [email],
  );
  assert(baseline.rows[0]!.count === "0", "synthetic account baseline not clean");

  await expectRefusal(envFor({
    PROOFSTUDIO_JUDGE_PROVISIONING_APPROVED: "TRUE",
    PROOFSTUDIO_DATABASE_URL: "not-a-database-url",
  }), "approval");
  await expectRefusal(envFor({ PROOFSTUDIO_JUDGE_EMAIL: "malformed" }), "email");
  await expectRefusal(envFor({ PROOFSTUDIO_JUDGE_EMAIL: "judge@mailinator.com" }), "email");
  await expectRefusal(envFor({ PROOFSTUDIO_JUDGE_EMAIL: "judge@example.com" }), "placeholder");
  await expectRefusal(envFor({ PROOFSTUDIO_JUDGE_ROLE: "owner" }), "role");
  await expectRefusal(envFor({ PROOFSTUDIO_JUDGE_ROLE: "administrator" }), "role");
  await expectRefusal(envFor({ PROOFSTUDIO_JUDGE_PASSWORD: "weak" }), "minimum");
  await expectRefusal(envFor({ PROOFSTUDIO_JUDGE_CAMPAIGN_ID: "bad campaign id" }), "campaign");
  await expectRefusal(envFor({ PROOFSTUDIO_JUDGE_CAMPAIGN_ID: "replace-with-campaign" }), "placeholder");
  await expectRefusal(envFor({
    PROOFSTUDIO_DATABASE_URL: "postgresql://invalid.invalid/proofstudio_production",
  }), "production");

  const first = await provisionJudgeAccount(envFor(), {
    allowDisposableSmokeDatabase: true,
    automatedSmoke: true,
  });
  accountId = first.account_id;
  assert(first.created_user && first.created_account && first.created_access, "first provisioning did not create records");
  assert(first.role === "viewer" && !first.rotated_password, "first provisioning receipt incorrect");
  const serializedReceipt = JSON.stringify(first);
  assert(!serializedReceipt.includes(firstSecret), "receipt exposed credential");
  assert(!serializedReceipt.includes("$scrypt$") &&
    !serializedReceipt.includes("credentialDigest") &&
    !serializedReceipt.includes("databaseUrl"), "receipt exposed credential material");

  const records = await pool.query<{ users: string; accounts: string; access: string; role: string }>(
    `select
      (select count(*) from auth_user where id = $1)::text as users,
      (select count(*) from auth_account where user_id = $1 and provider_id = 'credential')::text as accounts,
      (select count(*) from account_campaign_access where account_id = $1 and campaign_id = $2 and revoked_at is null)::text as access,
      (select access_role::text from account_campaign_access where account_id = $1 and campaign_id = $2 and revoked_at is null) as role`,
    [accountId, campaignId],
  );
  assert(records.rows[0]!.users === "1" && records.rows[0]!.accounts === "1", "user/account records missing");
  assert(records.rows[0]!.access === "1" && records.rows[0]!.role === "viewer", "campaign access missing");

  const identical = await provisionJudgeAccount(envFor(), {
    allowDisposableSmokeDatabase: true,
    automatedSmoke: true,
  });
  assert(!identical.created_user && !identical.created_account && !identical.created_access, "identical rerun not idempotent");
  assert(!identical.rotated_password && !identical.updated_access, "identical rerun mutated state");

  server = spawn(process.execPath, ["dist/src/server.js"], {
    env: {
      ...getConfiguredAuthSmokeEnv(port),
      PROOFSTUDIO_PROOF_API_BASE_URL: "http://127.0.0.1:1",
      PROOFSTUDIO_INTERNAL_SERVICE_TOKEN: internalToken,
      NODE_OPTIONS: `${process.env.NODE_OPTIONS ?? ""} --experimental-global-webcrypto`.trim(),
    },
    stdio: "ignore",
  });
  await waitForServer();
  const initialLogin = await login(firstSecret);
  assert(initialLogin.ok, `initial credential did not authenticate: ${initialLogin.status}:${initialLogin.reason}`);

  const rotated = await provisionJudgeAccount(envFor({
    PROOFSTUDIO_JUDGE_PASSWORD: secondSecret,
  }), { allowDisposableSmokeDatabase: true, automatedSmoke: true });
  assert(rotated.rotated_password, "rotation not reported");
  assert(!(await login(firstSecret)).ok, "previous credential still authenticates");
  assert((await login(secondSecret)).ok, "rotated credential does not authenticate");

  const reviewer = await provisionJudgeAccount(envFor({
    PROOFSTUDIO_JUDGE_PASSWORD: secondSecret,
    PROOFSTUDIO_JUDGE_ROLE: "reviewer",
  }), { allowDisposableSmokeDatabase: true, automatedSmoke: true });
  assert(reviewer.updated_access && reviewer.role === "reviewer", "viewer-to-reviewer update failed");
  const duplicates = await pool.query<{ count: string }>(
    `select count(*)::text as count from account_campaign_access
     where account_id = $1 and campaign_id = $2 and revoked_at is null`,
    [accountId, campaignId],
  );
  assert(duplicates.rows[0]!.count === "1", "duplicate active campaign access exists");

  console.log(JSON.stringify({
    ok: true,
    slice: "PS-042B2",
    smoke: "judge_provisioning",
    checks: {
      pre_client_validation: "pass",
      role_bounds: "viewer|reviewer",
      first_provisioning: "pass",
      sanitized_receipt: "pass",
      idempotency: "pass",
      password_rotation: "pass",
      prior_credential_rejected: "pass",
      role_update: "pass",
      active_access_rows: 1,
      external_http_calls: 0,
      production_database_calls: 0,
    },
  }));
} finally {
  if (server) {
    server.kill("SIGTERM");
    await new Promise((resolve) => server?.once("exit", resolve));
  }
  if (accountId) await pool.query("delete from auth_user where id = $1", [accountId]).catch(() => undefined);
  await pool.query("delete from auth_rate_limit").catch(() => undefined);
  for (const row of rateBaseline) {
    await pool.query(
      "insert into auth_rate_limit (id, key, count, last_request) values ($1, $2, $3, $4)",
      [row.id, row.key, row.count, row.last_request],
    ).catch(() => undefined);
  }
  await pool.end();
}
