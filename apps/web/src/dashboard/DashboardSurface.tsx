import { useCallback, useEffect, useMemo, useState } from "react";
import { loadDashboardModel } from "./dashboardClient";
import type {
  DashboardAction,
  DashboardCampaignSummary,
  DashboardDataSourceLabel,
  DashboardModel,
  DashboardProofLayerStatus,
  DashboardProofLayerStatusValue,
  DashboardSessionState,
} from "./dashboardData";

type LoadState =
  | { state: "loading"; model: null; error: null }
  | { state: "ready"; model: DashboardModel; error: null }
  | { state: "error"; model: null; error: string };

type EvidenceStage = {
  key: string;
  phase: string;
  label: string;
  status: DashboardProofLayerStatusValue;
  source: DashboardDataSourceLabel;
  detail: string;
  href?: string;
};

function toneForSource(source: DashboardDataSourceLabel): string {
  if (source.kind === "auth_session" || source.kind === "proof_api" || source.kind === "account_campaign_store") return "ok";
  if (source.kind === "checked_in_fixture" || source.kind === "demo_fixture") return "info";
  if (source.kind === "not_implemented") return "warn";
  return "danger";
}

function toneForStatus(status: DashboardProofLayerStatusValue): string {
  if (status === "available") return "ok";
  if (status === "not_implemented" || status === "not_captured") return "warn";
  if (status === "not_claimed") return "neutral";
  return "danger";
}

function DashboardPill({ tone, children }: { tone: string; children: React.ReactNode }) {
  return (
    <span className={`dashboard-pill dashboard-pill-${tone}`}>
      <span className="dashboard-pill-dot" aria-hidden="true" />
      {children}
    </span>
  );
}

function SourceBadge({ source }: { source: DashboardDataSourceLabel }) {
  return <DashboardPill tone={toneForSource(source)}>{source.kind}</DashboardPill>;
}

function sessionHeading(session: DashboardSessionState): string {
  if (session.state === "authenticated") return session.userLabel ?? "Authenticated";
  if (session.state === "unauthenticated") return "No active session";
  if (session.state === "runtime_unavailable") return "Unavailable";
  if (session.state === "network_error") return "Network error";
  return "Checking";
}

function campaignListHeading(model: DashboardModel): string {
  const list = model.campaignList;
  if (list.state === "available") return `${list.realAccountCampaigns.length} linked`;
  if (list.state === "available_empty") return "Available · 0 linked";
  if (list.state === "unauthenticated") return "Sign in required";
  if (list.state === "error") return "Request failed";
  return "Unavailable";
}

function ActionLink({ action, label }: { action: DashboardAction; label?: string }) {
  return (
    <a
      aria-disabled={action.disabled ? "true" : undefined}
      className={`dashboard-action ${action.disabled ? "dashboard-action-disabled" : ""}`}
      href={action.disabled ? undefined : action.href}
      title={action.detail}
    >
      <span className="dashboard-action-label">{label ?? action.label}</span>
      <SourceBadge source={action.source} />
      <span className="dashboard-action-arrow" aria-hidden="true">↗</span>
    </a>
  );
}

function MobileNavigation() {
  return (
    <details className="dashboard-mobile-menu">
      <summary aria-label="Open dashboard navigation">
        <span>Menu</span><span aria-hidden="true">＋</span>
      </summary>
      <nav aria-label="Mobile dashboard navigation">
        <a href="#dashboard-command-center">Command</a>
        <a href="#fixture-proof">Proof</a>
        <a href="#source-integrity">Sources</a>
        <a href="#account-campaigns">Account</a>
      </nav>
    </details>
  );
}

function DashboardNavigation() {
  return (
    <header className="dashboard-nav">
      <a className="dashboard-brand" href="/" aria-label="ProofStudio home">
        <span className="dashboard-brand-mark" aria-hidden="true">P</span>
        <span><strong>ProofStudio</strong><small>Dashboard</small></span>
      </a>
      <nav className="dashboard-desktop-nav" aria-label="Dashboard navigation">
        <a href="#dashboard-command-center">Command</a>
        <a href="#fixture-proof">Proof</a>
        <a href="#source-integrity">Sources</a>
        <a href="#account-campaigns">Account</a>
      </nav>
      <a className="dashboard-nav-room" href="/campaign-proof-room">Proof Room</a>
      <MobileNavigation />
    </header>
  );
}

