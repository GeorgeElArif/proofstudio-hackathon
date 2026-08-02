from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from proofstudio.api.b2_import_reader import B2ImportReaderConfig, BoundedB2ImportReader
from proofstudio.api.genblaze_external_adapter import ImportValidationError, build_candidate
from proofstudio.api.imported_bundle import B2ObjectReference, ImportBundleRequest

FIXTURE = Path(__file__).parent / "fixtures/ps041d/genblaze-multi-provider-bundle-v1.json"


class FakeBackend:
    def __init__(self, body: bytes = b'{"ok":true}') -> None:
        self.body = body; self.changed = False; self.missing = False; self.fail = False; self.calls: list[str] = []
    def head(self, key: str):
        self.calls.append("head")
        if self.missing: return None
        return {"size_bytes": len(self.body), "etag": "after" if self.changed and self.calls.count("head") > 1 else "before", "version_id": "v1"}
    def read_bytes(self, key: str, max_bytes: int) -> bytes:
        self.calls.append("read")
        if self.fail: raise OSError("fake unavailable")
        return self.body
    def list(self, prefix: str, limit: int): return [{"key": f"{prefix}{i}"} for i in range(limit)]


def ref(**updates):
    data = {"backend":"b2_s3", "bucket_alias":"configured", "object_key":"import-root/a.json"}; data.update(updates)
    return B2ObjectReference.model_validate(data)


def reader(backend: FakeBackend, **updates):
    return BoundedB2ImportReader(backend, B2ImportReaderConfig(enabled=True, bucket_alias="configured", root_prefix="import-root", **updates))


def test_disabled_alias_root_and_list_bounds() -> None:
    backend = FakeBackend()
    with pytest.raises(ImportValidationError, match="b2_import_disabled"):
        BoundedB2ImportReader(backend, B2ImportReaderConfig()).read_json(ref())
    with pytest.raises(ImportValidationError, match="b2_alias_not_allowed"):
        reader(backend).read_json(ref(bucket_alias="other"))
    with pytest.raises(ImportValidationError, match="b2_key_outside_root"):
        reader(backend).read_json(ref(object_key="other/a.json"))
    with pytest.raises(ImportValidationError, match="b2_object_count_exceeded"):
        reader(backend, max_listed_objects=1).list_bounded()


def test_metadata_head_before_get_json_and_sha() -> None:
    backend = FakeBackend(); digest = hashlib.sha256(backend.body).hexdigest()
    assert reader(backend).read_json(ref(sha256=digest)) == {"ok": True}
    assert backend.calls == ["head", "read", "head"]
    with pytest.raises(ImportValidationError, match="hash_mismatch"):
        reader(FakeBackend()).read_json(ref(sha256="0" * 64))


def test_missing_unavailable_malformed_size_aggregate_and_changed() -> None:
    backend = FakeBackend(); backend.missing = True
    with pytest.raises(ImportValidationError, match="object_missing"): reader(backend).read_json(ref())
    backend = FakeBackend(); backend.fail = True
    with pytest.raises(ImportValidationError, match="storage_unavailable"): reader(backend).read_json(ref())
    with pytest.raises(ImportValidationError, match="malformed_json"): reader(FakeBackend(b"not-json")).read_json(ref())
    with pytest.raises(ImportValidationError, match="b2_json_too_large"): reader(FakeBackend(b"{}"), max_json_bytes=1).read_json(ref())
    with pytest.raises(ImportValidationError, match="b2_aggregate_too_large"): reader(FakeBackend(), max_aggregate_bytes=1).read_json(ref())
    backend = FakeBackend(); backend.changed = True
    with pytest.raises(ImportValidationError, match="object_changed_during_read"): reader(backend).read_json(ref())


def test_reference_rejects_traversal_absolute_scheme_query_fragment() -> None:
    for key in ("../a", "/a", "https://example.invalid/a", "import-root/a?x=1", "import-root/a#x", "import-root\\a"):
        with pytest.raises(ValueError): B2ObjectReference(bucket_alias="configured", object_key=key)


def b2_request() -> dict:
    data = json.loads(FIXTURE.read_text())
    data["objects"][0].pop("inline_json")
    data["objects"][0]["b2_reference"] = {
        "backend": "b2_s3", "bucket_alias": "configured", "object_key": "import-root/a.json"
    }
    data["objects"][5]["b2_reference"]["bucket_alias"] = "configured"
    return data


@pytest.mark.parametrize(("value", "code"), [
    ({"nested": {"url": "https://example.invalid/object?X-Amz-Signature=do-not-echo"}}, "signed_or_credentialed_url_forbidden"),
    ({"nested": {"credentials": "do-not-echo"}}, "credential_field_forbidden"),
    ({"nested": "bad\u0001value"}, "control_character"),
    ({"nested": "e\u0301"}, "identifier_not_nfc"),
])
def test_b2_returned_json_uses_inline_sanitization_boundary(value: dict, code: str) -> None:
    backend = FakeBackend(json.dumps(value, ensure_ascii=False).encode())
    with pytest.raises(ImportValidationError) as exc:
        build_candidate("camp_b2", ImportBundleRequest.model_validate(b2_request()), b2_json_reader=reader(backend).read_json,
                        server_bucket_alias="configured", server_import_root="import-root")
    assert exc.value.code == code
    assert "do-not-echo" not in str(exc.value)


def test_b2_returned_json_depth_and_valid_content() -> None:
    nested: dict = {}; cursor = nested
    for _ in range(34):
        cursor["x"] = {}; cursor = cursor["x"]
    with pytest.raises(ImportValidationError, match="excessive_nesting"):
        build_candidate("camp_b2", ImportBundleRequest.model_validate(b2_request()),
                        b2_json_reader=reader(FakeBackend(json.dumps(nested).encode())).read_json,
                        server_bucket_alias="configured", server_import_root="import-root")
    built = build_candidate("camp_b2", ImportBundleRequest.model_validate(b2_request()),
                            b2_json_reader=reader(FakeBackend(b'{"title":"sanitized"}')).read_json,
                            server_bucket_alias="configured", server_import_root="import-root")
    assert any(node.metadata.get("title") == "sanitized" for node in built.nodes)
