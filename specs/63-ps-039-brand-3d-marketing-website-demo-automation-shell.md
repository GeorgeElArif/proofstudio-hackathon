# PS-039 — Brand Identity + 3D Marketing Website + Demo Automation Shell

Status: Spec only.
Slice: PS-039
Date: 2026-07-03
Branch: `ps-039/brand-3d-marketing-website-demo-automation-shell`
Spec: `specs/63-ps-039-brand-3d-marketing-website-demo-automation-shell.md`

## 1. Status

PS-039 — Brand Identity + 3D Marketing Website + Demo Automation Shell is
currently:

- Spec only.
- The authoritative written specification for the brand identity foundation,
  the cinematic 3D marketing website, the Campaign Proof Room presentation
  path, and the demo automation shell.
- No implementation code. No app files. No scripts. No evidence mutation. No
  env/secrets changes. No deployment changes. No provider calls. No model
  calls. No B2 reads/writes. No Cloudflare API/DNS/resource/deploy/R2
  behavior.

PS-039 must not implement the brand assets, must not implement the 3D
marketing website, must not implement the demo automation shell, must not
implement auth, must not implement the dashboard, must not deploy anything,
and must not run any provider, model, B2, or Cloudflare behavior. PS-039
records the specification only. It does not claim implementation exists.

The authoritative accepted base is the dynamic Git ref
`origin/accepted/proofstudio`, never a hardcoded commit hash. At the time of
this spec the ref resolves to commit
`7426d7e5d4f3d1009774d38ffe1d581a42ac71ad` (the post-PS-038b accepted state:
the Winning Product Presentation Architecture from PS-038b is specified, the
Campaign Proof Room from PS-038a is specified, and PS-038 Production
Readiness + Demo Mode is accepted). The ref is the authority; the commit hash
is recorded for traceability only and must not be treated as a hardcoded
base. PS-039 starts from `origin/accepted/proofstudio`, not from `main`.

This slice touches only this file:

- `specs/63-ps-039-brand-3d-marketing-website-demo-automation-shell.md` (this
  spec)

The roadmap ledgers (`specs/07-master-spec-plan.md` and
`specs/08-roadmap-slices.md`) already list PS-039 — Brand Identity + 3D
Marketing Website + Demo Automation Shell correctly (added by PS-038b), so
PS-039 does not modify them.

PS-039 obeys the root `AGENTS.md` operating law and the validation policy in
`docs/validation/proofstudio-smoke-harness-v1.md`. PS-039 does not weaken any
truth boundary from PS-037 through PS-038b.

PS-039a adds a required rebuild authority amendment after a rejected
GLM-built PS-039 implementation failed visual/product gate. That rejected
implementation must not be staged, must not be committed, must not be
accepted, must not be repaired by GLM, and must not be restored from discarded
working tree. GLM is excluded from PS-039 website and PS-041 dashboard
build/repair work. Codex GPT-5.5 in VS Code is the repo builder for the PS-039
website rebuild.

## 2. Purpose

PS-039 creates the authoritative written specification for ProofStudio's
brand identity foundation, cinematic 3D marketing website, Campaign Proof
Room presentation path, and demo automation shell, so that the future
implementation of PS-039 is spec-first and not improvised.

PS-039 locks the agreed specification for:

- the brand identity outputs and the logo/mark direction (without finalizing
  irreversible brand assets in this spec)
- the Proof Core / Evidence Orb / Campaign Record 3D metaphor
- the cinematic landing page structure and the scroll/story sequence
- the Campaign Proof Room CTA and the Judge demo CTA
- the demo automation shell behavior
- the B2 archive evidence story, the Genblaze manifest evidence story, the
  rehydrate check story, the review decision story, the provenance passport
  story, and the export pack story as on-page proof narratives
- the reduced-motion fallback, the mobile/tablet/desktop visual requirements,
  the screenshot evidence requirements, the accessibility requirements, and
  the performance constraints
- the future implementation file expectations, the validation gates, and the
  visual acceptance criteria
- the truth-boundary copy and the explicitly local/demo/static behavior

PS-039 exists because PS-038b recorded the presentation architecture as
strategy, but strategy is not a buildable specification. Before any brand,
3D, or demo-automation code is written, the repo needs a single authoritative
spec that defines scope, routes, metaphor behavior, story sequence, CTAs,
demo shell behavior, visual/accessibility/performance requirements, file
expectations, validation gates, acceptance criteria, and truth-boundary copy.
This spec is that document.

PS-039 does not implement the 3D website. PS-039 does not implement brand
assets. PS-039 does not implement the demo automation shell. PS-039 does not
implement auth. PS-039 does not implement the dashboard. PS-039 records the
specification only.

## 3. Root cause / product gap

PS-038b corrected the post-proof-core sequence and recorded the presentation
architecture as strategy. But strategy alone is not buildable. The next
implementation slice (the future build of PS-039) needs a deterministic,
auditable specification that defines:

- exactly which routes/pages the 3D marketing website owns
- exactly which brand identity outputs the build must produce
- exactly how the Proof Core / Evidence Orb / Campaign Record metaphor behaves
  on the page
- exactly how the scroll/story sequence unfolds
- exactly what the Campaign Proof Room CTA and the Judge demo CTA do
- exactly how the demo automation shell drives the page for a demo
- exactly which proof stories (B2 archive evidence, Genblaze manifest
  evidence, rehydrate check, review decision, provenance passport, export
  pack) appear on the page
- exactly how reduced-motion, mobile/tablet/desktop, accessibility,
  performance, and screenshot evidence must behave
