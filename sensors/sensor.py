import asyncio
from enum import Enum

class SensorState(Enum):
    EMPTY = 0
    OCCUPIED = 1
    UNKNOWN = 2

class Sensor:
    def __init__(self, zone: str, event_queue: asyncio.Queue, alarm_queue: asyncio.Queue):
        self.zone = zone
        self.event_queue = event_queue
        self.alarm_queue = alarm_queue
        self.state = SensorState.UNKNOWN
    
    async def loop(self) -> None:
        """Main loop for the sensor. This should be overridden by subclasses."""
        while True:
            print("Replace loop method in subclass for sensor:", self.zone)
            await asyncio.sleep(5)