import type { AuthDatabase } from "../db/client.js";
import { getCampaignAccessForAccount, type CampaignAccessRole } from "./campaign-access.js";

export type CampaignProofAccessDecision = {
  allowed: boolean;
  campaignAccessRole: CampaignAccessRole | null;
  reason: "allowed" | "mapping_not_found" | "capability_denied" | "authorization_unavailable";
};

const READ_ROLES = new Set<CampaignAccessRole>(["owner", "reviewer", "viewer"]);

export async function decideCampaignProofRead(
  database: AuthDatabase,
  accountId: string,
  campaignId: string,
): Promise<CampaignProofAccessDecision> {
  try {
    const mapping = await getCampaignAccessForAccount(database, accountId, campaignId);
    if (!mapping) return { allowed: false, campaignAccessRole: null, reason: "mapping_not_found" };
    const role = mapping.accessRole as CampaignAccessRole;
    if (!READ_ROLES.has(role)) return { allowed: false, campaignAccessRole: null, reason: "capability_denied" };
    return { allowed: true, campaignAccessRole: role, reason: "allowed" };
  } catch {
    return { allowed: false, campaignAccessRole: null, reason: "authorization_unavailable" };
  }
}
