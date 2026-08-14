<script setup lang="ts">
/**
 * Registration page. Mirrors the login form but collects an email and creates the
 * account. On success the store already holds a token (the backend logs the new
 * user straight in), so we can navigate to the dashboard immediately.
 */
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const auth = useAuthStore();

const username = ref("");
const email = ref("");
const password = ref("");
const error = ref<string | null>(null);
const busy = ref(false);

/**
 * Create the account, then route to the dashboard.
 *
 * Validation constraints (min lengths, email format) are enforced by the backend
 * Pydantic model; if the input violates them, or the username/email is taken, the
 * thrown error message is shown in the banner rather than silently failing.
 */
async function submit(): Promise<void> {
  error.value = null;
  busy.value = true;
  try {
    await auth.register(username.value, email.value, password.value);
    router.push({ name: "dashboard" });
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Registration failed.";
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <div class="auth-wrap">
    <form class="auth-card" @submit.prevent="submit">
      <div class="eyebrow">Night Shift Roadmap</div>
      <h1>Create your account</h1>

      <div v-if="error" class="auth-error">{{ error }}</div>

      <div class="auth-field">
        <label for="username">Username</label>
        <input id="username" v-model="username" autocomplete="username" required />
      </div>
      <div class="auth-field">
        <label for="email">Email</label>
        <input id="email" v-model="email" type="email" autocomplete="email" required />
      </div>
      <div class="auth-field">
        <label for="password">Password (min 8 characters)</label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="new-password"
          minlength="8"
          required
        />
      </div>

      <button class="btn btn-amber auth-btn" type="submit" :disabled="busy">
        {{ busy ? "Creating…" : "Create account" }}
      </button>

      <div class="auth-switch">
        Already have an account?
        <router-link to="/login">Sign in</router-link>
      </div>
    </form>
  </div>
</template>
