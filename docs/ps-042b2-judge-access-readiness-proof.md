# PS-042B2 — Judge access readiness proof

## Identity and scope

- Accepted base: `03c0f85b4d418b9c2520e6ad66e03819b1efe796`
- Branch: `ps-042b2/judge-access-readiness-v1`
- Commit: `COMMIT_SHA_PLACEHOLDER`
- Parent: `03c0f85b4d418b9c2520e6ad66e03819b1efe796`

Exact changed paths are recorded from the final commit:

```text
apps/auth-server/package.json
apps/auth-server/src/account/campaign-access.ts
apps/auth-server/scripts/provision-judge-account.ts
apps/auth-server/scripts/smoke-judge-access-readiness.ts
apps/auth-server/scripts/smoke-judge-provisioning.ts
apps/web/scripts/smoke-judge-authenticated-journey.mjs
scripts/ps042b2_judge_access_readiness_smoke.py
docs/deployment/judge-access.md
docs/deployment/preflight-checklist.md
docs/ps-042b2-judge-access-readiness-proof.md
```

No migration, schema, lockfile, public visual, or authorization-semantics
change was required.

## Provisioning model and safety evidence

Provisioning is a separately invoked operator script, never startup or
migration behavior. It validates exact lowercase approval, database URL
classification, email/domain policy, strong non-placeholder password,
ProofStudio campaign identifier, and the `viewer|reviewer` role bound before
creating a database client. Disposable database access is available only to
the imported smoke workflow through its explicit test-only option; automated
smoke rejects a production-like URL.

The script uses Better Auth's password implementation, creates or locates the
Better Auth user and credential account, explicitly records verification,
creates or updates one active account/campaign link, and closes the PostgreSQL
pool on every path. Repeating identical input makes no user, account,
credential, or access change. A changed password rotates the credential; the
old value is rejected and the new value authenticates.

Sanitized receipt fields:

```text
ok
operation
account_id
email_normalized
campaign_id
role
created_user
created_account
rotated_password
created_access
updated_access
revoked_conflicts
timestamp
```

Receipt inspection found no database URL, plaintext password, credential
digest, session value, internal token, or account credential.

## Disposable database and migration evidence

Validation starts by removing the Docker volume, starts the loopback-only
PostgreSQL service, applies migrations `0000`, `0001`, and `0002`, and invokes
the migration command again. The final validation transcript records the first
invocation's three files and an empty second `appliedMigrationFiles` list.
Both judge smokes delete their synthetic users; cascading cleanup removes
their account, session, and campaign-access rows. Database shutdown uses
`down -v`, restoring the clean disposable baseline.

## Login, session, access, and denial evidence

The full smoke follows:

```text
fresh database
→ migrations 0000–0002
→ approved synthetic judge provisioning
→ email/password login
→ session readback
→ dashboard campaign list
→ authorized Proof Room
→ authorized Passport
→ authorized lineage list
→ authorized lineage detail
→ authorized lineage Passport
→ denied unlinked campaign
→ denied second account
→ logout
→ session invalid
→ provisioning rerun
→ idempotency confirmation
```

The session cookie is HTTP-only and Secure in production-shaped
configuration. Browser code uses credentialed requests, no browser storage
authentication, and no internal service token. Authorization precedes proof
reads. The denial matrix is:

| Attempt | Result | Proof API calls |
| --- | --- | ---: |
| No session | denied | 0 |
| Judge reads unlinked campaign | `404` | 0 |
| Second account reads judge campaign | `404` | 0 |
| Logged-out session reads session | unauthenticated | 0 |

No fixture fallback occurs after denial. PostgreSQL contains only identity,
session, and campaign-link metadata; no private proof payload columns.

## Commands and results

The final run executes the required repository checks, top-level smoke, auth
typecheck/build and non-database smokes, disposable lifecycle and all database
smokes, web typecheck/build and smokes, full Python suite, central regression,
historical digest comparison, and classified cumulative/final secret scans.
Completed validation results:

```text
git diff --check: passed
hidden h/S index flags: 0
top-level PS-042B2 smoke: ok=true
auth typecheck/build and required non-database smokes: passed
migration invocation 1: 0000, 0001, 0002 applied
migration invocation 2: no migrations applied
judge provisioning smoke: passed
judge access readiness journey: passed
historical auth database smokes: passed
web typecheck/build: passed with installed Node 24 runtime
web source and runtime smokes: passed
Python suite: 523 passed
central regression: ok=true, failures=[], 12 historical contracts
central regression non-mutating: true
PS-034A report digest unchanged: true
```

Non-live counters:

```text
Render calls: 0
Deployments: 0
Paid-resource creations: 0
Production migrations: 0
Production database calls: 0
Production judge accounts provisioned: 0
External email sends: 0
OAuth calls: 0
B2 calls: 0
Provider calls: 0
Backend object operations: 0
```

## Known limitations and rollback

This slice does not test a real deployment, production network, production
secret manager, credential delivery channel, or scheduled expiry. Account
disablement remains an operator procedure. Roll back a campaign grant by
revoking the exact active account/campaign row. Roll back the account by
setting its disabled timestamp and revoking its sessions and active campaign
links. Do not delete proof payloads; they are outside the auth database.

## Truth boundary

This slice proves that the judge-account provisioning and authenticated
judge journey work against a disposable local PostgreSQL database. It does
not prove that a production database exists, that a production migration ran,
that a real judge account was provisioned, or that the public Render deployment
is operational.

ProofStudio proves what the pipeline recorded.
Proof does not equal truth.
