// PS-030 Failure-as-Proof Timeline -- verified timeline constants.
//
// Every golden value in this module is sourced verbatim from the same
// checked-in evidence already used by PS-021 / PS-024 / PS-025 / PS-026 /
// PS-027 / PS-028 / PS-029:
//
//   - docs/evidence/demo/golden-demo-run.json                          (PS-024 golden manifest)
//   - docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json        (PS-021 live B2 durable rehydrate)
//   - docs/evidence/ps-025/public-durable-passport-unlock-smoke.json   (PS-025 public durable passport)
//   - docs/evidence/ps-026/b2-evidence-explorer-smoke.json             (PS-026 B2 Evidence Explorer)
//   - docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json          (PS-027 Genblaze Pipeline Graph)
//   - docs/evidence/ps-028/manifest-verification-panel-smoke.json      (PS-028 Manifest Verification Panel)
//   - docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json          (PS-029 B2 Rehydrate Comparison)
//
// The PS-030 smoke validates that every value below matches the source
// evidence exactly AND that every source agrees on the same value. No value
// is invented here.
//
// These constants exist so the Failure-as-Proof Timeline surface
// (apps/web/src/FailureAsProofTimeline.tsx) can show the golden workflow as
// an evidence-backed operational timeline, show where captured failures /
// retries / fallbacks would appear, and show the no-provider-rerun story,
// without re-fetching the API on every render and without reading any B2
// object. The timeline performs no network call, calls no provider, and reads
// no B2 object: it only renders verified, checked-in evidence.
//
// Truth boundary: the timeline shows that the checked-in evidence records a
// B2 rehydrate proof with zero provider calls during rehydrate, that the
// evidence agrees on the archive URI and SHA-256, and that the rehydrate uses
// durable archive evidence instead of a live provider rerun for the verified
// golden run. The timeline shows where captured failures, retries, and
// fallbacks would appear if future evidence captured them, but the verified
// golden run currently proves durable B2 rehydrate with zero provider calls,
// and no actual provider failure / fallback is claimed unless evidence proves
// it. The timeline does not prove semantic truth, legal authenticity, C2PA
// authenticity, or human authorship. The timeline does not prove Object Lock
// or tamper-proof storage. The timeline did not fetch and hash the B2 object
// in the browser. The local contract is verified; the public deployment
// remains pending until the new backend is deployed and the public URL is
// verified end-to-end.

// Verified golden demo run_id (PS-021 -> PS-024 -> PS-025 -> PS-026 -> PS-027
// -> PS-028 -> PS-029).
export const FAILURE_TIMELINE_RUN_ID =
  "run_89d967f9000045efa22ed4cc78cfa67f";

// Verified golden demo campaign_id (PS-021 -> PS-024 -> PS-025 -> PS-026 ->
// PS-027 -> PS-028 -> PS-029).
export const FAILURE_TIMELINE_CAMPAIGN_ID =
  "camp_bea5161faa6244079d2ee01ce445c259";

// Verified Backblaze B2 archive URI for the golden demo run (PS-021).
export const FAILURE_TIMELINE_ARCHIVE_URI =
  "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json";

// Verified SHA-256 of the B2 archive content for the golden demo run (PS-021).
export const FAILURE_TIMELINE_ARCHIVE_SHA256 =
  "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141";

// Rehydrate source recorded by PS-021 (durable_source = b2_rehydrated).
export const FAILURE_TIMELINE_REHYDRATE_SOURCE = "b2_rehydrated";

// PS-021 proved zero provider calls during B2 rehydrate.
export const FAILURE_TIMELINE_PROVIDER_CALLS_DURING_REHYDRATE = 0;

// PS-021 proved no live provider call happened during B2 rehydrate.
export const FAILURE_TIMELINE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE = true;

