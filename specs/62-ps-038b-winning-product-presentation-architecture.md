# PS-038b — Winning Product Presentation Architecture

Status: Spec only / docs only.
Slice: PS-038b
Date: 2026-07-03
Branch: `ps-038b/winning-product-presentation-architecture`
Spec: `specs/62-ps-038b-winning-product-presentation-architecture.md`

## 1. Status

PS-038b — Winning Product Presentation Architecture is currently:

- Spec only / docs only.
- A docs / spec / roadmap alignment slice. It records the agreed product
  presentation architecture (brand identity direction, 3D marketing website
  strategy, dashboard strategy, auth/account strategy, deployment roadmap,
  agent/model operating plan, and the CodeRabbit post-build review gate) into
  the repo before any of it is built.
- No implementation code. No app files. No scripts. No evidence mutation. No
  env/secrets changes. No deployment changes. No provider calls. No model
  calls. No B2 reads/writes. No Cloudflare API/DNS/resource/deploy/R2
  behavior.

PS-038b must not implement the 3D website, must not implement auth, must not
implement the dashboard, must not deploy anything, and must not run any
provider, model, B2, or Cloudflare behavior. PS-038b records strategy only. It
does not claim implementation exists.

The authoritative accepted base is the dynamic Git ref
`origin/accepted/proofstudio`, never a hardcoded commit hash. At the time of
this spec the ref resolves to commit
`42fae3cda40f03316936ff8d500f614b4cde474b` (the post-PS-038a accepted state:
the Campaign Proof Room from PS-038a is specified, and PS-038 Production
Readiness + Demo Mode is accepted). The ref is the authority; the commit hash
is recorded for traceability only and must not be treated as a hardcoded base.
PS-038b starts from `origin/accepted/proofstudio`, not from `main`.

This slice touches only these files:

- `specs/62-ps-038b-winning-product-presentation-architecture.md` (this spec)
- `specs/07-master-spec-plan.md` (register PS-038b + corrected future sequence)
- `specs/08-roadmap-slices.md` (add PS-038b + corrected future sequence)
- `docs/ps-038b-winning-product-presentation-architecture-proof.md` (proof doc)

PS-038b obeys the root `AGENTS.md` operating law and the validation policy in
`docs/validation/proofstudio-smoke-harness-v1.md`. PS-038b does not weaken any
truth boundary from PS-037 through PS-038a.

## 2. Purpose

PS-038b records the winning product presentation architecture into the repo so
that implementation slices PS-039 onward are spec-first and not ad hoc. It
locks the agreed strategy for: brand identity direction; the 3D marketing
website; the cinematic ProofStudio visual metaphor; the world-class user
dashboard; the auth/account system; the deployment / domain / production demo
hardening roadmap; the agent/model operating plan; and the CodeRabbit
post-build review gate.

PS-038b exists because the roadmap previously jumped from the proof-core slices
(PS-023 through PS-038a) straight to the Final Submission Pack. That skipped
the presentation and productization layer a winning submission actually needs:
a serious premium media proof system needs a brand identity, a 3D marketing
website, a real auth/account system, a world-class dashboard, and a hardened
deployment — before the final submission pack and the Devpost package are
assembled. PS-038b corrects that sequence in the roadmap documents and records
the architecture for each future slice, without implementing any of them.

PS-038b does not implement the 3D website. PS-038b does not implement auth.
PS-038b does not implement the dashboard. PS-038b does not deploy anything.
PS-038b records strategy only.

## 3. Root cause / product gap

After PS-038a (Campaign Proof Room) the proof core is complete and inspectable.
But the roadmap that followed it assumed the next step was the Final Submission
Pack. That is a gap: a hackathon-winning and production-credible ProofStudio
needs the productization and presentation layer between the proof core and the
final submission.

Specifically the prior roadmap had no committed strategy for:

- a serious premium brand identity (not a generic AI toy: no random neon blobs,
  no robot mascots, no generic AI sparkles)
- a 3D marketing website that makes the proof story cinematic and judge-winning
- a real auth + account system (Google OAuth, Apple OAuth, GitHub OAuth,
  email/password signup, username login, email verification)
- a world-class, calm, data-first user dashboard
- a deployment / domain / production demo hardening pass
- the CodeRabbit review gate as a post-build safety layer

The Final Submission Pack and the Devpost package land better when the product
has a real brand, a real website, a real dashboard, real auth, and a hardened
deployment behind them. PS-038b corrects the sequence and records the
architecture for each of those future slices so that PS-039 is spec-first, not
improvised.

