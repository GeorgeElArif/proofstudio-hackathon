import type { AccountCampaignReference } from "./dashboardData";

export interface AccountCampaignListPayload {
  state: "available";
  source: "account_campaign_store";
  items: readonly AccountCampaignReference[];
  pageInfo: {
    hasMore: boolean;
    nextCursor: string | null;
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isTimestamp(value: unknown): value is string {
  return typeof value === "string" && value.trim() !== "" && Number.isFinite(Date.parse(value));
}

function parseAccountCampaignItem(value: unknown): AccountCampaignReference | null {
  if (!isRecord(value)) return null;

  const campaignId = typeof value.campaignId === "string" ? value.campaignId.trim() : "";
  const latestRunId = value.latestRunId;
  const role = value.campaignAccessRole;
  if (!campaignId) return null;
  if (latestRunId !== null && (typeof latestRunId !== "string" || latestRunId.trim() === "")) return null;
  if (role !== "owner" && role !== "reviewer" && role !== "viewer") return null;
  if (!isTimestamp(value.linkedAt) || !isTimestamp(value.updatedAt)) return null;
  if (value.source !== "account_campaign_store" || value.proofDetailState !== "not_fetched") return null;

  return {
    campaignId,
    latestRunId: typeof latestRunId === "string" ? latestRunId.trim() : null,
    campaignAccessRole: role,
    linkedAt: value.linkedAt,
    updatedAt: value.updatedAt,
    source: value.source,
    proofDetailState: value.proofDetailState,
  };
}

export function parseAccountCampaignListPayload(value: unknown): AccountCampaignListPayload | null {
  if (!isRecord(value) || value.state !== "available" || value.source !== "account_campaign_store") return null;
  if (!Array.isArray(value.items) || !isRecord(value.pageInfo)) return null;
  if (typeof value.pageInfo.hasMore !== "boolean") return null;
  if (value.pageInfo.nextCursor !== null && typeof value.pageInfo.nextCursor !== "string") return null;

  const items: AccountCampaignReference[] = [];
  for (const item of value.items) {
    const parsed = parseAccountCampaignItem(item);
    if (!parsed) return null;
    items.push(parsed);
  }

  return {
    state: "available",
    source: "account_campaign_store",
    items,
    pageInfo: {
      hasMore: value.pageInfo.hasMore,
      nextCursor: value.pageInfo.nextCursor,
    },
  };
}
