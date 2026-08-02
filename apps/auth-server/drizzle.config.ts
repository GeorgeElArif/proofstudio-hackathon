import { defineConfig } from "drizzle-kit";

const placeholderDatabaseUrls = new Set([
  "",
  "postgres://replace-with-host/replace-with-database",
  "postgresql://replace-with-host/replace-with-database",
]);

const databaseUrl = process.env.PROOFSTUDIO_DATABASE_URL ?? process.env.DATABASE_URL ?? "";

export default defineConfig({
  dialect: "postgresql",
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dbCredentials: {
    url: placeholderDatabaseUrls.has(databaseUrl)
      ? "postgres://placeholder.invalid/placeholder"
      : databaseUrl,
  },
  strict: true,
  verbose: true,
});
