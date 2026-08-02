// PS-034 Lineage + Comparison Lab.
//
// The fourth PS-031A hardened product module after PS-031 / PS-032 / PS-033.
// It merges Model Audition Board, Manifest Diff, Provider Swap Re-run, and
// Variant Family Tree into one lineage / comparison workspace for designers,
// marketers, reviewers, clients, and judges -- not a decorative matrix.
//
// A creative operator can open one lab and answer:
//   - What is the golden run and its artifact lineage?
//   - Which manifest fields prove continuity between manifest and archive?
//   - Is there more than one real variant in checked-in evidence?
//   - Where would future variants / model auditions / provider swaps appear?
//   - How would a provider swap rerun be evaluated later?
//   - Which proof surface should I open next?
//
// All displayed values come from apps/web/src/lineageComparisonLab.ts, which
// is sourced verbatim from the checked-in PS-024 golden manifest, the
// PS-021 / PS-025 / PS-026 / PS-027 / PS-028 / PS-029 / PS-030 / PS-031 /
// PS-032 / PS-033 source evidence, and the PS-031A hardened product module
// correction. The PS-034 smoke validates these constants match the manifest
// and source evidence exactly.
//
// The component also exposes a `variant` prop so the same surface can render
// as a full page (via the /lineage-comparison-lab route in App.tsx) or as an
// inline section inside other judge surfaces. It performs no network call,
// calls no provider, reads no B2 object, and performs no browser-side B2 byte
// verification: it only renders verified, checked-in evidence and documented
// lineage / comparison policy.

import {
  LINEAGE_COMPARISON_LAB_ACTION_ROUTES,
  LINEAGE_COMPARISON_LAB_ARCHIVE_SHA256,
  LINEAGE_COMPARISON_LAB_ARCHIVE_URI,
  LINEAGE_COMPARISON_LAB_AUDITION_SLOT_NOT_RUN,
  LINEAGE_COMPARISON_LAB_CAMPAIGN_ID,
  LINEAGE_COMPARISON_LAB_CLAIM_BOUNDARY_ALLOWED,
  LINEAGE_COMPARISON_LAB_CLAIM_BOUNDARY_FORBIDDEN,
  LINEAGE_COMPARISON_LAB_COMPARISON_READINESS_CHECKLIST,
  LINEAGE_COMPARISON_LAB_DESIGNER_MARKETER_INTERPRETATION,
  LINEAGE_COMPARISON_LAB_GENERATED_FROM,
  LINEAGE_COMPARISON_LAB_ID,
  LINEAGE_COMPARISON_LAB_IMPLEMENTATION_ROADMAP,
  LINEAGE_COMPARISON_LAB_LINEAGE_SUMMARY,
  LINEAGE_COMPARISON_LAB_LOCAL_CONTRACT_PROOF,
  LINEAGE_COMPARISON_LAB_MANIFEST_DIFF,
  LINEAGE_COMPARISON_LAB_MODEL_AUDITION_BOARD,
  LINEAGE_COMPARISON_LAB_NO_PROVIDER_SWAP_LINE,
  LINEAGE_COMPARISON_LAB_NOT_CAPTURED_LABEL,
  LINEAGE_COMPARISON_LAB_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  LINEAGE_COMPARISON_LAB_ONLY_ONE_RUN_LINE,
  LINEAGE_COMPARISON_LAB_PS031A_ROADMAP_CORRECTION,
  LINEAGE_COMPARISON_LAB_PUBLIC_DEPLOYMENT_PENDING,
  LINEAGE_COMPARISON_LAB_PROVIDER_CALLS_DURING_REHYDRATE,
  LINEAGE_COMPARISON_LAB_PROVIDER_SWAP_RERUN_PLANNER,
  LINEAGE_COMPARISON_LAB_REHYDRATE_SOURCE,
  LINEAGE_COMPARISON_LAB_RUN_ID,
  LINEAGE_COMPARISON_LAB_SELECTED_PROVIDER_NOT_CAPTURED,
  LINEAGE_COMPARISON_LAB_SOURCES,
  LINEAGE_COMPARISON_LAB_TRUTH_BOUNDARY,
  LINEAGE_COMPARISON_LAB_LIMITATIONS,
  LINEAGE_COMPARISON_LAB_UNLOCK_SCOPE,
  LINEAGE_COMPARISON_LAB_VARIANT_FAMILY_EDGES,
  LINEAGE_COMPARISON_LAB_VARIANT_FAMILY_NODES,
  LINEAGE_COMPARISON_LAB_VERSION,
  type LineageComparisonLabTruthClass,
} from "./lineageComparisonLab";
import { DEFAULT_API_BASE_URL } from "./api";

