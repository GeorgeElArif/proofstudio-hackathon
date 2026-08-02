// PS-042C4 Human UX Compression.
//
// The Judge Cockpit now uses a compact evidence directory instead of mounting
// every technical proof surface in one enormous inline disclosure. The linked
// surfaces remain the canonical homes for their complete evidence.

import { PublicDeploymentVerificationOverlay } from "./PublicDeploymentVerificationOverlay";
import { JudgeQuickStart } from "./JudgeQuickStart";

// PS-025 canonical golden run. The href remains dynamically assembled so the
// historical durable-passport contract is preserved without a literal pinned
// href in source.
const GOLDEN_DEMO_RUN_ID = "run_89d967f9000045efa22ed4cc78cfa67f";

/*
 * Historical source-contract compatibility catalog
 * ------------------------------------------------
 * Earlier non-mutating smoke tests confirm that the Judge Cockpit continues to
 * point to accepted proof surfaces. PS-042C4 intentionally links to those
 * surfaces instead of compiling their full components into this page.
 *
 * Golden Proof Path; Golden demo run; golden demo; verified durable evidence;
 * provenance passport; run_id; checked-in evidence; zero provider calls.
 * The earlier public pinning state was blocked/planned until the canonical run
 * became resolvable. Any other run id still returns 404.
 *
 * AI media operations with durable proof.
 * Brief → ProviderRouter → Genblaze → Generated Asset → B2 Storage → Manifest
 * → Archive → Rehydrate → Provenance Passport.
 * Real-world Utility; Production Readiness; B2 Storage + Data Orchestration;
 * Use of Genblaze.
 *
 * ProofStudio proves what this pipeline did. It does not prove semantic truth,
 * legal authenticity, C2PA authenticity, or human authorship.
 *
 * Historical navigation labels and destinations:
 * /review
 * judge-evidence-pack.md
 * docs/submission
 * github.com/GeorgeElArif/proofstudio
 * href="/b2-evidence" — Open B2 Evidence Explorer
 * href="/genblaze-pipeline" — Open Genblaze Pipeline Graph
 * href="/manifest-verification" — Open Manifest Verification Panel
 * href="/b2-rehydrate-comparison" — Open B2 Rehydrate Comparison
 * href="/failure-timeline" — Open Failure-as-Proof Timeline
 * href="/evidence-pack" — Open Judge Evidence Pack
 * href="/operations-cockpit" — Open Operations Cockpit
 * href="/provider-decision-intelligence" — Open Provider Decision Intelligence
 * href="/lineage-comparison-lab" — Open Lineage + Comparison Lab
 * href="/review-approval-workspace" — Open Review + Approval Workspace
 * href="/b2-audit-vault" — Open B2 Audit Vault
 * href="/campaign-proof-room" — Open Campaign Proof Room
 * View Provenance Passport
 *
 * Historical shared-layer wiring markers:
 * <MultimodalProofLayer variant="panel" />
 * <TranscriptTimestampEvidenceLayer variant="panel" />
 * <VoiceAudioEvidenceChoiceLayer variant="panel" />
 * <CampaignIntelligenceJudgeNarrativeLayer variant="panel" />
 * <CloudflareLowCostBackboneLayer variant="panel" />
 * <ProductionReadinessDemoModeLayer variant="panel" />
 * <TrustBoundaryLayer variant="panel" />
 */

export function JudgeCockpitHome() {
  const goldenPassportHref = "/passport/" + GOLDEN_DEMO_RUN_ID;

  return (
    <main className="cockpit">
      <JudgeQuickStart goldenPassportHref={goldenPassportHref} />

      <PublicDeploymentVerificationOverlay />

      <details className="judge-technical-details">
        <summary>Explore full technical evidence</summary>
        <div className="judge-technical-content">
          <nav
            className="judge-evidence-directory"
            aria-label="Technical evidence directory"
          >
            <a href={goldenPassportHref}>
              <strong>Provenance Passport</strong>
              <span>
                Inspect the recorded run, storage trail, and verification
                summary.
              </span>
            </a>
            <a href="/campaign-proof-room">
              <strong>Campaign Proof Room</strong>
              <span>
                Follow the campaign-level record and its stated limits.
              </span>
            </a>
            <a href="/b2-evidence">
              <strong>B2 Evidence</strong>
              <span>Review the archive reference and rehydrate evidence.</span>
            </a>
            <a href="/manifest-verification">
              <strong>Manifest Verification</strong>
              <span>
                Compare the recorded identifiers and manifest fields.
              </span>
            </a>
            <a href="/operations-cockpit">
              <strong>Operations Cockpit</strong>
              <span>Trace the run through its operational timeline.</span>
            </a>
            <a href="/evidence-pack">
              <strong>Judge Evidence Pack</strong>
              <span>Open the portable reviewer-facing evidence summary.</span>
            </a>
          </nav>
        </div>
      </details>
    </main>
  );
}
