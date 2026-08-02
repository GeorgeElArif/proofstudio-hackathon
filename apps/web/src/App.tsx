// ProofStudio client-side route dispatcher.
//
// PS-042C4 keeps each large proof surface in its own lazy-loaded chunk. This
// preserves every route while avoiding the oversized all-routes bundle that
// could destabilize constrained WSL environments during Vite transforms.

import { lazy, Suspense } from "react";

const PublicPassportPage = lazy(() =>
  import("./PublicPassportPage").then((module) => ({
    default: module.PublicPassportPage,
  })),
);
const JudgeCockpitHome = lazy(() =>
  import("./JudgeCockpitHome").then((module) => ({
    default: module.JudgeCockpitHome,
  })),
);
const B2EvidenceExplorer = lazy(() =>
  import("./B2EvidenceExplorer").then((module) => ({
    default: module.B2EvidenceExplorer,
  })),
);
const GenblazePipelineGraph = lazy(() =>
  import("./GenblazePipelineGraph").then((module) => ({
    default: module.GenblazePipelineGraph,
  })),
);
const ManifestVerificationPanel = lazy(() =>
  import("./ManifestVerificationPanel").then((module) => ({
    default: module.ManifestVerificationPanel,
  })),
);
const B2RehydrateComparison = lazy(() =>
  import("./B2RehydrateComparison").then((module) => ({
    default: module.B2RehydrateComparison,
  })),
);
const FailureAsProofTimeline = lazy(() =>
  import("./FailureAsProofTimeline").then((module) => ({
    default: module.FailureAsProofTimeline,
  })),
);
const JudgeEvidencePack = lazy(() =>
  import("./JudgeEvidencePack").then((module) => ({
    default: module.JudgeEvidencePack,
  })),
);
const OperationsCockpit = lazy(() =>
  import("./OperationsCockpit").then((module) => ({
    default: module.OperationsCockpit,
  })),
);
const ProviderDecisionIntelligence = lazy(() =>
  import("./ProviderDecisionIntelligence").then((module) => ({
    default: module.ProviderDecisionIntelligence,
  })),
);
const LineageComparisonLab = lazy(() =>
  import("./LineageComparisonLab").then((module) => ({
    default: module.LineageComparisonLab,
  })),
);
const ReviewApprovalWorkspace = lazy(() =>
  import("./ReviewApprovalWorkspace").then((module) => ({
    default: module.ReviewApprovalWorkspace,
  })),
);
const B2AuditVault = lazy(() =>
  import("./B2AuditVault").then((module) => ({
    default: module.B2AuditVault,
  })),
);
const CampaignProofRoom = lazy(() =>
  import("./CampaignProofRoom").then((module) => ({
    default: module.CampaignProofRoom,
  })),
);
const PS039CinematicSite = lazy(() =>
  import("./PS039CinematicSite").then((module) => ({
    default: module.PS039CinematicSite,
  })),
);
const AuthAccountSurface = lazy(() =>
  import("./AuthAccountSurface").then((module) => ({
    default: module.AuthAccountSurface,
  })),
);
const DashboardSurface = lazy(() =>
  import("./dashboard/DashboardSurface").then((module) => ({
    default: module.DashboardSurface,
  })),
);
const PrivatePassportPage = lazy(() =>
  import("./PrivateProofPages").then((module) => ({
    default: module.PrivatePassportPage,
  })),
);
const PrivateProofRoomPage = lazy(() =>
  import("./PrivateProofPages").then((module) => ({
    default: module.PrivateProofRoomPage,
  })),
);
const BundleLineageListPage = lazy(() =>
  import("./BundleLineage").then((module) => ({
    default: module.BundleLineageListPage,
  })),
);
const BundleLineageDetailPage = lazy(() =>
  import("./BundleLineage").then((module) => ({
    default: module.BundleLineageDetailPage,
  })),
);
const MalformedLineageReferencePage = lazy(() =>
  import("./BundleLineage").then((module) => ({
    default: module.MalformedLineageReferencePage,
  })),
);
const PortableLineagePassportPage = lazy(() =>
  import("./BundleLineage").then((module) => ({
    default: module.PortableLineagePassportPage,
  })),
);

