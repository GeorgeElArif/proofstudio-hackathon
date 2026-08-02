// PS-033 Provider Decision Intelligence -- verified constants.
//
// This is the PS-031A hardened product module "Provider Decision Intelligence".
// It merges Credit-Aware Provider Router, Provider Budget Modes, Cost and Time
// Ledger, Why This Provider, Emergency No-Key Mode, and quota / paid / free
// risk explanation into one provider decision surface for designers,
// marketers, reviewers, clients, and judges -- not a decorative provider
// matrix.
//
// Every golden value in this module is sourced verbatim from the same
// checked-in evidence already used by PS-021 / PS-024 / PS-025 / PS-026 /
// PS-027 / PS-028 / PS-029 / PS-030 / PS-031 / PS-032:
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
//
// Provider option facts are sourced from the documented provider / model
// inventory (docs/submission/provider-model-inventory.md) and the PS-005
// Pollinations fallback proof (docs/ps-005-pollinations-fallback-proof.md).
// Provider code that backs these options lives in
// src/proofstudio/providers/router.py and src/proofstudio/providers/types.py
// (ProviderRouter + ProviderAttempt + normalized status vocabulary), plus the
// live provider adapters live_pollinations.py / live_cloudflare.py.
//
// HONESTY RULE: the PS-021 durable rehydrate smoke (the evidence behind the
// golden run) records the archive URI / SHA-256 / rehydrate source and zero
// provider calls during rehydrate, but it does NOT record the golden run's
// selected provider, selected model, budget mode, attempt count, fallback
// count, measured cost, or measured latency. PS-033 therefore does NOT invent
// those values: it marks them "not captured in checked-in evidence" and
// explains the documented provider options and routing policies instead. No
// fake provider failure, retry, or fallback event is claimed.
//
// The PS-033 smoke validates that every published value below matches the
// source evidence exactly AND that every source agrees on the same value. No
// value is invented here.
//
// Truth boundary: the surface summarizes checked-in evidence and documented
// routing policy, explains provider decision tradeoffs, shows cost / budget
// classes as policy unless measured evidence exists, shows zero provider calls
// during rehydrate, helps marketers understand routing choices, and shows
// pending gaps honestly. It does not prove semantic truth, legal authenticity,
// C2PA authenticity, or human authorship. It does not prove Object Lock or
// tamper-proof storage. It did not fetch and hash the B2 object in the browser.
// The local contract is verified; the public deployment remains pending until
// the new backend is deployed and the public URL is verified end-to-end.

// Verified golden demo run_id (PS-021 -> PS-024 -> PS-025 -> PS-026 -> PS-027
// -> PS-028 -> PS-029 -> PS-030 -> PS-031 -> PS-032).
export const PROVIDER_DECISION_INTELLIGENCE_RUN_ID =
  "run_89d967f9000045efa22ed4cc78cfa67f";

// Verified golden demo campaign_id.
export const PROVIDER_DECISION_INTELLIGENCE_CAMPAIGN_ID =
  "camp_bea5161faa6244079d2ee01ce445c259";

// Verified Backblaze B2 archive URI for the golden demo run (PS-021).
export const PROVIDER_DECISION_INTELLIGENCE_ARCHIVE_URI =
  "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json";

// Verified SHA-256 of the B2 archive content for the golden demo run (PS-021).
export const PROVIDER_DECISION_INTELLIGENCE_ARCHIVE_SHA256 =
  "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141";

// Rehydrate source recorded by PS-021 (durable_source = b2_rehydrated).
export const PROVIDER_DECISION_INTELLIGENCE_REHYDRATE_SOURCE = "b2_rehydrated";

// PS-021 proved zero provider calls during B2 rehydrate.
export const PROVIDER_DECISION_INTELLIGENCE_PROVIDER_CALLS_DURING_REHYDRATE = 0;

// PS-021 proved no live provider call happened during B2 rehydrate.
export const PROVIDER_DECISION_INTELLIGENCE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE = true;

// Intelligence identity. The intelligence_id is deterministic (not a random
// UUID): derived from the verified golden run_id and the surface version, so
// the same golden run always yields the same intelligence_id. This keeps the
// smoke free of brittle timestamp/UUID expectations.
export const PROVIDER_DECISION_INTELLIGENCE_INTELLIGENCE_ID =
  "provider_decision_intelligence_ps033_" +
  PROVIDER_DECISION_INTELLIGENCE_RUN_ID;

// Intelligence schema version. Bumped on any shape change.
export const PROVIDER_DECISION_INTELLIGENCE_VERSION = "1.0.0";

// Honest provenance label. Surfaced verbatim so a judge never reads "live
// provider feed" when the values are produced locally from checked-in
// evidence and documented routing policy.
export const PROVIDER_DECISION_INTELLIGENCE_GENERATED_FROM =
  "local checked-in ProofStudio evidence (PS-021, PS-024, PS-025, PS-026, " +
  "PS-027, PS-028, PS-029, PS-030, PS-031, PS-032) plus documented provider " +
  "inventory and routing policy -- no server round-trip, no B2 byte read, " +
  "no provider call";

// PS-025 local contract (FastAPI TestClient against a fresh empty store
// resolving the golden run_id from checked-in evidence) is verified.
export const PROVIDER_DECISION_INTELLIGENCE_LOCAL_CONTRACT_PROOF = true;

// PS-025: the public Render deployment is NOT verified yet. The new backend
// code must be deployed and the public URL must be verified end-to-end before
// this flag is flipped.
export const PROVIDER_DECISION_INTELLIGENCE_PUBLIC_DEPLOYMENT_PENDING = true;

// PS-026 unlock scope marker. Mirrors the backend
// `GOLDEN_DEMO_UNLOCK_SCOPE = "golden_demo_only"` so the surface honestly
// reports the narrow allowlist (only this single run_id resolves publicly).
export const PROVIDER_DECISION_INTELLIGENCE_UNLOCK_SCOPE = "golden_demo_only";

// Checked-in source evidence paths the surface cross-references.
export const PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS024_MANIFEST =
  "docs/evidence/demo/golden-demo-run.json";
export const PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS021_EVIDENCE =
  "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json";
export const PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS025_EVIDENCE =
  "docs/evidence/ps-025/public-durable-passport-unlock-smoke.json";
export const PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS026_EVIDENCE =
  "docs/evidence/ps-026/b2-evidence-explorer-smoke.json";
