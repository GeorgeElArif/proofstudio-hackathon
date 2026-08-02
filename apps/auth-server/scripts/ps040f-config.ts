export const DEFAULT_TEST_DATABASE_URL =
  "postgres://proofstudio_auth_smoke:local_auth_smoke_password@127.0.0.1:55440/proofstudio_auth_smoke_test";

export function getSmokeDatabaseUrl(): string {
  return process.env.PROOFSTUDIO_DATABASE_URL ?? process.env.DATABASE_URL ?? DEFAULT_TEST_DATABASE_URL;
}

export function getConfiguredAuthSmokeEnv(port: number): NodeJS.ProcessEnv {
  return {
    ...process.env,
    PROOFSTUDIO_APP_BASE_URL: `http://127.0.0.1:${port}`,
    PROOFSTUDIO_PUBLIC_WEB_URL: "http://127.0.0.1:5173",
    PROOFSTUDIO_AUTH_SECRET: "ps040f-local-test-auth-secret-minimum-length",
    PROOFSTUDIO_DATABASE_URL: getSmokeDatabaseUrl(),
    PROOFSTUDIO_CORS_ORIGINS: "http://127.0.0.1:5173,http://localhost:5173",
    PROOFSTUDIO_EMAIL_PROVIDER: "capture",
    PROOFSTUDIO_EMAIL_FROM: "no-reply@proofstudio.test",
    PROOFSTUDIO_EMAIL_CAPTURE_MODE: "local",
    PROOFSTUDIO_DISPOSABLE_EMAIL_BLOCKLIST_SOURCE: "local",
    PROOFSTUDIO_AUTH_RATE_LIMIT_WINDOW_SECONDS: "60",
    PROOFSTUDIO_AUTH_RATE_LIMIT_MAX_ATTEMPTS: "20",
    PROOFSTUDIO_SESSION_COOKIE_NAME: "proofstudio_ps040f_test",
    PROOFSTUDIO_SESSION_COOKIE_SECURE: "false",
    PROOFSTUDIO_AUTH_SERVER_HOST: "127.0.0.1",
    PROOFSTUDIO_AUTH_SERVER_PORT: String(port),
  };
}
