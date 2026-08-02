# PS-041B Account Campaign Ownership + Real List Proof

## Result

PS-041B adds a durable account-to-campaign access index to auth-server Postgres, where Better Auth owns session identity. FastAPI remains the only owner of proof campaign/run content. No proof manifests, archive/rehydrate/review/export outcomes, hashes, providers, titles, or proof statuses are copied or invented.

The central regression gate, auth-server regression, PS-041B contract/API smokes, configured disposable-database validation, web regression, dashboard smokes, and both production dependency audits passed. The screenshots in the review pack demonstrate unauthenticated, authenticated-empty, authenticated-populated, row-detail, fixture-separation, and mobile-populated states.

## Architecture and schema

Migration `apps/auth-server/drizzle/0002_fluffy_sinister_six.sql` creates `campaign_access_role` (`owner`, `reviewer`, `viewer`) and `account_campaign_access`. The table uses the canonical text Better Auth user ID, a cascading foreign key to `auth_user(id)`, a nonblank campaign constraint, timestamps, optional latest-run reference, and nullable revocation timestamp.

The active `(account_id, campaign_id)` partial unique index prevents duplicate live mappings while permitting historical revoked mappings. Account-list and campaign-lookup indexes cover active listing, revocation filtering, lookup, and the stable `(linked_at, campaign_id)` cursor order.

Repository helpers validate campaign IDs, list only the authenticated account's non-revoked mappings, provide deterministic active-link upsert/revoke behavior, and never fetch proof data. Pagination defaults to 20, caps at 50 at the route boundary, fetches one look-ahead row, and returns an opaque base64url cursor over `linked_at` plus `campaign_id`. Malformed cursors and invalid limits fail with 400.

## Session and API boundary

`GET /account/campaigns` performs Better Auth session readback and derives `accountId` only from the returned session user. It returns 401 without a session, rejects `accountId`/`userId` query spoofing with 400, and fails closed when auth/database runtime is unavailable. Stable error reasons do not include SQL, stack traces, identity data, cookies, tokens, or database URLs.

The real-session API smoke created accounts through Better Auth sign-up and sign-in, locally simulated verification-link consumption, and used the issued session cookie. It did not insert or fabricate sessions. Account A received exactly two active mappings; its revoked mapping and the separate Account B mapping were absent. Account B could not scope a request to Account A. Malformed cursor handling also passed.

## Dashboard states and source separation

The dashboard client uses `credentials: include`, never browser storage, and distinguishes unauthenticated, unavailable, available-empty, available, and error states. The required screenshots show:

- unauthenticated: sign-in action, with no account rows;
- authenticated empty: a real session and “No campaigns are linked to this account yet”;
- authenticated populated: exactly two Account A active mappings;
- row detail: campaign ID, optional latest run ID, application campaign access role, linked timestamp, `account_campaign_store`, and `not_fetched` proof detail;
- fixture separation: the golden proof remains a checked-in fixture and is not account-linked;
- mobile populated: readable source labels and rows at 390×844 without horizontal overflow.

`owner` is an application campaign access role only. It does not imply legal ownership, legal authenticity, human authorship, or semantic truth. Access-index data and proof detail remain visibly separate. No title or proof status is invented for an account row.

### Final source-consistency and response-validation correction

The final targeted PS-041B correction makes Source Integrity derive its account-campaign messaging from `campaignList.state`. A populated list now reports `account_campaign_store` as available; an available-empty list reports an available source with zero mappings; unauthenticated, unavailable, and request-error states remain distinct. The account-campaign disclosure also varies by state: “Why sign-in is required,” “About this empty list,” “About access and proof details,” “Why this source is unavailable,” or “Why this request failed.” The checked-in golden fixture remains separately labeled `checked_in_fixture`, is not account-linked, and is never inserted into the real list.

The web client now runtime-validates the success response state and source, every item, and pagination metadata before accepting rows. Campaign IDs must be nonblank; optional run IDs must be null or nonblank strings; roles are limited to `owner`, `reviewer`, or `viewer`; linked and updated timestamps must be parseable; item and response source must be `account_campaign_store`; proof detail state must be `not_fetched`; and `pageInfo` must contain a boolean `hasMore` plus a string-or-null `nextCursor`. Any malformed success payload is rejected as a typed safe error with zero rows. Raw payload values are not rendered or logged, fixture rows are not used as fallback, and authenticated state is not forced.

Replacement screenshot inventory:

- `ps041b-dashboard-authenticated-populated-fixed.png`: real-session Account A list with two active mappings, available storage copy, `account_campaign_store` badges, and “About access and proof details”;
- `ps041b-dashboard-authenticated-empty-fixed.png`: real available-empty list with zero mappings and “About this empty list”;
- `ps041b-dashboard-unauthenticated-fixed.png`: sign-in action, zero rows, and “Why sign-in is required”;
- `ps041b-dashboard-mobile-populated-fixed.png`: 390×844 populated account list with readable source labels and no horizontal overflow.

For this web-only correction, `npm ci --ignore-scripts`, typecheck, production build, auth-client smoke, dashboard-contract smoke, dashboard UI smoke, strengthened dashboard account-campaign smoke, package-lock dry-run, and the production dependency audit completed successfully. The build emitted only the established non-blocking Vite large-chunk warning. The first production audit request encountered `EAI_AGAIN`; its single approved network retry reported 0 production vulnerabilities. The screenshot harness used the previously validated disposable local database and real Better Auth sessions, then removed its container, network, and volume. No auth-server implementation, migration, API, repository, or smoke source file was changed by this targeted correction, and FastAPI was unchanged.

## Validation actually run

- Branch/accepted-ref verification, unstaged-index check, `git diff --check`, and explicit `h`/`S` hidden-index scan: passed.
- Auth-server regression and PS-041B contract smoke: passed before final evidence capture.
- Disposable Postgres migration applied migrations `0000`, `0001`, and `0002`; all required tables were present.
- Real Better Auth session/API smoke: unauthenticated 401, real session, isolation, revoked exclusion, spoof rejection, and malformed cursor checks passed.
- Web regression, PS-041A dashboard UI smoke, and PS-041B dashboard smoke: passed. After the screenshot-only row-layout correction, the affected web production build and both dashboard smokes passed again.
- Canonical central regression gate: passed before final evidence capture.
- `npm audit --omit=dev` for auth-server and web: both reported 0 vulnerabilities before final evidence capture.
- Six screenshot assertions and visual review: passed.
- Final Docker teardown: container, network, and volume removed.
- Forbidden-claim, secret-pattern, fake-data/auth, logging-safety, review-pack safety, and final Git safety scans: classified in the review pack.

## Known limitations and next slice

`/account/campaigns` is session-gated, but downstream Proof Room and Passport routes are not authorized against this index. Public write routes were not added, FastAPI was not changed, and no production database was used. Proof-detail joins, downstream authorization, richer cursor coverage, and account-aware Proof Room/Passport enforcement remain out of scope.

Recommended PS-041C: enforce the authenticated account access mapping at downstream Proof Room and Passport read boundaries, with explicit denial/isolation smokes and no expansion of public write behavior.
