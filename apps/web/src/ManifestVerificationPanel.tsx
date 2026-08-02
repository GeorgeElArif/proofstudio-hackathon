// PS-028 Manifest Verification Panel.
//
// A dedicated, judge-facing product surface that exposes the golden run
// manifest as a cross-source verification table. It compares the verified
// golden values against five checked-in evidence sources and shows whether
// every required field agrees across all sources:
//
//   1. Golden demo manifest (PS-024)
//   2. PS-021 B2 durable rehydrate evidence
//   3. PS-025 public durable passport evidence
//   4. PS-026 B2 Evidence Explorer evidence
//   5. PS-027 Genblaze Pipeline Graph evidence
//
// All displayed values come from apps/web/src/manifestVerification.ts, which
// is sourced verbatim from the checked-in PS-024 golden demo manifest and
// the PS-021 / PS-025 / PS-026 / PS-027 source evidence. The PS-028 smoke
// validates these constants match the manifest and source evidence exactly.
//
// The component also exposes a `variant` prop so the same surface can render
// as a full page (via the /manifest-verification route in App.tsx) or as an
// inline section inside other judge surfaces. It performs no network call,
// calls no provider, and reads no B2 object: it only renders verified,
// checked-in evidence.

import {
  MANIFEST_CLAIM_BOUNDARY_ALLOWED,
  MANIFEST_CLAIM_BOUNDARY_FORBIDDEN,
  MANIFEST_VERIFICATION_ARCHIVE_SHA256,
  MANIFEST_VERIFICATION_ARCHIVE_URI,
  MANIFEST_VERIFICATION_CAMPAIGN_ID,
  MANIFEST_VERIFICATION_FIELDS,
  MANIFEST_VERIFICATION_LOCAL_CONTRACT_PROOF,
  MANIFEST_VERIFICATION_MATRIX,
  MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  MANIFEST_VERIFICATION_PUBLIC_DEPLOYMENT_PENDING,
  MANIFEST_VERIFICATION_PROVIDER_CALLS_DURING_REHYDRATE,
  MANIFEST_VERIFICATION_REHYDRATE_SOURCE,
  MANIFEST_VERIFICATION_RUN_ID,
  MANIFEST_VERIFICATION_SOURCES,
  MANIFEST_VERIFICATION_TRUTH_BOUNDARY,
  MANIFEST_VERIFICATION_UNLOCK_SCOPE,
  type ManifestFieldValue,
  type ManifestVerificationFieldKey,
} from "./manifestVerification";
import { DEFAULT_API_BASE_URL } from "./api";
import { TrustBoundaryLayer } from "./TrustBoundaryLayer";
import { MultimodalProofLayer } from "./MultimodalProofLayer";
import { TranscriptTimestampEvidenceLayer } from "./TranscriptTimestampEvidenceLayer";
import { CampaignIntelligenceJudgeNarrativeLayer } from "./CampaignIntelligenceJudgeNarrativeLayer";
import { CloudflareLowCostBackboneLayer } from "./CloudflareLowCostBackboneLayer";
import { ProductionReadinessDemoModeLayer } from "./ProductionReadinessDemoModeLayer";
import { VoiceAudioEvidenceChoiceLayer } from "./VoiceAudioEvidenceChoiceLayer";

type ManifestVerificationPanelVariant = "page" | "section";