This is a roadmap / architecture correction, not an implementation. PS-038b
does not write any implementation code and does not change any product,
backend, provider, deployment, env, or requirements file.

## 4. Current accepted base

The current accepted base for PS-038b is:

- branch: `accepted/proofstudio`
- ref: `origin/accepted/proofstudio` (the authoritative source of truth; the
  ref is the authority, not any hardcoded commit hash)
- commit the ref resolves to at the time of this spec:
  `42fae3cda40f03316936ff8d500f614b4cde474b`
- this is the post-PS-038a accepted state: the Campaign Proof Room is specified
  (`specs/61-ps-038a-campaign-proof-room.md`); PS-038 Production Readiness +
  Demo Mode is accepted; the Disclosure + Trust Boundary Layer (PS-037), the
  Multimodal Proof Layer (PS-037a), the Transcript/Timestamp Evidence layer
  (PS-037b), the Voice/Audio Evidence Provider Choice layer (PS-037c), the
  Gemini Campaign Intelligence / Judge Narrative layer (PS-037d), and the
  Cloudflare Low-Cost Backbone layer (PS-037e) are all in place; the root
  `AGENTS.md` operating law (PS-035D) is in place; the central regression gate
  is non-mutating by default (PS-035C); the golden-fixture digest freeze
  (PS-035B) and the golden-run manifest correctness (PS-035A) are in place.

PS-038b must start from `origin/accepted/proofstudio`, not from `main`.

PS-038b must not weaken any truth boundary from PS-037 through PS-038a, must
not change any golden run canonical constant, and must not change any
historical contract the regression gate verifies.

## 5. Scope

PS-038b is a docs / spec / roadmap alignment slice. It owns strategy, roadmap
correction, architecture direction, and contract recording only. It must:

1. Correct the post-proof-core roadmap sequence: the Final Submission Pack is
   not next. The corrected sequence before final submission is recorded in
   section 7.
2. Record the 3D marketing website architecture (section 8).
3. Record the ProofStudio cinematic visual metaphor (section 9).
4. Record the brand identity direction (section 10).
5. Record the dashboard architecture (section 11).
6. Record the auth/account architecture (section 12).
7. Record the agent/model operating plan (section 13).
8. Record the CodeRabbit post-build review gate (section 14).
9. Preserve the truth boundary (section 15) and not weaken any prior boundary.
10. Explicitly define PS-039 as the next slice.

PS-038b is local / static / docs only by design: no implementation code, no
deployment changes, no env/secrets changes, no render.yaml changes, no
requirements/dependency changes, no Cloudflare API calls, no DNS mutation, no
Cloudflare resource creation, no Cloudflare Pages deployment, no Cloudflare
Workers deployment, no Cloudflare R2 live reads, no Cloudflare R2 writes, no
Backblaze B2 writes, no provider calls, no model calls, no live B2 reads, no
B2 writes, and no broad B2 scans.

## 6. Non-goals

PS-038b must not:

- no implementation code (no app files, no product code, no backend code, no
  frontend code)
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
- do not implement the 3D marketing website (deferred to PS-039)
- do not implement auth / the account system (deferred to PS-040)
- do not implement the dashboard (deferred to PS-041)
- do not deploy / harden the production demo (deferred to PS-042)
- do not assemble the Final Submission Pack (deferred to PS-043)
- do not assemble the Devpost Package + 3-Minute Demo Script (deferred to
  PS-044)
- do not run the CodeRabbit review on the project (it is a post-build gate;
  PS-038b does not claim CodeRabbit has reviewed the project)
- do not edit product code under `src/**`
- do not edit frontend code under `apps/**`
- do not edit scripts under `scripts/**`
- do not edit evidence under `docs/evidence/**`
- do not edit `AGENTS.md`
- do not edit `.env*`
- do not edit `render.yaml`
- do not edit requirements files
- do not edit `docs/validation/proofstudio-smoke-harness-v1.md`
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not run recursive smokes
- do not stage, commit, or push (PM acceptance only)
- do not weaken, remove, or rewrite any prior truth boundary from PS-037
  through PS-038a
- do not change any golden run canonical constant
- do not rewrite unrelated historical slices
- do not claim implementation exists for anything PS-038b records as strategy

PS-038b only edits the four files listed in section 1.

## 7. Updated roadmap sequence

### 7.1 Roadmap correction

Final Submission Pack is not next. Before final submission, ProofStudio needs:

