// PS-034 Lineage + Comparison Lab -- verified constants.
//
// This is the PS-031A hardened product module "Lineage + Comparison Lab". It
// merges Model Audition Board, Manifest Diff, Provider Swap Re-run, and
// Variant Family Tree into one lineage / comparison workspace for designers,
// marketers, reviewers, clients, and judges -- not a decorative matrix.
//
// Every golden value in this module is sourced verbatim from the same
// checked-in evidence already used by PS-021 / PS-024 / PS-025 / PS-026 /
// PS-027 / PS-028 / PS-029 / PS-030 / PS-031 / PS-032 / PS-033:
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
//   - docs/evidence/ps-032/operations-cockpit-flight-recorder-v2-smoke.json (PS-032 Operations Cockpit)
//   - docs/evidence/ps-033/provider-decision-intelligence-smoke.json   (PS-033 Provider Decision Intelligence)
//
// HONESTY RULE: the checked-in evidence records the campaign_id, run_id,
// archive_uri, archive_sha256, rehydrate_source, provider_calls_during_
// rehydrate (0), no_live_provider_call_during_rehydrate (true), and public_
// deployment_pending (true) for the single verified golden run. It does NOT
// record a second real variant, a model audition result, a quality score, a
// cost score, a winner label, an executed provider swap rerun, measured
// spend, or measured latency. PS-034 therefore does NOT invent any of those:
// it marks them "not captured in checked-in evidence" and shows where they
// would appear in a future variant family. No provider swap rerun is claimed
// for the verified golden run.
//
// The PS-034 smoke validates that every published value below matches the
// source evidence exactly AND that every source agrees on the same value. No
// value is invented here.
//
// Truth boundary: the surface summarizes checked-in lineage evidence,
// compares known manifest / proof fields, shows where future variants and
// provider swaps would appear, shows only one verified golden run (because
// that is true), helps creative teams plan comparison workflows, and shows
// pending gaps honestly. It does not prove semantic truth, legal
// authenticity, C2PA authenticity, or human authorship. It does not prove
// Object Lock or tamper-proof storage. It did not fetch and hash the B2
// object in the browser. The local contract is verified; the public
// deployment remains pending until the new backend is deployed and the
// public URL is verified end-to-end.

// Verified golden demo run_id (PS-021 -> PS-024 -> PS-025 -> PS-026 -> PS-027
// -> PS-028 -> PS-029 -> PS-030 -> PS-031 -> PS-032 -> PS-033).
export const LINEAGE_COMPARISON_LAB_RUN_ID =
  "run_89d967f9000045efa22ed4cc78cfa67f";

// Verified golden demo campaign_id.
export const LINEAGE_COMPARISON_LAB_CAMPAIGN_ID =
  "camp_bea5161faa6244079d2ee01ce445c259";

// Verified Backblaze B2 archive URI for the golden demo run (PS-021).
export const LINEAGE_COMPARISON_LAB_ARCHIVE_URI =
  "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json";

// Verified SHA-256 of the B2 archive content for the golden demo run (PS-021).
export const LINEAGE_COMPARISON_LAB_ARCHIVE_SHA256 =
  "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141";

// Rehydrate source recorded by PS-021 (durable_source = b2_rehydrated).
export const LINEAGE_COMPARISON_LAB_REHYDRATE_SOURCE = "b2_rehydrated";

// PS-021 proved zero provider calls during B2 rehydrate.
export const LINEAGE_COMPARISON_LAB_PROVIDER_CALLS_DURING_REHYDRATE = 0;

// PS-021 proved no live provider call happened during B2 rehydrate.
export const LINEAGE_COMPARISON_LAB_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE =
  true;

// PS-025: the public Render deployment is NOT verified yet. The new backend
// code must be deployed and the public URL must be verified end-to-end before
// this flag is flipped.
export const LINEAGE_COMPARISON_LAB_PUBLIC_DEPLOYMENT_PENDING = true;

// Lab identity. The lab_id is deterministic (not a random UUID): derived from
// the verified golden run_id and the lab version, so the same golden run
// always yields the same lab_id. This keeps the smoke free of brittle
// timestamp/UUID expectations.
export const LINEAGE_COMPARISON_LAB_ID =
  "lineage_comparison_lab_ps034_" + LINEAGE_COMPARISON_LAB_RUN_ID;

// Lab schema version. Bumped on any shape change.
export const LINEAGE_COMPARISON_LAB_VERSION = "1.0.0";

// Honest provenance label. Surfaced verbatim so a judge never reads "live
// provider feed" or "live B2 read" when the values are produced locally from
// checked-in evidence and documented lineage policy.
export const LINEAGE_COMPARISON_LAB_GENERATED_FROM =
  "local checked-in ProofStudio lineage evidence (PS-021, PS-024, PS-025, " +
  "PS-026, PS-027, PS-028, PS-029, PS-030, PS-031, PS-032, PS-033) plus " +
  "documented PS-031A hardened product module policy -- no server round-trip, " +
  "no B2 byte read, no provider call";

// PS-025 local contract (FastAPI TestClient against a fresh empty store
// resolving the golden run_id from checked-in evidence) is verified.
export const LINEAGE_COMPARISON_LAB_LOCAL_CONTRACT_PROOF = true;

// PS-026 unlock scope marker. Mirrors the backend
// `GOLDEN_DEMO_UNLOCK_SCOPE = "golden_demo_only"` so the surface honestly
// reports the narrow allowlist (only this single run_id resolves publicly).
export const LINEAGE_COMPARISON_LAB_UNLOCK_SCOPE = "golden_demo_only";

// The honest disclosure that only one verified golden run exists. Surfaced
// verbatim in the Lineage Summary section.
export const LINEAGE_COMPARISON_LAB_ONLY_ONE_RUN_LINE =
  "Only one verified golden run is available in checked-in evidence.";

// The honest disclosure that no provider swap rerun is claimed. Surfaced
// verbatim in the Provider Swap Re-run Planner section.
export const LINEAGE_COMPARISON_LAB_NO_PROVIDER_SWAP_LINE =
  "No provider swap rerun is claimed for the verified golden run.";

// Checked-in source evidence paths the surface cross-references.
export const LINEAGE_COMPARISON_LAB_SOURCE_PS024_MANIFEST =
  "docs/evidence/demo/golden-demo-run.json";
