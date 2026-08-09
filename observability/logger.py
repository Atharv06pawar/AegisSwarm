"""
StructuredLogger module for emitting structured JSON log outputs.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class StructuredLogger:
    """
    Structured logger outputting JSON log dictionaries for system observability.
    """

    def __init__(self, component: str = "general"):
        self.component = component

    def log(
        self,
        level: str,
        message: str,
        session_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        provider: Optional[str] = None,
        agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Emits a structured JSON log payload.
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.upper(),
            "component": self.component,
            "session": session_id or "none",
            "campaign": campaign_id or "none",
            "execution": execution_id or "none",
            "provider": provider or "none",
            "agent": agent or "none",
            "message": message,
            "metadata": metadata or {}
        }
        
        json_output = json.dumps(entry)
        
        # Route to Python logging module according to level
        lvl_upper = level.upper()
        if lvl_upper == "DEBUG":
            logger.debug(json_output)
        elif lvl_upper == "WARNING":
            logger.warning(json_output)
        elif lvl_upper == "ERROR":
            logger.error(json_output)
        elif lvl_upper == "CRITICAL":
            logger.critical(json_output)
        else:
            logger.info(json_output)

        return entry

    def debug(self, message: str, **kwargs) -> Dict[str, Any]:
        return self.log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs) -> Dict[str, Any]:
        return self.log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs) -> Dict[str, Any]:
        return self.log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs) -> Dict[str, Any]:
        return self.log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs) -> Dict[str, Any]:
        return self.log("CRITICAL", message, **kwargs)
