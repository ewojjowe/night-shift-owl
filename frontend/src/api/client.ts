/**
 * A tiny fetch wrapper — the single choke-point for every call to the backend.
 *
 * Centralising HTTP here means three concerns are handled in exactly one place:
 *  1. the base URL (configurable via VITE_API_BASE),
 *  2. attaching the JWT to every request, and
 *  3. turning non-2xx responses into thrown errors with a useful message.
 *
 * Components and stores call `api.get/post/...` and never touch `fetch` directly.
 */

// Where the backend lives. In Docker the browser reaches it on the published
// localhost:8000 port; override with VITE_API_BASE for other environments.
const BASE_URL = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// The in-memory access token. Kept module-private and mutated only through
// setToken() so there's no way for scattered code to get out of sync.
let authToken: string | null = null;

/**
 * Store (or clear) the JWT used for subsequent requests.
 *
 * The auth store calls this after login/register (with a token) and on logout
 * (with null). Persisting the token to localStorage is the store's job; this
 * module only cares about the value to send on the wire.
 */
export function setToken(token: string | null): void {
  authToken = token;
}

// A callback the auth store registers to perform a silent token refresh. Keeping
// it as an injected function (rather than importing the store here) avoids a
// circular import — the store imports this module, not the other way around.
// It resolves to true if a new access token was obtained, false otherwise.
let refreshHandler: (() => Promise<boolean>) | null = null;

// Ensures only ONE refresh runs at a time: if several requests 401 at once, they
// all await this single in-flight promise instead of each firing their own
// /auth/refresh (which — because refresh rotates — would invalidate each other).
let refreshInFlight: Promise<boolean> | null = null;

// Auth endpoints must never trigger the refresh-and-retry loop: a 401 from login/
// register/refresh is a genuine failure, not an expired access token.
const AUTH_PATHS = ["/auth/login", "/auth/register", "/auth/refresh"];

/**
 * Register the store's refresh routine so the client can recover from a 401.
 *
 * Called once when the auth store initialises. The client stays ignorant of *how*
 * refreshing works (that's the store's job); it only needs something to call.
 */
export function setRefreshHandler(fn: (() => Promise<boolean>) | null): void {
  refreshHandler = fn;
}

/**
 * Run the registered refresh handler, collapsing concurrent callers into one run.
 *
 * The first caller starts the refresh and stores its promise; everyone else awaits
 * the same promise. The `finally` clears the slot so a later expiry can refresh
 * again. Returns false if no handler is registered (e.g. before login).
 */
function runRefresh(): Promise<boolean> {
  if (!refreshHandler) return Promise.resolve(false);
  if (!refreshInFlight) {
    refreshInFlight = refreshHandler().finally(() => {
      refreshInFlight = null;
    });
  }
  return refreshInFlight;
}

/**
 * Fire a single HTTP request and return the raw `Response`.
 *
 * Split out from `request` so the same call can be issued twice — once normally,
 * and once again after a silent refresh — without duplicating header/body setup.
 */
async function rawFetch(
  method: string,
  path: string,
  body?: unknown,
): Promise<Response> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  return fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

/**
 * Decode a response body, or throw an Error carrying the backend's message.
 *
 * A 204 yields `undefined`, a 2xx yields the decoded JSON, and anything else
 * throws with FastAPI's `detail` string (falling back to a generic message) so the
 * UI has something meaningful to show.
 */
async function parse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T;
  }
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message =
      (data && (data.detail as string)) || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return data as T;
}

/**
 * Perform a request, transparently refreshing the access token on a 401.
 *
 * The happy path is one `rawFetch` + `parse`. If the access token has expired the
 * server replies 401; we then run a single silent refresh (shared across any
 * concurrent 401s) and, if it succeeds, retry the original request exactly once
 * with the new token. This is what lets a short-lived access token feel seamless.
 * Auth endpoints are excluded so a real credential failure surfaces immediately.
 */
async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  let response = await rawFetch(method, path, body);

  if (response.status === 401 && !AUTH_PATHS.includes(path)) {
    const refreshed = await runRefresh();
    if (refreshed) {
      response = await rawFetch(method, path, body);
    }
  }

  return parse<T>(response);
}

/** Convenience methods so callers read as `api.get(...)`, `api.post(...)`, etc. */
export const api = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body?: unknown) => request<T>("POST", path, body),
  put: <T>(path: string, body?: unknown) => request<T>("PUT", path, body),
  patch: <T>(path: string, body?: unknown) => request<T>("PATCH", path, body),
};
