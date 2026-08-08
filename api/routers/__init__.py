from api.routers.health import router as health_router
from api.routers.version import router as version_router
from api.routers.plugins import router as plugins_router
from api.routers.ingest import router as ingest_router
from api.routers.dashboard import router as dashboard_router
from api.routers.corpus import router as corpus_router
from api.routers.search import router as search_router
from api.routers.reports import router as reports_router

__all__ = [
    "health_router",
    "version_router",
    "plugins_router",
    "ingest_router",
    "dashboard_router",
    "corpus_router",
    "search_router",
    "reports_router"
]
