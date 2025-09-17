import asyncio
from datetime import datetime
import time
from zoneinfo import ZoneInfo

from managers.config_manager import ConfigManager
from utils.config import Config


class SleepManager:
    def __init__(self):
        SleepManager.is_open = self.is_site_open()

    async def loop(self) -> None:
        while True:
            # Update is_open class variable
            SleepManager.is_open = self.is_site_open()
            # Sleep for configured amount of time
            await asyncio.sleep(Config.get().sleep.sleepInterval)

    def is_site_open(self) -> bool:
        # get timezone in config
        timezone = ZoneInfo(Config.get().sleep.timezone)
        # Get open and close time as datetime.time
        open_time = datetime.strptime(
            Config.get().sleep.openTime, "%H:%M").time()
        close_time = datetime.strptime(
            Config.get().sleep.closeTime, "%H:%M").time()
        current_time = datetime.now(timezone).time()
        return open_time <= current_time <= close_time

    def get_local_time(self) -> str:
        # get timezone in config
        timezone = ZoneInfo(Config.get().sleep.timezone)
        # Get open and close time as datetime.time
        return datetime.now(timezone).time().strftime("%H:%M")
