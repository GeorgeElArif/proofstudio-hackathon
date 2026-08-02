#!/usr/bin/env python3
"""
PS-004: Provider Router + Cloudflare Workers AI visual proof.

What this proves:
- ProofStudio can route a visual job through a real provider router.
- Cloudflare Workers AI is attempted first (primary model), then a fallback model.
- Every provider attempt is recorded in a normalized attempt ledger.
- Failures are mapped to normalized router statuses and never faked.
- On success the generated image, prompt packet, attempt ledger, and provider note
  are stored in Backblaze B2 through the Genblaze pipeline.
- The Genblaze manifest is written to B2, read back, and verified.
- The run must have zero transfer failures.

This script does not fake success. If Cloudflare keys are missing it records a
SKIPPED_MISSING_KEY ledger and fails. If both Cloudflare models fail it writes a
failed-provider-attempts report and exits non-zero without uploading any asset.
"""

from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import os
import re
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from genblaze_core.models.asset import Asset
from genblaze_core.pipeline.pipeline import Pipeline
from genblaze_core.storage.sink import ObjectStorageSink
from genblaze_s3.backend import S3StorageBackend


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_OUTPUT_DIR = Path(tempfile.gettempdir()) / "proofstudio-ps-004"
LOCAL_IMAGE_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps004-hero.png"
LOCAL_PROMPT_PACKET_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps004-prompt-packet.json"
LOCAL_LEDGER_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps004-attempt-ledger.json"
LOCAL_NOTE_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps004-provider-note.md"
LOCAL_FAILURE_PATH = LOCAL_OUTPUT_DIR / "failed-provider-attempts.json"
LOCAL_SUMMARY_PATH = LOCAL_OUTPUT_DIR / "last-run-summary.json"

B2_PREFIX = "proofstudio/ps-004"

B2_REQUIRED_ENV = [
    "B2_KEY_ID",
    "B2_APP_KEY",
    "B2_BUCKET",
    "B2_REGION",
]

CLOUDFLARE_REQUIRED_ENV = [
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_IMAGE_MODEL_PRIMARY",
    "CLOUDFLARE_IMAGE_MODEL_FALLBACK",
]

PROVIDER_ID = "cloudflare-workers-ai"
JOB_TYPE = "image_generation"
API_METHOD = "workers-ai-run"
BUDGET_MODE = os.getenv("PROOFSTUDIO_BUDGET_MODE", "free-only")

DEFAULT_PRIMARY_MODEL = "@cf/bytedance/stable-diffusion-xl-lightning"
DEFAULT_FALLBACK_MODEL = "@cf/stabilityai/stable-diffusion-xl-base-1.0"

CLOUDFLARE_ENDPOINT = (
    "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
)

REQUEST_TIMEOUT_SECONDS = 90

# Normalized status vocabulary (subset used by this slice).
STATUS_OK = "OK"
STATUS_AUTH_FAILED = "AUTH_FAILED"
STATUS_QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
STATUS_BILLING_REQUIRED = "BILLING_REQUIRED"
STATUS_MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
STATUS_SAFETY_BLOCKED = "SAFETY_BLOCKED"
STATUS_TIMEOUT = "TIMEOUT"
STATUS_BAD_REQUEST = "BAD_REQUEST"
STATUS_PROVIDER_DOWN = "PROVIDER_DOWN"
STATUS_SKIPPED_MISSING_KEY = "SKIPPED_MISSING_KEY"
STATUS_UNKNOWN_ERROR = "UNKNOWN_ERROR"

# Failures where retrying the same model later could plausibly succeed.
RETRYABLE_STATUSES = {
    STATUS_QUOTA_EXCEEDED,
    STATUS_MODEL_UNAVAILABLE,
    STATUS_TIMEOUT,
    STATUS_PROVIDER_DOWN,
    STATUS_UNKNOWN_ERROR,
}

# Failures where the router is allowed to try the next model/provider.
# OK and SKIPPED_MISSING_KEY are terminal and do not continue.
FALLBACK_ALLOWED_STATUSES = {
    STATUS_AUTH_FAILED,
    STATUS_QUOTA_EXCEEDED,
    STATUS_BILLING_REQUIRED,
    STATUS_MODEL_UNAVAILABLE,
    STATUS_SAFETY_BLOCKED,
    STATUS_BAD_REQUEST,
    STATUS_TIMEOUT,
    STATUS_PROVIDER_DOWN,
    STATUS_UNKNOWN_ERROR,
}

