from dataclasses import dataclass
from typing import Any, List
import json

@dataclass
class Sleep:
    timezone: str
    openTime: str
    closeTime: str
    sleepInterval: int

    @staticmethod
    def from_dict(obj: Any) -> 'Sleep':
        _timezone = str(obj.get("timezone"))
        _openTime = str(obj.get("openTime"))
        _closeTime = str(obj.get("closeTime"))
        _sleepInterval = int(obj.get("sleepInterval"))
        return Sleep(_timezone, _openTime, _closeTime, _sleepInterval)
    
    @staticmethod
    def to_dict(obj: 'Sleep') -> dict:
        return {
            "timezone": obj.timezone,
            "openTime": obj.openTime,
            "closeTime": obj.closeTime,
            "sleepInterval": obj.sleepInterval
        }


@dataclass
class DistanceSensorConfig:
    zone: str
    serialNumber: str
    occupiedDistance: int
    emptyReflectionStrength: int
    indicatorPin: int
    pwmChannel: int

    @staticmethod
    def from_dict(obj: Any) -> 'DistanceSensorConfig':
        _zone = str(obj.get("zone"))
        _serialNumber = str(obj.get("serialNumber"))
        _occupiedDistance = int(obj.get("occupiedDistance"))
        _emptyReflectionStrength = int(obj.get("emptyReflectionStrength"))
        _indicatorPin = int(obj.get("indicatorPin"))
        _pwmChannel = int(obj.get("pwmChannel"))
        return DistanceSensorConfig(_zone, _serialNumber, _occupiedDistance, _emptyReflectionStrength, _indicatorPin, _pwmChannel)
    
    @staticmethod
    def to_dict(obj: 'DistanceSensorConfig') -> dict:
        return {
            "zone": obj.zone,
            "serialNumber": obj.serialNumber,
            "occupiedDistance": obj.occupiedDistance,
            "emptyReflectionStrength": obj.emptyReflectionStrength,
            "indicatorPin": obj.indicatorPin,
            "pwmChannel": obj.pwmChannel
        }

@dataclass
class LongDistanceSensorConfig:
    zone: str
    serialNumber: str
    occupiedDistance: int
    emptyReflectionStrength: int

    @staticmethod
    def from_dict(obj: Any) -> 'LongDistanceSensorConfig':
        _zone = str(obj.get("zone"))
        _serialNumber = str(obj.get("serialNumber"))
        _occupiedDistance = int(obj.get("occupiedDistance"))
        _emptyReflectionStrength = int(obj.get("emptyReflectionStrength"))
        return LongDistanceSensorConfig(_zone, _serialNumber, _occupiedDistance, _emptyReflectionStrength)
    
    @staticmethod
    def to_dict(obj: 'LongDistanceSensorConfig') -> dict:
        return {
            "zone": obj.zone,
            "serialNumber": obj.serialNumber,
            "occupiedDistance": obj.occupiedDistance,
            "emptyReflectionStrength": obj.emptyReflectionStrength
        }

@dataclass
class StationMonitorConfig:
    leds: Leds
    distanceSensors: List[DistanceSensorConfig]
    longDistanceSensors: List[LongDistanceSensorConfig]
    sleep: Sleep
    alarmDuration: int
    minOccupiedDuration: int
    sensorPollRate: int
    proxyEventRoute: str
    proxyAlarmRoute: str
    proxyStatusUpdateRoute: str
    eventSendRate: int
    eventSendFailureCooldown: int
    updateConfigInterval: int
    updateHealthStatusInterval: int

    @staticmethod
    def from_dict(obj: Any) -> 'StationMonitorConfig':
        _leds = Leds.from_dict(obj.get("leds"))
        _distanceSensors = [DistanceSensorConfig.from_dict(y) for y in obj.get("distanceSensors")]
        _longDistanceSensors = [LongDistanceSensorConfig.from_dict(y) for y in obj.get("longDistanceSensors")]
        _sleep = Sleep.from_dict(obj.get("sleep"))
        _alarmDuration = int(obj.get("alarmDuration"))
        _minOccupiedDuration = int(obj.get("minOccupiedDuration"))
        _sensorPollRate = int(obj.get("sensorPollRate"))
        _proxyEventRoute = str(obj.get("proxyEventRoute"))
        _proxyAlarmRoute = str(obj.get("proxyAlarmRoute"))
        _proxyStatusUpdateRoute = str(obj.get("proxyStatusUpdateRoute"))
        _eventSendRate = int(obj.get("eventSendRate"))
        _eventSendFailureCooldown = int(obj.get("eventSendFailureCooldown"))
        _updateConfigInterval = int(obj.get("updateConfigInterval"))
        _updateHealthStatusInterval = int(obj.get("updateHealthStatusInterval"))
        return StationMonitorConfig(_leds, _distanceSensors, _longDistanceSensors, _sleep, _alarmDuration, _minOccupiedDuration, _sensorPollRate, _proxyEventRoute, _proxyAlarmRoute, _proxyStatusUpdateRoute, _eventSendRate, _eventSendFailureCooldown, _updateConfigInterval, _updateHealthStatusInterval)

    @staticmethod
    def to_dict(obj: 'StationMonitorConfig') -> dict:
        return {
            "leds": Leds.to_dict(obj.leds),
            "distanceSensors": [DistanceSensorConfig.to_dict(y) for y in obj.distanceSensors],
            "longDistanceSensors": [LongDistanceSensorConfig.to_dict(y) for y in obj.longDistanceSensors],
            "sleep": Sleep.to_dict(obj.sleep),
            "alarmDuration": obj.alarmDuration,
            "minOccupiedDuration": obj.minOccupiedDuration,
            "sensorPollRate": obj.sensorPollRate,
            "proxyEventRoute": obj.proxyEventRoute,
            "proxyAlarmRoute": obj.proxyAlarmRoute,
            "proxyStatusUpdateRoute": obj.proxyStatusUpdateRoute,
            "eventSendRate": obj.eventSendRate,
            "eventSendFailureCooldown": obj.eventSendFailureCooldown,
            "updateConfigInterval": obj.updateConfigInterval,
            "updateHealthStatusInterval": obj.updateHealthStatusInterval
        }

class Config:
    conf: StationMonitorConfig = None

    @staticmethod
    def get() -> StationMonitorConfig:
        if Config.conf is None:
            with open("./config.jsonc", encoding="utf-8") as f:
                Config.conf = StationMonitorConfig.from_dict(json.load(f))
        return Config.conf
