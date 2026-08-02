# PS-002 Gemini Campaign Intelligence

## Goal

Turn a ProofStudio campaign brief into a structured campaign intelligence package, then store and verify it through Backblaze B2 and Genblaze.

## Proof

~~~text
campaign brief
→ Gemini structured campaign strategy JSON
→ campaign prompt pack
→ channel plan
→ disclosure/provenance plan
→ export markdown
→ upload JSON + markdown to B2
→ Genblaze manifest
→ stored manifest verification
→ zero transfer failures
~~~

## Required environment variables

- B2_KEY_ID
- B2_APP_KEY
- B2_BUCKET
- B2_REGION
- GEMINI_API_KEY

## Models

Default primary model:

~~~text
models/gemini-2.5-pro
~~~

Default fallback model:

~~~text
models/gemini-2.5-flash
~~~

Override locally if needed:

~~~bash
export GEMINI_STRATEGY_MODEL="models/gemini-2.5-pro"
export GEMINI_STRATEGY_FALLBACK_MODEL="models/gemini-2.5-flash"
~~~

## Run

~~~bash
source .venv/bin/activate
python scripts/ps002_gemini_campaign_intelligence.py
~~~

## Local outputs

~~~text
/tmp/proofstudio-ps-002/
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

## Product value

This is the strategy layer that drives the rest of ProofStudio:

- image prompts
- video prompts
- voiceover prompt
- channel-specific assets
- review gates
- export package design
- provenance/disclosure limits
