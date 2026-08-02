// PS-041E1 — Private Dynamic Lineage UI source-contract smoke (check-only).
//
// Inspects source/build contracts only. Performs no network call, no provider
// call, no live B2 read, and writes no evidence. Mirrors the established
// check-only style of the other PS-041 web smokes.

import { readFileSync, readdirSync } from "node:fs";
import { resolve } from "node:path";

const app = readFileSync(resolve("src/App.tsx"), "utf8");
const client = readFileSync(resolve("src/authorizedProofClient.ts"), "utf8");
const lineageClient = readFileSync(resolve("src/bundleLineage.ts"), "utf8");
const bundleLineage = readFileSync(resolve("src/BundleLineage.tsx"), "utf8");
const dashboard = readFileSync(resolve("src/dashboard/DashboardSurface.tsx"), "utf8");
const publicPage = readFileSync(resolve("src/PublicPassportPage.tsx"), "utf8");
const styles = readFileSync(resolve("src/styles.css"), "utf8");
const pkg = JSON.parse(readFileSync(resolve("package.json"), "utf8"));

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

// --- 1. All three private routes registered in route-correct order ----------
assert(app.includes("getPrivateLineagePath"), "App must expose a private lineage path matcher");
assert(app.includes('"lineage-passport"'), "App must dispatch lineage-passport route");
assert(app.includes('"lineage-detail"'), "App must dispatch lineage-detail route");
assert(app.includes('"lineage-list"'), "App must dispatch lineage-list route");
assert(app.includes('"lineage-invalid"'), "App must dispatch lineage-invalid route (static malformed-reference page, zero reads)");
assert(app.includes("MalformedLineageReferencePage"), "App must render MalformedLineageReferencePage for malformed route");
// Within the matcher function, passport must be matched before detail and list.
const matcherStart = app.indexOf("function getPrivateLineagePath");
const matcherClose = app.indexOf("return null;", matcherStart);
const matcherBody = app.slice(matcherStart, matcherClose);
const ifPassport = matcherBody.indexOf("if (passport)");
const ifDetail = matcherBody.indexOf("if (detail)");
const ifList = matcherBody.indexOf("if (list)");
assert(ifPassport !== -1 && ifDetail !== -1 && ifList !== -1, "matcher must contain passport/detail/list branches");
assert(ifPassport < ifDetail && ifDetail < ifList, "matcher order: passport → detail → list");
assert(app.includes("decodeURIComponent"), "route IDs must be decoded safely");
// Malformed route produces the explicit lineage-invalid variant (never a fallback
// that would invoke a data hook with an empty campaign id).
assert(matcherBody.includes('{ kind: "lineage-invalid" }'), "matcher must return lineage-invalid on decode failure or empty id");

// --- 2. All reads use authorizedProofClient ----------------------------------
assert(client.includes("fetchCampaignLineage") && client.includes("fetchCampaignLineageBundle") && client.includes("fetchCampaignLineagePassport"), "client must export the three lineage readers");
assert(bundleLineage.includes('from "./authorizedProofClient"'), "BundleLineage must import the authorized client");
assert(bundleLineage.includes("fetchCampaignLineage(") && bundleLineage.includes("fetchCampaignLineageBundle(") && bundleLineage.includes("fetchCampaignLineagePassport("), "BundleLineage must call the three readers");

// --- 3. credentials: include present -----------------------------------------
assert(client.includes('credentials: "include"'), "private client must include credentials");

// --- 4. No direct FastAPI URL -------------------------------------------------
assert(!client.includes("localhost:8000") && !client.includes("127.0.0.1:8000"), "no direct FastAPI URL in client");
assert(!bundleLineage.includes("localhost:8000") && !bundleLineage.includes("127.0.0.1:8000"), "no direct FastAPI URL in BundleLineage");
// All fetch paths are relative gateway routes only.
assert(client.includes("/account/campaigns/"), "client must use relative /account gateway routes");

// --- 5. No operator/import action / service token ----------------------------
assert(!bundleLineage.includes("genblaze-bundles"), "no operator import mutation surface in UI");
assert(!bundleLineage.includes("X-ProofStudio-Import-Token") && !client.includes("X-ProofStudio-Import-Token"), "no operator token in browser code");
assert(!bundleLineage.includes("INTERNAL_SERVICE_TOKEN") && !client.includes("INTERNAL_SERVICE_TOKEN"), "no service token in browser code");
assert(!bundleLineage.includes("X-ProofStudio-Internal-Token") && !client.includes("X-ProofStudio-Internal-Token"), "no internal service header in browser code");

