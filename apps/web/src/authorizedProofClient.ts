import { getAuthBaseUrl } from "./authClient";

export type AuthorizedProofState =
  | { state: "available"; source: "proof_api"; campaignAccessRole: "owner" | "reviewer" | "viewer"; payload: Record<string, unknown> }
  | { state: "unauthenticated" | "not_found" | "unavailable" | "error" };

// PS-041E1: lineage gateway reads return the same role-tagged envelope as the
// accepted proof-room / passport gateways. The payload key differs by route:
//   list     -> `lineage` (bundles array under payload.lineage is set by server)
//   detail   -> `lineage`
//   passport -> `passport`
// The server always returns `state: "available"`, `source: "proof_api"`, and a
// campaign access role before the structured payload. The browser re-checks the
// minimal envelope and rejects anything that does not match before parsing.
export type LineageReadKind = "list" | "detail" | "passport";

export type AuthorizedLineageState =
  | { state: "available"; source: "proof_api"; campaignAccessRole: "owner" | "reviewer" | "viewer"; payload: Record<string, unknown> }
  | { state: "unauthenticated" | "not_found" | "unavailable" | "error" };

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function isRole(value: unknown): value is "owner" | "reviewer" | "viewer" {
  return value === "owner" || value === "reviewer" || value === "viewer";
}

function isProofPayload(value: unknown, kind: "proofRoom" | "passport"): value is Record<string, unknown> {
  if (!isRecord(value) || value.source !== "proof_api") return false;
  const allowed = kind === "proofRoom"
    ? new Set(["source", "campaign", "selected_run", "attempts", "assets", "manifest", "passport_ref", "export_refs"])
    : new Set(["source", "campaign_access_scope", "passport"]);
  if (Object.keys(value).some((key) => !allowed.has(key))) return false;
  if (kind === "proofRoom") return isRecord(value.campaign) && Array.isArray(value.attempts) && Array.isArray(value.assets) && Array.isArray(value.export_refs);
  return typeof value.campaign_access_scope === "string" && isRecord(value.passport);
}

async function readAuthorized(path: string, payloadKey: "proofRoom" | "passport"): Promise<AuthorizedProofState> {
  try {
    const response = await fetch(`${getAuthBaseUrl()}${path}`, {
      method: "GET",
      credentials: "include",
      headers: { accept: "application/json" },
    });
    if (response.status === 401) return { state: "unauthenticated" };
    if (response.status === 404) return { state: "not_found" };
    if (response.status === 503) return { state: "unavailable" };
    if (!response.ok) return { state: "error" };
    const value: unknown = await response.json();
    if (!isRecord(value) || value.state !== "available" || value.source !== "proof_api" || !isRole(value.campaignAccessRole) || !isProofPayload(value[payloadKey], payloadKey)) {
      return { state: "error" };
    }
    return { state: "available", source: "proof_api", campaignAccessRole: value.campaignAccessRole, payload: value[payloadKey] as Record<string, unknown> };
  } catch {
    return { state: "unavailable" };
  }
}

export function getAuthorizedProofRoom(campaignId: string, runId?: string): Promise<AuthorizedProofState> {
  const query = runId ? `?runId=${encodeURIComponent(runId)}` : "";
  return readAuthorized(`/account/campaigns/${encodeURIComponent(campaignId)}/proof-room${query}`, "proofRoom");
}

export function getAuthorizedPassport(campaignId: string, runId: string): Promise<AuthorizedProofState> {
  return readAuthorized(`/account/campaigns/${encodeURIComponent(campaignId)}/passport/${encodeURIComponent(runId)}`, "passport");
}

// PS-041E1: relative auth-server gateway reads only. credentials: "include"
// carries the Better Auth session cookie; no Authorization/service/operator
// header is sent, no browser storage auth is read, no direct
// FastAPI URL is ever constructed, and no retry loop runs. 401/404/503 are
// preserved distinctly so the UI can render honest states and never fall back
// to a fixture after an API failure.
async function readLineageAuthorized(path: string, payloadKey: "lineage" | "passport"): Promise<AuthorizedLineageState> {
  try {
    const response = await fetch(`${getAuthBaseUrl()}${path}`, {
      method: "GET",
      credentials: "include",
      headers: { accept: "application/json" },
    });
    if (response.status === 401) return { state: "unauthenticated" };
    if (response.status === 404) return { state: "not_found" };
    if (response.status === 503) return { state: "unavailable" };
    if (!response.ok) return { state: "error" };
    const value: unknown = await response.json();
    if (!isRecord(value) || value.state !== "available" || value.source !== "proof_api" || !isRole(value.campaignAccessRole) || !isRecord(value[payloadKey])) {
      return { state: "error" };
    }
    return { state: "available", source: "proof_api", campaignAccessRole: value.campaignAccessRole, payload: value[payloadKey] as Record<string, unknown> };
  } catch {
    return { state: "unavailable" };
  }
}

export function fetchCampaignLineage(campaignId: string): Promise<AuthorizedLineageState> {
  return readLineageAuthorized(`/account/campaigns/${encodeURIComponent(campaignId)}/lineage`, "lineage");
}

export function fetchCampaignLineageBundle(campaignId: string, bundleId: string): Promise<AuthorizedLineageState> {
  return readLineageAuthorized(`/account/campaigns/${encodeURIComponent(campaignId)}/lineage/${encodeURIComponent(bundleId)}`, "lineage");
}

export function fetchCampaignLineagePassport(campaignId: string, bundleId: string): Promise<AuthorizedLineageState> {
  return readLineageAuthorized(`/account/campaigns/${encodeURIComponent(campaignId)}/lineage/${encodeURIComponent(bundleId)}/passport`, "passport");
}
