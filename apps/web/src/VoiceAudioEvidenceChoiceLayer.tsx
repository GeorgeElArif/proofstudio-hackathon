// PS-037c Voice/Audio Evidence Provider Choice Layer -- shared component.
//
// A reusable voice/audio evidence provider choice layer rendered additively on
// every core proof surface so the voice/audio provider-choice framing is
// identical everywhere proof is shown. It reads only from
// apps/web/src/voiceAudioEvidenceChoice.ts. It is a voice/audio evidence
// provider choice layer, not a new proof surface, not a new route, and not a
// new backend endpoint.
//
// It is purely client-side by default: it makes no ElevenLabs API call, makes
// no Hume API call, calls no provider, reads no B2 object, performs no
// browser-side B2 byte verification, performs no broad B2 scan, and writes no
// B2 object. It only renders the canonical voice/audio evidence provider
// choice contract sourced from accepted local / golden / demo data.
//
// Variants (following the project's `variant` convention):
//   - variant="summary"  -> a compact voice/audio provider-choice summary.
//   - variant="panel"    -> the expanded voice/audio provider-choice panel.
//
// It renders alongside the existing TrustBoundaryLayer (PS-037), the
// MultimodalProofLayer (PS-037a), and the TranscriptTimestampEvidenceLayer
// (PS-037b) so the PS-037 disclosure boundary, the PS-037a multimodal proof
// contract, and the PS-037b transcript/timestamp contract stay canonical; it
// cross-references PS-037a (fills the voice/audio provider-choice evidence
// PS-037a reserved as deferred), cross-references PS-037b (surfaces an honest
// transcript/timestamp cross-reference), and never contradicts the PS-037
// boundary or the PS-037a deferred voice/emotion states or the PS-037b
// contract.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Voice/Audio
// Evidence Provider Choice Layer is not voice authenticity, not speaker
// identity, not biometric identification, not emotion truth, not psychological
// diagnosis, not health inference, not mental state diagnosis, not semantic
// truth, not legal authenticity, not human authorship, not C2PA authenticity,
// not Object Lock, not tamper-proof, not browser-side B2 byte verification,
// not live B2 availability, not live ElevenLabs availability, not live Hume
// availability, and not production security.

import {
  VOICE_AUDIO_EVIDENCE_CHOICE_CONCEPTS,
  VOICE_AUDIO_EVIDENCE_CHOICE_DEESCALATION_PAIRS,
  VOICE_AUDIO_EVIDENCE_CHOICE_DEFERRED_HEADING,
  VOICE_AUDIO_EVIDENCE_CHOICE_DEFERRED_OWNERS,
  VOICE_AUDIO_EVIDENCE_CHOICE_DEFERRED_STATES,
  VOICE_AUDIO_EVIDENCE_CHOICE_ITEMS,
  VOICE_AUDIO_EVIDENCE_CHOICE_MULTIMODAL_CROSS_REFERENCE,
  VOICE_AUDIO_EVIDENCE_CHOICE_NEGATIVE_BOUNDARY,
  VOICE_AUDIO_EVIDENCE_CHOICE_PERSISTENT_STATEMENT,
  VOICE_AUDIO_EVIDENCE_CHOICE_POSITIONING,
  VOICE_AUDIO_EVIDENCE_CHOICE_POSTURE,
  VOICE_AUDIO_EVIDENCE_CHOICE_SLICE_ID,
  VOICE_AUDIO_EVIDENCE_CHOICE_SUMMARY,
  VOICE_AUDIO_EVIDENCE_CHOICE_TITLE,
  VOICE_AUDIO_EVIDENCE_CHOICE_TRACKS,
  VOICE_AUDIO_EVIDENCE_CHOICE_TRANSCRIPT_CROSS_REFERENCE,
} from "./voiceAudioEvidenceChoice";

type VoiceAudioEvidenceChoiceLayerVariant = "panel" | "summary";

