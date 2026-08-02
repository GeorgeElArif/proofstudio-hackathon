// PS-032 Operations Cockpit / Flight Recorder v2 -- verified cockpit
// constants.
//
// This is the PS-031A hardened product module "Operations Cockpit / Flight
// Recorder v2". It merges Mission Control, Flight Recorder, Failure-as-Proof
// Timeline, Failure Theater, Evidence Graph, and the pipeline lifecycle view
// into one operating cockpit for designers, marketers, reviewers, clients, and
// judges.
//
// Every golden value in this module is sourced verbatim from the same
// checked-in evidence already used by PS-021 / PS-024 / PS-025 / PS-026 /
// PS-027 / PS-028 / PS-029 / PS-030 / PS-031:
//
//   - docs/evidence/demo/golden-demo-run.json                          (PS-024 golden manifest)
//   - docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json        (PS-021 live B2 durable rehydrate)
//   - docs/evidence/ps-025/public-durable-passport-unlock-smoke.json   (PS-025 public durable passport)
//   - docs/evidence/ps-026/b2-evidence-explorer-smoke.json             (PS-026 B2 Evidence Explorer)
//   - docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json          (PS-027 Genblaze Pipeline Graph)
//   - docs/evidence/ps-028/manifest-verification-panel-smoke.json      (PS-028 Manifest Verification Panel)
//   - docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json          (PS-029 B2 Rehydrate Comparison)
//   - docs/evidence/ps-030/failure-as-proof-timeline-smoke.json        (PS-030 Failure-as-Proof Timeline)
//   - docs/evidence/ps-031/export-campaign-pack-v2-smoke.json          (PS-031 Judge Evidence Pack)
//
// The PS-032 smoke validates that every value below matches the source
// evidence exactly AND that every source agrees on the same value. No value
// is invented here.
//
// These constants exist so the Operations Cockpit surface
// (apps/web/src/OperationsCockpit.tsx) can render a real operating cockpit
// (run status summary, operational phase map, flight recorder timeline,
// evidence graph, Failure Theater slot, action rail, designer / marketer next
// actions, truth boundary, limitations) without re-fetching the API on every
// render and without reading any B2 object. The cockpit performs no network
// call, calls no provider, and reads no B2 object: it only renders verified,
// checked-in evidence.
//
// Truth boundary: the Operations Cockpit shows that the checked-in evidence
// (PS-021 through PS-031) records a B2 rehydrate proof with zero provider
// calls during rehydrate, agrees on the golden run's identifiers, archive URI,
// and archive SHA-256, and records rehydrate_source = b2_rehydrated. The
// cockpit summarizes checked-in evidence, links to B2 archive evidence, links
// to Genblaze manifest evidence, shows zero provider calls during rehydrate,
// helps reviewers understand workflow provenance, and shows pending product
// gaps honestly. The cockpit does not prove semantic truth, legal
// authenticity, C2PA authenticity, or human authorship. The cockpit does not
// prove Object Lock or tamper-proof storage. The cockpit did not fetch and
// hash the B2 object in the browser. The local contract is verified; the
// public deployment remains pending until the new backend is deployed and the
// public URL is verified end-to-end.

// Verified golden demo run_id (PS-021 -> PS-024 -> PS-025 -> PS-026 -> PS-027
// -> PS-028 -> PS-029 -> PS-030 -> PS-031).
export const OPERATIONS_COCKPIT_RUN_ID =
  "run_89d967f9000045efa22ed4cc78cfa67f";

// Verified golden demo campaign_id (PS-021 -> PS-024 -> PS-025 -> PS-026 ->
// PS-027 -> PS-028 -> PS-029 -> PS-030 -> PS-031).
export const OPERATIONS_COCKPIT_CAMPAIGN_ID =
  "camp_bea5161faa6244079d2ee01ce445c259";

// Verified Backblaze B2 archive URI for the golden demo run (PS-021).
export const OPERATIONS_COCKPIT_ARCHIVE_URI =
  "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json";

// Verified SHA-256 of the B2 archive content for the golden demo run (PS-021).
export const OPERATIONS_COCKPIT_ARCHIVE_SHA256 =
  "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141";

// Rehydrate source recorded by PS-021 (durable_source = b2_rehydrated).
export const OPERATIONS_COCKPIT_REHYDRATE_SOURCE = "b2_rehydrated";

// PS-021 proved zero provider calls during B2 rehydrate.
export const OPERATIONS_COCKPIT_PROVIDER_CALLS_DURING_REHYDRATE = 0;

// PS-021 proved no live provider call happened during B2 rehydrate.
export const OPERATIONS_COCKPIT_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE = true;

// Cockpit identity. The cockpit_id is deterministic (not a random UUID): it is
// derived from the verified golden run_id and the cockpit version, so the same
// golden run always yields the same cockpit_id. This keeps the smoke free of
// brittle timestamp/UUID expectations.
export const OPERATIONS_COCKPIT_COCKPIT_ID =
  "cockpit_ps032_" + OPERATIONS_COCKPIT_RUN_ID;

// Cockpit schema version. Bumped on any shape change to the cockpit data.
export const OPERATIONS_COCKPIT_COCKPIT_VERSION = "1.0.0";