export const PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS027_EVIDENCE =
  "docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json";
export const PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS028_EVIDENCE =
  "docs/evidence/ps-028/manifest-verification-panel-smoke.json";
export const PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS029_EVIDENCE =
  "docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json";
export const PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS030_EVIDENCE =
  "docs/evidence/ps-030/failure-as-proof-timeline-smoke.json";
export const PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS031_EVIDENCE =
  "docs/evidence/ps-031/export-campaign-pack-v2-smoke.json";
export const PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS032_EVIDENCE =
  "docs/evidence/ps-032/operations-cockpit-flight-recorder-v2-smoke.json";

// Documented provider / model inventory (backs the provider option matrix).
export const PROVIDER_DECISION_INTELLIGENCE_PROVIDER_INVENTORY_DOC =
  "docs/submission/provider-model-inventory.md";

// PS-005 Pollinations fallback proof (backs the emergency no-key mode row).
export const PROVIDER_DECISION_INTELLIGENCE_PS005_PROOF =
  "docs/ps-005-pollinations-fallback-proof.md";

// PS-006 / PS-007 provider router proof (backs the router policy vocabulary).
export const PROVIDER_DECISION_INTELLIGENCE_PS006_PROOF =
  "docs/ps-006-provider-router-core-proof.md";

// PS-033 references the binding implementation roadmap and the PS-031A
// hardened product module correction.
export const PROVIDER_DECISION_INTELLIGENCE_IMPLEMENTATION_ROADMAP =
  "docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md";
export const PROVIDER_DECISION_INTELLIGENCE_PS031A_ROADMAP_CORRECTION =
  "docs/roadmap/ps-031a-hardened-product-modules-correction.md";

// ---------------------------------------------------------------------------
// Required source list. The surface cross-references nine evidence sources
// (PS-021 through PS-032) plus the implementation roadmap, the PS-031A
// correction, the documented provider inventory, and the PS-005 / PS-006
// router proofs that back the provider options.
// ---------------------------------------------------------------------------

export type ProviderDecisionIntelligenceSourceKind =
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
  | "provider_inventory"
  | "provider_proof"
  | "router_proof"
  | "roadmap_correction";

export interface ProviderDecisionIntelligenceSource {
  id: string;
  label: string;
  sliceTag: string;
  kind: ProviderDecisionIntelligenceSourceKind;
  evidencePath: string;
}

export const PROVIDER_DECISION_INTELLIGENCE_SOURCES: readonly ProviderDecisionIntelligenceSource[] =
  [
    {
      id: "ps024",
      label: "Golden demo manifest",
      sliceTag: "PS-024",
      kind: "golden_manifest",
      evidencePath:
        PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS024_MANIFEST,
    },
    {
      id: "ps021",
      label: "PS-021 B2 durable rehydrate evidence",
      sliceTag: "PS-021",
      kind: "b2_durable_evidence",
      evidencePath:
        PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS021_EVIDENCE,
    },
    {
      id: "ps025",
      label: "PS-025 public durable passport evidence",
      sliceTag: "PS-025",
      kind: "passport_evidence",
      evidencePath:
        PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS025_EVIDENCE,
    },
    {
      id: "ps026",
      label: "PS-026 B2 Evidence Explorer evidence",
      sliceTag: "PS-026",
      kind: "explorer_evidence",
      evidencePath:
        PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS026_EVIDENCE,
    },
    {
      id: "ps027",
      label: "PS-027 Genblaze Pipeline Graph evidence",
      sliceTag: "PS-027",
      kind: "pipeline_evidence",
      evidencePath:
        PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS027_EVIDENCE,
    },
    {
      id: "ps028",
      label: "PS-028 Manifest Verification Panel evidence",
      sliceTag: "PS-028",
      kind: "manifest_panel_evidence",
      evidencePath:
        PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS028_EVIDENCE,
    },
    {
      id: "ps029",
      label: "PS-029 B2 Rehydrate Comparison evidence",
      sliceTag: "PS-029",
      kind: "rehydrate_comparison_evidence",
      evidencePath:
        PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS029_EVIDENCE,
    },
    {
      id: "ps030",
      label: "PS-030 Failure-as-Proof Timeline evidence",
      sliceTag: "PS-030",
      kind: "failure_timeline_evidence",
      evidencePath:
        PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS030_EVIDENCE,
    },
    {
      id: "ps031",
      label: "PS-031 Judge Evidence Pack evidence",
      sliceTag: "PS-031",
      kind: "export_pack_evidence",
      evidencePath:
        PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS031_EVIDENCE,
    },
    {
      id: "ps032",
      label: "PS-032 Operations Cockpit evidence",
      sliceTag: "PS-032",
      kind: "operations_cockpit_evidence",
      evidencePath:
        PROVIDER_DECISION_INTELLIGENCE_SOURCE_PS032_EVIDENCE,
    },
    {
      id: "ps031a",
      label: "PS-031A hardened product module roadmap correction",
      sliceTag: "PS-031A",
      kind: "roadmap_correction",
      evidencePath:
        PROVIDER_DECISION_INTELLIGENCE_PS031A_ROADMAP_CORRECTION,
    },
    {
      id: "inventory",
      label: "Documented provider / model inventory",
      sliceTag: "PS-002 / PS-005 / PS-007",
      kind: "provider_inventory",
      evidencePath:
        PROVIDER_DECISION_INTELLIGENCE_PROVIDER_INVENTORY_DOC,
    },
    {
      id: "ps005",
      label: "PS-005 Pollinations no-key fallback proof",
      sliceTag: "PS-005",
      kind: "provider_proof",
      evidencePath: PROVIDER_DECISION_INTELLIGENCE_PS005_PROOF,
    },
    {
      id: "ps006",
      label: "PS-006 Provider router core proof",
      sliceTag: "PS-006 / PS-007",
      kind: "router_proof",
      evidencePath: PROVIDER_DECISION_INTELLIGENCE_PS006_PROOF,
    },
  ];

// ---------------------------------------------------------------------------
// Truth classes.
//
// The spec-required set for PS-033. Each provider option, budget mode, ledger
// row, and fallback policy row carries one of these classes so a reviewer can
// read evidence-backed facts vs documented options vs policy vs gaps.
// ---------------------------------------------------------------------------

