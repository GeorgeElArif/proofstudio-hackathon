# PS-041B — Account Campaign Ownership + Real List Contract

## Boundary

Auth proves account/session identity only. `account_campaign_access` records an application access association; it does not prove legal ownership, human authorship, semantic truth, or proof authenticity independently of recorded proof data. The `owner` value is a campaign access role only.

Sources remain labeled and separate: `account_campaign_store` owns persisted account-to-campaign references; `proof_api` owns campaign/run proof content and proof-layer status; `checked_in_fixture` owns the existing golden fixture.

## Read route

`GET /account/campaigns` requires a real Better Auth session and derives account ID only from server session readback. Caller-supplied account/user scope is rejected. Unauthenticated requests return safe HTTP 401; unavailable auth/DB returns safe HTTP 503; malformed cursor or invalid limit returns safe HTTP 400. Success returns source `account_campaign_store`, reference-only items, and stable `pageInfo`.

Default limit is 20 and maximum is 50. Ordering is ascending `linked_at`, then `campaign_id`. The opaque cursor contains only those public ordering values and never a SQL/internal primary key.

Roles are `owner`, `reviewer`, and `viewer`; they are campaign-specific and unrelated to global RBAC.

## Persistence and access

The auth Postgres table stores account ID, campaign ID, optional latest run ID, access role, linked/updated/revoked timestamps. Active account/campaign association is unique; blank campaign IDs and invalid roles are constrained. Revoked rows are excluded by default. Internal helpers link, update, lookup, list, and revoke; PS-041B exposes no public mutation.

The dashboard distinguishes unauthenticated, unavailable, available-empty, available, and error states. Access rows never invent proof titles or statuses. The checked-in fixture is visibly separate and is not linked to the account.

## Limitation

This route is session-gated, but existing Proof Room and Passport routes are not ownership-gated. PS-041B does not claim end-to-end proof-room access control; downstream enforcement belongs to a later PS-041 slice.
