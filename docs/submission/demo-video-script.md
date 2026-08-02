# ProofStudio — Demo Video Script (~3 minutes)

A narrated demo script for the hackathon submission. Target runtime: **about 3
minutes**. Designed to be recorded from the local Review Room (see
[`recording-runbook.md`](./recording-runbook.md)).

The default demo path is **safe**: it uses a one-click helper and a safe dry-run,
and it never calls a live provider or B2 unless you explicitly opt into the live
proof flow during the 1:20–2:10 segment.

> Note on screenshots/video: they must be **captured** during a real recording
> session following the runbook. This script does not assume any screenshots
> already exist.

---

## 0:00-0:20 Hook

**On screen:** Review Room hero / positioning header.

**Narration:**

> Creative and marketing teams generate AI media across multiple providers — but
> they lose the evidence trail: the prompt, the model, the retries, the storage,
> the manifest, and what can actually be trusted. Every run becomes a black box.

**Pain point:** AI media generation has no reviewable, durable, evidence-backed
workflow. Outputs appear, but the *how* and *what was tried* disappear.

---

## 0:20-0:45 Product

**On screen:** Keep the Review Room open; point at the API Status card.

**Narration:**

> ProofStudio is a **Review Room for AI media operations**. It turns a campaign
> brief into a verified media kit: campaign intelligence → provider-routed
> generation → Backblaze B2 storage → Genblaze manifest verification → a
> Provenance Passport reviewers can trust.

**Audience (state clearly):**

- **creator teams** producing AI assets at volume
- **marketing teams** reviewing campaign media across channels
- **agencies** managing multiple clients and providers
- **production teams** reviewing AI-generated assets before release

---

## 0:45-1:20 Safe Demo Setup

**On screen:** Terminal running the one-click helper; then the Review Room
showing the API Status card online and a freshly seeded campaign + safe dry-run.

**Narration:**

> Setup is one command. The PS-015 one-click helper seeds a demo campaign and
> creates a **safe dry-run**. By default it calls **no live provider and no B2**,
> and it fakes no media. The API Status card confirms the backend is online.

**Show:**

- The one-click helper command and its printed Review Room + API docs URLs.
- The API Status card reporting the backend online (health + version).
- A safe dry-run with the honest **no media / no manifest** state.

**Make the safety point explicit:** the default path never spends provider
credits and never touches B2.

---

## 1:20-2:10 Live Proof Flow

**On screen:** Toggle **Live mode** on; read the warning; click **Create Live
Proof Run**. Show the attempt ledger, evidence overview, and (if available)
assets and manifest.

**Narration:**

> Now the explicit live path. Live mode is **opt-in** — there is always a clear
> warning: *Live mode may call external providers and B2.* We create a live proof
> run through the provider router: a primary provider, with a no-key fallback.

**Show:**

- The **explicit live mode warning**.
- The **provider attempt ledger** — every attempt preserved, including failures
  and skips (failure is also evidence).
- The **fallback / readiness story**: if the primary provider fails or is
  blocked, the router advances to the fallback provider.
- **Generated asset metadata** if the live run produced media (SHA-256, media
  type, size, B2 URL).
- **Manifest evidence** if available (manifest URI, manifest hash, stored
  manifest verification).

**Fallback if the live provider fails or is blocked:** show the honest
`live_failed` or `live_blocked` state with the sanitized reason, and explain
that **failed attempts are also recorded evidence** — never faked as success. If
no live credentials are configured, narrate the safe dry-run + the recorded
prior live evidence instead (see `provider-model-inventory.md` for what was
proven in earlier slices).

---

## 2:10-2:40 Provenance Passport

**On screen:** Provenance Passport panel.

**Narration:**

> Everything funnels into the **Provenance Passport**. It summarizes the
> generation, the manifest verification, the archive/rehydrate path, the trust
> boundary, and reviewer next actions — assembled from the real stored evidence.

**Show:**

- **Generation summary** (selected provider/model, media present, asset hashes).
- **Manifest verification** (manifest hash, stored-manifest verification result).
- **Archive / rehydration** evidence (run archived to B2 and rehydrated from B2
  object content, without rerunning any provider).
- **Trust boundary** (claims asserted vs. explicitly non-claimed).
- **Reviewer next actions**.

---

## 2:40-3:00 Why It Wins

**On screen:** Truth Boundary footer / judging-criteria summary.

**Narration:**

> ProofStudio maps directly to the judging criteria. **Real-world utility:** a
> Review Room for teams drowning in opaque AI media. **Production readiness:** a
> typed FastAPI contract, a durable archive/rehydrate path, and honest failure
> handling. **Backblaze B2:** assets, manifests, and run archives are stored and
> byte-level verified. **Genblaze:** manifests are written and verified as
> provenance evidence.

**Closing claim:**

> ProofStudio turns AI media generation from a black-box output into a
> reviewable, durable, evidence-backed workflow.
