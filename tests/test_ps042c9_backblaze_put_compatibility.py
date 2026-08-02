from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest
from botocore.exceptions import ClientError
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "ps042c6_gmi_submit_reconciliation.py"
SPEC = importlib.util.spec_from_file_location("ps042c9_runner_tests", RUNNER)
assert SPEC and SPEC.loader
r = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = r
SPEC.loader.exec_module(r)

REVISION = "9e1d4e75738e9748bb94ed3235f9f9dd116db45b"
REQUEST_ID = r.FUNDED_AUTHORIZED_REQUEST_ID
ASSET_URL = "https://storage.googleapis.com/offline/proof.png?signature=redacted"


def valid_png() -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (r.c5.WIDTH, r.c5.HEIGHT), (11, 23, 47)).save(
        output, format="PNG"
    )
    return output.getvalue()


def response(status: int, *, data: Any = None, content: bytes = b"") -> httpx.Response:
    request = httpx.Request("GET", "https://offline.invalid/")
    if data is not None:
        return httpx.Response(status, json=data, request=request)
    return httpx.Response(status, content=content, request=request)


class FakeProvider:
    def __init__(self, status: str = "success", asset: bytes | None = None):
        self.status = status
        self.asset = valid_png() if asset is None else asset
        self.gets: list[str] = []
        self.posts = 0

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        assert kwargs["follow_redirects"] is False
        self.gets.append(url)
        if url.startswith("/requests/"):
            return response(
                200,
                data={
                    "status": self.status,
                    "outcome": {"media_urls": [{"url": ASSET_URL}]},
                },
            )
        return response(200, content=self.asset)

    def post(self, *_args: Any, **_kwargs: Any) -> Any:
        self.posts += 1
        raise AssertionError("POST reached transport")

    def close(self) -> None:
        pass


class Body:
    def __init__(self, value: bytes):
        self.value = value

    def read(self) -> bytes:
        return self.value


def missing_error(operation: str = "HeadObject") -> ClientError:
    return ClientError(
        {"Error": {"Code": "404"}, "ResponseMetadata": {"HTTPStatusCode": 404}},
        operation,
    )


class FakeB2:
    def __init__(self):
        self.objects: dict[str, bytes] = {}
        self.ops: list[tuple[str, str]] = []
        self.put_kwargs: list[dict[str, Any]] = []
        self.collision: str | None = None
        self.put_error: BaseException | None = None
        self.get_transform: Any = lambda _key, value: value

    def head_object(self, *, Bucket: str, Key: str) -> dict[str, Any]:
        self.ops.append(("HEAD", Key))
        if Key == self.collision:
            return {}
        raise missing_error()

    def put_object(self, **kwargs: Any) -> dict[str, Any]:
        key = kwargs["Key"]
        self.ops.append(("PUT", key))
        self.put_kwargs.append(dict(kwargs))
        if self.put_error is not None:
            raise self.put_error
        self.objects[key] = bytes(kwargs["Body"])
        return {}

    def get_object(self, *, Bucket: str, Key: str) -> dict[str, Any]:
        self.ops.append(("GET", Key))
        return {"Body": Body(self.get_transform(Key, self.objects[Key]))}

    def close(self) -> None:
        pass


def env_all() -> dict[str, str]:
    return {
        "GMI_API_KEY": "offline-provider-secret",
        "B2_KEY_ID": "offline-id",
        "B2_APP_KEY": "offline-app-secret",
        "B2_BUCKET": "offline-bucket",
        "B2_REGION": "eu-central-003",
    }


def repo(**changes: Any) -> r.ResumeRepoState:
    values = {
        "branch": r.REQUIRED_BRANCH,
        "head": REVISION,
        "origin": REVISION,
        "clean": True,
        "source_revision_is_ancestor": True,
    }
    values.update(changes)
    return r.ResumeRepoState(**values)