1. Brand Identity + 3D Marketing Website + Demo Automation Shell
2. Auth + Account System
3. World-Class User Dashboard
4. Deployment / Domain / Production Demo Hardening
5. Final Submission Pack
6. Devpost Package + 3-Minute Demo Script

### 7.2 Corrected future sequence

- PS-038b — Winning Product Presentation Architecture (this slice; docs only)
- PS-039 — Brand Identity + 3D Marketing Website + Demo Automation Shell
- PS-040 — Auth + Account System
- PS-041 — World-Class User Dashboard
- PS-042 — Deployment / Domain / Production Demo Hardening
- PS-043 — Final Submission Pack
- PS-044 — Devpost Package + 3-Minute Demo Script

### 7.3 What this corrects

The historical pre-PS-038b roadmap ledger listed PS-039 as Final Submission
Pack and an earlier historical Devpost/demo-script identifier that is now
folded into PS-044, with PS-040 (Product Dashboard + Marketing Website)
delayed/optional. PS-038b corrects this: the presentation + productization
layer (brand / 3D website, auth, dashboard, deployment hardening) is now
required and is sequenced before the Final Submission Pack.
From PS-039a onward, PS-039a means Website/Dashboard Build Authority + Visual Rebuild Contract only.
The final submission numbering is renumbered so that PS-043 — Final Submission
Pack and PS-044 — Devpost Package + 3-Minute Demo Script are the last two
slices. The earlier historical Devpost/demo-script identifier is folded into
PS-044.

### 7.4 PS-039 is explicitly next

PS-039 — Brand Identity + 3D Marketing Website + Demo Automation Shell is the
next slice after PS-038b. It must start from `origin/accepted/proofstudio`
after PS-038b is accepted. It must be spec-first, then implementation. It must
not include auth, dashboard, or deployment work unless explicitly approved by
the PM.

### 7.5 History preservation

PS-038b preserves prior accepted history. It does not rewrite unrelated
historical slices (PS-001 through PS-038a). It does not remove or weaken the
PS-037 through PS-038a truth boundaries. It does not change any golden run
canonical constant. It does not change any historical contract the regression
gate verifies. The only roadmap changes are: adding PS-038b, correcting the
post-PS-038a future sequence, and renumbering the final submission slices.

## 8. 3D marketing website architecture

This is the recorded architecture for PS-039 — Brand Identity + 3D Marketing
Website + Demo Automation Shell. PS-038b records it; PS-039 implements it.

Tech stack and strategy:

- Next.js 16 + React 19 + TypeScript as the application foundation
- Tailwind CSS v4 for styling
- Three.js + React Three Fiber + Drei for the 3D layer
- GSAP ScrollTrigger + Lenis for scrollytelling
- Framer Motion / Motion-style microinteractions
- Canvas/image-sequence for cinematic hero moments
- GLB/glTF assets authored in Blender or Spline
- reduced-motion fallback (a first-class path, not an afterthought)
- mobile/tablet/desktop variants (responsive, not desktop-only)
- performance budgets and lazy loading (the site must stay fast; heavy 3D /
  GLB/glTF assets must lazy-load, and the hero must respect a budget)
- no fake production/security/performance claims (the marketing site may not
  claim production readiness, production security, semantic truth, legal
authenticity, C2PA authenticity, human authorship, Object Lock, tamper-proof
  storage, browser-side B2 byte verification, uptime guarantee, cost
  guarantee, or performance guarantee)

The 3D website is a marketing/presentation surface. It is not a proof system.
It must not fabricate proof, must not call live providers from the marketing
surface unless a later PM-approved slice enables it with env gates and
controls, and must not contradict the PS-037 Disclosure + Trust Boundary.

PS-038b does not implement this. PS-039 does.

## 9. ProofStudio visual metaphor

The cinematic proof story for PS-039 uses a ProofStudio 3D animation
metaphor:

- Proof Core — the central object that represents a proven campaign artifact.
- Evidence Orb — the orb that forms around the Proof Core as evidence
  accumulates.
- Campaign Record — the object appears as a campaign artifact (the recorded
  campaign artifact from PS-038a).

The cinematic sequence:

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