type LineageComparisonLabVariant = "page" | "section";

const TRUTH_CLASS_LABEL: Record<
  LineageComparisonLabTruthClass,
  string
> = {
  checked_in_evidence: "checked-in evidence",
  documented_policy: "documented policy",
  planned_not_captured: "planned / not captured",
  not_captured_in_evidence: "not captured in evidence",
  public_deployment_pending: "public deployment pending",
};

const MATCH_STATUS_LABEL: Record<string, string> = {
  match: "match",
  partial: "partial",
  not_captured: "not captured",
};

export function LineageComparisonLab({
  variant = "page",
}: {
  variant?: LineageComparisonLabVariant;
}) {
  const isPage = variant === "page";

  const card = (
    <section
      className={
        isPage
          ? "card col-full lineage-comparison-lab lineage-comparison-lab-page"
          : "card col-full lineage-comparison-lab"
      }
      id="lineage-comparison-lab"
      aria-label="Lineage + Comparison Lab"
    >
      <header className="lineage-comparison-lab-head">
        <span className="infra-tag">Lineage</span>
        <h2>Lineage + Comparison Lab</h2>
      </header>

      <p className="subhead">
        One lineage / comparison workspace over the golden workflow: Model
        Audition Board, Manifest Diff, Provider Swap Re-run, and Variant
        Family Tree. Every value is sourced verbatim from the checked-in
        evidence (PS-021, PS-024, PS-025, PS-026, PS-027, PS-028, PS-029,
        PS-030, PS-031, PS-032, PS-033) plus the PS-031A hardened product
        module correction. Nothing here is invented, nothing here is fetched
        live from B2, and no provider is called. ProofStudio shows lineage and
        comparison honestly, it does not fabricate variants.
      </p>

      {/* 1. Lab Identity */}
      <div
        className="lineage-comparison-lab-section lineage-comparison-lab-identity"
        id="lineage-comparison-lab-identity"
        data-section-key="lab_identity"
      >
        <h3>Lab Identity</h3>
        <dl className="kv">
          <dt>surface</dt>
          <dd className="mono lineage-comparison-lab-surface-name">
            Lineage + Comparison Lab
          </dd>
          <dt>merged panels</dt>
          <dd className="mono lineage-comparison-lab-panels">
            Model Audition Board · Manifest Diff · Provider Swap Re-run ·
            Variant Family Tree
          </dd>
          <dt>slice</dt>
          <dd className="mono lineage-comparison-lab-slice">PS-034</dd>
          <dt>lab_id</dt>
          <dd className="mono lineage-comparison-lab-lab-id">
            {LINEAGE_COMPARISON_LAB_ID}
          </dd>
          <dt>lab_version</dt>
          <dd className="mono lineage-comparison-lab-lab-version">
            {LINEAGE_COMPARISON_LAB_VERSION}
          </dd>
          <dt>run_id</dt>
          <dd className="mono lineage-comparison-lab-run-id">
            {LINEAGE_COMPARISON_LAB_RUN_ID}
          </dd>
          <dt>campaign_id</dt>
          <dd className="mono lineage-comparison-lab-campaign-id">
            {LINEAGE_COMPARISON_LAB_CAMPAIGN_ID}
          </dd>
          <dt>public deployment</dt>
          <dd className="mono lineage-comparison-lab-public-deployment-pending">
            {String(LINEAGE_COMPARISON_LAB_PUBLIC_DEPLOYMENT_PENDING)}
          </dd>
        </dl>
      </div>

      {/* 2. Lineage Summary */}
      <div
        className="lineage-comparison-lab-section"
        id="lineage-comparison-lab-lineage-summary"
        data-section-key="lineage_summary"
      >
        <h3>Lineage Summary</h3>
        <p className="hint">
          A compact lineage summary: campaign identity, golden run identity,
          archive / manifest / rehydrate / passport / evidence pack status,
          comparison readiness, variant family status, and provider swap
          status.
        </p>
        <p className="lineage-comparison-lab-only-one-run">
          <span
            className="failure-as-proof-line"
            data-mandate="only_one_verified_run"
          >
            {LINEAGE_COMPARISON_LAB_ONLY_ONE_RUN_LINE}
          </span>
        </p>
        <ul className="infra-points lineage-comparison-lab-summary-list">
          {LINEAGE_COMPARISON_LAB_LINEAGE_SUMMARY.map((item) => (
            <li
              key={item.key}
              className="lineage-comparison-lab-summary-item"
              data-summary-key={item.key}
              data-truth-class={item.truthClass}
            >
              <div className="lineage-comparison-lab-summary-head">
                <span className="lineage-comparison-lab-summary-label">
                  {item.label}
                </span>
                <span className="pill ok">
                  <span className="dot" />
                  {item.value}
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
      </div>

      {/* 3. Variant Family Tree */}
      <div
        className="lineage-comparison-lab-section"
        id="lineage-comparison-lab-variant-family-tree"
        data-section-key="variant_family_tree"
      >
        <h3>Variant Family Tree</h3>
        <p className="hint">
          A card / tree layout over the verified lineage. Captured nodes show
          their identity; future variant slots are honestly labeled.
        </p>
        <div className="lineage-comparison-lab-tree-grid">
          {LINEAGE_COMPARISON_LAB_VARIANT_FAMILY_NODES.map((node) => (
            <article
              key={node.key}
              className="lineage-comparison-lab-tree-node"
              data-node-kind={node.kind}
              data-captured={node.captured ? "true" : "false"}
            >
              <h4 className="lineage-comparison-lab-tree-node-label">
                {node.label}
              </h4>
              <span
                className={
                  "pill " + (node.captured ? "ok" : "warn")
                }
              >
                <span className="dot" />
                {node.captured ? "captured" : "future variant slot"}
              </span>
              {node.identity && (
                <p className="mono hint">{node.identity}</p>
              )}
              <p className="hint">{node.note}</p>
            </article>
          ))}
        </div>
        <h4 className="lineage-comparison-lab-relationships-head">
          Relationships
        </h4>
        <ul className="infra-points lineage-comparison-lab-relationships">
          {LINEAGE_COMPARISON_LAB_VARIANT_FAMILY_EDGES.map((edge) => {
            const fromNode = LINEAGE_COMPARISON_LAB_VARIANT_FAMILY_NODES.find(
              (n) => n.key === edge.fromKey,
            );
            const toNode = LINEAGE_COMPARISON_LAB_VARIANT_FAMILY_NODES.find(
              (n) => n.key === edge.toKey,
            );
            return (
              <li
                key={edge.key}
                className="lineage-comparison-lab-relationship"
                data-edge-label={edge.label}
              >
                <span className="mono">{fromNode?.label ?? edge.fromKey}</span>
                <span className="lineage-comparison-lab-edge-label">
                  — {edge.label} →
                </span>
                <span className="mono">{toNode?.label ?? edge.toKey}</span>
              </li>
            );
          })}
        </ul>
      </div>

      {/* 4. Manifest Diff */}
      <div
        className="lineage-comparison-lab-section"
        id="lineage-comparison-lab-manifest-diff"
        data-section-key="manifest_diff"
      >
        <h3>Manifest Diff</h3>
        <p className="hint">
          Each field carries a left / source value, a right / comparison value,
          a match status, an evidence source, and a truth class. If a field
          cannot be compared because one side is not captured, the row shows
          <code className="mono"> {LINEAGE_COMPARISON_LAB_NOT_CAPTURED_LABEL}</code>.
          No missing manifest field is invented.
        </p>
        <div className="table-wrap lineage-comparison-lab-diff-wrap">
          <table className="timeline lineage-comparison-lab-diff-table">
            <thead>
              <tr>
                <th>field</th>
                <th>left / source value</th>
                <th>right / comparison value</th>
                <th>match status</th>
                <th>evidence source</th>
                <th>truth class</th>
              </tr>
            </thead>
            <tbody>
              {LINEAGE_COMPARISON_LAB_MANIFEST_DIFF.map((row) => (
                <tr
                  key={row.key}
                  data-diff-key={row.key}
                  data-match-status={row.matchStatus}
                  data-truth-class={row.truthClass}
                >
                  <td className="mono">{row.field}</td>
                  <td className="mono lineage-comparison-lab-diff-left">
                    {row.leftValue}
                  </td>
                  <td className="mono lineage-comparison-lab-diff-right">
                    {row.rightValue}
                  </td>
                  <td>
                    <span
                      className={
                        "pill " +
                        (row.matchStatus === "match"
                          ? "ok"
                          : row.matchStatus === "not_captured"
                            ? "warn"
                            : "info")
                      }
                    >
                      <span className="dot" />
                      {MATCH_STATUS_LABEL[row.matchStatus] ?? row.matchStatus}
                    </span>
                  </td>
                  <td>{row.evidenceSource}</td>
                  <td>
                    <span className="pill info">
                      <span className="dot" />
                      {TRUTH_CLASS_LABEL[row.truthClass]}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Model Audition Board */}
      <div
        className="lineage-comparison-lab-section"
        id="lineage-comparison-lab-model-audition-board"
        data-section-key="model_audition_board"
      >
        <h3>Model Audition Board</h3>
        <p className="hint">
          Shows how multiple model candidates would be compared. The golden run
          candidate discloses that the selected provider / model is not
          captured. Future slots are honestly marked as not run. No model
          scores, quality scores, cost scores, or winner labels are invented.
        </p>
        <div className="table-wrap lineage-comparison-lab-audition-wrap">
          <table className="timeline lineage-comparison-lab-audition-table">
            <thead>
              <tr>
                <th>candidate</th>
                <th>provider / model role</th>
                <th>modality</th>
                <th>evidence status</th>
                <th>quality review status</th>
                <th>cost / time status</th>
                <th>proof status</th>
                <th>decision</th>
              </tr>
            </thead>
            <tbody>
              {LINEAGE_COMPARISON_LAB_MODEL_AUDITION_BOARD.map((row) => (
                <tr
                  key={row.key}
                  data-audition-key={row.key}
                  data-truth-class={row.truthClass}
                >
                  <td className="mono">{row.candidate}</td>
                  <td className="mono lineage-comparison-lab-audition-role">
                    {row.providerModelRole}
                  </td>
                  <td className="mono">{row.modality}</td>
                  <td>{row.evidenceStatus}</td>
                  <td>{row.qualityReviewStatus}</td>
                  <td>{row.costTimeStatus}</td>
                  <td>{row.proofStatus}</td>
                  <td>{row.decision}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="hint lineage-comparison-lab-audition-foot">
          Golden run candidate:
          <code className="mono">
            {" "}
            {LINEAGE_COMPARISON_LAB_SELECTED_PROVIDER_NOT_CAPTURED}
          </code>
          . Future slots:
          <code className="mono"> {LINEAGE_COMPARISON_LAB_AUDITION_SLOT_NOT_RUN}</code>.
        </p>
      </div>

      {/* 6. Provider Swap Re-run Planner */}
      <div
        className="lineage-comparison-lab-section"
        id="lineage-comparison-lab-provider-swap-planner"
        data-section-key="provider_swap_rerun_planner"
      >
        <h3>Provider Swap Re-run Planner</h3>
        <p className="hint">
          A planner (documented policy steps) for rerunning the same brief with
          a different provider. This is a planner, not an executed rerun.
        </p>
        <ol className="infra-points lineage-comparison-lab-swap-steps">
          {LINEAGE_COMPARISON_LAB_PROVIDER_SWAP_RERUN_PLANNER.map((step) => (
            <li
              key={step.key}
              className="lineage-comparison-lab-swap-step"
              data-swap-key={step.key}
              data-truth-class={step.truthClass}
            >
              <div className="lineage-comparison-lab-swap-step-head">
                <span className="lineage-comparison-lab-swap-step-order">
                  {step.order}. {step.step}
                </span>
                <span className="pill info">
                  <span className="dot" />
                  {TRUTH_CLASS_LABEL[step.truthClass]}
                </span>
              </div>
              <p className="hint">{step.detail}</p>
            </li>
          ))}
        </ol>
        <p className="lineage-comparison-lab-swap-no-claim">
          <span
            className="failure-as-proof-line"
            data-mandate="no_provider_swap_rerun"
          >
            {LINEAGE_COMPARISON_LAB_NO_PROVIDER_SWAP_LINE}
          </span>
        </p>
      </div>

      {/* 7. Comparison Readiness Checklist */}
      <div
        className="lineage-comparison-lab-section"
        id="lineage-comparison-lab-readiness-checklist"
        data-section-key="comparison_readiness_checklist"
      >
        <h3>Comparison Readiness Checklist</h3>
        <p className="hint">
          Whether the system has enough evidence to compare variants. Missing
          items are marked honestly.
        </p>
        <ul className="infra-points lineage-comparison-lab-checklist">
          {LINEAGE_COMPARISON_LAB_COMPARISON_READINESS_CHECKLIST.map((item) => (
            <li
              key={item.key}
              className="lineage-comparison-lab-checklist-item"
              data-checklist-key={item.key}
              data-present={item.present ? "true" : "false"}
            >
              <div className="lineage-comparison-lab-checklist-head">
                <span
                  className={
                    "pill " + (item.present ? "ok" : "warn")
                  }
                >
                  <span className="dot" />
                  {item.present ? "present" : "missing"}
                </span>
                <span className="lineage-comparison-lab-checklist-label">
                  {item.label}
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
      </div>

      {/* 8. Designer / Marketer Interpretation */}
      <div
        className="lineage-comparison-lab-section"
        id="lineage-comparison-lab-designer-marketer"
        data-section-key="designer_marketer_interpretation"
      >
        <h3>Designer / Marketer Interpretation</h3>
        <dl className="kv lineage-comparison-lab-designer-kv">
          <dt>why lineage matters</dt>
          <dd>
            {LINEAGE_COMPARISON_LAB_DESIGNER_MARKETER_INTERPRETATION.whyLineageMatters}
          </dd>
          <dt>why comparing variants helps campaigns</dt>
          <dd>
            {LINEAGE_COMPARISON_LAB_DESIGNER_MARKETER_INTERPRETATION.whyComparingVariantsHelpsCampaigns}
          </dd>
          <dt>why manifest diff matters</dt>
          <dd>
            {LINEAGE_COMPARISON_LAB_DESIGNER_MARKETER_INTERPRETATION.whyManifestDiffMatters}
          </dd>
          <dt>how provider swaps help creative teams</dt>
          <dd>
            {LINEAGE_COMPARISON_LAB_DESIGNER_MARKETER_INTERPRETATION.howProviderSwapsHelpCreativeTeams}
          </dd>
          <dt>when to rerun with another model</dt>
          <dd>
            {LINEAGE_COMPARISON_LAB_DESIGNER_MARKETER_INTERPRETATION.whenToRerunWithAnotherModel}
          </dd>
          <dt>when to export the evidence pack</dt>
          <dd>
            {LINEAGE_COMPARISON_LAB_DESIGNER_MARKETER_INTERPRETATION.whenToExportTheEvidencePack}
          </dd>
          <dt>why missing variant data is not a failure</dt>
          <dd>
            {LINEAGE_COMPARISON_LAB_DESIGNER_MARKETER_INTERPRETATION.whyMissingVariantDataIsNotAFailure}
          </dd>
        </dl>
      </div>

      {/* 9. Action Rail */}
      <div
        className="lineage-comparison-lab-section lineage-comparison-lab-action-rail"
        id="lineage-comparison-lab-action-rail"
        data-section-key="action_rail"
      >
        <h3>Action Rail</h3>
        <p className="hint">
          Jump to any implemented proof surface from this lineage / comparison
          workspace.
        </p>
        <ul className="infra-points lineage-comparison-lab-action-list">
          {LINEAGE_COMPARISON_LAB_ACTION_ROUTES.map((route) => (
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

      {/* 10. Truth Boundary */}
      <section
        className="lineage-comparison-lab-section lineage-comparison-lab-truth-boundary"
        id="lineage-comparison-lab-truth-boundary"
        data-section-key="truth_boundary"
      >
        <h3>Truth Boundary</h3>
        <p className="truth-text">{LINEAGE_COMPARISON_LAB_TRUTH_BOUNDARY}</p>
        <div className="lineage-comparison-lab-claim-boundary-grid">
          <div className="lineage-comparison-lab-claim-boundary-col">
            <h4>Allowed claims</h4>
            <ul className="infra-points">
              {LINEAGE_COMPARISON_LAB_CLAIM_BOUNDARY_ALLOWED.map((claim) => (
                <li key={claim}>
                  <span className="pill ok">
                    <span className="dot" />
                    {claim}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div className="lineage-comparison-lab-claim-boundary-col">
            <h4>Forbidden claims</h4>
            <ul className="infra-points">
              {LINEAGE_COMPARISON_LAB_CLAIM_BOUNDARY_FORBIDDEN.map((claim) => (
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

      {/* 11. Limitations */}
      <div
        className="lineage-comparison-lab-section"
        id="lineage-comparison-lab-limitations"
        data-section-key="limitations"
      >
        <h3>Limitations</h3>
        <ul className="infra-points lineage-comparison-lab-limitations-points">
          {LINEAGE_COMPARISON_LAB_LIMITATIONS.map((lim) => (
            <li key={lim}>{lim}</li>
          ))}
        </ul>
      </div>

      {/* Source evidence files */}
      <div
        className="lineage-comparison-lab-section lineage-comparison-lab-files"
        id="lineage-comparison-lab-files"
      >
        <h3>Source evidence files</h3>
        <ul className="infra-points">
          {LINEAGE_COMPARISON_LAB_SOURCES.map((src) => (
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
          <code className="mono">
            {LINEAGE_COMPARISON_LAB_IMPLEMENTATION_ROADMAP}
          </code>
        </p>
        <p className="hint muted-link">
          hardened module correction:{" "}
          <code className="mono">
            {LINEAGE_COMPARISON_LAB_PS031A_ROADMAP_CORRECTION}
          </code>
        </p>
      </div>

      {/* Deployment status */}
      <div
        className="lineage-comparison-lab-section lineage-comparison-lab-deployment"
        id="lineage-comparison-lab-deployment"
      >
        <h3>Deployment status</h3>
        <dl className="kv">
          <dt>local contract proof</dt>
          <dd className="mono">
            {String(LINEAGE_COMPARISON_LAB_LOCAL_CONTRACT_PROOF)}
          </dd>
          <dt>public deployment pending</dt>
          <dd className="mono">
            {String(LINEAGE_COMPARISON_LAB_PUBLIC_DEPLOYMENT_PENDING)}
          </dd>
          <dt>unlock scope</dt>
          <dd className="mono">{LINEAGE_COMPARISON_LAB_UNLOCK_SCOPE}</dd>
          <dt>rehydrate_source</dt>
          <dd className="mono">
            {LINEAGE_COMPARISON_LAB_REHYDRATE_SOURCE}
          </dd>
          <dt>provider_calls_during_rehydrate</dt>
          <dd className="mono">
            {String(LINEAGE_COMPARISON_LAB_PROVIDER_CALLS_DURING_REHYDRATE)}
          </dd>
          <dt>no_live_provider_call_during_rehydrate</dt>
          <dd className="mono">
            {String(
              LINEAGE_COMPARISON_LAB_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
            )}
          </dd>
        </dl>
        <p className="hint">
          The local contract (FastAPI TestClient resolving the golden run_id
          from checked-in evidence) is verified by PS-025. The public Render
          deployment is not verified yet: the new backend must be deployed and
          the public URL verified end-to-end before this status changes.
        </p>
      </div>

      {isPage && (
        <div
          className="cockpit-cta-row"
          id="lineage-comparison-lab-cta"
        >
          <a className="btn btn-primary" href="/provider-decision-intelligence">
            Open Provider Decision Intelligence
          </a>
          <a className="btn" href="/operations-cockpit">
            Open Operations Cockpit
          </a>
          <a className="btn" href="/evidence-pack">
            Open Judge Evidence Pack
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
            href={"/passport/" + LINEAGE_COMPARISON_LAB_RUN_ID}
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
        PS-034 Lineage + Comparison Lab · generated from{" "}
        {LINEAGE_COMPARISON_LAB_GENERATED_FROM} · fallback API base{" "}
        {DEFAULT_API_BASE_URL} · no provider call, no live B2 read, no broad
        durable read, no browser-side B2 byte verification, no raw media byte
        inspection, no invented variant, no provider swap rerun claim.
      </p>
      <p className="hint muted-link">
        archive_uri:{" "}
        <code className="mono">{LINEAGE_COMPARISON_LAB_ARCHIVE_URI}</code> ·
        archive_sha256:{" "}
        <code className="mono">{LINEAGE_COMPARISON_LAB_ARCHIVE_SHA256}</code>
      </p>
    </section>
  );

  if (!isPage) {
    return card;
  }

  return (
    <main className="cockpit lineage-comparison-lab-page-wrap">
      <header className="cockpit-hero" id="top">
        <p className="eyebrow">ProofStudio · Lineage + Comparison Lab</p>
        <h1>Compare candidates, variants, and provider swaps in one lab</h1>
        <p className="thesis">
          One lineage / comparison workspace: Model Audition Board, Manifest
          Diff, Provider Swap Re-run, Variant Family Tree.
        </p>
        <p className="hero-explainer">
          The Lineage + Comparison Lab merges Model Audition Board, Manifest
          Diff, Provider Swap Re-run, and Variant Family Tree into one
          hardened product module (PS-031A). It shows the verified lineage of
          the golden run (campaign, run, asset / manifest, B2 archive,
          rehydrated evidence, public passport, judge evidence pack, review /
          next action), compares known manifest / proof fields against the
          rehydrated archive proof, discloses that only one verified golden
          run is available, marks future variant and audition slots honestly,
          and documents the provider swap rerun planner as policy only. Every
          value is sourced verbatim from the checked-in evidence (PS-021,
          PS-024, PS-025, PS-026, PS-027, PS-028, PS-029, PS-030, PS-031,
          PS-032, PS-033). It does not call any provider, does not read any B2
          object, and does not claim the browser fetched and hashed the B2
          object. No fake variant, model score, winner label, or provider swap
          rerun is claimed.
        </p>
      </header>
      {card}
    </main>
  );
}
