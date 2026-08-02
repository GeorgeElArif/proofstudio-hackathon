import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const authClient = readFileSync(resolve("src/authClient.ts"), "utf8");

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

assert(authClient.includes("/readyz"), "auth client should read auth-server readiness");
assert(authClient.includes("/session"), "auth client should read sanitized session endpoint");
assert(authClient.includes("/auth/sign-in/email"), "auth client should target Better Auth email sign-in");
assert(authClient.includes("/auth/sign-up/email"), "auth client should target Better Auth email sign-up");
assert(authClient.includes("/logout"), "auth client should target safe logout wrapper");
assert(authClient.includes('credentials: "include"'), "auth client should use cookie credentials");
assert(!authClient.includes("localStorage"), "auth client must not store auth in localStorage");
assert(!authClient.includes("sessionStorage"), "auth client must not store auth in sessionStorage");
assert(!authClient.includes("authenticated: true,"), "auth client must not force authenticated success");

console.log("PS-040E web auth client boundary smoke passed.");