// Checked-in source evidence paths the timeline cross-references. These are
// the files the PS-030 smoke reads to verify every published value.
export const FAILURE_TIMELINE_SOURCE_PS024_MANIFEST =
  "docs/evidence/demo/golden-demo-run.json";
export const FAILURE_TIMELINE_SOURCE_PS021_EVIDENCE =
  "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json";
export const FAILURE_TIMELINE_SOURCE_PS025_EVIDENCE =
  "docs/evidence/ps-025/public-durable-passport-unlock-smoke.json";
export const FAILURE_TIMELINE_SOURCE_PS026_EVIDENCE =
  "docs/evidence/ps-026/b2-evidence-explorer-smoke.json";
export const FAILURE_TIMELINE_SOURCE_PS027_EVIDENCE =
  "docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json";
export const FAILURE_TIMELINE_SOURCE_PS028_EVIDENCE =
  "docs/evidence/ps-028/manifest-verification-panel-smoke.json";
export const FAILURE_TIMELINE_SOURCE_PS029_EVIDENCE =
  "docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json";

// PS-030 references the binding implementation roadmap.
export const FAILURE_TIMELINE_IMPLEMENTATION_ROADMAP =
  "docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md";

// PS-025 local contract (FastAPI TestClient against a fresh empty store
// resolving the golden run_id from checked-in evidence) is verified.
export const FAILURE_TIMELINE_LOCAL_CONTRACT_PROOF = true;

// PS-025: the public Render deployment is NOT verified for the golden passport
// unlock yet. The new backend code must be deployed and the public URL must be
// verified end-to-end before this flag is flipped. Surfacing this honestly in
// the timeline is required so a judge never reads "public deployment verified"
// when it has not been tested.
export const FAILURE_TIMELINE_PUBLIC_DEPLOYMENT_PENDING = true;

// PS-026 unlock scope marker. Mirrors the backend
// `GOLDEN_DEMO_UNLOCK_SCOPE = "golden_demo_only"` so the timeline honestly
// reports the narrow allowlist (only this single run_id resolves publicly).
export const FAILURE_TIMELINE_UNLOCK_SCOPE = "golden_demo_only";

// ---------------------------------------------------------------------------
// Required source list. The timeline cross-references seven evidence sources
// plus the implementation roadmap.
// ---------------------------------------------------------------------------

export type FailureTimelineSourceKind =
  | "golden_manifest"
  | "b2_durable_evidence"
  | "passport_evidence"
  | "explorer_evidence"
  | "pipeline_evidence"
  | "manifest_panel_evidence"
  | "rehydrate_comparison_evidence";

export interface FailureTimelineSource {
  id: string;
  label: string;
  sliceTag: string;
  kind: FailureTimelineSourceKind;
  evidencePath: string;
}

export const FAILURE_TIMELINE_SOURCES: readonly FailureTimelineSource[] = [
  {
    id: "ps024",
    label: "Golden demo manifest",
    sliceTag: "PS-024",
    kind: "golden_manifest",
    evidencePath: FAILURE_TIMELINE_SOURCE_PS024_MANIFEST,
  },
  {
    id: "ps021",
    label: "PS-021 B2 durable rehydrate evidence",
    sliceTag: "PS-021",
    kind: "b2_durable_evidence",
    evidencePath: FAILURE_TIMELINE_SOURCE_PS021_EVIDENCE,
  },
  {
    id: "ps025",
    label: "PS-025 public durable passport evidence",
    sliceTag: "PS-025",
    kind: "passport_evidence",
    evidencePath: FAILURE_TIMELINE_SOURCE_PS025_EVIDENCE,
  },
  {
    id: "ps026",
    label: "PS-026 B2 Evidence Explorer evidence",
    sliceTag: "PS-026",
    kind: "explorer_evidence",
    evidencePath: FAILURE_TIMELINE_SOURCE_PS026_EVIDENCE,
  },
  {
    id: "ps027",
    label: "PS-027 Genblaze Pipeline Graph evidence",
    sliceTag: "PS-027",
    kind: "pipeline_evidence",
    evidencePath: FAILURE_TIMELINE_SOURCE_PS027_EVIDENCE,
  },
  {
    id: "ps028",
    label: "PS-028 Manifest Verification Panel evidence",
    sliceTag: "PS-028",
    kind: "manifest_panel_evidence",
    evidencePath: FAILURE_TIMELINE_SOURCE_PS028_EVIDENCE,
  },
  {
    id: "ps029",
    label: "PS-029 B2 Rehydrate Comparison evidence",
    sliceTag: "PS-029",
    kind: "rehydrate_comparison_evidence",
    evidencePath: FAILURE_TIMELINE_SOURCE_PS029_EVIDENCE,
  },
];

