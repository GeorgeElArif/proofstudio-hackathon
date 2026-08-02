import { writeAuthAuditEvent } from "../src/auth/audit.js";
import { evaluateEmailDomainPolicy } from "../src/auth/domain-policy.js";
import { getEmailDeliveryReadiness, sendVerificationEmailFoundation } from "../src/auth/email.js";
import { InMemoryAuthRateLimiter } from "../src/auth/rate-limit.js";
import { roleHasPermission } from "../src/auth/rbac.js";
import { getAuthRuntimeReadiness, loadAuthRuntimeEnv } from "../src/env.js";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

const noEnv = loadAuthRuntimeEnv({});
const readiness = getAuthRuntimeReadiness(noEnv);
assert(readiness.processLive, "readiness should remain process-live");
assert(!readiness.authRuntimeAvailable, "auth runtime should not be available without env");
assert(readiness.providers.email.status === "missing", "email should be safely missing");

const emailReadiness = getEmailDeliveryReadiness(noEnv);
assert(emailReadiness.status === "unavailable", "email delivery should be unavailable without env");
assert(
  (await sendVerificationEmailFoundation(noEnv, {
    to: "person@example.com",
    verificationUrl: "https://example.localhost/verify",
  })).status === "unavailable",
  "verification email should not report sent without provider env",
);

assert(
  evaluateEmailDomainPolicy("Person@Mailinator.com").reason === "disposable_domain",
  "disposable domain should be blocked",
);
assert(
  evaluateEmailDomainPolicy("Person@Allowed.test", { allowlist: ["allowed.test"] }).allowed,
  "allowlisted domain should be allowed",
);

let now = 10_000;
const limiter = new InMemoryAuthRateLimiter({
  maxAttempts: 1,
  windowMs: 500,
  now: () => now,
});
assert(limiter.attempt("signup:person@example.com").allowed, "first auth-sensitive attempt should pass");
assert(!limiter.attempt("signup:person@example.com").allowed, "repeated attempt should be blocked");
now += 600;
assert(limiter.attempt("signup:person@example.com").allowed, "window expiry should reset local counter");

assert(roleHasPermission("owner", "auth.manage"), "owner role should manage auth");
assert(!roleHasPermission("viewer", "auth.manage"), "viewer role should not manage auth");

const audit = await writeAuthAuditEvent(null, {
  eventType: "login_failed",
  outcome: "unavailable",
  reason: "database_not_configured",
  metadata: { email: "person@example.com", token: "should-redact-if-persisted" },
});
assert(audit.status === "unavailable", "audit writer should not fake persistence without DB");

console.log("PS-040D auth behavior smoke passed.");
