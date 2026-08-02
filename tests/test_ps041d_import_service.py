from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from proofstudio.api.genblaze_external_adapter import ImportValidationError, build_candidate, parse_bundle_bytes
from proofstudio.api.imported_bundle import EdgeKind, ImportBundleRequest
from proofstudio.api.lineage import LineageValidationError
from proofstudio.api.models import CampaignCreate
from proofstudio.api.services import ProofStudioService
from proofstudio.api.store import InMemoryStore

FIXTURE = Path(__file__).parent / "fixtures/ps041d/genblaze-multi-provider-bundle-v1.json"


def payload() -> ImportBundleRequest:
    return parse_bundle_bytes(FIXTURE.read_bytes())


def fixture_dict() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def one_object_payload(obj: dict, relationships: list[dict] | None = None) -> ImportBundleRequest:
    data = fixture_dict()
    data["objects"] = [copy.deepcopy(obj)]
    data["relationships"] = relationships or []
    return ImportBundleRequest.model_validate(data)


def manifest_parent_relationship(run_id: str, parent_id: str) -> list[dict]:
    return [{
        "kind": "parent_run", "source_id": run_id, "missing_source_id": parent_id,
        "evidence_class": "recorded", "source_locator": "manifest.run.parent_run_id",
        "hash_covered": False,
    }]


def campaign(service: ProofStudioService, name: str) -> str:
    return service.create_campaign(CampaignCreate(name=name, brief="PS-041D isolated test"))["campaign_id"]


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
    if parent_id is None:
        return
    rel = {"kind": "parent_run", "source_id": run_id, "evidence_class": "recorded",
           "source_locator": "manifest.run.parent_run_id", "hash_covered": False}
    if any((obj.get("inline_json") or {}).get("run", {}).get("run_id") == parent_id for obj in data["objects"]):
        rel["target_id"] = parent_id
    else:
        rel["missing_source_id"] = parent_id
    data["relationships"].append(rel)


def test_first_reimport_reordered_and_passport_are_deterministic() -> None:
    service = ProofStudioService(); campaign_id = campaign(service, "one")
    first = service.import_genblaze_bundle(campaign_id, payload())
    second = service.import_genblaze_bundle(campaign_id, payload())
    data = json.loads(FIXTURE.read_text()); data["objects"].reverse(); data["relationships"].reverse()
    reordered = service.import_genblaze_bundle(campaign_id, ImportBundleRequest.model_validate(data))
    assert first.created is True and second.created is False and reordered.created is False
    assert first.bundle.bundle_id == second.bundle.bundle_id == reordered.bundle.bundle_id
    assert len(service.list_imported_bundles(campaign_id)) == 1
    passport = service.get_imported_passport(campaign_id, first.bundle.bundle_id)
    assert passport.bundle_fingerprint == first.bundle.bundle_fingerprint
    assert [e.edge_id for e in passport.edges] == [e.edge_id for e in sorted(passport.edges, key=lambda e: (e.kind.value, e.source_node_id, e.target_node_id or e.missing_source_id or "", e.edge_id))]


def test_descriptor_role_reclassification_conflicts_and_preserves_original_bundle() -> None:
    service = ProofStudioService(); campaign_id = campaign(service, "descriptor-role")
    data = fixture_dict()
    shared_artifact = copy.deepcopy(data["objects"][0])
    shared_artifact["source_id"] = "shared-artifact"
    first = service.import_genblaze_bundle(campaign_id, one_object_payload(shared_artifact))
    before = service.get_imported_passport(campaign_id, first.bundle.bundle_id).model_dump(mode="json")

    reclassified = copy.deepcopy(shared_artifact)
    reclassified["role"] = "stage_c_composition"
    with pytest.raises(ImportValidationError, match="import_conflict") as exc:
        service.import_genblaze_bundle(campaign_id, one_object_payload(reclassified))
    assert exc.value.status == 409

    after = service.get_imported_passport(campaign_id, first.bundle.bundle_id).model_dump(mode="json")
    assert after == before
    assert len(service.list_imported_bundles(campaign_id)) == 1


