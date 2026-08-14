<script setup lang="ts">
/**
 * The "Full roadmap" accordion: one collapsible track per row, each listing its
 * modules with a done / current / locked marker. This is the at-a-glance progress
 * map from the original `renderRoadmap()`.
 */
import { computed } from "vue";
import { useCurriculumStore } from "@/stores/curriculum";
import { useProgressStore } from "@/stores/progress";
import type { Track } from "@/types";

const curriculum = useCurriculumStore();
const progress = useProgressStore();

// The curriculum arrives sorted by key; re-order it into the UI's preferred
// sequence (daily habits first, then the weekday tracks, projects last).
const DISPLAY_ORDER = ["math", "dsa", "python", "aiml", "go", "sysdesign", "aieng", "projects"];

const orderedTracks = computed<Track[]>(() =>
  [...curriculum.tracks].sort(
    (a, b) => DISPLAY_ORDER.indexOf(a.key) - DISPLAY_ORDER.indexOf(b.key),
  ),
);

/** Current module index for a track ("projects" is stored separately from tracks). */
function idxFor(key: string): number {
  if (key === "projects") return progress.state?.projects.idx ?? 0;
  return progress.state?.tracks[key]?.idx ?? 0;
}

/**
 * Classify a module relative to the current index: everything before it is done,
 * the one at it is current, the rest are locked. Returns the CSS class + glyph so
 * the template stays declarative.
 */
function itemState(trackKey: string, i: number): { cls: string; icon: string } {
  const idx = idxFor(trackKey);
  if (i < idx) return { cls: "done", icon: "✓" };
  if (i === idx) return { cls: "current", icon: "▶" };
  return { cls: "locked", icon: "🔒" };
}

/** Completion percentage for a track's progress bar (capped at 100%). */
function pctFor(track: Track): number {
  const total = track.lessons.length;
  return total ? Math.round((Math.min(idxFor(track.key), total) / total) * 100) : 0;
}
</script>

<template>
  <details v-for="track in orderedTracks" :key="track.key" class="roadmap-track">
    <summary>
      <span>{{ track.icon }}</span>
      <span class="rt-name">{{ track.label }}</span>
      <span class="rt-day">{{ track.day }}</span>
      <span class="rt-bar"><span class="rt-bar-fill" :style="{ width: pctFor(track) + '%' }"></span></span>
      <span class="rt-count">{{ Math.min(idxFor(track.key), track.lessons.length) }}/{{ track.lessons.length }}</span>
    </summary>
    <div class="rt-list">
      <div
        v-for="(lesson, i) in track.lessons"
        :key="lesson.t"
        class="rt-item"
        :class="itemState(track.key, i).cls"
      >
        <div class="rt-icon">{{ itemState(track.key, i).icon }}</div>
        <div>{{ lesson.t }}</div>
      </div>
    </div>
  </details>
</template>
