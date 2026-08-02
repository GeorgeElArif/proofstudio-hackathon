# PS-038b — Winning Product Presentation Architecture — Proof

Status: Spec only / docs only.
Slice: PS-038b
Date: 2026-07-03
Branch: `ps-038b/winning-product-presentation-architecture`
Base ref: `origin/accepted/proofstudio`
Starting HEAD: `42fae3cda40f03316936ff8d500f614b4cde474b`
Spec: `specs/62-ps-038b-winning-product-presentation-architecture.md`

PS-038b is documentation / spec / roadmap alignment only. It does not implement
the 3D marketing website, auth, the dashboard, or deployment. It does not touch
product code, backend, providers, deployment, requirements, or dependencies. It
does not call providers, does not read B2, does not call Cloudflare, and does
not run any model. It records strategy only and does not claim implementation
exists.

## 0. Why this proof doc exists

The closest accepted analog to PS-038b is PS-034C (a docs / spec / roadmap
alignment slice that modified `specs/07-master-spec-plan.md` and
`specs/08-roadmap-slices.md`). PS-034C paired its spec + roadmap edits with a
proof doc (`docs/ps-034c-winning-roadmap-master-spec-replan-proof.md`) in its
replan commit. PS-038b follows that established convention: when a roadmap
alignment slice modifies the master spec plan and the roadmap slices ledger, it
ships a proof doc that records the changed files, the roadmap correction, the
captured strategy, and the truth boundary. No smoke script or evidence report
is created for PS-038b (those paths are out of scope and explicitly forbidden
for this slice).

## 1. Files changed

PS-038b changed only the following files:

- `specs/62-ps-038b-winning-product-presentation-architecture.md` (this slice's
  spec)
- `specs/07-master-spec-plan.md` (added section 8.14 + corrected the
  Post-PS-034C Roadmap Ledger)
- `specs/08-roadmap-slices.md` (added the PS-038b slice entry + corrected the
  future sequence to PS-038b -> PS-039 -> PS-040 -> PS-041 -> PS-042 -> PS-043
  -> PS-044 + updated the Wave 8 Decisions Summary)
- `docs/ps-038b-winning-product-presentation-architecture-proof.md` (this
  proof doc)

No other files were changed. No product, backend, provider, deployment,
requirements, or `.env*` files were touched. No file under `apps/**`, `src/**`,
`scripts/**`, or `docs/evidence/**` was modified. `AGENTS.md`, `render.yaml`,
requirements files, and `docs/validation/proofstudio-smoke-harness-v1.md` were
not modified. No prior-slice evidence was modified.

## 2. Roadmap correction summary

Final Submission Pack is not next. Before final submission, ProofStudio needs:

1. Brand Identity + 3D Marketing Website + Demo Automation Shell
2. Auth + Account System
3. World-Class User Dashboard
4. Deployment / Domain / Production Demo Hardening
5. Final Submission Pack
6. Devpost Package + 3-Minute Demo Script

Corrected future sequence:

- PS-038b — Winning Product Presentation Architecture (docs only)
- PS-039 — Brand Identity + 3D Marketing Website + Demo Automation Shell
- PS-040 — Auth + Account System
- PS-041 — World-Class User Dashboard
- PS-042 — Deployment / Domain / Production Demo Hardening
- PS-043 — Final Submission Pack
- PS-044 — Devpost Package + 3-Minute Demo Script

What this corrects: the pre-PS-038b ledger listed PS-039 as Final Submission
Pack, PS-039a as Devpost Submission Package + 3-Minute Demo Script, and PS-040
(Product Dashboard + Marketing Website) as delayed/optional. PS-038b makes the
presentation + productization layer required and sequences it before the Final
Submission Pack. The earlier PS-039a (Devpost) identifier is folded into
PS-044.

PS-038b preserves prior accepted history. It does not rewrite unrelated
historical slices (PS-001 through PS-038a). It does not remove or weaken any
truth boundary from PS-037 through PS-038a. It does not change any golden run
canonical constant. It does not change any historical contract the regression
gate verifies.

## 3. Strategy captured summary

### 3.1 3D marketing website (for PS-039)

Next.js 16 + React 19 + TypeScript, Tailwind CSS v4, Three.js + React Three
Fiber + Drei, GSAP ScrollTrigger + Lenis, Framer Motion, Canvas/image-sequence
for cinematic hero moments, GLB/glTF assets from Blender or Spline,
reduced-motion fallback, mobile/tablet/desktop variants, performance budgets
and lazy loading. No fake production/security/performance claims.

