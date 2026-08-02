export type ProviderConfigStatus = {
  status: "configured" | "missing" | "placeholder" | "invalid_shape";
  required: boolean;
  safeName: string;
  issues: string[];
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

export type AuthHealthResponse = {
  service: "proofstudio-auth-server";
  liveRuntimeAuth: boolean;
  ready: boolean;
  readiness: AuthRuntimeReadiness;
  trustBoundary: string;
};

export type AuthSessionReadback =
  | {
      state: "authenticated";
      authenticated: true;
      liveRuntimeAuth: true;
      readiness: AuthRuntimeReadiness;
      session: {
        id: string | null;
        userId: string | null;
        expiresAt: string | null;
        createdAt: string | null;
        updatedAt: string | null;
      };
      user: {
        id: string | null;
        email: string | null;
        name: string | null;
        emailVerified: boolean;
        image: string | null;
      };
    }
  | {
      state: "unauthenticated";
      authenticated: false;
      liveRuntimeAuth: boolean;
      readiness: AuthRuntimeReadiness;
      session: null;
      user: null;
      reason?: string;
      logout?: "not_performed";
    }
  | {
      state: "unavailable";
      authenticated: false;
      liveRuntimeAuth: false;
      readiness?: AuthRuntimeReadiness;
      reason: string;
      error?: string;
    }
  | {
      state: "network_error";
      authenticated: false;
      liveRuntimeAuth: false;
      reason: string;
    };

export type AuthActionResult =
  | {
      state: "accepted";
      ok: true;
      message: string;
    }
  | {
      state: "unavailable" | "rejected" | "network_error";
      ok: false;
      message: string;
      status?: number;
    };

export type LoginInput = {
  email: string;
  password: string;
};

export type SignupInput = LoginInput & {
  name: string;
};

const DEFAULT_AUTH_BASE_URL = "http://127.0.0.1:8787";

function normalizeAuthBaseUrl(value: string): string {
  const normalized = value.trim().replace(/\/+$/, "");
  if (normalized.startsWith("//")) {
    throw new Error("Protocol-relative auth base URLs are not allowed.");
  }
  return normalized;
}

export function resolveAuthBaseUrl(
  configuredAuthBaseUrl: string | undefined,
  productionBrowser: boolean,
  browserOrigin: string | undefined,
): string {
  const configured = configuredAuthBaseUrl?.trim();
  if (configured) {
    return normalizeAuthBaseUrl(configured);
  }
  if (productionBrowser && browserOrigin?.trim()) {
    return normalizeAuthBaseUrl(browserOrigin);
  }
  return DEFAULT_AUTH_BASE_URL;
}

export function getAuthBaseUrl(): string {
  return resolveAuthBaseUrl(
    import.meta.env.VITE_PROOFSTUDIO_AUTH_BASE_URL,
    import.meta.env.PROD && typeof window !== "undefined",
    typeof window !== "undefined" ? window.location.origin : undefined,
  );
}

async function readJson<T>(response: Response): Promise<T> {
  return (await response.json()) as T;
}

function actionMessage(payload: unknown, fallback: string): string {
  if (typeof payload === "object" && payload !== null) {
    const maybeReason = "reason" in payload ? payload.reason : undefined;
    const maybeMessage = "message" in payload ? payload.message : undefined;
    if (typeof maybeReason === "string") return maybeReason;
    if (typeof maybeMessage === "string") return maybeMessage;
  }
  return fallback;
}

export async function getAuthReadiness(): Promise<AuthHealthResponse | null> {
  try {
    const response = await fetch(`${getAuthBaseUrl()}/readyz`, {
      credentials: "include",
      headers: { accept: "application/json" },
    });
    return await readJson<AuthHealthResponse>(response);
  } catch {
    return null;
  }
}

export async function getAuthSession(): Promise<AuthSessionReadback> {
  try {
    const response = await fetch(`${getAuthBaseUrl()}/session`, {
      credentials: "include",
      headers: { accept: "application/json" },
    });
    const payload = await readJson<AuthSessionReadback>(response);
    if (!response.ok && payload.state !== "unavailable") {
      return {
        state: "unavailable",
        authenticated: false,
        liveRuntimeAuth: false,
        readiness: "readiness" in payload ? payload.readiness : undefined,
        reason: actionMessage(payload, "Auth session readback is unavailable."),
      };
    }
    return payload;
  } catch {
    return {
      state: "network_error",
      authenticated: false,
      liveRuntimeAuth: false,
      reason: "Auth server is not reachable from this browser session.",
    };
  }
}

export async function submitLogin(input: LoginInput): Promise<AuthActionResult> {
  return submitAuthAction("/auth/sign-in/email", {
    email: input.email,
    password: input.password,
    rememberMe: true,
  }, "Login request was accepted by the auth server. Session readback is the source of truth for whether a session exists.");
}

export async function submitSignup(input: SignupInput): Promise<AuthActionResult> {
  return submitAuthAction("/auth/sign-up/email", {
    name: input.name,
    email: input.email,
    password: input.password,
  }, "Signup request was accepted by the auth server. Email verification and session readback remain server-owned.");
}

export async function submitLogout(): Promise<AuthActionResult> {
  return submitAuthAction("/logout", undefined, "Logout request was accepted by the auth server. Session readback will confirm the current state.");
}

async function submitAuthAction(
  path: string,
  body: Record<string, unknown> | undefined,
  successMessage: string,
): Promise<AuthActionResult> {
  try {
    const response = await fetch(`${getAuthBaseUrl()}${path}`, {
      method: "POST",
      credentials: "include",
      headers: {
        accept: "application/json",
        ...(body ? { "content-type": "application/json" } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    const payload = await response.json().catch(() => null) as unknown;
    if (!response.ok) {
      return {
        state: response.status === 503 ? "unavailable" : "rejected",
        ok: false,
        status: response.status,
        message: actionMessage(payload, "The auth server did not accept this request."),
      };
    }
    return { state: "accepted", ok: true, message: successMessage };
  } catch {
    return {
      state: "network_error",
      ok: false,
      message: "Auth server is not reachable from this browser session.",
    };
  }
}
