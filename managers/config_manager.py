import asyncio

import pyjson5
import requests

from utils.config import Config


class ConfigManager:
    def __init__(self) -> None:
        pass

    async def loop(self) -> None:
        while True:
            await self.update_config()
            # Every 10 minutes
            await asyncio.sleep(10 * 60)

    async def update_config(self) -> None:
        print("Updating config")
        res = requests.get("http://192.168.17.202/config.jsonc")
        print("response", res)
        remote_config = pyjson5.loads(res.text)
        print("config", remote_config)
        Config.conf["leds"] = remote_config["leds"]
