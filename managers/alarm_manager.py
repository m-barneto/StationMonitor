import asyncio
from datetime import datetime, timezone

from managers.sensor_manager import EventState, SensorManager
from utils.config import Config
from utils.sensor_event import EventData


class AlarmManager:
    def __init__(self, sensor_manager: SensorManager, q: asyncio.Queue) -> None:
        self.alarm_queue = q
        self.sensor_manager = sensor_manager

    async def loop(self) -> None:
        while True:
            await self.poll_alarm()
            await asyncio.sleep(10.0)

    async def poll_alarm(self):
        # Iterate over all sensors and check if they've sent an alarm already
        
        for sensor in self.sensor_manager.sensors:
            #sprint(f"Checking sensor {sensor.zone} for alarm")
            sensor_ctx = self.sensor_manager.get_sensor_ctx(sensor.zone)
            
            if sensor_ctx.alarm_sent:
                # If the alarm has been sent, we don't need to do anything else
                #print(f"Alarm already sent for sensor {sensor.zone}, skipping")
                continue

            # Check if sensor is in occupied started state
            if sensor_ctx.current_event_state != EventState.OCCUPIED_STARTED:
                #print(f"Sensor {sensor.zone} is not in OCCUPIED_STARTED state, its current event state is {sensor_ctx.current_event_state.name}")
                continue
            #print(f"Sensor {sensor.zone} is in OCCUPIED_STARTED state")
            # Get the duration of the current event
            event_start_time = self.sensor_manager.get_sensor_occupied_time(sensor.zone)
            if event_start_time is None:
                continue
            
            event_duration = (datetime.now(timezone.utc) - event_start_time).total_seconds()

            #print(f"Sensor {sensor.zone} event duration: {event_duration} seconds")

            if event_duration >= float(Config.get().alarmDuration * 60):
                print(f"Alarm triggered for zone {sensor.zone} with duration {event_duration} seconds")
                # If the event duration is greater than the alarm duration, send an alarm event
                await self.send_alarm_event(sensor.zone, sensor_ctx.occupied_start_time, datetime.now(timezone.utc), event_duration)
                # Set the alarm sent flag to True
                sensor_ctx.alarm_sent = True

    async def send_alarm_event(self, zone: str, start_time: datetime, end_time: datetime, duration: float) -> None:
        # Create the alarm event
        alarm_event = EventData.alarm_event(zone, start_time, end_time, duration)

        # Send the alarm event to the queue
        await self.alarm_queue.put(alarm_event)