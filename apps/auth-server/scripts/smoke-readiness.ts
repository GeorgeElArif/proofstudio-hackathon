import { getAuthRuntimeReadiness, loadAuthRuntimeEnv } from "../src/env.js";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

const missing = getAuthRuntimeReadiness(loadAuthRuntimeEnv({}));
assert(!missing.envConfigured, "empty env should not be configured");
assert(missing.providers.database.status === "missing", "database should be missing");
assert(missing.providers.google.status === "missing", "google should be missing");
assert(missing.providers.email.status === "missing", "email should be missing");

const placeholders = getAuthRuntimeReadiness(
  loadAuthRuntimeEnv({
    PROOFSTUDIO_APP_BASE_URL: "https://example.localhost",
    PROOFSTUDIO_PUBLIC_WEB_URL: "https://replace-with-web-host",
    PROOFSTUDIO_AUTH_SECRET: "CHANGE_ME_AUTH_SECRET",
    PROOFSTUDIO_DATABASE_URL: "postgres://replace-with-host/replace-with-database",
    PROOFSTUDIO_CORS_ORIGINS: "http://127.0.0.1:5173",
    PROOFSTUDIO_EMAIL_PROVIDER: "replace-with-email-provider",
    PROOFSTUDIO_EMAIL_FROM: "no-reply@example.invalid",
    PROOFSTUDIO_EMAIL_API_KEY: "replace-with-email-provider-key",
    PROOFSTUDIO_DISPOSABLE_EMAIL_BLOCKLIST_SOURCE: "replace-with-disposable-domain-source",
    PROOFSTUDIO_GOOGLE_CLIENT_ID: "your-google-client-id",
    PROOFSTUDIO_GOOGLE_CLIENT_SECRET: "replace-with-google-client-secret",
  }),
);
assert(!placeholders.envConfigured, "placeholder env should not be configured");
assert(placeholders.providers.authBase.status === "placeholder", "auth base should detect placeholders");
assert(placeholders.providers.database.status === "placeholder", "database should detect placeholders");
assert(placeholders.providers.google.status === "placeholder", "google should detect placeholders");

const invalid = getAuthRuntimeReadiness(
  loadAuthRuntimeEnv({
    PROOFSTUDIO_APP_BASE_URL: "not-a-url",
    PROOFSTUDIO_PUBLIC_WEB_URL: "https://app.test",
    PROOFSTUDIO_AUTH_SECRET: "local-test-auth-secret",
    PROOFSTUDIO_DATABASE_URL: "sqlite://not-postgres",
    PROOFSTUDIO_CORS_ORIGINS: "http://127.0.0.1:5173",
    PROOFSTUDIO_EMAIL_PROVIDER: "api",
    PROOFSTUDIO_EMAIL_FROM: "bad-address",
    PROOFSTUDIO_EMAIL_API_KEY: "local-test-email-key",
    PROOFSTUDIO_DISPOSABLE_EMAIL_BLOCKLIST_SOURCE: "local",
  }),
);
assert(!invalid.envConfigured, "invalid-shaped env should not be configured");
assert(invalid.providers.authBase.status === "invalid_shape", "auth URL shape should be checked");
assert(invalid.providers.database.status === "invalid_shape", "database URL shape should be checked");
assert(invalid.providers.email.status === "invalid_shape", "email sender shape should be checked");

const configured = getAuthRuntimeReadiness(
  loadAuthRuntimeEnv({
    PROOFSTUDIO_APP_BASE_URL: "https://auth.test",
    PROOFSTUDIO_PUBLIC_WEB_URL: "https://app.test",
    PROOFSTUDIO_AUTH_SECRET: "local-test-auth-secret",
    PROOFSTUDIO_DATABASE_URL: "postgres://localhost/proofstudio_test",
    PROOFSTUDIO_CORS_ORIGINS: "http://127.0.0.1:5173",
    PROOFSTUDIO_EMAIL_PROVIDER: "api",
    PROOFSTUDIO_EMAIL_FROM: "no-reply@proofstudio.test",
    PROOFSTUDIO_EMAIL_API_KEY: "local-test-email-key",
    PROOFSTUDIO_DISPOSABLE_EMAIL_BLOCKLIST_SOURCE: "local",
    PROOFSTUDIO_GITHUB_CLIENT_ID: "github-local-client",
    PROOFSTUDIO_GITHUB_CLIENT_SECRET: "github-local-secret",
  }),
  null,
);
assert(configured.envConfigured, "local-shaped env should be configured");
assert(configured.providers.github.status === "configured", "github pair should be configured");
assert(configured.providers.apple.status === "missing", "optional apple provider can be missing");

console.log("PS-040D readiness smoke passed.");
