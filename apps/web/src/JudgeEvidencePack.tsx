// PS-031 Export Campaign Pack v2 / Judge Evidence Pack.
//
// A dedicated, judge-facing product surface that turns the existing
// ProofStudio proof chain into a portable, readable judge / client pack. It
// is NOT another image generator surface: it assembles the verified golden
// workflow (run identity, B2 archive, Genblaze manifest, B2 rehydrate,
// Failure-as-Proof, public passport, disclosure, limitations) into one
// readable pack and exposes honest local browser exports (pack JSON + pack
// README / Markdown).
//
// The component also exposes a `variant` prop so the same surface can render
// as a full page (via the /evidence-pack route in App.tsx) or as an inline
// section inside other judge surfaces. It performs no network call, calls no
// provider, and reads no B2 object: it only renders verified, checked-in
// evidence plus a local browser-side Blob/download for the pack JSON and the
// pack Markdown.
//
// Honest export labels (surfaced verbatim in the UI so a judge never reads
// "downloaded from the server" when the bytes were produced locally):
//
//   - Local browser export.
//   - Generated from checked-in ProofStudio evidence.
//   - Does not fetch B2 bytes.
//   - Does not include raw media bytes.
//   - Not a zip export (zip generation is not implemented in PS-031).
//
// The pack does not prove semantic truth, legal authenticity, C2PA
// authenticity, or human authorship. The pack does not prove Object Lock or
// tamper-proof storage. The pack did not fetch and hash the B2 object in the
// browser. The local contract is verified; the public deployment remains
// pending until the new backend is deployed and the public URL is verified
// end-to-end.

import { useState } from "react";
import {
  JUDGE_EVIDENCE_PACK_ARCHIVE_SUMMARY,
  JUDGE_EVIDENCE_PACK_ARCHIVE_SHA256,
  JUDGE_EVIDENCE_PACK_ARCHIVE_URI,
  JUDGE_EVIDENCE_PACK_CAMPAIGN_ID,
  JUDGE_EVIDENCE_PACK_CLAIM_BOUNDARY_ALLOWED,
  JUDGE_EVIDENCE_PACK_CLAIM_BOUNDARY_FORBIDDEN,
  JUDGE_EVIDENCE_PACK_DISCLOSURE_NOTES,
  JUDGE_EVIDENCE_PACK_FAILURE_AS_PROOF_SUMMARY,
  JUDGE_EVIDENCE_PACK_GENERATED_FROM,
  JUDGE_EVIDENCE_PACK_GENERATION_EVIDENCE_SUMMARY,
  JUDGE_EVIDENCE_PACK_IMPLEMENTATION_ROADMAP,
  JUDGE_EVIDENCE_PACK_LIMITATIONS,
  JUDGE_EVIDENCE_PACK_LOCAL_CONTRACT_PROOF,
  JUDGE_EVIDENCE_PACK_NEXT_ACTIONS,
  JUDGE_EVIDENCE_PACK_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
  JUDGE_EVIDENCE_PACK_PACK_ID,
  JUDGE_EVIDENCE_PACK_PACK_VERSION,
  JUDGE_EVIDENCE_PACK_PROOF_CHAIN,
  JUDGE_EVIDENCE_PACK_PROVIDER_CALLS_DURING_REHYDRATE,
  JUDGE_EVIDENCE_PACK_PROVIDER_LEDGER_SUMMARY,
  JUDGE_EVIDENCE_PACK_PUBLIC_DEPLOYMENT_PENDING,
  JUDGE_EVIDENCE_PACK_REHYDRATE_SOURCE,
  JUDGE_EVIDENCE_PACK_REVIEW_STATUS,
  JUDGE_EVIDENCE_PACK_ROUTES,
  JUDGE_EVIDENCE_PACK_RUN_ID,
  JUDGE_EVIDENCE_PACK_SOURCES,
  JUDGE_EVIDENCE_PACK_TRUTH_BOUNDARY,
  JUDGE_EVIDENCE_PACK_UNLOCK_SCOPE,
  buildJudgeEvidencePackJson,
  buildJudgeEvidencePackMarkdown,
  type JudgeEvidencePackProofKind,
} from "./judgeEvidencePack";
import { DEFAULT_API_BASE_URL } from "./api";
import { TrustBoundaryLayer } from "./TrustBoundaryLayer";
import { MultimodalProofLayer } from "./MultimodalProofLayer";
import { TranscriptTimestampEvidenceLayer } from "./TranscriptTimestampEvidenceLayer";
import { CampaignIntelligenceJudgeNarrativeLayer } from "./CampaignIntelligenceJudgeNarrativeLayer";
import { CloudflareLowCostBackboneLayer } from "./CloudflareLowCostBackboneLayer";
import { ProductionReadinessDemoModeLayer } from "./ProductionReadinessDemoModeLayer";
import { VoiceAudioEvidenceChoiceLayer } from "./VoiceAudioEvidenceChoiceLayer";

