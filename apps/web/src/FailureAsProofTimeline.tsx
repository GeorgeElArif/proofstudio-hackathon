// PS-030 Failure-as-Proof Timeline.
//
// A dedicated, judge-facing product surface that exposes the golden workflow
// as an evidence-backed operational timeline. It proves that ProofStudio is
// an AI media operations cockpit, not another AI generator: every operational
// step (provider routing, generation, archive, manifest, rehydrate) is an
// auditable timeline entry, and the surface shows exactly where captured
// failures, retries, and fallbacks would appear without inventing any.
//
// The timeline tells three stories at once:
//
//   1. What happened in the golden workflow (checked-in evidence)
//   2. Where operational failures would appear (Failure-as-Proof / Failure
//      Theater) if future evidence captured them
//   3. Why durable B2 rehydrate matters (no provider rerun, zero provider
//      calls) via the Archive / Rehydrate Lab foundation
//
// All displayed values come from apps/web/src/failureAsProofTimeline.ts,
// which is sourced verbatim from the checked-in PS-024 golden demo manifest
// and the PS-021 / PS-025 / PS-026 / PS-027 / PS-028 / PS-029 source
// evidence. The PS-030 smoke validates these constants match the manifest and
// source evidence exactly.
//
// The component also exposes a `variant` prop so the same surface can render
// as a full page (via the /failure-timeline route in App.tsx) or as an inline
// section inside other judge surfaces. It performs no network call, calls no
// provider, and reads no B2 object: it only renders verified, checked-in
// evidence.

import {
  FAILURE_TIMELINE_ARCHIVE_REHYDRATE_LAB_NOTE,
  FAILURE_TIMELINE_ARCHIVE_SHA256,
  FAILURE_TIMELINE_ARCHIVE_URI,
  FAILURE_TIMELINE_CAMPAIGN_ID,
  FAILURE_TIMELINE_CLAIM_BOUNDARY_ALLOWED,
  FAILURE_TIMELINE_CLAIM_BOUNDARY_FORBIDDEN,
  FAILURE_TIMELINE_EVENTS,
  FAILURE_TIMELINE_FAILURE_AS_PROOF_EXPLANATION,
  FAILURE_TIMELINE_FAILURE_THEATER_SLOTS,
  FAILURE_TIMELINE_IMPLEMENTATION_ROADMAP,
  FAILURE_TIMELINE_LOCAL_CONTRACT_PROOF,
  FAILURE_TIMELINE_NO_FAKE_FAILURES_LINE,
  FAILURE_TIMELINE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  FAILURE_TIMELINE_NO_PROVIDER_RERUN_STORY,
  FAILURE_TIMELINE_PUBLIC_DEPLOYMENT_PENDING,
  FAILURE_TIMELINE_PROVIDER_CALLS_DURING_REHYDRATE,
  FAILURE_TIMELINE_REHYDRATE_SOURCE,
  FAILURE_TIMELINE_RUN_ID,
  FAILURE_TIMELINE_SOURCES,
  FAILURE_TIMELINE_TRUTH_BOUNDARY,
  FAILURE_TIMELINE_UNLOCK_SCOPE,
  FAILURE_TIMELINE_WHERE_FAILURES_APPEAR_LINE,
  FAILURE_TIMELINE_ZERO_PROVIDER_CALLS_LINE,
  type FailureTimelineEvent,
} from "./failureAsProofTimeline";
import { DEFAULT_API_BASE_URL } from "./api";

type FailureAsProofTimelineVariant = "page" | "section";

const KIND_LABEL: Record<FailureTimelineEvent["kind"], string> = {
  checked_in_evidence: "checked-in evidence",
  durable_b2_archive_proof: "durable B2 archive proof",
  b2_rehydrate_proof: "B2 rehydrate proof",
  local_passport_contract_proof: "local public passport contract proof",
  inferred_product_explanation: "inferred product explanation",
  captured_failure_surface: "failure placement model",
  public_deployment_pending: "public deployment pending",
};

