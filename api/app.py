from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.config import settings
from api.middleware import setup_middleware
from api.exceptions import AegisSwarmAPIException, aegisswarm_exception_handler
from api.routers import (
    health_router,
    version_router,
    plugins_router,
    ingest_router,
    dashboard_router,
    corpus_router,
    search_router,
    reports_router,
    campaigns_router,
    telemetry_router,
    cluster_router,
    learning_router,
    reasoning_router,
    orchestrator_router,
    research_router,
    assets_router,
    experiments_router,
    live_router
)
from api.dependencies import get_plugin_registry
from logging import get_api_logger

logger = get_api_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager handling application startup and shutdown events.
    """
    logger.info(f"Starting AegisSwarm API service layer v{settings.app_version}...")
    registry = get_plugin_registry()
    logger.info(f"Discovered {len(registry.list_plugins())} dataset plugins.")
    
    yield
    
    logger.info("Shutting down AegisSwarm API service layer cleanly.")


def create_app() -> FastAPI:
    """
    Factory function instantiating and configuring the FastAPI application instance.
    """
    tags_metadata = [
        {"name": "Health & Status", "description": "Operational health, version, and status endpoints."},
        {"name": "Dashboard", "description": "Aggregate Data Lake command center metrics."},
        {"name": "Dataset Plugins", "description": "Ingestion dataset plugin discovery and metadata inspection."},
        {"name": "Pipeline Ingestion", "description": "Non-blocking background job submission and progress monitoring."},
        {"name": "Corpus Subsystem", "description": "Data Lake partitions, statistics, coverage, quality, and integrity endpoints."},
        {"name": "Search Engine", "description": "Streaming data lake query engine."},
        {"name": "Reports Engine", "description": "Publication research report generation and metadata."}
    ]

    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        version=settings.app_version,
        openapi_tags=tags_metadata,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # Setup Middleware & Exception Handlers
    setup_middleware(app)
    app.add_exception_handler(AegisSwarmAPIException, aegisswarm_exception_handler)

    # Register Routers
    app.include_router(health_router)
    app.include_router(version_router)
    app.include_router(plugins_router, prefix="/api/v1")
    app.include_router(ingest_router, prefix="/api/v1")
    app.include_router(dashboard_router, prefix="/api/v1")
    app.include_router(corpus_router, prefix="/api/v1")
    app.include_router(search_router, prefix="/api/v1")
    app.include_router(reports_router, prefix="/api/v1")
    app.include_router(campaigns_router, prefix="/api/v1")
    app.include_router(telemetry_router, prefix="/api/v1")
    app.include_router(cluster_router, prefix="/api/v1")
    app.include_router(learning_router, prefix="/api/v1")
    app.include_router(reasoning_router, prefix="/api/v1")
    app.include_router(orchestrator_router, prefix="/api/v1")
    app.include_router(research_router, prefix="/api/v1")
    app.include_router(assets_router, prefix="/api/v1")
    app.include_router(experiments_router, prefix="/api/v1")
    app.include_router(live_router, prefix="/api/v1")

    return app

app = create_app()
