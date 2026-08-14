/// <reference types="vite/client" />

// Lets TypeScript understand `.vue` single-file components when they are imported
// (e.g. `import App from './App.vue'`). Without this shim, TS would complain that
// the module has no type declarations.
declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

// Types the custom environment variables we read via `import.meta.env`, so
// `import.meta.env.VITE_API_BASE` is known to be a string instead of `any`.
interface ImportMetaEnv {
  readonly VITE_API_BASE: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