// Per-row concept columns rendered in the expanded panel. Each label is a
// required voice/audio evidence provider choice concept string (spec section
// 10.2 / 21).
const ROW_COLUMNS: { key: keyof typeof SAMPLE_ITEM; label: string }[] = [
  { key: "concept", label: "concept" },
  { key: "label", label: "label" },
  { key: "value", label: "value" },
  { key: "applicable", label: "applicable" },
  { key: "state", label: "state" },
];

// A reference item used only to satisfy the column `key` typing against the
// VoiceAudioEvidenceChoiceItem shape. The real rows iterate
// VOICE_AUDIO_EVIDENCE_CHOICE_ITEMS.
const SAMPLE_ITEM = VOICE_AUDIO_EVIDENCE_CHOICE_ITEMS[0];

export function VoiceAudioEvidenceChoiceLayer({
  variant = "panel",
}: {
  variant?: VoiceAudioEvidenceChoiceLayerVariant;
}) {
  if (variant === "summary") {
    return (
      <aside
        className="voice-audio-evidence-choice-layer voice-audio-evidence-choice-layer-summary"
        aria-label={VOICE_AUDIO_EVIDENCE_CHOICE_TITLE}
      >
        <span className="voice-audio-evidence-choice-layer-tag">
          {VOICE_AUDIO_EVIDENCE_CHOICE_SLICE_ID}
        </span>
        <span className="voice-audio-evidence-choice-layer-summary-text">
          {VOICE_AUDIO_EVIDENCE_CHOICE_SUMMARY}
        </span>
        <ul className="voice-audio-evidence-choice-layer-deferred-inline">
          {VOICE_AUDIO_EVIDENCE_CHOICE_DEFERRED_STATES.map((s) => (
            <li
              className="voice-audio-evidence-choice-layer-deferred-pill"
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
      className="voice-audio-evidence-choice-layer voice-audio-evidence-choice-layer-panel"
      aria-label={VOICE_AUDIO_EVIDENCE_CHOICE_TITLE}
    >
      <header className="voice-audio-evidence-choice-layer-head">
        <span className="voice-audio-evidence-choice-layer-tag">
          {VOICE_AUDIO_EVIDENCE_CHOICE_SLICE_ID}
        </span>
        <h3>{VOICE_AUDIO_EVIDENCE_CHOICE_TITLE}</h3>
        <p className="voice-audio-evidence-choice-layer-positioning">
          {VOICE_AUDIO_EVIDENCE_CHOICE_POSITIONING}
        </p>
      </header>

      {/* Provider-choice block */}
      <div
        className="voice-audio-evidence-choice-layer-choice"
        id="voice-audio-evidence-choice-layer-choice"
      >
        <h4>provider choice</h4>
        <p className="voice-audio-evidence-choice-layer-intro">
          One honest view of which voice/audio evidence path is selected and the
          two evidence tracks (ElevenLabs Voiceover Artifact Evidence / Hume
          Emotion-Signal Evidence), each with its honest present / not available
          / not claimed / unknown status. Provider choice does not equal
          provider availability.
        </p>
        <ul className="voice-audio-evidence-choice-layer-rows">
          {VOICE_AUDIO_EVIDENCE_CHOICE_ITEMS.filter((item) =>
            [
              "provider choice",
              "selected voice/audio evidence path",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="voice-audio-evidence-choice-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              {ROW_COLUMNS.map((col) => (
                <div
                  className="voice-audio-evidence-choice-layer-field"
                  key={col.key}
                >
                  <span className="voice-audio-evidence-choice-layer-concept">
                    {col.label}
                  </span>
                  <span className="voice-audio-evidence-choice-layer-value">
                    {String(item[col.key])}
                  </span>
                </div>
              ))}
            </li>
          ))}
        </ul>
        <ul className="voice-audio-evidence-choice-layer-tracks">
          {VOICE_AUDIO_EVIDENCE_CHOICE_TRACKS.map((track) => (
            <li
              className="voice-audio-evidence-choice-layer-track"
              key={track.name}
              data-provider={track.provider}
              data-evidence-status={track.evidence_status}
            >
              <span className="voice-audio-evidence-choice-layer-track-name">
                {track.name}
              </span>
              <span className="voice-audio-evidence-choice-layer-track-provider">
                provider: {track.provider}
              </span>
              <span className="voice-audio-evidence-choice-layer-track-note">
                {track.provider_label_note}
              </span>
              <span className="voice-audio-evidence-choice-layer-track-status">
                evidence status: {track.evidence_status}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Voiceover-evidence block (ElevenLabs) */}
      <div
        className="voice-audio-evidence-choice-layer-voiceover"
        id="voice-audio-evidence-choice-layer-voiceover"
      >
        <h4>voiceover evidence (ElevenLabs)</h4>
        <p className="voice-audio-evidence-choice-layer-intro">
          One honest view of the voiceover status, the audio artifact, the audio
          artifact reference, the audio artifact digest, the provider output
          reference, the provider output digest, the source media artifact
          reference, the source media artifact digest, and the provider
          (ElevenLabs, named for evidence labeling only). not_available means
          the voiceover artifact evidence is not in accepted data; PS-037c never
          fakes a voiceover artifact, a voice clone, or a provider output.
        </p>
        <ul className="voice-audio-evidence-choice-layer-rows">
          {VOICE_AUDIO_EVIDENCE_CHOICE_ITEMS.filter((item) =>
            [
              "voiceover artifact evidence",
              "voiceover status",
              "audio artifact",
              "audio artifact reference",
              "audio artifact digest",
              "provider output reference",
              "provider output digest",
              "source media artifact reference",
              "source media artifact digest",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="voice-audio-evidence-choice-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              {ROW_COLUMNS.map((col) => (
                <div
                  className="voice-audio-evidence-choice-layer-field"
                  key={col.key}
                >
                  <span className="voice-audio-evidence-choice-layer-concept">
                    {col.label}
                  </span>
                  <span className="voice-audio-evidence-choice-layer-value">
                    {String(item[col.key])}
                  </span>
                </div>
              ))}
            </li>
          ))}
        </ul>
      </div>

      {/* Emotion-signal-evidence block (Hume) */}
      <div
        className="voice-audio-evidence-choice-layer-emotion"
        id="voice-audio-evidence-choice-layer-emotion"
      >
        <h4>emotion-signal evidence (Hume)</h4>
        <p className="voice-audio-evidence-choice-layer-intro">
          One honest view of the emotion-signal status, the provider (Hume,
          named for evidence labeling only), the provider output reference, and
          the provider output digest. not_available means the emotion-signal
          evidence is not in accepted data; PS-037c never fakes an emotion
          signal, an emotion analysis, or a provider output.
        </p>
        <ul className="voice-audio-evidence-choice-layer-rows">
          {VOICE_AUDIO_EVIDENCE_CHOICE_ITEMS.filter((item) =>
            [
              "emotion-signal evidence",
              "emotion-signal status",
              "provider output reference",
              "provider output digest",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="voice-audio-evidence-choice-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="voice-audio-evidence-choice-layer-concept">
                {item.label}
              </span>
              <span className="voice-audio-evidence-choice-layer-value">
                {item.value}
              </span>
              <span className="voice-audio-evidence-choice-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Provider-activity / B2 / rehydrate block */}
      <div
        className="voice-audio-evidence-choice-layer-activity"
        id="voice-audio-evidence-choice-layer-activity"
      >
        <h4>provider activity / B2 / rehydrate</h4>
        <ul className="voice-audio-evidence-choice-layer-rows">
          {VOICE_AUDIO_EVIDENCE_CHOICE_ITEMS.filter((item) =>
            [
              "provider activity status",
              "B2 evidence status",
              "rehydrate evidence status",
              "local verification",
              "live verification status",
              "disclosure boundary",
              "voice/audio evidence status",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="voice-audio-evidence-choice-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="voice-audio-evidence-choice-layer-concept">
                {item.label}
              </span>
              <span className="voice-audio-evidence-choice-layer-value">
                {item.value}
              </span>
              <span className="voice-audio-evidence-choice-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Cross-reference with the PS-037a Multimodal Proof Layer. */}
      <p className="voice-audio-evidence-choice-layer-cross-reference">
        {VOICE_AUDIO_EVIDENCE_CHOICE_MULTIMODAL_CROSS_REFERENCE}
      </p>

      {/* Transcript/timestamp cross-reference with the PS-037b layer. */}
      <p className="voice-audio-evidence-choice-layer-transcript-cross-reference">
        {VOICE_AUDIO_EVIDENCE_CHOICE_TRANSCRIPT_CROSS_REFERENCE}
      </p>

      {/* Honest unavailable / not-claimed / deferred states (verbatim). */}
      <div
        className="voice-audio-evidence-choice-layer-deferred"
        id="voice-audio-evidence-choice-layer-deferred"
      >
        <h4>{VOICE_AUDIO_EVIDENCE_CHOICE_DEFERRED_HEADING}</h4>
        <p className="voice-audio-evidence-choice-layer-intro">
          Honest unavailable / not-claimed / deferred states. These are
          non-claims; an absent voiceover / emotion-signal / speaker-identity /
          voice-authenticity / emotion-truth / biometric / campaign-intelligence
          proof is stated, never hidden, and never faked.
        </p>
        <div className="non-claims">
          {VOICE_AUDIO_EVIDENCE_CHOICE_DEFERRED_STATES.map((s) => (
            <span className="pill warn" key={s}>
              <span className="dot" />
              {s}
            </span>
          ))}
        </div>
        <ul className="voice-audio-evidence-choice-layer-owners">
          {VOICE_AUDIO_EVIDENCE_CHOICE_DEFERRED_OWNERS.map((o) => (
            <li className="voice-audio-evidence-choice-layer-owner" key={o}>
              <span className="mono">{o}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Not claimed (per voice/audio evidence). */}
      <div
        className="voice-audio-evidence-choice-layer-not-claimed"
        id="voice-audio-evidence-choice-layer-not-claimed"
      >
        <h4>not claimed</h4>
        <div className="non-claims">
          {VOICE_AUDIO_EVIDENCE_CHOICE_NEGATIVE_BOUNDARY.map((nc) => (
            <span className="pill warn" key={nc}>
              <span className="dot" />
              {nc}
            </span>
          ))}
        </div>
      </div>

      {/* De-escalation pairs (verbatim). */}
      <div
        className="voice-audio-evidence-choice-layer-deescalation"
        id="voice-audio-evidence-choice-layer-deescalation"
      >
        <h4>De-escalation pairs</h4>
        <ul className="voice-audio-evidence-choice-layer-pairs">
          {VOICE_AUDIO_EVIDENCE_CHOICE_DEESCALATION_PAIRS.map((pair) => (
            <li className="voice-audio-evidence-choice-layer-pair" key={pair}>
              <span className="mono">{pair}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Concepts checklist (canonical voice/audio provider-choice concepts). */}
      <div
        className="voice-audio-evidence-choice-layer-concepts"
        id="voice-audio-evidence-choice-layer-concepts"
      >
        <h4>Concepts</h4>
        <ul className="voice-audio-evidence-choice-layer-concept-list">
          {VOICE_AUDIO_EVIDENCE_CHOICE_CONCEPTS.map((c) => (
            <li
              className="voice-audio-evidence-choice-layer-concept-item"
              key={c}
            >
              {c}
            </li>
          ))}
        </ul>
      </div>

      {/* Persistent boundary statement (verbatim). */}
      <p className="voice-audio-evidence-choice-layer-statement">
        {VOICE_AUDIO_EVIDENCE_CHOICE_PERSISTENT_STATEMENT}
      </p>

      {/* Posture notes (non-claim). */}
      <p className="voice-audio-evidence-choice-layer-posture">
        {VOICE_AUDIO_EVIDENCE_CHOICE_POSTURE.join(" · ")}.
      </p>
    </section>
  );
}
