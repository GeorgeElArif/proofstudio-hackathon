#!/usr/bin/env python3
"""
PS-007: Live ProviderRouter Chain smoke test.

What this proves:
- The reusable PS-006 ProviderRouter core drives real live providers end-to-end.
- Cloudflare Workers AI is the primary; Pollinations is the no-key fallback.
- Every provider attempt is recorded as a full ProviderAttempt record in a
  normalized attempt ledger. Skipped, failed, and successful attempts are all
  preserved. No compact attempt records are written to proof artifacts.
- The router result is the authority for which provider won. The winning live
  provider exposes its real image bytes and byte-detected MIME through safe
  instance attributes (``last_image_bytes`` / ``last_image_mime``) for this
  script to persist, hash, and upload. No fake image is ever written.
- On success the generated image, prompt packet, full attempt ledger, and
  provider note are stored in Backblaze B2 through the reusable Genblaze
  helper. The Genblaze manifest is written to B2, read back, and verified.
  The run must have zero transfer failures.
- On all-fail/all-skip a failed-provider-attempts report is written locally,
  no fake image is written, nothing is uploaded, and the script exits non-zero.

Truth boundary: this proves live provider routing, fallback behavior, evidence
capture, B2 storage, Genblaze manifest writing, and byte-level manifest
verification. It does not prove semantic truth, legal authenticity, human
authorship, or C2PA authenticity.

This script does not fake success. PS-004, PS-005, and PS-006 scripts are not
modified.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from proofstudio.providers import (  # noqa: E402
    LiveCloudflareProvider,
    LivePollinationsProvider,
    ProviderRouter,
)
from proofstudio.providers.live_cloudflare import (  # noqa: E402
    DEFAULT_PRIMARY_MODEL as CLOUDFLARE_DEFAULT_MODEL,
    detect_image_mime_from_bytes as detect_mime_from_bytes,
)
from proofstudio.providers.live_pollinations import is_disabled_env  # noqa: E402
from proofstudio.providers.types import (  # noqa: E402
    NS_OK,
    NS_QUOTA_OR_BILLING_BLOCKED,
    NS_SKIPPED_DISABLED,
    NS_SKIPPED_MISSING_KEY,
    ProviderAttempt,
    ProviderJob,
)
from proofstudio.provenance.genblaze_store import (  # noqa: E402
    AssetSpec,
    GenblazeStore,
)


LOCAL_OUTPUT_DIR = Path(tempfile.gettempdir()) / "proofstudio-ps-007"
LOCAL_IMAGE_STEM = LOCAL_OUTPUT_DIR / "proofstudio-ps007-hero"
LOCAL_PROMPT_PACKET_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps007-prompt-packet.json"
LOCAL_LEDGER_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps007-attempt-ledger.json"
LOCAL_NOTE_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps007-provider-note.md"
LOCAL_FAILURE_PATH = LOCAL_OUTPUT_DIR / "failed-provider-attempts.json"
LOCAL_SUMMARY_PATH = LOCAL_OUTPUT_DIR / "last-run-summary.json"

B2_PREFIX = "proofstudio/ps-007"

B2_REQUIRED_ENV = [
    "B2_KEY_ID",
    "B2_APP_KEY",
    "B2_BUCKET",
    "B2_REGION",
]

JOB_TYPE = "image_generation"

# Full required attempt-ledger schema per specs/10-attempt-ledger-contract.md
# section 4 and specs/14-ps-006-provider-router-core.md section 7. Every
# attempt written to the local ledger JSON must carry every field below.
REQUIRED_ATTEMPT_FIELDS = (
    "attempt_id",
    "attempt_index",
    "provider",
    "model",
    "api_method",
    "job_type",
    "status",
    "normalized_status",
    "started_at",
    "finished_at",
    "latency_ms",
    "retryable",
    "fallback_allowed",
    "skip_reason",
    "raw_error_type",
    "sanitized_error_message",
    "estimated_cost",
    "free_or_paid",
    "output_asset_refs",
    "notes",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fail(message: str, code: int = 1) -> None:
    print(f"FAIL {message}", file=sys.stderr)
    raise SystemExit(code)


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mime_to_ext(mime_type: str | None) -> str:
    if not mime_type:
        return ".png"
    if mime_type == "image/png":
        return ".png"
    if mime_type in {"image/jpeg", "image/jpg"}:
        return ".jpg"
    if mime_type == "image/webp":
        return ".webp"
    if mime_type == "image/gif":
        return ".gif"
    return mimetypes.guess_extension(mime_type) or ".bin"


def require_b2_env() -> dict[str, str]:
    load_dotenv(REPO_ROOT / ".env")
    missing = [name for name in B2_REQUIRED_ENV if not os.getenv(name)]
    if missing:
        print("Missing required B2 environment variables:", file=sys.stderr)
        for name in missing:
            print(f"   - {name}", file=sys.stderr)
        print(
            "Update your local .env file. Never commit .env.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return {name: os.environ[name] for name in B2_REQUIRED_ENV}


def build_prompt_packet(budget_mode: str) -> dict[str, Any]:
    return {
        "artifact_type": "proofstudio_visual_generation_prompt",
        "schema_version": "ps-007.1",
        "created_at": now_iso(),
        "provider_chain": [
            "cloudflare-workers-ai",
            "pollinations",
        ],
        "job_type": JOB_TYPE,
        "budget_mode": budget_mode,
        "campaign": {
            "product": "ProofStudio",
            "thesis": (
                "A provenance-aware AI media operations app that turns campaign "
                "briefs into verified media kits using Genblaze and Backblaze B2."
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
                "A polished workstation scene showing an abstract ProofStudio "
                "interface: campaign brief on the left, generated media cards "
                "in the center, a visible provenance passport / manifest panel "
                "on the right, and a durable cloud storage layer represented "
                "subtly in the background."
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
            "Create a premium 16:9 hero image for ProofStudio, a provenance-aware "
            "AI media operations app. Show a refined product interface in a "
            "cinematic studio workspace. The scene should communicate: campaign "
            "brief to media assets, visible manifest/hash verification, durable "
            "cloud storage, review/export workflow, and trustworthy AI media "
            "operations. Use a polished modern visual style, subtle depth, glass "
            "and metal materials, clean interface cards, elegant lighting, and a "
            "serious hackathon-winning feel. No tiny readable UI text. No fake "
            "logos. No people required."
        ),
        "negative_prompt": (
            "generic SaaS dashboard, fake readable text, cluttered UI, cartoon "
            "style, childish look, stock photo, medical claims, legal claims, "
            "surveillance aesthetic, low resolution"
        ),
    }


def build_providers() -> tuple[LiveCloudflareProvider, LivePollinationsProvider]:
    cloudflare = LiveCloudflareProvider(
        account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID"),
        api_token=os.getenv("CLOUDFLARE_API_TOKEN"),
        model=os.getenv("CLOUDFLARE_IMAGE_MODEL_PRIMARY") or CLOUDFLARE_DEFAULT_MODEL,
    )

    pollinations = LivePollinationsProvider(
        enabled=None if os.getenv("POLLINATIONS_ENABLED") is None else (
            not is_disabled_env(os.getenv("POLLINATIONS_ENABLED"))
        ),
        width=os.getenv("POLLINATIONS_WIDTH") or None,
        height=os.getenv("POLLINATIONS_HEIGHT") or None,
        model_name=os.getenv("POLLINATIONS_MODEL_NAME") or None,
    )
    return cloudflare, pollinations


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def validate_full_attempt_schema(attempts: list[dict[str, Any]]) -> list[str]:
    """Validate every attempt ledger record carries all required fields.

    This runs BEFORE any success is printed. If it returns any errors the
    smoke run must fail. Required fields come from
    specs/10-attempt-ledger-contract.md section 4 and
    specs/14-ps-006-provider-router-core.md section 7.
    """
    errors: list[str] = []
    if not isinstance(attempts, list):
        return [f"attempts must be a list, got {type(attempts).__name__}"]
    if not attempts:
        return ["attempts must contain at least one record"]
    for index, attempt in enumerate(attempts):
        if not isinstance(attempt, dict):
            errors.append(
                f"attempt[{index}]: must be a dict, got {type(attempt).__name__}"
            )
            continue
        for field_name in REQUIRED_ATTEMPT_FIELDS:
            if field_name not in attempt:
                errors.append(
                    f"attempt[{index}]: missing required field {field_name!r}"
                )
    return errors


def attempt_to_full_dict(attempt: ProviderAttempt) -> dict[str, Any]:
    """Return the full ProviderAttempt.to_dict() record.

    No compact records are ever written to proof artifacts. The router result
    is the authority; we only serialize what the router emitted.
    """
    return attempt.to_dict()


def attempts_compact(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compact attempt view for the human-readable summary block.

    This is for readability inside the printed/written summary only. The
    separate attempt-ledger JSON file always carries the full records.
    """
    return [
        {
            "attempt_index": a["attempt_index"],
            "provider": a["provider"],
            "model": a["model"],
            "status": a["status"],
            "normalized_status": a["normalized_status"],
            "latency_ms": a["latency_ms"],
            "retryable": a["retryable"],
            "fallback_allowed": a["fallback_allowed"],
            "skip_reason": a["skip_reason"],
            "raw_error_type": a["raw_error_type"],
            "sanitized_error_message": a["sanitized_error_message"],
        }
        for a in attempts
    ]


