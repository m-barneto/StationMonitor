import asyncio
from datetime import datetime, timedelta, timezone
import json
import RPi.GPIO as GPIO  # type: ignore

from managers.sleep_manager import SleepManager
from sensors.sensor import Sensor, SensorState
from utils.config import Config
from utils.sensor_event import AlarmEvent, OccupiedEvent, SensorEvent

from enum import Enum

class EventState(Enum):
    EMPTY = 0
    OCCUPIED_PENDING = 1
    OCCUPIED_STARTED = 2
    OCCUPIED_ENDED = 3
    #ALARM = 4


class SensorContext:
    previous_event_state: EventState = EventState.EMPTY
    current_event_state: EventState = EventState.EMPTY
    previous_sensor_state: SensorState = SensorState.EMPTY
    occupied_start_time: datetime


class SensorManager:
    def __init__(self, sensors: list[Sensor], event_queue: asyncio.Queue, alarm_queue: asyncio.Queue) -> None:
        self.sensor_ctx: dict[str, SensorContext] = {}
        self.event_queue = event_queue
        self.alarm_queue = alarm_queue
        self.sensors = sensors
        for sensor in sensors:
            # Initialize the sensor context for each sensor
            self.sensor_ctx[sensor.zone] = SensorContext()
            # Set the initial state of the sensor context to EMPTY
            self.sensor_ctx[sensor.zone].previous_event_state = EventState.EMPTY
            self.sensor_ctx[sensor.zone].current_event_state = EventState.EMPTY

    async def loop(self) -> None:
        while True:
            if not SleepManager.is_open:
                await asyncio.sleep(Config.get().sleep.sleepInterval)
                continue

            # Get the current time
            current_time = datetime.now(timezone.utc)

            # Loop through all sensors and call their loop method
            for sensor in self.sensors:
                await self.process_sensor(current_time, sensor.zone, sensor)
            
            # Sleep for configured interval
            await asyncio.sleep(float(1 / int(Config.get().sensorPollRate)))

    async def process_sensor(self, current_time: datetime, zone: str, sensor: Sensor) -> None:
        # Get current state of sensor
        event_state: EventState | None = self.update_event_state(zone, sensor)

        if event_state is None:
            # Do nothing
            return
        
        print(zone, ":", event_state)

    def update_event_state(self, zone: str, sensor: Sensor) -> EventState | None:
        # Get the zone context
        zone_ctx = self.sensor_ctx.get(zone)
        if zone_ctx is None:
            # If the context does not exist, return empty but print error
            print(f"Error: No context found for zone {zone}.")
            return None
        

        # Get the sensor state
        sensor_state: SensorState = sensor.get_state()

        event_state: EventState = None

        # Check if the sensor state has changed
        if sensor_state != zone_ctx.previous_sensor_state or zone_ctx.current_event_state != zone_ctx.previous_event_state:
            print(json.dumps(zone_ctx.__dict__, indent=4, default=str))
            if sensor_state == SensorState.EMPTY:
                if zone_ctx.previous_event_state == EventState.OCCUPIED_STARTED:
                    # If the previous state was occupied and now it's empty, set to EMPTY
                    zone_ctx.current_event_state = EventState.OCCUPIED_ENDED
                    event_state = EventState.OCCUPIED_ENDED
                elif zone_ctx.previous_event_state == EventState.OCCUPIED_ENDED:
                    zone_ctx.current_event_state = EventState.EMPTY
                    event_state = EventState.EMPTY

            
            elif sensor_state == SensorState.OCCUPIED:
                # EMPTY -> OCCUPIED = OCCUPIED_PENDING
                if zone_ctx.previous_event_state == EventState.EMPTY:
                    # If the previous state was empty and now it's occupied, set to OCCUPIED_PENDING
                    zone_ctx.current_event_state = EventState.OCCUPIED_PENDING
                    event_state = EventState.OCCUPIED_PENDING

                    # Assign the current time to occupied_start_time
                    zone_ctx.occupied_start_time = datetime.now(timezone.utc)

                # OCCUPIED_PENDING -> OCCUPIED = OCCUPIED_STARTED if duration is over min_duration
                elif zone_ctx.previous_event_state == EventState.OCCUPIED_PENDING:
                    duration = (datetime.now(timezone.utc) - zone_ctx.occupied_start_time).total_seconds()
                    if duration >= Config.get().minOccupiedDuration:
                        print("Duration of pending is over min duration")
                        # If the previous state was occupied pending and now it's occupied, set to OCCUPIED_STARTED
                        zone_ctx.current_event_state = EventState.OCCUPIED_STARTED
                        event_state = EventState.OCCUPIED_STARTED
                    else:
                        # If the previous state was occupied pending but not for long enough, keep it as OCCUPIED_PENDING
                        zone_ctx.current_event_state = EventState.OCCUPIED_PENDING
                        event_state = EventState.OCCUPIED_PENDING
            if event_state is not None:
                zone_ctx.previous_event_state = event_state
            zone_ctx.previous_sensor_state = sensor_state
        else:
            event_state = None
        return event_state