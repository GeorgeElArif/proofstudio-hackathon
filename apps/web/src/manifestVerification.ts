// PS-028 Manifest Verification Panel -- verified cross-source constants.
//
// Every value in this module is sourced verbatim from the same checked-in
// evidence already used by PS-021 / PS-024 / PS-025 / PS-026 / PS-027:
//
//   - docs/evidence/demo/golden-demo-run.json                          (PS-024 golden manifest)
//   - docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json        (PS-021 live B2 durable rehydrate)
//   - docs/evidence/ps-025/public-durable-passport-unlock-smoke.json   (PS-025 public durable passport)
//   - docs/evidence/ps-026/b2-evidence-explorer-smoke.json             (PS-026 B2 Evidence Explorer)
//   - docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json          (PS-027 Genblaze Pipeline Graph)
//
// The PS-028 smoke validates that every value below matches the source
// evidence exactly AND that every source agrees on the same value. No value
// is invented here.
//
// These constants exist so the Manifest Verification Panel
// (apps/web/src/ManifestVerificationPanel.tsx) can surface a cross-source
// consistency table without re-fetching the API on every render and without
// reading any B2 object. The panel performs no network call, calls no
// provider, and reads no B2 object: it only renders verified, checked-in
// evidence.
//
// Truth boundary: the Manifest Verification Panel shows that the checked-in
// evidence agrees on the golden run's identifiers, archive URI, archive
// SHA-256, rehydrate source, zero provider calls during rehydrate, and the
// no-live-provider-call flag. It does not prove semantic truth, legal
// authenticity, C2PA authenticity, or human authorship. The panel does not
// prove Object Lock or tamper-proof storage. The panel does not claim the
// browser fetched and hashed the B2 object. The local contract is verified;
// the public deployment remains pending until the new backend is deployed
// and the public URL is verified end-to-end.

// Verified golden demo run_id (PS-021 -> PS-024 -> PS-025 -> PS-026 -> PS-027).
export const MANIFEST_VERIFICATION_RUN_ID =
  "run_89d967f9000045efa22ed4cc78cfa67f";

// Verified golden demo campaign_id (PS-021 -> PS-024 -> PS-025 -> PS-026 -> PS-027).
export const MANIFEST_VERIFICATION_CAMPAIGN_ID =
  "camp_bea5161faa6244079d2ee01ce445c259";

// Verified Backblaze B2 archive URI for the golden demo run (PS-021).
export const MANIFEST_VERIFICATION_ARCHIVE_URI =
  "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json";

// Verified SHA-256 of the B2 archive content for the golden demo run (PS-021).
export const MANIFEST_VERIFICATION_ARCHIVE_SHA256 =
  "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141";

// Rehydrate source recorded by PS-021 (durable_source = b2_rehydrated).
export const MANIFEST_VERIFICATION_REHYDRATE_SOURCE = "b2_rehydrated";

// PS-021 proved zero provider calls during B2 rehydrate.
export const MANIFEST_VERIFICATION_PROVIDER_CALLS_DURING_REHYDRATE = 0;

// PS-021 proved no live provider call happened during B2 rehydrate.
export const MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE = true;

// Checked-in source evidence paths the panel cross-references. These are the
// files the PS-028 smoke reads to verify every published value.
export const MANIFEST_VERIFICATION_SOURCE_PS024_MANIFEST =
  "docs/evidence/demo/golden-demo-run.json";
export const MANIFEST_VERIFICATION_SOURCE_PS021_EVIDENCE =
  "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json";
export const MANIFEST_VERIFICATION_SOURCE_PS025_EVIDENCE =
  "docs/evidence/ps-025/public-durable-passport-unlock-smoke.json";
export const MANIFEST_VERIFICATION_SOURCE_PS026_EVIDENCE =
  "docs/evidence/ps-026/b2-evidence-explorer-smoke.json";
export const MANIFEST_VERIFICATION_SOURCE_PS027_EVIDENCE =
  "docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json";

// PS-025 local contract (FastAPI TestClient against a fresh empty store
// resolving the golden run_id from checked-in evidence) is verified.
export const MANIFEST_VERIFICATION_LOCAL_CONTRACT_PROOF = true;

// PS-025: the public Render deployment is NOT verified for the golden passport
// unlock yet. The new backend code must be deployed and the public URL must
// be verified end-to-end before this flag is flipped. Surfacing this honestly
// in the panel is required so a judge never reads "public deployment verified"
// when it has not been tested.
export const MANIFEST_VERIFICATION_PUBLIC_DEPLOYMENT_PENDING = true;

// PS-026 unlock scope marker. Mirrors the backend
// `GOLDEN_DEMO_UNLOCK_SCOPE = "golden_demo_only"` so the panel honestly
// reports the narrow allowlist (only this single run_id resolves publicly).
export const MANIFEST_VERIFICATION_UNLOCK_SCOPE = "golden_demo_only";

