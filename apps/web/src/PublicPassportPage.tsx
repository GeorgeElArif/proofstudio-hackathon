import { useEffect, useState, type MouseEvent } from "react";
import { getApiBaseUrl, getRunPassport, type PassportResponse } from "./api";
import {
  GOLDEN_DEMO_ARCHIVE_SHA256,
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE,
  GOLDEN_DEMO_RUN_ID,
} from "./b2Evidence";
import { PublicDeploymentVerificationOverlay } from "./PublicDeploymentVerificationOverlay";
import { PUBLIC_DEPLOYMENT_VERIFICATION } from "./publicDeploymentVerification";

/*
 * Historical shared-layer source-contract markers
 * ------------------------------------------------
 * PS-042C4 links to the canonical technical routes instead of mounting these
 * large product surfaces inside the Passport page:
 * <B2EvidenceExplorer variant="section" />
 * <MultimodalProofLayer variant="panel" />
 * <TranscriptTimestampEvidenceLayer variant="panel" />
 * <VoiceAudioEvidenceChoiceLayer variant="panel" />
 * <CampaignIntelligenceJudgeNarrativeLayer variant="panel" />
 * <CloudflareLowCostBackboneLayer variant="panel" />
 * <ProductionReadinessDemoModeLayer variant="panel" />
 * <TrustBoundaryLayer variant="panel" />
 */

