"""Curriculum collection access: read the seeded tracks, and seed them once."""

from app.db import get_database
from app.models.curriculum import Track


async def count() -> int:
    """Return how many curriculum documents exist.

    The seeder uses this to decide whether seeding is needed — a count of zero
    means a fresh database, anything else means we've already populated it.
    """
    return await get_database().curriculum.count_documents({})


async def insert_tracks(tracks: list[Track]) -> None:
    """Bulk-insert curriculum tracks. Called only by the seeder on an empty DB.

    We convert each Pydantic ``Track`` to a plain dict for storage. A single
    ``insert_many`` is one round-trip for all tracks, which is both faster and
    tidier than inserting them one at a time.
    """
    docs = [track.model_dump() for track in tracks]
    if docs:
        await get_database().curriculum.insert_many(docs)


async def get_all() -> list[Track]:
    """Return every curriculum track, validated back into typed ``Track`` models.

    Results are sorted by ``key`` purely for a stable, predictable order in the API
    response (the frontend re-orders them for display anyway). The ``projection``
    hides Mongo's internal ``_id`` so the payload matches the ``Track`` schema
    exactly and Pydantic doesn't have to ignore an extra field.
    """
    cursor = get_database().curriculum.find({}, {"_id": 0}).sort("key", 1)
    docs = await cursor.to_list(length=None)
    return [Track(**doc) for doc in docs]
