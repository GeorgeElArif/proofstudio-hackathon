// PS-036 Archive / Rehydrate / B2 Audit Vault.
//
// A dedicated, judge-facing product surface that frames Backblaze B2 as the
// durable system of record for the verified golden run. It gathers, in one
// place, the archive reference, archive SHA-256, manifest hash when present,
// rehydrate source, the zero-provider-call rehydrate proof, the B2 evidence
// status, the local verification status, an honest not-claimed / unknown
// panel, and a persistent truth-boundary panel.
//
// All displayed values come from apps/web/src/b2AuditVault.ts, which reuses
// the verified golden B2 archive / rehydrate constants from
// apps/web/src/b2Evidence.ts (PS-026) read-only and adds the manifest
// reference / hash sourced verbatim from the PS-024 golden manifest. No value
// is invented here and nothing is fetched live from B2.
//
// The component exposes a `variant` prop so the same surface can render as a
// full page (via the /b2-audit-vault route in App.tsx) or as an inline
// section. It performs no network call, calls no provider, reads no live B2
// object, writes no B2 object, and performs no broad B2 scan. It is not live
// B2 verification, not Object Lock, not tamper-proof, not production
// security, not legal authenticity, and not semantic truth.

import {
  B2_AUDIT_VAULT_AUDIT_NOTES_HEADING,
  B2_AUDIT_VAULT_B2_EVIDENCE_HEADING,
  B2_AUDIT_VAULT_BOUNDARY_RED_LINES,
  B2_AUDIT_VAULT_HIDDEN_GIT_RULE,
  B2_AUDIT_VAULT_LOCAL_CONTRACT_PROOF,
  B2_AUDIT_VAULT_LOCAL_VERIFICATION_NOTES,
  B2_AUDIT_VAULT_LOCAL_VERIFICATION_SUMMARY,
  B2_AUDIT_VAULT_NOT_CLAIMED,
  B2_AUDIT_VAULT_PUBLIC_DEPLOYMENT_PENDING,
  B2_AUDIT_VAULT_RECORDS,
  B2_AUDIT_VAULT_RUN_ID,
  B2_AUDIT_VAULT_SOURCE_GOLDEN_MANIFEST,
  B2_AUDIT_VAULT_TRUTH_BOUNDARY,
} from "./b2AuditVault";
import { DEFAULT_API_BASE_URL } from "./api";
import { TrustBoundaryLayer } from "./TrustBoundaryLayer";
import { MultimodalProofLayer } from "./MultimodalProofLayer";
import { TranscriptTimestampEvidenceLayer } from "./TranscriptTimestampEvidenceLayer";
import { CampaignIntelligenceJudgeNarrativeLayer } from "./CampaignIntelligenceJudgeNarrativeLayer";
import { CloudflareLowCostBackboneLayer } from "./CloudflareLowCostBackboneLayer";
import { ProductionReadinessDemoModeLayer } from "./ProductionReadinessDemoModeLayer";
import { VoiceAudioEvidenceChoiceLayer } from "./VoiceAudioEvidenceChoiceLayer";

type B2AuditVaultVariant = "page" | "section";

