// PS-037 Disclosure & Trust Boundary -- shared disclosure component.
//
// A reusable disclosure layer rendered additively on every core proof surface
// so the boundary language is identical everywhere proof is shown. It reads
// only from apps/web/src/trustBoundary.ts. It is a disclosure layer, not a new
// proof surface, not a new route, and not a new backend endpoint.
//
// It is purely client-side by default: it calls no provider, reads no B2
// object, performs no browser-side B2 byte verification, performs no broad B2
// scan, and writes no B2 object. It only renders the canonical disclosure
// contract sourced from accepted local / golden / demo data.
//
// Variants (following the project's `variant` convention):
//   - variant="badge"  -> a compact one-line disclosure badge.
//   - variant="panel"  -> the expanded disclosure panel (full contract).
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Disclosure
// & Trust Boundary layer is not semantic truth, not legal authenticity, not
// human authorship, not C2PA authenticity, not Object Lock, not tamper-proof,
// not browser-side B2 byte verification, not live B2 availability, and not
// production security.

import {
  TRUST_BOUNDARY_BADGE_SUMMARY,
  TRUST_BOUNDARY_DEESCALATION_PAIRS,
  TRUST_BOUNDARY_DOES_NOT_PROVE_ITEMS,
  TRUST_BOUNDARY_LAYER_POSITIONING,
  TRUST_BOUNDARY_LAYER_PROVES_HEADING,
  TRUST_BOUNDARY_LAYER_SLICE_ID,
  TRUST_BOUNDARY_LAYER_TITLE,
  TRUST_BOUNDARY_LAYER_DOES_NOT_PROVE_HEADING,
  TRUST_BOUNDARY_NEGATIVE_BOUNDARY,
  TRUST_BOUNDARY_PERSISTENT_STATEMENT,
  TRUST_BOUNDARY_POSTURE,
  TRUST_BOUNDARY_PROVES_ITEMS,
} from "./trustBoundary";

type TrustBoundaryLayerVariant = "badge" | "panel";

export function TrustBoundaryLayer({
  variant = "panel",
}: {
  variant?: TrustBoundaryLayerVariant;
}) {
  if (variant === "badge") {
    return (
      <aside
        className="trust-boundary-layer trust-boundary-layer-badge"
        aria-label={TRUST_BOUNDARY_LAYER_TITLE}
      >
        <span className="trust-boundary-layer-tag">{TRUST_BOUNDARY_LAYER_SLICE_ID}</span>
        <span className="trust-boundary-layer-badge-text">
          {TRUST_BOUNDARY_BADGE_SUMMARY}
        </span>
      </aside>
    );
  }

  return (
    <section
      className="trust-boundary-layer trust-boundary-layer-panel"
      aria-label={TRUST_BOUNDARY_LAYER_TITLE}
    >
      <header className="trust-boundary-layer-head">
        <span className="trust-boundary-layer-tag">
          {TRUST_BOUNDARY_LAYER_SLICE_ID}
        </span>
        <h3>{TRUST_BOUNDARY_LAYER_TITLE}</h3>
        <p className="trust-boundary-layer-positioning">
          {TRUST_BOUNDARY_LAYER_POSITIONING}
        </p>
      </header>

      {/* What ProofStudio proves */}
      <div
        className="trust-boundary-layer-proves"
        id="trust-boundary-layer-proves"
      >
        <h4>{TRUST_BOUNDARY_LAYER_PROVES_HEADING}</h4>
        <ul className="trust-boundary-layer-rows">
          {TRUST_BOUNDARY_PROVES_RENDERED.map((item) => (
            <li
              className="trust-boundary-layer-row"
              key={item.label}
              data-concept={item.concept}
              data-applicable={String(item.applicable)}
            >
              <span className="trust-boundary-layer-concept">
                {item.label}
              </span>
              <span className="trust-boundary-layer-value">{item.value}</span>
              <span className="trust-boundary-layer-verification">
                {item.verification}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* What ProofStudio does not prove */}
      <div
        className="trust-boundary-layer-does-not-prove"
        id="trust-boundary-layer-does-not-prove"
      >
        <h4>{TRUST_BOUNDARY_LAYER_DOES_NOT_PROVE_HEADING}</h4>
        <ul className="trust-boundary-layer-rows">
          {TRUST_BOUNDARY_DOES_NOT_PROVE_RENDERED.map((item) => (
            <li
              className="trust-boundary-layer-row"
              key={item.label}
              data-concept={item.concept}
            >
              <span className="trust-boundary-layer-concept">
                {item.label}
              </span>
              <span className="trust-boundary-layer-value">{item.value}</span>
              <span className="trust-boundary-layer-verification">
                {item.verification}
              </span>
            </li>
          ))}
        </ul>

        {/* Negative boundary strings (verbatim). */}
        <p className="trust-boundary-layer-not-claimed-heading">not claimed</p>
        <div className="non-claims">
          {TRUST_BOUNDARY_NEGATIVE_BOUNDARY.map((nc) => (
            <span className="pill warn" key={nc}>
              <span className="dot" />
              {nc}
            </span>
          ))}
        </div>
      </div>

      {/* De-escalation pairs (verbatim). */}
      <div
        className="trust-boundary-layer-deescalation"
        id="trust-boundary-layer-deescalation"
      >
        <h4>De-escalation pairs</h4>
        <ul className="trust-boundary-layer-pairs">
          {TRUST_BOUNDARY_DEESCALATION_PAIRS.map((pair) => (
            <li className="trust-boundary-layer-pair" key={pair}>
              <span className="mono">{pair}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Persistent boundary statement (verbatim). */}
      <p className="trust-boundary-layer-statement">
        {TRUST_BOUNDARY_PERSISTENT_STATEMENT}
      </p>

      {/* Posture notes (non-claim). */}
      <p className="trust-boundary-layer-posture">
        {TRUST_BOUNDARY_POSTURE.join(" · ")}.
      </p>
    </section>
  );
}

// Render-only views over the canonical disclosure items. Sourced entirely from
// apps/web/src/trustBoundary.ts.
const TRUST_BOUNDARY_PROVES_RENDERED = TRUST_BOUNDARY_PROVES_ITEMS;
const TRUST_BOUNDARY_DOES_NOT_PROVE_RENDERED = TRUST_BOUNDARY_DOES_NOT_PROVE_ITEMS;
