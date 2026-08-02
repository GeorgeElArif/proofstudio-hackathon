# PS-041E1 — Private Dynamic Lineage UI

Status: implementation slice. Web only. Accepted base: `origin/accepted/proofstudio` at `b345497868ccbdffb1f56450cd0d40c375f26cb4`.

PS-041E1 implements the private, read-only, dynamic lineage UI over the
accepted PS-041D auth-server gateway contract. It is built on the accepted
PS-041E0 Genblaze v0.5.0 upgrade base and uses no new web dependency.

## 1. Scope

- Private read-only lineage UI;
- auth-server gateway reads only (`credentials: "include"`);
- deterministic bundle list;
- dynamic Stage A / B0 / B1 / B2 / C detail;
- DOM/CSS stage lanes with one bounded SVG edge overlay;
- private portable Passport presentation;
- no graph/layout dependency;
- no backend redesign;
- no live B2;
- no provider call;
- no imported public Passport.

## 2. Accepted API dependencies

PS-041E1 reads only the accepted PS-041D private gateway routes:

- `GET /account/campaigns/{campaignId}/lineage`
- `GET /account/campaigns/{campaignId}/lineage/{bundleId}`
- `GET /account/campaigns/{campaignId}/lineage/{bundleId}/passport`

The gateway derives identity from Better Auth, checks active `proof.read`
mapping before calling FastAPI, allows owner / reviewer / viewer, rejects
caller-identity and evidence-query scopes, recursively validates every nested
field, contains redirects, and maps absent / revoked / cross-account to a
uniform 404 and dependency failures to a safe 503. PS-041E1 changes none of
this. No auth-server or FastAPI source is modified.

## 3. Private routes

The existing path-prefix dispatcher in `apps/web/src/App.tsx` gains three
private routes, matched in order so longer paths do not collide with the list
dispatcher:

- `/account/campaigns/:campaignId/lineage`
- `/account/campaigns/:campaignId/lineage/:bundleId`
- `/account/campaigns/:campaignId/lineage/:bundleId/passport`

IDs are decoded safely. Malformed percent-encoding (lone surrogates or invalid
UTF-8 sequences), or an empty decoded id, produces an explicit `lineage-invalid`
route variant that renders a STATIC `MalformedLineageReferencePage` — a page
that invokes NO data hook, emits ZERO gateway reads, and never produces a
request containing `/campaigns//`. This is verified at runtime by the lineage
UI runtime validation script (zero reads for malformed list, detail, and
passport routes). The golden public Passport route (`/passport/:id`) and all
existing proof-room routes remain unchanged. No public imported Passport route
is created.

## 4. Data bounds

The UI is designed for the accepted V1 bounds:

- at most 50 bundles;
- at most 512 nodes;
- at most 64 edges;
- 6 node kinds;
- 9 edge kinds;
- 15 check outcomes.

Stage grouping is `O(N+E)`, edge preparation is `O(E)`, node lookup uses a
`Map`, and the SVG edge overlay is a single bounded layer. No list
virtualization is required at these limits.

## 5. Component architecture

`apps/web/src/BundleLineage.tsx` exposes three route-level components:

- `BundleLineageListPage`
- `BundleLineageDetailPage`
- `PortableLineagePassportPage`

Supporting presentation components are small and focused:

- `LineageShell`, `LineageTruthBoundary`, `DashboardBackLink`;
- `LineageLoading`, `LineageStatePanel`;
- `LineageListBody`, `BundleListRow`;
- `LineageDetailReady`, `LineageStageLanes`, `LineageStage`,
  `LineageNodeCard`, `LineageEdgeLayer`, `LineageEdgeRow`;
- `LineageSelectedNodePanel`, `RunStepList`, `StepRow`;
- `CheckBadge`, `CheckBadgeList`, `LineageLimitations`, `B2ReferenceCard`;
- `PortablePassportBody`, `PassportNodesTable`, `PassportEdgesTable`,
  `FinalCompositionRelation`.

`apps/web/src/bundleLineage.ts` owns the strict TypeScript types, the
bounded runtime parser, deterministic stage grouping, deterministic node/edge
ordering, display-safe string normalization, safe labels, severity mapping,
limitation classification, provider/model formatting, and structured B2
reference formatting.

