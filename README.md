# Night Shift Owl

A shift-aware, self-paced study tracker. The original was a single HTML file that
saved everything in the browser. This version gives it **real user accounts**,
**server-side persistence in MongoDB**, and a **database-backed curriculum**, split
into a FastAPI backend and a Vue 3 frontend, all runnable with one command.

---

## What it does

- **Rotating weekly curriculum** — one Math problem, one DSA problem, and one main
  topic per day. The main topic rotates by weekday (Python Mon, AI/ML Tue, Go Wed,
  System Design Thu, AI Engineering Fri), with Saturday for a deep-dive review and
  Sunday for projects.
- **Shift-aware daily timeline** — you enter your weekly shift schedule; the app
  lays out each day (sleep, gym, study, etc.) into the free window around your
  shift, stretching the study block to fit.
- **Progress tracking** — reveal a module, mark it complete, and watch the roadmap
  and completion % advance. Everything is saved to your account, not the browser.

---

## Architecture

```
┌────────────┐      HTTP + JWT       ┌────────────┐     Motor (async)   ┌──────────┐
│  Frontend  │  ──────────────────▶  │  Backend   │  ────────────────▶  │ MongoDB  │
│ Vue 3 + TS │  ◀──────────────────  │  FastAPI   │  ◀────────────────  │          │
│ Pinia/Vite │      JSON responses   │  Pydantic  │     documents       │          │
└────────────┘                       └────────────┘                     └──────────┘
   :5173                                 :8000                              :27017
```

- **Frontend** (`night-shift-app/frontend`) — Vue 3 + TypeScript + Pinia + Vue
  Router, served by the Vite dev server. The shift-timeline maths lives here
  (`src/lib/timeline.ts`) because it is pure presentation derived from saved config.
- **Backend** (`night-shift-app/backend`) — FastAPI + Pydantic v2, talking to Mongo
  through the async Motor driver. Auth is JWT-based (bcrypt-hashed passwords).
- **Database** — MongoDB with three collections: `users`, `progress`, `curriculum`.

### Layered backend (endpoints separated from data access)

The backend keeps "how we answer a request" apart from "how we read/write data":

| Layer | Folder | Responsibility |
|-------|--------|----------------|
| Routers | `app/routers/` | HTTP endpoints; validate input, shape output. **No DB code.** |
| Repositories | `app/repositories/` | The **only** code that queries MongoDB. |
| Models | `app/models/` | Pydantic schemas for every payload. |
| Security / deps | `app/security.py`, `app/dependencies.py` | Hashing, JWTs, "who is logged in?". |
| Seed | `app/seed/` | Curriculum data + idempotent seeding. |

---

## Quickstart

**Prerequisite:** Docker Desktop (or Docker Engine + the Compose plugin).

For **local development**, use the dev compose file (hot-reload, local Mongo, Vite
dev server, zero config):

```bash
cd night-shift-app
docker compose -f dev-docker-compose.yml up --build
```

Then open:

- **App:** http://localhost:5173 — register an account and start.
- **API docs (Swagger):** http://localhost:8000/docs — try every endpoint live.

To stop: `Ctrl-C`, then `docker compose -f dev-docker-compose.yml down` (add `-v` to
also wipe the database volume). Editing any backend `.py` or frontend source file
hot-reloads the running container — no rebuild needed.

> **Production is different.** The default [`docker-compose.yml`](night-shift-app/docker-compose.yml)
> is the *production* stack (MongoDB auth + Caddy TLS, no frontend — Vercel serves it)
> and requires real secrets. See **[DEPLOYMENT.md](night-shift-app/DEPLOYMENT.md)** for
> the full production deploy + release guide.

Optionally copy `.env.example` to `.env` to override dev settings (see below). It is
optional for local dev; every value has a working default.

---

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `MONGO_URI` | `mongodb://mongo:27017` | MongoDB connection string (authenticated in prod). |
| `MONGO_DB_NAME` | `night_shift` | Database name. |
| `JWT_ACCESS_SECRET` | `dev-only-…` | Signs short-lived access JWTs — **change for real use.** |
| `JWT_REFRESH_SECRET` | `dev-only-…` | HMAC pepper for hashing refresh tokens — **change for real use.** |
| `ACCESS_EXPIRE_MINUTES` | `15` | Access-token lifetime (silently refreshed). |
| `REFRESH_EXPIRE_DAYS` | `7` | Refresh-token lifetime (rotated per use, revocable). |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | JSON array of allowed browser origins. |
| `VITE_API_BASE` | `http://localhost:8000` | Where the browser calls the API. |

