<script setup lang="ts">
/**
 * Login page. A small controlled form that hands credentials to the auth store and
 * navigates to the dashboard on success. All auth logic lives in the store; this
 * component only manages the form fields, a busy flag, and an error message.
 */
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const auth = useAuthStore();

const username = ref("");
const password = ref("");
const error = ref<string | null>(null);
const busy = ref(false);

/**
 * Attempt to log in, then route to the dashboard.
 *
 * We disable the button via `busy` while the request is in flight (preventing
 * double-submits) and surface any thrown error — e.g. the backend's "Incorrect
 * username or password" — in the error banner. The `finally` guarantees the form
 * re-enables whether the call succeeded or failed.
 */
async function submit(): Promise<void> {
  error.value = null;
  busy.value = true;
  try {
    await auth.login(username.value, password.value);
    router.push({ name: "dashboard" });
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Login failed.";
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <div class="auth-wrap">
    <form class="auth-card" @submit.prevent="submit">
      <div class="eyebrow">Night Shift Roadmap</div>
      <h1>Welcome back</h1>

      <div v-if="error" class="auth-error">{{ error }}</div>

      <div class="auth-field">
        <label for="username">Username</label>
        <input id="username" v-model="username" autocomplete="username" required />
      </div>
      <div class="auth-field">
        <label for="password">Password</label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
        />
      </div>

      <button class="btn btn-amber auth-btn" type="submit" :disabled="busy">
        {{ busy ? "Signing in…" : "Sign in" }}
      </button>

      <div class="auth-switch">
        No account yet?
        <router-link to="/register">Create one</router-link>
      </div>
    </form>
  </div>
</template>
