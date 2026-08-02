import { spawn } from "node:child_process";

const port = Number.parseInt(process.env.PROOFSTUDIO_AUTH_CONFIGURED_WEB_SMOKE_PORT ?? "8792", 10);
const databaseUrl =
  process.env.PROOFSTUDIO_DATABASE_URL ??
  process.env.DATABASE_URL ??
  "postgres://proofstudio_auth_smoke:local_auth_smoke_password@127.0.0.1:55440/proofstudio_auth_smoke_test";
const baseUrl = process.env.PROOFSTUDIO_AUTH_SMOKE_BASE_URL ?? `http://127.0.0.1:${port}`;

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

async function readJson(path) {
  const response = await fetch(`${baseUrl}${path}`, {
    headers: { accept: "application/json" },
    credentials: "include",
  });
  return { status: response.status, body: await response.json() };
}

function classifyDatabaseUrlSafety(rawUrl) {
  try {
    const parsed = new URL(rawUrl);
    const host = parsed.hostname.toLowerCase();
    const databaseName = parsed.pathname.replace(/^\/+/, "").toLowerCase();
    const local = host === "127.0.0.1" || host === "localhost" || host === "::1";
    const disposable = ["test", "local", "smoke", "dev"].some((marker) => databaseName.includes(marker));
    const productionLike = ["prod", "production", "supabase.co"].some((marker) =>
      `${host}/${databaseName}`.includes(marker),
    );
    if ((parsed.protocol !== "postgres:" && parsed.protocol !== "postgresql:") || productionLike) return "unsafe";
    return local && disposable ? "local_test" : "unsafe";
  } catch {
    return "unsafe";
  }
}

async function waitForReady() {
  const deadline = Date.now() + 15_000;
  while (Date.now() < deadline) {
    try {
      const ready = await readJson("/readyz");
      if (ready.status === 200) return ready;
    } catch {
      // Server still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error("configured auth server did not become ready for web smoke");
}

assert(classifyDatabaseUrlSafety(databaseUrl) === "local_test", "web configured auth smoke requires a local disposable test DB");

const server = spawn(process.execPath, ["../auth-server/dist/src/server.js"], {
  env: {
    ...process.env,
    PROOFSTUDIO_APP_BASE_URL: `http://127.0.0.1:${port}`,
    PROOFSTUDIO_PUBLIC_WEB_URL: "http://127.0.0.1:5173",
    PROOFSTUDIO_AUTH_SECRET: "ps040f-local-test-auth-secret-minimum-length",
    PROOFSTUDIO_DATABASE_URL: databaseUrl,
    PROOFSTUDIO_CORS_ORIGINS: "http://127.0.0.1:5173,http://localhost:5173",
    PROOFSTUDIO_EMAIL_PROVIDER: "capture",
    PROOFSTUDIO_EMAIL_FROM: "no-reply@proofstudio.test",
    PROOFSTUDIO_EMAIL_CAPTURE_MODE: "local",
    PROOFSTUDIO_DISPOSABLE_EMAIL_BLOCKLIST_SOURCE: "local",
    PROOFSTUDIO_AUTH_RATE_LIMIT_WINDOW_SECONDS: "60",
    PROOFSTUDIO_AUTH_RATE_LIMIT_MAX_ATTEMPTS: "20",
    PROOFSTUDIO_SESSION_COOKIE_NAME: "proofstudio_ps040f_web_test",
    PROOFSTUDIO_SESSION_COOKIE_SECURE: "false",
    PROOFSTUDIO_AUTH_SERVER_HOST: "127.0.0.1",
    PROOFSTUDIO_AUTH_SERVER_PORT: String(port),
  },
  stdio: ["ignore", "pipe", "pipe"],
});

try {
  const ready = await waitForReady();
  assert(ready.body.ready === true, "web smoke should see configured readiness");
  assert(ready.body.readiness?.authRuntimeAvailable === true, "web smoke should see runtime availability");

  const session = await readJson("/session");
  assert(session.status === 200, "web smoke should read session state");
  assert(session.body.authenticated === false, "web smoke should not invent an authenticated user");
  assert(session.body.user === null, "web smoke should not receive a user without server-owned session");

  console.log(JSON.stringify({
    smoke: "ps040f_web_configured_auth_runtime",
    result: "passed",
    readyz: { status: ready.status, ready: ready.body.ready },
    session: { authenticated: false, user: null },
  }));
} finally {
  server.kill("SIGTERM");
  await new Promise((resolve) => server.once("exit", resolve));
}