export const LINEAGE_COMPARISON_LAB_SOURCE_PS021_EVIDENCE =
  "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json";
export const LINEAGE_COMPARISON_LAB_SOURCE_PS025_EVIDENCE =
  "docs/evidence/ps-025/public-durable-passport-unlock-smoke.json";
export const LINEAGE_COMPARISON_LAB_SOURCE_PS026_EVIDENCE =
  "docs/evidence/ps-026/b2-evidence-explorer-smoke.json";
export const LINEAGE_COMPARISON_LAB_SOURCE_PS027_EVIDENCE =
  "docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json";
export const LINEAGE_COMPARISON_LAB_SOURCE_PS028_EVIDENCE =
  "docs/evidence/ps-028/manifest-verification-panel-smoke.json";
export const LINEAGE_COMPARISON_LAB_SOURCE_PS029_EVIDENCE =
  "docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json";
export const LINEAGE_COMPARISON_LAB_SOURCE_PS030_EVIDENCE =
  "docs/evidence/ps-030/failure-as-proof-timeline-smoke.json";
export const LINEAGE_COMPARISON_LAB_SOURCE_PS031_EVIDENCE =
  "docs/evidence/ps-031/export-campaign-pack-v2-smoke.json";
export const LINEAGE_COMPARISON_LAB_SOURCE_PS032_EVIDENCE =
  "docs/evidence/ps-032/operations-cockpit-flight-recorder-v2-smoke.json";
export const LINEAGE_COMPARISON_LAB_SOURCE_PS033_EVIDENCE =
  "docs/evidence/ps-033/provider-decision-intelligence-smoke.json";

// PS-034 references the binding implementation roadmap and the PS-031A
// hardened product module correction.
export const LINEAGE_COMPARISON_LAB_IMPLEMENTATION_ROADMAP =
  "docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md";
export const LINEAGE_COMPARISON_LAB_PS031A_ROADMAP_CORRECTION =
  "docs/roadmap/ps-031a-hardened-product-modules-correction.md";

// ---------------------------------------------------------------------------
// Required source list. The surface cross-references the checked-in lineage
// evidence (PS-021 through PS-033) plus the implementation roadmap and the
// PS-031A correction.
// ---------------------------------------------------------------------------

export type LineageComparisonLabSourceKind =
  | "golden_manifest"
  | "b2_durable_evidence"
  | "passport_evidence"
  | "explorer_evidence"
  | "pipeline_evidence"
  | "manifest_panel_evidence"
  | "rehydrate_comparison_evidence"
  | "failure_timeline_evidence"
  | "export_pack_evidence"
  | "operations_cockpit_evidence"
  | "provider_decision_evidence"
  | "roadmap_correction";

export interface LineageComparisonLabSource {
  id: string;
  label: string;
  sliceTag: string;
  kind: LineageComparisonLabSourceKind;
  evidencePath: string;
}

export const LINEAGE_COMPARISON_LAB_SOURCES: readonly LineageComparisonLabSource[] =
  [
    {
      id: "ps024",
      label: "Golden demo manifest",
      sliceTag: "PS-024",
      kind: "golden_manifest",
      evidencePath: LINEAGE_COMPARISON_LAB_SOURCE_PS024_MANIFEST,
    },
    {
      id: "ps021",
      label: "PS-021 B2 durable rehydrate evidence",
      sliceTag: "PS-021",
      kind: "b2_durable_evidence",
      evidencePath: LINEAGE_COMPARISON_LAB_SOURCE_PS021_EVIDENCE,
    },
    {
      id: "ps025",
      label: "PS-025 public durable passport evidence",
      sliceTag: "PS-025",
      kind: "passport_evidence",
      evidencePath: LINEAGE_COMPARISON_LAB_SOURCE_PS025_EVIDENCE,
    },
    {
      id: "ps026",
      label: "PS-026 B2 Evidence Explorer evidence",
      sliceTag: "PS-026",
      kind: "explorer_evidence",
      evidencePath: LINEAGE_COMPARISON_LAB_SOURCE_PS026_EVIDENCE,
    },
    {
      id: "ps027",
      label: "PS-027 Genblaze Pipeline Graph evidence",
      sliceTag: "PS-027",
      kind: "pipeline_evidence",
      evidencePath: LINEAGE_COMPARISON_LAB_SOURCE_PS027_EVIDENCE,
    },
    {
      id: "ps028",
      label: "PS-028 Manifest Verification Panel evidence",
      sliceTag: "PS-028",
      kind: "manifest_panel_evidence",
      evidencePath: LINEAGE_COMPARISON_LAB_SOURCE_PS028_EVIDENCE,
    },
    {
      id: "ps029",
      label: "PS-029 B2 Rehydrate Comparison evidence",
      sliceTag: "PS-029",
      kind: "rehydrate_comparison_evidence",
      evidencePath: LINEAGE_COMPARISON_LAB_SOURCE_PS029_EVIDENCE,
    },
    {
      id: "ps030",
      label: "PS-030 Failure-as-Proof Timeline evidence",
      sliceTag: "PS-030",
      kind: "failure_timeline_evidence",
      evidencePath: LINEAGE_COMPARISON_LAB_SOURCE_PS030_EVIDENCE,
    },
    {
      id: "ps031",
      label: "PS-031 Judge Evidence Pack evidence",
      sliceTag: "PS-031",
      kind: "export_pack_evidence",
      evidencePath: LINEAGE_COMPARISON_LAB_SOURCE_PS031_EVIDENCE,
    },
    {
      id: "ps032",
      label: "PS-032 Operations Cockpit evidence",
      sliceTag: "PS-032",
      kind: "operations_cockpit_evidence",
      evidencePath: LINEAGE_COMPARISON_LAB_SOURCE_PS032_EVIDENCE,
    },
    {
      id: "ps033",
      label: "PS-033 Provider Decision Intelligence evidence",
      sliceTag: "PS-033",
      kind: "provider_decision_evidence",
      evidencePath: LINEAGE_COMPARISON_LAB_SOURCE_PS033_EVIDENCE,
    },
    {
      id: "ps031a",
      label: "PS-031A hardened product module roadmap correction",
      sliceTag: "PS-031A",
      kind: "roadmap_correction",
      evidencePath: LINEAGE_COMPARISON_LAB_PS031A_ROADMAP_CORRECTION,
    },
  ];

