import os
import sys
import importlib.util

# 1. Bootstrap Python standard library logging cleanly from sys.prefix with dual __path__
if not hasattr(sys.modules.get("logging"), "Formatter"):
    pkg_dir = os.path.dirname(__file__)
    if os.name == 'nt':
        std_log_dir = os.path.join(sys.prefix, "Lib", "logging")
    else:
        py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
        std_log_dir = os.path.join(sys.prefix, "lib", py_ver, "logging")

    std_log_path = os.path.join(std_log_dir, "__init__.py")
    spec = importlib.util.spec_from_file_location("logging", std_log_path)
    std_log = importlib.util.module_from_spec(spec)
    std_log.__path__ = [pkg_dir, std_log_dir]
    sys.modules["logging"] = std_log
    spec.loader.exec_module(std_log)

    std_hnd_path = os.path.join(std_log_dir, "handlers.py")
    h_spec = importlib.util.spec_from_file_location("logging.handlers_std", std_hnd_path)
    std_hnd = importlib.util.module_from_spec(h_spec)
    sys.modules["logging.handlers_std"] = std_hnd
    h_spec.loader.exec_module(std_hnd)
else:
    std_log = sys.modules["logging"]

# 2. Import custom AegisSwarm components
from .context import request_id_var, correlation_id_var
from .formatters import StructuredJSONFormatter
from .handlers import get_rotating_json_handler, get_console_handler
from .logger import (
    setup_logging,
    get_logger,
    get_api_logger,
    get_pipeline_logger,
    get_ingestion_logger,
    get_error_logger
)

# Attach AegisSwarm components to std_log
std_log.setup_logging = setup_logging
std_log.get_logger = get_logger
std_log.get_api_logger = get_api_logger
std_log.get_pipeline_logger = get_pipeline_logger
std_log.get_ingestion_logger = get_ingestion_logger
std_log.get_error_logger = get_error_logger
std_log.request_id_var = request_id_var
std_log.correlation_id_var = correlation_id_var
std_log.StructuredJSONFormatter = StructuredJSONFormatter
std_log.get_rotating_json_handler = get_rotating_json_handler
std_log.get_console_handler = get_console_handler

__all__ = [
    "setup_logging",
    "get_logger",
    "get_api_logger",
    "get_pipeline_logger",
    "get_ingestion_logger",
    "get_error_logger",
    "request_id_var",
    "correlation_id_var",
    "StructuredJSONFormatter",
    "get_rotating_json_handler",
    "get_console_handler"
]
