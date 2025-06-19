import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("StationMonitor")
logger.setLevel(logging.INFO)

# Create a file handler that logs messages to a file with rotation
handler = RotatingFileHandler(
    "logs/station_monitor.log", maxBytes=1024 * 1024, backupCount=5
)
handler.setLevel(logging.INFO)

logger.addHandler(handler)

# Export the logger for use in other modules
__all__ = ["logger"]
