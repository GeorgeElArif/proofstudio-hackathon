import type { AuthRuntimeReadiness } from "../env.js";

export type HealthPayload = {
  service: "proofstudio-auth-server";
  slice: "PS-040C";
  liveRuntimeAuth: boolean;
  ready: boolean;
  readiness: AuthRuntimeReadiness;
  trustBoundary: string;
};

export function buildHealthPayload(
  readiness: AuthRuntimeReadiness,
  liveRuntimeAuth: boolean,
): HealthPayload {
  return {
    service: "proofstudio-auth-server",
    slice: "PS-040C",
    liveRuntimeAuth,
    ready: readiness.configured,
    readiness,
    trustBoundary:
      "Auth proves account/session identity only. ProofStudio proves what the pipeline recorded. Proof does not equal truth.",
  };
}
