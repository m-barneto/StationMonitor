import asyncio
from dataclasses import dataclass
from sensors.sensor import Sensor
import RPi.GPIO as GPIO  # type: ignore

@dataclass
class ReflectiveSensorConfig:
    zone: str
    gpioPin: int
    alarmDuration: int
    indicatorPin: int
    pwmChannel: int

class ReflectiveSensor(Sensor):
    def __init__(self, config: ReflectiveSensorConfig, event_queue: asyncio.Queue, alarm_queue: asyncio.Queue):
        """Initialize the reflective sensor with the given configuration."""
        Sensor.__init__(self, config.zone, event_queue, alarm_queue)

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.gpioPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def update_state(self):
        pass