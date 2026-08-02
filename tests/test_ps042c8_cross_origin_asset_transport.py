from __future__ import annotations

import hashlib
import importlib.util
import json
import logging
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "ps042c6_gmi_submit_reconciliation.py"
SPEC = importlib.util.spec_from_file_location("ps042c8_runner_tests", RUNNER)
assert SPEC and SPEC.loader
r = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = r
SPEC.loader.exec_module(r)
SMOKE = ROOT / "scripts" / "ps042c8_cross_origin_asset_transport_smoke.py"
SMOKE_SPEC = importlib.util.spec_from_file_location("ps042c8_smoke_tests", SMOKE)
assert SMOKE_SPEC and SMOKE_SPEC.loader
s = importlib.util.module_from_spec(SMOKE_SPEC)
sys.modules[SMOKE_SPEC.name] = s
SMOKE_SPEC.loader.exec_module(s)

REQUEST_ID = r.FUNDED_AUTHORIZED_REQUEST_ID
SIGNED_QUERY = "X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=private%2Fvalue&token=opaque"
ASSET_URL = f"https://storage.googleapis.com/proof-bucket/proof.png?{SIGNED_QUERY}"


class HTTPXFactory:
    def __init__(
        self,
        status_handler: Any | None = None,
        asset_handler: Any | None = None,
    ):
        self.configs: list[dict[str, Any]] = []
        self.requests: list[list[httpx.Request]] = [[], []]
        self.handlers = [status_handler, asset_handler]

    def __call__(self, **kwargs: Any) -> httpx.Client:
        index = len(self.configs)
        self.configs.append(dict(kwargs))

        def handler(request: httpx.Request) -> httpx.Response:
            self.requests[index].append(request)
            custom = self.handlers[index]
            if custom is not None:
                return custom(request)
            return httpx.Response(200, json={"status": "ok"})

        return httpx.Client(transport=httpx.MockTransport(handler), **kwargs)


def split(factory: HTTPXFactory | None = None):
    factory = factory or HTTPXFactory()
    return (
        r.SplitOriginProviderTransport(
            {"GMI_API_KEY": "gmi-bearer-value"}, client_factory=factory
        ),
        factory,
    )


def env_all() -> dict[str, str]:
    return {
        "GMI_API_KEY": "gmi-bearer-value",
        "B2_KEY_ID": "offline-id",
        "B2_APP_KEY": "offline-app",
        "B2_BUCKET": "offline-bucket",
        "B2_REGION": "offline-region",
    }


def good_repo() -> r.ResumeRepoState:
    return r.ResumeRepoState(
        branch=r.REQUIRED_BRANCH,
        head=r.FUNDED_SUBMIT_REVISION,
        origin=r.FUNDED_SUBMIT_REVISION,
        clean=True,
        source_revision_is_ancestor=True,
    )


def test_default_transport_is_split_and_clients_have_strict_configuration():
    transport = r._default_provider_transport({"GMI_API_KEY": "gmi-bearer-value"})
    try:
        assert isinstance(transport, r.SplitOriginProviderTransport)
        assert transport._status_client is not transport._asset_client
        assert str(transport._status_client.base_url) == r.GMI_STATUS_BASE_URL + "/"
        assert str(transport._asset_client.base_url) == ""
        status = transport._status_client.build_request(
            "GET", f"/requests/{REQUEST_ID}"
        )
        asset = transport._asset_client.build_request("GET", ASSET_URL)
        assert status.headers["authorization"] == "Bearer gmi-bearer-value"
        assert "authorization" not in asset.headers
    finally:
        transport.close()