// ---------------------------------------------------------------------------
// Truth classes.
//
// Each summary row, manifest diff row, audition row, and checklist item
// carries one of these classes so a reviewer can read evidence-backed facts
// vs policy vs not-captured gaps.
// ---------------------------------------------------------------------------

export type LineageComparisonLabTruthClass =
  | "checked_in_evidence"
  | "documented_policy"
  | "planned_not_captured"
  | "not_captured_in_evidence"
  | "public_deployment_pending";

// ---------------------------------------------------------------------------
// Lineage summary.
//
// A compact lineage summary so a designer / marketer / reviewer can read the
// artifact lineage state at a glance. HONESTY: only one verified golden run
// exists in checked-in evidence; the summary says so explicitly instead of
// inventing variants.
// ---------------------------------------------------------------------------

export interface LineageComparisonLabSummaryItem {
  key: string;
  label: string;
  value: string;
  truthClass: LineageComparisonLabTruthClass;
  note: string;
}

export const LINEAGE_COMPARISON_LAB_LINEAGE_SUMMARY: readonly LineageComparisonLabSummaryItem[] =
  [
    {
      key: "campaign_identity",
      label: "Campaign identity",
      value: LINEAGE_COMPARISON_LAB_CAMPAIGN_ID,
      truthClass: "checked_in_evidence",
      note:
        "The golden campaign_id is captured and agrees across PS-024 / " +
        "PS-021 / PS-025 / PS-026 / PS-027 / PS-028 / PS-029 / PS-030 / " +
        "PS-031 / PS-032 / PS-033.",
    },
    {
      key: "golden_run_identity",
      label: "Golden run identity",
      value: LINEAGE_COMPARISON_LAB_RUN_ID,
      truthClass: "checked_in_evidence",
      note:
        "The golden run_id is captured and agrees across every checked-in " +
        "lineage source.",
    },
    {
      key: "archive_status",
      label: "B2 archive status",
      value: "available (PS-021 verified)",
      truthClass: "checked_in_evidence",
      note:
        "PS-021 proved the run archive is reachable at a real Backblaze B2 " +
        "object with a recorded archive URI and SHA-256.",
    },
    {
      key: "manifest_status",
      label: "Manifest status",
      value: "pinned in checked-in evidence",
      truthClass: "checked_in_evidence",
      note:
        "The golden manifest (PS-024) pins run_id, campaign_id, archive_uri, " +
        "archive_sha256, rehydrate_source, and provider_calls_during_" +
        "rehydrate.",
    },
    {
      key: "rehydrate_status",
      label: "Rehydrate status",
      value: "b2_rehydrated, 0 provider calls",
      truthClass: "checked_in_evidence",
      note:
        "PS-021 records rehydrate_source = b2_rehydrated and " +
        "provider_calls_during_rehydrate = 0 with no live provider call.",
    },
    {
      key: "passport_status",
      label: "Public passport status",
      value: "local contract verified; public pending",
      truthClass: "public_deployment_pending",
      note:
        "PS-025 verifies the local contract (golden demo unlock only). The " +
        "public Render deployment remains pending.",
    },
    {
      key: "evidence_pack_status",
      label: "Judge evidence pack status",
      value: "exportable pack + README",
      truthClass: "checked_in_evidence",
      note:
        "PS-031 provides a portable pack JSON and pack README / Markdown " +
        "export (local browser export).",
    },
    {
      key: "comparison_readiness",
      label: "Comparison readiness",
      value: "lineage ready; variants not captured",
      truthClass: "not_captured_in_evidence",
      note:
        "There is enough lineage to trace one verified run, but not enough " +
        "captured variants to compare two real outputs side by side.",
    },
    {
      key: "variant_family_status",
      label: "Variant family status",
      value: "single verified run; future slots empty",
      truthClass: "not_captured_in_evidence",
      note:
        "No second real variant is captured in checked-in evidence. Future " +
        "variant slots are shown as not captured.",
    },
    {
      key: "provider_swap_status",
      label: "Provider swap status",
      value: "planner only; no rerun executed",
      truthClass: "planned_not_captured",
      note:
        "The provider swap rerun planner is documented policy. No provider " +
        "swap rerun is executed or claimed.",
    },
  ];

// ---------------------------------------------------------------------------
// Variant family tree.
//
// A card / tree layout over the verified lineage. Required nodes and required
// relationship labels. Empty slots are honestly labeled.
// ---------------------------------------------------------------------------

export interface LineageComparisonLabTreeNode {
  key: string;
  label: string;
  kind:
    | "campaign"
    | "golden_run"
    | "asset_manifest"
    | "b2_archive"
    | "rehydrated_evidence"
    | "public_passport"
    | "judge_evidence_pack"
    | "review_next_action"
    | "future_variant_slot";
  captured: boolean;
  identity?: string;
  note: string;
}

export interface LineageComparisonLabTreeEdge {
  key: string;
  fromKey: string;
  toKey: string;
  label:
    | "owns"
    | "generated"
    | "archived_to"
    | "rehydrated_from"
    | "exposes"
    | "exports"
    | "awaits_review";
}

