"""FastAPI application entry point.

This module wires the pieces together: it opens the database at startup, seeds the
curriculum, mounts the routers, and configures CORS so the Vue dev server may call
the API. Running ``uvicorn app.main:app`` (as the Dockerfile does) imports the
``app`` object defined here.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import close_mongo_connection, connect_to_mongo
from app.routers import auth, curriculum, progress
from app.seed.seed import seed_curriculum_if_empty


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Manage startup and shutdown work around the app's running lifetime.

    Everything before ``yield`` runs once when the server boots; everything after
    runs once when it stops. We connect to MongoDB and seed the curriculum on the
    way up, and close the connection on the way down. Using the lifespan context
    (rather than the older ``@app.on_event`` hooks) is the current FastAPI-endorsed
    pattern and guarantees the DB is ready before any request is served.
    """
    await connect_to_mongo()
    await seed_curriculum_if_empty()
    yield
    await close_mongo_connection()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance.

    A factory function (rather than configuring a module-level app inline) keeps
    setup in one readable place and makes it easy to spin up a fresh, independently
    configured app in tests. It attaches the lifespan handler, restricts CORS to the
    configured frontend origin, and registers each router.
    """
    settings = get_settings()
    app = FastAPI(
        title="Night Shift Learning Roadmap API",
        version="1.0.0",
        summary="Backend for the shift-aware self-paced learning tracker.",
        lifespan=lifespan,
    )

    # CORS: browsers block cross-origin API calls unless the server opts in. We
    # allow only the frontend origin from settings — not "*" — so a token can't be
    # replayed by an arbitrary site the user happens to visit.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(curriculum.router)
    app.include_router(progress.router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        """Lightweight liveness probe used by tooling and humans alike.

        Returns a tiny JSON payload without touching the database, so it stays fast
        and can't fail for a reason unrelated to the process being up. Handy for a
        quick ``curl`` check that the container is serving.
        """
        return {"status": "ok"}

    return app


# The ASGI application object uvicorn looks for (``app.main:app``).
app = create_app()