This is the cinematic proof story for PS-039. It is a presentation metaphor
over recorded proof. It does not prove campaign performance, marketing
effectiveness, business outcome, semantic truth, legal authenticity, legal
approval, human authorship, C2PA authenticity, production readiness, production
security, production compliance, uptime guarantee, cost guarantee, performance
guarantee, Object Lock, tamper-proof storage, or browser-side B2 byte
verification. The metaphor must keep every de-escalation pair from PS-038a
(proof does not equal truth; the Campaign Proof Room does not equal campaign
performance proof; manifest evidence does not equal semantic truth; etc.).

PS-038b records this metaphor. PS-039 implements it.

## 10. Brand identity direction

ProofStudio's brand must read as a serious premium media proof system, not a
generic AI toy.

Brand direction:

- serious premium media proof system
- not a generic AI toy
- no random neon blobs
- no robot mascots
- no generic AI sparkles
- near-black charcoal base (the canvas is dark, quiet, and premium)
- Backblaze-inspired orange used rarely as warmth (accent, never as the base
  wash)
- electric proof blue/cyan for verification
- muted green for verified
- amber for warning
- red only for destructive/error
- typography: premium grotesk, editorial headlines, precise evidence labels
- logo direction: a compact proof mark built from archive/check/manifest/orbit
  ideas

This direction is for PS-039. PS-038b records it; it does not design the final
logo or ship brand assets.

## 11. Dashboard architecture

This is the recorded architecture for PS-041 — World-Class User Dashboard.
PS-038b records it; PS-041 implements it.

Tech stack:

- Next.js 16 + React 19 + TypeScript
- Tailwind CSS v4
- shadcn/ui + Radix UI primitives
- TanStack Query v5
- TanStack Table v8
- React Hook Form + Zod
- Recharts first; ECharts only if heavy/high-frequency data requires it
- Supabase Postgres
- Drizzle ORM
- Better Auth primary, Supabase Auth backup

Dashboard principle: the dashboard must be calm, clear, data-first, useful, and
understandable in under 10 seconds. It is not a flashy marketing surface; it is
the working surface a creator/marketing team uses day to day.

The dashboard must include:

- campaign list
- proof status
- Campaign Proof Room launcher (cross-references PS-038a)
- passport launcher (provenance passport)
- B2 / Genblaze / rehydrate status
- review status
- export actions
- account/profile
- loading / empty / error / success states (every view must handle all four)

The dashboard must not contradict the PS-037 Disclosure + Trust Boundary. It
must reuse the PS-038a Campaign Proof Room framing. It must not claim campaign
performance proof, marketing effectiveness proof, business outcome guarantee,
semantic truth, legal authenticity, legal approval, human authorship, C2PA
authenticity, production readiness, production security, production compliance,
Object Lock, tamper-proof storage, or browser-side B2 byte verification.

PS-038b does not implement the dashboard. PS-041 does. PS-038b does not claim
the dashboard is implemented.

### 11.1 Dashboard personas

Execution personas for future PS-041 prompts/reviews:

- Dashboard Product Designer
- Data UX Architect
- Interaction Trust Reviewer
- Auth Security Architect
- Accessibility Reviewer
- PM Gatekeeper

## 12. Auth/account architecture

This is the recorded architecture for PS-040 — Auth + Account System.
PS-038b records it; PS-040 implements it.

Required auth capabilities:

- Google OAuth
- Apple OAuth
- GitHub OAuth
- email/password signup
- username login if useful
- email verification before activation
- block disposable/temp email domains
- validate email syntax
- validate domain/MX/deliverability where possible
- do not reject legitimate custom/company domains

Account / operational requirements:

- configurable allowlist/blocklist
- RBAC/account model
- rate limiting for auth-sensitive endpoints
- server-side validation
- audit hooks for important account actions

The auth layer must not overclaim. It must not claim enterprise security, must
not claim production compliance, and must not bypass the truth boundary.
Identity/authorization is real, but it does not prove semantic truth, legal
authenticity, human authorship, C2PA authenticity, or content authorship.

PS-038b does not implement auth. PS-040 does. PS-038b does not claim OAuth/auth
is implemented.

## 13. Agent/model operating plan

PS-038b records the agreed agent/model operating plan so that PS-039 onward
has a known assignment. These are execution roles, not authorities that can
override repo discipline. Rule: no model/agent may bypass repo gates, staging
policy, or PM acceptance.

Model/tool assignment:

- ChatGPT GPT-5.5 Thinking: PM/gatekeeper, roadmap, truth boundaries, final
  acceptance
- GLM 5.2 in VS Code/OpenCode: disciplined repo implementer
- Codex GPT-5.5 in VS Code: hard-code/refactor engineer, auth/security
  reviewer, complex implementation reviewer
