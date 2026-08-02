# PS-041E1 private dynamic lineage UI proof

PS-041E1 is built from accepted ref `origin/accepted/proofstudio` at
`b345497868ccbdffb1f56450cd0d40c375f26cb4` on branch
`ps-041e1/private-dynamic-lineage-ui-v1`. It implements the private read-only
dynamic lineage UI over the accepted PS-041D auth-server gateway contract. No
auth-server or FastAPI source was modified. No new web dependency was added.

## Files

Modified (tracked):

- `apps/web/package.json` — adds the `smoke:lineage-ui` and
  `smoke:lineage-ui-runtime` scripts.
- `apps/web/src/App.tsx` — adds `getPrivateLineagePath` and dispatches the
  three private lineage routes in passport → detail → list order; malformed
  percent-encoding or empty decoded id produces an explicit `lineage-invalid`
  route that renders the static `MalformedLineageReferencePage` (zero reads,
  no `/campaigns//` request). IDs decoded safely; golden public Passport and
  proof-room routes unchanged.
- `apps/web/src/authorizedProofClient.ts` — adds `fetchCampaignLineage`,
  `fetchCampaignLineageBundle`, `fetchCampaignLineagePassport`; uses
  `credentials: "include"`, relative `/account/campaigns/.../lineage[...]`
  routes, `encodeURIComponent`; no service/operator token; no direct FastAPI
  URL; no retry loop; no fixture fallback; 401/404/503 preserved.
- `apps/web/src/dashboard/DashboardSurface.tsx` — adds the read-only
  `Open recorded lineage` launcher for each account campaign, linking to the
  private lineage list with `encodeURIComponent`.
- `apps/web/src/styles.css` — adds the PS-041E1 lineage workspace styles
  (cards, stage lanes, single bounded SVG edge overlay with `overflow:
  hidden`, recorded/inferred legend, checks, limitations, B2 reference card,
  passport tables, dedicated bundle-root and unclassified sections, mobile
  fallback with semantic vertical connectors, reduced-motion).

New (untracked):

- `apps/web/src/bundleLineage.ts` — strict types, bounded runtime parser,
  graph-aware stage classification (`classifyNodeStages`,
  `buildStageLayout`), worst-outcome priority (`worstCheck`,
  `PRIORITY_ORDER`), deterministic ordering, display-safe labels, severity
  mapping, structured B2 reference fields, no URL construction, no raw JSON.
- `apps/web/src/BundleLineage.tsx` — `BundleLineageListPage`,
  `BundleLineageDetailPage`, `PortableLineagePassportPage`,
  `MalformedLineageReferencePage` and supporting presentation components.
  Copy/download serializes the exact raw server Passport object
  (`state.payload.passport`), not the camelCase DTO.
- `apps/web/scripts/smoke-lineage-ui.mjs` — check-only source-contract smoke.
- `apps/web/scripts/smoke-lineage-ui-runtime.mjs` — check-only runtime
  behavior validation (browser-driven; proves zero reads for malformed
  routes, 16/16 render, worst-outcome priority, 503 dependency-unavailable,
  exact raw Passport serialization, no FastAPI/provider/B2/public-passport
  requests).
- `apps/web/scripts/capture-ps041e-screenshots.mjs` — deterministic
  fixture-intercepted screenshot capture using Playwright (Node or Python)
  with one shared CAPTURE_PLAN consumed by both engines.
- `apps/web/scripts/fixtures/ps041e1/*.json` — ten deterministic fixtures
  derived from the exact accepted PS-041D runtime response (16 nodes / 16
  edges in the full and passport fixtures).
- `specs/70-ps-041e1-private-dynamic-lineage-ui.md` — this slice spec.
- `docs/ps-041e1-private-dynamic-lineage-ui-proof.md` — this proof document.

## Backend changes

None. No auth-server source or FastAPI source was modified. The slice reads
only the accepted PS-041D gateway routes. If a backend change had appeared
necessary, the operating law required stopping and documenting the missing
field/route instead of implementing it; no such blocker was encountered.

