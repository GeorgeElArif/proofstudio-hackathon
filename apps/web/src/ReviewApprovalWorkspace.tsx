// PS-035 Review + Approval Workspace.
//
// A dedicated, reviewer-facing product surface that turns the existing
// ProofStudio proof chain into a human decision workspace: a reviewer inspects
// a reviewable item from accepted local / golden / demo data, sees its asset /
// media summary, sees the proof / evidence the pipeline already captured
// (provenance passport, manifest verification, B2 evidence, rehydrate, export
// pack), sets a review state (pending_review / approved / rejected /
// needs_changes), records a rationale and notes, and reads a clear, persistent
// boundary message of what approval does and does not prove.
//
// It is distinct from the legacy `/review` Review Room (PS-013 / PS-014), which
// stays as the live operator flow. The Review + Approval Workspace is purely
// client-side by default: it reads no B2 object, calls no provider, exposes no
// arbitrary run_id input for live execution, and performs no browser-side B2
// byte verification.
//
// The component exposes a `variant` prop so the same surface can render as a
// full page (via the /review-approval-workspace route in App.tsx) or as an
// inline section inside other judge surfaces. It performs no network call,
// calls no provider, reads no B2 object, and performs no browser-side B2 byte
// verification: it only renders verified, checked-in evidence plus an
// in-session review ledger.
//
// Truth boundary: approval means "approved by this workflow / demo UI". It does
// not prove semantic truth, legal authenticity, C2PA authenticity, human
// authorship, Object Lock / tamper-proof storage, or production security. The
// review ledger is local / in-session; it is not durable, tamper-proof,
// replicated, or production-multi-user. The local contract is verified; the
// public deployment remains pending.

import { useState } from "react";
import {
  REVIEW_APPROVAL_WORKSPACE_BOUNDARY_MESSAGE,
  REVIEW_APPROVAL_WORKSPACE_CAMPAIGN_ID,
  REVIEW_APPROVAL_WORKSPACE_CLAIM_BOUNDARY_ALLOWED,
  REVIEW_APPROVAL_WORKSPACE_CLAIM_BOUNDARY_FORBIDDEN,
  REVIEW_APPROVAL_WORKSPACE_ID,
  REVIEW_APPROVAL_WORKSPACE_ITEMS,
  REVIEW_APPROVAL_WORKSPACE_LIMITATIONS,
  REVIEW_APPROVAL_WORKSPACE_REASON_CATEGORIES,
  REVIEW_APPROVAL_WORKSPACE_STATES,
  REVIEW_APPROVAL_WORKSPACE_VERSION,
  emptyDecisionStateMap,
  reviewStateLabel,
  reviewStateTone,
  type ReasonCategory,
  type ReviewDecisionRecord,
  type ReviewProofLink,
  type ReviewState,
} from "./reviewApprovalWorkspace";
import { DEFAULT_API_BASE_URL } from "./api";
import { TrustBoundaryLayer } from "./TrustBoundaryLayer";
import { MultimodalProofLayer } from "./MultimodalProofLayer";
import { TranscriptTimestampEvidenceLayer } from "./TranscriptTimestampEvidenceLayer";
import { CampaignIntelligenceJudgeNarrativeLayer } from "./CampaignIntelligenceJudgeNarrativeLayer";
import { CloudflareLowCostBackboneLayer } from "./CloudflareLowCostBackboneLayer";
import { ProductionReadinessDemoModeLayer } from "./ProductionReadinessDemoModeLayer";
import { VoiceAudioEvidenceChoiceLayer } from "./VoiceAudioEvidenceChoiceLayer";

type ReviewApprovalWorkspaceVariant = "page" | "section";

function Pill({
  tone,
  children,
}: {
  tone: "ok" | "warn" | "danger" | "info" | "neutral";
  children: React.ReactNode;
}) {
  return (
    <span className={`pill ${tone === "neutral" ? "" : tone}`}>
      <span className="dot" />
      {children}
    </span>
  );
}

function StatePill({ state }: { state: ReviewState }) {
  return (
    <Pill tone={reviewStateTone(state)}>{reviewStateLabel(state)}</Pill>
  );
}