export const LINEAGE_COMPARISON_LAB_VARIANT_FAMILY_NODES: readonly LineageComparisonLabTreeNode[] =
  [
    {
      key: "campaign",
      label: "Campaign",
      kind: "campaign",
      captured: true,
      identity: LINEAGE_COMPARISON_LAB_CAMPAIGN_ID,
      note: "The golden campaign owns the verified run lineage.",
    },
    {
      key: "golden_run",
      label: "Golden Run",
      kind: "golden_run",
      captured: true,
      identity: LINEAGE_COMPARISON_LAB_RUN_ID,
      note:
        "The single verified golden run pinned across all checked-in lineage " +
        "sources.",
    },
    {
      key: "asset_manifest",
      label: "Asset / Manifest",
      kind: "asset_manifest",
      captured: true,
      note:
        "The run's asset / manifest fields are pinned in the PS-024 golden " +
        "manifest. The selected provider / model for this run is not " +
        "captured in checked-in evidence.",
    },
    {
      key: "b2_archive",
      label: "B2 Archive",
      kind: "b2_archive",
      captured: true,
      identity: LINEAGE_COMPARISON_LAB_ARCHIVE_SHA256,
      note:
        "PS-021 proved the run archive is reachable at a real Backblaze B2 " +
        "object with the recorded SHA-256.",
    },
    {
      key: "rehydrated_evidence",
      label: "Rehydrated Evidence",
      kind: "rehydrated_evidence",
      captured: true,
      note:
        "PS-021 rehydrated from B2 with provider_calls_during_rehydrate = 0 " +
        "and no live provider call.",
    },
    {
      key: "public_passport",
      label: "Public Passport",
      kind: "public_passport",
      captured: true,
      note:
        "PS-025 unlocks the passport for the golden run only (golden demo " +
        "scope). Public deployment remains pending.",
    },
    {
      key: "judge_evidence_pack",
      label: "Judge Evidence Pack",
      kind: "judge_evidence_pack",
      captured: true,
      note:
        "PS-031 exports a portable pack JSON + pack README / Markdown from " +
        "the local browser.",
    },
    {
      key: "review_next_action",
      label: "Review / Next Action",
      kind: "review_next_action",
      captured: true,
      note:
        "The next action is to plan a future variant or provider swap rerun; " +
        "no second variant is captured yet.",
    },
    {
      key: "future_variant_slot_1",
      label: "future variant slot",
      kind: "future_variant_slot",
      captured: false,
      note: "not captured in checked-in evidence",
    },
    {
      key: "future_variant_slot_2",
      label: "future variant slot",
      kind: "future_variant_slot",
      captured: false,
      note: "not captured in checked-in evidence",
    },
  ];

export const LINEAGE_COMPARISON_LAB_VARIANT_FAMILY_EDGES: readonly LineageComparisonLabTreeEdge[] =
  [
    { key: "e1", fromKey: "campaign", toKey: "golden_run", label: "owns" },
    {
      key: "e2",
      fromKey: "golden_run",
      toKey: "asset_manifest",
      label: "generated",
    },
    {
      key: "e3",
      fromKey: "asset_manifest",
      toKey: "b2_archive",
      label: "archived_to",
    },
    {
      key: "e4",
      fromKey: "rehydrated_evidence",
      toKey: "b2_archive",
      label: "rehydrated_from",
    },
    {
      key: "e5",
      fromKey: "public_passport",
      toKey: "rehydrated_evidence",
      label: "exposes",
    },
    {
      key: "e6",
      fromKey: "judge_evidence_pack",
      toKey: "rehydrated_evidence",
      label: "exports",
    },
    {
      key: "e7",
      fromKey: "review_next_action",
      toKey: "judge_evidence_pack",
      label: "awaits_review",
    },
  ];

// ---------------------------------------------------------------------------
// Manifest diff.
//
// Compares the known golden manifest / evidence fields (left / source) against
// the rehydrated / archive proof fields (right / comparison) where available.
// Each row carries a match status, evidence source, and truth class. If a
// field cannot be compared because one side is not captured, the row shows
// the literal "not captured in checked-in evidence".
// ---------------------------------------------------------------------------

export const LINEAGE_COMPARISON_LAB_NOT_CAPTURED_LABEL =
  "not captured in checked-in evidence";

export type LineageComparisonLabMatchStatus =
  | "match"
  | "partial"
  | "not_captured";

export interface LineageComparisonLabManifestDiffRow {
  key: string;
  field: string;
  leftSource: string;
  leftValue: string;
  rightComparison: string;
  rightValue: string;
  matchStatus: LineageComparisonLabMatchStatus;
  evidenceSource: string;
  truthClass: LineageComparisonLabTruthClass;
}

export const LINEAGE_COMPARISON_LAB_MANIFEST_DIFF: readonly LineageComparisonLabManifestDiffRow[] =
  [
    {
      key: "run_id",
      field: "run_id",
      leftSource: "PS-024 golden manifest",
      leftValue: LINEAGE_COMPARISON_LAB_RUN_ID,
      rightComparison: "PS-021 durable rehydrate",
      rightValue: LINEAGE_COMPARISON_LAB_RUN_ID,
      matchStatus: "match",
      evidenceSource:
        "docs/evidence/demo/golden-demo-run.json vs " +
        "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json",
      truthClass: "checked_in_evidence",
    },
    {
      key: "campaign_id",
      field: "campaign_id",
      leftSource: "PS-024 golden manifest",
      leftValue: LINEAGE_COMPARISON_LAB_CAMPAIGN_ID,
      rightComparison: "PS-021 durable rehydrate",
      rightValue: LINEAGE_COMPARISON_LAB_CAMPAIGN_ID,
      matchStatus: "match",
      evidenceSource:
        "docs/evidence/demo/golden-demo-run.json vs " +
        "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json",
      truthClass: "checked_in_evidence",
    },
    {
      key: "archive_uri",
      field: "archive_uri",
      leftSource: "PS-024 golden manifest",
      leftValue: LINEAGE_COMPARISON_LAB_ARCHIVE_URI,
      rightComparison: "PS-021 durable rehydrate",
      rightValue: LINEAGE_COMPARISON_LAB_ARCHIVE_URI,
      matchStatus: "match",
      evidenceSource:
        "docs/evidence/demo/golden-demo-run.json vs " +
        "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json",
      truthClass: "checked_in_evidence",
    },
    {
      key: "archive_sha256",
      field: "archive_sha256",
      leftSource: "PS-024 golden manifest",
      leftValue: LINEAGE_COMPARISON_LAB_ARCHIVE_SHA256,
      rightComparison: "PS-021 durable rehydrate",
      rightValue: LINEAGE_COMPARISON_LAB_ARCHIVE_SHA256,
      matchStatus: "match",
      evidenceSource:
        "docs/evidence/demo/golden-demo-run.json vs " +
        "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json",
      truthClass: "checked_in_evidence",
    },
    {
      key: "rehydrate_source",
      field: "rehydrate_source",
      leftSource: "PS-024 golden manifest",
      leftValue: LINEAGE_COMPARISON_LAB_REHYDRATE_SOURCE,
      rightComparison: "PS-021 durable_source",
      rightValue: LINEAGE_COMPARISON_LAB_REHYDRATE_SOURCE,
      matchStatus: "match",
      evidenceSource:
        "docs/evidence/demo/golden-demo-run.json (rehydrate_source) vs " +
        "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json " +
        "(durable_source)",
      truthClass: "checked_in_evidence",
    },
    {
      key: "provider_calls_during_rehydrate",
      field: "provider_calls_during_rehydrate",
      leftSource: "PS-024 golden manifest",
      leftValue: String(
        LINEAGE_COMPARISON_LAB_PROVIDER_CALLS_DURING_REHYDRATE,
      ),
      rightComparison: "PS-021 durable rehydrate",
      rightValue: String(
        LINEAGE_COMPARISON_LAB_PROVIDER_CALLS_DURING_REHYDRATE,
      ),
      matchStatus: "match",
      evidenceSource:
        "docs/evidence/demo/golden-demo-run.json vs " +
        "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json",
      truthClass: "checked_in_evidence",
    },
    {
      key: "no_live_provider_call_during_rehydrate",
      field: "no_live_provider_call_during_rehydrate",
      leftSource: "PS-024 golden manifest",
      leftValue: String(
        LINEAGE_COMPARISON_LAB_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
      ),
      rightComparison: "PS-021 durable rehydrate",
      rightValue: String(
        LINEAGE_COMPARISON_LAB_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
      ),
      matchStatus: "match",
      evidenceSource:
        "docs/evidence/demo/golden-demo-run.json vs " +
        "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json",
      truthClass: "checked_in_evidence",
    },
    {
      key: "public_deployment_pending",
      field: "public_deployment_pending",
      leftSource: "PS-024 golden manifest",
      leftValue: LINEAGE_COMPARISON_LAB_NOT_CAPTURED_LABEL,
      rightComparison: "PS-025 passport evidence",
      rightValue: String(LINEAGE_COMPARISON_LAB_PUBLIC_DEPLOYMENT_PENDING),
      matchStatus: "not_captured",
      evidenceSource:
        "field not present in docs/evidence/demo/golden-demo-run.json; " +
        "captured as true in " +
        "docs/evidence/ps-025/public-durable-passport-unlock-smoke.json",
      truthClass: "public_deployment_pending",
    },
  ];

