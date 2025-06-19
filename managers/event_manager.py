import asyncio
import json
import requests

from utils.config import Config
from utils.sensor_event import OccupiedEvent

from functools import partial

class EventManager:
    def __init__(self, q: asyncio.Queue) -> None:
        self.event_queue = q
        self.current_event: OccupiedEvent | None = None
        self.processing = 0

    async def loop(self) -> None:
        while True:
            await self.process_event()

    async def process_event(self):
        # Waits for an event to become available
        self.current_event = await self.event_queue.get()
        self.processing = 1

        # We have an event, send it to the server.

        # Loop here is used to schedule our request without blocking
        loop = asyncio.get_event_loop()
        while True:
            try:
                # Sends the request while still allowing other loops to continue running
                res = await loop.run_in_executor(None, partial(requests.post, url=Config.get().proxyEventRoute, json=json.loads(json.dumps(self.current_event.to_dict(), default=str)), auth=("automsvc", "speed0Meter!")))
                print(f"Event sent: {self.current_event.to_dict()}")
                print(f"Response: {res.status_code} - {res.text}")
                # This is our rate limiting sleep
                await asyncio.sleep(float(1 / int(Config.get().eventSendRate)))
                # Break out of loop to allow us to process the next event in the queue
                break
            except requests.exceptions.ConnectionError as e:
                # sleep for a bit to avoid spamming a downed proxy
                await asyncio.sleep(float(Config.get().eventSendFailureCooldown))
        self.processing = 0
