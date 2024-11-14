import asyncio

import pyjson5
import requests

from utils.config import Config


class ConfigManager:
    def __init__(self) -> None:
        pass

    async def loop(self) -> None:
        while True:
            await ConfigManager.update_config()
            # Every 10 minutes
            await asyncio.sleep(10 * 60)

    @staticmethod
    async def update_config() -> None:
        try:
            res = requests.get("http://192.168.17.202/config.jsonc")
            print("Updating config")
            remote_config = pyjson5.loads(res.text)
            Config.conf["leds"] = remote_config["leds"]
            Config.conf["sleep"] = remote_config["sleep"]
        except requests.exceptions.ConnectionError as e:
            # sleep for a bit to avoid spamming a downed proxy
            await asyncio.sleep(10 * 60)