export function B2AuditVault({
  variant = "page",
}: {
  variant?: B2AuditVaultVariant;
}) {
  const isPage = variant === "page";

  const card = (
    <section
      className={
        isPage
          ? "card col-full b2-audit-vault b2-audit-vault-page"
          : "card col-full b2-audit-vault"
      }
      id="b2-audit-vault"
      aria-label="Archive / Rehydrate / B2 Audit Vault"
    >
      <header className="b2-audit-vault-head">
        <span className="infra-tag">Backblaze B2</span>
        <h2>Archive / Rehydrate / B2 Audit Vault</h2>
        <p className="subhead">B2 system of record</p>
      </header>

      <p className="subhead">
        One canonical vault over the verified durable evidence behind the
        golden demo run. Backblaze B2 is surfaced as the durable system of
        record for the verified golden run: the archive reference, archive
        SHA-256, manifest hash when present, rehydrate source, and zero
        provider calls during rehydrate. Every value is sourced verbatim from
        accepted checked-in evidence; nothing is fetched live from B2.
      </p>

      {/* Vault records: archive reference, archive sha256, manifest hash,
          rehydrate source, provider calls during rehydrate, no live provider
          call during rehydrate, B2 evidence status. */}
      <div className="b2-audit-vault-grid">
        {B2_AUDIT_VAULT_RECORDS.map((record) => (
          <div className="b2-audit-vault-block" key={record.record_key}>
            <h3>{record.label}</h3>
            <dl className="kv">
              <dt>{record.label}</dt>
              <dd className="mono b2-audit-vault-value">
                {record.available ? record.value : "not available"}
              </dd>
              <dt>available</dt>
              <dd className="mono">{String(record.available)}</dd>
              <dt>verification</dt>
              <dd className="mono">{record.verification}</dd>
              <dt>source paths</dt>
              <dd>
                <ul className="infra-points">
                  {record.source_paths.map((p) => (
                    <li key={p}>
                      <code className="mono">{p}</code>
                    </li>
                  ))}
                </ul>
              </dd>
            </dl>
            {!record.available && (
              <p className="hint">
                This record is honestly not available in accepted evidence. No
                value is fabricated.
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Rehydrate / provider-call proof, surfaced as its own read so a
          judge never mistakes durability for a fresh live run. */}
      <div className="b2-audit-vault-block">
        <h3>rehydrate source</h3>
        <p>
          The verified golden run rehydrates from Backblaze B2 archive content
          (rehydrate source = <code className="mono">b2_rehydrated</code>) with{" "}
          <strong>zero</strong> provider calls during rehydrate. The vault
          records this verbatim: provider calls during rehydrate = 0 and no
          live provider call during rehydrate = true.
        </p>
        <p className="hint">
          This is durability without a live provider rerun. It is not live B2
          verification: the vault did not fetch or hash the B2 object in the
          browser.
        </p>
      </div>

      {/* B2 evidence status. */}
      <div className="b2-audit-vault-block" id="b2-audit-vault-b2-evidence-status">
        <h3>B2 evidence status</h3>
        <dl className="kv">
          <dt>B2 evidence</dt>
          <dd className="mono">present</dd>
          <dt>local contract proof</dt>
          <dd className="mono">{String(B2_AUDIT_VAULT_LOCAL_CONTRACT_PROOF)}</dd>
          <dt>public deployment pending</dt>
          <dd className="mono">
            {String(B2_AUDIT_VAULT_PUBLIC_DEPLOYMENT_PENDING)}
          </dd>
        </dl>
        <p className="hint">
          B2 evidence is present over accepted checked-in evidence (PS-021 /
          PS-026 recorded the archive reference, archive SHA-256, and rehydrate
          proof). The local contract is verified; the public deployment remains
          pending.
        </p>
      </div>

      {/* Local verification status. */}
      <div className="b2-audit-vault-block" id="b2-audit-vault-local-verification">
        <h3>local verification</h3>
        <p>{B2_AUDIT_VAULT_LOCAL_VERIFICATION_SUMMARY}</p>
        <ul className="infra-points">
          {B2_AUDIT_VAULT_LOCAL_VERIFICATION_NOTES.map((note) => (
            <li key={note}>
              <code className="mono">{note}</code>
            </li>
          ))}
        </ul>
        <p className="hint">
          <div className="proof-card">
            <h3>Audit contract vocabulary</h3>
            <ul>
              <li>no live provider call during rehydrate</li>
              <li>not production security</li>
            </ul>
          </div>

          local verification, not live B2 verification. The vault records what
          the pipeline already captured; it does not re-fetch or re-hash live
          B2 bytes.
        </p>
      </div>

      {/* Not-claimed / unknown status panel. */}
      <div className="b2-audit-vault-block" id="b2-audit-vault-not-claimed">
        <h3>not claimed / unknown</h3>
        <p className="hint">
          The vault proves only what the pipeline recorded. The following are
          not claimed:
        </p>
        <div className="non-claims">
          {B2_AUDIT_VAULT_NOT_CLAIMED.map((nc) => (
            <span className="pill warn" key={nc}>
              <span className="dot" />
              {nc}
            </span>
          ))}
        </div>
      </div>

      {/* notes / audit contract anchors. */}
      <div className="b2-audit-vault-block" id="b2-audit-vault-notes">
        <h3>{B2_AUDIT_VAULT_AUDIT_NOTES_HEADING}</h3>
        <dl className="kv">
          <dt>{B2_AUDIT_VAULT_B2_EVIDENCE_HEADING}</dt>
          <dd className="mono">present</dd>
          <dt>broad B2 reads</dt>
          <dd className="mono">no broad B2 reads</dd>
          <dt>hidden Git flags</dt>
          <dd className="mono">{B2_AUDIT_VAULT_HIDDEN_GIT_RULE}</dd>
          <dt>golden run id</dt>
          <dd className="mono">{B2_AUDIT_VAULT_RUN_ID}</dd>
          <dt>golden manifest</dt>
          <dd className="mono">{B2_AUDIT_VAULT_SOURCE_GOLDEN_MANIFEST}</dd>
        </dl>
      </div>

      {/* Boundary red lines (stated as non-claims). */}
      <div className="b2-audit-vault-block" id="b2-audit-vault-red-lines">
        <h3>boundary red lines</h3>
        <ul className="infra-points">
          {B2_AUDIT_VAULT_BOUNDARY_RED_LINES.map((line) => (
            <li key={line}>
              <code className="mono">{line}</code>
            </li>
          ))}
        </ul>
      </div>

      {/* Persistent truth-boundary panel (spec section 11, verbatim). */}
      <section
        className="b2-audit-vault-truth-boundary"
        id="b2-audit-vault-truth-boundary"
      >
        <h3>truth boundary</h3>
        <p className="truth-text">{B2_AUDIT_VAULT_TRUTH_BOUNDARY}</p>
      </section>

      {isPage && (
        <div className="cockpit-cta-row">
          <a className="btn" href="/" title="Back to Judge Cockpit Home">
            Back to Judge Cockpit Home
          </a>
          <a
            className="btn btn-primary"
            href={"/passport/" + B2_AUDIT_VAULT_RUN_ID}
            title="Open the golden Provenance Passport"
          >
            Open Golden Provenance Passport
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
            href="/manifest-verification"
            title="Open the Manifest Verification Panel (PS-028)"
          >
            Open Manifest Verification Panel
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
        PS-036 Archive / Rehydrate / B2 Audit Vault · fallback API base{" "}
        {DEFAULT_API_BASE_URL} · no provider call, no live B2 read, no B2 write,
        no broad B2 scan.
      </p>
    </section>
  );

  if (!isPage) {
    return card;
  }

  return (
    <main className="cockpit b2-audit-vault-page-wrap">
      <header className="cockpit-hero" id="top">
        <p className="eyebrow">ProofStudio · Archive / Rehydrate / B2 Audit Vault</p>
        <h1>Archive / Rehydrate / B2 Audit Vault</h1>
        <p className="thesis">B2 system of record</p>
        <p className="hero-explainer">
          The Archive / Rehydrate / B2 Audit Vault frames Backblaze B2 as the
          durable system of record for the verified golden run. In one place a
          reviewer or judge can read the archive reference, archive SHA-256,
          manifest hash, rehydrate source, the zero-provider-call rehydrate
          proof, the B2 evidence status, the local verification status, an
          honest not-claimed panel, and a persistent truth-boundary panel.
        </p>
      </header>
      {card}
    </main>
  );
}