def dependencies(
    tmp_path: Path,
    *,
    provider: FakeProvider | None = None,
    b2: FakeB2 | None = None,
    repo_state: r.ResumeRepoState | None = None,
):
    provider = provider or FakeProvider()
    b2 = b2 or FakeB2()
    calls = {"provider": 0, "b2": 0}

    def provider_factory(_credentials: Any) -> FakeProvider:
        calls["provider"] += 1
        return provider

    def b2_factory(_credentials: Any) -> FakeB2:
        calls["b2"] += 1
        return b2

    deps = r.ContinuationDependencies(
        repo_state=lambda _revision: repo_state or repo(),
        provider_transport=provider_factory,
        b2_transport=b2_factory,
        local_receipt_root=tmp_path / "receipts",
        completion_root=tmp_path / "completion",
        execution_lock=tmp_path / "state" / "c9.lock",
    )
    return deps, calls, provider, b2


def run_c9(tmp_path: Path, **kwargs: Any):
    deps, calls, provider, b2 = dependencies(
        tmp_path,
        provider=kwargs.pop("provider", None),
        b2=kwargs.pop("b2", None),
        repo_state=kwargs.pop("repo_state", None),
    )
    result = r.continue_funded_b2(
        failure_receipt=r.FUNDED_FAILURE_RECEIPT,
        attempt_lock=r.FUNDED_ATTEMPT_LOCK,
        prior_resume_receipt=r.C9_PRIOR_RESUME_RECEIPT,
        request_id=kwargs.pop("request_id", REQUEST_ID),
        authorization_token=kwargs.pop(
            "authorization_token", r.C9_CONTINUATION_AUTHORIZATION_TOKEN
        ),
        expected_revision=kwargs.pop("expected_revision", REVISION),
        max_additional_cost=kwargs.pop("max_additional_cost", "0.00"),
        env=env_all(),
        dependencies=deps,
        attempt_profile=kwargs.pop("attempt_profile", "funded"),
    )
    assert not kwargs
    return result, deps, calls, provider, b2


def test_prior_resume_receipt_exact_hash_and_mutation_required(tmp_path: Path):
    prior = r.parse_prior_resume_receipt(r.C9_PRIOR_RESUME_RECEIPT)
    assert prior.sha256 == r.C9_PRIOR_RESUME_RECEIPT_SHA256
    copy = tmp_path / "prior.json"
    copy.write_bytes(r.C9_PRIOR_RESUME_RECEIPT.read_bytes() + b" ")
    with pytest.raises(r.SafetyError, match="modified"):
        r.parse_prior_resume_receipt(
            copy, expected_path=copy, expected_sha256=r.C9_PRIOR_RESUME_RECEIPT_SHA256
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("proof_id", "a" * 32, "proof ID"),
        ("provider_request_id", "wrong", "request ID"),
        ("reason_code", "Other", "reason"),
        ("provider_status", "pending", "status"),
    ],
)
def test_prior_identity_and_state_fail(tmp_path: Path, field: str, value: Any, message: str):
    data = json.loads(r.C9_PRIOR_RESUME_RECEIPT.read_text())
    data[field] = value
    raw = json.dumps(data, sort_keys=True).encode()
    path = tmp_path / "prior.json"
    path.write_bytes(raw)
    with pytest.raises(r.SafetyError, match=message):
        r.parse_prior_resume_receipt(
            path, expected_path=path, expected_sha256=hashlib.sha256(raw).hexdigest()
        )


@pytest.mark.parametrize("mutation", ["counter", "writes", "lineage"])
def test_prior_counters_writes_and_lineage_fail(tmp_path: Path, mutation: str):
    data = json.loads(r.C9_PRIOR_RESUME_RECEIPT.read_text())
    if mutation == "counter":
        data["resume_counters"]["b2_puts"] = 0
    elif mutation == "writes":
        data["successfully_written_keys"] = ["some/key"]
    else:
        data["combined_proof_lineage"]["total_provider_posts"] = 2
    raw = json.dumps(data, sort_keys=True).encode()
    path = tmp_path / "prior.json"
    path.write_bytes(raw)
    with pytest.raises(r.SafetyError):
        r.parse_prior_resume_receipt(
            path, expected_path=path, expected_sha256=hashlib.sha256(raw).hexdigest()
        )