Production adds `MONGO_ROOT_USER/PASSWORD`, `API_DOMAIN`, `ACME_EMAIL`, and
`IMAGE_TAG` — see [`.env.example`](night-shift-app/.env.example) and
[DEPLOYMENT.md](night-shift-app/DEPLOYMENT.md).

---

## API reference

All routes except register/login/refresh require an `Authorization: Bearer <token>` header.

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/auth/register` | Create an account, returns an access + refresh token pair. |
| `POST` | `/auth/login` | Log in, returns an access + refresh token pair. |
| `POST` | `/auth/refresh` | Exchange a refresh token for a new pair (rotation + reuse detection). |
| `POST` | `/auth/logout` | Revoke the presented refresh token. |
| `GET` | `/auth/me` | The current user's profile. |
| `GET` | `/curriculum` | All tracks + projects (from the DB). |
| `GET` | `/progress` | The current user's progress (auto-created on first call). |
| `PUT` | `/progress` | Update shift schedule / off-day defaults / overrides / UI state. |
| `PATCH` | `/progress/tracks/{key}/complete` | Advance one track (or `projects`) by one module. |
| `POST` | `/progress/reset` | Reset progress to day 1. |
| `GET` | `/health` | Liveness probe. |

---

## Where to look (a guided tour)

New to the codebase? Read it in this order — every function has a docstring
explaining *what it does and why*, so the code is meant to be read, not just run.

**Backend**
1. `backend/app/config.py` — how settings load from the environment.
2. `backend/app/db.py` — the single MongoDB connection + indexes.
3. `backend/app/models/` — the shapes of all data (`progress.py` is the interesting one).
4. `backend/app/security.py` + `dependencies.py` — password hashing, JWTs, the auth gate.
5. `backend/app/repositories/` — every database query, one file per collection.
6. `backend/app/routers/` — the endpoints; see how thin they stay by delegating to repositories.
7. `backend/app/seed/curriculum_data.py` — the ported curriculum; `seed.py` writes it once.
8. `backend/app/main.py` — where it's all wired together.

**Frontend**
1. `frontend/src/api/client.ts` — the one place HTTP happens.
2. `frontend/src/stores/` — Pinia state: `auth`, `curriculum`, `progress`.
3. `frontend/src/lib/timeline.ts` — the shift-timeline engine (ported verbatim).
4. `frontend/src/router/index.ts` — routing + the auth guard.
5. `frontend/src/views/` then `components/` — the login pages and the dashboard UI.

---

## Verifying it works end-to-end

1. `docker compose -f dev-docker-compose.yml up --build` — all three services start;
   `mongo` becomes healthy before `backend` boots.
2. Visit http://localhost:8000/docs and call `GET /curriculum` (after authorizing) —
   it returns the seeded tracks, confirming curriculum seeding.
3. Register at http://localhost:5173 → you land on the dashboard.
4. Reveal a lesson and mark it complete, then **refresh / log out and back in** — the
   progress is still there (persisted server-side, not in the browser).
5. Register a *second* account — it starts fresh at day 1, proving per-user isolation.
6. Edit your shift schedule → the timeline updates and the change survives a reload.
7. Click **Reset all progress** twice → back to day 1 / 0%.

---

## Production deployment

Deploying to production — frontend and backend both on **Render**, database on
**MongoDB Atlas** (free tier) — is covered end-to-end in
**[DEPLOYMENT.md](night-shift-app/DEPLOYMENT.md)**: Render setup for both services, the
environment-variable audit, the safe expand/contract migration runbook, preview testing,
quick rollback, and a release checklist. All three layers handle HTTPS/TLS automatically.

**Already implemented for production readiness:** **JWT refresh tokens with rotation +
reuse detection** (`/auth/refresh`, `/auth/logout`), and a hardened production
[`docker-compose.yml`](night-shift-app/docker-compose.yml) +
[`Caddyfile`](night-shift-app/Caddyfile) for self-hosted deployment as an alternative.

Still worth adding later: rate limiting on auth endpoints, and moving the refresh
token into an httpOnly cookie (the recommended hardening documented in DEPLOYMENT.md).
