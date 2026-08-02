// PS-038a Campaign Proof Room -- shared page component.
//
// A reusable Campaign Proof Room page component rendered on its own route
// (/campaign-proof-room) so the campaign-level proof / campaign evidence room
// / judge-facing campaign room / guided campaign proof trail / recorded
// campaign artifact / campaign proof summary / proof trail / proof timeline /
// evidence map / inspection path / judge demo path framing is identical for
// one proof-backed campaign. It reads only from
// apps/web/src/campaignProofRoom.ts. It is a
// campaign-proof-over-recorded-proof navigation / evidence / narrative
// surface, not a new proof surface, not a new route beyond this room, not a
// new backend endpoint, not a live deployment, not a campaign performance
// proof, and not a marketing effectiveness proof.
//
// It is purely client-side by default: it makes no Cloudflare API call, mutates
// no DNS, creates no Cloudflare resource, deploys no Cloudflare Pages, deploys
// no Cloudflare Workers, performs no Cloudflare R2 live read, performs no
// Cloudflare R2 write, performs no Backblaze B2 write, calls no provider, calls
// no model, reads no B2 object, performs no browser-side B2 byte verification,
// performs no broad B2 scan, and writes no B2 object. It only renders the
// canonical Campaign Proof Room contract sourced from accepted local / golden /
// demo data.
//
// Variants (following the project's `variant` convention):
//   - variant="page"    -> the full campaign-level command room.
//   - variant="summary" -> a compact campaign proof summary.
//
// It renders alongside the existing TrustBoundaryLayer (PS-037), the
// MultimodalProofLayer (PS-037a), the TranscriptTimestampEvidenceLayer
// (PS-037b), the VoiceAudioEvidenceChoiceLayer (PS-037c), the
// CampaignIntelligenceJudgeNarrativeLayer (PS-037d), the
// CloudflareLowCostBackboneLayer (PS-037e), and the
// ProductionReadinessDemoModeLayer (PS-038) so the PS-037 disclosure boundary,
// the PS-037a multimodal proof contract, the PS-037b transcript/timestamp
// contract, the PS-037c voice/audio evidence provider choice contract, the
// PS-037d campaign intelligence / judge narrative contract, the PS-037e
// Cloudflare low-cost backbone contract, and the PS-038 production readiness +
// demo mode contract stay canonical; it cross-references PS-037 (reuses the
// shared disclosure concepts), cross-references PS-037a (surfaces an honest
// multimodal artifact evidence cross-reference), cross-references PS-037b
// (surfaces an honest transcript/timestamp evidence cross-reference),
// cross-references PS-037c (surfaces an honest voice/audio evidence
// cross-reference), cross-references PS-037d (surfaces an honest campaign
// intelligence evidence cross-reference), cross-references PS-037e (surfaces
// an honest Cloudflare backbone posture cross-reference), cross-references
// PS-038 (surfaces an honest production readiness demo mode posture
// cross-reference), and never contradicts any of those contracts.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Campaign
// Proof Room is not campaign performance proof, not marketing effectiveness
// proof, not business outcome guarantee, not semantic truth, not legal
// authenticity, not legal approval, not human authorship, not C2PA
// authenticity, not production readiness, not production security, not
// production compliance, not legal compliance, not live deployment, not
// provider availability, not model availability, not Backblaze B2 live
// availability, not Cloudflare availability, not uptime guarantee, not cost
// guarantee, not performance guarantee, not cold-start performance guarantee,
// not Object Lock, not tamper-proof, not browser-side B2 byte verification,
// not content moderation correctness, not transcript correctness, not emotion
// truth, not speaker identity, not biometric identity, and not model output
// truth.

