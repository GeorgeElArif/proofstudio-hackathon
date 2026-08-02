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
SPEC = importlib.util.spec_from_file_location("ps042c7_runner_tests", RUNNER)
assert SPEC and SPEC.loader
r = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = r
SPEC.loader.exec_module(r)
SMOKE = ROOT / "scripts" / "ps042c7_funded_attempt_resume_smoke.py"
SMOKE_SPEC = importlib.util.spec_from_file_location("ps042c7_smoke_tests", SMOKE)
assert SMOKE_SPEC and SMOKE_SPEC.loader
s = importlib.util.module_from_spec(SMOKE_SPEC)
sys.modules[SMOKE_SPEC.name] = s
SMOKE_SPEC.loader.exec_module(s)

FUNDED_LOCK = r.FUNDED_ATTEMPT_LOCK
FUNDED_RECEIPT = r.FUNDED_FAILURE_RECEIPT
ORIGINAL_LOCK = r.DEFAULT_ATTEMPT_LOCK
ORIGINAL_RECEIPT = r.DEFAULT_FAILURE_RECEIPT
REVISION = r.FUNDED_SUBMIT_REVISION
REQUEST_ID = r.FUNDED_AUTHORIZED_REQUEST_ID
_PNG: bytes | None = None


def valid_png() -> bytes:
    global _PNG
    if _PNG is None:
        output = io.BytesIO()
        Image.new("RGB", (r.c5.WIDTH, r.c5.HEIGHT), (7, 19, 31)).save(
            output, format="PNG"
        )
        _PNG = output.getvalue()
    return _PNG


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


class FakeProvider:
    def __init__(
        self,
        *,
        status: dict[str, Any] | None = None,
        asset_status: int = 200,
        asset: bytes | None = None,
        asset_headers: dict[str, str] | None = None,
    ):
        self.status = status or {
            "status": "success",
            "outcome": {
                "media_urls": [
                    {"url": "https://assets.invalid/proof.png?sig=never-record-me"}
                ]
            },
        }
        self.asset_status = asset_status
        self.asset = valid_png() if asset is None else asset
        self.asset_headers = asset_headers or {"content-type": "image/png"}
        self.gets: list[tuple[str, dict[str, Any]]] = []
        self.posts = 0

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        self.gets.append((url, kwargs))
        if url.startswith("/requests/"):
            return response(200, self.status)
        return response(
            self.asset_status,
            content=self.asset,
            headers=self.asset_headers,
        )

    def post(self, *_args: Any, **_kwargs: Any) -> httpx.Response:
        self.posts += 1
        raise AssertionError("provider POST reached transport")

    def close(self) -> None:
        pass


class Body:
    def __init__(self, value: bytes):
        self.value = value

    def read(self) -> bytes:
        return self.value


class FakeB2:
    def __init__(self):
        self.objects: dict[str, bytes] = {}
        self.ops: list[tuple[str, str]] = []
        self.put_kwargs: list[dict[str, Any]] = []

    def head_object(self, *, Bucket: str, Key: str) -> dict[str, Any]:
        self.ops.append(("HEAD", Key))
        if Key in self.objects:
            return {}
        raise ClientError(
            {"Error": {"Code": "404"}, "ResponseMetadata": {"HTTPStatusCode": 404}},
            "HeadObject",
        )

    def put_object(self, **kwargs: Any) -> dict[str, Any]:
        key = kwargs["Key"]
        self.ops.append(("PUT", key))
        self.put_kwargs.append(kwargs)
        self.objects[key] = bytes(kwargs["Body"])
        return {}

    def get_object(self, *, Bucket: str, Key: str) -> dict[str, Any]:
        self.ops.append(("GET", Key))
        return {"Body": Body(self.objects[Key])}

    def close(self) -> None:
        pass


def env_all() -> dict[str, str]:
    return {
        "GMI_API_KEY": "offline-secret",
        "B2_KEY_ID": "offline-id",
        "B2_APP_KEY": "offline-app",
        "B2_BUCKET": "offline-bucket",
        "B2_REGION": "offline-region",
    }


