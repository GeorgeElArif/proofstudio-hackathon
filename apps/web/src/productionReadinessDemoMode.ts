// PS-038 Production Readiness + Demo Mode -- canonical data module.
//
// This is the single, shared source of Production Readiness + Demo Mode framing
// for every core proof surface. It exists so a reviewer, client, or judge reads
// the SAME honest demo mode / readiness posture / local fallback / live
// dependency boundary / cold-start mitigation plan / readiness checklist answer
// -- what demo mode is, whether demo mode is active or planned, whether demo
// mode uses local / golden / checked-in evidence, whether live dependencies are
// required for the judge demo, whether live providers are required, whether
// live B2 reads/writes are required, whether live Cloudflare is required,
// whether Cloudflare deployment exists, whether deployment evidence exists,
// whether production readiness evidence exists, whether production security
// evidence exists, whether production compliance evidence exists, whether
// cold-start mitigation is planned / implemented / measured / unavailable,
// whether startup health evidence exists, whether cost-control evidence exists,
// whether provider fallback evidence exists, whether failure-mode evidence
// exists, whether export/offline evidence exists, what the app can demo locally
// / statically, what still requires later production deployment work, and what
// this layer proves and does not prove -- on the Judge Cockpit Home, the B2
// Evidence Explorer, the Manifest Verification Panel, the B2 Rehydrate
// Comparison, the B2 Audit Vault, the Review + Approval Workspace, the Judge
// Evidence Pack, the Public Provenance Passport, and the Review Room.
//
// The layer is a demo-mode / readiness-posture / cold-start-mitigation
// inspection layer over already-recorded or honestly-unavailable data, not a
// new proof surface, not a new route, not a new backend endpoint, not a live
// deployment, not a production readiness system, not a production security
// system, not a production compliance system, and not a hosting engine. It is
// demo-path-and-readiness-posture-over-recorded-proof by design: it reads what
// the pipeline already recorded and renders a consistent demo mode / readiness
// posture / cold-start mitigation plan. It is purely client-side by default: it
// makes no Cloudflare API call, mutates no DNS, creates no Cloudflare resource,
// deploys no Cloudflare Pages, deploys no Cloudflare Workers, performs no
// Cloudflare R2 live read, performs no Cloudflare R2 write, performs no
// Backblaze B2 write, calls no provider, calls no model, reads no B2 object,
// performs no browser-side B2 byte verification, performs no broad B2 scan, and
// writes no B2 object. It only reads accepted local / golden / demo data and
// existing accepted data modules, and reuses the PS-037 disclosure concepts,
// the PS-037a multimodal proof framing, the PS-037b transcript/timestamp
// evidence framing, the PS-037c voice/audio evidence provider choice framing,
// the PS-037d campaign intelligence / judge narrative framing, and the PS-037e
// Cloudflare low-cost backbone framing.
//
// Demo mode is named as a judge-facing posture label for local / golden /
// checked-in demo evidence only. Naming demo mode does not imply a live
// deployment, a production readiness claim, a production security claim, a
// production compliance claim, an uptime guarantee, a cost guarantee, a
// performance guarantee, a cold-start performance guarantee, or any correctness
// guarantee. Demo mode does not equal production readiness. Local demo mode
// does not equal live deployment. The production readiness layer label does not
// equal a production readiness claim. The readiness checklist does not equal
// production security. The cold-start mitigation plan does not equal a measured
// performance guarantee. The low-cost demo posture does not equal cost
// guarantee. Local fallback does not equal live provider availability.
// Checked-in evidence does not equal live B2 availability. The Cloudflare
// dependency posture does not equal live Cloudflare availability. Demo/golden
// readiness evidence does not equal production compliance.
//
// PS-038 does not invent new live deployments, new production deployments, new
// production readiness, new production security, new production compliance, new
// legal compliance, new uptime guarantees, new cost guarantees, new performance
// guarantees, new cold-start performance guarantees, new cold-start
// measurements, new Cloudflare deployments, new Cloudflare availability, new
// Backblaze B2 live availability, new provider availability, or new model
// availability. It states the existing recorded demo / readiness posture
// consistently and honestly, and surfaces explicit honest "production
// deployment not available" / "production readiness evidence not available" /
// "production security evidence not available" / "production compliance
// evidence not available" / "live provider evidence not available" / "live B2
// evidence not available" / "live Cloudflare evidence not available" /
// "cold-start measurement not available" / "cold-start mitigation planned" /
// "ready for local demo" / "planned" / "not claimed" / "unknown" states where
// no evidence exists.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Production
// Readiness + Demo Mode layer is not a live deployment, not a production
// deployment, not a DNS change system, not a Cloudflare resource creator, not a
// Cloudflare Pages deployment system, not a Cloudflare Workers deployment
// system, not a Cloudflare R2 live reader, not a Cloudflare R2 writer, not a
// Backblaze B2 writer, not a live B2 verifier, not a truth system, not a
// semantic-truth system, not a model-output-truth system, not a production
// readiness system, not a production security system, not a production
// compliance system, not a legal compliance system, not an uptime guarantee
// system, not a cost guarantee system, not a performance guarantee system, not
// a cold-start performance guarantee system, not a load test, not a
// vulnerability scan, not a penetration test, not an incident-response
// readiness system, not an SLO/SLA system, not a data retention compliance
// system, not a privacy compliance system, not a campaign performance
// predictor, not a marketing effectiveness scorer, and not an identity /
// biometric / authenticity system. It is not production readiness, not
// production security, not production compliance, not legal compliance, not
// live deployment, not Cloudflare deployment, not Cloudflare availability, not
// Backblaze B2 live availability, not provider availability, not model
// availability, not uptime guarantee, not cost guarantee, not performance
// guarantee, not cold-start performance guarantee, not load-test coverage, not
// vulnerability scan coverage, not penetration test coverage, not incident
// response readiness, not SLO/SLA guarantee, not data retention compliance, not
// privacy compliance, not Object Lock, not tamper-proof, not browser-side B2
// byte verification, not semantic truth, not legal authenticity, not human
// authorship, and not C2PA authenticity.