// ---------------------------------------------------------------------------
// Required timeline events. The timeline renders one stage per event, in
// order. Each event maps to the checked-in evidence that proves it, and to
// the proof surface that exposes it.
//
// Events marked "captured_failure_surface" describe where captured failures,
// retries, and fallbacks would appear in the model if future evidence
// captured them. The verified golden run currently proves durable B2
// rehydrate with zero provider calls, so no actual failure / fallback is
// claimed for these slots.
// ---------------------------------------------------------------------------

export type FailureTimelineEventKind =
  | "checked_in_evidence"
  | "durable_b2_archive_proof"
  | "b2_rehydrate_proof"
  | "local_passport_contract_proof"
  | "inferred_product_explanation"
  | "captured_failure_surface"
  | "public_deployment_pending";

export interface FailureTimelineEvent {
  idx: number;
  key: string;
  title: string;
  kind: FailureTimelineEventKind;
  summary: string;
  // Slice tags that back this event, or "future model" for slots where
  // captured failures would appear if evidence captured them.
  sourceTags: readonly string[];
  // Route(s) this event links to (proof surfaces).
  links: readonly string[];
}

export const FAILURE_TIMELINE_EVENTS: readonly FailureTimelineEvent[] = [
  {
    idx: 1,
    key: "golden_run_identity",
    title: "Golden run identity established",
    kind: "checked_in_evidence",
    summary:
      "One canonical golden demo run is pinned honestly: run_id and " +
      "campaign_id sourced verbatim from the PS-024 golden demo manifest, " +
      "traced to the PS-021 live B2 durable rehydrate smoke.",
    sourceTags: ["PS-024", "PS-021"],
    links: ["/passport/" + FAILURE_TIMELINE_RUN_ID, "/b2-evidence"],
  },
  {
    idx: 2,
    key: "provider_routing_recorded",
    title: "Provider routing / orchestration path recorded",
    kind: "inferred_product_explanation",
    summary:
      "The ProviderRouter records the provider / model selection path for " +
      "each run. The golden workflow exposes this path as an evidence-backed " +
      "timeline entry rather than hiding it.",
    sourceTags: ["PS-006", "PS-007"],
    links: ["/genblaze-pipeline"],
  },
  {
    idx: 3,
    key: "generation_provenance_captured",
    title: "Generation / provenance path captured",
    kind: "inferred_product_explanation",
    summary:
      "The Genblaze pipeline records what each generation attempt produced " +
      "and verifies the stored manifest against the asset bytes. The " +
      "golden workflow exposes this provenance capture as a timeline entry.",
    sourceTags: ["PS-001A", "PS-007", "PS-011"],
    links: ["/genblaze-pipeline", "/manifest-verification"],
  },
  {
    idx: 4,
    key: "b2_archive_created",
    title: "B2 archive created",
    kind: "durable_b2_archive_proof",
    summary:
      "PS-021 proved the full run archive was written to a real Backblaze " +
      "B2 object behind explicit, default-off gates. The archive URI and " +
      "SHA-256 are recorded in checked-in evidence.",
    sourceTags: ["PS-021", "PS-026"],
    links: ["/b2-evidence"],
  },
  {
    idx: 5,
    key: "golden_manifest_pinned",
    title: "Golden manifest pinned",
    kind: "checked_in_evidence",
    summary:
      "PS-024 pinned the golden demo manifest so every later surface " +
      "(PS-025 through PS-029) cross-references the same verified values.",
    sourceTags: ["PS-024", "PS-028"],
    links: ["/manifest-verification"],
  },
  {
    idx: 6,
    key: "public_passport_unlocked_locally",
    title: "Public passport contract unlocked locally",
    kind: "local_passport_contract_proof",
    summary:
      "PS-025 unlocked a narrow public passport path for this single " +
      "golden run_id, resolved from checked-in evidence only. The local " +
      "contract (FastAPI TestClient) is verified; the public deployment " +
      "remains pending.",
    sourceTags: ["PS-025"],
    links: ["/passport/" + FAILURE_TIMELINE_RUN_ID],
  },
  {
    idx: 7,
    key: "b2_evidence_explorer_created",
    title: "B2 Evidence Explorer surface created",
    kind: "durable_b2_archive_proof",
    summary:
      "PS-026 surfaces the archive URI, archive SHA-256, rehydrate source, " +
      "and zero-provider-call proof as a first-class product surface.",
    sourceTags: ["PS-026"],
    links: ["/b2-evidence"],
  },
  {
    idx: 8,
    key: "genblaze_pipeline_graph_created",
    title: "Genblaze Pipeline Graph surface created",
    kind: "inferred_product_explanation",
    summary:
      "PS-027 surfaces the media pipeline as a Genblaze Pipeline Graph: " +
      "Brief through ProviderRouter, Genblaze orchestration, asset/manifest " +
      "capture, B2 archive, passport, and durable rehydrate.",
    sourceTags: ["PS-027"],
    links: ["/genblaze-pipeline"],
  },
  {
    idx: 9,
    key: "manifest_verification_confirms",
    title: "Manifest Verification Panel confirms consistency",
    kind: "checked_in_evidence",
    summary:
      "PS-028 confirms the golden run manifest agrees across every checked-in " +
      "evidence source on run_id, campaign_id, archive URI, archive SHA-256, " +
      "rehydrate source, and zero provider calls during rehydrate.",
    sourceTags: ["PS-028"],
    links: ["/manifest-verification"],
  },
  {
    idx: 10,
    key: "b2_rehydrate_comparison_confirms",
    title:
      "B2 Rehydrate Comparison confirms durable rehydrate without provider rerun",
    kind: "b2_rehydrate_proof",
    summary:
      "PS-029 confirms the rehydrate used durable B2 archive evidence " +
      "instead of a live provider rerun: provider_calls_during_rehydrate = " +
      "0 and no_live_provider_call_during_rehydrate = true.",
    sourceTags: ["PS-029", "PS-021"],
    links: ["/b2-rehydrate-comparison"],
  },
  {
    idx: 11,
    key: "captured_failure_slot",
    title:
      "Where captured failures, retries, and fallbacks would appear",
    kind: "captured_failure_surface",
    summary:
      "If future evidence captured a provider failure, a retry decision, a " +
      "fallback, a skipped provider, a disabled provider, or a quota block, " +
      "it would appear here as an auditable timeline entry. The verified " +
      "golden run currently proves durable B2 rehydrate with zero provider " +
      "calls; no actual failure or fallback is claimed unless evidence " +
      "proves it.",
    sourceTags: ["future model"],
    links: ["/b2-rehydrate-comparison"],
  },
  {
    idx: 12,
    key: "public_deployment_pending",
    title: "Public deployment pending remains explicit",
    kind: "public_deployment_pending",
    summary:
      "The local contract is verified. The public Render deployment is not " +
      "verified yet: the new backend must be deployed and the public URL " +
      "verified end-to-end before this status changes.",
    sourceTags: ["PS-025"],
    links: ["/"],
  },
];

