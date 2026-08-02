import {
  getApiBaseUrl,
  getHealth,
  describeApiError,
} from "../api";
import {
  getAuthBaseUrl,
  getAuthReadiness,
  getAuthSession,
  type AuthSessionReadback,
} from "../authClient";
import {
  GOLDEN_DEMO_ARCHIVE_SHA256,
  GOLDEN_DEMO_ARCHIVE_URI,
  GOLDEN_DEMO_CAMPAIGN_ID,
  GOLDEN_DEMO_MANIFEST_PATH,
  GOLDEN_DEMO_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE,
  GOLDEN_DEMO_REHYDRATE_SOURCE,
  GOLDEN_DEMO_RUN_ID,
} from "../b2Evidence";
import {
  ACCOUNT_CAMPAIGN_LIST_NOT_IMPLEMENTED_SOURCE,
  ACCOUNT_CAMPAIGN_STORE_SOURCE,
  CHECKED_IN_GOLDEN_FIXTURE_SOURCE,
  DASHBOARD_AUTH_BOUNDARY,
  DASHBOARD_TRUST_BOUNDARY,
  DEMO_FIXTURE_SOURCE,
  UNAVAILABLE_AUTH_SOURCE,
  UNAVAILABLE_PROOF_API_SOURCE,
  sourceLabel,
  type DashboardAction,
  type DashboardCampaignListState,
  type DashboardCampaignSummary,
  type DashboardModel,
  type DashboardProofApiState,
  type DashboardProofLayerStatus,
  type DashboardSessionState,
} from "./dashboardData";
import { parseAccountCampaignListPayload } from "./dashboardCampaignPayload";

function sessionFromReadback(session: AuthSessionReadback): DashboardSessionState {
  if (session.state === "authenticated") {
    return {
      source: sourceLabel(
        "auth_session",
        "Server session readback",
        "Authenticated state came from GET /session on the auth runtime.",
        { endpoint: `${getAuthBaseUrl()}/session` },
      ),
      state: "authenticated",
      userLabel: session.user.email ?? session.user.id ?? "authenticated account",
      emailVerified: session.user.emailVerified,
      readiness: session.readiness,
      raw: session,
    };
  }

  if (session.state === "unauthenticated") {
    return {
      source: sourceLabel(
        "auth_session",
        "Server session readback",
        "GET /session returned no active server session.",
        { endpoint: `${getAuthBaseUrl()}/session`, reason: "unauthenticated" },
      ),
      state: "unauthenticated",
      userLabel: null,
      emailVerified: null,
      readiness: session.readiness,
      raw: session,
    };
  }

  if (session.state === "network_error") {
    return {
      source: sourceLabel(
        "unavailable",
        "Auth network error",
        session.reason,
        { endpoint: `${getAuthBaseUrl()}/session`, reason: "auth_network_error" },
      ),
      state: "network_error",
      userLabel: null,
      emailVerified: null,
      readiness: null,
      raw: session,
    };
  }

  return {
    source: {
      ...UNAVAILABLE_AUTH_SOURCE,
      endpoint: `${getAuthBaseUrl()}/session`,
      detail: session.reason,
    },
    state: "runtime_unavailable",
    userLabel: null,
    emailVerified: null,
    readiness: session.readiness ?? null,
    raw: session,
  };
}

async function readDashboardSession(): Promise<DashboardSessionState> {
  const session = await getAuthSession();
  const dashboardSession = sessionFromReadback(session);
  if (dashboardSession.readiness) return dashboardSession;

  const readiness = await getAuthReadiness();
  if (!readiness) return dashboardSession;
  return {
    ...dashboardSession,
    readiness: readiness.readiness,
  };
}

async function readProofApiState(): Promise<DashboardProofApiState> {
  const baseUrl = getApiBaseUrl();
  try {
    const health = await getHealth();
    return {
      source: sourceLabel(
        "proof_api",
        "FastAPI health readback",
        "GET /health returned from the configured proof API runtime.",
        { endpoint: `${baseUrl}/health` },
      ),
      state: health.ok ? "available" : "unavailable",
      health,
      baseUrl,
      message: health.ok
        ? "Proof API health is readable."
        : "Proof API returned an unhealthy response.",
    };
  } catch (error) {
    return {
      source: {
        ...UNAVAILABLE_PROOF_API_SOURCE,
        endpoint: `${baseUrl}/health`,
        detail: describeApiError(error),
      },
      state: "unavailable",
      health: null,
      baseUrl,
      message: describeApiError(error),
    };
  }
}

