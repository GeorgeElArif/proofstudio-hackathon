// PS-033 Provider Decision Intelligence.
//
// The second PS-031A hardened product module after PS-032. It merges
// Credit-Aware Provider Router, Provider Budget Modes, Cost and Time Ledger,
// Why This Provider, Emergency No-Key Mode, and quota / paid / free risk
// explanation into one provider decision surface for designers, marketers,
// reviewers, clients, and judges -- not a decorative provider matrix.
//
// A creative operator can open one surface and answer:
//   - Which provider path was selected for the golden run?
//   - Which provider options are available or planned?
//   - Which providers require paid keys?
//   - Which providers can act as emergency no-key fallback?
//   - What budget mode would choose each path?
//   - What cost or time information is actually captured?
//   - What is only a policy classification and not measured billing?
//   - Why did ProofStudio choose this path?
//   - What would happen if keys, quota, or provider availability changed?
//   - Which proof surfaces verify the decision chain?
//
// All displayed values come from apps/web/src/providerDecisionIntelligence.ts,
// which is sourced verbatim from the checked-in PS-024 golden demo manifest,
// the PS-021 / PS-025 / PS-026 / PS-027 / PS-028 / PS-029 / PS-030 / PS-031 /
// PS-032 source evidence, the documented provider / model inventory, and the
// PS-005 / PS-006 router proofs. The PS-033 smoke validates these constants
// match the manifest and source evidence exactly.
//
// The component also exposes a `variant` prop so the same surface can render
// as a full page (via the /provider-decision-intelligence route in App.tsx)
// or as an inline section inside other judge surfaces. It performs no network
// call, calls no provider, and reads no B2 object: it only renders verified,
// checked-in evidence and documented routing policy.

import {
  PROVIDER_DECISION_INTELLIGENCE_ACTION_ROUTES,
  PROVIDER_DECISION_INTELLIGENCE_ARCHIVE_SHA256,
  PROVIDER_DECISION_INTELLIGENCE_ARCHIVE_URI,
  PROVIDER_DECISION_INTELLIGENCE_BUDGET_MODES,
  PROVIDER_DECISION_INTELLIGENCE_CAMPAIGN_ID,
  PROVIDER_DECISION_INTELLIGENCE_CLAIM_BOUNDARY_ALLOWED,
  PROVIDER_DECISION_INTELLIGENCE_CLAIM_BOUNDARY_FORBIDDEN,
  PROVIDER_DECISION_INTELLIGENCE_COST_TIME_LEDGER,
  PROVIDER_DECISION_INTELLIGENCE_DECISION_SUMMARY,
  PROVIDER_DECISION_INTELLIGENCE_DESIGNER_MARKETER_INTERPRETATION,
  PROVIDER_DECISION_INTELLIGENCE_EMERGENCY_NO_KEY_MODE,
  PROVIDER_DECISION_INTELLIGENCE_FALLBACK_NO_FAILURE_LINE,
  PROVIDER_DECISION_INTELLIGENCE_FALLBACK_POLICY,
  PROVIDER_DECISION_INTELLIGENCE_GENERATED_FROM,
  PROVIDER_DECISION_INTELLIGENCE_IMPLEMENTATION_ROADMAP,
  PROVIDER_DECISION_INTELLIGENCE_INTELLIGENCE_ID,
  PROVIDER_DECISION_INTELLIGENCE_LEDGER_FUTURE_FIELDS,
  PROVIDER_DECISION_INTELLIGENCE_LIMITATIONS,
  PROVIDER_DECISION_INTELLIGENCE_LOCAL_CONTRACT_PROOF,
  PROVIDER_DECISION_INTELLIGENCE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  PROVIDER_DECISION_INTELLIGENCE_PROVIDER_CALLS_DURING_REHYDRATE,
  PROVIDER_DECISION_INTELLIGENCE_PROVIDER_OPTIONS,
  PROVIDER_DECISION_INTELLIGENCE_PS031A_ROADMAP_CORRECTION,
  PROVIDER_DECISION_INTELLIGENCE_PUBLIC_DEPLOYMENT_PENDING,
  PROVIDER_DECISION_INTELLIGENCE_REHYDRATE_SOURCE,
  PROVIDER_DECISION_INTELLIGENCE_RUN_ID,
  PROVIDER_DECISION_INTELLIGENCE_SELECTED_ROUTE_SUMMARY,
  PROVIDER_DECISION_INTELLIGENCE_SOURCES,
  PROVIDER_DECISION_INTELLIGENCE_TRUTH_BOUNDARY,
  PROVIDER_DECISION_INTELLIGENCE_UNLOCK_SCOPE,
  PROVIDER_DECISION_INTELLIGENCE_VERSION,
  PROVIDER_DECISION_INTELLIGENCE_WHY_THIS_PROVIDER,
  type ProviderDecisionIntelligenceTruthClass,
} from "./providerDecisionIntelligence";
import { DEFAULT_API_BASE_URL } from "./api";

