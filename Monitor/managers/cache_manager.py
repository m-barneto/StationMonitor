import asyncio
from utils.config import Config

class CacheManager:
    def __init__(self):
        pass

    async def loop(self) -> None:
        while True:
            await asyncio.sleep(1)