import {
  GOLDEN_DEMO_ARCHIVE_SHA256,
  GOLDEN_DEMO_ARCHIVE_URI,
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE,
  GOLDEN_DEMO_REHYDRATE_SOURCE,
} from "./b2Evidence";
import {
  MULTIMODAL_PROOF_MANIFEST_HASH,
  MULTIMODAL_PROOF_MANIFEST_URI,
} from "./multimodalProof";

// ---------------------------------------------------------------------------
// Layer identity (spec section 21). Verbatim.
// ---------------------------------------------------------------------------

export const PRODUCTION_READINESS_DEMO_MODE_SLICE_ID = "PS-038";
export const PRODUCTION_READINESS_DEMO_MODE_TITLE = "Production Readiness + Demo Mode";

// One-line positioning statement. Surfaced by the summary variant and the panel
// header so the demo mode / readiness posture framing is identical on every
// core proof surface.
export const PRODUCTION_READINESS_DEMO_MODE_POSITIONING =
  "ProofStudio proves what the pipeline recorded for the demo path and " +
  "readiness posture; this is a demo-path-and-readiness-posture-over-" +
  "recorded-proof layer; demo mode and the production readiness layer label " +
  "are judge-facing posture labels for local / golden / checked-in demo " +
  "evidence only; demo mode does not equal production readiness; the " +
  "production readiness layer label does not equal a production readiness " +
  "claim.";

// ---------------------------------------------------------------------------
// Read-only reuse of accepted checked-in artifact evidence.
//
// The archive reference (archive_uri), the archive digest (archive_sha256),
// the rehydrate source, and the provider-call count are sourced verbatim from
// apps/web/src/b2Evidence.ts (PS-026), traced to
// docs/evidence/demo/golden-demo-run.json (PS-024) and the PS-021 live B2
// durable rehydrate smoke. The manifest_uri / manifest_hash are sourced
// verbatim from apps/web/src/multimodalProof.ts (PS-035A). PS-038 does not
// mutate these values and does not invent a live deployment, a production
// readiness, a production security, a production compliance, or a live provider
// / B2 / Cloudflare availability that is not in accepted data.
// ---------------------------------------------------------------------------

