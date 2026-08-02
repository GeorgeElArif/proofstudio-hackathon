"""PS-041D provider-neutral lineage validation and deterministic ordering."""

from __future__ import annotations

from collections import defaultdict

from proofstudio.api.imported_bundle import EdgeKind, EvidenceClass, ImportedLineageEdge, ImportedLineageNode, NodeKind


class LineageValidationError(ValueError):
    pass


_ALLOWED: dict[EdgeKind, set[tuple[NodeKind, NodeKind]]] = {
    EdgeKind.PARENT_RUN: {(NodeKind.GENBLAZE_RUN, NodeKind.GENBLAZE_RUN)},
    EdgeKind.GENERATED_ASSET: {(NodeKind.GENBLAZE_RUN, NodeKind.ASSET)},
    EdgeKind.EXTERNAL_INPUT: {(NodeKind.ASSET, NodeKind.GENBLAZE_RUN)},
    EdgeKind.STORYBOARD_FOR: {(NodeKind.STANDALONE_ARTIFACT, NodeKind.GENBLAZE_RUN)},
    EdgeKind.SCENE_MEMBER: {(NodeKind.STANDALONE_ARTIFACT, NodeKind.GENBLAZE_RUN), (NodeKind.ASSET, NodeKind.GENBLAZE_RUN)},
    EdgeKind.COMPOSITION_INPUT: {(NodeKind.GENBLAZE_RUN, NodeKind.EXTERNAL_COMPOSITION), (NodeKind.ASSET, NodeKind.EXTERNAL_COMPOSITION)},
    EdgeKind.COMPOSED_OUTPUT: {(NodeKind.EXTERNAL_COMPOSITION, NodeKind.ASSET)},
    EdgeKind.MANIFEST_FOR: {(NodeKind.MANIFEST, NodeKind.GENBLAZE_RUN)},
    EdgeKind.EMBEDDED_MANIFEST: {(NodeKind.ASSET, NodeKind.MANIFEST)},
}


def validate_lineage(nodes: list[ImportedLineageNode], edges: list[ImportedLineageEdge]) -> None:
    by_id = {node.node_id: node for node in nodes}
    if len(by_id) != len(nodes) or len({node.source_id for node in nodes}) != len(nodes):
        raise LineageValidationError("duplicate_source_id")
    if len(edges) > 64 or len({edge.edge_id for edge in edges}) != len(edges):
        raise LineageValidationError("duplicate_or_excessive_edge")
    campaigns = {node.campaign_id for node in nodes}
    if len(campaigns) != 1:
        raise LineageValidationError("cross_campaign_lineage")
    parent_of: dict[str, str] = {}
    graph: dict[str, list[str]] = defaultdict(list)
    signatures: set[tuple[object, ...]] = set()
    for edge in edges:
        source = by_id.get(edge.source_node_id)
        target = by_id.get(edge.target_node_id) if edge.target_node_id else None
        if source is None or edge.campaign_id != source.campaign_id:
            raise LineageValidationError("cross_campaign_lineage")
        signature = (edge.kind, edge.source_node_id, edge.target_node_id, edge.missing_source_id, edge.evidence_class)
        if signature in signatures:
            raise LineageValidationError("duplicate_edge")
        signatures.add(signature)
        if target is not None:
            if target.campaign_id != source.campaign_id:
                raise LineageValidationError("cross_campaign_lineage")
            if (source.kind, target.kind) not in _ALLOWED[edge.kind]:
                raise LineageValidationError("invalid_edge_kinds")
        if edge.kind is EdgeKind.PARENT_RUN:
            if edge.evidence_class is not EvidenceClass.RECORDED:
                raise LineageValidationError("parent_must_be_recorded")
            child = edge.source_node_id
            parent = edge.target_node_id
            if parent == child or edge.missing_source_id == source.source_id:
                raise LineageValidationError("self_parent")
            if child in parent_of:
                raise LineageValidationError("multiple_parent_unsupported")
            if parent:
                parent_of[child] = parent
                graph[child].append(parent)
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise LineageValidationError("lineage_cycle")
        if node_id in visited:
            return
        visiting.add(node_id)
        for parent in graph.get(node_id, []):
            visit(parent)
        visiting.remove(node_id)
        visited.add(node_id)
    for node_id in by_id:
        visit(node_id)


def ordered_nodes(nodes: list[ImportedLineageNode], edges: list[ImportedLineageEdge]) -> list[ImportedLineageNode]:
    stage_rank = {"stage_a_storyboard": 10, "stage_b0_manifest": 20, "stage_b1_manifest": 30,
                  "stage_b2_manifest": 40, "stage_c_composition": 50, "final_delivery": 60,
                  "embedded_manifest": 70, "import_bundle": 0, "generated_asset": 45, "external_input": 35}
    return sorted(nodes, key=lambda node: (stage_rank.get(getattr(node.source_role, "value", node.source_role), 80), node.kind.value, node.source_id, node.node_id))


def ordered_edges(edges: list[ImportedLineageEdge]) -> list[ImportedLineageEdge]:
    return sorted(edges, key=lambda edge: (edge.kind.value, edge.source_node_id, edge.target_node_id or edge.missing_source_id or "", edge.edge_id))
