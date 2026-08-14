# syntax=docker/dockerfile:1
#
# Frontend image — Vite dev server for the Vue app.
# Like the backend image this targets DEV: docker-compose bind-mounts the source
# over /app so edits hot-reload, and keeps node_modules in a container-only volume
# (so the host's OS/arch doesn't clash with installed native binaries).

FROM node:20-alpine

WORKDIR /app

# Install dependencies in their own cached layer. Copying only the manifest first
# means `npm install` re-runs only when dependencies actually change, not on every
# source edit.
COPY package.json ./
RUN npm install

# Copy the rest of the source. In dev this is shadowed by the compose bind mount.
COPY . .

EXPOSE 5173

# --host is set in the npm script so the dev server binds to 0.0.0.0 and is
# reachable from the host browser.
CMD ["npm", "run", "dev"]
