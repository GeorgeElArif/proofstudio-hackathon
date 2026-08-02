// PS-029 B2 Rehydrate Comparison.
//
// A dedicated, judge-facing product surface that exposes the B2 rehydrate
// value as a before/after comparison. It tells the rehydrate story across
// four columns:
//
//   1. Golden run / manifest      (what was pinned -- PS-024)
//   2. B2 archive evidence        (what was stored -- PS-021 / PS-026)
//   3. Rehydrated evidence        (what came back -- PS-025 / PS-027)
//   4. Rehydrate result           (the verdict -- PS-028 cross-source)
//
// The comparison cross-references six checked-in evidence sources and shows
// whether every required field agrees across all sources, and -- crucially --
// that the rehydrate used durable B2 archive evidence instead of a live
// provider rerun (provider_calls_during_rehydrate = 0,
// no_live_provider_call_during_rehydrate = true).
//
// All displayed values come from apps/web/src/b2RehydrateComparison.ts, which
// is sourced verbatim from the checked-in PS-024 golden demo manifest and the
// PS-021 / PS-025 / PS-026 / PS-027 / PS-028 source evidence. The PS-029
// smoke validates these constants match the manifest and source evidence
// exactly.
//
// The component also exposes a `variant` prop so the same surface can render
// as a full page (via the /b2-rehydrate-comparison route in App.tsx) or as an
// inline section inside other judge surfaces. It performs no network call,
// calls no provider, and reads no B2 object: it only renders verified,
// checked-in evidence.

import {
  B2_REHYDRATE_CLAIM_BOUNDARY_ALLOWED,
  B2_REHYDRATE_CLAIM_BOUNDARY_FORBIDDEN,
  B2_REHYDRATE_COMPARISON_ARCHIVE_SHA256,
  B2_REHYDRATE_COMPARISON_ARCHIVE_URI,
  B2_REHYDRATE_COMPARISON_CAMPAIGN_ID,
  B2_REHYDRATE_COMPARISON_COLUMNS,
  B2_REHYDRATE_COMPARISON_FIELDS,
  B2_REHYDRATE_COMPARISON_LOCAL_CONTRACT_PROOF,
  B2_REHYDRATE_COMPARISON_MATRIX,
  B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  B2_REHYDRATE_COMPARISON_PUBLIC_DEPLOYMENT_PENDING,
  B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE,
  B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE,
  B2_REHYDRATE_COMPARISON_RUN_ID,
  B2_REHYDRATE_COMPARISON_SOURCES,
  B2_REHYDRATE_COMPARISON_TRUTH_BOUNDARY,
  B2_REHYDRATE_COMPARISON_UNLOCK_SCOPE,
  B2_REHYDRATE_NO_PROVIDER_RERUN_STORY,
  type B2RehydrateComparisonFieldKey,
  type B2RehydrateComparisonFieldValue,
} from "./b2RehydrateComparison";
import { DEFAULT_API_BASE_URL } from "./api";
import { TrustBoundaryLayer } from "./TrustBoundaryLayer";
import { MultimodalProofLayer } from "./MultimodalProofLayer";
import { TranscriptTimestampEvidenceLayer } from "./TranscriptTimestampEvidenceLayer";
import { CampaignIntelligenceJudgeNarrativeLayer } from "./CampaignIntelligenceJudgeNarrativeLayer";
import { CloudflareLowCostBackboneLayer } from "./CloudflareLowCostBackboneLayer";
import { ProductionReadinessDemoModeLayer } from "./ProductionReadinessDemoModeLayer";
import { VoiceAudioEvidenceChoiceLayer } from "./VoiceAudioEvidenceChoiceLayer";

type B2RehydrateComparisonVariant = "page" | "section";

