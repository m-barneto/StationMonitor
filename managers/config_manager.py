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
            await asyncio.sleep(int(Config.conf["updateConfigInterval"]) * 60)

    @staticmethod
    async def update_config() -> None:
        try:
            with open("config.jsonc", "r", encoding="utf-8") as file:
                jsonc_content = file.read()
            remote_config = pyjson5.loads(jsonc_content)
            orig = deepcopy(Config.conf)
            Config.conf = remote_config
            Config.conf["sensors"] = orig["sensors"]
        except FileNotFoundError:
            print("Error: 'config.jsonc' file is not found.")
            # sleep for a bit to avoid spamming when local config file isn't found
            await asyncio.sleep(60)
        except Exception as e:
            print(f"An error occured when loading local jsonc config file: {e}")
            # sleep for a bit to avoid spamming if another error does occur when loading config jsonc file
            await asyncio.sleep(60)
