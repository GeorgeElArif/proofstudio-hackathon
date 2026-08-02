// PS-041E1 — Private Dynamic Lineage UI.
//
// Three route-level components:
//   BundleLineageListPage        — /account/campaigns/:campaignId/lineage
//   BundleLineageDetailPage      — /account/campaigns/:campaignId/lineage/:bundleId
//   PortableLineagePassportPage  — /account/campaigns/:campaignId/lineage/:bundleId/passport
//
// All reads go through the relative auth-server gateway only (credentials:
// "include"). No direct FastAPI URL is ever constructed; no Authorization,
// service, or operator token is sent to the browser; no localStorage /
// sessionStorage auth is read; no retry loop runs; no fixture fallback runs
// after an API failure. 401/404/503 are preserved distinctly.
//
// Stage presentation is fixed A → B0 → B1 → B2 → C. Stage A is a standalone
// storyboard artifact; B0/B1/B2 are separate Genblaze Runs; Stage C is an
// external composition (never a Genblaze Run). Parent edges are always shown
// as "Recorded" and "Not hash-covered" because Manifest 1.5 excludes
// parent_run_id from canonical hashing. Recorded relationships use solid
// edges; inferred relationships use dashed edges — color is never the only
// signal. Limitations and the truth boundary are always visible.

import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  fetchCampaignLineage,
  fetchCampaignLineageBundle,
  fetchCampaignLineagePassport,
  type AuthorizedLineageState,
} from "./authorizedProofClient";
import {
  b2ReferenceFields,
  buildNodeMap,
  buildStageLayout,
  checkOutcomeDetail,
  checkOutcomeLabel,
  checkSeverity,
  edgeAccessibleLabel,
  edgeKindLabel,
  LINEAGE_TRUTH_BOUNDARY,
  nodeKindLabel,
  parseLineageDetail,
  parseLineageList,
  parseLineagePassport,
  providerModelDisplay,
  safeBundleIdForFilename,
  SERVER_TRUTH_BOUNDARY,
  shortFingerprint,
  sortEdges,
  sourceRoleLabel,
  STAGE_ORDER,
  stageLabel,
  worstCheck,
  type B2Reference,
  type CheckOutcome,
  type LineageBundle,
  type LineageEdge,
  type LineageNode,
  type LineageRun,
  type LineageStep,
  type NodeStage,
  type StageKey,
} from "./bundleLineage";

const BUNDLE_SOURCE_REVISION = "2e31577b7a9d5a7b0309d814f2d0282088b33fe8";

// =============================================================================
// Shared shell
// =============================================================================

// Static malformed-reference page. PS-041E1 routes that fail to decode a valid
// campaign or bundle id return this page directly from App WITHOUT invoking
// any data hook. It performs zero gateway reads, emits zero fetches, and never
// produces a request containing `/campaigns//`. This is tested at runtime by
// the lineage UI validation script.
export function MalformedLineageReferencePage() {
  return (
    <main className="lineage-page" aria-labelledby="lineage-malformed-title">
      <header className="lineage-header">
        <p className="lineage-eyebrow">ProofStudio · Private recorded lineage</p>
        <h1 id="lineage-malformed-title">Malformed lineage reference</h1>
        <p className="lineage-context">
          The campaign or bundle reference in the URL could not be decoded safely. No lineage read was attempted, no
          gateway request was emitted, and no fixture fallback was used.
        </p>
        <div className="lineage-header-actions">
          <a className="lineage-button lineage-button-secondary" href="/dashboard">Back to dashboard</a>
        </div>
      </header>
      <section className="lineage-card lineage-state" role="status">
        <p className="lineage-state-eyebrow">Safe static error state</p>
        <p>This page does not invoke any data hook. The address bar reference is malformed; the lineage gateway was not called.</p>
      </section>
      <LineageTruthBoundary />
    </main>
  );
}

function LineageShell({ campaignId, children, back }: { campaignId: string; children: ReactNode; back: ReactNode }) {
  return (
    <main className="lineage-page" aria-labelledby="lineage-page-title">
      <header className="lineage-header">
        <p className="lineage-eyebrow">ProofStudio · Private recorded lineage</p>
        <h1 id="lineage-page-title">Recorded pipeline lineage</h1>
        <p className="lineage-context">
          Private read-only view. Campaign <code className="mono">{campaignId || "(invalid)"}</code>. Lineage is the
          imported record of what the pipeline produced; it is not a complete guarantee and not a public share.
        </p>
        <div className="lineage-header-actions">{back}</div>
      </header>
      {children}
      <LineageTruthBoundary />
    </main>
  );
}

function LineageTruthBoundary() {
  return (
    <footer className="lineage-truth-boundary" aria-label="Truth boundary">
      <h2>Truth boundary</h2>
      <p>{SERVER_TRUTH_BOUNDARY}</p>
      <ul>
        <li>This is a process-local imported record, not a live pipeline observation.</li>
        <li>Manifest <code>parent_run_id</code> is recorded but not canonical-hash-covered.</li>
        <li>Provider and model values are recorded evidence only.</li>
        <li>Stage A is standalone; Stage C is external composition.</li>
        <li>Byte verification may not have occurred for every recorded reference.</li>
        <li>Partial or missing evidence stays visible and is never upgraded.</li>
        <li>{LINEAGE_TRUTH_BOUNDARY}</li>
      </ul>
    </footer>
  );
}

function DashboardBackLink() {
  return <a className="lineage-button lineage-button-secondary" href="/dashboard">Back to dashboard</a>;
}

// =============================================================================
// State panels
// =============================================================================

function LineageLoading({ label }: { label: string }) {
  return (
    <section className="lineage-card lineage-state" aria-live="polite">
      <p className="lineage-state-eyebrow">{label}</p>
      <p>Authorizing private read through the auth-server gateway…</p>
    </section>
  );
}

function LineageStatePanel({ state, kind }: { state: AuthorizedLineageState; kind: "list" | "detail" | "passport" }) {
  if (state.state === "unauthenticated") {
    return (
      <section className="lineage-card lineage-state" role="status">
        <p className="lineage-state-eyebrow">Sign in required</p>
        <p>A current account session is required to open this private {kind}.</p>
        <a className="lineage-button" href="/login">Sign in</a>
      </section>
    );
  }
  if (state.state === "not_found") {
    return (
      <section className="lineage-card lineage-state" role="status">
        <p className="lineage-state-eyebrow">Lineage not found</p>
        <p>No accessible recorded lineage was found. Campaign, bundle, and run existence are not disclosed.</p>
      </section>
    );
  }
  if (state.state === "unavailable") {
    return (
      <section className="lineage-card lineage-state" role="status">
        <p className="lineage-state-eyebrow">Proof dependency unavailable</p>
        <p>The authorization or proof dependency is temporarily unavailable. No fixture fallback was used and no provider or live B2 call was made.</p>
      </section>
    );
  }
  if (state.state !== "available") {
    return (
      <section className="lineage-card lineage-state" role="status">
        <p className="lineage-state-eyebrow">Lineage response rejected</p>
        <p>The response did not match the private lineage contract and was not rendered.</p>
      </section>
    );
  }
  return null;
}

