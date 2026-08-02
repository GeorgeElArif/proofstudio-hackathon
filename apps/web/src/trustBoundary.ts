// PS-037 Disclosure & Trust Boundary -- canonical disclosure data module.
//
// This is the single, shared source of disclosure / trust-boundary language for
// every core proof surface. It exists so a reviewer, client, or judge reads the
// SAME honest boundary wording on the Judge Cockpit Home, the B2 Evidence
// Explorer, the Manifest Verification Panel, the B2 Rehydrate Comparison, the
// B2 Audit Vault, the Review + Approval Workspace, the Judge Evidence Pack, the
// Public Provenance Passport, and the Review Room footer.
//
// The layer is a disclosure layer, not a new proof surface, not a new route,
// and not a new backend endpoint. It is purely client-side by default: it calls
// no provider, reads no B2 object, exposes no arbitrary run_id input, performs
// no browser-side B2 byte verification, performs no broad B2 scan, and writes no
// B2 object. It only reads accepted local / golden / demo data already captured
// by the pipeline.
//
// PS-037 does not invent new claims. It states the existing boundary
// consistently. Every value below is the canonical, honest disclosure contract.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Disclosure
// & Trust Boundary layer is not a legal authenticity system, not a live B2
// verifier, and not a truth system. It is not semantic truth, not legal
// authenticity, not human authorship, not C2PA authenticity, not Object Lock,
// not tamper-proof, not browser-side B2 byte verification, not live B2
// availability, and not production security.

// ---------------------------------------------------------------------------
// Layer identity (spec section 20). Verbatim.
// ---------------------------------------------------------------------------

export const TRUST_BOUNDARY_LAYER_SLICE_ID = "PS-037";
export const TRUST_BOUNDARY_LAYER_TITLE = "Disclosure & Trust Boundary";

// One-line positioning statement. Surfaced by the badge variant and the panel
// header so the boundary is identical on every core proof surface.
export const TRUST_BOUNDARY_LAYER_POSITIONING =
  "ProofStudio proves what the pipeline recorded.";

// The two canonical section headings (spec section 11 / section 20). Verbatim.
export const TRUST_BOUNDARY_LAYER_PROVES_HEADING = "What ProofStudio proves";
export const TRUST_BOUNDARY_LAYER_DOES_NOT_PROVE_HEADING =
  "What ProofStudio does not prove";

// ---------------------------------------------------------------------------
// Disclosure concept keys (spec section 10.2). Stable identifiers.
// ---------------------------------------------------------------------------

export type TrustBoundaryConcept =
  | "pipeline-recorded-evidence"
  | "local-verification"
  | "live-verification-status"
  | "provider-activity-status"
  | "b2-evidence-status"
  | "reviewer-decision-boundary"
  | "not-claimed"
  | "unknown";

export type TrustBoundaryVerification =
  | "locally_verified"
  | "recorded_only"
  | "not_verified"
  | "not_claimed"
  | "unknown";

export interface TrustBoundaryDisclosureItem {
  concept: TrustBoundaryConcept;
  // label matches the verbatim disclosure-concept string (spec section 20).
  label: string;
  value: string;
  applicable: boolean;
  verification: TrustBoundaryVerification;
}

// ---------------------------------------------------------------------------
// "What ProofStudio proves" disclosure items (spec section 10.2 / 11).
//
// Each value is honest about what is locally verified versus recorded-only
// versus not verified. None of these overclaims. The default posture is local /
// static: no provider call, no live B2 read, no B2 write, no broad B2 scan.
// ---------------------------------------------------------------------------

const PROVES_ITEMS: readonly TrustBoundaryDisclosureItem[] = [
  {
    concept: "pipeline-recorded-evidence",
    label: "pipeline-recorded evidence",
    value: "what the pipeline recorded (accepted local / golden / demo data)",
    applicable: true,
    verification: "locally_verified",
  },
  {
    concept: "local-verification",
    label: "local verification",
    value:
      "locally verified against accepted checked-in evidence (manifest hashes, archive references, digests, provider-call counts)",
    applicable: true,
    verification: "locally_verified",
  },
  {
    concept: "live-verification-status",
    label: "live verification status",
    value: "local / check-only (live check not in scope for this disclosure)",
    applicable: true,
    verification: "not_verified",
  },
  {
    concept: "provider-activity-status",
    label: "provider activity status",
    value: "no provider calls (disclosure is local / static by default)",
    applicable: true,
    verification: "not_claimed",
  },
  {
    concept: "b2-evidence-status",
    label: "B2 evidence status",
    value: "recorded-only (B2 evidence referenced, not live-verified here)",
    applicable: true,
    verification: "recorded_only",
  },
  {
    concept: "reviewer-decision-boundary",
    label: "reviewer decision boundary",
    value:
      "a workflow decision, not a truth / legal / authorship claim",
    applicable: true,
    verification: "not_claimed",
  },
];