- exactly which files the future build is expected to add or change
- exactly which validation gates the future build must pass
- exactly which visual acceptance criteria define "done"
- exactly which truth-boundary copy the page must carry

Without this spec, the future build of PS-039 would drift into ad hoc design
choices. PS-039 closes that gap by writing the authoritative specification
before any implementation begins.

This is a specification slice, not an implementation. PS-039 does not write
any implementation code and does not change any product, backend, provider,
deployment, env, or requirements file.

## 4. Current accepted base

The current accepted base for PS-039 is:

- branch: `accepted/proofstudio`
- ref: `origin/accepted/proofstudio` (the authoritative source of truth; the
  ref is the authority, not any hardcoded commit hash)
- commit the ref resolves to at the time of this spec:
  `7426d7e5d4f3d1009774d38ffe1d581a42ac71ad`
- this is the post-PS-038b accepted state: the Winning Product Presentation
  Architecture is specified
  (`specs/62-ps-038b-winning-product-presentation-architecture.md`); the
  Campaign Proof Room is specified
  (`specs/61-ps-038a-campaign-proof-room.md`); PS-038 Production Readiness +
  Demo Mode is accepted; the Disclosure + Trust Boundary Layer (PS-037), the
  Multimodal Proof Layer (PS-037a), the Transcript/Timestamp Evidence layer
  (PS-037b), the Voice/Audio Evidence Provider Choice layer (PS-037c), the
  Gemini Campaign Intelligence / Judge Narrative layer (PS-037d), and the
  Cloudflare Low-Cost Backbone layer (PS-037e) are all in place; the root
  `AGENTS.md` operating law (PS-035D) is in place; the central regression
  gate is non-mutating by default (PS-035C); the golden-fixture digest freeze
  (PS-035B) and the golden-run manifest correctness (PS-035A) are in place.

PS-039 must start from `origin/accepted/proofstudio`, not from `main`.

PS-039 must not weaken any truth boundary from PS-037 through PS-038b, must
not change any golden run canonical constant, and must not change any
historical contract the regression gate verifies.

## 5. Scope

PS-039 is a specification slice. It owns the written specification for the
future brand identity + 3D marketing website + demo automation shell build.
It must:

1. Define the PS-039 scope (this section).
2. Define the non-goals (section 6).
3. Define the route/page target for future implementation (section 7).
4. Define the brand identity outputs (section 8).
5. Define the logo/mark direction without finalizing irreversible brand
   assets (section 9).
6. Define the Proof Core / Evidence Orb / Campaign Record 3D metaphor
   (section 10).
7. Define the cinematic landing page structure (section 11).
8. Define the scroll/story sequence (section 12).
9. Define the Campaign Proof Room CTA (section 13).
10. Define the Judge demo CTA (section 14).
11. Define the demo automation shell behavior (section 15).
12. Define the B2 archive evidence story (section 16.1).
13. Define the Genblaze manifest evidence story (section 16.2).
14. Define the rehydrate check story (section 16.3).
15. Define the review decision story (section 16.4).
16. Define the provenance passport story (section 16.5).
17. Define the export pack story (section 16.6).
18. Define the reduced-motion fallback (section 17).
19. Define the mobile/tablet/desktop visual requirements (section 18).
20. Define the screenshot evidence requirements (section 19).
21. Define the accessibility requirements (section 20).
22. Define the performance constraints (section 21).
23. Define the future implementation file expectations (section 22).
24. Define the validation gates (section 23).
25. Define the visual acceptance criteria (section 24).
26. Define the truth-boundary copy (section 25).
27. Define the explicitly local/demo/static behavior (section 26).
28. Preserve the truth boundary (section 25) and not weaken any prior
    boundary.

PS-039 is local / static / spec only by design: no implementation code, no
deployment changes, no env/secrets changes, no render.yaml changes, no
requirements/dependency changes, no Cloudflare API calls, no DNS mutation, no
Cloudflare resource creation, no Cloudflare Pages deployment, no Cloudflare
Workers deployment, no Cloudflare R2 live reads, no Cloudflare R2 writes, no
Backblaze B2 writes, no provider calls, no model calls, no live B2 reads, no
B2 writes, and no broad B2 scans.

## 6. Non-goals

PS-039 must not:

- no implementation code (no app files, no product code, no backend code, no
  frontend code, no 3D assets, no GLB/glTF files, no brand asset files)
- no auth implementation
- no dashboard implementation
- no deployment changes
- no env/secrets changes
- no render.yaml changes
- no requirements/dependency changes
- no Cloudflare API calls
- no DNS mutation
- no Cloudflare resource creation
- no Cloudflare Pages deployment
- no Cloudflare Workers deployment
- no Cloudflare R2 live reads
- no Cloudflare R2 writes
- no Backblaze B2 writes
- no provider calls
- no model calls
- no B2 reads/writes (no live B2 reads, no B2 writes, no broad B2 scans)
- no Cloudflare API/DNS/resource/deploy/R2 behavior
- do not finalize irreversible brand assets (logo lockup files, final color
  tokens, final type licenses, final brand guidelines PDF) inside this spec;
  this spec records direction only
- do not implement the 3D marketing website (deferred to the future PS-039
  build)
- do not implement the demo automation shell (deferred to the future PS-039
  build)
- do not implement auth / the account system (deferred to PS-040)
- do not implement the dashboard (deferred to PS-041)
- do not deploy / harden the production demo (deferred to PS-042)
- do not assemble the Final Submission Pack (deferred to PS-043)
- do not assemble the Devpost Package + 3-Minute Demo Script (deferred to
  PS-044)
