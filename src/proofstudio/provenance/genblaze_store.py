"""Reusable Genblaze + Backblaze B2 storage helper.

This module packages the proven working pattern from PS-001A, PS-004, and
PS-005 into a small reusable class so PS-007 (and later slices) can store
ProofStudio artifacts to B2 and verify them through a Genblaze manifest without
duplicating the upload/verify plumbing in every smoke script.

The working pattern reused here:

- ``S3StorageBackend.for_backblaze(...)`` for the B2 backend
- ``ObjectStorageSink(backend, prefix=...)`` for the manifest-aware sink
- local ``Asset(...)`` objects with ``file://`` URLs as ingest inputs
- ``Pipeline.ingest(assets=..., source=..., source_metadata=..., name=..., tenant_id=...)``
  WITHOUT a sink to build an in-memory run + manifest
- ``sink.write_run(result.run, result.manifest)`` to durably store the run
- ``result.manifest.verify()`` for in-memory manifest verification
- ``sink.read_manifest(result.run, verify=True)`` for stored manifest read-back
  and verification

Fail-fast policy: a real pass requires all of:

- ``transfer_failures`` empty after ``write_run``
- ``stored_transfer_failures`` empty after ``read_manifest``
- ``result.manifest.verify()`` true
- stored manifest ``verify()`` true

Truth boundary: this helper proves byte-level asset integrity and recorded
workflow integrity through the Genblaze manifest. It does not prove semantic
truth, legal authenticity, or C2PA authenticity.
"""

from __future__ import annotations

import datetime as _dt
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from genblaze_core.models.asset import Asset
from genblaze_core.pipeline.pipeline import Pipeline
from genblaze_core.storage.sink import ObjectStorageSink
from genblaze_s3.backend import S3StorageBackend


def build_backblaze_backend(
    *,
    bucket: str,
    region: str,
    key_id: str,
    app_key: str,
    auto_lifecycle: bool = False,
    preflight: bool = True,
) -> S3StorageBackend:
    """Build a Backblaze B2 S3-compatible backend.

    Credentials are passed straight into the backend and are never stored on
    the returned object by this helper beyond what the backend itself keeps in
    memory. Callers should not log the returned backend.
    """
    return S3StorageBackend.for_backblaze(
        bucket=bucket,
        region=region,
        key_id=key_id,
        app_key=app_key,
        auto_lifecycle=auto_lifecycle,
        preflight=preflight,
    )


def _transfer_failures(manifest: Any) -> list[Any]:
    failures = getattr(manifest, "transfer_failures", None)
    return list(failures or [])


def _summarize_assets(result: Any) -> list[dict[str, Any]]:
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
                    "metadata": dict(asset.metadata) if asset.metadata else {},
                }
            )
    return assets


@dataclass
class AssetSpec:
    """Specification for one local artifact to store.

    ``path`` is the local file path; it is converted to a ``file://`` URL when
    the :class:`Asset` is built. ``media_type`` becomes the Genblaze
    ``media_type``. ``metadata`` is merged into the Genblaze asset metadata.
    """

    path: Path
    media_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
    artifact_type: str = "proofstudio_artifact"

    def to_asset(self) -> Asset:
        merged: dict[str, Any] = {"artifact_type": self.artifact_type}
        merged.update(self.metadata)
        return Asset(
            url=self.path.resolve().as_uri(),
            media_type=self.media_type,
            metadata=merged,
        )


@dataclass
class GenblazeRunResult:
    """Outcome of a :meth:`GenblazeStore.store_and_verify` run."""

    result: Any
    stored_manifest: Any
    asset_summaries: list[dict[str, Any]]
    manifest_uri: str
    manifest_hash: str
    transfer_failures: list[Any]
    stored_transfer_failures: list[Any]
    in_memory_manifest_verify: bool
    stored_manifest_verify: bool
    run_id: str
    run_status: str


