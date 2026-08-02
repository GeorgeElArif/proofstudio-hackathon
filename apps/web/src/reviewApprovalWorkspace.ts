// PS-035 Review + Approval Workspace -- verified constants + local data.
//
// Every golden value in this module is sourced verbatim from the same
// checked-in evidence already used by PS-021 / PS-024 / PS-025 / PS-026 /
// PS-027 / PS-028 / PS-029 / PS-030 / PS-031 / PS-032 / PS-033 / PS-034:
//
//   - docs/evidence/demo/golden-demo-run.json                          (PS-024 golden manifest)
//   - docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json        (PS-021 live B2 durable rehydrate)
//
// The PS-035 smoke validates that every published value below matches the
// golden manifest exactly. No value is invented here.
//
// HONESTY RULE: the checked-in evidence records the campaign_id, run_id,
// archive_uri, archive_sha256, manifest_uri, manifest_hash, rehydrate_source,
// provider_calls_during_rehydrate (0), no_live_provider_call_during_rehydrate
// (true), and public_deployment_pending (true) for the single verified golden
// run. It does NOT record a captured provider/model for the golden asset, the
// raw media bytes, the asset size, or a human reviewer identity. PS-035
// therefore does NOT invent any of those: it marks them "not captured in
// checked-in evidence". PS-035 does not fabricate a verified status, a manifest
// hash, an archive URI, or a reviewer identity that is not in accepted data.
//
// The workspace is purely client-side by default: it reads no B2 object, calls
// no provider, exposes no arbitrary run_id input for live execution, and
// performs no browser-side B2 byte verification. It only renders verified,
// checked-in evidence plus an in-session review ledger.
//
// Truth boundary: approval means "approved by this workflow / demo UI". It does
// not prove semantic truth, legal authenticity, C2PA authenticity, human
// authorship, Object Lock / tamper-proof storage, or production security. The
// review ledger is local / in-session in this slice; it is not durable,
// tamper-proof, replicated, or production-multi-user. The local contract is
// verified; the public deployment remains pending until the new backend is
// deployed and the public URL is verified end-to-end.

// Verified golden demo run_id (PS-021 -> PS-024 -> PS-025 -> ...).
export const REVIEW_APPROVAL_WORKSPACE_RUN_ID =
  "run_89d967f9000045efa22ed4cc78cfa67f";

// Verified golden demo campaign_id.
export const REVIEW_APPROVAL_WORKSPACE_CAMPAIGN_ID =
  "camp_bea5161faa6244079d2ee01ce445c259";

// Verified Backblaze B2 archive URI for the golden demo run (PS-021).
export const REVIEW_APPROVAL_WORKSPACE_ARCHIVE_URI =
  "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json";

// Verified SHA-256 of the B2 archive content for the golden demo run (PS-021).
export const REVIEW_APPROVAL_WORKSPACE_ARCHIVE_SHA256 =
  "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141";

// Verified manifest URI for the golden demo run (PS-035a checked-in fixture).
export const REVIEW_APPROVAL_WORKSPACE_MANIFEST_URI =
  "docs/evidence/ps-035a/manifest-fixture.json";

// Verified manifest hash (64-hex) for the golden demo run (PS-035a).
export const REVIEW_APPROVAL_WORKSPACE_MANIFEST_HASH =
  "438fabca46481a232373067eedb6d0e3a684c8ed513410dfe2047e3b4950022f";

// Rehydrate source recorded by PS-021 (durable_source = b2_rehydrated).
export const REVIEW_APPROVAL_WORKSPACE_REHYDRATE_SOURCE = "b2_rehydrated";

// PS-021 proved zero provider calls during B2 rehydrate.
export const REVIEW_APPROVAL_WORKSPACE_PROVIDER_CALLS_DURING_REHYDRATE = 0;

// PS-021 proved no live provider call happened during B2 rehydrate.
export const REVIEW_APPROVAL_WORKSPACE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE =
  true;

// PS-025: the public Render deployment is NOT verified yet.
export const REVIEW_APPROVAL_WORKSPACE_PUBLIC_DEPLOYMENT_PENDING = true;

// Workspace identity. The workspace_id is deterministic (not a random UUID):
// derived from the verified golden run_id and the workspace version, so the
// same golden run always yields the same workspace_id.
export const REVIEW_APPROVAL_WORKSPACE_ID =
  "review_approval_workspace_ps035_" + REVIEW_APPROVAL_WORKSPACE_RUN_ID;

// Workspace schema version. Bumped on any shape change.
export const REVIEW_APPROVAL_WORKSPACE_VERSION = "1.0.0";

// ---------------------------------------------------------------------------
// Review state lifecycle (spec section 10.2). The required four states.
// ---------------------------------------------------------------------------

export type ReviewState =
  | "pending_review"
  | "approved"
  | "rejected"
  | "needs_changes";

export interface ReviewStateDef {
  value: ReviewState;
  label: string;
  tone: "ok" | "warn" | "danger" | "info" | "neutral";
}