SAFETY_KEYWORDS = (
    "safety",
    "content filter",
    "content-filter",
    "blocked",
    "prohibited",
    "not allowed",
    "policy",
)
QUOTA_KEYWORDS = (
    "quota",
    "rate limit",
    "rate-limit",
    "too many requests",
    "exceeded",
    "limit reached",
)
BILLING_KEYWORDS = (
    "billing",
    "payment",
    "paid plan",
    "subscription",
    "upgrade",
    "credit",
)
MODEL_KEYWORDS = ("not found", "unknown model", "not available", "unavailable")

SECRET_SCRUB_PATTERNS = [
    (re.compile(r"Bearer\s+[A-Za-z0-9\-_.=~]+"), "Bearer ***"),
    (
        re.compile(
            r"(?i)(authorization|api[_-]?key|api[_-]?token|token|secret)[\s:=]+[^\s,;'\"]+"
        ),
        r"\1=***",
    ),
]


def fail(message: str, code: int = 1) -> None:
    print(f"FAIL {message}", file=sys.stderr)
    raise SystemExit(code)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def scrub_secrets(text: str) -> str:
    if not text:
        return ""
    scrubbed = text
    for pattern, replacement in SECRET_SCRUB_PATTERNS:
        scrubbed = pattern.sub(replacement, scrubbed)
    return scrubbed


def require_b2_env() -> dict[str, str]:
    load_dotenv(REPO_ROOT / ".env")

    missing = [name for name in B2_REQUIRED_ENV if not os.getenv(name)]
    if missing:
        print("Missing required B2 environment variables:")
        for name in missing:
            print(f"   - {name}")
        print("Update your local .env file. Never commit .env.")
        raise SystemExit(2)

    return {name: os.environ[name] for name in B2_REQUIRED_ENV}


