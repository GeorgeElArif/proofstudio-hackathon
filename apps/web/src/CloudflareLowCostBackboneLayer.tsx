// PS-037e Cloudflare Low-Cost Backbone -- shared component.
//
// A reusable Cloudflare low-cost backbone layer rendered additively on every
// core proof surface so the low-cost backbone / infrastructure posture /
// deployment readiness framing is identical everywhere proof is shown. It reads
// only from apps/web/src/cloudflareLowCostBackbone.ts. It is a plan-over-
// recorded-proof layer, not a new proof surface, not a new route, and not a new
// backend endpoint.
//
// It is purely client-side by default: it makes no Cloudflare API call, mutates
// no DNS, creates no Cloudflare resource, deploys no Cloudflare Pages, deploys
// no Cloudflare Workers, performs no Cloudflare R2 live read, performs no
// Cloudflare R2 write, performs no Backblaze B2 write, calls no provider, reads
// no B2 object, performs no browser-side B2 byte verification, performs no
// broad B2 scan, and writes no B2 object. It only renders the canonical
// Cloudflare low-cost backbone contract sourced from accepted local / golden /
// demo data.
//
// Variants (following the project's `variant` convention):
//   - variant="summary"  -> a compact backbone posture summary.
//   - variant="panel"    -> the expanded infrastructure-posture panel.
//
// It renders alongside the existing TrustBoundaryLayer (PS-037), the
// MultimodalProofLayer (PS-037a), the TranscriptTimestampEvidenceLayer
// (PS-037b), the VoiceAudioEvidenceChoiceLayer (PS-037c), and the
// CampaignIntelligenceJudgeNarrativeLayer (PS-037d) so the PS-037 disclosure
// boundary, the PS-037a multimodal proof contract, the PS-037b transcript/
// timestamp contract, the PS-037c voice/audio evidence provider choice
// contract, and the PS-037d campaign intelligence / judge narrative contract
// stay canonical; it cross-references PS-037 (reuses the shared disclosure
// concepts), cross-references PS-037a (surfaces an honest multimodal proof
// cross-reference), cross-references PS-037b (surfaces an honest
// transcript/timestamp cross-reference), cross-references PS-037c (surfaces an
// honest voice/audio evidence cross-reference), cross-references PS-037d
// (surfaces an honest campaign intelligence cross-reference), and never
// contradicts any of those contracts.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Cloudflare
// Low-Cost Backbone layer is not live deployment, not production readiness, not
// production security, not production compliance, not legal compliance, not
// uptime guarantee, not cost guarantee, not performance guarantee, not
// cold-start mitigation implementation, not DNS ownership, not Cloudflare
// resource existence, not Cloudflare Pages availability, not Cloudflare Workers
// availability, not Cloudflare R2 availability, not Backblaze B2 live
// availability, not Object Lock, not tamper-proof, not browser-side B2 byte
// verification, not live B2 availability, not semantic truth, not legal
// authenticity, not human authorship, and not C2PA authenticity.

import {
  CLOUDFLARE_LOW_COST_BACKBONE_CAMPAIGN_INTELLIGENCE_CROSS_REFERENCE,
  CLOUDFLARE_LOW_COST_BACKBONE_CONCEPTS,
  CLOUDFLARE_LOW_COST_BACKBONE_DEESCALATION_PAIRS,
  CLOUDFLARE_LOW_COST_BACKBONE_DEFERRED_HEADING,
  CLOUDFLARE_LOW_COST_BACKBONE_DEFERRED_OWNERS,
  CLOUDFLARE_LOW_COST_BACKBONE_DEFERRED_STATES,
  CLOUDFLARE_LOW_COST_BACKBONE_ITEMS,
  CLOUDFLARE_LOW_COST_BACKBONE_MULTIMODAL_CROSS_REFERENCE,
  CLOUDFLARE_LOW_COST_BACKBONE_NEGATIVE_BOUNDARY,
  CLOUDFLARE_LOW_COST_BACKBONE_PERSISTENT_STATEMENT,
  CLOUDFLARE_LOW_COST_BACKBONE_POSITIONING,
  CLOUDFLARE_LOW_COST_BACKBONE_POSTURE,
  CLOUDFLARE_LOW_COST_BACKBONE_PROVIDER_LABEL,
  CLOUDFLARE_LOW_COST_BACKBONE_SLICE_ID,
  CLOUDFLARE_LOW_COST_BACKBONE_SUMMARY,
  CLOUDFLARE_LOW_COST_BACKBONE_TITLE,
  CLOUDFLARE_LOW_COST_BACKBONE_TRANSCRIPT_CROSS_REFERENCE,
  CLOUDFLARE_LOW_COST_BACKBONE_TRUST_BOUNDARY_CROSS_REFERENCE,
  CLOUDFLARE_LOW_COST_BACKBONE_VOICE_AUDIO_CROSS_REFERENCE,
} from "./cloudflareLowCostBackbone";

