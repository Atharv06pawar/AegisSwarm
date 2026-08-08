from datetime import datetime, timezone
from fastapi import APIRouter
from api.config import settings
from api.schemas.responses import HealthResponse

router = APIRouter(tags=["Health & Status"])

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API health status",
    description="Returns system operational status, UTC timestamp, and application version."
)
async def get_health() -> HealthResponse:
    """
    Returns API health status.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version=settings.app_version
    )
