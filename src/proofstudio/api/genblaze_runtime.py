"""PS-041E0 fail-closed Genblaze runtime version guard.

This is the single place that asserts the FastAPI service is running against
the exact selective Genblaze v0.7.0 GMICloud connector compatibility
matrix required by PS-041E0. Mixed worker versions are forbidden: a
partial upgrade (one or two of the three packages moved) must fail closed
before the service
is considered ready.

Contract:

- reads installed versions via the public ``importlib.metadata.version`` API
  only;
- compares against an exact-equality allowlist (:data:`EXPECTED_VERSIONS`);
- raises :class:`GenblazeRuntimeVersionError` on any mismatch, missing
  distribution, partial upgrade, or unexpected prerelease / local version;
- performs no provider import, no provider call, and no B2 / network access;
- never reads, prints, or logs environment variables, credentials, DB URLs,
  tokens, or filesystem paths;
- safe version numbers (package name + version string) may appear in the
  operator diagnostic.

The expected map is hard-coded here on purpose. It is never derived from the
installed packages, never overridden by an environment variable, and never
added to authorization or evidence identity.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Mapping


# Selective Genblaze v0.7.0 connector wave. The umbrella tag resolves to
# release commit ec81e810f2643ed7ad2eb5e639d9b02470c887fd. ProofStudio adopts
# the GMICloud connector update while retaining its validated core, S3, and
# Pillow security baseline. No individual package is claimed to be v0.7.0.
GENBLAZE_RELEASE_TAG = "v0.7.0"
GENBLAZE_RELEASE_COMMIT = "ec81e810f2643ed7ad2eb5e639d9b02470c887fd"

# Exact-equality allowlist. A worker is ready only when every installed
# distribution matches its expected version exactly. No minimum ranges, no
# compatibility markers, no environment overrides.
EXPECTED_VERSIONS: Mapping[str, str] = {
    "genblaze-core": "0.3.6",
    "genblaze-s3": "0.3.5",
    "genblaze-gmicloud": "0.3.5",
}


class GenblazeRuntimeVersionError(RuntimeError):
    """Raised when the installed Genblaze runtime versions do not match the
    PS-041E0 exact-equality allowlist.

    The message is operator-safe: it contains only package names and version
    strings. It never carries environment values, credentials, DB URLs,
    tokens, or filesystem paths.
    """

    def __init__(
        self,
        message: str,
        *,
        expected: Mapping[str, str],
        installed: Mapping[str, str | None],
    ) -> None:
        super().__init__(message)
        self.expected = dict(expected)
        self.installed = dict(installed)


def _installed_version(distribution: str) -> str | None:
    try:
        return version(distribution)
    except PackageNotFoundError:
        return None


def assert_genblaze_runtime_versions(
    *,
    expected: Mapping[str, str] | None = None,
) -> Mapping[str, str]:
    """Assert the installed Genblaze runtime matches the exact allowlist.

    Returns the installed version map on success. Raises
    :class:`GenblazeRuntimeVersionError` on any mismatch. Performs no provider
    import, provider call, or B2 / network access.

    The ``expected`` keyword is reserved for focused unit tests that need to
    drive the guard against a controlled allowlist. Production callers must
    omit it so the hard-coded :data:`EXPECTED_VERSIONS` allowlist is enforced.

    This function always performs a fresh ``importlib.metadata`` lookup; it is
    deliberately uncached so focused unit tests can drive it against controlled
    version surfaces via monkeypatching. Production startup callers that need
    idempotency across re-imports and ``create_app()`` calls must use
    :func:`verify_runtime_versions_cached` instead.
    """
    allowlist = EXPECTED_VERSIONS if expected is None else expected
    installed: dict[str, str | None] = {
        name: _installed_version(name) for name in allowlist
    }
    problems: list[str] = []
    for name, expected_version in allowlist.items():
        actual = installed[name]
        if actual is None:
            problems.append(
                f"{name} missing (expected {expected_version})"
            )
        elif actual != expected_version:
            problems.append(
                f"{name}=={actual} does not match expected {expected_version}"
            )
    if problems:
        joined = "; ".join(problems)
        message = (
            "Genblaze selective v0.7.0 connector-wave runtime check failed "
            "(mixed worker versions are forbidden): " + joined
        )
        raise GenblazeRuntimeVersionError(
            message, expected=dict(allowlist), installed=installed
        )
    # Narrow the typing: on success every installed entry is a real string.
    return {name: str(installed[name]) for name in allowlist}


# PS-041E0: idempotent cached single verification. The very first call runs
# the real metadata check and caches the verified version map; every later
# call in the same process returns the cached result without re-querying
# ``importlib.metadata``. This is what production startup uses so that
# ``proofstudio.api.__init__`` and ``proofstudio.api.app`` together invoke the
# underlying metadata check exactly once per process, even when
# ``create_app()`` is called repeatedly. The cache holds only safe
# package-name -> version-string entries.
_CACHED_VERIFIED_VERSIONS: Mapping[str, str] | None = None


def verify_runtime_versions_cached() -> Mapping[str, str]:
    """Return the cached verified Genblaze runtime version map.

    Runs :func:`assert_genblaze_runtime_versions` exactly once per process and
    caches the successful result. Subsequent calls return the cache directly.
    A failure always raises before any value is cached, so a later call (e.g.
    from ``create_app()``) still observes the same controlled
    :class:`GenblazeRuntimeVersionError`.

    This wrapper is stdlib-only, performs no provider import, provider call, or
    B2 / network access, and stores only safe package-name / version-string
    entries.
    """
    global _CACHED_VERIFIED_VERSIONS
    if _CACHED_VERIFIED_VERSIONS is None:
        _CACHED_VERIFIED_VERSIONS = assert_genblaze_runtime_versions()
    return _CACHED_VERIFIED_VERSIONS


def reset_cached_runtime_verification() -> None:
    """Clear the cached verification result.

    Reserved for focused unit tests that need to observe a fresh check after
    monkeypatching the metadata surface. Production code never calls this.
    """
    global _CACHED_VERIFIED_VERSIONS
    _CACHED_VERIFIED_VERSIONS = None


__all__ = [
    "GENBLAZE_RELEASE_TAG",
    "GENBLAZE_RELEASE_COMMIT",
    "EXPECTED_VERSIONS",
    "GenblazeRuntimeVersionError",
    "assert_genblaze_runtime_versions",
    "verify_runtime_versions_cached",
    "reset_cached_runtime_verification",
]