// ---------------------------------------------------------------------------
// Required source list. The panel renders one column per source.
// ---------------------------------------------------------------------------

export type ManifestSourceKind =
  | "golden_manifest"
  | "b2_durable_evidence"
  | "passport_evidence"
  | "explorer_evidence"
  | "pipeline_evidence";

export interface ManifestVerificationSource {
  id: string;
  label: string;
  sliceTag: string;
  kind: ManifestSourceKind;
  evidencePath: string;
}

export const MANIFEST_VERIFICATION_SOURCES: readonly ManifestVerificationSource[] =
  [
    {
      id: "ps024",
      label: "Golden demo manifest",
      sliceTag: "PS-024",
      kind: "golden_manifest",
      evidencePath: MANIFEST_VERIFICATION_SOURCE_PS024_MANIFEST,
    },
    {
      id: "ps021",
      label: "PS-021 B2 durable rehydrate evidence",
      sliceTag: "PS-021",
      kind: "b2_durable_evidence",
      evidencePath: MANIFEST_VERIFICATION_SOURCE_PS021_EVIDENCE,
    },
    {
      id: "ps025",
      label: "PS-025 public durable passport evidence",
      sliceTag: "PS-025",
      kind: "passport_evidence",
      evidencePath: MANIFEST_VERIFICATION_SOURCE_PS025_EVIDENCE,
    },
    {
      id: "ps026",
      label: "PS-026 B2 Evidence Explorer evidence",
      sliceTag: "PS-026",
      kind: "explorer_evidence",
      evidencePath: MANIFEST_VERIFICATION_SOURCE_PS026_EVIDENCE,
    },
    {
      id: "ps027",
      label: "PS-027 Genblaze Pipeline Graph evidence",
      sliceTag: "PS-027",
      kind: "pipeline_evidence",
      evidencePath: MANIFEST_VERIFICATION_SOURCE_PS027_EVIDENCE,
    },
  ];

// ---------------------------------------------------------------------------
// Required field list. The panel renders one row per field.
// ---------------------------------------------------------------------------

export type ManifestVerificationFieldKey =
  | "run_id"
  | "campaign_id"
  | "archive_uri"
  | "archive_sha256"
  | "rehydrate_source"
  | "provider_calls_during_rehydrate"
  | "no_live_provider_call_during_rehydrate";

export type ManifestFieldValue = string | number | boolean;

export interface ManifestVerificationField {
  key: ManifestVerificationFieldKey;
  label: string;
  // The verified golden value for this field. Sourced verbatim from the
  // PS-024 golden demo manifest, traced to PS-021.
  value: ManifestFieldValue;
}

export const MANIFEST_VERIFICATION_FIELDS: readonly ManifestVerificationField[] =
  [
    {
      key: "run_id",
      label: "run_id",
      value: MANIFEST_VERIFICATION_RUN_ID,
    },
    {
      key: "campaign_id",
      label: "campaign_id",
      value: MANIFEST_VERIFICATION_CAMPAIGN_ID,
    },
    {
      key: "archive_uri",
      label: "archive_uri",
      value: MANIFEST_VERIFICATION_ARCHIVE_URI,
    },
    {
      key: "archive_sha256",
      label: "archive_sha256",
      value: MANIFEST_VERIFICATION_ARCHIVE_SHA256,
    },
    {
      key: "rehydrate_source",
      label: "rehydrate_source",
      value: MANIFEST_VERIFICATION_REHYDRATE_SOURCE,
    },
    {
      key: "provider_calls_during_rehydrate",
      label: "provider_calls_during_rehydrate",
      value: MANIFEST_VERIFICATION_PROVIDER_CALLS_DURING_REHYDRATE,
    },
    {
      key: "no_live_provider_call_during_rehydrate",
      label: "no_live_provider_call_during_rehydrate",
      value: MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
    },
  ];

// ---------------------------------------------------------------------------
// Cross-source verification matrix.
//
// For each (source, field) pair, the value as observed in that source's
// checked-in evidence. PS-021 records rehydrate_source under the key
// "durable_source" -- the matrix stores the canonical value here and the
// PS-028 smoke maps the source key name when verifying.
// ---------------------------------------------------------------------------

export const MANIFEST_VERIFICATION_MATRIX: Readonly<
  Record<string, Partial<Record<ManifestVerificationFieldKey, ManifestFieldValue>>>
