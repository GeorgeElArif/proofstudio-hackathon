import { drizzle } from "drizzle-orm/node-postgres";
import pg from "pg";

import * as schema from "./schema.js";

export type AuthDatabase = ReturnType<typeof createAuthDatabase>;

export function createAuthDatabase(databaseUrl: string) {
  if (!databaseUrl || databaseUrl.includes("replace-with") || databaseUrl.includes("placeholder")) {
    throw new Error("PROOFSTUDIO_DATABASE_URL must be configured before creating the auth database client.");
  }

  const pool = new pg.Pool({ connectionString: databaseUrl });
  return {
    db: drizzle(pool, { schema }),
    async checkReady(): Promise<void> {
      await pool.query("select 1");
    },
    async close(): Promise<void> {
      await pool.end();
    },
  };
}
