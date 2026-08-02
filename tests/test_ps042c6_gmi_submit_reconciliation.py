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
SPEC = importlib.util.spec_from_file_location("ps042c6_runner_tests", RUNNER)
assert SPEC and SPEC.loader
r = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = r
SPEC.loader.exec_module(r)
c5 = r.c5
SMOKE = ROOT / "scripts" / "ps042c6_gmi_submit_reconciliation_smoke.py"
SMOKE_SPEC = importlib.util.spec_from_file_location("ps042c6_smoke_tests", SMOKE)
assert SMOKE_SPEC and SMOKE_SPEC.loader
s = importlib.util.module_from_spec(SMOKE_SPEC)
sys.modules[SMOKE_SPEC.name] = s
SMOKE_SPEC.loader.exec_module(s)

LOCK_BYTES = (
    b"authorized_at_utc=2026-07-30T22:04:57Z\n"
    b"branch=ps-042c0/free-render-staging-v1\n"
    b"revision=ca3b2d1e0ba4cea3978b2ffe33ab25dff8acedb8\n"
    b"maximum_cost_usd=0.05\n"
    b"generation_submit_limit=1\n"
)
REVISION = "b" * 40
_PNG: bytes | None = None


def response(
    status: int,
    data: Any = None,
    *,
    content: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    request = httpx.Request("GET", "https://offline.invalid/")
    if content is None:
        return httpx.Response(status, json=data, headers=headers, request=request)
    return httpx.Response(status, content=content, headers=headers, request=request)


def valid_png(size: tuple[int, int] = (c5.WIDTH, c5.HEIGHT)) -> bytes:
    global _PNG
    if size == (c5.WIDTH, c5.HEIGHT) and _PNG is not None:
        return _PNG
    output = io.BytesIO()
    Image.new("RGB", size, (4, 20, 31)).save(output, format="PNG")
    value = output.getvalue()
    if size == (c5.WIDTH, c5.HEIGHT):
        _PNG = value
    return value


def missing_error(key: str) -> ClientError:
    return ClientError(
        {"Error": {"Code": "404"}, "ResponseMetadata": {"HTTPStatusCode": 404}},
        "HeadObject",
    )


class Body:
    def __init__(self, data: bytes):
        self.data = data

    def read(self) -> bytes:
        return self.data


class FakeProvider:
    def __init__(
        self,
        statuses: list[Any] | None = None,
        *,
        asset: bytes | None = None,
        asset_status: int = 200,
    ):
        self.statuses = list(
            statuses
            or [
                {
                    "status": "success",
                    "outcome": {
                        "media_urls": [{"url": "https://assets.invalid/proof.png?sig=secret"}]
                    },
                }
            ]
        )
        self.asset = valid_png() if asset is None else asset
        self.asset_status = asset_status
        self.gets: list[tuple[str, dict[str, Any]]] = []
        self.posts = 0
        self.closed = False

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        self.gets.append((url, kwargs))
        if url.startswith("/requests/"):
            value = self.statuses.pop(0)
            if isinstance(value, httpx.Response):
                return value
            return response(200, value)
        return response(
            self.asset_status,
            content=self.asset,
            headers={"content-type": "image/png"},
        )

    def post(self, _url: str, **_kwargs: Any) -> httpx.Response:
        self.posts += 1
        raise AssertionError("POST reached transport")

    def close(self) -> None:
        self.closed = True


class FakeB2:
    def __init__(self, existing: set[str] | None = None):
        self.existing = set(existing or ())
        self.objects: dict[str, bytes] = {}
        self.ops: list[tuple[str, str]] = []
        self.put_kwargs: list[dict[str, Any]] = []
        self.closed = False

    def head_object(self, *, Bucket: str, Key: str) -> dict:
        self.ops.append(("HEAD", Key))
        if Key in self.existing or Key in self.objects:
            return {}
        raise missing_error(Key)

    def put_object(self, **kwargs: Any) -> dict:
        key = kwargs["Key"]
        self.ops.append(("PUT", key))
        self.put_kwargs.append(kwargs)
        if key in self.existing or key in self.objects:
            raise RuntimeError("conditional collision")
        self.objects[key] = bytes(kwargs["Body"])
        return {}

    def get_object(self, *, Bucket: str, Key: str) -> dict:
        self.ops.append(("GET", Key))
        return {"Body": Body(self.objects[Key])}

    def close(self) -> None:
        self.closed = True


def legacy_receipt(**changes: Any) -> dict[str, Any]:
    value = {
        "complete_proof": False,
        "failed_key": None,
        "network_counters": {
            "asset_download_gets": 0,
            "b2_gets": 0,
            "b2_heads": 5,
            "b2_puts": 0,
            "generation_posts": 1,
            "other_network_methods": 0,
            "status_poll_gets": 0,
        },
        "proof_id": r.ORIGINAL_PROOF_ID,
        "reason_code": "PipelineError",
        "schema": c5.LOCAL_RECEIPT_SCHEMA,
        "status": "incomplete",
        "successfully_written_keys": [],
    }
    value.update(changes)
    return value


def local_inputs(tmp_path: Path, receipt: dict[str, Any] | None = None):
    receipt_path = tmp_path / "failure-receipt.json"
    receipt_path.write_text(json.dumps(receipt or legacy_receipt()))
    lock_path = tmp_path / "attempt.lock"
    lock_path.write_bytes(LOCK_BYTES)
    return receipt_path, lock_path


def env_all() -> dict[str, str]:
    return {
        "GMI_API_KEY": "secret-gmi",
        "B2_KEY_ID": "secret-id",
        "B2_APP_KEY": "secret-app",
        "B2_BUCKET": "proof-bucket",
        "B2_REGION": "us-test-001",
    }


def good_repo(**changes: Any):
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
    provider: FakeProvider | None = None,
    b2: FakeB2 | None = None,
    state: Any = None,
):
    provider = provider or FakeProvider()
    b2 = b2 or FakeB2()
    calls = {"provider": 0, "b2": 0}

    def provider_factory(_credentials):
        calls["provider"] += 1
        return provider

    def b2_factory(_credentials):
        calls["b2"] += 1
        return b2

    deps = r.ResumeDependencies(
        repo_state=lambda _source: state or good_repo(),
        provider_transport=provider_factory,
        b2_transport=b2_factory,
        sleep=lambda _seconds: None,
        local_receipt_root=tmp_path / "resume-receipts",
        completion_root=tmp_path / "completion",
    )
    return deps, calls, provider, b2


