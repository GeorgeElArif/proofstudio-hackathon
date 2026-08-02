# 01 — Product One-Pager

## Product name

ProofStudio

## One-line pitch

ProofStudio is a provenance-aware AI media operations cockpit — a Campaign
Proof Room and proof system, not just a generator — that turns a campaign
brief into a verified AI media kit, with every asset, prompt, model, hash,
manifest, and version archived in Backblaze B2 and verified through Genblaze.

## What ProofStudio actually is

ProofStudio is not another AI image generator. It is an AI media operations
cockpit and a proof system: it proves the production workflow behind AI media,
from brief to export, against a durable B2 archive and a Genblaze manifest
chain.

A Campaign Proof Room — the marquee judge-facing surface — ties provenance, B2
evidence, rehydration, failure-as-proof, and lineage together in one room so a
designer, marketer, reviewer, client, or hackathon judge can see the full
provenance story end to end without reading raw JSON.

## Center of gravity: Backblaze B2 + Genblaze

- Backblaze B2 is the durable system of record: source briefs, prompt packets,
  generated assets, derived assets, manifests, attempt ledgers, review records,
  and export packs all live in B2. B2 is not decorative — the app can rehydrate
  campaign state from B2-backed artifacts.
- Genblaze produces verifiable SHA-256 manifests for stored artifacts. Genblaze
  v0.4.0 manifest correctness (real `manifest_uri` and `manifest_hash`, not
  nulls) is a blocking requirement for the golden run.

## Multimodal future-readiness

The roadmap adds a multimodal proof layer so image + voiceover/audio +
transcript can live under one campaign/passport/manifest. That includes
AssemblyAI transcript/timestamp evidence, a Hume or ElevenLabs voiceover
artifact, and Gemini/Google campaign intelligence for the judge-facing
narrative, served over a Cloudflare low-cost backbone. These are future
implementation slices, documented honestly — ProofStudio does not claim
multimodal capabilities that are not yet built.

## Target users

- marketing agencies
- creator teams
- startup growth teams
- brand managers
- reviewers and approvers
- hackathon judges and clients (via the Campaign Proof Room and export pack)

## Core problem

AI media generation creates assets quickly, but teams lose control of prompts,
versions, approvals, provenance, storage, and final exports. Most AI media
tools stop at output generation. ProofStudio shows the full production
lifecycle with proof.

## MVP promise

A user can generate a small campaign media kit, inspect how it was made, verify
stored artifacts, regenerate a variant, and share a review/export package —
with every step backed by B2 and a Genblaze manifest.

## Truth boundary (honest)

ProofStudio proves what the pipeline did. It does not prove semantic truth,
legal authenticity, C2PA authenticity, human authorship, Object Lock/
tamper-proof storage, browser-side B2 byte verification, or production
security unless those are actually implemented. Nothing in the pitch overclaims
capabilities that are not built.
