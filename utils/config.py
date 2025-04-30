from dataclasses import dataclass
from typing import Any, List
import pyjson5

@dataclass
class Flashing:
    shouldFlash: bool
    flashFrequency: float
    primaryColor: str
    secondaryColor: str

@dataclass
class Stage:
    color: str
    duration: float

@dataclass
class Leds:
    numLeds: int
    brightness: int
    stages: List[Stage]
    flashing: Flashing

@dataclass
class Sleep:
    timezone: str
    openTime: str
    closeTime: str
    sleepInterval: int


@dataclass
class DistanceSensorConfig:
    zone: str
    serialNumber: str
    port: str
    occupiedDistance: int

@dataclass
class ReflectiveSensorConfig:
    zone: str
    gpioPin: int
    alarmDuration: int
    indicatorPin: int
    pwmChannel: int

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


class Config:
    conf: StationMonitorConfig = None

    @staticmethod
    def get() -> StationMonitorConfig:
        if Config.conf is None:
            with open("./config.jsonc", encoding="utf-8") as f:
                Config.conf = pyjson5.load(f)
        return Config.conf