// ---------------------------------------------------------------------------
// Model audition board.
//
// Shows how multiple model candidates would be compared. The golden run row
// discloses that the selected provider / model is not captured. Future slots
// are honestly marked as not run. No model scores, quality scores, cost
// scores, or winner labels are invented.
// ---------------------------------------------------------------------------

export interface LineageComparisonLabAuditionRow {
  key: string;
  candidate: string;
  providerModelRole: string;
  modality: string;
  evidenceStatus: string;
  qualityReviewStatus: string;
  costTimeStatus: string;
  proofStatus: string;
  decision: string;
  truthClass: LineageComparisonLabTruthClass;
}

export const LINEAGE_COMPARISON_LAB_SELECTED_PROVIDER_NOT_CAPTURED =
  "selected provider/model not captured in checked-in evidence";

export const LINEAGE_COMPARISON_LAB_AUDITION_SLOT_NOT_RUN =
  "audition slot not run";

export const LINEAGE_COMPARISON_LAB_MODEL_AUDITION_BOARD: readonly LineageComparisonLabAuditionRow[] =
  [
    {
      key: "golden_run_candidate",
      candidate: "Golden run candidate",
      providerModelRole: LINEAGE_COMPARISON_LAB_SELECTED_PROVIDER_NOT_CAPTURED,
      modality: "not captured in checked-in evidence",
      evidenceStatus: "lineage verified; selected model not captured",
      qualityReviewStatus: "not captured in checked-in evidence",
      costTimeStatus: "not captured in checked-in evidence",
      proofStatus: "B2 archive + rehydrate verified (PS-021)",
      decision: "no winner label assigned",
      truthClass: "not_captured_in_evidence",
    },
    {
      key: "audition_slot_a",
      candidate: "Audition slot A",
      providerModelRole: LINEAGE_COMPARISON_LAB_AUDITION_SLOT_NOT_RUN,
      modality: "not captured in checked-in evidence",
      evidenceStatus: LINEAGE_COMPARISON_LAB_AUDITION_SLOT_NOT_RUN,
      qualityReviewStatus: "not captured in checked-in evidence",
      costTimeStatus: "not captured in checked-in evidence",
      proofStatus: "not captured in checked-in evidence",
      decision: "not captured in checked-in evidence",
      truthClass: "planned_not_captured",
    },
    {
      key: "audition_slot_b",
      candidate: "Audition slot B",
      providerModelRole: LINEAGE_COMPARISON_LAB_AUDITION_SLOT_NOT_RUN,
      modality: "not captured in checked-in evidence",
      evidenceStatus: LINEAGE_COMPARISON_LAB_AUDITION_SLOT_NOT_RUN,
      qualityReviewStatus: "not captured in checked-in evidence",
      costTimeStatus: "not captured in checked-in evidence",
      proofStatus: "not captured in checked-in evidence",
      decision: "not captured in checked-in evidence",
      truthClass: "planned_not_captured",
    },
  ];

// ---------------------------------------------------------------------------
// Provider swap re-run planner.
//
// A planner (documented policy steps) for rerunning the same brief with a
// different provider. This is NOT an executed rerun. The exact no-swap line
// is surfaced verbatim.
// ---------------------------------------------------------------------------

export interface LineageComparisonLabSwapStep {
  order: number;
  key: string;
  step: string;
  detail: string;
  truthClass: LineageComparisonLabTruthClass;
}

