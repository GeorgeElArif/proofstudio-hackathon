// PS-013 Demo UI Shell / Review Room - API client.
//
// Thin typed wrapper over the PS-012 FastAPI demo contract. Every function
// below maps 1:1 to a real backend route. The UI never hardcodes proof
// evidence: all health, campaign, run, attempt, asset, manifest, and passport
// data comes from these live readbacks.

// --- API base URL configuration --------------------------------------------
// Resolved at runtime from VITE_PROOFSTUDIO_API_BASE_URL with a safe fallback
// to the local FastAPI server (uvicorn proofstudio.api.app:app).
export const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export function getApiBaseUrl(): string {
  const fromEnv = import.meta.env.VITE_PROOFSTUDIO_API_BASE_URL;
  if (fromEnv && fromEnv.trim().length > 0) {
    return fromEnv.replace(/\/+$/, "");
  }
  return DEFAULT_API_BASE_URL;
}

// --- Response shapes (mirrors proofstudio.api.models) -----------------------
export interface HealthResponse {
  ok: boolean;
  service: string;
  mode: string;
  version: string;
  environment?: string;
}

export interface VersionResponse {
  service: string;
  version: string;
  framework_mode: string;
  capabilities: string[];
  slice?: string;
  git_branch?: string;
}

export interface CampaignInput {
  name: string;
  brief: string;
  target_audience?: string;
  platform?: string;
  objective?: string;
}

export interface CampaignRecord {
  campaign_id: string;
  name: string;
  brief: string;
  target_audience?: string | null;
  platform?: string | null;
  objective?: string | null;
  status?: string;
  created_at?: string;
}

export interface CampaignResponse {
  campaign_id: string;
  campaign: CampaignRecord;
}

export interface RunInput {
  campaign_id: string;
  prompt?: string;
  budget_mode?: string;
  dry_run?: boolean;
  run_live?: boolean;
}

export interface RunRecord {
  run_id: string;
  campaign_id: string;
  status: string;
  prompt?: string | null;
  budget_mode?: string;
  dry_run: boolean;
  run_live: boolean;
  selected_provider?: string | null;
  selected_model?: string | null;
  api_method?: string | null;
  job_type?: string | null;
  fallback_used?: boolean;
  attempt_count?: number;
  asset_count?: number;
  manifest_uri?: string | null;
  manifest_hash?: string | null;
  in_memory_manifest_verify?: boolean | null;
  stored_manifest_verify?: boolean | null;
  transfer_failures?: unknown[];
  stored_transfer_failures?: unknown[];
  created_at?: string;
  started_at?: string | null;
  finished_at?: string | null;
  truth_boundary?: string | null;
  error?: string | null;
  blocked_reason?: string | null;
}

export interface RunResponse {
  run_id: string;
  run: RunRecord;
}

export interface AttemptRecord {
  attempt_id: string;
  attempt_index: number;
  provider: string;
  model: string;
  api_method: string;
  job_type: string;
  status: string;
  normalized_status: string;
  started_at: string;
  finished_at: string;
  latency_ms: number;
  retryable: boolean;
  fallback_allowed: boolean;
  skip_reason?: string | null;
  raw_error_type?: string | null;
  sanitized_error_message?: string | null;
  estimated_cost?: Record<string, unknown>;
  free_or_paid?: string;
  output_asset_refs?: unknown[];
  notes?: string;
}

export interface AttemptsResponse {
  run_id: string;
  attempt_count: number;
  attempts: AttemptRecord[];
}

export interface AssetRecord {
  asset_id: string;
  run_id: string;
  kind: string;
  provider?: string | null;
  model?: string | null;
  media_type?: string | null;
  size_bytes?: number | null;
  sha256?: string | null;
  url?: string | null;
  b2_url?: string | null;
  produced_real_media?: boolean;
  metadata?: Record<string, unknown>;
}

export interface AssetsResponse {
  run_id: string;
  asset_count: number;
  assets: AssetRecord[];
}

export interface ManifestResponse {
  run_id: string;
  ready: boolean;
  manifest_uri?: string | null;
  manifest_hash?: string | null;
  in_memory_manifest_verify?: boolean | null;
  stored_manifest_verify?: boolean | null;
  transfer_failures?: unknown[];
  stored_transfer_failures?: unknown[];
  asset_count?: number;
  not_ready_reason?: string | null;
}

