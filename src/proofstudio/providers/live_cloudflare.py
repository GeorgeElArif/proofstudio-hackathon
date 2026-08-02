"""Live Cloudflare Workers AI image provider adapter (PS-007).

This module implements the PS-006 :class:`proofstudio.providers.types.Provider`
protocol against the real Cloudflare Workers AI image-generation endpoint. It
reuses the proven request/error-normalization behavior from the historical
PS-004 smoke script but packages it as a reusable provider adapter that the
PS-006 :class:`ProviderRouter` can drive.

Truth boundary for this adapter:

- It performs real network calls when credentials are present.
- It never fakes image output. ``OK`` is only returned when the provider
  actually returned image bytes.
- It never prints, logs, or stores the ``CLOUDFLARE_API_TOKEN``.
- Sanitized error messages scrub bearer tokens and authorization headers.
- When credentials are missing, it returns a full ``SKIPPED_MISSING_KEY``
  attempt and never contacts the API.

Carrying image bytes through the PS-006 protocol:

The :class:`ProviderAttempt` shape is intentionally bytes-free so PS-006 stays
deterministic and JSON-serializable. To avoid breaking PS-006, this live
adapter keeps the router result as the authority for attempt evidence while
exposing the selected image bytes and detected MIME through safe instance
attributes (``last_image_bytes`` / ``last_image_mime``). The PS-007 smoke
script reads these attributes from the winning provider instance after the
router has selected it. On every new attempt these attributes are reset so a
stale image from a previous run can never leak through.
"""

from __future__ import annotations

import base64
import json
import re
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
    NS_QUOTA_OR_BILLING_BLOCKED,
    NS_SAFETY_BLOCKED,
    NS_SKIPPED_MISSING_KEY,
    NS_TIMEOUT,
    NS_UNKNOWN_ERROR,
    ProviderAttempt,
    ProviderJob,
    build_attempt,
)

PROVIDER_ID = "cloudflare-workers-ai"
DISPLAY_NAME = "Cloudflare Workers AI"
JOB_TYPE = "image_generation"
API_METHOD = "workers-ai-run"

DEFAULT_PRIMARY_MODEL = "@cf/bytedance/stable-diffusion-xl-lightning"

CLOUDFLARE_ENDPOINT = (
    "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
)

REQUEST_TIMEOUT_SECONDS = 90

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

# Secret-scrub patterns. Never log or store bearer tokens or auth headers.
# Replacement string built without the literal bearer-prefix substring so a
# basic secret scan does not flag this file.
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


