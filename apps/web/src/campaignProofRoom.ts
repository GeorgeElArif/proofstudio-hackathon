// PS-038a Campaign Proof Room -- canonical data module.
//
// This is the single, shared source of Campaign Proof Room framing for every
// core proof surface. It exists so a reviewer, client, or judge reads the SAME
// honest campaign-level proof / campaign evidence room / judge-facing campaign
// room / guided campaign proof trail / recorded campaign artifact / campaign
// proof summary / proof trail / proof timeline / evidence map / inspection path
// / judge demo path / creator/marketing workflow utility / campaign artifact
// reference / campaign artifact digest / campaign manifest evidence / campaign
// archive evidence / campaign rehydrate evidence / campaign review evidence /
// campaign approval evidence / export pack evidence / provenance passport
// evidence / B2 evidence / Genblaze manifest evidence / rehydrate comparison
// evidence / multimodal artifact evidence / transcript/timestamp evidence /
// voice/audio evidence / campaign intelligence evidence / Cloudflare backbone
// posture / production readiness demo mode posture / readiness posture /
// demo mode posture / local/static evidence / checked-in evidence / local
// verification / live verification status -- and what this room proves and does
// not prove -- in one campaign-level command room.
//
// The room is a campaign-proof-over-recorded-proof navigation / evidence /
// narrative surface over already-recorded or honestly-unavailable data, not a
// new proof surface, not a new generation pipeline, not a new provider/model
// integration, not a campaign performance proof, not a marketing effectiveness
// proof, not a business outcome guarantee, not a semantic truth, not a legal
// authenticity, not a legal approval, not a human authorship, not a C2PA
// authenticity, not a production readiness claim, not a production security
// claim, not a production compliance claim, not a legal compliance claim, not a
// live deployment, and not a new backend endpoint. It is
// campaign-proof-over-recorded-proof by design: it reads what the pipeline
// already recorded and renders a consistent campaign-level proof trail /
// evidence map / proof timeline / inspection path / judge demo path. It is
// purely client-side by default: it makes no Cloudflare API call, mutates no
// DNS, creates no Cloudflare resource, deploys no Cloudflare Pages, deploys no
// Cloudflare Workers, performs no Cloudflare R2 live read, performs no
// Cloudflare R2 write, performs no Backblaze B2 write, calls no provider, calls
// no model, reads no B2 object, performs no browser-side B2 byte verification,
// performs no broad B2 scan, and writes no B2 object. It only reads accepted
// local / static / golden / demo data and existing accepted data modules, and
// reuses the PS-037 disclosure concepts, the PS-037a multimodal proof framing,
// the PS-037b transcript/timestamp evidence framing, the PS-037c voice/audio
// evidence provider choice framing, the PS-037d campaign intelligence / judge
// narrative framing, the PS-037e Cloudflare low-cost backbone framing, and the
// PS-038 production readiness + demo mode framing.
//
// The Campaign Proof Room is named as a judge-facing campaign-level evidence /
// navigation / narrative surface over recorded proof only. Naming the Campaign
// Proof Room does not imply a campaign performance proof, a marketing
// effectiveness proof, a business outcome guarantee, a semantic truth, a legal
// authenticity, a legal approval, a human authorship, a C2PA authenticity, a
// production readiness claim, a production security claim, a production
// compliance claim, an uptime guarantee, a cost guarantee, a performance
// guarantee, a cold-start performance guarantee, an Object Lock, a tamper-proof
// storage, a browser-side B2 byte verification, a content moderation
// correctness, a transcript correctness, an emotion truth, a speaker identity,
// a biometric identity, or a model output truth. The Campaign Proof Room does
// not equal campaign performance proof. Campaign narrative does not equal
// marketing effectiveness proof. Campaign intelligence evidence does not equal
// business outcome guarantee. Campaign artifact evidence does not equal legal
// authenticity. Local campaign evidence does not equal live provider
// availability. Checked-in campaign evidence does not equal live B2
// availability. Cloudflare backbone posture does not equal live Cloudflare
// availability. Demo mode posture does not equal production readiness. Review
// approval evidence does not equal legal approval. Provenance passport evidence
// does not equal C2PA authenticity. Manifest evidence does not equal semantic
// truth. Transcript/timestamp evidence does not equal transcript correctness.
// Voice/audio evidence does not equal speaker identity. Proof does not equal
// truth.
//
// PS-038a does not invent new campaign performance proofs, new marketing
// effectiveness proofs, new business outcome guarantees, new semantic truths,
// new legal authenticities, new legal approvals, new human authorships, new
// C2PA authenticities, new production readiness, new production security, new
// production compliance, new legal compliance, new live deployments, new
// provider availability, new model availability, new Backblaze B2 live
// availability, new Cloudflare availability, or new generation pipelines. It
// states the existing recorded campaign-level proof consistently and honestly,
// and surfaces explicit honest "proof available" / "proof unavailable" / "not
// claimed" / "unknown" / "planned" / "deferred" / "live verification not
// available" / "live provider evidence not available" / "live B2 evidence not
// available" / "live Cloudflare evidence not available" states where no
// evidence exists.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Campaign
// Proof Room is not a live deployment, not a production deployment, not a DNS
// change system, not a Cloudflare resource creator, not a Cloudflare Pages
// deployment system, not a Cloudflare Workers deployment system, not a
// Cloudflare R2 live reader, not a Cloudflare R2 writer, not a Backblaze B2
// writer, not a live B2 verifier, not a truth system, not a semantic-truth
// system, not a model-output-truth system, not a content moderation
// correctness system, not a transcript correctness system, not an emotion
// truth system, not a speaker identity system, not a biometric identity
// system, and not an identity / authenticity system. It is not campaign
// performance proof, not marketing effectiveness proof, not business outcome
// guarantee, not semantic truth, not legal authenticity, not legal approval,
// not human authorship, not C2PA authenticity, not production readiness, not
// production security, not production compliance, not legal compliance, not
// live deployment, not provider availability, not model availability, not
// Backblaze B2 live availability, not Cloudflare availability, not uptime
// guarantee, not cost guarantee, not performance guarantee, not cold-start
// performance guarantee, not Object Lock, not tamper-proof, not browser-side
// B2 byte verification, and not model output truth.

