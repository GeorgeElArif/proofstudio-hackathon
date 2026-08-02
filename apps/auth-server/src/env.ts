export type AuthRuntimeEnv = {
  appBaseUrl: string;
  publicWebUrl: string;
  authSecret: string;
  databaseUrl: string;
  corsAllowedOrigins: string[];
  proofApiBaseUrl: string;
  internalServiceToken: string;
  oauth: {
    googleClientId: string;
    googleClientSecret: string;
    githubClientId: string;
    githubClientSecret: string;
    appleClientId: string;
    appleTeamId: string;
    appleKeyId: string;
    applePrivateKey: string;
  };
  email: {
    provider: string;
    from: string;
    providerApiKey: string;
    smtpUrl: string;
    captureMode: string;
    disposableEmailBlocklistSource: string;
    domainAllowlist: string[];
    domainBlocklist: string[];
  };
  rateLimit: {
    windowSeconds: number;
    maxAttempts: number;
  };
  sessionCookie: {
    name: string;
    domain: string;
    secure: boolean;
  };
};

export type AuthRuntimeReadiness = {
  processLive: true;
  configured: boolean;
  envConfigured: boolean;
  databaseReachable: boolean | null;
  authRuntimeAvailable: boolean;
  missing: string[];
  placeholders: string[];
  providers: {
    authBase: ProviderConfigStatus;
    database: ProviderConfigStatus;
    email: ProviderConfigStatus;
    google: ProviderConfigStatus;
    github: ProviderConfigStatus;
    apple: ProviderConfigStatus;
  };
  databaseError?: string;
};

export type ProviderConfigStatus = {
  status: "configured" | "missing" | "placeholder" | "invalid_shape";
  required: boolean;
  safeName: string;
  issues: string[];
};

const PLACEHOLDER_MARKERS = [
  "",
  "CHANGE_ME",
  "replace-with",
  "your-",
  "placeholder",
  "example.",
  "localhost.invalid",
];

function readEnv(env: NodeJS.ProcessEnv, canonicalName: string, legacyName?: string): string {
  return env[canonicalName] ?? (legacyName ? env[legacyName] : undefined) ?? "";
}

function parseList(value: string): string[] {
  return value
    .split(",")
    .map((origin) => origin.trim())
    .filter(Boolean);
}

