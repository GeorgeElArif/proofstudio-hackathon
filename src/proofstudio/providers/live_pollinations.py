"""Live Pollinations no-key fallback image provider adapter (PS-007).

This module implements the PS-006 :class:`proofstudio.providers.types.Provider`
protocol against the real Pollinations public image endpoint. It reuses the
proven request/error-normalization and byte-based MIME detection behavior from
the historical PS-005 smoke script, packaged as a reusable provider adapter
that the PS-006 :class:`ProviderRouter` can drive as a fallback after the
Cloudflare primary.

Truth boundary for this adapter:

- It performs real network calls.
- It requires NO API key. No key is faked.
- It respects ``POLLINATIONS_ENABLED``. When disabled, it returns a full
  ``SKIPPED_DISABLED`` attempt and never contacts the endpoint.
- It detects MIME purely from magic bytes and rejects HTML, JSON errors,
  tiny payloads, and non-image bytes.
- It never fakes image output. ``OK`` is only returned when Pollinations
  actually returned valid image bytes.

Carrying image bytes through the PS-006 protocol:

Like the Cloudflare adapter, the selected image bytes and detected MIME are
exposed through safe instance attributes (``last_image_bytes`` /
``last_image_mime``) so the PS-007 smoke script can persist and upload them
without breaking the deterministic, bytes-free PS-006 router core.
"""

from __future__ import annotations

import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any

import requests

from proofstudio.providers.types import (
    ATTEMPT_STATUS_FAILED,
    ATTEMPT_STATUS_SKIPPED,
    ATTEMPT_STATUS_SUCCEEDED,
    NS_BAD_REQUEST,
    NS_MODEL_UNAVAILABLE,
    NS_OK,
    NS_PROVIDER_DOWN,
    NS_SAFETY_BLOCKED,
    NS_SKIPPED_DISABLED,
    NS_TIMEOUT,
    NS_UNKNOWN_ERROR,
    ProviderAttempt,
    ProviderJob,
    build_attempt,
)

PROVIDER_ID = "pollinations"
DISPLAY_NAME = "Pollinations (no-key fallback)"
JOB_TYPE = "image_generation"
API_METHOD = "pollinations-image-get"
DEFAULT_MODEL_LABEL = "pollinations-image-default"

POLLINATIONS_ENDPOINT = "https://image.pollinations.ai/prompt/{encoded_prompt}"

DEFAULT_TIMEOUT_SECONDS = 120

# Pollinations can return a tiny stub/error body; treat anything smaller than
# this as a non-image failure even if it is not obviously HTML/JSON.
MIN_IMAGE_BYTES = 1024

# Magic-byte signatures defined via bytes.fromhex(...) so there is no
# escaped-byte ambiguity. Provider content-type headers can lie; stored
# media_type and extension must match the actual bytes.
PNG_SIG = bytes.fromhex("89504e470d0a1a0a")
JPEG_SIG = bytes.fromhex("ffd8ff")
RIFF_SIG = bytes.fromhex("52494646")  # "RIFF"
WEBP_TAG = bytes.fromhex("57454250")  # "WEBP"
GIF87_SIG = bytes.fromhex("474946383761")  # "GIF87a"
GIF89_SIG = bytes.fromhex("474946383961")  # "GIF89a"

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


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def scrub_secrets(text: str) -> str:
    if not text:
        return ""
    scrubbed = text
    for pattern, replacement in SECRET_SCRUB_PATTERNS:
        scrubbed = pattern.sub(replacement, scrubbed)
    return scrubbed


def is_disabled_env(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"false", "0", "no", "off"}