def test_same_descriptor_manifest_role_reclassification_conflicts() -> None:
    service = ProofStudioService(); campaign_id = campaign(service, "manifest-descriptor-role")
    data = fixture_dict()
    descriptor = copy.deepcopy(data["objects"][2])
    descriptor["source_id"] = "shared-manifest-descriptor"
    first = service.import_genblaze_bundle(
        campaign_id,
        one_object_payload(descriptor, manifest_parent_relationship("b1-run-sanitized-001", "b0-run-sanitized-001")),
    )

    reclassified = copy.deepcopy(descriptor)
    reclassified["role"] = "stage_b2_manifest"
    with pytest.raises(ImportValidationError, match="import_conflict") as exc:
        service.import_genblaze_bundle(
            campaign_id,
            one_object_payload(reclassified, manifest_parent_relationship("b1-run-sanitized-001", "b0-run-sanitized-001")),
        )
    assert exc.value.status == 409
    assert service.get_imported_passport(campaign_id, first.bundle.bundle_id).bundle_id == first.bundle.bundle_id
    assert len(service.list_imported_bundles(campaign_id)) == 1


def test_same_run_id_stage_reclassification_conflicts_through_different_descriptors() -> None:
    service = ProofStudioService(); campaign_id = campaign(service, "run-stage")
    data = fixture_dict()
    b1_descriptor = copy.deepcopy(data["objects"][2])
    b1_descriptor["source_id"] = "run-stage-b1-descriptor"
    service.import_genblaze_bundle(
        campaign_id,
        one_object_payload(b1_descriptor, manifest_parent_relationship("b1-run-sanitized-001", "b0-run-sanitized-001")),
    )

    b2_descriptor = copy.deepcopy(b1_descriptor)
    b2_descriptor["source_id"] = "run-stage-b2-descriptor"
    b2_descriptor["role"] = "stage_b2_manifest"
    with pytest.raises(ImportValidationError, match="import_conflict") as exc:
        service.import_genblaze_bundle(
            campaign_id,
            one_object_payload(b2_descriptor, manifest_parent_relationship("b1-run-sanitized-001", "b0-run-sanitized-001")),
        )
    assert exc.value.status == 409

    b0_service = ProofStudioService(); b0_campaign = campaign(b0_service, "run-stage-b0")
    b0_descriptor = copy.deepcopy(data["objects"][1])
    b0_descriptor["source_id"] = "run-stage-b0-descriptor"
    b0_service.import_genblaze_bundle(b0_campaign, one_object_payload(b0_descriptor))

    b1_reclassified = copy.deepcopy(b0_descriptor)
    b1_reclassified["source_id"] = "run-stage-b1-descriptor"
    b1_reclassified["role"] = "stage_b1_manifest"
    with pytest.raises(ImportValidationError, match="import_conflict") as exc:
        b0_service.import_genblaze_bundle(b0_campaign, one_object_payload(b1_reclassified))
    assert exc.value.status == 409


def test_source_and_campaign_conflicts_and_golden_namespace() -> None:
    store = InMemoryStore(); service = ProofStudioService(store); a = campaign(service, "a"); b = campaign(service, "b")
    service.import_genblaze_bundle(a, payload())
    with pytest.raises(ImportValidationError, match="import_conflict"):
        service.import_genblaze_bundle(b, payload())
    changed = json.loads(FIXTURE.read_text()); changed["objects"][0]["inline_json"]["title"] = "different sanitized title"
    with pytest.raises(ImportValidationError, match="import_conflict"):
        service.import_genblaze_bundle(a, ImportBundleRequest.model_validate(changed))
    golden = json.loads(FIXTURE.read_text()); golden["objects"][0]["source_id"] = "golden-protected"
    for relationship in golden["relationships"]:
        if relationship["source_id"] == "storyboard-sanitized-001": relationship["source_id"] = "golden-protected"
    with pytest.raises(ImportValidationError, match="golden_namespace_conflict"):
        service.import_genblaze_bundle(b, ImportBundleRequest.model_validate(golden))
    assert len(service.list_imported_bundles(b)) == 0


