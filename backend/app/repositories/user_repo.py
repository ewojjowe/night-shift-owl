"""User collection access: create accounts and look them up.

All functions are ``async`` because Motor's operations are awaitable. Each returns
a typed ``UserInDB`` (or ``None``) rather than a raw Mongo document, so callers
work with validated objects and never see the ``_id``/``ObjectId`` plumbing.
"""

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

from app.db import get_database
from app.models.user import UserInDB


def _to_user(doc: dict) -> UserInDB:
    """Convert a raw MongoDB user document into a typed ``UserInDB``.

    MongoDB stores the primary key as ``_id`` (an ``ObjectId``); the rest of the
    app wants a plain string ``id``. Centralising that translation here means no
    other function has to remember to do it, and the shape stays consistent.
    """
    return UserInDB(
        id=str(doc["_id"]),
        username=doc["username"],
        email=doc["email"],
        hashed_password=doc["hashed_password"],
        created_at=doc["created_at"],
    )


async def create_user(username: str, email: str, hashed_password: str) -> UserInDB:
    """Insert a new user and return it, or raise ``DuplicateKeyError`` on a clash.

    We don't pre-check for an existing username/email and then insert — that has a
    race condition (two requests could both pass the check). Instead we rely on the
    unique indexes from ``db.py`` and let MongoDB reject the duplicate atomically;
    the router catches ``DuplicateKeyError`` and turns it into a friendly 409.
    """
    from datetime import datetime

    doc = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
    }
    result = await get_database().users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _to_user(doc)


async def get_by_username(username: str) -> UserInDB | None:
    """Fetch a user by their unique username, or None if nobody has it.

    Used by the login flow to find the account whose password hash we must check.
    """
    doc = await get_database().users.find_one({"username": username})
    return _to_user(doc) if doc else None


async def get_by_id(user_id: str) -> UserInDB | None:
    """Fetch a user by their string id, or None if not found / id is malformed.

    The auth dependency calls this on every protected request using the id stored
    in the JWT. We guard the ``ObjectId(user_id)`` conversion because a tampered or
    stale token could carry a non-ObjectId string, and we want that to read as
    "unknown user" (None) rather than crash the request.
    """
    try:
        oid = ObjectId(user_id)
    except (InvalidId, TypeError):
        return None
    doc = await get_database().users.find_one({"_id": oid})
    return _to_user(doc) if doc else None
