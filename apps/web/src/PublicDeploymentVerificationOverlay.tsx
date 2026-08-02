import {
  HISTORICAL_PS025_DEPLOYMENT_PENDING,
  PUBLIC_DEPLOYMENT_VERIFICATION,
} from "./publicDeploymentVerification";

export function PublicDeploymentVerificationOverlay() {
  const verification = PUBLIC_DEPLOYMENT_VERIFICATION;

  return (
    <section
      className="card col-full public-deployment-verification-overlay"
      id="public-deployment-verification"
    >
      {/* PS-042C2 contract:
          current public API deployment verified;
          historical PS-025 state preserved. */}

      <div className="deployment-status-summary">
        <div>
          <p className="eyebrow">Live status</p>
          <h2>Demo verified and ready</h2>
          <p>
            The public evidence page loads correctly, and private records
            remain protected.
          </p>
        </div>

        <span className="pill ok deployment-status-pill">
          <span className="dot" />
          Online
        </span>
      </div>

      <details className="deployment-technical-details">
        <summary>View technical verification</summary>

        <dl className="kv">
          <dt>verification</dt>
          <dd className="mono">{verification.slice}</dd>

          <dt>API</dt>
          <dd className="mono">{verification.apiUrl}</dd>

          <dt>API revision</dt>
          <dd className="mono">{verification.apiCommit}</dd>

          <dt>verified on</dt>
          <dd className="mono">{verification.verifiedOn}</dd>

          <dt>health</dt>
          <dd className="mono">HTTP {verification.healthStatus}</dd>

          <dt>public Passport</dt>
          <dd className="mono">HTTP {verification.passportStatus}</dd>

          <dt>private route protection</dt>
          <dd className="mono">
            HTTP {verification.privateRunStatus} ·{" "}
            {verification.privateRunCode}
          </dd>

          <dt>provider calls during rehydrate</dt>
          <dd className="mono">
            {verification.providerCallsDuringRehydrate}
          </dd>

          <dt>credentials used</dt>
          <dd className="mono">
            {String(verification.credentialsUsed)}
          </dd>

          <dt>receipt</dt>
          <dd className="mono">{verification.receiptPath}</dd>
        </dl>

        <p className="hint">
          The historical PS-025 value{" "}
          <code className="mono">
            public_deployment_pending:{" "}
            {String(HISTORICAL_PS025_DEPLOYMENT_PENDING)}
          </code>{" "}
          is preserved because it records the state at the time that evidence
          was captured. It is not the current deployment status.
        </p>
      </details>
    </section>
  );
}
