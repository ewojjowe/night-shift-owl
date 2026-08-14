<script setup lang="ts">
/**
 * The circular "dial" — the app's signature element. It arranges the seven
 * weekdays around a ring, highlights today, and shows today's focus in the centre.
 *
 * Node positions are computed with trig (the same maths as the original page):
 * each day sits at an even fraction of the circle, offset so Sunday starts at the
 * top. Labels for weekday tracks come from the curriculum store; Sunday and
 * Saturday are the fixed Project Day / Deep Dive.
 */
import { computed } from "vue";
import { useCurriculumStore } from "@/stores/curriculum";
import { DAY_ABBR, DAY_NAMES, WEEKDAY_KEY } from "@/lib/timeline";

const curriculum = useCurriculumStore();

// getDay(): Sunday=0 .. Saturday=6. Computed once per render; the dashboard is a
// per-day tool so we don't need it to tick live.
const today = new Date().getDay();

/** Human label for a given weekday index (Project/Deep Dive or the track's label). */
function topicFor(dayIndex: number): string {
  if (dayIndex === 0) return "Project Day";
  if (dayIndex === 6) return "Deep Dive";
  const key = WEEKDAY_KEY[dayIndex];
  return key ? (curriculum.byKey[key]?.label ?? key) : "";
}

/** Pre-computed node geometry + labels for all seven days. */
const nodes = computed(() => {
  const cx = 50;
  const cy = 50;
  const radius = 37; // percentages of the square container
  return Array.from({ length: 7 }, (_, i) => {
    const angle = (Math.PI * 2 * i) / 7 - Math.PI / 2;
    return {
      i,
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
      abbr: DAY_ABBR[i],
      topic: topicFor(i),
      isToday: i === today,
    };
  });
});

const centerTopic = computed(() => topicFor(today));
</script>

<template>
  <div class="dial-wrap">
    <div class="dial-ring"></div>
    <div
      v-for="node in nodes"
      :key="node.i"
      class="dial-node"
      :class="{ today: node.isToday }"
      :style="{ left: node.x + '%', top: node.y + '%' }"
    >
      <div class="dot"></div>
      <div class="d-abbr">{{ node.abbr }}</div>
      <div class="d-topic">{{ node.topic }}</div>
    </div>
    <div class="dial-center">
      <div class="day-lbl">Today</div>
      <div class="day-name">{{ DAY_NAMES[today] }}</div>
      <div class="day-focus">{{ centerTopic }}</div>
    </div>
  </div>
</template>
