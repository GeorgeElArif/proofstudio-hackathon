// PS-027 Genblaze Pipeline Graph.
//
// A dedicated, judge-facing product surface that exposes the ProofStudio media
// pipeline as a Genblaze Pipeline Graph: Brief -> ProviderRouter -> Genblaze
// pipeline -> Generated asset -> B2 archive -> Provenance passport -> Durable
// rehydrate (zero provider calls) -> Judge review.
//
// The graph renders verified golden demo evidence (run_id, campaign_id,
// archive URI, archive SHA-256, rehydrate_source = b2_rehydrated,
// provider_calls_during_rehydrate = 0, no_live_provider_call_during_rehydrate
// = true) and the truth boundary that distinguishes:
//   - verified pipeline evidence
//   - inferred product explanation
//   - local contract proof
//   - public deployment pending
//
// All displayed values come from apps/web/src/genblazePipeline.ts, which is
// sourced verbatim from docs/evidence/demo/golden-demo-run.json (PS-024
// manifest) and the PS-021 / PS-025 / PS-026 source evidence. The PS-027 smoke
// validates these constants match the manifest and source evidence exactly.
//
// The component also exposes a `variant` prop so the same surface can render
// as a full page (via the /genblaze-pipeline route in App.tsx) or as an
// inline section inside other judge surfaces. It performs no network call
// and no provider call: it only renders verified, checked-in evidence.

import {
  GENBLAZE_CLAIM_BOUNDARY_ALLOWED,
  GENBLAZE_CLAIM_BOUNDARY_FORBIDDEN,
  GENBLAZE_PIPELINE_ARCHIVE_SHA256,
  GENBLAZE_PIPELINE_ARCHIVE_URI,
  GENBLAZE_PIPELINE_CAMPAIGN_ID,
  GENBLAZE_PIPELINE_EDGES,
  GENBLAZE_PIPELINE_EVIDENCE_FILES,
  GENBLAZE_PIPELINE_LOCAL_CONTRACT_PROOF,
  GENBLAZE_PIPELINE_NODES,
  GENBLAZE_PIPELINE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  GENBLAZE_PIPELINE_PROVIDER_CALLS_DURING_REHYDRATE,
  GENBLAZE_PIPELINE_PUBLIC_DEPLOYMENT_PENDING,
  GENBLAZE_PIPELINE_REHYDRATE_SOURCE,
  GENBLAZE_PIPELINE_RUN_ID,
  GENBLAZE_PIPELINE_SOURCE_SLICE,
  GENBLAZE_PIPELINE_TRUTH_BOUNDARY,
  GENBLAZE_PIPELINE_UNLOCK_SCOPE,
  type GenblazePipelineNodeTruth,
} from "./genblazePipeline";
import { DEFAULT_API_BASE_URL } from "./api";

type GenblazePipelineGraphVariant = "page" | "section";

const TRUTH_CLASS_LABEL: Record<GenblazePipelineNodeTruth, string> = {
  verified_evidence: "verified pipeline evidence",
  inferred_explanation: "inferred product explanation",
  local_contract_proof: "local contract proof",
  public_deployment_pending: "public deployment pending",
};