export function FailureAsProofTimeline({
  variant = "page",
}: {
  variant?: FailureAsProofTimelineVariant;
}) {
  const isPage = variant === "page";

  const card = (
    <section
      className={
        isPage
          ? "card col-full failure-timeline failure-timeline-page"
          : "card col-full failure-timeline"
      }
      id="failure-as-proof-timeline"
      aria-label="Failure-as-Proof Timeline"
    >
      <header className="failure-timeline-head">
        <span className="infra-tag">Operations</span>
        <h2>Failure-as-Proof Timeline</h2>
      </header>

      <p className="subhead">
        One canonical judge-facing view over the golden workflow as an
        evidence-backed operational timeline. Every stage below is sourced
        verbatim from the checked-in evidence (PS-021, PS-024, PS-025, PS-026,
        PS-027, PS-028, PS-029). Nothing here is invented, nothing here is
        fetched live from B2, and no provider is called. ProofStudio is an AI
        media operations cockpit, not another AI generator.
      </p>

      {/* Operational timeline */}
      <div
        className="failure-timeline-events"
        id="failure-timeline-events"
      >
        <h3>Production workflow timeline</h3>
        <p className="hint">
          Each stage maps to the checked-in evidence that proves it, and to
          the proof surface that exposes it. The last operational slot shows
          where captured failures, retries, and fallbacks would appear.
        </p>
        <ol className="failure-timeline-list">
          {FAILURE_TIMELINE_EVENTS.map((event) => (
            <li
              key={event.key}
              className={`failure-timeline-event kind-${event.kind}`}
              data-event-key={event.key}
            >
              <span className="failure-timeline-event-idx">
                {String(event.idx).padStart(2, "0")}
              </span>
              <div className="failure-timeline-event-body">
                <div className="failure-timeline-event-head">
                  <h4 className="failure-timeline-event-title">
                    {event.title}
                  </h4>
                  <span
                    className={`pill ${event.kind === "captured_failure_surface" ? "warn" : event.kind === "public_deployment_pending" ? "info" : "ok"}`}
                  >
                    <span className="dot" />
                    {KIND_LABEL[event.kind]}
                  </span>
                </div>
                <p className="failure-timeline-event-summary">
                  {event.summary}
                </p>
                <p className="hint muted-link">
                  sources: {event.sourceTags.join(" / ")}
                </p>
                {event.links.length > 0 && (
                  <div className="failure-timeline-event-links">
                    {event.links.map((href) => (
                      <a key={href} className="btn" href={href}>
                        {linkLabel(href)}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </li>
          ))}
        </ol>
      </div>

      {/* Failure-as-Proof section */}
      <section
        className="failure-as-proof"
        id="failure-as-proof"
        aria-label="Failure-as-Proof"
      >
        <h3>Failure-as-Proof</h3>
        <ul className="infra-points failure-as-proof-points">
          {FAILURE_TIMELINE_FAILURE_AS_PROOF_EXPLANATION.map((point) => (
            <li key={point}>{point}</li>
          ))}
        </ul>
        <p className="failure-as-proof-mandate">
          <span className="failure-as-proof-line">
            {FAILURE_TIMELINE_WHERE_FAILURES_APPEAR_LINE}
          </span>
        </p>
        <p className="failure-as-proof-mandate">
          <span className="failure-as-proof-line">
            {FAILURE_TIMELINE_NO_FAKE_FAILURES_LINE}
          </span>
        </p>
        <p className="failure-as-proof-mandate">
          <span className="failure-as-proof-line failure-as-proof-zero-calls">
            {FAILURE_TIMELINE_ZERO_PROVIDER_CALLS_LINE}
          </span>
        </p>
      </section>

      {/* Failure Theater / failure-placement model */}
      <section
        className="failure-theater"
        id="failure-theater"
        aria-label="Failure Theater"
      >
        <h3>Failure Theater</h3>
        <p className="hint">
          The failure-placement model. If future evidence captured any of
          these operational events, each would appear as an auditable
          timeline entry above. None of these are claimed to have occurred
          for the verified golden run.
        </p>
        <div className="failure-theater-grid">
          {FAILURE_TIMELINE_FAILURE_THEATER_SLOTS.map((slot) => (
            <article key={slot.key} className={`failure-theater-slot slot-${slot.key}`}>
              <h4>{slot.title}</h4>
              <p>{slot.description}</p>
            </article>
          ))}
        </div>
      </section>

      {/* No-provider-rerun story */}
      <div
        className="failure-timeline-no-rerun"
        id="failure-timeline-no-rerun"
      >
        <h3>No live provider rerun required for rehydrate</h3>
        <p className="failure-timeline-no-rerun-story">
          {FAILURE_TIMELINE_NO_PROVIDER_RERUN_STORY}
        </p>
        <dl className="kv">
          <dt>rehydrate_source</dt>
          <dd className="mono failure-timeline-rehydrate-source">
            {FAILURE_TIMELINE_REHYDRATE_SOURCE}
          </dd>
          <dt>provider_calls_during_rehydrate</dt>
          <dd className="mono failure-timeline-provider-calls">
            {String(FAILURE_TIMELINE_PROVIDER_CALLS_DURING_REHYDRATE)}
          </dd>
          <dt>no_live_provider_call_during_rehydrate</dt>
          <dd className="mono failure-timeline-no-live-provider-call">
            {String(FAILURE_TIMELINE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE)}
          </dd>
        </dl>
      </div>

      {/* Archive / Rehydrate Lab foundation */}
      <section
        className="failure-timeline-lab"
        id="failure-timeline-archive-rehydrate-lab"
        aria-label="Archive / Rehydrate Lab foundation"
      >
        <h3>Archive / Rehydrate Lab foundation</h3>
        <p className="hint">{FAILURE_TIMELINE_ARCHIVE_REHYDRATE_LAB_NOTE}</p>
        <dl className="kv">
          <dt>archive URI</dt>
          <dd className="mono failure-timeline-lab-archive-uri">
            {FAILURE_TIMELINE_ARCHIVE_URI}
          </dd>
          <dt>archive SHA-256</dt>
          <dd className="mono failure-timeline-lab-archive-sha">
            {FAILURE_TIMELINE_ARCHIVE_SHA256}
          </dd>
          <dt>rehydrate source</dt>
          <dd className="mono failure-timeline-lab-rehydrate-source">
            {FAILURE_TIMELINE_REHYDRATE_SOURCE}
          </dd>
          <dt>provider calls during rehydrate</dt>
          <dd className="mono failure-timeline-lab-provider-calls">
            {String(FAILURE_TIMELINE_PROVIDER_CALLS_DURING_REHYDRATE)}
          </dd>
          <dt>no live provider call during rehydrate</dt>
          <dd className="mono failure-timeline-lab-no-live-provider-call">
            {String(FAILURE_TIMELINE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE)}
          </dd>
        </dl>
        <div className="btn-row">
          <a
            className="btn btn-primary"
            href="/b2-rehydrate-comparison"
            title="Open the B2 Rehydrate Comparison (PS-029)"
          >
            Open B2 Rehydrate Comparison
          </a>
        </div>
      </section>

      {/* Verified golden values */}
      <div className="failure-timeline-golden" id="failure-timeline-golden">
        <h3>Verified golden values</h3>
        <p className="hint">
          Sourced verbatim from{" "}
          <code className="mono">{FAILURE_TIMELINE_SOURCES[0].evidencePath}</code>{" "}
          (PS-024 golden manifest), itself traced to the PS-021 live B2 durable
          rehydrate smoke.
        </p>
        <dl className="kv">
          <dt>run_id</dt>
          <dd className="mono failure-timeline-golden-run-id">
            {FAILURE_TIMELINE_RUN_ID}
          </dd>
          <dt>campaign_id</dt>
          <dd className="mono failure-timeline-golden-campaign-id">
            {FAILURE_TIMELINE_CAMPAIGN_ID}
          </dd>
          <dt>archive URI</dt>
          <dd className="mono failure-timeline-golden-archive-uri">
            {FAILURE_TIMELINE_ARCHIVE_URI}
          </dd>
          <dt>archive SHA-256</dt>
          <dd className="mono failure-timeline-golden-archive-sha">
            {FAILURE_TIMELINE_ARCHIVE_SHA256}
          </dd>
          <dt>rehydrate_source</dt>
          <dd className="mono failure-timeline-golden-rehydrate-source">
            {FAILURE_TIMELINE_REHYDRATE_SOURCE}
          </dd>
          <dt>provider_calls_during_rehydrate</dt>
          <dd className="mono failure-timeline-golden-provider-calls">
            {String(FAILURE_TIMELINE_PROVIDER_CALLS_DURING_REHYDRATE)}
          </dd>
          <dt>no_live_provider_call_during_rehydrate</dt>
          <dd className="mono failure-timeline-golden-no-live-provider-call">
            {String(FAILURE_TIMELINE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE)}
          </dd>
        </dl>
      </div>

      {/* Source evidence files */}
      <div className="failure-timeline-files" id="failure-timeline-files">
        <h3>Source evidence files</h3>
        <ul className="infra-points">
          {FAILURE_TIMELINE_SOURCES.map((src) => (
            <li key={src.id}>
              <code className="mono">{src.evidencePath}</code>
              <span className="hint muted-link" style={{ marginLeft: 8 }}>
                {src.sliceTag} · {src.label}
              </span>
            </li>
          ))}
        </ul>
        <p className="hint muted-link">
          implementation roadmap:{" "}
          <code className="mono">{FAILURE_TIMELINE_IMPLEMENTATION_ROADMAP}</code>
        </p>
      </div>

      {/* Deployment status */}
      <div
        className="failure-timeline-deployment"
        id="failure-timeline-deployment"
      >
        <h3>Deployment status</h3>
        <dl className="kv">
          <dt>local contract proof</dt>
          <dd className="mono">
            {String(FAILURE_TIMELINE_LOCAL_CONTRACT_PROOF)}
          </dd>
          <dt>public deployment pending</dt>
          <dd className="mono">
            {String(FAILURE_TIMELINE_PUBLIC_DEPLOYMENT_PENDING)}
          </dd>
          <dt>unlock scope</dt>
          <dd className="mono">{FAILURE_TIMELINE_UNLOCK_SCOPE}</dd>
        </dl>
        <p className="hint">
          The local contract (FastAPI TestClient against a fresh empty store
          resolving the golden run_id from checked-in evidence) is verified by
          PS-025. The public Render deployment is not verified yet: the new
          backend must be deployed and the public URL must be verified
          end-to-end before this distinction changes.
        </p>
      </div>

      {/* Claim boundary */}
      <section
        className="failure-timeline-claim-boundary"
        id="failure-timeline-claim-boundary"
      >
        <h3>Claim boundary</h3>
        <div className="failure-timeline-claim-boundary-grid">
          <div className="failure-timeline-claim-boundary-col">
            <h4>Allowed claims</h4>
            <ul className="infra-points">
              {FAILURE_TIMELINE_CLAIM_BOUNDARY_ALLOWED.map((claim) => (
                <li key={claim}>
                  <span className="pill ok">
                    <span className="dot" />
                    {claim}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div className="failure-timeline-claim-boundary-col">
            <h4>Forbidden claims</h4>
            <ul className="infra-points">
              {FAILURE_TIMELINE_CLAIM_BOUNDARY_FORBIDDEN.map((claim) => (
                <li key={claim}>
                  <span className="pill warn">
                    <span className="dot" />
                    {claim}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* Truth boundary */}
      <section
        className="failure-timeline-truth-boundary"
        id="failure-timeline-truth-boundary"
      >
        <h3>Truth boundary</h3>
        <p className="truth-text">{FAILURE_TIMELINE_TRUTH_BOUNDARY}</p>
      </section>

      {isPage && (
        <div className="cockpit-cta-row" id="failure-timeline-cta">
          <a
            className="btn"
            href="/lineage-comparison-lab"
            title="Open the Lineage + Comparison Lab (PS-034)"
          >
            Open Lineage + Comparison Lab
          </a>
          <a
            className="btn btn-primary"
            href="/evidence-pack"
            title="Open the Judge Evidence Pack (PS-031)"
          >
            Open Judge Evidence Pack
          </a>
          <a
            className="btn"
            href="/operations-cockpit"
            title="Open the Operations Cockpit / Flight Recorder v2 (PS-032)"
          >
            Open Operations Cockpit
          </a>
          <a
            className="btn"
            href="/b2-rehydrate-comparison"
            title="Open the B2 Rehydrate Comparison (PS-029)"
          >
            Open B2 Rehydrate Comparison
          </a>
          <a
            className="btn"
            href="/manifest-verification"
            title="Open the Manifest Verification Panel (PS-028)"
          >
            Open Manifest Verification Panel
          </a>
          <a
            className="btn"
            href="/b2-evidence"
            title="Open the B2 Evidence Explorer (PS-026)"
          >
            Open B2 Evidence Explorer
          </a>
          <a
            className="btn"
            href="/genblaze-pipeline"
            title="Open the Genblaze Pipeline Graph (PS-027)"
          >
            Open Genblaze Pipeline Graph
          </a>
          <a
            className="btn"
            href={"/passport/" + FAILURE_TIMELINE_RUN_ID}
            title="Open the verified golden demo Provenance Passport"
          >
            Open Golden Passport
          </a>
          <a className="btn" href="/" title="Back to Judge Cockpit Home">
            Back to Judge Cockpit Home
          </a>
        </div>
      )}

      <p className="hint muted-link">
        PS-030 Failure-as-Proof Timeline · fallback API base{" "}
        {DEFAULT_API_BASE_URL} · no provider call, no live B2 read, no broad
        durable read, no browser-side B2 byte verification, no fake actual
        failures.
      </p>
    </section>
  );

  if (!isPage) {
    return card;
  }

  return (
    <main className="cockpit failure-timeline-page-wrap">
      <header className="cockpit-hero" id="top">
        <p className="eyebrow">ProofStudio · Failure-as-Proof Timeline</p>
        <h1>The golden workflow as an evidence-backed operational timeline</h1>
        <p className="thesis">
          Failure, skipped providers, retry decisions, fallback readiness,
          durable storage, and rehydrate behavior are auditable workflow
          evidence, not hidden noise.
        </p>
        <p className="hero-explainer">
          The Failure-as-Proof Timeline exposes the golden workflow as a
          production timeline: provider routing, generation, B2 archive,
          manifest, rehydrate. It shows exactly where captured failures,
          retries, and fallbacks would appear if future evidence captured
          them, while the verified golden run currently proves durable B2
          rehydrate with zero provider calls. Every value is sourced verbatim
          from the checked-in evidence (PS-021, PS-024, PS-025, PS-026, PS-027,
          PS-028, PS-029). No fake failures are claimed. The timeline does not
          call any provider, does not read any B2 object, and does not claim
          the browser fetched and hashed the B2 object.
        </p>
      </header>
      {card}
    </main>
  );
}

function linkLabel(href: string): string {
  if (href === "/b2-rehydrate-comparison") return "B2 Rehydrate Comparison";
  if (href === "/manifest-verification") return "Manifest Verification";
  if (href === "/b2-evidence") return "B2 Evidence Explorer";
  if (href === "/genblaze-pipeline") return "Genblaze Pipeline Graph";
  if (href.startsWith("/passport/")) return "Golden Passport";
  if (href === "/") return "Judge Cockpit Home";
  return href;
}
