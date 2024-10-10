import asyncio
from datetime import datetime, timezone
import RPi.GPIO as GPIO  # type: ignore

from utils.config import Config
from utils.sensor_event import OccupiedEvent, SensorEvent, SensorState
from utils.utils import PixelStrip


class SensorManager:
    def __init__(self, SENSOR_PIN: int, zone: str, q: asyncio.Queue) -> None:
        # Setup our sensor/gpio pin info
        self.SENSOR_PIN = SENSOR_PIN
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Assign our zone and event queue
        self.zone = zone
        self.event_queue = q

        # Start sensor off with an empty event
        self.sensor_state: SensorState = SensorState.EMPTY
        self.last_sensor_event = SensorEvent(
            self.zone, self.sensor_state)
        self.last_empty_event = SensorEvent(
            self.zone, self.sensor_state)

    async def loop(self) -> None:
        while True:
            # Get sensor state
            await self.process_sensor()
            # Sleep for configured interval
            await asyncio.sleep(float(1 / int(Config.get()["sensorPollRate"])))

    async def process_sensor(self) -> None:
        current_state: SensorState = not GPIO.input(self.SENSOR_PIN)

        # if previous state was occupied and now we're empty
        if SensorState(self.sensor_state) == SensorState.OCCUPIED and SensorState(current_state) == SensorState.EMPTY:
            print("Sending event.")

            occupied_event = OccupiedEvent(
                self.zone, self.last_empty_event.rpi_time, datetime.now(timezone.utc).timestamp())
            await self.event_queue.put(occupied_event)
        elif SensorState(current_state) == SensorState.EMPTY:
            self.last_empty_event = SensorEvent(
                self.zone, current_state)

        self.sensor_state = current_state
        self.last_sensor_event = SensorEvent(self.zone, current_state)

        # if current_state != self.sensor_state:
        #    # Create our event
        #    event = SensorEvent(self.zone, current_state)
#
        #    print(f"Produced event {event.zone} {event.rpi_time} {SensorState(event.state)}")
        #    # Enqueue the event
        #    await self.event_queue.put(event)
#
        #    # update our sensor_state
        #    self.sensor_state = current_state
        #    self.last_sensor_event = deepcopy(event)