def run_resume(
    tmp_path: Path,
    *,
    receipt: dict[str, Any] | None = None,
    provider: FakeProvider | None = None,
    b2: FakeB2 | None = None,
    state: Any = None,
    request_id: str = "request_safe_1",
):
    receipt_path, lock_path = local_inputs(tmp_path, receipt)
    deps, calls, provider, b2 = dependencies(tmp_path, provider, b2, state)
    result = r.resume_existing(
        failure_receipt=receipt_path,
        attempt_lock=lock_path,
        request_id=request_id,
        authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
        expected_revision=REVISION,
        max_additional_cost="0.00",
        env=env_all(),
        dependencies=deps,
    )
    return result, calls, provider, b2, lock_path


@pytest.mark.parametrize(
    ("status", "field"), [(200, "request_id"), (201, "id")]
)
def test_accepted_submit_response(status: int, field: str):
    resp = response(status, {field: "request_safe_1"})
    diagnostic, data, request_id = c5.classify_submit_response(resp)
    assert data and request_id == "request_safe_1"
    assert diagnostic["submit_classification"] == c5.ACCEPTED


@pytest.mark.parametrize("status", [400, 401, 403, 422, 429])
def test_4xx_is_definitive_rejection(status: int):
    diagnostic, _data, request_id = c5.classify_submit_response(
        response(status, {"error": {"code": "bad_request", "message": "rejected"}})
    )
    assert request_id is None
    assert diagnostic["submit_classification"] == c5.DEFINITIVE_PROVIDER_REJECTION


@pytest.mark.parametrize("status", [500, 503])
def test_5xx_is_ambiguous_response(status: int):
    diagnostic, _data, request_id = c5.classify_submit_response(
        response(status, {"error": "upstream"})
    )
    assert request_id is None
    assert diagnostic["submit_classification"] == c5.AMBIGUOUS_PROVIDER_RESPONSE


def test_3xx_is_ambiguous_even_with_request_id():
    diagnostic, _data, request_id = c5.classify_submit_response(
        response(302, {"request_id": "request_safe_1"})
    )
    assert request_id is None
    assert diagnostic["submit_classification"] == c5.AMBIGUOUS_PROVIDER_RESPONSE


