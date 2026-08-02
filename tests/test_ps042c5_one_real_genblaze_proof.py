from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest
from botocore.exceptions import ClientError
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "ps042c5_one_real_genblaze_proof.py"
SMOKE = ROOT / "scripts" / "ps042c5_one_real_genblaze_proof_smoke.py"
SPEC = importlib.util.spec_from_file_location("ps042c5_runner", RUNNER)
assert SPEC and SPEC.loader
r = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = r
SPEC.loader.exec_module(r)
SMOKE_SPEC = importlib.util.spec_from_file_location("ps042c5_smoke", SMOKE)
assert SMOKE_SPEC and SMOKE_SPEC.loader
s = importlib.util.module_from_spec(SMOKE_SPEC)
sys.modules[SMOKE_SPEC.name] = s
SMOKE_SPEC.loader.exec_module(s)

AUTHORIZED_REVISION = "53d4870b8e8dc0ffd916e8c0f7ee77172112c8df"


def response(status: int, data: Any = None, content: bytes | None = None, headers=None):
    request = httpx.Request("GET", "https://offline.invalid/")
    if content is None:
        return httpx.Response(status, json=data, headers=headers, request=request)
    return httpx.Response(status, content=content, headers=headers, request=request)


class FakeProvider:
    def __init__(
        self,
        *,
        submit_data=None,
        outcome=None,
        asset_bytes=None,
        post_error: Exception | None = None,
    ):
        self.submit_data = submit_data if submit_data is not None else {"request_id": "req_safe_1"}
        self.outcome = outcome if outcome is not None else {
            "media_urls": [{"url": "https://assets.invalid/proof.png"}]
        }
        self.asset_bytes = asset_bytes if asset_bytes is not None else valid_png()
        self.post_error = post_error
        self.posts = 0
        self.gets: list[str] = []
        self.closed = False

    def post(self, url: str, **kwargs):
        self.posts += 1
        if self.post_error:
            raise self.post_error
        return response(200, self.submit_data)

    def get(self, url: str, **kwargs):
        self.gets.append(url)
        if url.startswith("/requests/"):
            return response(200, {"status": "success", "outcome": self.outcome})
        return response(200, content=self.asset_bytes, headers={"content-type": "image/png"})

    def close(self):
        self.closed = True


def missing_error(key: str) -> ClientError:
    return ClientError(
        {"Error": {"Code": "404"}, "ResponseMetadata": {"HTTPStatusCode": 404}},
        "HeadObject",
    )


class FakeBody:
    def __init__(self, data: bytes):
        self.data = data

    def read(self):
        return self.data


class FakeB2:
    def __init__(
        self,
        *,
        existing: set[str] | None = None,
        fail_put_key: str | None = None,
        mutate_get: dict[str, bytes] | None = None,
    ):
        self.existing = set(existing or ())
        self.fail_put_key = fail_put_key
        self.mutate_get = mutate_get or {}
        self.objects: dict[str, bytes] = {}
        self.ops: list[tuple[str, str]] = []
        self.closed = False

    def head_object(self, *, Bucket: str, Key: str):
        self.ops.append(("HEAD", Key))
        if Key in self.existing or Key in self.objects:
            return {}
        raise missing_error(Key)

    def put_object(self, *, Bucket: str, Key: str, Body: bytes, ContentType: str):
        self.ops.append(("PUT", Key))
        if Key == self.fail_put_key:
            raise RuntimeError("fake-secret-that-must-not-escape")
        self.objects[Key] = bytes(Body)
        return {}

    def get_object(self, *, Bucket: str, Key: str):
        self.ops.append(("GET", Key))
        return {"Body": FakeBody(self.mutate_get.get(Key, self.objects[Key]))}

    def close(self):
        self.closed = True


_PNG: bytes | None = None


def valid_png() -> bytes:
    global _PNG
    if _PNG is None:
        out = io.BytesIO()
        Image.new("RGB", (r.WIDTH, r.HEIGHT), (4, 20, 31)).save(out, format="PNG")
        _PNG = out.getvalue()
    return _PNG


def env_all() -> dict[str, str]:
    return {
        "GMI_API_KEY": "test-gmi-value",
        "B2_KEY_ID": "test-b2-id",
        "B2_APP_KEY": "test-b2-app",
        "B2_BUCKET": "proof-bucket",
        "B2_REGION": "us-test-001",
    }