// Recorded B2 archive reference for the golden demo run (PS-021 / PS-026). This
// is the recorded system-of-record archive reference the layer cross-references
// (honestly surfaced, recorded-only).
export const PRODUCTION_READINESS_DEMO_MODE_ARCHIVE_REFERENCE =
  GOLDEN_DEMO_ARCHIVE_URI;

// Recorded SHA-256 digest of the B2 archive content for the golden demo run
// (PS-021 / PS-026). This is the recorded system-of-record archive digest.
export const PRODUCTION_READINESS_DEMO_MODE_ARCHIVE_DIGEST =
  GOLDEN_DEMO_ARCHIVE_SHA256;

// Recorded manifest reference (PS-035A) cross-referenced with the PS-037a
// multimodal proof layer and the Genblaze manifest.
export const PRODUCTION_READINESS_DEMO_MODE_MANIFEST_REFERENCE =
  MULTIMODAL_PROOF_MANIFEST_URI;

// Recorded 64-hex manifest hash (PS-035A) cross-referenced with PS-037a.
export const PRODUCTION_READINESS_DEMO_MODE_MANIFEST_HASH =
  MULTIMODAL_PROOF_MANIFEST_HASH;

// Recorded rehydrate source (durable_source = b2_rehydrated) from PS-021.
export const PRODUCTION_READINESS_DEMO_MODE_REHYDRATE_SOURCE =
  GOLDEN_DEMO_REHYDRATE_SOURCE;

// Recorded provider-call count during rehydrate (PS-021 proved zero).
export const PRODUCTION_READINESS_DEMO_MODE_PROVIDER_CALLS_DURING_REHYDRATE =
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE;

// The checked-in golden demo manifest the layer references (read-only).
export const PRODUCTION_READINESS_DEMO_MODE_GOLDEN_MANIFEST_PATH =
  "docs/evidence/demo/golden-demo-run.json";

// ---------------------------------------------------------------------------
// Production readiness + demo mode honesty (spec section 10.1 / 10.4 / 10.5).
// The default posture is local / demo / golden fixture evidence: no Cloudflare
// API call, no DNS mutation, no Cloudflare resource creation, no Cloudflare
// Pages deployment, no Cloudflare Workers deployment, no Cloudflare R2 live
// read, no Cloudflare R2 write, no Backblaze B2 write, no provider call, and no
// model call. No live deployment, production readiness, production security,
// production compliance, cold-start measurement, startup health evidence,
// cost-control evidence, live provider, live B2, or live Cloudflare evidence is
// checked into accepted data, so the layer surfaces honest "production
// deployment not available" / "production readiness evidence not available" /
// "production security evidence not available" / "production compliance
// evidence not available" / "live provider evidence not available" / "live B2
// evidence not available" / "live Cloudflare evidence not available" /
// "cold-start measurement not available" / "cold-start mitigation planned"
// states rather than fabricated values.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Canonical Production Readiness + Demo Mode concepts (spec section 10.2 / 21).
// Verbatim. Surfaced as the concept labels on every core proof surface.
// ---------------------------------------------------------------------------

export const PRODUCTION_READINESS_DEMO_MODE_CONCEPTS: readonly string[] = [
  "Production Readiness + Demo Mode",
  "demo mode",
  "readiness posture",
  "production readiness status",
  "demo mode status",
  "local demo status",
  "judge demo status",
  "local/static fallback",
  "golden evidence fallback",
  "checked-in evidence fallback",
  "live dependency status",
  "provider dependency status",
  "B2 dependency status",
  "Cloudflare dependency status",
  "deployment evidence status",
  "production security evidence status",
  "production compliance evidence status",
  "cold-start mitigation status",
  "startup health status",
  "cost-control status",
  "provider fallback status",
  "failure-mode status",
  "export/offline evidence status",
  "demo path evidence",
  "readiness checklist evidence",
  "local verification",
  "live verification status",
  "disclosure boundary",
  "trust boundary cross-reference",
  "multimodal proof cross-reference",
  "transcript/timestamp cross-reference",
  "voice/audio evidence cross-reference",
  "campaign intelligence cross-reference",
  "Cloudflare low-cost backbone cross-reference",
  "not claimed",
  "unknown",
  "planned",
];