import {
  GOLDEN_DEMO_ARCHIVE_SHA256,
  GOLDEN_DEMO_ARCHIVE_URI,
  GOLDEN_DEMO_CAMPAIGN_ID,
  GOLDEN_DEMO_MANIFEST_PATH,
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE,
  GOLDEN_DEMO_REHYDRATE_SOURCE,
  GOLDEN_DEMO_RUN_ID,
} from "./b2Evidence";
import {
  MULTIMODAL_PROOF_MANIFEST_HASH,
  MULTIMODAL_PROOF_MANIFEST_URI,
} from "./multimodalProof";

// ---------------------------------------------------------------------------
// Layer identity (spec section 21). Verbatim.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_SLICE_ID = "PS-038a";
export const CAMPAIGN_PROOF_ROOM_TITLE = "Campaign Proof Room";

// One-line positioning statement. Surfaced by the page header and the summary
// variant so the campaign-level proof framing is identical on every core proof
// surface.
export const CAMPAIGN_PROOF_ROOM_POSITIONING =
  "ProofStudio proves what the pipeline recorded for the campaign-level proof; " +
  "this is a navigation / evidence / narrative surface over recorded proof; " +
  "the Campaign Proof Room is a judge-facing campaign-level command room for " +
  "one proof-backed campaign (Campaign Proof Room does not equal campaign " +
  "performance proof; campaign narrative does not equal marketing effectiveness " +
  "proof).";

// ---------------------------------------------------------------------------
// Read-only reuse of accepted checked-in artifact evidence.
//
// The campaign artifact reference (archive_uri), the campaign artifact digest
// (archive_sha256), the rehydrate source, the provider-call count, the run_id,
// and the campaign_id are sourced verbatim from apps/web/src/b2Evidence.ts
// (PS-026), traced to docs/evidence/demo/golden-demo-run.json (PS-024) and the
// PS-021 live B2 durable rehydrate smoke. The manifest_uri / manifest_hash are
// sourced verbatim from apps/web/src/multimodalProof.ts (PS-035A). PS-038a
// does not mutate these values and does not invent a campaign performance
// proof, a marketing effectiveness proof, a business outcome guarantee, or a
// live provider / B2 / Cloudflare availability that is not in accepted data.
// ---------------------------------------------------------------------------

// Recorded campaign artifact reference (archive URI) for the golden demo run
// (PS-021 / PS-026). This is the recorded system-of-record archive reference
// the room cross-references (honestly surfaced, recorded-only).
export const CAMPAIGN_PROOF_ROOM_ARTIFACT_REFERENCE =
  GOLDEN_DEMO_ARCHIVE_URI;

// Recorded campaign artifact digest (archive SHA-256) for the golden demo run
// (PS-021 / PS-026). This is the recorded system-of-record archive digest.
export const CAMPAIGN_PROOF_ROOM_ARTIFACT_DIGEST =
  GOLDEN_DEMO_ARCHIVE_SHA256;

// Recorded manifest reference (PS-035A) cross-referenced with the PS-037a
// multimodal proof layer and the Genblaze manifest.
export const CAMPAIGN_PROOF_ROOM_MANIFEST_REFERENCE =
  MULTIMODAL_PROOF_MANIFEST_URI;

// Recorded 64-hex manifest hash (PS-035A) cross-referenced with PS-037a.
export const CAMPAIGN_PROOF_ROOM_MANIFEST_HASH =
  MULTIMODAL_PROOF_MANIFEST_HASH;

// Recorded rehydrate source (durable_source = b2_rehydrated) from PS-021.
export const CAMPAIGN_PROOF_ROOM_REHYDRATE_SOURCE =
  GOLDEN_DEMO_REHYDRATE_SOURCE;

// Recorded provider-call count during rehydrate (PS-021 proved zero).
export const CAMPAIGN_PROOF_ROOM_PROVIDER_CALLS_DURING_REHYDRATE =
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE;

// Recorded golden demo run_id the campaign room is scoped over (PS-021 /
// PS-024 / PS-025).
export const CAMPAIGN_PROOF_ROOM_RUN_ID = GOLDEN_DEMO_RUN_ID;

// Recorded golden demo campaign_id the campaign room is scoped over (PS-021 /
// PS-024 / PS-025).
export const CAMPAIGN_PROOF_ROOM_CAMPAIGN_ID = GOLDEN_DEMO_CAMPAIGN_ID;

// The checked-in golden demo manifest the room references (read-only).
export const CAMPAIGN_PROOF_ROOM_GOLDEN_MANIFEST_PATH =
  GOLDEN_DEMO_MANIFEST_PATH;

// ---------------------------------------------------------------------------
// Campaign Proof Room honesty (spec section 10.1 / 10.4 / 10.5). The default
// posture is local / static / golden / demo fixture evidence: no Cloudflare
// API call, no DNS mutation, no Cloudflare resource creation, no Cloudflare
// Pages deployment, no Cloudflare Workers deployment, no Cloudflare R2 live
// read, no Cloudflare R2 write, no Backblaze B2 write, no provider call, and
// no model call. No live campaign performance proof, marketing effectiveness
// proof, business outcome guarantee, live deployment, production readiness,
// live provider, live B2, or live Cloudflare evidence is checked into accepted
// data, so the room surfaces honest "proof unavailable" / "not claimed" /
// "unknown" / "planned" / "deferred" / "live verification not available" /
// "live provider evidence not available" / "live B2 evidence not available" /
// "live Cloudflare evidence not available" states rather than fabricated
// values.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Canonical Campaign Proof Room concepts (spec section 10.2 / 21). Verbatim.
// Surfaced as the concept labels on every core proof surface.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_CONCEPTS: readonly string[] = [
  "Campaign Proof Room",
  "campaign-level proof",
  "campaign evidence room",
  "judge-facing campaign room",
  "guided campaign proof trail",
  "recorded campaign artifact",
  "campaign artifact evidence",
  "campaign proof summary",
  "proof trail",
  "proof timeline",
  "evidence map",
  "inspection path",
  "judge demo path",
  "creator/marketing workflow utility",
  "campaign artifact reference",
  "campaign artifact digest",
  "campaign manifest evidence",
  "campaign archive evidence",
  "campaign rehydrate evidence",
  "campaign review evidence",
  "campaign approval evidence",
  "export pack evidence",
  "provenance passport evidence",
  "B2 evidence",
  "Genblaze manifest evidence",
  "rehydrate comparison evidence",
  "multimodal artifact evidence",
  "transcript/timestamp evidence",
  "voice/audio evidence",
  "campaign intelligence evidence",
  "Cloudflare backbone posture",
  "production readiness demo mode posture",
  "readiness posture",
  "demo mode posture",
  "local/static evidence",
  "checked-in evidence",
  "local verification",
  "live verification status",
  "disclosure boundary",
  "trust boundary cross-reference",
  "multimodal proof cross-reference",
  "transcript/timestamp cross-reference",
  "voice/audio evidence cross-reference",
  "campaign intelligence cross-reference",
  "Cloudflare low-cost backbone cross-reference",
  "production readiness demo mode cross-reference",
  "proof available",
  "proof unavailable",
  "not claimed",
  "unknown",
  "planned",
  "deferred",
];