def test_2xx_json_without_request_id_is_ambiguous():
    diagnostic, _data, request_id = c5.classify_submit_response(response(200, {"ok": True}))
    assert request_id is None
    assert diagnostic["submit_classification"] == c5.AMBIGUOUS_PROVIDER_RESPONSE


def test_2xx_non_json_is_ambiguous():
    diagnostic, data, request_id = c5.classify_submit_response(
        response(200, content=b"<html>ok</html>", headers={"content-type": "text/html"})
    )
    assert data is None and request_id is None
    assert diagnostic["submit_classification"] == c5.AMBIGUOUS_PROVIDER_RESPONSE


def test_transport_exception_is_ambiguous_and_never_retried():
    class Broken:
        calls = 0

        def post(self, *_args, **_kwargs):
            self.calls += 1
            raise httpx.ReadTimeout("timed out")

        def close(self):
            pass

    broken = Broken()
    counters = c5.NetworkCounters()
    boundary = c5.CountingProviderHTTP(broken, counters)
    payload = {
        "model": c5.MODEL,
        "payload": {
            "prompt": c5.CANONICAL_PROMPT,
            "size": c5.SIZE,
            "output_format": c5.OUTPUT_FORMAT,
            "max_images": 1,
            "sequential_image_generation": c5.SEQUENTIAL_IMAGE_GENERATION,
            "watermark": c5.WATERMARK,
        },
    }
    with pytest.raises(c5.AmbiguousGenerationError):
        boundary.post("/requests", json=payload)
    assert broken.calls == 1 and counters.generation_posts == 1
    assert boundary.submit_classification == c5.AMBIGUOUS_TRANSPORT_OUTCOME


def test_response_hash_keys_truncation_and_redaction():
    message = (
        "Authorization: bearer-secret "
        "https://assets.invalid/x?X-Amz-Credential=credential&X-Amz-Signature=signed "
        + "x" * 500
    )
    body = json.dumps(
        {"z": 1, "error": {"code": "safe.code", "message": message}, "a": 2}
    ).encode()
    diagnostic, _data, _request_id = c5.classify_submit_response(
        response(400, content=body, headers={"content-type": "application/json"})
    )
    assert diagnostic["response_body_sha256"] == hashlib.sha256(body).hexdigest()
    assert diagnostic["top_level_json_keys"] == ["a", "error", "z"]
    safe = diagnostic["safe_provider_error_message"]
    assert len(safe) <= c5.MAX_SAFE_ERROR_TEXT
    assert "bearer-secret" not in safe
    assert "X-Amz-" not in safe and "signed" not in safe
    assert "assets.invalid" not in safe


def test_known_credential_value_is_scrubbed_even_without_a_label():
    body = b'{"error":{"message":"provider echoed opaque-secret-value"}}'
    diagnostic, _data, _request_id = c5.classify_submit_response(
        response(403, content=body, headers={"content-type": "application/json"}),
        {"GMI_API_KEY": "opaque-secret-value"},
    )
    assert "opaque-secret-value" not in json.dumps(diagnostic)


def test_pipeline_error_wrapping_preserves_boundary_classification(tmp_path: Path):
    receipt_root = tmp_path / "c5"
    provider = FakeProvider()

    class Submit400(FakeProvider):
        def post(self, _url: str, **_kwargs: Any):
            self.posts += 1
            return response(400, {"error": {"code": "denied", "message": "no"}})

    provider = Submit400()
    b2 = FakeB2()
    deps = c5.ExecutionDependencies(
        repo_state=lambda: c5.RepoState(
            c5.REQUIRED_BRANCH,
            REVISION,
            REVISION,
            c5.TRUSTED_ANCESTOR_COMMIT,
            True,
        ),
        provider_transport=lambda _credentials: provider,
        b2_transport=lambda _credentials: b2,
        proof_id=lambda: r.ORIGINAL_PROOF_ID,
        sleep=lambda _seconds: None,
        local_receipt_root=receipt_root,
    )
    with pytest.raises(c5.SafetyError):
        c5.execute_proof(
            authorization_token=c5.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=REVISION,
            env=env_all(),
            dependencies=deps,
        )
    failure = json.loads(
        (receipt_root / r.ORIGINAL_PROOF_ID / "failure-receipt.json").read_text()
    )
    assert failure["reason_code"] == "PipelineError"
    assert failure["outer_exception_type"] == "PipelineError"
    assert failure["provider_submit_classification"] == (
        c5.DEFINITIVE_PROVIDER_REJECTION
    )
    assert failure["second_post_forbidden"] is True


