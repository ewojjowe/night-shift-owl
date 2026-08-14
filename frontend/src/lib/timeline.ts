/**
 * The shift-aware timeline engine — ported verbatim from the original HTML.
 *
 * This is pure, framework-free logic: given a user's shift config for a date, it
 * lays out that day's schedule (sleep, gym, study, etc.) into back-to-back time
 * blocks, stretching one flexible block to absorb whatever time is left. It lives
 * on the frontend because it is *presentation* derived from saved config — the
 * backend stores the inputs, and this recomputes the view whenever they change.
 *
 * Each day is either "working" (a shift touches it, so free time runs from when
 * the shift ends to when the next begins) or "off" (uses the off-day defaults).
 */

import type { ProgressState } from "@/types";

/** Maps JS `getDay()` (Sun=0..Sat=6) to the track key shown that weekday. */
export const WEEKDAY_KEY: (string | null)[] = [
  null, // Sun — Project Day
  "python", // Mon
  "aiml", // Tue
  "go", // Wed
  "sysdesign", // Thu
  "aieng", // Fri
  null, // Sat — Deep Dive
];

export const DAY_NAMES = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];
export const DAY_ABBR = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];

/** Keys whose blocks are highlighted in the timeline (the study-related ones). */
export const HIGHLIGHT_KEYS = ["math", "dsa", "main"];

/** One planned block before layout: a label, a duration, and how it may flex. */
interface Block {
  key: string;
  label: string;
  dur: number; // minutes
  flexible: boolean;
  isSleep?: boolean;
  isOverflow?: boolean;
  min?: number;
  max?: number;
}

/** A laid-out timeline entry with human-readable start/end times. */
export interface TimelineItem {
  key: string;
  label: string;
  start: string;
  end: string;
}

/** The engine's result: the ordered blocks plus an optional warning string. */
export interface TimelineResult {
  timeline: TimelineItem[];
  warning: string | null;
}

/** Blocks for a working day (recovery sleep + study squeezed around a shift). */
function workingBlocks(): Block[] {
  return [
    { key: "winddown", label: "Wind-down + breakfast", dur: 30, flexible: false },
    { key: "sleep", label: "Recovery sleep", dur: 390, flexible: false, isSleep: true, min: 300 },
    { key: "wake2", label: "Wake up, freshen up", dur: 30, flexible: false },
    { key: "gym", label: "Gym", dur: 45, flexible: false },
    { key: "errand", label: "Family / errands", dur: 90, flexible: false },
    { key: "dinner", label: "Dinner + family", dur: 60, flexible: false },
    { key: "math", label: "Daily Math Problem", dur: 25, flexible: false },
    { key: "dsa", label: "Daily DSA Problem", dur: 30, flexible: false },
    { key: "main", label: "Main Learning Topic", dur: 60, flexible: true, min: 30 },
    { key: "prep", label: "Prepare for work", dur: 30, flexible: false },
    { key: "buffer", label: "Buffer / commute", dur: 15, flexible: false },
  ];
}

/** Blocks for a day off (more study/project time, a free-time overflow block). */
function offdayBlocks(): Block[] {
  return [
    { key: "breakfast", label: "Breakfast + family", dur: 60, flexible: false },
    { key: "gym", label: "Gym", dur: 60, flexible: false },
    { key: "family", label: "Family time", dur: 90, flexible: false },
    { key: "math", label: "Daily Math Problem", dur: 30, flexible: false },
    { key: "dsa", label: "Daily DSA Problem", dur: 45, flexible: false },
    { key: "main", label: "Main Learning / Project Time", dur: 90, flexible: true, min: 60, max: 240 },
    { key: "free", label: "Free time", dur: 0, flexible: true, isOverflow: true },
  ];
}

/** Convert an "HH:MM" string to minutes-past-midnight (0 for empty input). */
export function toMin(hhmm: string): number {
  if (!hhmm) return 0;
  const [h, m] = hhmm.split(":").map(Number);
  return (h || 0) * 60 + (m || 0);
}

/** Format minutes-past-midnight as a 12-hour "h:MM AM/PM" string (wraps past 24h). */
export function fmtMin(m: number): string {
  const mm = ((m % 1440) + 1440) % 1440;
  const h = Math.floor(mm / 60);
  const mi = mm % 60;
  const ampm = h < 12 ? "AM" : "PM";
  let h12 = h % 12;
  if (h12 === 0) h12 = 12;
  return `${h12}:${String(mi).padStart(2, "0")} ${ampm}`;
}

