from __future__ import annotations

import json
import os
import secrets
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures/ps041d/genblaze-multi-provider-bundle-v1.json"
ROOT = Path(__file__).resolve().parents[1]


def call(base: str, method: str, path: str, body: bytes | None = None, headers: dict[str, str] | None = None):
    request = urllib.request.Request(base + path, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            raw = response.read(); return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read(); return exc.code, json.loads(raw) if raw else {}


@contextmanager
def server(operator: str, reader: str):
    sock = socket.socket(); sock.bind(("127.0.0.1", 0)); port = sock.getsockname()[1]; sock.close()
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), PROOFSTUDIO_IMPORT_OPERATOR_TOKEN=operator,
               PROOFSTUDIO_INTERNAL_SERVICE_TOKEN=reader)
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "proofstudio.api.app:app", "--host", "127.0.0.1", "--port", str(port), "--log-level", "error"],
        cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            if process.poll() is not None: raise AssertionError("FastAPI route server exited")
            try:
                if call(base, "GET", "/health")[0] == 200: break
            except OSError: time.sleep(0.05)
        else: raise AssertionError("FastAPI route server did not start")
        yield base, process
    finally:
        process.terminate()
        try: process.wait(timeout=5)
        except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=5)


def create_campaign(base: str, name: str) -> str:
    status, body = call(base, "POST", "/campaigns", json.dumps({"name": name, "brief": "isolated"}).encode(), {"Content-Type":"application/json"})
    assert status == 201; return body["campaign_id"]


def test_operator_and_private_read_boundaries() -> None:
    operator = secrets.token_urlsafe(32); reader = secrets.token_urlsafe(32)
    with server(operator, reader) as (base, process):
        campaign = create_campaign(base, "route"); other = create_campaign(base, "other")
        body = FIXTURE.read_bytes(); route = f"/internal/operator/campaigns/{campaign}/genblaze-bundles"
        assert call(base, "POST", route, body)[0] == 401
        assert call(base, "POST", route, body, {"X-ProofStudio-Import-Token": reader})[0] == 401
        status, created = call(base, "POST", route, body, {"X-ProofStudio-Import-Token":operator,"Content-Type":"application/json"})
        assert status == 201 and created["created"] is True; bundle_id = created["bundle"]["bundle_id"]
        status, repeated = call(base, "POST", route, body, {"X-ProofStudio-Import-Token":operator,"Content-Type":"application/json"})
        assert status == 200 and repeated["created"] is False
        changed = json.loads(body); changed["objects"][0]["inline_json"]["title"] = "changed"
        assert call(base, "POST", route, json.dumps(changed).encode(), {"X-ProofStudio-Import-Token":operator,"Content-Type":"application/json"})[0] == 409
        assert call(base, "POST", "/internal/operator/campaigns/camp_missing/genblaze-bundles", body, {"X-ProofStudio-Import-Token":operator,"Content-Type":"application/json"})[0] == 404
        assert call(base, "POST", "/campaigns/import", body)[0] in {404,405}
        list_route=f"/internal/campaigns/{campaign}/import-bundles"
        assert call(base,"GET",list_route)[0] == 401
        assert call(base,"GET",list_route,headers={"X-ProofStudio-Internal-Token":operator})[0] == 401
        status, listed=call(base,"GET",list_route,headers={"X-ProofStudio-Internal-Token":reader}); assert status==200 and len(listed["bundles"])==1
        status, detail=call(base,"GET",f"{list_route}/{bundle_id}",headers={"X-ProofStudio-Internal-Token":reader}); assert status==200
        status, passport=call(base,"GET",f"{list_route}/{bundle_id}/passport",headers={"X-ProofStudio-Internal-Token":reader}); assert status==200
        serialized=json.dumps(detail)+json.dumps(passport); assert "X-Amz-" not in serialized and "style_prompt" not in serialized and "provider_payload" not in serialized
        assert call(base,"GET",f"/internal/campaigns/{other}/import-bundles/{bundle_id}",headers={"X-ProofStudio-Internal-Token":reader})[0]==404
        assert process.poll() is None
    assert operator not in (process.stdout.read() + process.stderr.read()) and reader not in (process.stdout.read() + process.stderr.read())


def test_bounded_body_and_placeholder_fail_closed() -> None:
    placeholder="CHANGE_ME_IMPORT_OPERATOR_TOKEN"; reader=secrets.token_urlsafe(32)
    with server(placeholder,reader) as (base,_):
        campaign=create_campaign(base,"placeholder"); route=f"/internal/operator/campaigns/{campaign}/genblaze-bundles"
        assert call(base,"POST",route,b"{}",{"X-ProofStudio-Import-Token":placeholder,"Content-Type":"application/json"})[0]==401
    token=secrets.token_urlsafe(32)
    with server(token,reader) as (base,_):
        campaign=create_campaign(base,"limit"); route=f"/internal/operator/campaigns/{campaign}/genblaze-bundles"
        assert call(base,"POST",route,b" "*(1_048_576+1),{"X-ProofStudio-Import-Token":token,"Content-Type":"application/json"})[0]==413