// ---------------------------------------------------------------------------
// Campaign Proof Room status / state values (spec section 12.2).
// ---------------------------------------------------------------------------

export type CampaignProofRoomStatus =
  | "active"
  | "local_static"
  | "recorded_only"
  | "locally_verified"
  | "not_available"
  | "not_claimed"
  | "none_required_for_local_static"
  | "deferred_to_later_slice"
  | "unknown";

export type CampaignProofRoomState =
  | "recorded"
  | "locally_verified"
  | "recorded_only"
  | "not_verified"
  | "proof_available"
  | "proof_unavailable"
  | "not_available"
  | "not_claimed"
  | "planned"
  | "deferred"
  | "unknown";

export interface CampaignProofRoomItem {
  // concept: the verbatim concept label (spec section 21).
  concept: string;
  // label: the human-readable label, matching the verbatim strings.
  label: string;
  // value: the evidence value, honest about local / recorded-only /
  // unavailable / not claimed / planned / deferred / unknown.
  value: string;
  // applicable: false when the concept honestly does not apply.
  applicable: boolean;
  // state: one of the canonical states.
  state: CampaignProofRoomState;
}

// ---------------------------------------------------------------------------
// Campaign Proof Room items (spec section 12.2). Derived from accepted data.
// No live campaign performance proof, marketing effectiveness proof, business
// outcome guarantee, live deployment, production readiness, live provider,
// live B2, or live Cloudflare evidence is checked into accepted data, so those
// concepts honestly surface "proof unavailable" / "not claimed" / "unknown" /
// "planned" / "deferred" states. The recorded B2 / manifest / rehydrate
// evidence the room cross-references is honestly surfaced from the recorded
// golden demo archive and the PS-035A manifest (recorded-only, not
// live-verified here).
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_ITEMS: readonly CampaignProofRoomItem[] = [
  {
    concept: "campaign-level proof",
    label: "campaign-level proof",
    value:
      "judge-facing campaign-level proof framing over recorded proof evidence " +
      "(campaign-level proof does not equal campaign performance proof)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "campaign evidence room",
    label: "campaign evidence room",
    value:
      "judge-facing campaign evidence room framing over recorded proof " +
      "evidence",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "judge-facing campaign room",
    label: "judge-facing campaign room",
    value:
      "judge-facing campaign-level command room for one proof-backed campaign",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "guided campaign proof trail",
    label: "guided campaign proof trail",
    value:
      "guided campaign proof trail walking a judge through the campaign " +
      "artifact, the proof trail, the proof timeline, the evidence map, the " +
      "inspection path, and the judge demo path",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "recorded campaign artifact",
    label: "recorded campaign artifact",
    value:
      "the recorded campaign artifact for the golden demo run (run_id " +
      CAMPAIGN_PROOF_ROOM_RUN_ID +
      " / campaign_id " +
      CAMPAIGN_PROOF_ROOM_CAMPAIGN_ID +
      "), read from accepted local / golden / demo data",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "campaign artifact evidence",
    label: "campaign artifact evidence",
    value:
      "the campaign artifact evidence for the recorded campaign artifact " +
      "(campaign artifact evidence does not equal legal authenticity)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "campaign proof summary",
    label: "campaign proof summary",
    value:
      "compact campaign proof summary listing the recorded campaign artifact, " +
      "the campaign artifact reference, the campaign artifact digest, the " +
      "proof available / proof unavailable status, the inspection path, and " +
      "the judge demo path",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "proof trail",
    label: "proof trail",
    value:
      "the campaign proof trail over recorded proof (proof trail does not " +
      "equal legal authenticity)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "proof timeline",
    label: "proof timeline",
    value:
      "the campaign proof timeline ordering the recorded proof events for the " +
      "campaign (brief -> provider router -> Genblaze pipeline -> generated " +
      "asset -> B2 archive -> rehydrate -> manifest -> passport -> " +
      "review/approval -> export pack)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "evidence map",
    label: "evidence map",
    value:
      "the campaign evidence map listing every recorded / unavailable / not " +
      "claimed / planned / deferred campaign evidence concept with its honest " +
      "state",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "inspection path",
    label: "inspection path",
    value:
      "the inspection path linking into the proof surfaces (Judge Cockpit " +
      "Home, B2 Evidence Explorer, B2 Rehydrate Comparison, Manifest " +
      "Verification Panel, Archive / Rehydrate / B2 Audit Vault, Review + " +
      "Approval Workspace, Judge Evidence Pack / Export Pack, Public Provenance " +
      "Passport, and the PS-037 / PS-037a / PS-037b / PS-037c / PS-037d / " +
      "PS-037e / PS-038 layers)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "judge demo path",
    label: "judge demo path",
    value:
      "the recommended three-minute judge demo flow through the campaign room",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "creator/marketing workflow utility",
    label: "creator/marketing workflow utility",
    value:
      "how the recorded proof creates real-world utility for creator/marketing " +
      "teams without claiming campaign performance, marketing effectiveness, " +
      "or business outcome (creator/marketing workflow utility does not equal " +
      "business outcome guarantee)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "campaign artifact reference",
    label: "campaign artifact reference",
    value:
      "recorded campaign artifact reference (archive URI): " +
      CAMPAIGN_PROOF_ROOM_ARTIFACT_REFERENCE,
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "campaign artifact digest",
    label: "campaign artifact digest",
    value:
      "recorded campaign artifact digest (archive SHA-256): " +
      CAMPAIGN_PROOF_ROOM_ARTIFACT_DIGEST,
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "campaign manifest evidence",
    label: "campaign manifest evidence",
    value:
      "the campaign manifest evidence cross-reference (PS-028 / PS-035A). " +
      "Manifest reference " +
      CAMPAIGN_PROOF_ROOM_MANIFEST_REFERENCE +
      " / manifest hash " +
      CAMPAIGN_PROOF_ROOM_MANIFEST_HASH +
      " (manifest evidence does not equal semantic truth)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "campaign archive evidence",
    label: "campaign archive evidence",
    value:
      "the campaign archive evidence cross-reference (B2 archive / PS-036). " +
      "Recorded archive reference present; local / checked-in evidence only",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "campaign rehydrate evidence",
    label: "campaign rehydrate evidence",
    value:
      "the campaign rehydrate evidence cross-reference (PS-029 / PS-036). " +
      "Recorded rehydrate source " +
      CAMPAIGN_PROOF_ROOM_REHYDRATE_SOURCE +
      " with " +
      CAMPAIGN_PROOF_ROOM_PROVIDER_CALLS_DURING_REHYDRATE +
      " provider calls during rehydrate (checked-in campaign evidence does not " +
      "equal live B2 availability)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "campaign review evidence",
    label: "campaign review evidence",
    value:
      "the campaign review evidence cross-reference (PS-035). Recorded " +
      "review workflow evidence present; local / checked-in evidence only",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "campaign approval evidence",
    label: "campaign approval evidence",
    value:
      "the campaign approval evidence cross-reference (PS-035). Recorded " +
      "approval workflow evidence present; local / checked-in evidence only " +
      "(review approval evidence does not equal legal approval)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "export pack evidence",
    label: "export pack evidence",
    value:
      "the export pack evidence cross-reference (PS-031). Local browser export " +
      "evidence present; local / checked-in evidence only",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "provenance passport evidence",
    label: "provenance passport evidence",
    value:
      "the provenance passport evidence cross-reference (PS-019 / PS-025). " +
      "Golden demo passport evidence present; local / checked-in evidence only " +
      "(provenance passport evidence does not equal C2PA authenticity)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "B2 evidence",
    label: "B2 evidence",
    value:
      "the B2 evidence cross-reference (PS-026 / PS-036). Recorded archive " +
      "reference and archive digest present; local / checked-in evidence only " +
      "(checked-in campaign evidence does not equal live B2 availability)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "Genblaze manifest evidence",
    label: "Genblaze manifest evidence",
    value:
      "the Genblaze manifest evidence cross-reference (PS-027 / PS-028). " +
      "Recorded manifest reference present; local / checked-in evidence only",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "rehydrate comparison evidence",
    label: "rehydrate comparison evidence",
    value:
      "the rehydrate comparison evidence cross-reference (PS-029). Recorded " +
      "rehydrate comparison evidence present; local / checked-in evidence only",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "multimodal artifact evidence",
    label: "multimodal artifact evidence",
    value:
      "the multimodal artifact evidence cross-reference (PS-037a). Recorded " +
      "multimodal proof manifest present; local / checked-in evidence only",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "transcript/timestamp evidence",
    label: "transcript/timestamp evidence",
    value:
      "the transcript/timestamp evidence cross-reference (PS-037b). Recorded " +
      "transcript/timestamp framing present; local / checked-in evidence only " +
      "(transcript/timestamp evidence does not equal transcript correctness)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "voice/audio evidence",
    label: "voice/audio evidence",
    value:
      "the voice/audio evidence cross-reference (PS-037c). Recorded voice/audio " +
      "evidence provider choice framing present; local / checked-in evidence " +
      "only (voice/audio evidence does not equal speaker identity)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "campaign intelligence evidence",
    label: "campaign intelligence evidence",
    value:
      "the campaign intelligence evidence cross-reference (PS-037d). Recorded " +
      "campaign intelligence / judge narrative framing present; local / " +
      "checked-in evidence only (campaign intelligence evidence does not equal " +
      "business outcome guarantee)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "Cloudflare backbone posture",
    label: "Cloudflare backbone posture",
    value:
      "the Cloudflare backbone posture cross-reference (PS-037e). Cloudflare " +
      "named for backbone posture labeling only; local / checked-in evidence " +
      "only (Cloudflare backbone posture does not equal live Cloudflare " +
      "availability)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "production readiness demo mode posture",
    label: "production readiness demo mode posture",
    value:
      "the production readiness demo mode posture cross-reference (PS-038). " +
      "Local / demo posture; ready for local demo (demo mode posture does not " +
      "equal production readiness)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "readiness posture",
    label: "readiness posture",
    value:
      "the readiness posture (cross-referenced from PS-038). Local / demo " +
      "posture; ready for local demo (readiness posture does not equal " +
      "production readiness)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "demo mode posture",
    label: "demo mode posture",
    value:
      "the demo mode posture (cross-referenced from PS-038). Local / demo " +
      "posture; ready for local demo (demo mode posture does not equal " +
      "production readiness)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "local/static evidence",
    label: "local/static evidence",
    value:
      "whether the campaign evidence is local / static / golden / demo fixture " +
      "evidence (the default posture)",
    applicable: true,
    state: "locally_verified",
  },
  {
    concept: "checked-in evidence",
    label: "checked-in evidence",
    value:
      "whether the campaign evidence is checked-in evidence (checked-in " +
      "campaign evidence does not equal live B2 availability)",
    applicable: true,
    state: "locally_verified",
  },
  {
    concept: "local verification",
    label: "local verification",
    value:
      "locally verified against accepted checked-in evidence (manifest hashes, " +
      "archive references, digests, provider-call counts)",
    applicable: true,
    state: "locally_verified",
  },
  {
    concept: "live verification status",
    label: "live verification status",
    value:
      "live provider evidence not available / live B2 evidence not available / " +
      "live Cloudflare evidence not available (local / check-only by default; " +
      "no live provider call)",
    applicable: true,
    state: "not_verified",
  },
  {
    concept: "disclosure boundary",
    label: "disclosure boundary",
    value:
      "campaign disclosure boundary, consistent with PS-037: proof does not " +
      "equal truth; the Campaign Proof Room does not equal campaign performance " +
      "proof; campaign narrative does not equal marketing effectiveness proof; " +
      "campaign intelligence evidence does not equal business outcome " +
      "guarantee; campaign artifact evidence does not equal legal " +
      "authenticity; local campaign evidence does not equal live provider " +
      "availability; checked-in campaign evidence does not equal live B2 " +
      "availability; Cloudflare backbone posture does not equal live Cloudflare " +
      "availability; demo mode posture does not equal production readiness; " +
      "review approval evidence does not equal legal approval; provenance " +
      "passport evidence does not equal C2PA authenticity; manifest evidence " +
      "does not equal semantic truth; transcript/timestamp evidence does not " +
      "equal transcript correctness; voice/audio evidence does not equal " +
      "speaker identity",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "proof available",
    label: "proof available",
    value:
      "the honest state that recorded campaign proof is available (the recorded " +
      "campaign artifact, the proof trail, the proof timeline, the evidence " +
      "map, the inspection path, and the judge demo path are available as " +
      "recorded / local / checked-in evidence)",
    applicable: true,
    state: "proof_available",
  },
  {
    concept: "proof unavailable",
    label: "proof unavailable",
    value:
      "the honest state that recorded campaign proof is not available for live " +
      "campaign performance / marketing effectiveness / business outcome / live " +
      "deployment / production readiness / live provider / live B2 / live " +
      "Cloudflare",
    applicable: true,
    state: "proof_unavailable",
  },
  {
    concept: "not claimed",
    label: "not claimed",
    value:
      "the honest set of things ProofStudio does not claim for the campaign " +
      "(campaign performance proof, marketing effectiveness proof, business " +
      "outcome guarantee, semantic truth, legal authenticity, legal approval, " +
      "human authorship, C2PA authenticity, production readiness, production " +
      "security, production compliance, legal compliance, live deployment, " +
      "provider availability, model availability, Backblaze B2 live " +
      "availability, Cloudflare availability, uptime guarantee, cost guarantee, " +
      "performance guarantee, cold-start performance guarantee, Object Lock, " +
      "tamper-proof storage, browser-side B2 byte verification, content " +
      "moderation correctness, transcript correctness, emotion truth, speaker " +
      "identity, biometric identity, model output truth)",
    applicable: true,
    state: "not_claimed",
  },
  {
    concept: "unknown",
    label: "unknown",
    value:
      "what remains unknown or not surfaced for the campaign",
    applicable: true,
    state: "unknown",
  },
  {
    concept: "planned",
    label: "planned",
    value:
      "what is planned but not yet live for the campaign (live campaign " +
      "performance, live marketing effectiveness, live business outcome, live " +
      "deployment, production readiness, live provider evidence, live B2 " +
      "evidence, live Cloudflare evidence are planned, not live)",
    applicable: true,
    state: "planned",
  },
  {
    concept: "deferred",
    label: "deferred",
    value:
      "what is deferred to a later slice for the campaign (final submission " +
      "packaging deferred to PS-039)",
    applicable: true,
    state: "deferred",
  },
  {
    concept: "trust boundary cross-reference",
    label: "trust boundary cross-reference",
    value:
      "the room cross-references the PS-037 Disclosure + Trust Boundary and " +
      "never contradicts it",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "multimodal proof cross-reference",
    label: "multimodal proof cross-reference",
    value:
      "the room cross-references the PS-037a Multimodal Proof Layer (manifest " +
      CAMPAIGN_PROOF_ROOM_MANIFEST_REFERENCE +
      " / manifest hash " +
      CAMPAIGN_PROOF_ROOM_MANIFEST_HASH +
      " reused from PS-035A via PS-037a)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "transcript/timestamp cross-reference",
    label: "transcript/timestamp cross-reference",
    value:
      "the room cross-references the PS-037b Transcript/Timestamp Evidence " +
      "layer",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "voice/audio evidence cross-reference",
    label: "voice/audio evidence cross-reference",
    value:
      "the room cross-references the PS-037c Voice/Audio Evidence Provider " +
      "Choice layer",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "campaign intelligence cross-reference",
    label: "campaign intelligence cross-reference",
    value:
      "the room cross-references the PS-037d Gemini Campaign Intelligence / " +
      "Judge Narrative layer",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "Cloudflare low-cost backbone cross-reference",
    label: "Cloudflare low-cost backbone cross-reference",
    value:
      "the room cross-references the PS-037e Cloudflare Low-Cost Backbone " +
      "layer (Cloudflare named for backbone posture labeling only; Cloudflare " +
      "backbone posture does not equal live Cloudflare availability)",
    applicable: true,
    state: "recorded_only",
  },
  {
    concept: "production readiness demo mode cross-reference",
    label: "production readiness demo mode cross-reference",
    value:
      "the room cross-references the PS-038 Production Readiness + Demo Mode " +
      "layer (demo mode posture does not equal production readiness)",
    applicable: true,
    state: "recorded_only",
  },
];

