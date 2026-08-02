# 03 — Architecture

## Recommended architecture

Next.js UI → FastAPI API → Redis/RQ background worker → Genblaze pipeline → AI providers → Backblaze B2 object storage → Manifest/provenance verification → UI Provenance Passport.

## Critical rule

Long-running generation must run in a worker, not in the request thread.

## First proof target

Before building full UI, we must prove:

- Genblaze pipeline runs
- generated asset is saved to B2
- manifest is saved to B2
- verification result can be printed
