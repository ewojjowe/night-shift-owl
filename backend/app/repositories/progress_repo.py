"""Progress collection access: one document per user, read and mutated here.

The document stored in Mongo is a ``ProgressState`` dumped to a dict plus a
``user_id`` field that links it to the owner. These helpers translate between that
stored form and the typed model, and enforce the rules that progress may only
advance through ``advance_track`` (never by arbitrary edits).
"""

from datetime import date

from app.db import get_database
from app.models.progress import (
    TRACK_KEYS,
    OffDayDefaults,
    ProgressState,
    ProgressUpdate,
    ShiftDay,
    TrackProgress,
)


def build_default_progress() -> ProgressState:
    """Construct the starting progress document for a brand-new user.

    This is the Python twin of the original page's ``defaultState()``: day 1, every
    track at index 0, and a Monday–Friday night-shift template (free 08:00, back by
    22:00) with weekends off. Building it in code — rather than storing a template in
    the DB — keeps "what a fresh account looks like" versioned alongside the schema.
    """
    shift_template = {
        str(d): ShiftDay(working=1 <= d <= 5, shift_end="08:00", shift_start="22:00")
        for d in range(7)  # 0=Sunday .. 6=Saturday, matching JS getDay()
    }
    return ProgressState(
        start_date=date.today().isoformat(),
        tracks={key: TrackProgress(idx=0) for key in TRACK_KEYS},
        projects=TrackProgress(idx=0),
        shift_template=shift_template,
        off_day_defaults=OffDayDefaults(),
        shift_overrides={},
    )


def _to_state(doc: dict) -> ProgressState:
    """Rebuild a typed ``ProgressState`` from a stored Mongo document.

    We drop the storage-only fields (``_id`` and ``user_id``) and let Pydantic
    re-validate the rest. Re-validating on read is a cheap safety net: if an older
    document is missing a newer field, model defaults fill the gap instead of the
    frontend receiving a half-formed object.
    """
    data = {k: v for k, v in doc.items() if k not in ("_id", "user_id")}
    return ProgressState(**data)


async def get_or_create(user_id: str) -> ProgressState:
    """Return a user's progress, creating the default document on first access.

    New users never have to be given a progress row at registration time — the
    first ``GET /progress`` lazily creates it. This keeps registration simple and
    means the two operations can't get out of sync.
    """
    collection = get_database().progress
    doc = await collection.find_one({"user_id": user_id})
    if doc:
        return _to_state(doc)

    state = build_default_progress()
    await collection.insert_one({"user_id": user_id, **state.model_dump()})
    return state


async def update(user_id: str, changes: ProgressUpdate) -> ProgressState:
    """Apply a partial config update (shift schedule, defaults, UI state) and return it.

    Only the fields the client actually sent are written — ``exclude_none`` drops
    the untouched ones — so a request that only toggles a UI section doesn't
    clobber the shift schedule. ``$set`` with ``return_document=AFTER`` updates and
    reads back in a single atomic round-trip. The progress row is created first if
    it somehow doesn't exist yet, so this is always safe to call.
    """
    from pymongo import ReturnDocument

    await get_or_create(user_id)  # guarantee the document exists
    patch = changes.model_dump(exclude_none=True)
    doc = await get_database().progress.find_one_and_update(
        {"user_id": user_id},
        {"$set": patch},
        return_document=ReturnDocument.AFTER,
    )
    return _to_state(doc)


async def advance_track(user_id: str, key: str, track_length: int) -> ProgressState:
    """Increment one track's (or the projects') index, capped at the track length.

    This is the *only* way progress moves forward — the "Mark complete" button.
    ``key`` is either a track key like ``"python"`` (stored under ``tracks.<key>``)
    or the literal ``"projects"`` (stored at the top level), so we build the dotted
    field path accordingly. Reading the current value, capping, and writing happen
    against the freshly fetched state so we never advance past the last module.
    """
    from pymongo import ReturnDocument

    state = await get_or_create(user_id)
    if key == "projects":
        field = "projects.idx"
        current = state.projects.idx
    else:
        field = f"tracks.{key}.idx"
        current = state.tracks[key].idx

    new_idx = min(current + 1, track_length)
    doc = await get_database().progress.find_one_and_update(
        {"user_id": user_id},
        {"$set": {field: new_idx}},
        return_document=ReturnDocument.AFTER,
    )
    return _to_state(doc)


async def reset(user_id: str) -> ProgressState:
    """Replace a user's progress with a fresh default document.

    Backs the "Reset all progress" button. We overwrite the whole document (rather
    than nudging fields) so no stale overrides or counters can survive a reset, and
    keep the same ``user_id`` link so the row stays owned by the same account.
    """
    state = build_default_progress()
    await get_database().progress.replace_one(
        {"user_id": user_id},
        {"user_id": user_id, **state.model_dump()},
        upsert=True,
    )
    return state