// Honest provenance label for the cockpit. Surfaced verbatim so a judge never
// reads "live operational feed" when the values are produced locally from
// checked-in evidence.
export const OPERATIONS_COCKPIT_GENERATED_FROM =
  "local checked-in ProofStudio evidence (PS-021, PS-024, PS-025, PS-026, " +
  "PS-027, PS-028, PS-029, PS-030, PS-031) -- no server round-trip, no B2 " +
  "byte read, no provider call";

// PS-025 local contract (FastAPI TestClient against a fresh empty store
// resolving the golden run_id from checked-in evidence) is verified.
export const OPERATIONS_COCKPIT_LOCAL_CONTRACT_PROOF = true;

// PS-025: the public Render deployment is NOT verified yet. The new backend
// code must be deployed and the public URL must be verified end-to-end before
// this flag is flipped.
export const OPERATIONS_COCKPIT_PUBLIC_DEPLOYMENT_PENDING = true;

// PS-026 unlock scope marker. Mirrors the backend
// `GOLDEN_DEMO_UNLOCK_SCOPE = "golden_demo_only"` so the cockpit honestly
// reports the narrow allowlist (only this single run_id resolves publicly).
export const OPERATIONS_COCKPIT_UNLOCK_SCOPE = "golden_demo_only";

// Checked-in source evidence paths the cockpit cross-references. These are the
// files the PS-032 smoke reads to verify every published value.
export const OPERATIONS_COCKPIT_SOURCE_PS024_MANIFEST =
  "docs/evidence/demo/golden-demo-run.json";
export const OPERATIONS_COCKPIT_SOURCE_PS021_EVIDENCE =
  "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json";
export const OPERATIONS_COCKPIT_SOURCE_PS025_EVIDENCE =
  "docs/evidence/ps-025/public-durable-passport-unlock-smoke.json";
export const OPERATIONS_COCKPIT_SOURCE_PS026_EVIDENCE =
  "docs/evidence/ps-026/b2-evidence-explorer-smoke.json";
export const OPERATIONS_COCKPIT_SOURCE_PS027_EVIDENCE =
  "docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json";
export const OPERATIONS_COCKPIT_SOURCE_PS028_EVIDENCE =
  "docs/evidence/ps-028/manifest-verification-panel-smoke.json";
export const OPERATIONS_COCKPIT_SOURCE_PS029_EVIDENCE =
  "docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json";
export const OPERATIONS_COCKPIT_SOURCE_PS030_EVIDENCE =
  "docs/evidence/ps-030/failure-as-proof-timeline-smoke.json";
export const OPERATIONS_COCKPIT_SOURCE_PS031_EVIDENCE =
  "docs/evidence/ps-031/export-campaign-pack-v2-smoke.json";

// PS-032 references the binding implementation roadmap and the PS-031A
// hardened product module correction.
export const OPERATIONS_COCKPIT_IMPLEMENTATION_ROADMAP =
  "docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md";
export const OPERATIONS_COCKPIT_PS031A_ROADMAP_CORRECTION =
  "docs/roadmap/ps-031a-hardened-product-modules-correction.md";

// ---------------------------------------------------------------------------
// Required source list. The cockpit cross-references nine evidence sources
// plus the implementation roadmap and the PS-031A correction.
// ---------------------------------------------------------------------------

export type OperationsCockpitSourceKind =
  | "golden_manifest"
  | "b2_durable_evidence"
  | "passport_evidence"
  | "explorer_evidence"
  | "pipeline_evidence"
  | "manifest_panel_evidence"
  | "rehydrate_comparison_evidence"
  | "failure_timeline_evidence"
  | "export_pack_evidence"
  | "roadmap_correction";

export interface OperationsCockpitSource {
  id: string;
  label: string;
  sliceTag: string;
  kind: OperationsCockpitSourceKind;
  evidencePath: string;
}

