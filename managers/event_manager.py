import asyncio
import json
from typing import Any, Coroutine, NoReturn

import requests

from utils.config import Config
from utils.sensor_event import SensorState


class EventManager:
    def __init__(self, q: asyncio.Queue) -> None:
        self.event_queue = q

    async def loop(self) -> None:
        while True:
            await self.process_event()
    
    async def process_event(self):
        # waits for event to become available
        event = await self.event_queue.get()

        # we have an event, send it to the server.
        loop = asyncio.get_event_loop()
        while True:
            try:
                # TODO
                # this needs to be tested to see if this actually works to send the request...
                res = await loop.run_in_executor(None, requests.post, f'http://{Config.get()["proxyServerIp"]}', None, json.dumps(event.__dict__))
                print(res)
                #r = requests.post(f'http://{Config.get()["proxyServerIp"]}', json=json.dumps(event.__dict__))
                print(f"Consumed event {event.zone} {event.rpi_time} {SensorState(event.state)}")
                # this is our rate limiting sleep
                await asyncio.sleep(float(1 / int(Config.get()["eventSendRate"])))
                break
            except requests.exceptions.ConnectionError as e:
                print("Failed to post event data.")
                #print(e)
                # sleep for a bit to avoid spamming a downed proxy
                await asyncio.sleep(float(Config.get()["eventSendFailureCooldown"]))