export function ManifestVerificationPanel({
  variant = "page",
}: {
  variant?: ManifestVerificationPanelVariant;
}) {
  const isPage = variant === "page";

  // Compute field-level consistency across all sources. A field is consistent
  // only when every source records the same value for it. The matrix is
  // sourced verbatim from checked-in evidence; this check is purely a
  // presentation-level cross-reference, never an overclaim.
  const consistency: Record<ManifestVerificationFieldKey, boolean> =
    Object.fromEntries(
      MANIFEST_VERIFICATION_FIELDS.map((f) => [
        f.key,
        MANIFEST_VERIFICATION_SOURCES.every((src) => {
          const cell = MANIFEST_VERIFICATION_MATRIX[src.id]?.[f.key];
          return cell !== undefined && cell === f.value;
        }),
      ]),
    ) as Record<ManifestVerificationFieldKey, boolean>;

  const allConsistent = MANIFEST_VERIFICATION_FIELDS.every(
    (f) => consistency[f.key],
  );

  const card = (
    <section
      className={
        isPage
          ? "card col-full manifest-verification-panel manifest-verification-panel-page"
          : "card col-full manifest-verification-panel"
      }
      id="manifest-verification-panel"
      aria-label="Manifest Verification Panel"
    >
      <header className="manifest-verification-panel-head">
        <span className="infra-tag">Manifest</span>
        <h2>Manifest Verification Panel</h2>
      </header>

      <p className="subhead">
        One canonical judge-facing view over the golden run manifest as a
        cross-source verification table. Every field below is sourced verbatim
        from the checked-in evidence (PS-021, PS-024, PS-025, PS-026, PS-027).
        Nothing here is invented, nothing here is fetched live from B2, and
        no provider is called.
      </p>

      {/* Verification matrix */}
      <div
        className="manifest-verification-matrix-wrap"
        id="manifest-verification-matrix"
      >
        <h3>Cross-source verification matrix</h3>
        <p className="hint">
          Rows are required manifest fields. Columns are the five checked-in
          evidence sources. The rightmost column records whether every source
          agrees on that field.
        </p>
        <div className="table-wrap">
          <table className="manifest-verification-table">
            <thead>
              <tr>
                <th scope="col">Field</th>
                {MANIFEST_VERIFICATION_SOURCES.map((src) => (
                  <th key={src.id} scope="col">
                    <span className="manifest-source-tag">{src.sliceTag}</span>
                    <span className="manifest-source-label">{src.label}</span>
                  </th>
                ))}
                <th scope="col">Consistent</th>
              </tr>
            </thead>
            <tbody>
              {MANIFEST_VERIFICATION_FIELDS.map((field) => {
                const ok = consistency[field.key];
                return (
                  <tr
                    key={field.key}
                    className={`manifest-field-row ${
                      ok ? "row-consistent" : "row-inconsistent"
                    }`}
                    data-field-key={field.key}
                  >
                    <th scope="row">
                      <code className="mono manifest-field-label">
                        {field.label}
                      </code>
                    </th>
                    {MANIFEST_VERIFICATION_SOURCES.map((src) => {
                      const cell = MANIFEST_VERIFICATION_MATRIX[src.id]?.[
                        field.key
                      ];
                      const cellMatches =
                        cell !== undefined && cell === field.value;
                      return (
                        <td
                          key={src.id}
                          className={
                            "mono manifest-cell " +
                            (cellMatches
                              ? "cell-match"
                              : cell === undefined
                                ? "cell-unavailable"
                                : "cell-mismatch")
                          }
                          data-source-id={src.id}
                        >
                          {cell === undefined ? "—" : formatValue(cell)}
                        </td>
                      );
                    })}
                    <td>
                      <span
                        className={
                          "pill " + (ok ? "ok" : "warn") + " consistency-pill"
                        }
                      >
                        <span className="dot" />
                        {ok ? "all match" : "mismatch"}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Consistency summary */}
      <div
        className="manifest-verification-summary"
        id="manifest-verification-summary"
      >
        <h3>Consistency summary</h3>
        <dl className="kv">
          <dt>all core identifiers match</dt>
          <dd>
            <span
              className={
                "pill " +
                (consistency.run_id && consistency.campaign_id ? "ok" : "warn")
              }
            >
              <span className="dot" />
              {consistency.run_id && consistency.campaign_id ? "yes" : "no"}
            </span>
          </dd>
          <dt>archive URI matches</dt>
          <dd>
            <span
              className={
                "pill " + (consistency.archive_uri ? "ok" : "warn")
              }
            >
              <span className="dot" />
              {consistency.archive_uri ? "yes" : "no"}
            </span>
          </dd>
          <dt>archive SHA-256 matches</dt>
          <dd>
            <span
              className={
                "pill " + (consistency.archive_sha256 ? "ok" : "warn")
              }
            >
              <span className="dot" />
              {consistency.archive_sha256 ? "yes" : "no"}
            </span>
          </dd>
          <dt>rehydrate source is b2_rehydrated</dt>
          <dd>
            <span
              className={
                "pill " +
                (consistency.rehydrate_source &&
                MANIFEST_VERIFICATION_REHYDRATE_SOURCE === "b2_rehydrated"
                  ? "ok"
                  : "warn")
              }
            >
              <span className="dot" />
              {consistency.rehydrate_source &&
              MANIFEST_VERIFICATION_REHYDRATE_SOURCE === "b2_rehydrated"
                ? "yes"
                : "no"}
            </span>
          </dd>
          <dt>provider calls during rehydrate equal 0</dt>
          <dd>
            <span
              className={
                "pill " +
                (consistency.provider_calls_during_rehydrate &&
                MANIFEST_VERIFICATION_PROVIDER_CALLS_DURING_REHYDRATE === 0
                  ? "ok"
                  : "warn")
              }
            >
              <span className="dot" />
              {consistency.provider_calls_during_rehydrate &&
              MANIFEST_VERIFICATION_PROVIDER_CALLS_DURING_REHYDRATE === 0
                ? "yes"
                : "no"}
            </span>
          </dd>
          <dt>no live provider call during rehydrate is true</dt>
          <dd>
            <span
              className={
                "pill " +
                (consistency.no_live_provider_call_during_rehydrate &&
                MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE ===
                  true
                  ? "ok"
                  : "warn")
              }
            >
              <span className="dot" />
              {consistency.no_live_provider_call_during_rehydrate &&
              MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE ===
                true
                ? "yes"
                : "no"}
            </span>
          </dd>
          <dt>manifest consistency verified (all fields)</dt>
          <dd>
            <span
              className={"pill " + (allConsistent ? "ok" : "warn")}
              id="manifest-consistency-pill"
            >
              <span className="dot" />
              {allConsistent ? "verified" : "not verified"}
            </span>
          </dd>
        </dl>
      </div>

      {/* Verified golden values (single source of truth) */}
      <div
        className="manifest-verification-golden"
        id="manifest-verification-golden"
      >
        <h3>Verified golden values</h3>
        <p className="hint">
          Sourced verbatim from{" "}
          <code className="mono">
            docs/evidence/demo/golden-demo-run.json
          </code>{" "}
          (PS-024 golden manifest), itself traced to the PS-021 live B2 durable
          rehydrate smoke. Every cell in the matrix above must equal these
          values.
        </p>
        <dl className="kv">
          <dt>run_id</dt>
          <dd className="mono manifest-golden-run-id">
            {MANIFEST_VERIFICATION_RUN_ID}
          </dd>
          <dt>campaign_id</dt>
          <dd className="mono manifest-golden-campaign-id">
            {MANIFEST_VERIFICATION_CAMPAIGN_ID}
          </dd>
          <dt>archive URI</dt>
          <dd className="mono manifest-golden-archive-uri">
            {MANIFEST_VERIFICATION_ARCHIVE_URI}
          </dd>
          <dt>archive SHA-256</dt>
          <dd className="mono manifest-golden-archive-sha">
            {MANIFEST_VERIFICATION_ARCHIVE_SHA256}
          </dd>
          <dt>rehydrate_source</dt>
          <dd className="mono manifest-golden-rehydrate-source">
            {MANIFEST_VERIFICATION_REHYDRATE_SOURCE}
          </dd>
          <dt>provider_calls_during_rehydrate</dt>
          <dd className="mono manifest-golden-provider-calls">
            {String(MANIFEST_VERIFICATION_PROVIDER_CALLS_DURING_REHYDRATE)}
          </dd>
          <dt>no_live_provider_call_during_rehydrate</dt>
          <dd className="mono manifest-golden-no-live-provider-call">
            {String(
              MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
            )}
          </dd>
        </dl>
      </div>

      {/* Source evidence files */}
      <div className="manifest-verification-files" id="manifest-verification-files">
        <h3>Source evidence files</h3>
        <ul className="infra-points">
          {MANIFEST_VERIFICATION_SOURCES.map((src) => (
            <li key={src.id}>
              <code className="mono">{src.evidencePath}</code>
              <span className="hint muted-link" style={{ marginLeft: 8 }}>
                {src.sliceTag} · {src.label}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Deployment status */}
      <div className="manifest-verification-deployment" id="manifest-verification-deployment">
        <h3>Deployment status</h3>
        <dl className="kv">
          <dt>local contract proof</dt>
          <dd className="mono">
            {String(MANIFEST_VERIFICATION_LOCAL_CONTRACT_PROOF)}
          </dd>
          <dt>public deployment pending</dt>
          <dd className="mono">
            {String(MANIFEST_VERIFICATION_PUBLIC_DEPLOYMENT_PENDING)}
          </dd>
          <dt>unlock scope</dt>
          <dd className="mono">{MANIFEST_VERIFICATION_UNLOCK_SCOPE}</dd>
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
        className="manifest-verification-claim-boundary"
        id="manifest-claim-boundary"
      >
        <h3>Claim boundary</h3>
        <div className="manifest-claim-boundary-grid">
          <div className="manifest-claim-boundary-col">
            <h4>Allowed claims</h4>
            <ul className="infra-points">
              {MANIFEST_CLAIM_BOUNDARY_ALLOWED.map((claim) => (
                <li key={claim}>
                  <span className="pill ok">
                    <span className="dot" />
                    {claim}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div className="manifest-claim-boundary-col">
            <h4>Forbidden claims</h4>
            <ul className="infra-points">
              {MANIFEST_CLAIM_BOUNDARY_FORBIDDEN.map((claim) => (
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
        className="manifest-verification-truth-boundary"
        id="manifest-truth-boundary"
      >
        <h3>Truth boundary</h3>
        <p className="truth-text">{MANIFEST_VERIFICATION_TRUTH_BOUNDARY}</p>
      </section>

      {isPage && (
        <div className="cockpit-cta-row" id="manifest-verification-cta">
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
            href="/genblaze-pipeline"
            title="Open the Genblaze Pipeline Graph (PS-027)"
          >
            Open Genblaze Pipeline Graph
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
            href="/b2-rehydrate-comparison"
            title="Open the B2 Rehydrate Comparison (PS-029)"
          >
            Open B2 Rehydrate Comparison
          </a>
          <a
            className="btn"
            href={"/passport/" + MANIFEST_VERIFICATION_RUN_ID}
            title="Open the verified golden demo Provenance Passport"
          >
            Open Golden Passport
          </a>
          <a
            className="btn"
            href="/failure-timeline"
            title="Open the Failure-as-Proof Timeline (PS-030)"
          >
            Open Failure-as-Proof Timeline
          </a>
          <a className="btn" href="/" title="Back to Judge Cockpit Home">
            Back to Judge Cockpit Home
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
        PS-028 Manifest Verification Panel · fallback API base{" "}
        {DEFAULT_API_BASE_URL} · no provider call, no live B2 read, no broad
        durable read, no browser-side B2 byte verification.
      </p>
    </section>
  );

  if (!isPage) {
    return card;
  }

  return (
    <main className="cockpit manifest-verification-panel-page-wrap">
      <header className="cockpit-hero" id="top">
        <p className="eyebrow">ProofStudio · Manifest Verification Panel</p>
        <h1>Verified manifest consistency across checked-in evidence</h1>
        <p className="thesis">
          One judge-facing view over whether the golden run manifest agrees
          across every checked-in evidence source.
        </p>
        <p className="hero-explainer">
          The Manifest Verification Panel exposes the golden run manifest as a
          cross-source verification table: run_id, campaign_id, archive URI,
          archive SHA-256, rehydrate source (<code className="mono">b2_rehydrated</code>),
          zero provider calls during rehydrate, and the no-live-provider-call
          flag. Every value is sourced verbatim from the checked-in evidence
          (PS-021, PS-024, PS-025, PS-026, PS-027). The panel does not call any
          provider, does not read any B2 object, and does not claim the browser
          fetched and hashed the B2 object.
        </p>
      </header>
      {card}
    </main>
  );
}

function formatValue(value: ManifestFieldValue): string {
  if (typeof value === "boolean") return String(value);
  if (typeof value === "number") return String(value);
  return String(value);
}
