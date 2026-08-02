# 04 — B2 Storage Contract

## B2 role

Backblaze B2 is the durable system of record.

## MVP object layout

    campaigns/{campaign_id}/brief.json
    campaigns/{campaign_id}/runs/{run_id}/manifest.json
    campaigns/{campaign_id}/runs/{run_id}/assets/{asset_name}
    campaigns/{campaign_id}/runs/{run_id}/thumbs/{thumbnail_name}
    campaigns/{campaign_id}/runs/{run_id}/logs/pipeline.jsonl
    campaigns/{campaign_id}/exports/media-kit.zip

## Rules

- Do not store secrets in B2 metadata.
- Use object prefixes for organization.
- Use sidecar JSON files for rich metadata.
- Use presigned URLs for private asset access.
- B2 must be visible in the UI through object keys, manifest URIs, and storage status.