export const OPERATIONS_COCKPIT_SOURCES: readonly OperationsCockpitSource[] = [
  {
    id: "ps024",
    label: "Golden demo manifest",
    sliceTag: "PS-024",
    kind: "golden_manifest",
    evidencePath: OPERATIONS_COCKPIT_SOURCE_PS024_MANIFEST,
  },
  {
    id: "ps021",
    label: "PS-021 B2 durable rehydrate evidence",
    sliceTag: "PS-021",
    kind: "b2_durable_evidence",
    evidencePath: OPERATIONS_COCKPIT_SOURCE_PS021_EVIDENCE,
  },
  {
    id: "ps025",
    label: "PS-025 public durable passport evidence",
    sliceTag: "PS-025",
    kind: "passport_evidence",
    evidencePath: OPERATIONS_COCKPIT_SOURCE_PS025_EVIDENCE,
  },
  {
    id: "ps026",
    label: "PS-026 B2 Evidence Explorer evidence",
    sliceTag: "PS-026",
    kind: "explorer_evidence",
    evidencePath: OPERATIONS_COCKPIT_SOURCE_PS026_EVIDENCE,
  },
  {
    id: "ps027",
    label: "PS-027 Genblaze Pipeline Graph evidence",
    sliceTag: "PS-027",
    kind: "pipeline_evidence",
    evidencePath: OPERATIONS_COCKPIT_SOURCE_PS027_EVIDENCE,
  },
  {
    id: "ps028",
    label: "PS-028 Manifest Verification Panel evidence",
    sliceTag: "PS-028",
    kind: "manifest_panel_evidence",
    evidencePath: OPERATIONS_COCKPIT_SOURCE_PS028_EVIDENCE,
  },
  {
    id: "ps029",
    label: "PS-029 B2 Rehydrate Comparison evidence",
    sliceTag: "PS-029",
    kind: "rehydrate_comparison_evidence",
    evidencePath: OPERATIONS_COCKPIT_SOURCE_PS029_EVIDENCE,
  },
  {
    id: "ps030",
    label: "PS-030 Failure-as-Proof Timeline evidence",
    sliceTag: "PS-030",
    kind: "failure_timeline_evidence",
    evidencePath: OPERATIONS_COCKPIT_SOURCE_PS030_EVIDENCE,
  },
  {
    id: "ps031",
    label: "PS-031 Judge Evidence Pack evidence",
    sliceTag: "PS-031",
    kind: "export_pack_evidence",
    evidencePath: OPERATIONS_COCKPIT_SOURCE_PS031_EVIDENCE,
  },
  {
    id: "ps031a",
    label: "PS-031A hardened product module roadmap correction",
    sliceTag: "PS-031A",
    kind: "roadmap_correction",
    evidencePath: OPERATIONS_COCKPIT_PS031A_ROADMAP_CORRECTION,
  },
];

// ---------------------------------------------------------------------------
// Run status summary.
//
// A compact operational status row so a designer / marketer / reviewer can
// read the state of the golden run at a glance: campaign/run identity, archive
// status, manifest status, rehydrate status, provider call status during
// rehydrate, evidence pack status, review / export readiness, pending public
// deployment.
// ---------------------------------------------------------------------------

export interface OperationsCockpitRunStatusItem {
  key: string;
  label: string;
  status: string;
  truthClass: OperationsCockpitTruthClass;
  note: string;
}

export const OPERATIONS_COCKPIT_RUN_STATUS: readonly OperationsCockpitRunStatusItem[] =
  [
    {
      key: "campaign_run_identity",
      label: "Campaign / run identity",
      status: "pinned",
      truthClass: "checked_in_evidence",
      note:
        "One canonical golden demo run pinned honestly from the PS-024 golden " +
        "manifest, traced to the PS-021 live B2 durable rehydrate smoke.",
    },
    {
      key: "archive_status",
      label: "Archive status",
      status: "recorded",
      truthClass: "b2_archive_reference",
      note:
        "PS-021 proved the full run archive was written to a real Backblaze " +
        "B2 object behind explicit, default-off gates. Archive URI and " +
        "SHA-256 are recorded in checked-in evidence.",
    },
    {
      key: "manifest_status",
      label: "Manifest status",
      status: "verified cross-source",
      truthClass: "genblaze_manifest_evidence",
      note:
        "PS-028 confirms the golden run manifest agrees across every " +
        "checked-in evidence source on run_id, campaign_id, archive URI, " +
        "archive SHA-256, and rehydrate facts.",
    },
    {
      key: "rehydrate_status",
      label: "Rehydrate status",
      status: "durable",
      truthClass: "rehydrate_proof",
      note:
        "PS-021 / PS-029 confirm the run can be rehydrated from B2 archive " +
        "content after backend memory loss, without rerunning any provider.",
    },
    {
      key: "provider_call_status",
      label: "Provider call status during rehydrate",
      status: "zero calls",
      truthClass: "rehydrate_proof",
      note:
        "Checked-in evidence records provider_calls_during_rehydrate = 0 and " +
        "no_live_provider_call_during_rehydrate = true.",
    },
    {
      key: "evidence_pack_status",
      label: "Evidence pack status",
      status: "exportable locally",
      truthClass: "local_export_contract",
      note:
        "PS-031 ships a portable Judge Evidence Pack generated locally from " +
        "checked-in evidence (pack JSON + pack README / Markdown).",
    },
    {
      key: "review_export_readiness",
      label: "Review / export readiness",
      status: "ready for review, not approved",
      truthClass: "local_export_contract",
      note:
        "The pack is generated, not approved. ProofStudio does not claim an " +
        "enterprise review / approval workflow; the pack must still be " +
        "reviewed in context.",
    },
    {
      key: "public_deployment",
      label: "Pending public deployment",
      status: "pending",
      truthClass: "public_deployment_pending",
      note:
        "The local contract is verified. The public Render deployment is not " +
        "verified yet: the new backend must be deployed and the public URL " +
        "verified end-to-end before this status changes.",
    },
  ];

// ---------------------------------------------------------------------------
// Operational phase map.
//
// The cockpit shows the run as 10 phases. Each phase carries a title, status,
// truth class, evidence source, and the next route or action. The truth
// classes are the spec-required set.
// ---------------------------------------------------------------------------

export type OperationsCockpitTruthClass =
  | "checked_in_evidence"
  | "b2_archive_reference"
  | "genblaze_manifest_evidence"
  | "rehydrate_proof"
  | "local_export_contract"
  | "inferred_product_explanation"
  | "public_deployment_pending";

