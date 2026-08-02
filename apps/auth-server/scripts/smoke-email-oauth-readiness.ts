import { getEmailDeliveryReadiness, sendVerificationEmailFoundation } from "../src/auth/email.js";
import { getAuthRuntimeReadiness, loadAuthRuntimeEnv } from "../src/env.js";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

const missingEmailEnv = loadAuthRuntimeEnv({});
const missingEmail = getEmailDeliveryReadiness(missingEmailEnv);
assert(missingEmail.status === "unavailable", "missing email config should be unavailable");

const captureEnv = loadAuthRuntimeEnv({
  PROOFSTUDIO_APP_BASE_URL: "http://127.0.0.1:8787",
  PROOFSTUDIO_PUBLIC_WEB_URL: "http://127.0.0.1:5173",
  PROOFSTUDIO_AUTH_SECRET: "ps040f-local-test-auth-secret-minimum-length",
  PROOFSTUDIO_DATABASE_URL: "postgres://proofstudio_auth_smoke:local_auth_smoke_password@127.0.0.1:55440/proofstudio_auth_smoke_test",
  PROOFSTUDIO_CORS_ORIGINS: "http://127.0.0.1:5173",
  PROOFSTUDIO_EMAIL_PROVIDER: "capture",
  PROOFSTUDIO_EMAIL_CAPTURE_MODE: "local",
});
const captureReadiness = getEmailDeliveryReadiness(captureEnv);
const captureRuntimeReadiness = getAuthRuntimeReadiness(captureEnv, true);
assert(
  captureRuntimeReadiness.envConfigured,
  "capture mode should not require live-delivery configuration",
);
assert(
  captureRuntimeReadiness.providers.email.status === "configured",
  "capture mode email provider should be configured without a sender",
);
assert(captureReadiness.status === "captured", "capture email mode should report local capture");
assert(
  (await sendVerificationEmailFoundation(captureEnv, {
    to: "person@proofstudio.test",
    verificationUrl: "http://127.0.0.1:8787/auth/verify-email?token=redacted",
  })).status === "captured",
  "capture email mode should not send live email or fail delivery",
);

const placeholderOAuth = getAuthRuntimeReadiness(loadAuthRuntimeEnv({
  ...captureEnvToRecord(captureEnv),
  PROOFSTUDIO_GOOGLE_CLIENT_ID: "your-google-client-id",
  PROOFSTUDIO_GOOGLE_CLIENT_SECRET: "replace-with-google-client-secret",
  PROOFSTUDIO_GITHUB_CLIENT_ID: "github-local-client",
}));
assert(placeholderOAuth.providers.google.status === "placeholder", "google placeholders should be detected");
assert(placeholderOAuth.providers.github.status === "invalid_shape", "partial github config should be invalid");

const configuredOAuth = getAuthRuntimeReadiness(loadAuthRuntimeEnv({
  ...captureEnvToRecord(captureEnv),
  PROOFSTUDIO_GOOGLE_CLIENT_ID: "google-local-test-client",
  PROOFSTUDIO_GOOGLE_CLIENT_SECRET: "google-local-test-secret",
  PROOFSTUDIO_GITHUB_CLIENT_ID: "github-local-test-client",
  PROOFSTUDIO_GITHUB_CLIENT_SECRET: "github-local-test-secret",
  PROOFSTUDIO_APPLE_CLIENT_ID: "com.proofstudio.local.test",
  PROOFSTUDIO_APPLE_TEAM_ID: "TEAMLOCAL1",
  PROOFSTUDIO_APPLE_KEY_ID: "KEYLOCAL1",
  PROOFSTUDIO_APPLE_PRIVATE_KEY: "apple-local-test-private-key-material",
}));
assert(configuredOAuth.providers.google.status === "configured", "google local test shape should configure");
assert(configuredOAuth.providers.github.status === "configured", "github local test shape should configure");
assert(configuredOAuth.providers.apple.status === "configured", "apple local test shape should configure");

console.log(JSON.stringify({
  smoke: "ps040f_email_oauth_readiness",
  result: "passed",
  email: {
    missingStatus: missingEmail.status,
    captureStatus: captureReadiness.status,
    captureProvider: captureReadiness.provider,
  },
  oauth: {
    googlePlaceholderStatus: placeholderOAuth.providers.google.status,
    githubPartialStatus: placeholderOAuth.providers.github.status,
    googleConfiguredStatus: configuredOAuth.providers.google.status,
    githubConfiguredStatus: configuredOAuth.providers.github.status,
    appleConfiguredStatus: configuredOAuth.providers.apple.status,
  },
}));

function captureEnvToRecord(env: ReturnType<typeof loadAuthRuntimeEnv>): NodeJS.ProcessEnv {
  return {
    PROOFSTUDIO_APP_BASE_URL: env.appBaseUrl,
    PROOFSTUDIO_PUBLIC_WEB_URL: env.publicWebUrl,
    PROOFSTUDIO_AUTH_SECRET: env.authSecret,
    PROOFSTUDIO_DATABASE_URL: env.databaseUrl,
    PROOFSTUDIO_CORS_ORIGINS: env.corsAllowedOrigins.join(","),
    PROOFSTUDIO_EMAIL_PROVIDER: env.email.provider,
    PROOFSTUDIO_EMAIL_CAPTURE_MODE: env.email.captureMode,
  };
}
