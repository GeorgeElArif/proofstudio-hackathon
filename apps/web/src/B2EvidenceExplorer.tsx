// PS-026 B2 Evidence Explorer.
//
// A dedicated, judge-facing product surface that surfaces the verified
// Backblaze B2 durable evidence recorded by PS-021 and pinned by PS-024 /
// PS-025. The explorer shows every required durable field: run_id,
// campaign_id, archive URI, archive SHA-256, source slice, B2 archive
// status, rehydrate source, provider calls during rehydrate, no live
// provider call flag, source evidence files, the local-contract-vs-public
// deployment distinction, and the truth boundary.
//
// All displayed values come from apps/web/src/b2Evidence.ts, which is sourced
// verbatim from docs/evidence/demo/golden-demo-run.json. The PS-026 smoke
// validates these constants match the manifest and PS-021 evidence exactly.
//
// The component also exposes a `variant` prop so the same surface can render
// as a full page (via the /b2-evidence route in App.tsx) or as an inline
// section inside PublicPassportPage. It performs no network call and no
// provider call: it only renders verified, checked-in evidence.

import {
  B2_EVIDENCE_TRUTH_BOUNDARY,
  GOLDEN_DEMO_ARCHIVE_SHA256,
  GOLDEN_DEMO_ARCHIVE_URI,
  GOLDEN_DEMO_B2_ARCHIVE_STATUS,
  GOLDEN_DEMO_CAMPAIGN_ID,
  GOLDEN_DEMO_EVIDENCE_FILES,
  GOLDEN_DEMO_LOCAL_CONTRACT_PROOF,
  GOLDEN_DEMO_MANIFEST_PATH,
  GOLDEN_DEMO_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE,
  GOLDEN_DEMO_PUBLIC_DEPLOYMENT_PENDING,
  GOLDEN_DEMO_REHYDRATE_SOURCE,
  GOLDEN_DEMO_RUN_ID,
  GOLDEN_DEMO_SOURCE_SLICE,
  GOLDEN_DEMO_UNLOCK_SCOPE,
} from "./b2Evidence";
import { DEFAULT_API_BASE_URL } from "./api";
import { TrustBoundaryLayer } from "./TrustBoundaryLayer";
import { MultimodalProofLayer } from "./MultimodalProofLayer";
import { TranscriptTimestampEvidenceLayer } from "./TranscriptTimestampEvidenceLayer";
import { CampaignIntelligenceJudgeNarrativeLayer } from "./CampaignIntelligenceJudgeNarrativeLayer";
import { CloudflareLowCostBackboneLayer } from "./CloudflareLowCostBackboneLayer";
import { ProductionReadinessDemoModeLayer } from "./ProductionReadinessDemoModeLayer";
import { VoiceAudioEvidenceChoiceLayer } from "./VoiceAudioEvidenceChoiceLayer";

type B2EvidenceExplorerVariant = "page" | "section";