function parseInteger(value: string, fallback: number): number {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function parseBoolean(value: string): boolean {
  return value.toLowerCase() === "true";
}

function isPlaceholder(value: string): boolean {
  const normalized = value.trim();
  return PLACEHOLDER_MARKERS.some((marker) => marker !== "" && normalized.includes(marker));
}

function classifyRequiredValue(
  safeName: string,
  value: string,
  isValidShape: (value: string) => boolean = () => true,
): ProviderConfigStatus {
  const trimmed = value.trim();
  if (!trimmed) {
    return { safeName, required: true, status: "missing", issues: ["missing"] };
  }
  if (isPlaceholder(trimmed)) {
    return { safeName, required: true, status: "placeholder", issues: ["placeholder"] };
  }
  if (!isValidShape(trimmed)) {
    return { safeName, required: true, status: "invalid_shape", issues: ["invalid_shape"] };
  }
  return { safeName, required: true, status: "configured", issues: [] };
}

function classifyOptionalPair(
  safeName: string,
  first: string,
  second: string,
  isValidFirst: (value: string) => boolean = () => true,
): ProviderConfigStatus {
  const values = [first.trim(), second.trim()];
  const presentCount = values.filter(Boolean).length;
  if (presentCount === 0) {
    return { safeName, required: false, status: "missing", issues: ["missing"] };
  }
  if (values.some((value) => !value)) {
    return { safeName, required: false, status: "invalid_shape", issues: ["partial_config"] };
  }
  if (values.some((value) => isPlaceholder(value))) {
    return { safeName, required: false, status: "placeholder", issues: ["placeholder"] };
  }
  if (!isValidFirst(values[0])) {
    return { safeName, required: false, status: "invalid_shape", issues: ["invalid_shape"] };
  }
  return { safeName, required: false, status: "configured", issues: [] };
}

function looksLikeUrl(value: string): boolean {
  try {
    const parsed = new URL(value);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

function looksLikeDatabaseUrl(value: string): boolean {
  try {
    const parsed = new URL(value);
    return parsed.protocol === "postgres:" || parsed.protocol === "postgresql:";
  } catch {
    return false;
  }
}

function looksLikeEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function combineProviderStatus(
  safeName: string,
  required: boolean,
  statuses: ProviderConfigStatus[],
): ProviderConfigStatus {
  const rank = ["invalid_shape", "placeholder", "missing", "configured"] as const;
  const status = rank.find((candidate) => statuses.some((item) => item.status === candidate)) ?? "configured";
  return {
    safeName,
    required,
    status,
    issues: [...new Set(statuses.flatMap((item) => item.issues))],
  };
}

export function loadAuthRuntimeEnv(env: NodeJS.ProcessEnv = process.env): AuthRuntimeEnv {
  return {
    appBaseUrl: readEnv(env, "PROOFSTUDIO_APP_BASE_URL", "AUTH_BASE_URL"),
    publicWebUrl: readEnv(env, "PROOFSTUDIO_PUBLIC_WEB_URL"),
    authSecret: readEnv(env, "PROOFSTUDIO_AUTH_SECRET", "AUTH_SECRET"),
    databaseUrl: readEnv(env, "PROOFSTUDIO_DATABASE_URL", "DATABASE_URL"),
    corsAllowedOrigins: parseList(readEnv(env, "PROOFSTUDIO_CORS_ORIGINS", "CORS_ALLOWED_ORIGINS")),
    proofApiBaseUrl: readEnv(env, "PROOFSTUDIO_PROOF_API_BASE_URL"),
    internalServiceToken: readEnv(env, "PROOFSTUDIO_INTERNAL_SERVICE_TOKEN"),
    oauth: {
      googleClientId: readEnv(env, "PROOFSTUDIO_GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_ID"),
      googleClientSecret: readEnv(env, "PROOFSTUDIO_GOOGLE_CLIENT_SECRET", "GOOGLE_CLIENT_SECRET"),
      githubClientId: readEnv(env, "PROOFSTUDIO_GITHUB_CLIENT_ID", "GITHUB_CLIENT_ID"),
      githubClientSecret: readEnv(env, "PROOFSTUDIO_GITHUB_CLIENT_SECRET", "GITHUB_CLIENT_SECRET"),
      appleClientId: readEnv(env, "PROOFSTUDIO_APPLE_CLIENT_ID", "APPLE_CLIENT_ID"),
      appleTeamId: readEnv(env, "PROOFSTUDIO_APPLE_TEAM_ID", "APPLE_TEAM_ID"),
      appleKeyId: readEnv(env, "PROOFSTUDIO_APPLE_KEY_ID", "APPLE_KEY_ID"),
      applePrivateKey: readEnv(env, "PROOFSTUDIO_APPLE_PRIVATE_KEY", "APPLE_PRIVATE_KEY"),
    },
    email: {
      provider: readEnv(env, "PROOFSTUDIO_EMAIL_PROVIDER", "EMAIL_PROVIDER"),
      from: readEnv(env, "PROOFSTUDIO_EMAIL_FROM", "EMAIL_FROM"),
      providerApiKey: readEnv(env, "PROOFSTUDIO_EMAIL_API_KEY", "EMAIL_PROVIDER_API_KEY"),
      smtpUrl: readEnv(env, "PROOFSTUDIO_EMAIL_SMTP_URL", "EMAIL_SMTP_URL"),
      captureMode: readEnv(env, "PROOFSTUDIO_EMAIL_CAPTURE_MODE", "EMAIL_CAPTURE_MODE"),
      disposableEmailBlocklistSource: readEnv(
        env,
        "PROOFSTUDIO_DISPOSABLE_EMAIL_BLOCKLIST_SOURCE",
        "DISPOSABLE_EMAIL_BLOCKLIST_SOURCE",
      ),
      domainAllowlist: parseList(readEnv(env, "PROOFSTUDIO_EMAIL_DOMAIN_ALLOWLIST", "EMAIL_DOMAIN_ALLOWLIST")),
      domainBlocklist: parseList(readEnv(env, "PROOFSTUDIO_EMAIL_DOMAIN_BLOCKLIST", "EMAIL_DOMAIN_BLOCKLIST")),
    },
    rateLimit: {
      windowSeconds: parseInteger(
        readEnv(env, "PROOFSTUDIO_AUTH_RATE_LIMIT_WINDOW_SECONDS", "AUTH_RATE_LIMIT_WINDOW_SECONDS"),
        300,
      ),
      maxAttempts: parseInteger(
        readEnv(env, "PROOFSTUDIO_AUTH_RATE_LIMIT_MAX_ATTEMPTS", "AUTH_RATE_LIMIT_MAX_ATTEMPTS"),
        5,
      ),
    },
    sessionCookie: {
      name: readEnv(env, "PROOFSTUDIO_SESSION_COOKIE_NAME", "SESSION_COOKIE_NAME") || "proofstudio_session",
      domain: readEnv(env, "PROOFSTUDIO_SESSION_COOKIE_DOMAIN", "SESSION_COOKIE_DOMAIN"),
      secure: parseBoolean(readEnv(env, "PROOFSTUDIO_SESSION_COOKIE_SECURE", "SESSION_COOKIE_SECURE")),
    },
  };
}

export function getAuthRuntimeReadiness(
  config: AuthRuntimeEnv,
  databaseReachable: boolean | null = null,
  databaseError?: string,
): AuthRuntimeReadiness {
  const captureEmailMode =
    config.email.provider.trim().toLowerCase() === "capture" &&
    config.email.captureMode.trim().toLowerCase() === "local";

  const requiredValues: Record<string, string> = {
    PROOFSTUDIO_APP_BASE_URL: config.appBaseUrl,
    PROOFSTUDIO_PUBLIC_WEB_URL: config.publicWebUrl,
    PROOFSTUDIO_AUTH_SECRET: config.authSecret,
    PROOFSTUDIO_DATABASE_URL: config.databaseUrl,
    PROOFSTUDIO_CORS_ORIGINS: config.corsAllowedOrigins.join(","),
    PROOFSTUDIO_EMAIL_PROVIDER: config.email.provider,
    ...(captureEmailMode
      ? {}
      : {
          PROOFSTUDIO_EMAIL_FROM: config.email.from,
          PROOFSTUDIO_DISPOSABLE_EMAIL_BLOCKLIST_SOURCE:
            config.email.disposableEmailBlocklistSource,
        }),
  };

  const missing = Object.entries(requiredValues)
    .filter(([, value]) => value.trim() === "")
    .map(([name]) => name);

  const placeholders = Object.entries(requiredValues)
    .filter(([, value]) => isPlaceholder(value))
    .map(([name]) => name);

  const emailCredentialStatus = (() => {
    if (config.email.provider.toLowerCase() === "capture") {
      return classifyRequiredValue("email_capture_mode", config.email.captureMode, (value) => value === "local");
    }

    if (config.email.provider.toLowerCase() === "smtp") {
      return classifyRequiredValue("email_smtp_url", config.email.smtpUrl, (value) => {
        try {
          const parsed = new URL(value);
          return parsed.protocol === "smtp:" || parsed.protocol === "smtps:";
        } catch {
          return false;
        }
      });
    }

    return classifyRequiredValue("email_api_key", config.email.providerApiKey);
  })();
  const providers = {
    authBase: combineProviderStatus("auth_base", true, [
      classifyRequiredValue("app_base_url", config.appBaseUrl, looksLikeUrl),
      classifyRequiredValue("public_web_url", config.publicWebUrl, looksLikeUrl),
      classifyRequiredValue("auth_secret", config.authSecret),
    ]),
    database: classifyRequiredValue("database", config.databaseUrl, looksLikeDatabaseUrl),
    email: combineProviderStatus("email", true, [
      classifyRequiredValue("email_provider", config.email.provider),
      ...(captureEmailMode
        ? []
        : [
            classifyRequiredValue(
              "email_from",
              config.email.from,
              looksLikeEmail,
            ),
          ]),
      emailCredentialStatus,
    ]),
    google: classifyOptionalPair(
      "google_oauth",
      config.oauth.googleClientId,
      config.oauth.googleClientSecret,
    ),
    github: classifyOptionalPair(
      "github_oauth",
      config.oauth.githubClientId,
      config.oauth.githubClientSecret,
    ),
    apple: combineProviderStatus("apple_oauth", false, [
      classifyOptionalPair("apple_client", config.oauth.appleClientId, config.oauth.applePrivateKey),
      classifyOptionalPair("apple_team_key", config.oauth.appleTeamId, config.oauth.appleKeyId),
    ]),
  };
  const requiredProvidersConfigured = Object.values(providers)
    .filter((provider) => provider.required)
    .every((provider) => provider.status === "configured");
  const envConfigured = missing.length === 0 && placeholders.length === 0 && requiredProvidersConfigured;
  const authRuntimeAvailable = envConfigured && databaseReachable !== false;

  return {
    processLive: true,
    configured: envConfigured && databaseReachable !== false,
    envConfigured,
    databaseReachable,
    authRuntimeAvailable,
    missing,
    placeholders,
    providers,
    ...(databaseError ? { databaseError } : {}),
  };
}
