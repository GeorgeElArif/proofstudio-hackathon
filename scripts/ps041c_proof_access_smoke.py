#!/usr/bin/env python3
"""PS-041C local HTTP proof-read authorization smoke (no provider/B2 calls)."""

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
from pathlib import Path
from typing import Any

PORT = 0
BASE = ""
HEADER = "X-ProofStudio-Internal-Token"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def request(path: str, *, token: str | None = None, body: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    headers = {"accept": "application/json"}
    if token is not None:
        headers[HEADER] = token
    data = None
    method = "GET"
    if body is not None:
        headers["content-type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
        method = "POST"
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE + path, data=data, headers=headers, method=method), timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def main() -> None:
    global PORT, BASE
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        PORT = int(probe.getsockname()[1])
    BASE = f"http://127.0.0.1:{PORT}"
    token = secrets.token_urlsafe(32)
    env = {
        **os.environ,
        "PYTHONPATH": "src",
        "PROOFSTUDIO_INTERNAL_SERVICE_TOKEN": token,
        "PROOFSTUDIO_LIVE_RUNS_ENABLED": "false",
        "PROOFSTUDIO_B2_WRITES_ENABLED": "false",
    }
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "proofstudio.api.app:app", "--host", "127.0.0.1", "--port", str(PORT), "--log-level", "warning"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(80):
            try:
                if request("/health")[0] == 200:
                    break
            except (OSError, TimeoutError):
                pass
            time.sleep(0.25)
        else:
            raise AssertionError("local FastAPI did not start")

        _, first_body = request("/campaigns", body={"name": "PS-041C A", "brief": "Local authorization fixture."})
        _, second_body = request("/campaigns", body={"name": "PS-041C B", "brief": "Cross-campaign fixture."})
        first, second = first_body["campaign_id"], second_body["campaign_id"]
        _, run_body = request("/runs", body={"campaign_id": first, "dry_run": True})
        _, foreign_body = request("/runs", body={"campaign_id": second, "dry_run": True})
        run, foreign_run = run_body["run_id"], foreign_body["run_id"]

        protected = [f"/campaigns/{first}", f"/runs/{run}", f"/runs/{run}/attempts", f"/runs/{run}/assets", f"/runs/{run}/manifest"]
        require(all(request(path)[0] == 401 for path in protected), "direct arbitrary reads must require service auth")
        require(request(protected[0], token="wrong-token-value-that-is-long")[0] == 401, "wrong token accepted")
        require(all(request(path, token=token)[0] == 200 for path in protected), "correct token did not unlock protected reads")

        room_status, room = request(f"/internal/campaigns/{first}/proof-room?runId={run}", token=token)
        require(room_status == 200 and room["source"] == "proof_api", "internal Proof Room failed")
        require("local_image" not in json.dumps(room), "local filesystem field leaked")
        passport_status, passport = request(f"/internal/campaigns/{first}/runs/{run}/passport", token=token)
        require(passport_status == 200 and passport["source"] == "proof_api", "private Passport failed")
        require(request(f"/internal/campaigns/{first}/runs/{foreign_run}/passport", token=token)[0] == 404, "cross-campaign run accepted")
        require(request(f"/internal/campaigns/{first}/runs/missing-run/passport", token=token)[0] == 404, "missing run leaked")
        for bad in ["bad%20id", "bad%5Cid", "bad%2Fid", "%00control", "x" * 129, "%65%CC%81"]:
            status, payload = request(f"/internal/campaigns/{first}/proof-room?runId={bad}", token=token)
            require(status == 400 and payload["code"] == "invalid_request", f"malformed identifier accepted: {bad}")

        require(request(f"/runs/{run}/passport")[0] == 404, "arbitrary public Passport leaked")
        golden = json.loads(Path("docs/evidence/demo/golden-demo-run.json").read_text(encoding="utf-8"))["run_id"]
        golden_status, golden_body = request(f"/runs/{golden}/passport")
        require(golden_status == 200 and golden_body["golden_demo_unlock"]["public_unlock_scope"] == "golden_demo_only", "exact golden handler failed")
        require(token not in Path("src/proofstudio/api/app.py").read_text(encoding="utf-8"), "runtime token entered source")
        print("PS-041C FastAPI smoke: PASS")
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)


if __name__ == "__main__":
    main()