function SourceStrip({ model }: { model: DashboardModel }) {
  return (
    <section className="dashboard-source-strip" aria-label="Compact source state">
      <article>
        <span>Session</span>
        <strong>{sessionHeading(model.session)}</strong>
        <SourceBadge source={model.session.source} />
      </article>
      <article>
        <span>Proof runtime</span>
        <strong>{model.proofApi.state === "available" ? "Reachable" : "Unavailable"}</strong>
        <SourceBadge source={model.proofApi.source} />
      </article>
      <article>
        <span>Account campaigns</span>
        <strong>{campaignListHeading(model)}</strong>
        <SourceBadge source={model.campaignList.source} />
      </article>
    </section>
  );
}

function getLayer(
  layers: readonly DashboardProofLayerStatus[],
  key: DashboardProofLayerStatus["key"],
) {
  return layers.find((layer) => layer.key === key);
}

function evidenceStages(campaign: DashboardCampaignSummary): EvidenceStage[] {
  const manifest = getLayer(campaign.proofLayers, "genblaze_manifest");
  const archive = getLayer(campaign.proofLayers, "b2_archive");
  const rehydrate = getLayer(campaign.proofLayers, "rehydrate");
  const review = getLayer(campaign.proofLayers, "review");
  const exportPack = getLayer(campaign.proofLayers, "export_pack");
  const passport = getLayer(campaign.proofLayers, "passport");
  const candidates = [
    {
      key: "capture-campaign",
      phase: "01",
      label: "Capture / Campaign",
      status: "available" as const,
      source: campaign.source,
      detail: "The checked-in fixture records campaign and run identifiers for inspection.",
      href: "/campaign-proof-room",
    },
    manifest && { ...manifest, phase: "02", label: "Manifest / Genblaze" },
    archive && { ...archive, phase: "03", label: "Archive / B2" },
    rehydrate && { ...rehydrate, phase: "04", label: "Rehydrate" },
    review && { ...review, phase: "05", label: "Review" },
    exportPack && {
      key: "export-passport",
      phase: "06",
      label: "Export / Passport",
      status: exportPack.status,
      source: exportPack.source,
      detail: `${exportPack.detail} Passport: ${passport?.detail ?? "not captured"}`,
      href: exportPack.href ?? passport?.href,
    },
  ];
  return candidates.filter(Boolean) as EvidenceStage[];
}

function StageDetail({ stage }: { stage: EvidenceStage }) {
  return (
    <div className="dashboard-stage-detail" id={`stage-panel-${stage.key}`} role="tabpanel" aria-labelledby={`stage-tab-${stage.key}`}>
      <div className="dashboard-stage-detail-number" aria-hidden="true">{stage.phase}</div>
      <div>
        <p className="dashboard-kicker">Selected evidence stage</p>
        <h3>{stage.label}</h3>
        <p>{stage.detail}</p>
      </div>
      <div className="dashboard-stage-detail-actions">
        <DashboardPill tone={toneForStatus(stage.status)}>{stage.status}</DashboardPill>
        <SourceBadge source={stage.source} />
        {stage.href && <a href={stage.href}>Inspect stage <span aria-hidden="true">↗</span></a>}
      </div>
    </div>
  );
}

