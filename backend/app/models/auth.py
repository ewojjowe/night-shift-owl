"""Schemas for the authentication endpoints (register / login / token)."""

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    """Payload a new user submits to create an account.

    Validation rules are expressed declaratively via ``Field`` constraints so bad
    input is rejected before any of our code runs: usernames must be a sane length
    and passwords must be at least 8 characters. ``EmailStr`` verifies the address
    is well-formed (thanks to the ``email-validator`` dependency).
    """

    username: str = Field(min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    """Payload for logging in with an existing account.

    We authenticate by username + password. Kept separate from ``RegisterIn`` so
    the two endpoints can evolve independently (login should never grow an email
    field, for instance).
    """

    username: str
    password: str


class Token(BaseModel):
    """The token pair returned after register, login, or refresh.

    ``access_token`` is the short-lived JWT sent on every request as
    ``Authorization: Bearer <token>``. ``refresh_token`` is the long-lived opaque
    token the client stores and later exchanges (via /auth/refresh) for a fresh
    pair once the access token expires. ``token_type`` is the conventional
    "bearer". Returning a typed model keeps the OpenAPI docs accurate.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    """Payload for ``POST /auth/refresh`` — the client's current refresh token.

    Kept as its own one-field model (rather than a query/header) so the token
    stays out of URLs and server logs, and so the endpoint's contract is explicit
    in the OpenAPI schema.
    """

    refresh_token: str