### 3.2 Cinematic proof metaphor (for PS-039)

Proof Core / Evidence Orb / Campaign Record. The campaign artifact appears,
splits into proof layers (prompt, provider/model, B2 archive, Genblaze
manifest, rehydrate check, review decision, provenance passport, export pack),
and reassembles into the Campaign Proof Room. This keeps every PS-038a
de-escalation pair intact (proof does not equal truth; the Campaign Proof Room
does not equal campaign performance proof; manifest evidence does not equal
semantic truth; etc.).

### 3.3 Brand identity direction (for PS-039)

Serious premium media proof system, not a generic AI toy. No random neon blobs,
no robot mascots, no generic AI sparkles. Near-black charcoal base.
Backblaze-inspired orange used rarely as warmth. Electric proof blue/cyan for
verification. Muted green for verified. Amber for warning. Red only for
destructive/error. Premium grotesk typography, editorial headlines, precise
evidence labels. Compact proof mark built from archive/check/manifest/orbit
ideas.

### 3.4 Dashboard architecture (for PS-041)

Next.js 16 + React 19 + TypeScript, Tailwind CSS v4, shadcn/ui + Radix UI
primitives, TanStack Query v5, TanStack Table v8, React Hook Form + Zod,
Recharts first / ECharts only if heavy/high-frequency data requires it,
Supabase Postgres, Drizzle ORM, Better Auth primary / Supabase Auth backup.
Calm, clear, data-first, understandable in under 10 seconds. Campaign list,
proof status, Campaign Proof Room launcher, passport launcher, B2/Genblaze/
rehydrate status, review status, export actions, account/profile, and full
loading/empty/error/success states.

### 3.5 Auth/account architecture (for PS-040)

Google OAuth, Apple OAuth, GitHub OAuth, email/password signup, username login,
email verification before activation, block disposable/temp email domains,
validate email syntax, validate domain/MX/deliverability where possible, do
not reject legitimate custom/company domains, configurable allowlist/blocklist,
RBAC/account model, rate limiting for auth-sensitive endpoints, server-side
validation, audit hooks for important account actions.

### 3.6 Agent/model operating plan

ChatGPT GPT-5.5 Thinking (PM/gatekeeper), GLM 5.2 in VS Code/OpenCode
(disciplined repo implementer), Codex GPT-5.5 in VS Code (hard-code/refactor
engineer, auth/security reviewer), Claude 4.6 in Antigravity (Awwwards
creative director / visual critic), Gemini 3.1 Pro (large-context multimodal
researcher/reviewer), Gemini 3.5 Flash (fast variant generator). No model/agent
may bypass repo gates, staging policy, or PM acceptance.

### 3.7 CodeRabbit review gate

CodeRabbit is a recorded later post-build PR/static-review gate, used after
PS-039/PS-040/PS-041/PS-042 implementation PRs or before final submission
hardening. CodeRabbit is an extra review layer, not a replacement for local
gates. It does not replace the feature smoke, the central regression gate, the
frontend typecheck, the hidden Git flag check, the git diff check, or PM
acceptance.

## 4. Truth boundary

PS-038b records strategy only. It obeys every prior truth boundary from PS-037
through PS-038a and does not weaken any of them.

PS-038b:

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

PS-038b is local / static / docs only: no implementation code, no deployment
changes, no env/secrets changes, no provider calls, no model calls, no B2
reads/writes, and no Cloudflare API/DNS/resource/deploy/R2 behavior.

## 5. Validation results

- repo path confirmed: `/home/proofstudio-work/proofstudio`
- `origin` fetched; `origin/accepted/proofstudio` resolves to
  `42fae3cda40f03316936ff8d500f614b4cde474b`
- branch `ps-038b/winning-product-presentation-architecture` created from
  `origin/accepted/proofstudio`; starting HEAD equals
  `42fae3cda40f03316936ff8d500f614b4cde474b`
- changed file set is exactly the four files listed in section 1 (no other
  files changed; no forbidden files changed)
- no staged changes
- all required exact strings from the PS-038b spec section 18 are present
- no affirmative claim that implementation exists
- hidden Git flags `h`/`S` check clean (`git ls-files -v` shows no line whose
  first character is `h` or `S`)
- `git diff --check` clean
- no stage/commit/push performed (PM acceptance only)

This proof doc is not run by a smoke; PS-038b ships no smoke script and no
evidence report by design (those paths are out of scope for this slice).
