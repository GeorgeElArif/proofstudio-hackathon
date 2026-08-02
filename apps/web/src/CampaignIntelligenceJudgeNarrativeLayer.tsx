// PS-037d Gemini Campaign Intelligence / Judge Narrative Layer -- shared
// component.
//
// A reusable campaign intelligence / judge narrative layer rendered additively
// on every core proof surface so the campaign-intelligence / judge-narrative
// framing is identical everywhere proof is shown. It reads only from
// apps/web/src/geminiCampaignIntelligence.ts. It is a narrative-over-recorded-
// proof layer, not a new proof surface, not a new route, and not a new backend
// endpoint.
//
// It is purely client-side by default: it makes no Gemini API call, calls no
// model, calls no provider, reads no B2 object, performs no browser-side B2
// byte verification, performs no broad B2 scan, and writes no B2 object. It
// only renders the canonical campaign intelligence / judge narrative contract
// sourced from accepted local / golden / demo data.
//
// Variants (following the project's `variant` convention):
//   - variant="summary"  -> a compact campaign evidence summary.
//   - variant="panel"    -> the expanded judge-narrative panel.
//
// It renders alongside the existing TrustBoundaryLayer (PS-037), the
// MultimodalProofLayer (PS-037a), the TranscriptTimestampEvidenceLayer
// (PS-037b), and the VoiceAudioEvidenceChoiceLayer (PS-037c) so the PS-037
// disclosure boundary, the PS-037a multimodal proof contract, the PS-037b
// transcript/timestamp contract, and the PS-037c voice/audio evidence provider
// choice contract stay canonical; it cross-references PS-037 (reuses the
// shared disclosure concepts), cross-references PS-037a (fills the campaign
// intelligence evidence PS-037a reserved as deferred), cross-references
// PS-037b (surfaces an honest transcript/timestamp cross-reference),
// cross-references PS-037c (surfaces an honest voice/audio evidence
// cross-reference), and never contradicts any of those contracts.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Gemini
// Campaign Intelligence / Judge Narrative Layer is not model output truth, not
// semantic truth, not legal authenticity, not human authorship, not C2PA
// authenticity, not Object Lock, not tamper-proof, not browser-side B2 byte
// verification, not live B2 availability, not live Gemini availability, not
// production security, not production compliance, not legal review, not
// chain-of-custody guarantee, not campaign performance prediction, not
// marketing effectiveness proof, not business outcome guarantee, not conversion
// lift, not revenue impact, not audience targeting accuracy, not ad compliance
// approval, not identity verification, not biometric identification, not
// deepfake detection, not content moderation, not OCR correctness, not
// transcript correctness, not timestamp correctness, not voice authenticity,
// not speaker identity, and not emotion truth.

import {
  GEMINI_CAMPAIGN_INTELLIGENCE_CONCEPTS,
  GEMINI_CAMPAIGN_INTELLIGENCE_DEESCALATION_PAIRS,
  GEMINI_CAMPAIGN_INTELLIGENCE_DEFERRED_HEADING,
  GEMINI_CAMPAIGN_INTELLIGENCE_DEFERRED_OWNERS,
  GEMINI_CAMPAIGN_INTELLIGENCE_DEFERRED_STATES,
  GEMINI_CAMPAIGN_INTELLIGENCE_ITEMS,
  GEMINI_CAMPAIGN_INTELLIGENCE_MULTIMODAL_CROSS_REFERENCE,
  GEMINI_CAMPAIGN_INTELLIGENCE_NEGATIVE_BOUNDARY,
  GEMINI_CAMPAIGN_INTELLIGENCE_PERSISTENT_STATEMENT,
  GEMINI_CAMPAIGN_INTELLIGENCE_POSITIONING,
  GEMINI_CAMPAIGN_INTELLIGENCE_POSTURE,
  GEMINI_CAMPAIGN_INTELLIGENCE_PROVIDER_LABEL,
  GEMINI_CAMPAIGN_INTELLIGENCE_SLICE_ID,
  GEMINI_CAMPAIGN_INTELLIGENCE_SUMMARY,
  GEMINI_CAMPAIGN_INTELLIGENCE_TITLE,
  GEMINI_CAMPAIGN_INTELLIGENCE_TRANSCRIPT_CROSS_REFERENCE,
  GEMINI_CAMPAIGN_INTELLIGENCE_TRUST_BOUNDARY_CROSS_REFERENCE,
  GEMINI_CAMPAIGN_INTELLIGENCE_VOICE_AUDIO_CROSS_REFERENCE,
} from "./geminiCampaignIntelligence";