function EvidencePipeline({ campaign }: { campaign: DashboardCampaignSummary }) {
  const stages = useMemo(() => evidenceStages(campaign), [campaign]);
  const defaultStage = stages.find((stage) => stage.key === "b2_archive")?.key ?? stages[0]?.key;
  const [selectedKey, setSelectedKey] = useState(defaultStage);
  const selectedStage = stages.find((stage) => stage.key === selectedKey) ?? stages[0];

  const moveSelection = (index: number, direction: -1 | 1) => {
    const next = (index + direction + stages.length) % stages.length;
    setSelectedKey(stages[next].key);
    window.requestAnimationFrame(() => document.getElementById(`stage-tab-${stages[next].key}`)?.focus());
  };

  return (
    <section className="dashboard-pipeline" id="evidence-pipeline" aria-labelledby="dashboard-pipeline-title">
      <div className="dashboard-section-head">
        <div>
          <p className="dashboard-kicker">Evidence pipeline</p>
          <h2 id="dashboard-pipeline-title">Six recorded stages. One clear inspection path.</h2>
        </div>
        <span className="dashboard-section-count">06 stages</span>
      </div>
      <div className="dashboard-stage-tabs" role="tablist" aria-label="Evidence stages">
        {stages.map((stage, index) => (
          <button
            aria-controls={`stage-panel-${stage.key}`}
            aria-expanded={stage.key === selectedKey}
            aria-selected={stage.key === selectedKey}
            className={stage.key === selectedKey ? "is-selected" : ""}
            id={`stage-tab-${stage.key}`}
            key={stage.key}
            onClick={() => setSelectedKey(stage.key)}
            onKeyDown={(event) => {
              if (event.key === "ArrowRight" || event.key === "ArrowDown") {
                event.preventDefault(); moveSelection(index, 1);
              }
              if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
                event.preventDefault(); moveSelection(index, -1);
              }
            }}
            role="tab"
            tabIndex={stage.key === selectedKey ? 0 : -1}
            type="button"
          >
            <span className="dashboard-stage-number">{stage.phase}</span>
            <span className="dashboard-stage-title">{stage.label}</span>
            <span className={`dashboard-stage-status dashboard-stage-status-${toneForStatus(stage.status)}`}>
              <span aria-hidden="true" />{stage.status}
            </span>
          </button>
        ))}
      </div>
      <div className="dashboard-stage-detail-region">{selectedStage && <StageDetail stage={selectedStage} />}</div>
    </section>
  );
}

function GoldenInspectionObject({ campaign, onRefresh }: { campaign: DashboardCampaignSummary; onRefresh: () => void }) {
  const proofRoom = campaign.actions.find((action) => action.id === "open-proof-room");
  return (
    <section className="dashboard-hero" id="dashboard-command-center" aria-labelledby="dashboard-title">
      <div className="dashboard-hero-copy">
        <p className="dashboard-kicker">Source-labeled proof command</p>
        <h1 id="dashboard-title">Inspect the record.<br />See every boundary.</h1>
        <p className="dashboard-purpose">Navigate the golden proof, its recorded pipeline, and the live source state from one focused workspace.</p>
        <p className="dashboard-trust">ProofStudio proves what the pipeline recorded. Proof does not equal truth.</p>
        <div className="dashboard-hero-actions">
          {proofRoom && <a className="dashboard-cta dashboard-cta-primary" href={proofRoom.href}>Inspect golden proof <span aria-hidden="true">↗</span></a>}
          <button className="dashboard-cta" onClick={onRefresh} type="button">Refresh sources</button>
        </div>
      </div>
      <div className="dashboard-media-card" id="fixture-proof">
        <div className="dashboard-media-frame">
          <img
            alt="Sealed golden ProofStudio evidence capsule"
            decoding="async"
            loading="eager"
            src="/ps039/proof-object-sealed-poster.jpg"
          />
          <div className="dashboard-media-fallback" aria-hidden="true"><span /></div>
          <div className="dashboard-media-sheen" aria-hidden="true" />
          <span className="dashboard-media-label">Golden inspection object</span>
        </div>
        <div className="dashboard-media-meta">
          <div><strong>{campaign.title}</strong><span title={campaign.id}>Fixture evidence · not account-owned · {campaign.id}</span></div>
          <SourceBadge source={campaign.source} />
        </div>
      </div>
    </section>
  );
}