export const LINEAGE_COMPARISON_LAB_PROVIDER_SWAP_RERUN_PLANNER: readonly LineageComparisonLabSwapStep[] =
  [
    {
      order: 1,
      key: "keep_campaign_id",
      step: "keep campaign_id",
      detail: "Reuse the existing campaign_id so the new run stays in family.",
      truthClass: "documented_policy",
    },
    {
      order: 2,
      key: "create_new_run_id",
      step: "create new run_id",
      detail: "Mint a new run_id so the rerun is a distinct lineage node.",
      truthClass: "documented_policy",
    },
    {
      order: 3,
      key: "preserve_prompt",
      step: "preserve source prompt/brief if available",
      detail:
        "Keep the source prompt / brief so the two runs are comparable; " +
        "not captured in checked-in evidence for the golden run.",
      truthClass: "planned_not_captured",
    },
    {
      order: 4,
      key: "route_decision_policy",
      step: "route through provider decision policy",
      detail:
        "Route through the Provider Decision Intelligence policy (PS-033) " +
        "to choose a different documented provider path.",
      truthClass: "documented_policy",
    },
    {
      order: 5,
      key: "capture_asset_manifest",
      step: "capture new asset/manifest",
      detail: "Capture the new asset and manifest for the rerun.",
      truthClass: "documented_policy",
    },
    {
      order: 6,
      key: "archive_to_b2",
      step: "archive to B2",
      detail:
        "Archive the rerun to Backblaze B2 and record a new archive URI / " +
        "SHA-256.",
      truthClass: "documented_policy",
    },
    {
      order: 7,
      key: "compare_manifest_diff",
      step: "compare manifest diff",
      detail:
        "Diff the new manifest against the golden manifest in this lab.",
      truthClass: "documented_policy",
    },
    {
      order: 8,
      key: "attach_variant_family",
      step: "attach to variant family",
      detail:
        "Attach the rerun to the variant family tree as a new variant node.",
      truthClass: "documented_policy",
    },
    {
      order: 9,
      key: "update_review_export",
      step: "update review/export state",
      detail:
        "Update the review / next action and the Judge Evidence Pack export.",
      truthClass: "documented_policy",
    },
  ];

// ---------------------------------------------------------------------------
// Comparison readiness checklist.
//
// Shows whether the system has enough evidence to compare variants. Missing
// items are marked honestly.
// ---------------------------------------------------------------------------

export interface LineageComparisonLabChecklistItem {
  key: string;
  label: string;
  present: boolean;
  truthClass: LineageComparisonLabTruthClass;
  note: string;
}

export const LINEAGE_COMPARISON_LAB_COMPARISON_READINESS_CHECKLIST: readonly LineageComparisonLabChecklistItem[] =
  [
    {
      key: "golden_run_exists",
      label: "golden run exists",
      present: true,
      truthClass: "checked_in_evidence",
      note: "The verified golden run_id is pinned across all lineage sources.",
    },
    {
      key: "b2_archive_exists",
      label: "B2 archive exists",
      present: true,
      truthClass: "checked_in_evidence",
      note: "PS-021 proved the B2 archive is reachable.",
    },
    {
      key: "manifest_hash_exists",
      label: "manifest hash exists",
      present: true,
      truthClass: "checked_in_evidence",
      note: "archive_sha256 is captured and agrees across sources.",
    },
    {
      key: "rehydrate_proof_exists",
      label: "rehydrate proof exists",
      present: true,
      truthClass: "checked_in_evidence",
      note: "PS-021 records b2_rehydrated with 0 provider calls.",
    },
    {
      key: "provider_calls_captured",
      label: "provider calls during rehydrate captured",
      present: true,
      truthClass: "checked_in_evidence",
      note: "provider_calls_during_rehydrate = 0 is captured.",
    },
    {
      key: "evidence_pack_exists",
      label: "evidence pack exists",
      present: true,
      truthClass: "checked_in_evidence",
      note: "PS-031 provides the pack JSON + README export.",
    },
    {
      key: "operations_cockpit_exists",
      label: "operations cockpit exists",
      present: true,
      truthClass: "checked_in_evidence",
      note: "PS-032 provides the Operations Cockpit / Flight Recorder v2.",
    },
    {
      key: "provider_decision_policy_exists",
      label: "provider decision policy exists",
      present: true,
      truthClass: "checked_in_evidence",
      note: "PS-033 provides the Provider Decision Intelligence surface.",
    },
    {
      key: "second_real_variant_exists",
      label: "second real variant exists",
      present: false,
      truthClass: "not_captured_in_evidence",
      note:
        "No second real variant is captured in checked-in evidence. Future " +
        "variant slots are empty.",
    },
    {
      key: "model_scores_captured",
      label: "model scores captured",
      present: false,
      truthClass: "not_captured_in_evidence",
      note: "No model scores are captured; none are invented.",
    },
    {
      key: "measured_cost_captured",
      label: "measured cost captured",
      present: false,
      truthClass: "not_captured_in_evidence",
      note: "No measured cost is captured; cost classes are policy only.",
    },
    {
      key: "measured_latency_captured",
      label: "measured latency captured",
      present: false,
      truthClass: "not_captured_in_evidence",
      note: "No measured latency is captured; none are invented.",
    },
    {
      key: "review_decision_captured",
      label: "review decision captured",
      present: false,
      truthClass: "not_captured_in_evidence",
      note:
        "No review decision is captured for the golden run (Review + " +
        "Approval Workspace is PS-035).",
    },
  ];

// ---------------------------------------------------------------------------
// Designer / marketer interpretation.
//
// Plain-language explanations for non-technical users.
// ---------------------------------------------------------------------------

export interface LineageComparisonLabDesignerMarketerInterpretation {
  whyLineageMatters: string;
  whyComparingVariantsHelpsCampaigns: string;
  whyManifestDiffMatters: string;
  howProviderSwapsHelpCreativeTeams: string;
  whenToRerunWithAnotherModel: string;
  whenToExportTheEvidencePack: string;
  whyMissingVariantDataIsNotAFailure: string;
}

