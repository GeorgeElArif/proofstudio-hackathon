// PS-041E1 — Private Dynamic Lineage UI: browser-side types and bounded parser.
//
// This module mirrors the accepted PS-041D auth-server gateway contract only.
// The auth-server gateway has already recursively validated every nested field
// against exact keys, enum sets, hash/string/array bounds, and credential/URL
// rejection. The browser parser below is a defense-in-depth second check: it
// never trusts raw shapes, never reconstructs URLs, never renders arbitrary
// JSON, and fail-closes to an unsupported state for any unexpected structural
// field so the page never silently coerces an unknown kind into a known stage.
//
// It performs:
//   - bounded runtime parsing for list / detail / passport responses;
//   - deterministic stage grouping in fixed order A → B0 → B1 → B2 → C;
//   - deterministic node/edge ordering (stable sort by ID);
//   - display-safe string normalization (no controls, no URL reconstruction);
//   - safe labels for node kinds, edge kinds, source roles and check outcomes;
//   - check severity mapping (ok / warn / danger / neutral / unsupported);
//   - limitation classification;
//   - provider/model display formatting (unknown values render as plain text);
//   - structured B2 reference formatting (no URL, no account id, no signed url).
//
// It does not:
//   - render raw JSON;
//   - recursively render arbitrary data;
//   - generate arbitrary URLs;
//   - call any provider;
//   - access B2;
//   - persist anything to localStorage / sessionStorage.

export const LINEAGE_TRUTH_BOUNDARY =
  "ProofStudio shows what the recorded pipeline evidence contains. Proof does not equal truth.";

export const SERVER_TRUTH_BOUNDARY =
  "ProofStudio reports what the imported pipeline record states; proof does not equal truth.";

const SHA256 = /^[0-9a-f]{64}$/;

// Accepted enumerations — must match proof-api-client.ts exactly.
export const NODE_KINDS = [
  "import_bundle",
  "standalone_artifact",
  "genblaze_run",
  "manifest",
  "asset",
  "external_composition",
] as const;
export type NodeKind = (typeof NODE_KINDS)[number];

export const EDGE_KINDS = [
  "parent_run",
  "generated_asset",
  "external_input",
  "storyboard_for",
  "scene_member",
  "composition_input",
  "composed_output",
  "manifest_for",
  "embedded_manifest",
] as const;
export type EdgeKind = (typeof EDGE_KINDS)[number];

export const SOURCE_ROLES = [
  "stage_a_storyboard",
  "stage_b0_manifest",
  "stage_b1_manifest",
  "stage_b2_manifest",
  "stage_c_composition",
  "final_delivery",
  "embedded_manifest",
  "import_bundle",
  "generated_asset",
  "external_input",
] as const;
export type SourceRole = (typeof SOURCE_ROLES)[number];

export const CHECK_OUTCOMES = [
  "recorded",
  "parsed",
  "hash_present",
  "hash_verified",
  "hash_mismatch",
  "manifest_hash_verified",
  "manifest_output_hashes_declared",
  "manifest_invalid",
  "object_missing",
  "relationship_recorded",
  "relationship_inferred",
  "unsupported_schema",
  "partial_bundle",
  "unavailable",
  "not_checked",
] as const;
export type CheckOutcome = (typeof CHECK_OUTCOMES)[number];

const NODE_KIND_SET: ReadonlySet<string> = new Set(NODE_KINDS);
const EDGE_KIND_SET: ReadonlySet<string> = new Set(EDGE_KINDS);
const SOURCE_ROLE_SET: ReadonlySet<string> = new Set(SOURCE_ROLES);
const CHECK_OUTCOME_SET: ReadonlySet<string> = new Set(CHECK_OUTCOMES);

const EVIDENCE_CLASSES = new Set(["recorded", "inferred"]);
const RUN_STATUSES = new Set(["pending", "running", "completed", "failed", "cancelled"]);
const STEP_STATUSES = new Set(["pending", "submitted", "processing", "succeeded", "failed", "cancelled"]);
const MODALITIES = new Set(["image", "video", "audio", "text"]);
const BUNDLE_STATES = new Set(["complete", "partial_bundle"]);

export type EvidenceClass = "recorded" | "inferred";

// --- Accepted structural types -------------------------------------------------

export interface B2Reference {
  readonly backend: "b2_s3";
  readonly bucketAlias: string;
  readonly objectKey: string;
  readonly versionId: string | null;
  readonly sizeBytes: number | null;
  readonly contentType: string | null;
  readonly etag: string | null;
  readonly sha256: string | null;
  readonly uploadedAt: string | null;
  readonly sourcePrefix: string | null;
  readonly manifestHash: string | null;
}

export interface LineageCheck {
  readonly outcome: CheckOutcome;
  readonly subject: string;
  readonly detail: string | null;
}

export interface LineageLimitation {
  readonly code: string;
  readonly notice: string;
}

export interface LineageStep {
  readonly stepId: string;
  readonly stepIndex: number;
  readonly provider: string | null;
  readonly model: string;
  readonly modality: "image" | "video" | "audio" | "text";
  readonly status: string;
  readonly outputCount: number;
  readonly inputCount: number;
}

export interface LineageRun {
  readonly runId: string;
  readonly stage: "B0" | "B1" | "B2";
  readonly manifestSchema: "1.5";
  readonly manifestHash: string | null;
  readonly parentRunId: string | null;
  readonly status: string;
  readonly steps: readonly LineageStep[];
}

export interface LineageNode {
  readonly nodeId: string;
  readonly campaignId: string;
  readonly bundleId: string;
  readonly kind: NodeKind;
  readonly sourceId: string;
  readonly sourceRole: SourceRole;
  readonly contentFingerprint: string;
  readonly evidenceClass: EvidenceClass;
  readonly checks: readonly LineageCheck[];
  readonly limitations: readonly LineageLimitation[];
  readonly run: LineageRun | null;
  readonly b2Reference: B2Reference | null;
  readonly metadata: Readonly<Record<string, string | number | null>>;
}