def detect_image_mime_from_bytes(data: bytes, fallback: str | None = None) -> str:
    """Detect actual image MIME purely from magic bytes.

    Returns 'application/octet-stream' (or fallback) when bytes do not look
    like a supported image, so callers can reject HTML/JSON/error stubs.
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


def _looks_like_html(data: bytes) -> bool:
    head = data[:512].lstrip()
    if head[:5].lower() == b"<html" or head[:9].lower() == b"<!doctype":
        return True
    if head[:1] == b"<" and b"</" in data[:2048].lower():
        return True
    return False


def _looks_like_json(data: bytes) -> bool:
    head = data[:512].lstrip()
    return head[:1] in (b"{", b"[")


def _normalize_status(
    status_code: int | None,
    body_text: str,
    exception: BaseException | None,
) -> str:
    if exception is not None:
        if isinstance(exception, requests.exceptions.Timeout):
            return NS_TIMEOUT
        if isinstance(exception, requests.exceptions.ConnectionError):
            return NS_PROVIDER_DOWN
        return NS_UNKNOWN_ERROR

    lower = (body_text or "").lower()

    if status_code is None:
        if any(k in lower for k in SAFETY_KEYWORDS):
            return NS_SAFETY_BLOCKED
        if any(k in lower for k in QUOTA_KEYWORDS):
            return NS_MODEL_UNAVAILABLE
        if any(k in lower for k in MODEL_KEYWORDS):
            return NS_MODEL_UNAVAILABLE
        return NS_UNKNOWN_ERROR

    if status_code == 400:
        if any(k in lower for k in SAFETY_KEYWORDS):
            return NS_SAFETY_BLOCKED
        return NS_BAD_REQUEST
    if status_code == 404:
        return NS_MODEL_UNAVAILABLE
    if status_code == 408:
        return NS_TIMEOUT
    if status_code in (401, 403):
        # Unexpected for a no-key endpoint; treat as provider-side problem.
        if any(k in lower for k in SAFETY_KEYWORDS):
            return NS_SAFETY_BLOCKED
        return NS_PROVIDER_DOWN
    if status_code == 429:
        return NS_MODEL_UNAVAILABLE
    if 400 <= status_code < 500:
        if any(k in lower for k in SAFETY_KEYWORDS):
            return NS_SAFETY_BLOCKED
        if any(k in lower for k in MODEL_KEYWORDS):
            return NS_MODEL_UNAVAILABLE
        return NS_BAD_REQUEST
    if status_code >= 500:
        return NS_PROVIDER_DOWN

    if any(k in lower for k in SAFETY_KEYWORDS):
        return NS_SAFETY_BLOCKED
    if any(k in lower for k in MODEL_KEYWORDS):
        return NS_MODEL_UNAVAILABLE
    return NS_UNKNOWN_ERROR


def _pollinations_error_summary(status_code: int | None, body_text: str) -> str:
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


def _estimated_cost() -> dict[str, Any]:
    return {
        "amount": 0.0,
        "currency": "USD",
        "cost_basis": "no-key public endpoint",
        "free_tier_used": True,
        "paid_required": False,
        "provider_credit_note": (
            "Pollinations is a no-key public image endpoint. Estimated cost 0.0 USD."
        ),
    }


class LivePollinationsProvider:
    """Live Pollinations no-key fallback image provider adapter.

    Implements the PS-006 :class:`Provider` protocol. Requires no API key.
    Respects the ``POLLINATIONS_ENABLED`` disable flag. On success, image
    bytes and the byte-detected MIME type are exposed via ``last_image_bytes``
    and ``last_image_mime`` for the PS-007 smoke script.
    """

    provider_id: str = PROVIDER_ID
    display_name: str = DISPLAY_NAME
    job_type: str = JOB_TYPE
    api_method: str = API_METHOD

    def __init__(
        self,
        *,
        enabled: bool | None = None,
        width: str | int | None = None,
        height: str | int | None = None,
        model_name: str | None = None,
        model_label: str = DEFAULT_MODEL_LABEL,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        user_agent: str = "ProofStudio-PS-007/1.0",
    ) -> None:
        self._enabled = enabled
        self._width = str(width).strip() if width is not None else None
        self._height = str(height).strip() if height is not None else None
        self._model_name = (model_name or "").strip() or None
        self._model_label = model_label or DEFAULT_MODEL_LABEL
        self._timeout_seconds = int(timeout_seconds)
        self._user_agent = user_agent

        self.last_image_bytes: bytes | None = None
        self.last_image_mime: str | None = None

    @property
    def model(self) -> str:
        return self._model_label

    def _is_disabled(self) -> bool:
        if self._enabled is not None:
            return not self._enabled
        return False

    def _query_params(self) -> dict[str, str]:
        params: dict[str, str] = {
            "nologo": "true",
            "referrer": "proofstudio",
        }
        if self._width:
            params["width"] = self._width
        else:
            params["width"] = "1024"
        if self._height:
            params["height"] = self._height
        else:
            params["height"] = "576"
        if self._model_name:
            params["model"] = self._model_name
        else:
            params["model"] = "flux"
        return params

    def _build_skip_disabled_attempt(self) -> ProviderAttempt:
        started_at = _utc_now_iso()
        return build_attempt(
            attempt_index=0,
            provider=self.provider_id,
            model=self._model_label,
            api_method=self.api_method,
            job_type=self.job_type,
            status=ATTEMPT_STATUS_SKIPPED,
            normalized_status=NS_SKIPPED_DISABLED,
            started_at=started_at,
            finished_at=started_at,
            skip_reason=(
                "POLLINATIONS_ENABLED set to a falsey value (false/0/no/off)."
            ),
            raw_error_type="DisabledByConfig",
            sanitized_error_message=(
                "Pollinations provider skipped: POLLINATIONS_ENABLED is disabled."
            ),
            estimated_cost={
                "amount": 0.0,
                "currency": "USD",
                "cost_basis": "blocked before billing",
                "free_tier_used": False,
                "paid_required": False,
                "provider_credit_note": (
                    "Pollinations skipped by config; no cost incurred."
                ),
            },
            free_or_paid="free",
            notes=(
                "Pollinations fallback disabled by configuration. No image "
                "generated. No fake image created."
            ),
        )

    def attempt(self, job: ProviderJob) -> ProviderAttempt:
        # Reset image carry-over so a prior success cannot leak into this run.
        self.last_image_bytes = None
        self.last_image_mime = None

        if self._is_disabled():
            return self._build_skip_disabled_attempt()

        prompt = (job.prompt or "").strip()
        encoded_prompt = urllib.parse.quote(prompt, safe="")
        url = POLLINATIONS_ENDPOINT.format(encoded_prompt=encoded_prompt)
        params = self._query_params()
        started_at = _utc_now_iso()

        try:
            response = requests.get(
                url,
                params=params,
                headers={
                    "Accept": "image/png, image/jpeg, image/webp, image/*",
                    "User-Agent": self._user_agent,
                },
                timeout=self._timeout_seconds,
                allow_redirects=True,
            )
        except requests.exceptions.Timeout as exc:
            return self._failure_attempt(
                started_at=started_at,
                normalized_status=NS_TIMEOUT,
                raw_error_type=type(exc).__name__,
                sanitized_message=(
                    f"Pollinations request timed out after {self._timeout_seconds}s."
                ),
                notes="Pollinations request exceeded timeout.",
            )
        except requests.exceptions.ConnectionError as exc:
            return self._failure_attempt(
                started_at=started_at,
                normalized_status=NS_PROVIDER_DOWN,
                raw_error_type=type(exc).__name__,
                sanitized_message="Connection error contacting Pollinations.",
                notes="Network/connection failure reaching Pollinations endpoint.",
            )
        except requests.exceptions.RequestException as exc:
            return self._failure_attempt(
                started_at=started_at,
                normalized_status=NS_UNKNOWN_ERROR,
                raw_error_type=type(exc).__name__,
                sanitized_message=scrub_secrets(str(exc))[:500],
                notes="Unexpected requests exception while calling Pollinations.",
            )

        return self._handle_response(response, started_at)

    def _handle_response(
        self, response: requests.Response, started_at: str
    ) -> ProviderAttempt:
        finished_at = _utc_now_iso()
        status_code = response.status_code
        content = response.content or b""
        header_content_type = response.headers.get("content-type", "") or ""
        body_text = response.text or ""
        detected_mime = detect_image_mime_from_bytes(content)

        if (
            status_code == 200
            and detected_mime.startswith("image/")
            and len(content) >= MIN_IMAGE_BYTES
        ):
            return self._success_attempt(
                started_at=started_at,
                finished_at=finished_at,
                image_bytes=content,
                detected_mime=detected_mime,
                source_note=(
                    "Pollinations returned raw image bytes "
                    f"(byte-detected mime={detected_mime}, header content-type="
                    f"{header_content_type.split(';')[0].strip()})."
                ),
            )

        if _looks_like_html(content):
            normalized = _normalize_status(status_code, "html error page", None)
            if normalized == NS_UNKNOWN_ERROR:
                normalized = NS_PROVIDER_DOWN
            return self._failure_attempt(
                started_at=started_at,
                finished_at=finished_at,
                normalized_status=normalized,
                raw_error_type="HTMLResponse",
                sanitized_message=(
                    "Pollinations returned an HTML page instead of image bytes."
                ),
                notes="Pollinations returned HTML (likely an error/landing page).",
            )

        if _looks_like_json(content):
            normalized = _normalize_status(
                status_code,
                _pollinations_error_summary(status_code, body_text),
                None,
            )
            return self._failure_attempt(
                started_at=started_at,
                finished_at=finished_at,
                normalized_status=normalized,
                raw_error_type=f"JSONResponse(HTTP{status_code})",
                sanitized_message=_pollinations_error_summary(status_code, body_text),
                notes="Pollinations returned a JSON body instead of image bytes.",
            )

        if status_code == 200 and len(content) < MIN_IMAGE_BYTES:
            return self._failure_attempt(
                started_at=started_at,
                finished_at=finished_at,
                normalized_status=NS_PROVIDER_DOWN,
                raw_error_type="TinyResponse",
                sanitized_message=(
                    f"Pollinations returned only {len(content)} bytes (below "
                    f"{MIN_IMAGE_BYTES} byte minimum)."
                ),
                notes="Pollinations returned a tiny/invalid payload.",
            )

        if status_code == 200:
            normalized = _normalize_status(
                status_code,
                _pollinations_error_summary(status_code, body_text)
                or "non-image bytes",
                None,
            )
            return self._failure_attempt(
                started_at=started_at,
                finished_at=finished_at,
                normalized_status=normalized,
                raw_error_type="NonImageBytes",
                sanitized_message=_pollinations_error_summary(
                    status_code, body_text or "non-image bytes"
                ),
                notes="Pollinations returned HTTP 200 but non-image bytes.",
            )

        normalized = _normalize_status(
            status_code,
            _pollinations_error_summary(status_code, body_text),
            None,
        )
        return self._failure_attempt(
            started_at=started_at,
            finished_at=finished_at,
            normalized_status=normalized,
            raw_error_type=f"HTTP{status_code}",
            sanitized_message=_pollinations_error_summary(status_code, body_text),
            notes=f"Pollinations returned HTTP {status_code}.",
        )

    def _success_attempt(
        self,
        *,
        started_at: str,
        finished_at: str,
        image_bytes: bytes,
        detected_mime: str,
        source_note: str,
    ) -> ProviderAttempt:
        self.last_image_bytes = image_bytes
        self.last_image_mime = detected_mime

        return build_attempt(
            attempt_index=0,
            provider=self.provider_id,
            model=self._model_label,
            api_method=self.api_method,
            job_type=self.job_type,
            status=ATTEMPT_STATUS_SUCCEEDED,
            normalized_status=NS_OK,
            started_at=started_at,
            finished_at=finished_at,
            estimated_cost=_estimated_cost(),
            free_or_paid="free",
            output_asset_refs=[
                {
                    "kind": "generated_image",
                    "provider": self.provider_id,
                    "model": self._model_label,
                    "api_method": self.api_method,
                    "media_type": detected_mime,
                    "size_bytes": len(image_bytes),
                    "in_memory": True,
                    "produced_real_media": True,
                    "note": (
                        "Real image bytes are held on the provider instance "
                        "(last_image_bytes / last_image_mime) for the PS-007 "
                        "script to persist, hash, and upload."
                    ),
                }
            ],
            notes=source_note,
        )

    def _failure_attempt(
        self,
        *,
        started_at: str,
        normalized_status: str,
        raw_error_type: str,
        sanitized_message: str,
        notes: str,
        finished_at: str | None = None,
    ) -> ProviderAttempt:
        return build_attempt(
            attempt_index=0,
            provider=self.provider_id,
            model=self._model_label,
            api_method=self.api_method,
            job_type=self.job_type,
            status=ATTEMPT_STATUS_FAILED,
            normalized_status=normalized_status,
            started_at=started_at,
            finished_at=finished_at or _utc_now_iso(),
            raw_error_type=raw_error_type,
            sanitized_error_message=sanitized_message,
            estimated_cost=_estimated_cost(),
            free_or_paid="free",
            notes=notes,
        )


__all__ = [
    "LivePollinationsProvider",
    "PROVIDER_ID",
    "DEFAULT_MODEL_LABEL",
    "detect_image_mime_from_bytes",
    "is_disabled_env",
    "scrub_secrets",
]