// ---------------------------------------------------------------------------
// "What ProofStudio does not prove" disclosure items (spec section 10.2 / 11).
// ---------------------------------------------------------------------------

const DOES_NOT_PROVE_ITEMS: readonly TrustBoundaryDisclosureItem[] = [
  {
    concept: "not-claimed",
    label: "not claimed",
    value: "the honest set of things ProofStudio does not claim",
    applicable: true,
    verification: "not_claimed",
  },
  {
    concept: "unknown",
    label: "unknown",
    value: "what remains unknown or not surfaced by accepted evidence",
    applicable: true,
    verification: "unknown",
  },
];

// The full, ordered disclosure set rendered by the panel variant.
export const TRUST_BOUNDARY_DISCLOSURE_ITEMS: readonly TrustBoundaryDisclosureItem[] =
  [...PROVES_ITEMS, ...DOES_NOT_PROVE_ITEMS];

export const TRUST_BOUNDARY_PROVES_ITEMS = PROVES_ITEMS;
export const TRUST_BOUNDARY_DOES_NOT_PROVE_ITEMS = DOES_NOT_PROVE_ITEMS;

// ---------------------------------------------------------------------------
// Required de-escalation pairs (spec section 10.4 / 20). Surfaced verbatim so
// a judge never mistakes a strong-sounding artifact for a stronger guarantee.
// Stated as non-claims so context-aware forbidden-claim scanners never flag
// these boundary terms as overclaims.
// ---------------------------------------------------------------------------

export const TRUST_BOUNDARY_DEESCALATION_PAIRS: readonly string[] = [
  "proof does not equal truth",
  "workflow approval does not equal legal authenticity",
  "B2 archive reference does not equal Object Lock",
  "hash match does not equal semantic truth",
  "manifest hash does not equal human authorship",
  "local evidence does not equal live B2 availability",
  "demo/golden evidence does not equal production security",
];

// ---------------------------------------------------------------------------
// Required negative boundary strings (spec section 10.5 / 20). Surfaced
// verbatim. These are the canonical "not claimed" set rendered as pills.
// ---------------------------------------------------------------------------

export const TRUST_BOUNDARY_NEGATIVE_BOUNDARY: readonly string[] = [
  "not semantic truth",
  "not legal authenticity",
  "not human authorship",
  "not C2PA authenticity",
  "not Object Lock",
  "not tamper-proof",
  "not browser-side B2 byte verification",
  "not live B2 availability",
  "not production security",
];

// ---------------------------------------------------------------------------
// Persistent boundary statement (spec section 11). Verbatim-equivalent.
// Written as non-claim copy so the project's forbidden-claim scanners never
// flag the boundary terms.
// ---------------------------------------------------------------------------

export const TRUST_BOUNDARY_PERSISTENT_STATEMENT =
  "ProofStudio proves what the pipeline recorded. " +
  "Proof does not equal truth. " +
  "Workflow approval does not equal legal authenticity. " +
  "A B2 archive reference does not equal Object Lock. " +
  "A hash match does not equal semantic truth. " +
  "A manifest hash does not equal human authorship. " +
  "Local evidence does not equal live B2 availability. " +
  "Demo/golden evidence does not equal production security.";

// Compact one-line badge summary used by the badge variant.
export const TRUST_BOUNDARY_BADGE_SUMMARY =
  "Disclosure & Trust Boundary: ProofStudio proves what the pipeline " +
  "recorded; proof does not equal truth.";

// ---------------------------------------------------------------------------
// Truth-boundary posture (spec section 1 / 10.1). Surfaced so the disclosure
// contract is deterministic and auditable. These are non-claim posture notes.
// ---------------------------------------------------------------------------

export const TRUST_BOUNDARY_POSTURE: readonly string[] = [
  "no provider calls",
  "no live B2 reads",
  "no B2 writes",
  "no broad B2 scans",
  "local / static by default",
];

// ---------------------------------------------------------------------------
// Required core proof surfaces (spec section 10.3). Listed so the disclosure
// contract documents exactly where the shared layer is rendered.
// ---------------------------------------------------------------------------

export const TRUST_BOUNDARY_REQUIRED_SURFACES: readonly string[] = [
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
