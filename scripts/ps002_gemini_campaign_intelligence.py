#!/usr/bin/env python3
"""
PS-002: Gemini campaign intelligence + B2 + Genblaze manifest smoke test.
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
from google import genai
from google.genai import types

from genblaze_core.models.asset import Asset
from genblaze_core.pipeline.pipeline import Pipeline
from genblaze_core.storage.sink import ObjectStorageSink
from genblaze_s3.backend import S3StorageBackend


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_OUTPUT_DIR = Path(tempfile.gettempdir()) / "proofstudio-ps-002"
LOCAL_JSON_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps002-campaign-intelligence.json"
LOCAL_MARKDOWN_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps002-campaign-intelligence.md"
LOCAL_SUMMARY_PATH = LOCAL_OUTPUT_DIR / "last-run-summary.json"

PRIMARY_MODEL = os.getenv("GEMINI_STRATEGY_MODEL", "models/gemini-2.5-pro")
FALLBACK_MODEL = os.getenv("GEMINI_STRATEGY_FALLBACK_MODEL", "models/gemini-2.5-flash")

REQUIRED_ENV = [
    "B2_KEY_ID",
    "B2_APP_KEY",
    "B2_BUCKET",
    "B2_REGION",
    "GEMINI_API_KEY",
]

REQUIRED_TOP_LEVEL_KEYS = [
    "campaign",
    "audience",
    "positioning",
    "asset_system",
    "model_plan",
    "prompt_pack",
    "provenance_plan",
    "review_plan",
    "export_pack",
    "judge_demo_beats",
    "risks_and_mitigations",
]

FORBIDDEN_PROVIDER_PHRASES = [
    "Google" + " Media" + " Intelligence",
]

PROVIDER_PHRASE_REPLACEMENT = "an incorrect expansion of GMICloud"


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
        raise SystemExit(2)

    return {name: os.environ[name] for name in REQUIRED_ENV}


def campaign_brief() -> dict[str, Any]:
    return {
        "product": "ProofStudio",
        "one_liner": (
            "A provenance-aware AI media operations app that turns campaign briefs "
            "into verified media kits using Genblaze and Backblaze B2."
        ),
        "target_user": [
            "small marketing teams",
            "creator teams",
            "agencies",
            "brand operators who need reusable, auditable AI assets",
        ],
        "campaign_goal": (
            "Create a launch/demo campaign that proves ProofStudio is not just an AI generator. "
            "It is a system of record for briefs, prompts, generated media, manifests, review state, "
            "and export packs."
        ),
        "tone": [
            "premium",
            "technical but clear",
            "trust-first",
            "demo-ready",
            "not gimmicky",
        ],
        "channels": [
            "Devpost gallery",
            "3-minute demo video",
            "landing page hero",
            "product screenshots",
            "short social launch post",
        ],
        "mandatory_stack_story": [
            "Genblaze orchestrates media and intelligence pipelines.",
            "Backblaze B2 stores source assets, generated assets, manifests, logs, and exports.",
            "Gemini produces structured campaign intelligence and prompt packs.",
            "GMICloud image generation is prepared but currently requires credits for live generation.",
            "ElevenLabs can later create demo voiceover/audio assets.",
        ],
        "truth_constraints": [
            "Do not claim semantic truth or legal authenticity from SHA-256 manifests.",
            "Say the manifest proves recorded workflow integrity and byte-level verification.",
            "Do not hide provider billing limitations.",
            "Do not make C2PA claims unless implemented and verified.",
        ],
    }


def build_prompt(brief: dict[str, Any]) -> str:
    return f"""
You are the campaign strategist and media-ops planner inside ProofStudio.

Return STRICT JSON only. No markdown. No code fences.

Create a premium, judge-visible campaign intelligence package from this brief:

{json.dumps(brief, indent=2)}

Required top-level JSON keys:
{json.dumps(REQUIRED_TOP_LEVEL_KEYS, indent=2)}

Requirements:
- campaign: include title, one_liner, success_criteria, and demo_thesis.
- audience: define primary users, pain points, and usage context.
- positioning: explain why this is not a shallow AI generator.
- asset_system: define source assets, generated assets, derived assets, manifests, logs, export packs.
- model_plan: specify how Gemini, Genblaze, Backblaze B2, GMICloud, ElevenLabs, and optional future APIs should be used. Use the provider name exactly as GMICloud; do not invent or spell out expansions.
- prompt_pack: include image prompts, video prompts, voiceover prompt, landing copy prompt, metadata prompt, and review prompt.
- provenance_plan: specify what gets hashed, what gets stored, what gets verified, and what must not be claimed.
- review_plan: include approval states, reviewer checklist, rejection reasons, and export gate.
- export_pack: define exact files to export for judges and for a marketing team.
- judge_demo_beats: 8 to 12 steps for a tight demo narrative.
- risks_and_mitigations: include provider credits, model inconsistency, provenance overclaiming, provider naming mistakes, and demo fragility.

