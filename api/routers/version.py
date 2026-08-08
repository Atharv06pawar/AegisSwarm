from fastapi import APIRouter
from api.config import settings
from api.schemas.responses import VersionResponse

router = APIRouter(tags=["Health & Status"])

@router.get(
    "/version",
    response_model=VersionResponse,
    summary="Get system version details",
    description="Returns platform application name, core semantic version, and AUAO ontology specification version."
)
async def get_version() -> VersionResponse:
    """
    Returns system version information.
    """
    return VersionResponse(
        name=settings.app_title,
        version=settings.app_version,
        ontology_version="1.0.0",
        environment="production"
    )
