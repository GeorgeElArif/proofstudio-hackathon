import { createServer, type Server } from "node:http";
import { spawn, type ChildProcess } from "node:child_process";
import { randomBytes } from "node:crypto";
import pg from "pg";
import { getConfiguredAuthSmokeEnv, getSmokeDatabaseUrl } from "./ps040f-config.js";
import { assertSafeDatabaseUrlForSmoke } from "../src/db/url-safety.js";

const databaseUrl=getSmokeDatabaseUrl(); assertSafeDatabaseUrlForSmoke(databaseUrl,{action:"PS-041D imported lineage smoke"});
const authPort=8805, proofPort=8806, redirectPort=8808, base=`http://127.0.0.1:${authPort}`;
const readToken=randomBytes(32).toString("base64url"), operatorSentinel=randomBytes(32).toString("base64url");
const pool=new pg.Pool({connectionString:databaseUrl}); const stamp=Date.now();
const emails=[`ps041d-a-${stamp}@proofstudio.test`,`ps041d-b-${stamp}@proofstudio.test`]; const password=randomBytes(24).toString("base64url");
let auth:ChildProcess|null=null, proof:Server|null=null, redirect:Server|null=null, calls=0, redirectCalls=0, operatorHeaderSeen=false;
type RateRow={id:string;key:string;count:number;last_request:string}; let rateBaseline:RateRow[]=[];
function assert(value:unknown,message:string):asserts value{if(!value)throw new Error(message);}
async function json(path:string,init:RequestInit={}){const response=await fetch(base+path,init);let body:any={};try{body=await response.json();}catch{}return{response,body};}
async function wait(){for(let i=0;i<80;i++){try{if((await fetch(base+"/healthz")).ok)return;}catch{}await new Promise(r=>setTimeout(r,100));}throw new Error("server_start_timeout");}
async function stop(child:ChildProcess|null){if(!child||child.exitCode!==null||child.signalCode!==null)return;await new Promise<void>((resolve,reject)=>{child.once("error",reject);child.once("exit",()=>resolve());if(!child.kill("SIGTERM"))reject(new Error("termination_failed"));});}
async function close(server:Server|null){if(server)await new Promise<void>((resolve,reject)=>server.close(error=>error?reject(error):resolve()));}
async function signup(email:string){const headers={"content-type":"application/json",origin:"http://127.0.0.1:5173"};await json("/auth/sign-up/email",{method:"POST",headers,body:JSON.stringify({name:"PS041D",email,password})});await pool.query("update auth_user set email_verified=true,email_verified_at=now() where email_normalized=lower($1)",[email]);const login=await json("/auth/sign-in/email",{method:"POST",headers,body:JSON.stringify({email,password,rememberMe:true})});assert(login.response.ok,"real login failed");const cookie=login.response.headers.get("set-cookie")?.split(";")[0]??"";assert(cookie,"session cookie missing");const user=await pool.query<{id:string}>("select id from auth_user where email_normalized=lower($1)",[email]);return{id:user.rows[0]!.id,cookie};}
function bundle(campaign:string){return{bundle_id:"bundle-ok",campaign_id:campaign,bundle_fingerprint:"a".repeat(64),fingerprint_schema:"ps041d.fingerprint.v1",source_type:"genblaze_multi_provider_sample",source_slug:"genblaze-gen-media-multi-provider-sample",source_revision:"2e31577b7a9d5a7b0309d814f2d0282088b33fe8",state:"complete",node_ids:[] as string[],edge_ids:[] as string[]};}
function node(campaign:string){return{node_id:"node_ok",campaign_id:campaign,bundle_id:"bundle-ok",kind:"asset",source_id:"asset-ok",source_role:"generated_asset",content_fingerprint:"b".repeat(64),evidence_class:"recorded",checks:[{outcome:"hash_present",subject:"asset-ok",detail:null}],limitations:[],run:null,b2_reference:null,metadata:{media_type:"image/png",sha256:"c".repeat(64),size_bytes:1}};}
function edge(campaign:string){return{edge_id:"edge_ok",campaign_id:campaign,bundle_id:"bundle-ok",kind:"external_input",source_node_id:"node_ok",target_node_id:null,missing_source_id:"missing-upstream",evidence_class:"recorded",hash_covered:false,check_outcome:"relationship_recorded",source_locator:"manifest.input",limitations:[]};}
function detail(campaign:string){const b=bundle(campaign),n=node(campaign);b.node_ids=[n.node_id];return{source:"proof_api",campaign_access_scope:campaign,lineage:{created:false,bundle:b,nodes:[n],edges:[]}};}
function passport(campaign:string){const n=node(campaign);return{source:"proof_api",campaign_access_scope:campaign,passport:{schema:"proofstudio.portable_lineage_passport.v1",campaign_id:campaign,bundle_id:"bundle-ok",bundle_fingerprint:"a".repeat(64),source_type:"genblaze_multi_provider_sample",source_slug:"genblaze-gen-media-multi-provider-sample",source_revision:"2e31577b7a9d5a7b0309d814f2d0282088b33fe8",state:"complete",nodes:[n],edges:[],limitations:[],truth_boundary:"ProofStudio reports what the imported pipeline record states; proof does not equal truth."}};}
function upstream(path:string){
  const campaign=path.split("/")[3]??"";
  if(path.includes("missing-bundle"))return{status:404,body:{ok:false}};
  if(campaign==="malformed")return{status:200,body:{unexpected:true}};
  if(campaign==="oversized")return{status:200,body:{source:"proof_api",campaign_access_scope:campaign,bundles:[{padding:"x".repeat(1_600_000)}]}};
  if(path.endsWith("/passport")){
    const body:any=passport(campaign);
    if(campaign==="passport-extra")body.passport.nodes[0].metadata.extra={nested:true};
    return{status:200,body};
  }
  if(/\/import-bundles\/[^/]+$/.test(path)){
    const body:any=detail(campaign),n=body.lineage.nodes[0];
    if(campaign==="node-extra-url")n.url="https://example.invalid/not-returned";
    if(campaign==="nested-signed-url")n.b2_reference={backend:"b2_s3",bucket_alias:"configured",object_key:"import-root/a?X-Amz-Signature=not-a-secret",version_id:null,size_bytes:1,content_type:"application/json",etag:null,sha256:null,uploaded_at:null,source_prefix:"import-root",manifest_hash:null};
    if(campaign==="raw-prompt")n.prompt="not-returned";
    if(campaign==="bad-node-kind")n.kind="provider_payload";
    if(campaign==="bad-edge-evidence"){const e=edge(campaign);e.evidence_class="unknown" as any;body.lineage.edges=[e];body.lineage.bundle.edge_ids=[e.edge_id];}
    if(campaign==="bad-hash")n.content_fingerprint="ABC";
    if(campaign==="wrong-node-campaign")n.campaign_id="other-campaign";
    if(campaign==="wrong-node-bundle")n.bundle_id="other-bundle";
    if(campaign==="non-object-node")body.lineage.nodes.push("not-an-object");
    if(campaign==="non-object-edge")body.lineage.edges.push(7);
    if(campaign==="missing-required-field")delete body.lineage.bundle.state;
    return{status:200,body};
  }
  return{status:200,body:{source:"proof_api",campaign_access_scope:campaign,bundles:[bundle(campaign)]}};
}
let failure:unknown=null;
try{
  rateBaseline=(await pool.query<RateRow>("select id,key,count,last_request::text as last_request from auth_rate_limit order by id,key")).rows;await pool.query("delete from auth_rate_limit");
  redirect=createServer((_q,r)=>{redirectCalls++;r.writeHead(200,{"content-type":"application/json"});r.end("{}");}).listen(redirectPort,"127.0.0.1");
  proof=createServer((request,response)=>{calls++;operatorHeaderSeen ||= request.headers["x-proofstudio-import-token"]!==undefined || Object.values(request.headers).includes(operatorSentinel);const path=request.url??"";if(request.headers["x-proofstudio-internal-token"]!==readToken){response.writeHead(401);response.end("{}");return;}if(path.includes("redirect-302")||path.includes("redirect-307")){response.writeHead(path.includes("302")?302:307,{location:`http://127.0.0.1:${redirectPort}/target`});response.end();return;}if(path.includes("timeout")){setTimeout(()=>{response.writeHead(200,{"content-type":"application/json"});response.end("{}");},6000);return;}if(path.includes("nonjson")){response.writeHead(200,{"content-type":"text/plain"});response.end("no");return;}const result=upstream(path);response.writeHead(result.status,{"content-type":"application/json"});response.end(JSON.stringify(result.body));}).listen(proofPort,"127.0.0.1");
  auth=spawn(process.execPath,["dist/src/server.js"],{env:{...getConfiguredAuthSmokeEnv(authPort),PROOFSTUDIO_PROOF_API_BASE_URL:`http://127.0.0.1:${proofPort}`,PROOFSTUDIO_INTERNAL_SERVICE_TOKEN:readToken},stdio:"ignore"});await wait();
  assert((await json("/account/campaigns/owner/lineage")).response.status===401,"no session");const a=await signup(emails[0]!),b=await signup(emails[1]!);
  await pool.query(`insert into account_campaign_access(account_id,campaign_id,access_role,revoked_at) values
    ($1,'owner','owner',null),($1,'reviewer','reviewer',null),($1,'viewer','viewer',null),($1,'revoked','viewer',now()),
    ($1,'malformed','viewer',null),($1,'oversized','viewer',null),($1,'nonjson','viewer',null),($1,'timeout','viewer',null),
    ($1,'node-extra-url','viewer',null),($1,'nested-signed-url','viewer',null),($1,'raw-prompt','viewer',null),
    ($1,'bad-node-kind','viewer',null),($1,'bad-edge-evidence','viewer',null),($1,'bad-hash','viewer',null),
    ($1,'wrong-node-campaign','viewer',null),($1,'wrong-node-bundle','viewer',null),($1,'non-object-node','viewer',null),
    ($1,'non-object-edge','viewer',null),($1,'passport-extra','viewer',null),($1,'missing-required-field','viewer',null),
    ($1,'redirect-302','viewer',null),($1,'redirect-307','viewer',null),($1,'connection','viewer',null),($2,'foreign','owner',null)`,[a.id,b.id]);
  for(const campaign of ["owner","reviewer","viewer"]){for(const suffix of ["", "/bundle-ok", "/bundle-ok/passport"]){assert((await json(`/account/campaigns/${campaign}/lineage${suffix}`,{headers:{cookie:a.cookie}})).response.status===200,`${campaign}${suffix}`);}}
  assert((await json("/account/campaigns/foreign/lineage",{headers:{cookie:a.cookie}})).response.status===404,"cross account");assert((await json("/account/campaigns/revoked/lineage",{headers:{cookie:a.cookie}})).response.status===404,"revoked");assert((await json("/account/campaigns/absent/lineage",{headers:{cookie:a.cookie}})).response.status===404,"absent");
  const before=calls;assert((await json("/account/campaigns/absent/lineage",{headers:{cookie:a.cookie}})).response.status===404&&calls===before,"authorization before proof");
  assert((await json("/account/campaigns/owner/lineage?accountId=spoof",{headers:{cookie:a.cookie}})).response.status===400,"spoof");assert((await json("/account/campaigns/bad%20id/lineage",{headers:{cookie:a.cookie}})).response.status===400,"campaign id");assert((await json("/account/campaigns/owner/lineage/bad%20id",{headers:{cookie:a.cookie}})).response.status===400,"bundle id");assert((await json("/account/campaigns/owner/lineage/missing-bundle",{headers:{cookie:a.cookie}})).response.status===404,"missing bundle");
  for(const campaign of ["malformed","oversized","nonjson","timeout","redirect-302","redirect-307"]){assert((await json(`/account/campaigns/${campaign}/lineage`,{headers:{cookie:a.cookie,authorization:"Bearer browser-only"}})).response.status===503,campaign);}
  await pool.query("delete from auth_rate_limit");
  const malformedDetails=["node-extra-url","nested-signed-url","raw-prompt","bad-node-kind","bad-edge-evidence","bad-hash","wrong-node-campaign","wrong-node-bundle","non-object-node","non-object-edge","missing-required-field"];
  for(const campaign of malformedDetails){const result=await json(`/account/campaigns/${campaign}/lineage/bundle-ok`,{headers:{cookie:a.cookie}});const serialized=JSON.stringify(result.body);assert(result.response.status===503&&result.body.code==="proof_service_unavailable",`${campaign}:${result.response.status}:${String(result.body.code)}`);assert(!serialized.includes("example.invalid")&&!serialized.includes("not-returned")&&!serialized.includes("X-Amz-Signature")&&!serialized.includes("other-campaign")&&!serialized.includes("other-bundle"),`${campaign} leaked nested payload`);}
  {const result=await json("/account/campaigns/passport-extra/lineage/bundle-ok/passport",{headers:{cookie:a.cookie}});assert(result.response.status===503&&result.body.code==="proof_service_unavailable","passport extra nested field");assert(!JSON.stringify(result.body).includes("nested"),"passport nested payload leaked");}
  assert(redirectCalls===0,"redirect followed");assert(!operatorHeaderSeen,"operator token entered proof gateway");await close(proof);proof=null;assert((await json("/account/campaigns/connection/lineage",{headers:{cookie:a.cookie}})).response.status===503,"connection failure");
  const columns=await pool.query("select column_name from information_schema.columns where table_name='account_campaign_access'");assert(!columns.rows.some(row=>/prompt|manifest|asset|passport|proof_body|lineage/.test(row.column_name)),"proof field in Auth Postgres");
}catch(error){failure=error;}finally{
  const cleanup:unknown[]=[];try{await stop(auth);}catch(e){cleanup.push(e);}try{await close(proof);}catch(e){cleanup.push(e);}try{await close(redirect);}catch(e){cleanup.push(e);}
  try{await pool.query("delete from auth_user where email_normalized=any($1)",[emails]);await pool.query("delete from auth_rate_limit");for(const row of rateBaseline)await pool.query("insert into auth_rate_limit(id,key,count,last_request) values($1,$2,$3,$4)",[row.id,row.key,row.count,row.last_request]);}catch(e){cleanup.push(e);}try{await pool.end();}catch(e){cleanup.push(e);}if(!failure&&cleanup.length)failure=cleanup[0];
}
if(failure)throw failure;
console.log(JSON.stringify({ok:true,slice:"PS-041D",checks:{real_sessions:"pass",roles:"owner_reviewer_viewer",cross_account:"404",revoked:"404",spoof:"400",authorization_precedes_proof:"pass",upstream_failures:"503",redirects:"contained",operator_token:"absent",auth_postgres_proof_data:"absent",rate_limit:"restored"}}));