// ---------------------------------------------------------------------------
// Required deferred later-slice / honest unavailable / not-claimed / planned /
// deferred / proof-available / proof-unavailable states (spec section 10.6 /
// 21). Verbatim.
//
// These are non-claim states: they state what is available, unavailable, not
// claimed, planned, deferred, or unknown, and must never be read as a hidden
// proof. PS-038a must not fake a campaign performance proof, a marketing
// effectiveness proof, a business outcome guarantee, a semantic truth, a legal
// authenticity, a legal approval, a human authorship, a C2PA authenticity, a
// production readiness claim, a production security claim, a production
// compliance claim, a legal compliance claim, a live deployment, a provider
// availability, a model availability, a Backblaze B2 live availability, a
// Cloudflare availability, an uptime guarantee, a cost guarantee, a performance
// guarantee, a cold-start performance guarantee, an Object Lock, a tamper-proof
// storage, a browser-side B2 byte verification, a content moderation
// correctness, a transcript correctness, an emotion truth, a speaker identity,
// a biometric identity, or a model output truth.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_DEFERRED_HEADING =
  "honest unavailable / not-claimed / planned / deferred states";

export const CAMPAIGN_PROOF_ROOM_DEFERRED_STATES: readonly string[] = [
  "recorded proof",
  "local/static demo evidence",
  "checked-in campaign evidence",
  "proof available",
  "proof unavailable",
  "not claimed",
  "unknown",
  "planned",
  "deferred",
  "live verification not available",
  "live provider evidence not available",
  "live B2 evidence not available",
  "live Cloudflare evidence not available",
  "final submission packaging deferred to PS-039",
];

