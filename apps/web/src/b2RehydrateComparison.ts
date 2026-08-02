// PS-029 B2 Rehydrate Comparison -- verified comparison constants.
//
// Every value in this module is sourced verbatim from the same checked-in
// evidence already used by PS-021 / PS-024 / PS-025 / PS-026 / PS-027 / PS-028:
//
//   - docs/evidence/demo/golden-demo-run.json                          (PS-024 golden manifest)
//   - docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json        (PS-021 live B2 durable rehydrate)
//   - docs/evidence/ps-025/public-durable-passport-unlock-smoke.json   (PS-025 public durable passport)
//   - docs/evidence/ps-026/b2-evidence-explorer-smoke.json             (PS-026 B2 Evidence Explorer)
//   - docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json          (PS-027 Genblaze Pipeline Graph)
//   - docs/evidence/ps-028/manifest-verification-panel-smoke.json      (PS-028 Manifest Verification Panel)
//
// The PS-029 smoke validates that every value below matches the source
// evidence exactly AND that every source agrees on the same value. No value
// is invented here.
//
// These constants exist so the B2 Rehydrate Comparison surface
// (apps/web/src/B2RehydrateComparison.tsx) can show the before/after
// rehydrate story (golden run -> B2 archive -> rehydrated evidence ->
// rehydrate result) without re-fetching the API on every render and without
// reading any B2 object. The comparison performs no network call, calls no
// provider, and reads no B2 object: it only renders verified, checked-in
// evidence.
//
// Truth boundary: the B2 Rehydrate Comparison shows that the checked-in
// evidence records a B2 rehydrate proof with zero provider calls during
// rehydrate, that the evidence agrees on the archive URI and SHA-256, and
// that the rehydrate uses durable archive evidence instead of a live provider
// rerun for the verified golden run. It does not prove semantic truth, legal
// authenticity, C2PA authenticity, or human authorship. The comparison does
// not prove Object Lock or tamper-proof storage. The comparison does not
// claim the browser fetched and hashed the B2 object. The local contract is
// verified; the public deployment remains pending until the new backend is
// deployed and the public URL is verified end-to-end.

// Verified golden demo run_id (PS-021 -> PS-024 -> PS-025 -> PS-026 -> PS-027 -> PS-028).
export const B2_REHYDRATE_COMPARISON_RUN_ID =
  "run_89d967f9000045efa22ed4cc78cfa67f";

// Verified golden demo campaign_id (PS-021 -> PS-024 -> PS-025 -> PS-026 -> PS-027 -> PS-028).
export const B2_REHYDRATE_COMPARISON_CAMPAIGN_ID =
  "camp_bea5161faa6244079d2ee01ce445c259";

// Verified Backblaze B2 archive URI for the golden demo run (PS-021).
export const B2_REHYDRATE_COMPARISON_ARCHIVE_URI =
  "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json";

// Verified SHA-256 of the B2 archive content for the golden demo run (PS-021).
export const B2_REHYDRATE_COMPARISON_ARCHIVE_SHA256 =
  "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141";

// Rehydrate source recorded by PS-021 (durable_source = b2_rehydrated).
export const B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE = "b2_rehydrated";

// PS-021 proved zero provider calls during B2 rehydrate.
export const B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE = 0;

// PS-021 proved no live provider call happened during B2 rehydrate.
export const B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE = true;

// Checked-in source evidence paths the comparison cross-references. These are
// the files the PS-029 smoke reads to verify every published value.
export const B2_REHYDRATE_COMPARISON_SOURCE_PS024_MANIFEST =
  "docs/evidence/demo/golden-demo-run.json";
export const B2_REHYDRATE_COMPARISON_SOURCE_PS021_EVIDENCE =
  "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json";
export const B2_REHYDRATE_COMPARISON_SOURCE_PS025_EVIDENCE =
  "docs/evidence/ps-025/public-durable-passport-unlock-smoke.json";
export const B2_REHYDRATE_COMPARISON_SOURCE_PS026_EVIDENCE =
  "docs/evidence/ps-026/b2-evidence-explorer-smoke.json";
export const B2_REHYDRATE_COMPARISON_SOURCE_PS027_EVIDENCE =
  "docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json";
export const B2_REHYDRATE_COMPARISON_SOURCE_PS028_EVIDENCE =
  "docs/evidence/ps-028/manifest-verification-panel-smoke.json";

// PS-025 local contract (FastAPI TestClient against a fresh empty store
// resolving the golden run_id from checked-in evidence) is verified.
export const B2_REHYDRATE_COMPARISON_LOCAL_CONTRACT_PROOF = true;

