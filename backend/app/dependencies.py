"""Reusable FastAPI dependencies.

A "dependency" is a function FastAPI runs before your endpoint and injects the
result into it. The one here answers the question every protected route needs:
"who is making this request?" Declaring ``current_user`` as a parameter on a route
is all it takes to require a valid login — the framework wires the rest.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.models.user import UserInDB
from app.repositories import user_repo
from app.security import decode_access_token

# Tells FastAPI/Swagger that tokens are obtained from the /auth/login endpoint and
# arrive in the "Authorization: Bearer <token>" header. It also powers the
# "Authorize" button in the auto-generated /docs UI.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Resolve the request's bearer token into the authenticated ``UserInDB``.

    The flow is: extract the token (done by ``oauth2_scheme``), verify+decode it to
    a user id, then load that user. Any failure along the way — missing/invalid/
    expired token, or a user that no longer exists — raises 401 with the standard
    ``WWW-Authenticate: Bearer`` header. Routes depend on this to guarantee that by
    the time their code runs, ``current_user`` is a real, logged-in account.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_error

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_error

    return user
