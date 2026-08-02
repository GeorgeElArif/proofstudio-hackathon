"""Service layer for the PS-008 backend API skeleton.

This module separates business logic from the FastAPI route handlers in
``app.py``. Every function here is independently callable without an HTTP
server, which is how the PS-008 smoke script exercises the API.

Service surface (see specs/16-ps-008-backend-api-skeleton.md section 8):

- ``health``
- ``version``
- ``create_campaign``
- ``get_campaign``
- ``create_run``
- ``get_run``
- ``get_run_attempts``
- ``get_run_assets``
- ``get_run_manifest``

Dry-run contract (the default):

- ``create_run`` with ``dry_run`` true (or ``run_live`` false) MUST NOT call
  any live provider, MUST NOT call B2, MUST NOT call Genblaze, and MUST NOT
  fabricate media. It records a run with status ``dry_run_created`` and empty
  attempts / assets / no manifest.

Live hook (intentionally not wired in PS-008):

- ``run_live`` true records status ``live_execution_not_supported_in_ps008``.
  Later slices (PS-009 / PS-010) will connect ``_execute_live`` to the PS-007
  provider-router + B2 + Genblaze pipeline. The hook exists so the wiring
  point is explicit and so the truth boundary stays clean: PS-008 never lies
  about having executed a live run.

Missing-resource handling:

- ``get_campaign`` / ``get_run`` raise :class:`NotFoundError` for unknown ids.
- ``get_run_manifest`` raises :class:`NotFoundError` if the run itself is
  unknown, but returns a clear not-ready :class:`ManifestRecord` if the run
  exists but has no manifest yet.
"""

from __future__ import annotations

import os
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from proofstudio.api.live_bridge import (
    B2_REQUIRED_ENV as LIVE_B2_REQUIRED_ENV,
    JOB_TYPE as LIVE_JOB_TYPE,
    TRUTH_BOUNDARY as LIVE_TRUTH_BOUNDARY,
    execute_live_run,
    govern_live_run,
)
from proofstudio.api import archive as archive_module
from proofstudio.api import passport as passport_module
from proofstudio.api import durable_passport as durable_passport_module
from proofstudio.api.models import (
    CAMPAIGN_STATUS_CREATED,
    REQUIRED_ATTEMPT_FIELDS,
    RUN_STATUS_DRY_RUN_CREATED,
    RUN_STATUS_LIVE_BLOCKED,
    RUN_STATUS_LIVE_COMPLETED,
    RUN_STATUS_LIVE_FAILED,
    RUN_STATUS_LIVE_NOT_SUPPORTED,
    RUN_STATUS_LIVE_RUNNING,
    SERVICE_NAME,
    SLICE_ID,
    AssetRecord,
    AttemptRecord,
    CampaignCreate,
    CampaignRecord,
    ManifestRecord,
    RunCreate,
    RunRecord,
)
from proofstudio.api.store import InMemoryStore
from proofstudio.api.genblaze_external_adapter import ImportCandidate, build_candidate, passport_for
from proofstudio.api.imported_bundle import (
    ImportBundleRequest, ImportResult, ImportedBundleRecord, ImportedLineageEdge,
    ImportedLineageNode, PortableLineagePassport,
)

APP_VERSION = "0.1.0"
PROOF_VERSION = "ps-009"

# PS-012: detect FastAPI server-mode availability once at import time so the
# service layer can self-report its framework mode (``/health`` mode and
# ``/version`` framework_mode) and so ``app.py`` can share a single source of
# truth for the flag. service_only is still honest when FastAPI is absent.
def _detect_fastapi_available() -> bool:
    try:
        import fastapi  # noqa: F401
    except Exception:
        return False
    return True


_FASTAPI_AVAILABLE = _detect_fastapi_available()
FRAMEWORK_MODE = "fastapi" if _FASTAPI_AVAILABLE else "service_only"

# Product capabilities surfaced by ``GET /version`` (PS-012 section 9.2). Each
# maps to a prior milestone that proved it. ``fastapi_server`` is only reported
# when FastAPI is actually importable so the capability never lies.
CAPABILITIES: tuple[str, ...] = (
    "provider_router",        # PS-006 / PS-007
    "live_run_bridge",        # PS-009
    "b2_archive_rehydrate",   # PS-010
    "provenance_passport",    # PS-011
)

