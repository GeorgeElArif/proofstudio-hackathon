import {
  bigint,
  boolean,
  index,
  integer,
  jsonb,
  pgEnum,
  pgTable,
  primaryKey,
  text,
  timestamp,
  uniqueIndex,
  uuid,
  check,
} from "drizzle-orm/pg-core";
import { sql } from "drizzle-orm";

export const authRoleScope = pgEnum("auth_role_scope", ["global", "account", "team"]);
export const authDomainPolicyKind = pgEnum("auth_domain_policy_kind", ["allow", "block", "disposable"]);
export const campaignAccessRole = pgEnum("campaign_access_role", ["owner", "reviewer", "viewer"]);
export const authAuditEventType = pgEnum("auth_audit_event_type", [
  "signup_requested",
  "email_verification_requested",
  "email_verified",
  "login_succeeded",
  "login_failed",
  "logout",
  "session_revoked",
  "oauth_linked",
  "role_changed",
  "domain_policy_changed",
  "rate_limit_triggered",
]);

export const user = pgTable(
  "auth_user",
  {
    id: text("id").primaryKey(),
    name: text("name").notNull(),
    email: text("email").notNull(),
    email_normalized: text("email_normalized").notNull(),
    email_verified: boolean("email_verified").default(false).notNull(),
    image: text("image"),
    username: text("username"),
    email_verified_at: timestamp("email_verified_at", { withTimezone: true }),
    disabled_at: timestamp("disabled_at", { withTimezone: true }),
    created_at: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
    updated_at: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (table) => ({
    emailIdx: uniqueIndex("auth_user_email_normalized_idx").on(table.email_normalized),
    usernameIdx: uniqueIndex("auth_user_username_idx").on(table.username),
  }),
);

export const account = pgTable(
  "auth_account",
  {
    id: text("id").primaryKey(),
    user_id: text("user_id")
      .notNull()
      .references(() => user.id, { onDelete: "cascade" }),
    provider_id: text("provider_id").notNull(),
    account_id: text("account_id").notNull(),
    access_token: text("access_token"),
    refresh_token: text("refresh_token"),
    id_token: text("id_token"),
    access_token_expires_at: timestamp("access_token_expires_at", { withTimezone: true }),
    refresh_token_expires_at: timestamp("refresh_token_expires_at", { withTimezone: true }),
    scope: text("scope"),
    password: text("password"),
    created_at: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
    updated_at: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (table) => ({
    providerAccountIdx: uniqueIndex("auth_account_provider_account_idx").on(
      table.provider_id,
      table.account_id,
    ),
    userIdx: index("auth_account_user_idx").on(table.user_id),
  }),
);

export const session = pgTable(
  "auth_session",
  {
    id: text("id").primaryKey(),
    user_id: text("user_id")
      .notNull()
      .references(() => user.id, { onDelete: "cascade" }),
    token: text("token").notNull(),
    ip_address: text("ip_address"),
    user_agent: text("user_agent"),
    expires_at: timestamp("expires_at", { withTimezone: true }).notNull(),
    revoked_at: timestamp("revoked_at", { withTimezone: true }),
    created_at: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
    updated_at: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (table) => ({
    tokenIdx: uniqueIndex("auth_session_token_idx").on(table.token),
    userIdx: index("auth_session_user_idx").on(table.user_id),
  }),
);

export const verification = pgTable(
  "auth_verification",
  {
    id: text("id").primaryKey(),
    identifier: text("identifier").notNull(),
    value: text("value").notNull(),
    purpose: text("purpose").notNull(),
    expires_at: timestamp("expires_at", { withTimezone: true }).notNull(),
    consumed_at: timestamp("consumed_at", { withTimezone: true }),
    created_at: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
    updated_at: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (table) => ({
    valueIdx: uniqueIndex("auth_verification_value_idx").on(table.value),
    identifierIdx: index("auth_verification_identifier_idx").on(table.identifier),
  }),
);

export const rateLimit = pgTable(
  "auth_rate_limit",
  {
    id: text("id").primaryKey(),
    key: text("key").notNull(),
    count: integer("count").default(0).notNull(),
    last_request: bigint("last_request", { mode: "number" }).notNull(),
  },
  (table) => ({
    keyIdx: uniqueIndex("auth_rate_limit_key_idx").on(table.key),
  }),
);

export const authRoles = pgTable(
  "auth_role",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    name: text("name").notNull(),
    scope: authRoleScope("scope").notNull(),
    description: text("description"),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (table) => ({
    nameScopeIdx: uniqueIndex("auth_role_name_scope_idx").on(table.name, table.scope),
  }),
);

export const authMemberships = pgTable(
  "auth_membership",
  {
    userId: text("user_id")
      .notNull()
      .references(() => user.id, { onDelete: "cascade" }),
    roleId: uuid("role_id")
      .notNull()
      .references(() => authRoles.id, { onDelete: "cascade" }),
    accountScopeId: text("account_scope_id"),
    activatedAt: timestamp("activated_at", { withTimezone: true }).defaultNow().notNull(),
    disabledAt: timestamp("disabled_at", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (table) => ({
    pk: primaryKey({ columns: [table.userId, table.roleId, table.accountScopeId] }),
    userIdx: index("auth_membership_user_idx").on(table.userId),
  }),
);

export const authAuditEvents = pgTable(
  "auth_audit_event",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    userId: text("user_id").references(() => user.id, { onDelete: "set null" }),
    eventType: authAuditEventType("event_type").notNull(),
    actorUserId: text("actor_user_id").references(() => user.id, { onDelete: "set null" }),
    ipHash: text("ip_hash"),
    userAgentHash: text("user_agent_hash"),
    metadata: jsonb("metadata"),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (table) => ({
    userCreatedIdx: index("auth_audit_event_user_created_idx").on(table.userId, table.createdAt),
    eventCreatedIdx: index("auth_audit_event_type_created_idx").on(table.eventType, table.createdAt),
  }),
);

export const authEmailDomainPolicyEntries = pgTable(
  "auth_email_domain_policy_entry",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    domain: text("domain").notNull(),
    kind: authDomainPolicyKind("kind").notNull(),
    source: text("source").notNull(),
    reason: text("reason"),
    active: boolean("active").default(true).notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (table) => ({
    domainKindIdx: uniqueIndex("auth_email_domain_policy_domain_kind_idx").on(table.domain, table.kind),
    activeDomainIdx: index("auth_email_domain_policy_active_domain_idx").on(table.active, table.domain),
  }),
);

export const accountCampaignAccess = pgTable(
  "account_campaign_access",
  {
    accountId: text("account_id").notNull().references(() => user.id, { onDelete: "cascade" }),
    campaignId: text("campaign_id").notNull(),
    latestRunId: text("latest_run_id"),
    accessRole: campaignAccessRole("access_role").notNull(),
    linkedAt: timestamp("linked_at", { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
    revokedAt: timestamp("revoked_at", { withTimezone: true }),
  },
  (table) => ({
    activeAccountCampaignIdx: uniqueIndex("account_campaign_access_active_account_campaign_idx")
      .on(table.accountId, table.campaignId).where(sql`${table.revokedAt} is null`),
    accountListIdx: index("account_campaign_access_account_list_idx")
      .on(table.accountId, table.revokedAt, table.linkedAt, table.campaignId),
    campaignLookupIdx: index("account_campaign_access_campaign_lookup_idx")
      .on(table.campaignId, table.revokedAt),
    campaignNotBlank: check("account_campaign_access_campaign_not_blank", sql`btrim(${table.campaignId}) <> ''`),
  }),
);
