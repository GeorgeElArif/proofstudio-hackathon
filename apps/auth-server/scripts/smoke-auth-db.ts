import pg from "pg";

import { getSmokeDatabaseUrl } from "./ps040f-config.js";
import { assertSafeDatabaseUrlForSmoke, summarizeDatabaseUrlSafety } from "../src/db/url-safety.js";

const databaseUrl = getSmokeDatabaseUrl();
const allowNonLocal = process.env.PROOFSTUDIO_AUTH_DB_SMOKE_ALLOW_NONLOCAL === "true";

const requiredTables = [
  "auth_user",
  "auth_account",
  "auth_session",
  "auth_verification",
  "auth_audit_event",
  "auth_email_domain_policy_entry",
  "auth_rate_limit",
];

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

const safety = assertSafeDatabaseUrlForSmoke(databaseUrl, {
  allowNonlocalTestDb: allowNonLocal,
  action: "DB smoke",
});

const pool = new pg.Pool({ connectionString: databaseUrl });
const client = await pool.connect();

try {
  await client.query("select 1");

  const tableResult = await client.query<{ table_name: string }>(
    `
      select table_name
      from information_schema.tables
      where table_schema = 'public'
        and table_name = any($1)
    `,
    [requiredTables],
  );
  const presentTables = new Set(tableResult.rows.map((row) => row.table_name));
  const missingTables = requiredTables.filter((table) => !presentTables.has(table));
  assert(missingTables.length === 0, `missing auth schema tables: ${missingTables.join(", ")}`);

  await client.query("begin");
  await client.query(
    `
      insert into auth_audit_event (event_type, metadata)
      values ('login_failed', '{"source":"ps040d_db_smoke","outcome":"rolled_back"}'::jsonb)
    `,
  );
  await client.query(
    `
      insert into auth_rate_limit (id, key, count, last_request)
      values ('ps040f-db-smoke-rate-limit', 'ps040d-db-smoke', 1, extract(epoch from now())::bigint)
      on conflict (key) do update
      set count = auth_rate_limit.count + 1,
          last_request = excluded.last_request
    `,
  );
  await client.query("rollback");

  console.log(JSON.stringify({
    smoke: "ps040f_auth_db",
    result: "passed",
    database: summarizeDatabaseUrlSafety(safety),
  }));
} catch (error) {
  try {
    await client.query("rollback");
  } catch {
    // Ignore rollback failure; the original error is more useful.
  }
  throw error;
} finally {
  client.release();
  await pool.end();
}
