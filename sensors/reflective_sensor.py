import asyncio
from dataclasses import dataclass
from sensors.sensor import Sensor, SensorState
import RPi.GPIO as GPIO

from utils.config import Config  # type: ignore

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

    async def loop(self) -> None:
        while True:
            # Get current state of sensor
            self.current_reading = GPIO.input(self.zone)
            self.state = SensorState.OCCUPIED if self.current_reading else SensorState.EMPTY
            await asyncio.sleep(float(1 / Config.get().sensorPollRate))