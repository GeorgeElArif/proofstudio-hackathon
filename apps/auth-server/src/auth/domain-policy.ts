export type DomainPolicyDecision = {
  allowed: boolean;
  normalizedEmail?: string;
  domain?: string;
  reason:
    | "allowed"
    | "allowlisted"
    | "invalid_email_syntax"
    | "blocked_domain"
    | "disposable_domain";
};

export type DomainPolicyConfig = {
  allowlist?: string[];
  blocklist?: string[];
  disposableDomains?: string[];
};

export const DEFAULT_DISPOSABLE_DOMAINS = [
  "10minutemail.com",
  "mailinator.com",
  "tempmail.com",
  "trashmail.com",
];

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function normalizeDomainList(values: string[] | undefined): Set<string> {
  return new Set((values ?? []).map((value) => value.trim().toLowerCase()).filter(Boolean));
}

export function extractNormalizedEmailDomain(email: string): DomainPolicyDecision {
  const normalizedEmail = email.trim().toLowerCase();
  if (!EMAIL_PATTERN.test(normalizedEmail)) {
    return { allowed: false, reason: "invalid_email_syntax" };
  }

  const [, domain] = normalizedEmail.split("@");
  if (!domain || domain.startsWith(".") || domain.endsWith(".") || domain.includes("..")) {
    return { allowed: false, reason: "invalid_email_syntax" };
  }

  return { allowed: true, normalizedEmail, domain, reason: "allowed" };
}

export function evaluateEmailDomainPolicy(
  email: string,
  config: DomainPolicyConfig = {},
): DomainPolicyDecision {
  const parsed = extractNormalizedEmailDomain(email);
  if (!parsed.allowed || !parsed.domain || !parsed.normalizedEmail) {
    return parsed;
  }

  const allowlist = normalizeDomainList(config.allowlist);
  const blocklist = normalizeDomainList(config.blocklist);
  const disposableDomains = normalizeDomainList(config.disposableDomains ?? DEFAULT_DISPOSABLE_DOMAINS);

  if (allowlist.has(parsed.domain)) {
    return { ...parsed, allowed: true, reason: "allowlisted" };
  }
  if (blocklist.has(parsed.domain)) {
    return { ...parsed, allowed: false, reason: "blocked_domain" };
  }
  if (disposableDomains.has(parsed.domain)) {
    return { ...parsed, allowed: false, reason: "disposable_domain" };
  }

  return parsed;
}