function proofStatusPill(proof: ReviewProofLink) {
  if (proof.available) return <Pill tone="ok">{proof.status}</Pill>;
  return <Pill tone="warn">not available</Pill>;
}

function ProofLink({ proof }: { proof: ReviewProofLink }) {
  if (proof.available && proof.href) {
    return (
      <a className="btn" href={proof.href}>
        {proof.label}
      </a>
    );
  }
  return (
    <span className="btn" aria-disabled>
      {proof.label}
    </span>
  );
}

export function ReviewApprovalWorkspace({
  variant = "page",
}: {
  variant?: ReviewApprovalWorkspaceVariant;
}) {
  const isPage = variant === "page";
  const items = REVIEW_APPROVAL_WORKSPACE_ITEMS;
  const [itemStates, setItemStates] = useState<Record<string, ReviewState>>(
    () => emptyDecisionStateMap(items),
  );
  const [ledger, setLedger] = useState<ReviewDecisionRecord[]>([]);

  return (
    <ReviewApprovalWorkspaceBody
      isPage={isPage}
      items={items}
      itemStates={itemStates}
      setItemStates={setItemStates}
      ledger={ledger}
      setLedger={setLedger}
    />
  );
}

interface DraftForm {
  decision: ReviewState;
  reasonCategory: ReasonCategory | null;
  rationale: string;
  notes: string;
  reviewerLabel: string;
}

