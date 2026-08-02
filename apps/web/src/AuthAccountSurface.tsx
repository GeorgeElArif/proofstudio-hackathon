import { FormEvent, ReactNode, useCallback, useEffect, useMemo, useState } from "react";
import {
  getAuthBaseUrl,
  getAuthReadiness,
  getAuthSession,
  submitLogin,
  submitLogout,
  submitSignup,
  type AuthActionResult,
  type AuthHealthResponse,
  type AuthSessionReadback,
  type ProviderConfigStatus,
} from "./authClient";

type AuthView = "login" | "signup" | "account";

type AuthAccountSurfaceProps = {
  view: AuthView;
};

const TRUST_BOUNDARY =
  "Auth proves account/session identity only. ProofStudio proves what the pipeline recorded. Proof does not equal truth.";

function StatusPill({
  tone,
  children,
}: {
  tone: "ok" | "warn" | "danger" | "info" | "neutral";
  children: ReactNode;
}) {
  return (
    <span className={`pill ${tone === "neutral" ? "" : tone}`}>
      <span className="dot" />
      {children}
    </span>
  );
}

function providerTone(status: ProviderConfigStatus["status"]): "ok" | "warn" | "danger" | "neutral" {
  if (status === "configured") return "ok";
  if (status === "missing") return "neutral";
  if (status === "placeholder") return "warn";
  return "danger";
}

function ProviderRow({ label, provider }: { label: string; provider?: ProviderConfigStatus }) {
  if (!provider) {
    return (
      <div className="auth-provider-row">
        <span>{label}</span>
        <StatusPill tone="neutral">unknown</StatusPill>
      </div>
    );
  }

  return (
    <div className="auth-provider-row">
      <span>{label}</span>
      <StatusPill tone={providerTone(provider.status)}>{provider.status}</StatusPill>
    </div>
  );
}

function readinessTone(readiness: AuthHealthResponse | null): "ok" | "warn" | "danger" | "neutral" {
  if (!readiness) return "danger";
  if (readiness.ready) return "ok";
  if (readiness.readiness.envConfigured) return "warn";
  return "danger";
}

function sessionTone(session: AuthSessionReadback): "ok" | "warn" | "danger" | "neutral" {
  if (session.state === "authenticated") return "ok";
  if (session.state === "unauthenticated") return "neutral";
  if (session.state === "unavailable") return "warn";
  return "danger";
}

function sessionLabel(session: AuthSessionReadback): string {
  if (session.state === "authenticated") return "authenticated";
  if (session.state === "unauthenticated") return "unauthenticated";
  if (session.state === "unavailable") return "runtime unavailable";
  return "network failure";
}

function AuthNav({ view }: { view: AuthView }) {
  return (
    <nav className="auth-nav" aria-label="Auth navigation">
      <a aria-current={view === "login" ? "page" : undefined} href="/login">
        Login
      </a>
      <a aria-current={view === "signup" ? "page" : undefined} href="/signup">
        Signup
      </a>
      <a aria-current={view === "account" ? "page" : undefined} href="/account/session">
        Session
      </a>
    </nav>
  );
}

