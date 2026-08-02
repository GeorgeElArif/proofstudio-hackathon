"""Strict PS-041D imported-bundle contracts and deterministic helpers."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

BUNDLE_SCHEMA = "proofstudio.genblaze_bundle.v1"
FINGERPRINT_SCHEMA = "ps041d.fingerprint.v1"
SOURCE_TYPE = "genblaze_multi_provider_sample"
SOURCE_SLUG = "genblaze-gen-media-multi-provider-sample"
PINNED_SOURCE_REVISION = "2e31577b7a9d5a7b0309d814f2d0282088b33fe8"
MAX_BUNDLE_BYTES = 1_048_576
MAX_JSON_OBJECT_BYTES = 1_048_576
MAX_AGGREGATE_JSON_BYTES = 16_777_216
MAX_OBJECTS = 256
MAX_RELATIONSHIPS = 64
MAX_DEPTH = 32
MAX_STRING = 8_192
MAX_EVIDENCE_STRING = 256
MAX_NOTICE = 4_096


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)


class ImportRole(str, Enum):
    STAGE_A = "stage_a_storyboard"
    B0 = "stage_b0_manifest"
    B1 = "stage_b1_manifest"
    B2 = "stage_b2_manifest"
    STAGE_C = "stage_c_composition"
    FINAL = "final_delivery"
    EMBEDDED = "embedded_manifest"


class EvidenceClass(str, Enum):
    RECORDED = "recorded"
    INFERRED = "inferred"


class NodeKind(str, Enum):
    IMPORT_BUNDLE = "import_bundle"
    STANDALONE_ARTIFACT = "standalone_artifact"
    GENBLAZE_RUN = "genblaze_run"
    MANIFEST = "manifest"
    ASSET = "asset"
    EXTERNAL_COMPOSITION = "external_composition"


class EdgeKind(str, Enum):
    PARENT_RUN = "parent_run"
    GENERATED_ASSET = "generated_asset"
    EXTERNAL_INPUT = "external_input"
    STORYBOARD_FOR = "storyboard_for"
    SCENE_MEMBER = "scene_member"
    COMPOSITION_INPUT = "composition_input"
    COMPOSED_OUTPUT = "composed_output"
    MANIFEST_FOR = "manifest_for"
    EMBEDDED_MANIFEST = "embedded_manifest"


class CheckOutcome(str, Enum):
    RECORDED = "recorded"
    PARSED = "parsed"
    HASH_PRESENT = "hash_present"
    HASH_VERIFIED = "hash_verified"
    HASH_MISMATCH = "hash_mismatch"
    MANIFEST_HASH_VERIFIED = "manifest_hash_verified"
    MANIFEST_OUTPUT_HASHES_DECLARED = "manifest_output_hashes_declared"
    MANIFEST_INVALID = "manifest_invalid"
    OBJECT_MISSING = "object_missing"
    RELATIONSHIP_RECORDED = "relationship_recorded"
    RELATIONSHIP_INFERRED = "relationship_inferred"
    UNSUPPORTED_SCHEMA = "unsupported_schema"
    PARTIAL_BUNDLE = "partial_bundle"
    UNAVAILABLE = "unavailable"
    NOT_CHECKED = "not_checked"


def _bounded_text(value: str, limit: int = MAX_STRING) -> str:
    if value != unicodedata.normalize("NFC", value):
        raise ValueError("identifier_not_nfc")
    if len(value) > limit:
        raise ValueError("string_too_long")
    if any(unicodedata.category(ch) == "Cc" for ch in value):
        raise ValueError("control_character")
    return value


class B2ObjectReference(StrictModel):
    backend: Literal["b2_s3"] = "b2_s3"
    bucket_alias: str = Field(max_length=MAX_EVIDENCE_STRING)
    object_key: str = Field(max_length=MAX_STRING)
    version_id: str | None = Field(default=None, max_length=MAX_EVIDENCE_STRING)
    size_bytes: int | None = Field(default=None, ge=0)
    content_type: str | None = Field(default=None, max_length=MAX_EVIDENCE_STRING)
    etag: str | None = Field(default=None, max_length=MAX_EVIDENCE_STRING)
    sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    uploaded_at: datetime | None = None
    source_prefix: str | None = Field(default=None, max_length=MAX_STRING)
    manifest_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @field_validator("bucket_alias", "object_key", "version_id", "content_type", "etag", "source_prefix")
    @classmethod
    def bounded_strings(cls, value: str | None) -> str | None:
        return None if value is None else _bounded_text(value)

    @field_validator("object_key")
    @classmethod
    def safe_key(cls, value: str) -> str:
        lowered = value.lower()
        if (
            value.startswith("/") or "\\" in value or "?" in value or "#" in value
            or "://" in lowered or any(part == ".." for part in value.split("/"))
        ):
            raise ValueError("unsafe_object_key")
        return value

    @field_validator("source_prefix")
    @classmethod
    def safe_prefix(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value.startswith("/") or "\\" in value or "?" in value or "#" in value or "://" in value.lower() or any(part == ".." for part in value.split("/")):
            raise ValueError("unsafe_source_prefix")
        return value


class ImportObjectDescriptor(StrictModel):
    role: ImportRole
    source_id: str = Field(min_length=1, max_length=MAX_EVIDENCE_STRING)
    inline_json: dict[str, Any] | list[Any] | None = None
    b2_reference: B2ObjectReference | None = None
    content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    missing: bool = False
    limitation: str | None = Field(default=None, max_length=MAX_NOTICE)

    @field_validator("source_id", "limitation")
    @classmethod
    def safe_strings(cls, value: str | None) -> str | None:
        return None if value is None else _bounded_text(value, MAX_NOTICE)

    @model_validator(mode="after")
    def one_source(self) -> "ImportObjectDescriptor":
        sources = int(self.inline_json is not None) + int(self.b2_reference is not None)
        if self.missing:
            if sources:
                raise ValueError("missing_object_has_content")
        elif sources != 1:
            raise ValueError("exactly_one_content_source_required")
        return self


class ImportRelationshipDescriptor(StrictModel):
    kind: EdgeKind
    source_id: str = Field(min_length=1, max_length=MAX_EVIDENCE_STRING)
    target_id: str | None = Field(default=None, max_length=MAX_EVIDENCE_STRING)
    missing_source_id: str | None = Field(default=None, max_length=MAX_EVIDENCE_STRING)
    evidence_class: EvidenceClass
    source_locator: str | None = Field(default=None, max_length=MAX_NOTICE)
    limitation: str | None = Field(default=None, max_length=MAX_NOTICE)
    hash_covered: bool = False

    @field_validator("source_id", "target_id", "missing_source_id", "source_locator", "limitation")
    @classmethod
    def safe_strings(cls, value: str | None) -> str | None:
        return None if value is None else _bounded_text(value, MAX_NOTICE)

    @model_validator(mode="after")
    def target_or_missing(self) -> "ImportRelationshipDescriptor":
        if (self.target_id is None) == (self.missing_source_id is None):
            raise ValueError("exactly_one_relationship_target_required")
        return self


class ImportBundleRequest(StrictModel):
    bundle_schema: Literal["proofstudio.genblaze_bundle.v1"]
    source_type: Literal["genblaze_multi_provider_sample"]
    source_slug: Literal["genblaze-gen-media-multi-provider-sample"]
    source_revision: Literal["2e31577b7a9d5a7b0309d814f2d0282088b33fe8"]
    objects: list[ImportObjectDescriptor] = Field(max_length=MAX_OBJECTS)
    relationships: list[ImportRelationshipDescriptor] = Field(max_length=MAX_RELATIONSHIPS)
    positional_scene_convention: bool = False
    partial_bundle: bool = False


class ImportCheck(StrictModel):
    outcome: CheckOutcome
    subject: str = Field(max_length=MAX_EVIDENCE_STRING)
    detail: str | None = Field(default=None, max_length=MAX_NOTICE)


class ImportLimitation(StrictModel):
    code: str = Field(max_length=MAX_EVIDENCE_STRING)
    notice: str = Field(max_length=MAX_NOTICE)


class ImportedStepSummary(StrictModel):
    step_id: str = Field(max_length=MAX_EVIDENCE_STRING)
    step_index: int
    provider: str | None = Field(default=None, max_length=MAX_EVIDENCE_STRING)
    model: str = Field(max_length=MAX_EVIDENCE_STRING)
    modality: str = Field(max_length=MAX_EVIDENCE_STRING)
    status: str = Field(max_length=MAX_EVIDENCE_STRING)
    output_count: int = Field(ge=0)
    input_count: int = Field(ge=0)


class ImportedRunSummary(StrictModel):
    run_id: str = Field(max_length=MAX_EVIDENCE_STRING)
    stage: Literal["B0", "B1", "B2"]
    manifest_schema: Literal["1.5"]
    manifest_hash: str | None = None
    parent_run_id: str | None = Field(default=None, max_length=MAX_EVIDENCE_STRING)
    status: str = Field(max_length=MAX_EVIDENCE_STRING)
    steps: list[ImportedStepSummary]


class ImportedLineageNode(StrictModel):
    node_id: str
    campaign_id: str
    bundle_id: str
    kind: NodeKind
    source_id: str
    source_role: ImportRole | Literal["import_bundle", "generated_asset", "external_input"]
    content_fingerprint: str
    evidence_class: EvidenceClass
    checks: list[ImportCheck] = Field(default_factory=list)
    limitations: list[ImportLimitation] = Field(default_factory=list)
    run: ImportedRunSummary | None = None
    b2_reference: B2ObjectReference | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ImportedLineageEdge(StrictModel):
    edge_id: str
    campaign_id: str
    bundle_id: str
    kind: EdgeKind
    source_node_id: str
    target_node_id: str | None = None
    missing_source_id: str | None = None
    evidence_class: EvidenceClass
    hash_covered: bool
    check_outcome: CheckOutcome
    source_locator: str | None = None
    limitations: list[ImportLimitation] = Field(default_factory=list)


class ImportedBundleRecord(StrictModel):
    bundle_id: str
    campaign_id: str
    bundle_fingerprint: str
    fingerprint_schema: Literal["ps041d.fingerprint.v1"] = FINGERPRINT_SCHEMA
    source_type: str
    source_slug: str
    source_revision: str
    state: Literal["complete", "partial_bundle"]
    node_ids: list[str]
    edge_ids: list[str]


class ImportResult(StrictModel):
    created: bool
    bundle: ImportedBundleRecord
    nodes: list[ImportedLineageNode]
    edges: list[ImportedLineageEdge]


class PortableLineagePassport(StrictModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True, serialize_by_alias=True)
    passport_schema: Literal["proofstudio.portable_lineage_passport.v1"] = Field(
        default="proofstudio.portable_lineage_passport.v1", alias="schema"
    )
    campaign_id: str
    bundle_id: str
    bundle_fingerprint: str
    source_type: str
    source_slug: str
    source_revision: str
    state: Literal["complete", "partial_bundle"]
    nodes: list[ImportedLineageNode]
    edges: list[ImportedLineageEdge]
    limitations: list[ImportLimitation]
    truth_boundary: Literal["ProofStudio reports what the imported pipeline record states; proof does not equal truth."] = (
        "ProofStudio reports what the imported pipeline record states; proof does not equal truth."
    )


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def deterministic_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()
    return f"{prefix}_{digest[:32]}"


__all__ = [name for name in globals() if not name.startswith("_")]
