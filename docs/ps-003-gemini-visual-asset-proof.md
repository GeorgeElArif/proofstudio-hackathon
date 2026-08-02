# PS-003 Gemini Visual Asset Proof

## Goal

Generate a real visual ProofStudio campaign asset through Gemini visual/image APIs, then store and verify it through Backblaze B2 and Genblaze.

## Proof

~~~text
ProofStudio visual prompt
→ Gemini visual/image generation attempt
→ generated image saved locally
→ image + prompt packet + provider note uploaded to B2
→ Genblaze manifest written to B2
→ stored manifest read back and verified
→ zero transfer failures
~~~

## Required environment variables

- B2_KEY_ID
- B2_APP_KEY
- B2_BUCKET
- B2_REGION
- GEMINI_API_KEY

## Default model attempt order

~~~text
generate_content:
1. models/gemini-2.5-flash-image
2. models/gemini-3.1-flash-image
3. models/gemini-3-pro-image

generate_images fallback:
1. models/imagen-4.0-fast-generate-001
2. models/imagen-4.0-generate-001
~~~

## Run

~~~bash
source .venv/bin/activate
python scripts/ps003_gemini_visual_asset_proof.py
~~~

## Local outputs

~~~text
/tmp/proofstudio-ps-003/
~~~

## Acceptance criteria

A real pass must show:

~~~json
{
  "ok": true,
  "in_memory_manifest_verify": true,
  "stored_manifest_verify": true,
  "transfer_failures": [],
  "stored_transfer_failures": []
}
~~~

## Truth boundary

This proves visual generation and asset-storage integrity. It does not prove semantic truth, legal authenticity, or C2PA authenticity.

## Developer API note

In Gemini Developer API mode, the `negativePrompt` and `enhancePrompt` config fields are not accepted for `generate_images`.
For this smoke test, negative guidance is folded into the prompt text instead, and prompt enhancement is left off.

## Current Runtime Status

PS-003 is implemented and syntax-valid, but the live visual generation run is currently provider-blocked under the available accounts.

Observed live results:

~~~text
Gemini image generate_content models:
- models/gemini-2.5-flash-image -> 429 RESOURCE_EXHAUSTED / quota unavailable
- models/gemini-3.1-flash-image -> 429 RESOURCE_EXHAUSTED / quota unavailable
- models/gemini-3-pro-image -> 429 RESOURCE_EXHAUSTED / quota unavailable

Imagen generate_images models:
- models/imagen-4.0-fast-generate-001 -> paid plan required
- models/imagen-4.0-generate-001 -> paid plan required
~~~

Developer API compatibility fixes already applied:

~~~text
negativePrompt removed from GenerateImagesConfig
enhancePrompt removed from GenerateImagesConfig
negative guidance folded into prompt text
~~~

Acceptance remains blocked until at least one visual provider returns image bytes, after which the image, prompt packet, and provider note must be uploaded to B2 and verified through a Genblaze manifest with zero transfer failures.