export interface OperationsCockpitPhase {
  idx: number;
  key: string;
  title: string;
  status: string;
  truthClass: OperationsCockpitTruthClass;
  evidenceSource: string;
  nextRoute: string;
}

export const OPERATIONS_COCKPIT_PHASE_MAP: readonly OperationsCockpitPhase[] =
  [
    {
      idx: 1,
      key: "campaign_brief",
      title: "Campaign brief",
      status: "recorded",
      truthClass: "inferred_product_explanation",
      evidenceSource:
        "PS-002 campaign intelligence; the golden run's raw prompt packet is " +
        "not part of checked-in evidence consumed here.",
      nextRoute: "/review",
    },
    {
      idx: 2,
      key: "provider_routing_orchestration",
      title: "Provider routing / orchestration",
      status: "orchestrated",
      truthClass: "inferred_product_explanation",
      evidenceSource:
        "PS-006 / PS-007 ProviderRouter primary + fallback path; the golden " +
        "run's live attempt ledger is not part of checked-in evidence.",
      nextRoute: "/genblaze-pipeline",
    },
    {
      idx: 3,
      key: "media_generation_attempt",
      title: "Media generation attempt",
      status: "attempted",
      truthClass: "inferred_product_explanation",
      evidenceSource:
        "PS-001A / PS-007 generation attempt; the golden run's live attempt " +
        "ledger is not part of checked-in evidence.",
      nextRoute: "/genblaze-pipeline",
    },
    {
      idx: 4,
      key: "asset_manifest_capture",
      title: "Asset and manifest capture",
      status: "captured",
      truthClass: "genblaze_manifest_evidence",
      evidenceSource:
        "PS-027 Genblaze Pipeline Graph + PS-028 Manifest Verification " +
        "Panel (manifest fields agree cross-source).",
      nextRoute: "/manifest-verification",
    },
    {
      idx: 5,
      key: "backblaze_b2_archive",
      title: "Backblaze B2 archive",
      status: "archived",
      truthClass: "b2_archive_reference",
      evidenceSource:
        "PS-021 live B2 durable rehydrate smoke (archive URI + SHA-256); " +
        "PS-026 B2 Evidence Explorer.",
      nextRoute: "/b2-evidence",
    },
    {
      idx: 6,
      key: "genblaze_manifest_verification",
      title: "Genblaze manifest verification",
      status: "verified cross-source",
      truthClass: "genblaze_manifest_evidence",
      evidenceSource:
        "PS-028 confirms the golden run manifest agrees across every " +
        "checked-in evidence source.",
      nextRoute: "/manifest-verification",
    },
    {
      idx: 7,
      key: "b2_rehydrate",
      title: "B2 rehydrate",
      status: "durable",
      truthClass: "rehydrate_proof",
      evidenceSource:
        "PS-021 / PS-029 confirm rehydrate used durable B2 archive evidence " +
        "instead of a live provider rerun.",
      nextRoute: "/b2-rehydrate-comparison",
    },
    {
      idx: 8,
      key: "failure_as_proof_retry_visibility",
      title: "Failure-as-Proof / retry visibility",
      status: "placement model ready",
      truthClass: "inferred_product_explanation",
      evidenceSource:
        "PS-030 Failure-as-Proof Timeline shows where captured failures, " +
        "retries, and fallbacks would appear. No fake failures are claimed.",
      nextRoute: "/failure-timeline",
    },
    {
      idx: 9,
      key: "judge_evidence_pack_export",
      title: "Judge Evidence Pack export",
      status: "exportable locally",
      truthClass: "local_export_contract",
      evidenceSource:
        "PS-031 Judge Evidence Pack (local browser export of pack JSON + " +
        "pack README / Markdown from checked-in evidence).",
      nextRoute: "/evidence-pack",
    },
    {
      idx: 10,
      key: "review_next_action",
      title: "Review / next action",
      status: "pending review",
      truthClass: "public_deployment_pending",
      evidenceSource:
        "The pack is generated, not approved. Public deployment remains " +
        "pending; the Review + Approval Workspace is a PS-035 commitment.",
      nextRoute: "/passport/" + OPERATIONS_COCKPIT_RUN_ID,
    },
  ];

// ---------------------------------------------------------------------------
// Flight Recorder timeline.
//
// An ordered timeline of events that explains the golden run. Each event
// carries a sequence number, title, event type, status, evidence anchor,
// route link when available, and a truth class.
//
// The checked-in evidence does NOT carry real wall-clock timestamps for these
// operational events. To stay honest, each event records a timestampHonesty
// label instead of an invented timestamp:
//   - "source evidence order"
//   - "checked-in evidence order"
//   - "not timestamped in checked-in evidence"
// ---------------------------------------------------------------------------

export type OperationsCockpitFlightRecorderEventType =
  | "identity"
  | "orchestration"
  | "generation"
  | "capture"
  | "archive"
  | "verification"
  | "rehydrate"
  | "failure_visibility"
  | "export"
  | "review";