// --- 6. No raw JSON <pre> in new lineage UI ----------------------------------
// The lineage UI must not dump raw arbitrary JSON in a <pre>. We allow the
// accepted Passport JSON inside a details/summary only via the copy/download
// controls; never a <pre> dump.
const preMatches = bundleLineage.match(/<pre[^>]*>/g) ?? [];
assert(preMatches.length === 0, "lineage UI must not render raw JSON <pre> dumps");

// --- 7. No dangerouslySetInnerHTML -------------------------------------------
assert(!bundleLineage.includes("dangerouslySetInnerHTML"), "lineage UI must not use dangerouslySetInnerHTML");

// --- 8. No signed URL construction -------------------------------------------
assert(!bundleLineage.includes("X-Amz-") && !bundleLineage.includes("AWSAccessKeyId") && !bundleLineage.includes("signed_url"), "no signed URL tokens in lineage UI");
// b2ReferenceFields must not construct a URL — it only emits structured fields.
assert(bundleLineage.includes("b2ReferenceFields"), "B2 references must use the structured fields helper");
// The B2 fields helper must never concatenate a scheme or build a URL string.
const b2HelperStart = lineageClient.indexOf("function b2ReferenceFields");
const b2HelperEnd = lineageClient.indexOf("\n}\n", b2HelperStart);
const b2Helper = lineageClient.slice(b2HelperStart, b2HelperEnd);
assert(!b2Helper.includes('"https://') && !b2Helper.includes('"http://') && !b2Helper.includes("`https://") && !b2Helper.includes("`http://") && !b2Helper.includes("b2://"), "B2 fields helper must not construct URLs");

// --- 9. No public imported Passport ------------------------------------------
assert(!bundleLineage.includes("/passport/"), "no public imported Passport route (the golden /passport/:id stays separate)");

// --- 10. Stage A standalone copy ---------------------------------------------
assert(bundleLineage.includes("Stage A — Planning artifact"), "Stage A title must be present");
assert(bundleLineage.includes("Standalone artifact, not a Genblaze Run"), "Stage A standalone notice must be present");

// --- 11. B0/B1/B2 distinct ---------------------------------------------------
assert(bundleLineage.includes("Stage B0 — Reference image run"), "B0 title present");
assert(bundleLineage.includes("Stage B1 — Keyframe run"), "B1 title present");
assert(bundleLineage.includes("Stage B2 — Media run"), "B2 title present");

// --- 12. Stage C external copy -----------------------------------------------
assert(bundleLineage.includes("Stage C — External composition"), "Stage C title present");
assert(bundleLineage.includes("External ffmpeg composition, not a Genblaze Run"), "Stage C external notice present");

// --- 13. Recorded/inferred labels present ------------------------------------
assert(bundleLineage.includes("Recorded relationship") && bundleLineage.includes("Inferred relationship"), "edge legend must show recorded/inferred");
assert(styles.includes("lineage-edge-recorded") && styles.includes("lineage-edge-inferred"), "edge CSS must distinguish recorded/inferred");
assert(styles.includes("lineage-legend-recorded") && styles.includes("lineage-legend-inferred"), "legend CSS must distinguish recorded/inferred");

// --- 14. Parent not-hash-covered copy present --------------------------------
assert(bundleLineage.includes("Recorded parent — not hash-covered"), "parent not-hash-covered copy present");

// --- 15. Exact truth-boundary copy present -----------------------------------
assert(lineageClient.includes("ProofStudio reports what the imported pipeline record states; proof does not equal truth."), "exact server truth boundary present");
assert((bundleLineage + lineageClient).includes("ProofStudio shows what the recorded pipeline evidence contains. Proof does not equal truth."), "lineage truth boundary present (constant or literal)");

// --- 16. PRIVATE Passport copy/download labels -------------------------------
assert(bundleLineage.includes("PRIVATE Passport controls"), "PRIVATE passport controls heading present");
assert(bundleLineage.includes("Copy private Passport JSON"), "copy label present");
assert(bundleLineage.includes("Download private Passport JSON"), "download label present");
// The copy/download payload MUST be the exact validated server Passport object
// (state.payload.passport), not the parsed camelCase DTO nor the envelope.
assert(bundleLineage.includes("state.payload.passport"), "raw server Passport object reference present");
assert(bundleLineage.includes("rawPassportObject"), "rawPassportObject retained separately for serialization");
assert(!bundleLineage.includes("JSON.stringify(result.data"), "must not serialize the camelCase DTO for copy/download");

