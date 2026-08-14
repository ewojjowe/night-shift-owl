"""Night Shift Learning Roadmap — FastAPI backend package.

This package is organized into clear layers so responsibilities never blur:

* ``config``       — typed application settings loaded from the environment.
* ``db``           — the MongoDB connection and collection accessors.
* ``security``     — password hashing and JWT creation/verification.
* ``dependencies`` — reusable FastAPI dependencies (e.g. "who is logged in?").
* ``models``       — Pydantic schemas describing the shape of every payload.
* ``repositories`` — the ONLY code allowed to talk to MongoDB (data access).
* ``routers``      — HTTP endpoints; they validate input and call repositories.
* ``seed``         — the curriculum data and an idempotent seeding routine.

Keeping "how we answer a request" (routers) apart from "how we read/write data"
(repositories) is the separation the project brief asked for: you can change the
database layer without touching endpoints, and vice versa.
"""