export type ProviderDecisionIntelligenceTruthClass =
  | "checked_in_evidence"
  | "documented_provider_option"
  | "router_policy"
  | "fallback_policy"
  | "cost_policy_estimate"
  | "not_captured_in_evidence"
  | "public_deployment_pending";

// ---------------------------------------------------------------------------
// Decision summary.
//
// A compact routing summary so a designer / marketer / reviewer can read the
// provider decision state at a glance: selected route, decision state, budget
// mode state, cost / time ledger state, fallback state, emergency no-key mode
// state, and the evidence-backed vs policy / inferred split.
//
// HONESTY: the selected provider / model / budget mode / attempt count /
// fallback count / measured cost / measured latency for the golden run are
// NOT captured in the PS-021 durable rehydrate evidence consumed here. The
// summary says so explicitly instead of inventing a selected provider.
// ---------------------------------------------------------------------------

export interface ProviderDecisionIntelligenceSummaryItem {
  key: string;
  label: string;
  value: string;
  truthClass: ProviderDecisionIntelligenceTruthClass;
  note: string;
}

export const PROVIDER_DECISION_INTELLIGENCE_SELECTED_ROUTE_SUMMARY: string =
  "The selected provider / model for the golden proof chain is not " +
  "explicitly available from the checked-in durable rehydrate evidence " +
  "consumed by PS-033 (PS-021 records the archive URI, archive SHA-256, " +
  "rehydrate source, and zero provider calls during rehydrate, but not the " +
  "selected provider, selected model, budget mode, or attempt ledger). The " +
  "surface therefore explains the documented provider options and routing " +
  "policies instead of inventing a selected provider. Documented options " +
  "live in docs/submission/provider-model-inventory.md; the router core " +
  "lives in src/proofstudio/providers/router.py.";

export const PROVIDER_DECISION_INTELLIGENCE_DECISION_SUMMARY: readonly ProviderDecisionIntelligenceSummaryItem[] =
  [
    {
      key: "selected_route",
      label: "Selected route for the golden proof chain",
      value: "not captured in checked-in evidence",
      truthClass: "not_captured_in_evidence",
      note:
        "PS-021 records the archive + rehydrate facts but not the golden " +
        "run's selected provider, model, or budget mode. The surface does " +
        "not invent a selected provider.",
    },
    {
      key: "provider_decision_state",
      label: "Provider decision state",
      value: "documented options + router policy",
      truthClass: "router_policy",
      note:
        "The router (ProviderRouter, PS-006 / PS-007) runs providers in " +
        "priority order and preserves every attempt; the options shown below " +
        "are documented in the provider inventory.",
    },
    {
      key: "budget_mode_state",
      label: "Budget mode state",
      value: "policy classes, not live billing facts",
      truthClass: "cost_policy_estimate",
      note:
        "PS-033 presents free_safe / balanced / quality_max / " +
        "emergency_no_key as routing policies. The golden run's recorded " +
        "budget_mode literal is not captured in the durable rehydrate " +
        "evidence consumed here.",
    },
    {
      key: "cost_time_ledger_state",
      label: "Cost / time ledger state",
      value: "captured vs not-captured split",
      truthClass: "not_captured_in_evidence",
      note:
        "Only provider_calls_during_rehydrate (0) is captured for the golden " +
        "run. Measured cost, latency, attempt count, and fallback count are " +
        "not captured in the durable rehydrate evidence.",
    },
    {
      key: "fallback_state",
      label: "Fallback state",
      value: "policy, no real fallback captured",
      truthClass: "fallback_policy",
      note:
        "The router supports fallback through the chain. No actual " +
        "failure / retry / fallback event is claimed for the golden run " +
        "unless checked-in evidence proves it.",
    },
    {
      key: "emergency_no_key_state",
      label: "Emergency no-key mode state",
      value: "documented, not validated for this run",
      truthClass: "documented_provider_option",
      note:
        "Pollinations no-key fallback is live-proven in PS-005 but is not " +
        "claimed as the active path for the golden run.",
    },
    {
      key: "evidence_vs_policy_split",
      label: "Evidence-backed vs policy / inferred",
      value: "mixed (see truth class on each row)",
      truthClass: "router_policy",
      note:
        "Every row below carries a truth class so a reviewer can read what " +
        "is checked-in evidence, what is documented option, what is policy, " +
        "and what is not captured.",
    },
  ];

// ---------------------------------------------------------------------------
// Provider option matrix.
//
// Each option carries: provider name, model or role, modality or output type,
// key requirement, budget class, fallback role, evidence status, risk notes,
// truth class. Options are limited to providers supported by existing code /
// docs / evidence (provider-model-inventory.md + PS-005 + PS-006/007).
//
// Optional providers documented but not active in the golden run are marked
// documented_provider_option, not verified for this run. No provider is
// claimed as the golden run's selected provider.
// ---------------------------------------------------------------------------

export interface ProviderDecisionIntelligenceOption {
  key: string;
  provider: string;
  modelOrRole: string;
  modalityOrOutput: string;
  keyRequirement: string;
  budgetClass: string;
  fallbackRole: string;
  evidenceStatus: string;
  riskNotes: string;
  truthClass: ProviderDecisionIntelligenceTruthClass;
}

