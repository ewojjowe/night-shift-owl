# Deployment & Release Guide — Night Shift Learning Roadmap

Production deployment, operations, and release checklist for the app. The entire stack
runs on **Render + MongoDB Atlas**: frontend as a **Render Static Site**, backend as a
**Render Web Service**, and database on **MongoDB Atlas (free tier)**.

> **The key idea:** everything lives on one platform (Render) plus a managed database
> (Atlas). One dashboard for deploys, rollbacks, logs, and env vars. No servers to
> provision, no TLS certificates to wrangle, no Docker Compose in production.

---

## Table of contents

1. [Architecture](#1-architecture)
2. [MongoDB Atlas setup (free tier)](#2-mongodb-atlas-setup-free-tier)
3. [Render setup](#3-render-setup)
4. [Environment variable audit](#4-environment-variable-audit)
5. [Safe database migration runbook](#5-safe-database-migration-runbook)
6. [Preview deployments (test before promoting)](#6-preview-deployments)
7. [Quick rollback](#7-quick-rollback)
8. [HTTPS/TLS termination](#8-httpstls-termination)
9. [JWT refresh-token rotation](#9-jwt-refresh-token-rotation)
10. [Release checklist](#10-release-checklist)

---

## 1. Architecture

```
   Browser
      │
      │  HTTPS (Render-managed certs for both)
      ▼
┌───────────────────────────────────────────────────────┐
│                    Render                             │
│                                                       │
│  ┌─────────────────┐       ┌──────────────────────┐   │
│  │  Static Site    │       │  Web Service         │   │
│  │  Vue 3 + Vite   │──────▶│  FastAPI (Docker)    │   │
│  │                 │ JSON  │                      │   │
│  └─────────────────┘ +JWT  └──────────┬───────────┘   │
│                                       │               │
└───────────────────────────────────────┼───────────────┘
                                        │ mongodb+srv://
                                        │ (TLS by default)
                               ┌────────▼─────────┐
                               │  MongoDB Atlas   │
                               │  (M0 free tier)  │
                               └──────────────────┘
```

- **Frontend → Render Static Site.** Builds `night-shift-app/frontend` with Vite,
  serves the `dist/` output. Render handles SPA routing (rewrite rules configured
  during setup).
- **Backend → Render Web Service.** Builds and runs the existing
  [`backend/Dockerfile`](backend/Dockerfile). TLS, health checks, and zero-downtime
  deploys are handled automatically.
- **Database → MongoDB Atlas.** A free M0 cluster (512 MB) with built-in auth, TLS,
  and a `mongodb+srv://` connection string.

Both Render services deploy from the **same Git repo** — just different root
directories and service types.

**Alternatives:**

| Option | Notes |
|--------|-------|
| **Render** (this guide) | Frontend + backend on one platform; free tier available. |
| **Railway** | Deploys a Dockerfile; managed TLS + managed Mongo add-on. |
| **Fly.io** | Runs the container close to users; managed TLS. |
| **Vercel + Render** | Frontend on Vercel (static), backend on Render. The repo includes a [`vercel.json`](frontend/vercel.json) for this path. |
| **Self-host on a VM** | Full control; you run `docker compose` with the production [`docker-compose.yml`](docker-compose.yml) + [`Caddyfile`](Caddyfile) included in the repo. Most ops work. |
| MongoDB Atlas M2+ | Automated backups, performance advisor, larger storage. |

---

## 2. MongoDB Atlas setup (free tier)

### 2.1 Create a free cluster

1. Sign up at [cloud.mongodb.com](https://cloud.mongodb.com).
2. **Create a Cluster** → select the **M0 (Free)** tier → choose the cloud provider
   and region closest to your Render service (e.g. AWS us-east-1 if Render is in
   Oregon).
3. Wait for the cluster to provision (~1–3 minutes).

### 2.2 Create a database user

1. **Database Access** → **Add New Database User**.
2. Authentication: **Password**.
3. Username: `appuser` (or whatever you prefer).
4. Password: generate a strong random one — you'll paste this into the connection string.
5. **Database User Privileges** → **Specific Privilege** → add `readWrite` on
   database `night_shift`. This is least-privilege: the app can read and write its
   own database, nothing else.

### 2.3 Network access

1. **Network Access** → **Add IP Address**.
2. For the free tier, the simplest approach is **Allow Access from Anywhere**
   (`0.0.0.0/0`). This is safe because Atlas **always requires authentication** — the
   connection string includes credentials, and TLS is enforced. No anonymous access is
   possible.
   - If you want tighter restrictions: Render publishes [static outbound IPs](https://docs.render.com/static-outbound-ip-addresses)
     for paid plans. Add only those IPs for a defense-in-depth layer.

### 2.4 Get the connection string

1. **Database** → **Connect** → **Drivers** → copy the `mongodb+srv://` connection
   string.
2. Replace `<password>` with the database user's password and append the database name:
   ```
   mongodb+srv://appuser:<password>@cluster0.xxxxx.mongodb.net/night_shift?retryWrites=true&w=majority
   ```
3. This string goes into Render as the `MONGO_URI` environment variable (§4).

### 2.5 Backups

**Free tier (M0) caveat:** Atlas M0 does **not** include automated backups. Options:

- **Manual `mongodump`:** install the MongoDB Database Tools locally and run:
  ```bash
  mongodump --uri="mongodb+srv://appuser:<password>@cluster0.xxxxx.mongodb.net/night_shift" \
    --archive --gzip > "night_shift_$(date +%F).gz"
  ```
  Do this before any migration or when you have data you can't afford to lose.
- **Upgrade to M2+ ($9/mo):** enables Atlas automated daily snapshots with
  point-in-time restore. Worth it once you have real users.

**Restore** (from a manual dump):
```bash
mongorestore --uri="mongodb+srv://appuser:<password>@cluster0.xxxxx.mongodb.net/night_shift" \
  --archive --gzip --drop < night_shift_2026-08-14.gz
```

---

## 3. Render setup

### 3.1 Backend — Web Service

1. **Render dashboard** → **New** → **Web Service**.
2. Connect your Git repo.
3. Settings:
   - **Name:** `night-shift-backend`
   - **Root Directory:** `night-shift-app/backend`
   - **Runtime:** **Docker** (Render detects the Dockerfile automatically)
   - **Instance Type:** **Free** (or Starter for always-on)
   - **Branch:** `main`
4. Add environment variables (§4) — at minimum `MONGO_URI`, `JWT_ACCESS_SECRET`,
   `JWT_REFRESH_SECRET`, and `CORS_ORIGINS`.
5. **Create Web Service** → Render builds and deploys. Note the URL
   (e.g. `https://night-shift-backend.onrender.com`).

> **Free tier caveat:** Render free Web Services spin down after 15 minutes of
> inactivity and take ~30–60 seconds to cold-start on the next request. Upgrade to
> Starter ($7/mo) for always-on.

### 3.2 Frontend — Static Site

1. **Render dashboard** → **New** → **Static Site**.
2. Connect the same Git repo.
3. Settings:
   - **Name:** `night-shift-app`
   - **Root Directory:** `night-shift-app/frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
   - **Branch:** `main`
4. Add environment variable:
   - `VITE_API_BASE` = `https://night-shift-backend.onrender.com` (the backend URL
     from step 3.1)
5. **Rewrite Rules** (for SPA routing — so client-side routes like `/login` work on
   direct hits and refreshes):
   - **Source:** `/*`
   - **Destination:** `/index.html`
   - **Action:** **Rewrite**
6. **Create Static Site** → Render builds the Vite app and serves it.

### 3.3 Infrastructure as Code (optional)

Instead of clicking through the dashboard, create a `render.yaml` in the repo root:

```yaml
services:
  - type: web
    name: night-shift-backend
    runtime: docker
    rootDir: night-shift-app/backend
    envVars:
      - key: MONGO_URI
        sync: false  # set manually in dashboard — it's a secret
      - key: JWT_ACCESS_SECRET
        sync: false
      - key: JWT_REFRESH_SECRET
        sync: false
      - key: ACCESS_EXPIRE_MINUTES
        value: "15"
      - key: REFRESH_EXPIRE_DAYS
        value: "7"
      - key: CORS_ORIGINS
        value: '["https://night-shift-app.onrender.com"]'

  - type: web
    plan: free
    name: night-shift-app
    buildCommand: npm install && npm run build
    staticPublishPath: dist
    rootDir: night-shift-app/frontend
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
    envVars:
      - key: VITE_API_BASE
        value: https://night-shift-backend.onrender.com
```

Then: **Render dashboard** → **Blueprints** → connect the repo → Render creates both
services from the YAML.

---

## 4. Environment variable audit

**The rule:** all production variables live in the **Render dashboard** — backend
secrets on the Web Service, the one public frontend variable on the Static Site.

### 4.1 Inventory

| Variable | Used by | Secret? | Render service | Rotation |
|----------|---------|:------:|----------------|----------|
| `VITE_API_BASE` | Frontend (build-time, **public**) | No | **Static Site** | Change + rebuild |
| `MONGO_URI` | Backend | **Yes** | **Web Service** | Rotate Atlas password, update, redeploy |
| `JWT_ACCESS_SECRET` | Backend | **Yes** | **Web Service** | Rotate → invalidates live access tokens (users silently refresh) |
| `JWT_REFRESH_SECRET` | Backend | **Yes** | **Web Service** | Rotate → invalidates all refresh tokens (forces re-login) |
| `ACCESS_EXPIRE_MINUTES` | Backend | No | **Web Service** | Edit + redeploy |
| `REFRESH_EXPIRE_DAYS` | Backend | No | **Web Service** | Edit + redeploy |
| `CORS_ORIGINS` | Backend | No | **Web Service** | Edit + redeploy |

`CORS_ORIGINS` must include the Static Site's HTTPS URL (e.g.
`["https://night-shift-app.onrender.com"]`).

Variables from the self-hosted topology that are **not needed**: `MONGO_ROOT_USER`,
`MONGO_ROOT_PASSWORD` (Atlas manages DB auth), `API_DOMAIN`, `ACME_EMAIL` (Render
manages TLS), `IMAGE_TAG` (Render manages deploys).

### 4.2 Audit / drift check

`.env` is git-ignored ([`.gitignore`](.gitignore)); `.env.example` is the committed
source of truth for dev. Before a release, check the Render dashboard's Environment
tabs for both services — or diff against `render.yaml` if you use Infrastructure as
Code.

---

## 5. Safe database migration runbook

MongoDB is schemaless, so "migrations" mean **index changes** and **data backfills**.
The rule that keeps the live site up is **expand → migrate → contract**: never make a
change the currently-running code can't tolerate.

> **Why this is safe with rollback (§7):** because each step keeps old and new code
> working against the same data, you can roll the app back at any point without the
> database being "ahead" of the code.

### The workflow

1. **Back up first** (§2.5). Always. `mongodump` before any schema change (or use
   Atlas snapshots if on a paid tier).
2. **Expand (additive only).** Deploy code that *adds* — a new optional field, a new
   collection, a new index — while still reading/writing the old shape. New fields are
   optional/defaulted (our Pydantic models already default new fields, so old
   documents validate). **Never** rename or drop in this step.
3. **Build indexes without blocking.** Create new indexes in the background so writes
   aren't locked on a live DB. Connect to Atlas via `mongosh`:
   ```javascript
   // mongosh "mongodb+srv://appuser:<password>@cluster0.xxxxx.mongodb.net/night_shift"
   db.refresh_tokens.createIndex({ token_hash: 1 }, { unique: true })
   ```
   (Our app also creates indexes at startup — that is *additive-only* and safe.
   Destructive index changes are done here, by hand, not at startup.)
4. **Backfill idempotently.** If existing documents need the new field populated, run
   a one-off script that can be re-run safely (only touches docs missing the field):
   ```javascript
   db.users.updateMany({ new_field: { $exists: false } }, { $set: { new_field: "default" } })
   ```
5. **Verify.** Counts match, the app reads/writes both shapes, no error-rate spike.
6. **Contract (only after new code is fully deployed & stable).** Now remove the old
   field / drop the old index / delete dead code — in a *later* release. By the time
   you contract, nothing reads the old shape.

**Rollback per step:** steps 1–5 are reversible by rolling back on Render. Only step 6
is one-way — which is why it's a separate, later release you do only once the new
version has proven stable.

---

## 6. Preview deployments

Both Render services auto-deploy when you push to `main`. To test changes before they
hit production, use **pull request previews** or a **staging branch**.

### Render pull request previews

Render can automatically deploy a preview of your Web Service for every pull request:

1. **Web Service** → **Settings** → **Pull Request Previews** → **Enable**.
2. Each PR gets a temporary URL (e.g. `https://night-shift-backend-pr-42.onrender.com`).
3. For the Static Site, create a matching preview with the PR's backend URL as
   `VITE_API_BASE`.

### Staging branch alternative

Create a second pair of Render services (`night-shift-backend-staging` and
`night-shift-app-staging`) watching a `staging` branch, pointed at a separate Atlas
database. Push to `staging` to test, merge to `main` to promote.

### Smoke-test checklist (run on the preview URL before promoting)

- [ ] App loads over HTTPS; no console errors.
- [ ] **Register** a throwaway account → lands on dashboard.
- [ ] **Login / logout** work; logout returns you to `/login`.
- [ ] **Refresh flow:** stay idle past `ACCESS_EXPIRE_MINUTES` (or temporarily set it
      to 1) then do an action → it succeeds *without* a visible logout (silent
      refresh), and network shows a `POST /auth/refresh`.
- [ ] **Progress persists:** complete a module, reload, re-login → still there.
- [ ] **CORS:** requests to the backend succeed (origin allowed in `CORS_ORIGINS`).
- [ ] Direct-hit a client route (e.g. `/register`) and refresh → no 404 (SPA rewrite).

---

## 7. Quick rollback

### Frontend (Static Site) — redeploy previous build

1. Render dashboard → your Static Site → **Deploys**.
2. Find the last known-good deploy → **Roll Back**. Render re-publishes that build
   immediately.

### Backend (Web Service) — one click

1. Render dashboard → your Web Service → **Deploys**.
2. Find the last known-good deploy → **Roll Back**. Render redeploys that exact build
   with zero downtime.
3. Alternatively, revert the commit in Git and push — Render auto-deploys the revert.

### Database caveat

Rollback is safe **because migrations are expand/contract (§5)**: the previous code
version still works against the current schema, since you never dropped anything the
old code needs until a later, separate release. If you ever must undo a destructive
change, restore from backup (§2.5).

---

## 8. HTTPS/TLS termination

All three layers handle TLS automatically — there is nothing to configure:

- **Frontend (Render Static Site):** TLS is **fully automatic** — Render provisions
  and renews certificates for `*.onrender.com` subdomains and any custom domain you
  add. HTTPS is enforced.
- **Backend (Render Web Service):** Same — automatic TLS for the `*.onrender.com`
  subdomain and custom domains. HTTP requests are redirected to HTTPS.
- **Database (Atlas):** connections via `mongodb+srv://` use **TLS by default**. Atlas
  requires TLS for all connections — no cleartext option exists.

The backend `CORS_ORIGINS` must list the Static Site's **HTTPS** URL so the browser
allows the cross-origin API calls.

> **Self-hosted alternative:** if you run the backend on your own VM instead of Render,
> the repo includes a production [`docker-compose.yml`](docker-compose.yml) and
> [`Caddyfile`](Caddyfile) that terminate TLS via Caddy + Let's Encrypt automatically.

---

## 9. JWT refresh-token rotation

Implemented in the backend and frontend. The design:

| Token | Lifetime | Form | Stored server-side? | Revocable? |
|-------|----------|------|:-------------------:|:----------:|
| **Access** | ~15 min (`ACCESS_EXPIRE_MINUTES`) | Signed JWT | No (stateless) | No — kept short instead |
| **Refresh** | ~7 days (`REFRESH_EXPIRE_DAYS`) | Opaque random string | Yes (**hashed**) | **Yes** |

**Rotation + reuse detection** (in [`routers/auth.py`](backend/app/routers/auth.py)
`refresh`, backed by [`refresh_token_repo.py`](backend/app/repositories/refresh_token_repo.py)):

- Each login/register starts a refresh-token **family**.
- Every call to `POST /auth/refresh` issues a **new** pair and **revokes** the old
  refresh token (rotation) — a refresh token is single-use.
- If an **already-revoked** refresh token is presented, that's a replay (likely
  theft): the backend **revokes the entire family**, forcing a fresh login and
  locking out the attacker. This is the industry-standard *refresh token rotation
  with reuse detection* pattern.
- Refresh tokens are stored only as an **HMAC-SHA256 hash** (keyed with
  `JWT_REFRESH_SECRET`), so a database leak yields no usable tokens.
- A **TTL index** on `expires_at` ([`db.py`](backend/app/db.py)) auto-purges expired
  records — no cleanup job.
- `POST /auth/logout` revokes the presented refresh token immediately.

**Client side** ([`api/client.ts`](frontend/src/api/client.ts),
[`stores/auth.ts`](frontend/src/stores/auth.ts)): on any `401`, a **single** silent
`POST /auth/refresh` runs (concurrent 401s share one refresh), then the original
request retries with the new access token — so a short access lifetime is invisible to
the user. If refresh fails, the session is cleared and the router sends them to login.

### Recommended hardening (documented, not yet wired)

Today both tokens are returned in the JSON body and the client keeps them in
`localStorage` — convenient, and rotation/revocation already limit the blast radius,
but `localStorage` is readable by any injected script (XSS). To remove the refresh
token from JavaScript entirely:

- Have the backend set the refresh token as an **`httpOnly; Secure; SameSite=None`
  cookie** instead of returning it in the body (`SameSite=None` because the frontend
  and API are on different Render subdomains; `Secure` so it's HTTPS-only).
- Enable **credentialed CORS**: `allow_credentials=True` with `CORS_ORIGINS` locked to
  the exact Static Site origin (never `*`), and have the frontend send `credentials:
  "include"`.
- Keep the **access** token in memory only (not localStorage).

This is a self-contained change to token *delivery/storage* — the rotation, reuse
detection, and revocation logic stay exactly as they are.

---

## 10. Release checklist

**Pre-deploy**
- [ ] Backend tests / smoke pass locally (`docker compose -f dev-docker-compose.yml up`).
- [ ] Env audit (§4): required secrets present on both Render services.
- [ ] If schema changes: migration is **expand-only** this release (§5); backup taken (§2.5).

**Deploy**
- [ ] Push to `main` → both Render services auto-build and deploy.
- [ ] Backend `/health` returns ok.
- [ ] Frontend loads at the Static Site URL.

**Post-deploy**
- [ ] Run the §6 smoke checklist against production (register/login/refresh/persist/logout).
- [ ] Watch Render logs for errors (Dashboard → Web Service → Logs).

**If something breaks → Rollback (§7)**
- [ ] Frontend: Roll Back the Static Site deploy on Render.
- [ ] Backend: Roll Back the Web Service deploy on Render.
- [ ] Only if a destructive migration was involved: restore from backup (§2.5).