type JudgeEvidencePackVariant = "page" | "section";

const KIND_LABEL: Record<JudgeEvidencePackProofKind, string> = {
  checked_in_evidence: "checked-in evidence",
  durable_b2_archive_proof: "durable B2 archive proof",
  genblaze_manifest_evidence: "Genblaze manifest evidence",
  b2_rehydrate_proof: "B2 rehydrate proof",
  local_passport_contract_proof: "local public passport contract proof",
  local_browser_export: "local browser export",
  inferred_product_explanation: "inferred product explanation",
  public_deployment_pending: "public deployment pending",
};

// Honest export labels. Surfaced in the UI and asserted by the PS-031 smoke.
const EXPORT_LABELS: readonly string[] = [
  "Local browser export",
  "Generated from checked-in ProofStudio evidence",
  "Does not fetch B2 bytes",
  "Does not include raw media bytes",
  "Not a zip export (zip generation is not implemented in PS-031)",
];

export function JudgeEvidencePack({
  variant = "page",
}: {
  variant?: JudgeEvidencePackVariant;
}) {
  const isPage = variant === "page";
  // generated_at is the only dynamic field. We compute it at render time so
  // the local browser export carries a real timestamp. The smoke never
  // asserts on its value (spec: "If generated_at is dynamic in browser
  // export, the smoke must not use brittle timestamp expectations").
  const [generatedAt] = useState<string>(() =>
    new Date().toISOString(),
  );
  const [jsonCopied, setJsonCopied] = useState(false);
  const [mdCopied, setMdCopied] = useState(false);

  const packJson = buildJudgeEvidencePackJson(generatedAt);
  const packMarkdown = buildJudgeEvidencePackMarkdown(generatedAt);

  const handleDownloadJson = () => {
    const blob = new Blob([JSON.stringify(packJson, null, 2) + "\n"], {
      type: "application/json",
    });
    triggerBrowserDownload(blob, packJson.pack_id + ".json");
    setJsonCopied(true);
  };

  const handleDownloadMarkdown = () => {
    const blob = new Blob([packMarkdown + "\n"], {
      type: "text/markdown",
    });
    triggerBrowserDownload(blob, packJson.pack_id + ".README.md");
    setMdCopied(true);
  };

  const handleCopyJson = async () => {
    try {
      await navigator.clipboard.writeText(
        JSON.stringify(packJson, null, 2),
      );
      setJsonCopied(true);
    } catch {
      // Clipboard may be unavailable (CORS / insecure context). The download
      // action remains the primary export path; we do not fake success.
      setJsonCopied(false);
    }
  };

  const handleCopyMarkdown = async () => {
    try {
      await navigator.clipboard.writeText(packMarkdown);
      setMdCopied(true);
    } catch {
      setMdCopied(false);
    }
  };

  const card = (
    <section
      className={
        isPage
          ? "card col-full judge-evidence-pack judge-evidence-pack-page"
          : "card col-full judge-evidence-pack"
      }
      id="judge-evidence-pack"
      aria-label="Judge Evidence Pack"
    >
      <header className="judge-evidence-pack-head">
        <span className="infra-tag">Export</span>
        <h2>Judge Evidence Pack</h2>
      </header>

      <p className="subhead">
        One canonical judge-facing pack over the golden workflow: run
        identity, B2 archive, Genblaze manifest, B2 rehydrate, Failure-as-Proof,
        public passport, disclosure notes, limitations, and next actions.
        Every value is sourced verbatim from the checked-in evidence (PS-021,
        PS-024, PS-025, PS-026, PS-027, PS-028, PS-029, PS-030). The pack is
        generated locally in the browser. It does not call any provider, does
        not read any B2 object, and does not claim the browser fetched and
        hashed the B2 object.
      </p>

      {/* Local browser export actions */}
      <div
        className="judge-evidence-pack-export"
        id="judge-evidence-pack-export"
      >
        <h3>Local browser export</h3>
        <p className="hint">
          The pack JSON and the pack README / Markdown are generated locally
          from checked-in ProofStudio evidence. The browser does not fetch the
          B2 object, does not include raw media bytes, and does not produce a
          zip export.
        </p>
        <ul className="infra-points judge-evidence-pack-export-labels">
          {EXPORT_LABELS.map((label) => (
            <li
              key={label}
              className="judge-evidence-pack-export-label"
              data-export-label={label}
            >
              <span className="pill info">
                <span className="dot" />
                {label}
              </span>
            </li>
          ))}
        </ul>
        <div className="btn-row judge-evidence-pack-export-actions">
          <button
            type="button"
            className="btn btn-primary"
            id="judge-evidence-pack-download-json"
            data-export-kind="json"
            onClick={handleDownloadJson}
            title="Download the Judge Evidence Pack JSON (local browser export)"
          >
            Download pack JSON
          </button>
          <button
            type="button"
            className="btn"
            id="judge-evidence-pack-copy-json"
            data-export-kind="json"
            onClick={handleCopyJson}
            title="Copy the Judge Evidence Pack JSON to the clipboard"
          >
            {jsonCopied ? "Copied JSON" : "Copy pack JSON"}
          </button>
          <button
            type="button"
            className="btn btn-primary"
            id="judge-evidence-pack-download-markdown"
            data-export-kind="markdown"
            onClick={handleDownloadMarkdown}
            title="Download the Judge Evidence Pack README / Markdown (local browser export)"
          >
            Download pack README / Markdown
          </button>
          <button
            type="button"
            className="btn"
            id="judge-evidence-pack-copy-markdown"
            data-export-kind="markdown"
            onClick={handleCopyMarkdown}
            title="Copy the Judge Evidence Pack README / Markdown to the clipboard"
          >
            {mdCopied ? "Copied Markdown" : "Copy pack README / Markdown"}
          </button>
        </div>
        <details className="json judge-evidence-pack-json-preview">
          <summary>Pack JSON preview (local browser export)</summary>
          <pre>{JSON.stringify(packJson, null, 2)}</pre>
        </details>
        <details className="json judge-evidence-pack-markdown-preview">
          <summary>Pack README / Markdown preview (local browser export)</summary>
          <pre>{packMarkdown}</pre>
        </details>
      </div>

      {/* 1. Pack identity */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-identity"
        data-section-key="pack_identity"
      >
        <h3>Pack identity</h3>
        <dl className="kv">
          <dt>pack_id</dt>
          <dd className="mono judge-evidence-pack-pack-id">
            {JUDGE_EVIDENCE_PACK_PACK_ID}
          </dd>
          <dt>pack_version</dt>
          <dd className="mono judge-evidence-pack-pack-version">
            {JUDGE_EVIDENCE_PACK_PACK_VERSION}
          </dd>
          <dt>generated_from</dt>
          <dd className="mono judge-evidence-pack-generated-from">
            {JUDGE_EVIDENCE_PACK_GENERATED_FROM}
          </dd>
          <dt>generated_at</dt>
          <dd className="mono judge-evidence-pack-generated-at">
            {generatedAt}
          </dd>
        </dl>
      </div>

      {/* 2. Campaign / run identity */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-campaign-run"
        data-section-key="campaign_run_identity"
      >
        <h3>Campaign / run identity</h3>
        <dl className="kv">
          <dt>run_id</dt>
          <dd className="mono judge-evidence-pack-run-id">
            {JUDGE_EVIDENCE_PACK_RUN_ID}
          </dd>
          <dt>campaign_id</dt>
          <dd className="mono judge-evidence-pack-campaign-id">
            {JUDGE_EVIDENCE_PACK_CAMPAIGN_ID}
          </dd>
        </dl>
      </div>

      {/* 3. Final asset / archive summary */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-archive-summary"
        data-section-key="final_asset_archive_summary"
      >
        <h3>Final asset / archive summary</h3>
        <dl className="kv">
          <dt>archive URI</dt>
          <dd className="mono judge-evidence-pack-archive-uri">
            {JUDGE_EVIDENCE_PACK_ARCHIVE_SUMMARY.archive_uri}
          </dd>
          <dt>archive SHA-256</dt>
          <dd className="mono judge-evidence-pack-archive-sha">
            {JUDGE_EVIDENCE_PACK_ARCHIVE_SUMMARY.archive_sha256}
          </dd>
          <dt>rehydrate_source</dt>
          <dd className="mono judge-evidence-pack-rehydrate-source">
            {JUDGE_EVIDENCE_PACK_ARCHIVE_SUMMARY.rehydrate_source}
          </dd>
          <dt>provider_calls_during_rehydrate</dt>
          <dd className="mono judge-evidence-pack-provider-calls">
            {String(
              JUDGE_EVIDENCE_PACK_ARCHIVE_SUMMARY.provider_calls_during_rehydrate,
            )}
          </dd>
          <dt>no_live_provider_call_during_rehydrate</dt>
          <dd className="mono judge-evidence-pack-no-live-provider-call">
            {String(
              JUDGE_EVIDENCE_PACK_ARCHIVE_SUMMARY
                .no_live_provider_call_during_rehydrate,
            )}
          </dd>
        </dl>
        <p className="hint">{JUDGE_EVIDENCE_PACK_ARCHIVE_SUMMARY.note}</p>
      </div>

      {/* 4. Prompt / generation evidence summary */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-generation-evidence"
        data-section-key="prompt_generation_evidence_summary"
      >
        <h3>{JUDGE_EVIDENCE_PACK_GENERATION_EVIDENCE_SUMMARY.title}</h3>
        <p className="hint muted-link">
          available from checked-in evidence:{" "}
          {String(JUDGE_EVIDENCE_PACK_GENERATION_EVIDENCE_SUMMARY.available)}
        </p>
        <p className="judge-evidence-pack-generation-evidence-note">
          {JUDGE_EVIDENCE_PACK_GENERATION_EVIDENCE_SUMMARY.note}
        </p>
        <p className="hint muted-link">
          sources:{" "}
          {JUDGE_EVIDENCE_PACK_GENERATION_EVIDENCE_SUMMARY.sourceTags.join(
            " / ",
          )}
        </p>
      </div>

      {/* 5. Provider / model / attempt ledger summary */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-provider-ledger"
        data-section-key="provider_model_attempt_ledger_summary"
      >
        <h3>{JUDGE_EVIDENCE_PACK_PROVIDER_LEDGER_SUMMARY.title}</h3>
        <p className="hint muted-link">
          available from checked-in evidence:{" "}
          {String(JUDGE_EVIDENCE_PACK_PROVIDER_LEDGER_SUMMARY.available)}
        </p>
        <p className="judge-evidence-pack-provider-ledger-note">
          {JUDGE_EVIDENCE_PACK_PROVIDER_LEDGER_SUMMARY.note}
        </p>
        <p className="hint muted-link">
          sources:{" "}
          {JUDGE_EVIDENCE_PACK_PROVIDER_LEDGER_SUMMARY.sourceTags.join(" / ")}
        </p>
      </div>

      {/* 6. B2 archive evidence */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-b2-archive"
        data-section-key="b2_archive_evidence"
      >
        <h3>B2 archive evidence</h3>
        <p className="hint">
          PS-021 proved the run archive was written to and read from a real
          Backblaze B2 object behind explicit, default-off gates. The pack
          records the archive URI and SHA-256 from checked-in evidence; it
          did not fetch the B2 object in the browser.
        </p>
        <dl className="kv">
          <dt>archive URI</dt>
          <dd className="mono">{JUDGE_EVIDENCE_PACK_ARCHIVE_URI}</dd>
          <dt>archive SHA-256</dt>
          <dd className="mono">{JUDGE_EVIDENCE_PACK_ARCHIVE_SHA256}</dd>
          <dt>rehydrate_source</dt>
          <dd className="mono">{JUDGE_EVIDENCE_PACK_REHYDRATE_SOURCE}</dd>
          <dt>provider_calls_during_rehydrate</dt>
          <dd className="mono">
            {String(JUDGE_EVIDENCE_PACK_PROVIDER_CALLS_DURING_REHYDRATE)}
          </dd>
          <dt>no_live_provider_call_during_rehydrate</dt>
          <dd className="mono">
            {String(
              JUDGE_EVIDENCE_PACK_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
            )}
          </dd>
        </dl>
      </div>

      {/* 7. Genblaze manifest evidence */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-genblaze-manifest"
        data-section-key="genblaze_manifest_evidence"
      >
        <h3>Genblaze manifest evidence</h3>
        <p className="hint">
          The Genblaze pipeline records what each generation attempt produced
          and verifies the stored manifest against the asset bytes. PS-028
          confirms the manifest fields agree across every checked-in source
          for the golden run.
        </p>
        <dl className="kv">
          <dt>run_id (manifest consistency)</dt>
          <dd className="mono">{JUDGE_EVIDENCE_PACK_RUN_ID}</dd>
          <dt>campaign_id (manifest consistency)</dt>
          <dd className="mono">{JUDGE_EVIDENCE_PACK_CAMPAIGN_ID}</dd>
          <dt>archive SHA-256 (manifest consistency)</dt>
          <dd className="mono">{JUDGE_EVIDENCE_PACK_ARCHIVE_SHA256}</dd>
        </dl>
      </div>

      {/* 8. B2 rehydrate proof */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-rehydrate-proof"
        data-section-key="b2_rehydrate_proof"
      >
        <h3>B2 rehydrate proof</h3>
        <p className="hint">
          PS-029 confirms the rehydrate used durable B2 archive evidence
          instead of a live provider rerun. The pack records the rehydrate
          facts verbatim from checked-in evidence.
        </p>
        <dl className="kv">
          <dt>rehydrate_source</dt>
          <dd className="mono">{JUDGE_EVIDENCE_PACK_REHYDRATE_SOURCE}</dd>
          <dt>provider_calls_during_rehydrate</dt>
          <dd className="mono">
            {String(JUDGE_EVIDENCE_PACK_PROVIDER_CALLS_DURING_REHYDRATE)}
          </dd>
          <dt>no_live_provider_call_during_rehydrate</dt>
          <dd className="mono">
            {String(
              JUDGE_EVIDENCE_PACK_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE,
            )}
          </dd>
        </dl>
      </div>

      {/* 9. Failure-as-Proof summary */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-failure-as-proof"
        data-section-key="failure_as_proof_summary"
      >
        <h3>Failure-as-Proof summary</h3>
        <ul className="infra-points judge-evidence-pack-failure-as-proof-points">
          {JUDGE_EVIDENCE_PACK_FAILURE_AS_PROOF_SUMMARY.map((point) => (
            <li key={point}>{point}</li>
          ))}
        </ul>
      </div>

      {/* 10. Public passport link */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-passport-link"
        data-section-key="public_passport_link"
      >
        <h3>Public passport link</h3>
        <p className="hint">
          PS-025 unlocked a narrow public passport path for this single
          golden run_id from checked-in evidence only. The local contract is
          verified; the public deployment remains pending.
        </p>
        <div className="btn-row">
          <a
            className="btn btn-primary"
            href={"/passport/" + JUDGE_EVIDENCE_PACK_RUN_ID}
            title="Open the verified golden demo Provenance Passport"
          >
            Open Golden Passport
          </a>
        </div>
      </div>

      {/* 11. Review / approval status */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-review-status"
        data-section-key="review_approval_status"
      >
        <h3>Review / approval status</h3>
        <dl className="kv">
          <dt>generated</dt>
          <dd className="mono">
            {String(JUDGE_EVIDENCE_PACK_REVIEW_STATUS.generated)}
          </dd>
          <dt>approved</dt>
          <dd className="mono">
            {String(JUDGE_EVIDENCE_PACK_REVIEW_STATUS.approved)}
          </dd>
        </dl>
        <p className="hint">{JUDGE_EVIDENCE_PACK_REVIEW_STATUS.note}</p>
      </div>

      {/* 12. Disclosure readiness notes */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-disclosure-notes"
        data-section-key="disclosure_readiness_notes"
      >
        <h3>Disclosure readiness notes</h3>
        <ul className="infra-points judge-evidence-pack-disclosure-points">
          {JUDGE_EVIDENCE_PACK_DISCLOSURE_NOTES.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </div>

      {/* 13. Truth boundary */}
      <section
        className="judge-evidence-pack-section judge-evidence-pack-truth-boundary"
        id="judge-evidence-pack-truth-boundary"
        data-section-key="truth_boundary"
      >
        <h3>Truth boundary</h3>
        <p className="truth-text">{JUDGE_EVIDENCE_PACK_TRUTH_BOUNDARY}</p>
        <div className="judge-evidence-pack-claim-boundary-grid">
          <div className="judge-evidence-pack-claim-boundary-col">
            <h4>Allowed claims</h4>
            <ul className="infra-points">
              {JUDGE_EVIDENCE_PACK_CLAIM_BOUNDARY_ALLOWED.map((claim) => (
                <li key={claim}>
                  <span className="pill ok">
                    <span className="dot" />
                    {claim}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div className="judge-evidence-pack-claim-boundary-col">
            <h4>Forbidden claims</h4>
            <ul className="infra-points">
              {JUDGE_EVIDENCE_PACK_CLAIM_BOUNDARY_FORBIDDEN.map((claim) => (
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

      {/* 14. Limitations */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-limitations"
        data-section-key="limitations"
      >
        <h3>Limitations</h3>
        <ul className="infra-points judge-evidence-pack-limitations-points">
          {JUDGE_EVIDENCE_PACK_LIMITATIONS.map((lim) => (
            <li key={lim}>{lim}</li>
          ))}
        </ul>
      </div>

      {/* 15. Next actions for judge / client */}
      <div
        className="judge-evidence-pack-section"
        id="judge-evidence-pack-next-actions"
        data-section-key="next_actions"
      >
        <h3>Next actions for judge / client</h3>
        <ul className="infra-points judge-evidence-pack-next-actions-points">
          {JUDGE_EVIDENCE_PACK_NEXT_ACTIONS.map((action) => (
            <li key={action}>{action}</li>
          ))}
        </ul>
      </div>

      {/* Proof chain */}
      <div
        className="judge-evidence-pack-proof-chain"
        id="judge-evidence-pack-proof-chain"
      >
        <h3>Proof chain</h3>
        <p className="hint">
          The ordered proof trail the pack summarizes. Each step cites the
          checked-in evidence that backs it.
        </p>
        <ol className="failure-timeline-list judge-evidence-pack-proof-list">
          {JUDGE_EVIDENCE_PACK_PROOF_CHAIN.map((step) => (
            <li
              key={step.key}
              className={"failure-timeline-event kind-" + step.kind}
              data-proof-key={step.key}
            >
              <span className="failure-timeline-event-idx">
                {String(step.idx).padStart(2, "0")}
              </span>
              <div className="failure-timeline-event-body">
                <div className="failure-timeline-event-head">
                  <h4 className="failure-timeline-event-title">
                    {step.title}
                  </h4>
                  <span className="pill ok">
                    <span className="dot" />
                    {KIND_LABEL[step.kind]}
                  </span>
                </div>
                <p className="failure-timeline-event-summary">
                  {step.summary}
                </p>
                <p className="hint muted-link">
                  sources: {step.sourceTags.join(" / ")}
                </p>
                {step.links.length > 0 && (
                  <div className="failure-timeline-event-links">
                    {step.links.map((href) => (
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

      {/* Route map */}
      <div
        className="judge-evidence-pack-route-map"
        id="judge-evidence-pack-route-map"
      >
        <h3>Route map</h3>
        <p className="hint">
          The pack links out to every implemented proof surface so a judge
          can step out of the pack and into the underlying surface.
        </p>
        <ul className="infra-points judge-evidence-pack-route-list">
          {JUDGE_EVIDENCE_PACK_ROUTES.map((route) => (
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

      {/* Source evidence files */}
      <div
        className="judge-evidence-pack-files"
        id="judge-evidence-pack-files"
      >
        <h3>Source evidence files</h3>
        <ul className="infra-points">
          {JUDGE_EVIDENCE_PACK_SOURCES.map((src) => (
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
          <code className="mono">{JUDGE_EVIDENCE_PACK_IMPLEMENTATION_ROADMAP}</code>
        </p>
      </div>

      {/* Deployment status */}
      <div
        className="judge-evidence-pack-deployment"
        id="judge-evidence-pack-deployment"
      >
        <h3>Deployment status</h3>
        <dl className="kv">
          <dt>local contract proof</dt>
          <dd className="mono">
            {String(JUDGE_EVIDENCE_PACK_LOCAL_CONTRACT_PROOF)}
          </dd>
          <dt>public deployment pending</dt>
          <dd className="mono">
            {String(JUDGE_EVIDENCE_PACK_PUBLIC_DEPLOYMENT_PENDING)}
          </dd>
          <dt>unlock scope</dt>
          <dd className="mono">{JUDGE_EVIDENCE_PACK_UNLOCK_SCOPE}</dd>
        </dl>
        <p className="hint">
          The local contract (FastAPI TestClient resolving the golden run_id
          from checked-in evidence) is verified by PS-025. The public Render
          deployment is not verified yet: the new backend must be deployed
          and the public URL verified end-to-end before this status changes.
        </p>
      </div>

      {isPage && (
        <div className="cockpit-cta-row" id="judge-evidence-pack-cta">
          <a
            className="btn btn-primary"
            href="/failure-timeline"
            title="Open the Failure-as-Proof Timeline (PS-030)"
          >
            Open Failure-as-Proof Timeline
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
            href="/provider-decision-intelligence"
            title="Open the Provider Decision Intelligence (PS-033)"
          >
            Open Provider Decision Intelligence
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
            href={"/passport/" + JUDGE_EVIDENCE_PACK_RUN_ID}
            title="Open the verified golden demo Provenance Passport"
          >
            Open Golden Passport
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
        PS-031 Judge Evidence Pack · fallback API base {DEFAULT_API_BASE_URL}
        {" "}· local browser export · no provider call, no live B2 read, no
        broad durable read, no browser-side B2 byte verification, no raw media
        byte claim, no zip claim.
      </p>
    </section>
  );

  if (!isPage) {
    return card;
  }

  return (
    <main className="cockpit judge-evidence-pack-page-wrap">
      <header className="cockpit-hero" id="top">
        <p className="eyebrow">ProofStudio · Judge Evidence Pack</p>
        <h1>The golden workflow, packaged for a judge or client</h1>
        <p className="thesis">
          One portable proof summary: run identity, B2 archive, Genblaze
          manifest, B2 rehydrate, Failure-as-Proof, disclosure, limitations.
        </p>
        <p className="hero-explainer">
          The Judge Evidence Pack turns the existing ProofStudio proof chain
          into a readable pack a judge or client can take away. Every value
          is sourced verbatim from the checked-in evidence (PS-021, PS-024,
          PS-025, PS-026, PS-027, PS-028, PS-029, PS-030). The pack is
          generated locally in the browser and exports a pack JSON and a pack
          README / Markdown. It does not call any provider, does not read any
          B2 object, does not include raw media bytes, and does not produce a
          zip export. The local contract is verified; the public deployment
          remains pending.
        </p>
      </header>
      {card}
    </main>
  );
}

function triggerBrowserDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.rel = "noopener";
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  // Revoke on the next tick so the click has time to start the download.
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function linkLabel(href: string): string {
  if (href === "/failure-timeline") return "Failure-as-Proof Timeline";
  if (href === "/b2-rehydrate-comparison") return "B2 Rehydrate Comparison";
  if (href === "/manifest-verification") return "Manifest Verification";
  if (href === "/b2-evidence") return "B2 Evidence Explorer";
  if (href === "/genblaze-pipeline") return "Genblaze Pipeline Graph";
  if (href.startsWith("/passport/")) return "Golden Passport";
  if (href === "/evidence-pack") return "Judge Evidence Pack";
  if (href === "/") return "Judge Cockpit Home";
  return href;
}
