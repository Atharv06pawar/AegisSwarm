from typing import List
from fastapi import APIRouter, Depends, status
from api.dependencies import get_plugin_service
from api.services.plugin_service import PluginService
from api.schemas.responses import PluginListResponse, PluginMetadataResponse
from api.exceptions import PluginNotFoundException

router = APIRouter(prefix="/plugins", tags=["Dataset Plugins"])

@router.get(
    "",
    response_model=PluginListResponse,
    summary="List all discovered dataset plugins",
    description="Returns metadata for all dataset plugins registered in the AegisSwarm engine."
)
async def list_plugins(
    service: PluginService = Depends(get_plugin_service)
) -> PluginListResponse:
    """
    Returns list of all available dataset plugins and metadata.
    """
    metadata_list = service.list_plugins()
    plugin_responses: List[PluginMetadataResponse] = []

    for meta in metadata_list:
        plugin_responses.append(
            PluginMetadataResponse(
                dataset_id=meta.dataset_id,
                description=meta.description or "No description provided.",
                license_name=meta.license.name.value if hasattr(meta.license.name, "value") else str(meta.license.name),
                license_url=meta.license.url,
                parser_version="1.0.0"
            )
        )

    return PluginListResponse(
        total_count=len(plugin_responses),
        plugins=plugin_responses
    )


@router.get(
    "/{plugin_id}",
    response_model=PluginMetadataResponse,
    summary="Get plugin metadata by dataset ID",
    description="Retrieves detailed metadata for a specific dataset plugin."
)
async def get_plugin_metadata(
    plugin_id: str,
    service: PluginService = Depends(get_plugin_service)
) -> PluginMetadataResponse:
    """
    Retrieves metadata for a specific plugin or raises HTTP 404 error if not found.
    """
    plugin_instance = service.get_plugin(plugin_id)
    if not plugin_instance:
        raise PluginNotFoundException(plugin_id=plugin_id)

    meta = plugin_instance.metadata()
    return PluginMetadataResponse(
        dataset_id=meta.dataset_id,
        description=meta.description or "No description provided.",
        license_name=meta.license.name.value if hasattr(meta.license.name, "value") else str(meta.license.name),
        license_url=meta.license.url,
        parser_version=plugin_instance.parser_version
    )


@router.post(
    "/discover",
    response_model=PluginListResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger dynamic dataset plugin discovery",
    description="Rescans the plugins/datasets/ directory and registers newly discovered plugin modules."
)
async def discover_plugins(
    service: PluginService = Depends(get_plugin_service)
) -> PluginListResponse:
    """
    Triggers dynamic plugin discovery and returns updated plugin list.
    """
    service.discover_plugins()
    return await list_plugins(service=service)
