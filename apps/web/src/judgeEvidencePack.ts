// PS-031 Export Campaign Pack v2 / Judge Evidence Pack -- verified pack
// constants.
//
// Every golden value in this module is sourced verbatim from the same
// checked-in evidence already used by PS-021 / PS-024 / PS-025 / PS-026 /
// PS-027 / PS-028 / PS-029 / PS-030:
//
//   - docs/evidence/demo/golden-demo-run.json                          (PS-024 golden manifest)
//   - docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json        (PS-021 live B2 durable rehydrate)
//   - docs/evidence/ps-025/public-durable-passport-unlock-smoke.json   (PS-025 public durable passport)
//   - docs/evidence/ps-026/b2-evidence-explorer-smoke.json             (PS-026 B2 Evidence Explorer)
//   - docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json          (PS-027 Genblaze Pipeline Graph)
//   - docs/evidence/ps-028/manifest-verification-panel-smoke.json      (PS-028 Manifest Verification Panel)
//   - docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json          (PS-029 B2 Rehydrate Comparison)
//   - docs/evidence/ps-030/failure-as-proof-timeline-smoke.json        (PS-030 Failure-as-Proof Timeline)
//
// The PS-031 smoke validates that every value below matches the source
// evidence exactly AND that every source agrees on the same value. No value
// is invented here.
//
// These constants exist so the Judge Evidence Pack surface
// (apps/web/src/JudgeEvidencePack.tsx) can assemble a portable proof summary
// (pack identity, campaign/run identity, final asset/archive summary, prompt
// /generation evidence summary, provider/model/attempt ledger summary, B2
// archive evidence, Genblaze manifest evidence, B2 rehydrate proof,
// Failure-as-Proof summary, public passport link, review/approval status,
// disclosure readiness notes, truth boundary, limitations, next actions)
// without re-fetching the API on every render, without reading any B2
// object, and without calling any provider. The pack performs no network
// call, calls no provider, and reads no B2 object: it only renders verified,
// checked-in evidence plus deterministic local browser exports (JSON + a
// README/Markdown text).
//
// Truth boundary: the Judge Evidence Pack shows that the checked-in evidence
// (PS-021, PS-024, PS-025, PS-026, PS-027, PS-028, PS-029, PS-030) records a
// B2 rehydrate proof with zero provider calls during rehydrate, agrees on the
// golden run's identifiers, archive URI, and archive SHA-256, and records
// rehydrate_source = b2_rehydrated. The pack is generated from local
// checked-in ProofStudio evidence. The pack does not prove semantic truth,
// legal authenticity, C2PA authenticity, or human authorship. The pack does
// not prove Object Lock or tamper-proof storage. The pack did not fetch and
// hash the B2 object in the browser. The pack does not include raw media
// bytes (the B2 archive content is a JSON run archive, not the raw media).
// The pack does not produce a zip export (zip generation is not implemented).
// The local contract is verified; the public deployment remains pending until
// the new backend is deployed and the public URL is verified end-to-end.

// Verified golden demo run_id (PS-021 -> PS-024 -> PS-025 -> PS-026 -> PS-027
// -> PS-028 -> PS-029 -> PS-030).
export const JUDGE_EVIDENCE_PACK_RUN_ID =
  "run_89d967f9000045efa22ed4cc78cfa67f";

// Verified golden demo campaign_id (PS-021 -> PS-024 -> PS-025 -> PS-026 ->
// PS-027 -> PS-028 -> PS-029 -> PS-030).
export const JUDGE_EVIDENCE_PACK_CAMPAIGN_ID =
  "camp_bea5161faa6244079d2ee01ce445c259";

// Verified Backblaze B2 archive URI for the golden demo run (PS-021).
export const JUDGE_EVIDENCE_PACK_ARCHIVE_URI =
  "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json";

// Verified SHA-256 of the B2 archive content for the golden demo run (PS-021).
export const JUDGE_EVIDENCE_PACK_ARCHIVE_SHA256 =
  "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141";

// Rehydrate source recorded by PS-021 (durable_source = b2_rehydrated).
export const JUDGE_EVIDENCE_PACK_REHYDRATE_SOURCE = "b2_rehydrated";

// PS-021 proved zero provider calls during B2 rehydrate.
export const JUDGE_EVIDENCE_PACK_PROVIDER_CALLS_DURING_REHYDRATE = 0;

// PS-021 proved no live provider call happened during B2 rehydrate.
export const JUDGE_EVIDENCE_PACK_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE = true;

// Pack identity. The pack_id is deterministic (not a random UUID): it is
// derived from the verified golden run_id and the pack version, so the same
// golden run always yields the same pack_id. This keeps the smoke free of
// brittle timestamp/UUID expectations and keeps the export reproducible.
export const JUDGE_EVIDENCE_PACK_PACK_ID =
  "pack_ps031_" + JUDGE_EVIDENCE_PACK_RUN_ID;

