ALTER TABLE "auth_account" DROP CONSTRAINT "auth_account_user_id_auth_user_id_fk";--> statement-breakpoint
ALTER TABLE "auth_audit_event" DROP CONSTRAINT "auth_audit_event_user_id_auth_user_id_fk";--> statement-breakpoint
ALTER TABLE "auth_audit_event" DROP CONSTRAINT "auth_audit_event_actor_user_id_auth_user_id_fk";--> statement-breakpoint
ALTER TABLE "auth_membership" DROP CONSTRAINT "auth_membership_user_id_auth_user_id_fk";--> statement-breakpoint
ALTER TABLE "auth_session" DROP CONSTRAINT "auth_session_user_id_auth_user_id_fk";--> statement-breakpoint
ALTER TABLE "auth_account" ALTER COLUMN "id" SET DATA TYPE text;--> statement-breakpoint
ALTER TABLE "auth_account" ALTER COLUMN "id" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "auth_account" ALTER COLUMN "user_id" SET DATA TYPE text;--> statement-breakpoint
ALTER TABLE "auth_audit_event" ALTER COLUMN "user_id" SET DATA TYPE text;--> statement-breakpoint
ALTER TABLE "auth_audit_event" ALTER COLUMN "actor_user_id" SET DATA TYPE text;--> statement-breakpoint
ALTER TABLE "auth_membership" ALTER COLUMN "user_id" SET DATA TYPE text;--> statement-breakpoint
ALTER TABLE "auth_rate_limit" ALTER COLUMN "id" SET DATA TYPE text;--> statement-breakpoint
ALTER TABLE "auth_rate_limit" ALTER COLUMN "id" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "auth_session" ALTER COLUMN "id" SET DATA TYPE text;--> statement-breakpoint
ALTER TABLE "auth_session" ALTER COLUMN "id" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "auth_session" ALTER COLUMN "user_id" SET DATA TYPE text;--> statement-breakpoint
ALTER TABLE "auth_user" ALTER COLUMN "id" SET DATA TYPE text;--> statement-breakpoint
ALTER TABLE "auth_user" ALTER COLUMN "id" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "auth_verification" ALTER COLUMN "id" SET DATA TYPE text;--> statement-breakpoint
ALTER TABLE "auth_verification" ALTER COLUMN "id" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "auth_account" ADD CONSTRAINT "auth_account_user_id_auth_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "auth_audit_event" ADD CONSTRAINT "auth_audit_event_user_id_auth_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "auth_audit_event" ADD CONSTRAINT "auth_audit_event_actor_user_id_auth_user_id_fk" FOREIGN KEY ("actor_user_id") REFERENCES "public"."auth_user"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "auth_membership" ADD CONSTRAINT "auth_membership_user_id_auth_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "auth_session" ADD CONSTRAINT "auth_session_user_id_auth_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user"("id") ON DELETE cascade ON UPDATE no action;