export function B2RehydrateComparison({
  variant = "page",
}: {
  variant?: B2RehydrateComparisonVariant;
}) {
  const isPage = variant === "page";

  // Compute field-level consistency across all sources. A field is consistent
  // only when every source records the same value for it. The matrix is
  // sourced verbatim from checked-in evidence; this check is purely a
  // presentation-level cross-reference, never an overclaim.
  const consistency: Record<B2RehydrateComparisonFieldKey, boolean> =
    Object.fromEntries(
      B2_REHYDRATE_COMPARISON_FIELDS.map((f) => [
        f.key,
        B2_REHYDRATE_COMPARISON_SOURCES.every((src) => {
          const cell = B2_REHYDRATE_COMPARISON_MATRIX[src.id]?.[f.key];
          return cell !== undefined && cell === f.value;
        }),
      ]),
    ) as Record<B2RehydrateComparisonFieldKey, boolean>;

  const allConsistent = B2_REHYDRATE_COMPARISON_FIELDS.every(
    (f) => consistency[f.key],
  );

  const card = (
    <section
      className={
        isPage
          ? "card col-full b2-rehydrate-comparison b2-rehydrate-comparison-page"
          : "card col-full b2-rehydrate-comparison"
      }
      id="b2-rehydrate-comparison"
      aria-label="B2 Rehydrate Comparison"
    >
      <header className="b2-rehydrate-comparison-head">
        <span className="infra-tag">Backblaze B2</span>
        <h2>B2 Rehydrate Comparison</h2>
      </header>

      <p className="subhead">
        One canonical judge-facing view over the B2 rehydrate value: what was
        pinned, what was stored in B2, what came back from rehydrate, and the
        rehydrate result. Every value below is sourced verbatim from the
        checked-in evidence (PS-021, PS-024, PS-025, PS-026, PS-027, PS-028).
        Nothing here is invented, nothing here is fetched live from B2, and
        no provider is called.
      </p>

      {/* Comparison columns: the before/after rehydrate story */}
      <div
        className="b2-rehydrate-comparison-columns"
        id="b2-rehydrate-comparison-columns"
      >
        <h3>Comparison columns</h3>
        <p className="hint">
          The rehydrate story told as four columns. Each column maps to one or
          more checked-in evidence sources.
        </p>
        <div className="b2-rehydrate-comparison-columns-grid">
          {B2_REHYDRATE_COMPARISON_COLUMNS.map((col, i) => (
            <article
              key={col.id}
              className={`b2-rehydrate-comparison-column col-${col.id}`}
              data-column-id={col.id}
            >
              <header>
                <span className="b2-rehydrate-column-idx">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div>
                  <h4>{col.title}</h4>
                  <span className="b2-rehydrate-column-tag">{col.tag}</span>
                </div>
              </header>
              <p>{col.story}</p>
              <p className="hint muted-link">
                sources:{" "}
                {col.sourceIds
                  .map((sid) => {
                    const src = B2_REHYDRATE_COMPARISON_SOURCES.find(
                      (s) => s.id === sid,
                    );
                    return src ? src.sliceTag : sid;
                  })
                  .join(" / ")}
              </p>
            </article>
          ))}
        </div>
      </div>

      {/* No-provider-rerun story */}
      <div
        className="b2-rehydrate-comparison-no-rerun"
        id="b2-rehydrate-comparison-no-rerun"
      >
        <h3>No live provider rerun required for rehydrate</h3>
        <p className="b2-rehydrate-no-rerun-story">
          {B2_REHYDRATE_NO_PROVIDER_RERUN_STORY}
        </p>
        <dl className="kv">
          <dt>rehydrate_source</dt>
          <dd className="mono b2-rehydrate-rehydrate-source">
            {B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE}
          </dd>
          <dt>provider_calls_during_rehydrate</dt>
          <dd className="mono b2-rehydrate-provider-calls">
            {String(B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE)}
          </dd>
          <dt>no_live_provider_call_during_rehydrate</dt>
          <dd className="mono b2-rehydrate-no-live-provider-call">
            {String(
              B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
            )}
          </dd>
        </dl>
      </div>

      {/* Cross-source comparison matrix */}
      <div
        className="b2-rehydrate-comparison-matrix-wrap"
        id="b2-rehydrate-comparison-matrix"
      >
        <h3>Cross-source comparison matrix</h3>
        <p className="hint">
          Rows are required comparison fields. Columns are the six checked-in
          evidence sources. The rightmost column records whether every source
          agrees on that field.
        </p>
        <div className="table-wrap">
          <table className="b2-rehydrate-comparison-table">
            <thead>
              <tr>
                <th scope="col">Field</th>
                {B2_REHYDRATE_COMPARISON_SOURCES.map((src) => (
                  <th key={src.id} scope="col">
                    <span className="b2-rehydrate-source-tag">
                      {src.sliceTag}
                    </span>
                    <span className="b2-rehydrate-source-label">
                      {src.label}
                    </span>
                  </th>
                ))}
                <th scope="col">Consistent</th>
              </tr>
            </thead>
            <tbody>
              {B2_REHYDRATE_COMPARISON_FIELDS.map((field) => {
                const ok = consistency[field.key];
                return (
                  <tr
                    key={field.key}
                    className={`b2-rehydrate-field-row ${
                      ok ? "row-consistent" : "row-inconsistent"
                    }`}
                    data-field-key={field.key}
                  >
                    <th scope="row">
                      <code className="mono b2-rehydrate-field-label">
                        {field.label}
                      </code>
                    </th>
                    {B2_REHYDRATE_COMPARISON_SOURCES.map((src) => {
                      const cell =
                        B2_REHYDRATE_COMPARISON_MATRIX[src.id]?.[field.key];
                      const cellMatches =
                        cell !== undefined && cell === field.value;
                      return (
                        <td
                          key={src.id}
                          className={
                            "mono b2-rehydrate-cell " +
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

      {/* Rehydrate result summary */}
      <div
        className="b2-rehydrate-comparison-summary"
        id="b2-rehydrate-comparison-summary"
      >
        <h3>Rehydrate result summary</h3>
        <dl className="kv">
          <dt>same run_id</dt>
          <dd>
            <span
              className={"pill " + (consistency.run_id ? "ok" : "warn")}
            >
              <span className="dot" />
              {consistency.run_id ? "yes" : "no"}
            </span>
          </dd>
          <dt>same campaign_id</dt>
          <dd>
            <span
              className={
                "pill " + (consistency.campaign_id ? "ok" : "warn")
              }
            >
              <span className="dot" />
              {consistency.campaign_id ? "yes" : "no"}
            </span>
          </dd>
          <dt>same archive URI</dt>
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
          <dt>same archive SHA-256</dt>
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
          <dt>rehydrate_source is b2_rehydrated</dt>
          <dd>
            <span
              className={
                "pill " +
                (consistency.rehydrate_source &&
                B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE === "b2_rehydrated"
                  ? "ok"
                  : "warn")
              }
            >
              <span className="dot" />
              {consistency.rehydrate_source &&
              B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE === "b2_rehydrated"
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
                B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE === 0
                  ? "ok"
                  : "warn")
              }
            >
              <span className="dot" />
              {consistency.provider_calls_during_rehydrate &&
              B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE === 0
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
                B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE ===
                  true
                  ? "ok"
                  : "warn")
              }
            >
              <span className="dot" />
              {consistency.no_live_provider_call_during_rehydrate &&
              B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE ===
                true
                ? "yes"
                : "no"}
            </span>
          </dd>
          <dt>no live provider rerun required for rehydrate</dt>
          <dd>
            <span
              id="b2-rehydrate-no-rerun-pill"
              className={"pill " + (allConsistent ? "ok" : "warn")}
            >
              <span className="dot" />
              {allConsistent ? "yes" : "no"}
            </span>
          </dd>
          <dt>rehydrate comparison verified (all fields)</dt>
          <dd>
            <span
              className={"pill " + (allConsistent ? "ok" : "warn")}
              id="b2-rehydrate-comparison-pill"
            >
              <span className="dot" />
              {allConsistent ? "verified" : "not verified"}
            </span>
          </dd>
        </dl>
      </div>

      {/* Verified golden values (single source of truth) */}
      <div
        className="b2-rehydrate-comparison-golden"
        id="b2-rehydrate-comparison-golden"
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
          <dd className="mono b2-rehydrate-golden-run-id">
            {B2_REHYDRATE_COMPARISON_RUN_ID}
          </dd>
          <dt>campaign_id</dt>
          <dd className="mono b2-rehydrate-golden-campaign-id">
            {B2_REHYDRATE_COMPARISON_CAMPAIGN_ID}
          </dd>
          <dt>archive URI</dt>
          <dd className="mono b2-rehydrate-golden-archive-uri">
            {B2_REHYDRATE_COMPARISON_ARCHIVE_URI}
          </dd>
          <dt>archive SHA-256</dt>
          <dd className="mono b2-rehydrate-golden-archive-sha">
            {B2_REHYDRATE_COMPARISON_ARCHIVE_SHA256}
          </dd>
          <dt>rehydrate_source</dt>
          <dd className="mono b2-rehydrate-golden-rehydrate-source">
            {B2_REHYDRATE_COMPARISON_REHYDRATE_SOURCE}
          </dd>
          <dt>provider_calls_during_rehydrate</dt>
          <dd className="mono b2-rehydrate-golden-provider-calls">
            {String(B2_REHYDRATE_COMPARISON_PROVIDER_CALLS_DURING_REHYDRATE)}
          </dd>
          <dt>no_live_provider_call_during_rehydrate</dt>
          <dd className="mono b2-rehydrate-golden-no-live-provider-call">
            {String(
              B2_REHYDRATE_COMPARISON_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
            )}
          </dd>
        </dl>
      </div>

      {/* Source evidence files */}
      <div
        className="b2-rehydrate-comparison-files"
        id="b2-rehydrate-comparison-files"
      >
        <h3>Source evidence files</h3>
        <ul className="infra-points">
          {B2_REHYDRATE_COMPARISON_SOURCES.map((src) => (
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
      <div
        className="b2-rehydrate-comparison-deployment"
        id="b2-rehydrate-comparison-deployment"
      >
        <h3>Deployment status</h3>
        <dl className="kv">
          <dt>local contract proof</dt>
          <dd className="mono">
            {String(B2_REHYDRATE_COMPARISON_LOCAL_CONTRACT_PROOF)}
          </dd>
          <dt>public deployment pending</dt>
          <dd className="mono">
            {String(B2_REHYDRATE_COMPARISON_PUBLIC_DEPLOYMENT_PENDING)}
          </dd>
          <dt>unlock scope</dt>
          <dd className="mono">
            {B2_REHYDRATE_COMPARISON_UNLOCK_SCOPE}
          </dd>
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
        className="b2-rehydrate-comparison-claim-boundary"
        id="b2-rehydrate-claim-boundary"
      >
        <h3>Claim boundary</h3>
        <div className="b2-rehydrate-claim-boundary-grid">
          <div className="b2-rehydrate-claim-boundary-col">
            <h4>Allowed claims</h4>
            <ul className="infra-points">
              {B2_REHYDRATE_CLAIM_BOUNDARY_ALLOWED.map((claim) => (
                <li key={claim}>
                  <span className="pill ok">
                    <span className="dot" />
                    {claim}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div className="b2-rehydrate-claim-boundary-col">
            <h4>Forbidden claims</h4>
            <ul className="infra-points">
              {B2_REHYDRATE_CLAIM_BOUNDARY_FORBIDDEN.map((claim) => (
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
        className="b2-rehydrate-comparison-truth-boundary"
        id="b2-rehydrate-truth-boundary"
      >
        <h3>Truth boundary</h3>
        <p className="truth-text">
          {B2_REHYDRATE_COMPARISON_TRUTH_BOUNDARY}
        </p>
      </section>

      {isPage && (
        <div className="cockpit-cta-row" id="b2-rehydrate-comparison-cta">
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
            href={"/passport/" + B2_REHYDRATE_COMPARISON_RUN_ID}
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
        PS-029 B2 Rehydrate Comparison · fallback API base{" "}
        {DEFAULT_API_BASE_URL} · no provider call, no live B2 read, no broad
        durable read, no browser-side B2 byte verification.
      </p>
    </section>
  );

  if (!isPage) {
    return card;
  }

  return (
    <main className="cockpit b2-rehydrate-comparison-page-wrap">
      <header className="cockpit-hero" id="top">
        <p className="eyebrow">ProofStudio · B2 Rehydrate Comparison</p>
        <h1>B2 rehydrate value, compared across checked-in evidence</h1>
        <p className="thesis">
          One judge-facing view over what was archived, what was rehydrated,
          and why no live provider rerun was required.
        </p>
        <p className="hero-explainer">
          The B2 Rehydrate Comparison exposes the rehydrate value as a
          before/after story: golden run / manifest → B2 archive evidence →
          rehydrated evidence → rehydrate result. Every value is sourced
          verbatim from the checked-in evidence (PS-021, PS-024, PS-025,
          PS-026, PS-027, PS-028). The comparison records{" "}
          <code className="mono">rehydrate_source = b2_rehydrated</code>, zero
          provider calls during rehydrate, and the no-live-provider-call flag.
          It does not call any provider, does not read any B2 object, and does
          not claim the browser fetched and hashed the B2 object.
        </p>
      </header>
      {card}
    </main>
  );
}

function formatValue(value: B2RehydrateComparisonFieldValue): string {
  if (typeof value === "boolean") return String(value);
  if (typeof value === "number") return String(value);
  return String(value);
}
