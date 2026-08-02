// PS-037b AssemblyAI Transcript/Timestamp Evidence -- shared component.
//
// A reusable transcript/timestamp evidence-inspection layer rendered
// additively on every core proof surface so the transcript/timestamp framing
// is identical everywhere proof is shown. It reads only from
// apps/web/src/assemblyAITranscriptEvidence.ts. It is a transcript/timestamp
// evidence-inspection layer, not a new proof surface, not a new route, and
// not a new backend endpoint.
//
// It is purely client-side by default: it makes no AssemblyAI API call, calls
// no provider, reads no B2 object, performs no browser-side B2 byte
// verification, performs no broad B2 scan, and writes no B2 object. It only
// renders the canonical transcript/timestamp evidence contract sourced from
// accepted local / golden / demo data.
//
// Variants (following the project's `variant` convention):
//   - variant="summary"  -> a compact transcript/timestamp summary.
//   - variant="panel"    -> the expanded transcript/timestamp panel.
//
// It renders alongside the existing TrustBoundaryLayer (PS-037) and the
// MultimodalProofLayer (PS-037a) so the PS-037 disclosure boundary and the
// PS-037a multimodal proof contract stay canonical; it cross-references
// PS-037a, supplies the concrete transcript/timestamp evidence that PS-037a
// only reserved as deferred, and never contradicts the PS-037 boundary or the
// PS-037a deferred states.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The AssemblyAI
// Transcript/Timestamp Evidence layer is not transcript correctness, not
// timestamp correctness, not speaker identity, not voice authenticity, not
// semantic truth, not legal authenticity, not human authorship, not C2PA
// authenticity, not Object Lock, not tamper-proof, not browser-side B2 byte
// verification, not live B2 availability, not live AssemblyAI availability,
// and not production security.

import {
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_CONCEPTS,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_DEESCALATION_PAIRS,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_DEFERRED_HEADING,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_DEFERRED_OWNERS,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_DEFERRED_STATES,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_ITEMS,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_MULTIMODAL_CROSS_REFERENCE,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_NEGATIVE_BOUNDARY,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_PERSISTENT_STATEMENT,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_POSITIONING,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_POSTURE,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_SLICE_ID,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_SUMMARY,
  ASSEMBLYAI_TRANSCRIPT_EVIDENCE_TITLE,
} from "./assemblyAITranscriptEvidence";

type TranscriptTimestampEvidenceLayerVariant = "panel" | "summary";

// Per-row concept columns rendered in the expanded panel. Each label is a
// required transcript/timestamp evidence concept string (spec section 10.2 /
// 21).
const ROW_COLUMNS: { key: keyof typeof SAMPLE_ITEM; label: string }[] = [
  { key: "concept", label: "concept" },
  { key: "label", label: "label" },
  { key: "value", label: "value" },
  { key: "applicable", label: "applicable" },
  { key: "state", label: "state" },
];

// A reference item used only to satisfy the column `key` typing against the
// TranscriptTimestampEvidenceItem shape. The real rows iterate
// ASSEMBLYAI_TRANSCRIPT_EVIDENCE_ITEMS.
const SAMPLE_ITEM = ASSEMBLYAI_TRANSCRIPT_EVIDENCE_ITEMS[0];

