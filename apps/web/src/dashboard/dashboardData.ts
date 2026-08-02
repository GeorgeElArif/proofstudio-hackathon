import type { AuthRuntimeReadiness, AuthSessionReadback } from "../authClient";
import type { HealthResponse } from "../api";

export type DashboardDataSourceKind =
  | "auth_session"
  | "account_campaign_store"
  | "proof_api"
  | "checked_in_fixture"
  | "demo_fixture"
  | "unavailable"
  | "not_implemented";

export type DashboardUnavailableReason =
  | "auth_runtime_unavailable"
  | "auth_network_error"
  | "unauthenticated"
  | "proof_api_unavailable"
  | "campaign_list_api_not_implemented"
  | "account_campaign_ownership_not_implemented"
  | "fixture_only"
  | "not_configured"
  | "account_campaign_store_unavailable";

export interface DashboardDataSourceLabel {
  kind: DashboardDataSourceKind;
  label: string;
  detail: string;
  endpoint?: string;
  evidencePath?: string;
  reason?: DashboardUnavailableReason;
}

export interface DashboardSessionState {
  source: DashboardDataSourceLabel;
  state:
    | "checking"
    | "authenticated"
    | "unauthenticated"
    | "runtime_unavailable"
    | "network_error";
  userLabel: string | null;
  emailVerified: boolean | null;
  readiness: AuthRuntimeReadiness | null;
  raw: AuthSessionReadback | null;
}

export interface DashboardProofApiState {
  source: DashboardDataSourceLabel;
  state: "checking" | "available" | "unavailable";
  health: HealthResponse | null;
  baseUrl: string;
  message: string;
}

export type DashboardProofLayerStatusValue =
  | "available"
  | "unavailable"
  | "not_implemented"
  | "not_captured"
  | "not_claimed";

export interface DashboardProofLayerStatus {
  key:
    | "b2_archive"
    | "genblaze_manifest"
    | "rehydrate"
    | "review"
    | "export_pack"
    | "passport"
    | "campaign_ownership";
  label: string;
  status: DashboardProofLayerStatusValue;
  source: DashboardDataSourceLabel;
  detail: string;
  href?: string;
}

export interface DashboardAction {
  id: string;
  label: string;
  href: string;
  source: DashboardDataSourceLabel;
  intent: "inspect" | "create_local" | "account" | "demo";
  disabled?: boolean;
  detail: string;
}

export interface DashboardCampaignSummary {
  id: string;
  title: string;
  source: DashboardDataSourceLabel;
  runId: string | null;
  createdAt: string | null;
  status: "fixture_available" | "not_implemented" | "unavailable";
  accountOwned: false;
  summary: string;
  proofLayers: DashboardProofLayerStatus[];
  actions: DashboardAction[];
}

export interface DashboardCampaignListState {
  source: DashboardDataSourceLabel;
  state: "unauthenticated" | "unavailable" | "available_empty" | "available" | "error";
  realAccountCampaigns: readonly AccountCampaignReference[];
  message: string;
}

export interface AccountCampaignReference {
  campaignId: string; latestRunId: string | null; campaignAccessRole: "owner" | "reviewer" | "viewer";
  linkedAt: string; updatedAt: string; source: "account_campaign_store"; proofDetailState: "not_fetched";
}

export interface DashboardModel {
  generatedAt: string;
  trustBoundary: string;
  authBoundary: string;
  session: DashboardSessionState;
  proofApi: DashboardProofApiState;
  campaignList: DashboardCampaignListState;
  fixtureCampaigns: readonly DashboardCampaignSummary[];
  sourceLedger: readonly DashboardDataSourceLabel[];
  globalActions: readonly DashboardAction[];
}

export const DASHBOARD_TRUST_BOUNDARY =
  "ProofStudio proves what the pipeline recorded. Proof does not equal truth.";

export const DASHBOARD_AUTH_BOUNDARY =
  "Auth proves account/session identity only.";

export function sourceLabel(
  kind: DashboardDataSourceKind,
  label: string,
  detail: string,
  options: {
    endpoint?: string;
    evidencePath?: string;
    reason?: DashboardUnavailableReason;
  } = {},
): DashboardDataSourceLabel {
  return {
    kind,
    label,
    detail,
    ...options,
  };
}

export const ACCOUNT_CAMPAIGN_LIST_NOT_IMPLEMENTED_SOURCE = sourceLabel(
  "not_implemented",
  "Account campaign list",
  "No account-owned campaign list API or account-to-proof ownership join exists in this slice.",
  { reason: "campaign_list_api_not_implemented" },
);

export const ACCOUNT_CAMPAIGN_STORE_SOURCE = sourceLabel(
  "account_campaign_store", "Account campaign access",
  "Persisted application access mappings for the authenticated account.",
  { endpoint: `${typeof window === "undefined" ? "" : ""}/account/campaigns` },
);

export const CHECKED_IN_GOLDEN_FIXTURE_SOURCE = sourceLabel(
  "checked_in_fixture",
  "Checked-in golden proof fixture",
  "Accepted local evidence for one golden run. It is not an authenticated account campaign.",
  { evidencePath: "docs/evidence/demo/golden-demo-run.json", reason: "fixture_only" },
);

export const DEMO_FIXTURE_SOURCE = sourceLabel(
  "demo_fixture",
  "Demo shell",
  "PS-039 demo route and proof surfaces are launchable as demo/read-only surfaces.",
  { reason: "fixture_only" },
);

export const UNAVAILABLE_AUTH_SOURCE = sourceLabel(
  "unavailable",
  "Auth runtime unavailable",
  "The dashboard could not read a server-owned auth session.",
  { reason: "auth_runtime_unavailable" },
);

export const UNAVAILABLE_PROOF_API_SOURCE = sourceLabel(
  "unavailable",
  "Proof API unavailable",
  "The dashboard could not read FastAPI health.",
  { reason: "proof_api_unavailable" },
);
