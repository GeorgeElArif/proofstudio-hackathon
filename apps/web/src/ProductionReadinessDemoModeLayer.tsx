// PS-038 Production Readiness + Demo Mode -- shared component.
//
// A reusable Production Readiness + Demo Mode layer rendered additively on
// every core proof surface so the demo mode / readiness posture / local
// fallback / live dependency boundary / cold-start mitigation plan / readiness
// checklist framing is identical everywhere proof is shown. It reads only from
// apps/web/src/productionReadinessDemoMode.ts. It is a demo-path-and-
// readiness-posture-over-recorded-proof layer, not a new proof surface, not a
// new route, not a new backend endpoint, not a live deployment, and not a
// production readiness system.
//
// It is purely client-side by default: it makes no Cloudflare API call, mutates
// no DNS, creates no Cloudflare resource, deploys no Cloudflare Pages, deploys
// no Cloudflare Workers, performs no Cloudflare R2 live read, performs no
// Cloudflare R2 write, performs no Backblaze B2 write, calls no provider, calls
// no model, reads no B2 object, performs no browser-side B2 byte verification,
// performs no broad B2 scan, and writes no B2 object. It only renders the
// canonical Production Readiness + Demo Mode contract sourced from accepted
// local / golden / demo data.
//
// Variants (following the project's `variant` convention):
//   - variant="summary"  -> a compact demo / readiness posture summary.
//   - variant="panel"    -> the expanded readiness-posture / readiness-checklist
//                           panel.
//
// It renders alongside the existing TrustBoundaryLayer (PS-037), the
// MultimodalProofLayer (PS-037a), the TranscriptTimestampEvidenceLayer
// (PS-037b), the VoiceAudioEvidenceChoiceLayer (PS-037c), the
// CampaignIntelligenceJudgeNarrativeLayer (PS-037d), and the
// CloudflareLowCostBackboneLayer (PS-037e) so the PS-037 disclosure boundary,
// the PS-037a multimodal proof contract, the PS-037b transcript/timestamp
// contract, the PS-037c voice/audio evidence provider choice contract, the
// PS-037d campaign intelligence / judge narrative contract, and the PS-037e
// Cloudflare low-cost backbone contract stay canonical; it cross-references
// PS-037 (reuses the shared disclosure concepts), cross-references PS-037a
// (surfaces an honest multimodal proof cross-reference), cross-references
// PS-037b (surfaces an honest transcript/timestamp cross-reference),
// cross-references PS-037c (surfaces an honest voice/audio evidence
// cross-reference), cross-references PS-037d (surfaces an honest campaign
// intelligence cross-reference), cross-references PS-037e (surfaces an honest
// Cloudflare low-cost backbone cross-reference), and never contradicts any of
// those contracts.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Production
// Readiness + Demo Mode layer is not production readiness, not production
// security, not production compliance, not legal compliance, not live
// deployment, not Cloudflare deployment, not Cloudflare availability, not
// Backblaze B2 live availability, not provider availability, not model
// availability, not uptime guarantee, not cost guarantee, not performance
// guarantee, not cold-start performance guarantee, not load-test coverage, not
// vulnerability scan coverage, not penetration test coverage, not incident
// response readiness, not SLO/SLA guarantee, not data retention compliance, not
// privacy compliance, not Object Lock, not tamper-proof, not browser-side B2
// byte verification, not semantic truth, not legal authenticity, not human
// authorship, and not C2PA authenticity.

