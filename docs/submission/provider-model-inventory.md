# ProofStudio — Provider & Model Inventory

This inventory lists **only** providers/models actually implemented or proven in
this repo, plus the ones attempted but blocked, and the ones explicitly
deferred. No provider or model is claimed as implemented unless a proof script or
proof doc backs it.

## Live proven or implemented

### Cloudflare Workers AI (image, primary)

- **Provider id:** `cloudflare-workers-ai`
- **Model:** `@cf/bytedance/stable-diffusion-xl-lightning`
- **API method:** `workers-ai-run`
- **Job type:** `image_generation`
- **Status:** Live-proven. Used as the **primary** image provider in the router.
- **Backing slices:** PS-004 (first Cloudflare run), PS-007 (live router chain),
  PS-009 (API live bridge), PS-010 (archived live run), PS-011 (passport from
  rehydrated live run).
- **What was proven:** real image bytes returned, byte-detected MIME (not trusted
  from headers), image + prompt packet + attempt ledger + provider note uploaded
  to Backblaze B2, Genblaze manifest written and byte-level verified.

### Pollinations (image, no-key fallback)

- **Provider id:** `pollinations`
- **Model:** `pollinations-image-default`
- **API method:** `pollinations-image-get`
- **Job type:** `image_generation`
- **Status:** Live-proven. Used as the **fallback** image provider (no API key
  required).
- **Backing slice:** PS-005.
- **What was proven:** valid image bytes returned without an API key, same B2 +
  Genblaze provenance pipeline as the primary provider.
- **Note:** Pollinations is a fallback provider, not a premium final visual
  provider. The router advances to it when the primary is missing a key, fails,
  or is disabled (offline-validated in PS-006/PS-007).

### Gemini — campaign intelligence (strategy layer)

- **Provider:** Google Gemini
- **Models:** `models/gemini-2.5-pro` (primary), `models/gemini-2.5-flash`
  (fallback)
- **Status:** Implemented as the **campaign-intelligence / strategy layer**
  (brief → structured campaign strategy, prompt pack, channel plan,
  disclosure/provenance plan), stored to B2 with a Genblaze manifest.
- **Backing slice:** PS-002.
- **Note:** This is the **strategy/intelligence** layer, distinct from visual
  generation. Visual generation through Gemini/Imagen is a separate path (see
  "Attempted but blocked").

## Attempted but blocked

These are implemented paths that currently cannot complete a live generation run
in the available environment. They are **not** claimed as successful providers.

### GMI Cloud (generation blocked by credits)

- **Status:** Path implemented (PS-001B). Live generation is
  **billing-blocked** (`402 Insufficient credits`).
- **Evidence:** Auth and model validation work; generation is credit-gated.
  Not accepted as a passed provider until a generated asset is produced,
  uploaded to B2, and verified.

### Gemini / Imagen visual generation (quota / paid-plan blocked)

- **Status:** Path implemented (PS-003). Live visual generation is blocked
  under the available accounts.
- **Evidence:** `generate_content` models return `429 RESOURCE_EXHAUSTED`; Imagen
  `generate_images` models require a paid plan.
- **Models attempted:** `gemini-2.5-flash-image`, `gemini-3.1-flash-image`,
  `gemini-3-pro-image`, `imagen-4.0-fast-generate-001`,
  `imagen-4.0-generate-001`.

### Luma (skipped — card required)

- **Status:** Skipped. A card/payment method is required to enable the account,
  so it was not integrated.

## Optional later (NOT implemented)

The following are **not** implemented and are **not** claimed as working. They
are recorded only as potential future directions:

- **ElevenLabs** (audio/voice) — not implemented.
- **OpenAI** — not implemented.
- **Runway** (video) — not implemented.
- **Stability Audio** — not implemented.
- **NVIDIA NIM** — not implemented.

## Summary table

| Provider / Model | Role | Status | Backing |
|------------------|------|--------|---------|
| Cloudflare Workers AI · `@cf/bytedance/stable-diffusion-xl-lightning` | image primary | Live-proven | PS-004, PS-007, PS-009, PS-010, PS-011 |
| Pollinations · `pollinations-image-default` | image fallback | Live-proven | PS-005 |
| Gemini · `gemini-2.5-pro` / `gemini-2.5-flash` | campaign intelligence | Implemented | PS-002 |
| GMI Cloud | generation | Blocked (credits) | PS-001B |
| Gemini / Imagen visual | visual generation | Blocked (quota/paid) | PS-003 |
| Luma | — | Skipped (card required) | — |
| ElevenLabs / OpenAI / Runway / Stability Audio / NVIDIA NIM | — | Optional later, not implemented | — |
