# PS-041C Proof Room and Passport Access Authorization Proof

## Result and architecture decision

PS-041C implements the auth-server read gateway selected by accepted discovery. The browser presents only its Better Auth cookie to auth-server. Auth-server derives the account from session readback, evaluates the active campaign access mapping, and calls FastAPI server-to-server. FastAPI remains the proof-data authority; Auth Postgres stores references only.

## Contracts implemented

- Service trust: `PROOFSTUDIO_PROOF_API_BASE_URL`, server-only `PROOFSTUDIO_INTERNAL_SERVICE_TOKEN`, and `X-ProofStudio-Internal-Token`; placeholder/missing values fail closed and FastAPI compares in constant time.
- Identifiers: NFC `^[A-Za-z0-9_.:-]{1,128}$`, checked before lookup and encoded outbound.
- Roles: active `owner`, `reviewer`, and `viewer` each receive only `proof.read`. `owner` remains an application role.
- Enumeration: stable 400/401/403/404/503 envelopes and random non-identifying request IDs.
- Internal FastAPI routes: campaign-scoped Proof Room and Passport with FastAPI-owned campaign/run equality.
- Public/private split: raw arbitrary reads require service auth; only the exact checked-in golden Passport remains public.
- Web: distinct account Proof Room and Passport routes use the credentialed auth gateway; account dashboard rows link to them; private failure never falls back to a fixture.
- Legacy review: the browser-direct local operator flow is labeled unavailable in secured mode rather than receiving the service credential.

## Dependency behavior and data boundary

Authorization storage failure returns `authorization_unavailable` before any FastAPI call. Proof timeout, connection, non-JSON, malformed, oversized, internal-auth, upstream failure, or any 3xx redirect returns `proof_service_unavailable`. Proof-service redirects are never followed, preventing service-token forwarding outside the configured canonical proof-service endpoint. Absent/revoked/cross-account access and missing/cross-campaign proof converge on `proof_not_found`. No proof body is copied to the auth schema.

## Genblaze compatibility and truth boundary

Authorization uses account, active campaign mapping, and FastAPI-recorded campaign/run membership only. No provider, model, B2 key, URL, modality, or caller lineage participates. PS-041D should add provider-neutral multi-run import and recorded `parent_run_id`/B2 lineage without changing this authorization key.

This slice proves the tested access-control behavior of local components. It does not claim legal authenticity, semantic truth, human authorship, C2PA, Object Lock, enterprise security, or public deployment verification.

## Validation and screenshots

The focused FastAPI HTTP smoke passed missing/wrong/correct token behavior, all five raw direct-read protections, campaign/run equality, cross-campaign and unknown-run denial, ASCII/NFC/length/separator/control validation, arbitrary public Passport denial, and the exact golden fixture. It used only process-local dry-run records.

The disposable-Postgres auth smoke passed with real Better Auth sessions for owner, reviewer, and viewer. Cross-account, absent, and revoked access returned the same 404; identity spoofing and malformed IDs returned 400; foreign runs returned 404. An unavailable auth DB returned 503 without a proof call. Proof connection, timeout, non-JSON, malformed, oversized, internal-auth, upstream-500, 302-redirect, and 307-redirect outcomes all returned safe 503. The redirect target on a different loopback port received zero requests and therefore received no internal-token, cookie, or Authorization header; neither redirect Location nor upstream body detail appeared in the gateway response. Schema inspection found no proof-body column.

Auth-server typecheck/build and the accepted policy, readiness, auth behavior, body forwarding, missing-env, session, DB safety, email/OAuth, campaign contract/API, configured-auth, migration, and Drizzle checks passed. Web typecheck/build plus auth-client, configured auth-client, dashboard contract/UI/account-campaign, and private-proof smokes passed. Both production dependency audits reported zero vulnerabilities. The central regression gate passed non-mutating for 12 historical contracts with frontend validation and left the canonical PS-034A digest unchanged.

Ten screenshots cover unauthenticated, authorized, and non-disclosing Proof Room states; authorized and denied Passport states; exact golden and arbitrary public Passport states; dashboard launchers; and both mobile private routes. The harness used a real local Better Auth session and disposable FastAPI records and captured no cookie, token, DB URL, or production identity.

Validation transcripts, audits, screenshots, Docker teardown, full tracked diff, and preserved untracked source copies are assembled in `/tmp/proofstudio-ps041c-proof-access-pack/`. Known limitation: process-local proof data can disappear while durable auth mappings remain; the safe result is non-disclosing not-found.
