import asyncio
from functools import partial
import json
from typing import List
import requests

from sensors.sensor import Sensor
from utils.config import Config
from utils.sensor_event import AlarmEvent


class AlarmManager:
    def __init__(self, sensors: List[Sensor], q: asyncio.Queue) -> None:
        self.alarm_queue = q

    async def loop(self) -> None:
        while True:
            await self.poll_alarm()
            await asyncio.sleep(10.0)

    async def poll_alarm(self):
        # Iterate over all sensors and check if they've sent an alarm already
        