def collect_cloudflare_env() -> dict[str, str]:
    """Return Cloudflare env values. Missing values are recorded but not raised here."""
    values: dict[str, str] = {}
    for name in CLOUDFLARE_REQUIRED_ENV:
        values[name] = os.getenv(name, "").strip()
    return values


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_prompt_packet() -> dict[str, Any]:
    return {
        "artifact_type": "proofstudio_visual_generation_prompt",
        "schema_version": "ps-004.1",
        "created_at": now_iso(),
        "provider_target": PROVIDER_ID,
        "job_type": JOB_TYPE,
        "budget_mode": BUDGET_MODE,
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


def normalize_cloudflare_status(
    status_code: int | None,
    error_text: str,
    exception: BaseException | None,
) -> str:
    if exception is not None:
        if isinstance(exception, requests.exceptions.Timeout):
            return STATUS_TIMEOUT
        if isinstance(exception, requests.exceptions.ConnectionError):
            return STATUS_PROVIDER_DOWN
        return STATUS_UNKNOWN_ERROR

    lower = (error_text or "").lower()

    if status_code is None:
        if any(k in lower for k in SAFETY_KEYWORDS):
            return STATUS_SAFETY_BLOCKED
        if any(k in lower for k in QUOTA_KEYWORDS):
            return STATUS_QUOTA_EXCEEDED
        if any(k in lower for k in BILLING_KEYWORDS):
            return STATUS_BILLING_REQUIRED
        if any(k in lower for k in MODEL_KEYWORDS):
            return STATUS_MODEL_UNAVAILABLE
        return STATUS_UNKNOWN_ERROR

    if status_code in (401, 403):
        return STATUS_AUTH_FAILED
    if status_code == 402:
        return STATUS_BILLING_REQUIRED
    if status_code == 429:
        return STATUS_QUOTA_EXCEEDED
    if status_code == 404:
        return STATUS_MODEL_UNAVAILABLE
    if status_code == 400:
        if any(k in lower for k in SAFETY_KEYWORDS):
            return STATUS_SAFETY_BLOCKED
        if any(k in lower for k in BILLING_KEYWORDS):
            return STATUS_BILLING_REQUIRED
        return STATUS_BAD_REQUEST
    if status_code >= 500:
        return STATUS_PROVIDER_DOWN

    if any(k in lower for k in SAFETY_KEYWORDS):
        return STATUS_SAFETY_BLOCKED
    if any(k in lower for k in QUOTA_KEYWORDS):
        return STATUS_QUOTA_EXCEEDED
    if any(k in lower for k in BILLING_KEYWORDS):
        return STATUS_BILLING_REQUIRED
    if any(k in lower for k in MODEL_KEYWORDS):
        return STATUS_MODEL_UNAVAILABLE
    return STATUS_UNKNOWN_ERROR


def classify_status(normalized_status: str) -> tuple[bool, bool]:
    retryable = normalized_status in RETRYABLE_STATUSES
    fallback_allowed = normalized_status in FALLBACK_ALLOWED_STATUSES
    return retryable, fallback_allowed


def estimate_cost() -> dict[str, Any]:
    return {
        "amount": 0.0,
        "currency": "USD",
        "cost_basis": "free allocation",
        "free_tier_used": True,
        "paid_required": False,
        "provider_credit_note": (
            "Cloudflare Workers AI free allocation assumed for this smoke run."
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


def detect_image_mime_from_bytes(data: bytes, fallback: str | None = None) -> str:
    """Detect actual image MIME from magic bytes.

    Provider headers can be wrong or generic. For a provenance system, stored
    media_type and extension must match the actual bytes.
    """
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "image/gif"
    return fallback or "application/octet-stream"


def extract_image_bytes_from_json(data: Any) -> tuple[bytes | None, str | None]:
    """Best-effort extraction of image bytes from a Cloudflare JSON response."""
    if not isinstance(data, dict):
        return None, None

    # Cloudflare error envelope: do not treat as image.
    if data.get("success") is False or data.get("errors"):
        return None, None

    candidate_keys = ("image", "result", "data", "output")
    for key in candidate_keys:
        value = data.get(key)
        if isinstance(value, str):
            try:
                return base64.b64decode(value, validate=True), None
            except Exception:
                continue
        if isinstance(value, dict):
            for inner_key in ("image", "b64", "data", "base64"):
                inner = value.get(inner_key)
                if isinstance(inner, str):
                    try:
                        return base64.b64decode(inner, validate=True), None
                    except Exception:
                        continue
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    try:
                        return base64.b64decode(item, validate=True), None
                    except Exception:
                        continue
                if isinstance(item, dict):
                    image_bytes, _ = extract_image_bytes_from_json(item)
                    if image_bytes:
                        return image_bytes, None

    return None, None


def cloudflare_error_summary(status_code: int | None, body_text: str) -> str:
    """Pull a compact, secret-scrubbed summary out of a Cloudflare error body."""
    if not body_text:
        return f"HTTP {status_code}" if status_code is not None else "no response body"

    summary = body_text.strip()
    try:
        data = json.loads(summary)
        if isinstance(data, dict):
            errors = data.get("errors") or []
            messages = []
            for error in errors if isinstance(errors, list) else []:
                if isinstance(error, dict):
                    code = error.get("code")
                    message = error.get("message")
                    if message:
                        messages.append(f"[{code}] {message}" if code else str(message))
                    elif code is not None:
                        messages.append(f"[code={code}]")
            if data.get("message") and not messages:
                messages.append(str(data.get("message")))
            if messages:
                summary = "; ".join(messages)
            elif data.get("success") is False:
                summary = "success=false (no error message body)"
    except ValueError:
        pass

    return scrub_secrets(summary[:500])


def build_attempt(
    attempt_index: int,
    model: str,
    *,
    status: str,
    normalized_status: str,
    started_at: str,
    finished_at: str,
    raw_error_type: str | None = None,
    sanitized_error_message: str | None = None,
    skip_reason: str | None = None,
    output_asset_refs: list[dict[str, Any]] | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    retryable, fallback_allowed = classify_status(normalized_status)
    return {
        "attempt_id": uuid.uuid4().hex,
        "attempt_index": attempt_index,
        "provider": PROVIDER_ID,
        "model": model,
        "api_method": API_METHOD,
        "job_type": JOB_TYPE,
        "status": status,
        "normalized_status": normalized_status,
        "started_at": started_at,
        "finished_at": finished_at,
        "latency_ms": max(
            0,
            int(
                (
                    datetime.fromisoformat(finished_at)
                    - datetime.fromisoformat(started_at)
                ).total_seconds()
                * 1000
            ),
        ),
        "retryable": retryable,
        "fallback_allowed": fallback_allowed,
        "skip_reason": skip_reason,
        "raw_error_type": raw_error_type,
        "sanitized_error_message": sanitized_error_message,
        "estimated_cost": estimate_cost(),
        "free_or_paid": "free",
        "output_asset_refs": output_asset_refs or [],
        "notes": notes or "",
    }


def run_cloudflare_attempt(
    account_id: str,
    token: str,
    model: str,
    prompt: str,
    attempt_index: int,
) -> tuple[dict[str, Any], bytes | None, str | None]:
    """Run a single Cloudflare Workers AI image generation attempt.

    Returns (attempt_record, image_bytes_or_None, mime_type_or_None).
    Never raises; all failures are normalized into the attempt record.
    """
    url = CLOUDFLARE_ENDPOINT.format(account_id=account_id, model=model)
    started_at = now_iso()

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "image/png, application/json",
            },
            json={"prompt": prompt},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.exceptions.Timeout as exc:
        return (
            build_attempt(
                attempt_index,
                model,
                status="failed",
                normalized_status=STATUS_TIMEOUT,
                started_at=started_at,
                finished_at=now_iso(),
                raw_error_type=type(exc).__name__,
                sanitized_error_message=scrub_secrets(
                    f"Request timed out after {REQUEST_TIMEOUT_SECONDS}s."
                ),
                notes="Cloudflare Workers AI request exceeded timeout.",
            ),
            None,
            None,
        )
    except requests.exceptions.ConnectionError as exc:
        return (
            build_attempt(
                attempt_index,
                model,
                status="failed",
                normalized_status=STATUS_PROVIDER_DOWN,
                started_at=started_at,
                finished_at=now_iso(),
                raw_error_type=type(exc).__name__,
                sanitized_error_message="Connection error contacting Cloudflare API.",
                notes="Network/connection failure reaching Cloudflare Workers AI.",
            ),
            None,
            None,
        )
    except requests.exceptions.RequestException as exc:
        return (
            build_attempt(
                attempt_index,
                model,
                status="failed",
                normalized_status=STATUS_UNKNOWN_ERROR,
                started_at=started_at,
                finished_at=now_iso(),
                raw_error_type=type(exc).__name__,
                sanitized_error_message=scrub_secrets(str(exc))[:500],
                notes="Unexpected requests exception while calling Cloudflare.",
            ),
            None,
            None,
        )

    finished_at = now_iso()
    content_type = response.headers.get("content-type", "") or ""
    status_code = response.status_code

    if status_code == 200:
        if content_type.startswith("image/") and response.content:
            mime = content_type.split(";")[0].strip() or "image/png"
            return (
                build_attempt(
                    attempt_index,
                    model,
                    status="succeeded",
                    normalized_status=STATUS_OK,
                    started_at=started_at,
                    finished_at=finished_at,
                    notes=(
                        "Cloudflare returned raw image bytes "
                        f"(content-type={mime})."
                    ),
                ),
                response.content,
                mime,
            )

        # Try JSON extraction.
        body_text = response.text or ""
        parsed: Any = None
        try:
            parsed = response.json()
        except ValueError:
            parsed = None

        if parsed is not None:
            if isinstance(parsed, dict) and (
                parsed.get("success") is False or parsed.get("errors")
            ):
                normalized = normalize_cloudflare_status(
                    status_code, cloudflare_error_summary(status_code, body_text), None
                )
                return (
                    build_attempt(
                        attempt_index,
                        model,
                        status="failed",
                        normalized_status=normalized,
                        started_at=started_at,
                        finished_at=finished_at,
                        raw_error_type=f"HTTP{status_code}",
                        sanitized_error_message=cloudflare_error_summary(
                            status_code, body_text
                        ),
                        notes="Cloudflare returned an error envelope with HTTP 200.",
                    ),
                    None,
                    None,
                )

            image_bytes, _ = extract_image_bytes_from_json(parsed)
            if image_bytes:
                return (
                    build_attempt(
                        attempt_index,
                        model,
                        status="succeeded",
                        normalized_status=STATUS_OK,
                        started_at=started_at,
                        finished_at=finished_at,
                        notes="Cloudflare returned image bytes inside a JSON body.",
                    ),
                    image_bytes,
                    "image/png",
                )

        # 200 but no parseable image.
        return (
            build_attempt(
                attempt_index,
                model,
                status="failed",
                normalized_status=STATUS_UNKNOWN_ERROR,
                started_at=started_at,
                finished_at=finished_at,
                raw_error_type=f"HTTP{status_code}",
                sanitized_error_message=cloudflare_error_summary(
                    status_code, body_text or "HTTP 200 with no image body"
                ),
                notes="Cloudflare returned HTTP 200 but no usable image payload.",
            ),
            None,
            None,
        )

    # Non-200 response.
    body_text = response.text or ""
    normalized = normalize_cloudflare_status(
        status_code, cloudflare_error_summary(status_code, body_text), None
    )
    return (
        build_attempt(
            attempt_index,
            model,
            status="failed",
            normalized_status=normalized,
            started_at=started_at,
            finished_at=finished_at,
            raw_error_type=f"HTTP{status_code}",
            sanitized_error_message=cloudflare_error_summary(status_code, body_text),
            notes=f"Cloudflare Workers AI returned HTTP {status_code}.",
        ),
        None,
        None,
    )


def write_failed_provider_attempts(
    attempts: list[dict[str, Any]], reason: str
) -> None:
    LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "ok": False,
        "proof": "PS-004 provider router did not produce a visual asset.",
        "provider": PROVIDER_ID,
        "job_type": JOB_TYPE,
        "reason": reason,
        "attempt_count": len(attempts),
        "attempts": attempts,
        "written_at": now_iso(),
    }
    LOCAL_FAILURE_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def write_local_ledger(ledger: dict[str, Any]) -> None:
    LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_LEDGER_PATH.write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def write_local_prompt_packet(packet: dict[str, Any], selected: dict[str, Any]) -> None:
    LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "proofstudio_artifact_type": "visual_prompt_packet",
        "schema_version": "ps-004.1",
        "provider": PROVIDER_ID,
        "job_type": JOB_TYPE,
        "budget_mode": BUDGET_MODE,
        "selected": selected,
        "prompt_packet": packet,
    }
    LOCAL_PROMPT_PACKET_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def write_provider_note(
    ledger: dict[str, Any], image_path: Path, image_mime_type: str
) -> None:
    LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    selected = ledger.get("selected_model") or "(none)"
    lines = [
        "# PS-004 Provider Router + Cloudflare Workers AI Provider Note",
        "",
        f"- Generated at: `{ledger.get('completed_at')}`",
        f"- Provider: `{PROVIDER_ID}`",
        f"- Selected model: `{selected}`",
        f"- API method: `{API_METHOD}`",
        f"- Job type: `{JOB_TYPE}`",
        f"- Final status: `{ledger.get('final_status')}`",
        f"- Local image: `{image_path}`",
        f"- Image MIME type: `{image_mime_type}`",
        "",
        "## Truth boundary",
        "",
        "This proves provider-routed visual generation plus storage/manifest verification.",
        "It does not prove semantic truth, legal authenticity, or C2PA authenticity.",
        "The manifest proves recorded workflow integrity and byte-level verification.",
        "",
        "## Attempt summary",
        "",
        "| # | model | status | normalized | latency_ms |",
        "|---|-------|--------|------------|-----------|",
    ]

    for attempt in ledger.get("attempts", []):
        lines.append(
            f"| {attempt.get('attempt_index')} "
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


def build_ledger(
    attempts: list[dict[str, Any]],
    *,
    final_status: str,
    selected_provider: str | None,
    selected_model: str | None,
    output_assets: list[dict[str, Any]] | None = None,
    b2_artifacts: list[dict[str, Any]] | None = None,
    manifest_uri: str | None = None,
    manifest_hash: str | None = None,
) -> dict[str, Any]:
    run_id = uuid.uuid4().hex
    created_at = attempts[0]["started_at"] if attempts else now_iso()
    completed_at = attempts[-1]["finished_at"] if attempts else now_iso()
    return {
        "ledger_id": f"ps-004-{run_id}",
        "campaign_id": "proofstudio-launch",
        "job_id": run_id,
        "job_type": JOB_TYPE,
        "budget_mode": BUDGET_MODE,
        "created_at": created_at,
        "completed_at": completed_at,
        "final_status": final_status,
        "selected_provider": selected_provider,
        "selected_model": selected_model,
        "attempts": attempts,
        "output_assets": output_assets or [],
        "b2_artifacts": b2_artifacts or [],
        "manifest_uri": manifest_uri,
        "manifest_hash": manifest_hash,
        "truth_boundary": (
            "Manifest proves recorded workflow integrity and byte-level asset "
            "verification only. It does not prove semantic truth, legal authenticity, "
            "or C2PA authenticity."
        ),
    }


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


def run_cloudflare_router(
    cf_env: dict[str, str], prompt: str
) -> tuple[list[dict[str, Any]], bytes | None, str | None, str | None]:
    """Try Cloudflare primary then fallback. Returns attempts + best image."""
    account_id = cf_env["CLOUDFLARE_ACCOUNT_ID"]
    token = cf_env["CLOUDFLARE_API_TOKEN"]
    models = [
        cf_env.get("CLOUDFLARE_IMAGE_MODEL_PRIMARY") or DEFAULT_PRIMARY_MODEL,
        cf_env.get("CLOUDFLARE_IMAGE_MODEL_FALLBACK") or DEFAULT_FALLBACK_MODEL,
    ]

    attempts: list[dict[str, Any]] = []
    for index, model in enumerate(models):
        attempt, image_bytes, mime_type = run_cloudflare_attempt(
            account_id=account_id,
            token=token,
            model=model,
            prompt=prompt,
            attempt_index=index,
        )
        attempts.append(attempt)
        if attempt["normalized_status"] == STATUS_OK and image_bytes:
            return attempts, image_bytes, mime_type, model

    return attempts, None, None, None


def upload_and_verify(
    b2_env: dict[str, str],
    image_path: Path,
    image_mime_type: str,
    selected_model: str,
    ledger: dict[str, Any],
) -> dict[str, Any]:
    backend = S3StorageBackend.for_backblaze(
        bucket=b2_env["B2_BUCKET"],
        region=b2_env["B2_REGION"],
        key_id=b2_env["B2_KEY_ID"],
        app_key=b2_env["B2_APP_KEY"],
        auto_lifecycle=False,
        preflight=True,
    )

    sink = ObjectStorageSink(backend, prefix=B2_PREFIX)

    assets = [
        Asset(
            url=image_path.resolve().as_uri(),
            media_type=image_mime_type,
            metadata={
                "proofstudio_test": "ps-004",
                "artifact_type": "cloudflare_visual_asset",
                "provider": PROVIDER_ID,
                "model": selected_model,
                "api_method": API_METHOD,
            },
        ),
        Asset(
            url=LOCAL_PROMPT_PACKET_PATH.resolve().as_uri(),
            media_type="application/json",
            metadata={
                "proofstudio_test": "ps-004",
                "artifact_type": "visual_prompt_packet",
                "provider": PROVIDER_ID,
                "model": selected_model,
            },
        ),
        Asset(
            url=LOCAL_LEDGER_PATH.resolve().as_uri(),
            media_type="application/json",
            metadata={
                "proofstudio_test": "ps-004",
                "artifact_type": "provider_attempt_ledger",
                "provider": PROVIDER_ID,
            },
        ),
        Asset(
            url=LOCAL_NOTE_PATH.resolve().as_uri(),
            media_type="text/markdown",
            metadata={
                "proofstudio_test": "ps-004",
                "artifact_type": "provider_note",
                "provider": PROVIDER_ID,
                "model": selected_model,
            },
        ),
    ]

    try:
        result = Pipeline.ingest(
            assets=assets,
            source="cloudflare-workers-ai-visual",
            source_metadata={
                "scenario": "PS-004",
                "description": (
                    "Cloudflare Workers AI generated visual campaign asset for "
                    "ProofStudio, routed through the provider router, stored in "
                    "B2 and verified with a Genblaze manifest."
                ),
                "provider": PROVIDER_ID,
                "model": selected_model,
                "api_method": API_METHOD,
                "job_type": JOB_TYPE,
                "budget_mode": BUDGET_MODE,
            },
            name="proofstudio-ps-004-provider-router-cloudflare",
            tenant_id="local",
        )

        sink.write_run(result.run, result.manifest)
    except Exception as exc:
        fail(
            "B2/Genblaze upload failed: "
            f"{type(exc).__name__}: {scrub_secrets(str(exc))}"
        )

    if not result.manifest.verify():
        fail("In-memory manifest verification failed after B2 write.")

    failures = transfer_failures(result.manifest)
    if failures:
        fail(f"Asset transfer failures reported after B2 write: {failures}")

    try:
        stored_manifest = sink.read_manifest(result.run, verify=True)
    except Exception as exc:
        fail(
            "Failed to read stored manifest back from B2: "
            f"{type(exc).__name__}: {scrub_secrets(str(exc))}"
        )

    if not stored_manifest.verify():
        fail("Stored manifest verification failed after reading back from B2.")

    stored_failures = transfer_failures(stored_manifest)
    if stored_failures:
        fail(f"Stored manifest contains transfer failures: {stored_failures}")

    manifest_uri = result.manifest.manifest_uri or sink.manifest_url_for(result.run)
    manifest_hash = result.manifest.canonical_hash

    asset_summaries = summarize_assets(result)

    return {
        "result": result,
        "asset_summaries": asset_summaries,
        "manifest_uri": manifest_uri,
        "manifest_hash": manifest_hash,
        "transfer_failures": failures,
        "stored_transfer_failures": stored_failures,
        "in_memory_manifest_verify": result.manifest.verify(),
        "stored_manifest_verify": stored_manifest.verify(),
        "run_id": result.run.run_id,
        "run_status": str(result.run.status),
    }


def main() -> None:
    LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    b2_env = require_b2_env()
    cf_env = collect_cloudflare_env()

    missing_cf = [
        name for name in CLOUDFLARE_REQUIRED_ENV if not cf_env.get(name)
    ]

    packet = build_prompt_packet()
    prompt_text = packet["prompt"]

    # Missing Cloudflare keys: record a SKIPPED_MISSING_KEY ledger and fail.
    if missing_cf:
        started_at = now_iso()
        finished_at = started_at
        skip_attempt = build_attempt(
            attempt_index=0,
            model=cf_env.get("CLOUDFLARE_IMAGE_MODEL_PRIMARY") or DEFAULT_PRIMARY_MODEL,
            status="skipped",
            normalized_status=STATUS_SKIPPED_MISSING_KEY,
            started_at=started_at,
            finished_at=finished_at,
            raw_error_type="MissingCredentials",
            sanitized_error_message=(
                "Cloudflare provider skipped: required environment variables missing."
            ),
            skip_reason=(
                "Missing required Cloudflare env vars: " + ", ".join(missing_cf)
            ),
            notes=(
                "No Cloudflare credentials configured. Not attempting API calls. "
                "No image generated."
            ),
        )
        ledger = build_ledger(
            [skip_attempt],
            final_status="blocked",
            selected_provider=None,
            selected_model=None,
        )
        write_local_ledger(ledger)
        write_failed_provider_attempts(
            [skip_attempt],
            reason=(
                "Cloudflare keys missing. Required env: "
                + ", ".join(CLOUDFLARE_REQUIRED_ENV)
            ),
        )
        print(
            json.dumps(
                {
                    "ok": False,
                    "proof": "PS-004 blocked: Cloudflare credentials missing.",
                    "normalized_status": STATUS_SKIPPED_MISSING_KEY,
                    "missing_env": missing_cf,
                    "local_ledger": str(LOCAL_LEDGER_PATH),
                    "local_failure_report": str(LOCAL_FAILURE_PATH),
                    "next_step": (
                        "Set CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN, "
                        "CLOUDFLARE_IMAGE_MODEL_PRIMARY, and "
                        "CLOUDFLARE_IMAGE_MODEL_FALLBACK in your local .env."
                    ),
                },
                indent=2,
            )
        )
        fail("PS-004 blocked: Cloudflare credentials missing (SKIPPED_MISSING_KEY).")

    # Attempt Cloudflare primary then fallback.
    attempts, image_bytes, image_mime_type, selected_model = run_cloudflare_router(
        cf_env, prompt_text
    )

    success_attempt = next(
        (a for a in attempts if a["normalized_status"] == STATUS_OK), None
    )

    if success_attempt is None or image_bytes is None:
        ledger = build_ledger(
            attempts,
            final_status="failed",
            selected_provider=None,
            selected_model=None,
        )
        write_local_ledger(ledger)
        write_failed_provider_attempts(
            attempts,
            reason="All Cloudflare Workers AI image models failed.",
        )
        print(
            json.dumps(
                {
                    "ok": False,
                    "proof": "PS-004 failed: no Cloudflare model produced an image.",
                    "final_status": "failed",
                    "attempts": [
                        {
                            "attempt_index": a["attempt_index"],
                            "model": a["model"],
                            "normalized_status": a["normalized_status"],
                            "sanitized_error_message": a[
                                "sanitized_error_message"
                            ],
                        }
                        for a in attempts
                    ],
                    "local_ledger": str(LOCAL_LEDGER_PATH),
                    "local_failure_report": str(LOCAL_FAILURE_PATH),
                },
                indent=2,
            )
        )
        fail(
            "PS-004 failed: all Cloudflare Workers AI models failed. "
            f"See {LOCAL_FAILURE_PATH}."
        )

    # Success: persist image and metadata locally.
    detected_image_mime_type = detect_image_mime_from_bytes(image_bytes, image_mime_type)
    if detected_image_mime_type != image_mime_type:
        print(
            "INFO image MIME corrected from provider/header value "
            f"{image_mime_type!r} to byte-detected value {detected_image_mime_type!r}."
        )
        image_mime_type = detected_image_mime_type

    ext = mime_to_ext(image_mime_type)
    image_path = LOCAL_IMAGE_PATH.with_suffix(ext)
    image_path.write_bytes(image_bytes)

    image_sha = sha256_of_file(image_path)
    success_attempt["output_asset_refs"] = [
        {
            "kind": "generated_image",
            "local_path": str(image_path),
            "media_type": image_mime_type,
            "sha256": image_sha,
            "size_bytes": image_path.stat().st_size,
        }
    ]

    write_local_prompt_packet(
        packet,
        selected={
            "provider": PROVIDER_ID,
            "model": selected_model,
            "api_method": API_METHOD,
            "image_mime_type": image_mime_type,
            "image_sha256": image_sha,
        },
    )

    ledger_pre_upload = build_ledger(
        attempts,
        final_status="succeeded",
        selected_provider=PROVIDER_ID,
        selected_model=selected_model,
        output_assets=[
            {
                "kind": "generated_image",
                "local_path": str(image_path),
                "media_type": image_mime_type,
                "sha256": image_sha,
                "size_bytes": image_path.stat().st_size,
            }
        ],
    )
    write_local_ledger(ledger_pre_upload)
    write_provider_note(ledger_pre_upload, image_path, image_mime_type)

    # Upload through Genblaze/B2 and verify the manifest.
    upload = upload_and_verify(
        b2_env=b2_env,
        image_path=image_path,
        image_mime_type=image_mime_type,
        selected_model=selected_model,
        ledger=ledger_pre_upload,
    )

    # Re-write the ledger and note with B2/manifest references included.
    final_ledger = build_ledger(
        attempts,
        final_status="succeeded",
        selected_provider=PROVIDER_ID,
        selected_model=selected_model,
        output_assets=[
            {
                "kind": "generated_image",
                "local_path": str(image_path),
                "media_type": image_mime_type,
                "sha256": image_sha,
                "size_bytes": image_path.stat().st_size,
                "b2_manifest_asset_id": upload["asset_summaries"][0]["asset_id"]
                if upload["asset_summaries"]
                else None,
            }
        ],
        b2_artifacts=upload["asset_summaries"],
        manifest_uri=upload["manifest_uri"],
        manifest_hash=upload["manifest_hash"],
    )
    write_local_ledger(final_ledger)
    write_provider_note(final_ledger, image_path, image_mime_type)

    summary = {
        "ok": True,
        "proof": (
            "PS-004 Provider Router + Cloudflare Workers AI + B2 + Genblaze "
            "manifest smoke test passed."
        ),
        "provider": PROVIDER_ID,
        "selected_model": selected_model,
        "api_method": API_METHOD,
        "job_type": JOB_TYPE,
        "budget_mode": BUDGET_MODE,
        "image_mime_type": image_mime_type,
        "image_sha256": image_sha,
        "attempt_count": len(attempts),
        "attempts": [
            {
                "attempt_index": a["attempt_index"],
                "model": a["model"],
                "status": a["status"],
                "normalized_status": a["normalized_status"],
                "latency_ms": a["latency_ms"],
                "fallback_allowed": a["fallback_allowed"],
            }
            for a in attempts
        ],
        "run_id": upload["run_id"],
        "run_status": upload["run_status"],
        "manifest_hash": upload["manifest_hash"],
        "manifest_uri": upload["manifest_uri"],
        "in_memory_manifest_verify": upload["in_memory_manifest_verify"],
        "stored_manifest_verify": upload["stored_manifest_verify"],
        "transfer_failures": upload["transfer_failures"],
        "stored_transfer_failures": upload["stored_transfer_failures"],
        "asset_count": len(upload["asset_summaries"]),
        "assets": upload["asset_summaries"],
        "local_image": str(image_path),
        "local_prompt_packet": str(LOCAL_PROMPT_PACKET_PATH),
        "local_attempt_ledger": str(LOCAL_LEDGER_PATH),
        "local_provider_note": str(LOCAL_NOTE_PATH),
    }

    LOCAL_SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