Make it specific to ProofStudio. Avoid generic SaaS language.
"""


def extract_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return text

    chunks: list[str] = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            part_text = getattr(part, "text", None)
            if part_text:
                chunks.append(part_text)

    return "\n".join(chunks).strip()


def parse_json_response(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        debug_path = LOCAL_OUTPUT_DIR / "failed-gemini-response.txt"
        LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        debug_path.write_text(text, encoding="utf-8")
        fail(f"Gemini response was not valid JSON. Saved raw response to {debug_path}. Error: {exc}")

    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in data]
    if missing:
        fail(f"Gemini JSON missing required top-level keys: {missing}")

    return data


def sanitize_provider_naming(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Remove known wrong provider-name expansions from judge-facing artifacts.

    We keep this as an explicit sanitizer instead of weakening the acceptance gate.
    The summary records whether sanitization was needed without repeating the bad phrase.
    """
    raw = json.dumps(data, ensure_ascii=False)
    replacement_count = 0

    for phrase in FORBIDDEN_PROVIDER_PHRASES:
        count = raw.count(phrase)
        if count:
            replacement_count += count
            raw = raw.replace(phrase, PROVIDER_PHRASE_REPLACEMENT)

    return json.loads(raw), {
        "sanitized": replacement_count > 0,
        "replacement_count": replacement_count,
    }


def generate_campaign_intelligence(api_key: str) -> tuple[str, dict[str, Any], dict[str, Any]]:
    client = genai.Client(api_key=api_key)
    brief = campaign_brief()
    prompt = build_prompt(brief)

    config = types.GenerateContentConfig(
        responseMimeType="application/json",
        temperature=0.35,
        maxOutputTokens=12000,
        systemInstruction=(
            "You are a senior product marketer, AI media pipeline architect, "
            "and hackathon demo strategist. Be concrete, implementation-aware, "
            "and honest about provenance limits."
        ),
    )

    errors: list[str] = []
    attempts: list[dict[str, str]] = []

    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            text = extract_text(response)
            if not text:
                raise RuntimeError("Gemini returned an empty text response.")

            data = parse_json_response(text)
            data, provider_naming = sanitize_provider_naming(data)
            metadata = {
                "model": model,
                "fallback_used": model != PRIMARY_MODEL,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "usage_metadata": str(getattr(response, "usage_metadata", "")),
                "model_attempts": attempts + [{"model": model, "status": "ok"}],
                "provider_naming": provider_naming,
            }
            return model, data, metadata
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            attempts.append({"model": model, "status": "failed", "error": error})
            errors.append(f"{model}: {error}")

    fail("Gemini campaign intelligence failed on all configured models:\n" + "\n".join(errors))


def to_markdown(data: dict[str, Any], metadata: dict[str, Any]) -> str:
    lines: list[str] = []

    lines.append("# ProofStudio Campaign Intelligence")
    lines.append("")
    lines.append(f"- Generated at: `{metadata['generated_at']}`")
    lines.append(f"- Gemini model: `{metadata['model']}`")
    lines.append(f"- Fallback used: `{metadata['fallback_used']}`")
    lines.append("")

    for key in REQUIRED_TOP_LEVEL_KEYS:
        value = data.get(key)
        title = key.replace("_", " ").title()
        lines.append(f"## {title}")
        lines.append("")
        if isinstance(value, (dict, list)):
            lines.append("```json")
            lines.append(json.dumps(value, indent=2, ensure_ascii=False))
            lines.append("```")
        else:
            lines.append(str(value))
        lines.append("")

    return "\n".join(lines)


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

    model, intelligence, gemini_metadata = generate_campaign_intelligence(env["GEMINI_API_KEY"])

    payload = {
        "proofstudio_artifact_type": "campaign_intelligence",
        "schema_version": "ps-002.1",
        "brief": campaign_brief(),
        "gemini": gemini_metadata,
        "campaign_intelligence": intelligence,
    }

    LOCAL_JSON_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    LOCAL_MARKDOWN_PATH.write_text(to_markdown(intelligence, gemini_metadata), encoding="utf-8")

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
        prefix="proofstudio/ps-002",
    )

    assets = [
        Asset(
            url=LOCAL_JSON_PATH.resolve().as_uri(),
            media_type="application/json",
            metadata={
                "proofstudio_test": "ps-002",
                "artifact_type": "campaign_intelligence_json",
                "gemini_model": model,
            },
        ),
        Asset(
            url=LOCAL_MARKDOWN_PATH.resolve().as_uri(),
            media_type="text/markdown",
            metadata={
                "proofstudio_test": "ps-002",
                "artifact_type": "campaign_intelligence_markdown",
                "gemini_model": model,
            },
        ),
    ]

    result = Pipeline.ingest(
        assets=assets,
        source="gemini-campaign-intelligence",
        source_metadata={
            "scenario": "PS-002",
            "description": (
                "Gemini-generated structured campaign intelligence package for ProofStudio, "
                "stored in B2 and verified with a Genblaze manifest."
            ),
            "gemini_model": model,
        },
        name="proofstudio-ps-002-gemini-campaign-intelligence",
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
        "proof": "PS-002 Gemini campaign intelligence + B2 + Genblaze manifest smoke test passed.",
        "gemini_model": model,
        "fallback_used": gemini_metadata["fallback_used"],
        "model_attempts": gemini_metadata["model_attempts"],
        "provider_naming": gemini_metadata["provider_naming"],
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
        "local_json": str(LOCAL_JSON_PATH),
        "local_markdown": str(LOCAL_MARKDOWN_PATH),
    }

    LOCAL_SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