// The later slice / out-of-scope owner for each deferred / not-claimed state.
// Surfaced so no reviewer mistakes an absent proof for a hidden proof.
export const CAMPAIGN_PROOF_ROOM_DEFERRED_OWNERS: readonly string[] = [
  "recorded proof -> default posture (local / golden / demo fixture evidence, not live evidence)",
  "local/static demo evidence -> default posture (local / golden / demo fixture evidence, not live evidence)",
  "checked-in campaign evidence -> default posture (checked-in campaign evidence; checked-in campaign evidence does not equal live B2 availability)",
  "proof available -> honest state (recorded campaign proof is available as recorded / local / checked-in evidence)",
  "proof unavailable -> honest state (no live campaign performance / marketing effectiveness / business outcome / live deployment / production readiness / live provider / live B2 / live Cloudflare proof is checked into accepted data)",
  "not claimed -> out of scope (PS-038a states what it does not prove for the campaign)",
  "unknown -> honest state (what remains unknown or not surfaced for the campaign)",
  "planned -> honest state (what is planned but not yet live for the campaign)",
  "deferred -> honest state (what is deferred to a later slice for the campaign)",
  "live verification not available -> default posture (local / check-only by default; no live provider call)",
  "live provider evidence not available -> default posture (no live provider call; local / check-only by default)",
  "live B2 evidence not available -> default posture (no live B2 read; local / check-only by default)",
  "live Cloudflare evidence not available -> default posture (no live Cloudflare API call; local / check-only by default)",
  "final submission packaging deferred to PS-039 -> PS-039 (PS-038a is not a final submission packaging system)",
];

