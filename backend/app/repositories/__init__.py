"""Data-access layer — the ONLY place that reads from or writes to MongoDB.

Every function here takes/returns plain values or Pydantic models and hides the
database behind that. Routers call these functions; they never build a query
themselves. That boundary is what lets you reason about "how data is stored"
entirely within this folder — and swap MongoDB for something else later by
rewriting only these files.
"""
