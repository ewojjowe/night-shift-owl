"""Password hashing and token helpers (access JWTs + refresh tokens).

Three security concerns live here:

1. **Passwords** — we never store what the user typed. We store a bcrypt *hash*,
   a one-way function: given the hash you cannot recover the password, but you
   can check whether a fresh attempt matches.
2. **Access tokens** — after login we hand the browser a short-lived signed JWT.
   Because it's signed with our secret, we can trust its contents on later
   requests without a database lookup. It is *stateless*: we can't revoke an
   individual access JWT, so it's kept short-lived (minutes).
3. **Refresh tokens** — a long-lived, *opaque* random string (not a JWT). It is
   stored server-side (hashed) so it CAN be revoked, and it is rotated on every
   use. The browser trades it for a fresh access token when the old one expires.
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from passlib.context import CryptContext

from app.config import get_settings

# passlib's "context" abstracts the hashing scheme. Using it (rather than calling
# bcrypt directly) means we could add a newer algorithm later and passlib would
# transparently verify old hashes while writing new ones — future-proofing.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Turn a plaintext password into a salted bcrypt hash for storage.

    bcrypt automatically generates a random salt and embeds it in the output, so
    two users with the same password still get different hashes — defeating
    precomputed "rainbow table" attacks. The returned string is what we persist.
    """
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a login attempt against the stored hash, returning True on a match.

    passlib re-derives the hash from ``plain_password`` using the salt baked into
    ``hashed_password`` and compares them in constant time (which avoids leaking
    information through how long the comparison takes).
    """
    return _pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    """Create a signed, short-lived access JWT identifying the logged-in user.

    ``subject`` is the user id the token represents; it goes in the standard
    ``sub`` claim. We add ``exp`` (expiry, minutes away) so a leaked token is only
    briefly useful, and ``iat`` (issued-at). The payload is signed with the access
    secret — any tampering invalidates the signature on the next verify.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_expire_minutes),
    }
    return jwt.encode(
        payload, settings.jwt_access_secret, algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str) -> str | None:
    """Verify an access JWT and return the user id it represents, or None if invalid.

    "Invalid" covers a forged signature, an expired token, or a malformed string —
    ``python-jose`` raises ``JWTError`` for all of these, and we translate that
    into a simple ``None`` so the caller (the auth dependency) can respond with a
    clean 401 instead of leaking exception details.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.jwt_access_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload.get("sub")
    except JWTError:
        return None


def generate_refresh_token() -> str:
    """Generate a new opaque refresh token — a long, unguessable random string.

    Unlike the access JWT, a refresh token carries no readable claims; it is just a
    cryptographically-random secret (``secrets.token_urlsafe`` uses the OS CSPRNG).
    Its meaning lives entirely in the server-side record we store for it, which is
    what lets us revoke and rotate it. This raw value is returned to the client
    exactly once and never stored as-is (see ``hash_refresh_token``).
    """
    return secrets.token_urlsafe(48)


def hash_refresh_token(raw_token: str) -> str:
    """Hash a refresh token for storage, so a DB leak can't reveal usable tokens.

    We store only this hash, never the raw token — the same reasoning as password
    hashing. We use HMAC-SHA256 keyed with a server-side "pepper"
    (``jwt_refresh_secret``): because refresh tokens are already high-entropy we
    don't need bcrypt's slowness, but keying the hash means an attacker who dumps
    the database still can't precompute matches without also stealing the pepper.
    Lookups hash the presented token and compare against the stored hash.
    """
    settings = get_settings()
    return hmac.new(
        settings.jwt_refresh_secret.encode(),
        raw_token.encode(),
        hashlib.sha256,
    ).hexdigest()