// ---------------------------------------------------------------------------
// Production readiness + demo mode status values (spec section 12.2).
// ---------------------------------------------------------------------------

export type ProductionReadinessDemoModeStatus =
  | "active"
  | "planned"
  | "local_demo"
  | "ready_for_local_demo"
  | "not_available"
  | "not_claimed"
  | "none_required_for_local_demo"
  | "not_required_for_local_demo"
  | "deferred_to_later_production_work"
  | "unknown";

export type ProductionReadinessDemoModeState =
  | "recorded"
  | "locally_verified"
  | "recorded_only"
  | "not_verified"
  | "not_available"
  | "not_claimed"
  | "planned"
  | "unknown"
  | "deferred_to_later_slice";

export interface ProductionReadinessDemoModeItem {
  // concept: the verbatim concept label (spec section 21).
  concept: string;
  // label: the human-readable label, matching the verbatim strings.
  label: string;
  // value: the evidence value, honest about local / recorded-only /
  // unavailable / not claimed / planned / unknown.
  value: string;
  // applicable: false when the concept honestly does not apply.
  applicable: boolean;
  // state: one of the canonical states.
  state: ProductionReadinessDemoModeState;
}

// ---------------------------------------------------------------------------
// Production readiness + demo mode items (spec section 12.2). Derived from
// accepted data. No live deployment, production readiness, production security,
// production compliance, cold-start measurement, startup health evidence,
// cost-control evidence, live provider, live B2, or live Cloudflare evidence is
// checked into accepted data, so those concepts honestly surface "not
// available" / "planned" / "ready for local demo" states. The recorded B2 /
// manifest / rehydrate evidence the layer cross-references is honestly surfaced
// from the recorded golden demo archive and the PS-035A manifest (recorded-only,
// not live-verified here).
// ---------------------------------------------------------------------------

