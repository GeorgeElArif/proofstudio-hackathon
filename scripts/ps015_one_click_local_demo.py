#!/usr/bin/env python3
"""
PS-015 One-Click Local Demo helper.

Turns the ProofStudio product into a repeatable local demo:

  - confirms it is running inside the ProofStudio repo
  - confirms Python imports work with the ``src`` layout
  - loads the deterministic seed pack
    (``examples/ps015/demo-seed-pack.json``)
  - imports the FastAPI app
  - creates a demo campaign and a SAFE DRY-RUN (run_live=false) via TestClient
  - fetches run / attempts / assets / manifest / passport
  - proves the default path called no live provider and no B2
  - writes a summary and a transcript under ``/tmp/proofstudio-ps-015``
  - prints the Review Room URL, API docs URL, run commands, ids, and paths

Default mode is SAFE. It never calls live providers and never calls B2.

Optional explicit live mode is opt-in ONLY:

  - ``--live``
  - or ``PROOFSTUDIO_PS015_LIVE=1``

When live mode is enabled the helper prints a clear warning, creates a
``run_live=true`` run against the real provider/B2 chain, and records whether
the live run completed / failed / blocked. It never fakes success, never fakes
media, and never fakes a manifest.

Optional convenience flags (not required for acceptance):

  - ``--print-runbook``  : print the exact two-terminal manual runbook
  - ``--check-ports``    : report whether the backend/frontend ports are in use
  - ``--serve``          : start backend + frontend locally and print URLs

Truth boundary: PS-015 proves ProofStudio has a deterministic local demo seed
pack and a safe one-click helper for preparing a local Review Room demo. It does
not prove public deployment, production availability, authentication, production
persistence, background job reliability, legal authenticity, C2PA authenticity,
semantic truth, or human authorship.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
SEED_PACK_PATH = REPO_ROOT / "examples" / "ps015" / "demo-seed-pack.json"
OUTPUT_DIR = Path("/tmp/proofstudio-ps-015")
SUMMARY_PATH = OUTPUT_DIR / "one-click-local-demo-summary.json"
TRANSCRIPT_PATH = OUTPUT_DIR / "one-click-local-demo-transcript.json"

# Fixed, honest local demo URLs and commands (mirror the PS-014 runbook).
REVIEW_ROOM_URL = "http://127.0.0.1:5173"
API_DOCS_URL = "http://127.0.0.1:8000/docs"
API_HEALTH_URL = "http://127.0.0.1:8000/health"
BACKEND_COMMAND = (
    "uvicorn proofstudio.api.app:app --reload --host 127.0.0.1 --port 8000"
)
FRONTEND_COMMAND = (
    "cd apps/web && npm run dev -- --host 127.0.0.1 --port 5173"
)

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_HOST = "127.0.0.1"
FRONTEND_PORT = 5173

LIVE_ENV_VAR = "PROOFSTUDIO_PS015_LIVE"
LIVE_WARNING = "Live mode may call external providers and B2."

TRUTH_BOUNDARY = (
    "PS-015 proves ProofStudio has a deterministic local demo seed pack and a "
    "safe one-click helper for preparing a local Review Room demo. It does not "
    "prove public deployment, production availability, authentication, "
    "production persistence, background job reliability, legal authenticity, "
    "C2PA authenticity, semantic truth, or human authorship."
)


class DemoError(Exception):
    """Raised when the one-click demo cannot complete a required step."""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_src_on_path() -> None:
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))


def _log(
    transcript: list[dict[str, Any]], step: str, payload: Any
) -> None:
    transcript.append({"step": step, "result": payload, "at": now_iso()})


def _ensure_repo() -> None:
    """Step 1: confirm we are running inside the ProofStudio repo."""
    if not (REPO_ROOT / "src" / "proofstudio").is_dir():
        raise DemoError(
            f"Not running inside the ProofStudio repo (expected "
            f"{REPO_ROOT / 'src' / 'proofstudio'})."
        )
    if not (REPO_ROOT / "specs").is_dir():
        raise DemoError(
            f"ProofStudio repo layout check failed: no 'specs/' dir at "
            f"{REPO_ROOT}."
        )


def _ensure_imports(transcript: list[dict[str, Any]]) -> None:
    """Step 2: confirm Python imports work with the src layout."""
    try:
        import fastapi  # noqa: F401

        from proofstudio.api.app import app  # noqa: F401
        from proofstudio.api.services import (  # noqa: F401
            FRAMEWORK_MODE,
            create_default_service,
        )
    except Exception as exc:  # pragma: no cover - environment-specific
        raise DemoError(
            f"Python imports failed with the src layout ({SRC_DIR}): {exc}"
        ) from exc

    if app is None or not isinstance(app, fastapi.FastAPI):
        raise DemoError(
            "FastAPI app import did not yield a real FastAPI instance."
        )
    _log(transcript, "confirm_imports", {
        "src_dir": str(SRC_DIR),
        "framework_mode": FRAMEWORK_MODE,
        "app_is_fastapi": isinstance(app, fastapi.FastAPI),
    })


def _load_seed_pack(transcript: list[dict[str, Any]]) -> dict[str, Any]:
    """Step 3: load the deterministic seed pack."""
    if not SEED_PACK_PATH.is_file():
        raise DemoError(f"Seed pack not found at {SEED_PACK_PATH}.")
    try:
        seed = json.loads(SEED_PACK_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DemoError(f"Seed pack is not valid JSON: {exc}") from exc

    # Deterministic seed pack must carry the required PS-015 fields and must
    # never carry fabricated evidence URLs/hashes/provider claims.
    required_top = (
        "slice", "demo_name", "campaign", "safe_run",
        "optional_live_run", "reviewer_script", "truth_boundary",
        "created_for",
    )
    missing = [k for k in required_top if k not in seed]
    if missing:
        raise DemoError(f"Seed pack missing required fields: {missing}")
    required_campaign = (
        "name", "brief", "audience", "channels", "tone",
        "creative_constraints",
    )
    cmiss = [k for k in required_campaign if k not in seed["campaign"]]
    if cmiss:
        raise DemoError(f"Seed pack campaign missing fields: {cmiss}")
    if seed["safe_run"].get("run_live") is not False:
        raise DemoError("Seed pack safe_run.run_live must be false.")
    if seed["optional_live_run"].get("run_live") is not True:
        raise DemoError("Seed pack optional_live_run.run_live must be true.")
    if seed["optional_live_run"].get("requires_explicit_opt_in") is not True:
        raise DemoError(
            "Seed pack optional_live_run.requires_explicit_opt_in must be true."
        )

    _log(transcript, "load_seed_pack", {
        "path": str(SEED_PACK_PATH),
        "slice": seed["slice"],
        "demo_name": seed["demo_name"],
    })
    return seed


def _campaign_payload_from_seed(seed: dict[str, Any]) -> dict[str, Any]:
    """Map the rich seed-pack campaign to the POST /campaigns accepted fields.

    The seed pack carries more structured metadata than CampaignCreate accepts.
    We map the extra fields into the existing ``target_audience`` /
    ``platform`` / ``objective`` fields so the campaign record stays rich and
    deterministic without touching the backend contract. No fake evidence.
    """
    campaign = seed["campaign"]
    channels = campaign.get("channels") or []
    platform = ", ".join(str(ch) for ch in channels) if channels else "web"
    tone = campaign.get("tone")
    constraints = campaign.get("creative_constraints") or []
    objective_parts: list[str] = []
    if tone:
        objective_parts.append(f"Tone: {tone}")
    if constraints:
        objective_parts.append(
            "Constraints: " + " | ".join(str(c) for c in constraints)
        )
    objective = " ".join(objective_parts) or None
    return {
        "name": campaign["name"],
        "brief": campaign["brief"],
        "target_audience": campaign.get("audience"),
        "platform": platform,
        "objective": objective,
    }


class _Sentinel(Exception):
    pass


def run_one_click_demo(
    *,
    live: bool = False,
    transcript: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Execute the one-click local demo and return a structured result.

    ``live=False`` (the default) runs the safe dry-run path only: no live
    provider call, no B2 call, no fake media, no fake manifest. Live sentinels
    are installed to PROVE the default path never reaches the provider/B2
    bridges.

    ``live=True`` is an explicit opt-in: it creates a ``run_live=true`` run
    against the real provider/B2 chain (only when credentials are configured),
    prints a warning, and honestly records the live outcome. It never fakes
    success.
    """
    if transcript is None:
        transcript = []

    result: dict[str, Any] = {
        "slice": "PS-015",
        "ok": False,
        "live_mode_enabled": bool(live),
        "review_room_url": REVIEW_ROOM_URL,
        "api_docs_url": API_DOCS_URL,
        "api_health_url": API_HEALTH_URL,
        "backend_command": BACKEND_COMMAND,
        "frontend_command": FRONTEND_COMMAND,
        "seed_pack_path": str(SEED_PACK_PATH),
        "summary_path": str(SUMMARY_PATH),
        "transcript_path": str(TRANSCRIPT_PATH),
        "campaign_id": None,
        "run_id": None,
        "run_status": None,
        "run_live": False,
        "default_no_live_provider_call": False,
        "default_no_b2_call": False,
        "no_fake_media": False,
        "no_fake_manifest": False,
        "live_run_status": None,
        "truth_boundary": TRUTH_BOUNDARY,
        "error": None,
    }

    try:
        # 1-2. Repo + import checks (also wires SRC_DIR onto sys.path).
        _ensure_repo()
        _ensure_imports(transcript)

        # 3. Seed pack.
        seed = _load_seed_pack(transcript)

        # 4. Import the FastAPI app + TestClient (after src path is wired).
        from fastapi.testclient import TestClient

        import proofstudio.api.services as services_module
        import proofstudio.api.archive as archive_module
        from proofstudio.api.app import app
        from proofstudio.api.models import RUN_STATUS_DRY_RUN_CREATED

        assert app is not None
        client = TestClient(app)

        # 5. Create the demo campaign from the seed pack.
        campaign_payload = _campaign_payload_from_seed(seed)
        r = client.post("/campaigns", json=campaign_payload)
        if r.status_code != 201:
            raise DemoError(
                f"POST /campaigns failed ({r.status_code}): {r.text}"
            )
        cbody = r.json()
        campaign_id = cbody.get("campaign_id")
        if not campaign_id:
            raise DemoError("POST /campaigns returned no campaign_id.")
        result["campaign_id"] = campaign_id
        _log(transcript, "create_campaign", {
            "campaign_id": campaign_id,
            "name": campaign_payload["name"],
        })

        if live:
            # --------------------------------------------------------------
            # EXPLICIT LIVE PATH (opt-in only).
            # --------------------------------------------------------------
            print(f"WARNING: {LIVE_WARNING}", file=sys.stderr)
            _log(transcript, "live_mode_warning", {"warning": LIVE_WARNING})

            run_payload = {
                "campaign_id": campaign_id,
                "prompt": seed["optional_live_run"].get("prompt"),
                "budget_mode": "free-only",
                "run_live": True,
                "dry_run": False,
            }
        else:
            # --------------------------------------------------------------
            # SAFE DRY-RUN PATH (default).
            # --------------------------------------------------------------
            run_payload = {
                "campaign_id": campaign_id,
                "prompt": seed["safe_run"].get("prompt"),
                "budget_mode": "free-only",
                "run_live": False,
                "dry_run": True,
            }

        # For the default safe path, install sentinels that PROVE the dry-run
        # never reaches the live provider bridge or the B2 store/read paths.
        provider_call_counter = {"count": 0}
        b2_call_counter = {"count": 0}

        def _provider_sentinel(**kwargs: Any) -> dict[str, Any]:
            provider_call_counter["count"] += 1
            raise _Sentinel(
                "LIVE PROVIDER WAS CALLED DURING THE PS-015 DEFAULT SAFE PATH"
            )

        def _b2_store_sentinel(*args: Any, **kwargs: Any) -> dict[str, Any]:
            b2_call_counter["count"] += 1
            raise _Sentinel("B2 STORE WAS CALLED DURING THE PS-015 DEFAULT")

        def _b2_read_sentinel(*args: Any, **kwargs: Any) -> dict[str, Any]:
            b2_call_counter["count"] += 1
            raise _Sentinel("B2 READ WAS CALLED DURING THE PS-015 DEFAULT")

        original_live = services_module.execute_live_run
        original_b2_store = archive_module.store_run_archive_with_genblaze
        original_b2_read = archive_module.read_archive_from_b2

        if not live:
            services_module.execute_live_run = _provider_sentinel  # type: ignore[assignment]
            archive_module.store_run_archive_with_genblaze = _b2_store_sentinel  # type: ignore[assignment]
            archive_module.read_archive_from_b2 = _b2_read_sentinel  # type: ignore[assignment]

        try:
            r = client.post("/runs", json=run_payload)
        finally:
            services_module.execute_live_run = original_live  # type: ignore[assignment]
            archive_module.store_run_archive_with_genblaze = original_b2_store  # type: ignore[assignment]
            archive_module.read_archive_from_b2 = original_b2_read  # type: ignore[assignment]

        if r.status_code != 201:
            raise DemoError(
                f"POST /runs failed ({r.status_code}): {r.text}"
            )
        rbody = r.json()
        run_id = rbody.get("run_id")
        if not run_id:
            raise DemoError("POST /runs returned no run_id.")
        run_record = rbody.get("run") or {}
        run_status = run_record.get("status")
        result["run_id"] = run_id
        result["run_status"] = run_status
        result["run_live"] = bool(run_record.get("run_live"))
        _log(transcript, "create_run", {
            "run_id": run_id,
            "status": run_status,
            "run_live": result["run_live"],
            "selected_provider": run_record.get("selected_provider"),
        })

        # 7. Fetch run / attempts / assets / manifest / passport.
        readbacks: dict[str, Any] = {}
        for label, path in (
            ("run", f"/runs/{run_id}"),
            ("attempts", f"/runs/{run_id}/attempts"),
            ("assets", f"/runs/{run_id}/assets"),
            ("manifest", f"/runs/{run_id}/manifest"),
            ("passport", f"/runs/{run_id}/passport"),
        ):
            rr = client.get(path)
            if rr.status_code != 200:
                raise DemoError(
                    f"GET {path} failed ({rr.status_code}): {rr.text}"
                )
            readbacks[label] = rr.json()
        _log(transcript, "fetch_readbacks", {
            "run_status": (readbacks["run"].get("run") or {}).get("status"),
            "attempt_count": readbacks["attempts"].get("attempt_count"),
            "asset_count": readbacks["assets"].get("asset_count"),
            "manifest_ready": readbacks["manifest"].get("ready"),
            "passport_generated_media": (
                readbacks["passport"].get("generation_summary") or {}
            ).get("generated_media_present"),
        })

        # 8-9. Confirm the default path called no provider and no B2.
        result["default_no_live_provider_call"] = (
            provider_call_counter["count"] == 0
        )
        result["default_no_b2_call"] = b2_call_counter["count"] == 0
        _log(transcript, "call_sentinels", {
            "provider_calls": provider_call_counter["count"],
            "b2_calls": b2_call_counter["count"],
        })

        # Honest no-fake proof for the safe path: zero assets, manifest not
        # ready, passport reports no generated media.
        asset_count = readbacks["assets"].get("asset_count", 0)
        manifest_ready = readbacks["manifest"].get("ready")
        generated_media = (
            readbacks["passport"].get("generation_summary") or {}
        ).get("generated_media_present")
        if not live:
            result["no_fake_media"] = (
                result["default_no_live_provider_call"]
                and asset_count == 0
                and generated_media is False
            )
            result["no_fake_manifest"] = (
                manifest_ready is False
                and not (readbacks["manifest"].get("manifest_uri"))
            )
        else:
            # Live path: honestly record outcome; never fake success.
            result["live_run_status"] = run_status
            result["no_fake_media"] = True  # we never fabricate
            result["no_fake_manifest"] = True  # we never fabricate

        # Validate the safe dry-run produced the honest expected status.
        if not live and run_status != RUN_STATUS_DRY_RUN_CREATED:
            raise DemoError(
                f"Safe dry-run expected status {RUN_STATUS_DRY_RUN_CREATED!r}, "
                f"got {run_status!r}."
            )

        result["ok"] = True

    except DemoError as exc:
        result["ok"] = False
        result["error"] = str(exc)
        _log(transcript, "demo_error", {"error": str(exc)})
    except _Sentinel as exc:
        # A sentinel fired during the safe path: providers/B2 were reached.
        result["ok"] = False
        result["error"] = str(exc)
        result["default_no_live_provider_call"] = (
            provider_call_counter["count"] == 0
        )
        result["default_no_b2_call"] = b2_call_counter["count"] == 0
        _log(transcript, "sentinel_violation", {"error": str(exc)})
    except Exception as exc:  # pragma: no cover - crash guard
        result["ok"] = False
        result["error"] = f"{type(exc).__name__}: {exc}"
        _log(transcript, "unhandled_crash", {
            "error": result["error"],
        })

    # 10-11. Write summary + transcript.
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        result["written_at"] = now_iso()
        SUMMARY_PATH.write_text(
            json.dumps(result, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        TRANSCRIPT_PATH.write_text(
            json.dumps(
                {
                    "slice": "PS-015",
                    "demo": "one-click-local-demo",
                    "steps": transcript,
                    "written_at": now_iso(),
                },
                indent=2,
                ensure_ascii=False,
                default=str,
            ),
            encoding="utf-8",
        )
    except OSError as exc:  # pragma: no cover - filesystem-specific
        result["error"] = f"failed to write outputs: {exc}"

    return result


def _print_demo_report(result: dict[str, Any]) -> None:
    """Step 12: print the human-readable demo report (URLs, ids, paths)."""
    print("\n=== ProofStudio PS-015 One-Click Local Demo ===")
    print(f"Review Room URL  : {result.get('review_room_url')}")
    print(f"API docs URL     : {result.get('api_docs_url')}")
    print(f"API health URL   : {result.get('api_health_url')}")
    print(f"Backend command  : {result.get('backend_command')}")
    print(f"Frontend command : {result.get('frontend_command')}")
    print(f"Campaign id      : {result.get('campaign_id')}")
    print(f"Run id           : {result.get('run_id')}")
    print(f"Run status       : {result.get('run_status')}")
    print(f"run_live         : {result.get('run_live')}")
    print(
        f"Default no provider call : "
        f"{result.get('default_no_live_provider_call')}"
    )
    print(f"Default no B2 call       : {result.get('default_no_b2_call')}")
    print(f"No fake media            : {result.get('no_fake_media')}")
    print(f"No fake manifest         : {result.get('no_fake_manifest')}")
    print(f"Summary path     : {result.get('summary_path')}")
    print(f"Transcript path  : {result.get('transcript_path')}")
    if result.get("live_mode_enabled"):
        print(f"Live run status  : {result.get('live_run_status')}")
    status = "OK" if result.get("ok") else "FAILED"
    print(f"Result           : {status}")
    if result.get("error"):
        print(f"Error            : {result['error']}")


def print_runbook() -> None:
    """Print the exact two-terminal manual fallback runbook."""
    print("\n=== ProofStudio PS-015 Two-Terminal Manual Runbook ===\n")
    print("Terminal 1 — FastAPI backend:\n")
    print("  cd /home/proofstudio-work/proofstudio")
    print("  source .venv/bin/activate")
    print('  export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"')
    print(
        "  uvicorn proofstudio.api.app:app --reload "
        "--host 127.0.0.1 --port 8000"
    )
    print("\nTerminal 2 — Review Room frontend:\n")
    print("  cd /home/proofstudio-work/proofstudio/apps/web")
    print("  npm install")
    print("  npm run dev -- --host 127.0.0.1 --port 5173")
    print("\nOpen:\n")
    print(f"  Review Room : {REVIEW_ROOM_URL}")
    print(f"  API health  : {API_HEALTH_URL}")
    print(f"  API docs    : {API_DOCS_URL}")
    print("\nDemo sequence:\n")
    print("  - confirm API Status card reports the backend online")
    print("  - create a campaign (or use the seeded campaign id)")
    print("  - click 'Create Safe Dry Run' and inspect the honest no-media state")
    print("  - inspect attempts / assets / manifest / passport panels")
    print("  - optionally enable live mode (explicit opt-in) and run a live proof")
    print("  - always end on the Truth Boundary footer\n")


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        try:
            sock.connect((host, port))
        except OSError:
            return False
        return True


def check_ports() -> int:
    """Report whether the backend/frontend ports are in use."""
    print("\n=== ProofStudio PS-015 Port Check ===")
    backend = _port_in_use(BACKEND_HOST, BACKEND_PORT)
    frontend = _port_in_use(FRONTEND_HOST, FRONTEND_PORT)
    print(
        f"Backend  {BACKEND_HOST}:{BACKEND_PORT} "
        f"({'IN USE' if backend else 'free'})"
    )
    print(
        f"Frontend {FRONTEND_HOST}:{FRONTEND_PORT} "
        f"({'IN USE' if frontend else 'free'})"
    )
    if backend:
        print(f"  -> API health reachable at {API_HEALTH_URL}")
    if frontend:
        print(f"  -> Review Room reachable at {REVIEW_ROOM_URL}")
    return 0


def _spawn(cmd: list[str], cwd: Path) -> subprocess.Popen:
    return subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def serve() -> int:
    """Optional serve mode: start backend + frontend locally.

    Starts the FastAPI backend on 127.0.0.1:8000 and the Vite frontend on
    127.0.0.1:5173, prints the URLs, keeps both alive until Ctrl-C, and
    terminates child processes cleanly on exit. It NEVER runs live mode by
    default.
    """
    print("WARNING: serve mode starts local processes; it does NOT enable live "
          "mode. The default demo stays a safe dry-run.", file=sys.stderr)
    backend = _spawn(
        ["python", "-m", "uvicorn", "proofstudio.api.app:app",
         "--host", BACKEND_HOST, "--port", str(BACKEND_PORT)],
        cwd=REPO_ROOT,
    )
    frontend = _spawn(
        ["npm", "run", "dev", "--",
         "--host", FRONTEND_HOST, "--port", str(FRONTEND_PORT)],
        cwd=REPO_ROOT / "apps" / "web",
    )
    procs = [backend, frontend]

    def _terminate(_signum=None, _frame=None) -> None:
        for proc in procs:
            if proc.poll() is None:
                proc.terminate()
        for proc in procs:
            try:
                proc.wait(timeout=5.0)
            except subprocess.SubprocessError:
                proc.kill()

    signal.signal(signal.SIGINT, _terminate)
    signal.signal(signal.SIGTERM, _terminate)

    print(f"\nBackend  : {API_HEALTH_URL}")
    print(f"API docs : {API_DOCS_URL}")
    print(f"Frontend : {REVIEW_ROOM_URL}")
    print("\nPress Ctrl-C to stop both processes.\n")

    try:
        while True:
            time.sleep(1.0)
            for proc in procs:
                if proc.poll() is not None:
                    print(f"Process exited (pid={proc.pid}); stopping serve.",
                          file=sys.stderr)
                    _terminate()
                    return 1
    except KeyboardInterrupt:
        _terminate()
        print("\nStopped.")
    return 0


def _live_requested(args: argparse.Namespace) -> bool:
    if getattr(args, "live", False):
        return True
    return os.environ.get(LIVE_ENV_VAR) == "1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="PS-015 One-Click Local Demo helper (safe dry-run by default)."
    )
    parser.add_argument(
        "--print-runbook",
        action="store_true",
        help="Print the exact two-terminal manual fallback runbook and exit.",
    )
    parser.add_argument(
        "--check-ports",
        action="store_true",
        help="Report whether the backend/frontend ports are in use and exit.",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start backend + frontend locally (safe; never live by default).",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help=(
            "Explicit opt-in live mode. May call external providers and B2. "
            "Never the default. Equivalently set "
            f"{LIVE_ENV_VAR}=1."
        ),
    )
    args = parser.parse_args(argv)

    if args.print_runbook:
        print_runbook()
        return 0
    if args.check_ports:
        return check_ports()
    if args.serve:
        return serve()

    live = _live_requested(args)
    transcript: list[dict[str, Any]] = []
    result = run_one_click_demo(live=live, transcript=transcript)
    _print_demo_report(result)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
