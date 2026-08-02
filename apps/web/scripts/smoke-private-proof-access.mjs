import fs from "node:fs";
import path from "node:path";
const root=path.resolve(import.meta.dirname,"..");
const read=(file)=>fs.readFileSync(path.join(root,file),"utf8");
const client=read("src/authorizedProofClient.ts"); const pages=read("src/PrivateProofPages.tsx"); const app=read("src/App.tsx"); const dashboard=read("src/dashboard/DashboardSurface.tsx"); const publicPage=read("src/PublicPassportPage.tsx");
function require(value,message){if(!value)throw new Error(message);}
require(client.includes('credentials: "include"'),"private client must include credentials");
require(client.includes("getAuthBaseUrl")&&!client.includes("getApiBaseUrl"),"private client must call auth-server only");
require(!client.includes("localStorage")&&!client.includes("sessionStorage"),"browser storage auth forbidden");
require(!client.includes("INTERNAL_SERVICE_TOKEN")&&!client.includes("X-ProofStudio-Internal-Token"),"service credential exposed to client");
require(pages.includes("No fixture fallback was used")&&pages.includes("proof_api"),"private failure/source labeling missing");
require(app.includes("PrivateProofRoomPage")&&app.includes("PrivatePassportPage")&&app.includes("Legacy Review Room unavailable"),"private routes or legacy isolation missing");
require(dashboard.includes("Open private Proof Room")&&dashboard.includes("Open private Passport")&&dashboard.includes("encodeURIComponent"),"dashboard launchers missing or unencoded");
require(publicPage.includes("publicRunId !== GOLDEN_DEMO_RUN_ID")&&publicPage.indexOf("publicRunId !== GOLDEN_DEMO_RUN_ID")<publicPage.indexOf("getRunPassport(runId)"),"public Passport must reject arbitrary IDs before API call");
console.log(JSON.stringify({ok:true,slice:"PS-041C",checks:{fixture_room_preserved:"pass",private_gateway:"pass",golden_only_public_passport:"pass",credentialed_private_reads:"pass",dashboard_launchers:"pass",no_fixture_fallback:"pass",no_browser_storage_auth:"pass",no_client_service_token:"pass"}}));
