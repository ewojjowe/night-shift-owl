"""Refresh-token collection access — the server-side record behind each opaque token.

Storing refresh tokens (hashed) is what lets us do things a stateless access JWT
cannot: **revoke** a session immediately, **rotate** the token on every use, and
**detect reuse** of an already-spent token (a strong signal it was stolen).

Each document represents one issued refresh token:

    { user_id, token_hash, family_id, expires_at, revoked, created_at, replaced_by }

* ``token_hash`` — HMAC of the raw token (we never store the raw value).
* ``family_id``  — groups every token descended from a single login. Rotation
  keeps the family; detecting reuse revokes the whole family (see the router).
* ``replaced_by`` — the hash of the successor token created when this one rotated,
  useful for auditing a rotation chain.

Only this module queries the ``refresh_tokens`` collection.
"""

from datetime import datetime, timezone

from app.db import get_database


async def create(
    user_id: str, token_hash: str, family_id: str, expires_at: datetime
) -> None:
    """Persist a newly issued refresh token's record.

    Called at login/register (new family) and on every rotation (same family). We
    store the hash, the owning user, the family, and an absolute expiry — a TTL
    index on ``expires_at`` (declared in db.py) sweeps the row away once it lapses,
    so expired records never accumulate.
    """
    await get_database().refresh_tokens.insert_one(
        {
            "user_id": user_id,
            "token_hash": token_hash,
            "family_id": family_id,
            "expires_at": expires_at,
            "revoked": False,
            "created_at": datetime.now(timezone.utc),
            "replaced_by": None,
        }
    )


async def get_by_hash(token_hash: str) -> dict | None:
    """Look up a refresh token's record by its stored hash, or None if unknown.

    The caller hashes the raw token the client presented and passes it here. A
    ``None`` result means the token was never issued (or was already TTL-expired
    and swept) — either way, not usable.
    """
    return await get_database().refresh_tokens.find_one({"token_hash": token_hash})


async def mark_rotated(old_hash: str, new_hash: str) -> None:
    """Revoke a token because it was just exchanged, linking it to its successor.

    Rotation means "this refresh token has now been spent". We flip ``revoked`` so
    it can never be used again, and record ``replaced_by`` so a later presentation
    of this same (now-revoked) token is recognisable as reuse rather than a fresh
    unknown token.
    """
    await get_database().refresh_tokens.update_one(
        {"token_hash": old_hash},
        {"$set": {"revoked": True, "replaced_by": new_hash}},
    )


async def revoke(token_hash: str) -> None:
    """Revoke a single refresh token (used by logout).

    Idempotent: revoking an already-revoked token is a harmless no-op, so logout
    never errors even if the token was already spent or logged out elsewhere.
    """
    await get_database().refresh_tokens.update_one(
        {"token_hash": token_hash}, {"$set": {"revoked": True}}
    )


async def revoke_family(family_id: str) -> None:
    """Revoke every token in a family — the reuse-detection kill switch.

    If a *revoked* token is presented again, we must assume it was stolen and that
    the attacker (or the legitimate user) may hold other tokens in the same family.
    Revoking the whole family invalidates every descendant at once, forcing a fresh
    login and cutting off the thief.
    """
    await get_database().refresh_tokens.update_many(
        {"family_id": family_id}, {"$set": {"revoked": True}}
    )


async def revoke_all_for_user(user_id: str) -> None:
    """Revoke all of a user's refresh tokens — a global "log out everywhere".

    Not wired to an endpoint yet, but provided because it's the natural home for
    "sign out of all sessions" and for forced invalidation after a password change.
    """
    await get_database().refresh_tokens.update_many(
        {"user_id": user_id}, {"$set": {"revoked": True}}
    )
