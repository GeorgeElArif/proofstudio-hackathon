import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { randomUUID } from "node:crypto";

import { writeAuthAuditEvent, type AuthAuditEventType } from "./audit.js";
import { evaluateEmailDomainPolicy } from "./domain-policy.js";
import { sendVerificationEmailFoundation } from "./email.js";
import { createAuthDatabase, type AuthDatabase } from "../db/client.js";
import * as schema from "../db/schema.js";
import type { AuthRuntimeEnv, AuthRuntimeReadiness } from "../env.js";
import { decodeCampaignCursor, listAccountCampaigns } from "../account/campaign-access.js";
import { decideCampaignProofRead } from "../account/proof-access.js";
import { isValidProofIdentifier } from "../account/proof-identifier.js";
import { readPrivateLineageBundle, readPrivateLineageList, readPrivateLineagePassport, readPrivatePassport, readPrivateProofRoom } from "../proof/proof-api-client.js";

export type BetterAuthOptions = Parameters<typeof betterAuth>[0];
type BetterAuthRuntime = ReturnType<typeof betterAuth>;

export type AuthBoundaryRuntime = {
  live: boolean;
  reason: string;
  getReadiness: (databaseReachable?: boolean | null, databaseError?: string) => AuthRuntimeReadiness;
  handleAuthRequest: (request: Request) => Promise<Response>;
  handleSessionReadback: (request: Request) => Promise<Response>;
  handleLogoutRequest: (request: Request) => Promise<Response>;
  handleAccountCampaigns: (request: Request) => Promise<Response>;
  handlePrivateProofRoom: (request: Request, campaignId: string) => Promise<Response>;
  handlePrivatePassport: (request: Request, campaignId: string, runId: string) => Promise<Response>;
  handlePrivateLineage: (request: Request, campaignId: string, bundleId?: string) => Promise<Response>;
  handlePrivateLineagePassport: (request: Request, campaignId: string, bundleId: string) => Promise<Response>;
  close: () => Promise<void>;
};

type BetterAuthSessionPayload = {
  session?: {
    id?: unknown;
    userId?: unknown;
    expiresAt?: unknown;
    createdAt?: unknown;
    updatedAt?: unknown;
  } | null;
  user?: {
    id?: unknown;
    email?: unknown;
    name?: unknown;
    emailVerified?: unknown;
    image?: unknown;
  } | null;
} | null;

function hasValue(value: string): boolean {
  return value.trim() !== "";
}

function configuredPair(id: string, secret: string): boolean {
  return hasValue(id) && hasValue(secret);
}

function createSocialProviders(env: AuthRuntimeEnv): BetterAuthOptions["socialProviders"] {
  const providers: NonNullable<BetterAuthOptions["socialProviders"]> = {};

  if (configuredPair(env.oauth.googleClientId, env.oauth.googleClientSecret)) {
    providers.google = {
      clientId: env.oauth.googleClientId,
      clientSecret: env.oauth.googleClientSecret,
    };
  }

  if (configuredPair(env.oauth.githubClientId, env.oauth.githubClientSecret)) {
    providers.github = {
      clientId: env.oauth.githubClientId,
      clientSecret: env.oauth.githubClientSecret,
    };
  }

  if (
    hasValue(env.oauth.appleClientId) &&
    hasValue(env.oauth.applePrivateKey)
  ) {
    providers.apple = {
      clientId: env.oauth.appleClientId,
      clientSecret: env.oauth.applePrivateKey,
    };
  }

  return providers;
}

async function recordAuditFoundation(
  database: AuthDatabase | null,
  eventType: AuthAuditEventType,
  metadata: Record<string, unknown> = {},
  userId?: string,
): Promise<void> {
  const result = await writeAuthAuditEvent(database, {
    eventType,
    userId,
    actorUserId: userId,
    outcome: database ? "succeeded" : "unavailable",
    reason: database ? undefined : "database_not_configured",
    metadata,
  });

  console.info(
    JSON.stringify({
      component: "proofstudio-auth-server",
      slice: "PS-040D",
      eventType,
      auditPersistence: result.status,
      metadataKeys: Object.keys(metadata).sort(),
    }),
  );
}

