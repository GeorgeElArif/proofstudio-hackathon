import { useEffect, useState } from "react";
import { getAuthorizedPassport, getAuthorizedProofRoom, type AuthorizedProofState } from "./authorizedProofClient";

function StatePanel({ state, label }: { state: AuthorizedProofState; label: string }) {
  if (state.state === "unauthenticated") return <section className="card"><h2>Sign in required</h2><p>A current account session is required to open this private {label}.</p><a className="button" href="/login">Sign in</a></section>;
  if (state.state === "not_found") return <section className="card"><h2>Proof not found</h2><p>No accessible proof was found. Campaign and run existence are not disclosed.</p></section>;
  if (state.state === "unavailable") return <section className="card"><h2>Proof service unavailable</h2><p>The authorization or proof dependency is temporarily unavailable. No fixture fallback was used.</p></section>;
  if (state.state !== "available") return <section className="card"><h2>Proof response rejected</h2><p>The response did not match the private proof contract.</p></section>;
  return <section className="card"><p className="eyebrow">Private account-linked {label}</p><h2>Recorded proof data</h2><dl className="kv"><dt>proof source</dt><dd className="mono">proof_api</dd><dt>campaign access role</dt><dd>{state.campaignAccessRole} — application role only</dd></dl><details className="json" open><summary>Returned proof record</summary><pre>{JSON.stringify(state.payload, null, 2)}</pre></details><p className="muted">This record describes what the pipeline recorded. It does not prove legal authenticity, semantic truth, or human authorship.</p></section>;
}

export function PrivateProofRoomPage({ campaignId, runId }: { campaignId: string; runId?: string }) {
  const [state, setState] = useState<AuthorizedProofState | null>(null);
  useEffect(() => { let active = true; void getAuthorizedProofRoom(campaignId, runId).then((next) => { if (active) setState(next); }); return () => { active = false; }; }, [campaignId, runId]);
  return <main className="public-passport-page"><section className="passport-hero"><p className="eyebrow">ProofStudio Private Proof Room</p><h1>Account-authorized campaign proof</h1><p>Authorization uses the current session and active campaign access mapping; FastAPI validates recorded run membership.</p><a className="button secondary" href="/dashboard">Back to dashboard</a></section>{state ? <StatePanel state={state} label="Proof Room" /> : <section className="card"><h2>Authorizing proof read…</h2></section>}</main>;
}

export function PrivatePassportPage({ campaignId, runId }: { campaignId: string; runId: string }) {
  const [state, setState] = useState<AuthorizedProofState | null>(null);
  useEffect(() => { let active = true; void getAuthorizedPassport(campaignId, runId).then((next) => { if (active) setState(next); }); return () => { active = false; }; }, [campaignId, runId]);
  return <main className="public-passport-page"><section className="passport-hero"><p className="eyebrow">ProofStudio Private Passport</p><h1>Account-linked provenance record</h1><p>This private read has no arbitrary public or checked-in fixture fallback.</p><a className="button secondary" href="/dashboard">Back to dashboard</a></section>{state ? <StatePanel state={state} label="Passport" /> : <section className="card"><h2>Authorizing Passport read…</h2></section>}</main>;
}
