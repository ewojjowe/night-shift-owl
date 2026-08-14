"""Schemas describing a user account at rest and on the wire."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    """The public view of a user — safe to send to the browser.

    Crucially there is **no password field of any kind** here. Even though the
    stored document contains ``hashed_password``, this model simply omits it, so
    it can never accidentally be serialized into a response. The ``id`` is the
    MongoDB ``_id`` converted to a string by the repository layer.
    """

    id: str
    username: str
    email: EmailStr
    created_at: datetime


class UserInDB(BaseModel):
    """The full user document as it lives in MongoDB, including the hash.

    Used internally (e.g. during login, to read the hash and verify a password).
    It stays server-side only — endpoints return ``UserOut`` instead. Keeping this
    as its own model documents exactly what a user document contains.
    """

    id: str
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