export function TranscriptTimestampEvidenceLayer({
  variant = "panel",
}: {
  variant?: TranscriptTimestampEvidenceLayerVariant;
}) {
  if (variant === "summary") {
    return (
      <aside
        className="transcript-timestamp-evidence-layer transcript-timestamp-evidence-layer-summary"
        aria-label={ASSEMBLYAI_TRANSCRIPT_EVIDENCE_TITLE}
      >
        <span className="transcript-timestamp-evidence-layer-tag">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_SLICE_ID}
        </span>
        <span className="transcript-timestamp-evidence-layer-summary-text">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_SUMMARY}
        </span>
        <ul className="transcript-timestamp-evidence-layer-deferred-inline">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_DEFERRED_STATES.map((s) => (
            <li
              className="transcript-timestamp-evidence-layer-deferred-pill"
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
      className="transcript-timestamp-evidence-layer transcript-timestamp-evidence-layer-panel"
      aria-label={ASSEMBLYAI_TRANSCRIPT_EVIDENCE_TITLE}
    >
      <header className="transcript-timestamp-evidence-layer-head">
        <span className="transcript-timestamp-evidence-layer-tag">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_SLICE_ID}
        </span>
        <h3>{ASSEMBLYAI_TRANSCRIPT_EVIDENCE_TITLE}</h3>
        <p className="transcript-timestamp-evidence-layer-positioning">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_POSITIONING}
        </p>
      </header>

      {/* Transcript evidence block */}
      <div
        className="transcript-timestamp-evidence-layer-transcript"
        id="transcript-timestamp-evidence-layer-transcript"
      >
        <h4>transcript evidence</h4>
        <p className="transcript-timestamp-evidence-layer-intro">
          One honest view of whether transcript evidence exists, the recorded
          transcript artifact, the transcript artifact reference, the
          transcript artifact digest, the transcript provider (AssemblyAI), the
          media artifact reference, the media artifact digest, the transcript
          status, and the transcript verification status. Recorded-only means
          referenced in checked-in evidence, not live-verified here;
          not_available means the transcript evidence is not in accepted data.
        </p>
        <ul className="transcript-timestamp-evidence-layer-rows">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_ITEMS.filter((item) =>
            [
              "transcript evidence",
              "transcript artifact",
              "transcript artifact reference",
              "transcript artifact digest",
              "transcript provider",
              "media artifact reference",
              "media artifact digest",
              "transcript status",
              "transcript verification status",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="transcript-timestamp-evidence-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              {ROW_COLUMNS.map((col) => (
                <div
                  className="transcript-timestamp-evidence-layer-field"
                  key={col.key}
                >
                  <span className="transcript-timestamp-evidence-layer-concept">
                    {col.label}
                  </span>
                  <span className="transcript-timestamp-evidence-layer-value">
                    {String(item[col.key])}
                  </span>
                </div>
              ))}
            </li>
          ))}
        </ul>
      </div>

      {/* Timestamp evidence block */}
      <div
        className="transcript-timestamp-evidence-layer-timestamp"
        id="transcript-timestamp-evidence-layer-timestamp"
      >
        <h4>timestamp evidence</h4>
        <p className="transcript-timestamp-evidence-layer-intro">
          One honest view of whether timestamp evidence exists, the timestamp
          segments, the word timing evidence, the utterance timing evidence,
          the timestamp status, and the timestamp verification status.
          not_available means the timestamp evidence is not in accepted data;
          PS-037b never fakes timestamp segments, word timing, or utterance
          timing.
        </p>
        <ul className="transcript-timestamp-evidence-layer-rows">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_ITEMS.filter((item) =>
            [
              "timestamp evidence",
              "timestamp segments",
              "word timing evidence",
              "utterance timing evidence",
              "timestamp status",
              "timestamp verification status",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="transcript-timestamp-evidence-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              {ROW_COLUMNS.map((col) => (
                <div
                  className="transcript-timestamp-evidence-layer-field"
                  key={col.key}
                >
                  <span className="transcript-timestamp-evidence-layer-concept">
                    {col.label}
                  </span>
                  <span className="transcript-timestamp-evidence-layer-value">
                    {String(item[col.key])}
                  </span>
                </div>
              ))}
            </li>
          ))}
        </ul>
      </div>

      {/* Provider activity / B2 / rehydrate block */}
      <div
        className="transcript-timestamp-evidence-layer-activity"
        id="transcript-timestamp-evidence-layer-activity"
      >
        <h4>provider activity / B2 / rehydrate</h4>
        <ul className="transcript-timestamp-evidence-layer-rows">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_ITEMS.filter((item) =>
            [
              "provider activity status",
              "B2 evidence status",
              "rehydrate evidence status",
              "local verification",
              "live verification status",
              "disclosure boundary",
            ].includes(item.concept),
          ).map((item) => (
            <li
              className="transcript-timestamp-evidence-layer-row"
              key={item.concept}
              data-concept={item.concept}
              data-state={item.state}
            >
              <span className="transcript-timestamp-evidence-layer-concept">
                {item.label}
              </span>
              <span className="transcript-timestamp-evidence-layer-value">
                {item.value}
              </span>
              <span className="transcript-timestamp-evidence-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Cross-reference with the PS-037a Multimodal Proof Layer. */}
      <p className="transcript-timestamp-evidence-layer-cross-reference">
        {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_MULTIMODAL_CROSS_REFERENCE}
      </p>

      {/* Honest unavailable / not-claimed / deferred states (verbatim). */}
      <div
        className="transcript-timestamp-evidence-layer-deferred"
        id="transcript-timestamp-evidence-layer-deferred"
      >
        <h4>{ASSEMBLYAI_TRANSCRIPT_EVIDENCE_DEFERRED_HEADING}</h4>
        <p className="transcript-timestamp-evidence-layer-intro">
          Honest unavailable / not-claimed / deferred states. These are
          non-claims; an absent transcript / timestamp / speaker-identity /
          voice-authenticity / emotion / campaign-intelligence proof is stated,
          never hidden, and never faked.
        </p>
        <div className="non-claims">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_DEFERRED_STATES.map((s) => (
            <span className="pill warn" key={s}>
              <span className="dot" />
              {s}
            </span>
          ))}
        </div>
        <ul className="transcript-timestamp-evidence-layer-owners">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_DEFERRED_OWNERS.map((o) => (
            <li className="transcript-timestamp-evidence-layer-owner" key={o}>
              <span className="mono">{o}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Not claimed (per transcript/timestamp evidence). */}
      <div
        className="transcript-timestamp-evidence-layer-not-claimed"
        id="transcript-timestamp-evidence-layer-not-claimed"
      >
        <h4>not claimed</h4>
        <div className="non-claims">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_NEGATIVE_BOUNDARY.map((nc) => (
            <span className="pill warn" key={nc}>
              <span className="dot" />
              {nc}
            </span>
          ))}
        </div>
      </div>

      {/* De-escalation pairs (verbatim). */}
      <div
        className="transcript-timestamp-evidence-layer-deescalation"
        id="transcript-timestamp-evidence-layer-deescalation"
      >
        <h4>De-escalation pairs</h4>
        <ul className="transcript-timestamp-evidence-layer-pairs">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_DEESCALATION_PAIRS.map((pair) => (
            <li className="transcript-timestamp-evidence-layer-pair" key={pair}>
              <span className="mono">{pair}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Concepts checklist (canonical transcript/timestamp concepts). */}
      <div
        className="transcript-timestamp-evidence-layer-concepts"
        id="transcript-timestamp-evidence-layer-concepts"
      >
        <h4>Concepts</h4>
        <ul className="transcript-timestamp-evidence-layer-concept-list">
          {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_CONCEPTS.map((c) => (
            <li
              className="transcript-timestamp-evidence-layer-concept-item"
              key={c}
            >
              {c}
            </li>
          ))}
        </ul>
      </div>

      {/* Persistent boundary statement (verbatim). */}
      <p className="transcript-timestamp-evidence-layer-statement">
        {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_PERSISTENT_STATEMENT}
      </p>

      {/* Posture notes (non-claim). */}
      <p className="transcript-timestamp-evidence-layer-posture">
        {ASSEMBLYAI_TRANSCRIPT_EVIDENCE_POSTURE.join(" · ")}.
      </p>
    </section>
  );
}
