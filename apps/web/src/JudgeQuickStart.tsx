type JudgeQuickStartProps = {
  goldenPassportHref: string;
};

const STEPS = [
  {
    number: "01",
    title: "Record",
    body: "Capture the generation path, provider decisions, retries, and fallbacks.",
  },
  {
    number: "02",
    title: "Store",
    body: "Archive the evidence and manifest in Backblaze B2.",
  },
  {
    number: "03",
    title: "Verify",
    body: "Inspect hashes, lineage, and the Provenance Passport.",
  },
] as const;

export function JudgeQuickStart({
  goldenPassportHref,
}: JudgeQuickStartProps) {
  return (
    <header
      className="card col-full judge-quick-start"
      id="judge-quick-start"
    >
      <div className="judge-quick-start-status">
        <p className="eyebrow">ProofStudio · Judge view</p>

        <div className="judge-quick-start-pills">
          <span className="pill ok">
            <span className="dot" />
            Live demo ready
          </span>

          <span className="pill info">
            <span className="dot" />
            No login required
          </span>
        </div>
      </div>

      <h1>Proof you can inspect, not just trust.</h1>

      <p className="judge-quick-start-lede">
        ProofStudio turns an AI media run into a clear record of what
        happened, what was stored, and what can be verified.
      </p>

      <div className="cockpit-cta-row judge-quick-start-actions">
        <a className="btn btn-primary" href={goldenPassportHref}>
          View the verified demo
        </a>

        <a className="btn" href="/campaign-proof-room">
          See the proof map
        </a>
      </div>

      <div
        className="judge-quick-start-steps"
        aria-label="How ProofStudio works"
      >
        {STEPS.map((step) => (
          <article className="judge-quick-start-step" key={step.number}>
            <span className="judge-quick-start-number">
              {step.number}
            </span>
            <h2>{step.title}</h2>
            <p>{step.body}</p>
          </article>
        ))}
      </div>

      <p className="hint judge-quick-start-boundary">
        ProofStudio proves what the pipeline recorded. Proof does not equal
        truth.
      </p>
    </header>
  );
}
