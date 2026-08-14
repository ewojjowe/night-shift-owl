"""Pydantic schemas — the typed "shape" of everything crossing the API boundary.

These models do double duty: FastAPI uses them to validate incoming JSON and to
serialize outgoing responses, and they generate the OpenAPI docs at /docs. Splitting
"input" models (what a client may send) from "output" models (what we return) is a
deliberate safety habit — e.g. a client can send a password but can never read a
stored hash back, because no output model contains that field.
"""
