#!/usr/bin/env python3
"""
PS-005: Pollinations no-key fallback visual provider proof.

What this proves:
- ProofStudio can generate a visual asset through a no-key emergency fallback
  provider (Pollinations) while preserving the same B2 + Genblaze provenance
  pipeline used by PS-001A and PS-004.
- Every provider attempt is recorded in a normalized attempt ledger.
- Failures (HTML, JSON errors, tiny invalid payloads, timeouts, non-image bytes,
  HTTP errors) are mapped to normalized router statuses and never faked.
- On success the generated image, prompt packet, attempt ledger, and provider
  note are stored in Backblaze B2 through the Genblaze pipeline.
- The Genblaze manifest is written to B2, read back, and verified.
- The run must have zero transfer failures.

This script does not fake success. If POLLINATIONS_ENABLED is disabled it records
a SKIPPED_DISABLED ledger and fails. If Pollinations fails to return a valid
image it writes a failed-provider-attempts report and exits non-zero without
uploading any asset. No API key is required and none is faked.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import sys
import tempfile
import urllib.parse
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
LOCAL_OUTPUT_DIR = Path(tempfile.gettempdir()) / "proofstudio-ps-005"
LOCAL_IMAGE_STEM = LOCAL_OUTPUT_DIR / "proofstudio-ps005-hero"
LOCAL_PROMPT_PACKET_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps005-prompt-packet.json"
LOCAL_LEDGER_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps005-attempt-ledger.json"
LOCAL_NOTE_PATH = LOCAL_OUTPUT_DIR / "proofstudio-ps005-provider-note.md"
LOCAL_FAILURE_PATH = LOCAL_OUTPUT_DIR / "failed-provider-attempts.json"
LOCAL_SUMMARY_PATH = LOCAL_OUTPUT_DIR / "last-run-summary.json"

B2_PREFIX = "proofstudio/ps-005"

B2_REQUIRED_ENV = [
    "B2_KEY_ID",
    "B2_APP_KEY",
    "B2_BUCKET",
    "B2_REGION",
]

PROVIDER_ID = "pollinations"
JOB_TYPE = "image_generation"
API_METHOD = "pollinations-image-get"
POLLINATIONS_MODEL = "pollinations-image-default"
POLLINATIONS_ENDPOINT = "https://image.pollinations.ai/prompt/{encoded_prompt}"

BUDGET_MODE = os.getenv("PROOFSTUDIO_BUDGET_MODE", "free-only")

REQUEST_TIMEOUT_SECONDS = 120

# Pollinations can return a tiny stub/error body; treat anything smaller than
# this as a non-image failure even if it is not obviously HTML/JSON.
MIN_IMAGE_BYTES = 1024

# Normalized status vocabulary used by this slice.
STATUS_OK = "OK"
STATUS_MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
STATUS_SAFETY_BLOCKED = "SAFETY_BLOCKED"
STATUS_TIMEOUT = "TIMEOUT"
STATUS_BAD_REQUEST = "BAD_REQUEST"
STATUS_PROVIDER_DOWN = "PROVIDER_DOWN"
STATUS_UNSUPPORTED_MODE = "UNSUPPORTED_MODE"
STATUS_SKIPPED_DISABLED = "SKIPPED_DISABLED"
STATUS_UNKNOWN_ERROR = "UNKNOWN_ERROR"

# Failures where retrying later could plausibly succeed.
RETRYABLE_STATUSES = {
    STATUS_MODEL_UNAVAILABLE,
    STATUS_TIMEOUT,
    STATUS_PROVIDER_DOWN,
    STATUS_UNKNOWN_ERROR,
}

# Failures where the router is allowed to try the next provider.
FALLBACK_ALLOWED_STATUSES = {
    STATUS_MODEL_UNAVAILABLE,
    STATUS_SAFETY_BLOCKED,
    STATUS_BAD_REQUEST,
    STATUS_TIMEOUT,
    STATUS_PROVIDER_DOWN,
    STATUS_UNSUPPORTED_MODE,
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
    "nsfw",
)
QUOTA_KEYWORDS = (
    "quota",
    "rate limit",
    "rate-limit",
    "too many requests",
    "exceeded",
    "limit reached",
)
MODEL_KEYWORDS = (
    "not found",
    "unknown model",
    "not available",
    "unavailable",
    "no model",
    "invalid model",
)

SECRET_SCRUB_PATTERNS = [
    (re.compile(r"Bearer\s+[A-Za-z0-9\-_.=~]+"), "Bearer\u0020***"),
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


def is_disabled(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"false", "0", "no", "off"}


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


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_prompt_packet() -> dict[str, Any]:
    return {
        "artifact_type": "proofstudio_visual_generation_prompt",
        "schema_version": "ps-005.1",
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


def estimate_cost() -> dict[str, Any]:
    return {
        "amount": 0.0,
        "currency": "USD",
        "cost_basis": "no-key public endpoint",
        "free_tier_used": True,
        "paid_required": False,
        "provider_credit_note": (
            "Pollinations is a no-key public image endpoint. Estimated cost is 0.0 USD."
        ),
    }


def classify_status(normalized_status: str) -> tuple[bool, bool]:
    retryable = normalized_status in RETRYABLE_STATUSES
    fallback_allowed = normalized_status in FALLBACK_ALLOWED_STATUSES
    return retryable, fallback_allowed


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


# Image magic-byte signatures defined explicitly via bytes.fromhex(...) to avoid
# any escaped-byte validation ambiguity. Provider headers can lie; stored
# media_type and extension must match the actual bytes.
PNG_SIG = bytes.fromhex("89504e470d0a1a0a")
JPEG_SIG = bytes.fromhex("ffd8ff")
RIFF_SIG = bytes.fromhex("52494646")  # "RIFF"
WEBP_TAG = bytes.fromhex("57454250")  # "WEBP"
GIF87_SIG = bytes.fromhex("474946383761")  # "GIF87a"
GIF89_SIG = bytes.fromhex("474946383961")  # "GIF89a"


def detect_image_mime_from_bytes(data: bytes, fallback: str | None = None) -> str:
    """Detect actual image MIME purely from magic bytes.

    Returns 'application/octet-stream' (or fallback) when bytes do not look like
    a supported image, so callers can reject HTML/JSON/error stubs.
    """
    if data.startswith(PNG_SIG):
        return "image/png"
    if data.startswith(JPEG_SIG):
        return "image/jpeg"
    if data.startswith(RIFF_SIG) and data[8:12] == WEBP_TAG:
        return "image/webp"
    if data.startswith(GIF87_SIG) or data.startswith(GIF89_SIG):
        return "image/gif"
    return fallback or "application/octet-stream"


def is_image_mime(mime_type: str) -> bool:
    return mime_type.startswith("image/")


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


def looks_like_html(data: bytes) -> bool:
    head = data[:512].lstrip()
    if head[:5].lower() == b"<html" or head[:9].lower() == b"<!doctype":
        return True
    if head[:1] == b"<" and b"</" in data[:2048].lower():
        return True
    return False


def looks_like_json(data: bytes) -> bool:
    head = data[:512].lstrip()
    return head[:1] in (b"{", b"[")


def normalize_pollinations_status(
    status_code: int | None,
    body_text: str,
    exception: BaseException | None,
) -> str:
    if exception is not None:
        if isinstance(exception, requests.exceptions.Timeout):
            return STATUS_TIMEOUT
        if isinstance(exception, requests.exceptions.ConnectionError):
            return STATUS_PROVIDER_DOWN
        return STATUS_UNKNOWN_ERROR

    lower = (body_text or "").lower()

    if status_code is None:
        if any(k in lower for k in SAFETY_KEYWORDS):
            return STATUS_SAFETY_BLOCKED
        if any(k in lower for k in QUOTA_KEYWORDS):
            return STATUS_MODEL_UNAVAILABLE
        if any(k in lower for k in MODEL_KEYWORDS):
            return STATUS_MODEL_UNAVAILABLE
        return STATUS_UNKNOWN_ERROR

    if status_code == 400:
        if any(k in lower for k in SAFETY_KEYWORDS):
            return STATUS_SAFETY_BLOCKED
        return STATUS_BAD_REQUEST
    if status_code == 404:
        return STATUS_MODEL_UNAVAILABLE
    if status_code == 408:
        return STATUS_TIMEOUT
    if status_code in (401, 403):
        # Unexpected for a no-key endpoint; treat as provider-side problem.
        if any(k in lower for k in SAFETY_KEYWORDS):
            return STATUS_SAFETY_BLOCKED
        return STATUS_PROVIDER_DOWN
    if status_code == 429:
        return STATUS_MODEL_UNAVAILABLE
    if 400 <= status_code < 500:
        if any(k in lower for k in SAFETY_KEYWORDS):
            return STATUS_SAFETY_BLOCKED
        if any(k in lower for k in MODEL_KEYWORDS):
            return STATUS_MODEL_UNAVAILABLE
        return STATUS_BAD_REQUEST
    if status_code >= 500:
        return STATUS_PROVIDER_DOWN

    if any(k in lower for k in SAFETY_KEYWORDS):
        return STATUS_SAFETY_BLOCKED
    if any(k in lower for k in MODEL_KEYWORDS):
        return STATUS_MODEL_UNAVAILABLE
    return STATUS_UNKNOWN_ERROR


def pollinations_error_summary(status_code: int | None, body_text: str) -> str:
    """Pull a compact, secret-scrubbed summary out of a Pollinations error body."""
    if not body_text:
        return f"HTTP {status_code}" if status_code is not None else "no response body"

    summary = body_text.strip()
    try:
        data = json.loads(summary)
    except ValueError:
        data = None

    if isinstance(data, dict):
        for key in ("error", "message", "detail", "reason"):
            value = data.get(key)
            if isinstance(value, str) and value:
                summary = value
                break
            if value is not None:
                summary = json.dumps(value, ensure_ascii=False)
                break
    elif isinstance(data, list):
        summary = json.dumps(data, ensure_ascii=False)

    return scrub_secrets(summary[:500])


def build_safe_query_params() -> dict[str, str]:
    """Safe, no-secret query params for deterministic Pollinations output."""
    width = os.getenv("POLLINATIONS_WIDTH", "1024").strip() or "1024"
    height = os.getenv("POLLINATIONS_HEIGHT", "576").strip() or "576"
    model_name = os.getenv("POLLINATIONS_MODEL_NAME", "flux").strip() or "flux"
    return {
        "width": width,
        "height": height,
        "model": model_name,
        "nologo": "true",
        "referrer": "proofstudio",
    }


def run_pollinations_attempt(
    prompt: str,
    attempt_index: int,
) -> tuple[dict[str, Any], bytes | None, str | None]:
    """Run a single Pollinations image generation attempt.

    Returns (attempt_record, image_bytes_or_None, mime_type_or_None).
    Never raises; all failures are normalized into the attempt record.
    """
    encoded_prompt = urllib.parse.quote(prompt, safe="")
    params = build_safe_query_params()
    url = POLLINATIONS_ENDPOINT.format(encoded_prompt=encoded_prompt)
    started_at = now_iso()

    try:
        response = requests.get(
            url,
            params=params,
            headers={
                "Accept": "image/png, image/jpeg, image/webp, image/*",
                "User-Agent": "ProofStudio-PS-005/1.0",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
            allow_redirects=True,
        )
    except requests.exceptions.Timeout as exc:
        return (
            build_attempt(
                attempt_index,
                POLLINATIONS_MODEL,
                status="failed",
                normalized_status=STATUS_TIMEOUT,
                started_at=started_at,
                finished_at=now_iso(),
                raw_error_type=type(exc).__name__,
                sanitized_error_message=scrub_secrets(
                    f"Request timed out after {REQUEST_TIMEOUT_SECONDS}s."
                ),
                notes="Pollinations request exceeded timeout.",
            ),
            None,
            None,
        )
    except requests.exceptions.ConnectionError as exc:
        return (
            build_attempt(
                attempt_index,
                POLLINATIONS_MODEL,
                status="failed",
                normalized_status=STATUS_PROVIDER_DOWN,
                started_at=started_at,
                finished_at=now_iso(),
                raw_error_type=type(exc).__name__,
                sanitized_error_message="Connection error contacting Pollinations.",
                notes="Network/connection failure reaching Pollinations endpoint.",
            ),
            None,
            None,
        )
    except requests.exceptions.RequestException as exc:
        return (
            build_attempt(
                attempt_index,
                POLLINATIONS_MODEL,
                status="failed",
                normalized_status=STATUS_UNKNOWN_ERROR,
                started_at=started_at,
                finished_at=now_iso(),
                raw_error_type=type(exc).__name__,
                sanitized_error_message=scrub_secrets(str(exc))[:500],
                notes="Unexpected requests exception while calling Pollinations.",
            ),
            None,
            None,
        )

    finished_at = now_iso()
    status_code = response.status_code
    content = response.content or b""
    header_content_type = response.headers.get("content-type", "") or ""

    # First, trust the bytes over any header.
    detected_mime = detect_image_mime_from_bytes(content)

    if status_code == 200 and is_image_mime(detected_mime) and len(content) >= MIN_IMAGE_BYTES:
        return (
            build_attempt(
                attempt_index,
                POLLINATIONS_MODEL,
                status="succeeded",
                normalized_status=STATUS_OK,
                started_at=started_at,
                finished_at=finished_at,
                notes=(
                    "Pollinations returned raw image bytes "
                    f"(byte-detected mime={detected_mime}, "
                    f"header content-type={header_content_type.split(';')[0].strip()})."
                ),
            ),
            content,
            detected_mime,
        )

    # 200 but not a usable image: HTML, JSON error, tiny stub, or non-image bytes.
    body_text = response.text or ""
    if looks_like_html(content):
        normalized = normalize_pollinations_status(
            status_code, "html error page", None
        )
        if normalized == STATUS_UNKNOWN_ERROR:
            normalized = STATUS_PROVIDER_DOWN
        return (
            build_attempt(
                attempt_index,
                POLLINATIONS_MODEL,
                status="failed",
                normalized_status=normalized,
                started_at=started_at,
                finished_at=finished_at,
                raw_error_type="HTMLResponse",
                sanitized_error_message=(
                    "Pollinations returned an HTML page instead of image bytes."
                ),
                notes="Pollinations returned HTML (likely an error/landing page).",
            ),
            None,
            None,
        )

    if looks_like_json(content):
        normalized = normalize_pollinations_status(
            status_code, pollinations_error_summary(status_code, body_text), None
        )
        return (
            build_attempt(
                attempt_index,
                POLLINATIONS_MODEL,
                status="failed",
                normalized_status=normalized,
                started_at=started_at,
                finished_at=finished_at,
                raw_error_type=f"JSONResponse(HTTP{status_code})",
                sanitized_error_message=pollinations_error_summary(
                    status_code, body_text
                ),
                notes="Pollinations returned a JSON body instead of image bytes.",
            ),
            None,
            None,
        )

    if status_code == 200 and len(content) < MIN_IMAGE_BYTES:
        return (
            build_attempt(
                attempt_index,
                POLLINATIONS_MODEL,
                status="failed",
                normalized_status=STATUS_PROVIDER_DOWN,
                started_at=started_at,
                finished_at=finished_at,
                raw_error_type="TinyResponse",
                sanitized_error_message=scrub_secrets(
                    f"Pollinations returned only {len(content)} bytes "
                    f"(below {MIN_IMAGE_BYTES} byte minimum)."
                ),
                notes="Pollinations returned a tiny/invalid payload.",
            ),
            None,
            None,
        )

    if status_code == 200:
        # Non-image bytes that are not obviously HTML/JSON/tiny.
        normalized = normalize_pollinations_status(
            status_code,
            pollinations_error_summary(status_code, body_text) or "non-image bytes",
            None,
        )
        return (
            build_attempt(
                attempt_index,
                POLLINATIONS_MODEL,
                status="failed",
                normalized_status=normalized,
                started_at=started_at,
                finished_at=finished_at,
                raw_error_type="NonImageBytes",
                sanitized_error_message=pollinations_error_summary(
                    status_code, body_text or "non-image bytes"
                ),
                notes="Pollinations returned HTTP 200 but non-image bytes.",
            ),
            None,
            None,
        )

    # Non-200 response.
    normalized = normalize_pollinations_status(
        status_code, pollinations_error_summary(status_code, body_text), None
    )
    return (
        build_attempt(
            attempt_index,
            POLLINATIONS_MODEL,
            status="failed",
            normalized_status=normalized,
            started_at=started_at,
            finished_at=finished_at,
            raw_error_type=f"HTTP{status_code}",
            sanitized_error_message=pollinations_error_summary(
                status_code, body_text
            ),
            notes=f"Pollinations returned HTTP {status_code}.",
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
        "proof": "PS-005 fallback provider did not produce a visual asset.",
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


def write_local_prompt_packet(
    packet: dict[str, Any], selected: dict[str, Any]
) -> None:
    LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "proofstudio_artifact_type": "visual_prompt_packet",
        "schema_version": "ps-005.1",
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
        "# PS-005 Pollinations No-Key Fallback Provider Note",
        "",
        f"- Generated at: `{ledger.get('completed_at')}`",
        f"- Provider: `{PROVIDER_ID}` (no-key fallback)",
        f"- Selected model/endpoint: `{selected}`",
        f"- API method: `{API_METHOD}`",
        f"- Job type: `{JOB_TYPE}`",
        f"- Final status: `{ledger.get('final_status')}`",
        f"- Local image: `{image_path}`",
        f"- Image MIME type: `{image_mime_type}`",
        f"- Estimated cost: `0.0 USD` (no-key public endpoint)",
        "",
        "## Truth boundary",
        "",
        "Pollinations is an emergency no-key fallback visual provider, not the premium final provider.",
        "This proves provider-routed visual generation plus storage/manifest verification.",
        "It does not prove semantic truth, legal authenticity, or C2PA authenticity.",
        "The manifest proves recorded workflow integrity and byte-level verification only.",
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
        "ledger_id": f"ps-005-{run_id}",
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
            "or C2PA authenticity. Pollinations is a no-key fallback provider."
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


def upload_and_verify(
    b2_env: dict[str, str],
    image_path: Path,
    image_mime_type: str,
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
                "proofstudio_test": "ps-005",
                "artifact_type": "pollinations_visual_asset",
                "provider": PROVIDER_ID,
                "model": POLLINATIONS_MODEL,
                "api_method": API_METHOD,
            },
        ),
        Asset(
            url=LOCAL_PROMPT_PACKET_PATH.resolve().as_uri(),
            media_type="application/json",
            metadata={
                "proofstudio_test": "ps-005",
                "artifact_type": "visual_prompt_packet",
                "provider": PROVIDER_ID,
                "model": POLLINATIONS_MODEL,
            },
        ),
        Asset(
            url=LOCAL_LEDGER_PATH.resolve().as_uri(),
            media_type="application/json",
            metadata={
                "proofstudio_test": "ps-005",
                "artifact_type": "provider_attempt_ledger",
                "provider": PROVIDER_ID,
            },
        ),
        Asset(
            url=LOCAL_NOTE_PATH.resolve().as_uri(),
            media_type="text/markdown",
            metadata={
                "proofstudio_test": "ps-005",
                "artifact_type": "provider_note",
                "provider": PROVIDER_ID,
                "model": POLLINATIONS_MODEL,
            },
        ),
    ]

    try:
        result = Pipeline.ingest(
            assets=assets,
            source="pollinations-fallback-visual",
            source_metadata={
                "scenario": "PS-005",
                "description": (
                    "Pollinations no-key fallback provider generated a visual "
                    "campaign asset for ProofStudio, stored in B2 and verified "
                    "with a Genblaze manifest."
                ),
                "provider": PROVIDER_ID,
                "model": POLLINATIONS_MODEL,
                "api_method": API_METHOD,
                "job_type": JOB_TYPE,
                "budget_mode": BUDGET_MODE,
                "free_or_paid": "free",
            },
            name="proofstudio-ps-005-pollinations-fallback",
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

    packet = build_prompt_packet()
    prompt_text = packet["prompt"]

    # Respect optional POLLINATIONS_ENABLED disable flag.
    if is_disabled(os.getenv("POLLINATIONS_ENABLED")):
        started_at = now_iso()
        finished_at = started_at
        skip_attempt = build_attempt(
            attempt_index=0,
            model=POLLINATIONS_MODEL,
            status="skipped",
            normalized_status=STATUS_SKIPPED_DISABLED,
            started_at=started_at,
            finished_at=finished_at,
            raw_error_type="DisabledByConfig",
            sanitized_error_message=(
                "Pollinations provider skipped: POLLINATIONS_ENABLED is disabled."
            ),
            skip_reason="POLLINATIONS_ENABLED set to a falsey value (false/0/no/off).",
            notes=(
                "Pollinations fallback disabled by configuration. No image generated. "
                "No fake image created."
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
            reason="POLLINATIONS_ENABLED disabled. Pollinations fallback skipped.",
        )
        print(
            json.dumps(
                {
                    "ok": False,
                    "proof": "PS-005 blocked: Pollinations disabled by configuration.",
                    "normalized_status": STATUS_SKIPPED_DISABLED,
                    "local_ledger": str(LOCAL_LEDGER_PATH),
                    "local_failure_report": str(LOCAL_FAILURE_PATH),
                    "next_step": (
                        "Set POLLINATIONS_ENABLED=true (or unset it) to enable the "
                        "Pollinations fallback provider."
                    ),
                },
                indent=2,
            )
        )
        fail("PS-005 blocked: Pollinations disabled (SKIPPED_DISABLED).")

    # Attempt Pollinations image generation.
    attempt, image_bytes, image_mime_type = run_pollinations_attempt(
        prompt=prompt_text,
        attempt_index=0,
    )
    attempts = [attempt]

    success_attempt = attempt if attempt["normalized_status"] == STATUS_OK else None

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
            reason="Pollinations did not return a valid image.",
        )
        print(
            json.dumps(
                {
                    "ok": False,
                    "proof": "PS-005 failed: Pollinations did not produce a valid image.",
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
            "PS-005 failed: Pollinations did not return a valid image. "
            f"See {LOCAL_FAILURE_PATH}."
        )

    # Success: persist image and metadata locally.
    detected_image_mime_type = detect_image_mime_from_bytes(
        image_bytes, image_mime_type
    )
    if detected_image_mime_type != image_mime_type:
        print(
            "INFO image MIME corrected from provider/header value "
            f"{image_mime_type!r} to byte-detected value {detected_image_mime_type!r}."
        )
        image_mime_type = detected_image_mime_type

    ext = mime_to_ext(image_mime_type)
    image_path = LOCAL_IMAGE_STEM.with_suffix(ext)
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
            "model": POLLINATIONS_MODEL,
            "api_method": API_METHOD,
            "image_mime_type": image_mime_type,
            "image_sha256": image_sha,
        },
    )

    ledger_pre_upload = build_ledger(
        attempts,
        final_status="succeeded",
        selected_provider=PROVIDER_ID,
        selected_model=POLLINATIONS_MODEL,
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
        ledger=ledger_pre_upload,
    )

    # Re-write the ledger and note with B2/manifest references included.
    final_ledger = build_ledger(
        attempts,
        final_status="succeeded",
        selected_provider=PROVIDER_ID,
        selected_model=POLLINATIONS_MODEL,
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
            "PS-005 Pollinations no-key fallback provider + B2 + Genblaze "
            "manifest smoke test passed."
        ),
        "provider": PROVIDER_ID,
        "selected_model": POLLINATIONS_MODEL,
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