def build_ledger(
    *,
    attempts_full: list[dict[str, Any]],
    final_status: str,
    selected_provider: str | None,
    selected_model: str | None,
    fallback_used: bool,
    budget_mode: str,
    output_assets: list[dict[str, Any]] | None = None,
    b2_artifacts: list[dict[str, Any]] | None = None,
    manifest_uri: str | None = None,
    manifest_hash: str | None = None,
) -> dict[str, Any]:
    run_id = uuid.uuid4().hex
    created_at = attempts_full[0]["started_at"] if attempts_full else now_iso()
    completed_at = attempts_full[-1]["finished_at"] if attempts_full else now_iso()
    return {
        "ledger_id": f"ps-007-{run_id}",
        "campaign_id": "proofstudio-launch",
        "job_id": run_id,
        "job_type": JOB_TYPE,
        "budget_mode": budget_mode,
        "created_at": created_at,
        "completed_at": completed_at,
        "final_status": final_status,
        "selected_provider": selected_provider,
        "selected_model": selected_model,
        "fallback_used": fallback_used,
        "attempts": attempts_full,
        "output_assets": output_assets or [],
        "b2_artifacts": b2_artifacts or [],
        "manifest_uri": manifest_uri,
        "manifest_hash": manifest_hash,
        "truth_boundary": (
            "Manifest proves recorded workflow integrity and byte-level asset "
            "verification only. It does not prove semantic truth, legal "
            "authenticity, human authorship, or C2PA authenticity."
        ),
    }