// Pack schema version. Bumped on any shape change to the exported JSON.
export const JUDGE_EVIDENCE_PACK_PACK_VERSION = "2.0.0";

// Honest provenance label for the local browser export. Surfaced verbatim so
// a judge never reads "downloaded from the server" when the bytes were
// produced locally from checked-in evidence.
export const JUDGE_EVIDENCE_PACK_GENERATED_FROM =
  "local checked-in ProofStudio evidence (PS-021, PS-024, PS-025, PS-026, " +
  "PS-027, PS-028, PS-029, PS-030) -- no server round-trip, no B2 byte read, " +
  "no provider call";

// PS-025 local contract (FastAPI TestClient against a fresh empty store
// resolving the golden run_id from checked-in evidence) is verified.
export const JUDGE_EVIDENCE_PACK_LOCAL_CONTRACT_PROOF = true;

// PS-025: the public Render deployment is NOT verified for the golden passport
// unlock yet. The new backend code must be deployed and the public URL must
// be verified end-to-end before this flag is flipped.
export const JUDGE_EVIDENCE_PACK_PUBLIC_DEPLOYMENT_PENDING = true;

// PS-026 unlock scope marker. Mirrors the backend
// `GOLDEN_DEMO_UNLOCK_SCOPE = "golden_demo_only"` so the pack honestly
// reports the narrow allowlist (only this single run_id resolves publicly).
export const JUDGE_EVIDENCE_PACK_UNLOCK_SCOPE = "golden_demo_only";

// Checked-in source evidence paths the pack cross-references. These are the
// files the PS-031 smoke reads to verify every published value.
export const JUDGE_EVIDENCE_PACK_SOURCE_PS024_MANIFEST =
  "docs/evidence/demo/golden-demo-run.json";
export const JUDGE_EVIDENCE_PACK_SOURCE_PS021_EVIDENCE =
  "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json";
export const JUDGE_EVIDENCE_PACK_SOURCE_PS025_EVIDENCE =
  "docs/evidence/ps-025/public-durable-passport-unlock-smoke.json";
export const JUDGE_EVIDENCE_PACK_SOURCE_PS026_EVIDENCE =
  "docs/evidence/ps-026/b2-evidence-explorer-smoke.json";
export const JUDGE_EVIDENCE_PACK_SOURCE_PS027_EVIDENCE =
  "docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json";
export const JUDGE_EVIDENCE_PACK_SOURCE_PS028_EVIDENCE =
  "docs/evidence/ps-028/manifest-verification-panel-smoke.json";
export const JUDGE_EVIDENCE_PACK_SOURCE_PS029_EVIDENCE =
  "docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json";
export const JUDGE_EVIDENCE_PACK_SOURCE_PS030_EVIDENCE =
  "docs/evidence/ps-030/failure-as-proof-timeline-smoke.json";

// PS-031 references the binding implementation roadmap.
export const JUDGE_EVIDENCE_PACK_IMPLEMENTATION_ROADMAP =
  "docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md";

// ---------------------------------------------------------------------------
// Required source list. The pack cross-references eight evidence sources plus
// the implementation roadmap.
// ---------------------------------------------------------------------------

export type JudgeEvidencePackSourceKind =
  | "golden_manifest"
  | "b2_durable_evidence"
  | "passport_evidence"
  | "explorer_evidence"
  | "pipeline_evidence"
  | "manifest_panel_evidence"
  | "rehydrate_comparison_evidence"
  | "failure_timeline_evidence";

export interface JudgeEvidencePackSource {
  id: string;
  label: string;
  sliceTag: string;
  kind: JudgeEvidencePackSourceKind;
  evidencePath: string;
}

export const JUDGE_EVIDENCE_PACK_SOURCES: readonly JudgeEvidencePackSource[] =
  [
    {
      id: "ps024",
      label: "Golden demo manifest",
      sliceTag: "PS-024",
      kind: "golden_manifest",
      evidencePath: JUDGE_EVIDENCE_PACK_SOURCE_PS024_MANIFEST,
    },
    {
      id: "ps021",
      label: "PS-021 B2 durable rehydrate evidence",
      sliceTag: "PS-021",
      kind: "b2_durable_evidence",
      evidencePath: JUDGE_EVIDENCE_PACK_SOURCE_PS021_EVIDENCE,
    },
    {
      id: "ps025",
      label: "PS-025 public durable passport evidence",
      sliceTag: "PS-025",
      kind: "passport_evidence",
      evidencePath: JUDGE_EVIDENCE_PACK_SOURCE_PS025_EVIDENCE,
    },
    {
      id: "ps026",
      label: "PS-026 B2 Evidence Explorer evidence",
      sliceTag: "PS-026",
      kind: "explorer_evidence",
      evidencePath: JUDGE_EVIDENCE_PACK_SOURCE_PS026_EVIDENCE,
    },
    {
      id: "ps027",
      label: "PS-027 Genblaze Pipeline Graph evidence",
      sliceTag: "PS-027",
      kind: "pipeline_evidence",
      evidencePath: JUDGE_EVIDENCE_PACK_SOURCE_PS027_EVIDENCE,
    },
    {
      id: "ps028",
      label: "PS-028 Manifest Verification Panel evidence",
      sliceTag: "PS-028",
      kind: "manifest_panel_evidence",
      evidencePath: JUDGE_EVIDENCE_PACK_SOURCE_PS028_EVIDENCE,
    },
    {
      id: "ps029",
      label: "PS-029 B2 Rehydrate Comparison evidence",
      sliceTag: "PS-029",
      kind: "rehydrate_comparison_evidence",
      evidencePath: JUDGE_EVIDENCE_PACK_SOURCE_PS029_EVIDENCE,
    },
    {
      id: "ps030",
      label: "PS-030 Failure-as-Proof Timeline evidence",
      sliceTag: "PS-030",
      kind: "failure_timeline_evidence",
      evidencePath: JUDGE_EVIDENCE_PACK_SOURCE_PS030_EVIDENCE,
    },
  ];

