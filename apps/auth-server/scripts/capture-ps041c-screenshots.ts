import { randomBytes } from "node:crypto";
import { spawn, spawnSync, type ChildProcess } from "node:child_process";
import path from "node:path";
import pg from "pg";
import { getConfiguredAuthSmokeEnv, getSmokeDatabaseUrl } from "./ps040f-config.js";
import { assertSafeDatabaseUrlForSmoke } from "../src/db/url-safety.js";

const root = path.resolve(process.cwd(), "../..");
const databaseUrl = getSmokeDatabaseUrl();
assertSafeDatabaseUrlForSmoke(databaseUrl, { action: "PS-041C screenshots" });
const pool = new pg.Pool({ connectionString: databaseUrl });
const token = randomBytes(32).toString("base64url");
const stamp = Date.now(); const email = `ps041c-shot-${stamp}@proofstudio.test`; const password = randomBytes(24).toString("base64url");
const processes: ChildProcess[] = [];
async function wait(url: string) { for(let i=0;i<100;i++){try{if((await fetch(url)).status<500)return;}catch{}await new Promise(r=>setTimeout(r,200));}throw new Error(`local service unavailable: ${new URL(url).pathname}`); }
async function json(url: string, init: RequestInit={}) { const response=await fetch(url,init); return {response,body:await response.json() as Record<string,any>}; }
try {
  processes.push(spawn(path.join(root,".venv/bin/python"),["-m","uvicorn","proofstudio.api.app:app","--host","127.0.0.1","--port","8000","--log-level","warning"],{cwd:root,env:{...process.env,PYTHONPATH:"src",PROOFSTUDIO_INTERNAL_SERVICE_TOKEN:token,PROOFSTUDIO_LIVE_RUNS_ENABLED:"false",PROOFSTUDIO_B2_WRITES_ENABLED:"false"},stdio:"ignore"}));
  await wait("http://127.0.0.1:8000/health");
  const campaign=await json("http://127.0.0.1:8000/campaigns",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({name:"PS-041C private campaign",brief:"Disposable screenshot proof record"})});
  const campaignId=campaign.body.campaign_id as string;
  const run=await json("http://127.0.0.1:8000/runs",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({campaign_id:campaignId,prompt:"Disposable local proof",dry_run:true})});
  const runId=run.body.run_id as string;
  processes.push(spawn(process.execPath,["dist/src/server.js"],{cwd:process.cwd(),env:{...getConfiguredAuthSmokeEnv(8787),PROOFSTUDIO_PUBLIC_WEB_URL:"http://127.0.0.1:4173",PROOFSTUDIO_CORS_ORIGINS:"http://127.0.0.1:4173",PROOFSTUDIO_PROOF_API_BASE_URL:"http://127.0.0.1:8000",PROOFSTUDIO_INTERNAL_SERVICE_TOKEN:token},stdio:"ignore"}));
  await wait("http://127.0.0.1:8787/healthz");
  const headers={"content-type":"application/json",origin:"http://127.0.0.1:4173"};
  const signup=await json("http://127.0.0.1:8787/auth/sign-up/email",{method:"POST",headers,body:JSON.stringify({name:"PS041C Screenshot Account",email,password})});
  if(!signup.response.ok) throw new Error("real screenshot account signup failed");
  await pool.query("update auth_user set email_verified=true,email_verified_at=now() where email_normalized=lower($1)",[email]);
  const user=await pool.query<{id:string}>("select id from auth_user where email_normalized=lower($1)",[email]); if(!user.rows[0])throw new Error("real screenshot account missing after signup");
  await pool.query("insert into account_campaign_access(account_id,campaign_id,latest_run_id,access_role,revoked_at) values($1,$2,$3,'viewer',null)",[user.rows[0]!.id,campaignId,runId]);
  const login=await json("http://127.0.0.1:8787/auth/sign-in/email",{method:"POST",headers,body:JSON.stringify({email,password,rememberMe:true})});
  if(!login.response.ok) throw new Error("real screenshot session login failed");
  const cookie=login.response.headers.get("set-cookie")?.split(";")[0]??""; if(!cookie)throw new Error("real screenshot session cookie missing");
  processes.push(spawn("npm",["run","preview","--","--host","127.0.0.1","--port","4173"],{cwd:path.join(root,"apps/web"),stdio:"ignore"}));
  await wait("http://127.0.0.1:4173/dashboard");
  const capture=spawnSync("python",[path.join(root,"scripts/ps041c_capture_screenshots.py")],{cwd:root,env:{...process.env,PS041C_SCREENSHOT_COOKIE:cookie,PS041C_SCREENSHOT_CAMPAIGN_ID:campaignId,PS041C_SCREENSHOT_RUN_ID:runId,PS041C_SCREENSHOT_OUT:"/tmp/proofstudio-ps041c-proof-access-pack/screenshots"},encoding:"utf8"});
  if(capture.status!==0) throw new Error(capture.stderr||"screenshot capture failed");
  console.log(JSON.stringify({ok:true,slice:"PS-041C",screenshots:10,session:"real_better_auth",proofRecords:"disposable_fastapi"}));
} finally {
  await pool.query("delete from auth_user where email_normalized=lower($1)",[email]).catch(()=>undefined); await pool.end();
  for(const process of processes.reverse()){process.kill("SIGTERM");await new Promise<void>(resolve=>{const timer=setTimeout(resolve,3000);process.once("exit",()=>{clearTimeout(timer);resolve();});});}
}