// ---------------------------------------------------------------------------
// Cross-reference statements with the PS-037 Disclosure + Trust Boundary, the
// PS-037a Multimodal Proof Layer, the PS-037b Transcript/Timestamp Evidence
// layer, the PS-037c Voice/Audio Evidence Provider Choice layer, the PS-037d
// Gemini Campaign Intelligence / Judge Narrative layer, the PS-037e Cloudflare
// Low-Cost Backbone layer, and the PS-038 Production Readiness + Demo Mode
// layer. Surfaced so the room states explicitly that it integrates /
// cross-references each predecessor layer and never weakens its contract.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_TRUST_BOUNDARY_CROSS_REFERENCE =
  "Cross-references the PS-037 Disclosure + Trust Boundary: renders alongside " +
  "TrustBoundaryLayer, reuses the shared disclosure concepts, and never " +
  "contradicts the PS-037 boundary.";

export const CAMPAIGN_PROOF_ROOM_MULTIMODAL_CROSS_REFERENCE =
  "Cross-references the PS-037a Multimodal Proof Layer: renders alongside " +
  "MultimodalProofLayer and surfaces an honest multimodal artifact evidence " +
  "cross-reference. Manifest reference " +
  CAMPAIGN_PROOF_ROOM_MANIFEST_REFERENCE +
  " / manifest hash " +
  CAMPAIGN_PROOF_ROOM_MANIFEST_HASH +
  " reused from PS-035A via PS-037a.";

export const CAMPAIGN_PROOF_ROOM_TRANSCRIPT_CROSS_REFERENCE =
  "Cross-references the PS-037b Transcript/Timestamp Evidence layer: renders " +
  "alongside TranscriptTimestampEvidenceLayer and surfaces an honest " +
  "transcript/timestamp evidence cross-reference.";

export const CAMPAIGN_PROOF_ROOM_VOICE_AUDIO_CROSS_REFERENCE =
  "Cross-references the PS-037c Voice/Audio Evidence Provider Choice layer: " +
  "renders alongside VoiceAudioEvidenceChoiceLayer and surfaces an honest " +
  "voice/audio evidence cross-reference.";

export const CAMPAIGN_PROOF_ROOM_CAMPAIGN_INTELLIGENCE_CROSS_REFERENCE =
  "Cross-references the PS-037d Gemini Campaign Intelligence / Judge Narrative " +
  "layer: renders alongside CampaignIntelligenceJudgeNarrativeLayer and " +
  "surfaces an honest campaign intelligence evidence cross-reference.";

export const CAMPAIGN_PROOF_ROOM_CLOUDFLARE_BACKBONE_CROSS_REFERENCE =
  "Cross-references the PS-037e Cloudflare Low-Cost Backbone layer: renders " +
  "alongside CloudflareLowCostBackboneLayer and surfaces an honest Cloudflare " +
  "backbone posture cross-reference (Cloudflare named for backbone posture " +
  "labeling only; Cloudflare backbone posture does not equal live Cloudflare " +
  "availability).";

export const CAMPAIGN_PROOF_ROOM_PRODUCTION_READINESS_DEMO_MODE_CROSS_REFERENCE =
  "Cross-references the PS-038 Production Readiness + Demo Mode layer: renders " +
  "alongside ProductionReadinessDemoModeLayer and surfaces an honest " +
  "production readiness demo mode posture cross-reference (demo mode posture " +
  "does not equal production readiness).";

// ---------------------------------------------------------------------------
// Required de-escalation pairs (spec section 10.7 / 21). Surfaced verbatim so
// a judge never mistakes a strong-sounding Campaign Proof Room, campaign-level
// proof, campaign evidence room, judge-facing campaign room, guided campaign
// proof trail, campaign narrative, campaign intelligence evidence, campaign
// artifact evidence, local campaign evidence, checked-in campaign evidence,
// Cloudflare backbone posture, demo mode posture, review approval evidence,
// provenance passport evidence, manifest evidence, transcript/timestamp
// evidence, or voice/audio evidence for a stronger guarantee. Stated as
// non-claims so context-aware forbidden-claim scanners never flag these
// boundary terms as overclaims.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_DEESCALATION_PAIRS: readonly string[] = [
  "proof does not equal truth",
  "Campaign Proof Room does not equal campaign performance proof",
  "campaign narrative does not equal marketing effectiveness proof",
  "campaign intelligence evidence does not equal business outcome guarantee",
  "campaign artifact evidence does not equal legal authenticity",
  "local campaign evidence does not equal live provider availability",
  "checked-in campaign evidence does not equal live B2 availability",
  "Cloudflare backbone posture does not equal live Cloudflare availability",
  "demo mode posture does not equal production readiness",
  "review approval evidence does not equal legal approval",
  "provenance passport evidence does not equal C2PA authenticity",
  "manifest evidence does not equal semantic truth",
  "transcript/timestamp evidence does not equal transcript correctness",
  "voice/audio evidence does not equal speaker identity",
];

// ---------------------------------------------------------------------------
// Required negative boundary strings (spec section 10.8 / 21). Surfaced
// verbatim. These are the canonical "not claimed" set rendered as pills.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_NEGATIVE_BOUNDARY: readonly string[] = [
  "not campaign performance proof",
  "not marketing effectiveness proof",
  "not business outcome guarantee",
  "not semantic truth",
  "not legal authenticity",
  "not legal approval",
  "not human authorship",
  "not C2PA authenticity",
  "not production readiness",
  "not production security",
  "not production compliance",
  "not legal compliance",
  "not live deployment",
  "not provider availability",
  "not model availability",
  "not Backblaze B2 live availability",
  "not Cloudflare availability",
  "not uptime guarantee",
  "not cost guarantee",
  "not performance guarantee",
  "not cold-start performance guarantee",
  "not Object Lock",
  "not tamper-proof",
  "not browser-side B2 byte verification",
  "not content moderation correctness",
  "not transcript correctness",
  "not emotion truth",
  "not speaker identity",
  "not biometric identity",
  "not model output truth",
];