// PS-025: the public Render deployment is NOT verified for the golden passport
// unlock yet. The new backend code must be deployed and the public URL must
// be verified end-to-end before this flag is flipped. Surfacing this honestly
// in the comparison is required so a judge never reads "public deployment
// verified" when it has not been tested.
export const B2_REHYDRATE_COMPARISON_PUBLIC_DEPLOYMENT_PENDING = true;

// PS-026 unlock scope marker. Mirrors the backend
// `GOLDEN_DEMO_UNLOCK_SCOPE = "golden_demo_only"` so the comparison honestly
// reports the narrow allowlist (only this single run_id resolves publicly).
export const B2_REHYDRATE_COMPARISON_UNLOCK_SCOPE = "golden_demo_only";

// ---------------------------------------------------------------------------
// Required source list. The comparison cross-references all six sources.
// ---------------------------------------------------------------------------

export type B2RehydrateComparisonSourceKind =
  | "golden_manifest"
  | "b2_durable_evidence"
  | "passport_evidence"
  | "explorer_evidence"
  | "pipeline_evidence"
  | "manifest_panel_evidence";

export interface B2RehydrateComparisonSource {
  id: string;
  label: string;
  sliceTag: string;
  kind: B2RehydrateComparisonSourceKind;
  evidencePath: string;
}

export const B2_REHYDRATE_COMPARISON_SOURCES: readonly B2RehydrateComparisonSource[] =
  [
    {
      id: "ps024",
      label: "Golden demo manifest",
      sliceTag: "PS-024",
      kind: "golden_manifest",
      evidencePath: B2_REHYDRATE_COMPARISON_SOURCE_PS024_MANIFEST,
    },
    {
      id: "ps021",
      label: "PS-021 B2 durable rehydrate evidence",
      sliceTag: "PS-021",
      kind: "b2_durable_evidence",
      evidencePath: B2_REHYDRATE_COMPARISON_SOURCE_PS021_EVIDENCE,
    },
    {
      id: "ps025",
      label: "PS-025 public durable passport evidence",
      sliceTag: "PS-025",
      kind: "passport_evidence",
      evidencePath: B2_REHYDRATE_COMPARISON_SOURCE_PS025_EVIDENCE,
    },
    {
      id: "ps026",
      label: "PS-026 B2 Evidence Explorer evidence",
      sliceTag: "PS-026",
      kind: "explorer_evidence",
      evidencePath: B2_REHYDRATE_COMPARISON_SOURCE_PS026_EVIDENCE,
    },
    {
      id: "ps027",
      label: "PS-027 Genblaze Pipeline Graph evidence",
      sliceTag: "PS-027",
      kind: "pipeline_evidence",
      evidencePath: B2_REHYDRATE_COMPARISON_SOURCE_PS027_EVIDENCE,
    },
    {
      id: "ps028",
      label: "PS-028 Manifest Verification Panel evidence",
      sliceTag: "PS-028",
      kind: "manifest_panel_evidence",
      evidencePath: B2_REHYDRATE_COMPARISON_SOURCE_PS028_EVIDENCE,
    },
  ];

// ---------------------------------------------------------------------------
// Required field list. The comparison renders one row per field.
// ---------------------------------------------------------------------------

export type B2RehydrateComparisonFieldKey =
  | "run_id"
  | "campaign_id"
  | "archive_uri"
  | "archive_sha256"
  | "rehydrate_source"
  | "provider_calls_during_rehydrate"
  | "no_live_provider_call_during_rehydrate";

export type B2RehydrateComparisonFieldValue = string | number | boolean;

export interface B2RehydrateComparisonField {
  key: B2RehydrateComparisonFieldKey;
  label: string;
  // The verified golden value for this field. Sourced verbatim from the
  // PS-024 golden demo manifest, traced to PS-021.
  value: B2RehydrateComparisonFieldValue;
}

export const B2_REHYDRATE_COMPARISON_FIELDS: readonly B2RehydrateComparisonField[] =
  [
    {
      key: "run_id",
      label: "run_id",
      value: B2_REHYDRATE_COMPARISON_RUN_ID,
    },
    {
      key: "campaign_id",
      label: "campaign_id",
      value: B2_REHYDRATE_COMPARISON_CAMPAIGN_ID,
    },
    {
      key: "archive_uri",
      label: "archive_uri",
      value: B2_REHYDRATE_COMPARISON_ARCHIVE_URI,
    },
    {
      key: "archive_sha256",
      label: "archive_sha256",
      value: B2_REHYDRATE_COMPARISON_ARCHIVE_SHA256,
    },
    {
      key: "rehydrate_source",
      label: "rehydrate_source",
      value: B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE,
    },
    {
      key: "provider_calls_during_rehydrate",
      label: "provider_calls_during_rehydrate",
      value: B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE,
    },
    {
      key: "no_live_provider_call_during_rehydrate",
      label: "no_live_provider_call_during_rehydrate",
      value: B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
    },
  ];