def test_legacy_receipt_reconciles_to_manual_console_state(tmp_path: Path):
    receipt, lock = local_inputs(tmp_path)
    result = r.reconcile(receipt, lock)
    assert result["state"] == "NEEDS_PROVIDER_CONSOLE_RECONCILIATION"
    assert result["original_generation_posts"] == 1
    assert result["original_b2_heads"] == 5
    assert result["new_submit_authorized"] is False
    assert result["resume_possible_if_request_id_is_supplied"] is True


@pytest.mark.parametrize(
    "mutation",
    [
        {"schema": "bad"},
        {"proof_id": "UPPER"},
        {"network_counters": {}},
        {"successfully_written_keys": "bad"},
    ],
)
def test_malformed_receipt_rejected(tmp_path: Path, mutation: dict[str, Any]):
    receipt, lock = local_inputs(tmp_path, legacy_receipt(**mutation))
    with pytest.raises(r.SafetyError):
        r.reconcile(receipt, lock)


def test_missing_attempt_lock_rejected(tmp_path: Path):
    receipt, lock = local_inputs(tmp_path)
    lock.unlink()
    with pytest.raises(r.SafetyError, match="lock"):
        r.reconcile(receipt, lock)


def test_modified_attempt_lock_rejected(tmp_path: Path):
    receipt, lock = local_inputs(tmp_path)
    lock.write_bytes(LOCK_BYTES.replace(b"0.05", b"0.050"))
    with pytest.raises(r.SafetyError):
        r.reconcile(receipt, lock)


def attempt_and_lock(tmp_path: Path):
    receipt, lock = local_inputs(tmp_path)
    return r.parse_failure_receipt(receipt), r.parse_attempt_lock(lock)


@pytest.mark.parametrize(
    ("state", "message"),
    [
        (good_repo(branch="main"), "branch"),
        (good_repo(head="a" * 40), "HEAD"),
        (good_repo(clean=False), "clean"),
        (good_repo(source_revision_is_ancestor=False), "ancestor"),
    ],
)
def test_repository_gates_fail_closed(tmp_path: Path, state: Any, message: str):
    attempt, lock = attempt_and_lock(tmp_path)
    with pytest.raises(r.SafetyError, match=message):
        r.validate_resume_gates(
            attempt=attempt,
            lock=lock,
            request_id="request_1",
            authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            repo_state=state,
        )


def test_proof_id_mismatch_rejected(tmp_path: Path):
    receipt, lock = local_inputs(tmp_path, legacy_receipt(proof_id="a" * 32))
    with pytest.raises(r.SafetyError, match="proof-ID"):
        r.reconcile(receipt, lock)