function useGatewayRead<T>(
  read: () => Promise<AuthorizedLineageState>,
  deps: ReadonlyArray<unknown>,
  parser: (payload: unknown) => T | null,
  enabled = true,
): { status: "loading" } | { status: "error"; state: AuthorizedLineageState } | { status: "ready"; state: AuthorizedLineageState; data: T; rawPayload: Record<string, unknown> } {
  const [result, setResult] = useState<{ status: "loading" } | { status: "error"; state: AuthorizedLineageState } | { status: "ready"; state: AuthorizedLineageState; data: T; rawPayload: Record<string, unknown> }>({ status: "loading" });
  useEffect(() => {
    if (!enabled) return;
    let active = true;
    setResult({ status: "loading" });
    void read().then((state) => {
      if (!active) return;
      if (state.state !== "available") {
        setResult({ status: "error", state });
        return;
      }
      const parsed = parser(state.payload);
      if (!parsed) {
        setResult({ status: "error", state: { state: "error" } });
        return;
      }
      setResult({ status: "ready", state, data: parsed, rawPayload: state.payload });
    });
    return () => { active = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return result;
}

// =============================================================================
// Bundle list page
// =============================================================================

export function BundleLineageListPage({ campaignId }: { campaignId: string }) {
  // Defense-in-depth: the route guard in App.tsx renders MalformedLineageReferencePage
  // for empty/invalid campaign ids before this component mounts. We additionally
  // disable the gateway read when campaignId is empty so no fetch is ever emitted
  // with a malformed id (e.g. `/campaigns//lineage`).
  const enabled = Boolean(campaignId);
  const read = useCallback(() => fetchCampaignLineage(campaignId), [campaignId]);
  const result = useGatewayRead(read, [campaignId], parseLineageList, enabled);

  return (
    <LineageShell campaignId={campaignId} back={<DashboardBackLink />}>
      {!enabled ? (
        <section className="lineage-card lineage-state" role="status">
          <p className="lineage-state-eyebrow">Malformed campaign reference</p>
          <p>The campaign reference could not be decoded safely. No lineage read was attempted.</p>
        </section>
      ) : result.status === "loading" ? (
        <LineageLoading label="Reading lineage list" />
      ) : result.status === "error" ? (
        <LineageStatePanel state={result.state} kind="list" />
      ) : (
        <LineageListBody campaignId={campaignId} state={result.state} />
      )}
    </LineageShell>
  );
}

function LineageListBody({ campaignId, state }: { campaignId: string; state: AuthorizedLineageState }) {
  if (state.state !== "available") return null;
  const parsed = parseLineageList(state.payload);
  if (!parsed) return <LineageStatePanel state={{ state: "error" }} kind="list" />;
  const bundles = parsed.bundles;
  return (
    <>
      <section className="lineage-card lineage-overview" aria-labelledby="lineage-overview-title">
        <div>
          <p className="lineage-eyebrow">Source revision</p>
          <h2 id="lineage-overview-title">{bundles.length} recorded bundle{bundles.length === 1 ? "" : "s"}</h2>
          <p className="lineage-meta">Imported source: <code className="mono">genblaze-gen-media-multi-provider-sample</code> · revision <code className="mono">{BUNDLE_SOURCE_REVISION}</code></p>
          <p className="lineage-meta">Campaign access role: <code className="mono">{state.campaignAccessRole}</code> — application role only.</p>
          <p className="lineage-meta">Lineage is the recorded pipeline evidence. It is not a complete guarantee and not a public share.</p>
        </div>
      </section>

      {bundles.length === 0 ? (
        <section className="lineage-card lineage-empty" role="status">
          <p className="lineage-state-eyebrow">No bundles recorded</p>
          <p>No imported bundles have been recorded for this campaign yet. The list is empty by design — no fixture fallback was used.</p>
        </section>
      ) : (
        <ul className="lineage-bundle-list" role="list">
          {bundles.map((bundle) => (
            <BundleListRow key={bundle.bundleId} campaignId={campaignId} bundle={bundle} />
          ))}
        </ul>
      )}
    </>
  );
}

function BundleListRow({ campaignId, bundle }: { campaignId: string; bundle: LineageBundle }) {
  const partial = bundle.state === "partial_bundle";
  const detailHref = `/account/campaigns/${encodeURIComponent(campaignId)}/lineage/${encodeURIComponent(bundle.bundleId)}`;
  const passportHref = `/account/campaigns/${encodeURIComponent(campaignId)}/lineage/${encodeURIComponent(bundle.bundleId)}/passport`;
  return (
    <li className="lineage-bundle-row">
      <a className="lineage-bundle-link" href={detailHref} aria-label={`Open lineage detail for bundle ${bundle.bundleId}`}>
        <span className="lineage-bundle-id" title={bundle.bundleId}>{bundle.bundleId}</span>
        <span className="lineage-bundle-fingerprint" title={bundle.bundleFingerprint}>{shortFingerprint(bundle.bundleFingerprint)}</span>
        <span className={`lineage-bundle-state lineage-bundle-state-${partial ? "warn" : "ok"}`} aria-label={`Bundle state ${bundle.state}`}>{bundle.state}</span>
        <span className="lineage-bundle-counts">{bundle.nodeIds.length} nodes · {bundle.edgeIds.length} edges</span>
      </a>
      <details className="lineage-disclosure">
        <summary>Bundle identifiers</summary>
        <dl className="lineage-kv">
          <dt>Bundle ID</dt><dd className="mono">{bundle.bundleId}</dd>
          <dt>Fingerprint schema</dt><dd className="mono">{bundle.fingerprintSchema}</dd>
          <dt>Bundle fingerprint</dt><dd className="mono">{bundle.bundleFingerprint}</dd>
          <dt>Source type</dt><dd className="mono">{bundle.sourceType}</dd>
          <dt>Source slug</dt><dd className="mono">{bundle.sourceSlug}</dd>
          <dt>Source revision</dt><dd className="mono">{bundle.sourceRevision}</dd>
          <dt>State</dt><dd>{partial ? "Partial bundle — recorded evidence is incomplete." : "Complete bundle — recorded evidence parsed under the supported schema."}</dd>
        </dl>
      </details>
      <div className="lineage-bundle-actions">
        <a className="lineage-button lineage-button-secondary" href={passportHref}>Open private Passport</a>
      </div>
    </li>
  );
}

// =============================================================================
// Detail page (dynamic stage lanes + one SVG edge overlay)
// =============================================================================

export function BundleLineageDetailPage({ campaignId, bundleId }: { campaignId: string; bundleId: string }) {
  // Defense-in-depth: see BundleLineageListPage. The hook never fires when
  // either id is empty.
  const enabled = Boolean(campaignId) && Boolean(bundleId);
  const read = useCallback(() => fetchCampaignLineageBundle(campaignId, bundleId), [campaignId, bundleId]);
  const result = useGatewayRead(read, [campaignId, bundleId], parseLineageDetail, enabled);

  return (
    <LineageShell campaignId={campaignId} back={<DashboardBackLink />}>
      {!enabled ? (
        <section className="lineage-card lineage-state" role="status">
          <p className="lineage-state-eyebrow">Malformed reference</p>
          <p>The campaign or bundle reference could not be decoded safely. No lineage read was attempted.</p>
        </section>
      ) : result.status === "loading" ? (
        <LineageLoading label="Reading lineage detail" />
      ) : result.status === "error" ? (
        <LineageStatePanel state={result.state} kind="detail" />
      ) : (
        <LineageDetailBody campaignId={campaignId} bundleId={bundleId} state={result.state} />
      )}
    </LineageShell>
  );
}

function LineageDetailBody({ campaignId, bundleId, state }: { campaignId: string; bundleId: string; state: AuthorizedLineageState }) {
  if (state.state !== "available") return <LineageStatePanel state={state} kind="detail" />;
  const parsed = parseLineageDetail(state.payload);
  if (!parsed) return <LineageStatePanel state={{ state: "error" }} kind="detail" />;
  return <LineageDetailReady campaignId={campaignId} bundleId={bundleId} parsed={parsed} role={state.campaignAccessRole} />;
}

function LineageDetailReady({
  campaignId,
  bundleId,
  parsed,
  role,
}: {
  campaignId: string;
  bundleId: string;
  parsed: NonNullable<ReturnType<typeof parseLineageDetail>>;
  role: "owner" | "reviewer" | "viewer";
}) {
  // Graph-aware stage classification. Built once in O(N+E) before render.
  const layout = useMemo(() => buildStageLayout(parsed.nodes, parsed.edges), [parsed.nodes, parsed.edges]);
  const stages = layout.stages;
  const nodeMap = useMemo(() => buildNodeMap(parsed.nodes), [parsed.nodes]);
  const sortedEdges = useMemo(() => sortEdges(parsed.edges), [parsed.edges]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const selectedNode = selectedNodeId ? nodeMap.get(selectedNodeId) ?? null : null;

  const listHref = `/account/campaigns/${encodeURIComponent(campaignId)}/lineage`;
  const passportHref = `/account/campaigns/${encodeURIComponent(campaignId)}/lineage/${encodeURIComponent(bundleId)}/passport`;

  return (
    <>
      <section className="lineage-card lineage-overview" aria-labelledby="lineage-detail-title">
        <div>
          <p className="lineage-eyebrow">Bundle {bundleId}</p>
          <h2 id="lineage-detail-title">Recorded A → B0 → B1 → B2 → C lineage</h2>
          <p className="lineage-meta">Bundle fingerprint <code className="mono" title={parsed.bundle.bundleFingerprint}>{shortFingerprint(parsed.bundle.bundleFingerprint)}</code> · state <code className="mono">{parsed.bundle.state}</code> · {parsed.nodes.length} nodes · {parsed.edges.length} edges</p>
          <p className="lineage-meta">Campaign access role: <code className="mono">{role}</code> — application role only.</p>
        </div>
        <div className="lineage-overview-actions">
          <a className="lineage-button lineage-button-secondary" href={listHref}>Back to bundle list</a>
          <a className="lineage-button lineage-button-secondary" href={passportHref}>Open private Passport</a>
        </div>
      </section>

      {layout.bundleRoot && <BundleRootContext node={layout.bundleRoot} />}

      <LineageStageLanes
        stages={stages}
        edges={sortedEdges}
        nodeMap={nodeMap}
        selectedNodeId={selectedNodeId}
        onSelectNode={setSelectedNodeId}
      />

      {layout.unclassified.length > 0 && (
        <UnclassifiedNodesSection
          nodes={layout.unclassified}
          selectedNodeId={selectedNodeId}
          onSelectNode={setSelectedNodeId}
        />
      )}

      {selectedNode ? (
        <LineageSelectedNodePanel node={selectedNode} onClose={() => setSelectedNodeId(null)} />
      ) : (
        <p className="lineage-hint" aria-live="polite">Select a card to inspect its recorded evidence in detail.</p>
      )}

      <section className="lineage-card lineage-edges" aria-labelledby="lineage-edges-title">
        <h2 id="lineage-edges-title">Recorded relationships</h2>
        <p className="lineage-meta">Every relationship shows its evidence class. The textual list below is the authoritative readable presentation; the bounded line layer above is a visual aid only.</p>
        <ul className="lineage-edge-list" role="list">
          {sortedEdges.map((edge) => {
            const source = nodeMap.get(edge.sourceNodeId);
            const target = edge.targetNodeId ? nodeMap.get(edge.targetNodeId) : undefined;
            return <LineageEdgeRow key={edge.edgeId} edge={edge} source={source} target={target} />;
          })}
        </ul>
      </section>

      {parsed.bundle.state === "partial_bundle" && (
        <section className="lineage-card lineage-state-lineage" role="status">
          <p className="lineage-state-eyebrow">Partial bundle</p>
          <p>The imported record for this bundle is incomplete. Missing evidence remains visible and is never upgraded.</p>
        </section>
      )}

      <LineageLimitations limitations={extractLimitationsFromGraph(parsed.nodes, parsed.edges)} title="Bundle limitations" />
    </>
  );
}

function BundleRootContext({ node }: { node: LineageNode }) {
  return (
    <section className="lineage-card lineage-bundle-root" aria-label="Import bundle root context">
      <p className="lineage-eyebrow">Bundle context</p>
      <h2>{nodeKindLabel(node.kind)} — {node.sourceId}</h2>
      <p className="lineage-meta">Import-bundle root recorded under source revision <code className="mono">{BUNDLE_SOURCE_REVISION}</code>. This node lives outside the A/B0/B1/B2/C lanes; its evidence class is <code className="mono">{node.evidenceClass}</code>.</p>
      <dl className="lineage-kv">
        <dt>Bundle</dt><dd className="mono">{node.bundleId}</dd>
        <dt>Source role</dt><dd>{sourceRoleLabel(node.sourceRole)}</dd>
        <dt>Content fingerprint</dt><dd className="mono" title={node.contentFingerprint}>{shortFingerprint(node.contentFingerprint)}</dd>
      </dl>
    </section>
  );
}

function UnclassifiedNodesSection({
  nodes,
  selectedNodeId,
  onSelectNode,
}: {
  nodes: readonly LineageNode[];
  selectedNodeId: string | null;
  onSelectNode: (id: string | null) => void;
}) {
  return (
    <section className="lineage-card lineage-unclassified-section" aria-label="Unclassified recorded nodes">
      <p className="lineage-eyebrow">Outside the stage lanes</p>
      <h2>Unclassified recorded nodes</h2>
      <p className="lineage-meta">These recorded nodes could not be assigned to Stage A, B0, B1, B2, or C from the accepted node and edge evidence. They are shown explicitly in this dedicated section — never coerced into a stage and never hidden inside Stage A.</p>
      <ul className="lineage-node-list" role="list">
        {nodes.map((node) => (
          <li key={node.nodeId}>
            <LineageNodeCard node={node} selected={node.nodeId === selectedNodeId} onSelect={onSelectNode} unsupported />
          </li>
        ))}
      </ul>
    </section>
  );
}

// =============================================================================
// Stage lanes + SVG edge overlay
// =============================================================================

function LineageStageLanes({
  stages,
  edges,
  nodeMap,
  selectedNodeId,
  onSelectNode,
}: {
  stages: Readonly<Record<StageKey, readonly LineageNode[]>>;
  edges: readonly LineageEdge[];
  nodeMap: ReadonlyMap<string, LineageNode>;
  selectedNodeId: string | null;
  onSelectNode: (id: string | null) => void;
}) {
  // We measure lane DOM positions once after mount and on resize to draw one
  // bounded SVG edge overlay. The measurement is throttled via
  // requestAnimationFrame to avoid ResizeObserver loops; geometry is recomputed
  // only when node count or selection changes.
  const containerRef = useRef<HTMLDivElement | null>(null);
  const nodeRefs = useRef<Map<string, HTMLElement>>(new Map());
  const [geometry, setGeometry] = useState<readonly EdgeGeometry[]>([]);

  useEffect(() => {
    let frame = 0;
    const recompute = () => {
      frame = 0;
      const container = containerRef.current;
      if (!container) return;
      const containerRect = container.getBoundingClientRect();
      const geoms: EdgeGeometry[] = [];
      for (const edge of edges) {
        const sourceEl = nodeRefs.current.get(edge.sourceNodeId);
        const targetId = edge.targetNodeId;
        const targetEl = targetId ? nodeRefs.current.get(targetId) : null;
        if (!sourceEl) continue;
        const sourceCenter = elementCenter(sourceEl, containerRect);
        if (!targetEl || !targetId) {
          geoms.push({ edgeId: edge.edgeId, source: sourceCenter, target: null, evidence: edge.evidenceClass, kind: edge.kind });
          continue;
        }
        const targetCenter = elementCenter(targetEl, containerRect);
        geoms.push({ edgeId: edge.edgeId, source: sourceCenter, target: targetCenter, evidence: edge.evidenceClass, kind: edge.kind });
      }
      setGeometry(geoms);
    };
    const schedule = () => {
      if (frame) return;
      frame = window.requestAnimationFrame(recompute);
    };
    schedule();
    window.addEventListener("resize", schedule, { passive: true });
    return () => {
      if (frame) window.cancelAnimationFrame(frame);
      window.removeEventListener("resize", schedule);
    };
  }, [edges, selectedNodeId]);

  const registerNode = useCallback((id: string) => (el: HTMLElement | null) => {
    if (el) nodeRefs.current.set(id, el);
    else nodeRefs.current.delete(id);
  }, []);

  return (
    <section className="lineage-stages" aria-labelledby="lineage-stages-title" ref={containerRef}>
      <h2 id="lineage-stages-title" className="lineage-visually-hidden">Stage lanes</h2>
      <p className="lineage-stages-meta">Fixed stage order: A → B0 → B1 → B2 → C. Stage A is standalone. B0/B1/B2 are separate Runs. Stage C is external composition. Generated assets inherit the stage of their generating Run; external inputs inherit the stage of their connected Run; the embedded Manifest and final delivery sit in Stage C.</p>
      <div className="lineage-stage-grid" role="list">
        {STAGE_ORDER.map((stage) => (
          <LineageStage
            key={stage}
            stage={stage}
            stageNodes={stages[stage]}
            selectedNodeId={selectedNodeId}
            onSelectNode={onSelectNode}
            registerNode={registerNode}
          />
        ))}
      </div>
      <LineageEdgeLayer geometry={geometry} edges={edges} nodeMap={nodeMap} />
      <p className="lineage-stages-legend" aria-label="Edge legend">
        <span className="lineage-legend-item"><span className="lineage-legend-line lineage-legend-recorded" aria-hidden="true" /> Recorded relationship (solid)</span>
        <span className="lineage-legend-item"><span className="lineage-legend-line lineage-legend-inferred" aria-hidden="true" /> Inferred relationship (dashed)</span>
        <span className="lineage-legend-meta">Lines are a visual aid only — every relationship carries an accessible title and the full readable list is below.</span>
      </p>
    </section>
  );
}

interface EdgeGeometry {
  readonly edgeId: string;
  readonly source: { readonly x: number; readonly y: number };
  readonly target: { readonly x: number; readonly y: number } | null;
  readonly evidence: "recorded" | "inferred";
  readonly kind: string;
}

function elementCenter(el: HTMLElement, containerRect: DOMRect): { x: number; y: number } {
  const rect = el.getBoundingClientRect();
  return {
    x: rect.left - containerRect.left + rect.width / 2,
    y: rect.top - containerRect.top + rect.height / 2,
  };
}

function LineageStage({
  stage,
  stageNodes,
  selectedNodeId,
  onSelectNode,
  registerNode,
}: {
  stage: StageKey;
  stageNodes: readonly LineageNode[];
  selectedNodeId: string | null;
  onSelectNode: (id: string | null) => void;
  registerNode: (id: string) => (el: HTMLElement | null) => void;
}) {
  const { title, subtitle, standaloneNotice } = stageMeta(stage);
  return (
    <section className={`lineage-stage lineage-stage-${stage.toLowerCase()}`} aria-label={`${stageLabel(stage)} lane`}>
      <header className="lineage-stage-head">
        <h3>{title}</h3>
        <p className="lineage-stage-subtitle">{subtitle}</p>
      </header>
      {standaloneNotice && <p className="lineage-stage-notice">{standaloneNotice}</p>}
      {stageNodes.length === 0 ? (
        <p className="lineage-stage-empty">No recorded evidence for this stage.</p>
      ) : null}
      <ul className="lineage-node-list" role="list">
        {stageNodes.map((node) => (
          <li key={node.nodeId} ref={registerNode(node.nodeId)}>
            <LineageNodeCard node={node} selected={node.nodeId === selectedNodeId} onSelect={onSelectNode} />
          </li>
        ))}
      </ul>
    </section>
  );
}

function stageMeta(stage: StageKey): { title: string; subtitle: string; standaloneNotice: string | null } {
  switch (stage) {
    case "A":
      return {
        title: "Stage A — Planning artifact",
        subtitle: "Standalone artifact, not a Genblaze Run.",
        standaloneNotice: "Stage A is a standalone storyboard artifact. It has no durable recorded relation to B0/B1/B2/C; any visible Stage A relationship is inferred from bundle convention only.",
      };
    case "B0":
      return { title: "Stage B0 — Reference image run", subtitle: "Separate Genblaze Run, reference-image lineage root.", standaloneNotice: null };
    case "B1":
      return { title: "Stage B1 — Keyframe run", subtitle: "Separate Genblaze Run, explicit recorded parent edge to B0.", standaloneNotice: null };
    case "B2":
      return { title: "Stage B2 — Media run", subtitle: "Separate Genblaze Run, explicit recorded parent edge to B1.", standaloneNotice: null };
    case "C":
      return {
        title: "Stage C — External composition",
        subtitle: "External ffmpeg composition, not a Genblaze Run.",
        standaloneNotice: "Stage C is an external composition. It is not a Genblaze Run; ffmpeg composition is recorded workflow evidence, not pipeline execution.",
      };
  }
}

function LineageNodeCard({
  node,
  selected,
  onSelect,
  unsupported,
}: {
  node: LineageNode;
  selected: boolean;
  onSelect: (id: string | null) => void;
  unsupported?: boolean;
}) {
  const mainCheck = mainCheckForNode(node);
  return (
    <article
      className={`lineage-node-card ${selected ? "is-selected" : ""} ${unsupported ? "is-unsupported" : ""}`}
      aria-label={`${nodeKindLabel(node.kind)} ${node.sourceId}`}
    >
      <button
        type="button"
        className="lineage-node-card-button"
        aria-pressed={selected}
        onClick={() => onSelect(selected ? null : node.nodeId)}
      >
        <span className="lineage-node-kind">{nodeKindLabel(node.kind)}</span>
        <span className="lineage-node-source" title={node.sourceId}>{node.sourceId}</span>
        <span className="lineage-node-role">{sourceRoleLabel(node.sourceRole)}</span>
        {mainCheck && (
          <span className={`lineage-node-check lineage-severity-${checkSeverity(mainCheck.outcome)}`}>
            {checkOutcomeLabel(mainCheck.outcome)}
          </span>
        )}
        <span className={`lineage-node-evidence lineage-evidence-${node.evidenceClass}`}>{node.evidenceClass === "recorded" ? "Recorded" : "Inferred"}</span>
      </button>
    </article>
  );
}

function mainCheckForNode(node: LineageNode): { outcome: CheckOutcome } | null {
  // Highest-risk priority: the card summary surfaces the worst recorded
  // outcome so a success badge can never conceal a hash_mismatch or
  // manifest_invalid. Priority order is danger > unsupported > warn > neutral
  // > ok; ties resolve to the first recorded worst outcome.
  const worst = worstCheck(node.checks);
  return worst ? { outcome: worst.outcome } : null;
}

// =============================================================================
// SVG edge overlay — bounded visual layer
// =============================================================================

function LineageEdgeLayer({
  geometry,
  edges,
  nodeMap,
}: {
  geometry: readonly EdgeGeometry[];
  edges: readonly LineageEdge[];
  nodeMap: ReadonlyMap<string, LineageNode>;
}) {
  const edgeById = useMemo(() => {
    const map = new Map<string, LineageEdge>();
    for (const edge of edges) map.set(edge.edgeId, edge);
    return map;
  }, [edges]);
  // Compute a bounded viewBox from current geometry. Lines are drawn BEHIND the
  // cards (z-index: 0 in CSS) so they never obscure node content. No full
  // relationship sentences are rendered on the SVG — only a compact `R`/`I`
  // evidence marker at the source anchor, and an accessible <title> per edge.
  // The authoritative textual relationship list is rendered below the lanes.
  const width = geometry.reduce((max, g) => Math.max(max, g.target ? Math.max(g.source.x, g.target.x) : g.source.x), 1);
  const height = geometry.reduce((max, g) => Math.max(max, g.target ? Math.max(g.source.y, g.target.y) : g.source.y), 1);
  return (
    <svg
      className="lineage-edge-layer"
      aria-hidden="false"
      aria-label="Recorded and inferred relationship edges (visual aid; read the relationships list below for full semantics)"
      role="img"
      width={Math.max(width + 24, 100)}
      height={Math.max(height + 24, 100)}
      viewBox={`-12 -12 ${Math.max(width + 24, 100)} ${Math.max(height + 24, 100)}`}
    >
      <title>Recorded and inferred relationship edges — compact visual aid</title>
      <desc>Solid lines denote recorded relationships and dashed lines denote inferred relationships. Each line carries an accessible title with the full relationship sentence; the authoritative readable list is rendered below the lanes.</desc>
      {geometry.map((g) => {
        const edge = edgeById.get(g.edgeId);
        if (!edge) return null;
        const source = nodeMap.get(edge.sourceNodeId);
        const target = edge.targetNodeId ? nodeMap.get(edge.targetNodeId) : undefined;
        const label = edgeAccessibleLabel(edge, source, target);
        if (!g.target) {
          return (
            <g key={g.edgeId} className={`lineage-edge lineage-edge-${g.evidence} lineage-edge-dangling`}>
              <circle cx={g.source.x} cy={g.source.y} r={4} />
              <title>{label}</title>
            </g>
          );
        }
        return (
          <g key={g.edgeId} className={`lineage-edge lineage-edge-${g.evidence}`}>
            <line x1={g.source.x} y1={g.source.y} x2={g.target.x} y2={g.target.y} />
            <title>{label}</title>
          </g>
        );
      })}
    </svg>
  );
}

function LineageEdgeRow({ edge, source, target }: { edge: LineageEdge; source?: LineageNode; target?: LineageNode }) {
  const label = edgeAccessibleLabel(edge, source, target);
  return (
    <li className={`lineage-edge-row lineage-evidence-${edge.evidenceClass}`}>
      <span className={`lineage-edge-marker lineage-edge-marker-${edge.evidenceClass}`} aria-hidden="true" />
      <div>
        <p className="lineage-edge-label">
          <strong>{edgeKindLabel(edge.kind)}</strong>
          {" "}
          <span className={`lineage-evidence-badge lineage-evidence-${edge.evidenceClass}`}>{edge.evidenceClass === "recorded" ? "Recorded" : "Inferred"}</span>
          {edge.kind === "parent_run" && <span className="lineage-parent-limitation">Recorded parent — not hash-covered</span>}
        </p>
        <p className="lineage-edge-detail">{label}</p>
        {edge.sourceLocator && <p className="lineage-edge-locator">Locator: <code className="mono">{edge.sourceLocator}</code></p>}
        {edge.limitations.length > 0 && (
          <ul className="lineage-edge-limitations">
            {edge.limitations.map((l) => <li key={l.code}><code className="mono">{l.code}</code> — {l.notice}</li>)}
          </ul>
        )}
      </div>
    </li>
  );
}

// =============================================================================
// Selected node detail panel
// =============================================================================

function LineageSelectedNodePanel({ node, onClose }: { node: LineageNode; onClose: () => void }) {
  return (
    <section className="lineage-card lineage-selected" aria-labelledby="lineage-selected-title" aria-live="polite">
      <header className="lineage-selected-head">
        <div>
          <p className="lineage-eyebrow">Selected node</p>
          <h2 id="lineage-selected-title">{nodeKindLabel(node.kind)} — {node.sourceId}</h2>
          <p className="lineage-meta">{sourceRoleLabel(node.sourceRole)} · {node.evidenceClass === "recorded" ? "Recorded" : "Inferred"} evidence</p>
        </div>
        <button type="button" className="lineage-button lineage-button-secondary" onClick={onClose}>Close</button>
      </header>

      <dl className="lineage-kv">
        <dt>Node ID</dt><dd className="mono">{node.nodeId}</dd>
        <dt>Source ID</dt><dd className="mono">{node.sourceId}</dd>
        <dt>Content fingerprint</dt><dd className="mono" title={node.contentFingerprint}>{shortFingerprint(node.contentFingerprint)}</dd>
        <dt>Bundle</dt><dd className="mono">{node.bundleId}</dd>
      </dl>

      {node.run && <RunStepList run={node.run} />}

      {node.metadata && Object.keys(node.metadata).length > 0 && (
        <details className="lineage-disclosure" open>
          <summary>Recorded metadata</summary>
          <dl className="lineage-kv">
            {Object.entries(node.metadata).map(([key, value]) => (
              value === null ? null : (
                <div key={key} className="lineage-kv-row">
                  <dt>{key}</dt><dd className="mono">{String(value)}</dd>
                </div>
              )
            ))}
          </dl>
        </details>
      )}

      <CheckBadgeList checks={node.checks} />

      {node.b2Reference && <B2ReferenceCard reference={node.b2Reference} />}

      {node.limitations.length > 0 && <LineageLimitations limitations={node.limitations} title="Node limitations" />}
    </section>
  );
}

function RunStepList({ run }: { run: LineageRun }) {
  return (
    <details className="lineage-disclosure" open>
      <summary>Run {run.runId} — stage {run.stage}</summary>
      <dl className="lineage-kv">
        <dt>Run ID</dt><dd className="mono">{run.runId}</dd>
        <dt>Stage</dt><dd className="mono">{run.stage}</dd>
        <dt>Status</dt><dd className="mono">{run.status}</dd>
        <dt>Manifest schema</dt><dd className="mono">{run.manifestSchema}</dd>
        <dt>Manifest hash</dt><dd className="mono">{run.manifestHash ?? "(none recorded)"}</dd>
        <dt>Recorded parent run</dt>
        <dd className="mono">{run.parentRunId ?? "(none — root run)"}</dd>
      </dl>
      {run.parentRunId && (
        <p className="lineage-parent-note">
          <span className="lineage-evidence-badge lineage-evidence-recorded">Recorded</span>
          {" "}
          <span className="lineage-parent-limitation">Recorded parent — not hash-covered</span>
        </p>
      )}
      {run.steps.length > 0 && (
        <ol className="lineage-step-list" role="list">
          {run.steps.map((step) => <StepRow key={step.stepId} step={step} />)}
        </ol>
      )}
    </details>
  );
}

function StepRow({ step }: { step: LineageStep }) {
  const display = providerModelDisplay(step);
  const failed = step.status === "failed";
  return (
    <li className={`lineage-step lineage-step-${step.status}`}>
      <p className="lineage-step-head">
        <code className="mono">{step.modality}</code> · step {step.stepIndex}
        <span className={`lineage-step-status lineage-severity-${failed ? "danger" : "ok"}`}>{step.status}</span>
      </p>
      <dl className="lineage-kv">
        <dt>Step ID</dt><dd className="mono">{step.stepId}</dd>
        <dt>Provider</dt><dd>{display.provider}</dd>
        <dt>Model</dt><dd className="mono">{display.model}</dd>
        <dt>Inputs</dt><dd className="mono">{step.inputCount}</dd>
        <dt>Outputs</dt><dd className="mono">{step.outputCount}</dd>
      </dl>
      {failed && <p className="lineage-step-failed">This recorded step failed; any expected asset for this step is missing by design.</p>}
    </li>
  );
}

// =============================================================================
// Checks, limitations, B2 reference
// =============================================================================

function CheckBadgeList({ checks }: { checks: readonly { outcome: CheckOutcome; subject: string; detail: string | null }[] }) {
  if (checks.length === 0) {
    return <p className="lineage-hint">No recorded checks for this node.</p>;
  }
  return (
    <section className="lineage-checks" aria-label="Recorded checks">
      <h3>Recorded checks</h3>
      <ul className="lineage-check-list" role="list">
        {checks.map((check, idx) => (
          <CheckBadge key={`${check.outcome}-${check.subject}-${idx}`} outcome={check.outcome} subject={check.subject} detail={check.detail} />
        ))}
      </ul>
    </section>
  );
}

function CheckBadge({ outcome, subject, detail }: { outcome: CheckOutcome; subject: string; detail: string | null }) {
  const severity = checkSeverity(outcome);
  return (
    <li className={`lineage-check-badge lineage-severity-${severity}`}>
      <p className="lineage-check-head">
        <span className="lineage-check-outcome">{checkOutcomeLabel(outcome)}</span>
        <span className="lineage-check-subject" title={subject}>{subject}</span>
      </p>
      <p className="lineage-check-detail">{detail ?? checkOutcomeDetail(outcome)}</p>
    </li>
  );
}

function LineageLimitations({ limitations, title }: { limitations: readonly { code: string; notice: string }[]; title: string }) {
  if (limitations.length === 0) return null;
  return (
    <section className="lineage-card lineage-limitations" aria-label={title}>
      <h2>{title}</h2>
      <ul className="lineage-limitation-list" role="list">
        {limitations.map((l) => (
          <li key={l.code}><code className="mono">{l.code}</code> — {l.notice}</li>
        ))}
      </ul>
    </section>
  );
}

function B2ReferenceCard({ reference }: { reference: B2Reference }) {
  const fields = b2ReferenceFields(reference);
  return (
    <section className="lineage-b2-reference" aria-label="Recorded B2 archive reference">
      <h3>Recorded B2 archive reference</h3>
      <p className="lineage-meta">This is a credential-free structured reference. No bucket URL is constructed, no signed URL is exposed, no account id is shown, and no download action is offered.</p>
      <dl className="lineage-kv">
        {fields.map((field) => (
          <div key={field.label} className="lineage-kv-row">
            <dt>{field.label}</dt><dd className="mono">{field.value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

function extractLimitationsFromGraph(nodes: readonly LineageNode[], edges: readonly LineageEdge[]): readonly { code: string; notice: string }[] {
  const seen = new Set<string>();
  const out: { code: string; notice: string }[] = [];
  for (const node of nodes) for (const l of node.limitations) {
    const key = `${l.code}:${l.notice}`;
    if (!seen.has(key)) { seen.add(key); out.push(l); }
  }
  for (const edge of edges) for (const l of edge.limitations) {
    const key = `${l.code}:${l.notice}`;
    if (!seen.has(key)) { seen.add(key); out.push(l); }
  }
  return out.sort((a, b) => (a.code < b.code ? -1 : a.code > b.code ? 1 : 0));
}

// =============================================================================
// Private portable Passport page
// =============================================================================

export function PortableLineagePassportPage({ campaignId, bundleId }: { campaignId: string; bundleId: string }) {
  const enabled = Boolean(campaignId) && Boolean(bundleId);
  const read = useCallback(() => fetchCampaignLineagePassport(campaignId, bundleId), [campaignId, bundleId]);
  const result = useGatewayRead(read, [campaignId, bundleId], parseLineagePassport, enabled);
  const [copyState, setCopyState] = useState<"idle" | "copied" | "unavailable">("idle");
  const objectUrlRef = useRef<string | null>(null);

  useEffect(() => () => {
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
      objectUrlRef.current = null;
    }
  }, []);

  // PS-041E1: the copy/download payload MUST be the exact validated server
  // Passport object — `state.payload.passport` — NOT the parsed camelCase DTO,
  // NOT the auth gateway envelope, NOT a camelCase reconstruction, and NOT
  // enriched with `kind`, `campaignAccessScope`, UI fields, or browser
  // evidence. We retain the original object by reference, serialize it
  // without mutation, and never reorder, rename, add, or remove its fields.
  const rawPassportObject = result.status === "ready" ? (result.rawPayload.passport as unknown) : null;

  const onCopy = useCallback(async () => {
    if (result.status !== "ready" || !rawPassportObject) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(rawPassportObject, null, 2));
      setCopyState("copied");
      window.setTimeout(() => setCopyState("idle"), 2500);
    } catch {
      setCopyState("unavailable");
      window.setTimeout(() => setCopyState("idle"), 2500);
    }
  }, [result, rawPassportObject]);

  const onDownload = useCallback(() => {
    if (result.status !== "ready" || !rawPassportObject) return;
    const text = JSON.stringify(rawPassportObject, null, 2);
    const blob = new Blob([text], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    objectUrlRef.current = url;
    const a = document.createElement("a");
    a.href = url;
    a.rel = "noopener noreferrer";
    a.download = `proofstudio-private-lineage-passport-${safeBundleIdForFilename(bundleId)}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.setTimeout(() => {
      URL.revokeObjectURL(url);
      objectUrlRef.current = null;
    }, 0);
  }, [result, bundleId, rawPassportObject]);

  return (
    <LineageShell campaignId={campaignId} back={<DashboardBackLink />}>
      {!enabled ? (
        <section className="lineage-card lineage-state" role="status">
          <p className="lineage-state-eyebrow">Malformed reference</p>
          <p>The campaign or bundle reference could not be decoded safely. No Passport read was attempted.</p>
        </section>
      ) : result.status === "loading" ? (
        <LineageLoading label="Reading private Passport" />
      ) : result.status === "error" ? (
        <LineageStatePanel state={result.state} kind="passport" />
      ) : (
        <PortablePassportBody
          campaignId={campaignId}
          bundleId={bundleId}
          passport={result.data}
          role={result.state.state === "available" ? result.state.campaignAccessRole : "viewer"}
          onCopy={onCopy}
          onDownload={onDownload}
          copyState={copyState}
        />
      )}
    </LineageShell>
  );
}

function PortablePassportBody({
  campaignId,
  bundleId,
  passport,
  role,
  onCopy,
  onDownload,
  copyState,
}: {
  campaignId: string;
  bundleId: string;
  passport: ReturnType<typeof parseLineagePassport>;
  role: "owner" | "reviewer" | "viewer";
  onCopy: () => void;
  onDownload: () => void;
  copyState: "idle" | "copied" | "unavailable";
}) {
  if (!passport) return null;
  const detailHref = `/account/campaigns/${encodeURIComponent(campaignId)}/lineage/${encodeURIComponent(bundleId)}`;
  return (
    <>
      <section className="lineage-card lineage-overview" aria-labelledby="lineage-passport-title">
        <div>
          <p className="lineage-eyebrow">Private portable Passport</p>
          <h2 id="lineage-passport-title">proofstudio.portable_lineage_passport.v1</h2>
          <p className="lineage-meta">Bundle <code className="mono">{bundleId}</code> · fingerprint <code className="mono" title={passport.bundleFingerprint}>{shortFingerprint(passport.bundleFingerprint)}</code> · state <code className="mono">{passport.state}</code></p>
          <p className="lineage-meta">Schema <code className="mono">{passport.schema}</code> · role <code className="mono">{role}</code> — application role only.</p>
        </div>
        <div className="lineage-overview-actions">
          <a className="lineage-button lineage-button-secondary" href={detailHref}>Back to lineage detail</a>
        </div>
      </section>

      <section className="lineage-card lineage-passport-actions" aria-labelledby="lineage-passport-actions-title">
        <h2 id="lineage-passport-actions-title">PRIVATE Passport controls</h2>
        <p className="lineage-meta">These controls are labeled PRIVATE. The copy and download payload is the exact validated server Passport object (<code className="mono">state.payload.passport</code>) — never the auth gateway envelope, never the camelCase presentation DTO, and never enriched with <code className="mono">kind</code>, <code className="mono">campaignAccessScope</code>, UI fields, or browser evidence. Fields are not reordered, renamed, added, or removed.</p>
        <div className="lineage-passport-buttons">
          <button type="button" className="lineage-button" onClick={onCopy}>
            <span aria-hidden="true">🔒</span> Copy private Passport JSON
          </button>
          <button type="button" className="lineage-button" onClick={onDownload}>
            <span aria-hidden="true">🔒</span> Download private Passport JSON
          </button>
          {copyState === "copied" && <span className="lineage-passport-status" role="status">Copied the exact raw server Passport JSON to clipboard.</span>}
          {copyState === "unavailable" && <span className="lineage-passport-status" role="status">Clipboard unavailable in this browser. Use Download instead.</span>}
        </div>
      </section>

      <section className="lineage-card" aria-labelledby="lineage-passport-nodes-title">
        <h2 id="lineage-passport-nodes-title">Recorded nodes ({passport.nodes.length})</h2>
        <PassportNodesTable nodes={passport.nodes} edges={passport.edges} />
      </section>

      <section className="lineage-card" aria-labelledby="lineage-passport-edges-title">
        <h2 id="lineage-passport-edges-title">Recorded edges ({passport.edges.length})</h2>
        <PassportEdgesTable edges={passport.edges} />
      </section>

      <section className="lineage-card" aria-labelledby="lineage-passport-b2-title">
        <h2 id="lineage-passport-b2-title">Structured B2 references</h2>
        {passport.nodes.every((n) => !n.b2Reference) ? (
          <p className="lineage-hint">No structured B2 references recorded.</p>
        ) : (
          passport.nodes.filter((n) => n.b2Reference).map((n) => n.b2Reference ? <B2ReferenceCard key={n.nodeId} reference={n.b2Reference} /> : null)
        )}
      </section>

      {passport.limitations.length > 0 && <LineageLimitations limitations={passport.limitations} title="Passport limitations" />}

      <section className="lineage-card" aria-labelledby="lineage-passport-final-title">
        <h2 id="lineage-passport-final-title">Final composition relation</h2>
        <p className="lineage-meta">The final delivery relation is recorded only when the imported bundle records it. It is workflow evidence, not a quality guarantee.</p>
        <FinalCompositionRelation edges={passport.edges} nodes={passport.nodes} />
      </section>

      <section className="lineage-card lineage-truth-boundary-card" aria-label="Exact truth boundary">
        <h2>Exact truth boundary</h2>
        <p>{passport.truthBoundary}</p>
      </section>
    </>
  );
}

function PassportNodesTable({ nodes, edges }: { nodes: readonly LineageNode[]; edges: readonly LineageEdge[] }) {
  const classification = useMemo(() => classifyNodeStagesForTable(nodes, edges), [nodes, edges]);
  return (
    <div className="lineage-table-wrap" role="region" aria-label="Recorded nodes table" tabIndex={0}>
      <table className="lineage-table">
        <caption>Recorded nodes from the imported bundle</caption>
        <thead>
          <tr>
            <th scope="col">Kind</th>
            <th scope="col">Source ID</th>
            <th scope="col">Role</th>
            <th scope="col">Evidence</th>
            <th scope="col">Stage</th>
          </tr>
        </thead>
        <tbody>
          {nodes.map((node) => {
            const stage = classification.get(node.nodeId) ?? "unclassified";
            const label = stage === "bundle-root" ? "Bundle root"
              : stage === "unclassified" ? "(unclassified)"
              : stage;
            return (
              <tr key={node.nodeId}>
                <td>{nodeKindLabel(node.kind)}</td>
                <td className="mono">{node.sourceId}</td>
                <td>{sourceRoleLabel(node.sourceRole)}</td>
                <td>{node.evidenceClass === "recorded" ? "Recorded" : "Inferred"}</td>
                <td>{label}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// Local import-free alias to buildStageLayout.classification, memoized for the
// passport table. Kept inline so the passport table does not depend on edges
// ordering from the caller.
function classifyNodeStagesForTable(
  nodes: readonly LineageNode[],
  edges: readonly LineageEdge[],
): ReadonlyMap<string, NodeStage> {
  return buildStageLayout(nodes, edges).classification;
}

function PassportEdgesTable({ edges }: { edges: readonly LineageEdge[] }) {
  return (
    <div className="lineage-table-wrap" role="region" aria-label="Recorded edges table" tabIndex={0}>
      <table className="lineage-table">
        <caption>Recorded edges from the imported bundle</caption>
        <thead>
          <tr>
            <th scope="col">Kind</th>
            <th scope="col">Evidence</th>
            <th scope="col">Hash-covered</th>
            <th scope="col">Source → Target</th>
          </tr>
        </thead>
        <tbody>
          {edges.map((edge) => (
            <tr key={edge.edgeId}>
              <td>{edgeKindLabel(edge.kind)}</td>
              <td>{edge.evidenceClass === "recorded" ? "Recorded" : "Inferred"}</td>
              <td>{edge.hashCovered ? "Yes" : "No"}</td>
              <td className="mono">{edge.sourceNodeId} → {edge.targetNodeId ?? `missing ${edge.missingSourceId ?? ""}`}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function FinalCompositionRelation({ edges, nodes }: { edges: readonly LineageEdge[]; nodes: readonly LineageNode[] }) {
  const nodeMap = useMemo(() => buildNodeMap(nodes), [nodes]);
  const compositionInputs = edges.filter((e) => e.kind === "composition_input");
  const composedOutputs = edges.filter((e) => e.kind === "composed_output");
  if (compositionInputs.length === 0 && composedOutputs.length === 0) {
    return <p className="lineage-hint">No recorded final-composition relation for this bundle.</p>;
  }
  return (
    <ul className="lineage-edge-list" role="list">
      {[...compositionInputs, ...composedOutputs].map((edge) => {
        const source = nodeMap.get(edge.sourceNodeId);
        const target = edge.targetNodeId ? nodeMap.get(edge.targetNodeId) : undefined;
        return <LineageEdgeRow key={edge.edgeId} edge={edge} source={source} target={target} />;
      })}
    </ul>
  );
}
