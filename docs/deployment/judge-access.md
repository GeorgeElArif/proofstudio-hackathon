# Judge access operations

PS-042B2 prepares two deliberately separate judge journeys.

The public credential-free journey remains available for the golden public
Passport and other explicitly public evidence. It requires no account and is
appropriate for the first review of ProofStudio. The authenticated journey is
for private, account-scoped campaign evidence: login, session readback,
dashboard campaign selection, Proof Room, Passport, and imported lineage.
Both exist so a judge can see the public story without credential friction
while private evidence remains behind a server-owned session and campaign
authorization check.

## Provisioning model

Judge provisioning is an explicit operator action. It is not called by
application startup or migrations. The command fails unless
`PROOFSTUDIO_JUDGE_PROVISIONING_APPROVED` is exactly lowercase `true`. The
operator supplies these server-side process variables:

- `PROOFSTUDIO_DATABASE_URL`
- `PROOFSTUDIO_JUDGE_EMAIL`
- `PROOFSTUDIO_JUDGE_PASSWORD`
- `PROOFSTUDIO_JUDGE_CAMPAIGN_ID`
- `PROOFSTUDIO_JUDGE_ROLE`
- `PROOFSTUDIO_JUDGE_PROVISIONING_APPROVED`

The minimum and default role is `viewer`; `reviewer` is the only other
permitted judge role. `owner` and administrator-equivalent provisioning are
refused. The campaign identifier must use the ProofStudio identifier grammar.
Provisioning creates or updates one active link for that account and campaign,
is idempotent for identical input, rotates the Better Auth credential when the
password changes, and marks email verified only under this explicit
operator-approval path.

The exact production command template contains variable references only:

```bash
cd apps/auth-server
PROOFSTUDIO_DATABASE_URL="${PROOFSTUDIO_DATABASE_URL}" \
PROOFSTUDIO_JUDGE_EMAIL="${PROOFSTUDIO_JUDGE_EMAIL}" \
PROOFSTUDIO_JUDGE_PASSWORD="${PROOFSTUDIO_JUDGE_PASSWORD}" \
PROOFSTUDIO_JUDGE_CAMPAIGN_ID="${PROOFSTUDIO_JUDGE_CAMPAIGN_ID}" \
PROOFSTUDIO_JUDGE_ROLE="${PROOFSTUDIO_JUDGE_ROLE}" \
PROOFSTUDIO_JUDGE_PROVISIONING_APPROVED="${PROOFSTUDIO_JUDGE_PROVISIONING_APPROVED}" \
npm run provision:judge
```

Set real values only in the operator's approved secret manager/session. Never
put a judge credential in Git, an issue, build output, application log,
fixture, video, or screenshot. The JSON receipt is operational evidence but
contains no database URL, password, credential digest, session value, or
internal service token.

## Credential delivery and lifecycle

Deliver the generated password through Devpost's private judge-instructions
field or the event's equivalent access-controlled mechanism. Do not send it by
application email and do not place it in public submission text. Verify the
destination and access scope before saving the instructions.

Rotate by rerunning the same approved command with a new strong value in
`PROOFSTUDIO_JUDGE_PASSWORD`. Confirm the old password fails and the new
password succeeds before updating the private judge instructions. After
judging, disable the account by setting `auth_user.disabled_at`, revoke its
active `account_campaign_access` row, and revoke/delete active sessions in one
operator-controlled database transaction. Alternatively rotate to an
undelivered random value while completing the disable operation.

Rollback for a newly linked campaign is to set `revoked_at` on the exact
account/campaign link. Rollback for the account is the disable-and-session
revocation procedure above. Do not delete shared campaign proof data: the auth
database stores access mappings, not private proof payloads.

## Verification and limitations

Before any real provisioning, run migrations and the disposable-database
smokes, confirm the production URL and secret-manager values out of band, then
obtain the explicit approval. After provisioning, verify login, session
readback, the one linked dashboard campaign, authorized private routes,
unlinked denial, logout, and session invalidation.

PS-042B2 exercises only a disposable local PostgreSQL database and loopback
test servers. It does not provision a production database or judge account,
deliver a credential, contact Render, verify a public deployment, send email,
invoke OAuth, call B2, or call a provider. Account expiry is currently an
operator procedure rather than a scheduled job. The receipt contains the
normalized address because that is the current auth policy; operators must
treat the receipt as access-controlled operational metadata.

ProofStudio proves what the pipeline recorded. Proof does not equal truth.
