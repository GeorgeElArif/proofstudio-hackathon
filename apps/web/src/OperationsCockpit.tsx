// PS-032 Operations Cockpit / Flight Recorder v2.
//
// The first PS-031A hardened product module. It merges Mission Control, Flight
// Recorder, Failure-as-Proof Timeline, Failure Theater, Evidence Graph, and
// the pipeline lifecycle view into one operating cockpit for designers,
// marketers, reviewers, clients, and judges -- not another disconnected proof
// page.
//
// A creative operator can open one cockpit and answer:
//   - What campaign/run am I looking at?
//   - What happened first, next, and last?
//   - Which evidence is checked-in?
//   - Which evidence points to B2?
//   - Which evidence points to Genblaze manifest verification?
//   - Did rehydrate call providers again?
//   - Where would failures / retries / fallbacks appear?
//   - What is ready for review / export?
//   - What is still pending or not claimed?
//   - Which proof surface should I open next?
//
// All displayed values come from apps/web/src/operationsCockpit.ts, which is
// sourced verbatim from the checked-in PS-024 golden demo manifest and the
// PS-021 / PS-025 / PS-026 / PS-027 / PS-028 / PS-029 / PS-030 / PS-031
// source evidence. The PS-032 smoke validates these constants match the
// manifest and source evidence exactly.
//
// The component also exposes a `variant` prop so the same surface can render
// as a full page (via the /operations-cockpit route in App.tsx) or as an
// inline section inside other judge surfaces. It performs no network call,
// calls no provider, and reads no B2 object: it only renders verified,
// checked-in evidence.

import {
  OPERATIONS_COCKPIT_ACTION_ROUTES,
  OPERATIONS_COCKPIT_CAMPAIGN_ID,
  OPERATIONS_COCKPIT_CLAIM_BOUNDARY_ALLOWED,
  OPERATIONS_COCKPIT_CLAIM_BOUNDARY_FORBIDDEN,
  OPERATIONS_COCKPIT_COCKPIT_ID,
  OPERATIONS_COCKPIT_COCKPIT_VERSION,
  OPERATIONS_COCKPIT_DESIGNER_MARKETER_NEXT_ACTIONS,
  OPERATIONS_COCKPIT_EVIDENCE_GRAPH_EDGES,
  OPERATIONS_COCKPIT_EVIDENCE_GRAPH_NODES,
  OPERATIONS_COCKPIT_FAILURE_THEATER_NOTE,
  OPERATIONS_COCKPIT_FLIGHT_RECORDER_EVENTS,
  OPERATIONS_COCKPIT_GENERATED_FROM,
  OPERATIONS_COCKPIT_IMPLEMENTATION_ROADMAP,
  OPERATIONS_COCKPIT_LIMITATIONS,
  OPERATIONS_COCKPIT_LOCAL_CONTRACT_PROOF,
  OPERATIONS_COCKPIT_NO_FAKE_FAILURES_LINE,
  OPERATIONS_COCKPIT_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  OPERATIONS_COCKPIT_PHASE_MAP,
  OPERATIONS_COCKPIT_PS031A_ROADMAP_CORRECTION,
  OPERATIONS_COCKPIT_PUBLIC_DEPLOYMENT_PENDING,
  OPERATIONS_COCKPIT_PROVIDER_CALLS_DURING_REHYDRATE,
  OPERATIONS_COCKPIT_REHYDRATE_SOURCE,
  OPERATIONS_COCKPIT_RUN_ID,
  OPERATIONS_COCKPIT_RUN_STATUS,
  OPERATIONS_COCKPIT_SOURCES,
  OPERATIONS_COCKPIT_TRUTH_BOUNDARY,
  OPERATIONS_COCKPIT_UNLOCK_SCOPE,
  OPERATIONS_COCKPIT_ZERO_PROVIDER_CALLS_LINE,
  type OperationsCockpitTruthClass,
} from "./operationsCockpit";
import { DEFAULT_API_BASE_URL } from "./api";

