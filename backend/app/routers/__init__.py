"""HTTP endpoint layer.

Each module here is a FastAPI ``APIRouter`` grouping related endpoints. Routers are
thin on purpose: they validate/shape input and output (via the Pydantic models) and
delegate all data access to the ``repositories`` package. If you find database query
code creeping into a router, it belongs in a repository instead.
"""
