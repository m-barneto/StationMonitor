from dataclasses import dataclass
from typing import Any, List
import pyjson5

@dataclass
class Flashing:
    shouldFlash: bool
    flashFrequency: float
    primaryColor: str
    secondaryColor: str

    @staticmethod
    def from_dict(obj: Any) -> 'Flashing':
        _shouldFlash = bool(obj.get("shouldFlash"))
        _flashFrequency = float(obj.get("flashFrequency"))
        _primaryColor = str(obj.get("primaryColor"))
        _secondaryColor = str(obj.get("secondaryColor"))
        return Flashing(_shouldFlash, _flashFrequency, _primaryColor, _secondaryColor)

@dataclass
class Stage:
    color: str
    duration: float

    @staticmethod
    def from_dict(obj: Any) -> 'Stage':
        _color = str(obj.get("color"))
        _duration = float(obj.get("duration"))
        return Stage(_color, _duration)

@dataclass
class Leds:
    numLeds: int
    brightness: int
    stages: List[Stage]
    flashing: Flashing

    @staticmethod
    def from_dict(obj: Any) -> 'Leds':
        _numLeds = int(obj.get("numLeds"))
        _brightness = int(obj.get("brightness"))
        _stages = [Stage.from_dict(y) for y in obj.get("stages")]
        _flashing = Flashing.from_dict(obj.get("flashing"))
        return Leds(_numLeds, _brightness, _stages, _flashing)

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


@dataclass
class DistanceSensorConfig:
    zone: str
    serialNumber: str
    port: str
    occupiedDistance: int

    @staticmethod
    def from_dict(obj: Any) -> 'DistanceSensorConfig':
        _zone = str(obj.get("zone"))
        _port = str(obj.get("port"))
        _serialNumber = str(obj.get("serialNumber"))
        _occupiedDistance = int(obj.get("occupiedDistance"))
        return DistanceSensorConfig(_zone, _port, _serialNumber, _occupiedDistance)

@dataclass
class ReflectiveSensorConfig:
    zone: str
    gpioPin: int
    alarmDuration: int
    indicatorPin: int
    pwmChannel: int

    @staticmethod
    def from_dict(obj: Any) -> 'ReflectiveSensorConfig':
        _zone = str(obj.get("zone"))
        _gpioPin = int(obj.get("gpioPin"))
        _alarmDuration = int(obj.get("alarmDuration"))
        _indicatorPin = int(obj.get("indicatorPin"))
        _pwmChannel = int(obj.get("pwmChannel"))
        return ReflectiveSensorConfig(_zone, _gpioPin, _alarmDuration, _indicatorPin, _pwmChannel)

@dataclass
class StationMonitorConfig:
    leds: Leds
    reflectiveSensors: List[ReflectiveSensorConfig]
    distanceSensors: List[DistanceSensorConfig]
    sleep: Sleep
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
        _reflectiveSensors = [ReflectiveSensorConfig.from_dict(y) for y in obj.get("reflectiveSensors")]
        _distanceSensors = [DistanceSensorConfig.from_dict(y) for y in obj.get("distanceSensors")]
        _sleep = Sleep.from_dict(obj.get("sleep"))
        _minOccupiedDuration = int(obj.get("minOccupiedDuration"))
        _sensorPollRate = int(obj.get("sensorPollRate"))
        _proxyEventRoute = str(obj.get("proxyEventRoute"))
        _proxyAlarmRoute = str(obj.get("proxyAlarmRoute"))
        _proxyStatusUpdateRoute = str(obj.get("proxyStatusUpdateRoute"))
        _eventSendRate = int(obj.get("eventSendRate"))
        _eventSendFailureCooldown = int(obj.get("eventSendFailureCooldown"))
        _updateConfigInterval = int(obj.get("updateConfigInterval"))
        _updateHealthStatusInterval = int(obj.get("updateHealthStatusInterval"))
        return StationMonitorConfig(_leds, _reflectiveSensors, _distanceSensors, _sleep, _minOccupiedDuration, _sensorPollRate, _proxyEventRoute, _proxyAlarmRoute, _proxyStatusUpdateRoute, _eventSendRate, _eventSendFailureCooldown, _updateConfigInterval, _updateHealthStatusInterval)


class Config:
    conf: StationMonitorConfig = None

    @staticmethod
    def get() -> StationMonitorConfig:
        if Config.conf is None:
            with open("./config.jsonc", encoding="utf-8") as f:
                Config.conf = StationMonitorConfig.from_dict(pyjson5.load(f))
        return Config.conf
