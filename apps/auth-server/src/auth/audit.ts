import { createHash } from "node:crypto";

import type { AuthDatabase } from "../db/client.js";
import { authAuditEvents, authAuditEventType } from "../db/schema.js";

export type AuthAuditEventType = (typeof authAuditEventType.enumValues)[number];

export type AuditOutcome = "succeeded" | "failed" | "deferred" | "unavailable";

export type AuditEventInput = {
  eventType: AuthAuditEventType;
  actorUserId?: string | null;
  userId?: string | null;
  requestId?: string | null;
  ipAddress?: string | null;
  userAgent?: string | null;
  outcome: AuditOutcome;
  reason?: string;
  metadata?: Record<string, unknown>;
};

export type AuditWriteResult = {
  status: "persisted" | "unavailable";
  reason?: string;
};

function hashOptional(value?: string | null): string | null {
  if (!value) {
    return null;
  }
  return createHash("sha256").update(value).digest("hex");
}

function redactMetadata(metadata: Record<string, unknown> = {}): Record<string, unknown> {
  const redacted: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(metadata)) {
    const normalizedKey = key.toLowerCase();
    if (
      normalizedKey.includes("secret") ||
      normalizedKey.includes("token") ||
      normalizedKey.includes("password") ||
      normalizedKey.includes("api_key")
    ) {
      redacted[key] = "[redacted]";
    } else if (normalizedKey === "email" && typeof value === "string") {
      const [, domain] = value.toLowerCase().split("@");
      redacted.emailDomain = domain ?? "invalid";
    } else {
      redacted[key] = value;
    }
  }
  return redacted;
}

export async function writeAuthAuditEvent(
  database: AuthDatabase | null,
  input: AuditEventInput,
): Promise<AuditWriteResult> {
  if (!database) {
    return { status: "unavailable", reason: "database_not_configured" };
  }

  await database.db.insert(authAuditEvents).values({
    eventType: input.eventType,
    actorUserId: input.actorUserId ?? null,
    userId: input.userId ?? null,
    ipHash: hashOptional(input.ipAddress),
    userAgentHash: hashOptional(input.userAgent),
    metadata: {
      ...redactMetadata(input.metadata),
      outcome: input.outcome,
      reason: input.reason,
      requestId: input.requestId ?? undefined,
    },
  });

  return { status: "persisted" };
}