function proofLayer(
  layer: DashboardProofLayerStatus["key"],
  label: string,
  detail: string,
  href: string | undefined,
): DashboardProofLayerStatus {
  return {
    key: layer,
    label,
    status: "available",
    source: CHECKED_IN_GOLDEN_FIXTURE_SOURCE,
    detail,
    href,
  };
}

export function getGoldenFixtureCampaignSummary(): DashboardCampaignSummary {
  const passportHref = `/passport/${GOLDEN_DEMO_RUN_ID}`;
  const proofLayers: DashboardProofLayerStatus[] = [
    proofLayer(
      "b2_archive",
      "B2 archive reference",
      `Archive URI ${GOLDEN_DEMO_ARCHIVE_URI} and SHA-256 ${GOLDEN_DEMO_ARCHIVE_SHA256} are recorded in checked-in evidence.`,
      "/b2-evidence",
    ),
    proofLayer(
      "genblaze_manifest",
      "Genblaze manifest",
      `Manifest fixture path: ${GOLDEN_DEMO_MANIFEST_PATH}.`,
      "/genblaze-pipeline",
    ),
    proofLayer(
      "rehydrate",
      "Rehydrate check",
      `${GOLDEN_DEMO_REHYDRATE_SOURCE}; provider calls during rehydrate: ${GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE}; no live provider call: ${String(GOLDEN_DEMO_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE)}.`,
      "/b2-rehydrate-comparison",
    ),
    proofLayer(
      "review",
      "Review workspace",
      "Review state is a local/demo workflow over accepted evidence, not an account-owned durable approval record.",
      "/review-approval-workspace",
    ),
    proofLayer(
      "export_pack",
      "Evidence pack",
      "Local evidence pack surface over checked-in evidence; it does not add account campaign ownership.",
      "/evidence-pack",
    ),
    proofLayer(
      "passport",
      "Provenance Passport",
      "Golden run passport route for the accepted run identifier.",
      passportHref,
    ),
    {
      key: "campaign_ownership",
      label: "Account ownership",
      status: "not_implemented",
      source: ACCOUNT_CAMPAIGN_LIST_NOT_IMPLEMENTED_SOURCE,
      detail:
        "No account-to-proof ownership join exists yet, so this golden entry is not presented as an account campaign.",
    },
  ];

  const actions: DashboardAction[] = [
    {
      id: "open-proof-room",
      label: "Campaign Proof Room",
      href: "/campaign-proof-room",
      source: CHECKED_IN_GOLDEN_FIXTURE_SOURCE,
      intent: "inspect",
      detail: "Open the campaign-level proof navigation room.",
    },
    {
      id: "open-passport",
      label: "Passport",
      href: passportHref,
      source: CHECKED_IN_GOLDEN_FIXTURE_SOURCE,
      intent: "inspect",
      detail: "Open the golden run passport.",
    },
    {
      id: "open-b2",
      label: "B2 Evidence",
      href: "/b2-evidence",
      source: CHECKED_IN_GOLDEN_FIXTURE_SOURCE,
      intent: "inspect",
      detail: "Inspect the checked-in B2 archive reference.",
    },
    {
      id: "open-genblaze",
      label: "Genblaze",
      href: "/genblaze-pipeline",
      source: CHECKED_IN_GOLDEN_FIXTURE_SOURCE,
      intent: "inspect",
      detail: "Inspect the checked-in pipeline graph.",
    },
    {
      id: "open-rehydrate",
      label: "Rehydrate",
      href: "/b2-rehydrate-comparison",
      source: CHECKED_IN_GOLDEN_FIXTURE_SOURCE,
      intent: "inspect",
      detail: "Inspect the rehydrate comparison.",
    },
    {
      id: "open-review",
      label: "Review",
      href: "/review-approval-workspace",
      source: CHECKED_IN_GOLDEN_FIXTURE_SOURCE,
      intent: "inspect",
      detail: "Open the local review workflow.",
    },
    {
      id: "open-export",
      label: "Evidence Pack",
      href: "/evidence-pack",
      source: CHECKED_IN_GOLDEN_FIXTURE_SOURCE,
      intent: "inspect",
      detail: "Open the local evidence pack surface.",
    },
  ];

  return {
    id: GOLDEN_DEMO_CAMPAIGN_ID,
    title: "Golden proof fixture",
    source: CHECKED_IN_GOLDEN_FIXTURE_SOURCE,
    runId: GOLDEN_DEMO_RUN_ID,
    createdAt: null,
    status: "fixture_available",
    accountOwned: false,
    summary:
      "One checked-in proof entry for navigation and inspection. It is not a real authenticated campaign list row.",
    proofLayers,
    actions,
  };
}

