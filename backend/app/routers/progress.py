"""Progress endpoints: read, update config, advance a track, and reset.

Every route is scoped to the logged-in user via ``get_current_user`` — a user can
only ever read or change *their own* progress, because the user id comes from their
token, never from the request body or URL.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.models.progress import TRACK_KEYS, ProgressState, ProgressUpdate
from app.models.user import UserInDB
from app.repositories import curriculum_repo, progress_repo

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=ProgressState)
async def get_progress(
    current_user: UserInDB = Depends(get_current_user),
) -> ProgressState:
    """Return the current user's progress, creating defaults on first access.

    The frontend calls this right after login to hydrate its Pinia store. The
    "create on first read" behaviour (in the repository) means a new account is
    seamlessly given a day-1 document without any registration-time bookkeeping.
    """
    return await progress_repo.get_or_create(current_user.id)


@router.put("", response_model=ProgressState)
async def update_progress(
    changes: ProgressUpdate,
    current_user: UserInDB = Depends(get_current_user),
) -> ProgressState:
    """Apply a partial config update (shift schedule, defaults, UI open-state).

    ``ProgressUpdate`` intentionally can't carry the ``idx`` counters, so this
    endpoint can never be used to skip ahead in a track — it only touches the
    schedule/UI settings the user is allowed to edit freely. The frontend calls it
    whenever a shift input or a section toggle changes.
    """
    return await progress_repo.update(current_user.id, changes)


@router.patch("/tracks/{key}/complete", response_model=ProgressState)
async def complete_module(
    key: str,
    current_user: UserInDB = Depends(get_current_user),
) -> ProgressState:
    """Advance one track (or "projects") to its next module — the "Mark complete" button.

    We first look up the track in the curriculum to learn its length, both to
    validate that ``key`` is real (404 otherwise) and to cap the index at the final
    module so a user can't advance past the end. Only then do we ask the repository
    to increment. Fetching the length from the curriculum keeps the cap correct even
    if tracks gain or lose modules over time.
    """
    valid_keys = set(TRACK_KEYS) | {"projects"}
    if key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown track '{key}'.",
        )

    tracks = {t.key: t for t in await curriculum_repo.get_all()}
    track = tracks.get(key)
    if track is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track '{key}' is not seeded in the database.",
        )

    return await progress_repo.advance_track(current_user.id, key, len(track.lessons))


@router.post("/reset", response_model=ProgressState)
async def reset_progress(
    current_user: UserInDB = Depends(get_current_user),
) -> ProgressState:
    """Wipe the user's progress back to a fresh day-1 document.

    Backs the "Reset all progress" button. Returns the new default state so the
    frontend can update its store from the response without a follow-up GET.
    """
    return await progress_repo.reset(current_user.id)