// ---------------------------------------------------------------------------
// No-provider-rerun story.
//
// A short, judge-readable explanation of why the rehydrate required no live
// provider rerun. Surfaced as a dedicated section so the B2 value (durability
// without provider availability) is visible at a glance.
// ---------------------------------------------------------------------------

export const FAILURE_TIMELINE_NO_PROVIDER_RERUN_STORY =
  "For the verified golden run, rehydrate uses B2-backed evidence with " +
  "zero provider calls. PS-021 proved the run can be rehydrated from B2 " +
  "archive content after backend memory loss. The checked-in evidence " +
  "records provider_calls_during_rehydrate = 0 and " +
  "no_live_provider_call_during_rehydrate = true. That means the rehydrate " +
  "path used the durable Backblaze B2 archive evidence instead of calling " +
  "any media provider again.";

// ---------------------------------------------------------------------------
// Failure-as-Proof explanation.
//
// The required visible language must appear verbatim in the surface. These
// constants keep them in one place so the PS-030 smoke can verify them.
// ---------------------------------------------------------------------------

export const FAILURE_TIMELINE_NO_FAKE_FAILURES_LINE =
  "No fake failures are claimed.";

export const FAILURE_TIMELINE_WHERE_FAILURES_APPEAR_LINE =
  "This timeline shows where captured failures, retries, and fallbacks would appear.";

