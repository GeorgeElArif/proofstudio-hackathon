import { spawn } from "node:child_process";

const port = "18787";
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
      if (response.ok) {
        return;
      }
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }
  throw new Error("auth server did not become reachable");
}

async function readJson(path: string): Promise<{ status: number; body: unknown }> {
  const response = await fetch(`${baseUrl}${path}`);
  return { status: response.status, body: await response.json() };
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

  const healthz = await readJson("/healthz");
  assert(healthz.status === 200, `/healthz expected 200, got ${healthz.status}`);

  const readyz = await readJson("/readyz");
  assert(readyz.status === 503, `/readyz expected 503 without env, got ${readyz.status}`);
  assert(
    typeof readyz.body === "object" &&
      readyz.body !== null &&
      "ready" in readyz.body &&
      readyz.body.ready === false,
    "/readyz did not report not ready",
  );
  assert(
    typeof readyz.body === "object" &&
      readyz.body !== null &&
      "readiness" in readyz.body &&
      typeof readyz.body.readiness === "object" &&
      readyz.body.readiness !== null &&
      "providers" in readyz.body.readiness,
    "/readyz did not include safe provider readiness categories",
  );

  const authSession = await readJson("/auth/session");
  assert(
    authSession.status === 503,
    `/auth/session expected fail-closed 503 without env, got ${authSession.status}`,
  );
  assert(
    typeof authSession.body === "object" &&
      authSession.body !== null &&
      !("user" in authSession.body) &&
      !("session" in authSession.body),
    "/auth/session returned fake authenticated data",
  );

  console.log("PS-040D missing-env auth boundary smoke passed.");
} finally {
  child.kill("SIGTERM");
}

const exitCode = await new Promise<number>((resolve) => {
  child.on("exit", (code) => resolve(code ?? 0));
});

if (exitCode !== 0 && exitCode !== 143) {
  throw new Error(`auth server exited unexpectedly with ${exitCode}: ${stderr}`);
}
