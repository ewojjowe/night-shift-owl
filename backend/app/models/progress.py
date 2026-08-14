"""Schemas for a user's progress + shift configuration.

This is the server-side home of what the original page kept in ``STATE`` and saved
to ``window.storage``. One ``ProgressState`` document exists per user and captures:

* how far they've advanced in each track (the ``idx`` counters),
* their recurring weekly shift schedule,
* their days-off wake/wind-down defaults,
* one-off "today is different" overrides, and
* which UI sections they like expanded.

The shift-timeline *maths* is NOT here — that stays in the frontend, because it is
pure presentation derived from this config. The backend only persists the inputs.
"""

from pydantic import BaseModel, Field

# The seven learning tracks, in the order the UI presents them. This is the single
# source of truth for "which tracks exist"; the default-progress builder and the
# reset endpoint both derive from it, so adding a track is a one-line change.
TRACK_KEYS: list[str] = ["math", "dsa", "python", "aiml", "go", "sysdesign", "aieng"]

# Which section ids the frontend remembers the open/closed state of. Mirrors the
# ``uiOpen`` object in the original HTML.
UI_SECTION_DEFAULTS: dict[str, bool] = {
    "secShift": False,
    "secTimeline": False,
    "secHabits": True,
    "secFocus": True,
    "secRoadmap": False,
}


class TrackProgress(BaseModel):
    """How far a user has advanced within one track.

    ``idx`` is the zero-based index of the *current* module: everything before it
    is done, everything at/after it is upcoming. "Mark complete" simply increments
    it. A single-field model may look like overkill, but it documents intent and
    leaves room to add fields later (e.g. a ``completed_at`` timestamp) without a
    migration of the surrounding shape.
    """

    idx: int = 0


class ShiftDay(BaseModel):
    """The shift configuration for one day.

    When ``working`` is True the user is on shift, and their *free* window runs
    from ``shift_end`` (when the shift finishes) to ``shift_start`` (when the next
    one begins). When False it's a day off and the off-day defaults apply instead.
    Times are simple ``"HH:MM"`` 24-hour strings, matching an ``<input type=time>``.
    """

    working: bool = False
    shift_end: str = "08:00"
    shift_start: str = "22:00"


class OffDayDefaults(BaseModel):
    """Wake and wind-down times used to shape the timeline on days off."""

    wake: str = "08:00"
    bedtime: str = "00:00"


class ProgressState(BaseModel):
    """A user's complete, persisted progress + schedule document.

    This is what ``GET /progress`` returns. ``default_factory`` callables build the
    nested defaults so a brand-new user gets a fully-formed document (day 1, nothing
    completed, a Mon–Fri night-shift template) without any special-casing elsewhere.
    """

    start_date: str  # ISO "YYYY-MM-DD"; anchors the "Day N" counter in the header
    tracks: dict[str, TrackProgress]
    projects: TrackProgress = Field(default_factory=TrackProgress)
    shift_template: dict[str, ShiftDay]  # keys "0".."6" (Sun..Sat), JSON-object friendly
    off_day_defaults: OffDayDefaults = Field(default_factory=OffDayDefaults)
    shift_overrides: dict[str, ShiftDay] = Field(default_factory=dict)  # keyed by date
    ui_open: dict[str, bool] = Field(default_factory=lambda: dict(UI_SECTION_DEFAULTS))


class ProgressUpdate(BaseModel):
    """Payload for ``PUT /progress`` — the config a user is allowed to edit directly.

    Deliberately a *subset* of ``ProgressState``: it excludes the ``idx`` counters
    and ``start_date``, because progress may only advance through the dedicated
    "mark complete" endpoint (you can't skip ahead by editing JSON). Every field is
    optional so the frontend can send a partial update (e.g. just ``ui_open``) and
    the repository patches only what changed.
    """

    shift_template: dict[str, ShiftDay] | None = None
    off_day_defaults: OffDayDefaults | None = None
    shift_overrides: dict[str, ShiftDay] | None = None
    ui_open: dict[str, bool] | None = None