- do not edit product code under `src/**`
- do not edit frontend code under `apps/**`
- do not edit scripts under `scripts/**`
- do not edit evidence under `docs/evidence/**`
- do not edit `AGENTS.md`
- do not edit `.env*`
- do not edit `render.yaml`
- do not edit requirements files
- do not edit `package.json`, `package-lock.json`, `pnpm-lock.yaml`, or
  `yarn.lock`
- do not edit `docs/validation/proofstudio-smoke-harness-v1.md`
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not run recursive smokes
- do not stage, commit, or push (PM acceptance only)
- do not weaken, remove, or rewrite any prior truth boundary from PS-037
  through PS-038b
- do not change any golden run canonical constant
- do not rewrite unrelated historical slices
- do not claim implementation exists for anything PS-039 specifies

PS-039 only creates the one spec file listed in section 1.

## 7. Route / page target for future implementation

The future PS-039 build owns the public marketing surface. The route/page
target for the future implementation is:

- `/` — the cinematic 3D marketing landing page (the marquee surface). This
  is the primary route PS-039 owns.
- `/proof-room` — the Campaign Proof Room presentation page. This is the
  on-site presentation path for the Campaign Proof Room. It may be a
  marketing-styled wrapper around the PS-038a Campaign Proof Room framing,
  driven by local/demo/static data only. It must not call live providers,
  must not read live B2, and must not perform browser-side B2 byte
  verification.
- `/demo` — the Judge demo entry point. This route launches the demo
  automation shell so a judge can replay the cinematic story without manual
  scrolling. It must be local/demo/static only.
- A reduced-motion static landing variant reachable from `/` (for example via
  a query param such as `?reduced-motion=1` or via automatic OS preference
  detection). See section 17.

Routes PS-039 must not add:

- no auth routes (no `/login`, no `/signup`, no `/verify`, no `/account`) —
  deferred to PS-040
- no dashboard routes (no `/dashboard`, no `/campaigns`, no `/campaigns/:id`)
  — deferred to PS-041
- no deployment/admin routes — deferred to PS-042

The `/proof-room` route is a presentation path. The authoritative Campaign
Proof Room contract remains `specs/61-ps-038a-campaign-proof-room.md`. The
PS-039 `/proof-room` page must not redefine the Campaign Proof Room contract;
it must present it.

## 8. Brand identity outputs

The future PS-039 build must produce the following brand identity outputs.
PS-039 specifies them; it does not produce them.

- Brand direction document (recorded by PS-038b section 10 and reaffirmed
  here): serious premium media proof system, not a generic AI toy.
- Color token set: near-black charcoal base; Backblaze-inspired orange used
  rarely as warmth; electric proof blue/cyan for verification; muted green
  for verified; amber for warning; red only for destructive/error. Tokens
  must be defined as design tokens (CSS custom properties / Tailwind v4
  theme), not as inline values.
- Typography scale: premium grotesk for UI, editorial headlines for the
  cinematic moments, precise evidence labels (monospace or fixed-width) for
  hashes, manifest fields, and B2 object references.
- Logo/mark direction output (see section 9): direction recorded, final
  lockup deferred.
- Voice/tone guide: precise, calm, evidence-led, never hype, never overclaim.
  The voice must match the PS-037 Disclosure + Trust Boundary.
- Brand asset manifest: a manifest of which brand assets are directional vs
  final. Directional assets may change; final assets are locked only after
  PM acceptance.

PS-039 does not finalize irreversible brand assets. A final logo lockup, a
final licensed type family, a final brand guidelines PDF, and final color
token lock are explicitly out of scope for this spec and for the first
implementation pass unless the PM explicitly approves locking them.

## 9. Logo / mark direction

The logo/mark direction for PS-039 (recorded by PS-038b section 10 and
reaffirmed here):

- a compact proof mark built from archive/check/manifest/orbit ideas
- the mark must read as a serious premium media proof system, not a generic
  AI toy
- no random neon blobs
- no robot mascots
- no generic AI sparkles
- the mark must render legibly at small sizes (favicon, nav bar) and at large
  sizes (hero)
- the mark must have a monochrome/reduced-motion variant that does not depend
  on animation, glow, or color

PS-039 records direction only. PS-039 does not finalize the irreversible
brand mark. The future PS-039 build may produce candidate marks and a
selected working mark for the site, but the final locked logo lockup requires
explicit PM acceptance and is not claimed as finalized by this spec.

## 10. Proof Core / Evidence Orb / Campaign Record 3D metaphor

The cinematic proof story for PS-039 uses the ProofStudio 3D animation
metaphor recorded by PS-038b section 9. PS-039 specifies the metaphor
behavior on the page; the future PS-039 build implements it.

- Proof Core — the central object that represents a proven campaign artifact.
  On the page it is the focal 3D object in the hero and in the scroll/story
  sequence. It must be visually stable, premium, and calm (no jitter, no
  neon, no generic AI sparkle effects).
- Evidence Orb — the orb that forms around the Proof Core as evidence
  accumulates. On the page, as the user scrolls (or as the demo automation
  shell advances), proof layers orbit/accumulate around the Proof Core. Each
  layer is a labeled evidence chip: prompt, provider/model, B2 archive,
  Genblaze manifest, rehydrate check, review decision, provenance passport,
  export pack.
- Campaign Record — the object appears as a campaign artifact (the recorded
  campaign artifact from PS-038a). On the page it is the initial state of the
  Proof Core: a single recorded campaign artifact before the proof layers
  expand.