## Direct-FastAPI confirmation

The browser never constructs a direct FastAPI URL. `authorizedProofClient.ts`
uses only relative `/account/campaigns/...` gateway routes through
`getAuthBaseUrl()`. `BundleLineage.tsx` and `bundleLineage.ts` contain no
`localhost:8000` or `127.0.0.1:8000` direct-FastAPI references. The smoke
checks this explicitly.

## Token / signed-URL confirmation

No `Authorization`, service (`X-ProofStudio-Internal-Token`), or operator
(`X-ProofStudio-Import-Token`) header is sent to the browser. The browser
carries only the Better Auth session cookie via `credentials: "include"`. No
signed URL is constructed; the B2 reference card emits only accepted
structured fields and never builds a bucket URL. Fixtures contain no
`X-Amz-`, `AWSAccessKeyId`, `password`, `DATABASE_URL`, `@` (email-like), or
`prompt` markers.

## Route checks

- `/account/campaigns/:campaignId/lineage` → `BundleLineageListPage`
- `/account/campaigns/:campaignId/lineage/:bundleId` → `BundleLineageDetailPage`
- `/account/campaigns/:campaignId/lineage/:bundleId/passport` → `PortableLineagePassportPage`
- Malformed percent-encoding or empty decoded id → `lineage-invalid` →
  `MalformedLineageReferencePage` (static page, no data hook, zero reads)

The matcher checks passport before detail before list, so longer paths do
not collide with the list dispatcher. IDs are decoded with
`decodeURIComponent` inside a `try`/`catch`; malformed encoding yields the
static `MalformedLineageReferencePage`. The runtime validation script
confirms ZERO gateway reads for malformed list, detail, and passport routes
and ZERO requests containing `/campaigns//`.

## Client fetch contract

All reads go through `fetchCampaignLineage`,
`fetchCampaignLineageBundle`, `fetchCampaignLineagePassport`:

- `credentials: "include"`;
- relative `/account/campaigns/{encodeURIComponent(campaignId)}/lineage[/...]`;
- 401 → `unauthenticated`; 404 → `not_found`; 503 → `unavailable`;
- non-`available` envelope or missing role → `error`;
- no retry loop; no fixture fallback after an API failure;
- `campaignId` / `bundleId` always passed through `encodeURIComponent`.

## Dashboard launcher

The dashboard account-campaign list renders a read-only
`Open recorded lineage` launcher for each account campaign. It links to the
private lineage list with `encodeURIComponent(campaignId)`. It does not show
an import button, upload button, or public-share action, and it does not use
any of the forbidden labels (Verify authenticity, Complete provenance,
Certified ownership, View truth, Public Passport).

## Bundle-list behavior

The list shows: campaign context; private/read-only status; deterministic
bundle rows; source revision; bundle ID and fingerprint in progressive
detail; node/edge counts; bundle state; safe empty state; safe loading;
safe 401; uniform 404; safe 503; malformed-response state. Bundle rows are
keyboard-selectable links with visible focus. Selection navigates to detail
by mouse, keyboard, and visible focus. No raw JSON, prompts, signed URLs,
credentials, service tokens, import action, or public-share action.

## Stage A behavior

Title: `Stage A — Planning artifact`. Notice: `Standalone artifact, not a
Genblaze Run`. The card shows the recorded storyboard summary only. It states
the missing durable relation honestly and never fabricates a Stage A → B0
relation. Stage A is never labeled pipeline execution. The graph-aware
classifier places exactly one node in Stage A for the accepted 16-node
fixture (the storyboard); no unrelated or unsupported node is ever placed in
Stage A.

## Bundle-root context

The `import_bundle` root node is rendered in its own "Bundle context" section
above the stage lanes. It is not coerced into Stage A or any other lane. For
the accepted 16-node fixture this is exactly one node.

## Stage B0 behavior

Title: `Stage B0 — Reference image run`. The B0 Genblaze Run, the B0 Manifest
observation, and the B0-generated reference-image asset are all placed in
Stage B0 (3 nodes for the accepted fixture). The Run card shows recorded
provider/model, root (no parent) state, generated assets summary, and
recorded checks and limitations.