// ---------------------------------------------------------------------------
// Route map. The pack links out to every implemented proof surface so a
// judge can step out of the pack and into the underlying surface.
// ---------------------------------------------------------------------------

export interface JudgeEvidencePackRoute {
  href: string;
  label: string;
  tag: string;
  description: string;
}

export const JUDGE_EVIDENCE_PACK_ROUTES: readonly JudgeEvidencePackRoute[] = [
  {
    href: "/failure-timeline",
    label: "Failure-as-Proof Timeline",
    tag: "PS-030",
    description:
      "The golden workflow as an evidence-backed operational timeline and " +
      "where captured failures, retries, and fallbacks would appear.",
  },
  {
    href: "/b2-rehydrate-comparison",
    label: "B2 Rehydrate Comparison",
    tag: "PS-029",
    description:
      "Before/after rehydrate value compared across every checked-in " +
      "evidence source.",
  },
  {
    href: "/manifest-verification",
    label: "Manifest Verification Panel",
    tag: "PS-028",
    description:
      "Cross-source manifest field consistency for the golden run.",
  },
  {
    href: "/b2-evidence",
    label: "B2 Evidence Explorer",
    tag: "PS-026",
    description:
      "The verified Backblaze B2 durable evidence behind the golden run.",
  },
  {
    href: "/genblaze-pipeline",
    label: "Genblaze Pipeline Graph",
    tag: "PS-027",
    description:
      "The media pipeline as a Genblaze Pipeline Graph: brief through " +
      "durable rehydrate.",
  },
  {
    href: "/passport/" + JUDGE_EVIDENCE_PACK_RUN_ID,
    label: "Golden Passport",
    tag: "PS-019 / PS-025",
    description:
      "The narrow public provenance passport unlock for the golden run.",
  },
  {
    href: "/",
    label: "Judge Cockpit Home",
    tag: "PS-023",
    description: "Back to the judge cockpit.",
  },
];

// ---------------------------------------------------------------------------
// Proof chain. The pack exposes the verified proof chain as an ordered list
// so a judge can read the operational trail top to bottom. Each step cites
// the checked-in evidence that backs it.
// ---------------------------------------------------------------------------

export type JudgeEvidencePackProofKind =
  | "checked_in_evidence"
  | "durable_b2_archive_proof"
  | "genblaze_manifest_evidence"
  | "b2_rehydrate_proof"
  | "local_passport_contract_proof"
  | "local_browser_export"
  | "inferred_product_explanation"
  | "public_deployment_pending";

export interface JudgeEvidencePackProofStep {
  idx: number;
  key: string;
  title: string;
  kind: JudgeEvidencePackProofKind;
  summary: string;
  sourceTags: readonly string[];
  links: readonly string[];
}

