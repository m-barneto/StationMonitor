import asyncio
from datetime import datetime
import time
from zoneinfo import ZoneInfo

from utils.config import Config


class SleepManager:
    async def loop(self) -> None:
        while True:
            print("Open:", self.is_site_open())
            if self.is_site_open():
                # if we're open then wait async
                await asyncio.sleep(Config.get()["sleep"]["sleepInterval"])
            else:
                # not open, wait syncronously
                time.sleep(Config.get()["sleep"]["sleepInterval"])

    def is_site_open(self) -> bool:
        # get timezone in config
        timezone = ZoneInfo(Config.get()["sleep"]["timezone"])
        # Get open and close time as datetime.time
        open_time = datetime.strptime(
            Config.get()["sleep"]["openTime"], "%H:%M").time()
        close_time = datetime.strptime(
            Config.get()["sleep"]["closeTime"], "%H:%M").time()
        current_time = datetime.now(timezone).time()

        return open_time <= current_time and current_time <= close_time