export const PROVIDER_DECISION_INTELLIGENCE_PROVIDER_OPTIONS: readonly ProviderDecisionIntelligenceOption[] =
  [
    {
      key: "cloudflare_workers_ai",
      provider: "Cloudflare Workers AI",
      modelOrRole: "@cf/bytedance/stable-diffusion-xl-lightning",
      modalityOrOutput: "image (image_generation)",
      keyRequirement: "paid API key required",
      budgetClass: "quality_max / balanced",
      fallbackRole: "primary (not fallback)",
      evidenceStatus:
        "Live-proven in PS-004 / PS-007 / PS-009 / PS-010 / PS-011; not " +
        "claimed as the golden run's selected provider.",
      riskNotes:
        "Quota / credit gating possible; documented as the primary image " +
        "path. Not captured for the golden run's selected route.",
      truthClass: "documented_provider_option",
    },
    {
      key: "pollinations",
      provider: "Pollinations",
      modelOrRole: "pollinations-image-default",
      modalityOrOutput: "image (image_generation)",
      keyRequirement: "no API key required",
      budgetClass: "emergency_no_key / free_safe",
      fallbackRole: "fallback (no-key emergency)",
      evidenceStatus:
        "Live-proven in PS-005 as a no-key fallback; not claimed as the " +
        "golden run's selected provider.",
      riskNotes:
        "Documented as a fallback provider, not a premium final visual " +
        "provider. Used when the primary is missing a key, fails, or is " +
        "disabled.",
      truthClass: "documented_provider_option",
    },
    {
      key: "gemini_campaign",
      provider: "Google Gemini",
      modelOrRole:
        "models/gemini-2.5-pro (primary), models/gemini-2.5-flash (fallback)",
      modalityOrOutput: "text (campaign intelligence / strategy)",
      keyRequirement: "API key required",
      budgetClass: "balanced",
      fallbackRole: "strategy layer (not visual generation)",
      evidenceStatus:
        "Implemented as the campaign-intelligence / strategy layer in " +
        "PS-002; distinct from visual generation.",
      riskNotes:
        "Strategy layer, not the visual generation path. Visual generation " +
        "through Gemini / Imagen is quota / paid-plan blocked (see below).",
      truthClass: "documented_provider_option",
    },
    {
      key: "gmi_cloud",
      provider: "GMI Cloud",
      modelOrRole: "generation",
      modalityOrOutput: "image (visual generation, attempted)",
      keyRequirement: "API key + credits required",
      budgetClass: "quality_max (attempted)",
      fallbackRole: "attempted (blocked)",
      evidenceStatus:
        "Path implemented in PS-001B; live generation is billing-blocked " +
        "(402 Insufficient credits). Not accepted as a passed provider.",
      riskNotes:
        "Auth and model validation work, but generation is credit-gated. " +
        "Quota / billing risk is real for this path.",
      truthClass: "documented_provider_option",
    },
    {
      key: "gemini_imagen_visual",
      provider: "Google Gemini / Imagen (visual)",
      modelOrRole:
        "gemini-*-flash-image, imagen-4.0-generate-001 (attempted)",
      modalityOrOutput: "image (visual generation, attempted)",
      keyRequirement: "API key + paid plan required",
      budgetClass: "quality_max (attempted)",
      fallbackRole: "attempted (blocked)",
      evidenceStatus:
        "Path implemented in PS-003; live visual generation is blocked " +
        "(429 RESOURCE_EXHAUSTED; Imagen requires a paid plan).",
      riskNotes:
        "Quota / paid-plan risk is the documented blocker. Not accepted as " +
        "a passed provider.",
      truthClass: "documented_provider_option",
    },
    {
      key: "luma",
      provider: "Luma",
      modelOrRole: "video (planned)",
      modalityOrOutput: "video (skipped)",
      keyRequirement: "card / payment required",
      budgetClass: "quality_max (planned)",
      fallbackRole: "skipped",
      evidenceStatus:
        "Skipped: a card / payment method is required to enable the " +
        "account, so it was not integrated.",
      riskNotes:
        "Not implemented. Recorded only as a documented potential direction.",
      truthClass: "documented_provider_option",
    },
    {
      key: "optional_later",
      provider: "ElevenLabs / OpenAI / Runway / Stability Audio / NVIDIA NIM",
      modelOrRole: "audio / video / image (optional later)",
      modalityOrOutput: "audio / video / image (not implemented)",
      keyRequirement: "varies (not integrated)",
      budgetClass: "n/a (not implemented)",
      fallbackRole: "optional later",
      evidenceStatus:
        "Not implemented and not claimed as working. Recorded only as " +
        "potential future directions.",
      riskNotes:
        "No backing slice. Listed only so the matrix is honest about what is " +
        "out of scope.",
      truthClass: "documented_provider_option",
    },
  ];

// ---------------------------------------------------------------------------
// Budget modes.
//
// Presented as ROUTING POLICIES, not live billing facts. Each mode carries a
// goal, preferred route behavior, fallback behavior, key / payment
// dependency, risk, what is measured, and what is not measured yet.
//
// The PS-033 policy modes (free_safe / balanced / quality_max /
// emergency_no_key) are policy classifications; the live demo app's
// budget_mode literals (free-only / cheap / premium-final) are documented in
// the Review Room and the FastAPI run input model. The golden run's recorded
// budget_mode literal is not captured in the durable rehydrate evidence
// consumed here.
// ---------------------------------------------------------------------------

export interface ProviderDecisionIntelligenceBudgetMode {
  key: string;
  label: string;
  goal: string;
  preferredRouteBehavior: string;
  fallbackBehavior: string;
  keyPaymentDependency: string;
  risk: string;
  whatIsMeasured: string;
  whatIsNotMeasuredYet: string;
  truthClass: ProviderDecisionIntelligenceTruthClass;
}

