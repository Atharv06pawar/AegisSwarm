import json
import traceback
from datetime import datetime, timezone
from typing import Dict, Any
from .stdlib_logging import std_logging
from .context import request_id_var, correlation_id_var

class StructuredJSONFormatter(std_logging.Formatter):
    """
    Production JSON log formatter producing structured, machine-readable logs.
    Includes timestamps, severity levels, request IDs, correlation IDs, exception stacks,
    and performance timing metadata.
    """

    def format(self, record: std_logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread
        }

        req_id = getattr(record, "request_id", request_id_var.get(None))
        corr_id = getattr(record, "correlation_id", correlation_id_var.get(None))

        if req_id:
            log_data["request_id"] = req_id
        if corr_id:
            log_data["correlation_id"] = corr_id

        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        extra_data = {}
        for key, val in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process", "request_id", "correlation_id", "duration_ms"
            ):
                extra_data[key] = val

        if extra_data:
            log_data["extra"] = extra_data

        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "UnknownException",
                "message": str(record.exc_info[1]),
                "stacktrace": traceback.format_exception(*record.exc_info)
            }

        return json.dumps(log_data)
