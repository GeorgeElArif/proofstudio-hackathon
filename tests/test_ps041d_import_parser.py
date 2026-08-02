from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from proofstudio.api.genblaze_external_adapter import ImportValidationError, build_candidate, parse_bundle_bytes
from proofstudio.api.imported_bundle import (
    CheckOutcome, EdgeKind, EvidenceClass, ImportBundleRequest, NodeKind, PINNED_SOURCE_REVISION,
    sha256_json,
)

FIXTURE = Path(__file__).parent / "fixtures/ps041d/genblaze-multi-provider-bundle-v1.json"


def fixture_dict() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def one_object_request(obj: dict, relationships: list[dict] | None = None) -> ImportBundleRequest:
    data = fixture_dict()
    data["objects"] = [copy.deepcopy(obj)]
    data["relationships"] = relationships or []
    return ImportBundleRequest.model_validate(data)


def candidate():
    return build_candidate("camp_parser", parse_bundle_bytes(FIXTURE.read_bytes()))


def set_parent(data: dict, run_id: str, parent_id: str | None) -> None:
    for obj in data["objects"]:
        run = (obj.get("inline_json") or {}).get("run") if isinstance(obj.get("inline_json"), dict) else None
        if run and run.get("run_id") == run_id:
            run["parent_run_id"] = parent_id
            break
    else:
        raise AssertionError(f"missing run {run_id}")
    data["relationships"] = [
        rel for rel in data["relationships"]
        if not (rel["kind"] == "parent_run" and rel["source_id"] == run_id)
    ]
    rel = {"kind": "parent_run", "source_id": run_id, "evidence_class": "recorded",
           "source_locator": "manifest.run.parent_run_id", "hash_covered": False}
    if parent_id is None:
        return
    if any((obj.get("inline_json") or {}).get("run", {}).get("run_id") == parent_id for obj in data["objects"]):
        rel["target_id"] = parent_id
    else:
        rel["missing_source_id"] = parent_id
    data["relationships"].append(rel)


def test_valid_sanitized_pinned_bundle_normalizes_stage_contract() -> None:
    built = candidate()
    assert built.bundle.source_revision == PINNED_SOURCE_REVISION
    assert built.bundle.state == "partial_bundle"
    assert any(n.kind is NodeKind.STANDALONE_ARTIFACT and n.source_role == "stage_a_storyboard" for n in built.nodes)
    runs = [n for n in built.nodes if n.kind is NodeKind.GENBLAZE_RUN]
    assert [n.run.stage for n in runs] == ["B0", "B1", "B2"]
    assert all(n.run.manifest_schema == "1.5" for n in runs)
    assert any(step.provider == "unknown-video-vendor" for n in runs for step in n.run.steps)
    parents = [e for e in built.edges if e.kind is EdgeKind.PARENT_RUN]
    assert len(parents) == 2 and all(e.evidence_class is EvidenceClass.RECORDED and not e.hash_covered for e in parents)
    assert any(e.kind is EdgeKind.SCENE_MEMBER and e.evidence_class is EvidenceClass.INFERRED for e in built.edges)
    assert any(n.kind is NodeKind.EXTERNAL_COMPOSITION and n.source_role == "stage_c_composition" for n in built.nodes)
    serialized = json.dumps([node.model_dump(mode="json") for node in built.nodes])
    assert "style_prompt" not in serialized and "provider_payload" not in serialized and "b2://" not in serialized


def test_reordered_equivalent_has_same_fingerprint() -> None:
    data = fixture_dict()
    first = build_candidate("camp_parser", ImportBundleRequest.model_validate(data))
    data["objects"].reverse(); data["relationships"].reverse()
    second = build_candidate("camp_parser", ImportBundleRequest.model_validate(data))
    assert first.bundle.bundle_fingerprint == second.bundle.bundle_fingerprint
    assert first.bundle.bundle_id == second.bundle.bundle_id