export const PROVIDER_DECISION_INTELLIGENCE_BUDGET_MODES: readonly ProviderDecisionIntelligenceBudgetMode[] =
  [
    {
      key: "free_safe",
      label: "free_safe",
      goal:
        "Avoid spend and quota risk; prefer free / no-key-safe routing.",
      preferredRouteBehavior:
        "Prefer documented free paths (e.g. Pollinations no-key image " +
        "fallback); skip paid-only providers.",
      fallbackBehavior:
        "Fall back through the chain; reach no-key emergency path if needed.",
      keyPaymentDependency: "No paid key required to produce output.",
      risk:
        "Lower visual fidelity than quality-max paths; fallback provider is " +
        "documented as not premium.",
      whatIsMeasured:
        "Provider call status during rehydrate (0 for the golden run).",
      whatIsNotMeasuredYet:
        "Measured cost, latency, and quota usage are not captured in the " +
        "durable rehydrate evidence consumed here.",
      truthClass: "cost_policy_estimate",
    },
    {
      key: "balanced",
      label: "balanced",
      goal:
        "Trade cost and quality; prefer a capable provider when a key is " +
        "available.",
      preferredRouteBehavior:
        "Prefer the documented primary image provider (Cloudflare Workers " +
        "AI) when a paid key is present.",
      fallbackBehavior:
        "Fall back through documented options if the primary is missing a " +
        "key, fails, or is disabled.",
      keyPaymentDependency: "Paid key improves the selected route.",
      risk:
        "Quota / credit gating possible on the primary; fallback reduces " +
        "fidelity.",
      whatIsMeasured:
        "Provider call status during rehydrate (0 for the golden run).",
      whatIsNotMeasuredYet:
        "Measured cost, latency, and quota usage are not captured in the " +
        "durable rehydrate evidence consumed here.",
      truthClass: "cost_policy_estimate",
    },
    {
      key: "quality_max",
      label: "quality_max",
      goal: "Maximize output quality; accept paid / quota cost.",
      preferredRouteBehavior:
        "Prefer documented premium paths (Cloudflare Workers AI primary; " +
        "Gemini/Imagen visual when unblocked).",
      fallbackBehavior:
        "Fall back through documented options on failure, but quality is " +
        "the first priority.",
      keyPaymentDependency: "Paid key and credits are expected.",
      risk:
        "Billing-blocked (GMI Cloud 402) and quota-blocked (Gemini/Imagen " +
        "429) are documented blockers for some premium paths.",
      whatIsMeasured:
        "Provider call status during rehydrate (0 for the golden run).",
      whatIsNotMeasuredYet:
        "Measured cost, latency, and quota usage are not captured in the " +
        "durable rehydrate evidence consumed here.",
      truthClass: "cost_policy_estimate",
    },
    {
      key: "emergency_no_key",
      label: "emergency_no_key",
      goal:
        "Keep demos and onboarding running when keys are missing.",
      preferredRouteBehavior:
        "Use the documented no-key path (Pollinations) so a demo never " +
        "dead-ends on a missing key.",
      fallbackBehavior:
        "This mode IS the fallback path; it is labeled honestly as not " +
        "equivalent to paid production output.",
      keyPaymentDependency: "No key required.",
      risk:
        "Lower fidelity; documented as fallback, not premium. Do not claim " +
        "production-grade output.",
      whatIsMeasured:
        "PS-005 proved valid image bytes return without an API key.",
      whatIsNotMeasuredYet:
        "Production no-key generation is not validated for the golden run " +
        "and is not claimed as such.",
      truthClass: "fallback_policy",
    },
  ];

// ---------------------------------------------------------------------------
// Why This Provider panel.
//
// A human-readable explanation answering the five required questions. Written
// as policy / inferred explanation so it never overclaims a selected provider
// for the golden run.
// ---------------------------------------------------------------------------

export interface ProviderDecisionIntelligenceWhyThisProvider {
  whyAcceptable: string;
  whatEvidenceBacksIt: string;
  whatIsNotKnown: string;
  howSystemBehavesIfKeyUnavailable: string;
  howEmergencyNoKeyDiffersFromQuality: string;
}

export const PROVIDER_DECISION_INTELLIGENCE_WHY_THIS_PROVIDER: ProviderDecisionIntelligenceWhyThisProvider =
  {
    whyAcceptable:
      "The golden proof chain is acceptable because PS-021 proved the run " +
      "archive can be rehydrated from a real Backblaze B2 object with zero " +
      "provider calls during rehydrate, and PS-024 / PS-025 / PS-026 / " +
      "PS-027 / PS-028 / PS-029 / PS-030 / PS-031 / PS-032 all agree on the " +
      "run_id, campaign_id, archive URI, and archive SHA-256. The provider " +
      "decision surface does not need a live provider call to be useful: it " +
      "explains the documented routing policy and the real provider " +
      "options behind it.",
    whatEvidenceBacksIt:
      "Checked-in evidence (PS-021 durable rehydrate smoke) records " +
      "provider_calls_during_rehydrate = 0 and no_live_provider_call_during" +
      "_rehydrate = true. The documented provider inventory records the " +
      "real provider options (Cloudflare Workers AI primary, Pollinations " +
      "no-key fallback, Gemini campaign intelligence) with their backing " +
      "slices. The ProviderRouter core (PS-006 / PS-007) defines the " +
      "ordered-chain + preserve-every-attempt + fallback policy.",
    whatIsNotKnown:
      "The golden run's selected provider, selected model, budget mode, " +
      "attempt count, fallback count, measured cost, measured latency, and " +
      "quota status are NOT captured in the durable rehydrate evidence " +
      "consumed by PS-033. PS-033 does not invent them.",
    howSystemBehavesIfKeyUnavailable:
      "If a paid provider key is missing, the documented router policy is " +
      "to fall back through the chain and reach the documented no-key path " +
      "(Pollinations) so a demo or onboarding does not dead-end. No actual " +
      "fallback event is claimed for the golden run unless evidence proves " +
      "it.",
    howEmergencyNoKeyDiffersFromQuality:
      "Emergency no-key mode keeps a demo running without any key " +
      "(documented Pollinations fallback, PS-005). Quality-max mode prefers " +
      "documented premium paths (Cloudflare Workers AI primary; Gemini / " +
      "Imagen visual when unblocked) and accepts paid / quota cost. The two " +
      "modes trade fidelity for resilience; emergency no-key is documented " +
      "as not equivalent to paid production output.",
  };

// ---------------------------------------------------------------------------
// Cost and time ledger.
//
// Separates captured values, not-captured values, and future measurement
// fields. If measured cost or latency is not captured, the literal "not " +
// "captured in checked-in evidence" is used. No price, spend, latency, quota,
// or token usage is invented.
// ---------------------------------------------------------------------------

export const PROVIDER_DECISION_INTELLIGENCE_NOT_CAPTURED_LABEL =
  "not captured in checked-in evidence";

export interface ProviderDecisionIntelligenceLedgerRow {
  key: string;
  provider: string;
  modelOrRole: string;
  attemptCount: string;
  fallbackCount: string;
  providerCallsDuringRehydrate: string;
  estimatedCostClass: string;
  measuredCost: string;
  measuredLatency: string;
  evidenceSource: string;
  truthClass: ProviderDecisionIntelligenceTruthClass;
}

export const PROVIDER_DECISION_INTELLIGENCE_COST_TIME_LEDGER: readonly ProviderDecisionIntelligenceLedgerRow[] =
  [
    {
      key: "golden_run_ledger",
      provider: "not captured in checked-in evidence",
      modelOrRole: "not captured in checked-in evidence",
      attemptCount: "not captured in checked-in evidence",
      fallbackCount: "not captured in checked-in evidence",
      providerCallsDuringRehydrate: "0",
      estimatedCostClass: "not captured in checked-in evidence",
      measuredCost: PROVIDER_DECISION_INTELLIGENCE_NOT_CAPTURED_LABEL,
      measuredLatency: PROVIDER_DECISION_INTELLIGENCE_NOT_CAPTURED_LABEL,
      evidenceSource:
        "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json " +
        "(records provider_calls_during_rehydrate = 0; does not record " +
        "provider / model / attempt count / fallback count / cost / latency).",
      truthClass: "not_captured_in_evidence",
    },
  ];