def test_same_declared_hash_cannot_hide_changed_inline_content() -> None:
    service = ProofStudioService(); campaign_id = campaign(service, "declared")
    data = json.loads(FIXTURE.read_text()); data["objects"][0]["content_sha256"] = "a" * 64
    first = service.import_genblaze_bundle(campaign_id, ImportBundleRequest.model_validate(data))
    repeated = service.import_genblaze_bundle(campaign_id, ImportBundleRequest.model_validate(copy.deepcopy(data)))
    assert first.created is True and repeated.created is False
    changed = copy.deepcopy(data); changed["objects"][0]["inline_json"]["title"] = "different content, same declaration"
    with pytest.raises(ImportValidationError, match="import_conflict") as exc:
        service.import_genblaze_bundle(campaign_id, ImportBundleRequest.model_validate(changed))
    assert exc.value.status == 409


def test_changed_unchecked_declaration_is_idempotent_but_content_still_conflicts() -> None:
    service = ProofStudioService(); campaign_id = campaign(service, "declared-change")
    data = json.loads(FIXTURE.read_text()); data["objects"][0]["content_sha256"] = "a" * 64
    first = service.import_genblaze_bundle(campaign_id, ImportBundleRequest.model_validate(data))
    changed_declaration = copy.deepcopy(data); changed_declaration["objects"][0]["content_sha256"] = "b" * 64
    second = service.import_genblaze_bundle(campaign_id, ImportBundleRequest.model_validate(changed_declaration))
    assert first.created is True and second.created is False
    assert first.bundle.bundle_fingerprint == second.bundle.bundle_fingerprint
    assert first.bundle.bundle_id == second.bundle.bundle_id
    assert len(service.list_imported_bundles(campaign_id)) == 1

    changed_content = copy.deepcopy(data)
    changed_content["objects"][0]["inline_json"]["title"] = "different content, changed declaration"
    changed_content["objects"][0]["content_sha256"] = "c" * 64
    with pytest.raises(ImportValidationError, match="import_conflict") as exc:
        service.import_genblaze_bundle(campaign_id, ImportBundleRequest.model_validate(changed_content))
    assert exc.value.status == 409
    assert len(service.list_imported_bundles(campaign_id)) == 1


def test_same_manifest_run_id_changed_parent_lineage_conflicts() -> None:
    service = ProofStudioService(); campaign_id = campaign(service, "parent-conflict")
    first = service.import_genblaze_bundle(campaign_id, payload())
    changed = json.loads(FIXTURE.read_text())
    original_hash = changed["objects"][2]["inline_json"]["canonical_hash"]
    set_parent(changed, "b1-run-sanitized-001", "missing-parent-recorded-001")
    assert changed["objects"][2]["inline_json"]["canonical_hash"] == original_hash
    candidate = build_candidate(campaign_id, ImportBundleRequest.model_validate(changed))
    changed_run = next(node for node in candidate.nodes if node.source_id == "b1-run-sanitized-001")
    first_run = next(node for node in first.nodes if node.source_id == "b1-run-sanitized-001")
    assert changed_run.content_fingerprint != first_run.content_fingerprint
    with pytest.raises(ImportValidationError, match="import_conflict") as exc:
        service.import_genblaze_bundle(campaign_id, ImportBundleRequest.model_validate(changed))
    assert exc.value.status == 409
    assert len(service.list_imported_bundles(campaign_id)) == 1


