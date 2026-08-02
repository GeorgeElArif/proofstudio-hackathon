import { spawn, type ChildProcess } from "node:child_process";

import pg from "pg";

import { getConfiguredAuthSmokeEnv, getSmokeDatabaseUrl } from "./ps040f-config.js";
import { assertSafeDatabaseUrlForSmoke, summarizeDatabaseUrlSafety } from "../src/db/url-safety.js";

type JsonRecord = Record<string, unknown>;

const port = Number.parseInt(process.env.PROOFSTUDIO_AUTH_CONFIGURED_SMOKE_PORT ?? "8791", 10);
const baseUrl = `http://127.0.0.1:${port}`;
const databaseUrl = getSmokeDatabaseUrl();
const allowNonLocal = process.env.AUTH_ALLOW_NONLOCAL_TEST_DB === "true";
const safety = assertSafeDatabaseUrlForSmoke(databaseUrl, {
  allowNonlocalTestDb: allowNonLocal,
  action: "configured auth runtime smoke",
});
const testEmail = `ps040f-smoke-${Date.now()}@proofstudio.test`;

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

async function fetchJson(path: string, init?: RequestInit): Promise<{ status: number; headers: Headers; body: JsonRecord }> {
  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: {
      accept: "application/json",
      ...(init?.headers ?? {}),
    },
  });
  const body = await response.json().catch(() => ({})) as JsonRecord;
  return { status: response.status, headers: response.headers, body };
}

async function waitForHealth(): Promise<void> {
  const deadline = Date.now() + 15_000;
  while (Date.now() < deadline) {
    try {
      const health = await fetchJson("/healthz");
      if (health.status === 200) return;
    } catch {
      // Server still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error("auth server did not become healthy for configured runtime smoke");
}

function startServer(): ChildProcess {
  return spawn(process.execPath, ["dist/src/server.js"], {
    env: getConfiguredAuthSmokeEnv(port),
    stdio: ["ignore", "pipe", "pipe"],
  });
}

function redactSmokeOutput(value: string): string {
  return value
    .replaceAll(databaseUrl, "[redacted-database-url]")
    .replaceAll(testEmail, "[redacted-smoke-email]")
    .replaceAll("ps040f-local-test-password-12345", "[redacted-password]")
    .split("\n")
    .slice(-8)
    .join(" | ");
}

async function cleanupTestRows(): Promise<void> {
  const pool = new pg.Pool({ connectionString: databaseUrl });
  try {
    await pool.query("delete from auth_user where email_normalized = lower($1)", [testEmail]);
  } finally {
    await pool.end();
  }
}

let server: ChildProcess | null = null;
try {
  await cleanupTestRows();
  server = startServer();
  let serverOutput = "";
  server.stdout?.on("data", (chunk) => {
    serverOutput += String(chunk);
  });
  server.stderr?.on("data", (chunk) => {
    serverOutput += String(chunk);
  });

  await waitForHealth();

  const ready = await fetchJson("/readyz");
  assert(ready.status === 200, "configured auth runtime should report ready with safe local/test DB");
  assert(ready.body.ready === true, "readyz payload should be ready");
  const readiness = ready.body.readiness as JsonRecord;
  assert(readiness.authRuntimeAvailable === true, "auth runtime should be available");

  const initialSession = await fetchJson("/session");
  const directInitialSession = initialSession.status === 200 ? null : await fetchJson("/auth/get-session");
  assert(
    initialSession.status === 200,
    `initial session readback should succeed, got status ${initialSession.status} state ${String(initialSession.body.state)} reason ${String(initialSession.body.reason)} directReason ${String(directInitialSession?.body.reason)} databaseError ${String((initialSession.body.readiness as JsonRecord | undefined)?.databaseError)}`,
  );
  assert(initialSession.body.authenticated === false, "initial session should be unauthenticated");
  assert(initialSession.body.user === null, "initial session should not invent a user");

  const signup = await fetchJson("/auth/sign-up/email", {
    method: "POST",
    headers: { "content-type": "application/json", origin: "http://127.0.0.1:5173" },
    body: JSON.stringify({
      name: "PS040F Runtime Smoke",
      email: testEmail,
      password: "ps040f-local-test-password-12345",
    }),
  });
  assert(
    signup.status < 500,
    `signup should not hit a server/runtime failure, got status ${signup.status} reason ${String(signup.body.reason ?? signup.body.message ?? signup.body.error)} server ${redactSmokeOutput(serverOutput)}`,
  );

  const pool = new pg.Pool({ connectionString: databaseUrl });
  const userResult = await pool.query<{ email_verified: boolean }>(
    "select email_verified from auth_user where email_normalized = lower($1)",
    [testEmail],
  );
  await pool.end();
  assert(
    userResult.rowCount === 1,
    `signup should create exactly one runtime user row, got rows ${userResult.rowCount ?? 0} signupStatus ${signup.status} reason ${String(signup.body.reason ?? signup.body.message ?? signup.body.error)} server ${redactSmokeOutput(serverOutput)}`,
  );
  assert(userResult.rows[0]?.email_verified === false, "signup user should remain unverified");

  const postSignupSession = await fetchJson("/session", {
    headers: { cookie: signup.headers.get("set-cookie") ?? "" },
  });
  assert(postSignupSession.body.authenticated === false, "signup should not create an authenticated session before verification");

  const login = await fetchJson("/auth/sign-in/email", {
    method: "POST",
    headers: { "content-type": "application/json", origin: "http://127.0.0.1:5173" },
    body: JSON.stringify({
      email: testEmail,
      password: "ps040f-local-test-password-12345",
      rememberMe: true,
    }),
  });
  assert(login.status >= 400, "login should not succeed before email verification");

  const logout = await fetchJson("/logout", { method: "POST", headers: { origin: "http://127.0.0.1:5173" } });
  assert(logout.status === 401, "logout without a session should report not performed");
  assert(logout.body.authenticated === false, "logout without a session must not report authenticated");

  console.log(JSON.stringify({
    smoke: "ps040f_configured_auth_runtime",
    result: "passed",
    database: summarizeDatabaseUrlSafety(safety),
    readyz: { status: ready.status, ready: ready.body.ready },
    signup: { status: signup.status, userCreated: true, emailVerified: false },
    login: { status: login.status, success: false, reason: "email_verification_required_or_runtime_rejected" },
    session: { initialAuthenticated: false, postSignupAuthenticated: false },
    logout: { status: logout.status, performed: false },
  }));

  if (serverOutput.includes(databaseUrl) || serverOutput.includes("ps040f-local-test-password")) {
    throw new Error("configured auth runtime smoke detected unsafe secret-like output");
  }
} finally {
  await cleanupTestRows().catch(() => undefined);
  if (server) {
    server.kill("SIGTERM");
    await new Promise((resolve) => server?.once("exit", resolve));
  }
}
