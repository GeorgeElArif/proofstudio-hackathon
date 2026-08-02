# PS-041C — Proof Room and Passport Access Authorization

Status: implementation contract. Accepted base: dynamic ref `origin/accepted/proofstudio`, resolving to `1b30315e1c6d1846bebdc7318eddef5d83133d0a` when this slice began.

## Architecture and authority

The browser reads private proof only through auth-server. Auth-server obtains the account from Better Auth session readback, checks the active `account_campaign_access` row, and then calls FastAPI with a server-only credential. Auth Postgres owns identity, sessions, access mappings, and proof references only. FastAPI remains the sole authority for campaign, run, attempt, asset, manifest, archive, rehydrate, review, export, and Passport content. No proof body is persisted in Auth Postgres.

Private routes are `GET /account/campaigns/{campaignId}/proof-room` with optional `runId`, and `GET /account/campaigns/{campaignId}/passport/{runId}`. Their service-authenticated readbacks are `GET /internal/campaigns/{campaign_id}/proof-room` and `GET /internal/campaigns/{campaign_id}/runs/{run_id}/passport`.

## Service trust boundary

`PROOFSTUDIO_PROOF_API_BASE_URL` and `PROOFSTUDIO_INTERNAL_SERVICE_TOKEN` are server-only. FastAPI and auth-server receive the same random token through runtime secret injection; the browser never receives it and no `VITE_` name exists. Requests use `X-ProofStudio-Internal-Token`. A token shorter than 24 characters, surrounded by whitespace, missing, or containing an obvious placeholder marker fails closed. FastAPI compares configured and supplied values in constant time. Neither readiness nor logs include the value.

The auth-server client is GET-only, applies a five-second timeout and 1.5 MB response ceiling, validates JSON and the exact top-level response schema, encodes identifiers, and never forwards an upstream body or exception. Proof-service redirects are never followed: every 3xx response fails closed as `proof_service_unavailable`, preventing service-token forwarding outside the configured canonical proof-service endpoint. It does not cache authorization or proof.

## Identifier contract

Campaign and run identifiers are provider-neutral opaque strings matching exactly `^[A-Za-z0-9_.:-]{1,128}$`. Values must already be Unicode NFC. The grammar rejects empty values, whitespace, controls, decoded slash/backslash, normalization ambiguity, and excessive length. It intentionally does not require `camp_` or `run_`. Every outbound path segment is URL-encoded. Syntax is checked before authorization or resource lookup; failure is HTTP 400 `invalid_request`.

## Capability matrix

| Active application campaign role | `proof.read` | Mutation inferred |
| --- | --- | --- |
| `owner` | yes | no |
| `reviewer` | yes | no |
| `viewer` | yes | no |

`owner` is only an application campaign access label. These meanings do not modify global RBAC and do not establish legal ownership or authorship. Missing and revoked mappings are excluded. A corrupt/unrecognized active role is capability denied.

## Enumeration policy

- 400 `invalid_request`: malformed identifier, forbidden caller scope, duplicate or unknown query scope.
- 401 `authentication_required`: no current Better Auth session.
- 403 `capability_denied`: an active mapping exists but lacks `proof.read`; unreachable for the three valid PS-041C roles.
- 404 `proof_not_found`: absent/revoked/foreign mapping, unknown campaign/run, cross-campaign run, or arbitrary non-golden public Passport.
- 503 `authorization_unavailable`: session, auth DB, or access lookup unavailable. FastAPI is not called.
- 503 `proof_service_unavailable`: FastAPI timeout, connection error, malformed/non-JSON/oversized response, any 3xx redirect, upstream failure, or internal-auth failure.

Errors contain a random request ID unrelated to account/campaign/run values. They contain no raw identity, proof ID, SQL, database URL, token, cookie, stack, or upstream body. Authorization precedes proof lookup.

## Campaign/run relationship and response bounds

FastAPI loads the requested run and requires recorded `run.campaign_id == campaign_id`; `latestRunId` is a dashboard launcher hint only. The Proof Room composite contains the existing campaign and, when requested, the selected run, attempts, assets, manifest, and already-recorded references. It strips local filesystem fields and invents no evidence. The private Passport uses the existing FastAPI assembler only after campaign/run equality. Lists and the gateway response are bounded.

## Direct bypass closure and golden exception

Arbitrary FastAPI reads of campaign, run, attempts, assets, and manifest require the service credential regardless of Origin. Public `GET /runs/{run_id}/passport` first equality-checks the exact ID from `docs/evidence/demo/golden-demo-run.json`, then uses only checked-in golden fixture assembly. It never queries arbitrary in-memory or durable account proof. Every other public run ID returns non-disclosing 404 without lookup. CORS and route hiding are not authorization.

`/campaign-proof-room` remains a fixed public checked-in fixture with no ID parameter. Private routes are distinct and never fall back to it. The legacy `/review` operator flow is explicitly unavailable while secured proof reads are active because its browser-direct arbitrary read path cannot safely receive the internal credential. Fixed judge surfaces remain intact.

## Failure, fixture, and provider boundaries

Missing configuration and dependency failures fail closed. There is no stale cache or fixture fallback. No account mapping is inserted automatically. PS-041C makes no provider or B2 call, imports no Genblaze application, and never authorizes from provider, model, modality, key, asset URL, or browser `parentRunId`.

Provider-neutral multi-stage import, canonical `parent_run_id` lineage, and B2 lineage mapping belong to PS-041D — Genblaze Multi-Provider Run Import + B2 Lineage Mapping.

## Known limitations

Proof records remain process-local in this accepted architecture. A mapping can therefore outlive proof content and safely return 404. One request already authorized may finish immediately after revocation; authorization is checked on every request and is not cached. There is no publication state or share-token system, so only the exact checked-in golden Passport is public. Deployment still needs a real auth-server service and preferably a private service network in addition to route authentication.

## Acceptance gates

Acceptance requires focused FastAPI, real-session disposable-Postgres auth, web route/client, direct-bypass, golden-public, identifier, revocation/IDOR/cross-run, dependency-failure, token/log, no-proof-duplication, no-provider/B2, and no-public-write tests; required existing regressions; non-mutating central regression; screenshots; security scans; clean Docker teardown; a complete review pack; `git diff --check`; no hidden `h`/`S` flags; and no stage, commit, push, merge, tag, or PR.
