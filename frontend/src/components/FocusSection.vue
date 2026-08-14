<script setup lang="ts">
/**
 * The weekday-dependent "main focus" section. It routes on today's weekday exactly
 * like the original `renderFocus()`:
 *   - Saturday → a deep-dive review (pick a topic to revisit),
 *   - Sunday   → the Project Day card,
 *   - Mon–Fri  → that day's track, shown with the LessonCard focus layout.
 *
 * The section title (exposed to the parent) changes to match.
 */
import { computed } from "vue";
import { useCurriculumStore } from "@/stores/curriculum";
import { useProgressStore } from "@/stores/progress";
import { DAY_NAMES, WEEKDAY_KEY } from "@/lib/timeline";
import LessonCard from "@/components/LessonCard.vue";

const curriculum = useCurriculumStore();
const progress = useProgressStore();

const today = new Date().getDay();

/** The heading shown for this section, surfaced to the dashboard via defineExpose. */
const title = computed(() => {
  if (today === 6) return "Saturday — Deep Dive";
  if (today === 0) return "Sunday — Project Day";
  return `Today's main focus — ${DAY_NAMES[today]}`;
});
defineExpose({ title });

// --- Deep dive (Saturday) --------------------------------------------------
const deepDiveOptions: [string, string][] = [
  ["math", "Math"],
  ["dsa", "DSA"],
  ["python", "Python"],
  ["aiml", "AI / ML"],
  ["go", "Go"],
  ["sysdesign", "System Design"],
  ["aieng", "AI Engineering"],
];

/**
 * The lesson to revisit for the chosen deep-dive track.
 *
 * Mirrors the original: review the module they *just* finished (idx − 1), clamped
 * so a fresh track (idx 0) still shows its first module and a completed track shows
 * its last. No progress is advanced on a deep-dive day — it's for consolidation.
 */
const deepDiveLesson = computed(() => {
  const key = progress.deepDiveChoice;
  if (!key) return null;
  const track = curriculum.byKey[key];
  if (!track) return null;
  const raw = (progress.state?.tracks[key]?.idx ?? 0) - 1;
  const clamped = Math.min(Math.max(0, raw), track.lessons.length - 1);
  return track.lessons[clamped];
});

// --- Project Day (Sunday) --------------------------------------------------
const projectsTrack = computed(() => curriculum.byKey["projects"]);
const projectIdx = computed(() => progress.state?.projects.idx ?? 0);
const projectTotal = computed(() => projectsTrack.value?.lessons.length ?? 0);
const projectComplete = computed(() => projectIdx.value >= projectTotal.value);
const currentProject = computed(() => projectsTrack.value?.lessons[projectIdx.value]);
const projectRevealed = computed(() => progress.isRevealed("projects"));

// --- Weekday track (Mon–Fri) ----------------------------------------------
const weekdayKey = computed(() => WEEKDAY_KEY[today]);
</script>

<template>
  <!-- Saturday: deep-dive review -->
  <div v-if="today === 6" class="focus-card">
    <div class="focus-tag">🔎 Weekly review</div>
    <div class="focus-title">Which topic felt weakest this week?</div>
    <div class="chip-row">
      <button
        v-for="[key, label] in deepDiveOptions"
        :key="key"
        class="chip"
        :class="{ selected: progress.deepDiveChoice === key }"
        @click="progress.setDeepDive(key)"
      >
        {{ label }}
      </button>
    </div>
    <div v-if="deepDiveLesson" class="paper">
      <div class="p-focus">
        Revisit: <strong>{{ deepDiveLesson.t }}</strong> — {{ deepDiveLesson.f }}
      </div>
      <h4>Resources to re-run</h4>
      <ul>
        <li v-for="r in deepDiveLesson.res" :key="r.url">
          <a :href="r.url" target="_blank" rel="noopener">{{ r.name }}</a>
        </li>
      </ul>
      <div class="practice">
        Redo one problem/exercise from this module today, or read one resource more slowly than
        you had time for during the week. No need to advance — this day is for consolidation, not
        new material.
      </div>
    </div>
  </div>

  <!-- Sunday: Project Day -->
  <div v-else-if="today === 0" class="focus-card">
    <template v-if="projectComplete">
      <div class="focus-tag">🛠 Project Day</div>
      <div class="focus-title">All project milestones complete 🎉</div>
      <div class="done-banner" style="margin-top: 10px">
        Time to design your own capstone, or loop back and rebuild an early project with everything
        you know now.
      </div>
    </template>
    <template v-else>
      <div class="focus-head">
        <div>
          <div class="focus-tag">🛠 Project Day</div>
          <div class="focus-title">{{ currentProject?.t }}</div>
        </div>
        <div class="focus-count">Project {{ projectIdx + 1 }} of {{ projectTotal }}</div>
      </div>
      <div v-if="!projectRevealed" style="margin-top: 14px">
        <button class="btn btn-amber" @click="progress.reveal('projects')">
          Reveal today's project →
        </button>
      </div>
      <div v-else class="paper">
        <div class="p-focus">{{ currentProject?.f }}</div>
        <div class="practice">
          Combine this week's main topic with whatever you've already built. Keep scope small
          enough to finish in one session — you can always extend it next Sunday.
        </div>
        <div class="paper-actions">
          <button class="btn btn-amber" @click="progress.complete('projects')">
            Mark complete — next project →
          </button>
        </div>
      </div>
    </template>
  </div>

  <!-- Weekday: the day's track -->
  <LessonCard v-else-if="weekdayKey" :track-key="weekdayKey" mode="focus" />
</template>
