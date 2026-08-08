from pathlib import Path
from .stdlib_logging import std_logging
from .context import request_id_var, correlation_id_var
from .handlers import get_rotating_json_handler, get_console_handler

_logging_initialized = False

def setup_logging(log_dir: str = "logs", level: int = std_logging.INFO) -> None:
    """
    Initializes AegisSwarm structured production logging infrastructure.
    Configures channel routing to api.log, pipeline.log, ingestion.log, and errors.log.
    """
    global _logging_initialized
    if _logging_initialized:
        return

    base_dir = Path(log_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    # 1. API Channel Handler -> logs/api.log
    api_handler = get_rotating_json_handler(str(base_dir / "api.log"), level=level)
    api_logger = std_logging.getLogger("aegisswarm.api")
    api_logger.setLevel(level)
    api_logger.addHandler(api_handler)
    api_logger.propagate = False

    # 2. Pipeline Channel Handler -> logs/pipeline.log
    pipeline_handler = get_rotating_json_handler(str(base_dir / "pipeline.log"), level=level)
    pipeline_logger = std_logging.getLogger("aegisswarm.pipeline")
    pipeline_logger.setLevel(level)
    pipeline_logger.addHandler(pipeline_handler)
    pipeline_logger.propagate = False

    # 3. Ingestion Channel Handler -> logs/ingestion.log
    ingestion_handler = get_rotating_json_handler(str(base_dir / "ingestion.log"), level=level)
    ingestion_logger = std_logging.getLogger("aegisswarm.ingestion")
    ingestion_logger.setLevel(level)
    ingestion_logger.addHandler(ingestion_handler)
    ingestion_logger.propagate = False

    # 4. Error Channel Handler -> logs/errors.log (Filters level >= ERROR)
    error_handler = get_rotating_json_handler(str(base_dir / "errors.log"), level=std_logging.ERROR)
    error_logger = std_logging.getLogger("aegisswarm.errors")
    error_logger.setLevel(std_logging.ERROR)
    error_logger.addHandler(error_handler)
    error_logger.propagate = False

    # Root Logger Configuration
    root_logger = std_logging.getLogger()
    root_logger.setLevel(level)
    
    # Attach console output and error handler to root
    console_h = get_console_handler(level=level)
    root_logger.addHandler(console_h)
    root_logger.addHandler(error_handler)

    _logging_initialized = True

def get_logger(name: str = "aegisswarm"):
    """
    Returns a configured logger instance. Ensures logging setup is initialized.
    """
    setup_logging()
    return std_logging.getLogger(name)

# Specialized Channel Loggers
def get_api_logger():
    return get_logger("aegisswarm.api")

def get_pipeline_logger():
    return get_logger("aegisswarm.pipeline")

def get_ingestion_logger():
    return get_logger("aegisswarm.ingestion")

def get_error_logger():
    return get_logger("aegisswarm.errors")
