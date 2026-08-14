<script setup lang="ts">
/**
 * The shift-schedule editor. It lets the user set, per weekday, whether they're
 * working and their free-time window, plus days-off wake/wind-down defaults and a
 * one-off "today is different" override. Every change persists to the backend and
 * the timeline recomputes reactively from the saved state.
 *
 * The form keeps its own local copy of the config (seeded once from the store).
 * That keeps the inputs snappy and avoids a feedback loop where saving replaces the
 * store's state and yanks the values out from under the user mid-edit; we push
 * changes to the server on `change`, we don't pull the whole form back on save.
 */
import { reactive, ref } from "vue";
import { useProgressStore } from "@/stores/progress";
import { isoLocal } from "@/lib/timeline";
import type { ShiftDay } from "@/types";

const progress = useProgressStore();
const state = progress.state!; // dashboard guarantees progress is loaded first

const DAY_ABBR = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const todayIso = isoLocal(new Date());

/**
 * Deep-clone plain config data out of the reactive store.
 *
 * We deliberately use a JSON round-trip rather than `structuredClone`: the store's
 * values are Vue reactive Proxies, which `structuredClone` refuses to clone
 * (DataCloneError). Our config is pure JSON (strings + booleans), so this is both
 * safe and gives us an ordinary, non-reactive snapshot to edit locally.
 */
function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value));
}

// --- Local, editable copies of the persisted config ------------------------
// A plain clone so edits don't mutate the store directly (we save explicitly).
const template = reactive<Record<string, ShiftDay>>(clone(state.shift_template));
const offWake = ref(state.off_day_defaults.wake);
const offBed = ref(state.off_day_defaults.bedtime);

const existingOverride = state.shift_overrides[todayIso];
const overrideEnabled = ref(!!existingOverride);
const override = reactive<ShiftDay>(
  existingOverride
    ? clone(existingOverride)
    : { working: true, shift_end: "08:00", shift_start: "22:00" },
);

// --- Persistence helpers ---------------------------------------------------

/** Save the weekly template (sends the whole 7-day map, which the backend replaces). */
function saveTemplate(): void {
  progress.updateConfig({ shift_template: { ...template } });
}

/** Save the days-off default wake/wind-down times. */
function saveOffDefaults(): void {
  progress.updateConfig({ off_day_defaults: { wake: offWake.value, bedtime: offBed.value } });
}

/**
 * Save the per-day override map.
 *
 * We start from the *stored* overrides (preserving other dates) and either set or
 * delete today's entry depending on the toggle, then send the whole map. Toggling
 * the override off must remove today's key so the timeline falls back to the
 * weekly template.
 */
function saveOverride(): void {
  const overrides: Record<string, ShiftDay> = { ...state.shift_overrides };
  if (overrideEnabled.value) {
    overrides[todayIso] = { ...override };
  } else {
    delete overrides[todayIso];
  }
  progress.updateConfig({ shift_overrides: overrides });
}
</script>

<template>
  <div class="shift-panel">
    <div class="shift-intro">
      Set the times you're free — from when a shift ends to when the next one starts. Days off use
      your default wake / wind-down times instead. Math, DSA and today's main lesson get placed
      automatically, and the study block stretches or shrinks to fit whatever's actually left.
    </div>

    <!-- One row per weekday -->
    <div v-for="d in 7" :key="d - 1" class="shift-row">
      <span class="shift-day">{{ DAY_ABBR[d - 1] }}</span>
      <label class="shift-toggle">
        <input type="checkbox" v-model="template[String(d - 1)].working" @change="saveTemplate" />
        Working
      </label>
      <span v-show="template[String(d - 1)].working" class="shift-times">
        <label>
          Free from
          <input type="time" v-model="template[String(d - 1)].shift_end" @change="saveTemplate" />
        </label>
        <label>
          Back by
          <input type="time" v-model="template[String(d - 1)].shift_start" @change="saveTemplate" />
        </label>
      </span>
    </div>

    <!-- Days-off defaults -->
    <div class="offday-defaults">
      <label>
        Wake time on days off
        <input type="time" v-model="offWake" @change="saveOffDefaults" />
      </label>
      <label>
        Wind-down time on days off
        <input type="time" v-model="offBed" @change="saveOffDefaults" />
      </label>
    </div>

    <!-- Today-only override -->
    <div class="today-override">
      <div class="override-head">
        <strong>Today different from usual?</strong>
        <label>
          <input type="checkbox" v-model="overrideEnabled" @change="saveOverride" />
          Override just for today
        </label>
      </div>
      <div v-show="overrideEnabled" class="override-fields">
        <label>
          <input type="checkbox" v-model="override.working" @change="saveOverride" />
          Working today
        </label>
        <label>
          Free from
          <input type="time" v-model="override.shift_end" @change="saveOverride" />
        </label>
        <label>
          Back by
          <input type="time" v-model="override.shift_start" @change="saveOverride" />
        </label>
      </div>
    </div>
  </div>
</template>
