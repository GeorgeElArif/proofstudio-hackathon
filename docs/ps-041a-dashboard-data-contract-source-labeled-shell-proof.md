# PS-041A Dashboard Data Contract + Source-Labeled Shell Proof

Date: 2026-07-11
Branch: `ps-041/world-class-user-dashboard-v1`
Base: `origin/accepted/proofstudio @ e7611de9c8ad912bf6ae3d31363bf8d7459cafcc`

## Final Information Architecture

The final PS-041A pass compresses `/dashboard` into one inspection-oriented
product flow:

1. compact ProofStudio navigation
2. dashboard purpose, trust boundary, primary inspection action, and refresh
3. branded golden inspection object
4. three-state source strip
5. six-stage interactive evidence pipeline
6. compact source-integrity summary with a collapsed ledger
7. one account-campaign empty state
8. four primary commands with secondary tools collapsed

This is a presentation and interaction pass over the existing PS-041A model.
No source contract or backend behavior changed.

## PS-039 Brand Integration

The inspection object reuses the committed PS-039 sealed capsule poster:

`apps/web/public/ps039/proof-object-sealed-poster.jpg`

The dashboard uses the image as a non-autoplay still, supplies the meaningful
alternative text `Sealed golden ProofStudio evidence capsule`, and retains a
CSS fallback behind the image. No visual asset, external URL, base64 payload,
or new video behavior was added. The PS-039 landing scroll-scrub implementation
is unchanged.

## First Viewport

At 1440×900 the top of the page shows the compact navigation, title and
one-sentence purpose, required trust boundary, `Inspect golden proof`,
`Refresh sources`, PS-039 capsule, three-state source strip, the full evidence
rail, and the beginning of the selected Archive/B2 detail.

The source strip contains only:

- Session — server auth/session state and source badge
- Proof runtime — reachability state and source badge
- Account campaigns — connection state and `not_implemented` source badge

Detailed explanations no longer compete with the first-view decision path.

## Interactive Evidence Pipeline

The former six expanded proof cards are now one six-stage rail and one selected
detail panel:

1. Capture / Campaign
2. Manifest / Genblaze
3. Archive / B2
4. Rehydrate
5. Review
6. Export / Passport

Archive/B2 is selected by default. Desktop uses semantic tab controls with a
single `tabpanel`; mobile converts the controls into a vertical stepper and
keeps one detail panel expanded. Selection is component-local React state only.
Arrow keys move between stages, focus follows the selection, and Enter/Space
retain native button activation. Every stage retains its textual status,
source badge, and existing inspect route where available.

## Progressive Source Disclosure

Source integrity is reduced to three factual summary groups: real sources,
fixture sources, and the missing account ownership/list source. A closed native
`details` element contains the complete deduplicated source ledger, endpoints or
evidence paths, and the auth boundary. Source labels and limitations remain in
the model and are not hidden.

## Account Campaign Empty State

The previous Missing/Why/Next/Refusal grid is one compact panel:

- heading: `Account campaigns are not connected yet`
- one short explanation
- `Inspect golden proof` action
- closed `Why this is unavailable` disclosure

The disclosure records the missing ownership API, missing list API, refusal to
insert fake campaigns/users/sessions/metrics, and PS-041B as the next backend
contract slice. This limitation is not repeated across visible sections.

## Commands

Four primary commands remain visible:

- Open Proof Room
- Open Passport
- Inspect Pipeline
- Open Evidence Pack

`More proof tools` is collapsed by default and contains B2 evidence, Genblaze,
Rehydrate, Review workspace, Account session, Demo route, and Review room. Each
action retains the source from the existing dashboard model.

## Mobile Product Behavior

Mobile replaces the former horizontally scrolling rail with a native expandable
menu for Command, Proof, Sources, and Account. At 390×844 the capsule and both
top actions are visible before the source strip. At 320px the page reflows to a
single column with no document-level horizontal overflow. The evidence stages
become full-width 58px controls; source detail and secondary tools remain closed.
Fixture identifiers truncate visually while retaining the full identifier in a
title attribute.

## Accessibility Findings

- Evidence controls are buttons with tab semantics, `aria-selected`,
  `aria-expanded`, `aria-controls`, and a labelled selected panel.
- Arrow-key navigation was exercised from Archive/B2 to Rehydrate.
- Keyboard focus renders a 2px gold outline with a 3px offset.
- Native `details`/`summary` controls expose disclosure state.
- Mobile menu, actions, stage controls, disclosures, and the brand/home link
  measure at least 44 CSS pixels high at 390px and 320px.
- Browser measurements reported `scrollWidth === innerWidth` at both 390px and
  320px; duplicate IDs: zero.
- Heading order is one H1, section H2s, and the selected-stage H3.
- The capsule has meaningful alt text; its CSS fallback is decorative.
- Links and buttons have border/background affordances and visible focus.
- State is communicated by text and badge shape as well as color.

## Screenshots

Captured from the top of local `/dashboard` with unavailable local auth/proof
runtimes represented truthfully:

- `ps041a-dashboard-desktop-first-viewport.png` — 1440×900
- `ps041a-dashboard-desktop-full.png` — 1440px full page
- `ps041a-dashboard-mobile-first-viewport.png` — 390×844
- `ps041a-dashboard-mobile-full.png` — 390px full page
- `ps041a-dashboard-stage-detail.png` — desktop Archive/B2 selected detail

Review location:
`/tmp/proofstudio-ps041a-final-dashboard-review-pack/screenshots/`

## Validation

- `git diff --check`: passed
- hidden Git flag scan: passed; no leading `h` or `S`
- `npm ci --ignore-scripts`: passed
- `npm run typecheck`: passed
- `npm run build`: passed with the existing Vite large-chunk warning
- `npm run smoke:auth-client`: passed
- `npm run smoke:dashboard-contract`: passed
- `npm run smoke:dashboard-ui`: passed
- `npm audit --omit=dev`: sandbox attempt hit `EAI_AGAIN`; single approved retry
  passed with zero production vulnerabilities

`npm ci`'s automatic all-dependency audit reported one moderate and one high
development-tree advisory; the required production-only audit reported zero.

## Unchanged Source and Data Boundaries

The dashboard continues to preserve:

- `DashboardSessionState`
- `DashboardCampaignSummary`
- `DashboardProofLayerStatus`
- `DashboardAction`
- `DashboardDataSourceLabel`
- `DashboardUnavailableReason`
- auth/session readback through the existing client
- proof API health readback through the existing client
- source kinds `auth_session`, `proof_api`, `checked_in_fixture`,
  `demo_fixture`, `unavailable`, and `not_implemented`
- an empty real account campaign list
- a checked-in golden fixture that is not account-owned

Required trust boundary:

`ProofStudio proves what the pipeline recorded. Proof does not equal truth.`

No auth-server or FastAPI files changed. No campaign ownership/list API,
durable campaign store, fake campaign, fake metric, fake session, fake user, or
proof state was added.

## Remaining PS-041B Limitations

PS-041B still owns the backend contract for account-to-campaign ownership and
account campaign listing. Until that contract, authorization, storage, and
query behavior exist, PS-041A must keep real account campaign rows empty and
must keep the golden entry labeled as checked-in fixture evidence.