function ReviewApprovalWorkspaceBody({
  isPage,
  items,
  itemStates,
  setItemStates,
  ledger,
  setLedger,
}: {
  isPage: boolean;
  items: typeof REVIEW_APPROVAL_WORKSPACE_ITEMS;
  itemStates: Record<string, ReviewState>;
  setItemStates: (
    updater: (prev: Record<string, ReviewState>) => Record<string, ReviewState>,
  ) => void;
  ledger: ReviewDecisionRecord[];
  setLedger: (
    updater: (prev: ReviewDecisionRecord[]) => ReviewDecisionRecord[],
  ) => void;
}) {
  const card = (
    <section
      className={
        isPage
          ? "card col-full review-approval-workspace review-approval-workspace-page"
          : "card col-full review-approval-workspace"
      }
      id="review-approval-workspace"
      aria-label="Review + Approval Workspace"
    >
      <header className="review-approval-workspace-head">
        <span className="infra-tag">Review</span>
        <h2>Review + Approval Workspace</h2>
      </header>

      <p className="subhead">
        One human decision surface over the golden workflow: inspect a reviewable
        item, read its asset / media summary, read the proof the pipeline
        already captured, set a review state, record your rationale and notes,
        and read the approval trail. Every reviewed value is sourced verbatim
        from the checked-in evidence (PS-021, PS-024, PS-025, PS-035a). The
        workspace reads no B2 object, calls no provider, and performs no
        browser-side B2 byte verification.
      </p>

      <dl className="kv" style={{ marginBottom: 8 }}>
        <dt>workspace id</dt>
        <dd className="mono">{REVIEW_APPROVAL_WORKSPACE_ID}</dd>
        <dt>workspace version</dt>
        <dd className="mono">{REVIEW_APPROVAL_WORKSPACE_VERSION}</dd>
        <dt>campaign id</dt>
        <dd className="mono">{REVIEW_APPROVAL_WORKSPACE_CAMPAIGN_ID}</dd>
        <dt>review states</dt>
        <dd>
          <div className="btn-row" style={{ marginTop: -2 }}>
            {REVIEW_APPROVAL_WORKSPACE_STATES.map((s) => (
              <Pill key={s.value} tone={s.tone}>
                {s.label}
              </Pill>
            ))}
          </div>
        </dd>
      </dl>

      {/* 1. Reviewable items */}
      <div
        className="review-approval-workspace-section"
        id="review-approval-workspace-items"
        data-section-key="reviewable_items"
      >
        <h3>Reviewable items</h3>
        <p className="hint">
          At least one reviewable item sourced from accepted local / golden /
          demo data. Every item starts in Pending Review until a reviewer sets a
          decision.
        </p>
        <div className="review-approval-workspace-item-grid">
          {items.map((item) => (
            <ReviewableItemCard
              key={item.itemId}
              item={item}
              currentState={itemStates[item.itemId] ?? item.initialState}
              ledger={ledger}
              onCommit={(record) => {
                setItemStates((prev) => ({
                  ...prev,
                  [item.itemId]: record.decisionState,
                }));
                setLedger((prev) => [record, ...prev]);
              }}
            />
          ))}
        </div>
      </div>

      {/* 2. Review ledger */}
      <div
        className="review-approval-workspace-section"
        id="review-approval-workspace-ledger"
        data-section-key="review_ledger"
      >
        <h3>Review ledger</h3>
        <p className="hint">
          The local / in-session approval trail. It is not durable,
          tamper-proof, replicated, or production-multi-user.
        </p>
        {ledger.length === 0 ? (
          <div className="empty">
            No decisions recorded yet in this session. Set a review state and
            record your rationale to add an entry.
          </div>
        ) : (
          <div className="table-wrap">
            <table className="timeline review-approval-workspace-ledger-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>item</th>
                  <th>decision</th>
                  <th>reason</th>
                  <th>rationale</th>
                  <th>notes</th>
                  <th>reviewer</th>
                  <th>recorded at</th>
                </tr>
              </thead>
              <tbody>
                {ledger.map((rec, i) => (
                  <tr key={`${rec.itemId}-${rec.recordedAt}-${i}`}>
                    <td className="mono">{String(i + 1).padStart(2, "0")}</td>
                    <td className="mono">{rec.itemId}</td>
                    <td>
                      <StatePill state={rec.decisionState} />
                    </td>
                    <td className="mono">{rec.reasonCategory ?? "—"}</td>
                    <td>{rec.rationale || "—"}</td>
                    <td>{rec.notes || "—"}</td>
                    <td>{rec.reviewerLabel || "—"}</td>
                    <td className="mono">{rec.recordedAt}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 3. Boundary */}
      <section
        className="review-approval-workspace-section review-approval-workspace-boundary"
        id="review-approval-workspace-boundary"
        data-section-key="boundary"
      >
        <h3>Boundary</h3>
        <p className="trust-text">{REVIEW_APPROVAL_WORKSPACE_BOUNDARY_MESSAGE}</p>
        <p className="trust-text review-approval-workspace-boundary-summary">
          Proof boundary &mdash; approval records the reviewer's workflow decision;
          it does not prove semantic truth, does not prove legal authenticity,
          does not prove C2PA authenticity, does not prove human authorship,
          does not prove Object Lock / tamper-proof storage, and
          does not prove production security.
        </p>
        <div className="review-approval-workspace-claim-boundary-grid">
          <div className="review-approval-workspace-claim-boundary-col">
            <h4>What approval means here</h4>
            <ul className="infra-points">
              {REVIEW_APPROVAL_WORKSPACE_CLAIM_BOUNDARY_ALLOWED.map((claim) => (
                <li key={claim}>
                  <span className="pill ok">
                    <span className="dot" />
                    {claim}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div className="review-approval-workspace-claim-boundary-col">
            <h4>What approval does NOT mean</h4>
            <ul className="infra-points">
              {REVIEW_APPROVAL_WORKSPACE_CLAIM_BOUNDARY_FORBIDDEN.map(
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

      {/* 4. Limitations */}
      <div
        className="review-approval-workspace-section"
        id="review-approval-workspace-limitations"
        data-section-key="limitations"
      >
        <h3>Limitations</h3>
        <ul className="infra-points review-approval-workspace-limitations-points">
          {REVIEW_APPROVAL_WORKSPACE_LIMITATIONS.map((lim) => (
            <li key={lim}>{lim}</li>
          ))}
        </ul>
      </div>

      {isPage && (
        <div className="cockpit-cta-row" id="review-approval-workspace-cta">
          <a
            className="btn"
            href="/evidence-pack"
            title="Open the Judge Evidence Pack (PS-031)"
          >
            Open Judge Evidence Pack
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
        PS-035 Review + Approval Workspace · fallback API base{" "}
        {DEFAULT_API_BASE_URL} · local / in-session ledger · no provider call,
        no live B2 read, no live B2 write, no browser-side B2 byte verification.
      </p>
    </section>
  );

  if (!isPage) {
    return card;
  }

  return (
    <main className="cockpit review-approval-workspace-page-wrap">
      <header className="cockpit-hero" id="top">
        <p className="eyebrow">ProofStudio · Review + Approval Workspace</p>
        <h1>Approve, reject, and explain — over the golden workflow</h1>
        <p className="thesis">
          One workspace to inspect a reviewable item, read its proof, make a
          decision, and record the reason.
        </p>
        <p className="hero-explainer">
          The Review + Approval Workspace turns the existing ProofStudio proof
          chain into a human decision surface. A reviewer opens a reviewable
          item from accepted local / golden / demo data, reads its asset /
          media summary and the proof the pipeline already captured, sets a
          review state, records a rationale and notes, and reads a clear
          boundary message. Every value is sourced verbatim from the checked-in
          evidence. The workspace reads no B2 object, calls no provider, and
          performs no browser-side B2 byte verification. Approval records the
          reviewer's workflow decision; it does not prove semantic truth, legal
          authenticity, C2PA authenticity, human authorship, Object Lock /
          tamper-proof storage, or production security.
        </p>
      </header>
      {card}
    </main>
  );
}

function ReviewableItemCard({
  item,
  currentState,
  ledger,
  onCommit,
}: {
  item: (typeof REVIEW_APPROVAL_WORKSPACE_ITEMS)[number];
  currentState: ReviewState;
  ledger: ReviewDecisionRecord[];
  onCommit: (record: ReviewDecisionRecord) => void;
}) {
  const initial: DraftForm = {
    decision: currentState,
    reasonCategory: null,
    rationale: "",
    notes: "",
    reviewerLabel: "",
  };
  const [form, setForm] = useState<DraftForm>(initial);
  const itemLedger = ledger.filter((r) => r.itemId === item.itemId);

  const handleCommit = () => {
    const rationale = form.rationale.trim();
    if (!rationale) return;
    const record: ReviewDecisionRecord = {
      itemId: item.itemId,
      decisionState: form.decision,
      reasonCategory: form.reasonCategory,
      rationale,
      notes: form.notes.trim(),
      reviewerLabel: form.reviewerLabel.trim() || null,
      recordedAt: new Date().toISOString(),
    };
    onCommit(record);
    setForm((f) => ({ ...f, rationale: "", notes: "" }));
  };

  const asset = item.assetSummary;
  const proof = item.proofSummary;

  return (
    <article
      className="review-approval-workspace-item-card"
      id={`review-item-${item.itemId}`}
      data-item-id={item.itemId}
    >
      <header className="review-approval-workspace-item-head">
        <div>
          <h4 className="review-approval-workspace-item-title">
            Reviewable item
          </h4>
          <code className="mono review-approval-workspace-item-id">
            {item.itemId}
          </code>
        </div>
        <span
          className="review-approval-workspace-state-pill"
          data-state={currentState}
        >
          <StatePill state={currentState} />
        </span>
      </header>

      <dl className="kv">
        <dt>run id</dt>
        <dd className="mono">{item.runId}</dd>
        <dt>campaign id</dt>
        <dd className="mono">{item.campaignId}</dd>
      </dl>

      {/* Asset / media summary */}
      <div className="review-approval-workspace-subblock">
        <h5>Asset / media summary</h5>
        <dl className="kv">
          <dt>kind</dt>
          <dd className="mono">{asset.kind}</dd>
          <dt>provider</dt>
          <dd className={asset.provider ? "mono" : "muted"}>
            {asset.provider ?? "(not captured in checked-in evidence)"}
          </dd>
          <dt>model</dt>
          <dd className={asset.model ? "mono" : "muted"}>
            {asset.model ?? "(not captured in checked-in evidence)"}
          </dd>
          <dt>media type</dt>
          <dd className="mono">{asset.mediaType ?? "(none)"}</dd>
          <dt>size</dt>
          <dd className={asset.sizeBytes != null ? "mono" : "muted"}>
            {asset.sizeBytes != null
              ? `${asset.sizeBytes} bytes`
              : "(not captured in checked-in evidence)"}
          </dd>
          <dt>sha256</dt>
          <dd className="mono">{asset.sha256 ?? "(none)"}</dd>
          <dt>url</dt>
          <dd className={asset.url ? "mono" : "muted"}>
            {asset.url ?? "(none)"}
          </dd>
        </dl>
      </div>

      {/* Proof / evidence summary */}
      <div className="review-approval-workspace-subblock">
        <h5>Proof / evidence summary</h5>
        <p className="hint">
          Each entry below maps to a checked-in artifact: provenance passport,
          manifest verification, B2 evidence, rehydrate, and export pack.
        </p>
        <ul className="review-approval-workspace-proof-list">
          {(
            [
              ["provenance_passport", proof.provenancePassport],
              ["manifest_verification", proof.manifestVerification],
              ["b2_evidence", proof.b2Evidence],
              ["rehydrate", proof.rehydrate],
              ["export_pack", proof.exportPack],
            ] as const
          ).map(([key, p]) => (
            <li
              key={key}
              className="review-approval-workspace-proof-item"
              data-proof-key={key}
              data-available={p.available ? "true" : "false"}
            >
              <div className="review-approval-workspace-proof-head">
                <ProofLink proof={p} />
                {proofStatusPill(p)}
              </div>
              <p className="hint review-approval-workspace-proof-detail">
                {p.detail ??
                  "Not available from checked-in evidence. No link or verified status is fabricated."}
              </p>
            </li>
          ))}
        </ul>
      </div>

      {/* Reviewer decision */}
      <div className="review-approval-workspace-subblock">
        <h5>Reviewer decision</h5>
        <div className="field">
          <label htmlFor={`decision-${item.itemId}`}>Decision state</label>
          <select
            id={`decision-${item.itemId}`}
            value={form.decision}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                decision: e.target.value as ReviewState,
              }))
            }
          >
            {REVIEW_APPROVAL_WORKSPACE_STATES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor={`reason-${item.itemId}`}>Reason category</label>
          <select
            id={`reason-${item.itemId}`}
            value={form.reasonCategory ?? ""}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                reasonCategory: (e.target.value || null) as ReasonCategory | null,
              }))
            }
          >
            <option value="">(optional)</option>
            {REVIEW_APPROVAL_WORKSPACE_REASON_CATEGORIES.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor={`rationale-${item.itemId}`}>Rationale</label>
          <textarea
            id={`rationale-${item.itemId}`}
            value={form.rationale}
            onChange={(e) =>
              setForm((f) => ({ ...f, rationale: e.target.value }))
            }
            placeholder="Why this decision? (required to record)"
          />
        </div>
        <div className="field">
          <label htmlFor={`notes-${item.itemId}`}>Notes</label>
          <textarea
            id={`notes-${item.itemId}`}
            value={form.notes}
            onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
            placeholder="Additional reviewer notes (optional)."
          />
        </div>
        <div className="field">
          <label htmlFor={`reviewer-${item.itemId}`}>Reviewer label</label>
          <input
            id={`reviewer-${item.itemId}`}
            type="text"
            value={form.reviewerLabel}
            onChange={(e) =>
              setForm((f) => ({ ...f, reviewerLabel: e.target.value }))
            }
            placeholder="Your name / role (optional). PS-035 does not verify identity."
          />
        </div>
        <div className="btn-row">
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleCommit}
            disabled={!form.rationale.trim()}
            title="Record the decision in the local / in-session ledger"
          >
            Record decision
          </button>
        </div>
        {itemLedger.length > 0 && (
          <div className="review-approval-workspace-item-history">
            <p className="hint">Recorded rationale / notes for this item:</p>
            <ul className="infra-points">
              {itemLedger.map((rec, i) => (
                <li key={`${rec.recordedAt}-${i}`}>
                  <StatePill state={rec.decisionState} />
                  <span className="muted-link" style={{ marginLeft: 6 }}>
                    {rec.rationale}
                    {rec.notes ? ` · notes: ${rec.notes}` : ""}
                    {rec.reviewerLabel ? ` · reviewer: ${rec.reviewerLabel}` : ""}
                    {rec.reasonCategory ? ` · ${rec.reasonCategory}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </article>
  );
}