The cinematic sequence (specified for the future build):

1. A campaign artifact appears (Campaign Record).
2. It splits into proof layers, each rendered as part of the Evidence Orb:
   - prompt
   - provider/model
   - B2 archive
   - Genblaze manifest
   - rehydrate check
   - review decision
   - provenance passport
   - export pack
3. It then reassembles into the Campaign Proof Room.

This is a presentation metaphor over recorded proof. It does not prove
campaign performance, marketing effectiveness, business outcome, semantic
truth, legal authenticity, legal approval, human authorship, C2PA
authenticity, content authorship, production readiness, production security,
production compliance, uptime guarantee, cost guarantee, performance
guarantee, Object Lock, tamper-proof storage, live B2 availability, live
provider availability, or browser-side B2 byte verification. The metaphor
must keep every de-escalation pair from PS-038a (proof does not equal truth;
the Campaign Proof Room does not equal campaign performance proof; manifest
evidence does not equal semantic truth; etc.).

The metaphor data must come from local/demo/static fixtures only (the golden
run / accepted demo data), never from live provider calls or live B2 reads,
unless a later PM-approved slice explicitly owns live behavior with env gates
and controls.

## 11. Cinematic landing page structure

The future PS-039 build must produce a cinematic landing page at `/` with the
following section structure (top to bottom):

1. Hero — the Proof Core / Campaign Record appears. Headline, subhead,
   primary CTA (Campaign Proof Room CTA, section 13), secondary CTA (Judge
   demo CTA, section 14). Reduced-motion static fallback must be available.
2. Thesis — the one-sentence ProofStudio thesis (provenance-aware AI media
   operations; ProofStudio proves what the pipeline recorded). Plain language,
   no hype.
3. Proof story scroll — the scroll/story sequence (section 12) that expands
   the Evidence Orb layer by layer.
4. Proof layer detail bands — one band per proof layer (B2 archive evidence,
   Genblaze manifest evidence, rehydrate check, review decision, provenance
   passport, export pack). See section 16.
5. Campaign Proof Room preview — a framed preview/CTA for the Campaign Proof
   Room (section 13).
6. Judge demo band — a framed CTA for the Judge demo (section 14).
7. Truth boundary band — the canonical truth-boundary copy (section 25),
   visible without scrolling forever (above the footer, not buried).
8. Footer — minimal footer with brand mark, the truth-boundary one-liner,
   and a link to the Campaign Proof Room. No fake legal/compliance claims.

Every section must carry its own loading/empty/error/success state if it
depends on data, even if the data is local/demo/static. A section that fails
to load its local fixture must degrade gracefully, not crash the page.

## 12. Scroll / story sequence

The scroll/story sequence (specified for the future build; implemented via
GSAP ScrollTrigger + Lenis per PS-038b section 8):

1. Hero loads with the Campaign Record (the Proof Core in its initial,
   unexpanded state).
2. On scroll, the Evidence Orb begins to form. Each scroll milestone adds one
   labeled evidence chip in this order:
   - prompt
   - provider/model
   - B2 archive
   - Genblaze manifest
   - rehydrate check
   - review decision
   - provenance passport
   - export pack
3. At the end of the scroll, the assembled evidence reassembles into the
   Campaign Proof Room preview/CTA.
4. The scroll sequence must be pausable, reversible (scroll back), and
   keyboard-navigable (section 20).
5. The scroll sequence must have a reduced-motion fallback (section 17) that
   delivers the same narrative without 3D/scroll-driven animation.

The scroll sequence is a presentation over recorded proof. It does not prove
semantic truth, legal authenticity, legal approval, human authorship, C2PA
authenticity, content authorship, campaign performance, marketing
effectiveness, business outcome, production readiness, production security,
production compliance, uptime guarantee, cost guarantee, performance
guarantee, Object Lock, tamper-proof storage, live B2 availability, live
provider availability, or browser-side B2 byte verification.

## 13. Campaign Proof Room CTA

The Campaign Proof Room CTA is the primary call to action on the landing
page. It must:

- link to `/proof-room` (the on-site Campaign Proof Room presentation page,
  section 7)
- use calm, precise copy (for example "Enter the Campaign Proof Room" or
  "See the full proof story"). The exact copy is decided in the future build;
  the direction is calm and evidence-led, never hype.
- frame the Campaign Proof Room as the single marquee judge-facing surface
  (per PS-038a)
- not overclaim. The CTA copy must not claim campaign performance, marketing
  effectiveness, business outcome, semantic truth, legal authenticity, legal
  approval, human authorship, C2PA authenticity, content authorship,
  production readiness, production security, production compliance, uptime
  guarantee, cost guarantee, performance guarantee, Object Lock, tamper-proof
  storage, live B2 availability, live provider availability, or browser-side
  B2 byte verification.

The `/proof-room` page must present the Campaign Proof Room framing from
`specs/61-ps-038a-campaign-proof-room.md`, driven by local/demo/static data.
It must not redefine the Campaign Proof Room contract.

## 14. Judge demo CTA

The Judge demo CTA is the secondary call to action on the landing page. It
must:

- link to `/demo` (the Judge demo entry point, section 7) or trigger the demo
  automation shell directly (section 15)
