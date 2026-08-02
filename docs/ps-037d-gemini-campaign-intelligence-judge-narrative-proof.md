# PS-037d — Gemini Campaign Intelligence / Judge Narrative

## 1. What PS-037d adds

PS-037d adds a reusable **Gemini Campaign Intelligence / Judge Narrative**
layer that turns ProofStudio's existing recorded proof stack into a single,
consistent, judge-facing campaign story. It is a narrative-over-recorded-proof
layer: it reads what the pipeline already recorded and renders a consistent
campaign proof narrative. It is not a new proof surface, not a new route, not a
new backend endpoint, not a live Gemini integration, and not a model generation
system.

PS-037d proves what the pipeline recorded for campaign intelligence / judge
narrative. Proof does not equal truth. The Gemini label does not equal live
Gemini availability. A model output reference does not equal semantic truth. A
judge narrative does not equal legal authenticity. Campaign intelligence does
not equal campaign performance. A campaign narrative does not equal marketing
effectiveness. Local campaign intelligence does not equal live Gemini
availability. Demo/golden campaign narrative does not equal production
security.

The layer:

- exposes the recorded campaign intelligence framing and the recorded judge
  narrative as local / demo narratives over recorded proof evidence;
- names Gemini as a campaign intelligence / judge narrative provider label for
  evidence labeling only (the Gemini label does not equal live Gemini
  availability);
- surfaces an honest "model output not available" / "Gemini evidence not
  available" state because no model output is checked into accepted evidence;
- summarizes the recorded proof stack (B2 archive / rehydrate evidence, Genblaze
  manifest evidence, the PS-037 Disclosure + Trust Boundary, the PS-037a
  Multimodal Proof Layer, the PS-037b Transcript/Timestamp Evidence layer, and
  the PS-037c Voice/Audio Evidence Provider Choice layer) into one consistent
  campaign proof narrative;
- cross-references PS-037, PS-037a, PS-037b, and PS-037c additively without
  weakening any of those contracts;
- states honestly what it proves, what it does not claim, and what is
  unavailable / not claimed / unknown.

## 2. Files changed

New files:

- `apps/web/src/geminiCampaignIntelligence.ts` — the canonical campaign
  intelligence / judge narrative data module (single shared source for every
  core proof surface).
- `apps/web/src/CampaignIntelligenceJudgeNarrativeLayer.tsx` — the shared
  campaign intelligence / judge narrative component (`variant="panel"` /
  `variant="summary"`).
- `scripts/ps037d_gemini_campaign_intelligence_judge_narrative_smoke.py` — the
  PS-037d feature smoke (local / static; non-mutating by default).
- `docs/ps-037d-gemini-campaign-intelligence-judge-narrative-proof.md` — this
  proof doc.
- `docs/evidence/ps-037d/gemini-campaign-intelligence-judge-narrative-report.json`
  — the PS-037d evidence report (written only when `--write-evidence` is
  explicit).

Additively modified files (import + render, no contract weakened):

- `apps/web/src/App.tsx` (Review Room)
- `apps/web/src/B2AuditVault.tsx`
- `apps/web/src/B2EvidenceExplorer.tsx`
- `apps/web/src/B2RehydrateComparison.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/JudgeEvidencePack.tsx`
- `apps/web/src/ManifestVerificationPanel.tsx`
- `apps/web/src/PublicPassportPage.tsx`
- `apps/web/src/ReviewApprovalWorkspace.tsx`
- `apps/web/src/styles.css` (additive campaign-intelligence classes only)

## 3. How Gemini campaign intelligence / judge narrative works

The data module (`geminiCampaignIntelligence.ts`) reads accepted local /
golden / demo data and existing accepted data modules as read-only inputs:

- archive reference / digest, rehydrate source, and provider-call count are
  reused verbatim from `apps/web/src/b2Evidence.ts` (PS-026 / PS-021);
- manifest reference / hash are reused verbatim from
  `apps/web/src/multimodalProof.ts` (PS-035A);
- the layer reuses the PS-037 disclosure concepts, the PS-037a multimodal proof
  framing, the PS-037b transcript/timestamp evidence framing, and the PS-037c
  voice/audio evidence provider choice framing.

The component (`CampaignIntelligenceJudgeNarrativeLayer.tsx`) renders the layer
in two variants: a compact `summary` campaign evidence summary and an expanded
`panel` judge-narrative panel. It reads only from the data module. It is
rendered additively alongside `TrustBoundaryLayer` (PS-037),
`MultimodalProofLayer` (PS-037a), `TranscriptTimestampEvidenceLayer` (PS-037b),
and `VoiceAudioEvidenceChoiceLayer` (PS-037c) on every required core proof
surface.

No value is invented. Where no accepted campaign intelligence / model output
exists, the layer surfaces explicit honest "not available" / "not claimed" /
"unknown" states.

## 4. Why Gemini label does not equal live Gemini availability

Gemini is named as a campaign intelligence / judge narrative provider label for
evidence labeling only. Naming Gemini does not imply a live Gemini API call,
live Gemini availability, live model availability, or any correctness guarantee.
PS-037d makes no Gemini API call, no model call, and no provider call. The
default posture is local / demo / golden fixture evidence with "live provider
evidence not available", "Gemini evidence not available", and "model output not
available". Therefore the Gemini label does not equal live Gemini availability.

