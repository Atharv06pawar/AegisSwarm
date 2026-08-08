import sys
from pathlib import Path

std_handlers = sys.modules.get("logging.handlers_std")
if std_handlers and hasattr(std_handlers, "RotatingFileHandler"):
    RotatingFileHandler = std_handlers.RotatingFileHandler
else:
    import logging.handlers as _h
    RotatingFileHandler = _h.RotatingFileHandler

std_logging = sys.modules["logging"]

def get_rotating_json_handler(
    filepath: str, 
    level: int = std_logging.INFO, 
    max_bytes: int = 10 * 1024 * 1024, # 10MB per file
    backup_count: int = 5
):
    """
    Constructs a RotatingFileHandler using StructuredJSONFormatter.
    Automates log rotation and retention policies.
    """
    from logging.formatters import StructuredJSONFormatter
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        filename=str(path),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    handler.setLevel(level)
    handler.setFormatter(StructuredJSONFormatter())
    return handler

def get_console_handler(level: int = std_logging.INFO):
    """
    Constructs a StreamHandler for stdout using StructuredJSONFormatter.
    """
    from logging.formatters import StructuredJSONFormatter
    handler = std_logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(StructuredJSONFormatter())
    return handler
