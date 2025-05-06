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
            sensor_ctx = self.sensor_manager.get_sensor_ctx(sensor.zone)
            
            if sensor_ctx.alarm_sent:
                # If the alarm has been sent, we don't need to do anything else
                continue

            # Check if sensor is in occupied started state
            if sensor_ctx.current_event_state != EventState.OCCUPIED_STARTED:
                continue

            # Get the duration of the current event
            event_duration = self.sensor_manager.get_sensor_occupied_time(sensor.zone)
            if event_duration is None:
                continue

            if event_duration >= Config.get().alarmDuration:
                # If the event duration is greater than the alarm duration, send an alarm event
                await self.send_alarm_event(sensor.zone, sensor_ctx.occupied_start_time)
                # Set the alarm sent flag to True
                sensor_ctx.alarm_sent = True

    async def send_alarm_event(self, zone: str, start_time: datetime) -> None:
        # Create the alarm event
        alarm_event = EventData.alarm_event(zone, start_time, datetime.now(timezone.utc))

        # Send the alarm event to the queue
        await self.alarm_queue.put(alarm_event)