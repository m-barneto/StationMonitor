from datetime import datetime, timezone
from enum import Enum

class SensorState(Enum):
    EMPTY = 0
    OCCUPIED = 1


class SensorEvent:
    def __init__(self, state: SensorState) -> None:
        # Set our rpi's utc timestamp
        # Seconds from epoch
        self.rpi_time = datetime.now(timezone.utc).timestamp()
        # Load ID from config
        self.id = "A1"

        self.state = state