## 5. Why model output does not equal semantic truth

No model output is checked into accepted evidence, so the layer surfaces honest
"model output not available" and "Gemini evidence not available" states and
never fabricates a model output reference or digest. Even where a model output
reference is recorded as evidence, it is surfaced as local / recorded-only.
PS-037d does not prove model output truth. Therefore a model output reference
does not equal semantic truth.

## 6. Why campaign intelligence does not equal campaign performance

PS-037d renders the recorded campaign intelligence framing over accepted proof
evidence. It does not predict campaign performance, does not score marketing
effectiveness, does not forecast business outcomes, and does not measure
conversion lift, revenue impact, audience targeting accuracy, or ad compliance
approval. Each of those is surfaced as an honest "not claimed" state. Therefore
campaign intelligence does not equal campaign performance.

## 7. Why judge narrative does not equal legal authenticity

The judge narrative is a recorded, judge-facing summary over the recorded proof
stack. It is local / demo narrative evidence, not a legal review, not a legal
authenticity verdict, and not a chain-of-custody guarantee. PS-037d does not
prove legal authenticity. Therefore a judge narrative does not equal legal
authenticity.

## 8. Local / static default; no live behavior

PS-037d is local / static by default. It performs: no Gemini API calls, no
provider calls, no live B2 reads, no B2 writes, and no broad B2 scans. It adds
no new backend, no new Gemini client, no new model client, no new provider
wrapper, no new B2 client, no new env variable, and no deployment change. It
works offline from accepted local / golden / demo fixtures.

## 9. PS-037 / PS-037a / PS-037b / PS-037c preservation and cross-reference

- PS-037 Disclosure + Trust Boundary: the campaign intelligence / judge
  narrative layer renders alongside `TrustBoundaryLayer`, reuses the shared
  disclosure concepts, and never contradicts the PS-037 boundary.
- PS-037a Multimodal Proof Layer: the layer renders alongside
  `MultimodalProofLayer` and fills the concrete campaign intelligence / judge
  narrative evidence that PS-037a reserved as "campaign intelligence not
  available -> deferred to PS-037d". The PS-037a deferred state is not removed.
- PS-037b Transcript/Timestamp Evidence: the layer renders alongside
  `TranscriptTimestampEvidenceLayer` and surfaces an honest
  transcript/timestamp cross-reference; the PS-037b contract is not weakened.
- PS-037c Voice/Audio Evidence Provider Choice: the layer renders alongside
  `VoiceAudioEvidenceChoiceLayer` and surfaces an honest voice/audio evidence
  cross-reference; the PS-037c contract is not weakened.

PS-037d does not edit the PS-037, PS-037a, PS-037b, or PS-037c contract files.
The shared `.trust-boundary-layer*` classes, the multimodal proof layer classes,
the transcript/timestamp evidence layer classes, and the voice/audio evidence
provider choice layer classes are not removed or weakened; only additive
campaign-intelligence classes are added to `styles.css`.

## 10. Validation commands and results

Feature smoke (non-mutating local validation):

```
python scripts/ps037d_gemini_campaign_intelligence_judge_narrative_smoke.py --check-only --no-frontend
```

Feature smoke (writes only `docs/evidence/ps-037d/` evidence):

```
python scripts/ps037d_gemini_campaign_intelligence_judge_narrative_smoke.py --write-evidence --no-frontend
```

Central regression gate (contract-only):

```
python scripts/proofstudio_regression_gate.py --current ps037d --no-frontend --report-out /tmp/proofstudio-ps037d-regression-report.json
```

Frontend typecheck:

```
cd apps/web && npx tsc --noEmit
```

Hidden Git flags check (explicit h / S over `git ls-files -v`, fails on
`line[0]` == `h` or `S`):

```
git ls-files -v
```

Whitespace / conflict-marker check:

```
git diff --check
```

All of the above pass for this slice. The PS-037d evidence report at
`docs/evidence/ps-037d/gemini-campaign-intelligence-judge-narrative-report.json`
carries `ok: true`, `slice_id: ps037d`, and an empty `failures` list, with real
JSON booleans for every measured field.

## 11. Truth boundary / negative claims

PS-037d proves what the pipeline recorded. The Gemini Campaign Intelligence /
Judge Narrative Layer is: not model output truth, not semantic truth, not legal
authenticity, not human authorship, not C2PA authenticity, not Object Lock, not
tamper-proof, not browser-side B2 byte verification, not live B2 availability,
not live Gemini availability, not production security, not production
compliance, not legal review, not chain-of-custody guarantee, not campaign
performance prediction, not marketing effectiveness proof, not business outcome
guarantee, not conversion lift, not revenue impact, not audience targeting
accuracy, not ad compliance approval, not identity verification, not biometric
identification, not deepfake detection, not content moderation, not OCR
correctness, not transcript correctness, not timestamp correctness, not voice
authenticity, not speaker identity, and not emotion truth.

PS-037d obeys the root `AGENTS.md` operating law: no hidden Git flags, no
recursive smokes, no Gemini API calls, no provider calls, no live B2 reads, no
B2 writes, no broad B2 scans, and no staging, commit, or push.