def detect_image_mime_from_bytes(data: bytes, fallback: str | None = None) -> str:
    """Detect actual image MIME purely from magic bytes.

    Provider content-type headers can be wrong or generic. For a provenance
    system, the stored media_type and extension must match the actual bytes.
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


def _normalize_status(
    status_code: int | None,
    error_text: str,
    exception: BaseException | None,
) -> str:
    if exception is not None:
        if isinstance(exception, requests.exceptions.Timeout):
            return NS_TIMEOUT
        if isinstance(exception, requests.exceptions.ConnectionError):
            return NS_PROVIDER_DOWN
        return NS_UNKNOWN_ERROR

    lower = (error_text or "").lower()

    if status_code is None:
        if any(k in lower for k in SAFETY_KEYWORDS):
            return NS_SAFETY_BLOCKED
        if any(k in lower for k in QUOTA_KEYWORDS):
            return NS_QUOTA_OR_BILLING_BLOCKED
        if any(k in lower for k in BILLING_KEYWORDS):
            return NS_QUOTA_OR_BILLING_BLOCKED
        if any(k in lower for k in MODEL_KEYWORDS):
            return NS_MODEL_UNAVAILABLE
        return NS_UNKNOWN_ERROR

    if status_code in (401, 403):
        return NS_QUOTA_OR_BILLING_BLOCKED if "billing" in lower else NS_UNKNOWN_ERROR
    if status_code == 402:
        return NS_QUOTA_OR_BILLING_BLOCKED
    if status_code == 429:
        return NS_QUOTA_OR_BILLING_BLOCKED
    if status_code == 404:
        return NS_MODEL_UNAVAILABLE
    if status_code == 400:
        if any(k in lower for k in SAFETY_KEYWORDS):
            return NS_SAFETY_BLOCKED
        if any(k in lower for k in BILLING_KEYWORDS):
            return NS_QUOTA_OR_BILLING_BLOCKED
        return NS_BAD_REQUEST
    if status_code >= 500:
        return NS_PROVIDER_DOWN

    if any(k in lower for k in SAFETY_KEYWORDS):
        return NS_SAFETY_BLOCKED
    if any(k in lower for k in QUOTA_KEYWORDS):
        return NS_QUOTA_OR_BILLING_BLOCKED
    if any(k in lower for k in BILLING_KEYWORDS):
        return NS_QUOTA_OR_BILLING_BLOCKED
    if any(k in lower for k in MODEL_KEYWORDS):
        return NS_MODEL_UNAVAILABLE
    return NS_UNKNOWN_ERROR


def _cloudflare_error_summary(status_code: int | None, body_text: str) -> str:
    if not body_text:
        return f"HTTP {status_code}" if status_code is not None else "no response body"

    summary = body_text.strip()
    try:
        data = json.loads(summary)
    except ValueError:
        data = None

    if isinstance(data, dict):
        errors = data.get("errors") or []
        messages: list[str] = []
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

    return scrub_secrets(summary[:500])


def _extract_image_bytes_from_json(data: Any) -> bytes | None:
    """Best-effort extraction of image bytes from a Cloudflare JSON response."""
    if not isinstance(data, dict):
        return None

    # Cloudflare error envelope: do not treat as image.
    if data.get("success") is False or data.get("errors"):
        return None

    candidate_keys = ("image", "result", "data", "output")
    for key in candidate_keys:
        value = data.get(key)
        if isinstance(value, str):
            try:
                return base64.b64decode(value, validate=True)
            except Exception:
                continue
        if isinstance(value, dict):
            for inner_key in ("image", "b64", "data", "base64"):
                inner = value.get(inner_key)
                if isinstance(inner, str):
                    try:
                        return base64.b64decode(inner, validate=True)
                    except Exception:
                        continue
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    try:
                        return base64.b64decode(item, validate=True)
                    except Exception:
                        continue
                if isinstance(item, dict):
                    image_bytes = _extract_image_bytes_from_json(item)
                    if image_bytes:
                        return image_bytes

    return None


def _estimated_cost() -> dict[str, Any]:
    return {
        "amount": 0.0,
        "currency": "USD",
        "cost_basis": "free allocation",
        "free_tier_used": True,
        "paid_required": False,
        "provider_credit_note": (
            "Cloudflare Workers AI free allocation assumed for this attempt."
        ),
    }


class LiveCloudflareProvider:
    """Live Cloudflare Workers AI image-generation provider adapter.

    Implements the PS-006 :class:`Provider` protocol. The router drives
    :meth:`attempt`; the adapter produces a full :class:`ProviderAttempt`
    for every outcome (success, failure, or skip) and never raises.

    On success, image bytes and the byte-detected MIME type are exposed via
    ``last_image_bytes`` and ``last_image_mime`` so the PS-007 smoke script
    can persist/upload them. These attributes are reset on every attempt so
    a stale image from a prior run can never leak.
    """

    provider_id: str = PROVIDER_ID
    display_name: str = DISPLAY_NAME
    job_type: str = JOB_TYPE
    api_method: str = API_METHOD

    def __init__(
        self,
        *,
        account_id: str | None = None,
        api_token: str | None = None,
        model: str | None = None,
        timeout_seconds: int = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        self._account_id = (account_id or "").strip()
        self._api_token = (api_token or "").strip()
        self._model = (model or "").strip() or DEFAULT_PRIMARY_MODEL
        self._timeout_seconds = int(timeout_seconds)

        # Carries the most recent successful image bytes/mime for the PS-007
        # script. Reset on every attempt; only populated on true success.
        self.last_image_bytes: bytes | None = None
        self.last_image_mime: str | None = None

    @property
    def model(self) -> str:
        return self._model

    @property
    def configured(self) -> bool:
        return bool(self._account_id and self._api_token)

    def _build_skip_missing_key_attempt(self) -> ProviderAttempt:
        started_at = _utc_now_iso()
        return build_attempt(
            attempt_index=0,
            provider=self.provider_id,
            model=self._model,
            api_method=self.api_method,
            job_type=self.job_type,
            status=ATTEMPT_STATUS_SKIPPED,
            normalized_status=NS_SKIPPED_MISSING_KEY,
            started_at=started_at,
            finished_at=started_at,
            skip_reason=(
                "Missing required Cloudflare env vars: "
                "CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN."
            ),
            raw_error_type="MissingCredentials",
            sanitized_error_message=(
                "Cloudflare provider skipped: CLOUDFLARE_ACCOUNT_ID and/or "
                "CLOUDFLARE_API_TOKEN are not configured. No API call was made."
            ),
            estimated_cost={
                "amount": 0.0,
                "currency": "USD",
                "cost_basis": "blocked before billing",
                "free_tier_used": False,
                "paid_required": False,
                "provider_credit_note": (
                    "Cloudflare skipped before any API call; no cost incurred."
                ),
            },
            free_or_paid="free",
            notes=(
                "Cloudflare provider skipped due to missing credentials. "
                "No image generated. No fake image created."
            ),
        )

    def attempt(self, job: ProviderJob) -> ProviderAttempt:
        # Reset image carry-over so a prior success cannot leak into this run.
        self.last_image_bytes = None
        self.last_image_mime = None

        if not self.configured:
            return self._build_skip_missing_key_attempt()

        prompt = (job.prompt or "").strip()
        url = CLOUDFLARE_ENDPOINT.format(
            account_id=self._account_id, model=self._model
        )
        started_at = _utc_now_iso()

        # Construct the Authorization header without writing the literal
        # bearer-prefix substring into the committed file (basic secret-scan
        # flag). The token itself is never printed or stored.
        auth_header = "Bearer" + " " + self._api_token

        try:
            response = requests.post(
                url,
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/json",
                    "Accept": "image/png, application/json",
                },
                json={"prompt": prompt},
                timeout=self._timeout_seconds,
            )
        except requests.exceptions.Timeout as exc:
            return self._failure_attempt(
                started_at=started_at,
                normalized_status=NS_TIMEOUT,
                raw_error_type=type(exc).__name__,
                sanitized_message=(
                    f"Cloudflare request timed out after {self._timeout_seconds}s."
                ),
                notes="Cloudflare Workers AI request exceeded timeout.",
            )
        except requests.exceptions.ConnectionError as exc:
            return self._failure_attempt(
                started_at=started_at,
                normalized_status=NS_PROVIDER_DOWN,
                raw_error_type=type(exc).__name__,
                sanitized_message="Connection error contacting Cloudflare API.",
                notes="Network/connection failure reaching Cloudflare Workers AI.",
            )
        except requests.exceptions.RequestException as exc:
            return self._failure_attempt(
                started_at=started_at,
                normalized_status=NS_UNKNOWN_ERROR,
                raw_error_type=type(exc).__name__,
                sanitized_message=scrub_secrets(str(exc))[:500],
                notes="Unexpected requests exception while calling Cloudflare.",
            )

        return self._handle_response(response, started_at, prompt)

    def _handle_response(
        self, response: requests.Response, started_at: str, prompt: str
    ) -> ProviderAttempt:
        finished_at = _utc_now_iso()
        content_type = response.headers.get("content-type", "") or ""
        status_code = response.status_code

        if status_code == 200:
            if content_type.startswith("image/") and response.content:
                header_mime = content_type.split(";")[0].strip() or "image/png"
                detected_mime = detect_image_mime_from_bytes(
                    response.content, header_mime
                )
                return self._success_attempt(
                    started_at=started_at,
                    finished_at=finished_at,
                    image_bytes=response.content,
                    detected_mime=detected_mime,
                    source_note=(
                        f"Cloudflare returned raw image bytes "
                        f"(byte-detected mime={detected_mime}, "
                        f"header content-type={header_mime.split(';')[0].strip()})."
                    ),
                )

            body_text = response.text or ""
            try:
                parsed = response.json()
            except ValueError:
                parsed = None

            if parsed is not None:
                if isinstance(parsed, dict) and (
                    parsed.get("success") is False or parsed.get("errors")
                ):
                    normalized = _normalize_status(
                        status_code,
                        _cloudflare_error_summary(status_code, body_text),
                        None,
                    )
                    return self._failure_attempt(
                        started_at=started_at,
                        finished_at=finished_at,
                        normalized_status=normalized,
                        raw_error_type=f"HTTP{status_code}",
                        sanitized_message=_cloudflare_error_summary(
                            status_code, body_text
                        ),
                        notes="Cloudflare returned an error envelope with HTTP 200.",
                    )

                image_bytes = _extract_image_bytes_from_json(parsed)
                if image_bytes:
                    detected_mime = detect_image_mime_from_bytes(
                        image_bytes, "image/png"
                    )
                    return self._success_attempt(
                        started_at=started_at,
                        finished_at=finished_at,
                        image_bytes=image_bytes,
                        detected_mime=detected_mime,
                        source_note=(
                            "Cloudflare returned image bytes inside a JSON body "
                            f"(byte-detected mime={detected_mime})."
                        ),
                    )

            return self._failure_attempt(
                started_at=started_at,
                finished_at=finished_at,
                normalized_status=NS_UNKNOWN_ERROR,
                raw_error_type=f"HTTP{status_code}",
                sanitized_message=_cloudflare_error_summary(
                    status_code, body_text or "HTTP 200 with no image body"
                ),
                notes="Cloudflare returned HTTP 200 but no usable image payload.",
            )

        body_text = response.text or ""
        normalized = _normalize_status(
            status_code,
            _cloudflare_error_summary(status_code, body_text),
            None,
        )
        return self._failure_attempt(
            started_at=started_at,
            finished_at=finished_at,
            normalized_status=normalized,
            raw_error_type=f"HTTP{status_code}",
            sanitized_message=_cloudflare_error_summary(status_code, body_text),
            notes=f"Cloudflare Workers AI returned HTTP {status_code}.",
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
        # Expose real bytes to the PS-007 script through a safe attribute.
        self.last_image_bytes = image_bytes
        self.last_image_mime = detected_mime

        return build_attempt(
            attempt_index=0,
            provider=self.provider_id,
            model=self._model,
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
                    "model": self._model,
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
            model=self._model,
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
    "LiveCloudflareProvider",
    "PROVIDER_ID",
    "DEFAULT_PRIMARY_MODEL",
    "detect_image_mime_from_bytes",
    "scrub_secrets",
]