DEFAULT_BUDGET_MODE = "free-only"
DEFAULT_LIVE_OUTPUT_DIR = "/tmp/proofstudio-ps-009/live-run"
DEFAULT_LIVE_B2_PREFIX = "proofstudio/ps-009"


class NotFoundError(Exception):
    """Raised when a requested campaign or run does not exist.

    The API layer translates this into a clean 404 :class:`ErrorResponse`
    instead of letting a traceback leak.
    """

    def __init__(self, resource: str, resource_id: str, detail: str | None = None) -> None:
        self.resource = resource
        self.resource_id = resource_id
        self.detail = detail or f"{resource} {resource_id!r} not found"
        super().__init__(self.detail)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def detect_git_branch() -> str | None:
    """Best-effort detection of the current git branch.

    Used by ``version`` so the API can self-report which branch it was built
    from. Returns ``None`` if detection fails (e.g. not a git checkout, or
    ``git`` is unavailable). Never raises.
    """
    # Preferred: read .git/HEAD without spawning a subprocess.
    try:
        repo_root = Path(__file__).resolve()
        for parent in repo_root.parents:
            git_dir = parent / ".git"
            if git_dir.is_dir():
                head_file = git_dir / "HEAD"
                if head_file.is_file():
                    text = head_file.read_text(encoding="utf-8").strip()
                    if text.startswith("ref:"):
                        # "ref: refs/heads/<branch>" -> "<branch>"
                        # (preserve branch namespaces like "ps-008/...")
                        ref = text[len("ref:"):].strip()
                        heads_prefix = "refs/heads/"
                        if ref.startswith(heads_prefix):
                            return ref[len(heads_prefix):] or None
                        return ref or None
                    return text or None
                break
    except OSError:
        pass

    # Fallback: ask git directly. Only used if the file heuristic failed.
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2.0,
            check=False,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            return branch or None
    except (OSError, subprocess.SubprocessError):
        pass

    return None


def _validate_attempt_shape(attempt: dict[str, Any]) -> list[str]:
    """Validate an attempt carries the PS-006 20-field shape.

    Returns a list of missing-field error strings (empty when valid). This is
    used when attempts are registered so the store never holds a compact
    attempt that violates the PS-007 attempt-ledger contract.
    """
    return [
        field
        for field in REQUIRED_ATTEMPT_FIELDS
        if field not in attempt
    ]


