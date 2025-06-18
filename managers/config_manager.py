import asyncio
from copy import deepcopy

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
            await asyncio.sleep(int(Config.conf.updateConfigInterval) * 60)

    @staticmethod
    async def update_config() -> None:
        try:
            res = requests.get("http://192.168.17.202/config.jsonc")
            remote_config = pyjson5.loads(res.text)
            orig = deepcopy(Config.conf)

            Config.conf = remote_config
            Config.conf.distanceSensors = orig.distanceSensors
            Config.conf.reflectiveSensors = orig.reflectiveSensors
            Config.conf.longDistanceSensors = orig.longDistanceSensors
        except requests.exceptions.ConnectionError as e:
            # sleep for a bit to avoid spamming a downed proxy
            await asyncio.sleep(60)
