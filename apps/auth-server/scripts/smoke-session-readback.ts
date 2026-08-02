import { spawn } from "node:child_process";

const port = "18788";
const baseUrl = `http://127.0.0.1:${port}`;
const authEnvPrefixes = [
  "AUTH_",
  "DATABASE_URL",
  "CORS_ALLOWED_ORIGINS",
  "GOOGLE_",
  "GITHUB_",
  "APPLE_",
  "EMAIL_",
  "DISPOSABLE_EMAIL_",
  "SESSION_COOKIE_",
  "PROOFSTUDIO_APP_BASE_URL",
  "PROOFSTUDIO_AUTH_SECRET",
  "PROOFSTUDIO_DATABASE_URL",
  "PROOFSTUDIO_CORS_ORIGINS",
  "PROOFSTUDIO_GOOGLE_",
  "PROOFSTUDIO_GITHUB_",
  "PROOFSTUDIO_APPLE_",
  "PROOFSTUDIO_EMAIL_",
  "PROOFSTUDIO_DISPOSABLE_EMAIL_",
  "PROOFSTUDIO_SESSION_COOKIE_",
];

function scrubEnv(): NodeJS.ProcessEnv {
  const cleanEnv: NodeJS.ProcessEnv = {};
  for (const [key, value] of Object.entries(process.env)) {
    if (!authEnvPrefixes.some((prefix) => key.startsWith(prefix))) {
      cleanEnv[key] = value;
    }
  }
  cleanEnv.PROOFSTUDIO_AUTH_SERVER_PORT = port;
  return cleanEnv;
}

async function waitForServer(): Promise<void> {
  const startedAt = Date.now();
  while (Date.now() - startedAt < 10_000) {
    try {
      const response = await fetch(`${baseUrl}/healthz`);
      if (response.ok) return;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }
  throw new Error("auth server did not become reachable");
}

async function readJson(path: string, init?: RequestInit): Promise<{ status: number; body: Record<string, unknown> }> {
  const response = await fetch(`${baseUrl}${path}`, init);
  return { status: response.status, body: await response.json() as Record<string, unknown> };
}

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

const child = spawn("node", ["dist/src/server.js"], {
  cwd: process.cwd(),
  env: scrubEnv(),
  stdio: ["ignore", "pipe", "pipe"],
});

let stderr = "";
child.stderr.on("data", (chunk: Buffer) => {
  stderr += chunk.toString("utf8");
});

try {
  await waitForServer();

  const session = await readJson("/session");
  assert(session.status === 503, `/session expected 503 without env, got ${session.status}`);
  assert(session.body.state === "unavailable", "/session should report unavailable without env");
  assert(session.body.authenticated === false, "/session should not report authenticated without env");
  assert(!("user" in session.body), "/session should not return a user without env");
  assert(!("session" in session.body), "/session should not return a session without env");

  const authSession = await readJson("/auth/session");
  assert(authSession.status === 503, `/auth/session expected 503 without env, got ${authSession.status}`);
  assert(authSession.body.state === "unavailable", "/auth/session should use the safe readback wrapper");

  const logout = await readJson("/logout", { method: "POST" });
  assert(logout.status === 503, `/logout expected 503 without env, got ${logout.status}`);
  assert(logout.body.state === "unavailable", "/logout should report unavailable without env");
  assert(logout.body.authenticated === false, "/logout should not report authenticated without env");

  console.log("PS-040E session readback/logout missing-env smoke passed.");
} finally {
  child.kill("SIGTERM");
}

const exitCode = await new Promise<number>((resolve) => {
  child.on("exit", (code) => resolve(code ?? 0));
});

if (exitCode !== 0 && exitCode !== 143) {
  throw new Error(`auth server exited unexpectedly with ${exitCode}: ${stderr}`);
}