export const PRODUCTION_READINESS_DEMO_MODE_ITEMS: readonly ProductionReadinessDemoModeItem[] =
  [
    {
      concept: "demo mode",
      label: "demo mode",
      value:
        "judge-facing demo mode posture for local / golden / checked-in demo " +
        "evidence only (demo mode does not equal production readiness)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "readiness posture",
      label: "readiness posture",
      value:
        "judge-facing readiness posture view over the recorded proof stack " +
        "(local / demo posture; readiness posture does not equal production " +
        "readiness)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "production readiness status",
      label: "production readiness status",
      value:
        "deferred to later production work (production readiness evidence not " +
        "available); the production readiness layer label does not equal a " +
        "production readiness claim",
      applicable: true,
      state: "deferred_to_later_slice",
    },
    {
      concept: "demo mode status",
      label: "demo mode status",
      value:
        "planned (demo mode is planned / local_demo by default; demo mode " +
        "does not equal production readiness)",
      applicable: true,
      state: "planned",
    },
    {
      concept: "local demo status",
      label: "local demo status",
      value: "ready for local demo",
      applicable: true,
      state: "locally_verified",
    },
    {
      concept: "judge demo status",
      label: "judge demo status",
      value: "ready for local demo (local_demo)",
      applicable: true,
      state: "locally_verified",
    },
    {
      concept: "local/static fallback",
      label: "local/static fallback",
      value:
        "active by default (the demo falls back to local / static evidence " +
        "when live dependencies are unavailable)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "golden evidence fallback",
      label: "golden evidence fallback",
      value:
        "active by default (the demo falls back to golden demo evidence)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "checked-in evidence fallback",
      label: "checked-in evidence fallback",
      value:
        "active by default (the demo falls back to checked-in evidence)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "live dependency status",
      label: "live dependency status",
      value: "none required for local demo",
      applicable: true,
      state: "not_verified",
    },
    {
      concept: "provider dependency status",
      label: "provider dependency status",
      value: "not required for local demo (live provider evidence not available)",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "B2 dependency status",
      label: "B2 dependency status",
      value: "not required for local demo (live B2 evidence not available)",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "Cloudflare dependency status",
      label: "Cloudflare dependency status",
      value:
        "not required for local demo (live Cloudflare evidence not " +
        "available); the Cloudflare dependency posture does not equal live " +
        "Cloudflare availability",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "deployment evidence status",
      label: "deployment evidence status",
      value: "production deployment not available",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "production security evidence status",
      label: "production security evidence status",
      value: "production security evidence not available",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "production compliance evidence status",
      label: "production compliance evidence status",
      value: "production compliance evidence not available",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "cold-start mitigation status",
      label: "cold-start mitigation status",
      value:
        "cold-start mitigation planned (cold-start measurement not " +
        "available); the cold-start mitigation plan does not equal a measured " +
        "performance guarantee",
      applicable: true,
      state: "planned",
    },
    {
      concept: "startup health status",
      label: "startup health status",
      value: "planned (startup health evidence not available)",
      applicable: true,
      state: "planned",
    },
    {
      concept: "cost-control status",
      label: "cost-control status",
      value:
        "planned (cost-control evidence not available); the low-cost demo " +
        "posture does not equal cost guarantee",
      applicable: true,
      state: "planned",
    },
    {
      concept: "provider fallback status",
      label: "provider fallback status",
      value: "planned (local_demo fallback; live provider evidence not available)",
      applicable: true,
      state: "planned",
    },
    {
      concept: "failure-mode status",
      label: "failure-mode status",
      value: "planned (local_demo evidence)",
      applicable: true,
      state: "planned",
    },
    {
      concept: "export/offline evidence status",
      label: "export/offline evidence status",
      value: "planned (local_demo evidence; final submission packaging deferred to PS-039)",
      applicable: true,
      state: "planned",
    },
    {
      concept: "demo path evidence",
      label: "demo path evidence",
      value: "ready for local demo (local_demo)",
      applicable: true,
      state: "locally_verified",
    },
    {
      concept: "readiness checklist evidence",
      label: "readiness checklist evidence",
      value:
        "judge-facing readiness checklist evidence framing (the readiness " +
        "checklist does not equal production security)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "trust boundary cross-reference",
      label: "trust boundary cross-reference",
      value:
        "the layer cross-references the PS-037 Disclosure + Trust Boundary and " +
        "never contradicts it",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "multimodal proof cross-reference",
      label: "multimodal proof cross-reference",
      value:
        "the layer cross-references the PS-037a Multimodal Proof Layer (manifest " +
        PRODUCTION_READINESS_DEMO_MODE_MANIFEST_REFERENCE +
        " / manifest hash " +
        PRODUCTION_READINESS_DEMO_MODE_MANIFEST_HASH +
        " reused from PS-035A via PS-037a)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "transcript/timestamp cross-reference",
      label: "transcript/timestamp cross-reference",
      value:
        "the layer cross-references the PS-037b Transcript/Timestamp Evidence " +
        "layer",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "voice/audio evidence cross-reference",
      label: "voice/audio evidence cross-reference",
      value:
        "the layer cross-references the PS-037c Voice/Audio Evidence Provider " +
        "Choice layer",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "campaign intelligence cross-reference",
      label: "campaign intelligence cross-reference",
      value:
        "the layer cross-references the PS-037d Gemini Campaign Intelligence / " +
        "Judge Narrative layer",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "Cloudflare low-cost backbone cross-reference",
      label: "Cloudflare low-cost backbone cross-reference",
      value:
        "the layer cross-references the PS-037e Cloudflare Low-Cost Backbone " +
        "layer (Cloudflare named for dependency posture labeling only; the " +
        "Cloudflare dependency posture does not equal live Cloudflare " +
        "availability)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "local verification",
      label: "local verification",
      value:
        "local/demo evidence (locally checked-in golden / demo data; not " +
        "live-verified)",
      applicable: true,
      state: "locally_verified",
    },
    {
      concept: "live verification status",
      label: "live verification status",
      value:
        "live provider evidence not available / live B2 evidence not available " +
        "/ live Cloudflare evidence not available (local / check-only by " +
        "default; no live provider call)",
      applicable: true,
      state: "not_verified",
    },
    {
      concept: "disclosure boundary",
      label: "disclosure boundary",
      value:
        "demo / readiness disclosure boundary, consistent with PS-037: proof " +
        "does not equal truth; demo mode does not equal production readiness; " +
        "the production readiness layer label does not equal a production " +
        "readiness claim; the readiness checklist does not equal production " +
        "security; local demo mode does not equal live deployment; the " +
        "cold-start mitigation plan does not equal a measured performance " +
        "guarantee; the low-cost demo posture does not equal cost guarantee; " +
        "local fallback does not equal live provider availability; checked-in " +
        "evidence does not equal live B2 availability; the Cloudflare " +
        "dependency posture does not equal live Cloudflare availability; " +
        "demo/golden readiness evidence does not equal production compliance",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "not claimed",
      label: "not claimed",
      value:
        "the honest set of things ProofStudio does not claim for the demo / " +
        "readiness layer",
      applicable: true,
      state: "not_claimed",
    },
    {
      concept: "unknown",
      label: "unknown",
      value:
        "what remains unknown or not surfaced for the demo / readiness layer",
      applicable: true,
      state: "unknown",
    },
    {
      concept: "planned",
      label: "planned",
      value:
        "what is planned but not yet live for the demo / readiness layer " +
        "(cold-start mitigation plan / startup health / cost-control posture / " +
        "provider fallback / failure-mode evidence / export-offline evidence " +
        "are planned, not live)",
      applicable: true,
      state: "planned",
    },
  ];