export interface PassportResponse {
  passport_identity: {
    passport_id: string;
    passport_schema_version: string;
    run_id: string;
    campaign_id: string;
    created_at: string;
    source: string;
  };
  run_summary: Record<string, unknown>;
  campaign_snapshot: Record<string, unknown>;
  generation_summary: {
    generated_media_present: boolean;
    primary_asset_uri?: string | null;
    primary_asset_media_type?: string | null;
    primary_asset_sha256?: string | null;
    primary_asset_size_bytes?: number | null;
  };
  attempt_timeline: Record<string, unknown>[];
  assets: Record<string, unknown>[];
  manifest_verification: Record<string, unknown>;
  archive_and_rehydration: {
    status: string;
    reason?: string;
  };
    durable_passport?: Record<string, unknown>;
  trust_boundary: {
    claims: string[];
    non_claims: string[];
  };
  review_room_summary: {
    one_sentence_summary: string;
    risk_flags: string[];
    reviewer_next_actions: string[];
  };
  truth_boundary: string;
}

// --- Fetch helper -----------------------------------------------------------
export class ApiError extends Error {
  readonly status: number;
  readonly body: unknown;
  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

// PS-013A: classify an API error into reviewer-friendly copy. A fetch() that
// never reached the backend (status 0) is reported as a backend-not-running /
// CORS-style failure instead of a generic "network error", so the operator can
// tell what to fix. Never fakes success and never hides the underlying cause.
export function describeApiError(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 0) {
      return (
        `Backend not reachable at ${getApiBaseUrl()}. Start the FastAPI ` +
        "backend (uvicorn proofstudio.api.app:app --host 127.0.0.1 --port " +
        "8000). If it is already running, this is likely a CORS block: the " +
        "backend must allow this origin."
      );
    }
    return `${err.message} (HTTP ${err.status})`;
  }
  return err instanceof Error ? err.message : String(err);
}

async function request<T>(
  method: "GET" | "POST",
  path: string,
  body?: unknown,
): Promise<T> {
  const base = getApiBaseUrl();
  let resp: Response;
  try {
    resp = await fetch(`${base}${path}`, {
      method,
      headers:
        body !== undefined ? { "Content-Type": "application/json" } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (err) {
    throw new ApiError(
      `Network error reaching ${base}${path}`,
      0,
      err instanceof Error ? err.message : String(err),
    );
  }
  const text = await resp.text();
  let parsed: unknown = null;
  if (text) {
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = text;
    }
  }
  if (!resp.ok) {
    throw new ApiError(
      `${method} ${path} failed (${resp.status})`,
      resp.status,
      parsed,
    );
  }
  return parsed as T;
}

// --- Endpoint helpers (one per PS-012 contract route) ----------------------
// Each helper references the real route path so the API surface stays auditable.

export function getHealth(): Promise<HealthResponse> {
  // GET /health
  return request<HealthResponse>("GET", "/health");
}

export function getVersion(): Promise<VersionResponse> {
  // GET /version
  return request<VersionResponse>("GET", "/version");
}

export function createCampaign(input: CampaignInput): Promise<CampaignResponse> {
  // POST /campaigns
  return request<CampaignResponse>("POST", "/campaigns", input);
}

export function getCampaign(campaignId: string): Promise<CampaignResponse> {
  // GET /campaigns/{campaign_id}
  return request<CampaignResponse>("GET", `/campaigns/${campaignId}`);
}

export function createRun(input: RunInput): Promise<RunResponse> {
  // POST /runs
  return request<RunResponse>("POST", "/runs", input);
}

export function getRun(runId: string): Promise<RunResponse> {
  // GET /runs/{run_id}
  return request<RunResponse>("GET", `/runs/${runId}`);
}

export function getRunAttempts(runId: string): Promise<AttemptsResponse> {
  // GET /runs/{run_id}/attempts
  return request<AttemptsResponse>("GET", `/runs/${runId}/attempts`);
}

export function getRunAssets(runId: string): Promise<AssetsResponse> {
  // GET /runs/{run_id}/assets
  return request<AssetsResponse>("GET", `/runs/${runId}/assets`);
}

export function getRunManifest(runId: string): Promise<ManifestResponse> {
  // GET /runs/{run_id}/manifest
  return request<ManifestResponse>("GET", `/runs/${runId}/manifest`);
}

export function getRunPassport(runId: string): Promise<PassportResponse> {
  // GET /runs/{run_id}/passport
  return request<PassportResponse>("GET", `/runs/${runId}/passport`);
}