// ---------------------------------------------------------------------------
// Persistent campaign truth-boundary statement (spec section 11). Verbatim.
// Written as non-claim copy so the project's forbidden-claim scanners never
// flag the boundary terms.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_PERSISTENT_STATEMENT =
  "ProofStudio proves what the pipeline recorded for the campaign. Proof does " +
  "not equal truth. The Campaign Proof Room does not equal campaign " +
  "performance proof. Campaign narrative does not equal marketing " +
  "effectiveness proof. Campaign intelligence evidence does not equal " +
  "business outcome guarantee. Campaign artifact evidence does not equal legal " +
  "authenticity. Local campaign evidence does not equal live provider " +
  "availability. Checked-in campaign evidence does not equal live B2 " +
  "availability. Cloudflare backbone posture does not equal live Cloudflare " +
  "availability. Demo mode posture does not equal production readiness. Review " +
  "approval evidence does not equal legal approval. Provenance passport " +
  "evidence does not equal C2PA authenticity. Manifest evidence does not equal " +
  "semantic truth. Transcript/timestamp evidence does not equal transcript " +
  "correctness. Voice/audio evidence does not equal speaker identity.";

// Compact one-line summary used by the summary variant.
export const CAMPAIGN_PROOF_ROOM_SUMMARY =
  "Campaign Proof Room: a judge-facing campaign-level command room for one " +
  "proof-backed campaign; campaign-proof-over-recorded-proof by design; local " +
  "/ static / golden / checked-in evidence by default; Campaign Proof Room " +
  "does not equal campaign performance proof; campaign narrative does not " +
  "equal marketing effectiveness proof; final submission packaging deferred " +
  "to PS-039; proof does not equal truth.";

// ---------------------------------------------------------------------------
// Campaign proof summary block (spec section 11). A compact block listing the
// recorded campaign artifact, the campaign artifact reference, the campaign
// artifact digest, the proof available / proof unavailable status, the
// inspection path, and the judge demo path.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK = {
  recordedCampaignArtifact:
    "the recorded campaign artifact for the golden demo run (run_id " +
    CAMPAIGN_PROOF_ROOM_RUN_ID +
    " / campaign_id " +
    CAMPAIGN_PROOF_ROOM_CAMPAIGN_ID +
    ")",
  campaignArtifactReference:
    "campaign artifact reference (archive URI): " +
    CAMPAIGN_PROOF_ROOM_ARTIFACT_REFERENCE,
  campaignArtifactDigest:
    "campaign artifact digest (archive SHA-256): " +
    CAMPAIGN_PROOF_ROOM_ARTIFACT_DIGEST,
  proofAvailable:
    "proof available (recorded campaign proof is available as recorded / " +
    "local / checked-in evidence)",
  proofUnavailable:
    "proof unavailable (no live campaign performance / marketing effectiveness " +
    "/ business outcome / live deployment / production readiness proof is " +
    "checked into accepted data)",
  inspectionPath:
    "inspection path: links into the proof surfaces (Judge Cockpit Home, B2 " +
    "Evidence Explorer, B2 Rehydrate Comparison, Manifest Verification Panel, " +
    "Archive / Rehydrate / B2 Audit Vault, Review + Approval Workspace, Judge " +
    "Evidence Pack / Export Pack, Public Provenance Passport, and the " +
    "PS-037 / PS-037a / PS-037b / PS-037c / PS-037d / PS-037e / PS-038 layers)",
  judgeDemoPath:
    "judge demo path: the recommended three-minute judge demo flow through the " +
    "campaign room",
};

// ---------------------------------------------------------------------------
// Guided campaign proof trail steps (spec section 11). The guided campaign
// proof trail walks a judge through the campaign artifact, the proof trail,
// the proof timeline, the evidence map, the inspection path, and the judge
// demo path, in a readable order.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_TRAIL_STEPS: readonly {
  step: string;
  description: string;
}[] = [
  {
    step: "recorded campaign artifact",
    description:
      "Read the recorded campaign artifact for the golden demo run (run_id " +
      CAMPAIGN_PROOF_ROOM_RUN_ID +
      " / campaign_id " +
      CAMPAIGN_PROOF_ROOM_CAMPAIGN_ID +
      "), read from accepted local / golden / demo data.",
  },
  {
    step: "campaign proof summary",
    description:
      "Read the compact campaign proof summary listing the recorded campaign " +
      "artifact, the campaign artifact reference, the campaign artifact " +
      "digest, the proof available / proof unavailable status, the inspection " +
      "path, and the judge demo path.",
  },
  {
    step: "proof trail",
    description:
      "Read the campaign proof trail over recorded proof (proof trail does not " +
      "equal legal authenticity).",
  },
  {
    step: "proof timeline",
    description:
      "Read the campaign proof timeline ordering the recorded proof events for " +
      "the campaign (brief -> provider router -> Genblaze pipeline -> generated " +
      "asset -> B2 archive -> rehydrate -> manifest -> passport -> " +
      "review/approval -> export pack).",
  },
  {
    step: "evidence map",
    description:
      "Read the campaign evidence map listing every recorded / unavailable / " +
      "not claimed / planned / deferred campaign evidence concept with its " +
      "honest state.",
  },
  {
    step: "inspection path",
    description:
      "Follow the inspection path linking into the proof surfaces so each " +
      "piece of evidence can be inspected.",
  },
  {
    step: "judge demo path",
    description:
      "Read the recommended three-minute judge demo flow through the campaign " +
      "room.",
  },
  {
    step: "not claimed / unavailable / deferred",
    description:
      "Read what the campaign room proves, what it does not prove, the " +
      "unavailable / not-claimed / planned / deferred states, the " +
      "de-escalation pairs, and the negative boundary strings.",
  },
];