import {
  PRODUCTION_READINESS_DEMO_MODE_CAMPAIGN_INTELLIGENCE_CROSS_REFERENCE,
  PRODUCTION_READINESS_DEMO_MODE_CLOUDFLARE_BACKBONE_CROSS_REFERENCE,
  PRODUCTION_READINESS_DEMO_MODE_CONCEPTS,
  PRODUCTION_READINESS_DEMO_MODE_DEESCALATION_PAIRS,
  PRODUCTION_READINESS_DEMO_MODE_DEFERRED_HEADING,
  PRODUCTION_READINESS_DEMO_MODE_DEFERRED_OWNERS,
  PRODUCTION_READINESS_DEMO_MODE_DEFERRED_STATES,
  PRODUCTION_READINESS_DEMO_MODE_ITEMS,
  PRODUCTION_READINESS_DEMO_MODE_MULTIMODAL_CROSS_REFERENCE,
  PRODUCTION_READINESS_DEMO_MODE_NEGATIVE_BOUNDARY,
  PRODUCTION_READINESS_DEMO_MODE_PERSISTENT_STATEMENT,
  PRODUCTION_READINESS_DEMO_MODE_POSITIONING,
  PRODUCTION_READINESS_DEMO_MODE_POSTURE,
  PRODUCTION_READINESS_DEMO_MODE_SLICE_ID,
  PRODUCTION_READINESS_DEMO_MODE_SUMMARY,
  PRODUCTION_READINESS_DEMO_MODE_TITLE,
  PRODUCTION_READINESS_DEMO_MODE_TRANSCRIPT_CROSS_REFERENCE,
  PRODUCTION_READINESS_DEMO_MODE_TRUST_BOUNDARY_CROSS_REFERENCE,
  PRODUCTION_READINESS_DEMO_MODE_VOICE_AUDIO_CROSS_REFERENCE,
} from "./productionReadinessDemoMode";

type ProductionReadinessDemoModeLayerVariant = "panel" | "summary";

// Per-row concept columns rendered in the expanded panel. Each label is a
// required Production Readiness + Demo Mode concept string (spec section 10.2 /
// 21).
const ROW_COLUMNS: { key: keyof typeof SAMPLE_ITEM; label: string }[] = [
  { key: "concept", label: "concept" },
  { key: "label", label: "label" },
  { key: "value", label: "value" },
  { key: "applicable", label: "applicable" },
  { key: "state", label: "state" },
];

// A reference item used only to satisfy the column `key` typing against the
// ProductionReadinessDemoModeItem shape. The real rows iterate
// PRODUCTION_READINESS_DEMO_MODE_ITEMS.
const SAMPLE_ITEM = PRODUCTION_READINESS_DEMO_MODE_ITEMS[0];

