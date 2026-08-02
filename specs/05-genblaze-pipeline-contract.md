# 05 — Genblaze Pipeline Contract

## Genblaze role

Genblaze is the orchestration and provenance layer.

## MVP pipeline stages

1. Parse campaign brief
2. Generate creative plan
3. Generate media asset
4. Create thumbnail or preview
5. Store outputs in B2
6. Generate manifest
7. Verify manifest
8. Link variants through parent_run_id

## Judge-visible evidence

The UI must show:

- pipeline steps
- provider/model
- prompt
- parameters where available
- SHA-256 hash
- manifest URI
- verification status
- parent/variant lineage
