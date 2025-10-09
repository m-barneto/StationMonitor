import asyncio
from dataclasses import dataclass
from sensors.sensor import Sensor, SensorState

from utils.config import Config, ReflectiveSensorConfig  # type: ignore

class ReflectiveSensor(Sensor):
    def __init__(self, config: ReflectiveSensorConfig, event_queue: asyncio.Queue):
        """Initialize the reflective sensor with the given configuration."""
        pass

    async def loop(self) -> None:
        pass