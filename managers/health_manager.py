import asyncio
import json
import logging

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
                res = await loop.run_in_executor(None, requests.post, Config.get()["proxyStatusUpdateRoute"], None, json.loads(json.dumps(ServerManager.status_dict(), default=str)))
                
                # This is our rate limiting sleep
                await asyncio.sleep(int(Config.get()["updateHealthStatusInterval"]) * 60)
                # Break out of loop to allow us to process the next event in the queue
                break
            except requests.exceptions.ConnectionError as e:
                # sleep for a bit to avoid spamming a downed proxy
                await asyncio.sleep(60)