// --- 17. Mobile fallback styles present --------------------------------------
assert(styles.includes("@media (max-width: 760px)"), "mobile fallback present");
assert(styles.includes("@media (max-width: 390px)"), "narrow mobile fallback present");

// --- 18. Reduced-motion styles present ---------------------------------------
assert(styles.includes("prefers-reduced-motion"), "reduced-motion styles present");

// --- 19. No graph dependency added -------------------------------------------
const deps = Object.keys(pkg.dependencies ?? {});
assert(!deps.includes("reactflow") && !deps.includes("@xyflow/react") && !deps.includes("cytoscape") && !deps.includes("d3") && !deps.includes("elkjs") && !deps.includes("vis-network"), "no graph/layout dependency added");
assert(pkg.dependencies.react === "^18.3.1", "React pin unchanged");

// --- 20. Golden public Passport route unchanged ------------------------------
assert(publicPage.includes("getPublicPassportRunId"), "golden public Passport route helper preserved");
assert(app.includes("getPublicPassportRunId"), "App still dispatches golden public Passport route");
assert(app.includes("/passport/"), "golden /passport/:id route path preserved");

// --- 21. Dashboard launcher present with the accepted label ------------------
assert(dashboard.includes("Open recorded lineage"), "dashboard launcher label present");
assert(dashboard.includes("dashboard-lineage-launcher"), "dashboard launcher class present");
assert(!dashboard.includes("Verify authenticity") && !dashboard.includes("Complete provenance") && !dashboard.includes("Certified ownership") && !dashboard.includes("View truth") && !dashboard.includes("Public Passport"), "dashboard must not use forbidden launcher labels");

// --- 22. Deterministic fixtures present --------------------------------------
const fixtures = readdirSync(resolve("scripts/fixtures/ps041e1")).filter((f) => f.endsWith(".json"));
const required = [
  "lineage-list-valid.json",
  "lineage-detail-full.json",
  "lineage-passport-valid.json",
  "lineage-detail-partial.json",
  "lineage-detail-hash-mismatch.json",
  "lineage-detail-dangling-parent.json",
  "lineage-detail-final-missing.json",
  "lineage-detail-unknown-provider.json",
  "lineage-list-empty.json",
  "lineage-malformed-response.json",
];
for (const name of required) assert(fixtures.includes(name), `required fixture missing: ${name}`);
for (const name of fixtures) {
  const text = readFileSync(resolve("scripts/fixtures/ps041e1", name), "utf8");
  assert(!text.includes("X-Amz-") && !text.includes("AWSAccessKeyId"), `fixture ${name} must not contain signed URL tokens`);
  assert(!text.toLowerCase().includes("password") && !text.includes("DATABASE_URL"), `fixture ${name} must not contain secret markers`);
  assert(!text.includes("@"), `fixture ${name} must not contain email-like markers`);
  assert(!text.includes("raw_prompt") && !text.includes("prompt"), `fixture ${name} must not contain raw prompt fields`);
}
// Full + Passport fixtures carry the accepted 16-node / 16-edge graph.
const detailFull = JSON.parse(readFileSync(resolve("scripts/fixtures/ps041e1", "lineage-detail-full.json"), "utf8"));
const passportValid = JSON.parse(readFileSync(resolve("scripts/fixtures/ps041e1", "lineage-passport-valid.json"), "utf8"));
assert(detailFull.lineage.nodes.length === 16, "full detail fixture must have 16 nodes");
assert(detailFull.lineage.edges.length === 16, "full detail fixture must have 16 edges");
assert(passportValid.passport.nodes.length === 16, "passport fixture must have 16 nodes");
assert(passportValid.passport.edges.length === 16, "passport fixture must have 16 edges");
// Unique node and edge ids, and bundle id sets match the graph.
const fullNodeIds = new Set(detailFull.lineage.nodes.map((n) => n.node_id));
const fullEdgeIds = new Set(detailFull.lineage.edges.map((e) => e.edge_id));
assert(fullNodeIds.size === 16, "full detail fixture node ids unique");
assert(fullEdgeIds.size === 16, "full detail fixture edge ids unique");
assert(new Set(detailFull.lineage.bundle.node_ids).size === 16, "bundle.node_ids length 16");
assert(new Set(detailFull.lineage.bundle.edge_ids).size === 16, "bundle.edge_ids length 16");
for (const id of detailFull.lineage.bundle.node_ids) assert(fullNodeIds.has(id), "bundle.node_ids ⊆ graph");
for (const id of detailFull.lineage.bundle.edge_ids) assert(fullEdgeIds.has(id), "bundle.edge_ids ⊆ graph");
// The accepted six node kinds and at least the eight accepted edge kinds
// present in the accepted response (external_input only appears when the
// accepted bundle records one).
const nodeKinds = new Set(detailFull.lineage.nodes.map((n) => n.kind));
for (const k of ["import_bundle", "standalone_artifact", "genblaze_run", "manifest", "asset", "external_composition"]) {
  assert(nodeKinds.has(k), `accepted node kind present: ${k}`);
}
const edgeKinds = new Set(detailFull.lineage.edges.map((e) => e.kind));
for (const k of ["parent_run", "generated_asset", "storyboard_for", "scene_member", "composition_input", "composed_output", "manifest_for", "embedded_manifest"]) {
  assert(edgeKinds.has(k), `accepted edge kind present: ${k}`);
}
// Malformed fixture must declare a structurally invalid payload.
const malformedText = readFileSync(resolve("scripts/fixtures/ps041e1", "lineage-malformed-response.json"), "utf8");
assert(malformedText.includes("unsupported_kind_value"), "malformed fixture must carry an unsupported kind for parser rejection");

