# /backend/app/core/logging_config.py
# v1.5.5 - Structured Logging Configuration
# "Debugging is twice as hard as writing the code in the first place."

"""
Structured Logging Setup
Replaces print() statements with proper logging for production monitoring.
"""

import logging
import sys
from datetime import datetime, timezone
from backend.app.core.utils import utcnow
from typing import Optional

# Custom formatter for structured logs


class StructuredFormatter(logging.Formatter):
    """
    Formats log messages with timestamp, level, module, and message.
    Makes logs easier to parse and search.
    """

    def format(self, record):
        # Add timestamp
        record.timestamp = utcnow().isoformat()

        # Add request ID if available (set by middleware)
        if not hasattr(record, 'request_id'):
            record.request_id = 'N/A'

        # Format: [TIMESTAMP] [LEVEL] [MODULE] [REQUEST_ID] Message
        log_format = '[%(timestamp)s] [%(levelname)s] [%(name)s] [%(request_id)s] %(message)s'
        formatter = logging.Formatter(log_format)
        return formatter.format(record)


def setup_logging(debug: bool = False):
    """
    Configure application-wide logging.

    Args:
        debug: If True, set log level to DEBUG, otherwise INFO
    """

    # Set log level
    log_level = logging.DEBUG if debug else logging.INFO

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(StructuredFormatter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Create application logger
    app_logger = logging.getLogger("SoulLink")
    app_logger.info(
        f"[OK] Logging initialized (level: {logging.getLevelName(log_level)})")

    return app_logger


# Convenience function for getting loggers
def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(f"SoulLink.{name}")


class LegionLogger:
    """
    Specialized logger for engine-specific events.
    Replaces the legacy core/logger.py.
    """

    @staticmethod
    def log_brain_thought(soul_id: str, prompt: str):
        logger = get_logger("Brain")
        logger.debug(
            "\n\U0001f9e0 [BRAIN THOUGHT - %s]\n%s\n%s\n%s",
            soul_id, "-" * 50, prompt, "-" * 50
        )

    @staticmethod
    def log_gatekeeper(action: str, allowed: bool):
        logger = get_logger("Gatekeeper")
        status = "\u2705 ALLOWED" if allowed else "\U0001f6ab BLOCKED"
        logger.info("\U0001f6e1\ufe0f [GATEKEEPER] %s: %s", action, status)