export const LINEAGE_COMPARISON_LAB_DESIGNER_MARKETER_INTERPRETATION: LineageComparisonLabDesignerMarketerInterpretation =
  {
    whyLineageMatters:
      "Lineage matters because it shows how a campaign, run, manifest, B2 " +
      "archive, rehydrated evidence, public passport, and judge evidence pack " +
      "connect. A client or judge can trace one artifact back to its origin " +
      "without trusting a single opaque output.",
    whyComparingVariantsHelpsCampaigns:
      "Comparing variants helps a creative team pick the strongest output " +
      "instead of committing to the first generation. The Lab shows where " +
      "future variants would sit so the comparison workflow is ready the " +
      "moment a second run is captured.",
    whyManifestDiffMatters:
      "The manifest diff matters because it proves continuity: the run_id, " +
      "archive URI, and archive SHA-256 agree between the golden manifest and " +
      "the rehydrated archive proof. A reviewer can see the chain did not " +
      "silently change.",
    howProviderSwapsHelpCreativeTeams:
      "Provider swaps help a creative team test how a different model or " +
      "provider changes the same brief. The swap planner is a documented " +
      "workflow (keep the campaign, mint a new run, archive, diff, attach to " +
      "family) -- it is not an executed rerun yet.",
    whenToRerunWithAnotherModel:
      "Rerun with another model when the first output is acceptable but you " +
      "want to compare style, fidelity, or provider behavior. The Lab marks " +
      "these future slots honestly so a team never mistakes a planned slot " +
      "for a real result.",
    whenToExportTheEvidencePack:
      "Export the Judge Evidence Pack when a client or judge needs a " +
      "portable, readable proof summary (run identity, B2 archive, manifest, " +
      "rehydrate, limitations) instead of opening every surface.",
    whyMissingVariantDataIsNotAFailure:
      "Missing variant data is not a failure: it is an honest gap. ProofStudio " +
      "shows where a second variant, model score, or provider swap rerun " +
      "would appear instead of inventing results. Honesty about gaps is what " +
      "makes the lineage trustworthy.",
  };

// ---------------------------------------------------------------------------
// Action rail.
//
// The surface links out to every implemented proof surface plus the golden
// passport and the Judge Cockpit Home.
// ---------------------------------------------------------------------------

export interface LineageComparisonLabRoute {
  href: string;
  label: string;
  tag: string;
  description: string;
}

