import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// Vite configuration for the Vue dev server + build.
// - The Vue plugin enables single-file component (.vue) compilation.
// - `server.host` binds to all interfaces so the dev server is reachable from
//   outside the container (docker-compose publishes port 5173).
// - `usePolling` makes hot-reload work reliably for bind-mounted files on macOS
//   and Windows Docker, where native filesystem events don't cross the VM boundary.
// - The `@` alias lets us write `@/stores/auth` instead of long relative paths.
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    watch: {
      usePolling: true,
    },
  },
});
