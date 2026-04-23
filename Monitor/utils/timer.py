import asyncio

from periphery import GPIO

class Timer:
    def __init__(self, zone: str, pin_start: int, pin_reset: int):
        self.zone = zone
        self.start_io = GPIO(pin_start, "out")
        self.reset_io = GPIO(pin_reset, "out")

        self.start_io.write(False)
        self.reset_io.write(False)

    async def start(self):
        self.start_io.write(True)
        await asyncio.sleep(0.25)
        self.start_io.write(False)

    async def reset(self):
        self.reset_io.write(True)
        await asyncio.sleep(0.25)
        self.reset_io.write(False)