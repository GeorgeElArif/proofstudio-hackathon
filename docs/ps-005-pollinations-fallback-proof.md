# PS-005 Pollinations Fallback Runtime Proof

## Status

Accepted pass.

PS-005 proved a no-key emergency visual fallback provider path for ProofStudio.

## Proof Summary

- ok: True
- provider: pollinations
- selected_model: pollinations-image-default
- api_method: pollinations-image-get
- job_type: image_generation
- budget_mode: free-only
- image_mime_type: image/jpeg
- image_sha256: 907020f9337f2e12e0b9ae9f2586595b18959e72ad31915706fb1514d0b70cc8
- attempt_count: 1
- run_id: e0ed42e6-f588-4f67-832f-23d643500e30
- manifest_hash: 6227cc16c6ebc1cf0423a0f2d78385d0afa862d53883e16490fd8daf3ac2e2b7
- manifest_uri: https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-005/manifests/e0ed42e6-f588-4f67-832f-23d643500e30.json
- in_memory_manifest_verify: True
- stored_manifest_verify: True
- transfer_failures: []
- stored_transfer_failures: []
- asset_count: 4

## What Passed

- Pollinations returned valid image bytes without an API key.
- The script detected the actual image MIME from bytes.
- Generated image was saved locally with the correct extension.
- Provider attempt ledger was created.
- Prompt packet was saved locally.
- Provider note was saved locally.
- Generated image was uploaded to Backblaze B2.
- Prompt packet was uploaded to Backblaze B2.
- Provider note was uploaded to Backblaze B2.
- Attempt ledger was uploaded to Backblaze B2.
- Genblaze manifest was written to B2.
- Stored manifest was read back.
- Manifest verification passed.
- Transfer failures were empty.

## B2 / Genblaze Evidence

Manifest URI:

    https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-005/manifests/e0ed42e6-f588-4f67-832f-23d643500e30.json

Manifest hash:

    6227cc16c6ebc1cf0423a0f2d78385d0afa862d53883e16490fd8daf3ac2e2b7

Generated image SHA-256:

    907020f9337f2e12e0b9ae9f2586595b18959e72ad31915706fb1514d0b70cc8

## Assets Stored

[
  {
    "asset_id": "7808b558-f9f4-4085-a906-fa8015da49e7",
    "url": "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-005/assets/7e/63/7e63d5604a9ac2b0b29b48f8524bbb9ff19d5ce26ea8091e20240f8521c8c708.md",
    "media_type": "text/markdown",
    "sha256": "7e63d5604a9ac2b0b29b48f8524bbb9ff19d5ce26ea8091e20240f8521c8c708",
    "size_bytes": 2353,
    "metadata": {
      "proofstudio_test": "ps-005",
      "artifact_type": "provider_note",
      "provider": "pollinations",
      "model": "pollinations-image-default"
    }
  },
  {
    "asset_id": "91d69eb5-56a2-4e5f-a8ac-b2eb10b8f001",
    "url": "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-005/assets/3f/5d/3f5dbce0764efbab5807187b5227142dd0a7782102c7302dabfffa029ea5e236.json",
    "media_type": "application/json",
    "sha256": "3f5dbce0764efbab5807187b5227142dd0a7782102c7302dabfffa029ea5e236",
    "size_bytes": 2594,
    "metadata": {
      "proofstudio_test": "ps-005",
      "artifact_type": "visual_prompt_packet",
      "provider": "pollinations",
      "model": "pollinations-image-default"
    }
  },
  {
    "asset_id": "9d1bdf3f-0c2e-4c3b-9a4b-d000aadd91fa",
    "url": "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-005/assets/90/70/907020f9337f2e12e0b9ae9f2586595b18959e72ad31915706fb1514d0b70cc8.jpg",
    "media_type": "image/jpeg",
    "sha256": "907020f9337f2e12e0b9ae9f2586595b18959e72ad31915706fb1514d0b70cc8",
    "size_bytes": 56245,
    "metadata": {
      "proofstudio_test": "ps-005",
      "artifact_type": "pollinations_visual_asset",
      "provider": "pollinations",
      "model": "pollinations-image-default",
      "api_method": "pollinations-image-get"
    }
  },
  {
    "asset_id": "bac4db59-9f4c-4de6-88fc-c90c0f14efd1",
    "url": "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-005/assets/b9/61/b96141b1956a6dab0da8668e2a140a24308a0a4ca8b57f7bf7d16b3af492d78a.json",
    "media_type": "application/json",
    "sha256": "b96141b1956a6dab0da8668e2a140a24308a0a4ca8b57f7bf7d16b3af492d78a",
    "size_bytes": 2443,
    "metadata": {
      "proofstudio_test": "ps-005",
      "artifact_type": "provider_attempt_ledger",
      "provider": "pollinations"
    }
  }
]

## Product Meaning

This proves that ProofStudio can preserve campaign continuity through a no-key fallback provider while keeping the same B2 + Genblaze provenance pipeline.

This supports:

- Free-only mode
- Provider fallback resilience
- Failure-as-Proof Timeline
- Why This Provider?
- Model Audition Board
- Export Pack continuity
- B2 system of record
- Genblaze manifest verification

## Truth Boundary

Pollinations is a fallback provider, not the premium final visual provider.

This run proves provider execution, storage, manifest generation, accurate byte-level media metadata, and byte-level verification.

It does not prove semantic truth, legal authenticity, C2PA authenticity, or human authorship.
