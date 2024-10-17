import asyncio
import json
import requests

from utils.config import Config
from utils.sensor_event import AlarmEvent


class AlarmManager:
    def __init__(self, q: asyncio.Queue) -> None:
        self.alarm_queue = q

    async def loop(self) -> None:
        while True:
            await self.process_event()

    async def process_event(self):
        # Waits for an event to become available
        event: AlarmEvent = await self.alarm_queue.get()

        # We have an event, send it to the server.

        # Loop here is used to schedule our request without blocking
        loop = asyncio.get_event_loop()
        while True:
            try:
                # Sends the request while still allowing other loops to continue running
                res = await loop.run_in_executor(None, requests.post, Config.get()["proxyServerIp"] + "/alarms", None, json.dumps(event.__dict__))
                print("Sending alarm event")
                # This is our rate limiting sleep
                await asyncio.sleep(float(1 / int(Config.get()["eventSendRate"])))
                # Break out of loop to allow us to process the next event in the queue
                break
            except requests.exceptions.ConnectionError as e:
                # sleep for a bit to avoid spamming a downed proxy
                await asyncio.sleep(float(Config.get()["eventSendFailureCooldown"]))