def write_failed_provider_attempts(
    attempts_full: list[dict[str, Any]],
    *,
    reason: str,
    fallback_used: bool,
    budget_mode: str,
) -> None:
    payload = {
        "ok": False,
        "proof": "PS-007 provider chain did not produce a visual asset.",
        "job_type": JOB_TYPE,
        "budget_mode": budget_mode,
        "reason": reason,
        "fallback_used": fallback_used,
        "attempt_count": len(attempts_full),
        "attempts": attempts_full,
        "written_at": now_iso(),
    }
    write_json(LOCAL_FAILURE_PATH, payload)


def write_local_prompt_packet(
    packet: dict[str, Any],
    *,
    selected: dict[str, Any],
    budget_mode: str,
) -> None:
    payload = {
        "proofstudio_artifact_type": "visual_prompt_packet",
        "schema_version": "ps-007.1",
        "job_type": JOB_TYPE,
        "budget_mode": budget_mode,
        "selected": selected,
        "prompt_packet": packet,
    }
    write_json(LOCAL_PROMPT_PACKET_PATH, payload)


def write_provider_note(
    *,
    ledger: dict[str, Any],
    image_path: Path,
    image_mime_type: str,
    image_sha: str,
    fallback_used: bool,
) -> None:
    selected_provider = ledger.get("selected_provider") or "(none)"
    selected_model = ledger.get("selected_model") or "(none)"
    lines = [
        "# PS-007 Live ProviderRouter Chain Provider Note",
        "",
        f"- Generated at: `{ledger.get('completed_at')}`",
        f"- Selected provider: `{selected_provider}`",
        f"- Selected model: `{selected_model}`",
        f"- Fallback used: `{fallback_used}`",
        f"- Job type: `{JOB_TYPE}`",
        f"- Final status: `{ledger.get('final_status')}`",
        f"- Local image: `{image_path}`",
        f"- Image MIME type: `{image_mime_type}`",
        f"- Image SHA-256: `{image_sha}`",
        f"- Manifest URI: `{ledger.get('manifest_uri')}`",
        f"- Manifest hash: `{ledger.get('manifest_hash')}`",
        "",
        "## Truth boundary",
        "",
        "PS-007 proves live provider routing, fallback behavior, evidence capture,",
        "B2 storage, Genblaze manifest writing, and byte-level manifest verification.",
        "It does not prove semantic truth, legal authenticity, human authorship,",
        "or C2PA authenticity. The manifest proves recorded workflow integrity and",
        "byte-level asset verification only.",
        "",
        "## Provider chain",
        "",
        "1. Cloudflare Workers AI (primary)",
        "2. Pollinations (no-key fallback)",
        "",
        "## Attempt summary",
        "",
        "| # | provider | model | status | normalized | latency_ms |",
        "|---|----------|-------|--------|------------|-----------|",
    ]

    for attempt in ledger.get("attempts", []):
        lines.append(
            f"| {attempt.get('attempt_index')} "
            f"| `{attempt.get('provider')}` "
            f"| `{attempt.get('model')}` "
            f"| {attempt.get('status')} "
            f"| {attempt.get('normalized_status')} "
            f"| {attempt.get('latency_ms')} |"
        )

    lines.extend(
        [
            "",
            "## Full attempt ledger",
            "",
            "```json",
            json.dumps(ledger.get("attempts", []), indent=2, ensure_ascii=False),
            "```",
        ]
    )

    LOCAL_NOTE_PATH.write_text("\n".join(lines), encoding="utf-8")