## Stage B1 behavior

Title: `Stage B1 — Keyframe run`. The B1 Genblaze Run, the B1 Manifest, and
the two generated keyframe assets are all placed in Stage B1 (4 nodes for the
accepted fixture). The Run has an explicit parent edge to B0. The parent edge
label includes `Recorded parent — not hash-covered`. Scene membership is
visibly inferred (dashed edge + `Inferred` badge).

## Stage B2 behavior

Title: `Stage B2 — Media run`. The B2 Genblaze Run, the B2 Manifest, and the
generated video and audio assets are all placed in Stage B2 (4 nodes for the
accepted fixture). The Run has an explicit parent edge to B1. Video / TTS /
music steps render in accepted order with provider/model per step. Failed
steps render honestly as missing-by-design. External-input identity
limitations are visible. No raw prompt is rendered by default.

## Stage C behavior

Title: `Stage C — External composition`. Notice: `External ffmpeg
composition, not a Genblaze Run`. Stage C contains the external composition,
the final-delivery asset (with structured B2 reference), and the embedded
Manifest observation when present (3 nodes for the accepted fixture). It
never claims ffmpeg composition is a Genblaze Run.

## Unclassified-node behavior

A node that cannot be assigned to a stage from the accepted node and edge
evidence is rendered in a dedicated "Unclassified recorded nodes" section
OUTSIDE Stage A, never coerced into a lane and never hidden. The accepted
16-node fixture yields ZERO unclassified nodes; this is verified at runtime.

## Highest-risk (worst-outcome) check priority

Each node-card summary surfaces the highest-risk recorded outcome so a
success badge can never conceal a mismatch or invalid Manifest. Priority is
danger > unsupported > warn > neutral > ok; ties resolve to the first
recorded worst outcome. Runtime validation confirms the mismatch fixture's
B2 Run (with both `parsed` and `hash_mismatch` checks) displays a `Hash
mismatch` badge with danger severity, never an ok badge.

## Recorded/inferred behavior

Every relationship shows its evidence class as text: `Recorded` (solid edge)
or `Inferred` (dashed edge). Color is never the only signal. The legend
explicitly distinguishes the two. Every SVG edge carries an accessible
`<title>` describing source, relationship type, target, evidence class, and
hash coverage. The SVG layer is bounded: it draws `<line>` elements only,
behind the cards, with `overflow: hidden`. No full-sentence text label is
rendered on the SVG itself; no text extends outside the stage container; no
line or label obscures node content. The authoritative readable relationship
list is rendered below the lanes. On tablet and mobile the SVG layer is
hidden and replaced by semantic vertical lane connectors plus the textual
relationships list.

## Parent hash-coverage presentation

Every `parent_run` edge shows `Recorded` and `Recorded parent — not
hash-covered`. The UI never uses "verified parent". The exact Manifest 1.5
limitation is preserved.

## Missing / partial / mismatch behavior

- Partial bundles show a `partial_bundle` state badge and a dedicated
  "Partial bundle" panel; missing evidence remains visible.
- Hash mismatch renders `hash_mismatch` severity-danger with the exact copy
  "Recorded and observed hashes did not match."
- Dangling parent edges render with a missing target and a dangling
  marker; they are never upgraded.
- Final-delivery-missing fixtures render without a final asset and without a
  composed-output edge.

## B2-reference presentation

The B2 reference card renders only accepted structured fields: configured
alias, normalized object key, recorded version ID, recorded content length,
recorded content type, recorded ETag, recorded SHA-256, recorded uploaded
timestamp. It never constructs a bucket URL, displays an endpoint URL,
displays a signed URL, exposes account IDs or access keys, exposes arbitrary
upstream metadata, or offers a download action. It is labeled "Recorded B2
archive reference".

## Private Passport behavior

