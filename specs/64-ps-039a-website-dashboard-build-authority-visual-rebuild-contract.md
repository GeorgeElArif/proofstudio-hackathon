# PS-039a — Website/Dashboard Build Authority + Visual Rebuild Contract

Status: Docs/spec alignment only.
Slice: PS-039a
Date: 2026-07-03
Branch: `ps-039a/website-dashboard-build-authority-visual-rebuild-contract`
Spec: `specs/64-ps-039a-website-dashboard-build-authority-visual-rebuild-contract.md`

## 1. Status

PS-039a — Website/Dashboard Build Authority + Visual Rebuild Contract is a
docs/spec alignment only slice. It records the corrected build authority and
the visual/product acceptance contract before PS-039 is rebuilt.

From PS-039a onward, PS-039a means Website/Dashboard Build Authority + Visual Rebuild Contract only.
The earlier historical Devpost/demo-script identifier is folded into PS-044.

PS-039a is not an implementation slice. It has no implementation code, no app
files, no scripts, no evidence mutation, no env/secrets changes, no deployment
changes, no provider calls, no model calls, no B2 reads/writes, and no
Cloudflare API/DNS/resource/deploy/R2 behavior.

The accepted base for this slice is:

- ref: `origin/accepted/proofstudio`
- commit the ref resolves to at the time of this spec:
  `4ee42823d25fba670b9c2367882d86bc2c62f389`

The ref is the authority. The commit is recorded for traceability and because
this slice was explicitly opened against
`origin/accepted/proofstudio @ 4ee42823d25fba670b9c2367882d86bc2c62f389`.

## 2. Rejected PS-039 Build

The rejected GLM-built PS-039 implementation failed visual/product gate. Static
checks, builds, and smokes may pass while the product surface still fails the
PS-039 standard.

The rejected GLM-built PS-039 implementation:

- must not be staged
- must not be committed
- must not be accepted
- must not be repaired by GLM
- must not be restored from discarded working tree

The root cause is that GLM optimized for static proof strings, cards, and
safety checks, but failed the intended product surface: a cinematic premium
winning-project presentation layer. The prior result looked like a dense
technical docs page with flat evidence-card layout instead of a cinematic 3D
marketing site.

## 3. Corrected Model / Tool Team

Corrected model/tool team:

- ChatGPT GPT-5.5 Thinking: PM / release gatekeeper
- Codex GPT-5.5 in VS Code: repo builder for PS-039 website and PS-041 dashboard
- Claude 4.6 in Antigravity: Awwwards Creative Director / visual critic
- Gemini 3.1 Pro: large-context researcher / multimodal reviewer / screenshot
  and spec reviewer
- Gemini 3.5 Flash: fast variant generator for layouts, copy, and
  microinteractions
- CodeRabbit: later post-build PR/static review layer only
- GLM: excluded from PS-039 website and PS-041 dashboard build/repair work

GLM is excluded from PS-039 website and PS-041 dashboard build/repair work.
Claude 4.6 and Gemini roles remain active. Only GLM was removed from
website/dashboard build authority, and Codex GPT-5.5 in VS Code was promoted
as builder for those surfaces.

## 4. PS-039 Website Target

The PS-039 website target is a winning-project presentation layer: a cinematic
3D marketing site with deep near-black premium atmosphere,
Apple/Awwwards-level typography and hierarchy, a sticky full-screen
Canvas/image-sequence or equivalent cinematic hero, scroll-synchronized story
beats, and a clear judge demo CTA.

The cinematic metaphor remains Proof Core / Evidence Orb / Campaign Record.
The campaign artifact appears, splits into proof layers, and reassembles into
Campaign Proof Room.

Required proof layers:

- prompt
- provider/model
- B2 archive
- Genblaze manifest
- rehydrate check
- review decision
- provenance passport
- export pack

The PS-039 rebuild must include a reduced-motion fallback and intentional
desktop/tablet/mobile layouts.

## 5. PS-039 Hard Visual Rejection List

The PS-039 rebuild must reject:

- dense technical docs page
- tiny text everywhere
- flat evidence-card layout
- generic dark UI
- random neon blobs
- generic AI sparkles
- robot mascots
- crypto/NFT dashboard vibes
- proof details competing with the cinematic story

## 6. PS-041 Dashboard Target

The PS-041 dashboard target is a calm, clear, fast tool interface. It is not a
marketing page. It is data-first, understandable in under 10 seconds, and the
UI should point toward the data, not compete with it.

Required dashboard characteristics:

- quiet persistent sidebar
- one primary insight/action per screen
- search/filter/sort/selection tables
- contextual bulk actions
- functional charts with axes/labels/values
- loading/empty/error/success states
- optimistic feedback where appropriate
- clear interaction intent
- safe destructive confirmations
- server-side RBAC
- Zod validation
- audit hooks

## 7. Website Target Stack

The PS-039 website target stack is:

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS v4
- Three.js
- React Three Fiber
- Drei
- GSAP ScrollTrigger
- Lenis
- Motion / Framer-style microinteractions
- Canvas/image-sequence
- GLB/glTF
- reduced-motion fallback

