import type { AuthRuntimeEnv } from "../env.js";
import { encodeProofIdentifier } from "../account/proof-identifier.js";

const MAX_RESPONSE_BYTES = 1_500_000;
const REQUEST_TIMEOUT_MS = 5_000;
const PLACEHOLDER_MARKERS = ["change_me", "replace-with", "your-", "placeholder", "example."];

export type ProofApiOutcome =
  | { state: "available"; payload: Record<string, unknown> }
  | { state: "not_found" }
  | { state: "unavailable"; reason: "configuration" | "timeout" | "connection" | "internal_auth" | "upstream" | "non_json" | "malformed" | "oversized" };

function configured(env: AuthRuntimeEnv): boolean {
  const token = env.internalServiceToken;
  const lowered = token.trim().toLowerCase();
  if (token.length < 24 || token !== token.trim() || PLACEHOLDER_MARKERS.some((marker) => lowered.includes(marker))) return false;
  try {
    const url = new URL(env.proofApiBaseUrl);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

type ProofResponseKind = "proof-room" | "passport" | "lineage-list" | "lineage-detail" | "lineage-passport";

const SHA256 = /^[0-9a-f]{64}$/;
const NODE_KINDS = new Set(["import_bundle", "standalone_artifact", "genblaze_run", "manifest", "asset", "external_composition"]);
const EDGE_KINDS = new Set(["parent_run", "generated_asset", "external_input", "storyboard_for", "scene_member", "composition_input", "composed_output", "manifest_for", "embedded_manifest"]);
const EVIDENCE_CLASSES = new Set(["recorded", "inferred"]);
const CHECK_OUTCOMES = new Set(["recorded", "parsed", "hash_present", "hash_verified", "hash_mismatch", "manifest_hash_verified", "manifest_output_hashes_declared", "manifest_invalid", "object_missing", "relationship_recorded", "relationship_inferred", "unsupported_schema", "partial_bundle", "unavailable", "not_checked"]);
const SOURCE_ROLES = new Set(["stage_a_storyboard", "stage_b0_manifest", "stage_b1_manifest", "stage_b2_manifest", "stage_c_composition", "final_delivery", "embedded_manifest", "import_bundle", "generated_asset", "external_input"]);
const RUN_STATUSES = new Set(["pending", "running", "completed", "failed", "cancelled"]);
const STEP_STATUSES = new Set(["pending", "submitted", "processing", "succeeded", "failed", "cancelled"]);
const MODALITIES = new Set(["image", "video", "audio", "text"]);
const TRUTH_BOUNDARY = "ProofStudio reports what the imported pipeline record states; proof does not equal truth.";

function record(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function exactObject(value: unknown, keys: readonly string[]): value is Record<string, unknown> {
  if (!record(value)) return false;
  const actual = Object.keys(value);
  return actual.length === keys.length && keys.every((key) => Object.hasOwn(value, key));
}

function boundedString(value: unknown, max = 256, min = 1): value is string {
  return typeof value === "string" && value.length >= min && value.length <= max && !/[\u0000-\u001f\u007f]/u.test(value);
}

function safeEvidenceString(value: unknown, max = 4096, min = 1): value is string {
  return boundedString(value, max, min) && !value.includes("://") && !/[?#]/u.test(value);
}

function nullable(value: unknown, validator: (item: unknown) => boolean): boolean {
  return value === null || validator(value);
}

function boundedArray(value: unknown, max: number, validator: (item: unknown) => boolean): value is unknown[] {
  return Array.isArray(value) && value.length <= max && value.every(validator);
}

function validCheck(value: unknown): boolean {
  return exactObject(value, ["outcome", "subject", "detail"])
    && typeof value.outcome === "string" && CHECK_OUTCOMES.has(value.outcome)
    && safeEvidenceString(value.subject, 256)
    && nullable(value.detail, (item): item is string => safeEvidenceString(item, 4096));
}

function validLimitation(value: unknown): boolean {
  return exactObject(value, ["code", "notice"])
    && safeEvidenceString(value.code, 256) && safeEvidenceString(value.notice, 4096);
}

function validStep(value: unknown): boolean {
  return exactObject(value, ["step_id", "step_index", "provider", "model", "modality", "status", "output_count", "input_count"])
    && safeEvidenceString(value.step_id, 256) && Number.isInteger(value.step_index) && (value.step_index as number) >= 0
    && nullable(value.provider, (item): item is string => safeEvidenceString(item, 256))
    && safeEvidenceString(value.model, 256)
    && typeof value.modality === "string" && MODALITIES.has(value.modality)
    && typeof value.status === "string" && STEP_STATUSES.has(value.status)
    && Number.isInteger(value.output_count) && (value.output_count as number) >= 0
    && Number.isInteger(value.input_count) && (value.input_count as number) >= 0;
}

function validRun(value: unknown): boolean {
  return exactObject(value, ["run_id", "stage", "manifest_schema", "manifest_hash", "parent_run_id", "status", "steps"])
    && safeEvidenceString(value.run_id, 256) && ["B0", "B1", "B2"].includes(value.stage as string)
    && value.manifest_schema === "1.5"
    && nullable(value.manifest_hash, (item): item is string => typeof item === "string" && SHA256.test(item))
    && nullable(value.parent_run_id, (item): item is string => safeEvidenceString(item, 256))
    && typeof value.status === "string" && RUN_STATUSES.has(value.status)
    && boundedArray(value.steps, 256, validStep);
}

function validB2Reference(value: unknown): boolean {
  return exactObject(value, ["backend", "bucket_alias", "object_key", "version_id", "size_bytes", "content_type", "etag", "sha256", "uploaded_at", "source_prefix", "manifest_hash"])
    && value.backend === "b2_s3" && safeEvidenceString(value.bucket_alias, 256)
    && boundedString(value.object_key, 8192) && !value.object_key.startsWith("/") && !value.object_key.includes("\\")
    && !value.object_key.includes("..") && !value.object_key.includes("://") && !/[?#]/u.test(value.object_key)
    && nullable(value.version_id, (item): item is string => safeEvidenceString(item, 256))
    && (value.size_bytes === null || (Number.isInteger(value.size_bytes) && (value.size_bytes as number) >= 0))
    && nullable(value.content_type, (item): item is string => safeEvidenceString(item, 256))
    && nullable(value.etag, (item): item is string => safeEvidenceString(item, 256))
    && nullable(value.sha256, (item): item is string => typeof item === "string" && SHA256.test(item))
    && nullable(value.uploaded_at, (item): item is string => boundedString(item, 64))
    && nullable(value.source_prefix, (item): item is string => boundedString(item, 8192) && !item.includes("://") && !/[?#]/u.test(item))
    && nullable(value.manifest_hash, (item): item is string => typeof item === "string" && SHA256.test(item));
}

function validMetadata(value: unknown, kind: string): boolean {
  if (!record(value)) return false;
  const allowedByKind: Record<string, Set<string>> = {
    import_bundle: new Set(), genblaze_run: new Set(),
    manifest: new Set(["manifest_schema", "manifest_hash", "declared_content_sha256"]),
    asset: new Set(["title", "status", "media_type", "sha256", "size_bytes", "manifest_schema", "declared_content_sha256"]),
    standalone_artifact: new Set(["title", "status", "media_type", "sha256", "size_bytes", "manifest_schema", "declared_content_sha256"]),
    external_composition: new Set(["title", "status", "media_type", "sha256", "size_bytes", "manifest_schema", "declared_content_sha256"]),
  };
  const allowed = allowedByKind[kind];
  if (!allowed || Object.keys(value).some((key) => !allowed.has(key))) return false;
  return Object.entries(value).every(([key, item]) => {
    if (["sha256", "manifest_hash", "declared_content_sha256"].includes(key)) return item === null || (typeof item === "string" && SHA256.test(item));
    if (key === "size_bytes") return item === null || (Number.isInteger(item) && (item as number) >= 0);
    if (key === "manifest_schema") return item === "1.5";
    return item === null || safeEvidenceString(item, 256);
  });
}

function validNode(value: unknown, campaignId: string, bundleId: string): boolean {
  if (!exactObject(value, ["node_id", "campaign_id", "bundle_id", "kind", "source_id", "source_role", "content_fingerprint", "evidence_class", "checks", "limitations", "run", "b2_reference", "metadata"])) return false;
  if (!safeEvidenceString(value.node_id, 128) || value.campaign_id !== campaignId || value.bundle_id !== bundleId
    || typeof value.kind !== "string" || !NODE_KINDS.has(value.kind) || !safeEvidenceString(value.source_id, 256)
    || typeof value.source_role !== "string" || !SOURCE_ROLES.has(value.source_role)
    || typeof value.content_fingerprint !== "string" || !SHA256.test(value.content_fingerprint)
    || typeof value.evidence_class !== "string" || !EVIDENCE_CLASSES.has(value.evidence_class)
    || !boundedArray(value.checks, 32, validCheck) || !boundedArray(value.limitations, 32, validLimitation)
    || !nullable(value.b2_reference, validB2Reference) || !validMetadata(value.metadata, value.kind)) return false;
  if (value.kind === "genblaze_run") return validRun(value.run);
  return value.run === null;
}

function validEdge(value: unknown, campaignId: string, bundleId: string, nodeIds: Set<string>): boolean {
  return exactObject(value, ["edge_id", "campaign_id", "bundle_id", "kind", "source_node_id", "target_node_id", "missing_source_id", "evidence_class", "hash_covered", "check_outcome", "source_locator", "limitations"])
    && safeEvidenceString(value.edge_id, 128) && value.campaign_id === campaignId && value.bundle_id === bundleId
    && typeof value.kind === "string" && EDGE_KINDS.has(value.kind)
    && safeEvidenceString(value.source_node_id, 128) && nodeIds.has(value.source_node_id)
    && nullable(value.target_node_id, (item): item is string => safeEvidenceString(item, 128) && nodeIds.has(item))
    && nullable(value.missing_source_id, (item): item is string => safeEvidenceString(item, 256))
    && ((value.target_node_id === null) !== (value.missing_source_id === null))
    && typeof value.evidence_class === "string" && EVIDENCE_CLASSES.has(value.evidence_class)
    && typeof value.hash_covered === "boolean"
    && typeof value.check_outcome === "string" && CHECK_OUTCOMES.has(value.check_outcome)
    && nullable(value.source_locator, (item): item is string => safeEvidenceString(item, 4096))
    && boundedArray(value.limitations, 32, validLimitation);
}

function validBundle(value: unknown, campaignId: string, expectedBundleId?: string): value is Record<string, unknown> {
  if (!exactObject(value, ["bundle_id", "campaign_id", "bundle_fingerprint", "fingerprint_schema", "source_type", "source_slug", "source_revision", "state", "node_ids", "edge_ids"])) return false;
  return safeEvidenceString(value.bundle_id, 128) && (expectedBundleId === undefined || value.bundle_id === expectedBundleId)
    && value.campaign_id === campaignId && typeof value.bundle_fingerprint === "string" && SHA256.test(value.bundle_fingerprint)
    && value.fingerprint_schema === "ps041d.fingerprint.v1" && value.source_type === "genblaze_multi_provider_sample"
    && value.source_slug === "genblaze-gen-media-multi-provider-sample" && value.source_revision === "2e31577b7a9d5a7b0309d814f2d0282088b33fe8"
    && ["complete", "partial_bundle"].includes(value.state as string)
    && boundedArray(value.node_ids, 512, (item) => safeEvidenceString(item, 128))
    && boundedArray(value.edge_ids, 64, (item) => safeEvidenceString(item, 128));
}

function sameIdentifiers(declared: unknown, actual: string[]): boolean {
  return Array.isArray(declared) && declared.length === actual.length
    && new Set(declared).size === declared.length && actual.every((id) => declared.includes(id));
}

function validGraph(nodesValue: unknown, edgesValue: unknown, campaignId: string, bundleId: string,
                    nodeIdsValue?: unknown, edgeIdsValue?: unknown): boolean {
  if (!Array.isArray(nodesValue) || nodesValue.length > 512 || !nodesValue.every((item) => validNode(item, campaignId, bundleId))) return false;
  const nodeIds = new Set(nodesValue.map((item) => (item as Record<string, unknown>).node_id as string));
  if (nodeIds.size !== nodesValue.length || !Array.isArray(edgesValue) || edgesValue.length > 64
    || !edgesValue.every((item) => validEdge(item, campaignId, bundleId, nodeIds))) return false;
  const edgeIds = edgesValue.map((item) => (item as Record<string, unknown>).edge_id as string);
  return new Set(edgeIds).size === edgeIds.length
    && (nodeIdsValue === undefined || sameIdentifiers(nodeIdsValue, [...nodeIds]))
    && (edgeIdsValue === undefined || sameIdentifiers(edgeIdsValue, edgeIds));
}

function validTopLevel(payload: unknown, kind: ProofResponseKind, campaignId?: string, bundleId?: string): payload is Record<string, unknown> {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return false;
  const value = payload as Record<string, unknown>;
  const allowed = kind === "proof-room"
    ? new Set(["source", "campaign", "selected_run", "attempts", "assets", "manifest", "passport_ref", "export_refs"])
    : kind === "passport" || kind === "lineage-passport" ? new Set(["source", "campaign_access_scope", "passport"])
    : kind === "lineage-list" ? new Set(["source", "campaign_access_scope", "bundles"])
    : new Set(["source", "campaign_access_scope", "lineage"]);
  if (!exactObject(value, [...allowed]) || value.source !== "proof_api") return false;
  if (kind === "proof-room") {
    return Boolean(value.campaign && typeof value.campaign === "object") && Array.isArray(value.attempts) && Array.isArray(value.assets) && Array.isArray(value.export_refs);
  }
  if (kind === "passport") return Boolean(value.passport && typeof value.passport === "object" && !Array.isArray(value.passport));
  if (!campaignId || value.campaign_access_scope !== campaignId) return false;
  if (kind === "lineage-passport") {
    if (!bundleId || !exactObject(value.passport, ["schema", "campaign_id", "bundle_id", "bundle_fingerprint", "source_type", "source_slug", "source_revision", "state", "nodes", "edges", "limitations", "truth_boundary"])) return false;
    return value.passport.schema === "proofstudio.portable_lineage_passport.v1" && value.passport.campaign_id === campaignId
      && value.passport.bundle_id === bundleId && typeof value.passport.bundle_fingerprint === "string" && SHA256.test(value.passport.bundle_fingerprint)
      && value.passport.source_type === "genblaze_multi_provider_sample" && value.passport.source_slug === "genblaze-gen-media-multi-provider-sample"
      && value.passport.source_revision === "2e31577b7a9d5a7b0309d814f2d0282088b33fe8" && ["complete", "partial_bundle"].includes(value.passport.state as string)
      && validGraph(value.passport.nodes, value.passport.edges, campaignId, bundleId)
      && boundedArray(value.passport.limitations, 32, validLimitation) && value.passport.truth_boundary === TRUTH_BOUNDARY;
  }
  if (kind === "lineage-list") return boundedArray(value.bundles, 50, (item) => validBundle(item, campaignId));
  if (!bundleId || !exactObject(value.lineage, ["created", "bundle", "nodes", "edges"]) || typeof value.lineage.created !== "boolean"
    || !validBundle(value.lineage.bundle, campaignId, bundleId)) return false;
  return validGraph(value.lineage.nodes, value.lineage.edges, campaignId, bundleId,
    value.lineage.bundle.node_ids, value.lineage.bundle.edge_ids);
}

async function readBounded(response: Response): Promise<string | null> {
  const declared = Number(response.headers.get("content-length") ?? "0");
  if (declared > MAX_RESPONSE_BYTES) return null;
  if (!response.body) return "";
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let size = 0;
  let result = "";
  while (true) {
    const chunk = await reader.read();
    if (chunk.done) break;
    size += chunk.value.byteLength;
    if (size > MAX_RESPONSE_BYTES) {
      await reader.cancel();
      return null;
    }
    result += decoder.decode(chunk.value, { stream: true });
  }
  return result + decoder.decode();
}

async function requestProof(env: AuthRuntimeEnv, path: string, kind: ProofResponseKind, campaignId?: string, bundleId?: string): Promise<ProofApiOutcome> {
  if (!configured(env)) return { state: "unavailable", reason: "configuration" };
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(`${env.proofApiBaseUrl.replace(/\/+$/, "")}${path}`, {
      method: "GET",
      headers: { accept: "application/json", "X-ProofStudio-Internal-Token": env.internalServiceToken },
      redirect: "manual",
      signal: controller.signal,
    });
    if (response.status >= 300 && response.status <= 399) return { state: "unavailable", reason: "upstream" };
    if (response.status === 404) return { state: "not_found" };
    if (response.status === 401 || response.status === 403) return { state: "unavailable", reason: "internal_auth" };
    if (!response.ok) return { state: "unavailable", reason: "upstream" };
    const text = await readBounded(response);
    if (text === null) return { state: "unavailable", reason: "oversized" };
    let payload: unknown;
    try { payload = JSON.parse(text); } catch { return { state: "unavailable", reason: "non_json" }; }
    return validTopLevel(payload, kind, campaignId, bundleId) ? { state: "available", payload } : { state: "unavailable", reason: "malformed" };
  } catch (error) {
    return { state: "unavailable", reason: error instanceof Error && error.name === "AbortError" ? "timeout" : "connection" };
  } finally {
    clearTimeout(timeout);
  }
}

export function readPrivateProofRoom(env: AuthRuntimeEnv, campaignId: string, runId?: string): Promise<ProofApiOutcome> {
  const query = runId ? `?runId=${encodeProofIdentifier(runId)}` : "";
  return requestProof(env, `/internal/campaigns/${encodeProofIdentifier(campaignId)}/proof-room${query}`, "proof-room");
}

export function readPrivatePassport(env: AuthRuntimeEnv, campaignId: string, runId: string): Promise<ProofApiOutcome> {
  return requestProof(env, `/internal/campaigns/${encodeProofIdentifier(campaignId)}/runs/${encodeProofIdentifier(runId)}/passport`, "passport");
}

export function readPrivateLineageList(env: AuthRuntimeEnv, campaignId: string): Promise<ProofApiOutcome> {
  return requestProof(env, `/internal/campaigns/${encodeProofIdentifier(campaignId)}/import-bundles`, "lineage-list", campaignId);
}

export function readPrivateLineageBundle(env: AuthRuntimeEnv, campaignId: string, bundleId: string): Promise<ProofApiOutcome> {
  return requestProof(env, `/internal/campaigns/${encodeProofIdentifier(campaignId)}/import-bundles/${encodeProofIdentifier(bundleId)}`, "lineage-detail", campaignId, bundleId);
}

export function readPrivateLineagePassport(env: AuthRuntimeEnv, campaignId: string, bundleId: string): Promise<ProofApiOutcome> {
  return requestProof(env, `/internal/campaigns/${encodeProofIdentifier(campaignId)}/import-bundles/${encodeProofIdentifier(bundleId)}/passport`, "lineage-passport", campaignId, bundleId);
}
