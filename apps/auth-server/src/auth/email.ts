import type { AuthRuntimeEnv } from "../env.js";

export type EmailVerificationRequest = {
  to: string;
  verificationUrl: string;
  userId?: string;
};

export type EmailSendResult = {
  status: "captured" | "deferred" | "unavailable";
  provider: "api" | "smtp" | "capture" | "none";
  reason: string;
};

function hasValue(value: string): boolean {
  return value.trim() !== "";
}

export function getEmailDeliveryReadiness(env: AuthRuntimeEnv): EmailSendResult {
  if (!hasValue(env.email.provider)) {
    return {
      status: "unavailable",
      provider: "none",
      reason: "email_provider_or_sender_missing",
    };
  }

  const provider = env.email.provider.trim().toLowerCase();

  if (provider === "capture") {
    return env.email.captureMode.trim().toLowerCase() === "local"
      ? { status: "captured", provider: "capture", reason: "local_capture_mode_no_live_email" }
      : { status: "unavailable", provider: "capture", reason: "email_capture_mode_not_local" };
  }

  if (!hasValue(env.email.from)) {
    return {
      status: "unavailable",
      provider: "none",
      reason: "email_provider_or_sender_missing",
    };
  }

  if (provider === "smtp") {
    return hasValue(env.email.smtpUrl)
      ? { status: "deferred", provider: "smtp", reason: "smtp_delivery_not_enabled_in_ps040d" }
      : { status: "unavailable", provider: "smtp", reason: "smtp_url_missing" };
  }

  return hasValue(env.email.providerApiKey)
    ? { status: "deferred", provider: "api", reason: "api_delivery_not_enabled_in_ps040d" }
    : { status: "unavailable", provider: "api", reason: "email_api_key_missing" };
}

export async function sendVerificationEmailFoundation(
  env: AuthRuntimeEnv,
  _request: EmailVerificationRequest,
): Promise<EmailSendResult> {
  const readiness = getEmailDeliveryReadiness(env);
  if (readiness.status === "unavailable") {
    return readiness;
  }

  if (readiness.status === "captured") {
    return readiness;
  }

  return {
    status: "deferred",
    provider: readiness.provider,
    reason: "live_email_delivery_deferred_until_provider_slice",
  };
}