export const JUDGE_EVIDENCE_PACK_PROOF_CHAIN: readonly JudgeEvidencePackProofStep[] =
  [
    {
      idx: 1,
      key: "pack_identity",
      title: "Pack identity established",
      kind: "local_browser_export",
      summary:
        "PS-031 builds a deterministic Judge Evidence Pack from local " +
        "checked-in evidence. The pack_id is derived from the verified " +
        "golden run_id and the pack version, so the same golden run always " +
        "yields the same pack_id.",
      sourceTags: ["PS-031"],
      links: ["/evidence-pack"],
    },
    {
      idx: 2,
      key: "golden_run_pinned",
      title: "Golden run identity pinned",
      kind: "checked_in_evidence",
      summary:
        "PS-024 pinned one canonical golden demo manifest: run_id and " +
        "campaign_id sourced verbatim from the PS-024 golden manifest, " +
        "traced to the PS-021 live B2 durable rehydrate smoke.",
      sourceTags: ["PS-024", "PS-021"],
      links: ["/passport/" + JUDGE_EVIDENCE_PACK_RUN_ID, "/b2-evidence"],
    },
    {
      idx: 3,
      key: "b2_archive_recorded",
      title: "B2 archive recorded",
      kind: "durable_b2_archive_proof",
      summary:
        "PS-021 proved the full run archive was written to a real Backblaze " +
        "B2 object behind explicit, default-off gates. The archive URI and " +
        "SHA-256 are recorded in checked-in evidence.",
      sourceTags: ["PS-021", "PS-026"],
      links: ["/b2-evidence"],
    },
    {
      idx: 4,
      key: "genblaze_manifest_captured",
      title: "Genblaze manifest captured",
      kind: "genblaze_manifest_evidence",
      summary:
        "The Genblaze pipeline records what each generation attempt " +
        "produced and verifies the stored manifest against the asset bytes. " +
        "PS-028 confirms the manifest fields agree across every checked-in " +
        "source for the golden run.",
      sourceTags: ["PS-027", "PS-028"],
      links: ["/genblaze-pipeline", "/manifest-verification"],
    },
    {
      idx: 5,
      key: "passport_unlocked_locally",
      title: "Public passport contract unlocked locally",
      kind: "local_passport_contract_proof",
      summary:
        "PS-025 unlocked a narrow public passport path for this single " +
        "golden run_id, resolved from checked-in evidence only. The local " +
        "contract (FastAPI TestClient) is verified; the public deployment " +
        "remains pending.",
      sourceTags: ["PS-025"],
      links: ["/passport/" + JUDGE_EVIDENCE_PACK_RUN_ID],
    },
    {
      idx: 6,
      key: "rehydrate_proven_durable",
      title: "Rehydrate proven durable without provider rerun",
      kind: "b2_rehydrate_proof",
      summary:
        "PS-029 confirms the rehydrate used durable B2 archive evidence " +
        "instead of a live provider rerun: provider_calls_during_rehydrate = " +
        "0 and no_live_provider_call_during_rehydrate = true.",
      sourceTags: ["PS-029", "PS-021"],
      links: ["/b2-rehydrate-comparison"],
    },
    {
      idx: 7,
      key: "failure_as_proof_carried",
      title: "Failure-as-Proof carried into the pack",
      kind: "checked_in_evidence",
      summary:
        "PS-030 carried the golden workflow as an evidence-backed " +
        "operational timeline and shows where captured failures, retries, " +
        "and fallbacks would appear. The pack carries that summary forward.",
      sourceTags: ["PS-030"],
      links: ["/failure-timeline"],
    },
    {
      idx: 8,
      key: "public_deployment_pending",
      title: "Public deployment pending remains explicit",
      kind: "public_deployment_pending",
      summary:
        "The local contract is verified. The public Render deployment is " +
        "not verified yet: the new backend must be deployed and the public " +
        "URL verified end-to-end before this status changes.",
      sourceTags: ["PS-025"],
      links: ["/"],
    },
  ];

// ---------------------------------------------------------------------------
// Failure-as-Proof summary. Carried forward from PS-030 so the pack is a
// superset of the timeline's operational story, not a replacement for it.
// ---------------------------------------------------------------------------

export const JUDGE_EVIDENCE_PACK_FAILURE_AS_PROOF_SUMMARY: readonly string[] =
  [
    "Operational events (provider attempts, retry decisions, fallback " +
      "readiness, storage, and rehydrate behavior) are auditable workflow " +
      "evidence, not hidden noise.",
    "The Failure-as-Proof Timeline shows where captured failures, retries, " +
      "and fallbacks would appear if future evidence captured them.",
    "The verified golden run currently proves durable B2 rehydrate with " +
      "zero provider calls during rehydrate.",
    "No actual provider failure or fallback is claimed unless checked-in " +
      "evidence proves it. No fake failures are claimed.",
    "For the verified golden run, rehydrate uses B2-backed evidence with " +
      "zero provider calls.",
  ];

// ---------------------------------------------------------------------------
// Prompt / generation evidence summary.
//
// The pack does not surface the raw prompt packet of the golden run (it is
// not part of the checked-in evidence consumed by PS-021 through PS-030).
// Instead it explains, honestly, what the generation evidence layer records
// and what it does not include.
// ---------------------------------------------------------------------------

export interface JudgeEvidencePackEvidenceSummary {
  title: string;
  available: boolean;
  note: string;
  sourceTags: readonly string[];
}

export const JUDGE_EVIDENCE_PACK_GENERATION_EVIDENCE_SUMMARY: JudgeEvidencePackEvidenceSummary =
  {
    title: "Prompt / generation evidence summary",
    available: false,
    note:
      "The checked-in evidence used by this pack (PS-021 through PS-030) " +
      "records the golden run identity, the B2 archive digest, the " +
      "Genblaze manifest verification, and the durable rehydrate proof. " +
      "It does not include the raw prompt packet or per-token generation " +
      "metadata for the golden run. If a later slice checks that in, the " +
      "pack will surface it here; until then the pack honestly marks this " +
      "section as not available from checked-in evidence.",
    sourceTags: ["PS-024", "PS-027", "PS-028"],
  };