def good_repo(**changes: Any) -> r.ResumeRepoState:
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

    deps = r.ResumeDependencies(
        repo_state=lambda _revision: good_repo(),
        provider_transport=provider_factory,
        b2_transport=b2_factory,
        sleep=lambda _seconds: None,
        local_receipt_root=tmp_path / "resume-receipts",
        completion_root=tmp_path / "completion",
    )
    return deps, calls, provider, b2


def run_funded(
    tmp_path: Path,
    *,
    provider: FakeProvider | None = None,
    b2: FakeB2 | None = None,
):
    deps, calls, provider, b2 = dependencies(tmp_path, provider, b2)
    result = r.resume_existing(
        failure_receipt=FUNDED_RECEIPT,
        attempt_lock=FUNDED_LOCK,
        request_id=REQUEST_ID,
        authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
        expected_revision=REVISION,
        max_additional_cost="0.00",
        env=env_all(),
        dependencies=deps,
        attempt_profile="funded",
    )
    return result, calls, provider, b2


def copied_inputs(tmp_path: Path, receipt: Path, lock: Path) -> tuple[Path, Path]:
    receipt_copy = tmp_path / "failure-receipt.json"
    lock_copy = tmp_path / "attempt.lock"
    receipt_copy.write_bytes(receipt.read_bytes())
    lock_copy.write_bytes(lock.read_bytes())
    return receipt_copy, lock_copy


def test_profiles_are_exactly_the_two_immutable_profiles():
    assert set(r.ATTEMPT_PROFILES) == {"original", "funded"}
    assert r.ORIGINAL_AMBIGUOUS_ATTEMPT.name == "ORIGINAL_AMBIGUOUS_ATTEMPT"
    assert r.FUNDED_ACCEPTED_ATTEMPT.name == "FUNDED_ACCEPTED_ATTEMPT"
    assert len(r.AttemptProfile.__dataclass_fields__) == 10


def test_original_profile_still_reconciles_strictly():
    result = r.reconcile(ORIGINAL_RECEIPT, ORIGINAL_LOCK, "original")
    assert result["state"] == "NEEDS_PROVIDER_CONSOLE_RECONCILIATION"
    assert result["proof_id"] == r.ORIGINAL_PROOF_ID
    assert result["original_generation_posts"] == 1


def test_funded_profile_reconciles_to_required_state_and_facts():
    result = r.reconcile(FUNDED_RECEIPT, FUNDED_LOCK, "funded")
    assert result["state"] == "READY_TO_RESUME_EXISTING_SUCCESSFUL_REQUEST"
    assert result["proof_id"] == r.FUNDED_PROOF_ID
    assert result["authorized_request_id"] == REQUEST_ID
    assert result["original_generation_posts"] == 1
    assert result["original_status_poll_gets"] == 1
    assert result["original_asset_download_gets"] == 1
    assert result["original_b2_heads"] == 5
    assert result["original_b2_gets"] == 0
    assert result["original_b2_puts"] == 0
    assert result["new_submit_authorized"] is False
    assert result["resume_provider_post_limit"] == 0
    assert result["maximum_additional_generation_cost_usd"] == "0.00"
    assert set(result["network_counters"].values()) == {0}


@pytest.mark.parametrize(
    ("receipt", "lock", "profile"),
    [
        (FUNDED_RECEIPT, FUNDED_LOCK, "original"),
        (ORIGINAL_RECEIPT, ORIGINAL_LOCK, "funded"),
        (FUNDED_RECEIPT, ORIGINAL_LOCK, "funded"),
        (ORIGINAL_RECEIPT, FUNDED_LOCK, "original"),
    ],
)
def test_wrong_profile_and_cross_profile_pairings_fail(
    receipt: Path, lock: Path, profile: str
):
    with pytest.raises(r.SafetyError):
        r.reconcile(receipt, lock, profile)


def test_modified_lock_and_receipt_fail_hash_validation(tmp_path: Path):
    receipt, lock = copied_inputs(tmp_path, FUNDED_RECEIPT, FUNDED_LOCK)
    lock.write_bytes(lock.read_bytes() + b"\n")
    with pytest.raises(r.SafetyError):
        r.reconcile(receipt, lock, "funded")
    receipt, lock = copied_inputs(tmp_path, FUNDED_RECEIPT, FUNDED_LOCK)
    receipt.write_bytes(receipt.read_bytes() + b" ")
    with pytest.raises(r.SafetyError, match="receipt"):
        r.reconcile(receipt, lock, "funded")