async function getCampaignListState(session: DashboardSessionState): Promise<DashboardCampaignListState> {
  const source = { ...ACCOUNT_CAMPAIGN_STORE_SOURCE, endpoint: `${getAuthBaseUrl()}/account/campaigns` };
  if (session.state === "unauthenticated") return { source, state: "unauthenticated", realAccountCampaigns: [], message: "Sign in to read campaigns linked to this account." };
  if (session.state !== "authenticated") return { source, state: "unavailable", realAccountCampaigns: [], message: "The account campaign source is unavailable." };
  let response: Response;
  try {
    response = await fetch(`${getAuthBaseUrl()}/account/campaigns`, { credentials: "include", headers: { accept: "application/json" } });
  } catch {
    return { source, state: "unavailable", realAccountCampaigns: [], message: "The account campaign source could not be reached." };
  }
  if (response.status === 401) return { source, state: "unauthenticated", realAccountCampaigns: [], message: "The authenticated session is no longer active." };
  if (!response.ok) return { source, state: response.status === 503 ? "unavailable" : "error", realAccountCampaigns: [],
    message: response.status === 503 ? "The account campaign source is unavailable." : "The account campaign request failed safely." };
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    return { source, state: "error", realAccountCampaigns: [], message: "The account campaign response was invalid and was not displayed." };
  }
  const parsed = parseAccountCampaignListPayload(payload);
  if (!parsed) return { source, state: "error", realAccountCampaigns: [], message: "The account campaign response was invalid and was not displayed." };
  return { source, state: parsed.items.length ? "available" : "available_empty", realAccountCampaigns: parsed.items,
    message: parsed.items.length ? "Persisted campaign references linked to this account." : "No campaigns are linked to this account yet." };
}

function getGlobalActions(): readonly DashboardAction[] {
  return [
    {
      id: "open-review-room",
      label: "Create local API campaign",
      href: "/review",
      source: sourceLabel(
        "proof_api",
        "FastAPI operator room",
        "Existing Review Room can create process-local demo campaigns through the proof API.",
      ),
      intent: "create_local",
      detail: "Use the legacy operator flow for local API experiments.",
    },
    {
      id: "open-account",
      label: "Account session",
      href: "/account/session",
      source: sourceLabel(
        "auth_session",
        "Auth account surface",
        "Existing account route reads the server-owned session.",
      ),
      intent: "account",
      detail: "Inspect auth runtime readiness and current session readback.",
    },
    {
      id: "open-demo",
      label: "Demo route",
      href: "/demo",
      source: DEMO_FIXTURE_SOURCE,
      intent: "demo",
      detail: "Open the PS-039 demo shell.",
    },
  ];
}

export async function loadDashboardModel(): Promise<DashboardModel> {
  const [session, proofApi] = await Promise.all([
    readDashboardSession(),
    readProofApiState(),
  ]);
  const fixtureCampaigns = [getGoldenFixtureCampaignSummary()];
  const campaignList = await getCampaignListState(session);

  return {
    generatedAt: new Date().toISOString(),
    trustBoundary: DASHBOARD_TRUST_BOUNDARY,
    authBoundary: DASHBOARD_AUTH_BOUNDARY,
    session,
    proofApi,
    campaignList,
    fixtureCampaigns,
    sourceLedger: [
      session.source,
      proofApi.source,
      campaignList.source,
      CHECKED_IN_GOLDEN_FIXTURE_SOURCE,
      DEMO_FIXTURE_SOURCE,
    ],
    globalActions: getGlobalActions(),
  };
}