- use calm, precise copy (for example "Watch the judge demo" or "Replay the
  proof story"). The exact copy is decided in the future build; the direction
  is calm and evidence-led.
- frame the demo as a guided replay of the cinematic proof story, not as a
  live generation run
- not overclaim. The CTA copy must obey the same truth boundary as the
  Campaign Proof Room CTA (section 13).

The Judge demo must be local/demo/static only. It must not call live
providers, must not read live B2, must not write B2, and must not perform
browser-side B2 byte verification.

## 15. Demo automation shell behavior

The demo automation shell is the deterministic replay layer that drives the
cinematic proof story for a judge without manual scrolling. PS-039 specifies
its behavior; the future PS-039 build implements it.

Required behavior:

- The shell launches from `/demo` or from the Judge demo CTA.
- The shell advances the scroll/story sequence (section 12) deterministically:
  Campaign Record -> prompt -> provider/model -> B2 archive -> Genblaze
  manifest -> rehydrate check -> review decision -> provenance passport ->
  export pack -> Campaign Proof Room.
- The shell must have explicit controls: play, pause, step forward, step
  back, reset, and exit. The judge must always be able to pause or take over
  manual scrolling.
- The shell must respect reduced-motion (section 17). In reduced-motion mode
  the shell advances the static narrative, not the 3D animation.
- The shell must be driven by local/demo/static fixtures only (the golden run
  / accepted demo data). It must not call live providers and must not read
  live B2.
- The shell must show a visible "demo mode" indicator so a judge always knows
  they are watching a deterministic replay of recorded proof, not a live run.
- The shell must not overclaim. The demo mode indicator and the shell copy
  must obey the truth boundary (section 25).

The demo automation shell is a presentation/replay layer. It is not a live
pipeline. It does not prove campaign performance, marketing effectiveness,
business outcome, semantic truth, legal authenticity, legal approval, human
authorship, C2PA authenticity, content authorship, production readiness,
production security, production compliance, uptime guarantee, cost guarantee,
performance guarantee, Object Lock, tamper-proof storage, live B2
availability, live provider availability, or browser-side B2 byte
verification.

## 16. Proof layer stories

Each proof layer has an on-page story band (section 11.4). The stories are
presentation over recorded proof. They do not overclaim.

### 16.1 B2 archive evidence story

The B2 archive evidence story band must:

- show that the campaign artifact is archived in Backblaze B2 (per the B2
  system of record from the master spec and PS-036)
- display the recorded B2 object reference / archive path from the
  local/demo/static fixture (not a live B2 fetch)
- explain that B2 is the durable system of record
- explicitly not claim Object Lock, tamper-proof storage, browser-side B2
  byte verification, live B2 availability, or production immutability
- explicitly not perform a live B2 read or a browser-side B2 byte
  verification

### 16.2 Genblaze manifest evidence story

The Genblaze manifest evidence story band must:

- show that the archived artifact carries a Genblaze manifest (per PS-035A
  golden-run manifest correctness and the master spec Genblaze layer)
- display the recorded `manifest_uri`, `manifest_hash`, and recorded
  `genblaze_version` from the local/demo/static fixture (not a live fetch)
- explain that the manifest proves byte-level asset integrity and recorded
  workflow integrity, not semantic truth or legal authenticity
- explicitly not claim C2PA authenticity, human authorship, content
  authorship, or legal authenticity
- explicitly not claim a live manifest fetch unless a later PM-approved slice
  owns it

### 16.3 Rehydrate check story

The rehydrate check story band must:

- show that the campaign can be rehydrated from B2-backed artifacts and
  manifests (per PS-036 and the master spec rehydrate-from-B2 differentiator)
- explain that rehydration proves B2 is the durable state layer
- display the recorded rehydrate result from the local/demo/static fixture
- explicitly not claim live B2 availability, Object Lock, tamper-proof
  storage, or browser-side B2 byte verification
- explicitly not perform a live B2 read during the marketing demo

### 16.4 Review decision story

The review decision story band must:

- show the recorded review decision (per PS-035 Review + Approval Workspace)
  from the local/demo/static fixture
- explain that approval records the reviewer's workflow decision
- explicitly not claim that approval proves semantic truth, legal
  authenticity, legal approval, human authorship, C2PA authenticity, or
  content authorship
- explicitly not claim production multi-user review, durable replicated
  review ledger, or production security

### 16.5 Provenance passport story

The provenance passport story band must:

- show the provenance passport (per the master spec section 3.5 and PS-038a)
  from the local/demo/static fixture
- display campaign, source brief, provider, model, prompt, generation
  parameters, recorded B2 object URL, SHA-256, manifest hash, lineage,
  review status, export status, and truth-boundary note
- explain that the passport is the recorded provenance of what the pipeline
  produced
- explicitly not claim semantic truth, legal authenticity, legal approval,
  human authorship, C2PA authenticity, content authorship, Object Lock,
  tamper-proof storage, live B2 availability, live provider availability, or
  browser-side B2 byte verification

### 16.6 Export pack story

The export pack story band must:

- show the export pack framing (per the master spec section 3.10 and PS-037
  Disclosure + Trust Boundary) from the local/demo/static fixture
- explain that the export pack includes approved assets, prompt packet,
  campaign copy, metadata, review summary, provider attempt ledger, manifest,
  truth-boundary note, and disclosure note
- explain that the export pack is disclosure-ready, not legally authoritative
- explicitly not claim legal authenticity, legal approval, semantic truth,
  human authorship, C2PA authenticity, or content authorship

## 17. Reduced-motion fallback

The reduced-motion fallback is a first-class path, not an afterthought
(recorded by PS-038b section 8). The future PS-039 build must:

- detect the OS/browser reduced-motion preference automatically
- offer an explicit reduced-motion entry (for example `?reduced-motion=1`)
- in reduced-motion mode, deliver the same narrative (Campaign Record ->
  evidence layers -> Campaign Proof Room) without 3D/scroll-driven animation,
  without Evidence Orb motion, without GSAP ScrollTrigger motion, and without
  autoplaying canvas/image-sequences
- keep all proof layer stories (section 16) fully readable and complete in
  reduced-motion mode
- keep the Campaign Proof Room CTA (section 13), the Judge demo CTA
  (section 14), and the demo automation shell (section 15) fully functional
  in reduced-motion mode
- keep the truth-boundary band (section 25) visible in reduced-motion mode

Reduced-motion must not mean reduced proof. The full evidence narrative must
be available without animation.

## 18. Mobile / tablet / desktop visual requirements

The future PS-039 build must support mobile/tablet/desktop variants
(recorded by PS-038b section 8). Requirements:

- mobile (approx. 360-428px width): single-column layout, simplified hero
  (no heavy 3D on mobile by default; static Campaign Record mark or
  lightweight canvas), full proof story scroll, full proof layer bands, full
  CTAs, full truth-boundary band. Performance budget must hold on mid-tier
  mobile.
- tablet (approx. 768-1024px width): adapted layout, optional lighter 3D,
  full narrative.
- desktop (approx. 1280px+ width): full cinematic 3D hero, full Evidence Orb
  sequence, full scroll/story sequence.
- every breakpoint must carry loading/empty/error/success states.
- every breakpoint must respect reduced-motion (section 17).
- every breakpoint must keep the truth-boundary band visible.
- touch targets must meet the accessibility requirements (section 20).
- no layout may rely on hover-only interaction (hover is a desktop
  enhancement, never a requirement).

## 19. Screenshot evidence requirements

The future PS-039 build must produce screenshot evidence for visual
acceptance. Requirements:

- desktop hero screenshot (full page above-the-fold)
- desktop full-page screenshot (the full cinematic scroll)
- desktop Campaign Proof Room preview screenshot
- desktop `/proof-room` screenshot
- desktop `/demo` screenshot
- tablet hero screenshot
- tablet full-page screenshot
- mobile hero screenshot
- mobile full-page screenshot
- reduced-motion screenshot (desktop)
- one screenshot showing the "demo mode" indicator active

Screenshots must be stored under `docs/evidence/ps-039/` (created by the
future build, not by this spec). Screenshots must not be fabricated: each
screenshot must correspond to a real render of the built site. If the site
has not been built yet, no screenshot evidence exists and must not be
claimed.

## 20. Accessibility requirements

The future PS-039 build must meet these accessibility requirements:

- WCAG 2.1 AA as the target (color contrast, text resize, focus visibility,
  semantic structure)
- keyboard navigation for every interactive element (hero CTAs, scroll/story
  milestones, demo automation controls, Campaign Proof Room CTA, Judge demo
  CTA)
- visible focus indicators on every focusable element
- screen-reader-friendly narrative: the proof story must be available as
  structured text/landmarks, not only as canvas/3D
- reduced-motion fully supported (section 17)
- no motion that triggers vestibular distress (no parallax abuse, no
  high-frequency strobing)
- touch targets at least 44x44 CSS pixels on mobile/tablet
- alt text / accessible labels for the Proof Core, Evidence Orb, and
  Campaign Record visuals where they convey information not present in text
- the truth-boundary band must be readable by assistive tech (real text, not
  image-only)
- the "demo mode" indicator must be announced to assistive tech

Accessibility must not be deferred to "later". The first implementation pass
must meet AA on the narrative path (the reduced-motion, text-first path).

## 21. Performance constraints

The future PS-039 build must hold performance budgets so the cinematic site
does not become slow. Constraints (direction; final numbers confirmed in the
future build):

- the hero must respect a performance budget: First Contentful Paint and
  Largest Contentful Paint targets must be defined and measured for desktop
  and mobile
- heavy 3D / GLB/glTF assets must lazy-load and must not block the hero text
  or the CTAs
- the reduced-motion path must be the fastest path (no 3D, no scroll-driven
  animation)
- the page must not ship megabytes of JS to mobile by default; code-splitting
  and lazy-loading are required for the 3D layer
- the page must remain usable on mid-tier mobile on a slow connection (the
  text-first narrative must render before the 3D layer)
- the demo automation shell must advance smoothly without dropping the page
  below an interactive frame rate target

PS-039 does not claim a specific Lighthouse score or a specific production
performance guarantee. Performance budgets are targets for the future build,
not claims. The future build must measure and record actual numbers; it must
not fabricate them.

## 22. Future implementation file expectations

The future PS-039 build is expected to add/change files in these areas only
(direction; exact paths decided in the future build, within the
`apps/web/**` surface allowed for PS-039):

- brand tokens / theme files (colors, type, spacing) — design tokens, not
  inline values
- the 3D marketing landing page route and components (`/`)
- the Campaign Proof Room presentation route (`/proof-room`)
- the Judge demo route (`/demo`) and the demo automation shell module
- the scroll/story sequence module
- the reduced-motion fallback path
- local/demo/static fixture loaders for the proof stories (reading accepted
  local / golden / demo data; no live provider calls, no live B2 reads)
- screenshot evidence under `docs/evidence/ps-039/` (only the future build
  creates this)
- a PS-039 feature smoke under `scripts/` (only the future build creates
  this; PS-039 spec-only does not)

PS-039 must not add/change:

- `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock` (these
  are forbidden files for PS-039 spec-only; the future build may touch them
  within its own acceptance criteria, but this spec does not)
- `src/**` (backend)
- `.env*`
- `render.yaml`
- requirements files
- `docs/evidence/**` (prior evidence is protected)
- `AGENTS.md`
- `docs/validation/proofstudio-smoke-harness-v1.md`

PS-039 spec-only changes exactly one file: this spec.

## 23. Validation gates

The future PS-039 build must pass these validation gates. PS-039 spec-only
passes a subset (the spec-only gates marked below).

Spec-only gates (this slice):

- this spec exists at
  `specs/63-ps-039-brand-3d-marketing-website-demo-automation-shell.md`
- the branch `ps-039/brand-3d-marketing-website-demo-automation-shell` starts
  from `origin/accepted/proofstudio` and the starting HEAD equals
  `7426d7e5d4f3d1009774d38ffe1d581a42ac71ad`
- the changed file set is exactly the one file in section 1 (this spec) — no
  other files changed
- all required exact strings (section 27) are present
- no implementation code, no app files, no scripts, no evidence mutation, no
  env/secrets changes, no deployment changes
- no provider calls, no model calls, no B2 reads/writes, no Cloudflare
  API/DNS/resource/deploy/R2 behavior
- no hidden Git flags `h` or `S` (verified by the explicit h/S checker over
  `git ls-files -v`, failing when `line[0]` is `h` or `S`)
- `git diff --check` is clean
- no weakening of any truth boundary from PS-037 through PS-038b
- no change to any golden run canonical constant
- no staging, commit, or push (PM acceptance only)

Future-build gates (for the later implementation pass, not for this slice):

- a PS-039 feature smoke under `scripts/` that is local/static by default
  (`--check-only`, `--write-evidence`, `--no-frontend` per AGENTS.md section
  2), writes only `docs/evidence/ps-039/`, and never recursively executes
  another smoke
- the central regression gate run non-mutating
  (`scripts/proofstudio_regression_gate.py --current ps039 --check-only
  --report-out /tmp/...`) per AGENTS.md section 3
- the frontend typecheck for the marketing site
- the hidden Git flag h/S check
- `git diff --check`
- screenshot evidence captured under `docs/evidence/ps-039/`
- accessibility AA check on the reduced-motion / text-first path
- performance budget measurement recorded under `docs/evidence/ps-039/`

The CodeRabbit review gate (recorded by PS-038b section 14) is an extra
post-build review layer; it is not a replacement for the feature smoke, the
central regression gate, the frontend typecheck, the hidden Git flag check,
the git diff check, or PM acceptance.

## 24. Visual acceptance criteria

The future PS-039 build is visually "done" when:

- it is a winning-project presentation layer and a cinematic 3D marketing site,
  not a dense technical docs page
- it has deep near-black premium atmosphere, Apple/Awwwards-level typography
  and hierarchy, a sticky full-screen Canvas/image-sequence or equivalent
  cinematic hero, and scroll-synchronized story beats
- the hero reads as a serious premium media proof system (not a generic AI
  toy; no neon blobs, no robot mascots, no generic AI sparkles)
- the Proof Core / Evidence Orb / Campaign Record metaphor renders and
  behaves per section 10
- the scroll/story sequence unfolds per section 12 with all eight evidence
  layers
- the Campaign Proof Room CTA and the Judge demo CTA are present, calm, and
  non-overclaiming (sections 13, 14)
- the demo automation shell plays, pauses, steps, resets, exits, and
  respects reduced-motion (section 15)
- every proof layer story band (section 16) is present, complete, and
  non-overclaiming
- the reduced-motion path delivers the full narrative without animation
  (section 17)
- mobile/tablet/desktop variants all pass (section 18)
- screenshot evidence is captured and matches the rendered site (section 19)
- accessibility AA is met on the text-first path (section 20)
- performance budgets are measured and recorded (section 21)
- the truth-boundary band is visible and readable (section 25)
- the "demo mode" indicator is visible and announced (section 15)

Hard visual rejection list for the future PS-039 build:

- dense technical docs page
- tiny text everywhere
- flat evidence-card layout
- generic dark UI
- random neon blobs
- generic AI sparkles
- robot mascots
- crypto/NFT dashboard vibes
- proof details competing with the cinematic story

PS-039 spec-only does not claim any visual acceptance criterion is met. The
visual acceptance criteria apply to the future build.

## 25. Truth-boundary copy

PS-039 preserves the canonical truth boundary verbatim:

```
ProofStudio proves what the pipeline recorded.
Proof does not equal truth.
```

The on-page truth-boundary band (section 11.7) must carry at minimum:

- "ProofStudio proves what the pipeline recorded."
- "Proof does not equal truth."

PS-039 does not prove or claim:

- semantic truth
- legal authenticity
- legal approval
- human authorship
- C2PA authenticity
- content authorship
- Object Lock
- tamper-proof storage
- browser-side B2 byte verification
- live B2 availability
- live provider availability
- production security
- production compliance
- uptime guarantee
- cost guarantee
- performance guarantee
- campaign performance
- marketing effectiveness
- business outcome guarantee

PS-039 specifically:

- does not claim production readiness
- does not claim production security
- does not claim production compliance
- does not claim campaign performance
- does not claim marketing effectiveness
- does not claim semantic truth
- does not claim legal authenticity
- does not claim legal approval
- does not claim human authorship
- does not claim C2PA authenticity
- does not claim content authorship
- does not claim Object Lock / tamper-proof storage / browser-side B2 byte
  verification unless implemented and verified
- does not claim live B2 availability or live provider availability
- does not claim uptime guarantee, cost guarantee, or performance guarantee
- does not claim business outcome guarantee
- does not claim the brand identity is finalized
- does not claim the 3D marketing website is implemented (this slice is
  spec-only)
- does not claim the demo automation shell is implemented (this slice is
  spec-only)

PS-039 is local / static / spec only. It makes no Cloudflare API calls,
mutates no DNS, creates no Cloudflare resource, deploys no Cloudflare Pages,
deploys no Cloudflare Workers, performs no Cloudflare R2 live reads, performs
no Cloudflare R2 writes, performs no Backblaze B2 writes, calls no provider,
calls no model, reads no live B2, writes no B2, performs no broad B2 scans,
and changes no deployment / env / render.yaml / requirements config.

## 26. Explicitly local / demo / static behavior

Unless a later PM-approved slice explicitly owns live behavior with env
gates and controls, PS-039 (and its future build) is explicitly local /
demo / static:

- all proof story data comes from accepted local / golden / demo fixtures
- the Campaign Proof Room presentation page (`/proof-room`) reads
  local/demo/static data only
- the Judge demo (`/demo`) and the demo automation shell replay
  local/demo/static data only
- the marketing surface performs no live provider call
- the marketing surface performs no live B2 read and no B2 write
- the marketing surface performs no browser-side B2 byte verification
- the marketing surface performs no Cloudflare API/DNS/resource/deploy/R2
  behavior
- the marketing surface does not call the auth system (auth is PS-040)
- the marketing surface does not call the dashboard (dashboard is PS-041)
- the marketing surface does not perform deployment (deployment is PS-042)

If a later slice (for example PS-042 deployment hardening) makes the
marketing surface live, that slice owns the live behavior and the truth
boundary for it. PS-039 does not pre-claim live behavior.

## 27. Verbatim implementation/audit contract strings

The PS-039 spec and any future PS-039 build docs must preserve the following
exact strings so the PS-039 contract is deterministic and auditable. Any
future PM audit must check these exact strings; do not rely on close-enough
wording. No surprise audit checks: any exact string a future PM audit should
check is listed here.

The required identity / slice strings are:

- PS-039
- Brand Identity + 3D Marketing Website + Demo Automation Shell

The required visual metaphor / surface strings are:

- Proof Core
- Evidence Orb
- Campaign Record
- Campaign Proof Room

The required proof story strings are:

- B2 archive evidence
- Genblaze manifest evidence
- rehydrate check
- review decision
- provenance passport
- export pack

The required posture / fallback strings are:

- reduced-motion fallback
- mobile/tablet/desktop

The required posture / boundary strings are:

- no auth implementation
- no dashboard implementation
- no deployment changes
- no env/secrets changes
- no provider calls
- no model calls
- no B2 reads/writes
- no Cloudflare API/DNS/resource/deploy/R2 behavior

The required truth-boundary (does-not-claim) strings are:

- does not claim production readiness
- does not claim production security
- does not claim production compliance
- does not claim campaign performance
- does not claim marketing effectiveness
- does not claim semantic truth
- does not claim legal authenticity

The required canonical truth-boundary lines are:

- ProofStudio proves what the pipeline recorded.
- Proof does not equal truth.

The required base-ref strings are:

- origin/accepted/proofstudio
- 7426d7e5d4f3d1009774d38ffe1d581a42ac71ad

## 28. Acceptance criteria

PS-039 (this spec-only slice) is accepted only when:

- this spec exists at
  `specs/63-ps-039-brand-3d-marketing-website-demo-automation-shell.md`
- the branch `ps-039/brand-3d-marketing-website-demo-automation-shell` starts
  from `origin/accepted/proofstudio` and the starting HEAD equals
  `7426d7e5d4f3d1009774d38ffe1d581a42ac71ad`
- the changed file set is exactly the one file in section 1 (this spec) — no
  other files changed
- no implementation code, no app files, no scripts, no evidence mutation, no
  env/secrets changes, no deployment changes, no render.yaml changes, no
  requirements/dependency changes
- no provider calls, no model calls, no B2 reads/writes, no Cloudflare
  API/DNS/resource/deploy/R2 behavior
- no weakening, removal, or rewrite of any truth boundary from PS-037
  through PS-038b
- no change to any golden run canonical constant
- all required exact strings (section 27) are present
- no hidden Git flags `h` or `S` are present (verified by the explicit h/S
  checker over `git ls-files -v`, failing when `line[0]` is `h` or `S`)
- `git diff --check` is clean
- no staging, commit, or push occurs until PM acceptance

## 29. Rollback

Rollback of PS-039 is a single revert of this slice, because PS-039 changes
only one spec file and changes no product, backend, provider, deployment,
env, requirements, or evidence behavior.

Specifically, rollback removes
`specs/63-ps-039-brand-3d-marketing-website-demo-automation-shell.md`.

Rollback of PS-039 must not touch any evidence under `docs/evidence/**`, must
not touch the central gate (`scripts/proofstudio_regression_gate.py`),
`scripts/smoke_lib.py`, `AGENTS.md`, `.env*`, `render.yaml`, requirements
files, `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`,
any provider wrapper, any model client, any Cloudflare client, any B2
storage path, any DNS mutation path, or any deployment config path. Rollback
is isolated and reversible because PS-039 is a self-contained specification
slice; it does not change provider behavior, model behavior, generation
behavior, Cloudflare behavior, DNS behavior, B2 behavior, billing behavior,
or deployment topology.
