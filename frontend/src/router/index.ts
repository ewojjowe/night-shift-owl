/**
 * Client-side routing + the authentication guard.
 *
 * Three routes: the dashboard (protected) and login/register (public). A single
 * global `beforeEach` guard enforces the rules — send anonymous users to /login,
 * and bounce already-logged-in users away from the auth pages — so no individual
 * component has to check auth itself.
 */

import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "dashboard",
      component: () => import("@/views/DashboardView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      meta: { publicOnly: true },
    },
    {
      path: "/register",
      name: "register",
      component: () => import("@/views/RegisterView.vue"),
      meta: { publicOnly: true },
    },
    {
      path: "/welcome",
      name: "welcome",
      component: () => import("@/views/LandingView.vue"),
    },
  ],
});

/**
 * Gate every navigation on the presence of a token.
 *
 * We treat "has a token" as "logged in" — cheap and synchronous, so navigation
 * never stalls on a network call (the token's real validity is confirmed once, at
 * app start, by `fetchMe`). `requiresAuth` pages redirect anonymous users to login;
 * `publicOnly` pages redirect authenticated users to the dashboard so they don't
 * see the login form while signed in.
 */
router.beforeEach((to) => {
  const auth = useAuthStore();
  const isLoggedIn = !!auth.token;

  if (to.meta.requiresAuth && !isLoggedIn) {
    return { name: "welcome" };
  }
  if (to.meta.publicOnly && isLoggedIn) {
    return { name: "dashboard" };
  }
  return true;
});

export default router;