// ---------------------------------------------------------------------------
// Provider / model / attempt ledger summary.
//
// Same honesty rule as the generation summary: the golden run's provider /
// model / attempt ledger is not part of the checked-in evidence consumed by
// this pack. The pack states what it records (the provider-calls-during-
// rehydrate = 0 fact) and what it does not include (the live attempt ledger
// for the golden run).
// ---------------------------------------------------------------------------

export const JUDGE_EVIDENCE_PACK_PROVIDER_LEDGER_SUMMARY: JudgeEvidencePackEvidenceSummary =
  {
    title: "Provider / model / attempt ledger summary",
    available: false,
    note:
      "The checked-in evidence used by this pack does not include the live " +
      "provider / model / attempt ledger for the golden run. What the pack " +
      "does record is the durable rehydrate ledger fact: " +
      "provider_calls_during_rehydrate = 0 and " +
      "no_live_provider_call_during_rehydrate = true (PS-021, PS-029). " +
      "The full attempt ledger for the golden run can be created live in " +
      "the Review Room; it is not part of this checked-in pack.",
    sourceTags: ["PS-021", "PS-029"],
  };

// ---------------------------------------------------------------------------
// Final asset / archive summary.
// ---------------------------------------------------------------------------

export interface JudgeEvidencePackArchiveSummary {
  archive_uri: string;
  archive_sha256: string;
  rehydrate_source: string;
  provider_calls_during_rehydrate: number;
  no_live_provider_call_during_rehydrate: boolean;
  note: string;
  sourceTags: readonly string[];
}

export const JUDGE_EVIDENCE_PACK_ARCHIVE_SUMMARY: JudgeEvidencePackArchiveSummary =
  {
    archive_uri: JUDGE_EVIDENCE_PACK_ARCHIVE_URI,
    archive_sha256: JUDGE_EVIDENCE_PACK_ARCHIVE_SHA256,
    rehydrate_source: JUDGE_EVIDENCE_PACK_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      JUDGE_EVIDENCE_PACK_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      JUDGE_EVIDENCE_PACK_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
    note:
      "The B2 archive content is a JSON run archive (passport / attempt " +
      "ledger / asset metadata), not the raw media bytes. The pack records " +
      "the archive URI and SHA-256 from checked-in evidence; it does not " +
      "fetch the B2 object in the browser and does not include the raw " +
      "media bytes in the local export.",
    sourceTags: ["PS-021", "PS-026"],
  };

// ---------------------------------------------------------------------------
// Review / approval status. The pack is generated, not approved; this section
// honestly surfaces that the pack itself is not an approval artifact.
// ---------------------------------------------------------------------------

export interface JudgeEvidencePackReviewStatus {
  generated: boolean;
  approved: boolean;
  note: string;
}

export const JUDGE_EVIDENCE_PACK_REVIEW_STATUS: JudgeEvidencePackReviewStatus =
  {
    generated: true,
    approved: false,
    note:
      "The pack is generated locally from checked-in evidence. It is not an " +
      "approval artifact: no human reviewer has signed off on this pack, " +
      "and ProofStudio does not claim enterprise review / approval " +
      "workflow. A judge or client should treat the pack as a portable " +
      "proof summary that must still be reviewed in context.",
  };

// ---------------------------------------------------------------------------
// Disclosure readiness notes. Carries the Disclosure Readiness Layer
// commitment forward (PS-035) without claiming it is shipped.
// ---------------------------------------------------------------------------

export const JUDGE_EVIDENCE_PACK_DISCLOSURE_NOTES: readonly string[] = [
  "Plain-language disclosure: this pack summarizes what the checked-in " +
    "evidence records (golden run identity, B2 archive digest, durable " +
    "rehydrate, zero provider calls during rehydrate).",
  "Known facts: the local contract is verified; the archive URI and " +
    "SHA-256 are recorded in checked-in evidence; the rehydrate used " +
    "durable B2 archive evidence instead of a live provider rerun.",
  "Unknown / not-claimed facts: the pack does not prove the semantic " +
    "truth of the media, legal authenticity, C2PA authenticity, human " +
    "authorship, Object Lock, or tamper-proof storage.",
  "Channel-ready copy is planned for PS-035 (Disclosure Readiness Layer). " +
    "This pack is a proof summary, not a channel-ready disclosure asset.",
  "This pack is not legal advice and is not a certification.",
];

// ---------------------------------------------------------------------------
// Limitations. Required to be visible.
// ---------------------------------------------------------------------------

