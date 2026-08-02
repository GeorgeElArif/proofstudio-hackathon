# PS-004 Provider Router + Cloudflare Runtime Proof

## Status

Accepted pass.

PS-004 proved the first working free/cheap visual provider path for ProofStudio.

## Proof Summary

- ok: True
- provider: cloudflare-workers-ai
- selected_model: @cf/bytedance/stable-diffusion-xl-lightning
- api_method: workers-ai-run
- job_type: image_generation
- budget_mode: free-only
- image_mime_type: image/jpeg
- image_sha256: a9eddb25c27920ac0b0080c3b12fa8b742d6ceaef204790f0a3a45e3dcb7e87c
- attempt_count: 1
- run_id: aed1cef1-2a85-44be-ad7d-45aa68f2ff3a
- manifest_hash: c61934df83e267d54f831531ca968862e36730d34d9f40b733a5450a522a376f
- manifest_uri: https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-004/manifests/aed1cef1-2a85-44be-ad7d-45aa68f2ff3a.json
- in_memory_manifest_verify: True
- stored_manifest_verify: True
- transfer_failures: []
- stored_transfer_failures: []
- asset_count: 4

## What Passed

- Cloudflare Workers AI primary model returned image bytes.
- The script detected the actual image MIME from bytes before storing metadata.
- Provider attempt ledger was created.
- Generated image was saved locally.
- Prompt packet was saved locally.
- Provider note was saved locally.
- Attempt ledger was saved locally.
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

    https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-004/manifests/aed1cef1-2a85-44be-ad7d-45aa68f2ff3a.json

Manifest hash:

    c61934df83e267d54f831531ca968862e36730d34d9f40b733a5450a522a376f

Generated image SHA-256:

    a9eddb25c27920ac0b0080c3b12fa8b742d6ceaef204790f0a3a45e3dcb7e87c

## Assets Stored

[
  {
    "asset_id": "375e452f-2d32-47b1-8c81-adcb7fac76f5",
    "url": "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-004/assets/92/58/9258389b42699bfe4c0e755f32d73972db65102b687cdf65c317198cadfb7436.json",
    "media_type": "application/json",
    "sha256": "9258389b42699bfe4c0e755f32d73972db65102b687cdf65c317198cadfb7436",
    "size_bytes": 2388,
    "metadata": {
      "proofstudio_test": "ps-004",
      "artifact_type": "provider_attempt_ledger",
      "provider": "cloudflare-workers-ai"
    }
  },
  {
    "asset_id": "3ab61515-9d3d-4aef-a0e3-c043becfb5c1",
    "url": "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-004/assets/39/e7/39e7a698fa19982e67bf878ae49c3b2498e9952eb2178e98843d35a8b1ec8b5e.json",
    "media_type": "application/json",
    "sha256": "39e7a698fa19982e67bf878ae49c3b2498e9952eb2178e98843d35a8b1ec8b5e",
    "size_bytes": 2630,
    "metadata": {
      "proofstudio_test": "ps-004",
      "artifact_type": "visual_prompt_packet",
      "provider": "cloudflare-workers-ai",
      "model": "@cf/bytedance/stable-diffusion-xl-lightning"
    }
  },
  {
    "asset_id": "7e86651b-418a-4e63-9ef9-fdcc9054b49d",
    "url": "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-004/assets/2f/27/2f273db2674f5a41d7a38223118a3069309339bf3d31c9ec4b777363672c9e83.md",
    "media_type": "text/markdown",
    "sha256": "2f273db2674f5a41d7a38223118a3069309339bf3d31c9ec4b777363672c9e83",
    "size_bytes": 2182,
    "metadata": {
      "proofstudio_test": "ps-004",
      "artifact_type": "provider_note",
      "provider": "cloudflare-workers-ai",
      "model": "@cf/bytedance/stable-diffusion-xl-lightning"
    }
  },
  {
    "asset_id": "999b87b4-9720-4a10-bdea-ab365e3fb215",
    "url": "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-004/assets/a9/ed/a9eddb25c27920ac0b0080c3b12fa8b742d6ceaef204790f0a3a45e3dcb7e87c.jpg",
    "media_type": "image/jpeg",
    "sha256": "a9eddb25c27920ac0b0080c3b12fa8b742d6ceaef204790f0a3a45e3dcb7e87c",
    "size_bytes": 134027,
    "metadata": {
      "proofstudio_test": "ps-004",
      "artifact_type": "cloudflare_visual_asset",
      "provider": "cloudflare-workers-ai",
      "model": "@cf/bytedance/stable-diffusion-xl-lightning",
      "api_method": "workers-ai-run"
    }
  }
]

## Product Meaning

This proves that ProofStudio can move beyond one provider and route visual generation through a free/cheap provider while preserving the same B2 + Genblaze provenance pipeline.

This directly supports:

- Credit-Aware Provider Router
- Failure-as-Proof Timeline
- Why This Provider?
- Cost Ledger
- Provenance Passport
- Model Audition Board
- B2 system of record
- Genblaze manifest verification

## Truth Boundary

This run proves provider execution, storage, manifest generation, accurate byte-level media metadata, and byte-level verification.

It does not prove semantic truth, legal authenticity, C2PA authenticity, or human authorship.
