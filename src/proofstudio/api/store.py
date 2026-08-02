"""In-memory store for the PS-008 backend API skeleton.

This is a process-local, non-durable store. It exists so the API/service layer
can demonstrate the full product-concept lifecycle (campaign -> run ->
attempts / assets / manifest) without a production database and without any
network calls.

Required operations (see specs/16-ps-008-backend-api-skeleton.md section 7):

- create campaign
- get campaign
- create run
- get run
- list attempts for run
- list assets for run
- get manifest metadata for run

Design notes:

- Pure stdlib. No network or persistence. Imported-bundle mutations use one
  process-local lock and copy-on-write dictionaries.
- All keys are strings (campaign_id / run_id).
- ``get_*`` methods return ``None`` for missing resources rather than raising,
  so the service layer can translate misses into clean 404-style responses.
- The store never fabricates attempts, assets, or manifests. Dry-run runs have
  empty attempt/asset lists and no manifest until a later slice writes one.
"""

from __future__ import annotations

from threading import RLock
from typing import Any

from proofstudio.api.genblaze_external_adapter import ImportCandidate, ImportValidationError

GOLDEN_NAMESPACE_PREFIXES = ("golden-", "golden_", "ps_golden", "run_golden")


class InMemoryStore:
    """Process-local store keyed by campaign_id / run_id.

    State is held in plain dicts so it is trivially JSON-serializable for
    debugging and snapshotting in smoke transcripts.
    """

    def __init__(self) -> None:
        self._campaigns: dict[str, dict[str, Any]] = {}
        self._runs: dict[str, dict[str, Any]] = {}
        # run_id -> list[attempt dict]
        self._attempts: dict[str, list[dict[str, Any]]] = {}
        # run_id -> list[asset dict]
        self._assets: dict[str, list[dict[str, Any]]] = {}
        # run_id -> manifest metadata dict
        self._manifests: dict[str, dict[str, Any]] = {}
        # PS-041D imported proof overlay. Atomicity and idempotency are only
        # process-local; restart and multi-worker durability are not claimed.
        self._import_lock = RLock()
        self._import_bundles: dict[str, dict[str, Any]] = {}
        self._import_nodes: dict[str, dict[str, Any]] = {}
        self._import_edges: dict[str, dict[str, Any]] = {}
        self._bundle_fingerprint_index: dict[str, str] = {}
        self._source_fingerprint_index: dict[tuple[str, str], tuple[str, str]] = {}
        self._bundle_campaign_binding: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Campaign
    # ------------------------------------------------------------------

    def create_campaign(self, campaign_id: str, record: dict[str, Any]) -> dict[str, Any]:
        self._campaigns[campaign_id] = dict(record)
        return dict(self._campaigns[campaign_id])

    def get_campaign(self, campaign_id: str) -> dict[str, Any] | None:
        record = self._campaigns.get(campaign_id)
        return dict(record) if record is not None else None

    def has_campaign(self, campaign_id: str) -> bool:
        return campaign_id in self._campaigns

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def create_run(self, run_id: str, record: dict[str, Any]) -> dict[str, Any]:
        self._runs[run_id] = dict(record)
        # Ensure sub-resource buckets exist so later reads are predictable.
        self._attempts.setdefault(run_id, [])
        self._assets.setdefault(run_id, [])
        return dict(self._runs[run_id])

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        record = self._runs.get(run_id)
        return dict(record) if record is not None else None

    def has_run(self, run_id: str) -> bool:
        return run_id in self._runs

    def update_run(self, run_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
        record = self._runs.get(run_id)
        if record is None:
            return None
        record.update(patch)
        return dict(record)

    # ------------------------------------------------------------------
    # Attempts (PS-006 20-field records, only for real provider attempts)
    # ------------------------------------------------------------------

    def add_attempt(self, run_id: str, attempt: dict[str, Any]) -> list[dict[str, Any]]:
        bucket = self._attempts.setdefault(run_id, [])
        bucket.append(dict(attempt))
        return [dict(a) for a in bucket]

    def set_attempts(
        self, run_id: str, attempts: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Replace the full attempt ledger for a run.

        PS-009 uses this when the live bridge returns the complete PS-006
        attempt ledger in one shot. Replaces any prior attempts so a live
        re-run of the same run id cannot mix stale and fresh evidence.
        """
        self._attempts[run_id] = [dict(a) for a in attempts]
        return [dict(a) for a in self._attempts[run_id]]

    def list_attempts(self, run_id: str) -> list[dict[str, Any]]:
        return [dict(a) for a in self._attempts.get(run_id, [])]

    # ------------------------------------------------------------------
    # Assets
    # ------------------------------------------------------------------

    def add_asset(self, run_id: str, asset: dict[str, Any]) -> list[dict[str, Any]]:
        bucket = self._assets.setdefault(run_id, [])
        bucket.append(dict(asset))
        return [dict(a) for a in bucket]

    def set_assets(
        self, run_id: str, assets: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Replace the full asset list for a run.

        PS-009 uses this when the live bridge has captured the complete set of
        stored asset references (generated image, prompt packet, attempt
        ledger, provider note) from the Genblaze manifest.
        """
        self._assets[run_id] = [dict(a) for a in assets]
        return [dict(a) for a in self._assets[run_id]]

    def list_assets(self, run_id: str) -> list[dict[str, Any]]:
        return [dict(a) for a in self._assets.get(run_id, [])]

    # ------------------------------------------------------------------
    # Manifest metadata
    # ------------------------------------------------------------------

    def set_manifest(self, run_id: str, manifest: dict[str, Any]) -> dict[str, Any]:
        self._manifests[run_id] = dict(manifest)
        return dict(self._manifests[run_id])

    def get_manifest(self, run_id: str) -> dict[str, Any] | None:
        record = self._manifests.get(run_id)
        return dict(record) if record is not None else None

    # ------------------------------------------------------------------
    # PS-041D imported lineage overlay
    # ------------------------------------------------------------------

    def commit_import_candidate(
        self, candidate: ImportCandidate, *, fail_before_commit: bool = False
    ) -> tuple[bool, dict[str, Any]]:
        """Atomically bind a fully validated candidate using copy-on-write."""
        bundle = candidate.bundle
        with self._import_lock:
            if bundle.campaign_id not in self._campaigns:
                raise ImportValidationError("campaign_not_found", 404)
            existing_campaign = self._bundle_campaign_binding.get(bundle.bundle_fingerprint)
            if existing_campaign is not None and existing_campaign != bundle.campaign_id:
                raise ImportValidationError("import_conflict", 409)
            existing_bundle_id = self._bundle_fingerprint_index.get(bundle.bundle_fingerprint)
            if existing_bundle_id is not None:
                existing = self._import_bundles[existing_bundle_id]
                if existing.get("campaign_id") != bundle.campaign_id:
                    raise ImportValidationError("import_conflict", 409)
                return False, dict(existing)
            for source_key, content_fp in candidate.source_fingerprints.items():
                _, source_id = source_key
                if source_id.lower().startswith(GOLDEN_NAMESPACE_PREFIXES):
                    raise ImportValidationError("golden_namespace_conflict", 409)
                prior = self._source_fingerprint_index.get(source_key)
                if prior is not None and prior[0] != content_fp:
                    raise ImportValidationError("import_conflict", 409)
                if prior is not None and prior[1] != bundle.campaign_id:
                    raise ImportValidationError("import_conflict", 409)
            for node in candidate.nodes:
                if node.campaign_id != bundle.campaign_id:
                    raise ImportValidationError("cross_campaign_lineage", 409)
                if node.source_id.lower().startswith(GOLDEN_NAMESPACE_PREFIXES):
                    raise ImportValidationError("golden_namespace_conflict", 409)
            if fail_before_commit:
                raise RuntimeError("injected_pre_commit_failure")
            bundles = dict(self._import_bundles)
            nodes = dict(self._import_nodes)
            edges = dict(self._import_edges)
            fingerprint_index = dict(self._bundle_fingerprint_index)
            source_index = dict(self._source_fingerprint_index)
            bindings = dict(self._bundle_campaign_binding)
            bundles[bundle.bundle_id] = bundle.model_dump(mode="json")
            nodes.update({node.node_id: node.model_dump(mode="json") for node in candidate.nodes})
            edges.update({edge.edge_id: edge.model_dump(mode="json") for edge in candidate.edges})
            fingerprint_index[bundle.bundle_fingerprint] = bundle.bundle_id
            bindings[bundle.bundle_fingerprint] = bundle.campaign_id
            for source_key, content_fp in candidate.source_fingerprints.items():
                source_index[source_key] = (content_fp, bundle.campaign_id)
            self._import_bundles = bundles
            self._import_nodes = nodes
            self._import_edges = edges
            self._bundle_fingerprint_index = fingerprint_index
            self._source_fingerprint_index = source_index
            self._bundle_campaign_binding = bindings
            return True, dict(bundles[bundle.bundle_id])

    def list_import_bundles(self, campaign_id: str, limit: int = 50) -> list[dict[str, Any]]:
        records = [dict(record) for record in self._import_bundles.values() if record.get("campaign_id") == campaign_id]
        return sorted(records, key=lambda record: (record["bundle_fingerprint"], record["bundle_id"]))[:limit]

    def get_import_bundle(self, campaign_id: str, bundle_id: str) -> dict[str, Any] | None:
        record = self._import_bundles.get(bundle_id)
        if record is None or record.get("campaign_id") != campaign_id:
            return None
        return dict(record)

    def get_import_graph(self, campaign_id: str, bundle_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]] | None:
        bundle = self.get_import_bundle(campaign_id, bundle_id)
        if bundle is None:
            return None
        nodes = [dict(self._import_nodes[node_id]) for node_id in bundle["node_ids"]]
        edges = [dict(self._import_edges[edge_id]) for edge_id in bundle["edge_ids"]]
        return nodes, edges

    def clear_import_campaign(self, campaign_id: str) -> None:
        """Test/smoke cleanup for state owned by one process-local campaign."""
        with self._import_lock:
            bundle_ids = {key for key, value in self._import_bundles.items() if value.get("campaign_id") == campaign_id}
            fingerprints = {value["bundle_fingerprint"] for key, value in self._import_bundles.items() if key in bundle_ids}
            self._import_bundles = {key: value for key, value in self._import_bundles.items() if key not in bundle_ids}
            self._import_nodes = {key: value for key, value in self._import_nodes.items() if value.get("campaign_id") != campaign_id}
            self._import_edges = {key: value for key, value in self._import_edges.items() if value.get("campaign_id") != campaign_id}
            self._bundle_fingerprint_index = {key: value for key, value in self._bundle_fingerprint_index.items() if key not in fingerprints}
            self._bundle_campaign_binding = {key: value for key, value in self._bundle_campaign_binding.items() if key not in fingerprints}
            self._source_fingerprint_index = {key: value for key, value in self._source_fingerprint_index.items() if value[1] != campaign_id}

    # ------------------------------------------------------------------
    # Introspection / debug
    # ------------------------------------------------------------------

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-serializable snapshot of the whole store.

        Used by the smoke transcript so the in-memory state is auditable.
        """
        return {
            "campaign_count": len(self._campaigns),
            "run_count": len(self._runs),
            "campaigns": {k: dict(v) for k, v in self._campaigns.items()},
            "runs": {k: dict(v) for k, v in self._runs.items()},
            "attempts": {k: [dict(a) for a in v] for k, v in self._attempts.items()},
            "assets": {k: [dict(a) for a in v] for k, v in self._assets.items()},
            "manifests": {k: dict(v) for k, v in self._manifests.items()},
            "import_bundle_count": len(self._import_bundles),
            "import_node_count": len(self._import_nodes),
            "import_edge_count": len(self._import_edges),
        }


__all__ = ["InMemoryStore"]