export function AuthAccountSurface({ view }: AuthAccountSurfaceProps) {
  const [readiness, setReadiness] = useState<AuthHealthResponse | null>(null);
  const [session, setSession] = useState<AuthSessionReadback>({
    state: "network_error",
    authenticated: false,
    liveRuntimeAuth: false,
    reason: "Auth session has not been read yet.",
  });
  const [busy, setBusy] = useState(false);
  const [actionResult, setActionResult] = useState<AuthActionResult | null>(null);
  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [signupForm, setSignupForm] = useState({ name: "", email: "", password: "" });

  const refreshAuthState = useCallback(async () => {
    const [nextReadiness, nextSession] = await Promise.all([
      getAuthReadiness(),
      getAuthSession(),
    ]);
    setReadiness(nextReadiness);
    setSession(nextSession);
  }, []);

  useEffect(() => {
    void refreshAuthState();
  }, [refreshAuthState]);

  const runtimeReady = readiness?.ready === true && session.state !== "unavailable";
  const formUnavailable = !runtimeReady;
  const providers = session.state === "network_error"
    ? readiness?.readiness.providers
    : session.readiness?.providers ?? readiness?.readiness.providers;
  const heading = view === "login" ? "Login" : view === "signup" ? "Signup" : "Account session";
  const subhead = useMemo(() => {
    if (view === "account") return "Read the current server-owned session state without dashboard access.";
    if (view === "signup") return "Create an account only when the auth runtime is configured and email verification can run.";
    return "Submit credentials to the auth runtime only; the UI waits for server session readback.";
  }, [view]);

  async function runAction(action: () => Promise<AuthActionResult>) {
    setBusy(true);
    setActionResult(null);
    try {
      const result = await action();
      setActionResult(result);
      await refreshAuthState();
    } finally {
      setBusy(false);
    }
  }

  function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void runAction(() => submitLogin(loginForm));
  }

  function handleSignup(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void runAction(() => submitSignup(signupForm));
  }

  return (
    <main className="auth-page">
      <section className="auth-hero" aria-labelledby="auth-heading">
        <div>
          <p className="eyebrow">ProofStudio · PS-040E</p>
          <h1 id="auth-heading">{heading}</h1>
          <p>{subhead}</p>
        </div>
        <AuthNav view={view} />
      </section>

      <section className="auth-shell" aria-label="Auth session workspace">
        <div className="auth-panel auth-panel-primary">
          <div className="auth-panel-head">
            <div>
              <h2>{view === "account" ? "Session readback" : `${heading} boundary`}</h2>
              <p>{getAuthBaseUrl()}</p>
            </div>
            <StatusPill tone={sessionTone(session)}>{sessionLabel(session)}</StatusPill>
          </div>

          {view === "login" && (
            <form className="auth-form" onSubmit={handleLogin}>
              <label>
                Email
                <input
                  autoComplete="email"
                  disabled={formUnavailable || busy}
                  inputMode="email"
                  onChange={(event) => setLoginForm((current) => ({ ...current, email: event.target.value }))}
                  required
                  type="email"
                  value={loginForm.email}
                />
              </label>
              <label>
                Password
                <input
                  autoComplete="current-password"
                  disabled={formUnavailable || busy}
                  minLength={8}
                  onChange={(event) => setLoginForm((current) => ({ ...current, password: event.target.value }))}
                  required
                  type="password"
                  value={loginForm.password}
                />
              </label>
              <button className="btn btn-primary" disabled={formUnavailable || busy} type="submit">
                {busy ? "Submitting..." : "Submit login"}
              </button>
            </form>
          )}

          {view === "signup" && (
            <form className="auth-form" onSubmit={handleSignup}>
              <label>
                Name
                <input
                  autoComplete="name"
                  disabled={formUnavailable || busy}
                  onChange={(event) => setSignupForm((current) => ({ ...current, name: event.target.value }))}
                  required
                  type="text"
                  value={signupForm.name}
                />
              </label>
              <label>
                Email
                <input
                  autoComplete="email"
                  disabled={formUnavailable || busy}
                  inputMode="email"
                  onChange={(event) => setSignupForm((current) => ({ ...current, email: event.target.value }))}
                  required
                  type="email"
                  value={signupForm.email}
                />
              </label>
              <label>
                Password
                <input
                  autoComplete="new-password"
                  disabled={formUnavailable || busy}
                  minLength={8}
                  onChange={(event) => setSignupForm((current) => ({ ...current, password: event.target.value }))}
                  required
                  type="password"
                  value={signupForm.password}
                />
              </label>
              <button className="btn btn-primary" disabled={formUnavailable || busy} type="submit">
                {busy ? "Submitting..." : "Submit signup"}
              </button>
            </form>
          )}

          {view === "account" && (
            <div className="auth-session-card">
              {session.state === "authenticated" ? (
                <dl className="kv">
                  <dt>user</dt>
                  <dd>{session.user.email ?? session.user.id ?? "available"}</dd>
                  <dt>email verified</dt>
                  <dd>{session.user.emailVerified ? "yes" : "no"}</dd>
                  <dt>session expires</dt>
                  <dd>{session.session.expiresAt ?? "not reported"}</dd>
                </dl>
              ) : (
                <div className="empty">
                  {session.state === "network_error"
                    ? session.reason
                    : session.state === "unavailable"
                      ? session.reason
                      : "No active server session was returned."}
                </div>
              )}
              <div className="btn-row auth-actions">
                <button className="btn" disabled={busy} onClick={() => void refreshAuthState()} type="button">
                  Refresh
                </button>
                {session.state === "authenticated" && (
                  <button className="btn btn-danger" disabled={busy} onClick={() => void runAction(submitLogout)} type="button">
                    Logout
                  </button>
                )}
              </div>
            </div>
          )}

          {formUnavailable && view !== "account" && (
            <div className="warn-inline">
              Auth runtime is not ready, so the form is not submitted. Configure the auth server and database first.
            </div>
          )}

          {actionResult && (
            <div className={actionResult.ok ? "info-inline" : "err-box"}>
              {actionResult.message}
            </div>
          )}
        </div>

        <aside className="auth-panel">
          <div className="auth-panel-head">
            <div>
              <h2>Runtime readiness</h2>
              <p>Safe categories only. No credentials are exposed.</p>
            </div>
            <StatusPill tone={readinessTone(readiness)}>
              {readiness?.ready ? "ready" : readiness ? "not ready" : "unreachable"}
            </StatusPill>
          </div>
          <div className="auth-provider-list">
            <ProviderRow label="Auth base" provider={providers?.authBase} />
            <ProviderRow label="Database" provider={providers?.database} />
            <ProviderRow label="Email" provider={providers?.email} />
            <ProviderRow label="Google OAuth" provider={providers?.google} />
            <ProviderRow label="GitHub OAuth" provider={providers?.github} />
            <ProviderRow label="Apple OAuth" provider={providers?.apple} />
          </div>
          <div className="auth-oauth-actions" aria-label="OAuth providers">
            {(["google", "github", "apple"] as const).map((provider) => {
              const status = providers?.[provider];
              const configured = status?.status === "configured";
              return (
                <button className="btn" disabled={!configured || busy} key={provider} type="button">
                  {provider} {configured ? "continue" : "not configured"}
                </button>
              );
            })}
          </div>
        </aside>
      </section>

      <section className="auth-boundary" aria-label="Trust boundary">
        <p>{TRUST_BOUNDARY}</p>
        <p>
          Auth does not prove semantic truth, legal authenticity, human authorship, or C2PA authenticity.
        </p>
      </section>
    </main>
  );
}