def test_status_and_asset_route_to_distinct_clients_with_query_preserved():
    transport, factory = split()
    try:
        transport.get(f"/requests/{REQUEST_ID}", follow_redirects=False)
        transport.get(ASSET_URL, follow_redirects=False)
    finally:
        transport.close()
    assert len(factory.requests[0]) == 1
    assert len(factory.requests[1]) == 1
    status_request = factory.requests[0][0]
    asset_request = factory.requests[1][0]
    assert status_request.headers["authorization"] == "Bearer gmi-bearer-value"
    assert "authorization" not in asset_request.headers
    assert asset_request.url.query.decode() == SIGNED_QUERY
    assert "base_url" not in factory.configs[1]
    assert factory.configs[0]["follow_redirects"] is False
    assert factory.configs[1]["follow_redirects"] is False


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/proof.png?token=opaque",
        "http://storage.googleapis.com/proof.png?token=opaque",
        "https://storage.googleapis.com:444/proof.png?token=opaque",
        "https://user@storage.googleapis.com/proof.png?token=opaque",
        "https://user:password@storage.googleapis.com/proof.png?token=opaque",
        "https://storage.googleapis.com/proof.png?token=opaque#fragment",
        "https://storage.googleapis.com",
        "/requests/arbitrary/extra",
        "/arbitrary",
        "relative/path",
        "https://console.gmicloud.ai/api/v1/ie/requestqueue/apikey/requests/id",
    ],
)
def test_unapproved_relative_and_absolute_urls_fail_before_transport(url: str):
    transport, factory = split()
    try:
        with pytest.raises(r.SafetyError, match="target"):
            transport.get(url, follow_redirects=False)
        assert factory.requests == [[], []]
    finally:
        transport.close()


def test_explicit_443_asset_port_is_allowed_and_anonymous():
    transport, factory = split()
    try:
        transport.get(
            "https://storage.googleapis.com:443/bucket/proof.png?signature=opaque",
            follow_redirects=False,
        )
        assert factory.requests[0] == []
        assert len(factory.requests[1]) == 1
        assert "authorization" not in factory.requests[1][0].headers
    finally:
        transport.close()


def test_redirect_override_and_asset_authorization_fail_before_transport():
    transport, factory = split()
    try:
        with pytest.raises(r.SafetyError, match="redirects"):
            transport.get(ASSET_URL, follow_redirects=True)
        with pytest.raises(r.SafetyError, match="options"):
            transport.get(
                ASSET_URL,
                headers={"Authorization": "Bearer forbidden"},
                follow_redirects=False,
            )
        assert factory.requests == [[], []]
    finally:
        transport.close()


def test_status_never_reaches_asset_and_asset_never_reaches_status():
    def status_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "console.gmicloud.ai"
        return httpx.Response(200, json={"status": "success"})

    def asset_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "storage.googleapis.com"
        return httpx.Response(200, content=b"asset")

    transport, factory = split(HTTPXFactory(status_handler, asset_handler))
    try:
        transport.get(f"/requests/{REQUEST_ID}", follow_redirects=False)
        transport.get(ASSET_URL, follow_redirects=False)
        assert len(factory.requests[0]) == len(factory.requests[1]) == 1
    finally:
        transport.close()


def test_second_asset_get_remains_blocked_before_send():
    transport, factory = split()
    boundary = r.ResumeProviderHTTP(transport, REQUEST_ID, r.ResumeCounters())
    boundary.download_asset(ASSET_URL)
    with pytest.raises(r.SafetyError, match="second asset GET"):
        boundary.download_asset(ASSET_URL)
    boundary.close()
    assert len(factory.requests[1]) == 1


def test_provider_post_remains_structurally_unavailable():
    transport, factory = split()
    boundary = r.ResumeProviderHTTP(transport, REQUEST_ID, r.ResumeCounters())
    with pytest.raises(r.SafetyError, match="POST"):
        boundary.post("/requests")
    boundary.close()
    assert factory.requests == [[], []]


class ProbeClient:
    def __init__(self):
        self.close_calls = 0

    def get(self, _url: str, **_kwargs: Any) -> httpx.Response:
        return httpx.Response(200, request=httpx.Request("GET", "https://offline.invalid"))

    def close(self) -> None:
        self.close_calls += 1


def test_both_clients_close_exactly_once_even_if_close_is_repeated():
    clients = [ProbeClient(), ProbeClient()]

    def factory(**_kwargs: Any) -> ProbeClient:
        return clients.pop(0)

    status, asset = clients
    transport = r.SplitOriginProviderTransport(
        {"GMI_API_KEY": "gmi-bearer-value"}, client_factory=factory
    )
    transport.close()
    transport.close()
    assert status.close_calls == 1
    assert asset.close_calls == 1


def test_partial_construction_failure_closes_authenticated_client_once():
    status = ProbeClient()
    calls = 0

    def factory(**_kwargs: Any) -> ProbeClient:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("anonymous construction failed")
        return status

    with pytest.raises(RuntimeError, match="anonymous construction"):
        r.SplitOriginProviderTransport(
            {"GMI_API_KEY": "gmi-bearer-value"}, client_factory=factory
        )
    assert status.close_calls == 1


