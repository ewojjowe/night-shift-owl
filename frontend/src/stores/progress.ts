/**
 * Progress store — the client-side mirror of the user's server-persisted state.
 *
 * It holds the `ProgressState` fetched from the backend, exposes derived values
 * the header/roadmap need (day count, completion %), and provides the actions that
 * mutate progress by calling the API. Two pieces of state are deliberately
 * *ephemeral* — `revealed` and `deepDiveChoice` — matching the original page where
 * "reveal today's lesson" and the deep-dive pick reset each session and are never
 * saved.
 */

import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { api } from "@/api/client";
import type { ProgressState, ProgressUpdate } from "@/types";
import { useCurriculumStore } from "@/stores/curriculum";

export const useProgressStore = defineStore("progress", () => {
  const state = ref<ProgressState | null>(null);

  // Session-only UI flags (never persisted, cleared on reload) --------------
  const revealed = ref<Set<string>>(new Set());
  const deepDiveChoice = ref<string | null>(null);

  /**
   * "Day N" since the user started — matches the header counter in the original.
   *
   * Computed as whole days elapsed since `start_date`, plus one so the first day
   * reads "Day 1" (not "Day 0"), and floored at 1 to stay sensible if the clock or
   * timezone nudges it negative.
   */
  const dayCount = computed<number>(() => {
    if (!state.value) return 1;
    const start = new Date(state.value.start_date);
    const now = new Date();
    const diff = Math.floor((now.getTime() - start.getTime()) / 86_400_000) + 1;
    return Math.max(1, diff);
  });

  /**
   * Total modules across all tracks + projects, and how many are done.
   *
   * `done` counts completed modules per track (capped at the track length so an
   * over-shot index can't inflate the number). Track lengths come from the
   * curriculum store, so this recomputes automatically once the curriculum loads.
   */
  const totalUnits = computed<{ total: number; done: number }>(() => {
    const curriculum = useCurriculumStore();
    let total = 0;
    let done = 0;
    if (!state.value) return { total, done };
    for (const track of curriculum.tracks) {
      const len = track.lessons.length;
      total += len;
      if (track.key === "projects") {
        done += Math.min(state.value.projects.idx, len);
      } else {
        done += Math.min(state.value.tracks[track.key]?.idx ?? 0, len);
      }
    }
    return { total, done };
  });

  /** Whole-number completion percentage for the header (0 when nothing loaded). */
  const pct = computed<number>(() => {
    const { total, done } = totalUnits.value;
    return total === 0 ? 0 : Math.round((done / total) * 100);
  });

  /** Fetch the user's progress after login (backend creates defaults if needed). */
  async function load(): Promise<void> {
    state.value = await api.get<ProgressState>("/progress");
  }

  /**
   * Persist a config change (shift schedule, off-day defaults, overrides, UI).
   *
   * We send only the changed slice and replace local state with the backend's
   * authoritative response, so client and server can never disagree about what was
   * saved. Every shift input and section toggle routes through here.
   */
  async function updateConfig(changes: ProgressUpdate): Promise<void> {
    state.value = await api.put<ProgressState>("/progress", changes);
  }

  /**
   * Mark the current module of a track (or "projects") complete.
   *
   * Delegates the "advance and cap at the end" logic to the backend and stores the
   * returned state. We also drop the track's reveal flag so the next module starts
   * hidden again, exactly like the original "Mark complete" flow.
   */
  async function complete(key: string): Promise<void> {
    state.value = await api.patch<ProgressState>(`/progress/tracks/${key}/complete`);
    revealed.value.delete(key);
  }

  /** Reset all progress to a fresh day-1 document and clear session UI flags. */
  async function reset(): Promise<void> {
    state.value = await api.post<ProgressState>("/progress/reset");
    revealed.value.clear();
    deepDiveChoice.value = null;
  }

  /** Reveal a track's lesson body for this session (not persisted). */
  function reveal(key: string): void {
    revealed.value.add(key);
  }

  /** Whether a track's lesson body is currently revealed this session. */
  function isRevealed(key: string): boolean {
    return revealed.value.has(key);
  }

  /** Remember the Saturday deep-dive topic the user picked (session-only). */
  function setDeepDive(key: string): void {
    deepDiveChoice.value = key;
  }

  /** Clear everything on logout so the next user starts from a blank slate. */
  function clear(): void {
    state.value = null;
    revealed.value.clear();
    deepDiveChoice.value = null;
  }

  return {
    state,
    revealed,
    deepDiveChoice,
    dayCount,
    totalUnits,
    pct,
    load,
    updateConfig,
    complete,
    reset,
    reveal,
    isRevealed,
    setDeepDive,
    clear,
  };
});
