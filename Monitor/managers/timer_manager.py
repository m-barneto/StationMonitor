import asyncio

from utils.config import Config
from utils.timer import Timer


class TimerManager:
    def __init__(self):
        self.timers: dict[str, Timer] = {}

        timers = Config.get().timers

        for timer_cfg in timers:
            zone = timer_cfg["zone"]
            self.timers[zone] = Timer(
                zone,
                timer_cfg["pinStart"],
                timer_cfg["pinReset"]
            )
    
    async def loop(self) -> None:
        for timer in self.timers.values():
            await timer.reset()
            await asyncio.sleep(1)

    def get(self, zone: str) -> Timer | None:
        return self.timers.get(zone)

    def has(self, zone: str) -> bool:
        return zone in self.timers