from datetime import datetime, timezone
from enum import Enum

class SensorState(Enum):
    EMPTY = 0
    OCCUPIED = 1


class SensorEvent:
    def __init__(self, zone: str, state: SensorState) -> None:
        # Set our rpi's utc timestamp
        # Seconds from epoch
        self.rpi_time = datetime.now(timezone.utc).timestamp()
        # Load ID from config
        self.zone = zone

        self.state = state

class OccupiedEvent:
    def __init__(self, zone: str, start_time: float, end_time: float):
        self.zone = zone
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
