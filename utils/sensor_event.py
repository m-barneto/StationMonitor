from datetime import datetime, timezone
from enum import Enum


class SensorState(Enum):
    EMPTY = 0
    OCCUPIED = 1


class SensorEvent:
    def __init__(self, zone: str, state: SensorState) -> None:
        # Set our rpi's utc timestamp
        # Seconds from epoch
        self.rpi_time = datetime.now(timezone.utc)
        # Load ID from config
        self.zone = zone

        self.state = state


class OccupiedEvent:
    def __init__(self, zone: str, start_time: datetime, end_time: datetime):
        self.alarmType = "occupation"
        self.body = {}
        self.body["zone"] = zone
        self.body["startTime"] = start_time
        self.body["endTime"] = end_time
        self.body["duration"] = end_time - start_time
        self.body["triggeredAlarm"] = True


class AlarmEvent:
    def __init__(self, zone: str, start_time: datetime, rpi_time: datetime):
        self.alarmType = "alarm"
        self.body["zone"] = zone
        self.body["startTime"] = start_time
        self.body["endTime"] = rpi_time
        self.body["duration"] = rpi_time - start_time