function SourceIntegrity({ model }: { model: DashboardModel }) {
  const campaignList = model.campaignList;
  const campaignSourceState = campaignList.state === "available"
    ? { label: "Account campaign access", state: "Available", detail: "Persisted application access mappings for the authenticated account." }
    : campaignList.state === "available_empty"
      ? { label: "Account campaign access", state: "Available · 0 mappings", detail: "Account campaign storage is available. No campaigns are currently linked to this account." }
      : campaignList.state === "unauthenticated"
        ? { label: "Account campaign access", state: "Sign-in required", detail: "An authenticated session is required to read account campaign mappings." }
        : campaignList.state === "unavailable"
          ? { label: "Account campaign access", state: "Unavailable", detail: campaignList.message }
          : { label: "Account campaign access", state: "Request failed", detail: "The response was rejected safely and no campaign rows were displayed." };
  const uniqueSources = useMemo(() => {
    const seen = new Set<string>();
    return model.sourceLedger.filter((source) => {
      const key = `${source.kind}:${source.label}:${source.endpoint ?? source.evidencePath ?? ""}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [model.sourceLedger]);

  return (
    <section className="dashboard-integrity" id="source-integrity" aria-labelledby="dashboard-integrity-title">
      <div className="dashboard-section-head">
        <div><p className="dashboard-kicker">Source integrity</p><h2 id="dashboard-integrity-title">The source map, compressed</h2></div>
      </div>
      <div className="dashboard-integrity-summary" aria-label="Source integrity summary">
        <p><strong>Real sources</strong><span>auth/session · proof API</span></p>
        <p><strong>{campaignSourceState.label}</strong><span>{campaignSourceState.state} · account_campaign_store · {campaignSourceState.detail}</span></p>
        <p><strong>Fixture source</strong><span>checked_in_fixture · not account-linked</span></p>
      </div>
      <details className="dashboard-disclosure dashboard-source-ledger" id="source-ledger">
        <summary><span>Full source detail</span><span>{uniqueSources.length} labels</span></summary>
        <div className="dashboard-ledger-grid">
          {uniqueSources.map((source) => (
            <article className="dashboard-ledger-row" key={`${source.kind}:${source.label}`}>
              <div><div className="dashboard-ledger-title"><SourceBadge source={source} /><strong>{source.label}</strong></div><p>{source.detail}</p></div>
              <code>{source.endpoint ?? source.evidencePath ?? source.reason ?? "source-labeled"}</code>
            </article>
          ))}
          <p className="dashboard-auth-boundary">{model.authBoundary}</p>
        </div>
      </details>
    </section>
  );
}

function AccountCampaignList({ model }: { model: DashboardModel }) {
  const list = model.campaignList;
  const disclosureLabel = list.state === "unauthenticated" ? "Why sign-in is required"
    : list.state === "available_empty" ? "About this empty list"
      : list.state === "available" ? "About access and proof details"
        : list.state === "unavailable" ? "Why this source is unavailable"
          : "Why this request failed";
  return (
    <section className="dashboard-account-empty" id="account-campaigns" aria-labelledby="dashboard-account-title">
      <div>
        <p className="dashboard-kicker">Account campaigns</p>
        <h2 id="dashboard-account-title">Account campaign references</h2>
        {list.state === "unauthenticated" && <p>Sign in to view campaigns linked to your account. No account campaign rows are shown without a real session.</p>}
        {list.state === "available_empty" && <p>Account campaign storage is available. No campaigns are currently linked to this account.</p>}
        {list.state === "unavailable" && <p>Account campaign source unavailable. {list.message}</p>}
        {list.state === "error" && <p>Account campaign request failed safely. No campaign rows were displayed.</p>}
        {list.state === "available" && <><p>Account campaign storage is available. {list.realAccountCampaigns.length} campaigns are linked to this account.</p><div className="dashboard-account-list">{list.realAccountCampaigns.map((item) => <article key={item.campaignId}>
          <strong>{item.campaignId}</strong><span>{item.latestRunId ?? "No latest run reference"}</span>
          <span>{item.campaignAccessRole} — application campaign access role</span>
          <span><a href={`/account/campaigns/${encodeURIComponent(item.campaignId)}/proof-room${item.latestRunId ? `?runId=${encodeURIComponent(item.latestRunId)}` : ""}`}>Open private Proof Room</a>{item.latestRunId ? <> · <a href={`/account/campaigns/${encodeURIComponent(item.campaignId)}/passport/${encodeURIComponent(item.latestRunId)}`}>Open private Passport</a></> : null}</span>
          <span><a className="dashboard-lineage-launcher" href={`/account/campaigns/${encodeURIComponent(item.campaignId)}/lineage`}>Open recorded lineage</a></span>
          <span>Linked {new Date(item.linkedAt).toLocaleDateString()}</span><SourceBadge source={list.source} />
          <span>Proof detail: {item.proofDetailState}</span>
        </article>)}</div></>}
      </div>
      <div className="dashboard-empty-actions">
        {list.state === "unauthenticated" && <a className="dashboard-cta dashboard-cta-primary" href="/account">Sign in</a>}
        <a className="dashboard-cta dashboard-cta-primary" href="#fixture-proof">Inspect golden proof</a>
        <details className="dashboard-disclosure dashboard-empty-disclosure">
          <summary>{disclosureLabel}</summary>
          <div>
            <p>Account access mappings are application-level access associations. The <code>owner</code> role is an application campaign access role only; access does not imply legal ownership or authorship and does not prove semantic truth.</p>
            <p>Proof detail is sourced separately from <code>proof_api</code>. The <code>checked_in_fixture</code> golden proof is not account-owned and is not inserted into the real account campaign list.</p>
            <SourceBadge source={model.campaignList.source} />
          </div>
        </details>
      </div>
    </section>
  );
}

function CommandActions({ model }: { model: DashboardModel }) {
  const campaignActions = model.fixtureCampaigns[0]?.actions ?? [];
  const allActions = [...campaignActions, ...model.globalActions];
  const byId = (id: string) => allActions.find((action) => action.id === id);
  const primary = [
    ["open-proof-room", "Open Proof Room"],
    ["open-passport", "Open Passport"],
    ["pipeline", "Inspect Pipeline"],
    ["open-export", "Open Evidence Pack"],
  ] as const;
  const secondary = [
    ["open-b2", "B2 evidence"], ["open-genblaze", "Genblaze"],
    ["open-rehydrate", "Rehydrate"], ["open-review", "Review workspace"],
    ["open-account", "Account session"], ["open-demo", "Demo route"],
    ["open-review-room", "Review room"],
  ] as const;

  return (
    <section className="dashboard-command" aria-labelledby="dashboard-command-title">
      <div className="dashboard-section-head"><div><p className="dashboard-kicker">Commands</p><h2 id="dashboard-command-title">Go directly to the proof surface</h2></div></div>
      <div className="dashboard-command-grid">
        {primary.map(([id, label]) => {
          if (id === "pipeline") return <a className="dashboard-action" href="#evidence-pipeline" key={id}><span className="dashboard-action-label">{label}</span><DashboardPill tone="info">checked_in_fixture</DashboardPill><span className="dashboard-action-arrow" aria-hidden="true">↓</span></a>;
          const action = byId(id); return action ? <ActionLink action={action} label={label} key={id} /> : null;
        })}
      </div>
      <details className="dashboard-disclosure dashboard-more-tools">
        <summary>More proof tools</summary>
        <div className="dashboard-more-tools-grid">
          {secondary.map(([id, label]) => { const action = byId(id); return action ? <ActionLink action={action} label={label} key={id} /> : null; })}
        </div>
      </details>
    </section>
  );
}

function DashboardReady({ model, onRefresh }: { model: DashboardModel; onRefresh: () => void }) {
  const campaign = model.fixtureCampaigns[0];
  return (
    <main className="dashboard-page">
      <DashboardNavigation />
      <div className="dashboard-main">
        {campaign && <GoldenInspectionObject campaign={campaign} onRefresh={onRefresh} />}
        <SourceStrip model={model} />
        {campaign && <EvidencePipeline campaign={campaign} />}
        <SourceIntegrity model={model} />
        <AccountCampaignList model={model} />
        <CommandActions model={model} />
        <footer className="dashboard-footer">Source-labeled dashboard state refreshed <time>{model.generatedAt}</time>.</footer>
      </div>
    </main>
  );
}

export function DashboardSurface() {
  const [loadState, setLoadState] = useState<LoadState>({ state: "loading", model: null, error: null });
  const refresh = useCallback(async () => {
    setLoadState({ state: "loading", model: null, error: null });
    try { setLoadState({ state: "ready", model: await loadDashboardModel(), error: null }); }
    catch (error) { setLoadState({ state: "error", model: null, error: error instanceof Error ? error.message : String(error) }); }
  }, []);
  useEffect(() => { void refresh(); }, [refresh]);

  if (loadState.state === "loading") return <main className="dashboard-page dashboard-loading"><section className="dashboard-loading-panel"><p className="dashboard-kicker">PS-041A dashboard</p><h1>Reading source-labeled state</h1><p>Checking auth session and proof API health.</p></section></main>;
  if (loadState.state === "error") return <main className="dashboard-page dashboard-loading"><section className="dashboard-loading-panel"><p className="dashboard-kicker">PS-041A dashboard</p><h1>Dashboard shell unavailable</h1><p>{loadState.error}</p><button className="dashboard-cta" onClick={refresh} type="button">Retry</button></section></main>;
  return <DashboardReady model={loadState.model} onRefresh={refresh} />;
}