export const LINEAGE_COMPARISON_LAB_ACTION_ROUTES: readonly LineageComparisonLabRoute[] =
  [
    {
      href: "/provider-decision-intelligence",
      label: "Open Provider Decision Intelligence",
      tag: "PS-033",
      description: "Provider decision policy that a swap rerun would route through.",
    },
    {
      href: "/operations-cockpit",
      label: "Open Operations Cockpit",
      tag: "PS-032",
      description: "Operating cockpit / flight recorder over the golden run.",
    },
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
      href: "/passport/" + LINEAGE_COMPARISON_LAB_RUN_ID,
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
// Truth boundary + claim boundary.
// ---------------------------------------------------------------------------

export const LINEAGE_COMPARISON_LAB_TRUTH_BOUNDARY =
  "The Lineage + Comparison Lab summarizes checked-in lineage evidence " +
  "(PS-021, PS-024, PS-025, PS-026, PS-027, PS-028, PS-029, PS-030, PS-031, " +
  "PS-032, PS-033), compares known manifest / proof fields, shows where " +
  "future variants and provider swaps would appear, shows only one verified " +
  "golden run (because that is true), helps creative teams plan comparison " +
  "workflows, and shows pending gaps honestly. The surface does not prove " +
  "semantic truth, legal authenticity, C2PA authenticity, or human " +
  "authorship. The surface does not prove Object Lock or tamper-proof " +
  "storage. The surface did not fetch and hash the B2 object in the browser. " +
  "The local contract is verified; the public deployment remains pending " +
  "until the new backend is deployed and the public URL is verified " +
  "end-to-end.";

export const LINEAGE_COMPARISON_LAB_CLAIM_BOUNDARY_ALLOWED: readonly string[] =
  [
    "The surface summarizes checked-in lineage evidence.",
    "The surface compares known manifest / proof fields.",
    "The surface shows where future variants and provider swaps would appear.",
    "The surface shows only one verified golden run (because that is true).",
    "The surface helps creative teams plan comparison workflows.",
    "The surface shows pending gaps honestly.",
  ];

export const LINEAGE_COMPARISON_LAB_CLAIM_BOUNDARY_FORBIDDEN: readonly string[] =
  [
    "The surface does not claim multiple real variants unless captured.",
    "The surface does not claim completed provider swap reruns unless captured.",
    "The surface does not claim model audition results unless captured.",
    "The surface does not claim actual quality scores unless captured.",
    "The surface does not claim actual winner labels unless captured.",
    "The surface does not claim actual spend unless captured in evidence.",
    "The surface does not claim actual latency unless captured in evidence.",
    "The surface does not prove semantic truth, legal authenticity, C2PA " +
      "authenticity, or human authorship.",
    "The surface does not prove Object Lock or tamper-proof storage.",
    "The surface did not fetch and hash the B2 object in the browser.",
    "Public deployment has not been verified (it remains pending).",
    "The surface does not claim enterprise security.",
  ];

// ---------------------------------------------------------------------------
// Limitations. Required to be visible.
// ---------------------------------------------------------------------------

export const LINEAGE_COMPARISON_LAB_LIMITATIONS: readonly string[] = [
  "No live provider call in PS-034: the surface performs no network call.",
  "No provider swap rerun executed: the planner is documented policy only.",
  "No second real variant captured unless evidence exists: none exists yet.",
  "No model score captured unless evidence exists: none exists yet.",
  "No broad B2 read: the surface records the archive URI and SHA-256 from " +
    "checked-in evidence; it did not fetch the B2 object.",
  "No live pricing API: cost classes are policy, not measured billing.",
  "No measured billing unless present in checked-in evidence: measured cost " +
    "is not captured for the golden run.",
  "No measured latency unless present in checked-in evidence.",
  "Public deployment pending: the local contract is verified; the public " +
    "Render deployment remains pending.",
  "Checked-in evidence and documented policy only: the surface does not " +
    "read a live provider feed.",
  "No invented variant events: future variant slots and audition slots are " +
    "honestly marked as not captured.",
];

// ---------------------------------------------------------------------------
// Required lab sections (headings the component must render).
// ---------------------------------------------------------------------------

export const LINEAGE_COMPARISON_LAB_REQUIRED_SECTIONS: readonly string[] = [
  "Lab Identity",
  "Lineage Summary",
  "Variant Family Tree",
  "Manifest Diff",
  "Model Audition Board",
  "Provider Swap Re-run Planner",
  "Comparison Readiness Checklist",
  "Designer / Marketer Interpretation",
  "Action Rail",
  "Truth Boundary",
  "Limitations",
];

// ---------------------------------------------------------------------------
// Lab JSON shape.
//
// buildLineageComparisonLabJson() returns the deterministic lab JSON the
// surface summarizes. No dynamic field is used here.
// ---------------------------------------------------------------------------

export interface LineageComparisonLabJson {
  lab_id: string;
  lab_version: string;
  generated_from: string;
  run_id: string;
  campaign_id: string;
  archive_uri: string;
  archive_sha256: string;
  rehydrate_source: string;
  provider_calls_during_rehydrate: number;
  no_live_provider_call_during_rehydrate: boolean;
  public_deployment_pending: boolean;
  lineage_summary: readonly {
    key: string;
    label: string;
    value: string;
    truth_class: LineageComparisonLabTruthClass;
    note: string;
  }[];
  variant_family_tree: {
    nodes: readonly {
      key: string;
      label: string;
      kind: string;
      captured: boolean;
      identity?: string;
      note: string;
    }[];
    edges: readonly {
      key: string;
      from_key: string;
      to_key: string;
      label: string;
    }[];
  };
  manifest_diff: readonly {
    key: string;
    field: string;
    left_source: string;
    left_value: string;
    right_comparison: string;
    right_value: string;
    match_status: string;
    evidence_source: string;
    truth_class: LineageComparisonLabTruthClass;
  }[];
  model_audition_board: readonly {
    key: string;
    candidate: string;
    provider_model_role: string;
    modality: string;
    evidence_status: string;
    quality_review_status: string;
    cost_time_status: string;
    proof_status: string;
    decision: string;
    truth_class: LineageComparisonLabTruthClass;
  }[];
  provider_swap_rerun_planner: {
    no_swap_line: string;
    steps: readonly {
      order: number;
      key: string;
      step: string;
      detail: string;
      truth_class: LineageComparisonLabTruthClass;
    }[];
  };
  comparison_readiness_checklist: readonly {
    key: string;
    label: string;
    present: boolean;
    truth_class: LineageComparisonLabTruthClass;
    note: string;
  }[];
  designer_marketer_interpretation: LineageComparisonLabDesignerMarketerInterpretation;
  action_routes: readonly { href: string; label: string; tag: string }[];
  truth_boundary: string;
  limitations: readonly string[];
  source_evidence: readonly {
    id: string;
    slice_tag: string;
    label: string;
    evidence_path: string;
  }[];
}

export function buildLineageComparisonLabJson(): LineageComparisonLabJson {
  return {
    lab_id: LINEAGE_COMPARISON_LAB_ID,
    lab_version: LINEAGE_COMPARISON_LAB_VERSION,
    generated_from: LINEAGE_COMPARISON_LAB_GENERATED_FROM,
    run_id: LINEAGE_COMPARISON_LAB_RUN_ID,
    campaign_id: LINEAGE_COMPARISON_LAB_CAMPAIGN_ID,
    archive_uri: LINEAGE_COMPARISON_LAB_ARCHIVE_URI,
    archive_sha256: LINEAGE_COMPARISON_LAB_ARCHIVE_SHA256,
    rehydrate_source: LINEAGE_COMPARISON_LAB_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      LINEAGE_COMPARISON_LAB_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      LINEAGE_COMPARISON_LAB_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
    public_deployment_pending:
      LINEAGE_COMPARISON_LAB_PUBLIC_DEPLOYMENT_PENDING,
    lineage_summary: LINEAGE_COMPARISON_LAB_LINEAGE_SUMMARY.map((s) => ({
      key: s.key,
      label: s.label,
      value: s.value,
      truth_class: s.truthClass,
      note: s.note,
    })),
    variant_family_tree: {
      nodes: LINEAGE_COMPARISON_LAB_VARIANT_FAMILY_NODES.map((n) => ({
        key: n.key,
        label: n.label,
        kind: n.kind,
        captured: n.captured,
        identity: n.identity,
        note: n.note,
      })),
      edges: LINEAGE_COMPARISON_LAB_VARIANT_FAMILY_EDGES.map((e) => ({
        key: e.key,
        from_key: e.fromKey,
        to_key: e.toKey,
        label: e.label,
      })),
    },
    manifest_diff: LINEAGE_COMPARISON_LAB_MANIFEST_DIFF.map((r) => ({
      key: r.key,
      field: r.field,
      left_source: r.leftSource,
      left_value: r.leftValue,
      right_comparison: r.rightComparison,
      right_value: r.rightValue,
      match_status: r.matchStatus,
      evidence_source: r.evidenceSource,
      truth_class: r.truthClass,
    })),
    model_audition_board: LINEAGE_COMPARISON_LAB_MODEL_AUDITION_BOARD.map(
      (r) => ({
        key: r.key,
        candidate: r.candidate,
        provider_model_role: r.providerModelRole,
        modality: r.modality,
        evidence_status: r.evidenceStatus,
        quality_review_status: r.qualityReviewStatus,
        cost_time_status: r.costTimeStatus,
        proof_status: r.proofStatus,
        decision: r.decision,
        truth_class: r.truthClass,
      }),
    ),
    provider_swap_rerun_planner: {
      no_swap_line: LINEAGE_COMPARISON_LAB_NO_PROVIDER_SWAP_LINE,
      steps: LINEAGE_COMPARISON_LAB_PROVIDER_SWAP_RERUN_PLANNER.map((s) => ({
        order: s.order,
        key: s.key,
        step: s.step,
        detail: s.detail,
        truth_class: s.truthClass,
      })),
    },
    comparison_readiness_checklist:
      LINEAGE_COMPARISON_LAB_COMPARISON_READINESS_CHECKLIST.map((c) => ({
        key: c.key,
        label: c.label,
        present: c.present,
        truth_class: c.truthClass,
        note: c.note,
      })),
    designer_marketer_interpretation:
      LINEAGE_COMPARISON_LAB_DESIGNER_MARKETER_INTERPRETATION,
    action_routes: LINEAGE_COMPARISON_LAB_ACTION_ROUTES.map((r) => ({
      href: r.href,
      label: r.label,
      tag: r.tag,
    })),
    truth_boundary: LINEAGE_COMPARISON_LAB_TRUTH_BOUNDARY,
    limitations: LINEAGE_COMPARISON_LAB_LIMITATIONS,
    source_evidence: LINEAGE_COMPARISON_LAB_SOURCES.map((src) => ({
      id: src.id,
      slice_tag: src.sliceTag,
      label: src.label,
      evidence_path: src.evidencePath,
    })),
  };
}