## 6. Stage semantics

The fixed stage order is A → B0 → B1 → B2 → C. Stage assignment is graph-aware:
`classifyNodeStages(nodes, edges)` builds adjacency Maps in O(N+E) once before
render and assigns each node to exactly one lane, the dedicated bundle-root
context, or a dedicated "Unclassified recorded nodes" section. Only accepted
node kinds, edge kinds, source roles, and run stages are used — no
relationship is ever invented.

- The `import_bundle` root node is rendered in its own **Bundle context**
  section, outside the A/B0/B1/B2/C lanes.
- Stage A is a standalone planning artifact (storyboard). It is not a Genblaze
  Run, has no durable recorded relation to B0/B1/B2/C, and the UI states this
  honestly. Stage A never contains an unrelated, unsupported node.
- Stage B0 is the reference-image Genblaze Run. It is the lineage root. The
  B0 Manifest observation (source role `stage_b0_manifest`, kind `manifest`)
  is placed in Stage B0 alongside the Run.
- Stage B1 is the keyframe Genblaze Run. It has an explicit recorded parent
  edge to B0. The B1 Manifest and the two generated keyframe assets
  (`asset-keyframe-001/002`) inherit Stage B1 via the accepted
  `generated_asset` edge from the B1 Run.
- Stage B2 is the media Genblaze Run. It has an explicit recorded parent edge
  to B1. The B2 Manifest, generated video asset, and generated audio asset
  inherit Stage B2 via the accepted `generated_asset` edge from the B2 Run.
  Video / TTS / music steps render in accepted order, including failed steps,
  which are shown honestly as missing-by-design.
- Stage C is an external ffmpeg composition, plus the final-delivery asset and
  the embedded Manifest observation when present. None of these are Genblaze
  Runs. The UI states this honestly and never labels ffmpeg composition as
  pipeline execution.
- A generated asset whose stage cannot be derived from a recorded
  `generated_asset` edge, or an external input without a recorded
  `external_input` edge, is **not** coerced into a stage. It is rendered in
  the dedicated "Unclassified recorded nodes" section OUTSIDE Stage A. The
  accepted 16-node fixture has zero unclassified nodes; this section exists
  to fail-closed for any future bundle that records an orphan node.

Stage distribution for the accepted 16-node fixture is A:1, B0:3, B1:4, B2:4,
C:3, plus the import_bundle root in its own context section (total 16).
Hidden closed disclosures (e.g. the unclassified section) are never used as
SVG geometry anchors.

## 7. Recorded versus inferred

Every relationship identifies its evidence class with text, not color alone:

- Recorded relationships use a solid edge and a `Recorded` textual badge.
- Inferred relationships use a dashed edge and an `Inferred` textual badge.

The SVG edge layer is bounded: it draws only solid/dashed `<line>` elements
behind the cards (z-index 0, `overflow: hidden`), with one accessible
`<title>` per edge carrying the full relationship sentence. No full-sentence
text label is rendered on the SVG itself; no text may extend outside the
stage container; no line or label may obscure node content. The authoritative
readable relationship list is rendered as a textual list below the lanes.
On tablet and mobile the SVG layer is hidden and replaced by semantic
vertical lane connectors (left border) plus the textual relationships list.

## 8. Node-card highest-risk (worst-outcome) priority

Each node card surfaces exactly one summary badge — the highest-risk recorded
outcome — so a success badge can never conceal a `hash_mismatch` or
`manifest_invalid`. The deterministic priority is:

1. danger (`hash_mismatch`, `manifest_invalid`, `unsupported_schema`,
   `unavailable`)
2. unsupported
3. warn (`hash_present`, `object_missing`, `partial_bundle`,
   `manifest_output_hashes_declared`, `relationship_inferred`)
4. neutral (`not_checked`)
5. ok (`parsed`, `recorded`, `manifest_hash_verified`, `hash_verified`,
   `relationship_recorded`)

Ties resolve to the first recorded worst outcome (stable). This is implemented
by `worstCheck(checks)` in `apps/web/src/bundleLineage.ts` and exercised by
the lineage UI runtime validation: the mismatch fixture's B2 Run (with both
`parsed` and `hash_mismatch` checks) surfaces `Hash mismatch` with a
danger-severity badge, never a success badge.

