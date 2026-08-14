"""Schemas for the curriculum — the study material seeded into the database.

In the original HTML these lived as hard-coded JavaScript arrays (MATH, DSA,
PYTHON, ...). Here they become typed documents stored in MongoDB and served over
the API, which is what makes the lesson resources persistent and editable without
shipping a new frontend.
"""

from pydantic import BaseModel


class Resource(BaseModel):
    """A single external learning link (name + URL).

    Mirrors the ``R(name, url)`` helper from the original page. Modelling it
    explicitly (rather than a loose dict) means a malformed resource is caught at
    seed time, not when a user clicks a broken link.
    """

    name: str
    url: str


class Lesson(BaseModel):
    """One module within a track.

    Field names are kept terse to match the source data verbatim:
    ``t`` = title, ``f`` = focus/description, ``res`` = its list of resources.
    Keeping the original keys makes it obvious this is a faithful port and avoids
    a translation layer during seeding.
    """

    t: str
    f: str
    res: list[Resource] = []


class Track(BaseModel):
    """A full learning track (e.g. Python) or the Projects list.

    ``kind`` distinguishes an ordinary lesson track from the Sunday projects list,
    which the frontend renders differently. ``day`` records the weekday this track
    surfaces as the "main focus" (e.g. Python on Monday); daily tracks use
    "Daily". This is the exact metadata the dial and roadmap views need.
    """

    key: str          # stable identifier, e.g. "python" or "projects"
    label: str        # human label, e.g. "Python"
    day: str          # weekday it appears, e.g. "Monday" / "Daily" / "Sunday"
    icon: str         # emoji/glyph shown in the UI
    kind: str         # "track" for lesson tracks, "projects" for the project list
    lessons: list[Lesson]
