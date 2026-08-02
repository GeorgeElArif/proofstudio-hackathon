import { and, asc, eq, gt, isNull, or, sql } from "drizzle-orm";

import type { AuthDatabase } from "../db/client.js";
import { accountCampaignAccess } from "../db/schema.js";

export type CampaignAccessRole = "owner" | "reviewer" | "viewer";
export type CampaignCursor = { linkedAt: string; campaignId: string };

export function requireCampaignId(value: string): string {
  const campaignId = value.trim();
  if (!/^[A-Za-z0-9_.:-]{1,128}$/.test(campaignId) || campaignId !== campaignId.normalize("NFC")) {
    throw new Error("invalid_campaign_id");
  }
  return campaignId;
}

export function encodeCampaignCursor(cursor: CampaignCursor): string {
  return Buffer.from(JSON.stringify(cursor), "utf8").toString("base64url");
}

export function decodeCampaignCursor(value: string): CampaignCursor {
  try {
    const parsed = JSON.parse(Buffer.from(value, "base64url").toString("utf8")) as Partial<CampaignCursor>;
    if (typeof parsed.linkedAt !== "string" || !Number.isFinite(Date.parse(parsed.linkedAt)) ||
        typeof parsed.campaignId !== "string" || !parsed.campaignId.trim()) throw new Error();
    return { linkedAt: new Date(parsed.linkedAt).toISOString(), campaignId: parsed.campaignId };
  } catch { throw new Error("malformed_cursor"); }
}

export async function listAccountCampaigns(database: AuthDatabase, input: {
  accountId: string; limit?: number; cursor?: CampaignCursor;
}) {
  const limit = input.limit ?? 20;
  const cursorDate = input.cursor ? new Date(input.cursor.linkedAt) : null;
  const rows = await database.db.select().from(accountCampaignAccess).where(and(
    eq(accountCampaignAccess.accountId, input.accountId), isNull(accountCampaignAccess.revokedAt),
    cursorDate ? or(gt(accountCampaignAccess.linkedAt, cursorDate), and(
      eq(accountCampaignAccess.linkedAt, cursorDate), gt(accountCampaignAccess.campaignId, input.cursor!.campaignId),
    )) : undefined,
  )).orderBy(asc(accountCampaignAccess.linkedAt), asc(accountCampaignAccess.campaignId)).limit(limit + 1);
  const hasMore = rows.length > limit;
  const items = rows.slice(0, limit);
  const last = items.at(-1);
  return { items, hasMore, nextCursor: hasMore && last ? encodeCampaignCursor({ linkedAt: last.linkedAt.toISOString(), campaignId: last.campaignId }) : null };
}

export async function getCampaignAccessForAccount(database: AuthDatabase, accountId: string, campaignId: string) {
  return (await database.db.select().from(accountCampaignAccess).where(and(
    eq(accountCampaignAccess.accountId, accountId), eq(accountCampaignAccess.campaignId, requireCampaignId(campaignId)),
    isNull(accountCampaignAccess.revokedAt),
  )).limit(1))[0] ?? null;
}

export async function linkCampaignAccess(database: AuthDatabase, input: {
  accountId: string; campaignId: string; latestRunId?: string | null; accessRole: CampaignAccessRole;
}) {
  const campaignId = requireCampaignId(input.campaignId);
  const now = new Date();
  return (await database.db.insert(accountCampaignAccess).values({ ...input, campaignId, updatedAt: now })
    .onConflictDoUpdate({ target: [accountCampaignAccess.accountId, accountCampaignAccess.campaignId],
      targetWhere: sql`${accountCampaignAccess.revokedAt} is null`,
      set: { latestRunId: input.latestRunId ?? null, accessRole: input.accessRole, updatedAt: now } }).returning())[0];
}

export async function revokeCampaignAccess(database: AuthDatabase, accountId: string, campaignId: string) {
  const now = new Date();
  return database.db.update(accountCampaignAccess).set({ revokedAt: now, updatedAt: now }).where(and(
    eq(accountCampaignAccess.accountId, accountId), eq(accountCampaignAccess.campaignId, requireCampaignId(campaignId)), isNull(accountCampaignAccess.revokedAt),
  )).returning();
}