type OperationsCockpitVariant = "page" | "section";

const TRUTH_CLASS_LABEL: Record<OperationsCockpitTruthClass, string> = {
  checked_in_evidence: "checked-in evidence",
  b2_archive_reference: "B2 archive reference",
  genblaze_manifest_evidence: "Genblaze manifest evidence",
  rehydrate_proof: "rehydrate proof",
  local_export_contract: "local export contract",
  inferred_product_explanation: "inferred product explanation",
  public_deployment_pending: "public deployment pending",
};

export function OperationsCockpit({
  variant = "page",
}: {
  variant?: OperationsCockpitVariant;
}) {
  const isPage = variant === "page";

  const card = (
    <section
      className={
        isPage
          ? "card col-full operations-cockpit operations-cockpit-page"
          : "card col-full operations-cockpit"
      }
      id="operations-cockpit"
      aria-label="Operations Cockpit / Flight Recorder v2"
    >
      <header className="operations-cockpit-head">
        <span className="infra-tag">Operations</span>
        <h2>Operations Cockpit</h2>
      </header>

      <p className="subhead">
        One operating cockpit over the golden workflow: run status, operational
        phase map, flight recorder timeline, evidence graph, Failure Theater,
        action rail, designer / marketer next actions, and an honest truth
        boundary. Every value below is sourced verbatim from the checked-in
        evidence (PS-021, PS-024, PS-025, PS-026, PS-027, PS-028, PS-029,
        PS-030, PS-031). Nothing here is invented, nothing here is fetched
        live from B2, and no provider is called. ProofStudio is an AI media
        operations cockpit, not another AI generator.
      </p>

      {/* 1. Cockpit identity */}
      <div
        className="operations-cockpit-section operations-cockpit-identity"
        id="operations-cockpit-identity"
        data-section-key="cockpit_identity"
      >
        <h3>Cockpit identity</h3>
        <dl className="kv">
          <dt>surface</dt>
          <dd className="mono operations-cockpit-surface-name">
            Operations Cockpit
          </dd>
          <dt>recorder</dt>
          <dd className="mono operations-cockpit-recorder-name">
            Flight Recorder
          </dd>
          <dt>slice</dt>
          <dd className="mono operations-cockpit-slice">PS-032</dd>
          <dt>cockpit_id</dt>
          <dd className="mono operations-cockpit-cockpit-id">
            {OPERATIONS_COCKPIT_COCKPIT_ID}
          </dd>
          <dt>cockpit_version</dt>
          <dd className="mono operations-cockpit-cockpit-version">
            {OPERATIONS_COCKPIT_COCKPIT_VERSION}
          </dd>
          <dt>run_id</dt>
          <dd className="mono operations-cockpit-run-id">
            {OPERATIONS_COCKPIT_RUN_ID}
          </dd>
          <dt>campaign_id</dt>
          <dd className="mono operations-cockpit-campaign-id">
            {OPERATIONS_COCKPIT_CAMPAIGN_ID}
          </dd>
          <dt>public deployment</dt>
          <dd className="mono operations-cockpit-public-deployment-pending">
            {String(OPERATIONS_COCKPIT_PUBLIC_DEPLOYMENT_PENDING)}
          </dd>
        </dl>
      </div>

      {/* 2. Run status summary */}
      <div
        className="operations-cockpit-section"
        id="operations-cockpit-run-status"
        data-section-key="run_status_summary"
      >
        <h3>Run status summary</h3>
        <p className="hint">
          The state of the golden run at a glance: identity, archive, manifest,
          rehydrate, provider calls during rehydrate, evidence pack, review /
          export readiness, and pending public deployment.
        </p>
        <ul className="infra-points operations-cockpit-status-list">
          {OPERATIONS_COCKPIT_RUN_STATUS.map((item) => (
            <li
              key={item.key}
              className="operations-cockpit-status-item"
              data-status-key={item.key}
            >
              <div className="operations-cockpit-status-head">
                <span className="operations-cockpit-status-label">
                  {item.label}
                </span>
                <span className="pill ok">
                  <span className="dot" />
                  {item.status}
                </span>
                <span className="pill info">
                  <span className="dot" />
                  {TRUTH_CLASS_LABEL[item.truthClass]}
                </span>
              </div>
              <p className="hint">{item.note}</p>
            </li>
          ))}
        </ul>
        <dl className="kv">
          <dt>rehydrate_source</dt>
          <dd className="mono operations-cockpit-rehydrate-source">
            {OPERATIONS_COCKPIT_REHYDRATE_SOURCE}
          </dd>
          <dt>provider_calls_during_rehydrate</dt>
          <dd className="mono operations-cockpit-provider-calls">
            {String(OPERATIONS_COCKPIT_PROVIDER_CALLS_DURING_REHYDRATE)}
          </dd>
          <dt>no_live_provider_call_during_rehydrate</dt>
          <dd className="mono operations-cockpit-no-live-provider-call">
            {String(OPERATIONS_COCKPIT_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE)}
          </dd>
        </dl>
      </div>

      {/* 3. Operational phase map */}
      <div
        className="operations-cockpit-section"
        id="operations-cockpit-phase-map"
        data-section-key="phase_map"
      >
        <h3>Operational phase map</h3>
        <p className="hint">
          The run as 10 phases. Each phase carries a title, status, truth
          class, evidence source, and the next route or action.
        </p>
        <ol className="operations-cockpit-phase-list">
          {OPERATIONS_COCKPIT_PHASE_MAP.map((phase) => (
            <li
              key={phase.key}
              className={`operations-cockpit-phase kind-${phase.truthClass}`}
              data-phase-key={phase.key}
              data-truth-class={phase.truthClass}
            >
              <span className="operations-cockpit-phase-idx">
                {String(phase.idx).padStart(2, "0")}
              </span>
              <div className="operations-cockpit-phase-body">
                <div className="operations-cockpit-phase-head">
                  <h4 className="operations-cockpit-phase-title">
                    {phase.title}
                  </h4>
                  <span className="pill ok">
                    <span className="dot" />
                    {phase.status}
                  </span>
                  <span
                    className={`pill ${
                      phase.truthClass === "public_deployment_pending"
                        ? "info"
                        : phase.truthClass === "inferred_product_explanation"
                          ? "neutral"
                          : "ok"
                    }`}
                  >
                    <span className="dot" />
                    {TRUTH_CLASS_LABEL[phase.truthClass]}
                  </span>
                </div>
                <p className="hint operations-cockpit-phase-evidence">
                  evidence: {phase.evidenceSource}
                </p>
                <p className="hint muted-link operations-cockpit-phase-next">
                  next:{" "}
                  <a href={phase.nextRoute}>{routeLabel(phase.nextRoute)}</a>
                </p>
              </div>
            </li>
          ))}
        </ol>
      </div>

      {/* 4. Flight Recorder timeline */}
      <div
        className="operations-cockpit-section"
        id="operations-cockpit-flight-recorder"
        data-section-key="flight_recorder_timeline"
      >
        <h3>Flight Recorder timeline</h3>
        <p className="hint">
          An ordered timeline of events explaining the golden run. The
          checked-in evidence does not carry real wall-clock timestamps, so
          each event records a timestamp-honesty label instead of an invented
          timestamp ({" "}
          <code className="mono">source evidence order</code>,{" "}
          <code className="mono">checked-in evidence order</code>, or{" "}
          <code className="mono">
            not timestamped in checked-in evidence
          </code>
          ).
        </p>
        <ol className="failure-timeline-list operations-cockpit-flight-list">
          {OPERATIONS_COCKPIT_FLIGHT_RECORDER_EVENTS.map((event) => (
            <li
              key={event.key}
              className={`failure-timeline-event operations-cockpit-flight-event kind-${event.truthClass}`}
              data-event-key={event.key}
            >
              <span className="failure-timeline-event-idx">
                {String(event.seq).padStart(2, "0")}
              </span>
              <div className="failure-timeline-event-body">
                <div className="failure-timeline-event-head">
                  <h4 className="failure-timeline-event-title">
                    {event.title}
                  </h4>
                  <span className="pill ok">
                    <span className="dot" />
                    {event.status}
                  </span>
                  <span className="pill info">
                    <span className="dot" />
                    {TRUTH_CLASS_LABEL[event.truthClass]}
                  </span>
                  <span className="pill neutral">
                    <span className="dot" />
                    {event.eventType}
                  </span>
                </div>
                <p className="failure-timeline-event-summary">
                  {event.evidenceAnchor}
                </p>
                <p className="hint muted-link">
                  truth class: {TRUTH_CLASS_LABEL[event.truthClass]} ·
                  timestamp: {event.timestampHonesty}
                </p>
                {event.routeLink && (
                  <div className="failure-timeline-event-links">
                    <a className="btn" href={event.routeLink}>
                      {routeLabel(event.routeLink)}
                    </a>
                  </div>
                )}
              </div>
            </li>
          ))}
        </ol>
      </div>

      {/* 5. Evidence graph */}
      <div
        className="operations-cockpit-section"
        id="operations-cockpit-evidence-graph"
        data-section-key="evidence_graph"
      >
        <h3>Evidence graph</h3>
        <p className="hint">
          An accessible card / column representation (no graph library
          required). Nodes map to checked-in evidence and proof surfaces; edges
          trace the campaign → run → router → pipeline → asset → archive →
          verification → rehydrate → passport → pack → review chain.
        </p>
        <div className="operations-cockpit-graph-grid">
          {OPERATIONS_COCKPIT_EVIDENCE_GRAPH_NODES.map((node) => (
            <article
              key={node.id}
              className={`operations-cockpit-graph-node kind-${node.kind}`}
              data-node-id={node.id}
            >
              <h4>{node.label}</h4>
              <span className="pill info">
                <span className="dot" />
                {TRUTH_CLASS_LABEL[node.kind]}
              </span>
              {node.route && (
                <a className="btn" href={node.route}>
                  {routeLabel(node.route)}
                </a>
              )}
            </article>
          ))}
        </div>
        <div
          className="operations-cockpit-graph-edges"
          id="operations-cockpit-graph-edges"
        >
          <h4>Edges</h4>
          <ul className="infra-points operations-cockpit-graph-edge-list">
            {OPERATIONS_COCKPIT_EVIDENCE_GRAPH_EDGES.map((edge) => (
              <li
                key={`${edge.from}-${edge.to}`}
                className="operations-cockpit-graph-edge"
                data-edge-from={edge.from}
                data-edge-to={edge.to}
              >
                <code className="mono">
                  {nodeLabel(edge.from)} → {nodeLabel(edge.to)}
                </code>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 6. Failure Theater slot */}
      <section
        className="operations-cockpit-section operations-cockpit-failure-theater"
        id="operations-cockpit-failure-theater"
        aria-label="Failure Theater"
        data-section-key="failure_theater"
      >
        <h3>Failure Theater</h3>
        <p className="hint">{OPERATIONS_COCKPIT_FAILURE_THEATER_NOTE}</p>
        <p className="failure-as-proof-mandate">
          <span
            className="failure-as-proof-line operations-cockpit-no-fake-failures"
            data-mandate="no_fake_failures"
          >
            {OPERATIONS_COCKPIT_NO_FAKE_FAILURES_LINE}
          </span>
        </p>
        <p className="failure-as-proof-mandate">
          <span
            className="failure-as-proof-line failure-as-proof-zero-calls operations-cockpit-zero-provider-calls"
            data-mandate="zero_provider_calls"
          >
            {OPERATIONS_COCKPIT_ZERO_PROVIDER_CALLS_LINE}
          </span>
        </p>
      </section>

      {/* 7. Action rail */}
      <div
        className="operations-cockpit-section operations-cockpit-action-rail"
        id="operations-cockpit-action-rail"
        data-section-key="action_rail"
      >
        <h3>Action rail</h3>
        <p className="hint">
          Jump to any implemented proof surface from the cockpit.
        </p>
        <ul className="infra-points operations-cockpit-action-list">
          {OPERATIONS_COCKPIT_ACTION_ROUTES.map((route) => (
            <li key={route.href} data-route-href={route.href}>
              <a className="btn" href={route.href}>
                {route.label}
              </a>
              <span className="hint muted-link" style={{ marginLeft: 8 }}>
                {route.tag} · {route.description}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* 8. Designer / marketer next actions */}
      <div
        className="operations-cockpit-section"
        id="operations-cockpit-designer-marketer-next-actions"
        data-section-key="designer_marketer_next_actions"
      >
        <h3>Designer / marketer next actions</h3>
        <ul className="infra-points operations-cockpit-next-actions">
          {OPERATIONS_COCKPIT_DESIGNER_MARKETER_NEXT_ACTIONS.map((action) => (
            <li key={action}>{action}</li>
          ))}
        </ul>
      </div>

      {/* 9. Truth boundary */}
      <section
        className="operations-cockpit-section operations-cockpit-truth-boundary"
        id="operations-cockpit-truth-boundary"
        data-section-key="truth_boundary"
      >
        <h3>Truth boundary</h3>
        <p className="truth-text">{OPERATIONS_COCKPIT_TRUTH_BOUNDARY}</p>
        <div className="operations-cockpit-claim-boundary-grid">
          <div className="operations-cockpit-claim-boundary-col">
            <h4>Allowed claims</h4>
            <ul className="infra-points">
              {OPERATIONS_COCKPIT_CLAIM_BOUNDARY_ALLOWED.map((claim) => (
                <li key={claim}>
                  <span className="pill ok">
                    <span className="dot" />
                    {claim}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div className="operations-cockpit-claim-boundary-col">
            <h4>Forbidden claims</h4>
            <ul className="infra-points">
              {OPERATIONS_COCKPIT_CLAIM_BOUNDARY_FORBIDDEN.map((claim) => (
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

      {/* 10. Limitations */}
      <div
        className="operations-cockpit-section"
        id="operations-cockpit-limitations"
        data-section-key="limitations"
      >
        <h3>Limitations</h3>
        <ul className="infra-points operations-cockpit-limitations-points">
          {OPERATIONS_COCKPIT_LIMITATIONS.map((lim) => (
            <li key={lim}>{lim}</li>
          ))}
        </ul>
      </div>

      {/* Source evidence files */}
      <div
        className="operations-cockpit-section operations-cockpit-files"
        id="operations-cockpit-files"
      >
        <h3>Source evidence files</h3>
        <ul className="infra-points">
          {OPERATIONS_COCKPIT_SOURCES.map((src) => (
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
          <code className="mono">{OPERATIONS_COCKPIT_IMPLEMENTATION_ROADMAP}</code>
        </p>
        <p className="hint muted-link">
          hardened module correction:{" "}
          <code className="mono">
            {OPERATIONS_COCKPIT_PS031A_ROADMAP_CORRECTION}
          </code>
        </p>
      </div>

      {/* Deployment status */}
      <div
        className="operations-cockpit-section operations-cockpit-deployment"
        id="operations-cockpit-deployment"
      >
        <h3>Deployment status</h3>
        <dl className="kv">
          <dt>local contract proof</dt>
          <dd className="mono">
            {String(OPERATIONS_COCKPIT_LOCAL_CONTRACT_PROOF)}
          </dd>
          <dt>public deployment pending</dt>
          <dd className="mono">
            {String(OPERATIONS_COCKPIT_PUBLIC_DEPLOYMENT_PENDING)}
          </dd>
          <dt>unlock scope</dt>
          <dd className="mono">{OPERATIONS_COCKPIT_UNLOCK_SCOPE}</dd>
        </dl>
        <p className="hint">
          The local contract (FastAPI TestClient against a fresh empty store
          resolving the golden run_id from checked-in evidence) is verified by
          PS-025. The public Render deployment is not verified yet: the new
          backend must be deployed and the public URL verified end-to-end
          before this status changes.
        </p>
      </div>

      {isPage && (
        <div className="cockpit-cta-row" id="operations-cockpit-cta">
          <a className="btn btn-primary" href="/evidence-pack">
            Open Judge Evidence Pack
          </a>
          <a
            className="btn"
            href="/lineage-comparison-lab"
            title="Open the Lineage + Comparison Lab (PS-034)"
          >
            Open Lineage + Comparison Lab
          </a>
          <a
            className="btn"
            href="/provider-decision-intelligence"
            title="Open the Provider Decision Intelligence (PS-033)"
          >
            Open Provider Decision Intelligence
          </a>
          <a className="btn" href="/failure-timeline">
            Open Failure-as-Proof Timeline
          </a>
          <a className="btn" href="/b2-rehydrate-comparison">
            Open B2 Rehydrate Comparison
          </a>
          <a className="btn" href="/manifest-verification">
            Open Manifest Verification Panel
          </a>
          <a className="btn" href="/b2-evidence">
            Open B2 Evidence Explorer
          </a>
          <a className="btn" href="/genblaze-pipeline">
            Open Genblaze Pipeline Graph
          </a>
          <a
            className="btn"
            href={"/passport/" + OPERATIONS_COCKPIT_RUN_ID}
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
        PS-032 Operations Cockpit / Flight Recorder v2 · generated from{" "}
        {OPERATIONS_COCKPIT_GENERATED_FROM} · fallback API base{" "}
        {DEFAULT_API_BASE_URL} · no provider call, no live B2 read, no broad
        durable read, no browser-side B2 byte verification, no raw media byte
        inspection, no fake failure claim.
      </p>
    </section>
  );

  if (!isPage) {
    return card;
  }

  return (
    <main className="cockpit operations-cockpit-page-wrap">
      <header className="cockpit-hero" id="top">
        <p className="eyebrow">ProofStudio · Operations Cockpit</p>
        <h1>The golden run, as an operating cockpit</h1>
        <p className="thesis">
          Flight Recorder, phase map, evidence graph, and Failure Theater in
          one cockpit -- for designers, marketers, reviewers, clients, and
          judges.
        </p>
        <p className="hero-explainer">
          The Operations Cockpit merges Mission Control, Flight Recorder,
          Failure-as-Proof Timeline, Failure Theater, Evidence Graph, and the
          pipeline lifecycle view into one operating cockpit over the verified
          golden run. It shows run status, the operational phase map, an
          ordered flight recorder timeline, the evidence graph, where captured
          failures would appear, designer / marketer next actions, and an
          honest truth boundary. Every value is sourced verbatim from the
          checked-in evidence (PS-021, PS-024, PS-025, PS-026, PS-027, PS-028,
          PS-029, PS-030, PS-031). It does not call any provider, does not read
          any B2 object, and does not claim the browser fetched and hashed the
          B2 object. No fake failures are claimed.
        </p>
      </header>
      {card}
    </main>
  );
}

function routeLabel(href: string): string {
  if (href === "/evidence-pack") return "Judge Evidence Pack";
  if (href === "/failure-timeline") return "Failure-as-Proof Timeline";
  if (href === "/b2-rehydrate-comparison") return "B2 Rehydrate Comparison";
  if (href === "/manifest-verification") return "Manifest Verification Panel";
  if (href === "/b2-evidence") return "B2 Evidence Explorer";
  if (href === "/genblaze-pipeline") return "Genblaze Pipeline Graph";
  if (href.startsWith("/passport/")) return "Golden Passport";
  if (href === "/review") return "Review Room";
  if (href === "/") return "Judge Cockpit Home";
  return href;
}

function nodeLabel(nodeId: string): string {
  const node = OPERATIONS_COCKPIT_EVIDENCE_GRAPH_NODES.find(
    (n) => n.id === nodeId,
  );
  return node ? node.label : nodeId;
}