class GenblazeStore:
    """Reusable B2 + Genblaze manifest store.

    Wraps the PS-001A/PS-004/PS-005 working pattern so PS-007 can store a set
    of local ProofStudio artifacts (generated image, prompt packet JSON,
    attempt ledger JSON, provider note Markdown) to B2 and verify them through
    a Genblaze manifest with one call.

    The store never logs credentials, authorization headers, or signed URLs.
    Sanitization of any caller-provided text remains the caller's
    responsibility; this helper only passes caller-provided metadata into the
    Genblaze asset metadata.
    """

    def __init__(
        self,
        *,
        bucket: str,
        region: str,
        key_id: str,
        app_key: str,
        prefix: str,
        auto_lifecycle: bool = False,
        preflight: bool = True,
    ) -> None:
        self._prefix = prefix
        self._backend = build_backblaze_backend(
            bucket=bucket,
            region=region,
            key_id=key_id,
            app_key=app_key,
            auto_lifecycle=auto_lifecycle,
            preflight=preflight,
        )
        self._sink = ObjectStorageSink(self._backend, prefix=prefix)

    @property
    def prefix(self) -> str:
        return self._prefix

    def read_bytes_for_url(self, url: str) -> bytes:
        """Download raw object bytes for a B2 URL previously written here.

        Small reusable helper added for PS-010 so a run archive stored as a B2
        asset can be read back and rehydrated from real object content (strong
        pass) rather than a local copy. Raises ``ValueError`` if the URL cannot
        be resolved to an object key, and propagates backend errors otherwise.
        """
        key = self._backend.key_from_url(url)
        if not key:
            raise ValueError(f"Could not resolve B2 object key from url: {url}")
        return self._backend.get(key)

    def object_exists_for_url(self, url: str) -> bool:
        """Return True if a B2 object exists at ``url`` (best-effort)."""
        key = self._backend.key_from_url(url)
        if not key:
            return False
        try:
            return bool(self._backend.exists(key))
        except Exception:
            return False

    def store_and_verify(
        self,
        *,
        assets: Sequence[AssetSpec | Asset],
        source: str,
        source_metadata: dict[str, Any],
        name: str,
        tenant_id: str = "local",
    ) -> GenblazeRunResult:
        """Ingest local assets, write the run to B2, and verify the manifest.

        Raises ``RuntimeError`` on any hard failure:

        - ingest / write_run exception
        - in-memory manifest verification false
        - non-empty transfer failures after write
        - stored manifest read-back exception
        - stored manifest verification false
        - non-empty transfer failures in stored manifest
        """
        genblaze_assets: list[Asset] = []
        for item in assets:
            if isinstance(item, Asset):
                genblaze_assets.append(item)
            else:
                genblaze_assets.append(item.to_asset())

        try:
            result = Pipeline.ingest(
                assets=genblaze_assets,
                source=source,
                source_metadata=dict(source_metadata),
                name=name,
                tenant_id=tenant_id,
            )
            self._sink.write_run(result.run, result.manifest)
        except Exception as exc:
            raise RuntimeError(
                f"B2/Genblaze ingest or write_run failed: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        in_memory_verify = bool(result.manifest.verify())
        if not in_memory_verify:
            raise RuntimeError(
                "In-memory manifest verification failed after B2 write."
            )

        transfer_failures = _transfer_failures(result.manifest)
        if transfer_failures:
            raise RuntimeError(
                f"Asset transfer failures reported after B2 write: {transfer_failures}"
            )

        try:
            stored_manifest = self._sink.read_manifest(result.run, verify=True)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to read stored manifest back from B2: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        stored_verify = bool(stored_manifest.verify())
        if not stored_verify:
            raise RuntimeError(
                "Stored manifest verification failed after reading back from B2."
            )

        stored_transfer_failures = _transfer_failures(stored_manifest)
        if stored_transfer_failures:
            raise RuntimeError(
                f"Stored manifest contains transfer failures: "
                f"{stored_transfer_failures}"
            )

        manifest_uri = (
            getattr(result.manifest, "manifest_uri", None)
            or self._sink.manifest_url_for(result.run)
        )
        manifest_hash = getattr(result.manifest, "canonical_hash", "") or ""

        asset_summaries = _summarize_assets(result)

        return GenblazeRunResult(
            result=result,
            stored_manifest=stored_manifest,
            asset_summaries=asset_summaries,
            manifest_uri=manifest_uri,
            manifest_hash=manifest_hash,
            transfer_failures=transfer_failures,
            stored_transfer_failures=stored_transfer_failures,
            in_memory_manifest_verify=in_memory_verify,
            stored_manifest_verify=stored_verify,
            run_id=getattr(result.run, "run_id", "") or "",
            run_status=str(getattr(result.run, "status", "")),
        )


# ---------------------------------------------------------------------------
# Exact-key read adapter (PS-041E2-B Phase-1 correction)
# ---------------------------------------------------------------------------

# The pinned accepted genblaze-s3 package version. The exact-key adapter
# asserts this at construction so a future version drift cannot silently
# change the lazy-preflight behavior the adapter exists to bypass.
ACCEPTED_GENBLAZE_S3_VERSION = "0.3.5"


class ExactKeyReadError(Exception):
    """Stable-code error raised by :class:`ExactKeyReadAdapter`.

    Carries only a stable error code. The raw client exception text, bucket
    name, endpoint URL and object key are NEVER carried or printed.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _assert_genblaze_s3_version() -> None:
    """Assert the installed genblaze-s3 package is the pinned accepted version.

    Fail-closed with a stable ``ExactKeyReadError`` code on mismatch or when
    the package metadata cannot be resolved. This guard guarantees the
    adapter operates against the exact lazy-preflight behavior audited for
    genblaze-s3==0.3.5 (release commit c5f7a5ba).
    """
    try:
        from importlib.metadata import PackageNotFoundError, version
    except ImportError as exc:  # pragma: no cover — stdlib on pinned runtime
        raise ExactKeyReadError("genblaze_s3_metadata_unavailable") from exc
    try:
        installed = version("genblaze-s3")
    except PackageNotFoundError as exc:
        raise ExactKeyReadError("genblaze_s3_not_installed") from exc
    except Exception as exc:
        raise ExactKeyReadError("genblaze_s3_metadata_unavailable") from exc
    if installed != ACCEPTED_GENBLAZE_S3_VERSION:
        raise ExactKeyReadError("genblaze_s3_version_mismatch")


def _normalize_boto_last_modified(value: Any) -> str | None:
    """Normalize a boto3 ``LastModified`` value to a deterministic UTC ISO
    string with the ``Z`` suffix, or ``None`` when the value is absent.

    Accepts a ``datetime`` (as returned by boto3) or an ISO-8601 string.
    Naive datetimes are assumed UTC. Malformed values reject.
    """
    if value is None:
        return None
    if isinstance(value, _dt.datetime):
        dt = value
    elif isinstance(value, str):
        if value.strip() == "":
            return None
        try:
            dt = _dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            raise ExactKeyReadError("head_response_invalid_last_modified")
    else:
        raise ExactKeyReadError("head_response_invalid_last_modified")
    if not isinstance(dt, _dt.datetime):
        raise ExactKeyReadError("head_response_invalid_last_modified")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    return dt.astimezone(_dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _classify_client_error(exc: Exception) -> str:
    """Classify a boto3 ``ClientError`` (or any client exception) into a
    stable code.

    Returns ``"missing"`` for 404 / NoSuchKey responses and for the B2
    least-privilege 403 / AccessDenied shape (which hides non-existent keys
    behind 403). Returns ``"backend_operation_failed"`` for any other
    client-side failure. Never carries the raw exception text.
    """
    response = getattr(exc, "response", None)
    if isinstance(response, dict):
        code = response.get("Error", {}).get("Code", "")
        if code in ("404", "NoSuchKey"):
            return "missing"
        if code in ("403", "AccessDenied"):
            return "missing"
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status == 404:
            return "missing"
    return "backend_operation_failed"


class ExactKeyReadAdapter:
    """Narrow exact-key read adapter over an accepted :class:`S3StorageBackend`.

    Bypasses the lazy bucket-region preflight (``_ensure_region_verified``)
    and issues ONLY low-level ``HeadObject`` and ranged ``GetObject`` calls
    through the accepted backend's pinned boto3 client. It never calls
    ``head_bucket``, never performs regional discovery or probing, never
    lists, never writes, never deletes, and never generates signed URLs.

    Contract (enforced at construction and on every call):

    - exact genblaze-s3 package version is asserted (0.3.5);
    - the wrapped backend must expose the required internal attributes
      ``_client`` and ``_bucket`` (checked fail-closed);
    - :meth:`head_object` issues exactly one boto3 ``head_object`` call and
      returns a normalized metadata dict;
    - :meth:`get_range` issues exactly one ranged boto3 ``get_object`` call
      and returns exactly ``length`` bytes (or ``b""`` when ``length == 0``);
    - :meth:`close` delegates to the underlying backend's supported
      ``close()`` method exactly once;
    - the generic boto3 client is NEVER exposed to callers;
    - raw client errors are normalized to stable :class:`ExactKeyReadError`
      codes; the raw exception text, bucket name, endpoint and object key
      never escape.

    Counters distinguish SDK calls from actual HTTP attempts:

    - ``head_object_sdk_calls`` / ``ranged_get_object_sdk_calls`` count SDK
      invocations;
    - ``head_object_http_attempts`` / ``ranged_get_object_http_attempts``
      accumulate ``1 + RetryAttempts`` from successful responses;
    - ``head_bucket_http_attempts`` / ``regional_probe_http_attempts`` are
      always 0 because no preflight/probe path is reachable;
    - ``list_calls``, ``write_attempts``, ``delete_attempts``,
      ``signed_url_attempts`` — always 0 (forbidden surface never exposed).

    The accepted successful controlled read requires all of
    ``head_bucket_http_attempts``, ``regional_probe_http_attempts``, ``list_calls``,
    ``write_attempts``, ``delete_attempts`` and ``signed_url_attempts`` to
    remain zero. The caller computes ``live_b2_calls`` from the four explicit
    HTTP-attempt counters, never from SDK invocations.
    """

    def __init__(self, backend: S3StorageBackend) -> None:
        _assert_genblaze_s3_version()
        if backend is None:
            raise ExactKeyReadError("backend_missing")
        client = getattr(backend, "_client", None)
        bucket = getattr(backend, "_bucket", None)
        if client is None or bucket is None:
            raise ExactKeyReadError("backend_attributes_unavailable")
        if not isinstance(bucket, str) or not bucket:
            raise ExactKeyReadError("backend_attributes_unavailable")
        # Confined compatibility shim: the adapter holds the accepted
        # backend's pinned client and bucket name only. It never exports
        # the generic boto3 client to callers and never invokes the lazy
        # bucket-region preflight.
        self._backend = backend
        self._client = client
        self._bucket = bucket
        # SDK invocations and actual HTTP attempts are deliberately separate.
        # A single SDK call may perform 1 + RetryAttempts HTTP attempts under
        # the pinned Botocore adaptive retry policy.
        self.head_object_sdk_calls: int = 0
        self.ranged_get_object_sdk_calls: int = 0
        self.head_object_http_attempts: int = 0
        self.ranged_get_object_http_attempts: int = 0
        self.head_bucket_http_attempts: int = 0
        self.regional_probe_http_attempts: int = 0
        self.list_calls: int = 0
        self.write_attempts: int = 0
        self.delete_attempts: int = 0
        self.signed_url_attempts: int = 0

    @staticmethod
    def _is_exact_key_adapter(value: Any) -> bool:
        """Duck-type check used by callers to detect this adapter.

        The adapter is recognized by the combination of ``head_object``
        and explicit no-preflight HTTP-attempt counters. Generic backends and
        in-process fakes do not expose both.
        """
        return (
            hasattr(value, "head_object")
            and hasattr(value, "head_bucket_http_attempts")
            and hasattr(value, "ranged_get_object_sdk_calls")
        )

    @property
    def head_object_calls(self) -> int:
        """Compatibility alias; this is an SDK-call count, never HTTP attempts."""
        return self.head_object_sdk_calls

    @property
    def ranged_get_object_calls(self) -> int:
        """Compatibility alias; this is an SDK-call count, never HTTP attempts."""
        return self.ranged_get_object_sdk_calls

    @property
    def head_bucket_calls(self) -> int:
        return self.head_bucket_http_attempts

    @property
    def regional_probe_calls(self) -> int:
        return self.regional_probe_http_attempts

    def head_object(self, key: str) -> dict[str, Any] | None:
        """Issue one low-level ``HeadObject`` for ``key``.

        Returns a normalized metadata dict (``size_bytes``, ``etag``,
        ``version_id`` (None when absent), ``last_modified_iso`` (None when
        absent)), or ``None`` for a 404 / NoSuchKey / least-privilege 403
        missing response. Never triggers the lazy bucket-region preflight.
        """
        if not isinstance(key, str) or not key:
            raise ExactKeyReadError("head_object_invalid_key")
        self.head_object_sdk_calls += 1
        try:
            resp = self._client.head_object(Bucket=self._bucket, Key=key)
        except Exception as exc:
            if _classify_client_error(exc) == "missing":
                return None
            raise ExactKeyReadError("backend_operation_failed") from None
        self.head_object_http_attempts += self._response_http_attempts(
            resp, "head_response_retry_metadata_invalid"
        )
        return self._normalize_head_response(resp)

    @staticmethod
    def _response_http_attempts(resp: Any, error_code: str) -> int:
        """Return ``1 + RetryAttempts`` for a successful Botocore response."""
        if not isinstance(resp, Mapping):
            raise ExactKeyReadError(error_code)
        metadata = resp.get("ResponseMetadata")
        if not isinstance(metadata, Mapping):
            raise ExactKeyReadError(error_code)
        retries = metadata.get("RetryAttempts")
        if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
            raise ExactKeyReadError(error_code)
        return 1 + retries

    @staticmethod
    def _normalize_head_response(resp: Mapping[str, Any]) -> dict[str, Any]:
        """Normalize a boto3 ``head_object`` response to the canonical dict
        shape consumed by the accepted reader.

        Produces exactly:
        ``{"size_bytes": int, "etag": str, "version_id": str | None,
           "last_modified_iso": str | None}``

        ``version_id`` is ``None`` when the response does not carry one
        (the pinned genblaze-s3 ``ObjectMetadata`` shape and B2's standard
        head_object response do not expose a version id). A genuine version
        id string is retained as-is.
        """
        if not isinstance(resp, Mapping):
            raise ExactKeyReadError("head_response_invalid_shape")
        size = resp.get("ContentLength", 0)
        etag = resp.get("ETag", "")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise ExactKeyReadError("head_response_invalid_size")
        if not isinstance(etag, str) or etag == "":
            raise ExactKeyReadError("head_response_invalid_etag")
        version_id = resp.get("VersionId")
        if version_id is None:
            version_id_norm: str | None = None
        elif isinstance(version_id, str):
            version_id_norm = version_id if version_id != "" else None
        else:
            raise ExactKeyReadError("head_response_invalid_version_id")
        last_modified_iso = _normalize_boto_last_modified(resp.get("LastModified"))
        return {
            "size_bytes": size,
            "etag": etag,
            "version_id": version_id_norm,
            "last_modified_iso": last_modified_iso,
        }

    def get_range(self, key: str, *, offset: int, length: int) -> bytes:
        """Issue one ranged ``GetObject`` for ``key``.

        ``offset`` must be >= 0 and ``length`` must be >= 0. ``length == 0``
        returns ``b""`` without contacting the backend (mirrors the accepted
        genblaze-s3 ``get_range`` contract). Otherwise issues exactly one
        ranged ``get_object`` call and returns the served bytes.
        """
        if not isinstance(key, str) or not key:
            raise ExactKeyReadError("get_object_invalid_key")
        if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
            raise ExactKeyReadError("get_object_invalid_offset")
        if not isinstance(length, int) or isinstance(length, bool) or length < 0:
            raise ExactKeyReadError("get_object_invalid_length")
        if length == 0:
            return b""
        self.ranged_get_object_sdk_calls += 1
        range_header = f"bytes={offset}-{offset + length - 1}"
        try:
            resp = self._client.get_object(
                Bucket=self._bucket, Key=key, Range=range_header,
            )
        except Exception as exc:
            if _classify_client_error(exc) == "missing":
                raise ExactKeyReadError("get_object_missing") from None
            raise ExactKeyReadError("backend_operation_failed") from None
        if not isinstance(resp, Mapping):
            raise ExactKeyReadError("get_object_response_invalid_shape")
        body = resp.get("Body")
        read = getattr(body, "read", None)
        close = getattr(body, "close", None)
        if not callable(close):
            resp = None
            body = None
            read = None
            raise ExactKeyReadError("get_object_body_invalid")

        collected = bytearray()
        pending_code: str | None = None
        close_failed = False
        try:
            if not callable(read):
                raise ExactKeyReadError("get_object_body_invalid")
            attempts = self._response_http_attempts(
                resp, "get_object_response_retry_metadata_invalid"
            )
            self.ranged_get_object_http_attempts += attempts
            content_length = resp.get("ContentLength")
            if (
                isinstance(content_length, bool)
                or not isinstance(content_length, int)
                or content_length < 0
            ):
                raise ExactKeyReadError("get_object_content_length_invalid")
            if content_length != length:
                raise ExactKeyReadError("get_object_length_mismatch")
            content_range = resp.get("ContentRange")
            if content_range is not None:
                expected_prefix = f"bytes {offset}-{offset + length - 1}/"
                if (
                    not isinstance(content_range, str)
                    or not content_range.startswith(expected_prefix)
                ):
                    raise ExactKeyReadError("get_object_content_range_mismatch")
                total = content_range[len(expected_prefix):]
                if total != "*":
                    if not total.isascii() or not total.isdigit():
                        raise ExactKeyReadError("get_object_content_range_mismatch")
                    if int(total) < offset + length:
                        raise ExactKeyReadError("get_object_content_range_mismatch")
            while len(collected) <= length:
                remaining = length + 1 - len(collected)
                try:
                    chunk = read(remaining)
                except Exception:
                    raise ExactKeyReadError("get_object_body_read_failed") from None
                if not isinstance(chunk, (bytes, bytearray, memoryview)):
                    raise ExactKeyReadError("get_object_response_not_bytes")
                if len(chunk) > remaining:
                    raise ExactKeyReadError("get_object_range_exceeded")
                chunk_bytes = bytes(chunk)
                if not chunk_bytes:
                    break
                collected.extend(chunk_bytes)
                if len(collected) == length + 1:
                    raise ExactKeyReadError("get_object_range_exceeded")
        except ExactKeyReadError as exc:
            pending_code = exc.code
        except Exception:
            pending_code = "backend_operation_failed"
        finally:
            try:
                close()
            except Exception:
                close_failed = True
            # Do not let a returned exception traceback retain the response or
            # streaming body. Only stable scalar state survives this point.
            resp = None
            body = None
            read = None
            close = None
            chunk = None
            chunk_bytes = None

        if close_failed:
            raise ExactKeyReadError("get_object_body_close_failed") from None
        if pending_code is not None:
            raise ExactKeyReadError(pending_code) from None

        if len(collected) != length:
            raise ExactKeyReadError("get_object_length_mismatch")
        return bytes(collected)

    def close(self) -> None:
        """Delegate to the underlying backend's supported ``close()``.

        The accepted :class:`S3StorageBackend` exposes ``close()`` which
        releases the boto3 client's urllib3 connection pool. The adapter
        never owns the client; it only forwards the close to the backend
        that does.
        """
        close_method = getattr(self._backend, "close", None)
        if not callable(close_method):
            raise ExactKeyReadError("backend_close_unsupported")
        try:
            close_method()
        except Exception as exc:
            raise ExactKeyReadError("backend_close_failed") from exc


def build_exact_key_read_adapter(backend: S3StorageBackend) -> ExactKeyReadAdapter:
    """Build an :class:`ExactKeyReadAdapter` over an accepted backend.

    Convenience factory. The backend must have been constructed via the
    accepted :func:`build_backblaze_backend` (typically with
    ``preflight=False`` so construction does not itself run the lazy
    bucket-region preflight). The adapter bypasses the lazy preflight on
    every subsequent read; it issues only exact-key ``HeadObject`` and
    ranged ``GetObject`` calls.
    """
    return ExactKeyReadAdapter(backend)


__all__ = [
    "GenblazeStore",
    "GenblazeRunResult",
    "AssetSpec",
    "build_backblaze_backend",
    "ExactKeyReadAdapter",
    "ExactKeyReadError",
    "build_exact_key_read_adapter",
    "ACCEPTED_GENBLAZE_S3_VERSION",
]