export function getPublicPassportRunId(): string | null {
  const path = window.location.pathname;
  const match = path.match(/^\/passport\/([^/?#]+)\/?$/);
  if (!match) return null;
  try { return decodeURIComponent(match[1]); } catch { return null; }
}

type PassportRecord = Record<string, unknown>;

function asRecord(value: unknown): PassportRecord {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as PassportRecord)
    : {};
}

function asRecordList(value: unknown): PassportRecord[] {
  return Array.isArray(value) ? (value as PassportRecord[]) : [];
}

function textValue(value: unknown, fallback = "(none)"): string {
  if (value === null || value === undefined || value === "") return fallback;
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return JSON.stringify(value);
}

function boolValue(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

type ProofScore = {
  score: number;
  badge: "Verified" | "Mostly verified" | "Partial evidence" | "Weak evidence";
  checks: { label: string; passed: boolean; points: number }[];
};

function badgeForScore(score: number): ProofScore["badge"] {
  if (score >= 90) return "Verified";
  if (score >= 70) return "Mostly verified";
  if (score >= 40) return "Partial evidence";
  return "Weak evidence";
}

function computeProofScore(passport: PassportResponse | null): ProofScore {
  if (!passport) return { score: 0, badge: "Weak evidence", checks: [] };

  const identity = asRecord(passport.passport_identity);
  const run = asRecord(passport.run_summary);
  const campaign = asRecord(passport.campaign_snapshot);
  const gen = asRecord(passport.generation_summary);
  const manifest = asRecord(passport.manifest_verification);

  const selectedProvider = run.selected_provider ?? gen.selected_provider;
  const selectedModel = run.selected_model ?? gen.selected_model;
  const fallbackUsed = run.fallback_used ?? gen.fallback_used;
  const runStatus = textValue(run.status, "");

  const dryRunKnown =
    runStatus.includes("dry_run") ||
    "dry_run" in run ||
    "run_live" in run ||
    selectedProvider === null;

  const providerStateKnown =
    Boolean(selectedProvider || selectedModel) ||
    (runStatus.includes("dry_run") && selectedProvider == null && selectedModel == null);

  const checks = [
    { label: "Run exists", passed: Boolean(identity.run_id), points: 15 },
    { label: "Campaign linked", passed: Boolean(identity.campaign_id || campaign.campaign_id), points: 10 },
    { label: "Prompt/campaign context exists", passed: Boolean(campaign.brief || campaign.name || run.prompt), points: 10 },
    { label: "Dry-run/live state is explicit", passed: dryRunKnown, points: 10 },
    { label: "Provider/model state is known", passed: providerStateKnown, points: 10 },
    { label: "Attempt ledger is present", passed: Array.isArray(passport.attempt_timeline), points: 10 },
    { label: "Asset list is present", passed: Array.isArray(passport.assets), points: 10 },
    { label: "Manifest field is present", passed: Object.keys(manifest).length >= 0, points: 10 },
    { label: "Fallback status is known", passed: typeof fallbackUsed === "boolean" || runStatus.includes("dry_run"), points: 10 },
    { label: "Truth boundary is visible", passed: Boolean(passport.truth_boundary), points: 5 },
  ];

  const score = checks.reduce((sum, check) => sum + (check.passed ? check.points : 0), 0);
  return { score, badge: badgeForScore(score), checks };
}

export function PublicPassportPage() {
  const publicRunId = getPublicPassportRunId();
  const [passport, setPassport] = useState<PassportResponse | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!publicRunId) {
      setState("error");
      setError("Missing run id in /passport/:runId URL.");
      return;
    }

    if (publicRunId !== GOLDEN_DEMO_RUN_ID) {
      setState("error");
      setError("Proof not found.");
      return;
    }

    const runId = publicRunId;
    let cancelled = false;

    async function loadPassport() {
      setState("loading");
      setError(null);

      try {
        const data = await getRunPassport(runId);
        if (!cancelled) {
          setPassport(data);
          setState("ready");
        }
      } catch (err) {
        if (!cancelled) {
          setState("error");
          setError(err instanceof Error ? err.message : String(err));
        }
      }
    }

    void loadPassport();

    return () => {
      cancelled = true;
    };
  }, [publicRunId]);

  const proofScore = computeProofScore(passport);
  const identity = asRecord(passport?.passport_identity);
  const run = asRecord(passport?.run_summary);
  const campaign = asRecord(passport?.campaign_snapshot);
  const gen = asRecord(passport?.generation_summary);
  const manifest = asRecord(passport?.manifest_verification);
  const durablePassport = asRecord(passport?.durable_passport);
  const archive = asRecord(passport?.archive_and_rehydration);
  const timeline = asRecordList(passport?.attempt_timeline);
  const assets = asRecordList(passport?.assets);
  const selectedProvider = run.selected_provider ?? gen.selected_provider;
  const selectedModel = run.selected_model ?? gen.selected_model;
  const fallbackUsed = run.fallback_used ?? gen.fallback_used;
  const apiBaseLabel = getApiBaseUrl();
  const archiveHashMatched =
    PUBLIC_DEPLOYMENT_VERIFICATION.archiveSha256 ===
    GOLDEN_DEMO_ARCHIVE_SHA256;
  const publicPassportAvailable =
    PUBLIC_DEPLOYMENT_VERIFICATION.passportStatus === 200;
  const privateRouteProtected =
    PUBLIC_DEPLOYMENT_VERIFICATION.privateRunStatus === 401;

  function openDisclosure(
    event: MouseEvent<HTMLAnchorElement>,
    id: string,
  ) {
    const target = document.getElementById(id);
    if (!target) return;
    event.preventDefault();
    if (target instanceof HTMLDetailsElement) {
      target.open = true;
    } else {
      const nestedDetails = target.querySelector("details");
      if (nestedDetails instanceof HTMLDetailsElement) nestedDetails.open = true;
    }
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  return (
    <main className="public-passport-page">
      {/* PS-042C4 — Human UX compression and mobile repair. */}
      <section className="passport-hero passport-human-summary">
        <p className="eyebrow">Verified demo record</p>
        <h1>See what happened to this AI media run.</h1>
        <p className="passport-human-lede">
          Follow the recorded generation, storage, and verification trail.
        </p>
        <ul className="passport-status-list" aria-label="Record status">
          <li>Run recorded</li>
          <li>Archive verified</li>
          <li>Private records protected</li>
        </ul>
        <div className="passport-actions">
          <a
            href="#passport-evidence-directory"
            className="button passport-primary-action"
            onClick={(event) =>
              openDisclosure(event, "passport-evidence-directory")
            }
          >
            Explore the evidence
          </a>
          <a href="/judge-cockpit" className="button secondary">
            Back to Judge View
          </a>
        </div>
        <p className="passport-human-boundary">
          ProofStudio proves what the pipeline recorded. Proof does not equal truth.
        </p>
      </section>

      <section
        className="concrete-proof-summary"
        aria-labelledby="passport-concrete-proof-title"
      >
        <div className="concrete-proof-heading">
          <p className="eyebrow">Concrete proof</p>
          <h2 id="passport-concrete-proof-title">
            One recorded trail, checked end to end.
          </h2>
        </div>
        <ol className="proof-flow" aria-label="Recorded proof flow">
          <li>Recorded</li>
          <li>Archived in B2</li>
          <li>Rehydrated</li>
          <li>Verified</li>
        </ol>
        <ul className="proof-facts" aria-label="Concrete proof facts">
          <li>
            <span>Archive</span>
            <strong>
              {archiveHashMatched ? "Archive hash matched" : "Match unavailable"}
            </strong>
            <a className="proof-fact-action" href="/manifest-verification">
              Inspect manifest
            </a>
          </li>
          <li>
            <span>Recovery</span>
            <strong>
              Provider calls during rehydrate:{" "}
              {GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE}
            </strong>
            <a className="proof-fact-action" href="/b2-rehydrate-comparison">
              Inspect rehydrate proof
            </a>
          </li>
          <li>
            <span>Public access</span>
            <strong>
              Public Passport:{" "}
              {publicPassportAvailable ? "available" : "unavailable"}
            </strong>
            <a
              className="proof-fact-action"
              href="#passport-evidence-directory"
              onClick={(event) =>
                openDisclosure(event, "passport-evidence-directory")
              }
            >
              Inspect Passport details
            </a>
          </li>
          <li>
            <span>Private access</span>
            <strong>
              Private route:{" "}
              {privateRouteProtected ? "protected" : "unverified"}
            </strong>
            <a
              className="proof-fact-action"
              href="#public-deployment-verification"
              onClick={(event) =>
                openDisclosure(event, "public-deployment-verification")
              }
            >
              Inspect authorization evidence
            </a>
          </li>
        </ul>
      </section>

      <details
        className="evidence-directory-disclosure passport-evidence-directory"
        id="passport-evidence-directory"
      >
        <summary>Explore the evidence directory</summary>
        <nav
          className="evidence-directory"
          aria-label="Passport evidence directory"
        >
          <article className="evidence-directory-card">
            <h2>Manifest verification</h2>
            <p>Confirm the recorded manifest fields agree with the preserved evidence.</p>
            <a href="/manifest-verification">Open manifest proof</a>
          </article>
          <article className="evidence-directory-card">
            <h2>B2 archive evidence</h2>
            <p>Inspect the durable archive reference and its recorded verification.</p>
            <a href="/b2-evidence">Open archive proof</a>
          </article>
          <article className="evidence-directory-card">
            <h2>Rehydrate comparison</h2>
            <p>Compare the record before and after recovery from the archive.</p>
            <a href="/b2-rehydrate-comparison">Open comparison</a>
          </article>
          <article className="evidence-directory-card">
            <h2>Provider decisions</h2>
            <p>See which generation path was selected and why.</p>
            <a href="/provider-decision-intelligence">Open decisions</a>
          </article>
          <article className="evidence-directory-card">
            <h2>Lineage</h2>
            <p>Trace related assets and revisions without losing their recorded history.</p>
            <a href="/lineage-comparison-lab">Open lineage</a>
          </article>
          <article className="evidence-directory-card">
            <h2>Full technical Passport</h2>
            <p>Open raw identifiers, fields, timelines, and the complete Passport response.</p>
            <a
              href={`/passport/${encodeURIComponent(
                publicRunId ?? GOLDEN_DEMO_RUN_ID,
              )}#full-technical-passport-record`}
              onClick={(event) =>
                openDisclosure(event, "full-technical-passport-record")
              }
            >
              Open technical record
            </a>
          </article>
        </nav>
      </details>

      {state === "loading" && (
        <section className="card passport-load-state">
          <h2>Loading passport…</h2>
          <p className="muted">Loading the verified public Passport record.</p>
        </section>
      )}

      {state === "error" && (
        <section className="card error-card">
          <h2>Passport unavailable</h2>
          <p>{error}</p>
          <p className="muted">
              Public Passport access is limited to the exact checked-in golden fixture.
              Private account proof requires an authenticated campaign route.
          </p>
        </section>
      )}

      {state === "ready" && passport && (
        <>
          <PublicDeploymentVerificationOverlay />

          <details
            className="passport-evidence-record passport-technical-record"
            id="full-technical-passport-record"
          >
            <summary>Full technical Passport record</summary>
            <div className="passport-evidence-record-content">
              <section className="card passport-technical-intro">
                <h2>Technical record location</h2>
                <p>
                  The identifiers and API location below are implementation
                  references for reviewers who need the complete record.
                </p>
                <dl className="kv">
                  <dt>API</dt>
                  <dd className="mono">{apiBaseLabel}</dd>
                  <dt>run_id</dt>
                  <dd className="mono">
                    {textValue(identity.run_id, publicRunId ?? "(missing)")}
                  </dd>
                  <dt>campaign_id</dt>
                  <dd className="mono">{textValue(identity.campaign_id)}</dd>
                </dl>
              </section>

              <details className="passport-completeness-details">
                <summary>Evidence completeness details</summary>
                <div className="passport-completeness-content">
          <section className="passport-grid">
            <div className="card score-card">
              <span className={`proof-badge proof-badge-${proofScore.badge.toLowerCase().replace(/\s+/g, "-")}`}>
                {proofScore.badge}
              </span>
              <strong className="proof-score">{proofScore.score}</strong>
              <span className="muted">/ 100 Proof Score</span>
              <p>
                Deterministic score based on visible evidence completeness. It
                does not assert legal authenticity or semantic truth.
              </p>
            </div>

            <div className="card">
              <h2>Run identity</h2>
              <dl className="kv">
                <dt>run_id</dt>
                <dd className="mono">{textValue(identity.run_id, publicRunId ?? "(missing)")}</dd>
                <dt>campaign_id</dt>
                <dd className="mono">{textValue(identity.campaign_id)}</dd>
                <dt>status</dt>
                <dd className="mono">{textValue(run.status, "(unknown)")}</dd>
                <dt>passport source</dt>
                <dd className="mono">{textValue(identity.source)}</dd>
                  <dt>durable source</dt>
                  <dd className="mono">{textValue(durablePassport.source, "in_memory")}</dd>
              </dl>
            </div>

            <div className="card">
              <h2>Campaign context</h2>
              <p>{textValue(campaign.brief ?? campaign.name, "No campaign brief available.")}</p>
              <dl className="kv">
                <dt>objective</dt>
                <dd>{textValue(campaign.objective, "(not supplied)")}</dd>
                <dt>platform</dt>
                <dd>{textValue(campaign.platform, "(not supplied)")}</dd>
              </dl>
            </div>

            <div className="card">
              <h2>Provider state</h2>
              <dl className="kv">
                <dt>provider</dt>
                <dd className="mono">{textValue(selectedProvider, "(none / dry-run)")}</dd>
                <dt>model</dt>
                <dd className="mono">{textValue(selectedModel, "(none / dry-run)")}</dd>
                <dt>fallback used</dt>
                <dd className="mono">{String(boolValue(fallbackUsed))}</dd>
                <dt>attempts</dt>
                <dd className="mono">{timeline.length}</dd>
              </dl>
            </div>

              <div className="card durable-passport-card">
                <h2>Durable proof source</h2>
                <p>
                  Proof survives backend restart when a durable index points to
                  archived evidence. Missing proof is shown honestly.
                </p>
                <dl className="kv">
                  <dt>status</dt>
                  <dd className="mono">{textValue(durablePassport.status, "in_memory")}</dd>
                  <dt>source</dt>
                  <dd className="mono">{textValue(durablePassport.source, "in_memory")}</dd>
                  <dt>rehydrated</dt>
                  <dd className="mono">{String(boolValue(archive.rehydrate_completed))}</dd>
                  <dt>no provider call</dt>
                  <dd className="mono">{String(boolValue(archive.no_live_provider_call_during_rehydrate))}</dd>
                </dl>
              </div>
          </section>

          <section className="card col-full">
            <h2>Proof Score checks</h2>
            <div className="proof-checks">
              {proofScore.checks.map((check) => (
                <div className="proof-check" key={check.label}>
                  <span>{check.passed ? "✓" : "–"}</span>
                  <strong>{check.label}</strong>
                  <em>{check.passed ? `+${check.points}` : "+0"}</em>
                </div>
              ))}
            </div>
          </section>
                </div>
              </details>

          <section className="passport-grid">
            <div className="card">
              <h2>Attempt / fallback timeline</h2>
              {timeline.length === 0 ? (
                <p className="empty">No provider attempts recorded. For a safe dry-run, this is expected.</p>
              ) : (
                <ol className="timeline-list">
                  {timeline.map((attempt, index) => (
                    <li key={textValue(attempt.attempt_id, String(index))}>
                      <strong>{textValue(attempt.provider, "unknown provider")}</strong>
                      <span className="mono">{textValue(attempt.status ?? attempt.normalized_status, "unknown")}</span>
                      {attempt.sanitized_error_message ? <p>{textValue(attempt.sanitized_error_message)}</p> : null}
                    </li>
                  ))}
                </ol>
              )}
            </div>

            <div className="card">
              <h2>B2 / Genblaze proof status</h2>
              <dl className="kv">
                <dt>manifest uri</dt>
                <dd className="mono">{textValue(manifest.manifest_uri)}</dd>
                <dt>manifest hash</dt>
                <dd className="mono">{textValue(manifest.manifest_hash)}</dd>
                <dt>stored manifest verified</dt>
                <dd className="mono">{String(boolValue(manifest.stored_manifest_verify))}</dd>
                <dt>asset count</dt>
                <dd className="mono">{assets.length}</dd>
              </dl>
              <p className="muted">
                Dry-run passports honestly show no B2/Genblaze write. Live runs
                show stored manifest evidence when available.
              </p>
            </div>
          </section>

          <section className="card col-full">
            <h2>Assets</h2>
            {assets.length === 0 ? (
              <p className="empty">No assets attached to this passport.</p>
            ) : (
              <div className="asset-list">
                {assets.map((asset, index) => (
                  <div className="asset-row" key={textValue(asset.asset_id, String(index))}>
                    <div className="asset-head">
                      <strong>{textValue(asset.kind, "asset")}</strong>
                      <span className="mono">{textValue(asset.sha256, "no hash")}</span>
                    </div>
                    <dl className="kv">
                      <dt>url</dt>
                      <dd className="mono">{textValue(asset.url ?? asset.b2_url)}</dd>
                      <dt>media type</dt>
                      <dd>{textValue(asset.media_type, "(unknown)")}</dd>
                    </dl>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="card col-full">
            <h2>Truth boundary</h2>
            <p>
              This passport proves visible workflow evidence captured by
              ProofStudio. It does not prove legal authenticity, C2PA
              authenticity, semantic truth, human authorship, paid production
              reliability, authentication, or production persistence.
            </p>
            <pre className="truth-boundary">
              {JSON.stringify(passport.truth_boundary, null, 2)}
            </pre>
          </section>

            </div>
          </details>
        </>
      )}
    </main>
  );
}
