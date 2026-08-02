# PS-001 Local Setup

## Goal

Run the first ProofStudio smoke tests.

## PS-001A

Proves:

~~~text
local generated PNG
→ Genblaze Pipeline.ingest()
→ Backblaze B2 ObjectStorageSink
→ manifest stored in B2
→ manifest.verify() PASS
→ stored manifest read back from B2 and verified
→ zero asset transfer failures
~~~

This does not require live AI generation.

Required environment variables:

- B2_KEY_ID
- B2_APP_KEY
- B2_BUCKET
- B2_REGION

Run:

~~~bash
source .venv/bin/activate
python scripts/ps001a_b2_manifest_smoke.py
~~~

Local generated files are written under the system temp directory:

~~~text
/tmp/proofstudio-ps-001a/
~~~

This keeps local smoke artifacts outside the repo.

## PS-001B

Later proof:

~~~text
GMI model
→ generated image
→ B2 upload
→ manifest verification
~~~

Required additionally:

- GMI_API_KEY

## Rule

Never commit a real `.env` file.

## PS-001B Live GMI Generation

Proves:

~~~text
local campaign source PNG
→ source uploaded to Backblaze B2
→ temporary presigned B2 URL used as GMI input
→ live GMI image variant generated through Genblaze
→ generated output uploaded to Backblaze B2
→ manifest stored in B2
→ stored manifest read back from B2 and verified
→ zero asset transfer failures
~~~

Required environment variables:

- B2_KEY_ID
- B2_APP_KEY
- B2_BUCKET
- B2_REGION
- GMI_API_KEY

Run:

~~~bash
source .venv/bin/activate
python scripts/ps001b_gmi_b2_generation_smoke.py
~~~

Local generated files are written under the system temp directory:

~~~text
/tmp/proofstudio-ps-001b/
~~~

This live run may spend a small amount of GMI credits.

## PS-001B Current Runtime Status

The PS-001B script is implemented and syntax-valid, but the live GMI generation run requires available GMI credits.

A `402 Insufficient credits` response means:

~~~text
GMI auth works
GMI model validation works
GMI live generation is billing-blocked
PS-001B is not accepted as passed until a generated asset is produced,
uploaded to B2, and verified through a stored manifest with zero transfer failures.
~~~
