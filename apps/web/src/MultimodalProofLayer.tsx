// PS-037a Multimodal Proof Layer -- shared multimodal proof component.
//
// A reusable proof-inspection layer rendered additively on every core proof
// surface so the per-modality artifact-evidence framing is identical everywhere
// proof is shown. It reads only from apps/web/src/multimodalProof.ts. It is a
// proof-inspection layer, not a new proof surface, not a new route, and not a
// new backend endpoint.
//
// It is purely client-side by default: it calls no provider, reads no B2
// object, performs no browser-side B2 byte verification, performs no broad B2
// scan, and writes no B2 object. It only renders the canonical multimodal proof
// contract sourced from accepted local / golden / demo data.
//
// Variants (following the project's `variant` convention):
//   - variant="summary"  -> a compact per-modality summary (deferred states).
//   - variant="panel"    -> the expanded per-modality panel (full contract).
//
// It renders alongside the existing TrustBoundaryLayer so the PS-037 disclosure
// boundary stays canonical; it reuses the shared disclosure concepts and never
// contradicts the PS-037 boundary.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Multimodal
// Proof Layer is not semantic truth, not legal authenticity, not human
// authorship, not C2PA authenticity, not Object Lock, not tamper-proof, not
// browser-side B2 byte verification, not live B2 availability, and not
// production security.

import {
  MULTIMODAL_PROOF_CONCEPTS,
  MULTIMODAL_PROOF_DEESCALATION_PAIRS,
  MULTIMODAL_PROOF_DEFERRED_HEADING,
  MULTIMODAL_PROOF_DEFERRED_OWNERS,
  MULTIMODAL_PROOF_DEFERRED_STATES,
  MULTIMODAL_PROOF_ITEMS,
  MULTIMODAL_PROOF_LAYER_POSITIONING,
  MULTIMODAL_PROOF_LAYER_SLICE_ID,
  MULTIMODAL_PROOF_LAYER_TITLE,
  MULTIMODAL_PROOF_NEGATIVE_BOUNDARY,
  MULTIMODAL_PROOF_PERSISTENT_STATEMENT,
  MULTIMODAL_PROOF_POSTURE,
  MULTIMODAL_PROOF_SUMMARY,
} from "./multimodalProof";

type MultimodalProofLayerVariant = "panel" | "summary";

// Per-modality concept columns rendered in the expanded panel. Each label is a
// required multimodal proof concept string (spec section 10.2 / 21).
const MODALITY_COLUMNS: { key: keyof typeof SAMPLE_ITEM; label: string }[] = [
  { key: "modality", label: "modality" },
  { key: "media_kind", label: "media kind" },
  { key: "artifact_reference", label: "artifact reference" },
  { key: "artifact_digest", label: "artifact digest" },
  { key: "manifest_reference", label: "manifest reference" },
  { key: "manifest_hash", label: "manifest hash" },
  { key: "b2_evidence_status", label: "B2 evidence status" },
  { key: "rehydrate_evidence_status", label: "rehydrate evidence status" },
  { key: "provider_activity_status", label: "provider activity status" },
  { key: "local_verification", label: "local verification" },
  { key: "live_verification_status", label: "live verification status" },
  { key: "disclosure_boundary", label: "disclosure boundary" },
];

// A reference item used only to satisfy the column `key` typing against the
// MultimodalProofItem shape. The real rows iterate MULTIMODAL_PROOF_ITEMS.
const SAMPLE_ITEM = MULTIMODAL_PROOF_ITEMS[0];