export const FAILURE_TIMELINE_ZERO_PROVIDER_CALLS_LINE =
  "For the verified golden run, rehydrate uses B2-backed evidence with zero provider calls.";

export const FAILURE_TIMELINE_FAILURE_AS_PROOF_EXPLANATION: readonly string[] =
  [
    "Traditional AI media tools hide failed attempts, skipped providers, " +
      "retry decisions, and provider instability. The output is shown; the " +
      "operational trail is discarded.",
    "ProofStudio treats operational events as auditable workflow evidence. " +
      "Provider attempts, retry decisions, fallback readiness, storage, and " +
      "rehydrate behavior are part of the production proof trail, not " +
      "hidden noise.",
    "This timeline shows where captured failures, retries, and fallbacks " +
      "would appear.",
    "The verified golden run currently proves durable B2 rehydrate with " +
      "zero provider calls during rehydrate.",
    "No actual provider failure or fallback is claimed unless checked-in " +
      "evidence proves it. No fake failures are claimed.",
    "For the verified golden run, rehydrate uses B2-backed evidence with " +
      "zero provider calls.",
  ];

// ---------------------------------------------------------------------------
// Failure Theater -- the failure-placement model.
//
// Explains the categories of operational events the model would surface if
// captured by evidence. None of these are claimed to have occurred for the
// golden run.
// ---------------------------------------------------------------------------

export interface FailureTheaterSlot {
  key: string;
  title: string;
  description: string;
}

export const FAILURE_TIMELINE_FAILURE_THEATER_SLOTS: readonly FailureTheaterSlot[] =
  [
    {
      key: "captured_failure",
      title: "Captured failure",
      description:
        "A provider call that failed (network error, rate limit, model " +
        "error). Surfaced with sanitized error text, latency, and retryable " +
        "flag. None claimed for the golden run.",
    },
    {
      key: "retry_decision",
      title: "Retry decision",
      description:
        "A retry attempt after a failure, with attempt index and outcome. " +
        "None claimed for the golden run.",
    },
    {
      key: "fallback",
      title: "Fallback",
      description:
        "A switch to a fallback provider or model after the primary path " +
        "could not complete. None claimed for the golden run.",
    },
    {
      key: "skipped_provider",
      title: "Skipped provider",
      description:
        "A provider that was skipped due to budget mode, availability, or " +
        "policy. None claimed for the golden run.",
    },
    {
      key: "disabled_provider",
      title: "Disabled provider",
      description:
        "A provider disabled by configuration or credentials. None claimed " +
        "for the golden run.",
    },
    {
      key: "quota_block",
      title: "Quota block",
      description:
        "A provider call blocked by a quota ceiling. None claimed for the " +
        "golden run.",
    },
  ];