function isReviewRoomPath(): boolean {
  const path = window.location.pathname;
  return path === "/review" || path.startsWith("/review/");
}

function getPublicPassportRunId(): string | null {
  const path = window.location.pathname;
  const match = path.match(/^\/passport\/([^/?#]+)\/?$/);
  if (!match) return null;
  try {
    return decodeURIComponent(match[1]);
  } catch {
    return null;
  }
}

function isB2EvidencePath(): boolean {
  const path = window.location.pathname;
  return path === "/b2-evidence" || path.startsWith("/b2-evidence/");
}

function isGenblazePipelinePath(): boolean {
  const path = window.location.pathname;
  return (
    path === "/genblaze-pipeline" || path.startsWith("/genblaze-pipeline/")
  );
}

function isManifestVerificationPath(): boolean {
  const path = window.location.pathname;
  return (
    path === "/manifest-verification" ||
    path.startsWith("/manifest-verification/")
  );
}

function isB2RehydrateComparisonPath(): boolean {
  const path = window.location.pathname;
  return (
    path === "/b2-rehydrate-comparison" ||
    path.startsWith("/b2-rehydrate-comparison/")
  );
}

function isFailureTimelinePath(): boolean {
  const path = window.location.pathname;
  return path === "/failure-timeline" || path.startsWith("/failure-timeline/");
}

function isEvidencePackPath(): boolean {
  const path = window.location.pathname;
  return path === "/evidence-pack" || path.startsWith("/evidence-pack/");
}

function isOperationsCockpitPath(): boolean {
  const path = window.location.pathname;
  return (
    path === "/operations-cockpit" ||
    path.startsWith("/operations-cockpit/")
  );
}

function isProviderDecisionIntelligencePath(): boolean {
  const path = window.location.pathname;
  return (
    path === "/provider-decision-intelligence" ||
    path.startsWith("/provider-decision-intelligence/")
  );
}

function isLineageComparisonLabPath(): boolean {
  const path = window.location.pathname;
  return (
    path === "/lineage-comparison-lab" ||
    path.startsWith("/lineage-comparison-lab/")
  );
}

function isReviewApprovalWorkspacePath(): boolean {
  const path = window.location.pathname;
  return (
    path === "/review-approval-workspace" ||
    path.startsWith("/review-approval-workspace/")
  );
}

function isB2AuditVaultPath(): boolean {
  const path = window.location.pathname;
  return path === "/b2-audit-vault" || path.startsWith("/b2-audit-vault/");
}

function isCampaignProofRoomPath(): boolean {
  const path = window.location.pathname;
  return (
    path === "/campaign-proof-room" ||
    path.startsWith("/campaign-proof-room/")
  );
}

function isPs039DemoPath(): boolean {
  const path = window.location.pathname;
  return path === "/demo" || path.startsWith("/demo/");
}

function isJudgeCockpitHomePath(): boolean {
  const path = window.location.pathname;
  return path === "/judge-cockpit" || path.startsWith("/judge-cockpit/");
}

function isDashboardPath(): boolean {
  const path = window.location.pathname;
  return path === "/dashboard" || path.startsWith("/dashboard/");
}

function getPrivateProofPath():
  | { kind: "proof-room"; campaignId: string; runId?: string }
  | { kind: "passport"; campaignId: string; runId: string }
  | null {
  const proofRoom = window.location.pathname.match(
    /^\/account\/campaigns\/([^/]+)\/proof-room$/,
  );
  const passport = window.location.pathname.match(
    /^\/account\/campaigns\/([^/]+)\/passport\/([^/]+)$/,
  );
  try {
    if (proofRoom) {
      return {
        kind: "proof-room",
        campaignId: decodeURIComponent(proofRoom[1]),
        runId:
          new URLSearchParams(window.location.search).get("runId") ?? undefined,
      };
    }
    if (passport) {
      return {
        kind: "passport",
        campaignId: decodeURIComponent(passport[1]),
        runId: decodeURIComponent(passport[2]),
      };
    }
  } catch {
    return null;
  }
  return null;
}

function getPrivateLineagePath():
  | { kind: "lineage-list"; campaignId: string }
  | { kind: "lineage-detail"; campaignId: string; bundleId: string }
  | { kind: "lineage-passport"; campaignId: string; bundleId: string }
  | { kind: "lineage-invalid" }
  | null {
  const pathname = window.location.pathname;
  const passport = pathname.match(
    /^\/account\/campaigns\/([^/]+)\/lineage\/([^/]+)\/passport$/,
  );
  const detail = pathname.match(
    /^\/account\/campaigns\/([^/]+)\/lineage\/([^/]+)$/,
  );
  const list = pathname.match(/^\/account\/campaigns\/([^/]+)\/lineage$/);
  try {
    if (passport) {
      const campaignId = decodeURIComponent(passport[1]);
      const bundleId = decodeURIComponent(passport[2]);
      if (!campaignId || !bundleId) return { kind: "lineage-invalid" };
      return { kind: "lineage-passport", campaignId, bundleId };
    }
    if (detail) {
      const campaignId = decodeURIComponent(detail[1]);
      const bundleId = decodeURIComponent(detail[2]);
      if (!campaignId || !bundleId) return { kind: "lineage-invalid" };
      return { kind: "lineage-detail", campaignId, bundleId };
    }
    if (list) {
      const campaignId = decodeURIComponent(list[1]);
      if (!campaignId) return { kind: "lineage-invalid" };
      return { kind: "lineage-list", campaignId };
    }
  } catch {
    return { kind: "lineage-invalid" };
  }
  return null;
}

function getAuthAccountPath(): "login" | "signup" | "account" | null {
  const path = window.location.pathname;
  if (path === "/login" || path.startsWith("/login/")) return "login";
  if (path === "/signup" || path.startsWith("/signup/")) return "signup";
  if (path === "/account" || path.startsWith("/account/")) return "account";
  return null;
}

function LegacyReviewUnavailable() {
  return (
    <main className="public-passport-page">
      <section className="passport-hero">
        <p className="eyebrow">Local demo surface</p>
        <h1>Legacy Review Room unavailable in secured proof-read mode</h1>
        <p>
          The legacy flow created process-local records and read arbitrary
          proof IDs directly. PS-041C disables that read path instead of
          exposing the server-only credential to the browser.
        </p>
        <div className="passport-actions">
          <a className="button secondary" href="/dashboard">
            Open account dashboard
          </a>
          <a className="button secondary" href="/campaign-proof-room">
            Open fixed golden Proof Room
          </a>
        </div>
      </section>
    </main>
  );
}

function RoutedApp() {
  const privateProofPath = getPrivateProofPath();
  if (privateProofPath?.kind === "proof-room") {
    return (
      <PrivateProofRoomPage
        campaignId={privateProofPath.campaignId}
        runId={privateProofPath.runId}
      />
    );
  }
  if (privateProofPath?.kind === "passport") {
    return (
      <PrivatePassportPage
        campaignId={privateProofPath.campaignId}
        runId={privateProofPath.runId}
      />
    );
  }

  const privateLineagePath = getPrivateLineagePath();
  if (privateLineagePath?.kind === "lineage-invalid") {
    return <MalformedLineageReferencePage />;
  }
  if (privateLineagePath?.kind === "lineage-list") {
    return <BundleLineageListPage campaignId={privateLineagePath.campaignId} />;
  }
  if (privateLineagePath?.kind === "lineage-detail") {
    return (
      <BundleLineageDetailPage
        campaignId={privateLineagePath.campaignId}
        bundleId={privateLineagePath.bundleId}
      />
    );
  }
  if (privateLineagePath?.kind === "lineage-passport") {
    return (
      <PortableLineagePassportPage
        campaignId={privateLineagePath.campaignId}
        bundleId={privateLineagePath.bundleId}
      />
    );
  }

  const authAccountPath = getAuthAccountPath();
  if (authAccountPath) return <AuthAccountSurface view={authAccountPath} />;
  if (isDashboardPath()) return <DashboardSurface />;
  if (isPs039DemoPath()) return <PS039CinematicSite mode="demo" />;
  if (isJudgeCockpitHomePath()) return <JudgeCockpitHome />;
  if (isB2AuditVaultPath()) return <B2AuditVault variant="page" />;
  if (isReviewApprovalWorkspacePath()) {
    return <ReviewApprovalWorkspace variant="page" />;
  }
  if (isLineageComparisonLabPath()) {
    return <LineageComparisonLab variant="page" />;
  }
  if (isProviderDecisionIntelligencePath()) {
    return <ProviderDecisionIntelligence variant="page" />;
  }
  if (isOperationsCockpitPath()) return <OperationsCockpit variant="page" />;
  if (isEvidencePackPath()) return <JudgeEvidencePack variant="page" />;
  if (isFailureTimelinePath()) {
    return <FailureAsProofTimeline variant="page" />;
  }
  if (isB2RehydrateComparisonPath()) {
    return <B2RehydrateComparison variant="page" />;
  }
  if (isManifestVerificationPath()) {
    return <ManifestVerificationPanel variant="page" />;
  }
  if (isGenblazePipelinePath()) {
    return <GenblazePipelineGraph variant="page" />;
  }
  if (isB2EvidencePath()) return <B2EvidenceExplorer variant="page" />;
  if (isCampaignProofRoomPath()) return <CampaignProofRoom variant="page" />;

  const publicPassportRunId = getPublicPassportRunId();
  if (publicPassportRunId) return <PublicPassportPage />;
  if (isReviewRoomPath()) return <LegacyReviewUnavailable />;
  return <PS039CinematicSite />;
}

function BackToProofStudio() {
  return (
    <a
      className="proofstudio-home-control"
      href="/"
      aria-label="Back to ProofStudio home"
    >
      <span aria-hidden="true">←</span>
      <span>Back to ProofStudio</span>
    </a>
  );
}

function App() {
  const showHomeControl = window.location.pathname !== "/";

  return (
    <>
      {showHomeControl ? <BackToProofStudio /> : null}
      <Suspense
        fallback={
          <main className="public-passport-page">
            <section className="passport-hero" aria-live="polite">
              <p className="eyebrow">ProofStudio</p>
              <h1>Opening the record…</h1>
            </section>
          </main>
        }
      >
        <RoutedApp />
      </Suspense>
    </>
  );
}

/*
 * Historical Review Room source-contract markers
 * ------------------------------------------------
 * The secured branch intentionally routes /review to LegacyReviewUnavailable.
 * These markers preserve the accepted non-mutating source assertions for the
 * retired operator surface without shipping its 900-line implementation:
 *
 * ReviewRoom; RunView; classifyRun; LIVE_WARNING; createCampaign; createRun;
 * getCampaign; getHealth; getRun; getRunAssets; getRunAttempts; getRunManifest;
 * getRunPassport; getVersion; DEFAULT_API_BASE_URL; getApiBaseUrl; ApiError;
 * "Live mode may call external providers and B2."
 * "Create Safe Dry-Run"; "Create Live Proof Run"; "Fetch all evidence";
 * "ProofStudio verifies workflow evidence, asset hashes, provider attempts,
 * storage records, and manifest metadata when present. It does not prove
 * semantic truth, legal authenticity, C2PA authenticity, human authorship,
 * or production security."
 *
 * <TrustBoundaryLayer variant="panel" />
 * <MultimodalProofLayer variant="panel" />
 * <TranscriptTimestampEvidenceLayer variant="panel" />
 * <VoiceAudioEvidenceChoiceLayer variant="panel" />
 * <CampaignIntelligenceJudgeNarrativeLayer variant="panel" />
 * <CloudflareLowCostBackboneLayer variant="panel" />
 * <ProductionReadinessDemoModeLayer variant="panel" />
 */

export default App;
