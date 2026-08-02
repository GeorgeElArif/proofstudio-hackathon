#!/usr/bin/env python3
"""
PS-001B: ProofStudio live GMI + B2 + Genblaze smoke test.

What this proves:
- ProofStudio can create a source campaign image.
- Source media can be uploaded to Backblaze B2.
- A temporary presigned B2 URL can be used as GMI image input.
- Genblaze can run a live GMI image-edit generation step.
- Generated output can be uploaded to Backblaze B2.
- The manifest can be read back from B2 and verified.
- The run has zero asset transfer failures.

This may spend a small amount of GMI credits.
"""

from __future__ import annotations

import hashlib
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
from genblaze_gmicloud.image import GMICloudImageProvider
from genblaze_s3.backend import S3StorageBackend


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_OUTPUT_DIR = Path(tempfile.gettempdir()) / "proofstudio-ps-001b"
LOCAL_SOURCE_IMAGE_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps001b-source.png"
LOCAL_SUMMARY_PATH = LOCAL_OUTPUT_DIR / "last-run-summary.json"

MODEL_ID = "seededit-3-0-i2i-250628"

REQUIRED_ENV = [
    "B2_KEY_ID",
    "B2_APP_KEY",
    "B2_BUCKET",
    "B2_REGION",
    "GMI_API_KEY",
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
        print("Update your local .env file.")
        print("Never commit .env.")
        raise SystemExit(2)

    return {name: os.environ[name] for name in REQUIRED_ENV}


def create_source_campaign_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    width, height = 1200, 675
    image = Image.new("RGB", (width, height), color=(245, 241, 232))
    draw = ImageDraw.Draw(image)

    # Simple campaign-card source image. The live model should produce a variant.
    draw.rectangle((70, 70, width - 70, height - 70), outline=(35, 39, 47), width=4)
    draw.rectangle((110, 120, 540, 555), fill=(28, 32, 42))
    draw.ellipse((190, 205, 460, 475), fill=(224, 194, 132))
    draw.rectangle((620, 170, 1080, 245), fill=(28, 32, 42))
    draw.rectangle((620, 285, 980, 335), fill=(92, 98, 112))
    draw.rectangle((620, 365, 1040, 415), fill=(92, 98, 112))

    lines = [
        "ProofStudio",
        "Campaign Source Asset",
        "Generate a premium variant",
        datetime.now(timezone.utc).isoformat(),
    ]

    y = 470
    for line in lines:
        draw.text((620, y), line, fill=(28, 32, 42))
        y += 35

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

    create_source_campaign_image(LOCAL_SOURCE_IMAGE_PATH)

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
        prefix="proofstudio/ps-001b",
    )

    source_key = "proofstudio/ps-001b/source/proofstudio-ps001b-source.png"
    source_bytes = LOCAL_SOURCE_IMAGE_PATH.read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()

    source_durable_url = backend.put(
        source_key,
        source_bytes,
        content_type="image/png",
    )

    source_presigned_url = backend.get_url(source_key, expires_in=3600)

    provider = GMICloudImageProvider(api_key=env["GMI_API_KEY"])

    validation = provider.validate_model(MODEL_ID)
    validation_outcome = getattr(validation.outcome, "value", str(validation.outcome)).lower()
    if not validation_outcome.startswith("ok"):
        fail(f"GMI model validation failed for {MODEL_ID}: {validation}")

    source_asset = Asset(
        url=source_presigned_url,
        media_type="image/png",
        sha256=source_sha256,
        size_bytes=len(source_bytes),
        width=1200,
        height=675,
        metadata={
            "proofstudio_test": "ps-001b-source",
            "durable_b2_url": source_durable_url,
            "note": "Presigned URL used only so GMI can fetch the private B2 source image.",
        },
    )

    result = (
        Pipeline(
            "proofstudio-ps-001b-gmi-b2-generation-smoke",
            tenant_id="local",
            chain=False,
        )
        .step(
            provider,
            model=MODEL_ID,
            prompt=(
                "Create a premium marketing campaign variant from this source image. "
                "Keep the ProofStudio brand feeling: polished, cinematic, modern, "
                "high-trust, suitable for a hackathon demo asset. Do not add tiny unreadable text."
            ),
            external_inputs=[source_asset],
        )
        .run(
            sink=sink,
            timeout=240,
            pipeline_timeout=360,
            raise_on_failure=True,
            progress=False,
        )
    )

    if not result.manifest.verify():
        fail("In-memory manifest verification failed.")

    failures = transfer_failures(result.manifest)
    if failures:
        fail(f"Asset transfer failures reported: {failures}")

    stored_manifest = sink.read_manifest(result.run, verify=True)

    if not stored_manifest.verify():
        fail("Stored manifest verification failed after reading back from B2.")

    stored_failures = transfer_failures(stored_manifest)
    if stored_failures:
        fail(f"Stored manifest contains transfer failures: {stored_failures}")

    manifest_uri = result.manifest.manifest_uri or sink.manifest_url_for(result.run)

    summary = {
        "ok": True,
        "proof": "PS-001B live GMI generation + B2 + Genblaze manifest smoke test passed.",
        "model_id": MODEL_ID,
        "run_id": result.run.run_id,
        "run_status": str(result.run.status),
        "manifest_hash": result.manifest.canonical_hash,
        "manifest_uri": manifest_uri,
        "source_b2_url": source_durable_url,
        "source_sha256": source_sha256,
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
