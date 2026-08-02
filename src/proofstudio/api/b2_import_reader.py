"""Optional bounded PS-041D reader over an injected genblaze-s3-like backend."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Protocol

from proofstudio.api.genblaze_external_adapter import ImportValidationError, _duplicate_key
from proofstudio.api.imported_bundle import B2ObjectReference


class B2Backend(Protocol):
    def head(self, key: str) -> dict[str, Any] | None: ...
    def read_bytes(self, key: str, max_bytes: int) -> bytes: ...
    def list(self, prefix: str, limit: int) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class B2ImportReaderConfig:
    enabled: bool = False
    bucket_alias: str = ""
    root_prefix: str = ""
    max_listed_objects: int = 256
    max_json_bytes: int = 1_048_576
    max_asset_bytes: int = 134_217_728
    max_aggregate_bytes: int = 536_870_912


class BoundedB2ImportReader:
    def __init__(self, backend: B2Backend, config: B2ImportReaderConfig) -> None:
        self.backend = backend
        self.config = config
        self._read_bytes = 0

    def _key(self, reference: B2ObjectReference) -> str:
        if not self.config.enabled:
            raise ImportValidationError("b2_import_disabled", 503)
        if reference.bucket_alias != self.config.bucket_alias:
            raise ImportValidationError("b2_alias_not_allowed")
        root = self.config.root_prefix.rstrip("/") + "/"
        if not reference.object_key.startswith(root):
            raise ImportValidationError("b2_key_outside_root")
        return reference.object_key

    def list_bounded(self) -> list[dict[str, Any]]:
        if not self.config.enabled:
            raise ImportValidationError("b2_import_disabled", 503)
        items = self.backend.list(self.config.root_prefix.rstrip("/") + "/", self.config.max_listed_objects + 1)
        if len(items) > self.config.max_listed_objects:
            raise ImportValidationError("b2_object_count_exceeded")
        return items

    def read_json(self, reference: B2ObjectReference) -> dict[str, Any]:
        key = self._key(reference)
        before = self.backend.head(key)
        if before is None:
            raise ImportValidationError("object_missing")
        if int(before.get("size_bytes", 0)) > self.config.max_json_bytes:
            raise ImportValidationError("b2_json_too_large", 413)
        try:
            raw = self.backend.read_bytes(key, self.config.max_json_bytes)
        except ImportValidationError:
            raise
        except Exception as exc:
            raise ImportValidationError("storage_unavailable", 503) from exc
        self._read_bytes += len(raw)
        if self._read_bytes > self.config.max_aggregate_bytes:
            raise ImportValidationError("b2_aggregate_too_large", 413)
        after = self.backend.head(key)
        observation = ("etag", "size_bytes", "version_id")
        if after is None or any(before.get(field) != after.get(field) for field in observation):
            raise ImportValidationError("object_changed_during_read")
        if reference.sha256 and hashlib.sha256(raw).hexdigest() != reference.sha256:
            raise ImportValidationError("hash_mismatch")
        try:
            value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_duplicate_key)
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ImportValidationError("malformed_json") from exc
        if not isinstance(value, dict):
            raise ImportValidationError("malformed_json")
        return value
