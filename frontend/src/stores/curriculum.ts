/**
 * Curriculum store — fetches and caches the study material.
 *
 * The curriculum is identical for every user and never changes during a session,
 * so we fetch it once after login and keep it here. A `byKey` lookup is exposed so
 * views can grab a track (e.g. "python") in O(1) instead of scanning the array.
 */

import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { api } from "@/api/client";
import type { Track } from "@/types";

export const useCurriculumStore = defineStore("curriculum", () => {
  const tracks = ref<Track[]>([]);
  const loaded = ref(false);

  /** Track lookup keyed by `key` (e.g. `byKey.value["python"]`), built reactively. */
  const byKey = computed<Record<string, Track>>(() =>
    Object.fromEntries(tracks.value.map((t) => [t.key, t])),
  );

  /**
   * Load the curriculum from the API, but only once per session.
   *
   * The `loaded` guard makes this safe to call from multiple places (e.g. the
   * dashboard mount) without triggering duplicate network requests.
   */
  async function load(): Promise<void> {
    if (loaded.value) return;
    tracks.value = await api.get<Track[]>("/curriculum");
    loaded.value = true;
  }

  /** Reset the cache on logout so the next user re-fetches cleanly. */
  function clear(): void {
    tracks.value = [];
    loaded.value = false;
  }

  return { tracks, loaded, byKey, load, clear };
});
