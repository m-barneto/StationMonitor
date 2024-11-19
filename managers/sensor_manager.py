import asyncio
from datetime import datetime, timedelta, timezone
import json
import RPi.GPIO as GPIO  # type: ignore

from managers.sleep_manager import SleepManager
from utils.config import Config
from utils.sensor_event import AlarmEvent, OccupiedEvent, SensorEvent, SensorState
from utils.utils import PixelStrip


class SensorManager:
    def __init__(self, SENSOR_PIN: int, zone: str, alarm_duration: int, event_queue: asyncio.Queue, alarm_queue: asyncio.Queue) -> None:
        # Setup our sensor/gpio pin info
        self.SENSOR_PIN = SENSOR_PIN
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Assign our zone and event queue
        self.zone = zone
        self.event_queue = event_queue
        self.alarm_queue = alarm_queue
        self.alarm_duration = alarm_duration
        self.has_sent_alarm = False

        # Start sensor off with an empty event
        self.sensor_state: SensorState = SensorState.EMPTY
        self.last_sensor_event = SensorEvent(
            self.zone, self.sensor_state)
        self.last_empty_event = SensorEvent(
            self.zone, self.sensor_state)

    async def loop(self) -> None:
        while True:
            if not SleepManager.is_open:
                await asyncio.sleep(Config.get()["sleep"]["sleepInterval"])
                continue
            # Get sensor state
            await self.process_sensor()
            # Sleep for configured interval
            await asyncio.sleep(float(1 / int(Config.get()["sensorPollRate"])))

    async def process_sensor(self) -> None:
        current_state: SensorState = GPIO.input(self.SENSOR_PIN)

        # if previous state was occupied and now we're empty
        if SensorState(self.sensor_state) == SensorState.OCCUPIED and SensorState(current_state) == SensorState.EMPTY:
            occupied_event = OccupiedEvent(
                self.zone, self.last_empty_event.rpi_time, datetime.now(timezone.utc), self.has_sent_alarm)

            print(json.dumps(occupied_event.__dict__, default=str))
            await self.event_queue.put(occupied_event)
            self.has_sent_alarm = False
        elif SensorState(self.sensor_state) == SensorState.OCCUPIED and SensorState(current_state) == SensorState.OCCUPIED and not self.has_sent_alarm:
            # We are still occupied, check time to see if its over the config's alarm setting
            # Get time from start of event to now
            rpi_time = datetime.now(timezone.utc)
            duration = rpi_time - self.last_empty_event.rpi_time
            if duration >= timedelta(minutes=self.alarm_duration):
                print("Sending alarm out for event over",
                      self.alarm_duration, "mins")
                alarm_event = AlarmEvent(
                    self.zone, self.last_empty_event.rpi_time, rpi_time)
                await self.alarm_queue.put(alarm_event)
                self.has_sent_alarm = True

        elif SensorState(current_state) == SensorState.EMPTY:
            self.last_empty_event = SensorEvent(
                self.zone, current_state)
            self.has_sent_alarm = False

        self.sensor_state = current_state
        self.last_sensor_event = SensorEvent(self.zone, current_state)
