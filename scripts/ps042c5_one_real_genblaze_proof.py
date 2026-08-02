#!/usr/bin/env python3
"""PS-042C5 one-real-GenBlaze-proof execution harness.

``--plan`` and ``--self-test`` are strictly offline. ``--execute`` is a
future, explicitly authorized one-submit path; it is never exercised by this
slice's validation.  The network boundaries are injected and counted below
the GenBlaze provider abstraction and immediately above botocore.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import secrets
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol
from urllib.parse import urlparse

import httpx
from botocore.config import Config
from botocore.exceptions import ClientError
from PIL import Image

from genblaze_core.models.asset import Asset
from genblaze_core.models.enums import Modality, RunStatus, StepStatus
from genblaze_core.models.manifest import Manifest, parse_manifest
from genblaze_core.models.run import Run
from genblaze_core.models.step import Step
from genblaze_core.pipeline.pipeline import Pipeline
from genblaze_core.providers.retry import RetryPolicy
from genblaze_gmicloud.image import GMICloudImageProvider


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_BRANCH = "ps-042c0/free-render-staging-v1"
TRUSTED_ANCESTOR_COMMIT = "34e23ba80b60f3bdcaa6b46c3728310faa11ddfa"
AUTHORIZATION_TOKEN = "AUTHORIZE_ONE_REAL_GENBLAZE_REQUEST"
PROVIDER_NAME = "gmicloud-image"
PROVIDER_CLASS = "genblaze_gmicloud.image.GMICloudImageProvider"
MODEL = "seedream-5.0-lite"
EXPECTED_PRICE_USD = Decimal("0.035")
MAX_COST_USD = Decimal("0.05")
OUTPUT_COUNT = 1
GENERATION_SUBMIT_LIMIT = 1
AUTOMATIC_RETRY_COUNT = 0
FALLBACK_PROVIDER_COUNT = 0
GENERATION_PREFLIGHT = False
OUTPUT_FORMAT = "png"
WIDTH = 4096
HEIGHT = 2304
SIZE = f"{WIDTH}x{HEIGHT}"
SEQUENTIAL_IMAGE_GENERATION = "disabled"
WATERMARK = False
PROVIDER_TIMEOUT_SECONDS = 120.0
ASSET_DOWNLOAD_ATTEMPTS = 1
MAX_IMAGE_BYTES = 50 * 1024 * 1024
MIN_IMAGE_BYTES = 1024
BASE_PREFIX = "proofstudio/submission/genblaze-live-proof-v1"
HISTORICAL_GOLDEN_PREFIX = "proofstudio/ps-021"
REQUIRED_CREDENTIALS = (
    "GMI_API_KEY",
    "B2_KEY_ID",
    "B2_APP_KEY",
    "B2_BUCKET",
    "B2_REGION",
)
CANONICAL_PROMPT = (
    "A premium launch visual for ProofStudio: a single AI media artifact moving "
    "through four clearly implied stages—generation, durable archive, rehydration, "
    "and verification. Cinematic dark background with restrained blue and teal "
    "light, professional enterprise design, landscape 16:9 composition, no logos, "
    "no text, no people."
)
PROMPT_SHA256 = "4cfc3b6319f2f24da6fe7d4fc3f85f9f52f292a34d9e21f2b61dab3689af7af8"
PUBLIC_RECEIPT_SCHEMA = "proofstudio.ps042c5.public-receipt.v1"
LOCAL_RECEIPT_SCHEMA = "proofstudio.ps042c5.local-execution-receipt.v1"
ACCEPTED = "ACCEPTED"
DEFINITIVE_PROVIDER_REJECTION = "DEFINITIVE_PROVIDER_REJECTION"
AMBIGUOUS_PROVIDER_RESPONSE = "AMBIGUOUS_PROVIDER_RESPONSE"
AMBIGUOUS_TRANSPORT_OUTCOME = "AMBIGUOUS_TRANSPORT_OUTCOME"
SAFE_REQUEST_ID_PATTERN = re.compile(r"[A-Za-z0-9._:-]{1,200}")
MAX_SAFE_ERROR_TEXT = 240


class SafetyError(RuntimeError):
    """A fail-closed, safe-to-display execution error."""


class AmbiguousGenerationError(SafetyError):
    """Submission may have happened, so no second POST is ever safe."""


class DefinitiveProviderRejectionError(SafetyError):
    """An HTTP 4xx proved rejection, while still forbidding an automatic retry."""


@dataclass(frozen=True)
class RepoState:
    branch: str
    head: str
    origin: str
    trusted_ancestor_merge_base: str
    clean: bool


@dataclass(frozen=True)
class KeyPlan:
    proof_id: str
    prefix: str
    brief: str
    image: str
    manifest: str
    archive: str
    receipt: str

    @property
    def ordered(self) -> tuple[str, ...]:
        return (self.brief, self.image, self.manifest, self.archive, self.receipt)

    @property
    def rehydrate(self) -> tuple[str, ...]:
        return (self.image, self.manifest, self.archive, self.receipt)


@dataclass
class NetworkCounters:
    generation_posts: int = 0
    status_poll_gets: int = 0
    asset_download_gets: int = 0
    b2_heads: int = 0
    b2_puts: int = 0
    b2_gets: int = 0
    other_network_methods: int = 0


@dataclass(frozen=True)
class ValidatedImage:
    data: bytes
    sha256: str
    size_bytes: int
    media_type: str
    width: int
    height: int


class ResponseLike(Protocol):
    status_code: int
    headers: Mapping[str, str]
    content: bytes
    text: str

    def json(self) -> Any: ...


class ProviderTransport(Protocol):
    def post(self, url: str, **kwargs: Any) -> ResponseLike: ...
    def get(self, url: str, **kwargs: Any) -> ResponseLike: ...
    def close(self) -> None: ...


class B2Transport(Protocol):
    def head_object(self, **kwargs: Any) -> Any: ...
    def put_object(self, **kwargs: Any) -> Any: ...
    def get_object(self, **kwargs: Any) -> Any: ...
    def close(self) -> None: ...


@dataclass
class ExecutionDependencies:
    repo_state: Callable[[], RepoState]
    provider_transport: Callable[[Mapping[str, str]], ProviderTransport]
    b2_transport: Callable[[Mapping[str, str]], B2Transport]
    proof_id: Callable[[], str] = lambda: secrets.token_hex(16)
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
    monotonic: Callable[[], float] = time.monotonic
    sleep: Callable[[float], None] = time.sleep
    local_receipt_root: Path = field(
        default_factory=lambda: Path(tempfile.gettempdir()) / "proofstudio-ps042c5-execution"
    )


def _git(*args: str) -> str:
    result = subprocess.run(
        ("git", *args),
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return result.stdout.strip()


def inspect_repo_state() -> RepoState:
    head = _git("rev-parse", "HEAD")
    try:
        trusted_ancestor_merge_base = _git(
            "merge-base",
            "HEAD",
            TRUSTED_ANCESTOR_COMMIT,
        )
    except subprocess.CalledProcessError:
        trusted_ancestor_merge_base = ""
    return RepoState(
        branch=_git("branch", "--show-current"),
        head=head,
        origin=_git("rev-parse", f"origin/{REQUIRED_BRANCH}"),
        trusted_ancestor_merge_base=trusted_ancestor_merge_base,
        clean=not bool(_git("status", "--porcelain")),
    )


def credential_presence(env: Mapping[str, str]) -> dict[str, bool]:
    """Return booleans only. Values never leave this function."""
    return {name: bool(env.get(name)) for name in REQUIRED_CREDENTIALS}


def make_key_plan(proof_id: str) -> KeyPlan:
    if not proof_id or any(c not in "0123456789abcdef" for c in proof_id):
        raise SafetyError("proof ID must be lowercase hexadecimal")
    prefix = f"{BASE_PREFIX}/{proof_id}"
    plan = KeyPlan(
        proof_id=proof_id,
        prefix=prefix,
        brief=f"{prefix}/source/brief.json",
        image=f"{prefix}/media/proofstudio-launch-image.png",
        manifest=f"{prefix}/manifest/genblaze-manifest.json",
        archive=f"{prefix}/archive/run-bundle.json",
        receipt=f"{prefix}/receipt/verification-receipt.json",
    )
    for key in plan.ordered:
        if not key.startswith(f"{BASE_PREFIX}/") or ".." in key.split("/"):
            raise SafetyError("object key escaped the authorized base prefix")
        if key.startswith(HISTORICAL_GOLDEN_PREFIX):
            raise SafetyError("historical golden prefix is forbidden")
    if len(set(plan.ordered)) != 5:
        raise SafetyError("object keys are not unique")
    return plan


def object_key_plan_template() -> list[str]:
    return [
        f"{BASE_PREFIX}/<proof_id>/source/brief.json",
        f"{BASE_PREFIX}/<proof_id>/media/proofstudio-launch-image.png",
        f"{BASE_PREFIX}/<proof_id>/manifest/genblaze-manifest.json",
        f"{BASE_PREFIX}/<proof_id>/archive/run-bundle.json",
        f"{BASE_PREFIX}/<proof_id>/receipt/verification-receipt.json",
    ]


def fixed_plan(env: Mapping[str, str]) -> dict[str, Any]:
    return {
        "mode": "offline-plan",
        "provider": PROVIDER_NAME,
        "provider_class": PROVIDER_CLASS,
        "model": MODEL,
        "expected_price_usd_per_output": str(EXPECTED_PRICE_USD),
        "authorized_cost_ceiling_usd": str(MAX_COST_USD),
        "generation_submit_limit": GENERATION_SUBMIT_LIMIT,
        "requested_output_count": OUTPUT_COUNT,
        "automatic_retry_count": AUTOMATIC_RETRY_COUNT,
        "fallback_provider_count": FALLBACK_PROVIDER_COUNT,
        "generation_preflight": GENERATION_PREFLIGHT,
        "prompt_sha256": PROMPT_SHA256,
        "output_format": OUTPUT_FORMAT,
        "dimensions": SIZE,
        "sequential_image_generation": SEQUENTIAL_IMAGE_GENERATION,
        "watermark": WATERMARK,
        "provider_timeout_seconds": int(PROVIDER_TIMEOUT_SECONDS),
        "asset_download_attempts": ASSET_DOWNLOAD_ATTEMPTS,
        "credential_presence": credential_presence(env),
        "object_keys": object_key_plan_template(),
        "network": {
            "provider_calls": 0,
            "b2_reads": 0,
            "b2_writes": 0,
        },
    }


class NoNetworkClient:
    """Injected self-test client; every possible network action raises."""

    def __getattr__(self, name: str) -> Any:
        raise AssertionError(f"offline self-test attempted network method: {name}")


def build_generation_step() -> Step:
    return Step(
        provider=PROVIDER_NAME,
        model=MODEL,
        modality=Modality.IMAGE,
        prompt=CANONICAL_PROMPT,
        params={
            "size": SIZE,
            "output_format": OUTPUT_FORMAT,
            "max_images": OUTPUT_COUNT,
            "sequential_image_generation": SEQUENTIAL_IMAGE_GENERATION,
            "watermark": WATERMARK,
        },
    )


def offline_self_test(env: Mapping[str, str]) -> dict[str, Any]:
    if hashlib.sha256(CANONICAL_PROMPT.encode("utf-8")).hexdigest() != PROMPT_SHA256:
        raise SafetyError("canonical prompt hash mismatch")
    if EXPECTED_PRICE_USD != Decimal("0.035") or MAX_COST_USD != Decimal("0.05"):
        raise SafetyError("fixed cost contract mismatch")
    if (OUTPUT_COUNT, GENERATION_SUBMIT_LIMIT, AUTOMATIC_RETRY_COUNT, FALLBACK_PROVIDER_COUNT) != (
        1,
        1,
        0,
        0,
    ):
        raise SafetyError("fixed request-boundary contract mismatch")
    policy = RetryPolicy.disabled()
    if policy.max_attempts != 1 or policy.retryable_codes:
        raise SafetyError("RetryPolicy.disabled() is not disabled")
    provider = GMICloudImageProvider(http_client=NoNetworkClient(), retry_policy=policy)
    payload = provider.prepare_payload(build_generation_step())
    expected_payload = {
        "prompt": CANONICAL_PROMPT,
        "size": SIZE,
        "output_format": OUTPUT_FORMAT,
        "max_images": 1,
        "sequential_image_generation": "disabled",
        "watermark": False,
    }
    if payload != expected_payload or "number_of_images" in payload:
        raise SafetyError("installed connector payload contract mismatch")
    pipeline = Pipeline("ps042c5-contract-check", chain=False, preflight=False).step(
        provider,
        model=MODEL,
        prompt=CANONICAL_PROMPT,
        fallback_models=[],
        params=build_generation_step().params,
    )
    if pipeline._preflight or len(pipeline._steps) != 1 or pipeline._steps[0].fallback_models:
        raise SafetyError("pipeline preflight/step/fallback contract mismatch")
    result = fixed_plan(env)
    result.update(
        {
            "mode": "offline-self-test",
            "status": "PASS",
            "connector_payload_verified": True,
            "retry_policy_disabled": True,
            "pipeline_preflight_disabled": True,
            "network_client_constructed": False,
        }
    )
    return result


def validate_execute_gates(
    authorization_token: str | None,
    max_cost: str | None,
    expected_revision: str | None,
    env: Mapping[str, str],
    state: RepoState,
) -> dict[str, str]:
    """All gates run before any network-capable client factory is called."""
    if state.branch != REQUIRED_BRANCH:
        raise SafetyError("wrong branch")
    if not state.clean:
        raise SafetyError("worktree is not clean")
    if expected_revision is None:
        raise SafetyError("explicit expected revision is required")
    if re.fullmatch(r"[0-9a-f]{40}", expected_revision) is None:
        raise SafetyError("expected revision must be exactly 40 lowercase hexadecimal characters")
    if state.head != expected_revision:
        raise SafetyError("HEAD does not equal expected revision")
    if state.origin != expected_revision:
        raise SafetyError("origin does not equal expected revision")
    if state.head != state.origin:
        raise SafetyError("HEAD does not equal origin")
    if state.trusted_ancestor_merge_base != TRUSTED_ANCESTOR_COMMIT:
        raise SafetyError("trusted ancestor is not an ancestor of HEAD")
    if authorization_token != AUTHORIZATION_TOKEN:
        raise SafetyError("authorization token rejected")
    try:
        supplied_max = Decimal(max_cost or "")
    except Exception as exc:
        raise SafetyError("explicit maximum cost is required") from exc
    if supplied_max != MAX_COST_USD:
        raise SafetyError("maximum cost must equal 0.05 USD")
    if EXPECTED_PRICE_USD * OUTPUT_COUNT > supplied_max:
        raise SafetyError("expected charge exceeds authorized ceiling")
    present = credential_presence(env)
    missing = [name for name, is_present in present.items() if not is_present]
    if missing:
        raise SafetyError("missing required credential variable(s): " + ", ".join(missing))
    if MODEL != "seedream-5.0-lite":
        raise SafetyError("model contract mismatch")
    if OUTPUT_COUNT != 1 or GENERATION_SUBMIT_LIMIT != 1:
        raise SafetyError("one-output/one-submit contract mismatch")
    if AUTOMATIC_RETRY_COUNT != 0 or FALLBACK_PROVIDER_COUNT != 0:
        raise SafetyError("retry/fallback contract mismatch")
    return {name: env[name] for name in REQUIRED_CREDENTIALS}


def _scrub_safe_text(
    value: Any,
    limit: int = MAX_SAFE_ERROR_TEXT,
    sensitive_values: tuple[str, ...] = (),
) -> str | None:
    """Return bounded diagnostic text with credentials, URLs, and paths removed."""
    if not isinstance(value, (str, int, float, bool)):
        return None
    text = str(value)
    for secret in sensitive_values:
        if secret:
            text = text.replace(secret, "[REDACTED_CREDENTIAL]")
    text = re.sub(r"(?i)\b(?:authorization|api[-_ ]?key|cookie)\b\s*[:=]\s*\S+",
                  "[REDACTED_CREDENTIAL]", text)
    text = re.sub(r"(?i)\bbearer\s+\S+", "Bearer [REDACTED]", text)
    text = re.sub(r"https?://[^\s\"'<>]+", "[REDACTED_URL]", text)
    text = re.sub(r"(?i)\b(?:x-amz-[a-z0-9_-]+|signature|credential)=[^\s&]+",
                  "[REDACTED_SIGNED_VALUE]", text)
    text = re.sub(r"(?:/home|/tmp|/mnt|/Users)/[^\s\"'<>]+", "[REDACTED_PATH]", text)
    text = re.sub(r"[A-Za-z]:\\[^\s\"'<>]+", "[REDACTED_PATH]", text)
    text = " ".join(text.split())
    if not text:
        return None
    if len(text) > limit:
        return text[: max(0, limit - 3)] + "..."
    return text


def _safe_json_key(value: Any) -> str:
    scrubbed = _scrub_safe_text(str(value), 80)
    return scrubbed or "[EMPTY_KEY]"


def _safe_error_fields(
    data: Mapping[str, Any] | None,
    sensitive_values: tuple[str, ...] = (),
) -> tuple[str | None, str | None]:
    if data is None:
        return None, None
    nested = data.get("error")
    nested_error = nested if isinstance(nested, Mapping) else {}
    code = (
        data.get("error_code")
        or data.get("code")
        or nested_error.get("code")
        or nested_error.get("error_code")
    )
    message = (
        data.get("message")
        or data.get("detail")
        or nested_error.get("message")
        or nested_error.get("detail")
        or (nested if isinstance(nested, str) else None)
    )
    safe_code = _scrub_safe_text(code, 64, sensitive_values)
    if safe_code is not None and re.fullmatch(r"[A-Za-z0-9._:-]{1,64}", safe_code) is None:
        safe_code = "[REDACTED_CODE]"
    return safe_code, _scrub_safe_text(message, MAX_SAFE_ERROR_TEXT, sensitive_values)


def classify_submit_response(
    response: ResponseLike,
    sensitive_values: Mapping[str, str] | tuple[str, ...] = (),
) -> tuple[dict[str, Any], Mapping[str, Any] | None, str | None]:
    """Classify one submit response without retaining or printing its raw body."""
    secrets_to_scrub = tuple(
        sensitive_values.values()
        if isinstance(sensitive_values, Mapping)
        else sensitive_values
    )
    status = int(response.status_code)
    body = bytes(response.content)
    content_type = _scrub_safe_text(
        response.headers.get("content-type", ""), 120, secrets_to_scrub
    )
    data: Mapping[str, Any] | None = None
    try:
        decoded = response.json()
        if isinstance(decoded, Mapping):
            data = decoded
    except Exception:
        decoded = None

    request_id: str | None = None
    if data is not None:
        candidate = data.get("request_id") or data.get("id")
        if isinstance(candidate, str) and SAFE_REQUEST_ID_PATTERN.fullmatch(candidate):
            request_id = candidate

    if 200 <= status < 300 and request_id is not None:
        classification = ACCEPTED
    elif 400 <= status < 500:
        classification = DEFINITIVE_PROVIDER_REJECTION
        request_id = None
    else:
        classification = AMBIGUOUS_PROVIDER_RESPONSE
        request_id = None

    safe_code, safe_message = _safe_error_fields(data, secrets_to_scrub)
    diagnostic = {
        "http_status": status,
        "response_content_type": content_type,
        "response_byte_length": len(body),
        "response_body_sha256": hashlib.sha256(body).hexdigest(),
        "top_level_json_keys": (
            sorted({_safe_json_key(key) for key in data}) if data is not None else None
        ),
        "safe_provider_error_code": safe_code,
        "safe_provider_error_message": safe_message,
        "submit_classification": classification,
    }
    return diagnostic, data, request_id


class CountingProviderHTTP:
    """Fail-closed HTTP boundary injected into the installed connector."""

    def __init__(
        self,
        transport: ProviderTransport,
        counters: NetworkCounters,
        sensitive_values: Mapping[str, str] | None = None,
    ):
        self._transport = transport
        self.counters = counters
        self.request_id: str | None = None
        self.asset_url: str | None = None
        self._sensitive_values = sensitive_values or {}
        self.submit_classification: str | None = None
        self.submit_diagnostic: dict[str, Any] | None = None

    def _record_transport_ambiguity(self) -> None:
        self.submit_classification = AMBIGUOUS_TRANSPORT_OUTCOME
        self.submit_diagnostic = {
            "http_status": None,
            "response_content_type": None,
            "response_byte_length": None,
            "response_body_sha256": None,
            "top_level_json_keys": None,
            "safe_provider_error_code": None,
            "safe_provider_error_message": None,
            "submit_classification": AMBIGUOUS_TRANSPORT_OUTCOME,
        }

    def post(self, url: str, **kwargs: Any) -> ResponseLike:
        if url != "/requests":
            self.counters.other_network_methods += 1
            raise SafetyError("unexpected provider POST endpoint")
        body = kwargs.get("json")
        expected_payload = {
            "prompt": CANONICAL_PROMPT,
            "size": SIZE,
            "output_format": OUTPUT_FORMAT,
            "max_images": 1,
            "sequential_image_generation": "disabled",
            "watermark": False,
        }
        if body != {"model": MODEL, "payload": expected_payload}:
            self.counters.other_network_methods += 1
            raise SafetyError("unexpected provider POST payload")
        if self.counters.generation_posts >= GENERATION_SUBMIT_LIMIT:
            raise SafetyError("second generation POST blocked before sending")
        self.counters.generation_posts += 1
        try:
            response = self._transport.post(url, **kwargs)
        except Exception as exc:
            self._record_transport_ambiguity()
            raise AmbiguousGenerationError(
                "generation submit outcome was ambiguous; no retry allowed"
            ) from exc
        diagnostic, data, request_id = classify_submit_response(
            response, self._sensitive_values
        )
        self.submit_diagnostic = diagnostic
        self.submit_classification = diagnostic["submit_classification"]
        if self.submit_classification == DEFINITIVE_PROVIDER_REJECTION:
            raise DefinitiveProviderRejectionError(
                "generation submit received a definitive provider rejection; no retry allowed"
            )
        if self.submit_classification != ACCEPTED:
            raise AmbiguousGenerationError("submit response had no request ID; no retry allowed")
        if not isinstance(data, Mapping):
            raise AmbiguousGenerationError("submit response structure was ambiguous; no retry allowed")
        self.request_id = request_id
        return response

    def get(self, url: str, **kwargs: Any) -> ResponseLike:
        if url == "/requests":
            self.counters.other_network_methods += 1
            raise SafetyError("provider authentication preflight blocked")
        expected = f"/requests/{self.request_id}" if self.request_id else None
        if expected is not None and url == expected:
            self.counters.status_poll_gets += 1
            try:
                response = self._transport.get(url, **kwargs)
                if response.status_code >= 400:
                    raise SafetyError("provider status request failed")
                detail = response.json()
                status = detail.get("status") if isinstance(detail, Mapping) else None
                if status in {"failed", "cancelled"}:
                    raise SafetyError("provider reached a terminal non-success status")
                if status == "success":
                    outcome = detail.get("outcome") or {}
                    media_urls = outcome.get("media_urls") or []
                    candidates = [
                        item.get("url") if isinstance(item, Mapping) else item
                        for item in media_urls
                    ]
                    if any(
                        not isinstance(candidate, str)
                        or urlparse(candidate).scheme.lower() != "https"
                        for candidate in candidates
                    ):
                        raise SafetyError("provider returned an unsafe media URL")
                return response
            except SafetyError:
                raise
            except Exception as exc:
                raise SafetyError("provider status request failed") from exc
        if self.asset_url is not None and url == self.asset_url:
            if self.counters.asset_download_gets >= ASSET_DOWNLOAD_ATTEMPTS:
                raise SafetyError("second generated-asset GET blocked before sending")
            if urlparse(url).scheme.lower() != "https":
                raise SafetyError("generated-asset URL must use HTTPS")
            self.counters.asset_download_gets += 1
            try:
                response = self._transport.get(
                    url,
                    timeout=PROVIDER_TIMEOUT_SECONDS,
                    follow_redirects=False,
                )
            except Exception as exc:
                raise SafetyError("generated-asset GET failed without retry") from exc
            if 300 <= response.status_code < 400:
                location = response.headers.get("location", "")
                if urlparse(location).scheme.lower() != "https":
                    raise SafetyError("asset redirect to non-HTTPS URL blocked")
                raise SafetyError("asset redirects are disabled")
            return response
        self.counters.other_network_methods += 1
        raise SafetyError("unexpected provider GET endpoint")

    def delete(self, *_args: Any, **_kwargs: Any) -> Any:
        self.counters.other_network_methods += 1
        raise SafetyError("provider DELETE is forbidden")

    def request(self, *_args: Any, **_kwargs: Any) -> Any:
        self.counters.other_network_methods += 1
        raise SafetyError("unexpected provider network method")

    def close(self) -> None:
        self._transport.close()


class CountingB2Client:
    """Exact-key-only, no-retry B2 boundary."""

    def __init__(
        self,
        transport: B2Transport,
        bucket: str,
        plan: KeyPlan,
        counters: NetworkCounters,
    ):
        self._transport = transport
        self.bucket = bucket
        self.plan = plan
        self.allowed = frozenset(plan.ordered)
        self.counters = counters
        self.image_validated = False
        self.put_attempts: set[str] = set()
        self.successful_writes: list[str] = []

    def _key(self, kwargs: Mapping[str, Any]) -> str:
        if kwargs.get("Bucket") != self.bucket:
            raise SafetyError("unexpected B2 bucket")
        key = kwargs.get("Key")
        if not isinstance(key, str) or key not in self.allowed:
            raise SafetyError("B2 key outside exact plan")
        return key

    def exists(self, key: str) -> bool:
        self._key({"Bucket": self.bucket, "Key": key})
        self.counters.b2_heads += 1
        try:
            self._transport.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if code in {"404", "NoSuchKey", "NotFound"} or status == 404:
                return False
            raise SafetyError("B2 exact-key HEAD failed") from exc

    def assert_all_absent(self) -> None:
        for key in self.plan.ordered:
            if self.exists(key):
                raise SafetyError(f"planned B2 key already exists: {key}")

    def put_once(self, key: str, data: bytes, content_type: str) -> None:
        if not self.image_validated:
            raise SafetyError("B2 PUT blocked before strict image validation")
        if key in self.put_attempts:
            raise SafetyError("B2 PUT retry blocked before sending")
        if self.exists(key):
            raise SafetyError(f"B2 key appeared before PUT: {key}")
        self.put_attempts.add(key)
        self.counters.b2_puts += 1
        try:
            self._transport.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
        except Exception as exc:
            raise SafetyError("B2 PUT failed without retry") from exc
        self.successful_writes.append(key)

    def get_exact(self, key: str) -> bytes:
        self._key({"Bucket": self.bucket, "Key": key})
        self.counters.b2_gets += 1
        try:
            response = self._transport.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except Exception as exc:
            raise SafetyError("B2 exact-key GET failed") from exc

    def close(self) -> None:
        self._transport.close()

    def __getattr__(self, name: str) -> Any:
        if name.startswith(("list", "delete")):
            self.counters.other_network_methods += 1
            raise SafetyError("B2 list/delete operation is forbidden")
        raise AttributeError(name)


def validate_png(response: ResponseLike) -> ValidatedImage:
    if response.status_code != 200:
        raise SafetyError("generated-asset GET did not return HTTP 200")
    data = response.content
    if len(data) < MIN_IMAGE_BYTES:
        raise SafetyError("generated asset is too small")
    if len(data) > MAX_IMAGE_BYTES:
        raise SafetyError("generated asset exceeds 50 MiB")
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SafetyError("generated asset failed PNG magic-byte validation")
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            detected_format = image.format
            width, height = image.size
    except Exception as exc:
        raise SafetyError("generated asset failed local image decoding") from exc
    if detected_format != "PNG":
        raise SafetyError("detected media type is not image/png")
    if (width, height) != (WIDTH, HEIGHT):
        raise SafetyError("generated image dimensions do not match 4096x2304")
    return ValidatedImage(
        data=data,
        sha256=hashlib.sha256(data).hexdigest(),
        size_bytes=len(data),
        media_type="image/png",
        width=width,
        height=height,
    )


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _b2_uri(bucket: str, key: str) -> str:
    return f"b2://{bucket}/{key}"


def _safe_time(value: datetime | None) -> str | None:
    return value.astimezone(timezone.utc).isoformat() if value else None


def build_public_receipt(
    *,
    proof_id: str,
    run: Run,
    step: Step,
    image: ValidatedImage,
    manifest: Manifest,
    manifest_file_sha256: str,
    bucket: str,
    plan: KeyPlan,
    rehydrated_image_sha256: str,
    complete: bool,
) -> dict[str, Any]:
    return {
        "schema": PUBLIC_RECEIPT_SCHEMA,
        "proof_id": proof_id,
        "run_id": run.run_id,
        "campaign_id": f"ps042c5-{proof_id}",
        "provider": PROVIDER_NAME,
        "model": MODEL,
        "configured_prompt_sha256": PROMPT_SHA256,
        "attempt_started_at": _safe_time(step.started_at),
        "attempt_finished_at": _safe_time(step.completed_at),
        "status": "succeeded" if complete else "incomplete",
        "provider_request_id": step.provider_payload["gmicloud"]["request_id"],
        "image_media_type": image.media_type,
        "image_size_bytes": image.size_bytes,
        "image_sha256": image.sha256,
        "manifest_canonical_hash": manifest.canonical_hash,
        "manifest_file_sha256": manifest_file_sha256,
        "manifest_verification": manifest.verify(),
        "b2_uris": {name: _b2_uri(bucket, key) for name, key in (
            ("brief", plan.brief),
            ("image", plan.image),
            ("manifest", plan.manifest),
            ("archive", plan.archive),
            ("receipt", plan.receipt),
        )},
        "rehydrated_image_sha256": rehydrated_image_sha256,
        "provider_calls_during_rehydrate": 0,
        "cost_basis_usd_per_output": str(EXPECTED_PRICE_USD),
        "authorized_ceiling_usd": str(MAX_COST_USD),
        "output_count": OUTPUT_COUNT,
        "request_submit_count": GENERATION_SUBMIT_LIMIT,
        "truth_boundary": (
            "This receipt proves the recorded pipeline operations and byte/hash "
            "comparisons only; it does not prove semantic truth, legal authenticity, "
            "human authorship, C2PA, public deployment, or tamper-proof storage."
        ),
        "completeness_status": "complete" if complete else "incomplete",
    }


def assert_redacted(value: Any, credential_values: Mapping[str, str]) -> None:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    forbidden = ("Authorization", "X-Amz-", "file://", str(REPO_ROOT))
    if any(token in text for token in forbidden):
        raise SafetyError("receipt/archive redaction rule failed")
    for name in ("GMI_API_KEY", "B2_KEY_ID", "B2_APP_KEY"):
        secret_value = credential_values.get(name, "")
        if secret_value and secret_value in text:
            raise SafetyError("credential value reached receipt/archive")
    for uri in _walk_strings(value):
        parsed = urlparse(uri)
        if parsed.query and ("signature" in parsed.query.lower() or "credential" in parsed.query.lower()):
            raise SafetyError("signed URL reached receipt/archive")


def _walk_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for child in value.values():
            yield from _walk_strings(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _walk_strings(child)


def write_local_failure_receipt(
    root: Path,
    plan: KeyPlan,
    b2: CountingB2Client | None,
    counters: NetworkCounters,
    failed_key: str | None,
    reason_code: str,
    *,
    outer_exception_type: str | None = None,
    provider_submit_classification: str | None = None,
    provider_response_diagnostic: Mapping[str, Any] | None = None,
) -> Path:
    directory = root / plan.proof_id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "failure-receipt.json"
    successful_writes = list(b2.successful_writes) if b2 else []
    original_counters = dict(counters.__dict__)
    second_post_forbidden = counters.generation_posts >= 1
    resume_possible = second_post_forbidden and provider_submit_classification != (
        DEFINITIVE_PROVIDER_REJECTION
    )
    payload = {
        "schema": LOCAL_RECEIPT_SCHEMA,
        "proof_id": plan.proof_id,
        "status": "incomplete",
        "reason_code": reason_code,
        "outer_exception_type": outer_exception_type or reason_code,
        "provider_submit_classification": provider_submit_classification,
        "provider_response_diagnostic": (
            dict(provider_response_diagnostic) if provider_response_diagnostic else None
        ),
        "successfully_written_keys": successful_writes,
        "b2_keys_successfully_written": successful_writes,
        "failed_key": failed_key,
        "failed_b2_key": failed_key,
        "network_counters": original_counters,
        "original_network_counters": original_counters,
        "second_post_forbidden": second_post_forbidden,
        "resume_by_known_request_id_may_be_possible": resume_possible,
        "complete_proof": False,
    }
    assert_redacted(payload, {})
    path.write_bytes(_canonical_json_bytes(payload) + b"\n")
    return path


def _default_provider_transport(credentials: Mapping[str, str]) -> ProviderTransport:
    return httpx.Client(
        base_url="https://console.gmicloud.ai/api/v1/ie/requestqueue/apikey",
        headers={"Authorization": f"Bearer {credentials['GMI_API_KEY']}"},
        timeout=PROVIDER_TIMEOUT_SECONDS,
        follow_redirects=False,
    )


def _default_b2_transport(credentials: Mapping[str, str]) -> B2Transport:
    import boto3

    return boto3.client(
        "s3",
        endpoint_url=f"https://s3.{credentials['B2_REGION']}.backblazeb2.com",
        region_name=credentials["B2_REGION"],
        aws_access_key_id=credentials["B2_KEY_ID"],
        aws_secret_access_key=credentials["B2_APP_KEY"],
        config=Config(
            retries={"max_attempts": 0, "mode": "standard"},
            connect_timeout=PROVIDER_TIMEOUT_SECONDS,
            read_timeout=PROVIDER_TIMEOUT_SECONDS,
        ),
    )


def default_dependencies() -> ExecutionDependencies:
    return ExecutionDependencies(
        repo_state=inspect_repo_state,
        provider_transport=_default_provider_transport,
        b2_transport=_default_b2_transport,
    )


def execute_proof(
    *,
    authorization_token: str | None,
    max_cost: str | None,
    expected_revision: str | None,
    env: Mapping[str, str],
    dependencies: ExecutionDependencies,
) -> dict[str, Any]:
    credentials = validate_execute_gates(
        authorization_token,
        max_cost,
        expected_revision,
        env,
        dependencies.repo_state(),
    )
    proof_id = dependencies.proof_id()
    plan = make_key_plan(proof_id)
    counters = NetworkCounters()
    provider_http: CountingProviderHTTP | None = None
    b2: CountingB2Client | None = None
    failed_key: str | None = None
    try:
        # Construction occurs only after every gate above.
        b2 = CountingB2Client(
            dependencies.b2_transport(credentials),
            credentials["B2_BUCKET"],
            plan,
            counters,
        )
        b2.assert_all_absent()

        provider_http = CountingProviderHTTP(
            dependencies.provider_transport(credentials),
            counters,
            credentials,
        )
        provider = GMICloudImageProvider(
            http_client=provider_http,
            poll_interval=5.0,
            retry_policy=RetryPolicy.disabled(),
        )
        pipeline = Pipeline(
            "ps042c5-one-real-genblaze-proof",
            chain=False,
            preflight=False,
        ).step(
            provider,
            model=MODEL,
            prompt=CANONICAL_PROMPT,
            fallback_models=[],
            params=build_generation_step().params,
        )
        old_skip = os.environ.get("GENBLAZE_SKIP_PREFLIGHT")
        os.environ["GENBLAZE_SKIP_PREFLIGHT"] = "1"
        try:
            result = pipeline.run(
                sink=None,
                fail_fast=True,
                raise_on_failure=True,
                timeout=PROVIDER_TIMEOUT_SECONDS,
                max_retries=AUTOMATIC_RETRY_COUNT,
                progress=False,
                pipeline_timeout=PROVIDER_TIMEOUT_SECONDS,
            )
        finally:
            if old_skip is None:
                os.environ.pop("GENBLAZE_SKIP_PREFLIGHT", None)
            else:
                os.environ["GENBLAZE_SKIP_PREFLIGHT"] = old_skip

        if counters.generation_posts != 1:
            raise AmbiguousGenerationError("exactly one generation submit was not observed")
        if len(result.run.steps) != 1:
            raise AmbiguousGenerationError("result did not contain exactly one step")
        step = result.run.steps[0]
        request_id = step.provider_payload.get("gmicloud", {}).get("request_id")
        status = step.provider_payload.get("gmicloud", {}).get("status")
        if (
            step.status != StepStatus.SUCCEEDED
            or status != "success"
            or not isinstance(request_id, str)
            or request_id != provider_http.request_id
        ):
            raise AmbiguousGenerationError("provider result was not one terminal success")
        if len(step.assets) != 1:
            raise AmbiguousGenerationError("provider result must contain exactly one output URL")
        output_url = step.assets[0].url
        if not isinstance(output_url, str) or urlparse(output_url).scheme.lower() != "https":
            raise SafetyError("provider output URL must use HTTPS")
        provider_http.asset_url = output_url
        image = validate_png(provider_http.get(output_url))
        b2.image_validated = True

        step.assets = [
            Asset(
                asset_id=step.assets[0].asset_id,
                url=_b2_uri(credentials["B2_BUCKET"], plan.image),
                media_type=image.media_type,
                sha256=image.sha256,
                size_bytes=image.size_bytes,
                width=image.width,
                height=image.height,
                metadata={"source_classification": "provider-output-locally-verified"},
            )
        ]
        step.cost_usd = float(EXPECTED_PRICE_USD)
        result.run.status = RunStatus.COMPLETED
        manifest = Manifest.from_run(result.run)
        if not manifest.verify():
            raise SafetyError("GenBlaze Manifest.verify failed before archive")
        manifest_bytes = manifest.to_canonical_json().encode("utf-8")
        manifest_file_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
        brief = {
            "schema": "proofstudio.ps042c5.brief.v1",
            "campaign_id": f"ps042c5-{proof_id}",
            "prompt": CANONICAL_PROMPT,
            "prompt_sha256": PROMPT_SHA256,
            "provider": PROVIDER_NAME,
            "model": MODEL,
            "source_classification": {
                "prompt": "configured",
                "provider": "configured",
                "model": "configured",
            },
        }
        archive = {
            "schema": "proofstudio.ps042c5.run-bundle.v1",
            "proof_id": proof_id,
            "campaign_brief": brief,
            "prompt_metadata": {"sha256": PROMPT_SHA256, "encoding": "UTF-8"},
            "attempt_ledger": [{
                "provider": PROVIDER_NAME,
                "model": MODEL,
                "request_id": request_id,
                "started_at": _safe_time(step.started_at),
                "finished_at": _safe_time(step.completed_at),
                "status": "succeeded",
                "fallback_attempts": 0,
            }],
            "asset_record": {
                "uri": _b2_uri(credentials["B2_BUCKET"], plan.image),
                "media_type": image.media_type,
                "size_bytes": image.size_bytes,
                "sha256": image.sha256,
            },
            "manifest": json.loads(manifest_bytes),
            "b2_object_references": [_b2_uri(credentials["B2_BUCKET"], k) for k in plan.ordered],
            "truth_boundary": "pipeline-operations-and-byte-integrity-only",
            "source_classification": {
                "configured_values": ["provider", "model", "prompt", "price", "cost_ceiling"],
                "provider_observed": ["request_id", "status", "output_url"],
                "locally_computed": ["image_size", "image_sha256", "manifest_file_sha256"],
                "storage_observed": ["exact_key_head", "exact_key_put", "exact_key_get"],
            },
        }
        assert_redacted(brief, credentials)
        assert_redacted(archive, credentials)
        payloads = (
            (plan.brief, _canonical_json_bytes(brief), "application/json"),
            (plan.image, image.data, "image/png"),
            (plan.manifest, manifest_bytes, "application/json"),
            (plan.archive, _canonical_json_bytes(archive), "application/json"),
        )
        for failed_key, data, media_type in payloads:
            b2.put_once(failed_key, data, media_type)

        provider_posts_before_rehydrate = counters.generation_posts
        rehydrated_image = b2.get_exact(plan.image)
        rehydrated_manifest_bytes = b2.get_exact(plan.manifest)
        rehydrated_archive_bytes = b2.get_exact(plan.archive)
        rehydrated_sha = hashlib.sha256(rehydrated_image).hexdigest()
        if rehydrated_sha != image.sha256:
            raise SafetyError("original and rehydrated image hashes differ")
        parsed_manifest = parse_manifest(json.loads(rehydrated_manifest_bytes))
        if not parsed_manifest.verify() or parsed_manifest.canonical_hash != manifest.canonical_hash:
            raise SafetyError("rehydrated GenBlaze manifest verification mismatch")
        if hashlib.sha256(rehydrated_manifest_bytes).hexdigest() != manifest_file_sha256:
            raise SafetyError("rehydrated raw manifest-file hash mismatch")
        rehydrated_archive = json.loads(rehydrated_archive_bytes)
        if rehydrated_archive.get("proof_id") != proof_id:
            raise SafetyError("rehydrated archive identity mismatch")
        if counters.generation_posts != provider_posts_before_rehydrate:
            raise SafetyError("generation submit occurred during rehydrate")

        receipt = build_public_receipt(
            proof_id=proof_id,
            run=result.run,
            step=step,
            image=image,
            manifest=manifest,
            manifest_file_sha256=manifest_file_sha256,
            bucket=credentials["B2_BUCKET"],
            plan=plan,
            rehydrated_image_sha256=rehydrated_sha,
            complete=True,
        )
        assert_redacted(receipt, credentials)
        failed_key = plan.receipt
        b2.put_once(plan.receipt, _canonical_json_bytes(receipt), "application/json")
        if b2.successful_writes != list(plan.ordered):
            raise SafetyError("verification receipt was not written last")

        # Contractual after-all-five exact-key rehydration; never list.
        final_image = b2.get_exact(plan.image)
        final_manifest = b2.get_exact(plan.manifest)
        final_archive = b2.get_exact(plan.archive)
        final_receipt = b2.get_exact(plan.receipt)
        if hashlib.sha256(final_image).hexdigest() != image.sha256:
            raise SafetyError("final rehydrated image hash mismatch")
        if hashlib.sha256(final_manifest).hexdigest() != manifest_file_sha256:
            raise SafetyError("final rehydrated manifest-file hash mismatch")
        if json.loads(final_archive).get("proof_id") != proof_id:
            raise SafetyError("final archive identity mismatch")
        if json.loads(final_receipt).get("completeness_status") != "complete":
            raise SafetyError("final receipt readback mismatch")
        if counters.generation_posts != provider_posts_before_rehydrate:
            raise SafetyError("provider call occurred during final rehydrate")
        return receipt
    except Exception as exc:
        reason = type(exc).__name__
        write_local_failure_receipt(
            dependencies.local_receipt_root,
            plan,
            b2,
            counters,
            failed_key,
            reason,
            outer_exception_type=reason,
            provider_submit_classification=(
                provider_http.submit_classification if provider_http else None
            ),
            provider_response_diagnostic=(
                provider_http.submit_diagnostic if provider_http else None
            ),
        )
        if isinstance(exc, SafetyError):
            raise
        raise SafetyError("execution failed closed; see redacted local failure receipt") from exc
    finally:
        if provider_http is not None:
            provider_http.close()
        if b2 is not None:
            b2.close()


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PS-042C5 one-real-GenBlaze-proof runner",
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--plan", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--execute", action="store_true")
    parser.add_argument("--authorization-token")
    parser.add_argument("--max-cost-usd")
    parser.add_argument("--expected-revision")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not (args.plan or args.self_test or args.execute):
        parser.print_usage(sys.stderr)
        print("error: exactly one mode is required", file=sys.stderr)
        return 2
    if (args.plan or args.self_test) and (
        args.authorization_token or args.max_cost_usd or args.expected_revision
    ):
        print("error: execution-only arguments are forbidden in offline modes", file=sys.stderr)
        return 2
    try:
        if args.plan:
            _print_json(fixed_plan(os.environ))
        elif args.self_test:
            _print_json(offline_self_test(os.environ))
        else:
            _print_json(
                execute_proof(
                    authorization_token=args.authorization_token,
                    max_cost=args.max_cost_usd,
                    expected_revision=args.expected_revision,
                    env=os.environ,
                    dependencies=default_dependencies(),
                )
            )
    except SafetyError as exc:
        print(f"PS-042C5 blocked: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
