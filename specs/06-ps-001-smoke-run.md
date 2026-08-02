# 06 — PS-001 Genblaze + B2 Smoke Run

## Goal

Prove that the sponsor stack works before building the full MVP.

## Required output

A local Python script must:

1. Load credentials from `.env`.
2. Run one Genblaze pipeline.
3. Store a generated asset in Backblaze B2.
4. Store a manifest in Backblaze B2.
5. Print asset URL, object key, manifest URI, SHA-256, canonical hash, and verification result.

## Definition of done

PS-001 is done only when:

- script runs locally
- asset exists in B2
- manifest exists in B2
- verification prints PASS
- terminal screenshot is saved for proof
