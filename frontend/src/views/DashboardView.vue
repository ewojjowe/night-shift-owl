<script setup lang="ts">
/**
 * The main application screen — the full roadmap dashboard.
 *
 * On mount it loads the curriculum and the user's progress (both required before
 * anything can render), then lays out: the header stats, the weekday dial, and five
 * collapsible sections (shift schedule, timeline, habits, focus, roadmap). Section
 * open/closed state and progress all persist through the stores to the backend.
 */
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useCurriculumStore } from "@/stores/curriculum";
import { useProgressStore } from "@/stores/progress";
import { DAY_NAMES } from "@/lib/timeline";
import DialWidget from "@/components/DialWidget.vue";
import ShiftPanel from "@/components/ShiftPanel.vue";
import TimelineSection from "@/components/TimelineSection.vue";
import HabitsSection from "@/components/HabitsSection.vue";
import FocusSection from "@/components/FocusSection.vue";
import RoadmapSection from "@/components/RoadmapSection.vue";

const router = useRouter();
const auth = useAuthStore();
const curriculum = useCurriculumStore();
const progress = useProgressStore();

const loading = ref(true);
// Local mirror of the persisted section open-state; drives the <details> and is
// what we write back on toggle (see onToggle).
const uiOpen = reactive<Record<string, boolean>>({});

onMounted(async () => {
  // Both must succeed before rendering; either failing (e.g. a dead token) sends
  // the user back to login rather than showing a broken dashboard.
  try {
    await Promise.all([curriculum.load(), progress.load()]);
    Object.assign(uiOpen, progress.state?.ui_open ?? {});
  } catch {
    auth.logout();
    router.push({ name: "login" });
    return;
  }
  loading.value = false;
});

const today = new Date().getDay();

/** Heading for the focus section — matches FocusSection's own routing. */
const focusTitle = computed(() => {
  if (today === 6) return "Saturday — Deep Dive";
  if (today === 0) return "Sunday — Project Day";
  return `Today's main focus — ${DAY_NAMES[today]}`;
});

/**
 * Persist a section's open/closed state when the user toggles it.
 *
 * We only write when the value actually changed, so the initial render (which can
 * emit a toggle as the DOM syncs) doesn't cause a redundant save. The whole
 * `ui_open` map is sent so the backend stores a complete, consistent object.
 */
function onToggle(id: string, event: Event): void {
  const open = (event.target as HTMLDetailsElement).open;
  if (uiOpen[id] === open) return;
  uiOpen[id] = open;
  progress.updateConfig({ ui_open: { ...uiOpen } });
}

// --- Reset (two-click confirm, like the original) --------------------------
const resetConfirm = ref(false);
let resetTimer: number | undefined;

/**
 * Reset all progress, but require a confirming second click within 4 seconds.
 *
 * The first click arms the button and changes its label; a second click while
 * armed performs the reset. If the user hesitates, a timer disarms it so a stray
 * earlier click can't wipe progress later.
 */
async function onReset(): Promise<void> {
  if (resetConfirm.value) {
    window.clearTimeout(resetTimer);
    resetConfirm.value = false;
    await progress.reset();
    Object.assign(uiOpen, progress.state?.ui_open ?? {});
  } else {
    resetConfirm.value = true;
    resetTimer = window.setTimeout(() => (resetConfirm.value = false), 4000);
  }
}

/** Log out and return to the login screen, clearing cached user data. */
function logout(): void {
  auth.logout();
  progress.clear();
  curriculum.clear();
  router.push({ name: "login" });
}
</script>

<template>
  <div id="app-shell">
    <div v-if="loading" class="loading-note">Loading your roadmap…</div>

    <template v-else>
      <!-- HEADER -->
      <div class="hdr">
        <div>
          <div class="eyebrow">Personal curriculum · self-paced</div>
          <h1>Self-pace Learning Roadmap</h1>
          <div class="sub">
            One math problem, one DSA problem, one main topic a day, rotating through Python,
            AI/ML, Go, System Design and AI Engineering. Timed automatically around whatever shift
            you're actually working.
          </div>
        </div>
        <div class="hdr-stats">
          <div class="hdr-stat">
            <div class="num">{{ progress.dayCount }}</div>
            <div class="lbl">Day</div>
          </div>
          <div class="hdr-stat">
            <div class="num">{{ progress.pct }}%</div>
            <div class="lbl">Complete</div>
          </div>
        </div>
      </div>

      <div class="account-row">
        <span>Signed in as <span class="username">{{ auth.user?.username }}</span></span>
        <button class="btn-ghost" @click="logout">Log out</button>
      </div>

      <!-- DIAL -->
      <DialWidget />

      <!-- SHIFT SCHEDULE -->
      <details
        class="section-toggle"
        :open="uiOpen.secShift"
        @toggle="onToggle('secShift', $event)"
      >
        <summary>Your shift schedule</summary>
        <div class="section-body"><ShiftPanel /></div>
      </details>

      <!-- TIMELINE -->
      <details
        class="section-toggle"
        :open="uiOpen.secTimeline"
        @toggle="onToggle('secTimeline', $event)"
      >
        <summary>Today's timeline</summary>
        <div class="section-body"><TimelineSection /></div>
      </details>

      <!-- HABITS -->
      <details
        class="section-toggle"
        :open="uiOpen.secHabits"
        @toggle="onToggle('secHabits', $event)"
      >
        <summary>Daily habits</summary>
        <div class="section-body"><HabitsSection /></div>
      </details>

      <!-- FOCUS -->
      <details
        class="section-toggle"
        :open="uiOpen.secFocus"
        @toggle="onToggle('secFocus', $event)"
      >
        <summary>{{ focusTitle }}</summary>
        <div class="section-body"><FocusSection /></div>
      </details>

      <!-- ROADMAP -->
      <details
        class="section-toggle"
        :open="uiOpen.secRoadmap"
        @toggle="onToggle('secRoadmap', $event)"
      >
        <summary>Full roadmap</summary>
        <div class="section-body"><RoadmapSection /></div>
      </details>

      <!-- FOOTER -->
      <div class="footer">
        <div class="tip">
          Progress is saved to your account automatically. Go at whatever pace keeps this
          sustainable, a module a week is a fine default, slower is fine too.
        </div>
        <button class="btn-ghost" @click="onReset">
          {{ resetConfirm ? "Click again to confirm reset" : "Reset all progress" }}
        </button>
      </div>
      <div class="credit-footer>
          Created by <strong>Wei Zhu</strong> | Completely for Free
      </div>

    </template>
  </div>
</template>