type ProviderDecisionIntelligenceVariant = "page" | "section";

const TRUTH_CLASS_LABEL: Record<
  ProviderDecisionIntelligenceTruthClass,
  string
> = {
  checked_in_evidence: "checked-in evidence",
  documented_provider_option: "documented provider option",
  router_policy: "router policy",
  fallback_policy: "fallback policy",
  cost_policy_estimate: "cost policy estimate",
  not_captured_in_evidence: "not captured in evidence",
  public_deployment_pending: "public deployment pending",
};

export function ProviderDecisionIntelligence({
  variant = "page",
}: {
  variant?: ProviderDecisionIntelligenceVariant;
}) {
  const isPage = variant === "page";

  const card = (
    <section
      className={
        isPage
          ? "card col-full provider-decision-intelligence provider-decision-intelligence-page"
          : "card col-full provider-decision-intelligence"
      }
      id="provider-decision-intelligence"
      aria-label="Provider Decision Intelligence"
    >
      <header className="provider-decision-intelligence-head">
        <span className="infra-tag">Routing</span>
        <h2>Provider Decision Intelligence</h2>
      </header>

      <p className="subhead">
        One provider decision surface over the golden workflow: selected route,
        provider option matrix, budget modes, Why This Provider, cost / time
        ledger, emergency no-key mode, fallback policy, designer / marketer
        interpretation, action rail, and an honest truth boundary. Every value
        is sourced verbatim from the checked-in evidence (PS-021, PS-024,
        PS-025, PS-026, PS-027, PS-028, PS-029, PS-030, PS-031, PS-032) plus
        the documented provider inventory and routing policy. Nothing here is
        invented, nothing here is fetched live from B2, and no provider is
        called. ProofStudio explains routing decisions, it does not hide them.
      </p>

      {/* 1. Provider Decision Identity */}
      <div
        className="provider-decision-intelligence-section provider-decision-intelligence-identity"
        id="provider-decision-intelligence-identity"
        data-section-key="provider_decision_identity"
      >
        <h3>Provider Decision Identity</h3>
        <dl className="kv">
          <dt>surface</dt>
          <dd className="mono provider-decision-intelligence-surface-name">
            Provider Decision Intelligence
          </dd>
          <dt>panel</dt>
          <dd className="mono provider-decision-intelligence-panel-name">
            Why This Provider
          </dd>
          <dt>slice</dt>
          <dd className="mono provider-decision-intelligence-slice">PS-033</dd>
          <dt>intelligence_id</dt>
          <dd className="mono provider-decision-intelligence-intelligence-id">
            {PROVIDER_DECISION_INTELLIGENCE_INTELLIGENCE_ID}
          </dd>
          <dt>intelligence_version</dt>
          <dd className="mono provider-decision-intelligence-intelligence-version">
            {PROVIDER_DECISION_INTELLIGENCE_VERSION}
          </dd>
          <dt>run_id</dt>
          <dd className="mono provider-decision-intelligence-run-id">
            {PROVIDER_DECISION_INTELLIGENCE_RUN_ID}
          </dd>
          <dt>campaign_id</dt>
          <dd className="mono provider-decision-intelligence-campaign-id">
            {PROVIDER_DECISION_INTELLIGENCE_CAMPAIGN_ID}
          </dd>
          <dt>public deployment</dt>
          <dd className="mono provider-decision-intelligence-public-deployment-pending">
            {String(PROVIDER_DECISION_INTELLIGENCE_PUBLIC_DEPLOYMENT_PENDING)}
          </dd>
        </dl>
      </div>

      {/* 2. Decision Summary */}
      <div
        className="provider-decision-intelligence-section"
        id="provider-decision-intelligence-decision-summary"
        data-section-key="decision_summary"
      >
        <h3>Decision Summary</h3>
        <p className="hint">
          A compact routing summary: selected route, provider decision state,
          budget mode state, cost / time ledger state, fallback state,
          emergency no-key mode state, and the evidence-backed vs policy /
          inferred split.
        </p>
        <p className="provider-decision-intelligence-selected-route-summary">
          {PROVIDER_DECISION_INTELLIGENCE_SELECTED_ROUTE_SUMMARY}
        </p>
        <ul className="infra-points provider-decision-intelligence-summary-list">
          {PROVIDER_DECISION_INTELLIGENCE_DECISION_SUMMARY.map((item) => (
            <li
              key={item.key}
              className="provider-decision-intelligence-summary-item"
              data-summary-key={item.key}
            >
              <div className="provider-decision-intelligence-summary-head">
                <span className="provider-decision-intelligence-summary-label">
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
        <dl className="kv">
          <dt>rehydrate_source</dt>
          <dd className="mono provider-decision-intelligence-rehydrate-source">
            {PROVIDER_DECISION_INTELLIGENCE_REHYDRATE_SOURCE}
          </dd>
          <dt>provider_calls_during_rehydrate</dt>
          <dd className="mono provider-decision-intelligence-provider-calls">
            {String(
              PROVIDER_DECISION_INTELLIGENCE_PROVIDER_CALLS_DURING_REHYDRATE,
            )}
          </dd>
          <dt>no_live_provider_call_during_rehydrate</dt>
          <dd className="mono provider-decision-intelligence-no-live-provider-call">
            {String(
              PROVIDER_DECISION_INTELLIGENCE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
            )}
          </dd>
        </dl>
      </div>

      {/* 3. Provider Option Matrix */}
      <div
        className="provider-decision-intelligence-section"
        id="provider-decision-intelligence-option-matrix"
        data-section-key="provider_option_matrix"
      >
        <h3>Provider Option Matrix</h3>
        <p className="hint">
          Each option carries provider name, model or role, modality or output
          type, key requirement, budget class, fallback role, evidence status,
          risk notes, and a truth class. Options are limited to providers
          supported by existing code, docs, or evidence. Documented options not
          active in the golden run are marked documented, not verified for
          this run.
        </p>
        <div className="table-wrap provider-decision-intelligence-option-wrap">
          <table className="timeline provider-decision-intelligence-option-table">
            <thead>
              <tr>
                <th>provider</th>
                <th>model / role</th>
                <th>modality / output</th>
                <th>key requirement</th>
                <th>budget class</th>
                <th>fallback role</th>
                <th>evidence status</th>
                <th>risk notes</th>
                <th>truth class</th>
              </tr>
            </thead>
            <tbody>
              {PROVIDER_DECISION_INTELLIGENCE_PROVIDER_OPTIONS.map((opt) => (
                <tr
                  key={opt.key}
                  data-option-key={opt.key}
                  data-truth-class={opt.truthClass}
                >
                  <td className="mono">{opt.provider}</td>
                  <td className="mono">{opt.modelOrRole}</td>
                  <td className="mono">{opt.modalityOrOutput}</td>
                  <td className="mono">{opt.keyRequirement}</td>
                  <td className="mono">{opt.budgetClass}</td>
                  <td className="mono">{opt.fallbackRole}</td>
                  <td>{opt.evidenceStatus}</td>
                  <td>{opt.riskNotes}</td>
                  <td>
                    <span className="pill info">
                      <span className="dot" />
                      {TRUTH_CLASS_LABEL[opt.truthClass]}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Budget Modes */}
      <div
        className="provider-decision-intelligence-section"
        id="provider-decision-intelligence-budget-modes"
        data-section-key="budget_modes"
      >
        <h3>Budget Modes</h3>
        <p className="hint provider-decision-intelligence-budget-policy-note">
          Budget modes are routing policies, not live billing facts. Cost and
          budget classes are policy unless measured evidence exists. The
          golden run's recorded budget_mode literal is not captured in the
          durable rehydrate evidence consumed here.
        </p>
        <div className="provider-decision-intelligence-budget-grid">
          {PROVIDER_DECISION_INTELLIGENCE_BUDGET_MODES.map((mode) => (
            <article
              key={mode.key}
              className="provider-decision-intelligence-budget-card"
              data-mode-key={mode.key}
              data-truth-class={mode.truthClass}
            >
              <h4 className="provider-decision-intelligence-budget-label">
                {mode.label}
              </h4>
              <span className="pill info">
                <span className="dot" />
                {TRUTH_CLASS_LABEL[mode.truthClass]}
              </span>
              <dl className="kv provider-decision-intelligence-budget-kv">
                <dt>goal</dt>
                <dd>{mode.goal}</dd>
                <dt>preferred route behavior</dt>
                <dd>{mode.preferredRouteBehavior}</dd>
                <dt>fallback behavior</dt>
                <dd>{mode.fallbackBehavior}</dd>
                <dt>key / payment dependency</dt>
                <dd>{mode.keyPaymentDependency}</dd>
                <dt>risk</dt>
                <dd>{mode.risk}</dd>
                <dt>what is measured</dt>
                <dd>{mode.whatIsMeasured}</dd>
                <dt>what is not measured yet</dt>
                <dd>{mode.whatIsNotMeasuredYet}</dd>
              </dl>
            </article>
          ))}
        </div>
      </div>

      {/* 5. Why This Provider */}
      <div
        className="provider-decision-intelligence-section"
        id="provider-decision-intelligence-why-this-provider"
        data-section-key="why_this_provider"
      >
        <h3>Why This Provider</h3>
        <dl className="kv provider-decision-intelligence-why-kv">
          <dt>why this route is acceptable for the golden chain</dt>
          <dd>{PROVIDER_DECISION_INTELLIGENCE_WHY_THIS_PROVIDER.whyAcceptable}</dd>
          <dt>what evidence backs the decision</dt>
          <dd>
            {PROVIDER_DECISION_INTELLIGENCE_WHY_THIS_PROVIDER.whatEvidenceBacksIt}
          </dd>
          <dt>what is not known from checked-in evidence</dt>
          <dd>
            {PROVIDER_DECISION_INTELLIGENCE_WHY_THIS_PROVIDER.whatIsNotKnown}
          </dd>
          <dt>how the system behaves if a provider key is unavailable</dt>
          <dd>
            {
              PROVIDER_DECISION_INTELLIGENCE_WHY_THIS_PROVIDER
                .howSystemBehavesIfKeyUnavailable
            }
          </dd>
          <dt>how emergency no-key mode differs from quality mode</dt>
          <dd>
            {
              PROVIDER_DECISION_INTELLIGENCE_WHY_THIS_PROVIDER
                .howEmergencyNoKeyDiffersFromQuality
            }
          </dd>
        </dl>
      </div>

      {/* 6. Cost and Time Ledger */}
      <div
        className="provider-decision-intelligence-section"
        id="provider-decision-intelligence-cost-time-ledger"
        data-section-key="cost_time_ledger"
      >
        <h3>Cost and Time Ledger</h3>
        <p className="hint">
          Ledger-ready rows that separate captured values, not-captured
          values, and future measurement fields. If measured cost or latency
          is not captured, the row shows{" "}
          <code className="mono">not captured in checked-in evidence</code>.
          No price, spend, latency, quota, or token usage is invented.
        </p>
        <div className="table-wrap provider-decision-intelligence-ledger-wrap">
          <table className="timeline provider-decision-intelligence-ledger-table">
            <thead>
              <tr>
                <th>provider</th>
                <th>model_or_role</th>
                <th>attempt_count</th>
                <th>fallback_count</th>
                <th>provider_calls_during_rehydrate</th>
                <th>estimated_cost_class</th>
                <th>measured_cost</th>
                <th>measured_latency</th>
                <th>evidence_source</th>
                <th>truth class</th>
              </tr>
            </thead>
            <tbody>
              {PROVIDER_DECISION_INTELLIGENCE_COST_TIME_LEDGER.map((row) => (
                <tr
                  key={row.key}
                  data-ledger-key={row.key}
                  data-truth-class={row.truthClass}
                >
                  <td className="mono">{row.provider}</td>
                  <td className="mono">{row.modelOrRole}</td>
                  <td className="mono">{row.attemptCount}</td>
                  <td className="mono">{row.fallbackCount}</td>
                  <td className="mono provider-decision-intelligence-ledger-calls">
                    {row.providerCallsDuringRehydrate}
                  </td>
                  <td className="mono">{row.estimatedCostClass}</td>
                  <td
                    className="mono provider-decision-intelligence-ledger-cost"
                    data-measured-cost={row.measuredCost}
                  >
                    {row.measuredCost}
                  </td>
                  <td
                    className="mono provider-decision-intelligence-ledger-latency"
                    data-measured-latency={row.measuredLatency}
                  >
                    {row.measuredLatency}
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
        <div className="provider-decision-intelligence-ledger-future">
          <h4>Future measurement fields</h4>
          <ul className="infra-points">
            {PROVIDER_DECISION_INTELLIGENCE_LEDGER_FUTURE_FIELDS.map((f) => (
              <li key={f}>{f}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* 7. Emergency No-Key Mode */}
      <div
        className="provider-decision-intelligence-section"
        id="provider-decision-intelligence-emergency-no-key"
        data-section-key="emergency_no_key_mode"
      >
        <h3>Emergency No-Key Mode</h3>
        <dl className="kv provider-decision-intelligence-nokey-kv">
          <dt>when this mode is useful</dt>
          <dd>
            {PROVIDER_DECISION_INTELLIGENCE_EMERGENCY_NO_KEY_MODE.whenUseful}
          </dd>
          <dt>how it protects demos / onboarding</dt>
          <dd>
            {
              PROVIDER_DECISION_INTELLIGENCE_EMERGENCY_NO_KEY_MODE
                .howProtectsDemosAndOnboarding
            }
          </dd>
          <dt>quality tradeoffs</dt>
          <dd>
            {PROVIDER_DECISION_INTELLIGENCE_EMERGENCY_NO_KEY_MODE.qualityTradeoffs}
          </dd>
          <dt>evidence / code support</dt>
          <dd>
            {
              PROVIDER_DECISION_INTELLIGENCE_EMERGENCY_NO_KEY_MODE
                .evidenceOrCodeSupport
            }
          </dd>
          <dt>what is not verified for the golden run</dt>
          <dd>
            {
              PROVIDER_DECISION_INTELLIGENCE_EMERGENCY_NO_KEY_MODE
                .notVerifiedForGoldenRun
            }
          </dd>
        </dl>
      </div>

      {/* 8. Provider Failure / Fallback Policy */}
      <div
        className="provider-decision-intelligence-section"
        id="provider-decision-intelligence-fallback-policy"
        data-section-key="fallback_policy"
      >
        <h3>Provider Failure / Fallback Policy</h3>
        <p className="hint">
          One policy row per condition. None of these is claimed as having
          happened in the golden run unless checked-in evidence proves it.
        </p>
        <div className="provider-decision-intelligence-fallback-grid">
          {PROVIDER_DECISION_INTELLIGENCE_FALLBACK_POLICY.map((row) => (
            <article
              key={row.key}
              className="provider-decision-intelligence-fallback-card"
              data-fallback-key={row.key}
              data-truth-class={row.truthClass}
            >
              <h4 className="provider-decision-intelligence-fallback-condition">
                {row.condition}
              </h4>
              <span className="pill info">
                <span className="dot" />
                {TRUTH_CLASS_LABEL[row.truthClass]}
              </span>
              <p>{row.policy}</p>
            </article>
          ))}
        </div>
        <p className="provider-decision-intelligence-fallback-no-failure">
          <span
            className="failure-as-proof-line provider-decision-intelligence-no-failure-line"
            data-mandate="no_fake_failure"
          >
            {PROVIDER_DECISION_INTELLIGENCE_FALLBACK_NO_FAILURE_LINE}
          </span>
        </p>
      </div>

      {/* 9. Designer / Marketer Interpretation */}
      <div
        className="provider-decision-intelligence-section"
        id="provider-decision-intelligence-designer-marketer"
        data-section-key="designer_marketer_interpretation"
      >
        <h3>Designer / Marketer Interpretation</h3>
        <dl className="kv provider-decision-intelligence-designer-kv">
          <dt>best quality mode</dt>
          <dd>
            {
              PROVIDER_DECISION_INTELLIGENCE_DESIGNER_MARKETER_INTERPRETATION
                .bestQualityMode
            }
          </dd>
          <dt>cheapest safe mode</dt>
          <dd>
            {
              PROVIDER_DECISION_INTELLIGENCE_DESIGNER_MARKETER_INTERPRETATION
                .cheapestSafeMode
            }
          </dd>
          <dt>emergency demo mode</dt>
          <dd>
            {
              PROVIDER_DECISION_INTELLIGENCE_DESIGNER_MARKETER_INTERPRETATION
                .emergencyDemoMode
            }
          </dd>
          <dt>why provider choice affects review</dt>
          <dd>
            {
              PROVIDER_DECISION_INTELLIGENCE_DESIGNER_MARKETER_INTERPRETATION
                .whyProviderChoiceAffectsReview
            }
          </dd>
          <dt>why proof matters for client handoff</dt>
          <dd>
            {
              PROVIDER_DECISION_INTELLIGENCE_DESIGNER_MARKETER_INTERPRETATION
                .whyProofMattersForClientHandoff
            }
          </dd>
          <dt>when to export evidence pack</dt>
          <dd>
            {
              PROVIDER_DECISION_INTELLIGENCE_DESIGNER_MARKETER_INTERPRETATION
                .whenToExportEvidencePack
            }
          </dd>
        </dl>
      </div>

      {/* 10. Action Rail */}
      <div
        className="provider-decision-intelligence-section provider-decision-intelligence-action-rail"
        id="provider-decision-intelligence-action-rail"
        data-section-key="action_rail"
      >
        <h3>Action Rail</h3>
        <p className="hint">
          Jump to any implemented proof surface from this decision surface.
        </p>
        <ul className="infra-points provider-decision-intelligence-action-list">
          {PROVIDER_DECISION_INTELLIGENCE_ACTION_ROUTES.map((route) => (
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

      {/* 11. Truth Boundary */}
      <section
        className="provider-decision-intelligence-section provider-decision-intelligence-truth-boundary"
        id="provider-decision-intelligence-truth-boundary"
        data-section-key="truth_boundary"
      >
        <h3>Truth Boundary</h3>
        <p className="truth-text">
          {PROVIDER_DECISION_INTELLIGENCE_TRUTH_BOUNDARY}
        </p>
        <div className="provider-decision-intelligence-claim-boundary-grid">
          <div className="provider-decision-intelligence-claim-boundary-col">
            <h4>Allowed claims</h4>
            <ul className="infra-points">
              {PROVIDER_DECISION_INTELLIGENCE_CLAIM_BOUNDARY_ALLOWED.map(
                (claim) => (
                  <li key={claim}>
                    <span className="pill ok">
                      <span className="dot" />
                      {claim}
                    </span>
                  </li>
                ),
              )}
            </ul>
          </div>
          <div className="provider-decision-intelligence-claim-boundary-col">
            <h4>Forbidden claims</h4>
            <ul className="infra-points">
              {PROVIDER_DECISION_INTELLIGENCE_CLAIM_BOUNDARY_FORBIDDEN.map(
                (claim) => (
                  <li key={claim}>
                    <span className="pill warn">
                      <span className="dot" />
                      {claim}
                    </span>
                  </li>
                ),
              )}
            </ul>
          </div>
        </div>
      </section>

      {/* 12. Limitations */}
      <div
        className="provider-decision-intelligence-section"
        id="provider-decision-intelligence-limitations"
        data-section-key="limitations"
      >
        <h3>Limitations</h3>
        <ul className="infra-points provider-decision-intelligence-limitations-points">
          {PROVIDER_DECISION_INTELLIGENCE_LIMITATIONS.map((lim) => (
            <li key={lim}>{lim}</li>
          ))}
        </ul>
      </div>

      {/* Source evidence files */}
      <div
        className="provider-decision-intelligence-section provider-decision-intelligence-files"
        id="provider-decision-intelligence-files"
      >
        <h3>Source evidence files</h3>
        <ul className="infra-points">
          {PROVIDER_DECISION_INTELLIGENCE_SOURCES.map((src) => (
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
            {PROVIDER_DECISION_INTELLIGENCE_IMPLEMENTATION_ROADMAP}
          </code>
        </p>
        <p className="hint muted-link">
          hardened module correction:{" "}
          <code className="mono">
            {PROVIDER_DECISION_INTELLIGENCE_PS031A_ROADMAP_CORRECTION}
          </code>
        </p>
      </div>

      {/* Deployment status */}
      <div
        className="provider-decision-intelligence-section provider-decision-intelligence-deployment"
        id="provider-decision-intelligence-deployment"
      >
        <h3>Deployment status</h3>
        <dl className="kv">
          <dt>local contract proof</dt>
          <dd className="mono">
            {String(PROVIDER_DECISION_INTELLIGENCE_LOCAL_CONTRACT_PROOF)}
          </dd>
          <dt>public deployment pending</dt>
          <dd className="mono">
            {String(
              PROVIDER_DECISION_INTELLIGENCE_PUBLIC_DEPLOYMENT_PENDING,
            )}
          </dd>
          <dt>unlock scope</dt>
          <dd className="mono">
            {PROVIDER_DECISION_INTELLIGENCE_UNLOCK_SCOPE}
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
          id="provider-decision-intelligence-cta"
        >
          <a
            className="btn"
            href="/lineage-comparison-lab"
            title="Open the Lineage + Comparison Lab (PS-034)"
          >
            Open Lineage + Comparison Lab
          </a>
          <a className="btn btn-primary" href="/operations-cockpit">
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
            href={"/passport/" + PROVIDER_DECISION_INTELLIGENCE_RUN_ID}
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
        PS-033 Provider Decision Intelligence · generated from{" "}
        {PROVIDER_DECISION_INTELLIGENCE_GENERATED_FROM} · fallback API base{" "}
        {DEFAULT_API_BASE_URL} · no provider call, no live B2 read, no broad
        durable read, no browser-side B2 byte verification, no raw media byte
        inspection, no fake provider failure claim.
      </p>
      <p className="hint muted-link">
        archive_uri:{" "}
        <code className="mono">
          {PROVIDER_DECISION_INTELLIGENCE_ARCHIVE_URI}
        </code>{" "}
        · archive_sha256:{" "}
        <code className="mono">
          {PROVIDER_DECISION_INTELLIGENCE_ARCHIVE_SHA256}
        </code>
      </p>
    </section>
  );

  if (!isPage) {
    return card;
  }

  return (
    <main className="cockpit provider-decision-intelligence-page-wrap">
      <header className="cockpit-hero" id="top">
        <p className="eyebrow">ProofStudio · Provider Decision Intelligence</p>
        <h1>Why this provider, honestly</h1>
        <p className="thesis">
          One provider decision surface: selected route, provider options,
          budget modes, cost / time ledger, emergency no-key mode, fallback
          policy.
        </p>
        <p className="hero-explainer">
          The Provider Decision Intelligence surface merges Credit-Aware
          Provider Router, Provider Budget Modes, Cost and Time Ledger, Why
          This Provider, Emergency No-Key Mode, and quota / paid / free risk
          explanation into one hardened product module. It shows the selected
          route (honestly: not captured in the durable rehydrate evidence), the
          documented provider option matrix, the four budget modes as routing
          policy, the Why This Provider panel, the cost / time ledger with a
          captured-vs-not-captured split, the emergency no-key mode, the
          fallback policy, and a designer / marketer interpretation. Every
          value is sourced verbatim from the checked-in evidence (PS-021,
          PS-024, PS-025, PS-026, PS-027, PS-028, PS-029, PS-030, PS-031,
          PS-032) plus the documented provider inventory and routing policy. It
          does not call any provider, does not read any B2 object, and does not
          claim the browser fetched and hashed the B2 object. No fake provider
          failure is claimed.
        </p>
      </header>
      {card}
    </main>
  );
}
