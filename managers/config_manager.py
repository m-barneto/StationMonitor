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
        try:
            res = requests.get("http://192.168.17.202/config.jsonc")
            remote_config = pyjson5.loads(res.text)
            Config.conf["leds"] = remote_config["leds"]
        except requests.exceptions.ConnectionError as e:
            # sleep for a bit to avoid spamming a downed proxy
            await asyncio.sleep(10 * 60)