// ---------------------------------------------------------------------------
// Archive / Rehydrate Lab foundation.
//
// This is the timeline foundation for later PS-031 / PS-043 lab work, not the
// full lab yet. It surfaces the verified archive + rehydrate values so a
// judge can read the durable rehydrate story in one place.
// ---------------------------------------------------------------------------

export const FAILURE_TIMELINE_ARCHIVE_REHYDRATE_LAB_NOTE =
  "This card is the Archive / Rehydrate Lab foundation for later PS-031 / " +
  "PS-043 work. It is not the full lab yet: it surfaces the verified archive " +
  "and rehydrate values behind the golden run so the durable rehydrate story " +
  "is visible in one place. The full lab will add interactive archive / " +
  "rehydrate operations in a later slice.";

// ---------------------------------------------------------------------------
// Truth boundary + claim boundary.
// ---------------------------------------------------------------------------

// Canonical truth boundary text for the Failure-as-Proof Timeline. Written as
// a non-claim paragraph so the project's context-aware forbidden-claim
// scanners never flag the boundary terms as overclaims.
export const FAILURE_TIMELINE_TRUTH_BOUNDARY =
  "The Failure-as-Proof Timeline shows that the checked-in evidence " +
  "(PS-021, PS-024, PS-025, PS-026, PS-027, PS-028, PS-029) records a B2 " +
  "rehydrate proof with zero provider calls during rehydrate, agrees on the " +
  "golden run's identifiers, archive URI, and archive SHA-256, and records " +
  "rehydrate_source = b2_rehydrated. The timeline shows where captured " +
  "failures, retries, and fallbacks would appear if future evidence " +
  "captured them, but the verified golden run currently proves durable B2 " +
  "rehydrate with zero provider calls, and no actual provider failure or " +
  "fallback is claimed unless checked-in evidence proves it. The timeline " +
  "does not prove semantic truth, legal authenticity, C2PA authenticity, " +
  "or human authorship. The timeline does not prove Object Lock or " +
  "tamper-proof storage. The timeline did not fetch and hash the B2 object " +
  "in the browser. The local contract is verified; the public deployment " +
  "remains pending until the new backend is deployed and the public URL is " +
  "verified end-to-end.";

// Canonical claim boundary used by the timeline's "Claim boundary" section.
// Allowed claims are stated affirmatively; forbidden claims are stated as
// non-claims so the context-aware forbidden-claim scanners never flag the
// boundary terms as overclaims.
export const FAILURE_TIMELINE_CLAIM_BOUNDARY_ALLOWED: readonly string[] = [
  "Checked-in evidence records B2 rehydrate proof for the golden run.",
  "Checked-in evidence records zero provider calls during rehydrate.",
  "Checked-in evidence agrees on the archive URI and SHA-256.",
  "ProofStudio can present operational workflow steps as evidence-backed timeline entries.",
  "Future provider failures, retries, and fallbacks would be represented in this model if captured by evidence.",
];

export const FAILURE_TIMELINE_CLAIM_BOUNDARY_FORBIDDEN: readonly string[] = [
  "The timeline does not prove semantic truth of the media.",
  "The timeline does not prove legal authenticity.",
  "The timeline does not prove human authorship.",
  "The timeline does not prove C2PA authenticity.",
  "The timeline does not prove Object Lock or tamper-proof storage.",
  "The timeline did not fetch and hash the B2 object in the browser.",
  "The timeline does not claim an actual provider failure occurred unless evidence proves it.",
  "The timeline does not claim an actual fallback occurred unless evidence proves it.",
  "Public deployment has not been verified (it remains pending).",
];