export const JUDGE_EVIDENCE_PACK_LIMITATIONS: readonly string[] = [
  "The pack is generated locally in the browser from checked-in evidence. " +
    "It is not signed by a server and is not a notarized artifact.",
  "The pack does not include raw media bytes. The B2 archive content is a " +
    "JSON run archive, not the generated media.",
  "The pack does not produce a zip export. Zip generation is not " +
    "implemented in PS-031.",
  "The pack did not fetch and hash the B2 object in the browser. The " +
    "archive SHA-256 is the value recorded by PS-021, not a value the " +
    "browser recomputed.",
  "The pack does not prove semantic truth, legal authenticity, C2PA " +
    "authenticity, or human authorship.",
  "The pack does not prove Object Lock or tamper-proof storage.",
  "The public deployment is not verified. The local contract is verified; " +
    "the public Render deployment remains pending.",
  "The pack does not include the golden run's live provider / model / " +
    "attempt ledger or raw prompt packet; those are not part of the " +
    "checked-in evidence consumed by this pack.",
];

// ---------------------------------------------------------------------------
// Next actions for judge / client.
// ---------------------------------------------------------------------------

export const JUDGE_EVIDENCE_PACK_NEXT_ACTIONS: readonly string[] = [
  "Open the Golden Passport to read the shareable proof object for this run.",
  "Open the B2 Rehydrate Comparison to verify the rehydrate value across " +
    "every checked-in source.",
  "Open the Manifest Verification Panel to verify manifest field " +
    "consistency.",
  "Open the Failure-as-Proof Timeline to read the operational timeline.",
  "Export the pack JSON and the pack README locally, then review them in " +
    "context with the proof surfaces open.",
  "If a channel-ready disclosure asset is required, wait for PS-035 " +
    "(Disclosure Readiness Layer); this pack is not that asset.",
];

// ---------------------------------------------------------------------------
// Truth boundary + claim boundary.
// ---------------------------------------------------------------------------

// Canonical truth boundary text for the Judge Evidence Pack. Written as a
// non-claim paragraph so the project's context-aware forbidden-claim
// scanners never flag the boundary terms as overclaims.
export const JUDGE_EVIDENCE_PACK_TRUTH_BOUNDARY =
  "The Judge Evidence Pack shows that the checked-in evidence (PS-021, " +
  "PS-024, PS-025, PS-026, PS-027, PS-028, PS-029, PS-030) records a B2 " +
  "rehydrate proof with zero provider calls during rehydrate, agrees on the " +
  "golden run's identifiers, archive URI, and archive SHA-256, and records " +
  "rehydrate_source = b2_rehydrated. The pack is generated locally from " +
  "checked-in ProofStudio evidence. The pack does not prove semantic truth, " +
  "legal authenticity, C2PA authenticity, or human authorship. The pack " +
  "does not prove Object Lock or tamper-proof storage. The pack did not " +
  "fetch and hash the B2 object in the browser. The pack does not include " +
  "raw media bytes and does not produce a zip export. The local contract is " +
  "verified; the public deployment remains pending until the new backend is " +
  "deployed and the public URL is verified end-to-end.";

export const JUDGE_EVIDENCE_PACK_CLAIM_BOUNDARY_ALLOWED: readonly string[] =
  [
    "Checked-in evidence records B2 rehydrate proof for the golden run.",
    "Checked-in evidence records zero provider calls during rehydrate.",
    "Checked-in evidence agrees on the archive URI and SHA-256.",
    "The pack is generated from local checked-in ProofStudio evidence.",
    "The browser export gives judges a portable proof summary.",
    "The pack helps reviewers understand workflow provenance and limitations.",
  ];

export const JUDGE_EVIDENCE_PACK_CLAIM_BOUNDARY_FORBIDDEN: readonly string[] =
  [
    "The pack does not prove semantic truth of the media.",
    "The pack does not prove legal authenticity.",
    "The pack does not prove human authorship.",
    "The pack does not prove C2PA authenticity.",
    "The pack does not prove Object Lock or tamper-proof storage.",
    "The pack did not fetch and hash the B2 object in the browser.",
    "The pack does not include raw media bytes.",
    "The pack does not produce a zip export (zip generation is not implemented).",
    "Public deployment has not been verified (it remains pending).",
    "The pack is not a certification and is not legal advice.",
  ];

// ---------------------------------------------------------------------------
// Required pack sections. The component renders one card per section so the
// PS-031 smoke can verify each required section is visible by id / heading.
// ---------------------------------------------------------------------------

export const JUDGE_EVIDENCE_PACK_REQUIRED_SECTIONS: readonly string[] = [
  "Pack identity",
  "Campaign / run identity",
  "Final asset / archive summary",
  "Prompt / generation evidence summary",
  "Provider / model / attempt ledger summary",
  "B2 archive evidence",
  "Genblaze manifest evidence",
  "B2 rehydrate proof",
  "Failure-as-Proof summary",
  "Public passport link",
  "Review / approval status",
  "Disclosure readiness notes",
  "Truth boundary",
  "Limitations",
  "Next actions for judge / client",
];

