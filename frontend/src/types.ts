/**
 * Shared TypeScript types describing the API payloads.
 *
 * These mirror the backend Pydantic models field-for-field (snake_case included),
 * so the data flowing between server and client has one agreed shape. Keeping them
 * in one file means a backend change surfaces as a single, obvious edit here.
 */

/** A single external learning link. Mirrors backend `Resource`. */
export interface Resource {
  name: string;
  url: string;
}

/** One module within a track: title (`t`), focus (`f`), and its resources. */
export interface Lesson {
  t: string;
  f: string;
  res: Resource[];
}

/** A full learning track or the projects list. Mirrors backend `Track`. */
export interface Track {
  key: string;
  label: string;
  day: string;
  icon: string;
  kind: "track" | "projects";
  lessons: Lesson[];
}

/** How far the user has advanced within one track (index of current module). */
export interface TrackProgress {
  idx: number;
}

/** Shift configuration for a single day of the week. */
export interface ShiftDay {
  working: boolean;
  shift_end: string;
  shift_start: string;
}

/** Wake / wind-down times applied on days off. */
export interface OffDayDefaults {
  wake: string;
  bedtime: string;
}

/** The user's complete persisted progress + schedule. Mirrors backend `ProgressState`. */
export interface ProgressState {
  start_date: string;
  tracks: Record<string, TrackProgress>;
  projects: TrackProgress;
  shift_template: Record<string, ShiftDay>; // keys "0".."6" (Sun..Sat)
  off_day_defaults: OffDayDefaults;
  shift_overrides: Record<string, ShiftDay>; // keyed by "YYYY-MM-DD"
  ui_open: Record<string, boolean>;
}

/** Partial config update sent to `PUT /progress`. */
export interface ProgressUpdate {
  shift_template?: Record<string, ShiftDay>;
  off_day_defaults?: OffDayDefaults;
  shift_overrides?: Record<string, ShiftDay>;
  ui_open?: Record<string, boolean>;
}

/** The authenticated user's public profile. Mirrors backend `UserOut`. */
export interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
}
