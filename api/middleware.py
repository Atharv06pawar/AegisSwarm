import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.config import settings
from logging import get_api_logger, request_id_var, correlation_id_var

api_logger = get_api_logger()

def setup_middleware(app: FastAPI) -> None:
    """
    Registers CORS, Request-ID tracing, performance timing, and structured API logging middleware.
    """
    # 1. CORS Middleware Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Context Tracing & Timing Middleware
    @app.middleware("http")
    async def process_tracing_and_timing(request: Request, call_next):
        start_time = time.perf_counter()

        # Extract or generate Request ID & Correlation ID
        req_id = request.headers.get("X-Request-ID", f"req_{uuid.uuid4().hex[:12]}")
        corr_id = request.headers.get("X-Correlation-ID", f"corr_{uuid.uuid4().hex[:12]}")

        # Set ContextVars for logger formatters
        token_req = request_id_var.set(req_id)
        token_corr = correlation_id_var.set(corr_id)

        try:
            response = await call_next(request)
            
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Correlation-ID"] = corr_id
            response.headers["X-Process-Time-MS"] = str(elapsed_ms)

            # Structured API Log entry
            api_logger.info(
                f"{request.method} {request.url.path} - HTTP {response.status_code} ({elapsed_ms} ms)",
                extra={
                    "http_method": request.method,
                    "url_path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": elapsed_ms,
                    "client_host": request.client.host if request.client else "unknown"
                }
            )

            return response
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            api_logger.error(
                f"Unhandled Exception in {request.method} {request.url.path}: {exc}",
                exc_info=True,
                extra={
                    "http_method": request.method,
                    "url_path": request.url.path,
                    "duration_ms": elapsed_ms
                }
            )
            raise exc
        finally:
            request_id_var.reset(token_req)
            correlation_id_var.reset(token_corr)