def test_source_conflict_fingerprints_bind_descriptor_role_and_run_stage() -> None:
    data = fixture_dict()
    stage_a = data["objects"][0]
    as_stage_a = build_candidate("camp_parser", one_object_request(stage_a))
    stage_a_node = next(node for node in as_stage_a.nodes if node.source_id == stage_a["source_id"])
    assert as_stage_a.source_fingerprints[("object", stage_a["source_id"])] == sha256_json({
        "role": "stage_a_storyboard",
        "normalized_content_fingerprint": stage_a_node.content_fingerprint,
    })

    as_stage_c_data = copy.deepcopy(stage_a); as_stage_c_data["role"] = "stage_c_composition"
    as_stage_c = build_candidate("camp_parser", one_object_request(as_stage_c_data))
    stage_c_node = next(node for node in as_stage_c.nodes if node.source_id == stage_a["source_id"])
    assert stage_c_node.content_fingerprint == stage_a_node.content_fingerprint
    assert as_stage_c.source_fingerprints[("object", stage_a["source_id"])] == sha256_json({
        "role": "stage_c_composition",
        "normalized_content_fingerprint": stage_c_node.content_fingerprint,
    })
    assert as_stage_c.source_fingerprints[("object", stage_a["source_id"])] != as_stage_a.source_fingerprints[("object", stage_a["source_id"])]

    b1 = data["objects"][2]
    parent = [{"kind": "parent_run", "source_id": "b1-run-sanitized-001",
               "missing_source_id": "b0-run-sanitized-001", "evidence_class": "recorded",
               "source_locator": "manifest.run.parent_run_id", "hash_covered": False}]
    as_b1 = build_candidate("camp_parser", one_object_request(b1, parent))
    b1_run = next(node for node in as_b1.nodes if node.source_id == "b1-run-sanitized-001")
    assert as_b1.source_fingerprints[("genblaze_run", "b1-run-sanitized-001")] == sha256_json({
        "stage": "B1",
        "normalized_manifest_fingerprint": b1_run.content_fingerprint,
    })

    as_b2_data = copy.deepcopy(b1); as_b2_data["role"] = "stage_b2_manifest"; as_b2_data["source_id"] = "different-b2-descriptor"
    as_b2 = build_candidate("camp_parser", one_object_request(as_b2_data, parent))
    b2_run = next(node for node in as_b2.nodes if node.source_id == "b1-run-sanitized-001")
    assert b2_run.content_fingerprint == b1_run.content_fingerprint
    assert as_b2.source_fingerprints[("genblaze_run", "b1-run-sanitized-001")] == sha256_json({
        "stage": "B2",
        "normalized_manifest_fingerprint": b2_run.content_fingerprint,
    })
    assert as_b2.source_fingerprints[("genblaze_run", "b1-run-sanitized-001")] != as_b1.source_fingerprints[("genblaze_run", "b1-run-sanitized-001")]


def test_declared_hash_is_recorded_evidence_not_content_identity() -> None:
    data = fixture_dict()
    declared = "a" * 64
    data["objects"][0]["content_sha256"] = declared
    first = build_candidate("camp_parser", ImportBundleRequest.model_validate(data))
    repeated = build_candidate("camp_parser", ImportBundleRequest.model_validate(copy.deepcopy(data)))
    reordered = copy.deepcopy(data)
    reordered["objects"][0]["inline_json"] = dict(reversed(list(reordered["objects"][0]["inline_json"].items())))
    equivalent = build_candidate("camp_parser", ImportBundleRequest.model_validate(reordered))
    assert first.bundle.bundle_id == repeated.bundle.bundle_id == equivalent.bundle.bundle_id

    changed_declaration = copy.deepcopy(data)
    changed_declaration["objects"][0]["content_sha256"] = "b" * 64
    second = build_candidate("camp_parser", ImportBundleRequest.model_validate(changed_declaration))
    assert first.bundle.bundle_fingerprint == second.bundle.bundle_fingerprint
    assert first.bundle.bundle_id == second.bundle.bundle_id
    key = ("object", data["objects"][0]["source_id"])
    assert first.source_fingerprints[key] == second.source_fingerprints[key]
    node = next(item for item in second.nodes if item.source_id == data["objects"][0]["source_id"])
    assert node.metadata["declared_content_sha256"] == "b" * 64
    assert any(check.outcome is CheckOutcome.HASH_PRESENT for check in node.checks)
    assert all(check.outcome is not CheckOutcome.HASH_VERIFIED for check in node.checks)


