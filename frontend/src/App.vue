<script setup lang="ts">
/**
 * Root component. It is intentionally minimal: its only job is to render whichever
 * route is active via <router-view>. All real UI lives in the view components, and
 * the router guard decides which one shows. Keeping the shell this thin means there
 * is no layout logic to reason about at the top level.
 */
</script>

<template>
  <router-view />
</template>