export function ProductionReadinessDemoModeLayer({
  variant = "panel",
}: {
  variant?: ProductionReadinessDemoModeLayerVariant;
}) {
  if (variant === "summary") {
    return (
      <aside
        className="production-readiness-demo-mode-layer production-readiness-demo-mode-layer-summary"
        aria-label={PRODUCTION_READINESS_DEMO_MODE_TITLE}
      >
        <span className="production-readiness-demo-mode-layer-tag">
          {PRODUCTION_READINESS_DEMO_MODE_SLICE_ID}
        </span>
        <span className="production-readiness-demo-mode-layer-summary-text">
          {PRODUCTION_READINESS_DEMO_MODE_SUMMARY}
        </span>
        <ul className="production-readiness-demo-mode-layer-deferred-inline">
          {PRODUCTION_READINESS_DEMO_MODE_DEFERRED_STATES.map((s) => (
            <li
              className="production-readiness-demo-mode-layer-deferred-pill"
              key={s}
            >
              <span className="dot" />
              {s}
            </li>
          ))}
        </ul>
      </aside>
    );
  }

  return (
    <section
      className="production-readiness-demo-mode-layer production-readiness-demo-mode-layer-panel"
      aria-label={PRODUCTION_READINESS_DEMO_MODE_TITLE}
    >
      <header className="production-readiness-demo-mode-layer-head">
        <span className="production-readiness-demo-mode-layer-tag">
          {PRODUCTION_READINESS_DEMO_MODE_SLICE_ID}
        </span>
        <h3>{PRODUCTION_READINESS_DEMO_MODE_TITLE}</h3>
        <p className="production-readiness-demo-mode-layer-positioning">
          {PRODUCTION_READINESS_DEMO_MODE_POSITIONING}
        </p>
      </header>

      {/* Demo mode block */}
      <div
        className="production-readiness-demo-mode-layer-demo-mode"
        id="production-readiness-demo-mode-layer-demo-mode"
      >
        <h4>demo mode</h4>
        <p className="production-readiness-demo-mode-layer-intro">
          One honest view of demo mode, the readiness posture, the production
          readiness status, the demo mode status, the local demo status, and
          the judge demo status. The recorded demo mode plan and readiness
          posture are present as local / demo plans over recorded proof
          evidence; ready for local demo is the default posture; demo mode does
          not equal production readiness.
        </p>
        <ul className="production-readiness-demo-mode-layer-rows">
          {PRODUCTION_READINESS_DEMO_MODE_ITEMS.filter((item) =>
            [
              "demo mode",
              "readiness posture",
              "production readiness status",
              "demo mode status",
              "local demo status",
              "judge demo status",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="production-readiness-demo-mode-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              {ROW_COLUMNS.map((col) => (
                <div
                  className="production-readiness-demo-mode-layer-field"
                  key={col.key}
                >
                  <span className="production-readiness-demo-mode-layer-concept">
                    {col.label}
                  </span>
                  <span className="production-readiness-demo-mode-layer-value">
                    {String(item[col.key])}
                  </span>
                </div>
              ))}
            </li>
          ))}
        </ul>
      </div>

      {/* Local fallback block */}
      <div
        className="production-readiness-demo-mode-layer-local-fallback"
        id="production-readiness-demo-mode-layer-local-fallback"
      >
        <h4>local / fallback</h4>
        <p className="production-readiness-demo-mode-layer-intro">
          One honest view of the local/static fallback, the golden evidence
          fallback, the checked-in evidence fallback, the demo path evidence,
          the local verification, and the live verification status. The default
          posture is local / static / golden / checked-in fallback; ready for
          local demo; local fallback does not equal live provider availability;
          checked-in evidence does not equal live B2 availability.
        </p>
        <ul className="production-readiness-demo-mode-layer-rows">
          {PRODUCTION_READINESS_DEMO_MODE_ITEMS.filter((item) =>
            [
              "local/static fallback",
              "golden evidence fallback",
              "checked-in evidence fallback",
              "demo path evidence",
              "local verification",
              "live verification status",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="production-readiness-demo-mode-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="production-readiness-demo-mode-layer-concept">
                {item.label}
              </span>
              <span className="production-readiness-demo-mode-layer-value">
                {item.value}
              </span>
              <span className="production-readiness-demo-mode-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Live dependency block */}
      <div
        className="production-readiness-demo-mode-layer-live-dependency"
        id="production-readiness-demo-mode-layer-live-dependency"
      >
        <h4>live dependency</h4>
        <p className="production-readiness-demo-mode-layer-intro">
          One honest view of the live dependency status, the provider dependency
          status, the B2 dependency status, and the Cloudflare dependency
          status. not required for local demo means the judge demo needs no live
          provider / live B2 / live Cloudflare; the Cloudflare dependency
          posture does not equal live Cloudflare availability.
        </p>
        <ul className="production-readiness-demo-mode-layer-rows">
          {PRODUCTION_READINESS_DEMO_MODE_ITEMS.filter((item) =>
            [
              "live dependency status",
              "provider dependency status",
              "B2 dependency status",
              "Cloudflare dependency status",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="production-readiness-demo-mode-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="production-readiness-demo-mode-layer-concept">
                {item.label}
              </span>
              <span className="production-readiness-demo-mode-layer-value">
                {item.value}
              </span>
              <span className="production-readiness-demo-mode-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Readiness evidence block */}
      <div
        className="production-readiness-demo-mode-layer-readiness-evidence"
        id="production-readiness-demo-mode-layer-readiness-evidence"
      >
        <h4>readiness evidence</h4>
        <p className="production-readiness-demo-mode-layer-intro">
          One honest view of the deployment evidence status, the production
          security evidence status, the production compliance evidence status,
          the cold-start mitigation status, the startup health status, the
          cost-control status, the provider fallback status, the failure-mode
          status, the export/offline evidence status, and the readiness
          checklist evidence. not_available means no live evidence is checked
          into accepted evidence; planned means the concept is reserved but not
          live; PS-038 never fakes a live deployment, production readiness,
          production security, production compliance, or a cold-start
          measurement.
        </p>
        <ul className="production-readiness-demo-mode-layer-rows">
          {PRODUCTION_READINESS_DEMO_MODE_ITEMS.filter((item) =>
            [
              "deployment evidence status",
              "production security evidence status",
              "production compliance evidence status",
              "cold-start mitigation status",
              "startup health status",
              "cost-control status",
              "provider fallback status",
              "failure-mode status",
              "export/offline evidence status",
              "readiness checklist evidence",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="production-readiness-demo-mode-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="production-readiness-demo-mode-layer-concept">
                {item.label}
              </span>
              <span className="production-readiness-demo-mode-layer-value">
                {item.value}
              </span>
              <span className="production-readiness-demo-mode-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Cross-reference block */}
      <div
        className="production-readiness-demo-mode-layer-cross-references"
        id="production-readiness-demo-mode-layer-cross-references"
      >
        <h4>cross-references</h4>
        <p className="production-readiness-demo-mode-layer-intro">
          One honest view of the trust boundary cross-reference, the multimodal
          proof cross-reference, the transcript/timestamp cross-reference, the
          voice/audio evidence cross-reference, the campaign intelligence
          cross-reference, and the Cloudflare low-cost backbone cross-reference.
          Each cross-reference points at recorded evidence the Production
          Readiness + Demo Mode layer is built over (recorded-only, not
          live-verified here).
        </p>
        <ul className="production-readiness-demo-mode-layer-rows">
          {PRODUCTION_READINESS_DEMO_MODE_ITEMS.filter((item) =>
            [
              "trust boundary cross-reference",
              "multimodal proof cross-reference",
              "transcript/timestamp cross-reference",
              "voice/audio evidence cross-reference",
              "campaign intelligence cross-reference",
              "Cloudflare low-cost backbone cross-reference",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="production-readiness-demo-mode-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="production-readiness-demo-mode-layer-concept">
                {item.label}
              </span>
              <span className="production-readiness-demo-mode-layer-value">
                {item.value}
              </span>
              <span className="production-readiness-demo-mode-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Cross-reference with the PS-037 Disclosure + Trust Boundary. */}
      <p className="production-readiness-demo-mode-layer-trust-boundary-cross-reference">
        {PRODUCTION_READINESS_DEMO_MODE_TRUST_BOUNDARY_CROSS_REFERENCE}
      </p>

      {/* Cross-reference with the PS-037a Multimodal Proof Layer. */}
      <p className="production-readiness-demo-mode-layer-multimodal-cross-reference">
        {PRODUCTION_READINESS_DEMO_MODE_MULTIMODAL_CROSS_REFERENCE}
      </p>

      {/* Cross-reference with the PS-037b Transcript/Timestamp Evidence layer. */}
      <p className="production-readiness-demo-mode-layer-transcript-cross-reference">
        {PRODUCTION_READINESS_DEMO_MODE_TRANSCRIPT_CROSS_REFERENCE}
      </p>

      {/* Cross-reference with the PS-037c Voice/Audio Evidence Provider Choice layer. */}
      <p className="production-readiness-demo-mode-layer-voice-audio-cross-reference">
        {PRODUCTION_READINESS_DEMO_MODE_VOICE_AUDIO_CROSS_REFERENCE}
      </p>

      {/* Cross-reference with the PS-037d Gemini Campaign Intelligence / Judge Narrative layer. */}
      <p className="production-readiness-demo-mode-layer-campaign-intelligence-cross-reference">
        {PRODUCTION_READINESS_DEMO_MODE_CAMPAIGN_INTELLIGENCE_CROSS_REFERENCE}
      </p>

      {/* Cross-reference with the PS-037e Cloudflare Low-Cost Backbone layer. */}
      <p className="production-readiness-demo-mode-layer-cloudflare-backbone-cross-reference">
        {PRODUCTION_READINESS_DEMO_MODE_CLOUDFLARE_BACKBONE_CROSS_REFERENCE}
      </p>

      {/* Honest unavailable / not-claimed / planned / deferred states (verbatim). */}
      <div
        className="production-readiness-demo-mode-layer-deferred"
        id="production-readiness-demo-mode-layer-deferred"
      >
        <h4>{PRODUCTION_READINESS_DEMO_MODE_DEFERRED_HEADING}</h4>
        <p className="production-readiness-demo-mode-layer-intro">
          Honest unavailable / not-claimed / planned / deferred states. These
          are non-claims; an absent live deployment / production readiness /
          production security / production compliance / cold-start measurement /
          startup health / cost-control / live provider / live B2 / live
          Cloudflare / final submission packaging proof is stated, never hidden,
          and never faked.
        </p>
        <div className="non-claims">
          {PRODUCTION_READINESS_DEMO_MODE_DEFERRED_STATES.map((s) => (
            <span className="pill warn" key={s}>
              <span className="dot" />
              {s}
            </span>
          ))}
        </div>
        <ul className="production-readiness-demo-mode-layer-owners">
          {PRODUCTION_READINESS_DEMO_MODE_DEFERRED_OWNERS.map((o) => (
            <li
              className="production-readiness-demo-mode-layer-owner"
              key={o}
            >
              <span className="mono">{o}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Not claimed (per demo / readiness). */}
      <div
        className="production-readiness-demo-mode-layer-not-claimed"
        id="production-readiness-demo-mode-layer-not-claimed"
      >
        <h4>not claimed</h4>
        <div className="non-claims">
          {PRODUCTION_READINESS_DEMO_MODE_NEGATIVE_BOUNDARY.map((nc) => (
            <span className="pill warn" key={nc}>
              <span className="dot" />
              {nc}
            </span>
          ))}
        </div>
      </div>

      {/* De-escalation pairs (verbatim). */}
      <div
        className="production-readiness-demo-mode-layer-deescalation"
        id="production-readiness-demo-mode-layer-deescalation"
      >
        <h4>De-escalation pairs</h4>
        <ul className="production-readiness-demo-mode-layer-pairs">
          {PRODUCTION_READINESS_DEMO_MODE_DEESCALATION_PAIRS.map((pair) => (
            <li
              className="production-readiness-demo-mode-layer-pair"
              key={pair}
            >
              <span className="mono">{pair}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Concepts checklist (canonical Production Readiness + Demo Mode concepts). */}
      <div
        className="production-readiness-demo-mode-layer-concepts"
        id="production-readiness-demo-mode-layer-concepts"
      >
        <h4>Concepts</h4>
        <ul className="production-readiness-demo-mode-layer-concept-list">
          {PRODUCTION_READINESS_DEMO_MODE_CONCEPTS.map((c) => (
            <li
              className="production-readiness-demo-mode-layer-concept-item"
              key={c}
            >
              {c}
            </li>
          ))}
        </ul>
      </div>

      {/* Persistent boundary statement (verbatim). */}
      <p className="production-readiness-demo-mode-layer-statement">
        {PRODUCTION_READINESS_DEMO_MODE_PERSISTENT_STATEMENT}
      </p>

      {/* Posture notes (non-claim). */}
      <p className="production-readiness-demo-mode-layer-posture">
        {PRODUCTION_READINESS_DEMO_MODE_POSTURE.join(" · ")}.
      </p>
    </section>
  );
}