export interface LineageEdge {
  readonly edgeId: string;
  readonly campaignId: string;
  readonly bundleId: string;
  readonly kind: EdgeKind;
  readonly sourceNodeId: string;
  readonly targetNodeId: string | null;
  readonly missingSourceId: string | null;
  readonly evidenceClass: EvidenceClass;
  readonly hashCovered: boolean;
  readonly checkOutcome: CheckOutcome;
  readonly sourceLocator: string | null;
  readonly limitations: readonly LineageLimitation[];
}

export interface LineageBundle {
  readonly bundleId: string;
  readonly campaignId: string;
  readonly bundleFingerprint: string;
  readonly fingerprintSchema: "ps041d.fingerprint.v1";
  readonly sourceType: "genblaze_multi_provider_sample";
  readonly sourceSlug: "genblaze-gen-media-multi-provider-sample";
  readonly sourceRevision: "2e31577b7a9d5a7b0309d814f2d0282088b33fe8";
  readonly state: "complete" | "partial_bundle";
  readonly nodeIds: readonly string[];
  readonly edgeIds: readonly string[];
}

export interface LineageListPayload {
  readonly kind: "list";
  readonly campaignAccessScope: string;
  readonly bundles: readonly LineageBundle[];
}

export interface LineageDetailPayload {
  readonly kind: "detail";
  readonly campaignAccessScope: string;
  readonly created: boolean;
  readonly bundle: LineageBundle;
  readonly nodes: readonly LineageNode[];
  readonly edges: readonly LineageEdge[];
}

export interface LineagePassportPayload {
  readonly kind: "passport";
  readonly campaignAccessScope: string;
  readonly schema: "proofstudio.portable_lineage_passport.v1";
  readonly campaignId: string;
  readonly bundleId: string;
  readonly bundleFingerprint: string;
  readonly sourceType: "genblaze_multi_provider_sample";
  readonly sourceSlug: "genblaze-gen-media-multi-provider-sample";
  readonly sourceRevision: "2e31577b7a9d5a7b0309d814f2d0282088b33fe8";
  readonly state: "complete" | "partial_bundle";
  readonly nodes: readonly LineageNode[];
  readonly edges: readonly LineageEdge[];
  readonly limitations: readonly LineageLimitation[];
  readonly truthBoundary: typeof SERVER_TRUTH_BOUNDARY;
}

export type LineagePayload = LineageListPayload | LineageDetailPayload | LineagePassportPayload;

// --- Bounded primitives --------------------------------------------------------

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function boundedString(value: unknown, max = 256, min = 1): value is string {
  return typeof value === "string" && value.length >= min && value.length <= max && !/[\u0000-\u001f\u007f]/u.test(value);
}

