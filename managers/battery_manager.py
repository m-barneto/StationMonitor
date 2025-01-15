import asyncio
from datetime import datetime
import time
from zoneinfo import ZoneInfo

from managers.config_manager import ConfigManager
from utils.config import Config


class BatteryManager:
    def __init__(self):
        pass

    async def loop(self) -> None:
        while True:
            # Get battery status and send it to event server, no need to deal with queues

            # sleep for configurable time
            pass
