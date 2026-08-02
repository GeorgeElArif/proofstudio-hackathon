import { randomUUID } from "node:crypto";
import { pathToFileURL } from "node:url";

import { hashPassword, verifyPassword } from "better-auth/crypto";
import pg from "pg";

import { requireCampaignId } from "../src/account/campaign-access.js";
import { evaluateEmailDomainPolicy } from "../src/auth/domain-policy.js";
import { classifyDatabaseUrlSafety } from "../src/db/url-safety.js";

export const JUDGE_ROLES = ["viewer", "reviewer"] as const;
export type JudgeRole = (typeof JUDGE_ROLES)[number];

export type JudgeProvisioningReceipt = {
  ok: true;
  operation: "judge_account_provisioned";
  account_id: string;
  email_normalized: string;
  campaign_id: string;
  run_id: string;
  role: JudgeRole;
  created_user: boolean;
  created_account: boolean;
  rotated_password: boolean;
  created_access: boolean;
  updated_access: boolean;
  revoked_conflicts: number;
  timestamp: string;
};

type ValidatedInput = {
  databaseUrl: string;
  email: string;
  campaignId: string;
  runId: string;
  role: JudgeRole;
  password: string;
};

export type ProvisioningSafety = {
  allowDisposableSmokeDatabase?: boolean;
  automatedSmoke?: boolean;
};

const PLACEHOLDER_MARKERS = [
  "change_me",
  "changeme",
  "replace-with",
  "placeholder",
  "example-password",
  "password123",
];

function validatePassword(value: string): string {
  if (value.length < 12) throw new Error("judge_password_below_accepted_minimum");
  const normalized = value.toLowerCase();
  if (PLACEHOLDER_MARKERS.some((marker) => normalized.includes(marker))) {
    throw new Error("judge_password_placeholder_refused");
  }
  if (!/[a-z]/.test(value) || !/[A-Z]/.test(value) || !/[0-9]/.test(value) || !/[^A-Za-z0-9]/.test(value)) {
    throw new Error("judge_password_weak");
  }
  if (/^(.)\1+$/.test(value)) throw new Error("judge_password_weak");
  return value;
}

function validateInput(env: NodeJS.ProcessEnv, safety: ProvisioningSafety): ValidatedInput {
  if (env.PROOFSTUDIO_JUDGE_PROVISIONING_APPROVED !== "true") {
    throw new Error("judge_provisioning_approval_required");
  }

  const databaseUrl = env.PROOFSTUDIO_DATABASE_URL?.trim() ?? "";
  if (!databaseUrl) throw new Error("judge_database_url_required");
  const databaseSafety = classifyDatabaseUrlSafety(databaseUrl);
  if (databaseSafety.classification === "missing" || databaseSafety.classification === "invalid") {
    throw new Error(`judge_database_url_refused_${databaseSafety.classification}`);
  }
  if (databaseUrl.toLowerCase().includes("placeholder") || databaseUrl.toLowerCase().includes("replace-with")) {
    throw new Error("judge_database_url_placeholder_refused");
  }
  if (databaseSafety.safeForSmoke && !safety.allowDisposableSmokeDatabase) {
    throw new Error("judge_disposable_database_requires_smoke_override");
  }
  if (safety.automatedSmoke && !databaseSafety.safeForSmoke) {
    throw new Error("judge_automated_smoke_production_database_refused");
  }

  const emailDecision = evaluateEmailDomainPolicy(env.PROOFSTUDIO_JUDGE_EMAIL ?? "");
  if (!emailDecision.allowed || !emailDecision.normalizedEmail) {
    throw new Error(`judge_email_refused_${emailDecision.reason}`);
  }
  const emailDomain = emailDecision.normalizedEmail.split("@")[1] ?? "";
  if (["example.com", "example.org", "example.net", "invalid"].includes(emailDomain)) {
    throw new Error("judge_email_placeholder_refused");
  }

  const campaignId = requireCampaignId(env.PROOFSTUDIO_JUDGE_CAMPAIGN_ID ?? "");
  if (PLACEHOLDER_MARKERS.some((marker) => campaignId.toLowerCase().includes(marker))) {
    throw new Error("judge_campaign_id_placeholder_refused");
  }

  const runId = env.PROOFSTUDIO_JUDGE_RUN_ID?.trim() ?? "";
  if (!runId) throw new Error("judge_run_id_required");
  if (!/^[A-Za-z0-9_.:-]{1,128}$/.test(runId) || runId !== runId.normalize("NFC")) {
    throw new Error("judge_run_id_invalid");
  }
  if (PLACEHOLDER_MARKERS.some((marker) => runId.toLowerCase().includes(marker))) {
    throw new Error("judge_run_id_placeholder_refused");
  }

  const requestedRole = (env.PROOFSTUDIO_JUDGE_ROLE?.trim().toLowerCase() || "viewer");
  if (!JUDGE_ROLES.includes(requestedRole as JudgeRole)) throw new Error("judge_role_refused");

  return {
    databaseUrl,
    email: emailDecision.normalizedEmail,
    campaignId,
    runId,
    role: requestedRole as JudgeRole,
    password: validatePassword(env.PROOFSTUDIO_JUDGE_PASSWORD ?? ""),
  };
}

