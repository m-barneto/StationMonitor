import asyncio
from functools import partial
import json

import requests

from managers.server_manager import ServerManager
from utils.config import Config

class HealthManager:

    def __init__(self):
        pass

    async def loop(self) -> None:
        loop = asyncio.get_event_loop()
        while True:
            try:
                # Sends the request while still allowing other loops to continue running
                res = await loop.run_in_executor(None, partial(requests.post, url=Config.get()["proxyStatusUpdateRoute"], json=json.loads(json.dumps(ServerManager.status_dict(), default=str)), auth=("automsvc", "speed0Meter!")))
                # This is our rate limiting sleep
                await asyncio.sleep(float(Config.get()["updateHealthStatusInterval"]) * 60)
            except requests.exceptions.ConnectionError as e:
                # sleep for a bit to avoid spamming a downed proxy
                await asyncio.sleep(60)