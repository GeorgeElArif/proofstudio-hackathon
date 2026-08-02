# PS-042C0A — Free Render Staging Blueprint Proof

## Scope and result

PS-042C0A prepares a free staging Blueprint. It does not create Render
resources, run a staging migration, deploy the application, or prove that any
public endpoint is operational.

The local staging plan is `render.free.yaml`. It preserves the accepted four
resource names and Oregon topology while selecting free plans for API, auth,
and PostgreSQL. The static site has no paid plan field. All three Git-backed
services explicitly bind `ps-042c0/free-render-staging-v1`; automatic deploys
and preview generation are off.

## Safety boundaries

Migrations are operator-controlled and absent from build, start, startup,
pre-deploy, and initial-deploy commands. PostgreSQL external access starts
blocked. Auth receives the internal database connection through
`fromDatabase`, while auth calls the free API through the API service's public
`RENDER_EXTERNAL_URL`.

Live runs, B2 writes, and paid runs remain false. The cost cap is zero and
fixtures are frozen. No provider, B2, OAuth, SMTP, real email-delivery, judge
credential, or real secret is included. The accepted auth-only capture mode
satisfies readiness without sending email or changing authentication code.
Synthetic staging accounts remain a later explicit provisioning operation.

The same-origin gateway retains all six auth-facing rewrites before the SPA
fallback and all six `Cache-Control: no-store` rules. Its destination assumes
`https://proofstudio-auth.onrender.com`; live synchronization must stop if
Render does not assign that exact hostname. Synchronization must also stop if
the preview shows any non-zero charge.

## Live-operation receipt boundary

Local validation performs no Render call, resource creation, deployment,
migration, account provisioning, charge, email send, OAuth call, B2 call, or
provider call. The staging smoke reports all such counters as zero.

## Truth boundary

ProofStudio proves what the pipeline recorded.
Proof does not equal truth.
