"""Curriculum endpoint: serve the seeded study material."""

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.curriculum import Track
from app.models.user import UserInDB
from app.repositories import curriculum_repo

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


@router.get("", response_model=list[Track])
async def list_curriculum(
    _current_user: UserInDB = Depends(get_current_user),
) -> list[Track]:
    """Return every curriculum track and the projects list from the database.

    This replaces the hard-coded JavaScript arrays in the original page: the
    frontend fetches the material once after login and caches it in a Pinia store.
    Login is required (the ``_current_user`` dependency) — the leading underscore
    signals we only use it as an auth gate, not for its value. Because the content
    is identical for everyone, no per-user filtering is needed.
    """
    return await curriculum_repo.get_all()