export const PROVIDER_DECISION_INTELLIGENCE_LEDGER_FUTURE_FIELDS: readonly string[] =
  [
    "selected provider (from a future attempt ledger capture)",
    "selected model (from a future attempt ledger capture)",
    "budget_mode literal recorded for the run (from a future run capture)",
    "attempt_count (from a future attempt ledger capture)",
    "fallback_count (from a future attempt ledger capture)",
    "measured_cost (from a future billing capture; not an estimate)",
    "measured_latency_ms (from a future latency capture; not an estimate)",
    "token_usage (from a future token usage capture)",
    "quota_remaining (from a future quota inspection; PS-033 does not " +
      "inspect quota)",
  ];

// ---------------------------------------------------------------------------
// Emergency no-key mode.
//
// Explains when this mode is useful, how it protects demos / onboarding, what
// quality tradeoffs may exist, what evidence / code supports it, and what is
// not verified for the golden run. Production no-key generation is NOT claimed
// unless validated.
// ---------------------------------------------------------------------------

export interface ProviderDecisionIntelligenceEmergencyNoKeyMode {
  whenUseful: string;
  howProtectsDemosAndOnboarding: string;
  qualityTradeoffs: string;
  evidenceOrCodeSupport: string;
  notVerifiedForGoldenRun: string;
}

export const PROVIDER_DECISION_INTELLIGENCE_EMERGENCY_NO_KEY_MODE: ProviderDecisionIntelligenceEmergencyNoKeyMode =
  {
    whenUseful:
      "Useful when a paid provider key is missing, a provider fails, a " +
      "provider is disabled, or quota is exhausted -- and a demo or " +
      "onboarding flow must still produce an output.",
    howProtectsDemosAndOnboarding:
      "The documented router policy falls back through the chain to the " +
      "no-key path (Pollinations) so a judge demo or a new-user onboarding " +
      "does not dead-end on a missing key. The attempt is still recorded " +
      "honestly (success / failure / skip) by the ProviderRouter.",
    qualityTradeoffs:
      "The no-key fallback is documented as not a premium final visual " +
      "provider. Output fidelity is lower than quality-max paths.",
    evidenceOrCodeSupport:
      "PS-005 proved Pollinations returns valid image bytes without an API " +
      "key and ran the same B2 + Genblaze provenance pipeline. The " +
      "ProviderRouter core (src/proofstudio/providers/router.py, PS-006 / " +
      "PS-007) implements the ordered chain + preserve-every-attempt policy.",
    notVerifiedForGoldenRun:
      "Production no-key generation is NOT validated for the golden run. " +
      "The golden run's selected provider and any fallback are not captured " +
      "in the durable rehydrate evidence consumed by PS-033; PS-033 does " +
      "not claim no-key generation ran for the golden run.",
  };

// ---------------------------------------------------------------------------
// Provider failure / fallback policy.
//
// One policy row per required condition. None is claimed as having happened
// in the golden run unless checked-in evidence proves it.
// ---------------------------------------------------------------------------

export interface ProviderDecisionIntelligenceFallbackPolicyRow {
  key: string;
  condition: string;
  policy: string;
  truthClass: ProviderDecisionIntelligenceTruthClass;
}

export const PROVIDER_DECISION_INTELLIGENCE_FALLBACK_POLICY: readonly ProviderDecisionIntelligenceFallbackPolicyRow[] =
  [
    {
      key: "key_missing",
      condition: "Provider API key missing",
      policy:
        "Documented router policy: skip the provider, fall back through the " +
        "chain, reach the no-key path if needed. The router records the " +
        "skip honestly (SKIPPED_MISSING_KEY).",
      truthClass: "fallback_policy",
    },
    {
      key: "quota_exhausted",
      condition: "Quota exhausted",
      policy:
        "Documented router policy: treat as QUOTA_OR_BILLING_BLOCKED, fall " +
        "back through the chain. (GMI Cloud 402 and Gemini/Imagen 429 are " +
        "documented real blockers.)",
      truthClass: "fallback_policy",
    },
    {
      key: "provider_timeout",
      condition: "Provider timeout",
      policy:
        "Documented router policy: treat as TIMEOUT (retryable, fallback " +
        "allowed), fall back through the chain.",
      truthClass: "fallback_policy",
    },
    {
      key: "provider_unavailable",
      condition: "Provider unavailable",
      policy:
        "Documented router policy: treat as PROVIDER_DOWN (retryable, " +
        "fallback allowed), fall back through the chain.",
      truthClass: "fallback_policy",
    },
    {
      key: "moderation_safety_block",
      condition: "Moderation / safety block",
      policy:
        "Documented router policy: treat as SAFETY_BLOCKED (fallback " +
        "allowed), fall back through the chain.",
      truthClass: "fallback_policy",
    },
    {
      key: "paid_provider_skipped",
      condition: "Paid provider skipped",
      policy:
        "Documented router policy: when a paid provider is skipped " +
        "(SKIPPED_DISABLED / SKIPPED_MISSING_KEY), the router advances to " +
        "the next provider and may reach the no-key fallback.",
      truthClass: "fallback_policy",
    },
    {
      key: "fallback_to_no_key",
      condition: "Fallback to no-key mode",
      policy:
        "Documented router policy: reach the Pollinations no-key path so " +
        "the run still produces output. Labeled honestly as emergency " +
        "fallback, not premium output.",
      truthClass: "fallback_policy",
    },
  ];

export const PROVIDER_DECISION_INTELLIGENCE_FALLBACK_NO_FAILURE_LINE =
  "No real provider failure / retry / fallback event is claimed for the " +
  "golden run unless checked-in evidence proves it.";

// ---------------------------------------------------------------------------
// Designer / marketer interpretation.
//
// Plain-language explanations for non-technical users.
// ---------------------------------------------------------------------------

export interface ProviderDecisionIntelligenceDesignerMarketerInterpretation {
  bestQualityMode: string;
  cheapestSafeMode: string;
  emergencyDemoMode: string;
  whyProviderChoiceAffectsReview: string;
  whyProofMattersForClientHandoff: string;
  whenToExportEvidencePack: string;
}