// --- 23. Graph-aware stage assignment ----------------------------------------
assert(lineageClient.includes("classifyNodeStages"), "graph-aware classifyNodeStages helper present");
assert(lineageClient.includes("buildStageLayout"), "buildStageLayout helper present");
assert(lineageClient.includes("manifestToRunStage"), "manifest stage derived from manifest_for edge");
assert(lineageClient.includes("generatedAssetToRunStage"), "generated asset stage derived from generated_asset edge");
assert(lineageClient.includes("externalInputToRunStage"), "external input stage derived from external_input edge");
assert(bundleLineage.includes("Unclassified recorded nodes"), "dedicated unclassified section copy present");
assert(bundleLineage.includes("Bundle context"), "dedicated bundle-root context copy present");

// --- 24. Highest-risk check priority -----------------------------------------
assert(lineageClient.includes("PRIORITY_ORDER"), "explicit priority order constant present");
assert(lineageClient.includes("danger") && lineageClient.includes("unsupported") && lineageClient.includes("warn") && lineageClient.includes("neutral") && lineageClient.includes("ok"), "all five priority levels present");
assert(lineageClient.includes("worstCheck"), "worstCheck helper present");
assert(bundleLineage.includes("Highest-risk priority") || bundleLineage.includes("worst recorded"), "check priority comment present in node card logic");

// --- 25. SVG edge layer is bounded -------------------------------------------
assert(!bundleLineage.includes('className="lineage-edge-text"') && !bundleLineage.includes('<text x={midX}'), "SVG layer must not emit long midpoint text labels");
assert(!bundleLineage.includes("lineage-edge-marker-text"), "SVG layer must not emit marker text (lines + accessible title only)");
assert(bundleLineage.includes("authoritative readable presentation") || bundleLineage.includes("authoritative textual relationship list"), "SVG layer defers to the authoritative textual list");
assert(styles.includes("overflow: hidden"), "SVG layer is bounded (overflow hidden)");

console.log(JSON.stringify({
  ok: true,
  slice: "PS-041E1",
  checks: {
    routes_registered: "pass",
    route_order: "pass",
    authorized_client_used: "pass",
    credentials_include: "pass",
    no_direct_fastapi_url: "pass",
    no_operator_or_service_token: "pass",
    no_raw_json_pre: "pass",
    no_dangerously_set_inner_html: "pass",
    no_signed_url: "pass",
    no_public_imported_passport: "pass",
    stage_a_standalone: "pass",
    stages_b0_b1_b2_distinct: "pass",
    stage_c_external: "pass",
    recorded_inferred_labels: "pass",
    parent_not_hash_covered: "pass",
    exact_truth_boundary: "pass",
    private_passport_labels: "pass",
    mobile_fallback: "pass",
    reduced_motion: "pass",
    no_graph_dependency: "pass",
    golden_public_passport_unchanged: "pass",
    dashboard_launcher: "pass",
    deterministic_fixtures: "pass",
    fixtures_16_node_16_edge: "pass",
    graph_stage_assignment: "pass",
    check_priority: "pass",
    svg_edge_layer_bounded: "pass",
    malformed_route_invalid: "pass",
    exact_raw_passport_serialized: "pass",
  },
}));