/** Local (not UTC) "YYYY-MM-DD" for a date — used to key day-specific overrides. */
export function isoLocal(d: Date): string {
  return (
    d.getFullYear() +
    "-" +
    String(d.getMonth() + 1).padStart(2, "0") +
    "-" +
    String(d.getDate()).padStart(2, "0")
  );
}

/**
 * Resolve the effective shift for a date: a one-off override wins, else the
 * recurring weekly template for that weekday.
 */
export function getShiftForDate(state: ProgressState, dateObj: Date) {
  const iso = isoLocal(dateObj);
  if (state.shift_overrides[iso]) return state.shift_overrides[iso];
  return state.shift_template[String(dateObj.getDay())];
}

/**
 * Compute the full day's timeline for a date.
 *
 * The algorithm mirrors the original page exactly: fixed blocks keep their
 * durations, and the single flexible block ("main" study time) stretches or
 * shrinks to fill the free window. On a working day, recovery sleep also gives up
 * time before study drops below its minimum; if even that isn't enough, a warning
 * explains that the day is too tight. Blocks with zero duration are dropped, and
 * remaining blocks are placed back to back starting from `freeFrom`.
 */
export function computeTimeline(state: ProgressState, dateObj: Date): TimelineResult {
  const shift = getShiftForDate(state, dateObj);
  let freeFrom: number;
  let freeUntil: number;
  let blocks: Block[];
  let warning: string | null = null;

  if (shift.working) {
    freeFrom = toMin(shift.shift_end || "08:00");
    freeUntil = toMin(shift.shift_start || "22:00");
    if (freeUntil <= freeFrom) freeUntil += 1440;
    blocks = workingBlocks();

    const sleepBlock = blocks.find((b) => b.isSleep)!;
    const mainBlock = blocks.find((b) => b.flexible)!;
    const fixedSum = blocks
      .filter((b) => !b.flexible && !b.isSleep)
      .reduce((a, b) => a + b.dur, 0);
    const remaining = freeUntil - freeFrom - fixedSum;

    if (remaining < 0) {
      warning =
        "This shift leaves no real free time before you're back on the clock — the plan can't fit everything today. Consider trimming non-essentials.";
      sleepBlock.dur = 0;
      mainBlock.dur = 0;
    } else if (remaining >= sleepBlock.dur + (mainBlock.min ?? 0)) {
      mainBlock.dur = remaining - sleepBlock.dur;
    } else if (remaining >= (sleepBlock.min ?? 0) + (mainBlock.min ?? 0)) {
      mainBlock.dur = mainBlock.min ?? 0;
      sleepBlock.dur = remaining - mainBlock.dur;
    } else {
      warning = "Tight shift today — sleep and study time are both compressed below target.";
      mainBlock.dur = Math.max(0, Math.min(mainBlock.min ?? 0, remaining));
      sleepBlock.dur = Math.max(0, remaining - mainBlock.dur);
    }
  } else {
    freeFrom = toMin(state.off_day_defaults.wake || "08:00");
    freeUntil = toMin(state.off_day_defaults.bedtime || "00:00");
    if (freeUntil <= freeFrom) freeUntil += 1440;
    blocks = offdayBlocks();

    const mainBlock = blocks.find((b) => b.key === "main")!;
    const freeBlock = blocks.find((b) => b.key === "free")!;
    const fixedSum = blocks.filter((b) => !b.flexible).reduce((a, b) => a + b.dur, 0);
    const remaining = freeUntil - freeFrom - fixedSum;

    if (remaining < (mainBlock.min ?? 0)) {
      warning = "Shorter day off than usual — study time is reduced today.";
      mainBlock.dur = Math.max(0, remaining);
      freeBlock.dur = 0;
    } else if (remaining > (mainBlock.max ?? Infinity)) {
      mainBlock.dur = mainBlock.max ?? remaining;
      freeBlock.dur = remaining - (mainBlock.max ?? 0);
    } else {
      mainBlock.dur = remaining;
      freeBlock.dur = 0;
    }
  }

  let cursor = freeFrom;
  const timeline = blocks
    .filter((b) => b.dur > 0)
    .map((b) => {
      const start = cursor;
      const end = cursor + b.dur;
      cursor = end;
      return { key: b.key, label: b.label, start: fmtMin(start), end: fmtMin(end) };
    });

  return { timeline, warning };
}