export interface OperationsCockpitFlightRecorderEvent {
  seq: number;
  key: string;
  title: string;
  eventType: OperationsCockpitFlightRecorderEventType;
  status: string;
  evidenceAnchor: string;
  routeLink: string | null;
  truthClass: OperationsCockpitTruthClass;
  timestampHonesty: string;
}

export const OPERATIONS_COCKPIT_FLIGHT_RECORDER_EVENTS: readonly OperationsCockpitFlightRecorderEvent[] =
  [
    {
      seq: 1,
      key: "golden_run_pinned",
      title: "Golden run identity pinned",
      eventType: "identity",
      status: "pinned",
      evidenceAnchor: "PS-024 golden manifest (traced to PS-021).",
      routeLink: "/passport/" + OPERATIONS_COCKPIT_RUN_ID,
      truthClass: "checked_in_evidence",
      timestampHonesty: "not timestamped in checked-in evidence",
    },
    {
      seq: 2,
      key: "provider_routing_recorded",
      title: "Provider routing / orchestration recorded",
      eventType: "orchestration",
      status: "orchestrated",
      evidenceAnchor:
        "PS-006 / PS-007 ProviderRouter primary + fallback path.",
      routeLink: "/genblaze-pipeline",
      truthClass: "inferred_product_explanation",
      timestampHonesty: "source evidence order",
    },
    {
      seq: 3,
      key: "generation_attempt_recorded",
      title: "Media generation attempt recorded",
      eventType: "generation",
      status: "attempted",
      evidenceAnchor:
        "PS-001A / PS-007 generation attempt; live attempt ledger not in " +
        "checked-in evidence.",
      routeLink: "/genblaze-pipeline",
      truthClass: "inferred_product_explanation",
      timestampHonesty: "source evidence order",
    },
    {
      seq: 4,
      key: "asset_manifest_captured",
      title: "Asset and manifest captured",
      eventType: "capture",
      status: "captured",
      evidenceAnchor:
        "PS-027 Genblaze Pipeline Graph + PS-028 Manifest Verification.",
      routeLink: "/manifest-verification",
      truthClass: "genblaze_manifest_evidence",
      timestampHonesty: "source evidence order",
    },
    {
      seq: 5,
      key: "b2_archive_written",
      title: "Backblaze B2 archive written",
      eventType: "archive",
      status: "archived",
      evidenceAnchor:
        "PS-021 live B2 durable rehydrate smoke (archive URI + SHA-256).",
      routeLink: "/b2-evidence",
      truthClass: "b2_archive_reference",
      timestampHonesty: "not timestamped in checked-in evidence",
    },
    {
      seq: 6,
      key: "genblaze_manifest_verified",
      title: "Genblaze manifest verified cross-source",
      eventType: "verification",
      status: "verified cross-source",
      evidenceAnchor:
        "PS-028 Manifest Verification Panel (fields agree across sources).",
      routeLink: "/manifest-verification",
      truthClass: "genblaze_manifest_evidence",
      timestampHonesty: "source evidence order",
    },
    {
      seq: 7,
      key: "b2_rehydrate_proven_durable",
      title: "B2 rehydrate proven durable without provider rerun",
      eventType: "rehydrate",
      status: "durable",
      evidenceAnchor:
        "PS-021 / PS-029 (provider_calls_during_rehydrate = 0).",
      routeLink: "/b2-rehydrate-comparison",
      truthClass: "rehydrate_proof",
      timestampHonesty: "not timestamped in checked-in evidence",
    },
    {
      seq: 8,
      key: "failure_visibility_surface_ready",
      title: "Failure-as-Proof / retry visibility surface ready",
      eventType: "failure_visibility",
      status: "placement model ready",
      evidenceAnchor:
        "PS-030 Failure-as-Proof Timeline. No fake failures are claimed.",
      routeLink: "/failure-timeline",
      truthClass: "inferred_product_explanation",
      timestampHonesty: "source evidence order",
    },
    {
      seq: 9,
      key: "evidence_pack_export_ready",
      title: "Judge Evidence Pack export ready",
      eventType: "export",
      status: "exportable locally",
      evidenceAnchor:
        "PS-031 Judge Evidence Pack (pack JSON + pack README / Markdown).",
      routeLink: "/evidence-pack",
      truthClass: "local_export_contract",
      timestampHonesty: "source evidence order",
    },
    {
      seq: 10,
      key: "review_next_action_pending",
      title: "Review / next action pending",
      eventType: "review",
      status: "pending review",
      evidenceAnchor:
        "Pack generated, not approved. Public deployment pending; Review + " +
        "Approval Workspace is a PS-035 commitment.",
      routeLink: null,
      truthClass: "public_deployment_pending",
      timestampHonesty: "checked-in evidence order",
    },
  ];

// ---------------------------------------------------------------------------
// Evidence graph.
//
// An accessible card / column representation (no graph library required). The
// graph carries the required nodes and the required edges so a reviewer can
// read the campaign -> run -> router -> pipeline -> asset -> archive ->
// verification -> rehydrate -> passport -> pack -> review chain at a glance.
// ---------------------------------------------------------------------------

export interface OperationsCockpitEvidenceGraphNode {
  id: string;
  label: string;
  kind: OperationsCockpitTruthClass;
  route: string | null;
}

