<script setup lang="ts">
/**
 * "Today's timeline" plus a collapsible 7-day preview. Each table is produced by
 * the pure `computeTimeline` engine from the shift config, with the flexible
 * "main" study block labelled with the actual subject for that weekday.
 */
import { computed } from "vue";
import { useCurriculumStore } from "@/stores/curriculum";
import { useProgressStore } from "@/stores/progress";
import {
  computeTimeline,
  DAY_NAMES,
  HIGHLIGHT_KEYS,
  WEEKDAY_KEY,
  type TimelineItem,
} from "@/lib/timeline";

const curriculum = useCurriculumStore();
const progress = useProgressStore();

/** The subject name for a date's main block: Project / Deep Dive / weekday track. */
function mainSubject(date: Date): string {
  const d = date.getDay();
  if (d === 0) return "Project Day";
  if (d === 6) return "Deep Dive";
  const key = WEEKDAY_KEY[d];
  return key ? (curriculum.byKey[key]?.label ?? key) : "";
}

/** Rows + warning for one date, with the main block's label enriched by subject. */
function buildDay(date: Date): { rows: (TimelineItem & { display: string; hi: boolean })[]; warning: string | null } {
  if (!progress.state) return { rows: [], warning: null };
  const { timeline, warning } = computeTimeline(progress.state, date);
  const subj = mainSubject(date);
  const rows = timeline.map((item) => ({
    ...item,
    hi: HIGHLIGHT_KEYS.includes(item.key),
    display: item.key === "main" ? `${item.label} — ${subj}` : item.label,
  }));
  return { rows, warning };
}

const todayPlan = computed(() => buildDay(new Date()));

/** The next seven days (today first), each with its own laid-out plan. */
const week = computed(() =>
  Array.from({ length: 7 }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() + i);
    return {
      label: `${DAY_NAMES[d.getDay()]}${i === 0 ? " (today)" : ""}`,
      plan: buildDay(d),
    };
  }),
);
</script>

<template>
  <div class="timeline-card">
    <table class="timeline">
      <tbody>
        <tr v-for="(row, i) in todayPlan.rows" :key="i" :class="{ highlight: row.hi }">
          <td>{{ row.start }} – {{ row.end }}</td>
          <td>{{ row.display }}</td>
        </tr>
      </tbody>
    </table>
    <div v-if="todayPlan.warning" class="timeline-warn">⚠ {{ todayPlan.warning }}</div>
  </div>

  <details class="sched-toggle">
    <summary>📆 Full week preview</summary>
    <div class="sched-body">
      <div v-for="(day, i) in week" :key="i" class="week-day-block">
        <h5>{{ day.label }}</h5>
        <table class="timeline">
          <tbody>
            <tr v-for="(row, j) in day.plan.rows" :key="j" :class="{ highlight: row.hi }">
              <td>{{ row.start }} – {{ row.end }}</td>
              <td>{{ row.display }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="day.plan.warning" class="timeline-warn">⚠ {{ day.plan.warning }}</div>
      </div>
    </div>
  </details>
</template>
