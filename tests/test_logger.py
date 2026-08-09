import pytest
from observability.logger import StructuredLogger


def test_structured_logger_levels():
    """Verify StructuredLogger emits structured JSON log entries across levels."""
    logger = StructuredLogger(component="test_component")

    entry_info = logger.info("Test info message", session_id="sess-1", provider="openai")
    assert entry_info["level"] == "INFO"
    assert entry_info["component"] == "test_component"
    assert entry_info["session"] == "sess-1"
    assert entry_info["provider"] == "openai"

    entry_debug = logger.debug("Test debug")
    assert entry_debug["level"] == "DEBUG"

    entry_warn = logger.warning("Test warn")
    assert entry_warn["level"] == "WARNING"

    entry_err = logger.error("Test error")
    assert entry_err["level"] == "ERROR"

    entry_crit = logger.critical("Test critical")
    assert entry_crit["level"] == "CRITICAL"
