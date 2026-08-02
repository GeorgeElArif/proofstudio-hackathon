"""Defensive adapter from the pinned sample bundle to PS-041D records.

Only data models are parsed. Provider names are inert strings and no network or
provider package is dynamically imported.
"""

from __future__ import annotations

import copy
import hashlib
import ipaddress
import json
import os
import unicodedata
from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import urlsplit

from genblaze_core.models.manifest import ManifestError, parse_manifest
from pydantic import ValidationError

from proofstudio.api.imported_bundle import (
    BUNDLE_SCHEMA, FINGERPRINT_SCHEMA, MAX_AGGREGATE_JSON_BYTES, MAX_BUNDLE_BYTES,
    MAX_DEPTH, MAX_EVIDENCE_STRING, MAX_JSON_OBJECT_BYTES, MAX_STRING,
    B2ObjectReference, CheckOutcome, EdgeKind, EvidenceClass, ImportBundleRequest,
    ImportCheck, ImportLimitation, ImportObjectDescriptor, ImportResult, ImportedBundleRecord,
    ImportedLineageEdge, ImportedLineageNode, ImportedRunSummary, ImportedStepSummary,
    ImportRole, NodeKind, PortableLineagePassport, canonical_json, deterministic_id, sha256_json,
)
from proofstudio.api.lineage import ordered_edges, ordered_nodes, validate_lineage


class ImportValidationError(ValueError):
    def __init__(self, code: str, status: int = 400) -> None:
        self.code = code
        self.status = status
        super().__init__(code)


@dataclass(frozen=True)
class ImportCandidate:
    bundle: ImportedBundleRecord
    nodes: list[ImportedLineageNode]
    edges: list[ImportedLineageEdge]
    source_fingerprints: dict[tuple[str, str], str]


