<script setup lang="ts">
/**
 * A single lesson card, shared by the daily habits (Math/DSA) and the weekday main
 * focus — the `mode` prop switches between the compact "habit" layout and the
 * larger "focus" layout, exactly like the original `buildLessonCard(key, mode)`.
 *
 * The body (resources + "mark complete") stays hidden behind a "Reveal" button
 * until the user opts in, preserving the deliberate one-lesson-at-a-time feel.
 */
import { computed } from "vue";
import { useCurriculumStore } from "@/stores/curriculum";
import { useProgressStore } from "@/stores/progress";

const props = defineProps<{ trackKey: string; mode: "habit" | "focus" }>();

const curriculum = useCurriculumStore();
const progress = useProgressStore();

const track = computed(() => curriculum.byKey[props.trackKey]);
const total = computed(() => track.value?.lessons.length ?? 0);
const idx = computed(() => progress.state?.tracks[props.trackKey]?.idx ?? 0);
const isComplete = computed(() => idx.value >= total.value);
const lesson = computed(() => track.value?.lessons[idx.value]);
const pct = computed(() => (total.value ? Math.round((idx.value / total.value) * 100) : 0));
const revealed = computed(() => progress.isRevealed(props.trackKey));

/** Reveal this track's lesson body for the session. */
function reveal(): void {
  progress.reveal(props.trackKey);
}

/** Advance to the next module (persists via the store → backend). */
function complete(): void {
  progress.complete(props.trackKey);
}
</script>

<template>
  <div v-if="track" :class="mode === 'habit' ? 'habit-card' : 'focus-card'">
    <!-- Completed-track state: no more modules to show. -->
    <template v-if="isComplete">
      <div class="habit-top">
        <div class="habit-name">{{ track.icon }} {{ track.label }}</div>
        <div class="habit-progress">{{ total }}/{{ total }}</div>
      </div>
      <div class="habit-bar"><div class="habit-bar-fill" style="width: 100%"></div></div>
      <div class="done-banner">
        ✅ Track complete — pick a Saturday deep-dive topic to keep it sharp, or revisit any
        resource above.
      </div>
    </template>

    <!-- Habit layout (Math / DSA). -->
    <template v-else-if="mode === 'habit'">
      <div class="habit-top">
        <div class="habit-name">{{ track.icon }} {{ track.label }}</div>
        <div class="habit-progress">{{ idx }}/{{ total }}</div>
      </div>
      <div class="habit-bar"><div class="habit-bar-fill" :style="{ width: pct + '%' }"></div></div>
      <div class="habit-desc">Solve one problem/exercise a day from the current module below.</div>

      <button v-if="!revealed" class="btn btn-outline" @click="reveal">
        Reveal today's module →
      </button>
      <div v-else class="paper">
        <div class="p-focus">{{ lesson?.f }}</div>
        <h4>Resources</h4>
        <ul>
          <li v-for="r in lesson?.res" :key="r.url">
            <a :href="r.url" target="_blank" rel="noopener">{{ r.name }}</a>
          </li>
        </ul>
        <div class="paper-actions">
          <button class="btn btn-amber" @click="complete">Mark complete — next module →</button>
        </div>
      </div>
    </template>

    <!-- Focus layout (weekday main lesson). -->
    <template v-else>
      <div class="focus-head">
        <div>
          <div class="focus-tag">{{ track.icon }} {{ track.label }} · {{ track.day }}</div>
          <div class="focus-title">{{ lesson?.t }}</div>
        </div>
        <div class="focus-count">Module {{ idx + 1 }} of {{ total }}</div>
      </div>

      <div v-if="!revealed" style="margin-top: 14px">
        <button class="btn btn-amber" @click="reveal">Reveal today's lesson →</button>
      </div>
      <div v-else class="paper">
        <div class="p-focus">{{ lesson?.f }}</div>
        <h4>Resources</h4>
        <ul>
          <li v-for="r in lesson?.res" :key="r.url">
            <a :href="r.url" target="_blank" rel="noopener">{{ r.name }}</a>
          </li>
        </ul>
        <div class="paper-actions">
          <button class="btn btn-amber" @click="complete">Mark complete — next module →</button>
        </div>
      </div>
    </template>
  </div>
</template>