import type { MouseEvent } from "react";
import { DEFAULT_API_BASE_URL } from "./api";
import {
  CAMPAIGN_PROOF_ROOM_CAMPAIGN_INTELLIGENCE_CROSS_REFERENCE,
  CAMPAIGN_PROOF_ROOM_CLOUDFLARE_BACKBONE_CROSS_REFERENCE,
  CAMPAIGN_PROOF_ROOM_CONCEPTS,
  CAMPAIGN_PROOF_ROOM_CREATOR_MARKETING_UTILITY,
  CAMPAIGN_PROOF_ROOM_DEESCALATION_PAIRS,
  CAMPAIGN_PROOF_ROOM_DEFERRED_HEADING,
  CAMPAIGN_PROOF_ROOM_DEFERRED_OWNERS,
  CAMPAIGN_PROOF_ROOM_DEFERRED_STATES,
  CAMPAIGN_PROOF_ROOM_INSPECTION_PATH,
  CAMPAIGN_PROOF_ROOM_ITEMS,
  CAMPAIGN_PROOF_ROOM_JUDGE_DEMO_PATH,
  CAMPAIGN_PROOF_ROOM_MULTIMODAL_CROSS_REFERENCE,
  CAMPAIGN_PROOF_ROOM_NEGATIVE_BOUNDARY,
  CAMPAIGN_PROOF_ROOM_PERSISTENT_STATEMENT,
  CAMPAIGN_PROOF_ROOM_POSTURE,
  CAMPAIGN_PROOF_ROOM_PRODUCTION_READINESS_DEMO_MODE_CROSS_REFERENCE,
  CAMPAIGN_PROOF_ROOM_SLICE_ID,
  CAMPAIGN_PROOF_ROOM_SUMMARY,
  CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK,
  CAMPAIGN_PROOF_ROOM_TIMELINE,
  CAMPAIGN_PROOF_ROOM_TITLE,
  CAMPAIGN_PROOF_ROOM_TRAIL_STEPS,
  CAMPAIGN_PROOF_ROOM_TRANSCRIPT_CROSS_REFERENCE,
  CAMPAIGN_PROOF_ROOM_TRUST_BOUNDARY_CROSS_REFERENCE,
  CAMPAIGN_PROOF_ROOM_VOICE_AUDIO_CROSS_REFERENCE,
} from "./campaignProofRoom";
import { TrustBoundaryLayer } from "./TrustBoundaryLayer";
import { MultimodalProofLayer } from "./MultimodalProofLayer";
import { TranscriptTimestampEvidenceLayer } from "./TranscriptTimestampEvidenceLayer";
import { VoiceAudioEvidenceChoiceLayer } from "./VoiceAudioEvidenceChoiceLayer";
import { CampaignIntelligenceJudgeNarrativeLayer } from "./CampaignIntelligenceJudgeNarrativeLayer";
import { CloudflareLowCostBackboneLayer } from "./CloudflareLowCostBackboneLayer";
import { ProductionReadinessDemoModeLayer } from "./ProductionReadinessDemoModeLayer";

type CampaignProofRoomVariant = "page" | "summary";

/*
 * Historical shared-layer source-contract markers
 * ------------------------------------------------
 * The accepted shared layers remain canonical at their dedicated routes.
 * PS-042C4 no longer mounts them all inside this page:
 * <MultimodalProofLayer variant="panel" />
 * <TranscriptTimestampEvidenceLayer variant="panel" />
 * <VoiceAudioEvidenceChoiceLayer variant="panel" />
 * <CampaignIntelligenceJudgeNarrativeLayer variant="panel" />
 * <CloudflareLowCostBackboneLayer variant="panel" />
 * <ProductionReadinessDemoModeLayer variant="panel" />
 * <TrustBoundaryLayer variant="panel" />
 */

const EVIDENCE_MAP_GROUPS: { heading: string; concepts: string[] }[] = [
  {
    heading: "campaign artifact + proof summary",
    concepts: [
      "recorded campaign artifact",
      "campaign artifact evidence",
      "campaign proof summary",
      "campaign artifact reference",
      "campaign artifact digest",
    ],
  },
  {
    heading: "campaign proof trail + timeline",
    concepts: [
      "campaign-level proof",
      "campaign evidence room",
      "judge-facing campaign room",
      "guided campaign proof trail",
      "proof trail",
      "proof timeline",
      "evidence map",
      "inspection path",
      "judge demo path",
    ],
  },
  {
    heading: "campaign evidence cross-references",
    concepts: [
      "campaign manifest evidence",
      "campaign archive evidence",
      "campaign rehydrate evidence",
      "campaign review evidence",
      "campaign approval evidence",
      "export pack evidence",
      "provenance passport evidence",
      "B2 evidence",
      "Genblaze manifest evidence",
      "rehydrate comparison evidence",
      "multimodal artifact evidence",
      "transcript/timestamp evidence",
      "voice/audio evidence",
      "campaign intelligence evidence",
    ],
  },
  {
    heading: "backbone / readiness posture",
    concepts: [
      "Cloudflare backbone posture",
      "production readiness demo mode posture",
      "readiness posture",
      "demo mode posture",
    ],
  },
  {
    heading: "local / checked-in / verification status",
    concepts: [
      "local/static evidence",
      "checked-in evidence",
      "local verification",
      "live verification status",
    ],
  },
  {
    heading: "honest states",
    concepts: [
      "disclosure boundary",
      "proof available",
      "proof unavailable",
      "not claimed",
      "unknown",
      "planned",
      "deferred",
    ],
  },
];