def test_original_profile_and_generic_token_are_rejected_before_clients(tmp_path: Path):
    deps, calls, _provider, _b2 = dependencies(tmp_path)
    with pytest.raises(r.SafetyError, match="unavailable"):
        r.continue_funded_b2(
            failure_receipt=r.FUNDED_FAILURE_RECEIPT,
            attempt_lock=r.FUNDED_ATTEMPT_LOCK,
            prior_resume_receipt=r.C9_PRIOR_RESUME_RECEIPT,
            request_id=REQUEST_ID,
            authorization_token=r.C9_CONTINUATION_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
            attempt_profile="original",
        )
    with pytest.raises(r.SafetyError, match="authorization"):
        r.continue_funded_b2(
            failure_receipt=r.FUNDED_FAILURE_RECEIPT,
            attempt_lock=r.FUNDED_ATTEMPT_LOCK,
            prior_resume_receipt=r.C9_PRIOR_RESUME_RECEIPT,
            request_id=REQUEST_ID,
            authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
            attempt_profile="funded",
        )
    assert calls == {"provider": 0, "b2": 0}


@pytest.mark.parametrize(
    "change",
    [
        {"expected_revision": None},
        {"repo_state": repo(clean=False)},
        {"repo_state": repo(origin="a" * 40)},
    ],
)
def test_repository_gates_fail_before_client_and_lock(tmp_path: Path, change: dict[str, Any]):
    deps, calls, _provider, _b2 = dependencies(
        tmp_path, repo_state=change.get("repo_state")
    )
    with pytest.raises(r.SafetyError):
        r.continue_funded_b2(
            failure_receipt=r.FUNDED_FAILURE_RECEIPT,
            attempt_lock=r.FUNDED_ATTEMPT_LOCK,
            prior_resume_receipt=r.C9_PRIOR_RESUME_RECEIPT,
            request_id=REQUEST_ID,
            authorization_token=r.C9_CONTINUATION_AUTHORIZATION_TOKEN,
            expected_revision=change.get("expected_revision", REVISION),
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
            attempt_profile="funded",
        )
    assert calls == {"provider": 0, "b2": 0}
    assert not deps.execution_lock.exists()


def test_success_plain_put_immediate_verification_and_truth_boundary(tmp_path: Path):
    result, deps, calls, provider, b2 = run_c9(tmp_path)
    plan = r.c5.make_key_plan(r.FUNDED_PROOF_ID)
    assert calls == {"provider": 1, "b2": 1}
    assert provider.gets == [f"/requests/{REQUEST_ID}", ASSET_URL]
    assert provider.posts == 0
    assert [op for op, _key in b2.ops[:5]] == ["HEAD"] * 5
    assert b2.ops[5:] == [item for key in plan.ordered for item in (("PUT", key), ("GET", key))]
    assert [kwargs["Key"] for kwargs in b2.put_kwargs] == list(plan.ordered)
    assert all(
        set(kwargs) == {"Bucket", "Key", "Body", "ContentType"}
        for kwargs in b2.put_kwargs
    )
    assert result["continuation_counters"]["generation_posts"] == 0
    assert result["continuation_counters"]["b2_heads"] == 5
    assert result["continuation_counters"]["b2_puts"] == 5
    assert result["continuation_counters"]["b2_gets"] == 5
    assert result["combined_proof_lineage"]["original_provider_posts"] == 1
    assert result["combined_proof_lineage"]["resume_provider_posts"] == 0
    assert result["combined_proof_lineage"]["total_provider_posts"] == 1
    assert result["completeness_status"] == "complete"
    assert result["b2_write_mode"] == r.C9_B2_WRITE_MODE
    assert result["atomic_create_if_absent"] is False
    assert result["local_single_writer_enforced"] is True
    assert result["postwrite_byte_verification"] is True
    assert result["exact_key_preflight"] is True
    assert deps.execution_lock.is_file()
    lock = json.loads(deps.execution_lock.read_text())
    assert lock["provider_post_limit"] == 0 and lock["b2_put_limit"] == 5