function createBetterAuthOptions(env: AuthRuntimeEnv, database: AuthDatabase): BetterAuthOptions {
  return {
    appName: "ProofStudio",
    baseURL: env.appBaseUrl,
    basePath: "/auth",
    secret: env.authSecret,
    database: drizzleAdapter(database.db, {
      provider: "pg",
      schema,
    }),
    trustedOrigins: [env.publicWebUrl, ...env.corsAllowedOrigins],
    emailAndPassword: {
      enabled: true,
      requireEmailVerification: true,
      autoSignIn: false,
    },
    emailVerification: {
      sendOnSignUp: true,
      autoSignInAfterVerification: false,
      sendVerificationEmail: async ({ user, url }) => {
        const result = await sendVerificationEmailFoundation(env, {
          to: user.email,
          verificationUrl: url,
          userId: user.id,
        });
        await recordAuditFoundation(database, "email_verification_requested", {
          emailDelivery: result.status,
          emailProvider: result.provider,
          reason: result.reason,
          email: user.email,
        }, user.id);
        throw new Error(`Email verification delivery ${result.status}: ${result.reason}`);
      },
      afterEmailVerification: async (user) => {
        await recordAuditFoundation(database, "email_verified", { userId: user.id }, user.id);
      },
    },
    socialProviders: createSocialProviders(env),
    rateLimit: {
      enabled: true,
      storage: "database",
      window: env.rateLimit.windowSeconds,
      max: env.rateLimit.maxAttempts,
      fields: {
        lastRequest: "last_request",
      },
    },
    user: {
      fields: {
        emailVerified: "email_verified",
        createdAt: "created_at",
        updatedAt: "updated_at",
      },
      additionalFields: {
        email_normalized: {
          type: "string",
          fieldName: "email_normalized",
          required: false,
          input: false,
        },
        username: {
          type: "string",
          required: false,
        },
        disabledAt: {
          type: "date",
          fieldName: "disabled_at",
          required: false,
          input: false,
        },
        emailVerifiedAt: {
          type: "date",
          fieldName: "email_verified_at",
          required: false,
          input: false,
        },
      },
    },
    account: {
      fields: {
        providerId: "provider_id",
        accountId: "account_id",
        userId: "user_id",
        accessToken: "access_token",
        refreshToken: "refresh_token",
        idToken: "id_token",
        accessTokenExpiresAt: "access_token_expires_at",
        refreshTokenExpiresAt: "refresh_token_expires_at",
        createdAt: "created_at",
        updatedAt: "updated_at",
      },
      encryptOAuthTokens: true,
    },
    session: {
      fields: {
        userId: "user_id",
        ipAddress: "ip_address",
        userAgent: "user_agent",
        expiresAt: "expires_at",
        createdAt: "created_at",
        updatedAt: "updated_at",
      },
    },
    verification: {
      fields: {
        expiresAt: "expires_at",
        createdAt: "created_at",
        updatedAt: "updated_at",
      },
      additionalFields: {
        purpose: {
          type: "string",
          required: true,
          defaultValue: "email_verification",
        },
        consumedAt: {
          type: "date",
          fieldName: "consumed_at",
          required: false,
          input: false,
        },
      },
      storeIdentifier: "hashed",
    },
    advanced: {
      useSecureCookies: env.sessionCookie.secure,
      cookiePrefix: env.sessionCookie.name,
      ...(env.sessionCookie.domain
        ? {
            crossSubDomainCookies: {
              enabled: true,
              domain: env.sessionCookie.domain,
            },
          }
        : {}),
    },
    databaseHooks: {
      user: {
        create: {
          before: async (user) => ({
            data: (() => {
              const emailPolicy =
                typeof user.email === "string"
                  ? evaluateEmailDomainPolicy(user.email, {
                      allowlist: env.email.domainAllowlist,
                      blocklist: env.email.domainBlocklist,
                    })
                  : { allowed: false, reason: "invalid_email_syntax" as const };

              if (!emailPolicy.allowed) {
                throw new Error(`Email domain blocked: ${emailPolicy.reason}`);
              }

              return {
                ...user,
                email_normalized: emailPolicy.normalizedEmail,
              };
            })(),
          }),
          after: async (user) => {
            await recordAuditFoundation(database, "signup_requested", { userId: user.id }, user.id);
          },
        },
      },
      session: {
        create: {
          after: async (session) => {
            await recordAuditFoundation(database, "login_succeeded", { userId: session.userId }, session.userId);
          },
        },
        delete: {
          after: async (session) => {
            await recordAuditFoundation(database, "logout", { userId: session.userId }, session.userId);
          },
        },
      },
      account: {
        create: {
          after: async (account) => {
            await recordAuditFoundation(database, "oauth_linked", {
              userId: account.userId,
              providerId: account.providerId,
            }, account.userId);
          },
        },
      },
    },
    telemetry: {
      enabled: false,
    },
  };
}

