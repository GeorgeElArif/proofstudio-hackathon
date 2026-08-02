import { readFile, readdir } from "node:fs/promises";
import { resolve } from "node:path";

import pg from "pg";

import { getSmokeDatabaseUrl } from "./ps040f-config.js";
import { assertSafeDatabaseUrlForSmoke, summarizeDatabaseUrlSafety } from "../src/db/url-safety.js";

const requiredTables = [
  "auth_user",
  "auth_account",
  "auth_session",
  "auth_verification",
  "auth_audit_event",
  "auth_email_domain_policy_entry",
  "auth_rate_limit",
  "auth_role",
  "auth_membership",
];
const requiredTextIdColumns = [
  ["auth_user", "id"],
  ["auth_account", "id"],
  ["auth_account", "user_id"],
  ["auth_session", "id"],
  ["auth_session", "user_id"],
  ["auth_verification", "id"],
  ["auth_rate_limit", "id"],
  ["auth_audit_event", "user_id"],
  ["auth_audit_event", "actor_user_id"],
  ["auth_membership", "user_id"],
];

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

function splitDrizzleMigration(sql: string): string[] {
  return sql
    .split("--> statement-breakpoint")
    .map((statement) => statement.trim())
    .filter(Boolean);
}

const databaseUrl = getSmokeDatabaseUrl();
const allowNonLocal = process.env.AUTH_ALLOW_NONLOCAL_TEST_DB === "true";
const safety = assertSafeDatabaseUrlForSmoke(databaseUrl, {
  allowNonlocalTestDb: allowNonLocal,
  action: "migration smoke",
});

const pool = new pg.Pool({ connectionString: databaseUrl });
const client = await pool.connect();

async function applyMigrationFile(fileName: string): Promise<void> {
  const migrationSql = await readFile(resolve("drizzle", fileName), "utf8");
  for (const statement of splitDrizzleMigration(migrationSql)) {
    await client.query(statement);
  }
}

async function getMigrationFiles(): Promise<string[]> {
  const files = await readdir(resolve("drizzle"));
  return files.filter((file) => /^\d+_.+\.sql$/.test(file)).sort();
}

async function coreIdColumnsAreText(): Promise<boolean> {
  const columnResult = await client.query<{ table_name: string; column_name: string; data_type: string }>(
    `
      select table_name, column_name, data_type
      from information_schema.columns
      where table_schema = 'public'
        and (table_name, column_name) in (
          ${requiredTextIdColumns.map((_, index) => `($${index * 2 + 1}, $${index * 2 + 2})`).join(", ")}
        )
    `,
    requiredTextIdColumns.flat(),
  );
  const typeByColumn = new Map(
    columnResult.rows.map((row) => [`${row.table_name}.${row.column_name}`, row.data_type]),
  );
  return requiredTextIdColumns.every(([table, column]) => typeByColumn.get(`${table}.${column}`) === "text");
}

try {
  await client.query("select 1");
  const existing = await client.query<{ table_name: string }>(
    `
      select table_name
      from information_schema.tables
      where table_schema = 'public'
        and table_name = 'auth_user'
    `,
  );

  let appliedMigrationFiles: string[] = [];
  if (existing.rowCount === 0) {
    await client.query("begin");
    for (const fileName of await getMigrationFiles()) {
      await applyMigrationFile(fileName);
      appliedMigrationFiles.push(fileName);
    }
    await client.query("commit");
  } else if (!(await coreIdColumnsAreText())) {
    await client.query("begin");
    const pendingFiles = (await getMigrationFiles()).filter((fileName) => fileName !== "0000_bent_bullseye.sql");
    for (const fileName of pendingFiles) {
      await applyMigrationFile(fileName);
      appliedMigrationFiles.push(fileName);
    }
    await client.query("commit");
  }

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
  assert(await coreIdColumnsAreText(), "Better Auth core ID columns should be text-compatible");

  console.log(JSON.stringify({
    smoke: "ps040f_migration_apply",
    result: "passed",
    appliedMigrationFiles,
    requiredTablesPresent: requiredTables.length,
    database: summarizeDatabaseUrlSafety(safety),
  }));
} catch (error) {
  try {
    await client.query("rollback");
  } catch {
    // Original error is the useful failure.
  }
  throw error;
} finally {
  client.release();
  await pool.end();
}