// Evidence strings must not contain URL-ish characters; mirrors the server
// `safeEvidenceString` policy. This is a defense-in-depth second check.
function safeEvidenceString(value: unknown, max = 4096, min = 1): value is string {
  return boundedString(value, max, min) && !value.includes("://") && !/[?#]/u.test(value);
}

function isHash256(value: unknown): value is string {
  return typeof value === "string" && SHA256.test(value);
}

// Optional value: null stays null; otherwise `parse` must return T or null.
// Using T | null (not a type predicate) avoids contravariance issues with
// higher-order type predicates and keeps the parser readable.
function optional<T>(value: unknown, parse: (v: unknown) => T | null): T | null {
  return value === null ? null : parse(value);
}

// Optional string helper that distinguishes "valid string" from "invalid junk".
function optionalEvidence(value: unknown, max: number): string | null {
  return optional(value, (v): string | null => (safeEvidenceString(v, max) ? v : null));
}

// Optional bounded string (no evidence-string restriction).
function optionalBounded(value: unknown, max: number): string | null {
  return optional(value, (v): string | null => (boundedString(v, max) ? v : null));
}

// Bounded array parser. Each item is parsed via `parse`, which returns T or
// null. Returns the parsed array or null on any failure.
function parseArray<T>(value: unknown, max: number, parse: (v: unknown) => T | null): T[] | null {
  if (!Array.isArray(value) || value.length > max) return null;
  const out: T[] = [];
  for (const item of value) {
    const parsed = parse(item);
    if (parsed === null) return null;
    out.push(parsed);
  }
  return out;
}

function exactObject(value: unknown, keys: readonly string[]): value is Record<string, unknown> {
  if (!isRecord(value)) return false;
  const actual = Object.keys(value);
  return actual.length === keys.length && keys.every((key) => Object.prototype.hasOwnProperty.call(value, key));
}

// --- Nested guards -------------------------------------------------------------

function parseCheck(value: unknown): LineageCheck | null {
  if (!exactObject(value, ["outcome", "subject", "detail"])) return null;
  if (typeof value.outcome !== "string" || !CHECK_OUTCOME_SET.has(value.outcome)) return null;
  if (!safeEvidenceString(value.subject, 256)) return null;
  const detail = optionalEvidence(value.detail, 4096);
  if (detail === null && value.detail !== null) return null;
  return {
    outcome: value.outcome as CheckOutcome,
    subject: value.subject,
    detail,
  };
}

function parseLimitation(value: unknown): LineageLimitation | null {
  if (!exactObject(value, ["code", "notice"])) return null;
  if (!safeEvidenceString(value.code, 256) || !safeEvidenceString(value.notice, 4096)) return null;
  return { code: value.code, notice: value.notice };
}

function parseStep(value: unknown): LineageStep | null {
  if (!exactObject(value, ["step_id", "step_index", "provider", "model", "modality", "status", "output_count", "input_count"])) return null;
  if (!safeEvidenceString(value.step_id, 256)) return null;
  if (!Number.isInteger(value.step_index) || (value.step_index as number) < 0) return null;
  const provider = optionalEvidence(value.provider, 256);
  if (provider === null && value.provider !== null) return null;
  if (!safeEvidenceString(value.model, 256)) return null;
  if (typeof value.modality !== "string" || !MODALITIES.has(value.modality)) return null;
  if (typeof value.status !== "string" || !STEP_STATUSES.has(value.status)) return null;
  if (!Number.isInteger(value.output_count) || (value.output_count as number) < 0) return null;
  if (!Number.isInteger(value.input_count) || (value.input_count as number) < 0) return null;
  return {
    stepId: value.step_id,
    stepIndex: value.step_index as number,
    provider,
    model: value.model,
    modality: value.modality as LineageStep["modality"],
    status: value.status,
    outputCount: value.output_count as number,
    inputCount: value.input_count as number,
  };
}

function parseRun(value: unknown): LineageRun | null {
  if (!exactObject(value, ["run_id", "stage", "manifest_schema", "manifest_hash", "parent_run_id", "status", "steps"])) return null;
  if (!safeEvidenceString(value.run_id, 256)) return null;
  if (value.stage !== "B0" && value.stage !== "B1" && value.stage !== "B2") return null;
  if (value.manifest_schema !== "1.5") return null;
  const manifestHash = optional(value.manifest_hash, (v): string | null => (isHash256(v) ? v : null));
  if (manifestHash === null && value.manifest_hash !== null) return null;
  const parentRunId = optionalEvidence(value.parent_run_id, 256);
  if (parentRunId === null && value.parent_run_id !== null) return null;
  if (typeof value.status !== "string" || !RUN_STATUSES.has(value.status)) return null;
  const steps = parseArray(value.steps, 256, parseStep);
  if (steps === null) return null;
  return {
    runId: value.run_id,
    stage: value.stage,
    manifestSchema: value.manifest_schema,
    manifestHash,
    parentRunId,
    status: value.status,
    steps,
  };
}

function parseB2Reference(value: unknown): B2Reference | null {
  if (!exactObject(value, ["backend", "bucket_alias", "object_key", "version_id", "size_bytes", "content_type", "etag", "sha256", "uploaded_at", "source_prefix", "manifest_hash"])) return null;
  if (value.backend !== "b2_s3") return null;
  if (!safeEvidenceString(value.bucket_alias, 256)) return null;
  if (!boundedString(value.object_key, 8192) || value.object_key.startsWith("/") || value.object_key.includes("\\") || value.object_key.includes("..") || value.object_key.includes("://") || /[?#]/u.test(value.object_key)) return null;
  const versionId = optionalEvidence(value.version_id, 256);
  if (versionId === null && value.version_id !== null) return null;
  if (value.size_bytes !== null && (!Number.isInteger(value.size_bytes) || (value.size_bytes as number) < 0)) return null;
  const contentType = optionalEvidence(value.content_type, 256);
  if (contentType === null && value.content_type !== null) return null;
  const etag = optionalEvidence(value.etag, 256);
  if (etag === null && value.etag !== null) return null;
  const sha256 = optional(value.sha256, (v): string | null => (isHash256(v) ? v : null));
  if (sha256 === null && value.sha256 !== null) return null;
  const uploadedAt = optionalBounded(value.uploaded_at, 64);
  if (uploadedAt === null && value.uploaded_at !== null) return null;
  const sourcePrefix = optional(value.source_prefix, (v): string | null => (boundedString(v, 8192) && !v.includes("://") && !/[?#]/u.test(v) ? v : null));
  if (sourcePrefix === null && value.source_prefix !== null) return null;
  const manifestHash = optional(value.manifest_hash, (v): string | null => (isHash256(v) ? v : null));
  if (manifestHash === null && value.manifest_hash !== null) return null;
  return {
    backend: "b2_s3",
    bucketAlias: value.bucket_alias,
    objectKey: value.object_key,
    versionId,
    sizeBytes: value.size_bytes as number | null,
    contentType,
    etag,
    sha256,
    uploadedAt,
    sourcePrefix,
    manifestHash,
  };
}

function parseMetadata(value: unknown, kind: NodeKind): Readonly<Record<string, string | number | null>> | null {
  if (!isRecord(value)) return null;
  const allowedByKind: Record<string, ReadonlySet<string>> = {
    import_bundle: new Set(),
    genblaze_run: new Set(),
    manifest: new Set(["manifest_schema", "manifest_hash", "declared_content_sha256"]),
    asset: new Set(["title", "status", "media_type", "sha256", "size_bytes", "manifest_schema", "declared_content_sha256"]),
    standalone_artifact: new Set(["title", "status", "media_type", "sha256", "size_bytes", "manifest_schema", "declared_content_sha256"]),
    external_composition: new Set(["title", "status", "media_type", "sha256", "size_bytes", "manifest_schema", "declared_content_sha256"]),
  };
  const allowed = allowedByKind[kind];
  if (!allowed) return null;
  const out: Record<string, string | number | null> = {};
  for (const [key, item] of Object.entries(value)) {
    if (!allowed.has(key)) return null;
    if (["sha256", "manifest_hash", "declared_content_sha256"].includes(key)) {
      if (item !== null && !(typeof item === "string" && SHA256.test(item))) return null;
      out[key] = item as string | null;
    } else if (key === "size_bytes") {
      if (item !== null && (!Number.isInteger(item) || (item as number) < 0)) return null;
      out[key] = item as number | null;
    } else if (key === "manifest_schema") {
      if (item !== "1.5") return null;
      out[key] = item as string;
    } else {
      if (item !== null && !safeEvidenceString(item, 256)) return null;
      out[key] = item as string | null;
    }
  }
  return out;
}

function parseNode(value: unknown): LineageNode | null {
  if (!exactObject(value, ["node_id", "campaign_id", "bundle_id", "kind", "source_id", "source_role", "content_fingerprint", "evidence_class", "checks", "limitations", "run", "b2_reference", "metadata"])) return null;
  if (!safeEvidenceString(value.node_id, 128)) return null;
  if (!safeEvidenceString(value.campaign_id, 128)) return null;
  if (!safeEvidenceString(value.bundle_id, 128)) return null;
  if (typeof value.kind !== "string" || !NODE_KIND_SET.has(value.kind)) return null;
  if (!safeEvidenceString(value.source_id, 256)) return null;
  if (typeof value.source_role !== "string" || !SOURCE_ROLE_SET.has(value.source_role)) return null;
  if (!isHash256(value.content_fingerprint)) return null;
  if (typeof value.evidence_class !== "string" || !EVIDENCE_CLASSES.has(value.evidence_class)) return null;
  const checks = parseArray(value.checks, 32, parseCheck);
  if (checks === null) return null;
  const limitations = parseArray(value.limitations, 32, parseLimitation);
  if (limitations === null) return null;
  const b2Reference = optional(value.b2_reference, parseB2Reference);
  if (b2Reference === null && value.b2_reference !== null) return null;
  const metadata = parseMetadata(value.metadata, value.kind as NodeKind);
  if (!metadata) return null;
  let run: LineageRun | null = null;
  if (value.kind === "genblaze_run") {
    run = parseRun(value.run);
    if (!run) return null;
  } else if (value.run !== null) {
    return null;
  }
  return {
    nodeId: value.node_id,
    campaignId: value.campaign_id,
    bundleId: value.bundle_id,
    kind: value.kind as NodeKind,
    sourceId: value.source_id,
    sourceRole: value.source_role as SourceRole,
    contentFingerprint: value.content_fingerprint,
    evidenceClass: value.evidence_class as EvidenceClass,
    checks,
    limitations,
    run,
    b2Reference,
    metadata,
  };
}

function parseEdge(value: unknown, nodeIds: ReadonlySet<string>): LineageEdge | null {
  if (!exactObject(value, ["edge_id", "campaign_id", "bundle_id", "kind", "source_node_id", "target_node_id", "missing_source_id", "evidence_class", "hash_covered", "check_outcome", "source_locator", "limitations"])) return null;
  if (!safeEvidenceString(value.edge_id, 128)) return null;
  if (!safeEvidenceString(value.campaign_id, 128)) return null;
  if (!safeEvidenceString(value.bundle_id, 128)) return null;
  if (typeof value.kind !== "string" || !EDGE_KIND_SET.has(value.kind)) return null;
  if (!safeEvidenceString(value.source_node_id, 128) || !nodeIds.has(value.source_node_id)) return null;
  if (value.target_node_id !== null) {
    if (!safeEvidenceString(value.target_node_id, 128) || !nodeIds.has(value.target_node_id)) return null;
  }
  if (value.missing_source_id !== null) {
    if (!safeEvidenceString(value.missing_source_id, 256)) return null;
  }
  // Exactly one of target_node_id / missing_source_id must be present.
  if (((value.target_node_id === null) === (value.missing_source_id === null))) return null;
  if (typeof value.evidence_class !== "string" || !EVIDENCE_CLASSES.has(value.evidence_class)) return null;
  if (typeof value.hash_covered !== "boolean") return null;
  if (typeof value.check_outcome !== "string" || !CHECK_OUTCOME_SET.has(value.check_outcome)) return null;
  const sourceLocator = optionalEvidence(value.source_locator, 4096);
  if (sourceLocator === null && value.source_locator !== null) return null;
  const limitations = parseArray(value.limitations, 32, parseLimitation);
  if (limitations === null) return null;
  return {
    edgeId: value.edge_id,
    campaignId: value.campaign_id,
    bundleId: value.bundle_id,
    kind: value.kind as EdgeKind,
    sourceNodeId: value.source_node_id,
    targetNodeId: value.target_node_id,
    missingSourceId: value.missing_source_id,
    evidenceClass: value.evidence_class as EvidenceClass,
    hashCovered: value.hash_covered,
    checkOutcome: value.check_outcome as CheckOutcome,
    sourceLocator,
    limitations,
  };
}

function parseBundle(value: unknown): LineageBundle | null {
  if (!exactObject(value, ["bundle_id", "campaign_id", "bundle_fingerprint", "fingerprint_schema", "source_type", "source_slug", "source_revision", "state", "node_ids", "edge_ids"])) return null;
  if (!safeEvidenceString(value.bundle_id, 128)) return null;
  if (!safeEvidenceString(value.campaign_id, 128)) return null;
  if (!isHash256(value.bundle_fingerprint)) return null;
  if (value.fingerprint_schema !== "ps041d.fingerprint.v1") return null;
  if (value.source_type !== "genblaze_multi_provider_sample") return null;
  if (value.source_slug !== "genblaze-gen-media-multi-provider-sample") return null;
  if (value.source_revision !== "2e31577b7a9d5a7b0309d814f2d0282088b33fe8") return null;
  if (typeof value.state !== "string" || !BUNDLE_STATES.has(value.state)) return null;
  const nodeIds = parseArray(value.node_ids, 512, (v): string | null => (safeEvidenceString(v, 128) ? v : null));
  if (nodeIds === null) return null;
  const edgeIds = parseArray(value.edge_ids, 64, (v): string | null => (safeEvidenceString(v, 128) ? v : null));
  if (edgeIds === null) return null;
  return {
    bundleId: value.bundle_id,
    campaignId: value.campaign_id,
    bundleFingerprint: value.bundle_fingerprint,
    fingerprintSchema: value.fingerprint_schema,
    sourceType: value.source_type,
    sourceSlug: value.source_slug,
    sourceRevision: value.source_revision,
    state: value.state as "complete" | "partial_bundle",
    nodeIds,
    edgeIds,
  };
}

function parseGraph(nodesValue: unknown, edgesValue: unknown): { nodes: readonly LineageNode[]; edges: readonly LineageEdge[] } | null {
  const nodes = parseArray(nodesValue, 512, parseNode);
  if (nodes === null) return null;
  const nodeIds = new Set<string>();
  for (const node of nodes) {
    if (nodeIds.has(node.nodeId)) return null;
    nodeIds.add(node.nodeId);
  }
  if (!Array.isArray(edgesValue) || edgesValue.length > 64) return null;
  const edges: LineageEdge[] = [];
  const edgeIds = new Set<string>();
  for (const raw of edgesValue) {
    const edge = parseEdge(raw, nodeIds);
    if (!edge) return null;
    if (edgeIds.has(edge.edgeId)) return null;
    edgeIds.add(edge.edgeId);
    edges.push(edge);
  }
  return { nodes, edges };
}

// --- Top-level entrypoints -----------------------------------------------------

export function parseLineageList(payload: unknown): LineageListPayload | null {
  if (!exactObject(payload, ["source", "campaign_access_scope", "bundles"])) return null;
  if (payload.source !== "proof_api") return null;
  if (typeof payload.campaign_access_scope !== "string" || payload.campaign_access_scope.length === 0) return null;
  const bundles = parseArray(payload.bundles, 50, parseBundle);
  if (bundles === null) return null;
  const seen = new Set<string>();
  for (const bundle of bundles) {
    if (bundle.campaignId !== payload.campaign_access_scope) return null;
    if (seen.has(bundle.bundleId)) return null;
    seen.add(bundle.bundleId);
  }
  return { kind: "list", campaignAccessScope: payload.campaign_access_scope, bundles };
}

export function parseLineageDetail(payload: unknown): LineageDetailPayload | null {
  if (!exactObject(payload, ["source", "campaign_access_scope", "lineage"])) return null;
  if (payload.source !== "proof_api") return null;
  if (typeof payload.campaign_access_scope !== "string" || payload.campaign_access_scope.length === 0) return null;
  const lineage = payload.lineage;
  if (!exactObject(lineage, ["created", "bundle", "nodes", "edges"])) return null;
  if (typeof lineage.created !== "boolean") return null;
  const bundle = parseBundle(lineage.bundle);
  if (!bundle || bundle.campaignId !== payload.campaign_access_scope) return null;
  const graph = parseGraph(lineage.nodes, lineage.edges);
  if (!graph) return null;
  const nodeSet = new Set(graph.nodes.map((n) => n.nodeId));
  const edgeSet = new Set(graph.edges.map((e) => e.edgeId));
  if (bundle.nodeIds.length !== nodeSet.size || !bundle.nodeIds.every((id) => nodeSet.has(id))) return null;
  if (bundle.edgeIds.length !== edgeSet.size || !bundle.edgeIds.every((id) => edgeSet.has(id))) return null;
  for (const node of graph.nodes) {
    if (node.campaignId !== payload.campaign_access_scope || node.bundleId !== bundle.bundleId) return null;
  }
  for (const edge of graph.edges) {
    if (edge.campaignId !== payload.campaign_access_scope || edge.bundleId !== bundle.bundleId) return null;
  }
  return {
    kind: "detail",
    campaignAccessScope: payload.campaign_access_scope,
    created: lineage.created,
    bundle,
    nodes: graph.nodes,
    edges: graph.edges,
  };
}

export function parseLineagePassport(payload: unknown): LineagePassportPayload | null {
  if (!exactObject(payload, ["source", "campaign_access_scope", "passport"])) return null;
  if (payload.source !== "proof_api") return null;
  if (typeof payload.campaign_access_scope !== "string" || payload.campaign_access_scope.length === 0) return null;
  const passport = payload.passport;
  if (!exactObject(passport, ["schema", "campaign_id", "bundle_id", "bundle_fingerprint", "source_type", "source_slug", "source_revision", "state", "nodes", "edges", "limitations", "truth_boundary"])) return null;
  if (passport.schema !== "proofstudio.portable_lineage_passport.v1") return null;
  if (typeof passport.campaign_id !== "string" || passport.campaign_id !== payload.campaign_access_scope) return null;
  if (typeof passport.bundle_id !== "string" || passport.bundle_id.length === 0) return null;
  if (!isHash256(passport.bundle_fingerprint)) return null;
  if (passport.source_type !== "genblaze_multi_provider_sample") return null;
  if (passport.source_slug !== "genblaze-gen-media-multi-provider-sample") return null;
  if (passport.source_revision !== "2e31577b7a9d5a7b0309d814f2d0282088b33fe8") return null;
  if (typeof passport.state !== "string" || !BUNDLE_STATES.has(passport.state)) return null;
  if (passport.truth_boundary !== SERVER_TRUTH_BOUNDARY) return null;
  const limitations = parseArray(passport.limitations, 32, parseLimitation);
  if (limitations === null) return null;
  const graph = parseGraph(passport.nodes, passport.edges);
  if (!graph) return null;
  for (const node of graph.nodes) {
    if (node.campaignId !== payload.campaign_access_scope || node.bundleId !== passport.bundle_id) return null;
  }
  for (const edge of graph.edges) {
    if (edge.campaignId !== payload.campaign_access_scope || edge.bundleId !== passport.bundle_id) return null;
  }
  return {
    kind: "passport",
    campaignAccessScope: payload.campaign_access_scope,
    schema: passport.schema,
    campaignId: passport.campaign_id,
    bundleId: passport.bundle_id,
    bundleFingerprint: passport.bundle_fingerprint,
    sourceType: passport.source_type,
    sourceSlug: passport.source_slug,
    sourceRevision: passport.source_revision,
    state: passport.state as "complete" | "partial_bundle",
    nodes: graph.nodes,
    edges: graph.edges,
    limitations,
    truthBoundary: passport.truth_boundary,
  };
}

// --- Display-safe labels -------------------------------------------------------

export function nodeKindLabel(kind: NodeKind): string {
  switch (kind) {
    case "import_bundle": return "Import bundle";
    case "standalone_artifact": return "Standalone artifact";
    case "genblaze_run": return "Genblaze Run";
    case "manifest": return "Manifest observation";
    case "asset": return "Generated asset";
    case "external_composition": return "External composition";
  }
}

export function edgeKindLabel(kind: EdgeKind): string {
  switch (kind) {
    case "parent_run": return "parent run";
    case "generated_asset": return "generated asset";
    case "external_input": return "external input";
    case "storyboard_for": return "storyboard for";
    case "scene_member": return "scene member";
    case "composition_input": return "composition input";
    case "composed_output": return "composed output";
    case "manifest_for": return "manifest for";
    case "embedded_manifest": return "embedded manifest";
  }
}

export function sourceRoleLabel(role: SourceRole): string {
  switch (role) {
    case "stage_a_storyboard": return "Stage A storyboard";
    case "stage_b0_manifest": return "Stage B0 manifest";
    case "stage_b1_manifest": return "Stage B1 manifest";
    case "stage_b2_manifest": return "Stage B2 manifest";
    case "stage_c_composition": return "Stage C composition";
    case "final_delivery": return "Final delivery";
    case "embedded_manifest": return "Embedded manifest";
    case "import_bundle": return "Import bundle";
    case "generated_asset": return "Generated asset";
    case "external_input": return "External input";
  }
}

export function stageLabel(stage: StageKey): string {
  switch (stage) {
    case "A": return "Stage A";
    case "B0": return "Stage B0";
    case "B1": return "Stage B1";
    case "B2": return "Stage B2";
    case "C": return "Stage C";
  }
}

export function checkOutcomeLabel(outcome: CheckOutcome): string {
  switch (outcome) {
    case "recorded": return "Recorded";
    case "parsed": return "Parsed";
    case "hash_present": return "Hash present";
    case "hash_verified": return "Hash verified";
    case "hash_mismatch": return "Hash mismatch";
    case "manifest_hash_verified": return "Manifest hash verified";
    case "manifest_output_hashes_declared": return "Manifest output hashes declared";
    case "manifest_invalid": return "Manifest invalid";
    case "object_missing": return "Object missing";
    case "relationship_recorded": return "Relationship recorded";
    case "relationship_inferred": return "Relationship inferred";
    case "unsupported_schema": return "Unsupported schema";
    case "partial_bundle": return "Partial bundle";
    case "unavailable": return "Unavailable";
    case "not_checked": return "Not checked";
  }
}

export function checkOutcomeDetail(outcome: CheckOutcome): string {
  switch (outcome) {
    case "recorded": return "The pipeline recorded this evidence.";
    case "parsed": return "The recorded structure parsed under the supported schema.";
    case "hash_present": return "A digest was recorded; bytes were not necessarily retrieved and checked.";
    case "hash_verified": return "Recorded hash matched the checked content.";
    case "hash_mismatch": return "Recorded and observed hashes did not match.";
    case "manifest_hash_verified": return "The recorded Manifest canonical hash matched.";
    case "manifest_output_hashes_declared": return "Output hashes were declared in the Manifest; bytes were not necessarily retrieved and checked.";
    case "manifest_invalid": return "The recorded Manifest did not validate under the supported schema.";
    case "object_missing": return "The referenced object was recorded as missing.";
    case "relationship_recorded": return "The relationship is present in the recorded pipeline evidence.";
    case "relationship_inferred": return "The relationship was inferred from bundle convention, not recorded as evidence.";
    case "unsupported_schema": return "The source schema is not supported by this reader.";
    case "partial_bundle": return "The imported record is incomplete.";
    case "unavailable": return "The evidence dependency was unavailable.";
    case "not_checked": return "No byte-level verification was recorded.";
  }
}

export type Severity = "ok" | "warn" | "danger" | "neutral" | "unsupported";

export function checkSeverity(outcome: CheckOutcome): Severity {
  switch (outcome) {
    case "hash_verified":
    case "manifest_hash_verified":
    case "recorded":
    case "parsed":
    case "relationship_recorded":
      return "ok";
    case "hash_present":
    case "manifest_output_hashes_declared":
    case "relationship_inferred":
    case "partial_bundle":
    case "object_missing":
      return "warn";
    case "hash_mismatch":
    case "manifest_invalid":
    case "unsupported_schema":
    case "unavailable":
      return "danger";
    case "not_checked":
      return "neutral";
  }
}

// --- Highest-risk (worst-outcome) priority ------------------------------------
//
// The node-card summary must surface the highest-risk recorded outcome so a
// success badge can never conceal a mismatch or invalid Manifest. The priority
// order is:
//   1. danger     (hash_mismatch, manifest_invalid, unsupported_schema, unavailable)
//   2. unsupported
//   3. warn       (hash_present, object_missing, partial_bundle, ...)
//   4. neutral    (not_checked)
//   5. ok         (parsed, recorded, manifest_hash_verified, ...)
//
// Lower rank value wins (rank 0 is the worst). This deterministic priority is
// exercised by `mainCheckForNode` in BundleLineage.tsx and by the runtime
// check-priority validation.
export type Priority = "danger" | "unsupported" | "warn" | "neutral" | "ok";
export const PRIORITY_ORDER: readonly Priority[] = ["danger", "unsupported", "warn", "neutral", "ok"];
const PRIORITY_RANK: Record<Priority, number> = { danger: 0, unsupported: 1, warn: 2, neutral: 3, ok: 4 };

export function severityPriority(severity: Severity): Priority {
  return severity as Priority;
}

export function priorityRank(priority: Priority): number {
  return PRIORITY_RANK[priority];
}

// Returns the worst-outcome check deterministically. Ties are resolved by
// stable first-occurrence order (the earliest worst-outcome check wins) so the
// badge reflects the first recorded worst outcome the pipeline observed.
export function worstCheck<T extends { outcome: CheckOutcome }>(checks: readonly T[]): T | null {
  if (checks.length === 0) return null;
  let best = checks[0]!;
  let bestRank = priorityRank(severityPriority(checkSeverity(best.outcome)));
  for (let i = 1; i < checks.length; i++) {
    const check = checks[i]!;
    const rank = priorityRank(severityPriority(checkSeverity(check.outcome)));
    if (rank < bestRank) {
      best = check;
      bestRank = rank;
    }
  }
  return best;
}

// --- Stage classification ------------------------------------------------------

export type StageKey = "A" | "B0" | "B1" | "B2" | "C";
export const STAGE_ORDER: readonly StageKey[] = ["A", "B0", "B1", "B2", "C"];

// A node's stage placement can be one of the accepted lanes A/B0/B1/B2/C, the
// dedicated bundle-root context, or "unclassified" for truly unresolved nodes
// (rendered in a dedicated section outside Stage A, never inside it).
export type NodeStage = StageKey | "bundle-root" | "unclassified";

// Per-node fallback used by simple callers (e.g. the passport table). It does
// not consult edges, so generated-asset / external-input nodes that derive
// their stage from a connected Run may return "unclassified" here. Use
// `buildStageLayout` for the authoritative graph-aware classification.
export function stageForNode(node: LineageNode): StageKey | null {
  if (node.kind === "import_bundle") return null;
  switch (node.sourceRole) {
    case "stage_a_storyboard": return "A";
    case "stage_c_composition":
    case "final_delivery":
    case "embedded_manifest":
      return "C";
    default:
      return null;
  }
}

// O(N+E) graph-aware classification. Builds adjacency maps once before
// assigning each node to a lane, using only the accepted node kinds, edge
// kinds, source roles, and run stages. No relationship is invented.
//
// Accepted mapping:
//   import_bundle root                    -> bundle-root context
//   standalone_artifact (stage_a_storyboard) -> Stage A
//   genblaze_run with run.stage            -> its exact run.stage (B0/B1/B2)
//   manifest (stage_bN_manifest)           -> BN
//   manifest (embedded_manifest)           -> Stage C
//   asset (generated_asset)                -> stage of its generating Run via
//                                             the accepted generated_asset edge
//   asset (final_delivery)                 -> Stage C
//   asset (external_input)                 -> stage of its connected Run via
//                                             the accepted external_input edge
//   external_composition (stage_c)         -> Stage C
//   truly unresolved nodes                 -> "unclassified"
export function classifyNodeStages(
  nodes: readonly LineageNode[],
  edges: readonly LineageEdge[],
): ReadonlyMap<string, NodeStage> {
  const nodeById = new Map<string, LineageNode>();
  for (const n of nodes) nodeById.set(n.nodeId, n);

  // asset/node id -> stage derived from a recorded relationship edge.
  const manifestToRunStage = new Map<string, StageKey>();
  const generatedAssetToRunStage = new Map<string, StageKey>();
  const externalInputToRunStage = new Map<string, StageKey>();

  for (const edge of edges) {
    if (edge.kind === "manifest_for" && edge.targetNodeId) {
      const source = nodeById.get(edge.sourceNodeId);
      const target = nodeById.get(edge.targetNodeId);
      if (source?.kind === "manifest" && target?.kind === "genblaze_run" && target.run) {
        manifestToRunStage.set(source.nodeId, target.run.stage);
      }
    } else if (edge.kind === "generated_asset" && edge.targetNodeId) {
      const source = nodeById.get(edge.sourceNodeId);
      const target = nodeById.get(edge.targetNodeId);
      if (source?.kind === "genblaze_run" && source.run && target?.kind === "asset") {
        generatedAssetToRunStage.set(target.nodeId, source.run.stage);
      }
    } else if (edge.kind === "external_input") {
      const source = nodeById.get(edge.sourceNodeId);
      const target = edge.targetNodeId ? nodeById.get(edge.targetNodeId) : undefined;
      if (source && target?.kind === "genblaze_run" && target.run) {
        externalInputToRunStage.set(source.nodeId, target.run.stage);
      }
    }
  }

  const out = new Map<string, NodeStage>();
  for (const node of nodes) {
    if (node.kind === "import_bundle") {
      out.set(node.nodeId, "bundle-root");
      continue;
    }
    if (node.kind === "standalone_artifact" && node.sourceRole === "stage_a_storyboard") {
      out.set(node.nodeId, "A");
      continue;
    }
    if (node.kind === "genblaze_run" && node.run) {
      out.set(node.nodeId, node.run.stage);
      continue;
    }
    if (node.kind === "manifest") {
      if (node.sourceRole === "stage_b0_manifest") out.set(node.nodeId, "B0");
      else if (node.sourceRole === "stage_b1_manifest") out.set(node.nodeId, "B1");
      else if (node.sourceRole === "stage_b2_manifest") out.set(node.nodeId, "B2");
      else if (node.sourceRole === "embedded_manifest") out.set(node.nodeId, "C");
      else if (manifestToRunStage.has(node.nodeId)) out.set(node.nodeId, manifestToRunStage.get(node.nodeId)!);
      else out.set(node.nodeId, "unclassified");
      continue;
    }
    if (node.kind === "asset") {
      if (node.sourceRole === "final_delivery") {
        out.set(node.nodeId, "C");
      } else if (node.sourceRole === "generated_asset" && generatedAssetToRunStage.has(node.nodeId)) {
        out.set(node.nodeId, generatedAssetToRunStage.get(node.nodeId)!);
      } else if (node.sourceRole === "external_input" && externalInputToRunStage.has(node.nodeId)) {
        out.set(node.nodeId, externalInputToRunStage.get(node.nodeId)!);
      } else {
        out.set(node.nodeId, "unclassified");
      }
      continue;
    }
    if (node.kind === "external_composition") {
      out.set(node.nodeId, "C");
      continue;
    }
    if (node.sourceRole === "stage_c_composition" || node.sourceRole === "final_delivery" || node.sourceRole === "embedded_manifest") {
      out.set(node.nodeId, "C");
      continue;
    }
    out.set(node.nodeId, "unclassified");
  }
  return out;
}

export interface StageGroup {
  readonly stage: StageKey;
  readonly nodes: readonly LineageNode[];
  readonly unsupported: readonly LineageNode[];
}

export interface StageLayout {
  readonly bundleRoot: LineageNode | null;
  readonly stages: Readonly<Record<StageKey, readonly LineageNode[]>>;
  readonly unclassified: readonly LineageNode[];
  readonly classification: ReadonlyMap<string, NodeStage>;
}

// O(N+E) stage grouping using a single classification pass plus a stable
// sort by node ID within each lane. The import-bundle root node is presented
// in its own "bundle context" section; truly unresolved nodes are placed in
// a dedicated "Unclassified recorded nodes" section OUTSIDE Stage A.
export function buildStageLayout(nodes: readonly LineageNode[], edges: readonly LineageEdge[]): StageLayout {
  const classification = classifyNodeStages(nodes, edges);
  const ordered = [...nodes].sort(compareById);
  const buckets: Record<StageKey, LineageNode[]> = { A: [], B0: [], B1: [], B2: [], C: [] };
  let bundleRoot: LineageNode | null = null;
  const unclassified: LineageNode[] = [];
  for (const node of ordered) {
    const stage = classification.get(node.nodeId) ?? "unclassified";
    if (stage === "bundle-root") {
      if (!bundleRoot) bundleRoot = node;
      else unclassified.push(node);
    } else if (stage === "unclassified") {
      unclassified.push(node);
    } else {
      buckets[stage].push(node);
    }
  }
  const stages = {} as Record<StageKey, readonly LineageNode[]>;
  for (const stage of STAGE_ORDER) stages[stage] = buckets[stage];
  return { bundleRoot, stages, unclassified, classification };
}

// Back-compat wrapper for callers that ask for the legacy StageGroup shape.
// Internally delegates to the graph-aware layout. The per-stage `unsupported`
// list is always empty here — unsupported nodes are now hoisted into the
// dedicated "Unclassified recorded nodes" section by the detail page.
export function groupNodesByStage(nodes: readonly LineageNode[], edges: readonly LineageEdge[] = []): Readonly<Record<StageKey, StageGroup>> {
  const layout = buildStageLayout(nodes, edges);
  const result = {} as Record<StageKey, StageGroup>;
  for (const stage of STAGE_ORDER) {
    result[stage] = { stage, nodes: layout.stages[stage], unsupported: [] };
  }
  return result;
}

// --- Deterministic ordering ----------------------------------------------------

export function compareById(a: { readonly nodeId?: string; readonly edgeId?: string; readonly bundleId?: string; readonly stepId?: string; readonly runId?: string } | string, b: typeof a | string): number {
  const ka = typeof a === "string" ? a : (a.nodeId ?? a.edgeId ?? a.bundleId ?? a.stepId ?? a.runId ?? "");
  const kb = typeof b === "string" ? b : (b.nodeId ?? b.edgeId ?? b.bundleId ?? b.stepId ?? b.runId ?? "");
  if (ka < kb) return -1;
  if (ka > kb) return 1;
  return 0;
}

// O(E) edge preparation. Edges are sorted by (kind, source, target) for stable
// rendering. Node references are resolved via the supplied Map (O(1) lookup).
export function sortEdges(edges: readonly LineageEdge[]): readonly LineageEdge[] {
  return [...edges].sort((a, b) => {
    if (a.kind !== b.kind) return a.kind < b.kind ? -1 : 1;
    if (a.sourceNodeId !== b.sourceNodeId) return a.sourceNodeId < b.sourceNodeId ? -1 : 1;
    const ta = a.targetNodeId ?? a.missingSourceId ?? "";
    const tb = b.targetNodeId ?? b.missingSourceId ?? "";
    if (ta !== tb) return ta < tb ? -1 : 1;
    return 0;
  });
}

export function buildNodeMap(nodes: readonly LineageNode[]): ReadonlyMap<string, LineageNode> {
  const map = new Map<string, LineageNode>();
  for (const node of nodes) map.set(node.nodeId, node);
  return map;
}

// --- Edge accessible description ----------------------------------------------

export function edgeAccessibleLabel(edge: LineageEdge, sourceNode: LineageNode | undefined, targetNode: LineageNode | undefined): string {
  const rel = edgeKindLabel(edge.kind);
  const sourceLabel = sourceNode ? `${nodeKindLabel(sourceNode.kind)} ${sourceNode.sourceId}` : edge.sourceNodeId;
  let targetLabel: string;
  if (edge.targetNodeId && targetNode) targetLabel = `${nodeKindLabel(targetNode.kind)} ${targetNode.sourceId}`;
  else if (edge.targetNodeId) targetLabel = edge.targetNodeId;
  else targetLabel = `missing ${edge.missingSourceId ?? "source"}`;
  const evidence = edge.evidenceClass === "recorded" ? "Recorded" : "Inferred";
  const hashCover = edge.hashCovered ? "hash-covered" : "not hash-covered";
  return `${evidence} ${rel} from ${sourceLabel} to ${targetLabel} (${hashCover}).`;
}

// --- B2 reference display ------------------------------------------------------

export interface B2ReferenceField {
  readonly label: string;
  readonly value: string;
}

// Renders only accepted structured fields. Never constructs a URL, never
// exposes account ids / access keys / secret keys / signed URLs / arbitrary
// upstream metadata.
export function b2ReferenceFields(ref: B2Reference): readonly B2ReferenceField[] {
  const fields: B2ReferenceField[] = [
    { label: "Configured alias", value: ref.bucketAlias },
    { label: "Normalized object key", value: ref.objectKey },
  ];
  if (ref.versionId) fields.push({ label: "Recorded version ID", value: ref.versionId });
  if (ref.sizeBytes !== null) fields.push({ label: "Recorded content length", value: `${ref.sizeBytes} bytes` });
  if (ref.contentType) fields.push({ label: "Recorded content type", value: ref.contentType });
  if (ref.etag) fields.push({ label: "Recorded ETag", value: ref.etag });
  if (ref.sha256) fields.push({ label: "Recorded SHA-256", value: ref.sha256 });
  if (ref.uploadedAt) fields.push({ label: "Recorded uploaded at", value: ref.uploadedAt });
  return fields;
}

// --- Safe bundle id for filenames ---------------------------------------------

export function safeBundleIdForFilename(bundleId: string): string {
  // Keep only ASCII alphanumerics, dash, underscore, dot. Collapse repeats and
  // trim. The result is safe to embed in a download filename and contains no
  // path separators or signed-URL characters.
  const cleaned = bundleId.replace(/[^A-Za-z0-9._-]/g, "-").replace(/-{2,}/g, "-").replace(/^-+|-+$/g, "");
  const trimmed = cleaned.length > 64 ? cleaned.slice(0, 64) : cleaned;
  return trimmed.length > 0 ? trimmed : "bundle";
}

// --- Fingerprint progressive disclosure ---------------------------------------

export function shortFingerprint(fingerprint: string): string {
  // Progressive disclosure: show prefix and suffix only. Full value remains
  // available in an expandable details region in the UI.
  if (fingerprint.length <= 16) return fingerprint;
  return `${fingerprint.slice(0, 10)}…${fingerprint.slice(-6)}`;
}

// --- Provider / model display --------------------------------------------------

export function providerModelDisplay(step: LineageStep): { provider: string; model: string } {
  return {
    provider: step.provider ?? "(provider not recorded)",
    model: step.model,
  };
}
