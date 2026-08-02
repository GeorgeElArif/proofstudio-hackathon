import { createServer, type Server } from "node:http";
import { spawn, type ChildProcess } from "node:child_process";
import pg from "pg";
import { randomBytes } from "node:crypto";
import { getConfiguredAuthSmokeEnv, getSmokeDatabaseUrl } from "./ps040f-config.js";
import { assertSafeDatabaseUrlForSmoke } from "../src/db/url-safety.js";

const databaseUrl = getSmokeDatabaseUrl();
assertSafeDatabaseUrlForSmoke(databaseUrl, { action: "PS-041C proof access smoke" });
const authPort = 8795; const proofPort = 8796; const redirectTargetPort = 8798; const base = `http://127.0.0.1:${authPort}`;
const token = randomBytes(32).toString("base64url");
const pool = new pg.Pool({ connectionString: databaseUrl });
const stamp = Date.now(); const emails = [`ps041c-a-${stamp}@proofstudio.test`, `ps041c-b-${stamp}@proofstudio.test`];
const password = randomBytes(24).toString("base64url");
let authServer: ChildProcess | null = null; let unavailableAuthServer: ChildProcess | null = null; let proofServer: Server | null = null; let redirectTargetServer: Server | null = null; let proofCalls = 0;
let redirectTargetCalls = 0; let redirectTargetReceivedToken = false; let redirectTargetReceivedCookie = false; let redirectTargetReceivedAuthorization = false;
type RateLimitRow = { id: string; key: string; count: number; last_request: string };
let rateLimitBaseline: RateLimitRow[] | null = null;
let functionalError: unknown = null;
let functionalChecksPassed = false;
function assert(value: unknown, message: string): asserts value { if (!value) throw new Error(message); }
async function json(path: string, init: RequestInit = {}) { const response = await fetch(base + path, init); return { response, body: await response.json() as Record<string, any> }; }
async function wait() { for (let i=0;i<60;i++) { try { if ((await fetch(base+"/healthz")).ok) return; } catch {} await new Promise(r=>setTimeout(r,250)); } throw new Error("server_start_timeout"); }
async function readRateLimitRows(client: pg.Pool | pg.PoolClient): Promise<RateLimitRow[]> {
  const result=await client.query<RateLimitRow>("select id, key, count, last_request::text as last_request from auth_rate_limit order by id, key");
  return result.rows;
}
function rateLimitRowsEqual(left: RateLimitRow[], right: RateLimitRow[]): boolean { return JSON.stringify(left)===JSON.stringify(right); }
async function captureRateLimitBaseline(): Promise<RateLimitRow[]> {
  const client=await pool.connect();
  try {
    await client.query("begin");
    try {
      await client.query("lock table auth_rate_limit in exclusive mode");
      const baseline=await readRateLimitRows(client);
      await client.query("delete from auth_rate_limit");
      await client.query("commit");
      return baseline;
    } catch(error) {
      try { await client.query("rollback"); } catch(rollbackError) { throw new AggregateError([error,rollbackError],"rate_limit_capture_and_rollback_failed"); }
      throw error;
    }
  } finally { client.release(); }
}
async function stopChild(child: ChildProcess | null): Promise<void> {
  if(!child || child.exitCode!==null || child.signalCode!==null) return;
  await new Promise<void>((resolve,reject)=>{ child.once("error",reject); child.once("exit",()=>resolve()); if(!child.kill("SIGTERM")) reject(new Error("child_termination_failed")); });
}
async function closeListener(server: Server | null): Promise<void> {
  if(!server) return;
  await new Promise<void>((resolve,reject)=>server.close((error)=>error?reject(error):resolve()));
}
async function restoreRateLimitBaseline(baseline: RateLimitRow[]): Promise<void> {
  const client=await pool.connect();
  try {
    await client.query("begin");
    try {
      await client.query("delete from auth_rate_limit");
      for(const row of baseline) await client.query("insert into auth_rate_limit (id, key, count, last_request) values ($1, $2, $3, $4)",[row.id,row.key,row.count,row.last_request]);
      await client.query("commit");
    } catch(error) {
      try { await client.query("rollback"); } catch(rollbackError) { throw new AggregateError([error,rollbackError],"rate_limit_restore_and_rollback_failed"); }
      throw error;
    }
    const restored=await readRateLimitRows(client);
    assert(rateLimitRowsEqual(restored,baseline),"rate_limit_baseline_mismatch");
  } finally { client.release(); }
}
async function signup(email: string, name: string) {
  const headers = {"content-type":"application/json",origin:"http://127.0.0.1:5173"};
  await json("/auth/sign-up/email", {method:"POST",headers,body:JSON.stringify({name,email,password})});
  await pool.query("update auth_user set email_verified=true,email_verified_at=now() where email_normalized=lower($1)",[email]);
  const login=await json("/auth/sign-in/email",{method:"POST",headers,body:JSON.stringify({email,password,rememberMe:true})});
  assert(login.response.ok,"real Better Auth login failed"); const cookie=login.response.headers.get("set-cookie")?.split(";")[0]??""; assert(cookie,"missing real session cookie");
  const user=await pool.query<{id:string}>("select id from auth_user where email_normalized=lower($1)",[email]); return {id:user.rows[0]!.id,cookie};
}
function proofPayload(path: string) {
  const campaign = path.split("/")[3] ?? "";
  if (path.includes("foreign-run") || path.includes("missing")) return { status: 404, body: { ok:false,code:"proof_not_found",message:"Proof was not found." } };
  if (path.includes("malformed-upstream")) return { status: 200, body: { unexpected:true } };
  if (path.includes("internal-auth-upstream")) return { status: 401, body: { detail:"not forwarded" } };
  if (path.includes("upstream-500")) return { status: 500, body: { detail:"not forwarded" } };
  if (path.includes("oversized-upstream")) return { status: 200, body: { source:"proof_api",campaign:{padding:"x".repeat(1_600_000)},selected_run:null,attempts:[],assets:[],manifest:null,passport_ref:null,export_refs:[] } };
  if (path.includes("/passport")) return { status:200, body:{source:"proof_api",campaign_access_scope:campaign,passport:{passport_identity:{run_id:"recorded"}}} };
  return { status:200, body:{source:"proof_api",campaign:{campaign_id:campaign},selected_run:null,attempts:[],assets:[],manifest:null,passport_ref:null,export_refs:[]} };
}
try {
  rateLimitBaseline=await captureRateLimitBaseline();
  redirectTargetServer=createServer((request,response)=>{ redirectTargetCalls++; redirectTargetReceivedToken ||= request.headers["x-proofstudio-internal-token"] !== undefined; redirectTargetReceivedCookie ||= request.headers.cookie !== undefined; redirectTargetReceivedAuthorization ||= request.headers.authorization !== undefined; response.writeHead(200,{"content-type":"application/json"});response.end(JSON.stringify({unsafe_upstream_detail:"must-not-be-forwarded"})); }).listen(redirectTargetPort,"127.0.0.1");
  proofServer=createServer((request,response)=>{ proofCalls++; if(request.headers["x-proofstudio-internal-token"]!==token){response.writeHead(401,{"content-type":"application/json"});response.end("{}");return;} const url=request.url??""; if(url.includes("redirect-302")||url.includes("redirect-307")){const status=url.includes("redirect-302")?302:307;response.writeHead(status,{"content-type":"text/plain",location:`http://127.0.0.1:${redirectTargetPort}/redirect-target`});response.end("unsafe redirect upstream body");return;} if(url.includes("timeout-upstream")){setTimeout(()=>{response.writeHead(200,{"content-type":"application/json"});response.end("{}");},6_000);return;} if(url.includes("nonjson-upstream")){response.writeHead(200,{"content-type":"text/plain"});response.end("not-json");return;} const result=proofPayload(url); response.writeHead(result.status,{"content-type":"application/json"});response.end(JSON.stringify(result.body)); }).listen(proofPort,"127.0.0.1");
  authServer=spawn(process.execPath,["dist/src/server.js"],{env:{...getConfiguredAuthSmokeEnv(authPort),PROOFSTUDIO_PROOF_API_BASE_URL:`http://127.0.0.1:${proofPort}`,PROOFSTUDIO_INTERNAL_SERVICE_TOKEN:token},stdio:"ignore"}); await wait();
  assert((await json("/account/campaigns/owner-campaign/proof-room")).response.status===401,"no session must be 401");
  const a=await signup(emails[0]!,"PS041C A"), b=await signup(emails[1]!,"PS041C B");
  await pool.query(`insert into account_campaign_access(account_id,campaign_id,latest_run_id,access_role,revoked_at) values
    ($1,'owner-campaign','owner-run','owner',null),($1,'reviewer-campaign','reviewer-run','reviewer',null),($1,'viewer-campaign','viewer-run','viewer',null),
    ($1,'revoked-campaign',null,'viewer',now()),($1,'malformed-upstream',null,'viewer',null),($1,'internal-auth-upstream',null,'viewer',null),
    ($1,'timeout-upstream',null,'viewer',null),($1,'nonjson-upstream',null,'viewer',null),($1,'oversized-upstream',null,'viewer',null),
    ($1,'redirect-302',null,'viewer',null),($1,'redirect-307',null,'viewer',null),
    ($1,'upstream-500',null,'viewer',null),($1,'connection-upstream',null,'viewer',null),($2,'foreign-campaign','foreign-run','owner',null)`,[a.id,b.id]);
  for(const [campaign,run] of [["owner-campaign","owner-run"],["reviewer-campaign","reviewer-run"],["viewer-campaign","viewer-run"]]){
    assert((await json(`/account/campaigns/${campaign}/proof-room?runId=${run}`,{headers:{cookie:a.cookie}})).response.status===200,`${campaign} room denied`);
    assert((await json(`/account/campaigns/${campaign}/passport/${run}`,{headers:{cookie:a.cookie}})).response.status===200,`${campaign} passport denied`);
  }
  assert((await json("/account/campaigns/foreign-campaign/proof-room",{headers:{cookie:a.cookie}})).response.status===404,"cross-account read did not converge on 404");
  assert((await json("/account/campaigns/revoked-campaign/proof-room",{headers:{cookie:a.cookie}})).response.status===404,"revoked read did not converge on 404");
  assert((await json("/account/campaigns/absent-campaign/proof-room",{headers:{cookie:a.cookie}})).response.status===404,"absent mapping did not converge on 404");
  assert((await json("/account/campaigns/owner-campaign/proof-room?accountId=spoof",{headers:{cookie:a.cookie}})).response.status===400,"identity spoof accepted");
  assert((await json("/account/campaigns/bad%20id/proof-room",{headers:{cookie:a.cookie}})).response.status===400,"invalid ID accepted");
  assert((await json("/account/campaigns/owner-campaign/passport/foreign-run",{headers:{cookie:a.cookie}})).response.status===404,"foreign run leaked");
  assert((await json("/account/campaigns/malformed-upstream/proof-room",{headers:{cookie:a.cookie}})).response.status===503,"malformed proof response did not fail closed");
  assert((await json("/account/campaigns/internal-auth-upstream/proof-room",{headers:{cookie:a.cookie}})).response.status===503,"internal auth failure did not fail closed");
  assert((await json("/account/campaigns/timeout-upstream/proof-room",{headers:{cookie:a.cookie}})).response.status===503,"proof timeout did not fail closed");
  assert((await json("/account/campaigns/nonjson-upstream/proof-room",{headers:{cookie:a.cookie}})).response.status===503,"non-JSON proof response did not fail closed");
  assert((await json("/account/campaigns/oversized-upstream/proof-room",{headers:{cookie:a.cookie}})).response.status===503,"oversized proof response did not fail closed");
  assert((await json("/account/campaigns/upstream-500/proof-room",{headers:{cookie:a.cookie}})).response.status===503,"proof 500 did not fail closed");
  for (const status of [302,307]) {
    const result=await json(`/account/campaigns/redirect-${status}/proof-room`,{headers:{cookie:a.cookie,authorization:"Bearer browser-credential-must-not-forward"}});
    const serialized=JSON.stringify(result.body);
    assert(result.response.status===503&&result.body.code==="proof_service_unavailable",`${status} redirect did not return safe proof_service_unavailable`);
    assert(!serialized.includes(`127.0.0.1:${redirectTargetPort}`)&&!serialized.includes("redirect-target")&&!serialized.includes("unsafe redirect upstream body")&&!serialized.includes("must-not-be-forwarded"),`${status} redirect exposed Location or upstream detail`);
    assert(redirectTargetCalls===0,`${status} redirect target was contacted`);
  }
  assert(!redirectTargetReceivedToken&&!redirectTargetReceivedCookie&&!redirectTargetReceivedAuthorization,"redirect target received a protected header");
  const before=proofCalls; assert((await json("/account/campaigns/absent-campaign/proof-room",{headers:{cookie:a.cookie}})).response.status===404 && proofCalls===before,"proof service called before authorization");
  const unavailablePort=8797; const unavailableDatabaseUrl=new URL(databaseUrl); unavailableDatabaseUrl.port="59999"; unavailableAuthServer=spawn(process.execPath,["dist/src/server.js"],{env:{...getConfiguredAuthSmokeEnv(unavailablePort),PROOFSTUDIO_DATABASE_URL:unavailableDatabaseUrl.toString(),PROOFSTUDIO_PROOF_API_BASE_URL:`http://127.0.0.1:${proofPort}`,PROOFSTUDIO_INTERNAL_SERVICE_TOKEN:token},stdio:"ignore"});
  try { for(let i=0;i<60;i++){try{if((await fetch(`http://127.0.0.1:${unavailablePort}/healthz`)).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));} const prior=proofCalls; const unavailable=await fetch(`http://127.0.0.1:${unavailablePort}/account/campaigns/owner-campaign/proof-room`,{headers:{cookie:a.cookie}}); assert(unavailable.status===503&&proofCalls===prior,"auth DB unavailable must be 503 without proof call"); } finally { await stopChild(unavailableAuthServer); unavailableAuthServer=null; }
  await new Promise<void>((resolve)=>proofServer!.close(()=>resolve())); proofServer=null;
  assert((await json("/account/campaigns/connection-upstream/proof-room",{headers:{cookie:a.cookie}})).response.status===503,"proof connection failure did not fail closed");
  const schema=await pool.query("select column_name from information_schema.columns where table_name='account_campaign_access'");
  assert(!schema.rows.some((row)=>/prompt|manifest|asset|attempt|passport|proof_body/.test(row.column_name)),"proof content column exists in auth mapping table");
  functionalChecksPassed=true;
} catch(error) {
  functionalError=error;
} finally {
  const cleanupErrors: unknown[]=[];
  try { await stopChild(authServer); } catch(error) { cleanupErrors.push(error); } finally { authServer=null; }
  try { await stopChild(unavailableAuthServer); } catch(error) { cleanupErrors.push(error); } finally { unavailableAuthServer=null; }
  try { await closeListener(proofServer); } catch(error) { cleanupErrors.push(error); } finally { proofServer=null; }
  try { await closeListener(redirectTargetServer); } catch(error) { cleanupErrors.push(error); } finally { redirectTargetServer=null; }
  if(rateLimitBaseline) {
    try { await restoreRateLimitBaseline(rateLimitBaseline); console.log(JSON.stringify({rate_limit_baseline_restored:"pass"})); } catch(error) { cleanupErrors.push(error); }
  }
  try { await pool.query("delete from auth_user where email_normalized=any($1)",[emails]); } catch(error) { cleanupErrors.push(error); }
  try { await pool.end(); } catch(error) { cleanupErrors.push(error); }
  if(cleanupErrors.length>0) {
    console.error(JSON.stringify({ok:false,cleanup:"failed"}));
    if(functionalError===null) functionalError=cleanupErrors[0];
  }
}
if(functionalError!==null) throw functionalError;
assert(functionalChecksPassed,"functional_checks_incomplete");
console.log(JSON.stringify({ok:true,slice:"PS-041C",checks:{real_sessions:"pass",roles:"pass",cross_account:"404",revoked:"404",spoof:"400",cross_run:"404",auth_db_unavailable:"503_no_proof_call",proof_timeout:"503",proof_non_json:"503",proof_malformed:"503",proof_oversized:"503",proof_internal_auth:"503",proof_500:"503",proof_connection:"503",redirect_302:"503_target_not_contacted",redirect_307:"503_target_not_contacted",redirect_target_requests:redirectTargetCalls,redirect_protected_headers:"not_received",redirect_details:"not_exposed",authorization_precedes_proof:"pass",no_proof_duplication:"pass",rate_limit_cleanup:"baseline_restored"}}));
