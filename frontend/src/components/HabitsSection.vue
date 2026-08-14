<script setup lang="ts">
/**
 * The "Daily habits" section: the Math and DSA cards side by side. These two
 * tracks are worked every day regardless of weekday, so they get their own
 * always-visible row (rendered with the compact habit layout of LessonCard).
 */
import LessonCard from "@/components/LessonCard.vue";
</script>

<template>
  <div class="habits-row">
    <LessonCard track-key="math" mode="habit" />
    <LessonCard track-key="dsa" mode="habit" />
  </div>
</template>
