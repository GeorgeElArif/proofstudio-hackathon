#!/usr/bin/env python3
"""Local smoke for deterministic frozen-fixture API initialization."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from proofstudio.api.app import create_app
from proofstudio.api.frozen_staging_fixture import (
    CANONICAL_CAMPAIGN_ID,
    CANONICAL_RUN_ID,
    DIGEST_REGISTRY_REL,
    ENVIRONMENT,
    ENV_FIXTURES_FROZEN,
    GOLDEN_REL,
    LINEAGE_REL,
    MANIFEST_REL,
    maybe_seed_frozen_staging_fixture,
)
from proofstudio.api.services import (
    NotFoundError,
    ProofStudioService,
    create_default_service,
)

ROOT = Path(__file__).resolve().parents[1]
TOKEN_ENV = "PROOFSTUDIO_INTERNAL_SERVICE_TOKEN"
TOKEN = "ps042c1-local-internal-token"


def restore_environment(original: dict[str, str | None]) -> None:
    for key, value in original.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


tracked_env = {
    key: os.environ.get(key)
    for key in (ENV_FIXTURES_FROZEN, ENVIRONMENT, TOKEN_ENV)
}

try:
    os.environ.pop(ENV_FIXTURES_FROZEN, None)
    os.environ[ENVIRONMENT] = "staging"

    empty = create_default_service()
    assert not empty.store.has_campaign(CANONICAL_CAMPAIGN_ID)
    assert not empty.store.has_run(CANONICAL_RUN_ID)

    os.environ[ENV_FIXTURES_FROZEN] = "true"
    os.environ[ENVIRONMENT] = "production"

    try:
        create_default_service()
    except RuntimeError as exc:
        assert str(exc) == "frozen_fixture_requires_staging_environment"
    else:
        raise AssertionError("non-staging frozen fixture did not fail closed")

    os.environ[ENVIRONMENT] = "staging"
    os.environ[TOKEN_ENV] = TOKEN

    first = create_default_service()

    campaign = first.get_campaign(CANONICAL_CAMPAIGN_ID)["campaign"]
    run = first.get_run(CANONICAL_RUN_ID)["run"]
    attempts = first.get_run_attempts(CANONICAL_RUN_ID)
    assets = first.get_run_assets(CANONICAL_RUN_ID)
    manifest = first.get_run_manifest(CANONICAL_RUN_ID)

    assert campaign["campaign_id"] == CANONICAL_CAMPAIGN_ID
    assert run["run_id"] == CANONICAL_RUN_ID
    assert run["campaign_id"] == CANONICAL_CAMPAIGN_ID
    assert run["status"] == "golden_demo_evidence_derived"
    assert attempts["attempt_count"] == 0
    assert assets["asset_count"] == 0
    assert manifest["ready"] is True
    assert manifest["in_memory_manifest_verify"] is True
    assert manifest["stored_manifest_verify"] is None

    bundles = first.list_imported_bundles(CANONICAL_CAMPAIGN_ID)
    assert len(bundles) == 1
    bundle_id = bundles[0].bundle_id

    lineage = first.get_imported_bundle(
        CANONICAL_CAMPAIGN_ID,
        bundle_id,
    )
    lineage_passport = first.get_imported_passport(
        CANONICAL_CAMPAIGN_ID,
        bundle_id,
    )

    assert lineage.bundle.campaign_id == CANONICAL_CAMPAIGN_ID
    assert len(lineage.nodes) == 16
    assert len(lineage.edges) == 16
    assert lineage_passport.campaign_id == CANONICAL_CAMPAIGN_ID

    application = create_app(first)
    assert application is not None

    headers = {"x-proofstudio-internal-token": TOKEN}

    with TestClient(application) as client:
        room = client.get(
            (
                f"/internal/campaigns/{CANONICAL_CAMPAIGN_ID}/proof-room"
                f"?runId={CANONICAL_RUN_ID}"
            ),
            headers=headers,
        )
        assert room.status_code == 200, room.text
        assert room.json()["selected_run"]["run_id"] == CANONICAL_RUN_ID

        private_passport = client.get(
            (
                f"/internal/campaigns/{CANONICAL_CAMPAIGN_ID}"
                f"/runs/{CANONICAL_RUN_ID}/passport"
            ),
            headers=headers,
        )
        assert private_passport.status_code == 200, private_passport.text

        lineage_list = client.get(
            f"/internal/campaigns/{CANONICAL_CAMPAIGN_ID}/import-bundles",
            headers=headers,
        )
        assert lineage_list.status_code == 200, lineage_list.text

        lineage_detail = client.get(
            (
                f"/internal/campaigns/{CANONICAL_CAMPAIGN_ID}"
                f"/import-bundles/{bundle_id}"
            ),
            headers=headers,
        )
        assert lineage_detail.status_code == 200, lineage_detail.text

        portable_passport = client.get(
            (
                f"/internal/campaigns/{CANONICAL_CAMPAIGN_ID}"
                f"/import-bundles/{bundle_id}/passport"
            ),
            headers=headers,
        )
        assert portable_passport.status_code == 200, portable_passport.text

        public_passport = client.get(
            f"/runs/{CANONICAL_RUN_ID}/passport"
        )
        assert public_passport.status_code == 200, public_passport.text
        assert (
            public_passport.json()["golden_demo_unlock"]["run_id"]
            == CANONICAL_RUN_ID
        )

    second = create_default_service()
    second_bundles = second.list_imported_bundles(
        CANONICAL_CAMPAIGN_ID
    )

    assert second.get_run(CANONICAL_RUN_ID)["run"]["run_id"] == CANONICAL_RUN_ID
    assert len(second_bundles) == 1
    assert second_bundles[0].bundle_id == bundle_id

    with tempfile.TemporaryDirectory() as temporary:
        temporary_root = Path(temporary)

        for relative in (
            DIGEST_REGISTRY_REL,
            GOLDEN_REL,
            MANIFEST_REL,
            LINEAGE_REL,
        ):
            destination = temporary_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)

        corrupted = temporary_root / GOLDEN_REL
        corrupted.write_bytes(corrupted.read_bytes() + b"\n")

        try:
            maybe_seed_frozen_staging_fixture(
                ProofStudioService(),
                repo_root=temporary_root,
            )
        except RuntimeError as exc:
            assert str(exc).startswith("frozen_fixture_digest_mismatch:")
        else:
            raise AssertionError("fixture digest mismatch did not fail closed")

    with tempfile.TemporaryDirectory() as temporary:
        temporary_root = Path(temporary)

        for relative in (
            DIGEST_REGISTRY_REL,
            GOLDEN_REL,
            MANIFEST_REL,
            LINEAGE_REL,
        ):
            destination = temporary_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)

        corrupted_lineage = temporary_root / LINEAGE_REL
        corrupted_lineage.write_bytes(
            corrupted_lineage.read_bytes() + b"\n"
        )

        try:
            maybe_seed_frozen_staging_fixture(
                ProofStudioService(),
                repo_root=temporary_root,
            )
        except RuntimeError as exc:
            assert str(exc) == (
                "frozen_fixture_lineage_digest_mismatch:"
                f"{LINEAGE_REL.as_posix()}"
            )
        else:
            raise AssertionError(
                "lineage digest mismatch did not fail closed"
            )

    try:
        empty.get_campaign(CANONICAL_CAMPAIGN_ID)
    except NotFoundError:
        pass
    else:
        raise AssertionError("flag-off service unexpectedly contained fixture")

    print(json.dumps({
        "ok": True,
        "campaign_id": CANONICAL_CAMPAIGN_ID,
        "run_id": CANONICAL_RUN_ID,
        "bundle_id": bundle_id,
        "nodes": 16,
        "edges": 16,
        "attempts": 0,
        "assets": 0,
        "provider_calls": 0,
        "b2_calls": 0,
        "restart_reconstruction": "pass",
        "digest_mismatch": "fail_closed",
        "public_passport": "preserved",
        "private_routes": "pass",
    }, sort_keys=True))

    print("FROZEN_STAGING_RUNTIME_SEED=PASS")
finally:
    restore_environment(tracked_env)