// ---------------------------------------------------------------------------
// Required deferred later-slice / honest unavailable / not-claimed / planned /
// ready-for-local-demo states (spec section 10.6 / 21). Verbatim.
//
// These are non-claim states: they state what is not available, not claimed,
// planned, ready for local demo, or unknown, owned by PS-038 or a later slice,
// and must never be read as a hidden proof. PS-038 must not fake a live
// deployment, a production deployment, a production readiness, a production
// security, a production compliance, a cold-start measurement, or a live
// provider / B2 / Cloudflare availability.
// ---------------------------------------------------------------------------

export const PRODUCTION_READINESS_DEMO_MODE_DEFERRED_HEADING =
  "honest unavailable / not-claimed / planned / deferred states";

export const PRODUCTION_READINESS_DEMO_MODE_DEFERRED_STATES: readonly string[] = [
  "local/demo evidence",
  "ready for local demo",
  "production deployment not available",
  "production readiness evidence not available",
  "production security evidence not available",
  "production compliance evidence not available",
  "live provider evidence not available",
  "live B2 evidence not available",
  "live Cloudflare evidence not available",
  "cold-start measurement not available",
  "cold-start mitigation planned",
  "final submission packaging deferred to PS-039",
  "not claimed",
  "unknown",
  "planned",
];

// The later slice / out-of-scope owner for each deferred / not-claimed state.
// Surfaced so no reviewer mistakes an absent proof for a hidden proof.
export const PRODUCTION_READINESS_DEMO_MODE_DEFERRED_OWNERS: readonly string[] = [
  "local/demo evidence -> default posture (local / golden / demo fixture evidence, not live evidence)",
  "ready for local demo -> default posture (the app can be demoed locally / statically from checked-in evidence)",
  "production deployment not available -> out of scope (PS-038 is not a live deployment)",
  "production readiness evidence not available -> out of scope (PS-038 is not a production readiness system)",
  "production security evidence not available -> out of scope (PS-038 is not a production security system)",
  "production compliance evidence not available -> out of scope (PS-038 is not a production compliance system)",
  "live provider evidence not available -> default posture (no live provider call; local / check-only by default)",
  "live B2 evidence not available -> default posture (no live B2 read; local / check-only by default)",
  "live Cloudflare evidence not available -> default posture (no live Cloudflare API call; local / check-only by default)",
  "cold-start measurement not available -> out of scope (PS-038 owns the cold-start mitigation plan only; the cold-start mitigation plan does not equal a measured performance guarantee)",
  "cold-start mitigation planned -> PS-038 (PS-038 owns the plan; the implementation and measurement remain later / out-of-scope work)",
  "final submission packaging deferred to PS-039 -> PS-039 (PS-038 is not a final submission packaging system)",
  "not claimed -> out of scope (PS-038 states what it does not prove for the demo / readiness layer)",
  "unknown -> honest state (what remains unknown or not surfaced for the demo / readiness layer)",
  "planned -> honest state (what is planned but not yet live for the demo / readiness layer)",
];