export const PROVIDER_DECISION_INTELLIGENCE_DESIGNER_MARKETER_INTERPRETATION: ProviderDecisionIntelligenceDesignerMarketerInterpretation =
  {
    bestQualityMode:
      "Best quality = quality_max: prefer documented premium paths " +
      "(Cloudflare Workers AI primary; Gemini / Imagen visual when " +
      "unblocked). Accept paid / quota cost for higher fidelity.",
    cheapestSafeMode:
      "Cheapest safe = free_safe: prefer documented free paths (Pollinations " +
      "no-key fallback) and skip paid-only providers. Lower fidelity, no " +
      "spend.",
    emergencyDemoMode:
      "Emergency demo mode = emergency_no_key: use the documented no-key " +
      "path so a demo or onboarding keeps running when keys are missing. " +
      "Documented as not equivalent to paid production output.",
    whyProviderChoiceAffectsReview:
      "Provider choice affects what a reviewer sees: quality, fidelity, " +
      "whether a key was available, and whether a fallback ran. Reading " +
      "this surface before review sets honest expectations.",
    whyProofMattersForClientHandoff:
      "Proof matters for client handoff because the routing decision, the " +
      "documented provider options, and the fallback policy explain why an " +
      "asset looks the way it does -- without overclaiming authenticity.",
    whenToExportEvidencePack:
      "Export the Judge Evidence Pack when a client or judge needs a " +
      "portable, readable proof summary (run identity, B2 archive, " +
      "Genblaze manifest, rehydrate, limitations).",
  };

// ---------------------------------------------------------------------------
// Action rail.
//
// The surface links out to every implemented proof surface plus the golden
// passport and the Judge Cockpit Home.
// ---------------------------------------------------------------------------

export interface ProviderDecisionIntelligenceRoute {
  href: string;
  label: string;
  tag: string;
  description: string;
}