type CloudflareLowCostBackboneLayerVariant = "panel" | "summary";

// Per-row concept columns rendered in the expanded panel. Each label is a
// required Cloudflare low-cost backbone concept string (spec section 10.2 / 21).
const ROW_COLUMNS: { key: keyof typeof SAMPLE_ITEM; label: string }[] = [
  { key: "concept", label: "concept" },
  { key: "label", label: "label" },
  { key: "value", label: "value" },
  { key: "applicable", label: "applicable" },
  { key: "state", label: "state" },
];

// A reference item used only to satisfy the column `key` typing against the
// CloudflareBackboneItem shape. The real rows iterate
// CLOUDFLARE_LOW_COST_BACKBONE_ITEMS.
const SAMPLE_ITEM = CLOUDFLARE_LOW_COST_BACKBONE_ITEMS[0];

export function CloudflareLowCostBackboneLayer({
  variant = "panel",
}: {
  variant?: CloudflareLowCostBackboneLayerVariant;
}) {
  if (variant === "summary") {
    return (
      <aside
        className="cloudflare-low-cost-backbone-layer cloudflare-low-cost-backbone-layer-summary"
        aria-label={CLOUDFLARE_LOW_COST_BACKBONE_TITLE}
      >
        <span className="cloudflare-low-cost-backbone-layer-tag">
          {CLOUDFLARE_LOW_COST_BACKBONE_SLICE_ID}
        </span>
        <span className="cloudflare-low-cost-backbone-layer-summary-text">
          {CLOUDFLARE_LOW_COST_BACKBONE_SUMMARY}
        </span>
        <ul className="cloudflare-low-cost-backbone-layer-deferred-inline">
          {CLOUDFLARE_LOW_COST_BACKBONE_DEFERRED_STATES.map((s) => (
            <li
              className="cloudflare-low-cost-backbone-layer-deferred-pill"
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
      className="cloudflare-low-cost-backbone-layer cloudflare-low-cost-backbone-layer-panel"
      aria-label={CLOUDFLARE_LOW_COST_BACKBONE_TITLE}
    >
      <header className="cloudflare-low-cost-backbone-layer-head">
        <span className="cloudflare-low-cost-backbone-layer-tag">
          {CLOUDFLARE_LOW_COST_BACKBONE_SLICE_ID}
        </span>
        <h3>{CLOUDFLARE_LOW_COST_BACKBONE_TITLE}</h3>
        <p className="cloudflare-low-cost-backbone-layer-positioning">
          {CLOUDFLARE_LOW_COST_BACKBONE_POSITIONING}
        </p>
      </header>

      {/* Backbone-plan / infrastructure-posture block */}
      <div
        className="cloudflare-low-cost-backbone-layer-plan"
        id="cloudflare-low-cost-backbone-layer-plan"
      >
        <h4>low-cost backbone plan</h4>
        <p className="cloudflare-low-cost-backbone-layer-intro">
          One honest view of the low-cost backbone, the infrastructure posture,
          the deployment readiness evidence, the backbone status, and the
          deployment status. The recorded low-cost backbone plan and the
          recorded infrastructure posture are present as local / demo plans
          over recorded proof evidence; no live Cloudflare deployment exists.
        </p>
        <ul className="cloudflare-low-cost-backbone-layer-rows">
          {CLOUDFLARE_LOW_COST_BACKBONE_ITEMS.filter((item) =>
            [
              "low-cost backbone",
              "infrastructure posture",
              "deployment readiness evidence",
              "backbone status",
              "deployment status",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="cloudflare-low-cost-backbone-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              {ROW_COLUMNS.map((col) => (
                <div
                  className="cloudflare-low-cost-backbone-layer-field"
                  key={col.key}
                >
                  <span className="cloudflare-low-cost-backbone-layer-concept">
                    {col.label}
                  </span>
                  <span className="cloudflare-low-cost-backbone-layer-value">
                    {String(item[col.key])}
                  </span>
                </div>
              ))}
            </li>
          ))}
        </ul>
      </div>

      {/* Cloudflare / deployment block */}
      <div
        className="cloudflare-low-cost-backbone-layer-cloudflare"
        id="cloudflare-low-cost-backbone-layer-cloudflare"
      >
        <h4>Cloudflare / deployment</h4>
        <p className="cloudflare-low-cost-backbone-layer-intro">
          One honest view of the Cloudflare provider label ({CLOUDFLARE_LOW_COST_BACKBONE_PROVIDER_LABEL},
          named for evidence labeling only), the Cloudflare Pages plan, the
          Cloudflare Workers plan, the Cloudflare R2 plan, the Cloudflare
          resource status, and the DNS status. planned means the concept is
          reserved but not live; not_available means no live Cloudflare
          deployment / resource / DNS evidence is checked into accepted
          evidence; PS-037e never fakes a live deployment, a Cloudflare
          resource, a DNS change, a Cloudflare Pages deployment, a Cloudflare
          Workers deployment, a Cloudflare R2 availability, or a Backblaze B2
          live availability.
        </p>
        <ul className="cloudflare-low-cost-backbone-layer-rows">
          {CLOUDFLARE_LOW_COST_BACKBONE_ITEMS.filter((item) =>
            [
              "Cloudflare provider label",
              "Cloudflare Pages plan",
              "Cloudflare Workers plan",
              "Cloudflare R2 plan",
              "Cloudflare resource status",
              "DNS status",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="cloudflare-low-cost-backbone-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="cloudflare-low-cost-backbone-layer-concept">
                {item.label}
              </span>
              <span className="cloudflare-low-cost-backbone-layer-value">
                {item.value}
              </span>
              <span className="cloudflare-low-cost-backbone-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* System-of-record block */}
      <div
        className="cloudflare-low-cost-backbone-layer-system-of-record"
        id="cloudflare-low-cost-backbone-layer-system-of-record"
      >
        <h4>system of record</h4>
        <p className="cloudflare-low-cost-backbone-layer-intro">
          One honest view of the Backblaze B2 system of record, the B2 archive
          remains system of record indicator, the Genblaze manifest evidence
          remains system of record indicator, the cost-control status, the
          cold-start mitigation status, and the production readiness status.
          Backblaze B2 remains the durable proof/archive system of record; the
          Cloudflare low-cost backbone does not displace it.
        </p>
        <ul className="cloudflare-low-cost-backbone-layer-rows">
          {CLOUDFLARE_LOW_COST_BACKBONE_ITEMS.filter((item) =>
            [
              "Backblaze B2 system of record",
              "B2 archive remains system of record",
              "Genblaze manifest evidence remains system of record",
              "cost-control status",
              "cold-start mitigation status",
              "production readiness status",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="cloudflare-low-cost-backbone-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="cloudflare-low-cost-backbone-layer-concept">
                {item.label}
              </span>
              <span className="cloudflare-low-cost-backbone-layer-value">
                {item.value}
              </span>
              <span className="cloudflare-low-cost-backbone-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Cross-reference block */}
      <div
        className="cloudflare-low-cost-backbone-layer-cross-references"
        id="cloudflare-low-cost-backbone-layer-cross-references"
      >
        <h4>cross-references</h4>
        <p className="cloudflare-low-cost-backbone-layer-intro">
          One honest view of the trust boundary cross-reference, the multimodal
          proof cross-reference, the transcript/timestamp cross-reference, the
          voice/audio evidence cross-reference, and the campaign intelligence
          cross-reference. Each cross-reference points at recorded evidence the
          low-cost backbone layer is built over (recorded-only, not
          live-verified here).
        </p>
        <ul className="cloudflare-low-cost-backbone-layer-rows">
          {CLOUDFLARE_LOW_COST_BACKBONE_ITEMS.filter((item) =>
            [
              "trust boundary cross-reference",
              "multimodal proof cross-reference",
              "transcript/timestamp cross-reference",
              "voice/audio evidence cross-reference",
              "campaign intelligence cross-reference",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="cloudflare-low-cost-backbone-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="cloudflare-low-cost-backbone-layer-concept">
                {item.label}
              </span>
              <span className="cloudflare-low-cost-backbone-layer-value">
                {item.value}
              </span>
              <span className="cloudflare-low-cost-backbone-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Local / live verification block */}
      <div
        className="cloudflare-low-cost-backbone-layer-local-live"
        id="cloudflare-low-cost-backbone-layer-local-live"
      >
        <h4>local / live verification</h4>
        <ul className="cloudflare-low-cost-backbone-layer-rows">
          {CLOUDFLARE_LOW_COST_BACKBONE_ITEMS.filter((item) =>
            [
              "local verification",
              "live verification status",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="cloudflare-low-cost-backbone-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="cloudflare-low-cost-backbone-layer-concept">
                {item.label}
              </span>
              <span className="cloudflare-low-cost-backbone-layer-value">
                {item.value}
              </span>
              <span className="cloudflare-low-cost-backbone-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Cross-reference with the PS-037 Disclosure + Trust Boundary. */}
      <p className="cloudflare-low-cost-backbone-layer-trust-boundary-cross-reference">
        {CLOUDFLARE_LOW_COST_BACKBONE_TRUST_BOUNDARY_CROSS_REFERENCE}
      </p>

      {/* Cross-reference with the PS-037a Multimodal Proof Layer. */}
      <p className="cloudflare-low-cost-backbone-layer-multimodal-cross-reference">
        {CLOUDFLARE_LOW_COST_BACKBONE_MULTIMODAL_CROSS_REFERENCE}
      </p>

      {/* Cross-reference with the PS-037b Transcript/Timestamp Evidence layer. */}
      <p className="cloudflare-low-cost-backbone-layer-transcript-cross-reference">
        {CLOUDFLARE_LOW_COST_BACKBONE_TRANSCRIPT_CROSS_REFERENCE}
      </p>

      {/* Cross-reference with the PS-037c Voice/Audio Evidence Provider Choice layer. */}
      <p className="cloudflare-low-cost-backbone-layer-voice-audio-cross-reference">
        {CLOUDFLARE_LOW_COST_BACKBONE_VOICE_AUDIO_CROSS_REFERENCE}
      </p>

      {/* Cross-reference with the PS-037d Gemini Campaign Intelligence / Judge Narrative layer. */}
      <p className="cloudflare-low-cost-backbone-layer-campaign-intelligence-cross-reference">
        {CLOUDFLARE_LOW_COST_BACKBONE_CAMPAIGN_INTELLIGENCE_CROSS_REFERENCE}
      </p>

      {/* Honest unavailable / not-claimed / planned / deferred states (verbatim). */}
      <div
        className="cloudflare-low-cost-backbone-layer-deferred"
        id="cloudflare-low-cost-backbone-layer-deferred"
      >
        <h4>{CLOUDFLARE_LOW_COST_BACKBONE_DEFERRED_HEADING}</h4>
        <p className="cloudflare-low-cost-backbone-layer-intro">
          Honest unavailable / not-claimed / planned / deferred states. These
          are non-claims; an absent live deployment / Cloudflare resource / DNS
          / Cloudflare Pages / Cloudflare Workers / Cloudflare R2 / Backblaze B2
          / production readiness / production security / production compliance
          / cold-start mitigation proof is stated, never hidden, and never
          faked.
        </p>
        <div className="non-claims">
          {CLOUDFLARE_LOW_COST_BACKBONE_DEFERRED_STATES.map((s) => (
            <span className="pill warn" key={s}>
              <span className="dot" />
              {s}
            </span>
          ))}
        </div>
        <ul className="cloudflare-low-cost-backbone-layer-owners">
          {CLOUDFLARE_LOW_COST_BACKBONE_DEFERRED_OWNERS.map((o) => (
            <li
              className="cloudflare-low-cost-backbone-layer-owner"
              key={o}
            >
              <span className="mono">{o}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Not claimed (per low-cost backbone). */}
      <div
        className="cloudflare-low-cost-backbone-layer-not-claimed"
        id="cloudflare-low-cost-backbone-layer-not-claimed"
      >
        <h4>not claimed</h4>
        <div className="non-claims">
          {CLOUDFLARE_LOW_COST_BACKBONE_NEGATIVE_BOUNDARY.map((nc) => (
            <span className="pill warn" key={nc}>
              <span className="dot" />
              {nc}
            </span>
          ))}
        </div>
      </div>

      {/* De-escalation pairs (verbatim). */}
      <div
        className="cloudflare-low-cost-backbone-layer-deescalation"
        id="cloudflare-low-cost-backbone-layer-deescalation"
      >
        <h4>De-escalation pairs</h4>
        <ul className="cloudflare-low-cost-backbone-layer-pairs">
          {CLOUDFLARE_LOW_COST_BACKBONE_DEESCALATION_PAIRS.map((pair) => (
            <li
              className="cloudflare-low-cost-backbone-layer-pair"
              key={pair}
            >
              <span className="mono">{pair}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Concepts checklist (canonical Cloudflare low-cost backbone concepts). */}
      <div
        className="cloudflare-low-cost-backbone-layer-concepts"
        id="cloudflare-low-cost-backbone-layer-concepts"
      >
        <h4>Concepts</h4>
        <ul className="cloudflare-low-cost-backbone-layer-concept-list">
          {CLOUDFLARE_LOW_COST_BACKBONE_CONCEPTS.map((c) => (
            <li
              className="cloudflare-low-cost-backbone-layer-concept-item"
              key={c}
            >
              {c}
            </li>
          ))}
        </ul>
      </div>

      {/* Persistent boundary statement (verbatim). */}
      <p className="cloudflare-low-cost-backbone-layer-statement">
        {CLOUDFLARE_LOW_COST_BACKBONE_PERSISTENT_STATEMENT}
      </p>

      {/* Posture notes (non-claim). */}
      <p className="cloudflare-low-cost-backbone-layer-posture">
        {CLOUDFLARE_LOW_COST_BACKBONE_POSTURE.join(" · ")}.
      </p>
    </section>
  );
}
