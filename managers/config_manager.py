import asyncio

import pyjson5

from utils.config import Config


class ConfigManager:
    def __init__(self) -> None:
        pass

    async def loop(self) -> None:
        while True:
            await self.update_config()
            # Every 10 seconds
            await asyncio.sleep(1)  # 0 * 60

    async def update_config(self) -> None:
        print("Updating config")
        with open("./config.jsonc", encoding="utf-8") as f:
            remote_config = pyjson5.load(f)
            Config.conf["leds"] = remote_config["leds"]