def test_funded_six_field_lock_only_accepted_for_funded_profile():
    lock = r.parse_attempt_lock(FUNDED_LOCK, "funded")
    assert lock.expected_cost_usd == r.Decimal("0.035")
    with pytest.raises(r.SafetyError, match="field set"):
        r.parse_attempt_lock(FUNDED_LOCK, "original")


@pytest.mark.parametrize(
    "mutation",
    [
        lambda raw: raw + b"extra=value\n",
        lambda raw: raw.replace(b"expected_cost_usd=0.035\n", b""),
        lambda raw: raw.replace(b"expected_cost_usd=0.035", b"expected_cost_usd=0.036"),
        lambda raw: raw.replace(REVISION.encode(), ("a" * 40).encode()),
    ],
)
def test_extra_missing_wrong_cost_or_wrong_revision_lock_fails(
    tmp_path: Path, mutation: Any
):
    lock = tmp_path / "attempt.lock"
    lock.write_bytes(mutation(FUNDED_LOCK.read_bytes()))
    with pytest.raises(r.SafetyError):
        r.parse_attempt_lock(lock, "funded")


def test_wrong_proof_id_fails(tmp_path: Path):
    receipt, lock = copied_inputs(tmp_path, FUNDED_RECEIPT, FUNDED_LOCK)
    value = json.loads(receipt.read_text())
    value["proof_id"] = "a" * 32
    receipt.write_text(json.dumps(value))
    with pytest.raises(r.SafetyError, match="proof-ID"):
        r.reconcile(receipt, lock, "funded")


@pytest.mark.parametrize("request_id", [None, "wrong-request-id"])
def test_request_id_is_required_and_must_equal_funded_authorization(
    tmp_path: Path, request_id: str | None
):
    deps, calls, _provider, _b2 = dependencies(tmp_path)
    with pytest.raises(r.SafetyError, match="request ID"):
        r.resume_existing(
            failure_receipt=FUNDED_RECEIPT,
            attempt_lock=FUNDED_LOCK,
            request_id=request_id,
            authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
            attempt_profile="funded",
        )
    assert calls == {"provider": 0, "b2": 0}


def test_cli_requires_explicit_attempt_profile():
    with pytest.raises(SystemExit) as exc:
        r.build_parser().parse_args(["--plan"])
    assert exc.value.code == 2


def test_provider_post_is_blocked_before_transport_invocation():
    provider = FakeProvider()
    counters = r.ResumeCounters()
    boundary = r.ResumeProviderHTTP(provider, REQUEST_ID, counters)
    with pytest.raises(r.SafetyError, match="POST"):
        boundary.post("/requests", json={})
    assert provider.posts == 0
    assert counters.generation_posts == 0


def test_success_uses_one_exact_status_get_and_one_asset_get(tmp_path: Path):
    result, calls, provider, _b2 = run_funded(tmp_path)
    assert calls == {"provider": 1, "b2": 1}
    assert [url for url, _kwargs in provider.gets] == [
        f"/requests/{REQUEST_ID}",
        "https://assets.invalid/proof.png?sig=never-record-me",
    ]
    assert "/requests" not in [url for url, _kwargs in provider.gets]
    assert all(kwargs["follow_redirects"] is False for _url, kwargs in provider.gets)
    assert result["resume_counters"]["generation_posts"] == 0
    assert result["resume_counters"]["status_poll_gets"] == 1
    assert result["resume_counters"]["asset_download_gets"] == 1


def test_non_200_asset_response_writes_safe_diagnostic_without_b2(tmp_path: Path):
    body = b"upstream denied signed request"
    provider = FakeProvider(
        asset_status=403,
        asset=body,
        asset_headers={"content-type": "text/plain"},
    )
    deps, calls, _provider, b2 = dependencies(tmp_path, provider)
    with pytest.raises(r.AssetDownloadError):
        r.resume_existing(
            failure_receipt=FUNDED_RECEIPT,
            attempt_lock=FUNDED_LOCK,
            request_id=REQUEST_ID,
            authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
            attempt_profile="funded",
        )
    local = json.loads(
        (tmp_path / "resume-receipts" / r.FUNDED_PROOF_ID / "resume-receipt.json").read_text()
    )
    diagnostic = local["asset_download_diagnostic"]
    assert diagnostic == {
        "http_status": 403,
        "content_type": "text/plain",
        "byte_length": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest(),
    }
    assert calls["b2"] == 0 and b2.ops == []