## 9. Parent hash-coverage limitation

Manifest 1.5 records `parent_run_id` but excludes it from the canonical hash.
Every parent edge therefore renders two explicit badges:

- `Recorded`
- `Recorded parent — not hash-covered`

The UI never uses "verified parent".

## 10. B2 reference handling

B2 references render only accepted structured fields from `B2ObjectReference`:

- configured alias;
- normalized object key;
- recorded version ID;
- recorded content length;
- recorded content type;
- recorded ETag;
- recorded SHA-256;
- recorded uploaded timestamp.

The UI never constructs a bucket URL, never displays an endpoint URL, never
displays a signed URL, never exposes account IDs or access keys, never
displays arbitrary upstream metadata, and never offers a download action for
B2 objects. The reference is labeled "Recorded B2 archive reference", never
"Verified immutable B2 object".

## 11. Private portable Passport

The Passport page renders a camelCase presentation DTO for human reading, but
the copy/download payload is the EXACT validated server Passport object —
`state.payload.passport` — retained by reference and serialized without
mutation. It is never the parsed camelCase DTO, never the auth gateway
envelope, never a camelCase reconstruction, and never enriched with `kind`,
`campaignAccessScope`, UI fields, or browser evidence. Fields are not
reordered, renamed, added, or removed. The runtime validation script
deep-equals the clipboard payload against the fixture's exact `passport`
object.

The Passport page renders the accepted server Passport only:

- private status header;
- campaign and bundle identifiers;
- Passport schema and source revision;
- recorded nodes table;
- recorded edges table;
- checks;
- limitations;
- structured B2 references;
- final composition relation;
- the exact accepted truth boundary.

Controls are labeled `PRIVATE`:

- Copy private Passport JSON;
- Download private Passport JSON.

The downloaded filename is
`proofstudio-private-lineage-passport-<safe-bundle-id>.json`. Temporary
object URLs are revoked immediately after download. The page never creates a
public-share button or public URL, never uses `dangerouslySetInnerHTML`, and
never omits limitations or hides the truth boundary.

## 12. Accessibility

- semantic `main` / `nav` / `section` landmarks and correct heading order;
- visible focus and keyboard-operable bundle and node selection;
- no hover-only content;
- status distinctions rely on text badges, not color alone;
- `aria-live="polite"` for loading and result updates;
- accessible relationship descriptions on every SVG edge;
- reduced-motion styles;
- accessible copy/download status;
- buttons for actions and links for navigation.

## 13. Responsive behavior

Target widths:

- 1440px desktop: five stage lanes may appear horizontally when readable;
  edges remain visible; selected-node detail remains accessible.
- 1024px / 768px tablet: lanes wrap or stack; labels remain visible; no
  card/edge overlap.
- 390px mobile: vertical stage timeline; no compressed five-column graph;
  the SVG edge layer is hidden and replaced by semantic vertical lane
  connectors plus the textual relationships list; Passport tables become
  controlled scroll containers.

The UI never hides required evidence on mobile and never produces horizontal
page overflow. Runtime validation confirms `scrollWidth <= clientWidth` at
390px and that the SVG layer is hidden on mobile.

## 14. Performance

At the accepted V1 bounds, the implementation is `O(N+E)`:

- one pass for stage grouping;
- one pass for edge preparation;
- `Map`-based node lookup (no quadratic scan);
- memoized derived stage groups;
- deterministic sort order;
- stable React keys;
- one bounded SVG edge layer;
- no graph-layout animation loop;
- no uncontrolled ResizeObserver loop;
- no large expanded DOM by default.

## 15. Security boundaries

- relative auth-server gateway routes only;
- `credentials: "include"`;
- `encodeURIComponent` for campaign and bundle IDs;
- no direct FastAPI URL;
- no `Authorization`, service, or operator header;
- no `localStorage` / `sessionStorage` auth;
- no retry loop;
- no fixture fallback after an API failure;
- 401 / 404 / 503 distinctions preserved;
- no raw JSON rendering;
- no `dangerouslySetInnerHTML`;
- no signed-URL construction;
- no public imported Passport;
- no import / write / operator controls.

## 16. Screenshots and runtime validation