// ---------------------------------------------------------------------------
// Cross-source verification matrix.
//
// For each (source, field) pair, the value as observed in that source's
// checked-in evidence. PS-021 records rehydrate_source under the key
// "durable_source" -- the matrix stores the canonical value here and the
// PS-029 smoke maps the source key name when verifying.
// ---------------------------------------------------------------------------

export const B2_REHYDRATE_COMPARISON_MATRIX: Readonly<
  Record<
    string,
    Partial<
      Record<
        B2RehydrateComparisonFieldKey,
        B2RehydrateComparisonFieldValue
      >
    >
  >
> = {
  ps024: {
    run_id: B2_REHYDRATE_COMPARISON_RUN_ID,
    campaign_id: B2_REHYDRATE_COMPARISON_CAMPAIGN_ID,
    archive_uri: B2_REHYDRATE_COMPARISON_ARCHIVE_URI,
    archive_sha256: B2_REHYDRATE_COMPARISON_ARCHIVE_SHA256,
    rehydrate_source: B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  },
  ps021: {
    run_id: B2_REHYDRATE_COMPARISON_RUN_ID,
    campaign_id: B2_REHYDRATE_COMPARISON_CAMPAIGN_ID,
    archive_uri: B2_REHYDRATE_COMPARISON_ARCHIVE_URI,
    archive_sha256: B2_REHYDRATE_COMPARISON_ARCHIVE_SHA256,
    rehydrate_source: B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  },
  ps025: {
    run_id: B2_REHYDRATE_COMPARISON_RUN_ID,
    campaign_id: B2_REHYDRATE_COMPARISON_CAMPAIGN_ID,
    archive_uri: B2_REHYDRATE_COMPARISON_ARCHIVE_URI,
    archive_sha256: B2_REHYDRATE_COMPARISON_ARCHIVE_SHA256,
    rehydrate_source: B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  },
  ps026: {
    run_id: B2_REHYDRATE_COMPARISON_RUN_ID,
    campaign_id: B2_REHYDRATE_COMPARISON_CAMPAIGN_ID,
    archive_uri: B2_REHYDRATE_COMPARISON_ARCHIVE_URI,
    archive_sha256: B2_REHYDRATE_COMPARISON_ARCHIVE_SHA256,
    rehydrate_source: B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  },
  ps027: {
    run_id: B2_REHYDRATE_COMPARISON_RUN_ID,
    campaign_id: B2_REHYDRATE_COMPARISON_CAMPAIGN_ID,
    archive_uri: B2_REHYDRATE_COMPARISON_ARCHIVE_URI,
    archive_sha256: B2_REHYDRATE_COMPARISON_ARCHIVE_SHA256,
    rehydrate_source: B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  },
  ps028: {
    run_id: B2_REHYDRATE_COMPARISON_RUN_ID,
    campaign_id: B2_REHYDRATE_COMPARISON_CAMPAIGN_ID,
    archive_uri: B2_REHYDRATE_COMPARISON_ARCHIVE_URI,
    archive_sha256: B2_REHYDRATE_COMPARISON_ARCHIVE_SHA256,
    rehydrate_source: B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  },
};

// Per-source evidence key used to read the value out of that source's JSON.
// PS-021 uses "durable_source" instead of "rehydrate_source"; every other
// source uses the canonical key.
export const B2_REHYDRATE_COMPARISON_SOURCE_KEY_OVERRIDES: Readonly<
  Record<string, Partial<Record<B2RehydrateComparisonFieldKey, string>>>
> = {
  ps021: {
    rehydrate_source: "durable_source",
  },
};

// ---------------------------------------------------------------------------
// Comparison columns.
//
// The comparison tells the before/after rehydrate story across four columns.
// Each column maps to one or more checked-in sources so a judge can read the
// rehydrate value as a narrative, not just a consistency table.
// ---------------------------------------------------------------------------

export interface B2RehydrateComparisonColumn {
  id: string;
  title: string;
  tag: string;
  story: string;
  sourceIds: readonly string[];
}

