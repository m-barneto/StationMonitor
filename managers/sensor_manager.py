import asyncio
from copy import deepcopy
from datetime import datetime, timezone
import RPi.GPIO as GPIO

from utils.config import Config
from utils.sensor_event import OccupiedEvent, SensorEvent, SensorState



class SensorManager:
    last_sensor_event: SensorEvent = None

    last_empty_event: SensorEvent = None

    def __init__(self, SENSOR_PIN: int, zone: str, q: asyncio.Queue) -> None:
        self.SENSOR_PIN = SENSOR_PIN
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.zone = zone
        self.event_queue = q
        self.sensor_state: SensorState = SensorState.EMPTY
        SensorManager.last_sensor_event = SensorEvent(self.zone, self.sensor_state)
        SensorManager.last_empty_event = SensorEvent(self.zone, self.sensor_state)
    
    async def loop(self) -> None:
        while True:
            # Get sensor state
            await self.process_sensor()
            # Sleep for configured interval
            await asyncio.sleep(float(1 / int(Config.get()["sensorPollRate"])))
    
    async def process_sensor(self) -> None:
        current_state: SensorState = GPIO.input(self.SENSOR_PIN)

        # if previous state was occupied and now we're empty
        if SensorState(self.sensor_state) == SensorState.OCCUPIED and SensorState(current_state) == SensorState.EMPTY:
            print("Sending event.")

            occupied_event = OccupiedEvent(self.zone, self.last_sensor_event.rpi_time, datetime.now(timezone.utc).timestamp())
            await self.event_queue.put(occupied_event)
        elif SensorState(current_state) == SensorState.EMPTY:
            SensorManager.last_empty_event = SensorEvent(self.zone, current_state)
        self.sensor_state = current_state
        SensorManager.last_sensor_event = SensorEvent(self.zone, current_state)
        


        #if current_state != self.sensor_state:
        #    # Create our event
        #    event = SensorEvent(self.zone, current_state)
#
        #    print(f"Produced event {event.zone} {event.rpi_time} {SensorState(event.state)}")
        #    # Enqueue the event
        #    await self.event_queue.put(event)
#
        #    # update our sensor_state
        #    self.sensor_state = current_state
        #    SensorManager.last_sensor_event = deepcopy(event)