export async function provisionJudgeAccount(
  env: NodeJS.ProcessEnv = process.env,
  safety: ProvisioningSafety = {},
): Promise<JudgeProvisioningReceipt> {
  // All validation, including the approval and DB safety gates, precedes client creation.
  const input = validateInput(env, safety);
  const credentialDigest = await hashPassword(input.password);
  const pool = new pg.Pool({ connectionString: input.databaseUrl, max: 1 });
  let client: pg.PoolClient | null = null;

  try {
    client = await pool.connect();
    await client.query("begin");
    const now = new Date();
    const existingUser = await client.query<{ id: string }>(
      "select id from auth_user where email_normalized = $1 for update",
      [input.email],
    );
    const createdUser = existingUser.rowCount === 0;
    const userId = existingUser.rows[0]?.id ?? randomUUID();
    if (createdUser) {
      await client.query(
        `insert into auth_user
          (id, name, email, email_normalized, email_verified, email_verified_at, created_at, updated_at)
         values ($1, 'ProofStudio Judge', $2, $2, true, $3, $3, $3)`,
        [userId, input.email, now],
      );
    } else {
      await client.query(
        `update auth_user
         set email = $2, email_verified = true,
             email_verified_at = coalesce(email_verified_at, $3), disabled_at = null, updated_at = $3
         where id = $1`,
        [userId, input.email, now],
      );
    }

    const existingAccount = await client.query<{ id: string; password: string | null }>(
      "select id, password from auth_account where provider_id = 'credential' and account_id = $1 for update",
      [userId],
    );
    const createdAccount = existingAccount.rowCount === 0;
    const rotatedPassword = !createdAccount &&
      !(existingAccount.rows[0]!.password &&
        await verifyPassword({ hash: existingAccount.rows[0]!.password!, password: input.password }));
    if (createdAccount) {
      await client.query(
        `insert into auth_account
          (id, user_id, provider_id, account_id, password, created_at, updated_at)
         values ($1, $2, 'credential', $2, $3, $4, $4)`,
        [randomUUID(), userId, credentialDigest, now],
      );
    } else if (rotatedPassword) {
      await client.query(
        "update auth_account set user_id = $2, password = $3, updated_at = $4 where id = $1",
        [existingAccount.rows[0]!.id, userId, credentialDigest, now],
      );
    }

    const existingAccess = await client.query<{
      access_role: JudgeRole;
      latest_run_id: string | null;
    }>(
      `select access_role, latest_run_id
       from account_campaign_access
       where account_id = $1 and campaign_id = $2 and revoked_at is null
       for update`,
      [userId, input.campaignId],
    );
    const createdAccess = existingAccess.rowCount === 0;
    const updatedAccess = !createdAccess && (
      existingAccess.rows[0]!.access_role !== input.role ||
      existingAccess.rows[0]!.latest_run_id !== input.runId
    );
    if (createdAccess) {
      await client.query(
        `insert into account_campaign_access
          (account_id, campaign_id, latest_run_id, access_role, linked_at, updated_at)
         values ($1, $2, $3, $4, $5, $5)`,
        [userId, input.campaignId, input.runId, input.role, now],
      );
    } else if (updatedAccess) {
      await client.query(
        `update account_campaign_access
         set access_role = $3, latest_run_id = $4, updated_at = $5
         where account_id = $1 and campaign_id = $2 and revoked_at is null`,
        [userId, input.campaignId, input.role, input.runId, now],
      );
    }

    await client.query("commit");
    return {
      ok: true,
      operation: "judge_account_provisioned",
      account_id: userId,
      email_normalized: input.email,
      campaign_id: input.campaignId,
      run_id: input.runId,
      role: input.role,
      created_user: createdUser,
      created_account: createdAccount,
      rotated_password: rotatedPassword,
      created_access: createdAccess,
      updated_access: updatedAccess,
      revoked_conflicts: 0,
      timestamp: now.toISOString(),
    };
  } catch (error) {
    await client?.query("rollback").catch(() => undefined);
    throw error;
  } finally {
    client?.release();
    await pool.end();
  }
}

async function main(): Promise<void> {
  const receipt = await provisionJudgeAccount(process.env);
  console.log(JSON.stringify(receipt));
}

const entrypoint = process.argv[1];
if (entrypoint && import.meta.url === pathToFileURL(entrypoint).href) {
  await main().catch((error: unknown) => {
    console.error(JSON.stringify({
      ok: false,
      operation: "judge_account_provisioning_refused",
      reason: error instanceof Error ? error.message : "unknown_error",
      timestamp: new Date().toISOString(),
    }));
    process.exitCode = 1;
  });
}