export interface OperationsCockpitEvidenceGraphEdge {
  from: string;
  to: string;
}

export const OPERATIONS_COCKPIT_EVIDENCE_GRAPH_NODES: readonly OperationsCockpitEvidenceGraphNode[] =
  [
    {
      id: "campaign",
      label: "Campaign",
      kind: "checked_in_evidence",
      route: null,
    },
    {
      id: "run",
      label: "Run",
      kind: "checked_in_evidence",
      route: "/passport/" + OPERATIONS_COCKPIT_RUN_ID,
    },
    {
      id: "provider_router",
      label: "Provider Router",
      kind: "inferred_product_explanation",
      route: "/genblaze-pipeline",
    },
    {
      id: "genblaze_pipeline",
      label: "Genblaze Pipeline",
      kind: "genblaze_manifest_evidence",
      route: "/genblaze-pipeline",
    },
    {
      id: "asset_manifest",
      label: "Asset / Manifest",
      kind: "genblaze_manifest_evidence",
      route: "/manifest-verification",
    },
    {
      id: "b2_archive",
      label: "B2 Archive",
      kind: "b2_archive_reference",
      route: "/b2-evidence",
    },
    {
      id: "manifest_verification",
      label: "Manifest Verification",
      kind: "genblaze_manifest_evidence",
      route: "/manifest-verification",
    },
    {
      id: "b2_rehydrate",
      label: "B2 Rehydrate",
      kind: "rehydrate_proof",
      route: "/b2-rehydrate-comparison",
    },
    {
      id: "failure_as_proof_timeline",
      label: "Failure-as-Proof Timeline",
      kind: "inferred_product_explanation",
      route: "/failure-timeline",
    },
    {
      id: "judge_evidence_pack",
      label: "Judge Evidence Pack",
      kind: "local_export_contract",
      route: "/evidence-pack",
    },
    {
      id: "public_passport",
      label: "Public Passport",
      kind: "checked_in_evidence",
      route: "/passport/" + OPERATIONS_COCKPIT_RUN_ID,
    },
    {
      id: "review_next_action",
      label: "Review / Next Action",
      kind: "public_deployment_pending",
      route: null,
    },
  ];

export const OPERATIONS_COCKPIT_EVIDENCE_GRAPH_EDGES: readonly OperationsCockpitEvidenceGraphEdge[] =
  [
    { from: "campaign", to: "run" },
    { from: "run", to: "provider_router" },
    { from: "provider_router", to: "genblaze_pipeline" },
    { from: "genblaze_pipeline", to: "asset_manifest" },
    { from: "asset_manifest", to: "b2_archive" },
    { from: "asset_manifest", to: "manifest_verification" },
    { from: "b2_archive", to: "b2_rehydrate" },
    { from: "b2_rehydrate", to: "public_passport" },
    { from: "failure_as_proof_timeline", to: "judge_evidence_pack" },
    { from: "judge_evidence_pack", to: "review_next_action" },
  ];

// ---------------------------------------------------------------------------
// Action rail. The cockpit links out to every implemented proof surface plus
// the golden passport and the Judge Cockpit Home.
// ---------------------------------------------------------------------------

export interface OperationsCockpitRoute {
  href: string;
  label: string;
  tag: string;
  description: string;
}

export const OPERATIONS_COCKPIT_ACTION_ROUTES: readonly OperationsCockpitRoute[] =
  [
    {
      href: "/evidence-pack",
      label: "Open Judge Evidence Pack",
      tag: "PS-031",
      description: "Portable pack JSON + pack README / Markdown export.",
    },
    {
      href: "/failure-timeline",
      label: "Open Failure-as-Proof Timeline",
      tag: "PS-030",
      description: "Where captured failures, retries, and fallbacks appear.",
    },
    {
      href: "/b2-rehydrate-comparison",
      label: "Open B2 Rehydrate Comparison",
      tag: "PS-029",
      description: "Before / after rehydrate value cross-source.",
    },
    {
      href: "/manifest-verification",
      label: "Open Manifest Verification Panel",
      tag: "PS-028",
      description: "Cross-source manifest field consistency.",
    },
    {
      href: "/b2-evidence",
      label: "Open B2 Evidence Explorer",
      tag: "PS-026",
      description: "Verified Backblaze B2 durable evidence.",
    },
    {
      href: "/genblaze-pipeline",
      label: "Open Genblaze Pipeline Graph",
      tag: "PS-027",
      description: "Brief through durable rehydrate pipeline.",
    },
    {
      href: "/passport/" + OPERATIONS_COCKPIT_RUN_ID,
      label: "Open Golden Passport",
      tag: "PS-019 / PS-025",
      description: "Narrow public passport unlock for the golden run.",
    },
    {
      href: "/",
      label: "Back to Judge Cockpit Home",
      tag: "PS-023",
      description: "Back to the judge cockpit.",
    },
  ];

// ---------------------------------------------------------------------------
// Designer / marketer next actions.
//
// The cockpit must be useful to non-technical users. These are the next
// actions a designer or marketer would take from this cockpit.
// ---------------------------------------------------------------------------