export function GenblazePipelineGraph({
  variant = "page",
}: {
  variant?: GenblazePipelineGraphVariant;
}) {
  const isPage = variant === "page";

  const card = (
    <section
      className={
        isPage
          ? "card col-full genblaze-pipeline-graph genblaze-pipeline-graph-page"
          : "card col-full genblaze-pipeline-graph"
      }
      id="genblaze-pipeline-graph"
      aria-label="Genblaze Pipeline Graph"
    >
      <header className="genblaze-pipeline-graph-head">
        <span className="infra-tag">Genblaze</span>
        <h2>Genblaze Pipeline Graph</h2>
      </header>

      <p className="subhead">
        Brief → ProviderRouter → Genblaze orchestration → Media generation
        attempt → Asset/manifest capture → Backblaze B2 archive → Provenance
        passport → Durable rehydrate → Judge review. Every verified value
        below is sourced verbatim from the checked-in PS-024 golden demo
        manifest, itself traced to the PS-021 live B2 durable rehydrate smoke.
        Nothing here is invented and nothing here is fetched live from B2.
      </p>

      {/* Pipeline graph: nodes + directed edges */}
      <ol
        className="genblaze-pipeline-graph-steps"
        aria-label="Genblaze pipeline graph nodes"
      >
        {GENBLAZE_PIPELINE_NODES.map((node, i) => (
          <li
            key={node.id}
            className={`genblaze-pipeline-graph-step truth-${node.truthClass}`}
            data-node-id={node.id}
          >
            <span className="step-idx">{String(i + 1).padStart(2, "0")}</span>
            <span className="step-name">{node.label}</span>
            <span className={`truth-pill truth-pill-${node.truthClass}`}>
              {TRUTH_CLASS_LABEL[node.truthClass]}
            </span>
            {i < GENBLAZE_PIPELINE_NODES.length - 1 && (
              <span className="step-arrow" aria-hidden="true">→</span>
            )}
          </li>
        ))}
      </ol>

      {/* Edge story */}
      <div className="genblaze-pipeline-graph-edges" id="genblaze-pipeline-edges">
        <h3>Pipeline edge story</h3>
        <ol className="genblaze-pipeline-edge-list">
          {GENBLAZE_PIPELINE_EDGES.map((edge, i) => (
            <li
              key={`${edge.from}-${edge.to}-${i}`}
              className="genblaze-pipeline-edge"
            >
              <span className="mono edge-from">{edge.from}</span>
              <span className="edge-arrow" aria-hidden="true">→</span>
              <span className="mono edge-to">{edge.to}</span>
              <span className="edge-story">{edge.story}</span>
            </li>
          ))}
        </ol>
      </div>

      {/* Verified values */}
      <div className="genblaze-pipeline-graph-grid">
        <div className="genblaze-pipeline-block">
          <h3>Run identity</h3>
          <dl className="kv">
            <dt>run_id</dt>
            <dd className="mono genblaze-run-id">
              {GENBLAZE_PIPELINE_RUN_ID}
            </dd>
            <dt>campaign_id</dt>
            <dd className="mono genblaze-campaign-id">
              {GENBLAZE_PIPELINE_CAMPAIGN_ID}
            </dd>
            <dt>source slice</dt>
            <dd className="mono">{GENBLAZE_PIPELINE_SOURCE_SLICE}</dd>
            <dt>unlock scope</dt>
            <dd className="mono">{GENBLAZE_PIPELINE_UNLOCK_SCOPE}</dd>
          </dl>
        </div>

        <div className="genblaze-pipeline-block">
          <h3>B2 archive</h3>
          <dl className="kv">
            <dt>archive URI</dt>
            <dd className="mono genblaze-archive-uri">
              {GENBLAZE_PIPELINE_ARCHIVE_URI}
            </dd>
            <dt>archive SHA-256</dt>
            <dd className="mono genblaze-archive-sha">
              {GENBLAZE_PIPELINE_ARCHIVE_SHA256}
            </dd>
          </dl>
          <p className="hint">
            The archive URI points at a public Backblaze B2 object stored as
            run-archive JSON. The graph references the URI and SHA-256 but
            does not fetch the object itself; judges verify the bytes against
            the recorded SHA-256 if they want independent confirmation.
          </p>
        </div>

        <div className="genblaze-pipeline-block">
          <h3>Rehydrate proof</h3>
          <dl className="kv">
            <dt>rehydrate_source</dt>
            <dd className="mono genblaze-rehydrate-source">
              {GENBLAZE_PIPELINE_REHYDRATE_SOURCE}
            </dd>
            <dt>provider_calls_during_rehydrate</dt>
            <dd className="mono genblaze-provider-calls">
              {String(GENBLAZE_PIPELINE_PROVIDER_CALLS_DURING_REHYDRATE)}
            </dd>
            <dt>no_live_provider_call_during_rehydrate</dt>
            <dd className="mono genblaze-no-live-provider-call">
              {String(
                GENBLAZE_PIPELINE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
              )}
            </dd>
          </dl>
          <p className="hint">
            PS-021 proved the run can be rehydrated from B2 archive content
            with zero provider calls. The graph surfaces this verbatim so a
            judge never mistakes durability for a fresh live run.
          </p>
        </div>

        <div className="genblaze-pipeline-block">
          <h3>Deployment status</h3>
          <dl className="kv">
            <dt>local contract proof</dt>
            <dd className="mono">
              {String(GENBLAZE_PIPELINE_LOCAL_CONTRACT_PROOF)}
            </dd>
            <dt>public deployment pending</dt>
            <dd className="mono">
              {String(GENBLAZE_PIPELINE_PUBLIC_DEPLOYMENT_PENDING)}
            </dd>
          </dl>
          <p className="hint">
            The local contract (FastAPI TestClient against a fresh empty store
            resolving the golden run_id from checked-in evidence) is verified
            by PS-025. The public Render deployment is not verified yet: the
            new backend must be deployed and the public URL must be verified
            end-to-end before this distinction changes.
          </p>
        </div>
      </div>

      {/* Truth boundary */}
      <section
        className="genblaze-pipeline-graph-truth-boundary"
        id="genblaze-truth-boundary"
      >
        <h3>Truth boundary</h3>
        <p className="truth-text">{GENBLAZE_PIPELINE_TRUTH_BOUNDARY}</p>
        <div className="genblaze-claim-boundary" id="genblaze-claim-boundary">
          <div className="genblaze-claim-boundary-col">
            <h4>Allowed claims</h4>
            <ul className="infra-points">
              {GENBLAZE_CLAIM_BOUNDARY_ALLOWED.map((claim) => (
                <li key={claim}>
                  <span className="pill ok">
                    <span className="dot" />
                    {claim}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div className="genblaze-claim-boundary-col">
            <h4>Forbidden claims</h4>
            <ul className="infra-points">
              {GENBLAZE_CLAIM_BOUNDARY_FORBIDDEN.map((claim) => (
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

      {/* Source evidence files */}
      <div className="genblaze-pipeline-graph-files">
        <h3>Source evidence files</h3>
        <ul className="infra-points">
          {GENBLAZE_PIPELINE_EVIDENCE_FILES.map((file) => (
            <li key={file}>
              <code className="mono">{file}</code>
            </li>
          ))}
        </ul>
      </div>

      {isPage && (
        <div className="cockpit-cta-row">
          <a
            className="btn"
            href="/lineage-comparison-lab"
            title="Open the Lineage + Comparison Lab (PS-034)"
          >
            Open Lineage + Comparison Lab
          </a>
          <a
            className="btn"
            href="/operations-cockpit"
            title="Open the Operations Cockpit / Flight Recorder v2 (PS-032)"
          >
            Open Operations Cockpit
          </a>
          <a
            className="btn btn-primary"
            href="/b2-evidence"
            title="Open the B2 Evidence Explorer"
          >
            Open B2 Evidence Explorer
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
            href={"/passport/" + GENBLAZE_PIPELINE_RUN_ID}
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
        PS-027 Genblaze Pipeline Graph · fallback API base{" "}
        {DEFAULT_API_BASE_URL} · no provider call, no live B2 read, no broad
        durable read.
      </p>
    </section>
  );

  if (!isPage) {
    return card;
  }

  return (
    <main className="cockpit genblaze-pipeline-graph-page-wrap">
      <header className="cockpit-hero" id="top">
        <p className="eyebrow">ProofStudio · Genblaze Pipeline Graph</p>
        <h1>Verified Genblaze orchestration pipeline</h1>
        <p className="thesis">
          One judge-facing view over the verified pipeline behind the golden
          demo run.
        </p>
        <p className="hero-explainer">
          The Genblaze Pipeline Graph exposes how a run flows through the
          ProofStudio pipeline: Brief → ProviderRouter → Genblaze
          orchestration → Media generation attempt → Asset/manifest capture →
          Backblaze B2 archive → Provenance passport → Durable rehydrate
          (zero provider calls) → Judge review. Every verified value is
          sourced verbatim from the checked-in PS-024 golden demo manifest,
          itself traced to the PS-021 live B2 durable rehydrate smoke. The
          graph distinguishes verified evidence from inferred explanation,
          local contract proof, and public deployment pending.
        </p>
      </header>
      {card}
    </main>
  );
}