def pick_winning_provider(
    providers: list[Any],
    selected_provider_id: str | None,
) -> Any | None:
    if not selected_provider_id:
        return None
    for provider in providers:
        if getattr(provider, "provider_id", None) == selected_provider_id:
            return provider
    return None


def write_blocked_summary(
    *,
    reason: str,
    attempts_full: list[dict[str, Any]],
    fallback_used: bool,
    budget_mode: str,
) -> dict[str, Any]:
    summary = {
        "ok": False,
        "proof": "PS-007 blocked: no provider in the chain produced a visual asset.",
        "slice": "PS-007",
        "job_type": JOB_TYPE,
        "budget_mode": budget_mode,
        "final_status": "blocked",
        "fallback_used": fallback_used,
        "attempt_count": len(attempts_full),
        "attempts": attempts_compact(attempts_full),
        "local_failure_report": str(LOCAL_FAILURE_PATH),
        "local_summary": str(LOCAL_SUMMARY_PATH),
        "next_step": (
            "Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN for the primary "
            "provider, and ensure POLLINATIONS_ENABLED is unset or true for the "
            "fallback. Re-run the smoke script."
        ),
        "written_at": now_iso(),
    }
    write_json(LOCAL_SUMMARY_PATH, summary)
    return summary


def main() -> None:
    LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    b2_env = require_b2_env()
    budget_mode = os.getenv("PROOFSTUDIO_BUDGET_MODE", "free-only").strip() or "free-only"

    packet = build_prompt_packet(budget_mode=budget_mode)
    prompt_text = packet["prompt"]

    cloudflare, pollinations = build_providers()
    providers = [cloudflare, pollinations]

    router = ProviderRouter(providers=providers)

    job = ProviderJob(
        job_type=JOB_TYPE,
        prompt=prompt_text,
        budget_mode=budget_mode,
        campaign_id="proofstudio-launch",
    )

    result = router.route(job)

    # The router is the authority for attempt evidence. Every attempt here is
    # a real ProviderAttempt object emitted by the router; we serialize each
    # via to_dict() (full schema). No compact records are written to the
    # attempt ledger JSON.
    attempts_full: list[dict[str, Any]] = [
        attempt_to_full_dict(attempt) for attempt in result.attempts
    ]

    # Schema-gate the full attempt ledger BEFORE doing anything else. If any
    # required field is missing, fail loudly. No post-run JSON normalizer.
    schema_errors = validate_full_attempt_schema(attempts_full)
    if schema_errors:
        # Still write evidence so operators can see the bad records.
        write_json(LOCAL_LEDGER_PATH, {"attempts": attempts_full})
        write_failed_provider_attempts(
            attempts_full,
            reason=(
                "PS-007 attempt ledger schema validation failed: "
                + "; ".join(schema_errors)
            ),
            fallback_used=result.fallback_used,
            budget_mode=budget_mode,
        )
        blocked = write_blocked_summary(
            reason="Attempt ledger schema validation failed.",
            attempts_full=attempts_full,
            fallback_used=result.fallback_used,
            budget_mode=budget_mode,
        )
        print(json.dumps(blocked, indent=2, ensure_ascii=False))
        for err in schema_errors:
            print(f"   - SCHEMA ERROR: {err}", file=sys.stderr)
        fail("PS-007 attempt ledger schema validation failed.")

    # All providers failed or skipped: preserve evidence, do not fake anything.
    if not result.ok:
        write_json(LOCAL_LEDGER_PATH, {"attempts": attempts_full})
        write_failed_provider_attempts(
            attempts_full,
            reason=(
                "All providers in the PS-007 chain failed or were skipped. "
                "No image generated. No fake image written. No upload performed."
            ),
            fallback_used=result.fallback_used,
            budget_mode=budget_mode,
        )
        blocked = write_blocked_summary(
            reason="All providers failed or skipped.",
            attempts_full=attempts_full,
            fallback_used=result.fallback_used,
            budget_mode=budget_mode,
        )
        print(json.dumps(blocked, indent=2, ensure_ascii=False))
        fail(
            "PS-007 blocked: all providers failed or skipped. "
            f"See {LOCAL_FAILURE_PATH}."
        )

    # A provider succeeded. The router result is the authority; the winning
    # live provider exposes real image bytes through a safe instance attribute.
    winner = pick_winning_provider(providers, result.selected_provider)
    if winner is None:
        write_json(LOCAL_LEDGER_PATH, {"attempts": attempts_full})
        write_failed_provider_attempts(
            attempts_full,
            reason=(
                f"Router reported selected_provider={result.selected_provider!r} "
                "but no matching provider instance was found."
            ),
            fallback_used=result.fallback_used,
            budget_mode=budget_mode,
        )
        blocked = write_blocked_summary(
            reason="Selected provider instance not found.",
            attempts_full=attempts_full,
            fallback_used=result.fallback_used,
            budget_mode=budget_mode,
        )
        print(json.dumps(blocked, indent=2, ensure_ascii=False))
        fail("PS-007 failed: winning provider instance not found.")

    image_bytes = getattr(winner, "last_image_bytes", None)
    image_mime_from_provider = getattr(winner, "last_image_mime", None)

    if not image_bytes:
        write_json(LOCAL_LEDGER_PATH, {"attempts": attempts_full})
        write_failed_provider_attempts(
            attempts_full,
            reason=(
                f"Provider {result.selected_provider!r} was selected by the "
                "router but did not expose real image bytes. No fake image "
                "written."
            ),
            fallback_used=result.fallback_used,
            budget_mode=budget_mode,
        )
        blocked = write_blocked_summary(
            reason="Selected provider exposed no image bytes.",
            attempts_full=attempts_full,
            fallback_used=result.fallback_used,
            budget_mode=budget_mode,
        )
        print(json.dumps(blocked, indent=2, ensure_ascii=False))
        fail("PS-007 failed: selected provider had no image bytes.")

    # MIME detection from real bytes. Never trust only headers.
    detected_mime = detect_mime_from_bytes(image_bytes, image_mime_from_provider)
    if not detected_mime.startswith("image/"):
        write_json(LOCAL_LEDGER_PATH, {"attempts": attempts_full})
        write_failed_provider_attempts(
            attempts_full,
            reason=(
                f"Selected provider returned non-image bytes (detected mime="
                f"{detected_mime!r}). No fake image written."
            ),
            fallback_used=result.fallback_used,
            budget_mode=budget_mode,
        )
        blocked = write_blocked_summary(
            reason="Selected provider returned non-image bytes.",
            attempts_full=attempts_full,
            fallback_used=result.fallback_used,
            budget_mode=budget_mode,
        )
        print(json.dumps(blocked, indent=2, ensure_ascii=False))
        fail("PS-007 failed: selected provider returned non-image bytes.")

    if (
        image_mime_from_provider
        and detected_mime != image_mime_from_provider
    ):
        print(
            f"INFO image MIME corrected from provider value "
            f"{image_mime_from_provider!r} to byte-detected value "
            f"{detected_mime!r}."
        )

    ext = mime_to_ext(detected_mime)
    image_path = LOCAL_IMAGE_STEM.with_suffix(ext)
    image_path.write_bytes(image_bytes)

    image_sha = sha256_of_file(image_path)

    # Augment the selected attempt's output_asset_refs with the real on-disk
    # references. This is still a full ProviderAttempt.to_dict() record (all
    # required fields present); we only enrich the refs now that we know the
    # local path and hash.
    selected_index = result.selected_attempt_index
    if selected_index is not None and 0 <= selected_index < len(attempts_full):
        attempts_full[selected_index]["output_asset_refs"] = [
            {
                "kind": "generated_image",
                "provider": result.selected_provider,
                "model": result.selected_model,
                "api_method": attempts_full[selected_index].get("api_method"),
                "local_path": str(image_path),
                "media_type": detected_mime,
                "sha256": image_sha,
                "size_bytes": image_path.stat().st_size,
                "produced_real_media": True,
            }
        ]

    write_local_prompt_packet(
        packet,
        selected={
            "provider": result.selected_provider,
            "model": result.selected_model,
            "api_method": attempts_full[selected_index].get("api_method")
            if selected_index is not None
            else None,
            "image_mime_type": detected_mime,
            "image_sha256": image_sha,
            "fallback_used": result.fallback_used,
        },
        budget_mode=budget_mode,
    )

    # Pre-upload ledger; will be rewritten after B2/manifest info is known.
    ledger_pre_upload = build_ledger(
        attempts_full=attempts_full,
        final_status="succeeded",
        selected_provider=result.selected_provider,
        selected_model=result.selected_model,
        fallback_used=result.fallback_used,
        budget_mode=budget_mode,
        output_assets=[
            {
                "kind": "generated_image",
                "local_path": str(image_path),
                "media_type": detected_mime,
                "sha256": image_sha,
                "size_bytes": image_path.stat().st_size,
            }
        ],
    )
    write_json(LOCAL_LEDGER_PATH, ledger_pre_upload)
    write_provider_note(
        ledger=ledger_pre_upload,
        image_path=image_path,
        image_mime_type=detected_mime,
        image_sha=image_sha,
        fallback_used=result.fallback_used,
    )

    # Upload the four artifacts through the reusable Genblaze/B2 helper.
    store = GenblazeStore(
        bucket=b2_env["B2_BUCKET"],
        region=b2_env["B2_REGION"],
        key_id=b2_env["B2_KEY_ID"],
        app_key=b2_env["B2_APP_KEY"],
        prefix=B2_PREFIX,
    )

    common_metadata = {
        "proofstudio_test": "ps-007",
        "slice": "PS-007",
        "job_type": JOB_TYPE,
        "budget_mode": budget_mode,
        "selected_provider": result.selected_provider,
        "selected_model": result.selected_model,
        "fallback_used": result.fallback_used,
    }

    asset_specs = [
        AssetSpec(
            path=image_path,
            media_type=detected_mime,
            artifact_type="generated_image",
            metadata={
                **common_metadata,
                "image_mime_type": detected_mime,
                "image_sha256": image_sha,
                "produced_real_media": True,
            },
        ),
        AssetSpec(
            path=LOCAL_PROMPT_PACKET_PATH,
            media_type="application/json",
            artifact_type="visual_prompt_packet",
            metadata=common_metadata,
        ),
        AssetSpec(
            path=LOCAL_LEDGER_PATH,
            media_type="application/json",
            artifact_type="provider_attempt_ledger",
            metadata=common_metadata,
        ),
        AssetSpec(
            path=LOCAL_NOTE_PATH,
            media_type="text/markdown",
            artifact_type="provider_note",
            metadata=common_metadata,
        ),
    ]

    try:
        run_result = store.store_and_verify(
            assets=asset_specs,
            source="proofstudio-ps-007-live-provider-router-chain",
            source_metadata={
                "scenario": "PS-007",
                "description": (
                    "Live ProviderRouter chain (Cloudflare primary -> "
                    "Pollinations fallback) generated a visual campaign asset "
                    "for ProofStudio, stored in B2 and verified with a "
                    "Genblaze manifest."
                ),
                "provider_chain": ["cloudflare-workers-ai", "pollinations"],
                "selected_provider": result.selected_provider,
                "selected_model": result.selected_model,
                "api_method": attempts_full[selected_index].get("api_method")
                if selected_index is not None
                else None,
                "job_type": JOB_TYPE,
                "budget_mode": budget_mode,
                "fallback_used": result.fallback_used,
                "attempt_count": len(attempts_full),
            },
            name="proofstudio-ps-007-live-provider-router-chain",
            tenant_id="local",
        )
    except RuntimeError as exc:
        write_failed_provider_attempts(
            attempts_full,
            reason=f"B2/Genblaze storage failed: {exc}",
            fallback_used=result.fallback_used,
            budget_mode=budget_mode,
        )
        blocked = write_blocked_summary(
            reason=f"B2/Genblaze storage failed: {exc}",
            attempts_full=attempts_full,
            fallback_used=result.fallback_used,
            budget_mode=budget_mode,
        )
        print(json.dumps(blocked, indent=2, ensure_ascii=False))
        fail(f"PS-007 failed: B2/Genblaze storage failed: {exc}")

    # Final ledger with B2/manifest references included.
    final_ledger = build_ledger(
        attempts_full=attempts_full,
        final_status="succeeded",
        selected_provider=result.selected_provider,
        selected_model=result.selected_model,
        fallback_used=result.fallback_used,
        budget_mode=budget_mode,
        output_assets=[
            {
                "kind": "generated_image",
                "local_path": str(image_path),
                "media_type": detected_mime,
                "sha256": image_sha,
                "size_bytes": image_path.stat().st_size,
                "b2_manifest_asset_id": run_result.asset_summaries[0]["asset_id"]
                if run_result.asset_summaries
                else None,
            }
        ],
        b2_artifacts=run_result.asset_summaries,
        manifest_uri=run_result.manifest_uri,
        manifest_hash=run_result.manifest_hash,
    )
    write_json(LOCAL_LEDGER_PATH, final_ledger)
    write_provider_note(
        ledger=final_ledger,
        image_path=image_path,
        image_mime_type=detected_mime,
        image_sha=image_sha,
        fallback_used=result.fallback_used,
    )

    # Final schema validation on what was actually written to disk.
    final_schema_errors = validate_full_attempt_schema(
        final_ledger["attempts"]
    )
    if final_schema_errors:
        for err in final_schema_errors:
            print(f"   - SCHEMA ERROR: {err}", file=sys.stderr)
        fail("PS-007 final attempt ledger schema validation failed.")

    selected_api_method = (
        attempts_full[selected_index].get("api_method")
        if selected_index is not None
        else None
    )

    summary = {
        "ok": True,
        "proof": (
            "PS-007 Live ProviderRouter Chain (Cloudflare primary -> Pollinations "
            "fallback) + B2 + Genblaze manifest smoke test passed."
        ),
        "slice": "PS-007",
        "selected_provider": result.selected_provider,
        "selected_model": result.selected_model,
        "api_method": selected_api_method,
        "job_type": JOB_TYPE,
        "budget_mode": budget_mode,
        "fallback_used": result.fallback_used,
        "attempt_count": len(attempts_full),
        "attempts": attempts_full,
        "image_mime_type": detected_mime,
        "image_sha256": image_sha,
        "local_image": str(image_path),
        "run_id": run_result.run_id,
        "run_status": run_result.run_status,
        "manifest_hash": run_result.manifest_hash,
        "manifest_uri": run_result.manifest_uri,
        "in_memory_manifest_verify": run_result.in_memory_manifest_verify,
        "stored_manifest_verify": run_result.stored_manifest_verify,
        "transfer_failures": run_result.transfer_failures,
        "stored_transfer_failures": run_result.stored_transfer_failures,
        "asset_count": len(run_result.asset_summaries),
        "assets": run_result.asset_summaries,
        "local_prompt_packet": str(LOCAL_PROMPT_PACKET_PATH),
        "local_attempt_ledger": str(LOCAL_LEDGER_PATH),
        "local_provider_note": str(LOCAL_NOTE_PATH),
        "local_summary": str(LOCAL_SUMMARY_PATH),
        "truth_boundary": (
            "PS-007 proves live provider routing, fallback behavior, evidence "
            "capture, B2 storage, Genblaze manifest writing, and byte-level "
            "manifest verification. It does not prove semantic truth, legal "
            "authenticity, human authorship, or C2PA authenticity."
        ),
        "written_at": now_iso(),
    }

    write_json(LOCAL_SUMMARY_PATH, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
