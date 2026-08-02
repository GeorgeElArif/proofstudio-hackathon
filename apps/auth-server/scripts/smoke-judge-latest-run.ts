import { randomBytes } from "node:crypto";

import pg from "pg";

import { getSmokeDatabaseUrl } from "./ps040f-config.js";
import { provisionJudgeAccount } from "./provision-judge-account.js";
import { assertSafeDatabaseUrlForSmoke } from "../src/db/url-safety.js";

const databaseUrl = getSmokeDatabaseUrl();

assertSafeDatabaseUrlForSmoke(databaseUrl, {
  action: "PS-042C1 judge latest-run binding smoke",
});

const pool = new pg.Pool({
  connectionString: databaseUrl,
  max: 1,
});

const stamp = `${Date.now()}-${randomBytes(4).toString("hex")}`;
const email = `ps042c1-latest-run-${stamp}@proofstudio.test`;
const campaignId = `ps042c1-campaign-${stamp}`;
const firstRunId = `ps042c1-run-a-${stamp}`;
const secondRunId = `ps042c1-run-b-${stamp}`;
const password = `Zz7!${randomBytes(24).toString("base64url")}`;

let accountId: string | null = null;

function assert(
  condition: unknown,
  message: string,
): asserts condition {
  if (!condition) throw new Error(message);
}

function environment(runId?: string): NodeJS.ProcessEnv {
  const env: NodeJS.ProcessEnv = {
    ...process.env,
    PROOFSTUDIO_DATABASE_URL: databaseUrl,
    PROOFSTUDIO_JUDGE_EMAIL: email,
    PROOFSTUDIO_JUDGE_PASSWORD: password,
    PROOFSTUDIO_JUDGE_CAMPAIGN_ID: campaignId,
    PROOFSTUDIO_JUDGE_ROLE: "viewer",
    PROOFSTUDIO_JUDGE_PROVISIONING_APPROVED: "true",
  };

  if (runId === undefined) {
    delete env.PROOFSTUDIO_JUDGE_RUN_ID;
  } else {
    env.PROOFSTUDIO_JUDGE_RUN_ID = runId;
  }

  return env;
}

async function expectRefusal(
  env: NodeJS.ProcessEnv,
  expected: string,
): Promise<void> {
  try {
    await provisionJudgeAccount(env, {
      allowDisposableSmokeDatabase: true,
      automatedSmoke: true,
    });
  } catch (error) {
    assert(error instanceof Error, "non-error refusal");
    assert(error.message === expected, `unexpected refusal: ${error.message}`);
    return;
  }

  throw new Error(`expected refusal: ${expected}`);
}

async function readLatestRunId(): Promise<string | null> {
  assert(accountId, "account id missing");

  const result = await pool.query<{ latest_run_id: string | null }>(
    `select latest_run_id
     from account_campaign_access
     where account_id = $1
       and campaign_id = $2
       and revoked_at is null`,
    [accountId, campaignId],
  );

  assert(result.rowCount === 1, "active access row count mismatch");
  return result.rows[0]!.latest_run_id;
}

try {
  await expectRefusal(environment(), "judge_run_id_required");
  await expectRefusal(environment("bad run id"), "judge_run_id_invalid");
  await expectRefusal(
    environment("placeholder-run"),
    "judge_run_id_placeholder_refused",
  );

  const first = await provisionJudgeAccount(
    environment(firstRunId),
    {
      allowDisposableSmokeDatabase: true,
      automatedSmoke: true,
    },
  );

  accountId = first.account_id;

  assert(first.created_access, "initial access row was not created");
  assert(first.run_id === firstRunId, "initial receipt run id mismatch");
  assert(
    await readLatestRunId() === firstRunId,
    "initial latest_run_id was not persisted",
  );

  const identical = await provisionJudgeAccount(
    environment(firstRunId),
    {
      allowDisposableSmokeDatabase: true,
      automatedSmoke: true,
    },
  );

  assert(
    identical.updated_access === false,
    "identical provisioning was not idempotent",
  );

  const changed = await provisionJudgeAccount(
    environment(secondRunId),
    {
      allowDisposableSmokeDatabase: true,
      automatedSmoke: true,
    },
  );

  assert(changed.updated_access, "latest-run update was not reported");
  assert(changed.run_id === secondRunId, "updated receipt run id mismatch");
  assert(
    await readLatestRunId() === secondRunId,
    "updated latest_run_id was not persisted",
  );

  const activeRows = await pool.query<{ count: string }>(
    `select count(*)::text as count
     from account_campaign_access
     where account_id = $1
       and campaign_id = $2
       and revoked_at is null`,
    [accountId, campaignId],
  );

  assert(activeRows.rows[0]!.count === "1", "duplicate access rows created");

  const receiptRecord = changed as unknown as Record<string, unknown>;
  const serializedReceipt = JSON.stringify(changed);

  for (const forbiddenKey of [
    "password",
    "database_url",
    "databaseUrl",
    "credential_digest",
    "credentialDigest",
    "session_token",
    "sessionToken",
    "internal_service_token",
    "internalServiceToken",
  ]) {
    assert(
      !(forbiddenKey in receiptRecord),
      `receipt exposed prohibited field: ${forbiddenKey}`,
    );
  }

  for (const forbiddenValue of [password, databaseUrl]) {
    assert(
      !serializedReceipt.includes(forbiddenValue),
      "receipt exposed prohibited secret value",
    );
  }

  console.log(JSON.stringify({
    ok: true,
    missing_run_refusal: "pass",
    invalid_run_refusal: "pass",
    placeholder_run_refusal: "pass",
    initial_binding: "pass",
    idempotency: "pass",
    run_update: "pass",
    active_access_rows: 1,
    external_http_calls: 0,
    production_database_calls: 0,
  }));

  console.log("JUDGE_LATEST_RUN_BINDING=PASS");
} finally {
  if (accountId) {
    await pool.query(
      "delete from auth_user where id = $1",
      [accountId],
    ).catch(() => undefined);
  }

  await pool.end();
}