export function B2EvidenceExplorer({
  variant = "page",
}: {
  variant?: B2EvidenceExplorerVariant;
}) {
  const isPage = variant === "page";

  const card = (
    <section
      className={
        isPage
          ? "card col-full b2-evidence-explorer b2-evidence-explorer-page"
          : "card col-full b2-evidence-explorer"
      }
      id="b2-evidence-explorer"
      aria-label="B2 Evidence Explorer"
    >
      <header className="b2-evidence-explorer-head">
        <span className="infra-tag">Backblaze B2</span>
        <h2>B2 Evidence Explorer</h2>
      </header>

      <p className="subhead">
        One canonical judge-facing view over the verified durable evidence
        behind the golden demo run. Every field below is sourced verbatim from{" "}
        <code className="mono">{GOLDEN_DEMO_MANIFEST_PATH}</code>, which is
        itself traced to the PS-021 live B2 durable rehydrate smoke. Nothing
        here is invented and nothing here is fetched live from B2.
      </p>

      <div className="b2-evidence-explorer-grid">
        <div className="b2-evidence-block">
          <h3>Run identity</h3>
          <dl className="kv">
            <dt>run_id</dt>
            <dd className="mono">{GOLDEN_DEMO_RUN_ID}</dd>
            <dt>campaign_id</dt>
            <dd className="mono">{GOLDEN_DEMO_CAMPAIGN_ID}</dd>
            <dt>source slice</dt>
            <dd className="mono">{GOLDEN_DEMO_SOURCE_SLICE}</dd>
            <dt>unlock scope</dt>
            <dd className="mono">{GOLDEN_DEMO_UNLOCK_SCOPE}</dd>
          </dl>
        </div>

        <div className="b2-evidence-block">
          <h3>B2 archive</h3>
          <dl className="kv">
            <dt>archive URI</dt>
            <dd className="mono b2-archive-uri">{GOLDEN_DEMO_ARCHIVE_URI}</dd>
            <dt>archive SHA-256</dt>
            <dd className="mono b2-archive-sha">
              {GOLDEN_DEMO_ARCHIVE_SHA256}
            </dd>
            <dt>B2 archive status</dt>
            <dd className="mono">{GOLDEN_DEMO_B2_ARCHIVE_STATUS}</dd>
          </dl>
          <p className="hint">
            The archive URI points at a public Backblaze B2 object stored as
            run-archive JSON. The explorer references the URI and SHA-256 but
            does not fetch the object itself; judges verify the bytes against
            the recorded SHA-256 if they want independent confirmation.
          </p>
        </div>

        <div className="b2-evidence-block">
          <h3>Rehydrate proof</h3>
          <dl className="kv">
            <dt>rehydrate source</dt>
            <dd className="mono">{GOLDEN_DEMO_REHYDRATE_SOURCE}</dd>
            <dt>provider calls during rehydrate</dt>
            <dd className="mono">
              {String(GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE)}
            </dd>
            <dt>no live provider call during rehydrate</dt>
            <dd className="mono">
              {String(
                GOLDEN_DEMO_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
              )}
            </dd>
          </dl>
          <p className="hint">
            PS-021 proved the run can be rehydrated from B2 archive content
            with zero provider calls. The explorer surfaces this verbatim so a
            judge never mistakes durability for a fresh live run.
          </p>
        </div>

        <div className="b2-evidence-block">
          <h3>Deployment status</h3>
          <dl className="kv">
            <dt>local contract proof</dt>
            <dd className="mono">
              {String(GOLDEN_DEMO_LOCAL_CONTRACT_PROOF)}
            </dd>
            <dt>public deployment pending</dt>
            <dd className="mono">
              {String(GOLDEN_DEMO_PUBLIC_DEPLOYMENT_PENDING)}
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

      <div className="b2-evidence-files">
        <h3>Source evidence files</h3>
        <ul className="infra-points">
          {GOLDEN_DEMO_EVIDENCE_FILES.map((file) => (
            <li key={file}>
              <code className="mono">{file}</code>
            </li>
          ))}
        </ul>
      </div>

      <section className="b2-evidence-truth-boundary" id="b2-truth-boundary">
        <h3>Truth boundary</h3>
        <p className="truth-text">{B2_EVIDENCE_TRUTH_BOUNDARY}</p>
      </section>

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
            href={"/passport/" + GOLDEN_DEMO_RUN_ID}
            title="Open the verified golden demo Provenance Passport"
          >
            Open Golden Passport
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
            href="/b2-rehydrate-comparison"
            title="Open the B2 Rehydrate Comparison (PS-029)"
          >
            Open B2 Rehydrate Comparison
          </a>
          <a
            className="btn"
            href="/genblaze-pipeline"
            title="Open the Genblaze Pipeline Graph (PS-027)"
          >
            Open Genblaze Pipeline Graph
          </a>
          <a className="btn" href="/">
            Back to Judge Cockpit Home
          </a>
          <a className="btn" href="/review">
            Open Review Room
          </a>
        </div>
      )}

      <MultimodalProofLayer variant="panel" />

      <TranscriptTimestampEvidenceLayer variant="panel" />

      <VoiceAudioEvidenceChoiceLayer variant="panel" />

      <CampaignIntelligenceJudgeNarrativeLayer variant="panel" />

      <CloudflareLowCostBackboneLayer variant="panel" />

      <ProductionReadinessDemoModeLayer variant="panel" />

      <TrustBoundaryLayer variant="panel" />

      <p className="hint muted-link">
        PS-026 B2 Evidence Explorer · fallback API base {DEFAULT_API_BASE_URL} ·
        no provider call, no live B2 read, no broad durable read.
      </p>
    </section>
  );

  if (!isPage) {
    return card;
  }

  return (
    <main className="cockpit b2-evidence-explorer-page-wrap">
      <header className="cockpit-hero" id="top">
        <p className="eyebrow">ProofStudio · B2 Evidence Explorer</p>
        <h1>Verified Backblaze B2 durable evidence</h1>
        <p className="thesis">
          One judge-facing view over the strongest verified durable proof
          ProofStudio has produced.
        </p>
        <p className="hero-explainer">
          The B2 Evidence Explorer surfaces the verified durable evidence
          behind the golden demo run: the B2 archive URI and SHA-256, the
          rehydrate source (<code className="mono">b2_rehydrated</code>), zero
          provider calls during rehydrate, and the local-contract-vs-public
          deployment distinction. Every value is sourced verbatim from the
          checked-in PS-024 golden demo manifest, itself traced to the PS-021
          live B2 durable rehydrate smoke.
        </p>
      </header>
      {card}
    </main>
  );
}