def test_manifest_identity_uses_normalized_parent_lineage_not_verified_hash_only() -> None:
    data = fixture_dict()
    base = build_candidate("camp_parser", ImportBundleRequest.model_validate(data))
    changed = copy.deepcopy(data)
    original_hash = changed["objects"][2]["inline_json"]["canonical_hash"]
    set_parent(changed, "b1-run-sanitized-001", "missing-parent-recorded-001")
    assert changed["objects"][2]["inline_json"]["canonical_hash"] == original_hash
    mutated = build_candidate("camp_parser", ImportBundleRequest.model_validate(changed))

    base_run = next(node for node in base.nodes if node.source_id == "b1-run-sanitized-001")
    changed_run = next(node for node in mutated.nodes if node.source_id == "b1-run-sanitized-001")
    assert base_run.content_fingerprint != changed_run.content_fingerprint
    assert any(check.outcome is CheckOutcome.MANIFEST_HASH_VERIFIED for check in changed_run.checks)
    assert changed_run.run.manifest_hash == original_hash
    assert changed_run.run.parent_run_id == "missing-parent-recorded-001"
    assert any(
        edge.kind is EdgeKind.PARENT_RUN
        and edge.missing_source_id == "missing-parent-recorded-001"
        and edge.hash_covered is False
        for edge in mutated.edges
    )


def test_transport_url_only_differences_do_not_affect_identity_or_survive() -> None:
    data = fixture_dict()
    first = build_candidate("camp_parser", ImportBundleRequest.model_validate(data))
    changed = copy.deepcopy(data)
    changed["objects"][3]["inline_json"]["run"]["steps"][0]["inputs"][0]["url"] = "b2://configured-alias/import-root/changed-keyframe.png"
    changed["objects"][3]["inline_json"]["run"]["steps"][0]["assets"][0]["url"] = "b2://configured-alias/import-root/changed-video.mp4"
    second = build_candidate("camp_parser", ImportBundleRequest.model_validate(changed))
    assert first.bundle.bundle_fingerprint == second.bundle.bundle_fingerprint
    assert first.bundle.bundle_id == second.bundle.bundle_id
    serialized = json.dumps([node.model_dump(mode="json") for node in second.nodes])
    assert "changed-keyframe.png" not in serialized and "changed-video.mp4" not in serialized


@pytest.mark.parametrize("raw,code", [
    (b"\xff", "invalid_utf8"),
    (b'{"bundle_schema":"proofstudio.genblaze_bundle.v1","bundle_schema":"proofstudio.genblaze_bundle.v1"}', "duplicate_json_key"),
])
def test_encoding_and_duplicate_key_rejected(raw: bytes, code: str) -> None:
    with pytest.raises(ImportValidationError, match=code):
        parse_bundle_bytes(raw)


def test_unknown_schema_unknown_field_and_signed_url_rejected() -> None:
    data = fixture_dict(); data["bundle_schema"] = "future"
    with pytest.raises(ImportValidationError, match="unsupported_bundle_schema"):
        parse_bundle_bytes(json.dumps(data).encode())
    data = fixture_dict(); data["unexpected"] = True
    with pytest.raises(ImportValidationError, match="invalid_bundle"):
        parse_bundle_bytes(json.dumps(data).encode())
    data = fixture_dict()
    data["objects"][3]["inline_json"]["run"]["steps"][0]["inputs"][0]["url"] = "https://example.invalid/a?" + "X-Amz-" + "Signature=secret"
    with pytest.raises(ImportValidationError, match="signed_or_credentialed_url_forbidden"):
        build_candidate("camp_parser", ImportBundleRequest.model_validate(data))


def test_unsupported_manifest_schema_depth_control_and_limits() -> None:
    data = fixture_dict(); data["objects"][1]["inline_json"]["schema_version"] = "1.6"
    with pytest.raises(ImportValidationError, match="unsupported_schema"):
        build_candidate("camp_parser", ImportBundleRequest.model_validate(data))
    data = fixture_dict(); nested: dict = {}; cursor = nested
    for _ in range(34): cursor["x"] = {}; cursor = cursor["x"]
    data["objects"][0]["inline_json"]["nested"] = nested
    with pytest.raises(ImportValidationError, match="excessive_nesting"):
        parse_bundle_bytes(json.dumps(data).encode())
    data = fixture_dict(); data["objects"][0]["source_id"] = "bad\u0001id"
    with pytest.raises(ImportValidationError, match="control_character"):
        parse_bundle_bytes(json.dumps(data).encode())
    data = fixture_dict(); data["objects"] = data["objects"] * 37
    with pytest.raises(ImportValidationError, match="invalid_bundle"):
        parse_bundle_bytes(json.dumps(data).encode())


def test_bundle_and_object_byte_limits() -> None:
    with pytest.raises(ImportValidationError, match="bundle_too_large"):
        parse_bundle_bytes(b" " * (1_048_576 + 1))
    data = fixture_dict(); data["objects"][0]["inline_json"]["title"] = "x" * 9_000
    with pytest.raises(ImportValidationError, match="string_too_long"):
        parse_bundle_bytes(json.dumps(data).encode())
