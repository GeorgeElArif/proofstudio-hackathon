export type RateLimitDecision = {
  allowed: boolean;
  key: string;
  count: number;
  limit: number;
  resetAt: number;
  reason: "allowed" | "rate_limited";
};

export type RateLimitConfig = {
  windowMs: number;
  maxAttempts: number;
  now?: () => number;
};

type Bucket = {
  count: number;
  windowStart: number;
};

export class InMemoryAuthRateLimiter {
  private readonly buckets = new Map<string, Bucket>();
  private readonly now: () => number;

  constructor(private readonly config: RateLimitConfig) {
    this.now = config.now ?? Date.now;
  }

  attempt(key: string): RateLimitDecision {
    const now = this.now();
    const existing = this.buckets.get(key);
    const bucket =
      existing && now - existing.windowStart < this.config.windowMs
        ? existing
        : { count: 0, windowStart: now };

    bucket.count += 1;
    this.buckets.set(key, bucket);

    const resetAt = bucket.windowStart + this.config.windowMs;
    if (bucket.count > this.config.maxAttempts) {
      return {
        allowed: false,
        key,
        count: bucket.count,
        limit: this.config.maxAttempts,
        resetAt,
        reason: "rate_limited",
      };
    }

    return {
      allowed: true,
      key,
      count: bucket.count,
      limit: this.config.maxAttempts,
      resetAt,
      reason: "allowed",
    };
  }

  reset(key: string): void {
    this.buckets.delete(key);
  }
}