export const REVIEW_APPROVAL_WORKSPACE_STATES: readonly ReviewStateDef[] = [
  {
    value: "pending_review",
    label: "Pending Review",
    tone: "info",
  },
  {
    value: "approved",
    label: "Approved",
    tone: "ok",
  },
  {
    value: "rejected",
    label: "Rejected",
    tone: "danger",
  },
  {
    value: "needs_changes",
    label: "Needs Changes",
    tone: "warn",
  },
];

export function reviewStateLabel(value: ReviewState): string {
  for (const def of REVIEW_APPROVAL_WORKSPACE_STATES) {
    if (def.value === value) return def.label;
  }
  return value;
}

export function reviewStateTone(
  value: ReviewState,
): ReviewStateDef["tone"] {
  for (const def of REVIEW_APPROVAL_WORKSPACE_STATES) {
    if (def.value === value) return def.tone;
  }
  return "neutral";
}

// ---------------------------------------------------------------------------
// Reason taxonomy (spec section 10.3). Derived from the master spec review
// reasons (master spec section 3.9).
// ---------------------------------------------------------------------------

export type ReasonCategory =
  | "brand_mismatch"
  | "wrong_aspect_ratio"
  | "too_generic"
  | "compliance_issue"
  | "weak_quality"
  | "provider_failure"
  | "needs_disclosure"
  | "ready_for_export";

export interface ReasonCategoryDef {
  value: ReasonCategory;
  label: string;
}

export const REVIEW_APPROVAL_WORKSPACE_REASON_CATEGORIES: readonly ReasonCategoryDef[] =
  [
    { value: "brand_mismatch", label: "Brand mismatch" },
    { value: "wrong_aspect_ratio", label: "Wrong aspect ratio" },
    { value: "too_generic", label: "Too generic" },
    { value: "compliance_issue", label: "Compliance issue" },
    { value: "weak_quality", label: "Weak quality" },
    { value: "provider_failure", label: "Provider failure" },
    { value: "needs_disclosure", label: "Needs disclosure" },
    { value: "ready_for_export", label: "Ready for export" },
  ];

// ---------------------------------------------------------------------------
// Reviewable item shape (spec section 12.2). Sourced read-only from accepted
// data. A single reviewable item is the golden-run archive / asset.
// ---------------------------------------------------------------------------

export interface ReviewProofLink {
  available: boolean;
  label: string;
  href: string | null;
  status: string;
  detail: string | null;
}

export interface ReviewableAssetSummary {
  kind: string;
  provider: string | null;
  model: string | null;
  mediaType: string | null;
  sizeBytes: number | null;
  sha256: string | null;
  url: string | null;
}

export interface ReviewableProofSummary {
  provenancePassport: ReviewProofLink;
  manifestVerification: ReviewProofLink;
  b2Evidence: ReviewProofLink;
  rehydrate: ReviewProofLink;
  exportPack: ReviewProofLink;
}

export interface ReviewableItem {
  itemId: string;
  runId: string;
  campaignId: string;
  initialState: ReviewState;
  assetSummary: ReviewableAssetSummary;
  proofSummary: ReviewableProofSummary;
}

const GOLDEN_PASSPORT_HREF =
  "/passport/" + REVIEW_APPROVAL_WORKSPACE_RUN_ID;

export const REVIEW_APPROVAL_WORKSPACE_ITEMS: readonly ReviewableItem[] = [
  {
    itemId: REVIEW_APPROVAL_WORKSPACE_RUN_ID,
    runId: REVIEW_APPROVAL_WORKSPACE_RUN_ID,
    campaignId: REVIEW_APPROVAL_WORKSPACE_CAMPAIGN_ID,
    initialState: "pending_review",
    assetSummary: {
      kind: "run archive",
      // provider / model for the golden asset are not captured in checked-in
      // evidence; recorded honestly as not available.
      provider: null,
      model: null,
      // The golden archive content is a JSON run archive, not raw media bytes.
      mediaType: "application/json",
      // The asset size is not captured in checked-in evidence.
      sizeBytes: null,
      sha256: REVIEW_APPROVAL_WORKSPACE_ARCHIVE_SHA256,
      url: REVIEW_APPROVAL_WORKSPACE_ARCHIVE_URI,
    },
    proofSummary: {
      provenancePassport: {
        available: true,
        label: "Provenance Passport",
        href: GOLDEN_PASSPORT_HREF,
        status: "available",
        detail: "Golden-run provenance passport (PS-019 / PS-025).",
      },
      manifestVerification: {
        available: true,
        label: "Manifest Verification",
        href: "/manifest-verification",
        status: "available",
        detail:
          "manifest_uri + 64-hex manifest_hash recorded (PS-035a checked-in fixture).",
      },
      b2Evidence: {
        available: true,
        label: "B2 Evidence",
        href: "/b2-evidence",
        status: "available",
        detail: "archive_uri + archive SHA-256 recorded (PS-021).",
      },
      rehydrate: {
        available: true,
        label: "Rehydrate",
        href: "/b2-rehydrate-comparison",
        status: "available",
        detail:
          "rehydrate_source = b2_rehydrated, provider_calls_during_rehydrate = 0 (PS-021).",
      },
      exportPack: {
        available: true,
        label: "Export Pack",
        href: "/evidence-pack",
        status: "available",
        detail: "Judge Evidence Pack (PS-031).",
      },
    },
  },
];

