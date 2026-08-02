CREATE TYPE "public"."campaign_access_role" AS ENUM('owner', 'reviewer', 'viewer');--> statement-breakpoint
CREATE TABLE "account_campaign_access" (
	"account_id" text NOT NULL,
	"campaign_id" text NOT NULL,
	"latest_run_id" text,
	"access_role" "campaign_access_role" NOT NULL,
	"linked_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"revoked_at" timestamp with time zone,
	CONSTRAINT "account_campaign_access_campaign_not_blank" CHECK (btrim("account_campaign_access"."campaign_id") <> '')
);
--> statement-breakpoint
ALTER TABLE "account_campaign_access" ADD CONSTRAINT "account_campaign_access_account_id_auth_user_id_fk" FOREIGN KEY ("account_id") REFERENCES "public"."auth_user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE UNIQUE INDEX "account_campaign_access_active_account_campaign_idx" ON "account_campaign_access" USING btree ("account_id","campaign_id") WHERE "account_campaign_access"."revoked_at" is null;--> statement-breakpoint
CREATE INDEX "account_campaign_access_account_list_idx" ON "account_campaign_access" USING btree ("account_id","revoked_at","linked_at","campaign_id");--> statement-breakpoint
CREATE INDEX "account_campaign_access_campaign_lookup_idx" ON "account_campaign_access" USING btree ("campaign_id","revoked_at");