type CampaignIntelligenceJudgeNarrativeLayerVariant = "panel" | "summary";

// Per-row concept columns rendered in the expanded panel. Each label is a
// required campaign intelligence / judge narrative concept string (spec section
// 10.2 / 21).
const ROW_COLUMNS: { key: keyof typeof SAMPLE_ITEM; label: string }[] = [
  { key: "concept", label: "concept" },
  { key: "label", label: "label" },
  { key: "value", label: "value" },
  { key: "applicable", label: "applicable" },
  { key: "state", label: "state" },
];

// A reference item used only to satisfy the column `key` typing against the
// CampaignIntelligenceItem shape. The real rows iterate
// GEMINI_CAMPAIGN_INTELLIGENCE_ITEMS.
const SAMPLE_ITEM = GEMINI_CAMPAIGN_INTELLIGENCE_ITEMS[0];

export function CampaignIntelligenceJudgeNarrativeLayer({
  variant = "panel",
}: {
  variant?: CampaignIntelligenceJudgeNarrativeLayerVariant;
}) {
  if (variant === "summary") {
    return (
      <aside
        className="campaign-intelligence-judge-narrative-layer campaign-intelligence-judge-narrative-layer-summary"
        aria-label={GEMINI_CAMPAIGN_INTELLIGENCE_TITLE}
      >
        <span className="campaign-intelligence-judge-narrative-layer-tag">
          {GEMINI_CAMPAIGN_INTELLIGENCE_SLICE_ID}
        </span>
        <span className="campaign-intelligence-judge-narrative-layer-summary-text">
          {GEMINI_CAMPAIGN_INTELLIGENCE_SUMMARY}
        </span>
        <ul className="campaign-intelligence-judge-narrative-layer-deferred-inline">
          {GEMINI_CAMPAIGN_INTELLIGENCE_DEFERRED_STATES.map((s) => (
            <li
              className="campaign-intelligence-judge-narrative-layer-deferred-pill"
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
      className="campaign-intelligence-judge-narrative-layer campaign-intelligence-judge-narrative-layer-panel"
      aria-label={GEMINI_CAMPAIGN_INTELLIGENCE_TITLE}
    >
      <header className="campaign-intelligence-judge-narrative-layer-head">
        <span className="campaign-intelligence-judge-narrative-layer-tag">
          {GEMINI_CAMPAIGN_INTELLIGENCE_SLICE_ID}
        </span>
        <h3>{GEMINI_CAMPAIGN_INTELLIGENCE_TITLE}</h3>
        <p className="campaign-intelligence-judge-narrative-layer-positioning">
          {GEMINI_CAMPAIGN_INTELLIGENCE_POSITIONING}
        </p>
      </header>

      {/* Campaign-narrative block */}
      <div
        className="campaign-intelligence-judge-narrative-layer-narrative"
        id="campaign-intelligence-judge-narrative-layer-narrative"
      >
        <h4>campaign narrative</h4>
        <p className="campaign-intelligence-judge-narrative-layer-intro">
          One honest view of the campaign proof narrative, the campaign
          evidence summary, the proof stack summary, and the campaign
          intelligence status / judge narrative status. The recorded campaign
          intelligence framing and the recorded judge narrative are present as
          local / demo narratives over recorded proof evidence; no live
          Gemini-generated campaign intelligence or live model-generated judge
          narrative is available.
        </p>
        <ul className="campaign-intelligence-judge-narrative-layer-rows">
          {GEMINI_CAMPAIGN_INTELLIGENCE_ITEMS.filter((item) =>
            [
              "campaign intelligence",
              "judge narrative",
              "campaign proof narrative",
              "campaign evidence summary",
              "proof stack summary",
              "campaign intelligence status",
              "judge narrative status",
              "narrative source evidence",
              "narrative source evidence references",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="campaign-intelligence-judge-narrative-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              {ROW_COLUMNS.map((col) => (
                <div
                  className="campaign-intelligence-judge-narrative-layer-field"
                  key={col.key}
                >
                  <span className="campaign-intelligence-judge-narrative-layer-concept">
                    {col.label}
                  </span>
                  <span className="campaign-intelligence-judge-narrative-layer-value">
                    {String(item[col.key])}
                  </span>
                </div>
              ))}
            </li>
          ))}
        </ul>
      </div>

      {/* Gemini / model-output block */}
      <div
        className="campaign-intelligence-judge-narrative-layer-model-output"
        id="campaign-intelligence-judge-narrative-layer-model-output"
      >
        <h4>Gemini / model output</h4>
        <p className="campaign-intelligence-judge-narrative-layer-intro">
          One honest view of the Gemini provider label ({GEMINI_CAMPAIGN_INTELLIGENCE_PROVIDER_LABEL},
          named for evidence labeling only), the model output reference, the
          model output digest, the model output status, and the provider
          activity status. not_available means no model output is checked into
          accepted evidence; PS-037d never fakes a model output reference, a
          model output digest, or a campaign intelligence output.
        </p>
        <ul className="campaign-intelligence-judge-narrative-layer-rows">
          {GEMINI_CAMPAIGN_INTELLIGENCE_ITEMS.filter((item) =>
            [
              "Gemini provider label",
              "model output reference",
              "model output digest",
              "model output status",
              "provider activity status",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="campaign-intelligence-judge-narrative-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="campaign-intelligence-judge-narrative-layer-concept">
                {item.label}
              </span>
              <span className="campaign-intelligence-judge-narrative-layer-value">
                {item.value}
              </span>
              <span className="campaign-intelligence-judge-narrative-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Narrative-source-evidence / cross-reference block */}
      <div
        className="campaign-intelligence-judge-narrative-layer-source-evidence"
        id="campaign-intelligence-judge-narrative-layer-source-evidence"
      >
        <h4>narrative source evidence / cross-references</h4>
        <p className="campaign-intelligence-judge-narrative-layer-intro">
          One honest view of the B2 evidence cross-reference, the manifest
          evidence cross-reference, the rehydrate evidence cross-reference, the
          trust boundary cross-reference, the multimodal proof cross-reference,
          the transcript/timestamp cross-reference, and the voice/audio evidence
          cross-reference. Each cross-reference points at recorded evidence the
          narrative is built over (recorded-only, not live-verified here).
        </p>
        <ul className="campaign-intelligence-judge-narrative-layer-rows">
          {GEMINI_CAMPAIGN_INTELLIGENCE_ITEMS.filter((item) =>
            [
              "B2 evidence cross-reference",
              "manifest evidence cross-reference",
              "rehydrate evidence cross-reference",
              "trust boundary cross-reference",
              "multimodal proof cross-reference",
              "transcript/timestamp cross-reference",
              "voice/audio evidence cross-reference",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="campaign-intelligence-judge-narrative-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="campaign-intelligence-judge-narrative-layer-concept">
                {item.label}
              </span>
              <span className="campaign-intelligence-judge-narrative-layer-value">
                {item.value}
              </span>
              <span className="campaign-intelligence-judge-narrative-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Local / live verification block */}
      <div
        className="campaign-intelligence-judge-narrative-layer-local-live"
        id="campaign-intelligence-judge-narrative-layer-local-live"
      >
        <h4>local / live verification</h4>
        <ul className="campaign-intelligence-judge-narrative-layer-rows">
          {GEMINI_CAMPAIGN_INTELLIGENCE_ITEMS.filter((item) =>
            [
              "local verification",
              "live verification status",
              "local/demo evidence",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="campaign-intelligence-judge-narrative-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="campaign-intelligence-judge-narrative-layer-concept">
                {item.label}
              </span>
              <span className="campaign-intelligence-judge-narrative-layer-value">
                {item.value}
              </span>
              <span className="campaign-intelligence-judge-narrative-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Cross-reference with the PS-037 Disclosure + Trust Boundary. */}
      <p className="campaign-intelligence-judge-narrative-layer-cross-reference">
        {GEMINI_CAMPAIGN_INTELLIGENCE_TRUST_BOUNDARY_CROSS_REFERENCE}
      </p>

      {/* Cross-reference with the PS-037a Multimodal Proof Layer. */}
      <p className="campaign-intelligence-judge-narrative-layer-multimodal-cross-reference">
        {GEMINI_CAMPAIGN_INTELLIGENCE_MULTIMODAL_CROSS_REFERENCE}
      </p>

      {/* Cross-reference with the PS-037b Transcript/Timestamp Evidence layer. */}
      <p className="campaign-intelligence-judge-narrative-layer-transcript-cross-reference">
        {GEMINI_CAMPAIGN_INTELLIGENCE_TRANSCRIPT_CROSS_REFERENCE}
      </p>

      {/* Cross-reference with the PS-037c Voice/Audio Evidence Provider Choice layer. */}
      <p className="campaign-intelligence-judge-narrative-layer-voice-audio-cross-reference">
        {GEMINI_CAMPAIGN_INTELLIGENCE_VOICE_AUDIO_CROSS_REFERENCE}
      </p>

      {/* Honest unavailable / not-claimed / deferred states (verbatim). */}
      <div
        className="campaign-intelligence-judge-narrative-layer-deferred"
        id="campaign-intelligence-judge-narrative-layer-deferred"
      >
        <h4>{GEMINI_CAMPAIGN_INTELLIGENCE_DEFERRED_HEADING}</h4>
        <p className="campaign-intelligence-judge-narrative-layer-intro">
          Honest unavailable / not-claimed / deferred states. These are
          non-claims; an absent model output / campaign intelligence / judge
          narrative / campaign performance / marketing effectiveness / business
          outcome / conversion / revenue / audience / ad-compliance proof is
          stated, never hidden, and never faked.
        </p>
        <div className="non-claims">
          {GEMINI_CAMPAIGN_INTELLIGENCE_DEFERRED_STATES.map((s) => (
            <span className="pill warn" key={s}>
              <span className="dot" />
              {s}
            </span>
          ))}
        </div>
        <ul className="campaign-intelligence-judge-narrative-layer-owners">
          {GEMINI_CAMPAIGN_INTELLIGENCE_DEFERRED_OWNERS.map((o) => (
            <li
              className="campaign-intelligence-judge-narrative-layer-owner"
              key={o}
            >
              <span className="mono">{o}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Not claimed (per campaign intelligence / judge narrative). */}
      <div
        className="campaign-intelligence-judge-narrative-layer-not-claimed"
        id="campaign-intelligence-judge-narrative-layer-not-claimed"
      >
        <h4>not claimed</h4>
        <div className="non-claims">
          {GEMINI_CAMPAIGN_INTELLIGENCE_NEGATIVE_BOUNDARY.map((nc) => (
            <span className="pill warn" key={nc}>
              <span className="dot" />
              {nc}
            </span>
          ))}
        </div>
      </div>

      {/* De-escalation pairs (verbatim). */}
      <div
        className="campaign-intelligence-judge-narrative-layer-deescalation"
        id="campaign-intelligence-judge-narrative-layer-deescalation"
      >
        <h4>De-escalation pairs</h4>
        <ul className="campaign-intelligence-judge-narrative-layer-pairs">
          {GEMINI_CAMPAIGN_INTELLIGENCE_DEESCALATION_PAIRS.map((pair) => (
            <li
              className="campaign-intelligence-judge-narrative-layer-pair"
              key={pair}
            >
              <span className="mono">{pair}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Concepts checklist (canonical campaign intelligence / judge narrative concepts). */}
      <div
        className="campaign-intelligence-judge-narrative-layer-concepts"
        id="campaign-intelligence-judge-narrative-layer-concepts"
      >
        <h4>Concepts</h4>
        <ul className="campaign-intelligence-judge-narrative-layer-concept-list">
          {GEMINI_CAMPAIGN_INTELLIGENCE_CONCEPTS.map((c) => (
            <li
              className="campaign-intelligence-judge-narrative-layer-concept-item"
              key={c}
            >
              {c}
            </li>
          ))}
        </ul>
      </div>

      {/* Persistent boundary statement (verbatim). */}
      <p className="campaign-intelligence-judge-narrative-layer-statement">
        {GEMINI_CAMPAIGN_INTELLIGENCE_PERSISTENT_STATEMENT}
      </p>

      {/* Posture notes (non-claim). */}
      <p className="campaign-intelligence-judge-narrative-layer-posture">
        {GEMINI_CAMPAIGN_INTELLIGENCE_POSTURE.join(" · ")}.
      </p>
    </section>
  );
}