def test_pending_and_invalid_png_stop_before_b2(tmp_path: Path):
    provider = FakeProvider(status="processing")
    with pytest.raises(r.SafetyError, match="already-successful"):
        run_c9(tmp_path / "pending", provider=provider)
    assert provider.gets == [f"/requests/{REQUEST_ID}"]
    provider = FakeProvider(asset=b"not-png")
    deps, calls, _provider, _b2 = dependencies(tmp_path / "invalid", provider=provider)
    with pytest.raises(r.SafetyError):
        r.continue_funded_b2(
            failure_receipt=r.FUNDED_FAILURE_RECEIPT,
            attempt_lock=r.FUNDED_ATTEMPT_LOCK,
            prior_resume_receipt=r.C9_PRIOR_RESUME_RECEIPT,
            request_id=REQUEST_ID,
            authorization_token=r.C9_CONTINUATION_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
            attempt_profile="funded",
        )
    assert calls["b2"] == 0


def test_collision_blocks_all_puts_after_five_heads(tmp_path: Path):
    b2 = FakeB2()
    b2.collision = r.c5.make_key_plan(r.FUNDED_PROOF_ID).manifest
    with pytest.raises(r.SafetyError, match="already exists"):
        run_c9(tmp_path, b2=b2)
    assert [op for op, _key in b2.ops] == ["HEAD"] * 5


def test_byte_verification_failure_is_closed_without_redundant_get(tmp_path: Path):
    b2 = FakeB2()
    b2.get_transform = lambda _key, value: value[:-1]
    with pytest.raises(r.SafetyError, match="length mismatch"):
        run_c9(tmp_path, b2=b2)
    assert [op for op, _key in b2.ops].count("PUT") == 1
    assert [op for op, _key in b2.ops].count("GET") == 1


def test_existing_execution_lock_blocks_before_network(tmp_path: Path):
    deps, calls, _provider, _b2 = dependencies(tmp_path)
    deps.execution_lock.parent.mkdir(parents=True)
    deps.execution_lock.write_text("existing\n")
    with pytest.raises(r.SafetyError, match="already exists"):
        r.continue_funded_b2(
            failure_receipt=r.FUNDED_FAILURE_RECEIPT,
            attempt_lock=r.FUNDED_ATTEMPT_LOCK,
            prior_resume_receipt=r.C9_PRIOR_RESUME_RECEIPT,
            request_id=REQUEST_ID,
            authorization_token=r.C9_CONTINUATION_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
            attempt_profile="funded",
        )
    assert calls == {"provider": 0, "b2": 0}
    assert deps.execution_lock.read_text() == "existing\n"


def test_put_error_safe_diagnostic_and_no_reconciliation_operation(tmp_path: Path):
    b2 = FakeB2()
    raw_request_id = "raw-request-id-must-not-appear"
    arbitrary = "credential=secret arbitrary exception message"
    b2.put_error = ClientError(
        {
            "Error": {"Code": "InvalidRequest", "Message": arbitrary},
            "ResponseMetadata": {"HTTPStatusCode": 400, "RequestId": raw_request_id},
        },
        "PutObject",
    )
    with pytest.raises(r.B2CompatibilityError):
        run_c9(tmp_path, b2=b2)
    assert [op for op, _key in b2.ops].count("HEAD") == 5
    assert [op for op, _key in b2.ops].count("PUT") == 1
    assert [op for op, _key in b2.ops].count("GET") == 0
    receipt_text = (
        tmp_path / "receipts" / r.FUNDED_PROOF_ID / "continuation-receipt.json"
    ).read_text()
    receipt = json.loads(receipt_text)
    diagnostic = receipt["b2_failure_diagnostic"]
    assert diagnostic["operation"] == "PutObject"
    assert diagnostic["provider_error_code"] == "InvalidRequest"
    assert diagnostic["http_status"] == 400
    assert diagnostic["request_id_sha256"] == hashlib.sha256(
        raw_request_id.encode()
    ).hexdigest()
    for forbidden in (raw_request_id, arbitrary, "offline-provider-secret", "offline-app-secret"):
        assert forbidden not in receipt_text


def test_real_execution_lock_is_never_created_by_tests():
    assert not r.C9_DEFAULT_EXECUTION_LOCK.exists()
