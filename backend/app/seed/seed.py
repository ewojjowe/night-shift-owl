"""Idempotent curriculum seeding, run once at application startup."""

import logging

from app.repositories import curriculum_repo
from app.seed.curriculum_data import build_curriculum

logger = logging.getLogger("uvicorn.error")


async def seed_curriculum_if_empty() -> None:
    """Populate the curriculum collection, but only if it's currently empty.

    "Idempotent" means running it repeatedly is safe: on every startup we check the
    document count first and return early if data already exists. That's why it can
    live in the startup hook — it won't duplicate tracks on the second, third, or
    hundredth boot, and it won't overwrite any edits made to the stored curriculum.
    """
    existing = await curriculum_repo.count()
    if existing > 0:
        logger.info("Curriculum already seeded (%d tracks) — skipping.", existing)
        return

    tracks = build_curriculum()
    await curriculum_repo.insert_tracks(tracks)
    logger.info("Seeded curriculum with %d tracks.", len(tracks))