export const OPERATIONS_COCKPIT_DESIGNER_MARKETER_NEXT_ACTIONS: readonly string[] =
  [
    "Review asset proof: open the B2 Evidence Explorer to read the archive " +
      "URI and archive SHA-256 recorded by PS-021.",
    "Open evidence pack: export the Judge Evidence Pack (pack JSON + pack " +
      "README / Markdown) locally and review it with the proof surfaces open.",
    "Inspect rehydrate proof: open the B2 Rehydrate Comparison to confirm " +
      "the rehydrate used durable B2 archive evidence with zero provider " +
      "calls.",
    "Verify manifest: open the Manifest Verification Panel to confirm the " +
      "golden run manifest agrees across every checked-in source.",
    "Prepare client handoff: assemble the Judge Evidence Pack and the proof " +
      "surface links into a readable client review bundle.",
    "Understand disclosure boundary: read the Truth Boundary and the " +
      "Limitations so the handoff never overclaims authenticity.",
    "Continue to review / approval workspace when available: the Review + " +
      "Approval Workspace is a PS-035 commitment; until then review happens " +
      "in context with the proof surfaces open.",
  ];

// ---------------------------------------------------------------------------
// Failure Theater slot.
//
// The required visible language must appear verbatim in the surface. These
// constants keep them in one place so the PS-032 smoke can verify them.
// ---------------------------------------------------------------------------

export const OPERATIONS_COCKPIT_NO_FAKE_FAILURES_LINE =
  "No fake failures are claimed.";

export const OPERATIONS_COCKPIT_ZERO_PROVIDER_CALLS_LINE =
  "For the verified golden run, rehydrate uses B2-backed evidence with zero provider calls.";

export const OPERATIONS_COCKPIT_FAILURE_THEATER_NOTE =
  "If future evidence captured a provider failure, a retry decision, a " +
  "fallback, a skipped provider, a disabled provider, or a quota block, it " +
  "would appear here as an auditable cockpit entry. The verified golden run " +
  "currently proves durable B2 rehydrate with zero provider calls; no actual " +
  "failure or fallback is claimed unless evidence proves it.";

// ---------------------------------------------------------------------------
// Truth boundary + claim boundary.
// ---------------------------------------------------------------------------

// Canonical truth boundary text for the Operations Cockpit. Written as a
// non-claim paragraph so the project's context-aware forbidden-claim scanners
// never flag the boundary terms as overclaims.
export const OPERATIONS_COCKPIT_TRUTH_BOUNDARY =
  "The Operations Cockpit summarizes checked-in evidence (PS-021, PS-024, " +
  "PS-025, PS-026, PS-027, PS-028, PS-029, PS-030, PS-031), links to B2 " +
  "archive evidence, links to Genblaze manifest evidence, shows zero provider " +
  "calls during rehydrate, helps reviewers understand workflow provenance, " +
  "and shows pending product gaps honestly. The cockpit does not prove " +
  "semantic truth, legal authenticity, C2PA authenticity, or human " +
  "authorship. The cockpit does not prove Object Lock or tamper-proof " +
  "storage. The cockpit did not fetch and hash the B2 object in the browser. " +
  "The local contract is verified; the public deployment remains pending " +
  "until the new backend is deployed and the public URL is verified " +
  "end-to-end.";

export const OPERATIONS_COCKPIT_CLAIM_BOUNDARY_ALLOWED: readonly string[] = [
  "The cockpit summarizes checked-in evidence for the golden run.",
  "The cockpit links to B2 archive evidence (archive URI and SHA-256).",
  "The cockpit links to Genblaze manifest evidence (cross-source consistency).",
  "The cockpit shows zero provider calls during rehydrate.",
  "The cockpit helps reviewers understand workflow provenance and limitations.",
  "The cockpit shows pending product gaps honestly (public deployment pending).",
];

export const OPERATIONS_COCKPIT_CLAIM_BOUNDARY_FORBIDDEN: readonly string[] = [
  "The cockpit does not prove semantic truth of the media.",
  "The cockpit does not prove legal authenticity.",
  "The cockpit does not prove human authorship.",
  "The cockpit does not prove C2PA authenticity.",
  "The cockpit does not prove Object Lock or tamper-proof storage.",
  "The cockpit did not fetch and hash the B2 object in the browser.",
  "The cockpit does not perform browser-side B2 byte verification.",
  "Public deployment has not been verified (it remains pending).",
  "The cockpit does not claim enterprise security.",
];

// ---------------------------------------------------------------------------
// Limitations. Required to be visible.
// ---------------------------------------------------------------------------

export const OPERATIONS_COCKPIT_LIMITATIONS: readonly string[] = [
  "No live provider call in PS-032: the cockpit performs no network call.",
  "No broad B2 read: the cockpit records the archive URI and SHA-256 from " +
    "checked-in evidence; it did not fetch the B2 object.",
  "No browser-side B2 byte verification: the archive SHA-256 is the value " +
    "recorded by PS-021, not a value the browser recomputed.",
  "No raw media byte inspection: the B2 archive content is a JSON run " +
    "archive, not the generated media.",
  "Public deployment pending: the local contract is verified; the public " +
    "Render deployment remains pending.",
  "Checked-in evidence only: the cockpit surfaces the golden run's checked-in " +
    "evidence, not a live operational feed.",
  "No invented failure events: the Failure Theater slot shows where captured " +
    "failures would appear; none are claimed for the golden run.",
];

