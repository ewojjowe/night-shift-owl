/**
 * Authentication store — owns the token pair, the current user, and the session
 * lifecycle (login / register / silent refresh / logout).
 *
 * Two tokens are kept: a short-lived ACCESS token sent on every request, and a
 * long-lived REFRESH token used to obtain a new access token when the old one
 * expires. Both are persisted to localStorage so a page reload keeps the user
 * signed in. The store also registers a refresh callback with the API client, so
 * an expired access token is renewed transparently rather than logging the user
 * out. Everything auth-related funnels through here, keeping views/router simple.
 *
 * Storage note: localStorage is convenient but readable by any script on the page
 * (XSS-exposed). DEPLOYMENT.md documents the recommended hardening — moving the
 * refresh token into an httpOnly, Secure, SameSite=None cookie — which needs no
 * change to component code, only to this store and the backend's token delivery.
 */

import { defineStore } from "pinia";
import { ref } from "vue";
import { api, setRefreshHandler, setToken } from "@/api/client";
import type { User } from "@/types";

// Not exported: the localStorage keys are an implementation detail of this store.
const ACCESS_KEY = "night_shift_token";
const REFRESH_KEY = "night_shift_refresh";

// The backend's /auth response shape: an access + refresh pair.
type TokenPair = { access_token: string; refresh_token: string; token_type: string };

export const useAuthStore = defineStore("auth", () => {
  // Initialise from localStorage so a returning user starts already logged in.
  const token = ref<string | null>(localStorage.getItem(ACCESS_KEY));
  const refreshToken = ref<string | null>(localStorage.getItem(REFRESH_KEY));
  const user = ref<User | null>(null);
  setToken(token.value); // prime the API client with any restored access token

  /**
   * Persist a freshly issued token pair everywhere it needs to live.
   *
   * One helper keeps every copy of the tokens — the reactive refs, the API client,
   * and localStorage — from drifting apart. Passing `null, null` performs the
   * inverse (used by logout) and clears both slots.
   */
  function applyTokens(access: string | null, refresh: string | null): void {
    token.value = access;
    refreshToken.value = refresh;
    setToken(access);
    if (access) localStorage.setItem(ACCESS_KEY, access);
    else localStorage.removeItem(ACCESS_KEY);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
    else localStorage.removeItem(REFRESH_KEY);
  }

  /**
   * Register a new account, then store the returned token pair.
   *
   * The backend logs the user in as part of registering (it returns tokens), so
   * there's no separate login step for a brand-new user. Errors bubble up to the
   * view, which shows the backend's message (e.g. "username already registered").
   */
  async function register(username: string, email: string, password: string): Promise<void> {
    const res = await api.post<TokenPair>("/auth/register", { username, email, password });
    applyTokens(res.access_token, res.refresh_token);
    await fetchMe();
  }

  /** Log in with existing credentials and store the returned token pair. */
  async function login(username: string, password: string): Promise<void> {
    const res = await api.post<TokenPair>("/auth/login", { username, password });
    applyTokens(res.access_token, res.refresh_token);
    await fetchMe();
  }

  /**
   * Exchange the refresh token for a new pair — the API client's 401 recovery hook.
   *
   * Registered with the client via `setRefreshHandler`, so it runs automatically
   * when a request gets a 401. On success it stores the rotated pair and returns
   * true (the client then retries the original request). On any failure — no
   * refresh token, or the server rejecting it (expired / rotated / reuse-detected)
   * — it clears the session locally and returns false so the client stops retrying
   * and the router guard sends the user to login.
   */
  async function refresh(): Promise<boolean> {
    if (!refreshToken.value) return false;
    try {
      const res = await api.post<TokenPair>("/auth/refresh", {
        refresh_token: refreshToken.value,
      });
      applyTokens(res.access_token, res.refresh_token);
      return true;
    } catch {
      clearSession();
      return false;
    }
  }

  /**
   * Load the current user's profile using the access token.
   *
   * Called on app start to hydrate the user. A transient expired access token is
   * handled by the client's silent refresh; only a genuine auth failure (refresh
   * also invalid) reaches the catch, where we clear the session so the UI falls
   * back to login instead of a broken, half-authenticated state.
   */
  async function fetchMe(): Promise<void> {
    try {
      user.value = await api.get<User>("/auth/me");
    } catch {
      clearSession();
    }
  }

  /** Clear all auth state locally (no server call). Shared by refresh/fetchMe/logout. */
  function clearSession(): void {
    applyTokens(null, null);
    user.value = null;
  }

  /**
   * Log out: clear local state immediately, then revoke the token server-side.
   *
   * We capture the refresh token, clear the session *first* so the UI updates
   * instantly (no flash of logged-in state while a request is in flight), then fire
   * the revoke in the background — best-effort, since a network error shouldn't
   * trap the user in a logged-in UI. Revoking stops the session being resumed with
   * a stolen copy; the stateless access token simply lapses within minutes.
   */
  function logout(): void {
    const tokenToRevoke = refreshToken.value;
    clearSession();
    if (tokenToRevoke) {
      api.post("/auth/logout", { refresh_token: tokenToRevoke }).catch(() => {
        /* ignore — clearing locally is what matters for the user */
      });
    }
  }

  // Wire silent refresh into the API client for the lifetime of the app.
  setRefreshHandler(refresh);

  return { token, refreshToken, user, register, login, refresh, fetchMe, logout };
});