> = {
  ps024: {
    run_id: MANIFEST_VERIFICATION_RUN_ID,
    campaign_id: MANIFEST_VERIFICATION_CAMPAIGN_ID,
    archive_uri: MANIFEST_VERIFICATION_ARCHIVE_URI,
    archive_sha256: MANIFEST_VERIFICATION_ARCHIVE_SHA256,
    rehydrate_source: MANIFEST_VERIFICATION_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      MANIFEST_VERIFICATION_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  },
  ps021: {
    run_id: MANIFEST_VERIFICATION_RUN_ID,
    campaign_id: MANIFEST_VERIFICATION_CAMPAIGN_ID,
    archive_uri: MANIFEST_VERIFICATION_ARCHIVE_URI,
    archive_sha256: MANIFEST_VERIFICATION_ARCHIVE_SHA256,
    rehydrate_source: MANIFEST_VERIFICATION_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      MANIFEST_VERIFICATION_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  },
  ps025: {
    run_id: MANIFEST_VERIFICATION_RUN_ID,
    campaign_id: MANIFEST_VERIFICATION_CAMPAIGN_ID,
    archive_uri: MANIFEST_VERIFICATION_ARCHIVE_URI,
    archive_sha256: MANIFEST_VERIFICATION_ARCHIVE_SHA256,
    rehydrate_source: MANIFEST_VERIFICATION_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      MANIFEST_VERIFICATION_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  },
  ps026: {
    run_id: MANIFEST_VERIFICATION_RUN_ID,
    campaign_id: MANIFEST_VERIFICATION_CAMPAIGN_ID,
    archive_uri: MANIFEST_VERIFICATION_ARCHIVE_URI,
    archive_sha256: MANIFEST_VERIFICATION_ARCHIVE_SHA256,
    rehydrate_source: MANIFEST_VERIFICATION_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      MANIFEST_VERIFICATION_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  },
  ps027: {
    run_id: MANIFEST_VERIFICATION_RUN_ID,
    campaign_id: MANIFEST_VERIFICATION_CAMPAIGN_ID,
    archive_uri: MANIFEST_VERIFICATION_ARCHIVE_URI,
    archive_sha256: MANIFEST_VERIFICATION_ARCHIVE_SHA256,
    rehydrate_source: MANIFEST_VERIFICATION_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      MANIFEST_VERIFICATION_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  },
};

// Per-source evidence key used to read the value out of that source's JSON.
// PS-021 uses "durable_source" instead of "rehydrate_source"; every other
// source uses the canonical key.
export const MANIFEST_VERIFICATION_SOURCE_KEY_OVERRIDES: Readonly<
  Record<string, Partial<Record<ManifestVerificationFieldKey, string>>>
> = {
  ps021: {
    rehydrate_source: "durable_source",
  },
};

// ---------------------------------------------------------------------------
// Truth boundary + claim boundary.
// ---------------------------------------------------------------------------

// Canonical truth boundary text for the Manifest Verification Panel. Written
// as a non-claim paragraph so the project's context-aware forbidden-claim
// scanners never flag the boundary terms as overclaims.
export const MANIFEST_VERIFICATION_TRUTH_BOUNDARY =
  "The Manifest Verification Panel shows that the checked-in evidence " +
  "(PS-021, PS-024, PS-025, PS-026, PS-027) agrees on the golden run's " +
  "identifiers, archive URI, archive SHA-256, rehydrate source, zero " +
  "provider calls during rehydrate, and the no-live-provider-call flag. It " +
  "does not prove semantic truth, legal authenticity, C2PA authenticity, or " +
  "human authorship. The panel does not prove Object Lock or tamper-proof " +
  "storage. The panel does not claim the browser fetched and hashed the B2 " +
  "object. The local contract is verified; the public deployment remains " +
  "pending until the new backend is deployed and the public URL is verified " +
  "end-to-end.";

// Canonical claim boundary used by the panel's "Claim boundary" section.
// Allowed claims are stated affirmatively; forbidden claims are stated as
// non-claims so the context-aware forbidden-claim scanners never flag the
// boundary terms as overclaims.
export const MANIFEST_CLAIM_BOUNDARY_ALLOWED: readonly string[] = [
  "Checked-in evidence agrees on golden run identifiers (run_id, campaign_id).",
  "Checked-in evidence agrees on the archive URI and SHA-256.",
  "Checked-in evidence records rehydrate_source = b2_rehydrated.",
  "Checked-in evidence records provider_calls_during_rehydrate = 0.",
];

export const MANIFEST_CLAIM_BOUNDARY_FORBIDDEN: readonly string[] = [
  "The panel does not prove semantic truth of the media.",
  "The panel does not prove legal authenticity.",
  "The panel does not prove human authorship.",
  "The panel does not prove C2PA authenticity.",
  "The panel does not prove Object Lock or tamper-proof storage.",
  "The panel did not fetch and hash the B2 object in the browser.",
  "Public deployment has not been verified (it remains pending).",
];