// ---------------------------------------------------------------------------
// Cross-reference statements with the PS-037 Disclosure + Trust Boundary, the
// PS-037a Multimodal Proof Layer, the PS-037b Transcript/Timestamp Evidence
// layer, the PS-037c Voice/Audio Evidence Provider Choice layer, the PS-037d
// Gemini Campaign Intelligence / Judge Narrative layer, and the PS-037e
// Cloudflare Low-Cost Backbone layer. Surfaced so the layer states explicitly
// that it integrates / cross-references each predecessor layer and never
// weakens its contract.
// ---------------------------------------------------------------------------

export const PRODUCTION_READINESS_DEMO_MODE_TRUST_BOUNDARY_CROSS_REFERENCE =
  "Cross-references the PS-037 Disclosure + Trust Boundary: renders alongside " +
  "TrustBoundaryLayer, reuses the shared disclosure concepts, and never " +
  "contradicts the PS-037 boundary.";

export const PRODUCTION_READINESS_DEMO_MODE_MULTIMODAL_CROSS_REFERENCE =
  "Cross-references the PS-037a Multimodal Proof Layer: renders alongside " +
  "MultimodalProofLayer and surfaces an honest multimodal proof " +
  "cross-reference. Manifest reference " +
  PRODUCTION_READINESS_DEMO_MODE_MANIFEST_REFERENCE +
  " / manifest hash " +
  PRODUCTION_READINESS_DEMO_MODE_MANIFEST_HASH +
  " reused from PS-035A via PS-037a.";

export const PRODUCTION_READINESS_DEMO_MODE_TRANSCRIPT_CROSS_REFERENCE =
  "Cross-references the PS-037b Transcript/Timestamp Evidence layer: renders " +
  "alongside TranscriptTimestampEvidenceLayer and surfaces an honest " +
  "transcript/timestamp cross-reference.";

export const PRODUCTION_READINESS_DEMO_MODE_VOICE_AUDIO_CROSS_REFERENCE =
  "Cross-references the PS-037c Voice/Audio Evidence Provider Choice layer: " +
  "renders alongside VoiceAudioEvidenceChoiceLayer and surfaces an honest " +
  "voice/audio evidence cross-reference.";

export const PRODUCTION_READINESS_DEMO_MODE_CAMPAIGN_INTELLIGENCE_CROSS_REFERENCE =
  "Cross-references the PS-037d Gemini Campaign Intelligence / Judge Narrative " +
  "layer: renders alongside CampaignIntelligenceJudgeNarrativeLayer and " +
  "surfaces an honest campaign intelligence cross-reference.";

export const PRODUCTION_READINESS_DEMO_MODE_CLOUDFLARE_BACKBONE_CROSS_REFERENCE =
  "Cross-references the PS-037e Cloudflare Low-Cost Backbone layer: renders " +
  "alongside CloudflareLowCostBackboneLayer and surfaces an honest Cloudflare " +
  "low-cost backbone cross-reference (Cloudflare named for dependency posture " +
  "labeling only; the Cloudflare dependency posture does not equal live " +
  "Cloudflare availability).";

// ---------------------------------------------------------------------------
// Required de-escalation pairs (spec section 10.7 / 21). Surfaced verbatim so
// a judge never mistakes a strong-sounding demo mode label, production
// readiness layer label, readiness checklist, cold-start mitigation plan, local
// fallback, checked-in evidence, Cloudflare dependency posture, or low-cost
// demo posture for a stronger guarantee. Stated as non-claims so context-aware
// forbidden-claim scanners never flag these boundary terms as overclaims.
// ---------------------------------------------------------------------------

export const PRODUCTION_READINESS_DEMO_MODE_DEESCALATION_PAIRS: readonly string[] =
  [
    "proof does not equal truth",
    "demo mode does not equal production readiness",
    "production readiness layer does not equal production readiness claim",
    "readiness checklist does not equal production security",
    "local demo mode does not equal live deployment",
    "cold-start mitigation plan does not equal measured performance guarantee",
    "low-cost demo posture does not equal cost guarantee",
    "local fallback does not equal live provider availability",
    "checked-in evidence does not equal live B2 availability",
    "Cloudflare dependency posture does not equal live Cloudflare availability",
    "demo/golden readiness evidence does not equal production compliance",
  ];

