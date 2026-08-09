from api.routers.health import router as health_router
from api.routers.version import router as version_router
from api.routers.plugins import router as plugins_router
from api.routers.ingest import router as ingest_router
from api.routers.dashboard import router as dashboard_router
from api.routers.corpus import router as corpus_router
from api.routers.search import router as search_router
from api.routers.reports import router as reports_router
from api.routers.campaigns import campaigns_router
from api.routers.telemetry import telemetry_router
from api.routers.cluster import cluster_router
from api.routers.learning import learning_router
from api.routers.reasoning import reasoning_router
from api.routers.orchestrator import orchestrator_router
from api.routers.research import research_router
from api.routers.assets import assets_router
from api.routers.experiments import experiments_router
from api.routers.live import live_router

__all__ = [
    "health_router",
    "version_router",
    "plugins_router",
    "ingest_router",
    "dashboard_router",
    "corpus_router",
    "search_router",
    "reports_router",
    "campaigns_router",
    "telemetry_router",
    "cluster_router",
    "learning_router",
    "reasoning_router",
    "orchestrator_router",
    "research_router",
    "assets_router",
    "experiments_router",
    "live_router"
]