def test_run_asset_and_cross_campaign_typed_source_conflicts() -> None:
    store = InMemoryStore(); service = ProofStudioService(store); first_campaign = campaign(service, "typed-a")
    second_campaign = campaign(service, "typed-b"); service.import_genblaze_bundle(first_campaign, payload())

    reused_run = json.loads(FIXTURE.read_text())
    reused_run["objects"][1]["source_id"] = "different-b0-manifest-descriptor"
    reused_run["objects"][1]["inline_json"]["run"]["steps"][0]["model"] = "different-model"
    with pytest.raises(ImportValidationError, match="import_conflict"):
        service.import_genblaze_bundle(first_campaign, ImportBundleRequest.model_validate(reused_run))

    same_run_other_campaign = json.loads(FIXTURE.read_text())
    same_run_other_campaign["objects"][0]["source_id"] = "different-storyboard-descriptor"
    for relationship in same_run_other_campaign["relationships"]:
        if relationship["source_id"] == "storyboard-sanitized-001":
            relationship["source_id"] = "different-storyboard-descriptor"
    with pytest.raises(ImportValidationError, match="import_conflict"):
        service.import_genblaze_bundle(second_campaign, ImportBundleRequest.model_validate(same_run_other_campaign))

    reused_asset = json.loads(FIXTURE.read_text())
    reused_asset["objects"][3]["source_id"] = "different-b2-manifest-descriptor"
    reused_asset["objects"][3]["inline_json"]["run"]["run_id"] = "different-b2-run"
    reused_asset["objects"][3]["inline_json"]["run"]["steps"][0]["run_id"] = "different-b2-run"
    reused_asset["objects"][3]["inline_json"]["run"]["steps"][0]["assets"][0]["sha256"] = "e" * 64
    for relationship in reused_asset["relationships"]:
        if relationship["source_id"] == "b2-run-sanitized-001":
            relationship["source_id"] = "different-b2-run"
        if relationship.get("target_id") == "b2-run-sanitized-001":
            relationship["target_id"] = "different-b2-run"
    with pytest.raises(ImportValidationError, match="import_conflict"):
        service.import_genblaze_bundle(first_campaign, ImportBundleRequest.model_validate(reused_asset))

    store.clear_import_campaign(first_campaign)
    assert not any(value[1] == first_campaign for value in store._source_fingerprint_index.values())
    assert service.import_genblaze_bundle(second_campaign, payload()).created is True


def test_missing_campaign_parent_and_lineage_failures() -> None:
    service = ProofStudioService()
    with pytest.raises(ImportValidationError, match="campaign_not_found"):
        service.import_genblaze_bundle("camp_missing", payload())
    campaign_id = campaign(service, "lineage")
    missing = json.loads(FIXTURE.read_text())
    missing["objects"][2]["inline_json"]["run"]["parent_run_id"] = "unknown-parent"
    missing["relationships"][0]["target_id"] = None; missing["relationships"][0]["missing_source_id"] = "unknown-parent"
    built = build_candidate(campaign_id, ImportBundleRequest.model_validate(missing))
    assert any(e.kind is EdgeKind.PARENT_RUN and e.missing_source_id == "unknown-parent" for e in built.edges)
    self_parent = json.loads(FIXTURE.read_text())
    self_parent["objects"][1]["inline_json"]["run"]["parent_run_id"] = "b0-run-sanitized-001"
    self_parent["relationships"].append({"kind":"parent_run","source_id":"b0-run-sanitized-001","target_id":"b0-run-sanitized-001","evidence_class":"recorded","hash_covered":False})
    with pytest.raises(LineageValidationError, match="self_parent"):
        build_candidate(campaign_id, ImportBundleRequest.model_validate(self_parent))
    cycle = json.loads(FIXTURE.read_text())
    cycle["objects"][1]["inline_json"]["run"]["parent_run_id"] = "b2-run-sanitized-001"
    cycle["relationships"].append({"kind":"parent_run","source_id":"b0-run-sanitized-001","target_id":"b2-run-sanitized-001","evidence_class":"recorded","hash_covered":False})
    with pytest.raises(LineageValidationError, match="lineage_cycle"):
        build_candidate(campaign_id, ImportBundleRequest.model_validate(cycle))


def test_atomic_failure_leaves_nothing_and_retry_succeeds() -> None:
    store = InMemoryStore(); service = ProofStudioService(store); campaign_id = campaign(service, "atomic")
    with pytest.raises(RuntimeError, match="injected_pre_commit_failure"):
        service.import_genblaze_bundle(campaign_id, payload(), fail_before_commit=True)
    snapshot = store.snapshot()
    assert snapshot["import_bundle_count"] == snapshot["import_node_count"] == snapshot["import_edge_count"] == 0
    result = service.import_genblaze_bundle(campaign_id, payload())
    assert result.created and store.snapshot()["import_bundle_count"] == 1


def test_cross_campaign_candidate_is_rejected_without_mutation() -> None:
    store = InMemoryStore(); service = ProofStudioService(store); campaign_id = campaign(service, "cross")
    candidate = build_candidate(campaign_id, payload())
    candidate.nodes[0] = candidate.nodes[0].model_copy(update={"campaign_id": "camp_other"})
    with pytest.raises(ImportValidationError, match="cross_campaign_lineage"):
        store.commit_import_candidate(candidate)
    assert store.snapshot()["import_bundle_count"] == 0
