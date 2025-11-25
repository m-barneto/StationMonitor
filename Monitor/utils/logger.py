import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

logger = logging.getLogger("StationMonitor")
logger.setLevel(logging.INFO)

Path("/logs/").mkdir(parents=True, exist_ok=True)

# Create a file handler that logs messages to a file with rotation
handler = RotatingFileHandler(
    "logs/station_monitor.log", maxBytes=1024 * 1024, backupCount=5
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

logger.addHandler(handler)

# Export the logger for use in other modules
__all__ = ["logger"]