The Passport page renders a camelCase presentation DTO for human reading, but
the copy/download payload is the EXACT validated server Passport object —
`state.payload.passport` — retained by reference and serialized without
mutation. It is never the parsed camelCase DTO, never the auth gateway
envelope, never a camelCase reconstruction, and never enriched with `kind`,
`campaignAccessScope`, UI fields, or browser evidence. Fields are not
reordered, renamed, added, or removed. Runtime validation deep-equals the
clipboard payload against the fixture's exact `passport` object and confirms
it contains `campaign_id`, `bundle_id`, `bundle_fingerprint`,
`truth_boundary`, `nodes`, `edges`, and does NOT contain
`campaignAccessScope`, browser-only `kind`, or camelCase replacements such
as `bundleFingerprint`.

Controls are labeled PRIVATE: `Copy private Passport JSON` and `Download
private Passport JSON`. The downloaded filename is
`proofstudio-private-lineage-passport-<safe-bundle-id>.json`. Temporary
object URLs are revoked immediately after download. No public-share button,
no public URL, no `dangerouslySetInnerHTML`, no browser-generated evidence,
no omitted limitations, no hidden truth boundary.

## Truth-boundary presentation

The exact accepted server truth boundary is rendered verbatim:
"ProofStudio reports what the imported pipeline record states; proof does not
equal truth." The lineage footer additionally surfaces the process-local,
parent-not-hash-covered, provider-as-evidence, Stage A standalone, Stage C
external, byte-verification-may-not-have-occurred, partial/missing, and
"Proof does not equal truth" limitations. The UI never paraphrases into
stronger language.

## Accessibility result

Semantic landmarks; correct heading order; visible focus; keyboard-operable
bundle selection (links) and node selection (buttons with `aria-pressed`);
no hover-only content; status distinctions via text badges plus color;
`aria-live="polite"` on loading and selection updates; accessible SVG edge
labels with `role="img"` and `<title>`; reduced-motion styles; accessible
copy/download status via `role="status"`; Passport tables wrapped in
focusable scroll regions.

## Responsive result

Desktop (1440px): five stage lanes horizontally with one bounded SVG edge
overlay (`overflow: hidden`); the SVG layer contains only `<line>` elements
and accessible `<title>` elements — no full-sentence text labels, no
overflow, no clipping. Tablet (1024px / 768px): lanes wrap to three then two
columns; the SVG overlay hides and a notice points users to the
recorded-relationships list. Mobile (390px): vertical stage timeline with
semantic vertical lane connectors and the textual relationships list; no
compressed five-column graph; Passport tables become controlled scroll
containers; runtime validation confirms `scrollWidth <= clientWidth` (both
390) and that the SVG layer is hidden on mobile.

## Performance result

Stage grouping is `O(N+E)` (single pass plus stable sort by node ID). Edge
preparation is `O(E)`. Node lookup uses a `Map` (no quadratic scan). Derived
stage groups and node maps are memoized. The SVG edge layer is a single
bounded overlay recomputed via `requestAnimationFrame`-throttled measurement
on resize and selection change (no uncontrolled ResizeObserver loop). No
graph-layout animation loop. Stable React keys. No large expanded DOM by
default (progressive disclosure via native `<details>`).

## Fixture inventory

Ten deterministic fixtures under `apps/web/scripts/fixtures/ps041e1/`,
derived from the exact accepted PS-041D runtime response (16 nodes / 16
edges in the full and passport fixtures) with bounded modifications for each
variant:

1. `lineage-list-valid.json` — three bundle summaries (full, partial,
   mismatch).
2. `lineage-detail-full.json` — accepted 16-node / 16-edge graph,
   state=complete (idealized).
3. `lineage-passport-valid.json` — accepted 16-node / 16-edge Passport
   envelope, state=complete.
4. `lineage-detail-partial.json` — accepted 16/16 graph, state=partial_bundle
   (matches the actual accepted runtime response state).
5. `lineage-detail-hash-mismatch.json` — accepted 16/16 graph; the B2 Run
   carries `parsed` + `hash_mismatch` (worst-outcome priority test).
6. `lineage-detail-dangling-parent.json` — accepted 16/16 graph; the
   B1→B0 parent_run edge retargets to `missing_source_id`.