class ProofStudioService:
    """Business-logic facade over the in-memory store.

    Constructed with a store and optional runtime metadata. The FastAPI app
    holds one service instance; the smoke script may construct another to keep
    its test state isolated.
    """

    def __init__(
        self,
        store: InMemoryStore | None = None,
        *,
        service: str = SERVICE_NAME,
        slice_id: str = SLICE_ID,
        app_version: str = APP_VERSION,
        proof_version: str = PROOF_VERSION,
        environment: str | None = None,
        live_output_dir: str = DEFAULT_LIVE_OUTPUT_DIR,
        live_b2_prefix: str = DEFAULT_LIVE_B2_PREFIX,
    ) -> None:
        self.store = store or InMemoryStore()
        self._service = service
        self._slice = slice_id
        self._app_version = app_version
        self._proof_version = proof_version
        self._environment = environment or os.environ.get(
            "PROOFSTUDIO_ENV", "local"
        )
        self._live_output_dir = live_output_dir
        self._live_b2_prefix = live_b2_prefix

    # ------------------------------------------------------------------
    # Health / version
    # ------------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        # PS-012 contract: ok / service / mode / version. ``mode`` reports the
        # runtime framework mode (fastapi vs service_only) so a caller can tell
        # whether the HTTP server contract is live.
        return {
            "ok": True,
            "service": self._service,
            "mode": FRAMEWORK_MODE,
            "version": self._app_version,
            "environment": self._environment,
        }

    def version(self) -> dict[str, Any]:
        # PS-012 contract: service / version / framework_mode / capabilities.
        # The legacy slice/git_branch/app_version/proof_version keys are kept
        # so earlier smoke scripts (PS-008) keep working.
        capabilities = list(CAPABILITIES)
        if _FASTAPI_AVAILABLE:
            capabilities.append("fastapi_server")
        return {
            "service": self._service,
            "version": self._app_version,
            "framework_mode": FRAMEWORK_MODE,
            "capabilities": capabilities,
            "slice": self._slice,
            "git_branch": detect_git_branch(),
            "app_version": self._app_version,
            "proof_version": self._proof_version,
        }

    # ------------------------------------------------------------------
    # Campaign
    # ------------------------------------------------------------------

    def create_campaign(self, payload: CampaignCreate | dict[str, Any]) -> dict[str, Any]:
        if isinstance(payload, CampaignCreate):
            data = payload.model_dump()
        else:
            data = CampaignCreate.model_validate(payload).model_dump()

        campaign_id = _new_id("camp")
        now = _utc_now_iso()
        record = CampaignRecord(
            campaign_id=campaign_id,
            name=data["name"],
            brief=data["brief"],
            target_audience=data.get("target_audience"),
            platform=data.get("platform"),
            objective=data.get("objective"),
            status=CAMPAIGN_STATUS_CREATED,
            created_at=now,
        )
        stored = self.store.create_campaign(campaign_id, record.model_dump())
        return {
            "campaign_id": campaign_id,
            "status": CAMPAIGN_STATUS_CREATED,
            "campaign": stored,
        }

    def get_campaign(self, campaign_id: str) -> dict[str, Any]:
        record = self.store.get_campaign(campaign_id)
        if record is None:
            raise NotFoundError("campaign", campaign_id)
        return {"campaign_id": campaign_id, "campaign": record}

    # ------------------------------------------------------------------
    # PS-041D internal/operator imported lineage
    # ------------------------------------------------------------------

    def import_genblaze_bundle(
        self,
        campaign_id: str,
        payload: ImportBundleRequest,
        *,
        b2_json_reader: Any | None = None,
        fail_before_commit: bool = False,
    ) -> ImportResult:
        if not self.store.has_campaign(campaign_id):
            from proofstudio.api.genblaze_external_adapter import ImportValidationError
            raise ImportValidationError("campaign_not_found", 404)
        candidate = build_candidate(campaign_id, payload, b2_json_reader=b2_json_reader)
        created, record = self.store.commit_import_candidate(candidate, fail_before_commit=fail_before_commit)
        if created:
            return ImportResult(created=True, bundle=candidate.bundle, nodes=candidate.nodes, edges=candidate.edges)
        graph = self.store.get_import_graph(campaign_id, record["bundle_id"])
        assert graph is not None
        nodes, edges = graph
        return ImportResult(
            created=False, bundle=ImportedBundleRecord.model_validate(record),
            nodes=[ImportedLineageNode.model_validate(node) for node in nodes],
            edges=[ImportedLineageEdge.model_validate(edge) for edge in edges],
        )

    def list_imported_bundles(self, campaign_id: str) -> list[ImportedBundleRecord]:
        if not self.store.has_campaign(campaign_id):
            raise NotFoundError("campaign", campaign_id)
        return [ImportedBundleRecord.model_validate(item) for item in self.store.list_import_bundles(campaign_id)]

    def get_imported_bundle(self, campaign_id: str, bundle_id: str) -> ImportResult:
        record = self.store.get_import_bundle(campaign_id, bundle_id)
        graph = self.store.get_import_graph(campaign_id, bundle_id) if record else None
        if record is None or graph is None:
            raise NotFoundError("import_bundle", bundle_id)
        nodes, edges = graph
        return ImportResult(
            created=False, bundle=ImportedBundleRecord.model_validate(record),
            nodes=[ImportedLineageNode.model_validate(node) for node in nodes],
            edges=[ImportedLineageEdge.model_validate(edge) for edge in edges],
        )

    def get_imported_passport(self, campaign_id: str, bundle_id: str) -> PortableLineagePassport:
        result = self.get_imported_bundle(campaign_id, bundle_id)
        return passport_for(result)

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def create_run(self, payload: RunCreate | dict[str, Any]) -> dict[str, Any]:
        if isinstance(payload, RunCreate):
            data = payload.model_dump()
        else:
            data = RunCreate.model_validate(payload).model_dump()

        campaign_id = data["campaign_id"]
        if not self.store.has_campaign(campaign_id):
            raise NotFoundError("campaign", campaign_id)

        run_id = _new_id("run")
        now = _utc_now_iso()
        dry_run = bool(data.get("dry_run", True))
        run_live = bool(data.get("run_live", False))
        budget_mode = data.get("budget_mode") or DEFAULT_BUDGET_MODE
        prompt = data.get("prompt")

        live_requested = run_live and not dry_run

        # Determine initial status. Dry-run (the default) and any non-live
        # request never contact a provider. Live requests start in
        # ``live_running`` and transition to a terminal live status once the
        # bridge returns.
        if live_requested:
            status = RUN_STATUS_LIVE_RUNNING
        else:
            status = RUN_STATUS_DRY_RUN_CREATED

        links = {
            "self": f"/runs/{run_id}",
            "attempts": f"/runs/{run_id}/attempts",
            "assets": f"/runs/{run_id}/assets",
            "manifest": f"/runs/{run_id}/manifest",
            "campaign": f"/campaigns/{campaign_id}",
        }

        record = RunRecord(
            run_id=run_id,
            campaign_id=campaign_id,
            status=status,
            prompt=prompt,
            budget_mode=budget_mode,
            # PS-008 never claims a live run executed. For PS-009 live runs
            # the dry_run flag stays False here so the record honestly reflects
            # that a live path was requested.
            dry_run=not live_requested,
            run_live=run_live,
            selected_provider=None,
            selected_model=None,
            api_method=None,
            job_type=LIVE_JOB_TYPE if live_requested else None,
            fallback_used=False,
            attempt_count=0,
            asset_count=0,
            manifest_uri=None,
            prompt_packet_ref=None,
            attempt_ledger_ref=None,
            provider_note_ref=None,
            created_at=now,
            started_at=now if live_requested else None,
            finished_at=None,
            links=links,
        )

        stored = self.store.create_run(run_id, record.model_dump())

        # Live execution hook (PS-009). Only entered when run_live is true and
        # dry_run is false. The dry-run path below this block is completely
        # untouched from PS-008: no provider, no B2, no Genblaze, no fake media.
        if live_requested:
            stored = self._execute_live_and_apply(
                run_id=run_id,
                campaign_id=campaign_id,
                prompt=prompt,
                budget_mode=budget_mode,
            )
            response = dict(stored)
            selected_provider = response.get("selected_provider")
            fallback_used = response.get("fallback_used") or False
            attempt_count = response.get("attempt_count") or 0
            return {
                "run_id": run_id,
                "campaign_id": campaign_id,
                "status": response.get("status"),
                "selected_provider": selected_provider,
                "fallback_used": fallback_used,
                "attempt_count": attempt_count,
                "links": links,
                "run": response,
            }

        response = dict(stored)
        response["note"] = (
            "Dry-run run created. No provider was called, no B2 upload "
            "occurred, no Genblaze manifest was written, and no media was "
            "generated."
        )
        return {
            "run_id": run_id,
            "campaign_id": campaign_id,
            "status": status,
            "selected_provider": None,
            "fallback_used": False,
            "attempt_count": 0,
            "links": links,
            "run": response,
        }

    def get_run(self, run_id: str) -> dict[str, Any]:
        record = self.store.get_run(run_id)
        if record is None:
            raise NotFoundError("run", run_id)
        # Refresh derived counts so they always reflect current sub-resources.
        record = dict(record)
        record["attempt_count"] = len(self.store.list_attempts(run_id))
        record["asset_count"] = len(self.store.list_assets(run_id))
        self.store.update_run(run_id, {
            "attempt_count": record["attempt_count"],
            "asset_count": record["asset_count"],
        })
        return {"run": record}

    # ------------------------------------------------------------------
    # Run sub-resources
    # ------------------------------------------------------------------

    def get_run_attempts(self, run_id: str) -> dict[str, Any]:
        if not self.store.has_run(run_id):
            raise NotFoundError("run", run_id)
        attempts = self.store.list_attempts(run_id)
        # Defensive: never serve a compact attempt. If any stored attempt lost
        # a required field, report it loudly instead of pretending it is valid.
        for index, attempt in enumerate(attempts):
            missing = _validate_attempt_shape(attempt)
            if missing:
                raise RuntimeError(
                    f"Stored attempt {run_id}[{index}] is missing required "
                    f"PS-006 fields: {missing}"
                )
        return {
            "run_id": run_id,
            "attempt_count": len(attempts),
            "attempts": attempts,
            "note": (
                "No provider attempts recorded. Dry-run runs carry an empty "
                "attempt ledger and never pretend a provider executed."
            ) if not attempts else None,
        }

    def get_run_assets(self, run_id: str) -> dict[str, Any]:
        if not self.store.has_run(run_id):
            raise NotFoundError("run", run_id)
        assets = self.store.list_assets(run_id)
        return {
            "run_id": run_id,
            "asset_count": len(assets),
            "assets": assets,
            "note": (
                "No assets recorded. Dry-run runs carry no generated media "
                "and never fabricate an asset reference."
            ) if not assets else None,
        }

    def get_run_manifest(self, run_id: str) -> dict[str, Any]:
        if not self.store.has_run(run_id):
            raise NotFoundError("run", run_id)
        stored = self.store.get_manifest(run_id)
        if stored is None:
            # Clear not-ready response. No crash.
            record = ManifestRecord(
                run_id=run_id,
                ready=False,
                asset_count=len(self.store.list_assets(run_id)),
                not_ready_reason=(
                    "No manifest has been written for this run yet. Dry-run "
                    "runs never produce a manifest; live runs produce a "
                    "manifest only after the PS-007 B2 + Genblaze pipeline "
                    "stores artifacts."
                ),
            )
            return record.model_dump()
        stored = dict(stored)
        stored["ready"] = True
        return stored

    # ------------------------------------------------------------------
    # Registration helpers (used by later slices to attach real evidence)
    # ------------------------------------------------------------------

    def register_attempt(self, run_id: str, attempt: AttemptRecord | dict[str, Any]) -> None:
        """Attach a real provider attempt to a run.

        Validates the PS-006 20-field shape. Later slices call this after the
        PS-007 router returns. Not used by the dry-run path.
        """
        if not self.store.has_run(run_id):
            raise NotFoundError("run", run_id)
        data = (
            attempt.model_dump() if isinstance(attempt, AttemptRecord) else dict(attempt)
        )
        missing = _validate_attempt_shape(data)
        if missing:
            raise ValueError(
                f"Attempt is missing required PS-006 fields: {missing}"
            )
        self.store.add_attempt(run_id, data)

    def register_asset(self, run_id: str, asset: AssetRecord | dict[str, Any]) -> None:
        """Attach a real generated/stored asset to a run.

        Later slices call this after B2 + Genblaze storage. Not used by the
        dry-run path.
        """
        if not self.store.has_run(run_id):
            raise NotFoundError("run", run_id)
        data = asset.model_dump() if isinstance(asset, AssetRecord) else dict(asset)
        self.store.add_asset(run_id, data)

    def register_manifest(self, run_id: str, manifest: ManifestRecord | dict[str, Any]) -> None:
        """Attach manifest metadata to a run.

        Later slices call this after the PS-007 manifest write/read-back/verify.
        Not used by the dry-run path.
        """
        if not self.store.has_run(run_id):
            raise NotFoundError("run", run_id)
        data = (
            manifest.model_dump()
            if isinstance(manifest, ManifestRecord)
            else dict(manifest)
        )
        data["run_id"] = run_id
        data["ready"] = True
        self.store.set_manifest(run_id, data)

    # ------------------------------------------------------------------
    # PS-010 archive / rehydrate
    # ------------------------------------------------------------------

    def archive_run(self, run_id: str, *, campaign_id: str | None = None) -> dict[str, Any]:
        """Build a durable run-archive dict for ``run_id`` (PS-010).

        Reads the run and its sub-resources through the normal readback methods
        and returns an archive dict carrying the full PS-006 attempt ledger,
        asset refs, manifest metadata, and honest on-disk artifact metadata.
        Never calls a provider and never writes media. Storage of the returned
        archive to B2 is a separate, explicit step
        (see :func:`proofstudio.api.archive.store_run_archive_with_genblaze`).
        """
        return archive_module.build_run_archive(
            self, run_id, campaign_id=campaign_id
        )

    def rehydrate_run_from_archive(
        self, source: Any, *, source_kind: str = "auto"
    ) -> dict[str, Any]:
        """Rehydrate a run from an archive into this service's store (PS-010).

        ``source`` may be a parsed archive dict, a local file path, or raw JSON
        bytes read from B2. Restores campaign/run/attempts/assets/manifest
        metadata using plain store writes. Never calls ``create_run``, never
        calls the live bridge, never calls a provider, and never writes media.
        """
        return archive_module.rehydrate_run_from_archive(
            self, source, source_kind=source_kind
        )

    def clear_store_for_test(self) -> None:
        """Replace the backing store with a fresh empty one.

        Test-only convenience for PS-010: lets a smoke simulate memory loss
        (fresh process) and then rehydrate from a durable archive. Clearly
        named so it is never used in a live path.
        """
        self.store = InMemoryStore()

    # ------------------------------------------------------------------
    # PS-011 Review Room / Provenance Passport
    # ------------------------------------------------------------------

    def get_run_passport(
        self,
        run_id: str,
        *,
        archive_evidence: dict[str, Any] | None = None,
        source: str = "auto",
    ) -> dict[str, Any]:
        """Build a Provenance Passport for ``run_id`` (PS-011).

        Reads the run, its campaign, attempts, assets, and manifest metadata
        through the normal readback methods (``get_run`` /
        ``get_run_attempts`` / ``get_run_assets`` / ``get_run_manifest``) and
        folds them into a structured Review Room / Provenance Passport object.

        Optional ``archive_evidence`` may be supplied by the caller to populate
        the ``archive_and_rehydration`` section with real durable-archive /
        rehydration proof (e.g. the result of a PS-010 rehydrate). When it is
        omitted that section is explicitly ``not_available`` rather than
        fabricated.

        This method never calls a live provider, never reruns generation,
        never writes media, and never fakes manifest verification or archive
        proof.
        """
        if not self.store.has_run(run_id):
            durable_passport = durable_passport_module.try_rehydrate_passport(
                self, run_id
            )
            if durable_passport is not None:
                return durable_passport

            # PS-025: narrow public durable passport unlock. Only the single
            # verified golden demo run_id resolves here, from checked-in
            # evidence only. No B2 read, no provider call, no broad reads.
            golden_passport = durable_passport_module.try_golden_demo_passport(
                self, run_id
            )
            if golden_passport is not None:
                return golden_passport

        run_envelope = self.get_run(run_id)
        run_record = dict(run_envelope["run"])
        campaign_id = run_record.get("campaign_id") or ""
        campaign_record: dict[str, Any] = {}
        if campaign_id and self.store.has_campaign(campaign_id):
            campaign_record = dict(
                self.get_campaign(campaign_id).get("campaign") or {}
            )
        attempts = list(self.get_run_attempts(run_id).get("attempts") or [])
        assets = list(self.get_run_assets(run_id).get("assets") or [])
        manifest = dict(self.get_run_manifest(run_id))
        return passport_module.build_provenance_passport(
            run=run_record,
            campaign=campaign_record,
            attempts=attempts,
            assets=assets,
            manifest=manifest,
            archive_evidence=archive_evidence,
            source=source,
        )

    # ------------------------------------------------------------------
    # Internal: PS-009 live bridge wiring
    # ------------------------------------------------------------------

    def _execute_live_and_apply(
        self,
        *,
        run_id: str,
        campaign_id: str,
        prompt: str | None,
        budget_mode: str,
    ) -> dict[str, Any]:
        """Run the PS-009 live bridge and apply its result to the run record.

        This is the single PS-009 wiring point that connects the service layer
        to the PS-007 provider-router + B2 + Genblaze pipeline. It is only
        entered from :meth:`create_run` when ``run_live`` is true and
        ``dry_run`` is false. It never fakes success: the run record's status
        is derived directly from the bridge result.

        PS-035b: the default-off governance gate (``govern_live_run``) is
        honored here in the service layer before the live bridge is ever
        called. ``run_live=True`` alone is not sufficient;
        ``PROOFSTUDIO_LIVE_RUNS_ENABLED``, ``PROOFSTUDIO_PAID_RUN_APPROVED``,
        a non-zero ``PROOFSTUDIO_COST_CAP_USD``, and a non-free-only
        ``budget_mode`` must all permit execution. This honors the documented
        ``PROOFSTUDIO_RUN_LIVE_DEFAULT=false`` truthfully by superseding it
        with the enforced ``PROOFSTUDIO_LIVE_RUNS_ENABLED`` gate. No provider
        is called and no B2 access occurs when the gate blocks; the live
        bridge re-checks the same gate authoritatively.
        """
        # PS-035b governance gate (service-layer honor). Blocking here avoids
        # constructing providers when the governance flags do not permit a
        # live/paid run. The live bridge re-checks authoritatively.
        allowed, blocked_reason = govern_live_run(budget_mode=budget_mode)
        if not allowed:
            patch: dict[str, Any] = {
                "status": RUN_STATUS_LIVE_BLOCKED,
                "dry_run": False,
                "blocked_reason": blocked_reason,
                "selected_provider": None,
                "selected_model": None,
                "api_method": None,
                "job_type": LIVE_JOB_TYPE,
                "fallback_used": False,
                "attempts": [],
                "assets": [],
                "manifest_uri": None,
                "manifest_hash": None,
                "finished_at": _utc_now_iso(),
                "truth_boundary": LIVE_TRUTH_BOUNDARY,
                "error": None,
            }
            updated = self.store.update_run(run_id, patch)
            if updated is None:
                raise RuntimeError(f"Run {run_id} vanished during live execution.")
            updated["attempt_count"] = 0
            updated["asset_count"] = 0
            self.store.update_run(run_id, {"attempt_count": 0, "asset_count": 0})
            return updated

        campaign_record = self.store.get_campaign(campaign_id) or {}

        live_result = execute_live_run(
            campaign=campaign_record,
            prompt=prompt or "",
            budget_mode=budget_mode,
            output_dir=Path(self._live_output_dir),
            b2_prefix=self._live_b2_prefix,
            run_id=run_id,
        )

        status = self._live_status_from_result(live_result)
        attempts = list(live_result.get("attempts") or [])

        # Validate attempt shape at registration time so a compact attempt can
        # never silently enter the store. The live bridge produces full
        # ProviderAttempt.to_dict() records, so this is defensive.
        for index, attempt in enumerate(attempts):
            missing = _validate_attempt_shape(attempt)
            if missing:
                raise RuntimeError(
                    f"Live bridge returned attempt {run_id}[{index}] missing "
                    f"required PS-006 fields: {missing}"
                )

        if attempts:
            self.store.set_attempts(run_id, attempts)

        assets = list(live_result.get("assets") or [])
        if assets:
            self.store.set_assets(run_id, assets)

        manifest_uri = live_result.get("manifest_uri")
        if status == RUN_STATUS_LIVE_COMPLETED and manifest_uri:
            self.store.set_manifest(
                run_id,
                {
                    "run_id": run_id,
                    "ready": True,
                    "manifest_uri": manifest_uri,
                    "manifest_hash": live_result.get("manifest_hash"),
                    "in_memory_manifest_verify": (
                        live_result.get("in_memory_manifest_verify")
                    ),
                    "stored_manifest_verify": (
                        live_result.get("stored_manifest_verify")
                    ),
                    "transfer_failures": list(
                        live_result.get("transfer_failures") or []
                    ),
                    "stored_transfer_failures": list(
                        live_result.get("stored_transfer_failures") or []
                    ),
                    "asset_count": len(assets),
                },
            )

        patch: dict[str, Any] = {
            "status": status,
            "dry_run": False,
            "selected_provider": live_result.get("selected_provider"),
            "selected_model": live_result.get("selected_model"),
            "api_method": live_result.get("api_method"),
            "job_type": live_result.get("job_type") or LIVE_JOB_TYPE,
            "fallback_used": bool(live_result.get("fallback_used")),
            "attempts": attempts,
            "assets": assets,
            "manifest_uri": manifest_uri,
            "manifest_hash": live_result.get("manifest_hash"),
            "in_memory_manifest_verify": live_result.get(
                "in_memory_manifest_verify"
            ),
            "stored_manifest_verify": live_result.get("stored_manifest_verify"),
            "transfer_failures": list(
                live_result.get("transfer_failures") or []
            ),
            "stored_transfer_failures": list(
                live_result.get("stored_transfer_failures") or []
            ),
            "local_image": live_result.get("local_image"),
            "local_prompt_packet": live_result.get("local_prompt_packet"),
            "local_attempt_ledger": live_result.get("local_attempt_ledger"),
            "local_provider_note": live_result.get("local_provider_note"),
            "prompt_packet_ref": live_result.get("local_prompt_packet"),
            "attempt_ledger_ref": live_result.get("local_attempt_ledger"),
            "provider_note_ref": live_result.get("local_provider_note"),
            "truth_boundary": live_result.get("truth_boundary")
            or LIVE_TRUTH_BOUNDARY,
            "error": live_result.get("error"),
            "blocked_reason": live_result.get("blocked_reason"),
            "finished_at": _utc_now_iso(),
        }

        updated = self.store.update_run(run_id, patch)
        if updated is None:
            raise RuntimeError(f"Run {run_id} vanished during live execution.")

        # Refresh derived counts so the returned record matches the store.
        updated["attempt_count"] = len(self.store.list_attempts(run_id))
        updated["asset_count"] = len(self.store.list_assets(run_id))
        self.store.update_run(
            run_id,
            {
                "attempt_count": updated["attempt_count"],
                "asset_count": updated["asset_count"],
            },
        )
        return updated

    @staticmethod
    def _live_status_from_result(live_result: dict[str, Any]) -> str:
        bridge_status = (live_result.get("status") or "").strip()
        if bridge_status == "live_completed":
            return RUN_STATUS_LIVE_COMPLETED
        if bridge_status == "live_blocked":
            return RUN_STATUS_LIVE_BLOCKED
        return RUN_STATUS_LIVE_FAILED

    # ------------------------------------------------------------------
    # Internal: legacy PS-008 live hook placeholder (retained for reference)
    # ------------------------------------------------------------------

    def _record_live_not_supported_note(self, run_id: str) -> None:
        """Record an honest note that live execution was not wired in PS-008.

        Retained for historical reference. PS-009 replaces this no-op with
        :meth:`_execute_live_and_apply`, which connects the service layer to
        the PS-007 provider-router + B2 + Genblaze pipeline. This method is no
        longer invoked by :meth:`create_run`.
        """
        self.store.update_run(run_id, {
            "started_at": None,
            "finished_at": None,
        })


def create_default_service() -> ProofStudioService:
    """Construct the default API service.

    The normal result is a fresh empty in-memory store. Free Render staging may
    explicitly reconstruct the checked-in golden fixture through the exact
    ``PROOFSTUDIO_FIXTURES_FROZEN=true`` gate.
    """
    from proofstudio.api.frozen_staging_fixture import (
        maybe_seed_frozen_staging_fixture,
    )

    service = ProofStudioService()
    return maybe_seed_frozen_staging_fixture(service)


__all__ = [
    "ProofStudioService",
    "NotFoundError",
    "create_default_service",
    "detect_git_branch",
    "APP_VERSION",
    "PROOF_VERSION",
    "FRAMEWORK_MODE",
    "CAPABILITIES",
    "DEFAULT_BUDGET_MODE",
    "DEFAULT_LIVE_OUTPUT_DIR",
    "DEFAULT_LIVE_B2_PREFIX",
    "archive_module",
    "passport_module",
]
