export type DatabaseUrlSafetyClassification =
  | "missing"
  | "local_test"
  | "explicit_nonlocal_test_allowed"
  | "unsafe_nonlocal"
  | "production_like"
  | "invalid";

export type DatabaseUrlSafety = {
  classification: DatabaseUrlSafetyClassification;
  safeForSmoke: boolean;
  protocol: string | null;
  host: string | null;
  databaseName: string | null;
  reasons: string[];
};

const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", "::1"]);
const TEST_NAME_MARKERS = ["test", "local", "smoke", "dev"];
const PRODUCTION_MARKERS = ["prod", "production", "supabase.co", "amazonaws.com", "azure.com", "neon.tech"];

function containsAny(value: string, markers: string[]): boolean {
  const normalized = value.toLowerCase();
  return markers.some((marker) => normalized.includes(marker));
}

function stripLeadingSlash(value: string): string {
  return value.replace(/^\/+/, "");
}

export function classifyDatabaseUrlSafety(
  rawUrl: string | undefined,
  options: { allowNonlocalTestDb?: boolean } = {},
): DatabaseUrlSafety {
  const value = rawUrl?.trim() ?? "";
  if (!value) {
    return {
      classification: "missing",
      safeForSmoke: false,
      protocol: null,
      host: null,
      databaseName: null,
      reasons: ["database_url_missing"],
    };
  }

  let parsed: URL;
  try {
    parsed = new URL(value);
  } catch {
    return {
      classification: "invalid",
      safeForSmoke: false,
      protocol: null,
      host: null,
      databaseName: null,
      reasons: ["database_url_invalid"],
    };
  }

  const protocol = parsed.protocol.replace(/:$/, "");
  const host = parsed.hostname.toLowerCase();
  const databaseName = stripLeadingSlash(decodeURIComponent(parsed.pathname)).toLowerCase();
  const fullWithoutSecret = `${protocol}://${host}/${databaseName}`;

  if (protocol !== "postgres" && protocol !== "postgresql") {
    return {
      classification: "invalid",
      safeForSmoke: false,
      protocol,
      host,
      databaseName,
      reasons: ["database_url_not_postgres"],
    };
  }

  if (containsAny(fullWithoutSecret, PRODUCTION_MARKERS)) {
    return {
      classification: "production_like",
      safeForSmoke: false,
      protocol,
      host,
      databaseName,
      reasons: ["database_url_production_like"],
    };
  }

  const isLocal = LOCAL_HOSTS.has(host);
  const namesDisposableTestDb = containsAny(databaseName, TEST_NAME_MARKERS);

  if (isLocal && namesDisposableTestDb) {
    return {
      classification: "local_test",
      safeForSmoke: true,
      protocol,
      host,
      databaseName,
      reasons: ["database_url_local_disposable_test"],
    };
  }

  if (isLocal) {
    return {
      classification: "unsafe_nonlocal",
      safeForSmoke: false,
      protocol,
      host,
      databaseName,
      reasons: ["local_database_name_not_disposable_test"],
    };
  }

  if (options.allowNonlocalTestDb && namesDisposableTestDb) {
    return {
      classification: "explicit_nonlocal_test_allowed",
      safeForSmoke: true,
      protocol,
      host,
      databaseName,
      reasons: ["nonlocal_disposable_test_db_explicitly_allowed"],
    };
  }

  return {
    classification: "unsafe_nonlocal",
    safeForSmoke: false,
    protocol,
    host,
    databaseName,
    reasons: ["nonlocal_database_not_allowed_for_smoke"],
  };
}

export function summarizeDatabaseUrlSafety(safety: DatabaseUrlSafety): Record<string, unknown> {
  return {
    classification: safety.classification,
    safeForSmoke: safety.safeForSmoke,
    protocol: safety.protocol,
    host: safety.host,
    databaseName: safety.databaseName,
    reasons: safety.reasons,
  };
}

export function assertSafeDatabaseUrlForSmoke(
  rawUrl: string | undefined,
  options: { allowNonlocalTestDb?: boolean; action: string },
): DatabaseUrlSafety {
  const safety = classifyDatabaseUrlSafety(rawUrl, options);
  if (!safety.safeForSmoke) {
    throw new Error(
      `Refusing ${options.action}: database URL safety classification is ${safety.classification} (${safety.reasons.join(", ")}).`,
    );
  }
  return safety;
}
