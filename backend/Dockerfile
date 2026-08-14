# syntax=docker/dockerfile:1
#
# Backend image — FastAPI served by uvicorn.
# This image is tuned for DEV: source is bind-mounted over /app by docker-compose
# and uvicorn runs with --reload, so editing a .py file on the host restarts the
# server automatically. For production you would drop the bind mount and the
# --reload flag (see the README "future work" note).

FROM python:3.12-slim

# Keep Python predictable inside containers:
#   PYTHONDONTWRITEBYTECODE — don't litter the bind-mounted source with .pyc files
#   PYTHONUNBUFFERED       — flush stdout/stderr immediately so `docker logs` is live
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first, in their own layer. Because requirements.txt changes
# far less often than our source code, Docker can reuse this cached layer on most
# rebuilds and skip re-downloading everything.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code. In dev this is shadowed by the compose bind mount,
# but copying it keeps the image runnable on its own (e.g. `docker run`).
COPY . .

# Create and switch to a non-root user — a small but standard hardening step so a
# compromised process isn't running as root inside the container.
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# host 0.0.0.0 so the port is reachable from outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
