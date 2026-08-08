from datetime import datetime, timezone
from typing import Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse

class AegisSwarmAPIException(Exception):
    """
    Base exception class for all AegisSwarm API service layer exceptions.
    """
    def __init__(self, detail: str, code: str = "INTERNAL_ERROR", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.detail = detail
        self.code = code
        self.status_code = status_code
        super().__init__(detail)


class PluginNotFoundException(AegisSwarmAPIException):
    """
    Exception raised when a requested dataset plugin is not found in the registry.
    """
    def __init__(self, plugin_id: str):
        super().__init__(
            detail=f"Dataset plugin '{plugin_id}' was not found in the AegisSwarm registry.",
            code="PLUGIN_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )


class InternalServerException(AegisSwarmAPIException):
    """
    Exception raised when an unhandled server error occurs during processing.
    """
    def __init__(self, detail: str = "An internal server error occurred."):
        super().__init__(
            detail=detail,
            code="INTERNAL_SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def aegisswarm_exception_handler(request: Request, exc: AegisSwarmAPIException) -> JSONResponse:
    """
    Global exception handler converting AegisSwarmAPIException into structured JSON responses.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "code": exc.code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path)
        }
    )