7. `lineage-detail-final-missing.json` — bounded subset (14 nodes / 14
   edges) with final_delivery + embedded_manifest removed.
8. `lineage-detail-unknown-provider.json` — accepted 16/16 graph; the B0
   Run step records `provider=null`.
9. `lineage-list-empty.json` — empty bundle list.
10. `lineage-malformed-response.json` — well-formed envelope with an
    unsupported node kind and unknown source role; MUST be rejected by the
    browser parser.

The full and passport fixtures carry the accepted six node kinds
(`import_bundle`, `standalone_artifact`, `genblaze_run`, `manifest`,
`asset`, `external_composition`) and the eight accepted edge kinds present
in the accepted response (`parent_run`, `generated_asset`, `storyboard_for`,
`scene_member`, `composition_input`, `composed_output`, `manifest_for`,
`embedded_manifest`). `external_input` only appears in bundles that record
one; the accepted fixture does not. Every node id and edge id is unique;
every bundle `node_ids`/`edge_ids` set matches its graph. All ten were
validated against the browser parser (positive cases parse; malformed
rejects). They contain no credential, no signed URL, no real account email,
no production identifier, no raw prompt, and no live B2 data. The accepted
backend PS-041D fixture is unchanged.

## Golden public Passport regression

The golden public Passport route helper `getPublicPassportRunId` and the
`/passport/:id` dispatch in `App.tsx` are unchanged. The
`smoke:private-proof-access` smoke still verifies that the public Passport
rejects arbitrary IDs before any API call. The PS-041E1 smoke additionally
verifies the golden route is preserved.

## Provider / live-B2 calls

Zero. The slice performs no provider call and no live B2 read in source, in
fixtures, in smoke, in runtime validation, or in screenshot capture.
Screenshot capture and runtime validation use deterministic local fixture
interception only.

## Screenshot evidence

Ten screenshots under `/tmp/proofstudio-ps041e-screenshots/`:

1. `01-dashboard-lineage-entry.png` — dashboard lineage launcher.
2. `02-lineage-bundle-list.png` — private bundle list (three bundles).
3. `03-lineage-full-a-b0-b1-b2-c.png` — accepted 16-node graph; stage
   headers A/B0/B1/B2/C; Stage A contains only the storyboard (verified).
4. `04-recorded-vs-inferred.png` — bounded SVG layer over the stage grid;
   zero SVG text labels, zero overflow (verified).
5. `05-partial-missing-evidence.png` — partial_bundle state panel.
6. `06-hash-check-details.png` — B2 Run with `hash_mismatch` selected; the
   selected panel visibly contains `Hash mismatch` with a danger-severity
   badge (verified).
7. `07-structured-b2-reference.png` — final-delivery B2 reference selected;
   structured fields only, no URL, no signed token (verified).
8. `08-private-portable-passport.png` — PRIVATE Passport controls;
   copy/download serializes the exact raw server Passport (verified by
   clipboard deep-equal).
9. `09-mobile-lineage.png` — 390px mobile; no horizontal overflow; SVG layer
   hidden (verified `scrollWidth <= clientWidth`).
10. `10-safe-dependency-error.png` — HTTP 503; visible
    `Proof dependency unavailable`; no fixture fallback (verified).

Manual review confirms no credentials, raw prompts, URLs, real emails, or
public-share copy appear in any screenshot. Screenshots are not edited.

## Known limitations

- Imported lineage is a process-local record, not a live pipeline
  observation.
- Manifest `parent_run_id` is recorded but not canonical-hash-covered.
- Provider/model values are recorded evidence only.
- Stage A is standalone; Stage C is external composition.
- Byte verification may not have occurred for every recorded reference.
- Partial or missing evidence stays visible and is never upgraded.
- PS-041E2 sponsor evidence is not addressed by this slice.
- Screenshot capture depends on Playwright being installed in the capture
  environment; the capture script adds no new dependency and exits with a
  clear diagnostic if Playwright is unavailable.
