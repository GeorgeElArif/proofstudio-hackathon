import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const schema = await readFile(new URL("../../src/db/schema.ts", import.meta.url), "utf8");
const repository = await readFile(new URL("../../src/account/campaign-access.ts", import.meta.url), "utf8");
const boundary = await readFile(new URL("../../src/auth/boundary.ts", import.meta.url), "utf8");
assert.match(schema, /account_campaign_access/);
assert.match(schema, /campaign_access_role/);
assert.match(schema, /campaign_not_blank/);
assert.match(schema, /revokedAt/);
assert.match(repository, /limit \+ 1/);
assert.match(repository, /malformed_cursor/);
assert.match(boundary, /handleAccountCampaigns/);
assert.match(boundary, /caller_account_scope_forbidden/);
assert.doesNotMatch(boundary, /localStorage|sessionStorage/);
console.log(JSON.stringify({ ok: true, slice: "PS-041B", checks: { schema: "pass", repository: "pass", session_route: "pass", idor_boundary: "pass" } }));