export const B2_REHYDRATE_COMPARISON_COLUMNS: readonly B2RehydrateComparisonColumn[] =
  [
    {
      id: "golden_manifest",
      title: "Golden run / manifest",
      tag: "what was pinned",
      story:
        "The PS-024 golden demo manifest pins one canonical run_id and its " +
        "verified durable values. This is the source of truth every other " +
        "column is compared against.",
      sourceIds: ["ps024"],
    },
    {
      id: "b2_archive",
      title: "B2 archive evidence",
      tag: "what was stored",
      story:
        "PS-021 proved the run archive was written to and read from a real " +
        "Backblaze B2 object behind explicit, default-off gates. PS-026 " +
        "surfaces the archive URI and SHA-256 as a first-class product " +
        "surface.",
      sourceIds: ["ps021", "ps026"],
    },
    {
      id: "rehydrated",
      title: "Rehydrated evidence",
      tag: "what came back",
      story:
        "PS-025 unlocked a narrow public durable passport path for this run " +
        "from checked-in evidence. PS-027 carried the rehydrate values " +
        "through the pipeline graph. The rehydrate produced the same run " +
        "identity and archive digest as the pinned golden run.",
      sourceIds: ["ps025", "ps027"],
    },
    {
      id: "rehydrate_result",
      title: "Rehydrate result",
      tag: "the verdict",
      story:
        "PS-028 verified manifest field consistency across every source. " +
        "The rehydrate result: same run_id, same campaign_id, same archive " +
        "URI, same archive SHA-256, rehydrate_source = b2_rehydrated, zero " +
        "provider calls during rehydrate, and no live provider call during " +
        "rehydrate. No live provider rerun was required for rehydrate.",
      sourceIds: ["ps028"],
    },
  ];

// ---------------------------------------------------------------------------
// Truth boundary + claim boundary.
// ---------------------------------------------------------------------------

// Canonical truth boundary text for the B2 Rehydrate Comparison. Written as a
// non-claim paragraph so the project's context-aware forbidden-claim scanners
// never flag the boundary terms as overclaims.
export const B2_REHYDRATE_COMPARISON_TRUTH_BOUNDARY =
  "The B2 Rehydrate Comparison shows that the checked-in evidence " +
  "(PS-021, PS-024, PS-025, PS-026, PS-027, PS-028) records a B2 rehydrate " +
  "proof with zero provider calls during rehydrate, agrees on the golden " +
  "run's identifiers, archive URI, and archive SHA-256, and records " +
  "rehydrate_source = b2_rehydrated. It does not prove semantic truth, " +
  "legal authenticity, C2PA authenticity, or human authorship. The " +
  "comparison does not prove Object Lock or tamper-proof storage. The " +
  "comparison did not fetch and hash the B2 object in the browser. The " +
  "local contract is verified; the public deployment remains pending until " +
  "the new backend is deployed and the public URL is verified end-to-end.";

// Canonical claim boundary used by the comparison's "Claim boundary" section.
// Allowed claims are stated affirmatively; forbidden claims are stated as
// non-claims so the context-aware forbidden-claim scanners never flag the
// boundary terms as overclaims.
export const B2_REHYDRATE_CLAIM_BOUNDARY_ALLOWED: readonly string[] = [
  "Checked-in evidence records B2 rehydrate proof for the golden run.",
  "Checked-in evidence records zero provider calls during rehydrate.",
  "Checked-in evidence agrees on the archive URI and SHA-256.",
  "Rehydrate uses durable archive evidence instead of a live provider rerun for the verified golden run.",
];

export const B2_REHYDRATE_CLAIM_BOUNDARY_FORBIDDEN: readonly string[] = [
  "The comparison does not prove semantic truth of the media.",
  "The comparison does not prove legal authenticity.",
  "The comparison does not prove human authorship.",
  "The comparison does not prove C2PA authenticity.",
  "The comparison does not prove Object Lock or tamper-proof storage.",
  "The comparison did not fetch and hash the B2 object in the browser.",
  "Public deployment has not been verified (it remains pending).",
];

// ---------------------------------------------------------------------------
// No-provider-rerun story.
//
// A short, judge-readable explanation of why the rehydrate required no live
// provider rerun. Surfaced as a dedicated section so the B2 value (durability
// without provider availability) is visible at a glance.
// ---------------------------------------------------------------------------

export const B2_REHYDRATE_NO_PROVIDER_RERUN_STORY =
  "PS-021 proved the golden run can be rehydrated from B2 archive content " +
  "after backend memory loss. The checked-in evidence records " +
  "provider_calls_during_rehydrate = 0 and " +
  "no_live_provider_call_during_rehydrate = true. That means the rehydrate " +
  "path used the durable Backblaze B2 archive evidence instead of calling " +
  "any media provider again. B2 is what makes the rehydrate durable: the " +
  "run archive, not a fresh provider call, is the system of record for " +
  "this verified golden run.";