export const PROVIDER_DECISION_INTELLIGENCE_ACTION_ROUTES: readonly ProviderDecisionIntelligenceRoute[] =
  [
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
      href:
        "/passport/" + PROVIDER_DECISION_INTELLIGENCE_RUN_ID,
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

export const PROVIDER_DECISION_INTELLIGENCE_TRUTH_BOUNDARY =
  "The Provider Decision Intelligence surface summarizes checked-in evidence " +
  "(PS-021, PS-024, PS-025, PS-026, PS-027, PS-028, PS-029, PS-030, PS-031, " +
  "PS-032) and documented routing policy, explains provider decision " +
  "tradeoffs, shows cost / budget classes as policy unless measured evidence " +
  "exists, shows zero provider calls during rehydrate, helps marketers " +
  "understand routing choices, and shows pending gaps honestly. The surface " +
  "does not prove semantic truth, legal authenticity, C2PA authenticity, or " +
  "human authorship. The surface does not prove Object Lock or tamper-proof " +
  "storage. The surface did not fetch and hash the B2 object in the browser. " +
  "The local contract is verified; the public deployment remains pending " +
  "until the new backend is deployed and the public URL is verified " +
  "end-to-end.";

export const PROVIDER_DECISION_INTELLIGENCE_CLAIM_BOUNDARY_ALLOWED: readonly string[] =
  [
    "The surface summarizes checked-in evidence and documented routing policy.",
    "The surface explains provider decision tradeoffs.",
    "The surface shows cost / budget classes as policy unless measured " +
      "evidence exists.",
    "The surface shows zero provider calls during rehydrate.",
    "The surface helps marketers understand routing choices.",
    "The surface shows pending gaps honestly (selected provider not " +
      "captured; public deployment pending).",
  ];

export const PROVIDER_DECISION_INTELLIGENCE_CLAIM_BOUNDARY_FORBIDDEN: readonly string[] =
  [
    "The surface does not claim actual spend unless captured in evidence.",
    "The surface does not claim actual latency unless captured in evidence.",
    "The surface does not claim actual quota status unless captured.",
    "The surface does not claim real provider failures unless captured.",
    "The surface does not claim production no-key generation unless validated.",
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

export const PROVIDER_DECISION_INTELLIGENCE_LIMITATIONS: readonly string[] = [
  "No live provider call in PS-033: the surface performs no network call.",
  "No broad B2 read: the surface records the archive URI and SHA-256 from " +
    "checked-in evidence; it did not fetch the B2 object.",
  "No live pricing API: cost classes are policy, not measured billing.",
  "No measured billing unless present in checked-in evidence: measured cost " +
    "and measured latency are not captured for the golden run.",
  "No measured latency unless present in checked-in evidence.",
  "No quota inspection: quota status is not captured and not claimed.",
  "Public deployment pending: the local contract is verified; the public " +
    "Render deployment remains pending.",
  "Checked-in evidence and documented policy only: the surface does not " +
    "read a live provider feed.",
  "No invented provider failure events: the fallback policy shows where " +
    "captured failures would appear; none are claimed for the golden run.",
];

// ---------------------------------------------------------------------------
// Required intelligence sections (headings the component must render).
// ---------------------------------------------------------------------------

export const PROVIDER_DECISION_INTELLIGENCE_REQUIRED_SECTIONS: readonly string[] =
  [
    "Provider Decision Identity",
    "Decision Summary",
    "Provider Option Matrix",
    "Budget Modes",
    "Why This Provider",
    "Cost and Time Ledger",
    "Emergency No-Key Mode",
    "Provider Failure / Fallback Policy",
    "Designer / Marketer Interpretation",
    "Action Rail",
    "Truth Boundary",
    "Limitations",
  ];

// ---------------------------------------------------------------------------
// Intelligence JSON shape.
//
// buildProviderDecisionIntelligenceJson() returns the deterministic
// intelligence JSON the surface summarizes. No dynamic field is used here.
// ---------------------------------------------------------------------------

export interface ProviderDecisionIntelligenceJson {
  intelligence_id: string;
  intelligence_version: string;
  generated_from: string;
  run_id: string;
  campaign_id: string;
  archive_uri: string;
  archive_sha256: string;
  rehydrate_source: string;
  provider_calls_during_rehydrate: number;
  no_live_provider_call_during_rehydrate: boolean;
  public_deployment_pending: boolean;
  selected_route_summary: string;
  decision_summary: readonly {
    key: string;
    label: string;
    value: string;
    truth_class: ProviderDecisionIntelligenceTruthClass;
    note: string;
  }[];
  provider_options: readonly {
    key: string;
    provider: string;
    model_or_role: string;
    modality_or_output: string;
    key_requirement: string;
    budget_class: string;
    fallback_role: string;
    evidence_status: string;
    risk_notes: string;
    truth_class: ProviderDecisionIntelligenceTruthClass;
  }[];
  budget_modes: readonly {
    key: string;
    label: string;
    goal: string;
    preferred_route_behavior: string;
    fallback_behavior: string;
    key_payment_dependency: string;
    risk: string;
    what_is_measured: string;
    what_is_not_measured_yet: string;
    truth_class: ProviderDecisionIntelligenceTruthClass;
  }[];
  why_this_provider: ProviderDecisionIntelligenceWhyThisProvider;
  cost_time_ledger: readonly {
    key: string;
    provider: string;
    model_or_role: string;
    attempt_count: string;
    fallback_count: string;
    provider_calls_during_rehydrate: string;
    estimated_cost_class: string;
    measured_cost: string;
    measured_latency: string;
    evidence_source: string;
    truth_class: ProviderDecisionIntelligenceTruthClass;
  }[];
  ledger_future_fields: readonly string[];
  emergency_no_key_mode: ProviderDecisionIntelligenceEmergencyNoKeyMode;
  fallback_policy: readonly {
    key: string;
    condition: string;
    policy: string;
    truth_class: ProviderDecisionIntelligenceTruthClass;
  }[];
  designer_marketer_interpretation: ProviderDecisionIntelligenceDesignerMarketerInterpretation;
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

export function buildProviderDecisionIntelligenceJson(): ProviderDecisionIntelligenceJson {
  return {
    intelligence_id: PROVIDER_DECISION_INTELLIGENCE_INTELLIGENCE_ID,
    intelligence_version: PROVIDER_DECISION_INTELLIGENCE_VERSION,
    generated_from: PROVIDER_DECISION_INTELLIGENCE_GENERATED_FROM,
    run_id: PROVIDER_DECISION_INTELLIGENCE_RUN_ID,
    campaign_id: PROVIDER_DECISION_INTELLIGENCE_CAMPAIGN_ID,
    archive_uri: PROVIDER_DECISION_INTELLIGENCE_ARCHIVE_URI,
    archive_sha256: PROVIDER_DECISION_INTELLIGENCE_ARCHIVE_SHA256,
    rehydrate_source: PROVIDER_DECISION_INTELLIGENCE_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      PROVIDER_DECISION_INTELLIGENCE_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      PROVIDER_DECISION_INTELLIGENCE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
    public_deployment_pending:
      PROVIDER_DECISION_INTELLIGENCE_PUBLIC_DEPLOYMENT_PENDING,
    selected_route_summary:
      PROVIDER_DECISION_INTELLIGENCE_SELECTED_ROUTE_SUMMARY,
    decision_summary: PROVIDER_DECISION_INTELLIGENCE_DECISION_SUMMARY.map(
      (s) => ({
        key: s.key,
        label: s.label,
        value: s.value,
        truth_class: s.truthClass,
        note: s.note,
      }),
    ),
    provider_options:
      PROVIDER_DECISION_INTELLIGENCE_PROVIDER_OPTIONS.map((o) => ({
        key: o.key,
        provider: o.provider,
        model_or_role: o.modelOrRole,
        modality_or_output: o.modalityOrOutput,
        key_requirement: o.keyRequirement,
        budget_class: o.budgetClass,
        fallback_role: o.fallbackRole,
        evidence_status: o.evidenceStatus,
        risk_notes: o.riskNotes,
        truth_class: o.truthClass,
      })),
    budget_modes: PROVIDER_DECISION_INTELLIGENCE_BUDGET_MODES.map((b) => ({
      key: b.key,
      label: b.label,
      goal: b.goal,
      preferred_route_behavior: b.preferredRouteBehavior,
      fallback_behavior: b.fallbackBehavior,
      key_payment_dependency: b.keyPaymentDependency,
      risk: b.risk,
      what_is_measured: b.whatIsMeasured,
      what_is_not_measured_yet: b.whatIsNotMeasuredYet,
      truth_class: b.truthClass,
    })),
    why_this_provider: PROVIDER_DECISION_INTELLIGENCE_WHY_THIS_PROVIDER,
    cost_time_ledger: PROVIDER_DECISION_INTELLIGENCE_COST_TIME_LEDGER.map(
      (r) => ({
        key: r.key,
        provider: r.provider,
        model_or_role: r.modelOrRole,
        attempt_count: r.attemptCount,
        fallback_count: r.fallbackCount,
        provider_calls_during_rehydrate: r.providerCallsDuringRehydrate,
        estimated_cost_class: r.estimatedCostClass,
        measured_cost: r.measuredCost,
        measured_latency: r.measuredLatency,
        evidence_source: r.evidenceSource,
        truth_class: r.truthClass,
      }),
    ),
    ledger_future_fields: PROVIDER_DECISION_INTELLIGENCE_LEDGER_FUTURE_FIELDS,
    emergency_no_key_mode:
      PROVIDER_DECISION_INTELLIGENCE_EMERGENCY_NO_KEY_MODE,
    fallback_policy: PROVIDER_DECISION_INTELLIGENCE_FALLBACK_POLICY.map(
      (p) => ({
        key: p.key,
        condition: p.condition,
        policy: p.policy,
        truth_class: p.truthClass,
      }),
    ),
    designer_marketer_interpretation:
      PROVIDER_DECISION_INTELLIGENCE_DESIGNER_MARKETER_INTERPRETATION,
    action_routes: PROVIDER_DECISION_INTELLIGENCE_ACTION_ROUTES.map((r) => ({
      href: r.href,
      label: r.label,
      tag: r.tag,
    })),
    truth_boundary: PROVIDER_DECISION_INTELLIGENCE_TRUTH_BOUNDARY,
    limitations: PROVIDER_DECISION_INTELLIGENCE_LIMITATIONS,
    source_evidence: PROVIDER_DECISION_INTELLIGENCE_SOURCES.map((src) => ({
      id: src.id,
      slice_tag: src.sliceTag,
      label: src.label,
      evidence_path: src.evidencePath,
    })),
  };
}
