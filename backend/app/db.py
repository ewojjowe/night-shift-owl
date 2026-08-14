"""MongoDB connection management.

This module owns the single Motor client for the whole application. Everything
else asks it for *collections* (``users``, ``progress``, ``curriculum``) rather
than creating its own connections — one client, pooled, shared.

Motor is the async driver: every query returns an awaitable, which is what lets
FastAPI handle many requests concurrently on one thread without blocking on I/O.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

# Module-level handles. They start as None and are created once at startup by
# connect_to_mongo(). Keeping them at module scope means "import once, reuse
# everywhere" instead of reconnecting per request.
_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    """Open the shared MongoDB connection and create indexes.

    Called once from the FastAPI lifespan handler at startup. We create the
    client here (not at import time) so importing this module never triggers a
    network connection — important for tests and for tooling that just inspects
    the code. Indexes are declared here too, because MongoDB creates a collection
    lazily on first write and we want our uniqueness guarantees in place first.
    """
    global _client, _db
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.mongo_uri)
    _db = _client[settings.mongo_db_name]
    await _ensure_indexes()


async def close_mongo_connection() -> None:
    """Close the MongoDB connection cleanly on shutdown.

    Letting the process exit would also drop the sockets, but closing explicitly
    releases the connection pool promptly and is the tidy, testable thing to do.
    """
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_database() -> AsyncIOMotorDatabase:
    """Return the shared database handle, or fail loudly if we forgot to connect.

    Repositories call this to reach their collections. The explicit error turns a
    confusing ``NoneType`` crash deep in a query into a clear message that says
    "the startup hook didn't run", which is far easier to debug.
    """
    if _db is None:
        raise RuntimeError(
            "Database is not initialised — connect_to_mongo() must run at startup."
        )
    return _db


async def _ensure_indexes() -> None:
    """Create the unique indexes the data model depends on.

    Indexes are idempotent in MongoDB: creating one that already exists is a
    no-op, so this is safe to run on every startup.

    * ``users.username`` unique  — two people can't grab the same handle.
    * ``users.email`` unique     — one account per email address.
    * ``progress.user_id`` unique — exactly one progress document per user, which
      lets us treat "find the progress for this user" as a single-document lookup.
    * ``refresh_tokens.token_hash`` unique — fast, collision-free token lookups.
    * ``refresh_tokens.family_id`` — so the reuse-detection kill switch can revoke
      a whole family in one query.
    * ``refresh_tokens.expires_at`` **TTL** — MongoDB auto-deletes each token row
      once it expires (``expireAfterSeconds=0`` means "delete at the stored time"),
      so spent/expired tokens never pile up and cleanup needs no cron job.

    Note: these are all *additive* index creations, which are safe to run at
    startup. Destructive or blocking schema changes follow the migration runbook in
    DEPLOYMENT.md instead — never at boot.
    """
    db = get_database()
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
    await db.progress.create_index("user_id", unique=True)
    await db.curriculum.create_index("key", unique=True)
    await db.refresh_tokens.create_index("token_hash", unique=True)
    await db.refresh_tokens.create_index("family_id")
    await db.refresh_tokens.create_index("expires_at", expireAfterSeconds=0)