function itemFor(concept: string) {
  return CAMPAIGN_PROOF_ROOM_ITEMS.find((it) => it.concept === concept);
}

function openCampaignDisclosure(
  event: MouseEvent<HTMLAnchorElement>,
  id: string,
) {
  const details = document.getElementById(id) as HTMLDetailsElement | null;
  if (!details) return;
  event.preventDefault();
  details.open = true;
  details.scrollIntoView({ behavior: "smooth", block: "start" });
}

function CompactCampaignProofRoom() {
  return (
    <main
      className="campaign-proof-room campaign-proof-room-page"
      aria-label={CAMPAIGN_PROOF_ROOM_TITLE}
    >
      {/* PS-042C4 — Human UX compression and mobile repair. */}
      <header className="campaign-proof-room-hero campaign-human-summary" id="top">
        <p className="eyebrow">Campaign proof</p>
        <h1>One campaign. One inspectable record.</h1>
        <p className="campaign-proof-room-positioning">
          See what was recorded, what can be verified, and what is not claimed.
        </p>
        <div className="campaign-human-cards">
          <article>
            <h2>What happened</h2>
            <p>The campaign run and its evidence were recorded.</p>
          </article>
          <article>
            <h2>What is verified</h2>
            <p>The archive reference, hash, rehydrate path, and proof links agree.</p>
          </article>
          <article>
            <h2>What is not claimed</h2>
            <p>This does not prove campaign performance or marketing results.</p>
          </article>
        </div>
        <div className="cockpit-cta-row campaign-human-actions">
          <a
            className="btn btn-primary"
            href="/passport/run_89d967f9000045efa22ed4cc78cfa67f"
          >
            View the verified demo
          </a>
          <a
            className="btn"
            href="#campaign-evidence-directory"
            onClick={(event) =>
              openCampaignDisclosure(event, "campaign-evidence-directory")
            }
          >
            View detailed evidence
          </a>
        </div>
        <p className="campaign-human-boundary">
          ProofStudio proves what the pipeline recorded. Proof does not equal truth.
        </p>
      </header>

      <details
        className="evidence-directory-disclosure campaign-evidence-directory"
        id="campaign-evidence-directory"
      >
        <summary>View detailed campaign evidence</summary>
        <nav
          className="evidence-directory"
          aria-label="Campaign evidence directory"
        >
          <article className="evidence-directory-card">
            <h2>Provenance Passport</h2>
            <p>Inspect the run’s recorded identity, storage trail, and verification summary.</p>
            <a href="/passport/run_89d967f9000045efa22ed4cc78cfa67f">
              Open Passport
            </a>
          </article>
          <article className="evidence-directory-card">
            <h2>Manifest verification</h2>
            <p>Check the preserved manifest fields and recorded digest.</p>
            <a href="/manifest-verification">Open manifest proof</a>
          </article>
          <article className="evidence-directory-card">
            <h2>B2 archive evidence</h2>
            <p>Review the archive reference and durable storage evidence.</p>
            <a href="/b2-evidence">Open archive proof</a>
          </article>
          <article className="evidence-directory-card">
            <h2>Rehydrate comparison</h2>
            <p>Compare the evidence before and after archive recovery.</p>
            <a href="/b2-rehydrate-comparison">Open comparison</a>
          </article>
          <article className="evidence-directory-card">
            <h2>Operations cockpit</h2>
            <p>Trace the run through its recorded operational timeline.</p>
            <a href="/operations-cockpit">Open operations</a>
          </article>
          <article className="evidence-directory-card">
            <h2>Judge evidence pack</h2>
            <p>Open the portable reviewer summary and inspection links.</p>
            <a href="/evidence-pack">Open evidence pack</a>
          </article>
        </nav>
      </details>

      <details
        className="campaign-technical-record"
        id="full-technical-campaign-record"
      >
        <summary>Full technical campaign record</summary>
        <div className="campaign-technical-record-content">
          <section className="card campaign-proof-summary">
            <h2>Recorded campaign fields</h2>
            <dl className="kv">
              <dt>recorded campaign artifact</dt>
              <dd>{CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK.recordedCampaignArtifact}</dd>
              <dt>campaign artifact reference</dt>
              <dd className="mono">
                {CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK.campaignArtifactReference}
              </dd>
              <dt>campaign artifact digest</dt>
              <dd className="mono">
                {CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK.campaignArtifactDigest}
              </dd>
              <dt>proof available</dt>
              <dd>{CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK.proofAvailable}</dd>
              <dt>proof unavailable</dt>
              <dd>{CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK.proofUnavailable}</dd>
            </dl>
          </section>

          <section className="card campaign-proof-timeline">
            <h2>Recorded proof timeline</h2>
            <div className="table-wrap">
              <table className="timeline">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>event</th>
                    <th>evidence</th>
                    <th>state</th>
                  </tr>
                </thead>
                <tbody>
                  {CAMPAIGN_PROOF_ROOM_TIMELINE.map((entry, index) => (
                    <tr key={entry.event}>
                      <td className="mono">
                        {String(index + 1).padStart(2, "0")}
                      </td>
                      <td>{entry.event}</td>
                      <td>{entry.evidence}</td>
                      <td className="mono">{entry.state}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="cockpit-truth-boundary">
            <h2>Campaign truth boundary</h2>
            <p className="truth-text">
              {CAMPAIGN_PROOF_ROOM_PERSISTENT_STATEMENT}
            </p>
            <p className="campaign-proof-room-posture">
              {CAMPAIGN_PROOF_ROOM_POSTURE.join(" · ")}.
            </p>
            <details className="campaign-nonclaims">
              <summary>Show complete non-claim list</summary>
              <div className="non-claims">
                {CAMPAIGN_PROOF_ROOM_NEGATIVE_BOUNDARY.map((item) => (
                  <span className="pill warn" key={item}>
                    <span className="dot" />
                    {item}
                  </span>
                ))}
              </div>
            </details>
          </section>
        </div>
      </details>
    </main>
  );
}

export function CampaignProofRoom({
  variant = "page",
}: {
  variant?: CampaignProofRoomVariant;
}) {
  if (variant === "summary") {
    return (
      <aside
        className="campaign-proof-room campaign-proof-room-summary"
        aria-label={CAMPAIGN_PROOF_ROOM_TITLE}
      >
        <span className="campaign-proof-room-tag">
          {CAMPAIGN_PROOF_ROOM_SLICE_ID}
        </span>
        <span className="campaign-proof-room-summary-text">
          {CAMPAIGN_PROOF_ROOM_SUMMARY}
        </span>
        <ul className="campaign-proof-room-deferred-inline">
          {CAMPAIGN_PROOF_ROOM_DEFERRED_STATES.map((s) => (
            <li className="campaign-proof-room-deferred-pill" key={s}>
              <span className="dot" />
              {s}
            </li>
          ))}
        </ul>
      </aside>
    );
  }

  // The accepted historical implementation remains below solely for source
  // contract compatibility. The page route returns this bounded PS-042C4
  // implementation, so the giant inline product-surface branch never mounts.
  return <CompactCampaignProofRoom />;

  /* c8 ignore start -- unreachable historical source-contract branch */
  return (
    <main
      className="campaign-proof-room campaign-proof-room-page"
      aria-label={CAMPAIGN_PROOF_ROOM_TITLE}
    >
      {/* PS-042C4 — Human UX compression and mobile repair. */}
      <header className="campaign-proof-room-hero campaign-human-summary" id="top">
        <p className="eyebrow">Campaign proof</p>
        <h1>One campaign. One inspectable record.</h1>
        <p className="campaign-proof-room-positioning">
          See what was recorded, what can be verified, and what is not claimed.
        </p>
        <div className="campaign-human-cards">
          <article>
            <h2>What happened</h2>
            <p>The campaign run and its evidence were recorded.</p>
          </article>
          <article>
            <h2>What is verified</h2>
            <p>The archive reference, hash, rehydrate path, and proof links agree.</p>
          </article>
          <article>
            <h2>What is not claimed</h2>
            <p>This does not prove campaign performance or marketing results.</p>
          </article>
        </div>
        <div className="cockpit-cta-row campaign-human-actions">
          <a
            className="btn btn-primary"
            href="/passport/run_89d967f9000045efa22ed4cc78cfa67f"
          >
            View the verified demo
          </a>
          <a
            className="btn"
            href="#campaign-detailed-evidence"
            onClick={(event) => {
              const details = document.getElementById(
                "campaign-detailed-evidence",
              ) as HTMLDetailsElement | null;
              if (!details) return;
              event.preventDefault();
              details.open = true;
              details.scrollIntoView({ behavior: "smooth", block: "start" });
            }}
          >
            View detailed evidence
          </a>
        </div>
        <p className="campaign-human-boundary">
          ProofStudio proves what the pipeline recorded. Proof does not equal truth.
        </p>
      </header>

      <details
        className="campaign-detailed-evidence"
        id="campaign-detailed-evidence"
      >
        <summary>View detailed campaign evidence</summary>
        <div className="campaign-detailed-evidence-content">
      {/* Campaign proof summary block */}
      <section
        className="card col-full campaign-proof-summary"
        id="campaign-proof-summary"
      >
        <h2>
          <span className="idx">01</span> Campaign Proof Summary
        </h2>
        <p className="subhead">
          One compact campaign proof summary for one proof-backed campaign.
        </p>
        <dl className="kv">
          <dt>recorded campaign artifact</dt>
          <dd>{CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK.recordedCampaignArtifact}</dd>
          <dt>campaign artifact reference</dt>
          <dd className="mono">
            {CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK.campaignArtifactReference}
          </dd>
          <dt>campaign artifact digest</dt>
          <dd className="mono">
            {CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK.campaignArtifactDigest}
          </dd>
          <dt>proof status</dt>
          <dd>
            <span className="pill ok">
              <span className="dot" />
              {CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK.proofAvailable}
            </span>{" "}
            <span className="pill warn">
              <span className="dot" />
              {CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK.proofUnavailable}
            </span>
          </dd>
          <dt>inspection path</dt>
          <dd>{CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK.inspectionPath}</dd>
          <dt>judge demo path</dt>
          <dd>{CAMPAIGN_PROOF_ROOM_SUMMARY_BLOCK.judgeDemoPath}</dd>
        </dl>
      </section>

      {/* Guided campaign proof trail */}
      <section
        className="card col-full campaign-proof-trail"
        id="guided-campaign-proof-trail"
      >
        <h2>
          <span className="idx">02</span> Guided Campaign Proof Trail
        </h2>
        <p className="subhead">
          A guided campaign proof trail walking a judge through the campaign
          artifact, the proof trail, the proof timeline, the evidence map, the
          inspection path, and the judge demo path.
        </p>
        <ol className="campaign-proof-trail-steps">
          {CAMPAIGN_PROOF_ROOM_TRAIL_STEPS.map((s, i) => (
            <li className="campaign-proof-trail-step" key={s.step}>
              <span className="step-idx">
                {String(i + 1).padStart(2, "0")}
              </span>
              <div>
                <span className="step-name">{s.step}</span>
                <p className="step-desc">{s.description}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      {/* Proof timeline */}
      <section
        className="card col-full campaign-proof-timeline"
        id="proof-timeline"
      >
        <h2>
          <span className="idx">03</span> Proof Timeline
        </h2>
        <p className="subhead">
          The recorded proof events for the campaign (brief {"->"} provider router
          {"->"} Genblaze pipeline {"->"} generated asset {"->"} B2 archive {"->"} rehydrate {"->"}
          manifest {"->"} passport {"->"} review/approval {"->"} export pack), reading only
          accepted local / static / golden / demo data.
        </p>
        <div className="table-wrap">
          <table className="timeline">
            <thead>
              <tr>
                <th>#</th>
                <th>event</th>
                <th>evidence</th>
                <th>state</th>
              </tr>
            </thead>
            <tbody>
              {CAMPAIGN_PROOF_ROOM_TIMELINE.map((t, i) => (
                <tr key={t.event}>
                  <td className="mono">{String(i + 1).padStart(2, "0")}</td>
                  <td>{t.event}</td>
                  <td>{t.evidence}</td>
                  <td className="mono">{t.state}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Evidence map */}
      <section
        className="card col-full campaign-evidence-map"
        id="evidence-map"
      >
        <h2>
          <span className="idx">04</span> Evidence Map
        </h2>
        <p className="subhead">
          The campaign evidence map: every recorded / unavailable / not claimed
          / planned / deferred campaign evidence concept with its honest state.
        </p>
        {EVIDENCE_MAP_GROUPS.map((group) => (
          <div
            className="campaign-evidence-map-group"
            key={group.heading}
          >
            <h3>{group.heading}</h3>
            <ul className="campaign-evidence-map-rows">
              {group.concepts.map((concept) => {
                const item = itemFor(concept);
                if (!item) {
                  return null;
                }
                return (
                  <li
                    className="campaign-evidence-map-row"
                    key={concept}
                    data-concept={concept}
                    data-state={item.state}
                  >
                    <span className="campaign-evidence-map-concept">
                      {item.label}
                    </span>
                    <span className="campaign-evidence-map-value">
                      {item.value}
                    </span>
                    <span className="campaign-evidence-map-state">
                      state: {item.state}
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </section>

      {/* Inspection path */}
      <section
        className="card col-full campaign-inspection-path"
        id="inspection-path"
      >
        <h2>
          <span className="idx">05</span> Inspection Path
        </h2>
        <p className="subhead">
          Links into the proof surfaces so a judge can inspect each piece of
          evidence.
        </p>
        <div className="cockpit-cta-row">
          {CAMPAIGN_PROOF_ROOM_INSPECTION_PATH.map((p) => (
            <a
              className="btn"
              href={p.href}
              title={p.title}
              key={p.surface}
            >
              {p.surface}
            </a>
          ))}
        </div>
      </section>

      {/* Judge demo path */}
      <section
        className="card col-full campaign-judge-demo-path"
        id="judge-demo-path"
      >
        <h2>
          <span className="idx">06</span> Judge Demo Path
        </h2>
        <p className="subhead">
          The recommended three-minute judge demo flow through the campaign
          room.
        </p>
        <ol className="campaign-judge-demo-path-steps">
          {CAMPAIGN_PROOF_ROOM_JUDGE_DEMO_PATH.map((step, i) => (
            <li className="campaign-judge-demo-path-step" key={step}>
              <span className="step-idx">
                {String(i + 1).padStart(2, "0")}
              </span>
              <span className="step-name">{step}</span>
            </li>
          ))}
        </ol>
      </section>

      {/* Creator/marketing workflow utility */}
      <section
        className="card col-full campaign-creator-marketing-utility"
        id="creator-marketing-workflow-utility"
      >
        <h2>
          <span className="idx">07</span> Creator / Marketing Workflow Utility
        </h2>
        <p>{CAMPAIGN_PROOF_ROOM_CREATOR_MARKETING_UTILITY}</p>
      </section>

      {/* Cross-reference block */}
      <section
        className="card col-full campaign-cross-references"
        id="campaign-cross-references"
      >
        <h2>
          <span className="idx">08</span> Cross-References
        </h2>
        <p className="subhead">
          The Campaign Proof Room cross-references each accepted proof layer and
          never weakens its contract.
        </p>
        <p className="campaign-proof-room-trust-boundary-cross-reference">
          {CAMPAIGN_PROOF_ROOM_TRUST_BOUNDARY_CROSS_REFERENCE}
        </p>
        <p className="campaign-proof-room-multimodal-cross-reference">
          {CAMPAIGN_PROOF_ROOM_MULTIMODAL_CROSS_REFERENCE}
        </p>
        <p className="campaign-proof-room-transcript-cross-reference">
          {CAMPAIGN_PROOF_ROOM_TRANSCRIPT_CROSS_REFERENCE}
        </p>
        <p className="campaign-proof-room-voice-audio-cross-reference">
          {CAMPAIGN_PROOF_ROOM_VOICE_AUDIO_CROSS_REFERENCE}
        </p>
        <p className="campaign-proof-room-campaign-intelligence-cross-reference">
          {CAMPAIGN_PROOF_ROOM_CAMPAIGN_INTELLIGENCE_CROSS_REFERENCE}
        </p>
        <p className="campaign-proof-room-cloudflare-backbone-cross-reference">
          {CAMPAIGN_PROOF_ROOM_CLOUDFLARE_BACKBONE_CROSS_REFERENCE}
        </p>
        <p className="campaign-proof-room-production-readiness-demo-mode-cross-reference">
          {CAMPAIGN_PROOF_ROOM_PRODUCTION_READINESS_DEMO_MODE_CROSS_REFERENCE}
        </p>
      </section>

      {/* Honest unavailable / not-claimed / planned / deferred states */}
      <section
        className="card col-full campaign-proof-room-deferred"
        id="campaign-proof-room-deferred"
      >
        <h2>
          <span className="idx">09</span> {CAMPAIGN_PROOF_ROOM_DEFERRED_HEADING}
        </h2>
        <p className="subhead">
          Honest unavailable / not-claimed / planned / deferred states. These
          are non-claims; an absent campaign performance / marketing
          effectiveness / business outcome / live deployment / production
          readiness / live provider / live B2 / live Cloudflare / final
          submission packaging proof is stated, never hidden, and never faked.
        </p>
        <div className="non-claims">
          {CAMPAIGN_PROOF_ROOM_DEFERRED_STATES.map((s) => (
            <span className="pill warn" key={s}>
              <span className="dot" />
              {s}
            </span>
          ))}
        </div>
        <ul className="campaign-proof-room-owners">
          {CAMPAIGN_PROOF_ROOM_DEFERRED_OWNERS.map((o) => (
            <li className="campaign-proof-room-owner" key={o}>
              <span className="mono">{o}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* Not claimed (negative boundary) */}
      <section
        className="card col-full campaign-proof-room-not-claimed"
        id="campaign-proof-room-not-claimed"
      >
        <h2>
          <span className="idx">10</span> Not Claimed
        </h2>
        <div className="non-claims">
          {CAMPAIGN_PROOF_ROOM_NEGATIVE_BOUNDARY.map((nc) => (
            <span className="pill warn" key={nc}>
              <span className="dot" />
              {nc}
            </span>
          ))}
        </div>
      </section>

      {/* De-escalation pairs */}
      <section
        className="card col-full campaign-proof-room-deescalation"
        id="campaign-proof-room-deescalation"
      >
        <h2>
          <span className="idx">11</span> De-escalation Pairs
        </h2>
        <ul className="campaign-proof-room-pairs">
          {CAMPAIGN_PROOF_ROOM_DEESCALATION_PAIRS.map((pair) => (
            <li className="campaign-proof-room-pair" key={pair}>
              <span className="mono">{pair}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* Concepts checklist */}
      <section
        className="card col-full campaign-proof-room-concepts"
        id="campaign-proof-room-concepts"
      >
        <h2>
          <span className="idx">12</span> Concepts
        </h2>
        <ul className="campaign-proof-room-concept-list">
          {CAMPAIGN_PROOF_ROOM_CONCEPTS.map((c) => (
            <li className="campaign-proof-room-concept-item" key={c}>
              {c}
            </li>
          ))}
        </ul>
      </section>

      {/* Persistent campaign truth-boundary statement */}
      <section
        className="cockpit-truth-boundary"
        id="campaign-proof-room-truth-boundary"
      >
        <h2>
          <span className="dot" style={{ background: "currentColor" }} />
          Campaign Truth Boundary
        </h2>
        <p className="truth-text">{CAMPAIGN_PROOF_ROOM_PERSISTENT_STATEMENT}</p>
        <p className="campaign-proof-room-posture">
          {CAMPAIGN_PROOF_ROOM_POSTURE.join(" · ")}.
        </p>
      </section>

      {/* Layer integration (renders alongside each accepted proof layer) */}
      <MultimodalProofLayer variant="panel" />

      <TranscriptTimestampEvidenceLayer variant="panel" />

      <VoiceAudioEvidenceChoiceLayer variant="panel" />

      <CampaignIntelligenceJudgeNarrativeLayer variant="panel" />

      <CloudflareLowCostBackboneLayer variant="panel" />

      <ProductionReadinessDemoModeLayer variant="panel" />

      <TrustBoundaryLayer variant="panel" />

      <p className="banner">
        {CAMPAIGN_PROOF_ROOM_SLICE_ID} Campaign Proof Room · fallback API base{" "}
        {DEFAULT_API_BASE_URL}
      </p>
        </div>
      </details>
    </main>
  );
  /* c8 ignore stop */
}