function failClosed(readiness: AuthRuntimeReadiness, reason: string): Response {
  return Response.json(
    {
      error: "auth_runtime_unavailable",
      state: "unavailable",
      authenticated: false,
      liveRuntimeAuth: false,
      reason,
      readiness,
    },
    { status: 503 },
  );
}

function stringOrNull(value: unknown): string | null {
  return typeof value === "string" && value.trim() !== "" ? value : null;
}

function booleanOrFalse(value: unknown): boolean {
  return typeof value === "boolean" ? value : false;
}

function sanitizeSessionPayload(payload: BetterAuthSessionPayload) {
  if (!payload?.session || !payload.user) {
    return null;
  }

  return {
    session: {
      id: stringOrNull(payload.session.id),
      userId: stringOrNull(payload.session.userId),
      expiresAt: stringOrNull(payload.session.expiresAt),
      createdAt: stringOrNull(payload.session.createdAt),
      updatedAt: stringOrNull(payload.session.updatedAt),
    },
    user: {
      id: stringOrNull(payload.user.id),
      email: stringOrNull(payload.user.email),
      name: stringOrNull(payload.user.name),
      emailVerified: booleanOrFalse(payload.user.emailVerified),
      image: stringOrNull(payload.user.image),
    },
  };
}

export function createAuthBoundaryRuntime(
  env: AuthRuntimeEnv,
  getReadiness: (databaseReachable?: boolean | null, databaseError?: string) => AuthRuntimeReadiness,
): AuthBoundaryRuntime {
  let database: AuthDatabase | null = null;
  let auth: BetterAuthRuntime | null = null;

  function rewriteAuthRequest(request: Request, pathname: string, method = request.method): Request {
    const url = new URL(request.url);
    url.pathname = pathname;
    url.search = pathname === "/auth/get-session" ? "?disableCookieCache=true&disableRefresh=true" : "";
    return new Request(url, {
      method,
      headers: request.headers,
    });
  }

  async function getDatabase(): Promise<AuthDatabase> {
    if (!database) {
      database = createAuthDatabase(env.databaseUrl);
    }
    await database.checkReady();
    return database;
  }

  async function getAuth(): Promise<BetterAuthRuntime> {
    const db = await getDatabase();
    if (!auth) {
      auth = betterAuth(createBetterAuthOptions(env, db));
    }
    return auth;
  }

  function proofError(status: number, code: string, requestId = randomUUID()): Response {
    return Response.json({ ok: false, code, message: code, requestId }, { status });
  }

  async function sessionAccountId(request: Request): Promise<{ state: "authenticated"; accountId: string } | { state: "unauthenticated" | "unavailable" }> {
    try {
      const runtimeAuth = await getAuth();
      const response = await runtimeAuth.handler(rewriteAuthRequest(request, "/auth/get-session", "GET"));
      if (!response.ok) return { state: "unavailable" };
      const session = sanitizeSessionPayload(await response.json() as BetterAuthSessionPayload);
      const accountId = session?.user.id;
      return accountId ? { state: "authenticated", accountId } : { state: "unauthenticated" };
    } catch {
      return { state: "unavailable" };
    }
  }

  async function authorizeProofRequest(request: Request, campaignId: string) {
    const session = await sessionAccountId(request);
    if (session.state !== "authenticated") return session;
    let decision;
    try {
      decision = await decideCampaignProofRead(await getDatabase(), session.accountId, campaignId);
    } catch {
      return { state: "unavailable" as const };
    }
    if (decision.reason === "authorization_unavailable") return { state: "unavailable" as const };
    if (!decision.allowed) return { state: decision.reason === "capability_denied" ? "denied" as const : "not_found" as const };
    return { state: "allowed" as const, role: decision.campaignAccessRole };
  }

  return {
    live: getReadiness().authRuntimeAvailable,
    reason:
      "PS-040C wires Better Auth to Drizzle/Postgres behind an env and database gate. UI flows and live email delivery remain deferred.",
    getReadiness,
    async handleAuthRequest(request: Request): Promise<Response> {
      const readiness = getReadiness();
      if (!readiness.envConfigured) {
        return failClosed(readiness, "Required auth runtime environment is missing or placeholder.");
      }

      try {
        const runtimeAuth = await getAuth();
        return await runtimeAuth.handler(request);
      } catch (error) {
        const message = error instanceof Error ? error.message : "database_or_auth_runtime_error";
        return failClosed(
          getReadiness(false, "database_or_auth_runtime_unavailable"),
          message.includes(env.databaseUrl) ? "Auth runtime unavailable." : message,
        );
      }
    },
    async handleSessionReadback(request: Request): Promise<Response> {
      const readiness = getReadiness();
      if (!readiness.envConfigured) {
        return failClosed(readiness, "Required auth runtime environment is missing or placeholder.");
      }

      try {
        const runtimeAuth = await getAuth();
        const authResponse = await runtimeAuth.handler(rewriteAuthRequest(request, "/auth/get-session", "GET"));
        if (!authResponse.ok) {
          return failClosed(
            getReadiness(false, "database_or_auth_runtime_unavailable"),
            "Auth runtime session readback failed.",
          );
        }

        const payload = sanitizeSessionPayload(await authResponse.json() as BetterAuthSessionPayload);
        if (!payload) {
          return Response.json({
            state: "unauthenticated",
            authenticated: false,
            liveRuntimeAuth: true,
            readiness: getReadiness(true),
            session: null,
            user: null,
          });
        }

        return Response.json({
          state: "authenticated",
          authenticated: true,
          liveRuntimeAuth: true,
          readiness: getReadiness(true),
          ...payload,
        });
      } catch {
        return failClosed(
          getReadiness(false, "database_or_auth_runtime_unavailable"),
          "Auth runtime unavailable.",
        );
      }
    },
    async handleLogoutRequest(request: Request): Promise<Response> {
      const readiness = getReadiness();
      if (!readiness.envConfigured) {
        return failClosed(readiness, "Required auth runtime environment is missing or placeholder.");
      }

      try {
        const runtimeAuth = await getAuth();
        const sessionResponse = await runtimeAuth.handler(rewriteAuthRequest(request, "/auth/get-session", "GET"));
        if (!sessionResponse.ok) {
          return failClosed(
            getReadiness(false, "database_or_auth_runtime_unavailable"),
            "Auth runtime session readback failed.",
          );
        }

        const session = sanitizeSessionPayload(await sessionResponse.json() as BetterAuthSessionPayload);
        if (!session) {
          return Response.json(
            {
              state: "unauthenticated",
              authenticated: false,
              liveRuntimeAuth: true,
              logout: "not_performed",
              reason: "No active session was present.",
              readiness: getReadiness(true),
            },
            { status: 401 },
          );
        }

        const logoutResponse = await runtimeAuth.handler(rewriteAuthRequest(request, "/auth/sign-out", "POST"));
        if (!logoutResponse.ok) {
          return Response.json(
            {
              state: "authenticated",
              authenticated: true,
              liveRuntimeAuth: true,
              logout: "failed",
              reason: "Auth runtime did not complete sign-out.",
              readiness: getReadiness(true),
            },
            { status: logoutResponse.status },
          );
        }

        return Response.json({
          state: "unauthenticated",
          authenticated: false,
          liveRuntimeAuth: true,
          logout: "performed",
          readiness: getReadiness(true),
        });
      } catch {
        return failClosed(
          getReadiness(false, "database_or_auth_runtime_unavailable"),
          "Auth runtime unavailable.",
        );
      }
    },
    async handleAccountCampaigns(request: Request): Promise<Response> {
      const readiness = getReadiness();
      if (!readiness.envConfigured) return Response.json({ state: "unavailable", source: "account_campaign_store", reason: "auth_runtime_unavailable" }, { status: 503 });
      try {
        const runtimeAuth = await getAuth();
        const sessionResponse = await runtimeAuth.handler(rewriteAuthRequest(request, "/auth/get-session", "GET"));
        if (!sessionResponse.ok) return Response.json({ state: "unavailable", source: "account_campaign_store", reason: "session_readback_unavailable" }, { status: 503 });
        const session = sanitizeSessionPayload(await sessionResponse.json() as BetterAuthSessionPayload);
        const accountId = session?.user.id;
        if (!accountId) return Response.json({ state: "unauthenticated", source: "account_campaign_store", items: [], pageInfo: { hasMore: false, nextCursor: null } }, { status: 401 });
        const url = new URL(request.url);
        if (["accountId", "account_id", "userId", "user_id"].some((key) => url.searchParams.has(key))) {
          return Response.json({ state: "error", source: "account_campaign_store", reason: "caller_account_scope_forbidden" }, { status: 400 });
        }
        const rawLimit = url.searchParams.get("limit");
        const limit = rawLimit === null ? 20 : Number(rawLimit);
        if (!Number.isInteger(limit) || limit < 1 || limit > 50) return Response.json({ state: "error", source: "account_campaign_store", reason: "invalid_limit" }, { status: 400 });
        const rawCursor = url.searchParams.get("cursor");
        const cursor = rawCursor ? decodeCampaignCursor(rawCursor) : undefined;
        const result = await listAccountCampaigns(await getDatabase(), { accountId, limit, cursor });
        return Response.json({
          state: "available", source: "account_campaign_store",
          items: result.items.map((row) => ({ campaignId: row.campaignId, latestRunId: row.latestRunId,
            campaignAccessRole: row.accessRole, linkedAt: row.linkedAt.toISOString(), updatedAt: row.updatedAt.toISOString(),
            source: "account_campaign_store", proofDetailState: "not_fetched" })),
          pageInfo: { hasMore: result.hasMore, nextCursor: result.nextCursor },
        });
      } catch (error) {
        if (error instanceof Error && error.message === "malformed_cursor") return Response.json({ state: "error", source: "account_campaign_store", reason: "malformed_cursor" }, { status: 400 });
        return Response.json({ state: "unavailable", source: "account_campaign_store", reason: "account_campaign_store_unavailable" }, { status: 503 });
      }
    },
    async handlePrivateProofRoom(request: Request, campaignId: string): Promise<Response> {
      const requestId = randomUUID();
      const url = new URL(request.url);
      const allowedQuery = new Set(["runId"]);
      const forbidden = new Set(["accountId", "account_id", "userId", "user_id", "b2Key", "assetUrl", "manifestUrl", "provider", "model", "parentRunId"]);
      if (!isValidProofIdentifier(campaignId) || [...url.searchParams.keys()].some((key) => forbidden.has(key) || !allowedQuery.has(key))) {
        return proofError(400, "invalid_request", requestId);
      }
      const runId = url.searchParams.get("runId") ?? undefined;
      if (runId !== undefined && !isValidProofIdentifier(runId)) return proofError(400, "invalid_request", requestId);
      if (url.searchParams.getAll("runId").length > 1) return proofError(400, "invalid_request", requestId);
      const authorization = await authorizeProofRequest(request, campaignId);
      if (authorization.state === "unauthenticated") return proofError(401, "authentication_required", requestId);
      if (authorization.state === "unavailable") return proofError(503, "authorization_unavailable", requestId);
      if (authorization.state === "denied") return proofError(403, "capability_denied", requestId);
      if (authorization.state !== "allowed") return proofError(404, "proof_not_found", requestId);
      const proof = await readPrivateProofRoom(env, campaignId, runId);
      if (proof.state === "not_found") return proofError(404, "proof_not_found", requestId);
      if (proof.state !== "available") return proofError(503, "proof_service_unavailable", requestId);
      return Response.json({ ok: true, state: "available", source: "proof_api", campaignAccessRole: authorization.role, proofRoom: proof.payload, requestId });
    },
    async handlePrivatePassport(request: Request, campaignId: string, runId: string): Promise<Response> {
      const requestId = randomUUID();
      const url = new URL(request.url);
      if (!isValidProofIdentifier(campaignId) || !isValidProofIdentifier(runId) || url.searchParams.size > 0) {
        return proofError(400, "invalid_request", requestId);
      }
      const authorization = await authorizeProofRequest(request, campaignId);
      if (authorization.state === "unauthenticated") return proofError(401, "authentication_required", requestId);
      if (authorization.state === "unavailable") return proofError(503, "authorization_unavailable", requestId);
      if (authorization.state === "denied") return proofError(403, "capability_denied", requestId);
      if (authorization.state !== "allowed") return proofError(404, "proof_not_found", requestId);
      const proof = await readPrivatePassport(env, campaignId, runId);
      if (proof.state === "not_found") return proofError(404, "proof_not_found", requestId);
      if (proof.state !== "available") return proofError(503, "proof_service_unavailable", requestId);
      return Response.json({ ok: true, state: "available", source: "proof_api", campaignAccessRole: authorization.role, passport: proof.payload, requestId });
    },
    async handlePrivateLineage(request: Request, campaignId: string, bundleId?: string): Promise<Response> {
      const requestId = randomUUID();
      const url = new URL(request.url);
      if (!isValidProofIdentifier(campaignId) || (bundleId !== undefined && !isValidProofIdentifier(bundleId)) || url.searchParams.size > 0) {
        return proofError(400, "invalid_request", requestId);
      }
      const authorization = await authorizeProofRequest(request, campaignId);
      if (authorization.state === "unauthenticated") return proofError(401, "authentication_required", requestId);
      if (authorization.state === "unavailable") return proofError(503, "authorization_unavailable", requestId);
      if (authorization.state === "denied") return proofError(403, "capability_denied", requestId);
      if (authorization.state !== "allowed") return proofError(404, "proof_not_found", requestId);
      const proof = bundleId === undefined
        ? await readPrivateLineageList(env, campaignId)
        : await readPrivateLineageBundle(env, campaignId, bundleId);
      if (proof.state === "not_found") return proofError(404, "proof_not_found", requestId);
      if (proof.state !== "available") return proofError(503, "proof_service_unavailable", requestId);
      return Response.json({ ok: true, state: "available", source: "proof_api", campaignAccessRole: authorization.role, lineage: proof.payload, requestId });
    },
    async handlePrivateLineagePassport(request: Request, campaignId: string, bundleId: string): Promise<Response> {
      const requestId = randomUUID();
      const url = new URL(request.url);
      if (!isValidProofIdentifier(campaignId) || !isValidProofIdentifier(bundleId) || url.searchParams.size > 0) return proofError(400, "invalid_request", requestId);
      const authorization = await authorizeProofRequest(request, campaignId);
      if (authorization.state === "unauthenticated") return proofError(401, "authentication_required", requestId);
      if (authorization.state === "unavailable") return proofError(503, "authorization_unavailable", requestId);
      if (authorization.state === "denied") return proofError(403, "capability_denied", requestId);
      if (authorization.state !== "allowed") return proofError(404, "proof_not_found", requestId);
      const proof = await readPrivateLineagePassport(env, campaignId, bundleId);
      if (proof.state === "not_found") return proofError(404, "proof_not_found", requestId);
      if (proof.state !== "available") return proofError(503, "proof_service_unavailable", requestId);
      return Response.json({ ok: true, state: "available", source: "proof_api", campaignAccessRole: authorization.role, passport: proof.payload, requestId });
    },
    async close(): Promise<void> {
      if (database) {
        await database.close();
      }
    },
  };
}
