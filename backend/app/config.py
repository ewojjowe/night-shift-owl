"""Application configuration, loaded from environment variables.

We use ``pydantic-settings`` instead of reading ``os.environ`` by hand because it
gives us three things for free:

1. **Typing** — ``jwt_expire_minutes`` arrives as an ``int``, not a string.
2. **Validation** — a missing required value fails loudly at startup, not at 3am.
3. **One source of truth** — every setting is documented in one place with a default.

Secrets (like ``jwt_secret``) are read from the environment and never hard-coded,
which is why ``docker-compose.yml`` and ``.env.example`` supply them from outside.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed container for every configurable value in the backend.

    Each attribute maps to an environment variable of the same (upper-cased)
    name — e.g. the attribute ``mongo_uri`` is populated from ``MONGO_URI``.
    Defaults are chosen so the app still boots locally with zero configuration,
    while production deployments override the sensitive ones.
    """

    # Where to reach MongoDB. The default hostname "mongo" is the service name
    # defined in docker-compose.yml, so containers resolve it automatically.
    mongo_uri: str = "mongodb://mongo:27017"

    # Logical database name inside that MongoDB server.
    mongo_db_name: str = "night_shift"

    # Secret used to SIGN short-lived access JWTs. MUST be overridden in any real
    # deployment — a leaked secret lets anyone forge a login token. The default
    # exists only so the dev stack runs out of the box.
    jwt_access_secret: str = "dev-only-insecure-access-secret-change-me"

    # Separate secret used as an HMAC "pepper" when hashing refresh tokens before
    # they are stored (see security.hash_refresh_token). Keeping it distinct from
    # the access secret means compromising one does not automatically compromise
    # the other. Also MUST be overridden in production.
    jwt_refresh_secret: str = "dev-only-insecure-refresh-secret-change-me"

    # Signing algorithm for the access JWT. HS256 is symmetric (same secret
    # signs+verifies), the simplest correct choice for a single-service backend.
    jwt_algorithm: str = "HS256"

    # How long an ACCESS token stays valid. Deliberately short: if one leaks, the
    # window of misuse is small, because the client silently swaps it for a new one
    # using its refresh token (which is revocable server-side).
    access_expire_minutes: int = 15

    # How long a REFRESH token stays valid. Longer, so a user isn't forced to
    # re-enter their password often — but each use rotates it, and it can be
    # revoked instantly, which an access JWT cannot.
    refresh_expire_days: int = 7

    # Browser origin allowed to call this API (CORS). Locked down to the Vite dev
    # server so a random website can't drive the API using a logged-in user's token.
    cors_origins: list[str] = ["http://localhost:5173"]

    # Pydantic-settings behaviour: also read a local .env file if present, and
    # ignore any unrelated environment variables rather than erroring on them.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return a single, cached ``Settings`` instance for the whole process.

    ``lru_cache`` means the environment is parsed exactly once; every caller
    (routers, security helpers, the DB module) gets the same object. This is the
    canonical FastAPI pattern for configuration and makes the settings trivial to
    override in tests by clearing the cache.
    """
    return Settings()