## 8. Dashboard Target Stack

The PS-041 dashboard target stack is:

- Next.js 16 App Router
- React 19
- TypeScript
- Tailwind CSS v4
- shadcn/ui
- Radix UI primitives
- TanStack Query v5
- TanStack Table v8
- React Hook Form
- Zod
- Recharts first
- ECharts only if heavy/high-frequency visualization requires it
- Supabase Postgres
- Drizzle ORM
- Better Auth primary
- Supabase Auth backup

## 9. Future Workflow

Future workflow:

1. Accept PS-039a first.
2. Then produce Gemini 3.1 Pro / Claude 4.6 visual planning and critique pack.
3. Then Codex GPT-5.5 in VS Code rebuilds PS-039 implementation from accepted
   base.
4. Then PM/human review desktop/tablet/mobile/reduced-motion screenshots
   before any commit.

No model may bypass:

- PM acceptance
- local validation
- feature smoke
- central regression gate
- frontend typecheck/build
- hidden Git flag check
- git diff check
- screenshot gates
- staging policy
- human acceptance

## 10. Truth Boundary

PS-039a records process and strategy only. It does not claim implementation
exists. It does not claim production readiness. It does not claim production
security. It does not claim production compliance. It does not claim OAuth/auth
is implemented. It does not claim dashboard is implemented. It does not claim
deployment/domain is done. It does not claim CodeRabbit has reviewed the
project.

PS-039a does not claim campaign performance, marketing effectiveness, semantic
truth, legal authenticity, human authorship, C2PA authenticity, Object Lock,
tamper-proof storage, browser-side B2 byte verification, uptime guarantee,
cost guarantee, or performance guarantee.

## 11. Acceptance Criteria

PS-039a is accepted only when:

- this spec exists at
  `specs/64-ps-039a-website-dashboard-build-authority-visual-rebuild-contract.md`
- the branch starts from `origin/accepted/proofstudio`
- starting HEAD equals `4ee42823d25fba670b9c2367882d86bc2c62f389`
- `origin/accepted/proofstudio` resolves to
  `4ee42823d25fba670b9c2367882d86bc2c62f389`
- the rejected GLM-built PS-039 implementation is recorded as rejected
- the corrected build authority is recorded
- the PS-039 website visual rebuild contract is recorded
- the PS-041 dashboard contract is recorded
- no implementation code, no app files, no scripts, no evidence mutation, no
  env/secrets changes, no deployment changes, no provider calls, no model
  calls, no B2 reads/writes, no Cloudflare API/DNS/resource/deploy/R2 behavior
- no hidden Git flags `h` or `S` are present, checked using `git ls-files -v`
  and `line[0]`
- `git diff --check` is clean
- no staging, commit, or push occurs until PM acceptance

## 12. Required Exact Strings

The PS-039a docs must preserve these exact strings:

- PS-039a
- Website/Dashboard Build Authority + Visual Rebuild Contract
- rejected GLM-built PS-039 implementation
- failed visual/product gate
- must not be staged
- must not be committed
- must not be accepted
- must not be repaired by GLM
- GLM is excluded from PS-039 website and PS-041 dashboard build/repair work
- Codex GPT-5.5 in VS Code
- Claude 4.6 in Antigravity
- Gemini 3.1 Pro
- Gemini 3.5 Flash
- Awwwards Creative Director
- large-context researcher / multimodal reviewer
- fast variant generator
- ChatGPT GPT-5.5 Thinking
- PM / release gatekeeper
- winning-project presentation layer
- cinematic 3D marketing site
- deep near-black premium atmosphere
- Apple/Awwwards-level typography and hierarchy
- sticky full-screen Canvas/image-sequence
- scroll-synchronized story beats
- Proof Core
- Evidence Orb
- Campaign Record
- Campaign Proof Room
- prompt
- provider/model
- B2 archive
- Genblaze manifest
- rehydrate check
- review decision
- provenance passport
- export pack
- reduced-motion fallback
- desktop/tablet/mobile
- dense technical docs page
- flat evidence-card layout
- calm, clear, fast tool interface
- understandable in under 10 seconds
- the UI should point toward the data, not compete with it
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS v4
- Three.js
- React Three Fiber
- Drei
- GSAP ScrollTrigger
- Lenis
- Motion / Framer-style microinteractions
- Canvas/image-sequence
- GLB/glTF
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
- no implementation code
- no deployment changes
- no env/secrets changes
- no provider calls
- no model calls
- no B2 reads/writes
- no Cloudflare API/DNS/resource/deploy/R2 behavior
- does not claim implementation exists
- does not claim production readiness
- does not claim production security
- does not claim production compliance
- does not claim OAuth/auth is implemented
- does not claim dashboard is implemented
- does not claim deployment/domain is done
- does not claim CodeRabbit has reviewed the project
- origin/accepted/proofstudio
- 4ee42823d25fba670b9c2367882d86bc2c62f389
