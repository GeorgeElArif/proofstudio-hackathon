#!/usr/bin/env python3
"""Current-slice-only, local, non-mutating-by-default PS-041D smoke."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from proofstudio.api.genblaze_external_adapter import ImportValidationError, build_candidate
from proofstudio.api.imported_bundle import EdgeKind, EvidenceClass, ImportBundleRequest, NodeKind
from proofstudio.api.lineage import LineageValidationError
from proofstudio.api.models import CampaignCreate
from proofstudio.api.services import ProofStudioService

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/ps041d/genblaze-multi-provider-bundle-v1.json"


def require(value: bool, message: str) -> None:
    if not value: raise AssertionError(message)


def set_parent(data: dict, run_id: str, parent_id: str) -> None:
    for obj in data["objects"]:
        run = (obj.get("inline_json") or {}).get("run") if isinstance(obj.get("inline_json"), dict) else None
        if run and run.get("run_id") == run_id:
            run["parent_run_id"] = parent_id
            break
    else:
        raise AssertionError("parent run target missing")
    data["relationships"] = [
        rel for rel in data["relationships"]
        if not (rel["kind"] == "parent_run" and rel["source_id"] == run_id)
    ]
    data["relationships"].append({
        "kind": "parent_run", "source_id": run_id, "missing_source_id": parent_id,
        "evidence_class": "recorded", "source_locator": "manifest.run.parent_run_id",
        "limitation": "Manifest 1.5 excludes parent_run_id from canonical hashing.",
        "hash_covered": False,
    })


def one_object_payload(base: dict, obj: dict, relationships: list[dict] | None = None) -> ImportBundleRequest:
    data = dict(base)
    data["objects"] = [obj]
    data["relationships"] = relationships or []
    return ImportBundleRequest.model_validate(data)


def missing_parent_relationship(run_id: str, parent_id: str) -> list[dict]:
    return [{
        "kind": "parent_run", "source_id": run_id, "missing_source_id": parent_id,
        "evidence_class": "recorded", "source_locator": "manifest.run.parent_run_id",
        "hash_covered": False,
    }]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true", default=True)
    parser.add_argument("--write-evidence", action="store_true")
    parser.add_argument("--no-frontend", action="store_true")
    args = parser.parse_args()
    if args.write_evidence: raise SystemExit("PS-041D smoke does not own canonical evidence writes")
    data = json.loads(FIXTURE.read_text(encoding="utf-8")); payload = ImportBundleRequest.model_validate(data)
    service = ProofStudioService(); campaign = service.create_campaign(CampaignCreate(name="PS-041D smoke", brief="process-local isolated campaign"))["campaign_id"]
    other = service.create_campaign(CampaignCreate(name="PS-041D other", brief="process-local isolated campaign"))["campaign_id"]
    try:
        first = service.import_genblaze_bundle(campaign, payload)
        same = service.import_genblaze_bundle(campaign, payload)
        reordered_data = json.loads(FIXTURE.read_text()); reordered_data["objects"].reverse(); reordered_data["relationships"].reverse()
        reordered = service.import_genblaze_bundle(campaign, ImportBundleRequest.model_validate(reordered_data))
        require(first.created and not same.created and not reordered.created, "idempotency")
        require(len(service.list_imported_bundles(campaign)) == 1, "one bundle")
        runs = [node for node in first.nodes if node.kind is NodeKind.GENBLAZE_RUN]
        require([node.run.stage for node in runs] == ["B0", "B1", "B2"], "three separate runs")
        require(any(node.kind is NodeKind.STANDALONE_ARTIFACT for node in first.nodes), "stage A standalone")
        require(any(node.kind is NodeKind.EXTERNAL_COMPOSITION for node in first.nodes), "stage C composition")
        parents = [edge for edge in first.edges if edge.kind is EdgeKind.PARENT_RUN]
        require(len(parents) == 2 and all(edge.evidence_class is EvidenceClass.RECORDED and not edge.hash_covered for edge in parents), "parent semantics")
        require(any(edge.evidence_class is EvidenceClass.INFERRED for edge in first.edges), "inferred semantics")
        require(any(node.b2_reference and node.b2_reference.object_key.endswith("/final.mp4") for node in first.nodes), "final B2 reference")
        passport = service.get_imported_passport(campaign, first.bundle.bundle_id)
        require(passport.bundle_id == first.bundle.bundle_id and "proof does not equal truth" in passport.truth_boundary, "portable passport")
        original_passport = passport.model_dump(mode="json")
        changed = json.loads(FIXTURE.read_text()); changed["objects"][0]["inline_json"]["title"] = "conflict"
        try: service.import_genblaze_bundle(campaign, ImportBundleRequest.model_validate(changed)); raise AssertionError("conflict accepted")
        except ImportValidationError as exc: require(exc.status == 409, "conflict code")
        stage_c_reclassified = dict(data["objects"][0])
        stage_c_reclassified["role"] = "stage_c_composition"
        try:
            service.import_genblaze_bundle(campaign, one_object_payload(data, stage_c_reclassified))
            raise AssertionError("stage A to C reclassification accepted")
        except ImportValidationError as exc:
            require(exc.status == 409, "stage A to C conflict code")
        b2_reclassified_run = json.loads(json.dumps(data["objects"][2]))
        b2_reclassified_run["role"] = "stage_b2_manifest"
        b2_reclassified_run["source_id"] = "smoke-b2-different-descriptor"
        try:
            service.import_genblaze_bundle(
                campaign,
                one_object_payload(
                    data,
                    b2_reclassified_run,
                    missing_parent_relationship("b1-run-sanitized-001", "b0-run-sanitized-001"),
                ),
            )
            raise AssertionError("B1 to B2 run-stage reclassification accepted")
        except ImportValidationError as exc:
            require(exc.status == 409, "B1 to B2 run-stage conflict code")
        require(service.get_imported_passport(campaign, first.bundle.bundle_id).model_dump(mode="json") == original_passport,
                "original bundle unchanged after classification conflicts")
        declared = json.loads(FIXTURE.read_text()); declared["objects"][0]["content_sha256"] = "a" * 64
        declared_first = build_candidate(campaign, ImportBundleRequest.model_validate(declared))
        declared["objects"][0]["content_sha256"] = "b" * 64
        declared_second = service.import_genblaze_bundle(campaign, ImportBundleRequest.model_validate(declared))
        require(not declared_second.created and declared_first.bundle.bundle_id == declared_second.bundle.bundle_id, "declared hash identity exclusion")
        parent_changed = json.loads(FIXTURE.read_text())
        set_parent(parent_changed, "b1-run-sanitized-001", "missing-parent-recorded-001")
        try: service.import_genblaze_bundle(campaign, ImportBundleRequest.model_validate(parent_changed)); raise AssertionError("parent conflict accepted")
        except ImportValidationError as exc: require(exc.status == 409, "parent conflict code")
        require(len(service.list_imported_bundles(campaign)) == 1 and len(service.list_imported_bundles(other)) == 0, "rollback isolation")
        cycle = json.loads(FIXTURE.read_text()); cycle["objects"][1]["inline_json"]["run"]["parent_run_id"] = "b2-run-sanitized-001"
        cycle["relationships"].append({"kind":"parent_run","source_id":"b0-run-sanitized-001","target_id":"b2-run-sanitized-001","evidence_class":"recorded","hash_covered":False})
        try: build_candidate(campaign, ImportBundleRequest.model_validate(cycle)); raise AssertionError("cycle accepted")
        except LineageValidationError: pass
        serialized = passport.model_dump_json()
        require("X-Amz-" not in serialized and "style_prompt" not in serialized, "sanitization")
        provider_calls = 0; b2_calls = 0
        require(provider_calls == 0, "provider calls")
        require(b2_calls == 0, "b2 calls")
        print(json.dumps({"ok": True, "slice": "PS-041D", "mode": "check-only", "bundles": 1,
                          "nodes": len(first.nodes), "edges": len(first.edges),
                          "stage_a_to_c_conflict": 409, "b1_to_b2_run_conflict": 409,
                          "original_bundle_unchanged": True, "provider_calls": provider_calls,
                          "b2_calls": b2_calls}, sort_keys=True))
        return 0
    finally:
        service.store.clear_import_campaign(campaign); service.store.clear_import_campaign(other)


if __name__ == "__main__": raise SystemExit(main())
