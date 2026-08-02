import { spawn, type ChildProcess } from "node:child_process";
import pg from "pg";
import { getConfiguredAuthSmokeEnv, getSmokeDatabaseUrl } from "./ps040f-config.js";
import { assertSafeDatabaseUrlForSmoke } from "../src/db/url-safety.js";

const databaseUrl = getSmokeDatabaseUrl();
assertSafeDatabaseUrlForSmoke(databaseUrl, { action: "PS-041B API smoke" });
const port = 8794; const base = `http://127.0.0.1:${port}`; const stamp = Date.now();
const emails = [`ps041b-a-${stamp}@proofstudio.test`, `ps041b-b-${stamp}@proofstudio.test`];
const password = "ps041b-local-test-password-12345";
const pool = new pg.Pool({ connectionString: databaseUrl });
let server: ChildProcess | null = null;
function assert(condition: unknown, message: string): asserts condition { if (!condition) throw new Error(message); }
async function json(path: string, init: RequestInit = {}) { const response = await fetch(base + path, init); return { response, body: await response.json() as Record<string, any> }; }
async function wait() { for (let i=0;i<60;i++) { try { if ((await fetch(base+"/healthz")).ok) return; } catch {} await new Promise(r=>setTimeout(r,250)); } throw new Error("server_start_timeout"); }
async function signup(email: string, name: string) {
  const result = await json("/auth/sign-up/email", { method:"POST", headers:{"content-type":"application/json",origin:"http://127.0.0.1:5173"}, body:JSON.stringify({name,email,password}) });
  assert(result.response.status < 500, "signup runtime failure");
  await pool.query("update auth_user set email_verified=true, email_verified_at=now() where email_normalized=lower($1)", [email]); // local-only simulation of verification-link consumption
  const login = await json("/auth/sign-in/email", { method:"POST", headers:{"content-type":"application/json",origin:"http://127.0.0.1:5173"}, body:JSON.stringify({email,password,rememberMe:true}) });
  assert(login.response.ok, "real Better Auth login failed after local verification simulation");
  const cookie = login.response.headers.get("set-cookie")?.split(";")[0] ?? ""; assert(cookie, "login did not issue session cookie");
  const user = await pool.query<{id:string}>("select id from auth_user where email_normalized=lower($1)",[email]); return { id:user.rows[0]!.id, cookie };
}
try {
  server=spawn(process.execPath,["dist/src/server.js"],{env:getConfiguredAuthSmokeEnv(port),stdio:"ignore"}); await wait();
  assert((await json("/account/campaigns")).response.status===401,"unauthenticated list must be 401");
  const a=await signup(emails[0]!,"PS041B A"), b=await signup(emails[1]!,"PS041B B");
  await pool.query(`insert into account_campaign_access(account_id,campaign_id,latest_run_id,access_role,revoked_at) values
    ($1,'ps041b-local-a-1','ps041b-run-a-1','owner',null),($1,'ps041b-local-a-2',null,'viewer',null),
    ($1,'ps041b-local-a-revoked',null,'reviewer',now()),($2,'ps041b-local-b-1',null,'owner',null)`,[a.id,b.id]);
  const listA=await json("/account/campaigns?limit=20",{headers:{cookie:a.cookie}}); assert(listA.response.status===200,"A list failed");
  assert(listA.body.items.length===2 && listA.body.items.every((x:any)=>x.campaignId.startsWith("ps041b-local-a-")),"A isolation/revocation failed");
  const listB=await json("/account/campaigns?accountId="+encodeURIComponent(a.id),{headers:{cookie:b.cookie}}); assert(listB.response.status===400,"identity spoof must be rejected");
  assert((await json("/account/campaigns?cursor=bad",{headers:{cookie:a.cookie}})).response.status===400,"malformed cursor must be 400");
  const session=await json("/session",{headers:{cookie:a.cookie}}); assert(session.body.authenticated===true,"cookie must represent a real Better Auth session");
  console.log(JSON.stringify({ok:true,slice:"PS-041B",checks:{real_session:"pass",unauthenticated_401:"pass",isolation:"pass",revoked_excluded:"pass",spoof_rejected:"pass",malformed_cursor:"pass"}}));
} finally {
  await pool.query("delete from auth_user where email_normalized=any($1)",[emails]).catch(()=>undefined); await pool.end();
  if(server){server.kill("SIGTERM");await new Promise(r=>server?.once("exit",r));}
}
