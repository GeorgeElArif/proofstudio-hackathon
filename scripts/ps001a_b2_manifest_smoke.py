#!/usr/bin/env python3
"""
PS-001A: ProofStudio B2 + Genblaze manifest smoke test.

What this proves:
- A local ProofStudio test image can be represented as a Genblaze Asset.
- Genblaze can create a provenance manifest through Pipeline.ingest().
- ObjectStorageSink can upload the asset + manifest to Backblaze B2.
- The in-memory manifest verifies.
- The stored manifest can be read back from B2 and verifies again.
- The run has zero asset transfer failures.

This does NOT prove live AI generation yet.
That comes in PS-001B after model/provider selection.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from PIL import Image, ImageDraw

from genblaze_core.models.asset import Asset
from genblaze_core.pipeline.pipeline import Pipeline
from genblaze_core.storage.sink import ObjectStorageSink
from genblaze_s3.backend import S3StorageBackend


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_OUTPUT_DIR = Path(tempfile.gettempdir()) / "proofstudio-ps-001a"
LOCAL_IMAGE_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps001a-smoke.png"
LOCAL_SUMMARY_PATH = LOCAL_OUTPUT_DIR / "last-run-summary.json"

REQUIRED_ENV = [
    "B2_KEY_ID",
    "B2_APP_KEY",
    "B2_BUCKET",
    "B2_REGION",
]


def fail(message: str, code: int = 1) -> None:
    print(f"❌ {message}", file=sys.stderr)
    raise SystemExit(code)


def require_env() -> dict[str, str]:
    load_dotenv(REPO_ROOT / ".env")

    missing = [name for name in REQUIRED_ENV if not os.getenv(name)]
    if missing:
        print("❌ Missing required environment variables:")
        for name in missing:
            print(f"   - {name}")
        print("")
        print("Create a local .env file from .env.example.")
        print("Never commit .env.")
        raise SystemExit(2)

    return {name: os.environ[name] for name in REQUIRED_ENV}


def create_local_test_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    width, height = 1200, 675
    image = Image.new("RGB", (width, height), color=(18, 22, 33))
    draw = ImageDraw.Draw(image)

    lines = [
        "ProofStudio",
        "PS-001A B2 + Genblaze Manifest Smoke",
        datetime.now(timezone.utc).isoformat(),
    ]

    y = 230
    for line in lines:
        draw.text((80, y), line, fill=(245, 245, 245))
        y += 70

    draw.rectangle((70, 80, width - 70, height - 80), outline=(120, 120, 120), width=3)
    image.save(path, format="PNG")


def transfer_failures(manifest: Any) -> list[Any]:
    failures = getattr(manifest, "transfer_failures", None)
    return list(failures or [])


def summarize_assets(result: Any) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []

    for step in result.run.steps:
        for asset in step.assets:
            assets.append(
                {
                    "asset_id": asset.asset_id,
                    "url": asset.url,
                    "media_type": asset.media_type,
                    "sha256": asset.sha256,
                    "size_bytes": asset.size_bytes,
                    "width": asset.width,
                    "height": asset.height,
                    "metadata": asset.metadata,
                }
            )

    return assets


def main() -> None:
    env = require_env()

    create_local_test_image(LOCAL_IMAGE_PATH)

    backend = S3StorageBackend.for_backblaze(
        bucket=env["B2_BUCKET"],
        region=env["B2_REGION"],
        key_id=env["B2_KEY_ID"],
        app_key=env["B2_APP_KEY"],
        auto_lifecycle=False,
        preflight=True,
    )

    sink = ObjectStorageSink(
        backend,
        prefix="proofstudio/ps-001a",
    )

    asset = Asset(
        url=LOCAL_IMAGE_PATH.resolve().as_uri(),
        media_type="image/png",
        width=1200,
        height=675,
        metadata={
            "proofstudio_test": "ps-001a",
            "purpose": "local smoke asset for B2 + Genblaze manifest verification",
        },
    )

    # Important:
    # Do not pass sink into Pipeline.ingest().
    # We create the manifest first, then call sink.write_run() once.
    # This avoids double-transferring a private B2 durable URL.
    result = Pipeline.ingest(
        assets=[asset],
        source="proofstudio-local-smoke",
        source_metadata={
            "scenario": "PS-001A",
            "description": "Local generated image ingested into Genblaze and stored in Backblaze B2.",
            "created_by": "ProofStudio smoke script",
        },
        name="proofstudio-ps-001a-b2-manifest-smoke",
        tenant_id="local",
    )

    sink.write_run(result.run, result.manifest)

    if not result.manifest.verify():
        fail("In-memory manifest verification failed after B2 write.")

    failures = transfer_failures(result.manifest)
    if failures:
        fail(f"Asset transfer failures reported after B2 write: {failures}")

    stored_manifest = sink.read_manifest(result.run, verify=True)

    if not stored_manifest.verify():
        fail("Stored manifest verification failed after reading back from B2.")

    stored_failures = transfer_failures(stored_manifest)
    if stored_failures:
        fail(f"Stored manifest contains transfer failures: {stored_failures}")

    manifest_uri = result.manifest.manifest_uri or sink.manifest_url_for(result.run)

    summary = {
        "ok": True,
        "proof": "PS-001A B2 + Genblaze manifest smoke test passed with zero transfer failures.",
        "run_id": result.run.run_id,
        "run_status": str(result.run.status),
        "manifest_hash": result.manifest.canonical_hash,
        "manifest_uri": manifest_uri,
        "in_memory_manifest_verify": result.manifest.verify(),
        "stored_manifest_verify": stored_manifest.verify(),
        "transfer_failures": failures,
        "stored_transfer_failures": stored_failures,
        "asset_count": len(summarize_assets(result)),
        "assets": summarize_assets(result),
    }

    LOCAL_SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
