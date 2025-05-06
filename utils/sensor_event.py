from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, List
import pyjson5

from sensors.sensor import SensorState




class SensorEvent:
    def __init__(self, zone: str, state: SensorState) -> None:
        # Set our rpi's utc timestamp
        # Seconds from epoch
        self.rpi_time = datetime.now(timezone.utc)
        # Load ID from config
        self.zone = zone

        self.state = state


class OccupiedEvent:
    def __init__(self, zone: str, start_time: datetime, end_time: datetime, triggered_alarm: bool):
        self.alarmType = "occupation"
        self.body = {}
        self.body["zone"] = zone
        self.body["startTime"] = start_time
        self.body["endTime"] = end_time
        self.body["duration"] = end_time - start_time
        self.body["triggeredAlarm"] = triggered_alarm


class AlarmEvent:
    def __init__(self, zone: str, start_time: datetime, rpi_time: datetime):
        self.alarmType = "alarm"
        self.body = {}
        self.body["zone"] = zone
        self.body["startTime"] = start_time
        self.body["endTime"] = rpi_time
        self.body["duration"] = rpi_time - start_time


@dataclass
class EventBody:
    zone: str
    startTime: str
    endTime: str | None
    triggeredAlarm: bool
    duration: float | None

    @staticmethod
    def from_dict(obj: Any) -> 'EventBody':
        _zone = str(obj.get("zone"))
        _startTime = str(obj.get("startTime"))
        _endTime = None if obj.get("endTime") is None else str(obj.get("endTime"))
        _triggeredAlarm = bool(obj.get("triggeredAlarm"))
        _duration = None if obj.get("duration") is None else float(obj.get("duration"))
        return EventBody(_zone, _startTime, _endTime, _triggeredAlarm, _duration)

    def to_dict(self) -> dict[str, Any]:
        return {
            "zone": self.zone,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "triggeredAlarm": self.triggeredAlarm,
            "duration": self.duration
        }

@dataclass
class EventData:
    alarm_type: str
    body: EventBody

    @staticmethod
    def from_dict(obj: Any) -> 'EventData':
        _alarm_type = str(obj.get("alarm_type"))
        _body = EventBody.from_dict(obj.get("body"))
        return EventData(_alarm_type, _body)

    def to_dict(self) -> dict[str, Any]:
        return {
            "alarm_type": self.alarm_type,
            "body": self.body.to_dict()
        }
    
    @staticmethod
    def occupied_start(zone: str, start_time: datetime) -> 'EventData':
        _alarm_type = str("occupied")
        _body = EventBody.from_dict({
            "zone": zone,
            "startTime": str(start_time),
            "endTime": None,
            "triggeredAlarm": False,
            "duration": None
        })
        return EventData(_alarm_type, _body)
    
    @staticmethod
    def occupied_end(zone: str, start_time: datetime, end_time: datetime, triggered_alarm: bool) -> 'EventData':
        _alarm_type = str("occupied")
        _body = EventBody.from_dict({
            "zone": zone,
            "startTime": str(start_time),
            "endTime": str(end_time),
            "triggeredAlarm": False,
            "duration": (end_time - start_time).total_seconds()
        })
        return EventData(_alarm_type, _body)
    
    @staticmethod
    def alarm_event(zone: str, start_time: datetime, alarm_time: datetime) -> 'EventData':
        _alarm_type = str("alarm")
        _body = EventBody.from_dict({
            "zone": zone,
            "startTime": str(start_time),
            "endTime": str(alarm_time),
            "triggeredAlarm": True,
            "duration": (alarm_time - start_time).total_seconds()
        })
        return EventData(_alarm_type, _body)