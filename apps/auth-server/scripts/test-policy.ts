import { writeAuthAuditEvent } from "../src/auth/audit.js";
import {
  DEFAULT_DISPOSABLE_DOMAINS,
  evaluateEmailDomainPolicy,
  extractNormalizedEmailDomain,
} from "../src/auth/domain-policy.js";
import { getEmailDeliveryReadiness, sendVerificationEmailFoundation } from "../src/auth/email.js";
import { InMemoryAuthRateLimiter } from "../src/auth/rate-limit.js";
import { permissionsForRole, roleHasPermission, rolesHavePermission } from "../src/auth/rbac.js";
import { loadAuthRuntimeEnv } from "../src/env.js";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

const parsed = extractNormalizedEmailDomain(" USER@Example.COM ");
assert(parsed.allowed, "valid email should parse");
assert(parsed.normalizedEmail === "user@example.com", "email should normalize");
assert(parsed.domain === "example.com", "domain should normalize");

assert(!extractNormalizedEmailDomain("not-an-email").allowed, "invalid email syntax should be blocked");
assert(
  !evaluateEmailDomainPolicy("person@10minutemail.com").allowed,
  "default disposable domain should be blocked",
);
assert(
  evaluateEmailDomainPolicy("person@mailinator.com", {
    allowlist: ["mailinator.com"],
    disposableDomains: DEFAULT_DISPOSABLE_DOMAINS,
  }).allowed,
  "allowlisted domain should be allowed before disposable blocking",
);
assert(
  !evaluateEmailDomainPolicy("person@blocked.test", { blocklist: ["blocked.test"] }).allowed,
  "blocked domain should be blocked",
);
assert(
  !evaluateEmailDomainPolicy("person@TEMPMAIL.COM").allowed,
  "case-normalized disposable domain should be blocked",
);

assert(roleHasPermission("owner", "auth.manage"), "owner should manage auth");
assert(roleHasPermission("reviewer", "audit.read"), "reviewer should read audit");
assert(!roleHasPermission("viewer", "audit.read"), "viewer should not read audit");
assert(rolesHavePermission(["viewer", "reviewer"], "audit.read"), "combined roles should grant audit read");
assert(
  permissionsForRole("owner").length === 4,
  "owner should have all account-auth permissions in PS-040D",
);

let now = 1_000;
const limiter = new InMemoryAuthRateLimiter({
  windowMs: 1_000,
  maxAttempts: 2,
  now: () => now,
});
assert(limiter.attempt("login:user@example.com").allowed, "first attempt should be allowed");
assert(limiter.attempt("login:user@example.com").allowed, "second attempt should be allowed");
assert(!limiter.attempt("login:user@example.com").allowed, "third attempt should be rate limited");
now = 2_050;
assert(limiter.attempt("login:user@example.com").allowed, "attempt after window should reset");

const noEnv = loadAuthRuntimeEnv({});
assert(getEmailDeliveryReadiness(noEnv).status === "unavailable", "missing email env should be unavailable");
assert(
  (await sendVerificationEmailFoundation(noEnv, {
    to: "user@example.com",
    verificationUrl: "https://example.localhost/verify",
  })).status === "unavailable",
  "missing email env should not fake delivery",
);
assert(
  (await writeAuthAuditEvent(null, {
    eventType: "login_failed",
    outcome: "unavailable",
    reason: "no_database",
  })).status === "unavailable",
  "missing database should not fake audit persistence",
);

console.log("PS-040D policy tests passed.");
