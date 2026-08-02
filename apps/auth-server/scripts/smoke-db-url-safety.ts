import { classifyDatabaseUrlSafety } from "../src/db/url-safety.js";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

assert(classifyDatabaseUrlSafety("").classification === "missing", "missing DB URL should be classified");
assert(classifyDatabaseUrlSafety("not a url").classification === "invalid", "invalid DB URL should be classified");
assert(
  classifyDatabaseUrlSafety("postgres://user:pass@127.0.0.1:55440/proofstudio_auth_smoke_test").classification ===
    "local_test",
  "local disposable test DB should be safe",
);
assert(
  classifyDatabaseUrlSafety("postgres://user:pass@db.example.net/proofstudio_auth_smoke_test", {
    allowNonlocalTestDb: true,
  }).classification === "explicit_nonlocal_test_allowed",
  "explicit nonlocal disposable test DB should be classified separately",
);
assert(
  classifyDatabaseUrlSafety("postgres://user:pass@db.example.net/proofstudio_auth_smoke_test").classification ===
    "unsafe_nonlocal",
  "nonlocal DB should be refused without override",
);
assert(
  classifyDatabaseUrlSafety("postgres://user:pass@db.supabase.co/proofstudio_prod").classification ===
    "production_like",
  "production-looking DB should be refused",
);

console.log("PS-040F DB URL safety classifier smoke passed.");