@pytest.mark.parametrize("request_id", ["", ".", "..", "/bad", " bad", "x" * 201])
def test_invalid_resume_request_id_rejected_before_clients(
    tmp_path: Path, request_id: str
):
    receipt, lock = local_inputs(tmp_path)
    deps, calls, _provider, _b2 = dependencies(tmp_path)
    with pytest.raises(r.SafetyError, match="request ID"):
        r.resume_existing(
            failure_receipt=receipt,
            attempt_lock=lock,
            request_id=request_id,
            authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_resume_transport_post_blocked_before_sending():
    provider = FakeProvider()
    counters = r.ResumeCounters()
    boundary = r.ResumeProviderHTTP(provider, "request_1", counters)
    with pytest.raises(r.SafetyError, match="POST"):
        boundary.post("/requests", json={})
    assert provider.posts == 0 and counters.generation_posts == 0


def test_zero_retries_fallbacks_and_preflight():
    assert r.RESUME_GENERATION_POST_LIMIT == 0
    assert r.RESUME_AUTOMATIC_RETRIES == 0
    assert r.RESUME_FALLBACKS == 0
    assert r.RESUME_PREFLIGHT is False


def test_bounded_exact_request_status_gets():
    provider = FakeProvider(statuses=[{"status": "queued"}] * r.MAX_STATUS_GETS)
    counters = r.ResumeCounters()
    boundary = r.ResumeProviderHTTP(provider, "request_1", counters)
    with pytest.raises(r.ResumeIncompleteError):
        r.poll_existing_request(boundary, lambda _seconds: None)
    assert counters.status_poll_gets == r.MAX_STATUS_GETS
    assert {url for url, _kwargs in provider.gets} == {"/requests/request_1"}


@pytest.mark.parametrize("pending", ["queued", "processing"])
def test_pending_timeout_has_no_asset_or_b2(
    tmp_path: Path, pending: str
):
    provider = FakeProvider(statuses=[{"status": pending}] * r.MAX_STATUS_GETS)
    receipt, lock = local_inputs(tmp_path)
    deps, calls, provider, b2 = dependencies(tmp_path, provider=provider)
    with pytest.raises(r.ResumeIncompleteError):
        r.resume_existing(
            failure_receipt=receipt,
            attempt_lock=lock,
            request_id="request_1",
            authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
        )
    assert calls == {"provider": 1, "b2": 0}
    assert not any(not url.startswith("/requests/") for url, _ in provider.gets)
    local = json.loads(
        (tmp_path / "resume-receipts" / r.ORIGINAL_PROOF_ID / "resume-receipt.json").read_text()
    )
    assert local["resume_counters"]["generation_posts"] == 0


@pytest.mark.parametrize("terminal", ["failed", "cancelled"])
def test_terminal_failure_writes_redacted_receipt_without_b2(
    tmp_path: Path, terminal: str
):
    provider = FakeProvider(
        statuses=[
            {
                "status": terminal,
                "error": "Authorization: secret https://signed.invalid/?X-Amz-Signature=x",
            }
        ]
    )
    receipt, lock = local_inputs(tmp_path)
    deps, calls, _provider, _b2 = dependencies(tmp_path, provider=provider)
    with pytest.raises(r.ResumeTerminalError):
        r.resume_existing(
            failure_receipt=receipt,
            attempt_lock=lock,
            request_id="request_1",
            authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
        )
    assert calls["b2"] == 0
    local = json.loads(
        (tmp_path / "resume-receipts" / r.ORIGINAL_PROOF_ID / "resume-receipt.json").read_text()
    )
    assert local["provider_status"] == terminal
    assert "secret" not in json.dumps(local)


def test_unknown_status_fails_closed(tmp_path: Path):
    provider = FakeProvider(statuses=[{"status": "mystery"}])
    with pytest.raises(r.SafetyError, match="unknown"):
        run_resume(tmp_path, provider=provider)


@pytest.mark.parametrize("media_urls", [[], [{"url": "https://a"}, {"url": "https://b"}]])
def test_zero_or_multiple_output_assets_fail(
    tmp_path: Path, media_urls: list[Any]
):
    provider = FakeProvider(
        statuses=[{"status": "success", "outcome": {"media_urls": media_urls}}]
    )
    with pytest.raises(r.SafetyError, match="exactly one"):
        run_resume(tmp_path, provider=provider)


@pytest.mark.parametrize(
    "asset_url",
    [
        "http://assets.invalid/proof.png",
        "https://user:password@assets.invalid/proof.png",
        "https://assets.invalid/proof.png#fragment",
    ],
)
def test_unsafe_asset_url_rejected(tmp_path: Path, asset_url: str):
    provider = FakeProvider(
        statuses=[
            {"status": "success", "outcome": {"media_urls": [{"url": asset_url}]}}
        ]
    )
    with pytest.raises(r.SafetyError, match="unsafe"):
        run_resume(tmp_path, provider=provider)


def test_asset_redirect_rejected(tmp_path: Path):
    provider = FakeProvider(asset_status=302)
    with pytest.raises(r.SafetyError, match="redirect"):
        run_resume(tmp_path, provider=provider)


def test_invalid_png_rejected_before_b2(tmp_path: Path):
    provider = FakeProvider(asset=b"x" * 2048)
    receipt, lock = local_inputs(tmp_path)
    deps, calls, _provider, b2 = dependencies(tmp_path, provider=provider)
    with pytest.raises(r.SafetyError, match="PNG"):
        r.resume_existing(
            failure_receipt=receipt,
            attempt_lock=lock,
            request_id="request_1",
            authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
        )
    assert calls["b2"] == 0 and b2.ops == []


def test_wrong_dimensions_rejected(tmp_path: Path):
    provider = FakeProvider(asset=valid_png((512, 512)))
    with pytest.raises(r.SafetyError, match="dimensions"):
        run_resume(tmp_path, provider=provider)


def test_existing_key_collision_blocks_all_puts(tmp_path: Path):
    plan = c5.make_key_plan(r.ORIGINAL_PROOF_ID)
    b2 = FakeB2(existing={plan.manifest})
    with pytest.raises(r.SafetyError, match="already exists"):
        run_resume(tmp_path, b2=b2)
    assert not any(op == "PUT" for op, _key in b2.ops)


def test_success_exact_keys_receipt_last_lineage_and_complete_rehydration(
    tmp_path: Path,
):
    result, calls, provider, b2, lock = run_resume(tmp_path)
    plan = c5.make_key_plan(r.ORIGINAL_PROOF_ID)
    assert calls == {"provider": 1, "b2": 1}
    assert [key for op, key in b2.ops if op == "HEAD"] == list(plan.ordered)
    assert [key for op, key in b2.ops if op == "PUT"] == list(plan.ordered)
    assert [key for op, key in b2.ops if op == "GET"] == list(plan.ordered)
    assert all(kwargs["IfNoneMatch"] == "*" for kwargs in b2.put_kwargs)
    lineage = result["combined_proof_lineage"]
    assert lineage["original_provider_posts"] == 1
    assert lineage["resume_provider_posts"] == 0
    assert lineage["total_provider_posts"] == 1
    assert result["resume_counters"]["b2_heads"] == 5
    assert result["resume_counters"]["b2_puts"] == 5
    assert result["resume_counters"]["b2_gets"] == 5
    assert result["provider_calls_during_rehydrate"] == 0
    assert provider.posts == 0
    assert [url for url, _kwargs in provider.gets] == [
        "/requests/request_safe_1",
        "https://assets.invalid/proof.png?sig=secret",
    ]
    assert lock.read_bytes() == LOCK_BYTES
    marker = tmp_path / "completion" / r.ORIGINAL_PROOF_ID / "completion-marker.json"
    assert marker.is_file()


def test_offline_self_test_constructs_no_network_client():
    result = r.offline_self_test({})
    assert result["status"] == "PASS"
    assert result["network_client_constructed"] is False
    assert result["resume_provider_post_limit"] == 0


def test_plan_is_original_proof_and_zero_network():
    result = r.fixed_plan({})
    assert result["original_proof_id"] == r.ORIGINAL_PROOF_ID
    assert result["expected_b2_prefix"].endswith(f"{r.ORIGINAL_PROOF_ID}/")
    assert set(result["network_counters"].values()) == {0}
    assert result["maximum_additional_generation_cost_usd"] == "0.00"


def smoke_scope(
    *,
    working: frozenset[str],
    cumulative: frozenset[str],
    branch: str = s.REQUIRED_BRANCH,
    head: str = s.REQUIRED_START_REVISION,
    origin: str = s.REQUIRED_START_REVISION,
    ancestor: bool = True,
) -> dict[str, Any]:
    return s.evaluate_repository_scope(
        branch=branch,
        head=head,
        origin_head=origin,
        start_revision_is_ancestor=ancestor,
        working_tree_changed_paths=working,
        cumulative_source_paths=cumulative,
    )


def test_smoke_original_four_file_dirty_precommit_state_passes():
    result = smoke_scope(
        working=s.EXPECTED_CHANGED_PATHS,
        cumulative=frozenset(),
    )
    assert result["repository_state"] == "precommit"
    assert result["authorized_combined_source_paths"] == sorted(
        s.EXPECTED_CHANGED_PATHS
    )
    assert result["repository_source_scope_exact"] is True


def test_smoke_c6a_two_file_dirty_precommit_state_passes_with_committed_scope():
    working = frozenset(
        {
            str(SMOKE.relative_to(ROOT)),
            str(Path(__file__).relative_to(ROOT)),
        }
    )
    result = smoke_scope(working=working, cumulative=s.EXPECTED_CHANGED_PATHS)
    assert result["repository_state"] == "precommit"
    assert result["working_tree_changed_paths"] == sorted(working)
    assert result["repository_source_scope_exact"] is True


def test_smoke_clean_aligned_postcommit_state_passes():
    result = smoke_scope(
        working=frozenset(),
        cumulative=s.EXPECTED_CHANGED_PATHS,
    )
    assert result["repository_state"] == "postcommit"
    assert result["head_matches_origin"] is True
    assert result["repository_source_scope_exact"] is True


def test_smoke_clean_unpushed_postcommit_state_fails():
    with pytest.raises(RuntimeError, match="origin"):
        smoke_scope(
            working=frozenset(),
            cumulative=s.EXPECTED_CHANGED_PATHS,
            head="a" * 40,
        )


def test_smoke_clean_wrong_branch_postcommit_state_fails():
    with pytest.raises(RuntimeError, match="branch"):
        smoke_scope(
            working=frozenset(),
            cumulative=s.EXPECTED_CHANGED_PATHS,
            branch="main",
        )


def test_smoke_unexpected_dirty_path_fails():
    with pytest.raises(RuntimeError, match="scope"):
        smoke_scope(
            working=frozenset({"README.md"}),
            cumulative=s.EXPECTED_CHANGED_PATHS,
        )


def test_smoke_unexpected_cumulative_committed_path_fails():
    with pytest.raises(RuntimeError, match="scope"):
        smoke_scope(
            working=frozenset(),
            cumulative=s.EXPECTED_CHANGED_PATHS | {"README.md"},
        )


def test_smoke_missing_required_cumulative_c6_path_fails():
    missing = "scripts/ps042c6_gmi_submit_reconciliation.py"
    with pytest.raises(RuntimeError, match="scope"):
        smoke_scope(
            working=frozenset(),
            cumulative=s.EXPECTED_CHANGED_PATHS - {missing},
        )


def test_smoke_status_includes_staged_modified_and_untracked_paths():
    porcelain = "\n".join(
        (
            "M  scripts/staged.py",
            " M scripts/modified.py",
            "?? scripts/untracked.py",
        )
    )
    assert s.changed_paths_from_porcelain(porcelain) == frozenset(
        {
            "scripts/staged.py",
            "scripts/modified.py",
            "scripts/untracked.py",
        }
    )


def test_smoke_constructs_no_provider_or_b2_client(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    lock = tmp_path / "attempt.lock"
    receipt = tmp_path / "failure-receipt.json"
    lock.write_bytes(b"lock")
    receipt.write_bytes(b"receipt")

    class OfflineRunner:
        REQUIRED_CREDENTIALS = frozenset({"GMI_API_KEY"})
        RESUME_GENERATION_POST_LIMIT = 0

        def __init__(self):
            self.calls: list[str] = []

        def credential_presence(self, env: Any) -> dict[str, bool]:
            self.calls.append("credential_presence")
            return {"GMI_API_KEY": "GMI_API_KEY" in env}

        def offline_self_test(self, _env: Any) -> dict[str, Any]:
            self.calls.append("offline_self_test")
            return {"status": "PASS", "network_client_constructed": False}

        def reconcile(self, _receipt: Path, _lock: Path) -> dict[str, Any]:
            self.calls.append("reconcile")
            return {
                "state": "NEEDS_PROVIDER_CONSOLE_RECONCILIATION",
                "network_counters": {
                    "provider_posts": 0,
                    "provider_status_gets": 0,
                    "asset_gets": 0,
                    "b2_heads": 0,
                    "b2_gets": 0,
                    "b2_puts": 0,
                },
            }

    runner = OfflineRunner()
    scope = smoke_scope(
        working=frozenset(),
        cumulative=s.EXPECTED_CHANGED_PATHS,
    )
    monkeypatch.setattr(s, "ATTEMPT_LOCK", lock)
    monkeypatch.setattr(s, "FAILURE_RECEIPT", receipt)
    monkeypatch.setattr(s, "EXPECTED_ATTEMPT_LOCK_SHA256", s.sha256_file(lock))
    monkeypatch.setattr(s, "EXPECTED_FAILURE_RECEIPT_SHA256", s.sha256_file(receipt))
    monkeypatch.setattr(s, "repository_scope", lambda: scope)
    monkeypatch.setattr(s, "git", lambda *_args: "")
    monkeypatch.setattr(s, "load_runner", lambda: runner)

    result = s.run_smoke()

    assert runner.calls == ["credential_presence", "offline_self_test", "reconcile"]
    assert result["provider_client_constructed"] is False
    assert result["b2_client_constructed"] is False