- Claude 4.6 in Antigravity: Awwwards creative director / visual critic
- Gemini 3.1 Pro: large-context multimodal researcher/reviewer
- Gemini 3.5 Flash: fast variant generator for layouts, copy, microinteractions

PS-039a supersedes the website/dashboard portion of this assignment after the
rejected GLM-built PS-039 implementation failed visual/product gate. For PS-039
website and PS-041 dashboard build/repair work, GLM is excluded from PS-039
website and PS-041 dashboard build/repair work, and Codex GPT-5.5 in VS Code is
the repo builder. Claude 4.6 in Antigravity and Gemini 3.1 Pro / Gemini 3.5
Flash remain active in their visual critique, large-context researcher /
multimodal reviewer, and fast variant generator roles.

### 13.1 3D website personas/agents

Execution personas for future PS-039 prompts/reviews:

- Awwwards Creative Director
- Motion Director
- 3D Technical Director
- Brand Identity Director
- Premium Copywriter
- Frontend Performance Engineer

No agent or model may bypass the feature smoke, the central regression gate,
the frontend typecheck, the hidden Git flag check, the git diff check, or PM
acceptance.

## 14. CodeRabbit review gate

PS-038b adds the CodeRabbit review gate as a recorded later-stage review layer.

CodeRabbit should be used after major implementation/deployment slices (for
example after PS-039 / PS-040 / PS-041 / PS-042 implementation PRs, or before
final submission hardening), depending on repo flow. It is a post-build
PR/static-review gate.

CodeRabbit is an extra review layer, not a replacement for local gates. It is
not a replacement for:

- feature smoke
- central regression gate
- frontend typecheck
- hidden Git flag check
- git diff check
- PM acceptance

PS-038b does not run CodeRabbit. PS-038b does not claim CodeRabbit has reviewed
the project. The CodeRabbit review gate is recorded here so that PS-039 onward
knows when to apply it; it is enabled later, not by this slice.

## 15. Truth boundary

PS-038b records strategy only. It obeys every prior truth boundary from
PS-037 through PS-038a and does not weaken any of them. ProofStudio proves what
the pipeline did. It does not overclaim.

PS-038b specifically:

- does not claim production readiness
- does not claim production security
- does not claim production compliance
- does not claim OAuth/auth is implemented
- does not claim dashboard is implemented
- does not claim deployment/domain is done
- does not claim CodeRabbit has reviewed the project
- does not claim the 3D marketing website exists
- does not claim the brand identity is finalized
- does not claim campaign performance, marketing effectiveness, or business
  outcome
- does not claim semantic truth, legal authenticity, legal approval, human
  authorship, C2PA authenticity, or content authorship
- does not claim Object Lock / tamper-proof storage / browser-side B2 byte
  verification unless implemented and verified
- does not claim uptime guarantee, cost guarantee, or performance guarantee

PS-038b is local / static / docs only. It makes no Cloudflare API calls, mutates
no DNS, creates no Cloudflare resource, deploys no Cloudflare Pages, deploys no
Cloudflare Workers, performs no Cloudflare R2 live reads, performs no
Cloudflare R2 writes, performs no Backblaze B2 writes, calls no provider, calls
no model, reads no live B2, writes no B2, performs no broad B2 scans, and
changes no deployment / env / render.yaml / requirements config.

## 16. Acceptance criteria

PS-038b is accepted only when:

- this spec exists at
  `specs/62-ps-038b-winning-product-presentation-architecture.md`
- the branch `ps-038b/winning-product-presentation-architecture` starts from
  `origin/accepted/proofstudio` and the starting HEAD equals
  `42fae3cda40f03316936ff8d500f614b4cde474b`
- `specs/07-master-spec-plan.md` is updated to reflect PS-038b and the
  corrected future sequence, without rewriting unrelated historical slices and
  without weakening any prior truth boundary
- `specs/08-roadmap-slices.md` is updated to reflect PS-038b and the corrected
  future sequence (PS-038b -> PS-039 -> PS-040 -> PS-041 -> PS-042 -> PS-043 ->
  PS-044), without rewriting unrelated historical slices and without weakening
  any prior truth boundary
- the proof doc
  `docs/ps-038b-winning-product-presentation-architecture-proof.md` exists and
  records the changed files, the roadmap correction, and the truth boundary
- the changed file set is exactly the four files listed in section 1 (spec,
  07, 08, proof doc) — no other files changed