// ---------------------------------------------------------------------------
// Decision record shape (spec section 12.3). PS-035-owned local data.
// JSON-serializable; lives only in the in-session ledger.
// ---------------------------------------------------------------------------

export interface ReviewDecisionRecord {
  itemId: string;
  decisionState: ReviewState;
  reasonCategory: ReasonCategory | null;
  rationale: string;
  notes: string;
  reviewerLabel: string | null;
  recordedAt: string;
}

export function emptyDecisionStateMap(
  items: readonly ReviewableItem[],
): Record<string, ReviewState> {
  const out: Record<string, ReviewState> = {};
  for (const item of items) out[item.itemId] = item.initialState;
  return out;
}

// ---------------------------------------------------------------------------
// Boundary message (spec section 11). Persistent and verbatim-equivalent.
// Written as non-claim copy so the project's forbidden-claim scanners never
// flag the boundary terms.
// ---------------------------------------------------------------------------

export const REVIEW_APPROVAL_WORKSPACE_BOUNDARY_MESSAGE =
  "Approval records the reviewer's workflow decision; it does not prove " +
  "semantic truth, legal authenticity, C2PA authenticity, human authorship, " +
  "Object Lock / tamper-proof storage, or production security. The review " +
  "ledger is local / in-session in this slice; it is not durable, " +
  "tamper-proof, replicated, or production-multi-user. The workspace reads " +
  "no B2 object, calls no provider, and performs no browser-side B2 byte " +
  "verification. The local contract is verified; the public deployment " +
  "remains pending until the new backend is deployed and the public URL is " +
  "verified end-to-end.";

// Canonical truth-boundary terms the workspace must surface (spec section 16).
export const REVIEW_APPROVAL_WORKSPACE_TRUTH_BOUNDARY_TERMS: readonly string[] =
  [
    "does not prove semantic truth",
    "does not prove legal authenticity",
    "does not prove C2PA authenticity",
    "does not prove human authorship",
    "does not prove Object Lock",
    "does not prove production security",
  ];

// Allowed / forbidden claim boundary (mirrors the project's claim-boundary
// convention).
export const REVIEW_APPROVAL_WORKSPACE_CLAIM_BOUNDARY_ALLOWED: readonly string[] =
  [
    "Approval records the reviewer's workflow decision in this demo UI.",
    "The review ledger captures reviewer, decision, rationale, and notes.",
    "Proof links summarize checked-in evidence already captured by the pipeline.",
    "The workspace works offline from local / golden / demo data.",
  ];

export const REVIEW_APPROVAL_WORKSPACE_CLAIM_BOUNDARY_FORBIDDEN: readonly string[] =
  [
    "Approval does not prove semantic truth.",
    "Approval does not prove legal authenticity.",
    "Approval does not prove C2PA authenticity.",
    "Approval does not prove human authorship.",
    "Approval does not prove Object Lock or tamper-proof storage.",
    "Approval does not prove production security.",
    "The review ledger is not durable, tamper-proof, or replicated.",
    "The workspace did not fetch and hash the B2 object in the browser.",
    "The workspace performs no browser-side B2 byte verification.",
    "Public deployment has not been verified (it remains pending).",
  ];

// Limitations. Required to be visible.
export const REVIEW_APPROVAL_WORKSPACE_LIMITATIONS: readonly string[] = [
  "The review ledger is local / in-session. Closing the tab clears it; this " +
    "slice does not implement durable review storage.",
  "The ledger is not tamper-proof, not replicated, and not production " +
    "multi-user. PS-035 does not claim enterprise review / approval workflow.",
  "The reviewer label is free text and optional; PS-035 does not implement " +
    "auth or identity verification.",
  "The workspace reads no B2 object and performs no browser-side B2 byte " +
    "verification. Proof links summarize checked-in evidence, not a live read.",
  "No provider is called and no live B2 read or write occurs.",
  "The recorded timestamp is the local clock; it is not synchronized or " +
    "tamper-evident.",
];

// Required workspace sections. The component renders one block per section so
// the PS-035 smoke can verify each is visible by id / heading.
export const REVIEW_APPROVAL_WORKSPACE_REQUIRED_SECTIONS: readonly string[] =
  [
    "Reviewable items",
    "Asset / media summary",
    "Proof / evidence summary",
    "Reviewer decision",
    "Review ledger",
    "Boundary",
    "Limitations",
  ];
