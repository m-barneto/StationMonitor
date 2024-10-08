import asyncio
from typing import Any, Coroutine, NoReturn

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
        try:
            #r = requests.post("get ip from config", json=event.json())
            print(f"Consumed event {event.id} {event.rpi_time} {SensorState(event.state)}")
            # this is our rate limiting sleep, should be read from config
            # only sends one event to AWS per second
            await asyncio.sleep(1)
        except ConnectionError as e:
            print("Failed to post event data. Adding event to back of queue.")
            print(e)
            # add the event back to the queue
            self.event_queue.put(event)
            # sleep for a bit to avoid spamming a down aws
            await asyncio.sleep(5)