- no implementation code, no app files, no scripts, no evidence mutation, no
  env/secrets changes, no deployment changes, no render.yaml changes, no
  requirements/dependency changes
- no provider calls, no model calls, no B2 reads/writes, no Cloudflare
  API/DNS/resource/deploy/R2 behavior
- no weakening, removal, or rewrite of any truth boundary from PS-037 through
  PS-038a
- no change to any golden run canonical constant
- all required exact strings (section 18) are present
- no hidden Git flags `h` or `S` are present (verified by the explicit h/S
  checker over `git ls-files -v`, failing when `line[0]` is `h` or `S`)
- `git diff --check` is clean
- no staging, commit, or push occurs until PM acceptance

## 17. Rollback

Rollback of PS-038b is a single revert of this slice, because PS-038b changes
only four docs/spec/roadmap files and changes no product, backend, provider,
deployment, env, requirements, or evidence behavior.

Specifically, rollback reverts to pre-PS-038b state:

- remove `specs/62-ps-038b-winning-product-presentation-architecture.md`
- revert the PS-038b additions in `specs/07-master-spec-plan.md`
- revert the PS-038b additions in `specs/08-roadmap-slices.md`
- remove `docs/ps-038b-winning-product-presentation-architecture-proof.md`

Rollback of PS-038b must not touch any evidence under `docs/evidence/**`, must
not touch the central gate (`scripts/proofstudio_regression_gate.py`),
`scripts/smoke_lib.py`, `AGENTS.md`, `.env*`, `render.yaml`, requirements
files, any provider wrapper, any model client, any Cloudflare client, any B2
storage path, any DNS mutation path, or any deployment config path. Rollback is
isolated and reversible because PS-038b is a self-contained docs/spec/roadmap
alignment slice; it does not change provider behavior, model behavior,
generation behavior, Cloudflare behavior, DNS behavior, B2 behavior, billing
behavior, or deployment topology.

## 18. Verbatim implementation/audit contract strings

The PS-038b docs/roadmap edits and the proof doc must preserve the following
exact strings so the PS-038b contract is deterministic and auditable. Any
future PM audit must check these exact strings; do not rely on close-enough
wording. No surprise audit checks: any exact string a future PM audit should
check is listed here.

The required identity / slice strings are:

- PS-038b
- Winning Product Presentation Architecture

The required roadmap sequence strings are:

- Brand Identity + 3D Marketing Website + Demo Automation Shell
- Auth + Account System
- World-Class User Dashboard
- Deployment / Domain / Production Demo Hardening
- Final Submission Pack
- Devpost Package + 3-Minute Demo Script

The required visual metaphor strings are:

- Proof Core
- Evidence Orb
- Campaign Record
- Campaign Proof Room

The required 3D website stack / strategy strings are:

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS v4
- Three.js
- React Three Fiber
- Drei
- GSAP ScrollTrigger
- Lenis
- Framer Motion
- Canvas/image-sequence
- GLB/glTF
- reduced-motion fallback
- mobile/tablet/desktop

The required dashboard stack strings are:

- shadcn/ui
- Radix UI primitives
- TanStack Query v5
- TanStack Table v8
- React Hook Form
- Zod
- Recharts
- ECharts
- Supabase Postgres
- Drizzle ORM
- Better Auth
- Supabase Auth backup

The required auth strings are:

- Google OAuth
- Apple OAuth
- GitHub OAuth
- email/password signup
- username login
- email verification before activation
- block disposable/temp email domains
- validate domain/MX/deliverability
- do not reject legitimate custom/company domains

The required CodeRabbit / gate strings are:

- CodeRabbit review gate
- CodeRabbit is an extra review layer, not a replacement for local gates
- feature smoke
- central regression gate
- frontend typecheck
- hidden Git flag check
- git diff check
- PM acceptance

The required posture / boundary strings are:

- no implementation code
- no deployment changes
- no env/secrets changes
- no provider calls
- no model calls
- no B2 reads/writes
- no Cloudflare API/DNS/resource/deploy/R2 behavior
- hidden Git flags h
- line[0]

The required truth-boundary (does-not-claim) strings are:

- does not claim production readiness
- does not claim production security
- does not claim production compliance
- does not claim OAuth/auth is implemented
- does not claim dashboard is implemented
- does not claim deployment/domain is done
- does not claim CodeRabbit has reviewed the project

The required base-ref strings are:

- origin/accepted/proofstudio
- 42fae3cda40f03316936ff8d500f614b4cde474b