export function MultimodalProofLayer({
  variant = "panel",
}: {
  variant?: MultimodalProofLayerVariant;
}) {
  if (variant === "summary") {
    return (
      <aside
        className="multimodal-proof-layer multimodal-proof-layer-summary"
        aria-label={MULTIMODAL_PROOF_LAYER_TITLE}
      >
        <span className="multimodal-proof-layer-tag">
          {MULTIMODAL_PROOF_LAYER_SLICE_ID}
        </span>
        <span className="multimodal-proof-layer-summary-text">
          {MULTIMODAL_PROOF_SUMMARY}
        </span>
        <ul className="multimodal-proof-layer-deferred-inline">
          {MULTIMODAL_PROOF_DEFERRED_STATES.map((s) => (
            <li className="multimodal-proof-layer-deferred-pill" key={s}>
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
      className="multimodal-proof-layer multimodal-proof-layer-panel"
      aria-label={MULTIMODAL_PROOF_LAYER_TITLE}
    >
      <header className="multimodal-proof-layer-head">
        <span className="multimodal-proof-layer-tag">
          {MULTIMODAL_PROOF_LAYER_SLICE_ID}
        </span>
        <h3>{MULTIMODAL_PROOF_LAYER_TITLE}</h3>
        <p className="multimodal-proof-layer-positioning">
          {MULTIMODAL_PROOF_LAYER_POSITIONING}
        </p>
      </header>

      {/* Per-modality artifact evidence */}
      <div
        className="multimodal-proof-layer-modalities"
        id="multimodal-proof-layer-modalities"
      >
        <h4>artifact evidence</h4>
        <p className="multimodal-proof-layer-intro">
          One honest per-modality view of the recorded artifact evidence.
          Recorded-only means referenced in checked-in evidence, not live-verified
          here; unknown means the artifact evidence is not available yet.
        </p>
        <ul className="multimodal-proof-layer-rows">
          {MULTIMODAL_PROOF_ITEMS.map((item) => (
            <li
              className="multimodal-proof-layer-row"
              key={item.modality}
              data-modality={item.modality}
              data-state={item.state}
            >
              {MODALITY_COLUMNS.map((col) => (
                <div className="multimodal-proof-layer-field" key={col.key}>
                  <span className="multimodal-proof-layer-concept">
                    {col.label}
                  </span>
                  <span className="multimodal-proof-layer-value">
                    {String(item[col.key])}
                  </span>
                </div>
              ))}
              <span className="multimodal-proof-layer-state">
                state: {item.state}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Deferred later-slice states (verbatim). */}
      <div
        className="multimodal-proof-layer-deferred"
        id="multimodal-proof-layer-deferred"
      >
        <h4>{MULTIMODAL_PROOF_DEFERRED_HEADING}</h4>
        <p className="multimodal-proof-layer-intro">
          Honest "not available yet" states. These are non-claims; an absent
          transcript / timestamp / voice / emotion / campaign-intelligence proof
          is stated, never hidden, and never faked.
        </p>
        <div className="non-claims">
          {MULTIMODAL_PROOF_DEFERRED_STATES.map((s) => (
            <span className="pill warn" key={s}>
              <span className="dot" />
              {s}
            </span>
          ))}
        </div>
        <ul className="multimodal-proof-layer-owners">
          {MULTIMODAL_PROOF_DEFERRED_OWNERS.map((o) => (
            <li className="multimodal-proof-layer-owner" key={o}>
              <span className="mono">{o}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Not claimed (per modality). */}
      <div
        className="multimodal-proof-layer-not-claimed"
        id="multimodal-proof-layer-not-claimed"
      >
        <h4>not claimed</h4>
        <div className="non-claims">
          {MULTIMODAL_PROOF_NEGATIVE_BOUNDARY.map((nc) => (
            <span className="pill warn" key={nc}>
              <span className="dot" />
              {nc}
            </span>
          ))}
        </div>
      </div>

      {/* De-escalation pairs (verbatim). */}
      <div
        className="multimodal-proof-layer-deescalation"
        id="multimodal-proof-layer-deescalation"
      >
        <h4>De-escalation pairs</h4>
        <ul className="multimodal-proof-layer-pairs">
          {MULTIMODAL_PROOF_DEESCALATION_PAIRS.map((pair) => (
            <li className="multimodal-proof-layer-pair" key={pair}>
              <span className="mono">{pair}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Concepts checklist (canonical multimodal proof concepts). */}
      <div
        className="multimodal-proof-layer-concepts"
        id="multimodal-proof-layer-concepts"
      >
        <h4>Concepts</h4>
        <ul className="multimodal-proof-layer-concept-list">
          {MULTIMODAL_PROOF_CONCEPTS.map((c) => (
            <li className="multimodal-proof-layer-concept-item" key={c}>
              {c}
            </li>
          ))}
        </ul>
      </div>

      {/* Persistent boundary statement (verbatim). */}
      <p className="multimodal-proof-layer-statement">
        {MULTIMODAL_PROOF_PERSISTENT_STATEMENT}
      </p>

      {/* Posture notes (non-claim). */}
      <p className="multimodal-proof-layer-posture">
        {MULTIMODAL_PROOF_POSTURE.join(" · ")}.
      </p>
    </section>
  );
}
