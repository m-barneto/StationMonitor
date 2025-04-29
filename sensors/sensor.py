import asyncio

from utils.sensor_event import SensorState


class Sensor:
    def __init__(self, zone: str, event_queue: asyncio.Queue, alarm_queue: asyncio.Queue):
        self.zone = zone
        self.event_queue = event_queue
        self.alarm_queue = alarm_queue
    
    def update_state(self):
        pass