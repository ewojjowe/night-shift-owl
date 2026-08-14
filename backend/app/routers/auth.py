"""Authentication endpoints: register, login, refresh, logout, and "who am I".

Register/login are the only unauthenticated write endpoints; they issue the token
pair everything else relies on. Refresh and logout manage the lifecycle of that
pair — rotating the refresh token on each use and revoking it on sign-out.
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.config import get_settings
from app.dependencies import get_current_user
from app.models.auth import LoginIn, RefreshIn, RegisterIn, Token
from app.models.user import UserInDB, UserOut
from app.repositories import refresh_token_repo, user_repo
from app.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)

# ``prefix`` means every route below is mounted under /auth; ``tags`` groups them
# together in the /docs UI. Both are cosmetic-but-helpful organisation.
router = APIRouter(prefix="/auth", tags=["auth"])


async def _issue_token_pair(user_id: str, family_id: str) -> Token:
    """Mint a fresh access + refresh token pair and persist the refresh record.

    Shared by register, login (new ``family_id``) and refresh (existing family, to
    keep a rotation lineage). We generate the opaque refresh token, store only its
    hash with an absolute expiry, and return the *raw* pair to the caller — the raw
    refresh token is shown to the client exactly once and never persisted as-is.
    """
    settings = get_settings()
    raw_refresh = generate_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_expire_days
    )
    await refresh_token_repo.create(
        user_id=user_id,
        token_hash=hash_refresh_token(raw_refresh),
        family_id=family_id,
        expires_at=expires_at,
    )
    return Token(
        access_token=create_access_token(subject=user_id),
        refresh_token=raw_refresh,
    )


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterIn) -> Token:
    """Create a new account and immediately return a token pair.

    We hash the password before it ever reaches the database, then let the unique
    indexes enforce that the username/email aren't already taken — catching
    ``DuplicateKeyError`` to return a clean 409 instead of a 500. A new login family
    is started so this session's refresh tokens rotate independently of any other.
    """
    try:
        user = await user_repo.create_user(
            username=payload.username,
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That username or email is already registered.",
        )
    return await _issue_token_pair(user.id, family_id=str(uuid.uuid4()))


@router.post("/login", response_model=Token)
async def login(payload: LoginIn) -> Token:
    """Verify credentials and return a token pair, or 401 on failure.

    The error message is deliberately identical whether the username is unknown or
    the password is wrong. Telling an attacker *which* was correct would let them
    enumerate valid usernames, so we collapse both cases into one vague 401. A
    successful login starts a new refresh-token family for this session.
    """
    user = await user_repo.get_by_username(payload.username)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
    return await _issue_token_pair(user.id, family_id=str(uuid.uuid4()))


@router.post("/refresh", response_model=Token)
async def refresh(payload: RefreshIn) -> Token:
    """Exchange a valid refresh token for a brand-new pair — with rotation + reuse detection.

    The security model, step by step:

    1. Look up the presented token by its hash. Unknown → 401 (never issued, or
       already expired and swept by the TTL index).
    2. **Reuse detection:** if the record is already ``revoked``, someone is
       replaying a spent token — a classic sign of theft. We revoke the *entire
       family* (every descendant token) and return 401, forcing a fresh login and
       locking out both the thief and the victim's stale copy.
    3. Expired (belt-and-suspenders vs. the TTL sweep) → 401.
    4. Otherwise **rotate**: mint a new pair in the same family, then mark the old
       token revoked and linked to its successor. The old token can never be used
       again; only the newest token in the chain is live.
    """
    token_hash = hash_refresh_token(payload.refresh_token)
    record = await refresh_token_repo.get_by_hash(token_hash)

    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token.",
    )

    if record is None:
        raise invalid

    if record["revoked"]:
        # Reuse of a spent token — assume compromise and nuke the whole family.
        await refresh_token_repo.revoke_family(record["family_id"])
        raise invalid

    expires_at = record["expires_at"]
    # Mongo may return a naive datetime; treat stored times as UTC for comparison.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise invalid

    new_pair = await _issue_token_pair(record["user_id"], family_id=record["family_id"])
    await refresh_token_repo.mark_rotated(
        old_hash=token_hash,
        new_hash=hash_refresh_token(new_pair.refresh_token),
    )
    return new_pair


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshIn) -> None:
    """Revoke the presented refresh token, ending that session server-side.

    Logout only needs the refresh token (not a valid access token), so it still
    works even if the access token has already expired. Revocation is idempotent,
    so a double logout is harmless. The access JWT is stateless and simply lapses
    on its own within minutes; revoking the refresh token stops any renewal.
    """
    await refresh_token_repo.revoke(hash_refresh_token(payload.refresh_token))


@router.get("/me", response_model=UserOut)
async def read_me(current_user: UserInDB = Depends(get_current_user)) -> UserOut:
    """Return the profile of the currently logged-in user.

    Depending on ``get_current_user`` makes this route require a valid access token.
    We map the internal ``UserInDB`` to the public ``UserOut`` so the password hash
    is structurally impossible to leak. The frontend calls this on load to confirm a
    stored token is still valid and to show the username.
    """
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
    )
