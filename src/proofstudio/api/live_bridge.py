"""PS-009 API Live Run Bridge.

This module connects the PS-008 service/API run creation to the PS-007 live
ProviderRouter chain. It exposes :func:`execute_live_run`, a single clean
function that the service layer calls when ``create_run`` receives
``run_live=True``.

Product path (see specs/17-ps-009-api-live-run-bridge.md section 1):

    create_run(run_live=true)
    -> live ProviderRouter chain (Cloudflare primary, Pollinations fallback)
    -> full ProviderAttempt ledger
    -> generated image
    -> B2 storage + Genblaze manifest
    -> structured result fed back into the in-memory API store

Reuse requirement (section 7): the bridge reuses the PS-007 components directly
and never shells out to the PS-007 smoke script:

- ``proofstudio.providers.live_cloudflare.LiveCloudflareProvider``
- ``proofstudio.providers.live_pollinations.LivePollinationsProvider``
- ``proofstudio.providers.router.ProviderRouter``
- ``proofstudio.provenance.genblaze_store.GenblazeStore`` / ``AssetSpec``

Hard rules enforced here:

- Dry-run never enters this module. The service layer only calls
  :func:`execute_live_run` when ``run_live`` is true and ``dry_run`` is false.
- No fake image is ever written. ``OK`` only flows from a provider that
  returned real image bytes.
- No fake B2 or Genblaze metadata is ever produced. Manifest verification
  fields come straight from the real ``GenblazeStore.store_and_verify`` result.
- Secrets are never logged. Provider adapters scrub bearer tokens / auth
  headers; this bridge never prints credentials.

Truth boundary: this bridge proves the backend service can explicitly trigger
and store a live proof-backed generation run. It does not prove semantic truth,
legal authenticity, C2PA authenticity, or human authorship.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from proofstudio.providers.live_cloudflare import (
    DEFAULT_PRIMARY_MODEL as CLOUDFLARE_DEFAULT_MODEL,
)
from proofstudio.providers.live_cloudflare import (
    detect_image_mime_from_bytes as detect_mime_from_bytes,
)
from proofstudio.providers.live_pollinations import LivePollinationsProvider
from proofstudio.providers.live_pollinations import is_disabled_env
from proofstudio.providers.live_cloudflare import LiveCloudflareProvider
from proofstudio.providers.router import ProviderRouter
from proofstudio.providers.types import (
    NS_OK,
    ProviderJob,
)
from proofstudio.provenance.genblaze_store import AssetSpec, GenblazeStore

JOB_TYPE = "image_generation"

B2_REQUIRED_ENV = (
    "B2_KEY_ID",
    "B2_APP_KEY",
    "B2_BUCKET",
    "B2_REGION",
)

# PS-035b default-off governance controls. These are POLICY FLAGS, not secrets.
# They must never be treated as secrets, must never use names containing KEY,
# TOKEN, or SECRET, and must never be printed or exposed as secrets. All four
# default OFF so live provider execution, paid runs, B2 writes, and fixture
# mutation are blocked unless an operator explicitly enables them.
LIVE_RUNS_ENABLED_ENV = "PROOFSTUDIO_LIVE_RUNS_ENABLED"
B2_WRITES_ENABLED_ENV = "PROOFSTUDIO_B2_WRITES_ENABLED"
COST_CAP_USD_ENV = "PROOFSTUDIO_COST_CAP_USD"
FIXTURES_FROZEN_ENV = "PROOFSTUDIO_FIXTURES_FROZEN"
# Explicit PM/human approval gate for any paid/live run. A separate flag from
# the live-runs-enabled switch so run_live=True alone is never sufficient.
PAID_RUN_APPROVED_ENV = "PROOFSTUDIO_PAID_RUN_APPROVED"
# The documented live-default flag, superseded truthfully by the enforced
# LIVE_RUNS_ENABLED gate above so it is no longer a phantom-only contract.
RUN_LIVE_DEFAULT_ENV = "PROOFSTUDIO_RUN_LIVE_DEFAULT"

DEFAULT_COST_CAP_USD = 0.00
FREE_ONLY_BUDGET_MODE = "free-only"

TRUTH_BOUNDARY = (
    "PS-009 proves the backend API/service layer can explicitly trigger and "
    "store a live proof-backed generation run. It does not prove semantic "
    "truth, legal authenticity, C2PA authenticity, or human authorship. The "
    "manifest proves recorded workflow integrity and byte-level asset "
    "verification only."
)

NOT_READY_DEFAULTS: dict[str, Any] = {
    "ok": False,
    "status": "live_blocked",
    "selected_provider": None,
    "selected_model": None,
    "api_method": None,
    "job_type": JOB_TYPE,
    "fallback_used": False,
    "attempt_count": 0,
    "attempts": [],
    "image_mime_type": None,
    "image_sha256": None,
    "local_image": None,
    "manifest_hash": None,
    "manifest_uri": None,
    "in_memory_manifest_verify": None,
    "stored_manifest_verify": None,
    "transfer_failures": [],
    "stored_transfer_failures": [],
    "asset_count": 0,
    "assets": [],
    "local_prompt_packet": None,
    "local_attempt_ledger": None,
    "local_provider_note": None,
    "error": None,
    "blocked_reason": None,
    "truth_boundary": TRUTH_BOUNDARY,
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() == "true"


def cost_cap_usd() -> float:
    """PS-035b: the configured cost cap in USD (default 0.00)."""
    raw = os.getenv(COST_CAP_USD_ENV)
    if raw is None or raw.strip() == "":
        return DEFAULT_COST_CAP_USD
    try:
        return float(raw)
    except (TypeError, ValueError):
        return DEFAULT_COST_CAP_USD


def live_runs_enabled() -> bool:
    """PS-035b: whether live provider execution is permitted by governance.

    Default OFF. Only true when an operator explicitly sets
    ``PROOFSTUDIO_LIVE_RUNS_ENABLED=true``.
    """
    return _env_flag(LIVE_RUNS_ENABLED_ENV)


def b2_writes_enabled() -> bool:
    """PS-035b: whether B2 writes are permitted by governance.

    Default OFF. Only true when an operator explicitly sets
    ``PROOFSTUDIO_B2_WRITES_ENABLED=true``. B2 writes after a successful live
    provider run require this gate in addition to the live-run gate.
    """
    return _env_flag(B2_WRITES_ENABLED_ENV)


def fixtures_frozen() -> bool:
    """PS-035b: whether golden fixtures are frozen (default true)."""
    raw = os.getenv(FIXTURES_FROZEN_ENV)
    if raw is None or raw.strip() == "":
        return True
    return raw.strip().lower() == "true"


def govern_live_run(*, budget_mode: str) -> tuple[bool, str | None]:
    """PS-035b default-off live-run governance decision.

    Returns ``(allowed, blocked_reason)``. ``allowed`` is True only when ALL of
    the following gates pass, in order:

    - ``PROOFSTUDIO_LIVE_RUNS_ENABLED=true`` (live runs explicitly enabled)
    - ``PROOFSTUDIO_PAID_RUN_APPROVED=true`` (explicit PM/human approval)
    - ``PROOFSTUDIO_COST_CAP_USD`` > ``0.00`` (non-zero budget)
    - ``budget_mode`` != ``"free-only"`` (free-only blocks paid execution)

    ``run_live=True`` alone is NOT sufficient to execute providers. No provider
    is called and no B2 access occurs when this returns False. This is the
    authoritative backend gate; the documented ``PROOFSTUDIO_RUN_LIVE_DEFAULT``
    is honored truthfully by being superseded with the enforced
    ``PROOFSTUDIO_LIVE_RUNS_ENABLED`` control.
    """
    if not live_runs_enabled():
        return False, (
            "PROOFSTUDIO_LIVE_RUNS_ENABLED is not true. Live provider "
            "execution is blocked by default."
        )
    if not _env_flag(PAID_RUN_APPROVED_ENV):
        return False, (
            "PROOFSTUDIO_PAID_RUN_APPROVED is not true. A live/paid run "
            "requires explicit PM/human approval before execution."
        )
    cap = cost_cap_usd()
    if cap <= 0.0:
        return False, (
            f"PROOFSTUDIO_COST_CAP_USD is {cap:.2f}. Paid/non-free provider "
            "execution is blocked when the cost cap is zero."
        )
    if (budget_mode or "").strip().lower() == FREE_ONLY_BUDGET_MODE:
        return False, (
            "budget_mode is 'free-only'. Paid/non-free provider execution "
            "is blocked under the free-only budget."
        )
    return True, None


def _sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mime_to_ext(mime_type: str | None) -> str:
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


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _missing_b2_env() -> list[str]:
    return [name for name in B2_REQUIRED_ENV if not os.getenv(name)]


def build_cloudflare_provider() -> LiveCloudflareProvider:
    """Construct the live Cloudflare primary provider from environment."""
    return LiveCloudflareProvider(
        account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID"),
        api_token=os.getenv("CLOUDFLARE_API_TOKEN"),
        model=os.getenv("CLOUDFLARE_IMAGE_MODEL_PRIMARY") or CLOUDFLARE_DEFAULT_MODEL,
    )


def build_pollinations_provider() -> LivePollinationsProvider:
    """Construct the live Pollinations fallback provider from environment."""
    return LivePollinationsProvider(
        enabled=None if os.getenv("POLLINATIONS_ENABLED") is None else (
            not is_disabled_env(os.getenv("POLLINATIONS_ENABLED"))
        ),
        width=os.getenv("POLLINATIONS_WIDTH") or None,
        height=os.getenv("POLLINATIONS_HEIGHT") or None,
        model_name=os.getenv("POLLINATIONS_MODEL_NAME") or None,
    )


def build_prompt_packet(
    *,
    campaign: dict[str, Any],
    prompt: str,
    budget_mode: str,
) -> dict[str, Any]:
    """Build a campaign-aware prompt packet for the live router.

    If ``prompt`` is provided it is used verbatim. Otherwise the campaign
    brief drives the prompt so the router always receives non-empty text.
    """
    campaign_name = (campaign or {}).get("name") or "ProofStudio Campaign"
    campaign_brief = (campaign or {}).get("brief") or ""

    resolved_prompt = (prompt or "").strip()
    if not resolved_prompt:
        resolved_prompt = (
            f"Create a premium marketing visual for the campaign "
            f"\"{campaign_name}\". {campaign_brief}".strip()
        )

    return {
        "artifact_type": "proofstudio_visual_generation_prompt",
        "schema_version": "ps-009.1",
        "created_at": _utc_now_iso(),
        "provider_chain": ["cloudflare-workers-ai", "pollinations"],
        "job_type": JOB_TYPE,
        "budget_mode": budget_mode,
        "campaign": {
            "campaign_id": (campaign or {}).get("campaign_id"),
            "name": campaign_name,
            "brief": campaign_brief,
            "platform": (campaign or {}).get("platform"),
            "objective": (campaign or {}).get("objective"),
            "target_audience": (campaign or {}).get("target_audience"),
        },
        "prompt": resolved_prompt,
    }


def _write_prompt_packet(
    path: Path,
    *,
    packet: dict[str, Any],
    selected: dict[str, Any],
    budget_mode: str,
) -> None:
    payload = {
        "proofstudio_artifact_type": "visual_prompt_packet",
        "schema_version": "ps-009.1",
        "job_type": JOB_TYPE,
        "budget_mode": budget_mode,
        "selected": selected,
        "prompt_packet": packet,
    }
    _write_json(path, payload)


def _write_provider_note(
    path: Path,
    *,
    run_id: str,
    campaign_id: str,
    ledger: dict[str, Any],
    image_path: Path | None,
    image_mime_type: str | None,
    image_sha: str | None,
    fallback_used: bool,
) -> None:
    selected_provider = ledger.get("selected_provider") or "(none)"
    selected_model = ledger.get("selected_model") or "(none)"
    lines = [
        "# PS-009 API Live Run Bridge Provider Note",
        "",
        f"- Run id: `{run_id}`",
        f"- Campaign id: `{campaign_id}`",
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
        TRUTH_BOUNDARY,
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
    path.write_text("\n".join(lines), encoding="utf-8")


def _build_ledger(
    *,
    attempts_full: list[dict[str, Any]],
    final_status: str,
    selected_provider: str | None,
    selected_model: str | None,
    fallback_used: bool,
    budget_mode: str,
    run_id: str,
    campaign_id: str,
    output_assets: list[dict[str, Any]] | None = None,
    b2_artifacts: list[dict[str, Any]] | None = None,
    manifest_uri: str | None = None,
    manifest_hash: str | None = None,
) -> dict[str, Any]:
    created_at = attempts_full[0]["started_at"] if attempts_full else _utc_now_iso()
    completed_at = attempts_full[-1]["finished_at"] if attempts_full else _utc_now_iso()
    return {
        "ledger_id": f"ps-009-{run_id}",
        "campaign_id": campaign_id,
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
        "truth_boundary": TRUTH_BOUNDARY,
    }


def execute_live_run(
    *,
    campaign: dict[str, Any],
    prompt: str,
    budget_mode: str,
    output_dir: Path,
    b2_prefix: str,
    run_id: str | None = None,
    cloudflare_provider: LiveCloudflareProvider | None = None,
    pollinations_provider: LivePollinationsProvider | None = None,
    router: ProviderRouter | None = None,
    b2_env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute the live PS-007 provider-router chain for a PS-009 API run.

    Returns a structured result dict (see ``NOT_READY_DEFAULTS`` for the full
    field set). The function never fakes success: an ``ok=True`` / status
    ``live_completed`` result is only returned when a provider returned real
    image bytes AND the B2 + Genblaze manifest write + read-back + verify all
    passed.

    The caller (the service layer) is responsible for recording this result
    onto the run record and for registering the attempts / assets / manifest
    sub-resources.

    Injecting ``cloudflare_provider`` / ``pollinations_provider`` / ``router``
    / ``b2_env`` is supported for testability; when omitted the bridge builds
    them from the live environment exactly like the PS-007 smoke script.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    run_id = run_id or uuid.uuid4().hex
    campaign_id = (campaign or {}).get("campaign_id") or "proofstudio-launch"

    prompt_packet = build_prompt_packet(
        campaign=campaign, prompt=prompt, budget_mode=budget_mode
    )
    prompt_text = prompt_packet["prompt"]

    # PS-035b governance gate: live provider execution is blocked by default.
    # run_live=True is not enough; PROOFSTUDIO_LIVE_RUNS_ENABLED,
    # PROOFSTUDIO_PAID_RUN_APPROVED, a non-zero PROOFSTUDIO_COST_CAP_USD, and a
    # non-free-only budget_mode must all permit execution. No provider is
    # called and no B2 access occurs when this gate blocks.
    allowed, blocked_reason = govern_live_run(budget_mode=budget_mode)
    if not allowed:
        return _blocked_result(
            run_id=run_id,
            campaign_id=campaign_id,
            output_dir=output_dir,
            blocked_reason=blocked_reason,
            prompt_packet=prompt_packet,
        )

    # Resolve B2 credentials. Missing required B2 env is an honest block: the
    # bridge cannot store evidence, so it must not call providers.
    if b2_env is None:
        missing = _missing_b2_env()
        if missing:
            return _blocked_result(
                run_id=run_id,
                campaign_id=campaign_id,
                output_dir=output_dir,
                blocked_reason=(
                    "Missing required B2 environment variables: "
                    + ", ".join(missing)
                    + ". Live run blocked before any provider call."
                ),
                prompt_packet=prompt_packet,
            )
        b2_env = {name: os.environ[name] for name in B2_REQUIRED_ENV}

    cloudflare = cloudflare_provider or build_cloudflare_provider()
    pollinations = pollinations_provider or build_pollinations_provider()
    providers = [cloudflare, pollinations]
    active_router = router or ProviderRouter(providers=providers)

    job = ProviderJob(
        job_type=JOB_TYPE,
        prompt=prompt_text,
        budget_mode=budget_mode,
        campaign_id=campaign_id,
        job_id=run_id,
    )

    started_at = _utc_now_iso()
    result = active_router.route(job)
    finished_at = _utc_now_iso()

    attempts_full: list[dict[str, Any]] = [
        attempt.to_dict() for attempt in result.attempts
    ]

    # All providers failed or skipped. Preserve the full attempt ledger; no
    # fake image, no B2 upload, no manifest.
    if not result.ok:
        return _failed_result(
            run_id=run_id,
            campaign_id=campaign_id,
            output_dir=output_dir,
            attempts_full=attempts_full,
            fallback_used=result.fallback_used,
            final_normalized_status=result.final_normalized_status,
            selected_provider=None,
            selected_model=None,
            api_method=None,
            budget_mode=budget_mode,
            prompt_packet=prompt_packet,
            started_at=started_at,
            finished_at=finished_at,
            error=(
                "All providers in the PS-009 live chain failed or were "
                "skipped. No image generated. No fake image written. No B2 "
                "upload performed."
            ),
        )

    # A provider succeeded. Recover its real image bytes via the winning
    # provider instance's safe carry-over attribute.
    winner = None
    for provider in providers:
        if getattr(provider, "provider_id", None) == result.selected_provider:
            winner = provider
            break

    image_bytes = getattr(winner, "last_image_bytes", None) if winner else None
    image_mime_from_provider = getattr(winner, "last_image_mime", None) if winner else None

    if not image_bytes:
        return _failed_result(
            run_id=run_id,
            campaign_id=campaign_id,
            output_dir=output_dir,
            attempts_full=attempts_full,
            fallback_used=result.fallback_used,
            final_normalized_status=result.final_normalized_status,
            selected_provider=result.selected_provider,
            selected_model=result.selected_model,
            api_method=_selected_api_method(attempts_full, result.selected_attempt_index),
            budget_mode=budget_mode,
            prompt_packet=prompt_packet,
            started_at=started_at,
            finished_at=finished_at,
            error=(
                f"Provider {result.selected_provider!r} was selected by the "
                "router but did not expose real image bytes. No fake image "
                "written."
            ),
        )

    detected_mime = detect_mime_from_bytes(image_bytes, image_mime_from_provider)
    if not detected_mime.startswith("image/"):
        return _failed_result(
            run_id=run_id,
            campaign_id=campaign_id,
            output_dir=output_dir,
            attempts_full=attempts_full,
            fallback_used=result.fallback_used,
            final_normalized_status=result.final_normalized_status,
            selected_provider=result.selected_provider,
            selected_model=result.selected_model,
            api_method=_selected_api_method(attempts_full, result.selected_attempt_index),
            budget_mode=budget_mode,
            prompt_packet=prompt_packet,
            started_at=started_at,
            finished_at=finished_at,
            error=(
                f"Selected provider returned non-image bytes (detected mime="
                f"{detected_mime!r}). No fake image written."
            ),
        )

    # Persist the real image locally.
    ext = _mime_to_ext(detected_mime)
    image_path = output_dir / f"ps-009-run-{run_id}{ext}"
    image_path.write_bytes(image_bytes)
    image_sha = _sha256_of_file(image_path)

    # Enrich the selected attempt's output_asset_refs with on-disk evidence.
    selected_index = result.selected_attempt_index
    selected_api_method = _selected_api_method(attempts_full, selected_index)
    if selected_index is not None and 0 <= selected_index < len(attempts_full):
        attempts_full[selected_index]["output_asset_refs"] = [
            {
                "kind": "generated_image",
                "provider": result.selected_provider,
                "model": result.selected_model,
                "api_method": selected_api_method,
                "local_path": str(image_path),
                "media_type": detected_mime,
                "sha256": image_sha,
                "size_bytes": image_path.stat().st_size,
                "produced_real_media": True,
            }
        ]

    prompt_packet_path = output_dir / f"ps-009-run-{run_id}-prompt-packet.json"
    ledger_path = output_dir / f"ps-009-run-{run_id}-attempt-ledger.json"
    note_path = output_dir / f"ps-009-run-{run_id}-provider-note.md"

    _write_prompt_packet(
        prompt_packet_path,
        packet=prompt_packet,
        selected={
            "provider": result.selected_provider,
            "model": result.selected_model,
            "api_method": selected_api_method,
            "image_mime_type": detected_mime,
            "image_sha256": image_sha,
            "fallback_used": result.fallback_used,
        },
        budget_mode=budget_mode,
    )

    pre_upload_ledger = _build_ledger(
        attempts_full=attempts_full,
        final_status="succeeded",
        selected_provider=result.selected_provider,
        selected_model=result.selected_model,
        fallback_used=result.fallback_used,
        budget_mode=budget_mode,
        run_id=run_id,
        campaign_id=campaign_id,
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
    _write_json(ledger_path, pre_upload_ledger)
    _write_provider_note(
        note_path,
        run_id=run_id,
        campaign_id=campaign_id,
        ledger=pre_upload_ledger,
        image_path=image_path,
        image_mime_type=detected_mime,
        image_sha=image_sha,
        fallback_used=result.fallback_used,
    )

    # Upload the four artifacts through the reusable Genblaze/B2 helper.
    common_metadata = {
        "proofstudio_test": "ps-009",
        "slice": "PS-009",
        "job_type": JOB_TYPE,
        "budget_mode": budget_mode,
        "run_id": run_id,
        "campaign_id": campaign_id,
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
            path=prompt_packet_path,
            media_type="application/json",
            artifact_type="visual_prompt_packet",
            metadata=common_metadata,
        ),
        AssetSpec(
            path=ledger_path,
            media_type="application/json",
            artifact_type="provider_attempt_ledger",
            metadata=common_metadata,
        ),
        AssetSpec(
            path=note_path,
            media_type="text/markdown",
            artifact_type="provider_note",
            metadata=common_metadata,
        ),
    ]

    # PS-035b B2 write gate: B2 writes are blocked by default. The live
    # provider run produced a real local image, but B2/Genblaze storage after a
    # successful live run requires PROOFSTUDIO_B2_WRITES_ENABLED=true. No B2
    # write occurs when this gate blocks; the local image evidence is kept.
    if not b2_writes_enabled():
        return _failed_result(
            run_id=run_id,
            campaign_id=campaign_id,
            output_dir=output_dir,
            attempts_full=attempts_full,
            fallback_used=result.fallback_used,
            final_normalized_status=result.final_normalized_status,
            selected_provider=result.selected_provider,
            selected_model=result.selected_model,
            api_method=selected_api_method,
            budget_mode=budget_mode,
            prompt_packet=prompt_packet,
            started_at=started_at,
            finished_at=finished_at,
            local_image=str(image_path),
            image_mime_type=detected_mime,
            image_sha256=image_sha,
            error=(
                "PROOFSTUDIO_B2_WRITES_ENABLED is not true. The live provider "
                "run produced a real local image, but B2/Genblaze storage is "
                "blocked by default after the live run. No B2 write occurred."
            ),
        )

    try:
        store = GenblazeStore(
            bucket=b2_env["B2_BUCKET"],
            region=b2_env["B2_REGION"],
            key_id=b2_env["B2_KEY_ID"],
            app_key=b2_env["B2_APP_KEY"],
            prefix=b2_prefix,
        )
        run_result = store.store_and_verify(
            assets=asset_specs,
            source="proofstudio-ps-009-api-live-run-bridge",
            source_metadata={
                "scenario": "PS-009",
                "description": (
                    "PS-009 API live run bridge executed the live "
                    "ProviderRouter chain (Cloudflare primary -> Pollinations "
                    "fallback) for a campaign run, stored the generated image "
                    "and supporting artifacts in B2, and verified them through "
                    "a Genblaze manifest."
                ),
                "provider_chain": ["cloudflare-workers-ai", "pollinations"],
                "selected_provider": result.selected_provider,
                "selected_model": result.selected_model,
                "api_method": selected_api_method,
                "job_type": JOB_TYPE,
                "budget_mode": budget_mode,
                "fallback_used": result.fallback_used,
                "attempt_count": len(attempts_full),
                "run_id": run_id,
                "campaign_id": campaign_id,
            },
            name=f"proofstudio-ps-009-run-{run_id}",
            tenant_id="local",
        )
    except RuntimeError as exc:
        # Provider succeeded but B2/Genblaze storage failed. This is an honest
        # live_failed, not a block: real attempts and a real local image exist.
        return _failed_result(
            run_id=run_id,
            campaign_id=campaign_id,
            output_dir=output_dir,
            attempts_full=attempts_full,
            fallback_used=result.fallback_used,
            final_normalized_status=result.final_normalized_status,
            selected_provider=result.selected_provider,
            selected_model=result.selected_model,
            api_method=selected_api_method,
            budget_mode=budget_mode,
            prompt_packet=prompt_packet,
            started_at=started_at,
            finished_at=finished_at,
            local_image=str(image_path),
            image_mime_type=detected_mime,
            image_sha256=image_sha,
            error=f"B2/Genblaze storage failed: {exc}",
        )

    # Final ledger with B2/manifest references included.
    final_ledger = _build_ledger(
        attempts_full=attempts_full,
        final_status="succeeded",
        selected_provider=result.selected_provider,
        selected_model=result.selected_model,
        fallback_used=result.fallback_used,
        budget_mode=budget_mode,
        run_id=run_id,
        campaign_id=campaign_id,
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
    _write_json(ledger_path, final_ledger)
    _write_provider_note(
        note_path,
        run_id=run_id,
        campaign_id=campaign_id,
        ledger=final_ledger,
        image_path=image_path,
        image_mime_type=detected_mime,
        image_sha=image_sha,
        fallback_used=result.fallback_used,
    )

    assets_summary = [
        {
            "kind": "generated_image",
            "provider": result.selected_provider,
            "model": result.selected_model,
            "api_method": selected_api_method,
            "media_type": detected_mime,
            "sha256": image_sha,
            "size_bytes": image_path.stat().st_size,
            "local_path": str(image_path),
            "produced_real_media": True,
            "b2_url": run_result.asset_summaries[0]["url"]
            if run_result.asset_summaries
            else None,
            "b2_asset_id": run_result.asset_summaries[0]["asset_id"]
            if run_result.asset_summaries
            else None,
        }
    ]
    assets_summary.extend(
        {
            "kind": spec_metadata.get("artifact_type", "proofstudio_artifact"),
            "media_type": summary["media_type"],
            "sha256": summary["sha256"],
            "size_bytes": summary["size_bytes"],
            "b2_url": summary["url"],
            "b2_asset_id": summary["asset_id"],
            "produced_real_media": False,
        }
        for summary, spec_metadata in zip(
            run_result.asset_summaries[1:],
            [
                {"artifact_type": "visual_prompt_packet"},
                {"artifact_type": "provider_attempt_ledger"},
                {"artifact_type": "provider_note"},
            ],
        )
    )

    return {
        "ok": True,
        "status": "live_completed",
        "selected_provider": result.selected_provider,
        "selected_model": result.selected_model,
        "api_method": selected_api_method,
        "job_type": JOB_TYPE,
        "fallback_used": result.fallback_used,
        "attempt_count": len(attempts_full),
        "attempts": attempts_full,
        "image_mime_type": detected_mime,
        "image_sha256": image_sha,
        "local_image": str(image_path),
        "manifest_hash": run_result.manifest_hash,
        "manifest_uri": run_result.manifest_uri,
        "in_memory_manifest_verify": run_result.in_memory_manifest_verify,
        "stored_manifest_verify": run_result.stored_manifest_verify,
        "transfer_failures": run_result.transfer_failures,
        "stored_transfer_failures": run_result.stored_transfer_failures,
        "asset_count": len(assets_summary),
        "assets": assets_summary,
        "local_prompt_packet": str(prompt_packet_path),
        "local_attempt_ledger": str(ledger_path),
        "local_provider_note": str(note_path),
        "error": None,
        "blocked_reason": None,
        "truth_boundary": TRUTH_BOUNDARY,
    }


def _selected_api_method(
    attempts_full: list[dict[str, Any]], selected_index: int | None
) -> str | None:
    if selected_index is None or not (0 <= selected_index < len(attempts_full)):
        return None
    return attempts_full[selected_index].get("api_method")


def _blocked_result(
    *,
    run_id: str,
    campaign_id: str,
    output_dir: Path,
    blocked_reason: str,
    prompt_packet: dict[str, Any],
) -> dict[str, Any]:
    """Build a live_blocked result and persist the prompt packet for audit.

    Used when the environment cannot support live execution at all (e.g.
    missing B2 credentials). No provider is called and no image is written.
    """
    prompt_packet_path = output_dir / f"ps-009-run-{run_id}-prompt-packet.json"
    _write_prompt_packet(
        prompt_packet_path,
        packet=prompt_packet,
        selected={
            "provider": None,
            "model": None,
            "api_method": None,
            "image_mime_type": None,
            "image_sha256": None,
            "fallback_used": False,
        },
        budget_mode=prompt_packet.get("budget_mode", "free-only"),
    )
    result = dict(NOT_READY_DEFAULTS)
    result.update(
        {
            "status": "live_blocked",
            "blocked_reason": blocked_reason,
            "local_prompt_packet": str(prompt_packet_path),
        }
    )
    return result


def _failed_result(
    *,
    run_id: str,
    campaign_id: str,
    output_dir: Path,
    attempts_full: list[dict[str, Any]],
    fallback_used: bool,
    final_normalized_status: str,
    selected_provider: str | None,
    selected_model: str | None,
    api_method: str | None,
    budget_mode: str,
    prompt_packet: dict[str, Any],
    started_at: str,
    finished_at: str,
    error: str,
    local_image: str | None = None,
    image_mime_type: str | None = None,
    image_sha256: str | None = None,
) -> dict[str, Any]:
    """Build a live_failed result and persist a failed-provider ledger.

    Used when providers ran but none succeeded, or when B2/Genblaze storage
    failed after a provider did succeed. The full attempt ledger is always
    preserved so failure evidence is never lost.
    """
    prompt_packet_path = output_dir / f"ps-009-run-{run_id}-prompt-packet.json"
    ledger_path = output_dir / f"ps-009-run-{run_id}-attempt-ledger.json"

    _write_prompt_packet(
        prompt_packet_path,
        packet=prompt_packet,
        selected={
            "provider": selected_provider,
            "model": selected_model,
            "api_method": api_method,
            "image_mime_type": image_mime_type,
            "image_sha256": image_sha256,
            "fallback_used": fallback_used,
        },
        budget_mode=budget_mode,
    )

    failed_ledger = _build_ledger(
        attempts_full=attempts_full,
        final_status="failed",
        selected_provider=selected_provider,
        selected_model=selected_model,
        fallback_used=fallback_used,
        budget_mode=budget_mode,
        run_id=run_id,
        campaign_id=campaign_id,
        output_assets=(
            [
                {
                    "kind": "generated_image",
                    "local_path": local_image,
                    "media_type": image_mime_type,
                    "sha256": image_sha256,
                }
            ]
            if local_image
            else []
        ),
    )
    _write_json(ledger_path, failed_ledger)

    result = dict(NOT_READY_DEFAULTS)
    result.update(
        {
            "status": "live_failed",
            "selected_provider": selected_provider,
            "selected_model": selected_model,
            "api_method": api_method,
            "fallback_used": fallback_used,
            "attempt_count": len(attempts_full),
            "attempts": attempts_full,
            "error": error,
            "local_image": local_image,
            "image_mime_type": image_mime_type,
            "image_sha256": image_sha256,
            "local_prompt_packet": str(prompt_packet_path),
            "local_attempt_ledger": str(ledger_path),
        }
    )
    return result


__all__ = [
    "execute_live_run",
    "build_prompt_packet",
    "build_cloudflare_provider",
    "build_pollinations_provider",
    "govern_live_run",
    "live_runs_enabled",
    "b2_writes_enabled",
    "cost_cap_usd",
    "fixtures_frozen",
    "JOB_TYPE",
    "TRUTH_BOUNDARY",
    "B2_REQUIRED_ENV",
    "NOT_READY_DEFAULTS",
    "LIVE_RUNS_ENABLED_ENV",
    "B2_WRITES_ENABLED_ENV",
    "COST_CAP_USD_ENV",
    "FIXTURES_FROZEN_ENV",
    "PAID_RUN_APPROVED_ENV",
    "DEFAULT_COST_CAP_USD",
    "FREE_ONLY_BUDGET_MODE",
]
