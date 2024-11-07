import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from utils.config import Config


class SleepManager:
    async def loop(self) -> None:
        self.is_site_open()
        await asyncio.sleep(5)

    def is_site_open(self) -> bool:
        # get timezone in config
        timezone = ZoneInfo(Config.get()["sleep"]["timezone"])
        # Get open and close time as datetime.time
        open_time = datetime.strptime(
            Config.get()["sleep"]["openTime"], "%H:%M").time()
        close_time = datetime.strptime(
            Config.get()["sleep"]["closeTime"], "%H:%M").time()

        print("open", open_time)
        print("close", close_time)

        return False
