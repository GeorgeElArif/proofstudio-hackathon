#!/usr/bin/env python3
"""
PS-003: Gemini visual asset + B2 + Genblaze manifest smoke test.

What this proves:
- ProofStudio can generate a real visual campaign asset from a campaign prompt.
- Gemini visual/image-capable APIs are attempted transparently.
- The generated image, prompt packet, and provider note are saved locally.
- All artifacts are uploaded to Backblaze B2.
- Genblaze creates and stores a manifest.
- Stored manifest is read back and verified.
- The run must have zero transfer failures.

This script must not fake success. If all visual models are quota/billing blocked,
it fails and writes a local failure report.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

from genblaze_core.models.asset import Asset
from genblaze_core.pipeline.pipeline import Pipeline
from genblaze_core.storage.sink import ObjectStorageSink
from genblaze_s3.backend import S3StorageBackend


REPO_ROOT = Path(__file__).resolve().parents[1]

LOCAL_OUTPUT_DIR = Path(tempfile.gettempdir()) / "proofstudio-ps-003"
LOCAL_IMAGE_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps003-hero.png"
LOCAL_PROMPT_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps003-visual-prompt.json"
LOCAL_NOTE_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps003-provider-note.md"
LOCAL_FAILURE_PATH = LOCAL_OUTPUT_DIR / "failed-visual-attempts.json"
LOCAL_SUMMARY_PATH = LOCAL_OUTPUT_DIR / "last-run-summary.json"

REQUIRED_ENV = [
    "B2_KEY_ID",
    "B2_APP_KEY",
    "B2_BUCKET",
    "B2_REGION",
    "GEMINI_API_KEY",
]

CONTENT_IMAGE_MODELS = [
    os.getenv("GEMINI_IMAGE_MODEL_PRIMARY", "models/gemini-2.5-flash-image"),
    os.getenv("GEMINI_IMAGE_MODEL_FALLBACK_1", "models/gemini-3.1-flash-image"),
    os.getenv("GEMINI_IMAGE_MODEL_FALLBACK_2", "models/gemini-3-pro-image"),
]

IMAGEN_MODELS = [
    os.getenv("GEMINI_IMAGEN_MODEL_PRIMARY", "models/imagen-4.0-fast-generate-001"),
    os.getenv("GEMINI_IMAGEN_MODEL_FALLBACK_1", "models/imagen-4.0-generate-001"),
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


def visual_prompt_packet() -> dict[str, Any]:
    return {
        "artifact_type": "proofstudio_visual_generation_prompt",
        "schema_version": "ps-003.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "campaign": {
            "product": "ProofStudio",
            "thesis": (
                "A provenance-aware AI media operations app that turns campaign briefs "
                "into verified media kits using Genblaze and Backblaze B2."
            ),
            "audience": [
                "creator teams",
                "marketing teams",
                "agencies",
                "brand operators",
            ],
        },
        "visual_direction": {
            "format": "16:9 premium launch hero",
            "style": [
                "cinematic",
                "modern product UI",
                "high-trust",
                "technical but warm",
                "not generic SaaS",
                "not childish",
            ],
            "composition": (
                "A polished workstation scene showing an abstract ProofStudio interface: "
                "campaign brief on the left, generated media cards in the center, "
                "a visible provenance passport / manifest panel on the right, "
                "and a durable cloud storage layer represented subtly in the background."
            ),
            "avoid": [
                "tiny unreadable text",
                "fake brand logos",
                "medical/legal claims",
                "surveillance vibes",
                "overly busy dashboards",
                "cheap stock-photo look",
            ],
        },
        "prompt": (
            "Create a premium 16:9 hero image for ProofStudio, a provenance-aware AI media "
            "operations app. Show a refined product interface in a cinematic studio workspace. "
            "The scene should communicate: campaign brief to media assets, visible manifest/hash "
            "verification, durable cloud storage, review/export workflow, and trustworthy AI media "
            "operations. Use a polished modern visual style, subtle depth, glass and metal materials, "
            "clean interface cards, elegant lighting, and a serious hackathon-winning feel. "
            "No tiny readable UI text. No fake logos. No people required."
        ),
        "negative_prompt": (
            "generic SaaS dashboard, fake readable text, cluttered UI, cartoon style, childish look, "
            "stock photo, medical claims, legal claims, surveillance aesthetic, low resolution"
        ),
    }


def mime_to_ext(mime_type: str | None) -> str:
    if not mime_type:
        return ".png"

    if mime_type == "image/png":
        return ".png"
    if mime_type in {"image/jpeg", "image/jpg"}:
        return ".jpg"
    if mime_type == "image/webp":
        return ".webp"

    return mimetypes.guess_extension(mime_type) or ".bin"


def get_attr_any(obj: Any, names: list[str]) -> Any:
    for name in names:
        value = getattr(obj, name, None)
        if value is not None:
            return value
    return None


def decode_possible_bytes(value: Any) -> bytes | None:
    if value is None:
        return None

    if isinstance(value, bytes):
        return value

    if isinstance(value, str):
        try:
            return base64.b64decode(value)
        except Exception:
            return value.encode("utf-8")

    return None


def extract_inline_images_from_generate_content(response: Any) -> tuple[list[dict[str, Any]], str]:
    images: list[dict[str, Any]] = []
    text_chunks: list[str] = []

    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            part_text = get_attr_any(part, ["text"])
            if part_text:
                text_chunks.append(part_text)

            inline_data = get_attr_any(part, ["inline_data", "inlineData"])
            if not inline_data:
                continue

            mime_type = get_attr_any(inline_data, ["mime_type", "mimeType"])
            data = get_attr_any(inline_data, ["data"])

            image_bytes = decode_possible_bytes(data)
            if image_bytes and (not mime_type or str(mime_type).startswith("image/")):
                images.append(
                    {
                        "bytes": image_bytes,
                        "mime_type": mime_type or "image/png",
                    }
                )

    return images, "\n".join(text_chunks).strip()


def extract_images_from_generate_images(response: Any) -> tuple[list[dict[str, Any]], str]:
    images: list[dict[str, Any]] = []
    notes: list[str] = []

    generated_images = get_attr_any(response, ["generated_images", "generatedImages"]) or []

    for item in generated_images:
        image = get_attr_any(item, ["image"])
        if not image:
            continue

        image_bytes = get_attr_any(image, ["image_bytes", "imageBytes"])
        mime_type = get_attr_any(image, ["mime_type", "mimeType"]) or "image/png"

        decoded = decode_possible_bytes(image_bytes)
        if decoded:
            images.append(
                {
                    "bytes": decoded,
                    "mime_type": mime_type,
                }
            )

        rai_reason = get_attr_any(item, ["rai_filtered_reason", "raiFilteredReason"])
        if rai_reason:
            notes.append(f"RAI note: {rai_reason}")

    return images, "\n".join(notes).strip()


def save_first_image(images: list[dict[str, Any]]) -> tuple[Path, str]:
    if not images:
        fail("No image bytes were returned by the visual model.")

    first = images[0]
    image_bytes = first["bytes"]
    mime_type = first.get("mime_type") or "image/png"
    ext = mime_to_ext(mime_type)

    path = LOCAL_IMAGE_PATH.with_suffix(ext)
    path.write_bytes(image_bytes)

    return path, mime_type


def generate_visual_asset(api_key: str) -> tuple[Path, str, dict[str, Any]]:
    client = genai.Client(api_key=api_key)
    packet = visual_prompt_packet()
    prompt = packet["prompt"]

    attempts: list[dict[str, Any]] = []

    content_config = types.GenerateContentConfig(
        responseModalities=["TEXT", "IMAGE"],
        temperature=1.0,
    )

    for model in [m for m in CONTENT_IMAGE_MODELS if m]:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=content_config,
            )
            images, provider_text = extract_inline_images_from_generate_content(response)
            if not images:
                raise RuntimeError(
                    "generate_content returned no inline image data. "
                    f"Provider text: {provider_text[:500]}"
                )

            image_path, mime_type = save_first_image(images)
            attempts.append(
                {
                    "api_method": "generate_content",
                    "model": model,
                    "status": "ok",
                    "image_count": len(images),
                    "provider_text": provider_text,
                }
            )
            return image_path, mime_type, {
                "api_method": "generate_content",
                "model": model,
                "attempts": attempts,
                "prompt_packet": packet,
            }
        except Exception as exc:
            attempts.append(
                {
                    "api_method": "generate_content",
                    "model": model,
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    # Gemini Developer API mode rejects the negativePrompt config parameter.
    # Keep the negative guidance in the prompt text instead of using the config field.
    imagen_prompt = f"{prompt}\n\nAvoid: {packet['negative_prompt']}"

    image_config = types.GenerateImagesConfig(
        numberOfImages=1,
        aspectRatio="16:9",
        outputMimeType="image/png",
    )

    for model in [m for m in IMAGEN_MODELS if m]:
        try:
            response = client.models.generate_images(
                model=model,
                prompt=imagen_prompt,
                config=image_config,
            )
            images, provider_text = extract_images_from_generate_images(response)
            if not images:
                raise RuntimeError(
                    "generate_images returned no image data. "
                    f"Provider text: {provider_text[:500]}"
                )

            image_path, mime_type = save_first_image(images)
            attempts.append(
                {
                    "api_method": "generate_images",
                    "model": model,
                    "status": "ok",
                    "image_count": len(images),
                    "provider_text": provider_text,
                }
            )
            return image_path, mime_type, {
                "api_method": "generate_images",
                "model": model,
                "attempts": attempts,
                "prompt_packet": packet,
            }
        except Exception as exc:
            attempts.append(
                {
                    "api_method": "generate_images",
                    "model": model,
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    LOCAL_FAILURE_PATH.write_text(
        json.dumps(
            {
                "ok": False,
                "proof": "PS-003 visual generation did not produce an image.",
                "attempts": attempts,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    fail(f"All Gemini visual generation attempts failed. See {LOCAL_FAILURE_PATH}")


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
                    "metadata": asset.metadata,
                }
            )

    return assets


def main() -> None:
    env = require_env()
    LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image_path, image_mime_type, generation_metadata = generate_visual_asset(env["GEMINI_API_KEY"])

    prompt_packet = generation_metadata["prompt_packet"]

    LOCAL_PROMPT_PATH.write_text(
        json.dumps(
            {
                "proofstudio_artifact_type": "visual_prompt_packet",
                "schema_version": "ps-003.1",
                "generation": {
                    "api_method": generation_metadata["api_method"],
                    "model": generation_metadata["model"],
                    "attempts": generation_metadata["attempts"],
                },
                "prompt_packet": prompt_packet,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    LOCAL_NOTE_PATH.write_text(
        "\n".join(
            [
                "# PS-003 Visual Asset Provider Note",
                "",
                f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
                f"- API method: `{generation_metadata['api_method']}`",
                f"- Model: `{generation_metadata['model']}`",
                f"- Image MIME type: `{image_mime_type}`",
                "",
                "## Truth boundary",
                "",
                "This proves visual asset generation plus storage/manifest verification.",
                "It does not prove semantic truth, legal authenticity, or C2PA authenticity.",
                "The manifest proves recorded workflow integrity and byte-level verification.",
                "",
                "## Attempts",
                "",
                "```json",
                json.dumps(generation_metadata["attempts"], indent=2, ensure_ascii=False),
                "```",
            ]
        ),
        encoding="utf-8",
    )

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
        prefix="proofstudio/ps-003",
    )

    assets = [
        Asset(
            url=image_path.resolve().as_uri(),
            media_type=image_mime_type,
            metadata={
                "proofstudio_test": "ps-003",
                "artifact_type": "gemini_visual_asset",
                "gemini_model": generation_metadata["model"],
                "api_method": generation_metadata["api_method"],
            },
        ),
        Asset(
            url=LOCAL_PROMPT_PATH.resolve().as_uri(),
            media_type="application/json",
            metadata={
                "proofstudio_test": "ps-003",
                "artifact_type": "visual_prompt_packet",
                "gemini_model": generation_metadata["model"],
                "api_method": generation_metadata["api_method"],
            },
        ),
        Asset(
            url=LOCAL_NOTE_PATH.resolve().as_uri(),
            media_type="text/markdown",
            metadata={
                "proofstudio_test": "ps-003",
                "artifact_type": "provider_note",
                "gemini_model": generation_metadata["model"],
                "api_method": generation_metadata["api_method"],
            },
        ),
    ]

    result = Pipeline.ingest(
        assets=assets,
        source="gemini-visual-asset-generation",
        source_metadata={
            "scenario": "PS-003",
            "description": (
                "Gemini visual campaign asset generated from a ProofStudio prompt, "
                "stored in B2 and verified with a Genblaze manifest."
            ),
            "gemini_model": generation_metadata["model"],
            "api_method": generation_metadata["api_method"],
        },
        name="proofstudio-ps-003-gemini-visual-asset-proof",
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
        "proof": "PS-003 Gemini visual asset + B2 + Genblaze manifest smoke test passed.",
        "api_method": generation_metadata["api_method"],
        "gemini_model": generation_metadata["model"],
        "model_attempts": generation_metadata["attempts"],
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
        "local_image": str(image_path),
        "local_prompt_packet": str(LOCAL_PROMPT_PATH),
        "local_provider_note": str(LOCAL_NOTE_PATH),
    }

    LOCAL_SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