def test_non_200_asset_diagnostic_is_safe_and_query_absent(caplog: pytest.LogCaptureFixture):
    body = b"private response body"

    def asset_handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            302,
            content=body,
            headers={
                "content-type": "text/html; charset=utf-8",
                "location": "https://elsewhere.invalid/private/path?secret=query",
            },
        )

    transport, _factory = split(HTTPXFactory(asset_handler=asset_handler))
    boundary = r.ResumeProviderHTTP(transport, REQUEST_ID, r.ResumeCounters())
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(r.AssetDownloadError) as raised:
            boundary.download_asset(ASSET_URL)
    boundary.close()
    diagnostic = raised.value.diagnostic
    assert diagnostic == {
        "http_status": 302,
        "content_type": "text/html",
        "byte_length": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "redirect_location_host": "elsewhere.invalid",
        "redirect_location_path_sha256": hashlib.sha256(b"/private/path").hexdigest(),
    }
    rendered = json.dumps(diagnostic) + str(raised.value) + caplog.text
    for forbidden in (
        ASSET_URL,
        SIGNED_QUERY,
        "gmi-bearer-value",
        "Bearer gmi-bearer-value",
        "secret=query",
        body.decode(),
    ):
        assert forbidden not in rendered


def test_failed_asset_writes_only_redacted_receipt_and_never_constructs_b2(
    tmp_path: Path,
):
    def status_handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "status": "success",
                "outcome": {"media_urls": [{"url": ASSET_URL}]},
            },
        )

    def asset_handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, content=b"sensitive body", headers={"content-type": "text/plain"})

    factory = HTTPXFactory(status_handler, asset_handler)
    b2_calls = 0

    def forbidden_b2(_credentials: Any) -> Any:
        nonlocal b2_calls
        b2_calls += 1
        raise AssertionError("B2 constructed before valid PNG")

    deps = r.ResumeDependencies(
        repo_state=lambda _revision: good_repo(),
        provider_transport=lambda credentials: r.SplitOriginProviderTransport(
            credentials, client_factory=factory
        ),
        b2_transport=forbidden_b2,
        sleep=lambda _seconds: None,
        local_receipt_root=tmp_path / "receipts",
        completion_root=tmp_path / "completion",
    )
    with pytest.raises(r.AssetDownloadError):
        r.resume_existing(
            failure_receipt=r.FUNDED_FAILURE_RECEIPT,
            attempt_lock=r.FUNDED_ATTEMPT_LOCK,
            request_id=REQUEST_ID,
            authorization_token=r.RESUME_AUTHORIZATION_TOKEN,
            expected_revision=r.FUNDED_SUBMIT_REVISION,
            max_additional_cost="0.00",
            env=env_all(),
            dependencies=deps,
            attempt_profile="funded",
        )
    receipt = (
        tmp_path / "receipts" / r.FUNDED_PROOF_ID / "resume-receipt.json"
    ).read_text()
    assert b2_calls == 0
    for forbidden in (
        ASSET_URL,
        SIGNED_QUERY,
        "gmi-bearer-value",
        "Bearer gmi-bearer-value",
        "sensitive body",
    ):
        assert forbidden not in receipt


def test_existing_request_id_validation_and_funded_reconciliation_are_unchanged():
    assert r.REQUEST_ID_PATTERN.fullmatch(REQUEST_ID)
    assert r.REQUEST_ID_PATTERN.fullmatch("/bad") is None
    result = r.reconcile(r.FUNDED_FAILURE_RECEIPT, r.FUNDED_ATTEMPT_LOCK, "funded")
    assert result["state"] == "READY_TO_RESUME_EXISTING_SUCCESSFUL_REQUEST"
    assert result["authorized_request_id"] == REQUEST_ID
    assert result["resume_provider_post_limit"] == 0
    assert result["maximum_additional_generation_cost_usd"] == "0.00"


def test_c8_smoke_is_offline_and_exact_scope():
    result = s.run_smoke()
    assert result["external_client_sends"] == 0
    assert result["network_counters"] == s.ZERO_NETWORK_COUNTERS
    assert result["status_authorization_present"] is True
    assert result["asset_authorization_absent"] is True
    assert result["split_client_boundary"] is True
    assert result["redirects_disabled"] is True
    assert result["changed_paths"] == sorted(s.EXPECTED_CHANGED_PATHS)