def good_state(**changes) -> Any:
    values = dict(
        branch=r.REQUIRED_BRANCH,
        head=AUTHORIZED_REVISION,
        origin=AUTHORIZED_REVISION,
        trusted_ancestor_merge_base=r.TRUSTED_ANCESTOR_COMMIT,
        clean=True,
    )
    values.update(changes)
    return r.RepoState(**values)


def deps(tmp_path, provider=None, b2=None, state=None, factories=None):
    provider = provider or FakeProvider()
    b2 = b2 or FakeB2()
    calls = factories if factories is not None else {"provider": 0, "b2": 0}

    def provider_factory(_credentials):
        calls["provider"] += 1
        return provider

    def b2_factory(_credentials):
        calls["b2"] += 1
        return b2

    return r.ExecutionDependencies(
        repo_state=lambda: state or good_state(),
        provider_transport=provider_factory,
        b2_transport=b2_factory,
        proof_id=lambda: "0123456789abcdef0123456789abcdef",
        sleep=lambda _n: None,
        local_receipt_root=tmp_path,
    ), calls, provider, b2


def execute(tmp_path, **kwargs):
    dependencies, calls, provider, b2 = deps(tmp_path, **kwargs)
    receipt = r.execute_proof(
        authorization_token=r.AUTHORIZATION_TOKEN,
        max_cost="0.05",
        expected_revision=AUTHORIZED_REVISION,
        env=env_all(),
        dependencies=dependencies,
    )
    return receipt, calls, provider, b2


@pytest.fixture(autouse=True)
def no_pipeline_sleep(monkeypatch):
    monkeypatch.setattr("genblaze_core.providers.base.time.sleep", lambda _n: None)


def test_01_plan_mode_zero_network():
    plan = r.fixed_plan({})
    assert plan["network"] == {"provider_calls": 0, "b2_reads": 0, "b2_writes": 0}
    assert plan["credential_presence"] == {name: False for name in r.REQUIRED_CREDENTIALS}


def test_02_self_test_mode_zero_network():
    result = r.offline_self_test({})
    assert result["status"] == "PASS"
    assert result["network_client_constructed"] is False