// ---------------------------------------------------------------------------
// Pack JSON shape.
//
// buildJudgeEvidencePackJson() returns the deterministic, exported pack JSON.
// generated_at is the only dynamic field: the smoke never asserts on its
// value. Everything else is sourced verbatim from the constants above.
// ---------------------------------------------------------------------------

export interface JudgeEvidencePackJson {
  pack_id: string;
  pack_version: string;
  generated_from: string;
  generated_at: string;
  campaign_id: string;
  run_id: string;
  archive_uri: string;
  archive_sha256: string;
  rehydrate_source: string;
  provider_calls_during_rehydrate: number;
  no_live_provider_call_during_rehydrate: boolean;
  source_evidence: readonly {
    id: string;
    slice_tag: string;
    label: string;
    evidence_path: string;
  }[];
  route_map: readonly { href: string; label: string; tag: string }[];
  proof_chain: readonly {
    idx: number;
    key: string;
    title: string;
    kind: JudgeEvidencePackProofKind;
    summary: string;
    source_tags: readonly string[];
    links: readonly string[];
  }[];
  failure_as_proof_summary: readonly string[];
  disclosure_notes: readonly string[];
  truth_boundary: string;
  limitations: readonly string[];
  public_deployment_pending: boolean;
}

export function buildJudgeEvidencePackJson(
  generatedAt: string,
): JudgeEvidencePackJson {
  return {
    pack_id: JUDGE_EVIDENCE_PACK_PACK_ID,
    pack_version: JUDGE_EVIDENCE_PACK_PACK_VERSION,
    generated_from: JUDGE_EVIDENCE_PACK_GENERATED_FROM,
    generated_at: generatedAt,
    campaign_id: JUDGE_EVIDENCE_PACK_CAMPAIGN_ID,
    run_id: JUDGE_EVIDENCE_PACK_RUN_ID,
    archive_uri: JUDGE_EVIDENCE_PACK_ARCHIVE_URI,
    archive_sha256: JUDGE_EVIDENCE_PACK_ARCHIVE_SHA256,
    rehydrate_source: JUDGE_EVIDENCE_PACK_REHYDRATE_SOURCE,
    provider_calls_during_rehydrate:
      JUDGE_EVIDENCE_PACK_PROVIDER_CALLS_DURING_REHYDRATE,
    no_live_provider_call_during_rehydrate:
      JUDGE_EVIDENCE_PACK_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
    source_evidence: JUDGE_EVIDENCE_PACK_SOURCES.map((src) => ({
      id: src.id,
      slice_tag: src.sliceTag,
      label: src.label,
      evidence_path: src.evidencePath,
    })),
    route_map: JUDGE_EVIDENCE_PACK_ROUTES.map((route) => ({
      href: route.href,
      label: route.label,
      tag: route.tag,
    })),
    proof_chain: JUDGE_EVIDENCE_PACK_PROOF_CHAIN.map((step) => ({
      idx: step.idx,
      key: step.key,
      title: step.title,
      kind: step.kind,
      summary: step.summary,
      source_tags: step.sourceTags,
      links: step.links,
    })),
    failure_as_proof_summary: JUDGE_EVIDENCE_PACK_FAILURE_AS_PROOF_SUMMARY,
    disclosure_notes: JUDGE_EVIDENCE_PACK_DISCLOSURE_NOTES,
    truth_boundary: JUDGE_EVIDENCE_PACK_TRUTH_BOUNDARY,
    limitations: JUDGE_EVIDENCE_PACK_LIMITATIONS,
    public_deployment_pending:
      JUDGE_EVIDENCE_PACK_PUBLIC_DEPLOYMENT_PENDING,
  };
}

// ---------------------------------------------------------------------------
// Pack README / Markdown export.
//
// buildJudgeEvidencePackMarkdown() returns the deterministic README text.
// Like the JSON, it carries the verified golden values, the proof summary,
// the disclosure notes, the limitations, and the public deployment pending
// status. It does not claim zip, raw media bytes, B2 browser verification,
// or any forbidden authenticity claim.
// ---------------------------------------------------------------------------