`apps/web/scripts/capture-ps041e-screenshots.mjs` captures ten screenshots
to `/tmp/proofstudio-ps041e-screenshots/` using the repository-established
Playwright tooling (Node or Python engine) with deterministic fixture
interception. It makes no provider call, no live B2 read, no real-session
call, and no mutation. Both engines consume ONE explicit CAPTURE_PLAN that
pins viewport, URL, mocked response state, node-selection action, target
element/full-page, and output filename for every shot. The capture script:

- removes stale screenshots before capturing;
- creates the temporary helper directory explicitly under `/tmp/opencode/`;
- registers exactly one route handler per page (never duplicates);
- fails if any expected screenshot was not recreated;
- verifies all ten files are nonempty and distinct in size where distinct
  states are required (full graph vs. Hash mismatch vs. dependency error);
- screenshot 06 loads the hash-mismatch fixture, selects the B2 Run
  containing `hash_mismatch`, and captures a visible `Hash mismatch` badge
  with mismatch detail;
- screenshot 07 selects the final-delivery node and captures the structured
  B2 reference (no URL, no signed token);
- screenshot 10 intercepts the exact lineage detail request with HTTP 503,
  renders `Proof dependency unavailable`, proves no fixture fallback, and
  never uses final-missing success content.

`apps/web/scripts/smoke-lineage-ui-runtime.mjs` extends the source-contract
smoke with runtime behavior checks (check-only, deterministic interception,
no new dependency): malformed routes issue zero gateway reads; the full
fixture renders 16 nodes / 16 edges; no accepted node is placed under Stage A
unsupported; the mismatch node card presents the mismatch; HTTP 503 produces
the dependency-unavailable state; Passport serialization deep-equals the
original server Passport; no direct FastAPI request; no provider/B2 request;
no public imported Passport route.

The required capture viewports are 1440x1000 (desktop) and 390x844 (mobile).

## 17. Tests

- `apps/web/scripts/smoke-lineage-ui.mjs` is a check-only source-contract
  smoke that verifies all three routes plus the `lineage-invalid` malformed
  variant, the authorized client usage, `credentials: "include"`, no direct
  FastAPI URL, no operator/import action, no service token, no raw JSON
  `<pre>`, no `dangerouslySetInnerHTML`, no signed-URL construction, no
  public imported Passport, Stage A standalone copy, distinct B0/B1/B2,
  Stage C external copy, recorded/inferred labels, the parent not-hash-covered
  copy, the exact truth boundary, the PRIVATE Passport copy/download labels
  and the exact raw server Passport reference (`state.payload.passport`),
  mobile and reduced-motion styles, no graph dependency, the unchanged golden
  public Passport route, the dashboard launcher, the deterministic fixtures
  (16 nodes / 16 edges, unique ids, accepted six node kinds and eight edge
  kinds present), graph-aware stage assignment (`classifyNodeStages`,
  `buildStageLayout`), the worst-outcome check priority, the bounded SVG
  edge layer (no full-sentence text labels), and the malformed fixture
  rejection.
- `apps/web/scripts/smoke-lineage-ui-runtime.mjs` is a check-only runtime
  behavior validation (described in §16).
- Existing web smokes remain green (auth-client, dashboard-contract,
  dashboard-ui, private-proof-access, dashboard-account-campaigns).
- The deterministic fixtures under `apps/web/scripts/fixtures/ps041e1/` are
  derived from the exact accepted PS-041D runtime response (16 nodes / 16
  edges) with bounded modifications for each variant; the malformed fixture
  is structurally invalid and is rejected by the browser parser.

## 18. Known limitations

- This is a process-local imported record view, not a live pipeline
  observation.
- Manifest `parent_run_id` is recorded but not canonical-hash-covered.
- Provider and model values are recorded evidence only.
- Stage A is standalone; Stage C is external composition.
- Byte verification may not have occurred for every recorded reference.
- Partial or missing evidence stays visible and is never upgraded.
- PS-041E2 sponsor evidence is not addressed by this slice.
- No live B2 access and no provider call occurs.
- Screenshot capture depends on Playwright being installed in the capture
  environment; the script adds no new dependency and prints a clear
  diagnostic if Playwright is unavailable.

## 19. Truth boundary

> ProofStudio reports what the imported pipeline record states; proof does not
> equal truth.