def test_03_wrong_authorization_fails_before_clients(tmp_path):
    dependencies, calls, _, _ = deps(tmp_path)
    with pytest.raises(r.SafetyError, match="authorization token"):
        r.execute_proof(
            authorization_token="wrong",
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_04_missing_credential_fails_before_clients(tmp_path):
    dependencies, calls, _, _ = deps(tmp_path)
    values = env_all()
    values.pop("B2_APP_KEY")
    with pytest.raises(r.SafetyError, match="B2_APP_KEY"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=values,
            dependencies=dependencies,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_05_dirty_worktree_fails_before_clients(tmp_path):
    dependencies, calls, _, _ = deps(tmp_path, state=good_state(clean=False))
    with pytest.raises(r.SafetyError, match="clean"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_06_wrong_branch_fails_before_clients(tmp_path):
    dependencies, calls, _, _ = deps(tmp_path, state=good_state(branch="main"))
    with pytest.raises(r.SafetyError, match="branch"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_07_trusted_ancestor_mismatch_fails_before_clients(tmp_path):
    dependencies, calls, _, _ = deps(
        tmp_path,
        state=good_state(trusted_ancestor_merge_base="0" * 40),
    )
    with pytest.raises(r.SafetyError, match="trusted ancestor"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_08_second_generation_post_blocked():
    fake = FakeProvider()
    counted = r.CountingProviderHTTP(fake, r.NetworkCounters())
    body = {"model": r.MODEL, "payload": r.GMICloudImageProvider(
        http_client=r.NoNetworkClient(), retry_policy=r.RetryPolicy.disabled()
    ).prepare_payload(r.build_generation_step())}
    counted.post("/requests", json=body)
    with pytest.raises(r.SafetyError, match="second generation"):
        counted.post("/requests", json=body)
    assert fake.posts == 1


def test_09_model_validation_request_blocked():
    fake = FakeProvider()
    counted = r.CountingProviderHTTP(fake, r.NetworkCounters())
    with pytest.raises(r.SafetyError, match="payload"):
        counted.post("/requests", json={"model": r.MODEL, "payload": {}})
    assert fake.posts == 0


def test_10_provider_preflight_request_blocked():
    fake = FakeProvider()
    counted = r.CountingProviderHTTP(fake, r.NetworkCounters())
    with pytest.raises(r.SafetyError, match="preflight"):
        counted.get("/requests")
    assert fake.gets == []


def test_11_generation_timeout_no_second_post(tmp_path):
    provider = FakeProvider(post_error=httpx.ReadTimeout("timeout"))
    dependencies, _, _, _ = deps(tmp_path, provider=provider)
    with pytest.raises(r.SafetyError):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert provider.posts == 1


def test_12_missing_request_id_no_second_post(tmp_path):
    provider = FakeProvider(submit_data={})
    dependencies, _, _, _ = deps(tmp_path, provider=provider)
    with pytest.raises(r.SafetyError):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert provider.posts == 1


def test_13_multiple_output_urls_fail(tmp_path):
    provider = FakeProvider(outcome={"media_urls": [
        {"url": "https://assets.invalid/a.png"},
        {"url": "https://assets.invalid/b.png"},
    ]})
    dependencies, _, _, b2 = deps(tmp_path, provider=provider)
    with pytest.raises(r.AmbiguousGenerationError, match="exactly one"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert not any(op == "PUT" for op, _ in b2.ops)


def test_14_zero_output_urls_fail(tmp_path):
    provider = FakeProvider(outcome={"media_urls": []})
    dependencies, _, _, b2 = deps(tmp_path, provider=provider)
    with pytest.raises(r.SafetyError):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert not any(op == "PUT" for op, _ in b2.ops)


def test_15_invalid_png_fails_before_b2_put(tmp_path):
    provider = FakeProvider(asset_bytes=b"x" * 2048)
    dependencies, _, _, b2 = deps(tmp_path, provider=provider)
    with pytest.raises(r.SafetyError, match="PNG"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert not any(op == "PUT" for op, _ in b2.ops)


def test_16_oversized_asset_fails_before_b2_put(tmp_path, monkeypatch):
    monkeypatch.setattr(r, "MAX_IMAGE_BYTES", 1000)
    provider = FakeProvider(asset_bytes=valid_png())
    dependencies, _, _, b2 = deps(tmp_path, provider=provider)
    with pytest.raises(r.SafetyError, match="50 MiB"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert not any(op == "PUT" for op, _ in b2.ops)


def test_17_existing_b2_key_aborts_before_provider(tmp_path):
    plan = r.make_key_plan("0123456789abcdef0123456789abcdef")
    b2 = FakeB2(existing={plan.image})
    dependencies, calls, provider, _ = deps(tmp_path, b2=b2)
    with pytest.raises(r.SafetyError, match="already exists"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert provider.posts == 0 and calls["provider"] == 0


def test_18_b2_put_retry_blocked():
    plan = r.make_key_plan("0123456789abcdef0123456789abcdef")
    fake = FakeB2()
    counted = r.CountingB2Client(fake, "bucket", plan, r.NetworkCounters())
    counted.image_validated = True
    counted.put_once(plan.brief, b"{}", "application/json")
    with pytest.raises(r.SafetyError, match="retry"):
        counted.put_once(plan.brief, b"{}", "application/json")
    assert [x for x in fake.ops if x == ("PUT", plan.brief)] == [("PUT", plan.brief)]


def test_19_b2_failure_no_second_provider_submit(tmp_path):
    plan = r.make_key_plan("0123456789abcdef0123456789abcdef")
    b2 = FakeB2(fail_put_key=plan.image)
    dependencies, _, provider, _ = deps(tmp_path, b2=b2)
    with pytest.raises(r.SafetyError, match="PUT"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert provider.posts == 1


def test_20_receipt_written_last(tmp_path):
    _, _, _, b2 = execute(tmp_path)
    puts = [key for op, key in b2.ops if op == "PUT"]
    assert puts[-1].endswith("/receipt/verification-receipt.json")


def test_21_rehydrate_exact_keys_only(tmp_path):
    receipt, _, _, b2 = execute(tmp_path)
    gets = [key for op, key in b2.ops if op == "GET"]
    plan = r.make_key_plan(receipt["proof_id"])
    assert set(gets) <= set(plan.rehydrate)
    assert not any(op.startswith("LIST") for op, _ in b2.ops)


def test_22_rehydrate_zero_generation_submissions(tmp_path):
    receipt, _, provider, _ = execute(tmp_path)
    assert receipt["provider_calls_during_rehydrate"] == 0
    assert provider.posts == 1


def test_23_original_rehydrated_hash_match_required(tmp_path):
    plan = r.make_key_plan("0123456789abcdef0123456789abcdef")
    b2 = FakeB2(mutate_get={plan.image: valid_png() + b"x"})
    dependencies, _, _, _ = deps(tmp_path, b2=b2)
    with pytest.raises(r.SafetyError, match="hashes differ"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )


def test_24_manifest_verification_mismatch_fails(tmp_path):
    plan = r.make_key_plan("0123456789abcdef0123456789abcdef")
    b2 = FakeB2(mutate_get={plan.manifest: b'{"bad":true}'})
    dependencies, _, _, _ = deps(tmp_path, b2=b2)
    with pytest.raises(r.SafetyError):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )


def test_25_secrets_absent_from_receipts_and_logs(tmp_path, capsys):
    receipt, _, _, _ = execute(tmp_path)
    text = json.dumps(receipt) + capsys.readouterr().out + capsys.readouterr().err
    values = env_all()
    assert all(values[name] not in text for name in ("GMI_API_KEY", "B2_KEY_ID", "B2_APP_KEY"))
    assert "X-Amz-" not in text and "Authorization" not in text


def test_26_price_fixed():
    assert r.EXPECTED_PRICE_USD == r.Decimal("0.035")


def test_27_cost_ceiling_fixed():
    assert r.MAX_COST_USD == r.Decimal("0.05")


def test_28_one_output_enforced():
    step = r.build_generation_step()
    assert r.OUTPUT_COUNT == 1
    assert step.params["max_images"] == 1
    assert "number_of_images" not in step.params


def test_29_no_fallback_and_no_retry_enforced():
    result = r.offline_self_test({})
    assert result["fallback_provider_count"] == 0
    assert result["automatic_retry_count"] == 0
    assert result["retry_policy_disabled"] is True


def test_30_exact_patch_scope_enforced():
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    paths = {line[3:] for line in result.stdout.splitlines() if line}
    assert paths <= {
        "scripts/ps042c5_one_real_genblaze_proof.py",
        "scripts/ps042c5_one_real_genblaze_proof_smoke.py",
        "tests/test_ps042c5_one_real_genblaze_proof.py",
    }


def test_31_prompt_hash_exact():
    assert hashlib.sha256(r.CANONICAL_PROMPT.encode()).hexdigest() == r.PROMPT_SHA256


def test_32_default_no_mode_fails_closed():
    assert r.main([]) == 2


def test_33_non_https_asset_blocked_before_download(tmp_path):
    provider = FakeProvider(outcome={"media_urls": [{"url": "http://assets.invalid/a.png"}]})
    dependencies, _, _, _ = deps(tmp_path, provider=provider)
    with pytest.raises(r.SafetyError):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )


def test_34_public_receipt_has_no_local_path(tmp_path):
    receipt, _, _, _ = execute(tmp_path)
    assert str(ROOT) not in json.dumps(receipt)
    assert all(uri.startswith("b2://") for uri in receipt["b2_uris"].values())


def test_35_partial_failure_receipt_is_incomplete_and_redacted(tmp_path):
    plan = r.make_key_plan("0123456789abcdef0123456789abcdef")
    b2 = FakeB2(fail_put_key=plan.image)
    dependencies, _, _, _ = deps(tmp_path, b2=b2)
    with pytest.raises(r.SafetyError):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    local = json.loads((tmp_path / plan.proof_id / "failure-receipt.json").read_text())
    assert local["complete_proof"] is False
    assert local["failed_key"] == plan.image
    assert "fake-secret-that-must-not-escape" not in json.dumps(local)


def test_36_missing_expected_revision_fails_before_clients(tmp_path):
    dependencies, calls, _, _ = deps(tmp_path)
    with pytest.raises(r.SafetyError, match="expected revision"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=None,
            env=env_all(),
            dependencies=dependencies,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_37_malformed_expected_revision_fails_before_clients(tmp_path):
    dependencies, calls, _, _ = deps(tmp_path)
    with pytest.raises(r.SafetyError, match="40 lowercase hexadecimal"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision="abc",
            env=env_all(),
            dependencies=dependencies,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_38_uppercase_expected_revision_fails_before_clients(tmp_path):
    dependencies, calls, _, _ = deps(tmp_path)
    with pytest.raises(r.SafetyError, match="40 lowercase hexadecimal"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION.upper(),
            env=env_all(),
            dependencies=dependencies,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_39_expected_revision_different_from_head_fails_before_clients(tmp_path):
    dependencies, calls, _, _ = deps(tmp_path)
    with pytest.raises(r.SafetyError, match="HEAD does not equal expected revision"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision="a" * 40,
            env=env_all(),
            dependencies=dependencies,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_40_expected_revision_different_from_origin_fails_before_clients(tmp_path):
    dependencies, calls, _, _ = deps(tmp_path, state=good_state(origin="a" * 40))
    with pytest.raises(r.SafetyError, match="origin does not equal expected revision"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_41_head_and_origin_mismatch_fails_before_clients(tmp_path):
    dependencies, calls, _, _ = deps(tmp_path, state=good_state(head="a" * 40))
    with pytest.raises(r.SafetyError, match="HEAD does not equal expected revision"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_42_trusted_ancestor_mismatch_fails_before_clients(tmp_path):
    dependencies, calls, _, _ = deps(
        tmp_path,
        state=good_state(trusted_ancestor_merge_base="a" * 40),
    )
    with pytest.raises(r.SafetyError, match="trusted ancestor"):
        r.execute_proof(
            authorization_token=r.AUTHORIZATION_TOKEN,
            max_cost="0.05",
            expected_revision=AUTHORIZED_REVISION,
            env=env_all(),
            dependencies=dependencies,
        )
    assert calls == {"provider": 0, "b2": 0}


def test_43_valid_exact_expected_revision_passes_revision_gates():
    credentials = r.validate_execute_gates(
        r.AUTHORIZATION_TOKEN,
        "0.05",
        AUTHORIZED_REVISION,
        env_all(),
        good_state(),
    )
    assert credentials == env_all()


def test_44_plan_forbids_expected_revision():
    assert r.main(["--plan", "--expected-revision", AUTHORIZED_REVISION]) == 2


def test_45_self_test_forbids_expected_revision():
    assert r.main(["--self-test", "--expected-revision", AUTHORIZED_REVISION]) == 2


def test_46_execute_parser_accepts_exact_revision_argument():
    args = r.build_parser().parse_args(
        ["--execute", "--expected-revision", AUTHORIZED_REVISION]
    )
    assert args.execute is True
    assert args.expected_revision == AUTHORIZED_REVISION


class FakeSmokeGit:
    def __init__(
        self,
        *,
        head: str = AUTHORIZED_REVISION,
        origin: str = AUTHORIZED_REVISION,
        porcelain: str = "",
        staged: str = "",
        merge_base: str = r.TRUSTED_ANCESTOR_COMMIT,
        tracked: set[str] | None = None,
    ):
        self.head = head
        self.origin = origin
        self.porcelain = porcelain
        self.staged = staged
        self.merge_base = merge_base
        self.tracked = tracked if tracked is not None else set(s.EXPECTED_FILES)

    def __call__(self, *args: str) -> str:
        command = tuple(args)
        if command == ("status", "--porcelain"):
            return self.porcelain
        if command == ("diff", "--cached", "--name-only"):
            return self.staged
        if command == ("branch", "--show-current"):
            return r.REQUIRED_BRANCH
        if command == ("rev-parse", "HEAD"):
            return self.head
        if command == ("rev-parse", f"origin/{r.REQUIRED_BRANCH}"):
            return self.origin
        if command == ("merge-base", "HEAD", r.TRUSTED_ANCESTOR_COMMIT):
            return self.merge_base
        if command[:2] == ("ls-files", "--"):
            return "\n".join(sorted(self.tracked))
        raise AssertionError(f"unexpected fake Git command: {command}")


def precommit_porcelain(paths: set[str] | frozenset[str] = s.EXPECTED_FILES) -> str:
    return "\n".join(f" M {path}" for path in sorted(paths))


def inspect_fake_smoke(fake: FakeSmokeGit):
    return s.inspect_repository_state(fake, lambda path: path in s.EXPECTED_FILES)


def test_47_precommit_smoke_state_passes_with_fake_git_state():
    state = inspect_fake_smoke(FakeSmokeGit(porcelain=precommit_porcelain()))
    assert s.validate_repository_state("precommit", state) == "precommit"


def test_48_postcommit_smoke_state_passes_with_fake_git_state():
    state = inspect_fake_smoke(FakeSmokeGit())
    assert s.validate_repository_state("postcommit", state) == "postcommit"


def test_49_unexpected_dirty_scope_fails_with_fake_git_state():
    fake = FakeSmokeGit(porcelain=precommit_porcelain({"unexpected.txt"}))
    with pytest.raises(RuntimeError, match="neither exact precommit scope nor clean"):
        s.validate_repository_state("auto", inspect_fake_smoke(fake))