// ---------------------------------------------------------------------------
// Required cockpit sections. The component renders one card per section so
// the PS-032 smoke can verify each required section is visible by id / heading.
// ---------------------------------------------------------------------------

export const OPERATIONS_COCKPIT_REQUIRED_SECTIONS: readonly string[] = [
  "Cockpit identity",
  "Run status summary",
  "Operational phase map",
  "Flight Recorder timeline",
  "Evidence graph",
  "Failure Theater",
  "Action rail",
  "Designer / marketer next actions",
  "Truth boundary",
  "Limitations",
];

// ---------------------------------------------------------------------------
// Cockpit JSON shape.
//
// buildOperationsCockpitJson() returns the deterministic cockpit JSON. No
// dynamic field is used here (the cockpit has no per-render export like the
// pack); the smoke validates the shape deterministically.
// ---------------------------------------------------------------------------

export interface OperationsCockpitJson {
  cockpit_id: string;
  cockpit_version: string;
  generated_from: string;
  run_id: string;
  campaign_id: string;
  archive_uri: string;
  archive_sha256: string;
  rehydrate_source: string;
  provider_calls_during_rehydrate: number;
  no_live_provider_call_during_rehydrate: boolean;
  public_deployment_pending: boolean;
  phase_map: readonly {
    idx: number;
    key: string;
    title: string;
    status: string;
    truth_class: OperationsCockpitTruthClass;
    evidence_source: string;
    next_route: string;
  }[];
  flight_recorder_events: readonly {
    seq: number;
    key: string;
    title: string;
    event_type: OperationsCockpitFlightRecorderEventType;
    status: string;
    evidence_anchor: string;
    route_link: string | null;
    truth_class: OperationsCockpitTruthClass;
    timestamp_honesty: string;
  }[];
  evidence_graph: {
    nodes: readonly OperationsCockpitEvidenceGraphNode[];
    edges: readonly OperationsCockpitEvidenceGraphEdge[];
  };
  action_routes: readonly { href: string; label: string; tag: string }[];
  designer_marketer_next_actions: readonly string[];
  truth_boundary: string;
  limitations: readonly string[];
  source_evidence: readonly {
    id: string;
    slice_tag: string;
    label: string;
    evidence_path: string;
  }[];
}

export function buildOperationsCockpitJson(): OperationsCockpitJson {
  return {
    cockpit_id: OPERATIONS_COCKPIT_COCKPIT_ID,
    cockpit_version: OPERATIONS_COCKPIT_COCKPIT_VERSION,
    generated_from: OPERATIONS_COCKPIT_GENERATED_FROM,
    run_id: OPERATIONS_COCKPIT_RUN_ID,
    campaign_id: OPERATIONS_COCKPIT_CAMPAIGN_ID,
    archive_uri: OPERATIONS_COCKPIT_ARCHIVE_URI,
    archive_sha256: OPERATIONS_COCKPIT_ARCHIVE_SHA256,
    rehydrate_source: OPERATIONS_COCKPIT_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      OPERATIONS_COCKPIT_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      OPERATIONS_COCKPIT_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
    public_deployment_pending: OPERATIONS_COCKPIT_PUBLIC_DEPLOYMENT_PENDING,
    phase_map: OPERATIONS_COCKPIT_PHASE_MAP.map((p) => ({
      idx: p.idx,
      key: p.key,
      title: p.title,
      status: p.status,
      truth_class: p.truthClass,
      evidence_source: p.evidenceSource,
      next_route: p.nextRoute,
    })),
    flight_recorder_events: OPERATIONS_COCKPIT_FLIGHT_RECORDER_EVENTS.map(
      (e) => ({
        seq: e.seq,
        key: e.key,
        title: e.title,
        event_type: e.eventType,
        status: e.status,
        evidence_anchor: e.evidenceAnchor,
        route_link: e.routeLink,
        truth_class: e.truthClass,
        timestamp_honesty: e.timestampHonesty,
      }),
    ),
    evidence_graph: {
      nodes: OPERATIONS_COCKPIT_EVIDENCE_GRAPH_NODES,
      edges: OPERATIONS_COCKPIT_EVIDENCE_GRAPH_EDGES,
    },
    action_routes: OPERATIONS_COCKPIT_ACTION_ROUTES.map((r) => ({
      href: r.href,
      label: r.label,
      tag: r.tag,
    })),
    designer_marketer_next_actions: OPERATIONS_COCKPIT_DESIGNER_MARKETER_NEXT_ACTIONS,
    truth_boundary: OPERATIONS_COCKPIT_TRUTH_BOUNDARY,
    limitations: OPERATIONS_COCKPIT_LIMITATIONS,
    source_evidence: OPERATIONS_COCKPIT_SOURCES.map((src) => ({
      id: src.id,
      slice_tag: src.sliceTag,
      label: src.label,
      evidence_path: src.evidencePath,
    })),
  };
}
