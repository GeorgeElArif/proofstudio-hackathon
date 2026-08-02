CREATE TYPE "public"."auth_audit_event_type" AS ENUM('signup_requested', 'email_verification_requested', 'email_verified', 'login_succeeded', 'login_failed', 'logout', 'session_revoked', 'oauth_linked', 'role_changed', 'domain_policy_changed', 'rate_limit_triggered');--> statement-breakpoint
CREATE TYPE "public"."auth_domain_policy_kind" AS ENUM('allow', 'block', 'disposable');--> statement-breakpoint
CREATE TYPE "public"."auth_role_scope" AS ENUM('global', 'account', 'team');--> statement-breakpoint
CREATE TABLE "auth_account" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"provider_id" text NOT NULL,
	"account_id" text NOT NULL,
	"access_token" text,
	"refresh_token" text,
	"id_token" text,
	"access_token_expires_at" timestamp with time zone,
	"refresh_token_expires_at" timestamp with time zone,
	"scope" text,
	"password" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "auth_audit_event" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid,
	"event_type" "auth_audit_event_type" NOT NULL,
	"actor_user_id" uuid,
	"ip_hash" text,
	"user_agent_hash" text,
	"metadata" jsonb,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "auth_email_domain_policy_entry" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"domain" text NOT NULL,
	"kind" "auth_domain_policy_kind" NOT NULL,
	"source" text NOT NULL,
	"reason" text,
	"active" boolean DEFAULT true NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "auth_membership" (
	"user_id" uuid NOT NULL,
	"role_id" uuid NOT NULL,
	"account_scope_id" text,
	"activated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"disabled_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "auth_membership_user_id_role_id_account_scope_id_pk" PRIMARY KEY("user_id","role_id","account_scope_id")
);
--> statement-breakpoint
CREATE TABLE "auth_role" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"name" text NOT NULL,
	"scope" "auth_role_scope" NOT NULL,
	"description" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "auth_rate_limit" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"key" text NOT NULL,
	"count" integer DEFAULT 0 NOT NULL,
	"last_request" bigint NOT NULL
);
--> statement-breakpoint
CREATE TABLE "auth_session" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"token" text NOT NULL,
	"ip_address" text,
	"user_agent" text,
	"expires_at" timestamp with time zone NOT NULL,
	"revoked_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "auth_user" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"name" text NOT NULL,
	"email" text NOT NULL,
	"email_normalized" text NOT NULL,
	"email_verified" boolean DEFAULT false NOT NULL,
	"image" text,
	"username" text,
	"email_verified_at" timestamp with time zone,
	"disabled_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "auth_verification" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"identifier" text NOT NULL,
	"value" text NOT NULL,
	"purpose" text NOT NULL,
	"expires_at" timestamp with time zone NOT NULL,
	"consumed_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "auth_account" ADD CONSTRAINT "auth_account_user_id_auth_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "auth_audit_event" ADD CONSTRAINT "auth_audit_event_user_id_auth_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "auth_audit_event" ADD CONSTRAINT "auth_audit_event_actor_user_id_auth_user_id_fk" FOREIGN KEY ("actor_user_id") REFERENCES "public"."auth_user"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "auth_membership" ADD CONSTRAINT "auth_membership_user_id_auth_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "auth_membership" ADD CONSTRAINT "auth_membership_role_id_auth_role_id_fk" FOREIGN KEY ("role_id") REFERENCES "public"."auth_role"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "auth_session" ADD CONSTRAINT "auth_session_user_id_auth_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE UNIQUE INDEX "auth_account_provider_account_idx" ON "auth_account" USING btree ("provider_id","account_id");--> statement-breakpoint
CREATE INDEX "auth_account_user_idx" ON "auth_account" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX "auth_audit_event_user_created_idx" ON "auth_audit_event" USING btree ("user_id","created_at");--> statement-breakpoint
CREATE INDEX "auth_audit_event_type_created_idx" ON "auth_audit_event" USING btree ("event_type","created_at");--> statement-breakpoint
CREATE UNIQUE INDEX "auth_email_domain_policy_domain_kind_idx" ON "auth_email_domain_policy_entry" USING btree ("domain","kind");--> statement-breakpoint
CREATE INDEX "auth_email_domain_policy_active_domain_idx" ON "auth_email_domain_policy_entry" USING btree ("active","domain");--> statement-breakpoint
CREATE INDEX "auth_membership_user_idx" ON "auth_membership" USING btree ("user_id");--> statement-breakpoint
CREATE UNIQUE INDEX "auth_role_name_scope_idx" ON "auth_role" USING btree ("name","scope");--> statement-breakpoint
CREATE UNIQUE INDEX "auth_rate_limit_key_idx" ON "auth_rate_limit" USING btree ("key");--> statement-breakpoint
CREATE UNIQUE INDEX "auth_session_token_idx" ON "auth_session" USING btree ("token");--> statement-breakpoint
CREATE INDEX "auth_session_user_idx" ON "auth_session" USING btree ("user_id");--> statement-breakpoint
CREATE UNIQUE INDEX "auth_user_email_normalized_idx" ON "auth_user" USING btree ("email_normalized");--> statement-breakpoint
CREATE UNIQUE INDEX "auth_user_username_idx" ON "auth_user" USING btree ("username");--> statement-breakpoint
CREATE UNIQUE INDEX "auth_verification_value_idx" ON "auth_verification" USING btree ("value");--> statement-breakpoint
CREATE INDEX "auth_verification_identifier_idx" ON "auth_verification" USING btree ("identifier");