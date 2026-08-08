from contextvars import ContextVar
from typing import Optional

# Contextual variables for Request ID and Correlation ID tracing
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
