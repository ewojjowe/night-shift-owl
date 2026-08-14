/**
 * Application bootstrap.
 *
 * Creates the Vue app, installs Pinia (state) and the router (navigation), then
 * validates any restored token *before* the first render. Awaiting `fetchMe` here
 * means the app mounts already knowing whether the user is logged in, avoiding a
 * flash of the login screen for a returning, still-authenticated user.
 */

import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "@/App.vue";
import router from "@/router";
import { useAuthStore } from "@/stores/auth";
import "@/style.css";

async function bootstrap(): Promise<void> {
  const app = createApp(App);

  // Pinia must be installed before we touch any store (the auth check below does).
  const pinia = createPinia();
  app.use(pinia);

  // If a token was restored from localStorage, confirm it's still valid. An
  // invalid/expired token makes fetchMe log the user out, so the router guard then
  // correctly sends them to /login.
  const auth = useAuthStore();
  if (auth.token) {
    await auth.fetchMe();
  }

  app.use(router);
  app.mount("#app");
}

bootstrap();