def _duplicate_key(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ImportValidationError("duplicate_json_key")
        result[key] = value
    return result


def _walk_limits(value: Any, depth: int = 0) -> int:
    if depth > MAX_DEPTH:
        raise ImportValidationError("excessive_nesting")
    total = 0
    if isinstance(value, str):
        if len(value) > MAX_STRING:
            raise ImportValidationError("string_too_long")
        if value != unicodedata.normalize("NFC", value):
            raise ImportValidationError("identifier_not_nfc")
        if any(unicodedata.category(ch) == "Cc" for ch in value):
            raise ImportValidationError("control_character")
        return len(value.encode("utf-8"))
    if isinstance(value, dict):
        for key, item in value.items():
            total += _walk_limits(key, depth + 1) + _walk_limits(item, depth + 1)
    elif isinstance(value, list):
        total += sum(_walk_limits(item, depth + 1) for item in value)
    return total


def parse_bundle_bytes(raw: bytes) -> ImportBundleRequest:
    if len(raw) > MAX_BUNDLE_BYTES:
        raise ImportValidationError("bundle_too_large", 413)
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ImportValidationError("invalid_utf8") from exc
    try:
        value = json.loads(text, object_pairs_hook=_duplicate_key)
    except ImportValidationError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ImportValidationError("malformed_json") from exc
    if not isinstance(value, dict):
        raise ImportValidationError("invalid_bundle")
    _walk_limits(value)
    if value.get("bundle_schema") != BUNDLE_SCHEMA:
        raise ImportValidationError("unsupported_bundle_schema")
    try:
        request = ImportBundleRequest.model_validate(value)
    except ValidationError as exc:
        raise ImportValidationError("invalid_bundle") from exc
    aggregate = sum(len(canonical_json(obj.inline_json)) for obj in request.objects if obj.inline_json is not None)
    if any(len(canonical_json(obj.inline_json)) > MAX_JSON_OBJECT_BYTES for obj in request.objects if obj.inline_json is not None):
        raise ImportValidationError("object_json_too_large", 413)
    if aggregate > MAX_AGGREGATE_JSON_BYTES:
        raise ImportValidationError("aggregate_json_too_large", 413)
    return request


def _transport_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return bool(parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or parsed.username or parsed.password)


def _validate_external_fields(value: Any) -> None:
    if isinstance(value, dict):
        forbidden = {"authorization", "cookie", "access_key", "access_key_id", "secret_key", "secret_access_key", "session_token", "credentials"}
        if any(str(key).lower() in forbidden for key in value):
            raise ImportValidationError("credential_field_forbidden")
        for key, item in value.items():
            if str(key).lower() in {"url", "uri", "manifest_uri"} and isinstance(item, str) and item:
                try:
                    parsed = urlsplit(item)
                except ValueError as exc:
                    raise ImportValidationError("unsafe_url") from exc
                if parsed.username or parsed.password or parsed.query or parsed.fragment:
                    raise ImportValidationError("signed_or_credentialed_url_forbidden")
                if parsed.scheme not in {"https", "b2", "s3"}:
                    raise ImportValidationError("unsupported_url_scheme")
                host = parsed.hostname
                if host:
                    if host.lower() in {"localhost", "metadata.google.internal"} or host.lower().endswith(".localhost"):
                        raise ImportValidationError("private_url_target")
                    try:
                        address = ipaddress.ip_address(host)
                        if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
                            raise ImportValidationError("private_url_target")
                    except ValueError:
                        pass
            _validate_external_fields(item)
    elif isinstance(value, list):
        for item in value:
            _validate_external_fields(item)


def _fingerprint_safe(value: Any) -> Any:
    """Remove transport/raw-prompt material before content identity."""
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if key.lower() in {"url", "manifest_uri", "prompt", "negative_prompt", "provider_payload", "authorization", "cookie"}:
                continue
            result[key] = _fingerprint_safe(item)
        return result
    if isinstance(value, list):
        return [_fingerprint_safe(item) for item in value]
    if isinstance(value, str) and _transport_url(value):
        return "[transport-removed]"
    return value


def _content_fingerprint(obj: ImportObjectDescriptor, content: Any | None) -> str:
    if content is not None:
        return sha256_json(_fingerprint_safe(content))
    if obj.missing:
        return sha256_json({"missing": True, "role": obj.role.value, "source_id": obj.source_id})
    assert obj.b2_reference is not None
    return sha256_json({"object_key": obj.b2_reference.object_key, "version_id": obj.b2_reference.version_id})


def _declared_hash_checks(obj: ImportObjectDescriptor) -> list[ImportCheck]:
    if not obj.content_sha256:
        return []
    return [ImportCheck(outcome=CheckOutcome.HASH_PRESENT, subject="declared_content_sha256")]


def _safe_manifest_summary(manifest: Any, stage: str) -> tuple[ImportedRunSummary, list[ImportCheck]]:
    checks = [ImportCheck(outcome=CheckOutcome.PARSED, subject="manifest")]
    if manifest.canonical_hash:
        checks.append(ImportCheck(outcome=CheckOutcome.HASH_PRESENT, subject="manifest"))
        if manifest.verify_hash():
            checks.append(ImportCheck(outcome=CheckOutcome.MANIFEST_HASH_VERIFIED, subject="manifest"))
        else:
            checks.append(ImportCheck(outcome=CheckOutcome.HASH_MISMATCH, subject="manifest"))
    report = manifest.verification_report()
    if not report.unverified_sha256_ids:
        checks.append(ImportCheck(outcome=CheckOutcome.MANIFEST_OUTPUT_HASHES_DECLARED, subject="manifest_outputs"))
    steps = []
    for position, step in enumerate(manifest.run.steps):
        provider = step.provider
        if provider is not None and len(provider) > MAX_EVIDENCE_STRING:
            raise ImportValidationError("provider_too_long")
        if len(step.model) > MAX_EVIDENCE_STRING:
            raise ImportValidationError("model_too_long")
        steps.append(ImportedStepSummary(
            step_id=step.step_id, step_index=step.step_index if step.step_index is not None else position,
            provider=provider, model=step.model, modality=str(step.modality.value), status=str(step.status.value),
            output_count=len(step.assets), input_count=len(step.inputs),
        ))
    return ImportedRunSummary(
        run_id=manifest.run.run_id, stage=stage, manifest_schema="1.5",
        manifest_hash=manifest.canonical_hash or None, parent_run_id=manifest.run.parent_run_id,
        status=str(manifest.run.status.value), steps=steps,
    ), checks


def build_candidate(
    campaign_id: str,
    request: ImportBundleRequest,
    *,
    b2_json_reader: Callable[[B2ObjectReference], dict[str, Any]] | None = None,
    server_bucket_alias: str | None = None,
    server_import_root: str | None = None,
) -> ImportCandidate:
    bucket_alias = server_bucket_alias or os.environ.get("PROOFSTUDIO_IMPORT_BUCKET_ALIAS", "configured-import")
    import_root = (server_import_root or os.environ.get("PROOFSTUDIO_IMPORT_ROOT", "import-root")).rstrip("/")
    resolved: list[tuple[ImportObjectDescriptor, Any | None]] = []
    seen_sources: set[str] = set()
    aggregate_json_bytes = sum(
        len(canonical_json(obj.inline_json)) for obj in request.objects if obj.inline_json is not None
    )
    for obj in request.objects:
        if obj.source_id in seen_sources:
            raise ImportValidationError("duplicate_source_id")
        seen_sources.add(obj.source_id)
        content = obj.inline_json
        if content is not None:
            _walk_limits(content)
            _validate_external_fields(content)
        if obj.missing and not request.partial_bundle:
            raise ImportValidationError("missing_evidence_requires_partial_bundle")
        if obj.b2_reference is not None:
            if obj.b2_reference.bucket_alias != bucket_alias:
                raise ImportValidationError("b2_alias_not_allowed")
            if not obj.b2_reference.object_key.startswith(import_root + "/"):
                raise ImportValidationError("b2_key_outside_root")
        if obj.b2_reference is not None and not obj.missing and obj.role is not ImportRole.FINAL:
            if b2_json_reader is None:
                raise ImportValidationError("b2_import_disabled", 503)
            content = b2_json_reader(obj.b2_reference)
            if not isinstance(content, dict):
                raise ImportValidationError("malformed_json")
            _walk_limits(content)
            _validate_external_fields(content)
            content_bytes = len(canonical_json(content))
            if content_bytes > MAX_JSON_OBJECT_BYTES:
                raise ImportValidationError("object_json_too_large", 413)
            aggregate_json_bytes += content_bytes
            if aggregate_json_bytes > MAX_AGGREGATE_JSON_BYTES:
                raise ImportValidationError("aggregate_json_too_large", 413)
        resolved.append((obj, content))

    descriptor_fingerprints = {obj.source_id: _content_fingerprint(obj, content) for obj, content in resolved}
    source_fingerprints: dict[tuple[str, str], str] = {
        ("object", obj.source_id): sha256_json({
            "role": obj.role.value,
            "normalized_content_fingerprint": descriptor_fingerprints[obj.source_id],
        })
        for obj, _ in resolved
    }
    relationship_material = sorted(
        ({"kind": rel.kind.value, "from": rel.source_id, "to": rel.target_id or rel.missing_source_id,
          "evidence": rel.evidence_class.value} for rel in request.relationships),
        key=lambda item: canonical_json(item),
    )
    object_material = sorted(
        ({"role": obj.role.value, "source_id": obj.source_id, "content": descriptor_fingerprints[obj.source_id],
          "object_key": obj.b2_reference.object_key if obj.b2_reference else None,
          "version_id": obj.b2_reference.version_id if obj.b2_reference else None} for obj, _ in resolved),
        key=lambda item: canonical_json(item),
    )
    fingerprint = sha256_json({
        "fingerprint_schema": FINGERPRINT_SCHEMA, "source_type": request.source_type,
        "source_slug": request.source_slug, "objects": object_material, "relationships": relationship_material,
    })
    bundle_id = deterministic_id("bundle", fingerprint)
    nodes: list[ImportedLineageNode] = []
    edges: list[ImportedLineageEdge] = []
    source_nodes: dict[str, ImportedLineageNode] = {}
    bundle_node = ImportedLineageNode(
        node_id=deterministic_id("node", fingerprint, "bundle"), campaign_id=campaign_id, bundle_id=bundle_id,
        kind=NodeKind.IMPORT_BUNDLE, source_id=f"bundle:{fingerprint}", source_role="import_bundle",
        content_fingerprint=fingerprint, evidence_class=EvidenceClass.RECORDED,
        checks=[ImportCheck(outcome=CheckOutcome.PARTIAL_BUNDLE if request.partial_bundle else CheckOutcome.RECORDED, subject="bundle")],
    )
    nodes.append(bundle_node)

    stage_map = {ImportRole.B0: "B0", ImportRole.B1: "B1", ImportRole.B2: "B2"}
    manifest_by_run: dict[str, ImportedLineageNode] = {}
    for obj, content in resolved:
        fp = descriptor_fingerprints[obj.source_id]
        checks: list[ImportCheck] = _declared_hash_checks(obj)
        limitations: list[ImportLimitation] = []
        if obj.missing:
            checks.append(ImportCheck(outcome=CheckOutcome.OBJECT_MISSING, subject=obj.source_id))
            if obj.limitation:
                limitations.append(ImportLimitation(code="missing_evidence", notice=obj.limitation))
        if obj.role in stage_map:
            if not isinstance(content, dict):
                raise ImportValidationError("manifest_invalid")
            if content.get("schema_version") != "1.5":
                raise ImportValidationError("unsupported_schema")
            try:
                manifest = parse_manifest(copy.deepcopy(content))
                summary, manifest_checks = _safe_manifest_summary(manifest, stage_map[obj.role])
                checks.extend(manifest_checks)
            except (ManifestError, ValidationError, ValueError, TypeError) as exc:
                raise ImportValidationError("manifest_invalid") from exc
            manifest_node = ImportedLineageNode(
                node_id=deterministic_id("node", fingerprint, obj.source_id, "manifest"), campaign_id=campaign_id,
                bundle_id=bundle_id, kind=NodeKind.MANIFEST, source_id=obj.source_id, source_role=obj.role,
                content_fingerprint=fp, evidence_class=EvidenceClass.RECORDED, checks=checks,
                b2_reference=obj.b2_reference, limitations=limitations,
                metadata={"manifest_schema": "1.5", "manifest_hash": summary.manifest_hash,
                          "declared_content_sha256": obj.content_sha256},
            )
            run_node = ImportedLineageNode(
                node_id=deterministic_id("node", fingerprint, summary.run_id, "run"), campaign_id=campaign_id,
                bundle_id=bundle_id, kind=NodeKind.GENBLAZE_RUN, source_id=summary.run_id, source_role=obj.role,
                content_fingerprint=fp, evidence_class=EvidenceClass.RECORDED, checks=checks,
                run=summary, limitations=limitations,
            )
            nodes.extend([manifest_node, run_node]); source_nodes[obj.source_id] = manifest_node
            source_nodes[summary.run_id] = run_node; manifest_by_run[summary.run_id] = run_node
            source_fingerprints[("genblaze_run", summary.run_id)] = sha256_json({
                "stage": summary.stage,
                "normalized_manifest_fingerprint": fp,
            })
            edges.append(_edge(campaign_id, bundle_id, fingerprint, EdgeKind.MANIFEST_FOR, manifest_node,
                               run_node, EvidenceClass.RECORDED, True, "manifest.run"))
            for step in manifest.run.steps:
                for asset in step.assets:
                    asset_id = asset.asset_id
                    if asset_id in source_nodes:
                        raise ImportValidationError("duplicate_source_id")
                    asset_fp = sha256_json({"asset_id": asset_id, "media_type": asset.media_type,
                                            "sha256": asset.sha256, "size_bytes": asset.size_bytes})
                    asset_node = ImportedLineageNode(
                        node_id=deterministic_id("node", fingerprint, asset_id, "asset"), campaign_id=campaign_id,
                        bundle_id=bundle_id, kind=NodeKind.ASSET, source_id=asset_id, source_role="generated_asset",
                        content_fingerprint=asset_fp, evidence_class=EvidenceClass.RECORDED,
                        checks=[ImportCheck(outcome=CheckOutcome.HASH_PRESENT if asset.sha256 else CheckOutcome.RECORDED, subject=asset_id)],
                        metadata={"media_type": asset.media_type, "sha256": asset.sha256, "size_bytes": asset.size_bytes},
                    )
                    nodes.append(asset_node); source_nodes[asset_id] = asset_node
                    source_fingerprints[("asset", asset_id)] = asset_fp
                    edges.append(_edge(campaign_id, bundle_id, fingerprint, EdgeKind.GENERATED_ASSET, run_node,
                                       asset_node, EvidenceClass.RECORDED, True, f"step:{step.step_id}:output"))
        else:
            kind = (NodeKind.STANDALONE_ARTIFACT if obj.role is ImportRole.STAGE_A else
                    NodeKind.EXTERNAL_COMPOSITION if obj.role is ImportRole.STAGE_C else
                    NodeKind.MANIFEST if obj.role is ImportRole.EMBEDDED else NodeKind.ASSET)
            safe_metadata: dict[str, Any] = {}
            if isinstance(content, dict):
                for key in ("title", "status", "media_type", "sha256", "size_bytes", "manifest_schema"):
                    if key in content:
                        safe_metadata[key] = content[key]
            if obj.content_sha256:
                safe_metadata["declared_content_sha256"] = obj.content_sha256
            node = ImportedLineageNode(
                node_id=deterministic_id("node", fingerprint, obj.source_id, kind.value), campaign_id=campaign_id,
                bundle_id=bundle_id, kind=kind, source_id=obj.source_id, source_role=obj.role,
                content_fingerprint=fp, evidence_class=EvidenceClass.RECORDED,
                checks=checks or [ImportCheck(outcome=CheckOutcome.RECORDED, subject=obj.source_id)],
                limitations=limitations, b2_reference=obj.b2_reference, metadata=safe_metadata,
            )
            nodes.append(node); source_nodes[obj.source_id] = node

    # Manifest parent_run_id is authoritative evidence for parent edges. V1.5 excludes it from the hash.
    existing_parent: set[tuple[str, str]] = set()
    for run_id, run_node in manifest_by_run.items():
        parent_id = run_node.run.parent_run_id if run_node.run else None
        if parent_id:
            parent = manifest_by_run.get(parent_id)
            edges.append(_edge(campaign_id, bundle_id, fingerprint, EdgeKind.PARENT_RUN, run_node, parent,
                               EvidenceClass.RECORDED, False, "manifest.run.parent_run_id", missing=parent_id if parent is None else None,
                               limitation="Manifest 1.5 records parent_run_id but excludes it from the canonical hash."))
            existing_parent.add((run_id, parent_id))

    declared_parents = {
        (rel.source_id, rel.target_id or rel.missing_source_id or "")
        for rel in request.relationships if rel.kind is EdgeKind.PARENT_RUN
    }
    if existing_parent != declared_parents:
        raise ImportValidationError("parent_relationship_mismatch")

    for rel in request.relationships:
        if rel.kind is EdgeKind.PARENT_RUN and (rel.source_id, rel.target_id or rel.missing_source_id or "") in existing_parent:
            if rel.evidence_class is not EvidenceClass.RECORDED or rel.hash_covered:
                raise ImportValidationError("parent_relationship_mismatch")
            continue
        source = source_nodes.get(rel.source_id)
        if source is None:
            raise ImportValidationError("relationship_source_missing")
        target = source_nodes.get(rel.target_id) if rel.target_id else None
        if rel.target_id and target is None:
            raise ImportValidationError("relationship_target_missing")
        if rel.evidence_class is EvidenceClass.INFERRED and rel.kind in {EdgeKind.PARENT_RUN, EdgeKind.MANIFEST_FOR}:
            raise ImportValidationError("relationship_evidence_invalid")
        if rel.kind is EdgeKind.SCENE_MEMBER and rel.evidence_class is EvidenceClass.INFERRED and not request.positional_scene_convention:
            raise ImportValidationError("positional_convention_required")
        edges.append(_edge(campaign_id, bundle_id, fingerprint, rel.kind, source, target, rel.evidence_class,
                           rel.hash_covered, rel.source_locator, missing=rel.missing_source_id, limitation=rel.limitation))

    validate_lineage(nodes, edges)
    nodes = ordered_nodes(nodes, edges); edges = ordered_edges(edges)
    bundle = ImportedBundleRecord(
        bundle_id=bundle_id, campaign_id=campaign_id, bundle_fingerprint=fingerprint,
        source_type=request.source_type, source_slug=request.source_slug, source_revision=request.source_revision,
        state="partial_bundle" if request.partial_bundle else "complete",
        node_ids=[node.node_id for node in nodes], edge_ids=[edge.edge_id for edge in edges],
    )
    return ImportCandidate(bundle=bundle, nodes=nodes, edges=edges, source_fingerprints=source_fingerprints)


def _edge(campaign_id: str, bundle_id: str, fingerprint: str, kind: EdgeKind,
          source: ImportedLineageNode, target: ImportedLineageNode | None, evidence: EvidenceClass,
          hash_covered: bool, locator: str | None, *, missing: str | None = None,
          limitation: str | None = None) -> ImportedLineageEdge:
    target_key = target.node_id if target else missing or "missing"
    limitations = [ImportLimitation(code="relationship_limitation", notice=limitation)] if limitation else []
    return ImportedLineageEdge(
        edge_id=deterministic_id("edge", fingerprint, kind.value, source.node_id, target_key, evidence.value),
        campaign_id=campaign_id, bundle_id=bundle_id, kind=kind, source_node_id=source.node_id,
        target_node_id=target.node_id if target else None, missing_source_id=missing,
        evidence_class=evidence, hash_covered=hash_covered,
        check_outcome=CheckOutcome.RELATIONSHIP_RECORDED if evidence is EvidenceClass.RECORDED else CheckOutcome.RELATIONSHIP_INFERRED,
        source_locator=locator, limitations=limitations,
    )


def passport_for(candidate: ImportCandidate | ImportResult) -> PortableLineagePassport:
    bundle = candidate.bundle
    limitations = [
        ImportLimitation(code="process_local", notice="Import atomicity and idempotency are process-local and do not survive restart."),
        ImportLimitation(code="manifest_parent_hash", notice="Manifest 1.5 parent_run_id is recorded but is not canonical-hash-covered."),
        ImportLimitation(code="proof_boundary", notice="Provider and model values are recorded claims; remote asset bytes are not checked unless explicitly stated."),
    ]
    return PortableLineagePassport(
        campaign_id=bundle.campaign_id, bundle_id=bundle.bundle_id,
        bundle_fingerprint=bundle.bundle_fingerprint, source_type=bundle.source_type,
        source_slug=bundle.source_slug, source_revision=bundle.source_revision, state=bundle.state,
        nodes=ordered_nodes(list(candidate.nodes), list(candidate.edges)),
        edges=ordered_edges(list(candidate.edges)), limitations=limitations,
    )