export function buildJudgeEvidencePackMarkdown(
  generatedAt: string,
): string {
  const lines: string[] = [];
  lines.push("# ProofStudio Judge Evidence Pack");
  lines.push("");
  lines.push(
    "Generated locally from checked-in ProofStudio evidence. No server " +
      "round-trip, no B2 byte read, no provider call. This README is a " +
      "portable proof summary, not a certification.",
  );
  lines.push("");
  lines.push("- pack_id: `" + JUDGE_EVIDENCE_PACK_PACK_ID + "`");
  lines.push("- pack_version: `" + JUDGE_EVIDENCE_PACK_PACK_VERSION + "`");
  lines.push("- generated_from: " + JUDGE_EVIDENCE_PACK_GENERATED_FROM);
  lines.push("- generated_at: " + generatedAt);
  lines.push("");
  lines.push("## Run / campaign identity");
  lines.push("");
  lines.push("- run_id: `" + JUDGE_EVIDENCE_PACK_RUN_ID + "`");
  lines.push("- campaign_id: `" + JUDGE_EVIDENCE_PACK_CAMPAIGN_ID + "`");
  lines.push("");
  lines.push("## What this pack proves");
  lines.push("");
  lines.push(
    "- The checked-in evidence records a B2 rehydrate proof for the golden " +
      "run (PS-021).",
  );
  lines.push(
    "- The checked-in evidence records zero provider calls during rehydrate " +
      "(`provider_calls_during_rehydrate = 0`).",
  );
  lines.push(
    "- The checked-in evidence records " +
      "`no_live_provider_call_during_rehydrate = true`.",
  );
  lines.push(
    "- Rehydrate used durable B2 archive evidence instead of a live provider " +
      "rerun (rehydrate_source = `b2_rehydrated`).",
  );
  lines.push(
    "- The checked-in evidence agrees on the archive URI and SHA-256 across " +
      "PS-021 / PS-024 / PS-025 / PS-026 / PS-027 / PS-028 / PS-029 / " +
      "PS-030.",
  );
  lines.push(
    "- The pack is generated from local checked-in ProofStudio evidence.",
  );
  lines.push(
    "- The browser export gives judges a portable proof summary.",
  );
  lines.push("");
  lines.push("## What this pack does NOT prove");
  lines.push("");
  for (const claim of JUDGE_EVIDENCE_PACK_CLAIM_BOUNDARY_FORBIDDEN) {
    lines.push("- " + claim);
  }
  lines.push("");
  lines.push("## B2 archive URI");
  lines.push("");
  lines.push("- " + JUDGE_EVIDENCE_PACK_ARCHIVE_URI);
  lines.push("");
  lines.push("## Archive SHA-256");
  lines.push("");
  lines.push("- " + JUDGE_EVIDENCE_PACK_ARCHIVE_SHA256);
  lines.push("");
  lines.push("## Rehydrate proof");
  lines.push("");
  lines.push(
    "- PS-021 proved the golden run can be rehydrated from B2 archive " +
      "content after backend memory loss, without rerunning any provider.",
  );
  lines.push(
    "- rehydrate_source: `" + JUDGE_EVIDENCE_PACK_REHYDRATE_SOURCE + "`",
  );
  lines.push(
    "- provider_calls_during_rehydrate: " +
      String(JUDGE_EVIDENCE_PACK_PROVIDER_CALLS_DURING_REHYDRATE),
  );
  lines.push(
    "- no_live_provider_call_during_rehydrate: " +
      String(JUDGE_EVIDENCE_PACK_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE),
  );
  lines.push("");
  lines.push("## Zero provider calls during rehydrate");
  lines.push("");
  lines.push(
    "- The rehydrate path used durable B2 archive evidence. No media " +
      "provider was called during rehydrate. This is what makes the " +
      "rehydrate durable: the run archive, not a fresh provider call, is " +
      "the system of record for this verified golden run.",
  );
  lines.push("");
  lines.push("## Proof surface links");
  lines.push("");
  for (const route of JUDGE_EVIDENCE_PACK_ROUTES) {
    lines.push(
      "- [" + route.label + "](" + route.href + ") (" + route.tag + ")",
    );
  }
  lines.push("");
  lines.push("## Disclosure notes");
  lines.push("");
  for (const note of JUDGE_EVIDENCE_PACK_DISCLOSURE_NOTES) {
    lines.push("- " + note);
  }
  lines.push("");
  lines.push("## Limitations");
  lines.push("");
  for (const lim of JUDGE_EVIDENCE_PACK_LIMITATIONS) {
    lines.push("- " + lim);
  }
  lines.push("");
  lines.push("## Public deployment pending");
  lines.push("");
  lines.push(
    "- local_contract_proof: " +
      String(JUDGE_EVIDENCE_PACK_LOCAL_CONTRACT_PROOF),
  );
  lines.push(
    "- public_deployment_pending: " +
      String(JUDGE_EVIDENCE_PACK_PUBLIC_DEPLOYMENT_PENDING),
  );
  lines.push(
    "- unlock_scope: " + JUDGE_EVIDENCE_PACK_UNLOCK_SCOPE,
  );
  lines.push(
    "- The local contract (FastAPI TestClient resolving the golden run_id " +
      "from checked-in evidence) is verified by PS-025. The public Render " +
      "deployment is not verified yet: the new backend must be deployed " +
      "and the public URL verified end-to-end before this status changes.",
  );
  lines.push("");
  lines.push("## Truth boundary");
  lines.push("");
  lines.push(JUDGE_EVIDENCE_PACK_TRUTH_BOUNDARY);
  lines.push("");
  return lines.join("\n");
}