def test_redirect_diagnostic_redacts_signed_url_body_query_and_path(tmp_path: Path):
    signed = "https://cdn.invalid/private/proof.png?token=super-secret&sig=abc"
    body = b"redirect body must not be stored"
    provider = FakeProvider(
        asset_status=302,
        asset=body,
        asset_headers={"content-type": "text/html", "location": signed},
    )
    deps, calls, _provider, _b2 = dependencies(tmp_path, provider)
    with pytest.raises(r.AssetDownloadError, match="redirect"):
        r.resume_existing(
            failure_receipt=FUNDED_RECEIPT,
            attempt_lock=FUNDED_LOCK,
            request_id=REQUEST_ID,
            authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
            attempt_profile="funded",
        )
    receipt_text = (
        tmp_path / "resume-receipts" / r.FUNDED_PROOF_ID / "resume-receipt.json"
    ).read_text()
    diagnostic = json.loads(receipt_text)["asset_download_diagnostic"]
    assert diagnostic["http_status"] == 302
    assert diagnostic["redirect_location_host"] == "cdn.invalid"
    assert diagnostic["redirect_location_path_sha256"] == hashlib.sha256(
        b"/private/proof.png"
    ).hexdigest()
    for forbidden in (signed, "super-secret", "sig=abc", "/private/proof.png", body.decode()):
        assert forbidden not in receipt_text
    assert calls["b2"] == 0


def test_invalid_png_blocks_b2_construction_and_put(tmp_path: Path):
    provider = FakeProvider(asset=b"not-a-png" * 300)
    deps, calls, _provider, b2 = dependencies(tmp_path, provider)
    with pytest.raises(r.SafetyError, match="PNG"):
        r.resume_existing(
            failure_receipt=FUNDED_RECEIPT,
            attempt_lock=FUNDED_LOCK,
            request_id=REQUEST_ID,
            authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
            expected_revision=REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
            attempt_profile="funded",
        )
    assert calls["b2"] == 0
    assert not any(op == "PUT" for op, _key in b2.ops)


def test_funded_success_preserves_post_lineage_exact_keys_and_receipt_last(
    tmp_path: Path,
):
    result, _calls, provider, b2 = run_funded(tmp_path)
    plan = r.c5.make_key_plan(r.FUNDED_PROOF_ID)
    assert [key for op, key in b2.ops if op == "HEAD"] == list(plan.ordered)
    assert [key for op, key in b2.ops if op == "PUT"] == list(plan.ordered)
    assert [key for op, key in b2.ops if op == "GET"] == list(plan.ordered)
    assert [key for op, key in b2.ops if op == "PUT"][-1] == plan.receipt
    assert all(kwargs["IfNoneMatch"] == "*" for kwargs in b2.put_kwargs)
    lineage = result["combined_proof_lineage"]
    assert lineage["original_provider_posts"] == 1
    assert lineage["resume_provider_posts"] == 0
    assert lineage["total_provider_posts"] == 1
    assert lineage["original_submit_revision"] == REVISION
    assert provider.posts == 0


def test_c7_smoke_is_offline_and_exact_scope(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        s,
        "repository_scope",
        lambda: {
            "branch": s.REQUIRED_BRANCH,
            "head": s.REQUIRED_START_REVISION,
            "origin_head": s.REQUIRED_START_REVISION,
            "changed_paths": sorted(s.EXPECTED_CHANGED_PATHS),
            "repository_source_scope_exact": True,
        },
    )
    monkeypatch.setattr(s, "git", lambda *_args: "")
    result = s.run_smoke()
    assert result["provider_client_constructed"] is False
    assert result["b2_client_constructed"] is False
    assert result["network_counters"] == s.ZERO_NETWORK_COUNTERS
    assert result["repository_source_scope_exact"] is True