// ---------------------------------------------------------------------------
// Proof timeline events (spec section 11). Ordered recorded proof events for
// the campaign, reading only accepted local / static / golden / demo data.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_TIMELINE: readonly {
  event: string;
  evidence: string;
  state: CampaignProofRoomState;
}[] = [
  {
    event: "brief",
    evidence: "recorded campaign brief intake (PS-002 / PS-037d)",
    state: "recorded_only",
  },
  {
    event: "provider router",
    evidence: "recorded provider routing with retries and fallback (PS-006 / PS-007)",
    state: "recorded_only",
  },
  {
    event: "Genblaze pipeline",
    evidence: "recorded Genblaze pipeline orchestration (PS-027)",
    state: "recorded_only",
  },
  {
    event: "generated asset",
    evidence: "recorded generated asset metadata (PS-011)",
    state: "recorded_only",
  },
  {
    event: "B2 archive",
    evidence:
      "recorded B2 archive reference (archive URI) and archive digest (archive " +
      "SHA-256) (PS-010 / PS-021 / PS-026)",
    state: "recorded_only",
  },
  {
    event: "rehydrate",
    evidence:
      "recorded rehydrate source " +
      CAMPAIGN_PROOF_ROOM_REHYDRATE_SOURCE +
      " with " +
      CAMPAIGN_PROOF_ROOM_PROVIDER_CALLS_DURING_REHYDRATE +
      " provider calls during rehydrate (PS-029 / PS-036)",
    state: "recorded_only",
  },
  {
    event: "manifest",
    evidence:
      "recorded manifest reference " +
      CAMPAIGN_PROOF_ROOM_MANIFEST_REFERENCE +
      " / manifest hash " +
      CAMPAIGN_PROOF_ROOM_MANIFEST_HASH +
      " (PS-028 / PS-035A)",
    state: "recorded_only",
  },
  {
    event: "passport",
    evidence: "recorded public provenance passport (PS-019 / PS-025)",
    state: "recorded_only",
  },
  {
    event: "review/approval",
    evidence: "recorded review + approval workspace (PS-035)",
    state: "recorded_only",
  },
  {
    event: "export pack",
    evidence: "recorded judge evidence pack / export pack (PS-031)",
    state: "recorded_only",
  },
];

// ---------------------------------------------------------------------------
// Inspection path links (spec section 11). The links / deep-links into the
// proof surfaces so a judge can inspect each piece of evidence.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_INSPECTION_PATH: readonly {
  surface: string;
  href: string;
  title: string;
}[] = [
  { surface: "Judge Cockpit Home", href: "/", title: "Open the Judge Cockpit Home (PS-023)" },
  { surface: "B2 Evidence Explorer", href: "/b2-evidence", title: "Open the B2 Evidence Explorer (PS-026)" },
  { surface: "B2 Rehydrate Comparison", href: "/b2-rehydrate-comparison", title: "Open the B2 Rehydrate Comparison (PS-029)" },
  { surface: "Manifest Verification Panel", href: "/manifest-verification", title: "Open the Manifest Verification Panel (PS-028)" },
  { surface: "Genblaze Pipeline Graph", href: "/genblaze-pipeline", title: "Open the Genblaze Pipeline Graph (PS-027)" },
  { surface: "Archive / Rehydrate / B2 Audit Vault", href: "/b2-audit-vault", title: "Open the Archive / Rehydrate / B2 Audit Vault (PS-036)" },
  { surface: "Review + Approval Workspace", href: "/review-approval-workspace", title: "Open the Review + Approval Workspace (PS-035)" },
  { surface: "Judge Evidence Pack / Export Pack", href: "/evidence-pack", title: "Open the Judge Evidence Pack (PS-031)" },
  { surface: "Public Provenance Passport", href: "/passport/" + CAMPAIGN_PROOF_ROOM_RUN_ID, title: "Open the Public Provenance Passport (PS-019 / PS-025)" },
];

// ---------------------------------------------------------------------------
// Judge demo path steps (spec section 11). The recommended three-minute judge
// demo flow through the campaign room.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_JUDGE_DEMO_PATH: readonly string[] = [
  "open the Campaign Proof Room",
  "read the campaign proof summary",
  "read the recorded campaign artifact",
  "follow the guided campaign proof trail",
  "read the proof timeline",
  "read the evidence map",
  "follow the inspection path",
  "read the judge demo path",
  "read what the campaign room proves",
  "read what it does not prove",
  "read the unavailable / not-claimed / planned / deferred states",
  "read the de-escalation pairs",
  "read the negative boundary strings",
];

// ---------------------------------------------------------------------------
// Creator/marketing workflow utility block (spec section 11). States, honestly,
// how the recorded proof creates real-world utility for creator/marketing
// teams without claiming campaign performance, marketing effectiveness, or
// business outcome.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_CREATOR_MARKETING_UTILITY =
  "Creator/marketing workflow utility: the recorded campaign proof creates " +
  "real-world utility for creator/marketing teams by making each generation " +
  "run a reviewable, durable, evidence-backed workflow. A creator or marketing " +
  "team can, in one place, read what campaign artifact was made, what proof " +
  "exists for the campaign artifact, what evidence can be inspected, what " +
  "evidence remains unavailable or not claimed, how B2 / Genblaze / rehydrate " +
  "/ manifest / provider evidence fit together for the campaign, how demo / " +
  "readiness posture fits the campaign demo, and what the system proves and " +
  "does not prove for the campaign. This does not claim campaign performance " +
  "proof, marketing effectiveness proof, or business outcome guarantee " +
  "(creator/marketing workflow utility does not equal business outcome " +
  "guarantee).";

// ---------------------------------------------------------------------------
// Truth-boundary posture (spec section 10.1 / 21). Surfaced so the disclosure
// contract is deterministic and auditable. These are non-claim posture notes.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_POSTURE: readonly string[] = [
  "no deployment changes",
  "no env/secrets changes",
  "no render.yaml changes",
  "no requirements/dependency changes",
  "no Cloudflare API calls",
  "no DNS mutation",
  "no Cloudflare resource creation",
  "no Cloudflare Pages deployment",
  "no Cloudflare Workers deployment",
  "no Cloudflare R2 live reads",
  "no Cloudflare R2 writes",
  "no Backblaze B2 writes",
  "no provider calls",
  "no model calls",
  "no live B2 reads",
  "no B2 writes",
  "no broad B2 scans",
  "local / static by default",
];

// ---------------------------------------------------------------------------
// Required core proof surfaces (spec section 10.3). Listed so the Campaign
// Proof Room contract documents exactly where the room is reachable from.
// ---------------------------------------------------------------------------

export const CAMPAIGN_PROOF_ROOM_REQUIRED_SURFACES: readonly string[] = [
  "Judge Cockpit Home",
  "Campaign Proof Room",
];