// ---------------------------------------------------------------------------
// Required negative boundary strings (spec section 10.8 / 21). Surfaced
// verbatim. These are the canonical "not claimed" set rendered as pills.
// ---------------------------------------------------------------------------

export const PRODUCTION_READINESS_DEMO_MODE_NEGATIVE_BOUNDARY: readonly string[] =
  [
    "not production readiness",
    "not production security",
    "not production compliance",
    "not legal compliance",
    "not live deployment",
    "not Cloudflare deployment",
    "not Cloudflare availability",
    "not Backblaze B2 live availability",
    "not provider availability",
    "not model availability",
    "not uptime guarantee",
    "not cost guarantee",
    "not performance guarantee",
    "not cold-start performance guarantee",
    "not load-test coverage",
    "not vulnerability scan coverage",
    "not penetration test coverage",
    "not incident response readiness",
    "not SLO/SLA guarantee",
    "not data retention compliance",
    "not privacy compliance",
    "not Object Lock",
    "not tamper-proof",
    "not browser-side B2 byte verification",
    "not semantic truth",
    "not legal authenticity",
    "not human authorship",
    "not C2PA authenticity",
    "not campaign performance prediction",
    "not marketing effectiveness proof",
    "not model output truth",
  ];

// ---------------------------------------------------------------------------
// Persistent demo / readiness boundary statement (spec section 11). Verbatim.
// Written as non-claim copy so the project's forbidden-claim scanners never
// flag the boundary terms.
// ---------------------------------------------------------------------------

export const PRODUCTION_READINESS_DEMO_MODE_PERSISTENT_STATEMENT =
  "ProofStudio proves what the pipeline recorded for the demo path and " +
  "readiness posture. Proof does not equal truth. Demo mode does not equal " +
  "production readiness. The production readiness layer label does not equal " +
  "a production readiness claim. A readiness checklist does not equal " +
  "production security. Local demo mode does not equal live deployment. A " +
  "cold-start mitigation plan does not equal a measured performance " +
  "guarantee. A low-cost demo posture does not equal cost guarantee. Local " +
  "fallback does not equal live provider availability. Checked-in evidence " +
  "does not equal live B2 availability. A Cloudflare dependency posture does " +
  "not equal live Cloudflare availability. Demo/golden readiness evidence " +
  "does not equal production compliance.";

// Compact one-line summary used by the summary variant.
export const PRODUCTION_READINESS_DEMO_MODE_SUMMARY =
  "Production Readiness + Demo Mode: a demo mode / readiness posture / " +
  "cold-start mitigation plan over recorded proof evidence; ready for local " +
  "demo; local / static / golden / checked-in fallback by default; demo mode " +
  "does not equal production readiness; production deployment not available; " +
  "production readiness evidence not available; live provider evidence not " +
  "available; live B2 evidence not available; live Cloudflare evidence not " +
  "available; cold-start mitigation planned; final submission packaging " +
  "deferred to PS-039; proof does not equal truth.";

// ---------------------------------------------------------------------------
// Truth-boundary posture (spec section 10.1 / 21). Surfaced so the disclosure
// contract is deterministic and auditable. These are non-claim posture notes.
// ---------------------------------------------------------------------------

export const PRODUCTION_READINESS_DEMO_MODE_POSTURE: readonly string[] = [
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
// Required core proof surfaces (spec section 10.3). Listed so the Production
// Readiness + Demo Mode contract documents exactly where the shared layer is
// rendered.
// ---------------------------------------------------------------------------

export const PRODUCTION_READINESS_DEMO_MODE_REQUIRED_SURFACES: readonly string[] =
  [
    "Judge Cockpit Home",
    "B2 Evidence Explorer",
    "Manifest Verification Panel",
    "B2 Rehydrate Comparison",
    "Archive / Rehydrate / B2 Audit Vault",
    "Review + Approval Workspace",
    "Judge Evidence Pack",
    "Public Provenance Passport",
    "Review Room",
  ];
