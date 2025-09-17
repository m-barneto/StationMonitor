import asyncio

from managers.alarm_manager import AlarmManager
from managers.event_manager import EventManager
from managers.health_manager import HealthManager
from managers.sensor_manager import SensorManager
from managers.server_manager import ServerManager
from managers.sleep_manager import SleepManager
from managers.config_manager import ConfigManager

from sensors.long_distance_sensor import LongDistanceSensor

from typing import List
from sensors.sensor import Sensor
from utils.config import Config
from utils.logger import logger

# Initialize our queues
event_queue = asyncio.Queue()

# Create main event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Manager that sends out requests containing event data
event_manager = EventManager(event_queue)
loop.create_task(event_manager.loop())

# Syncs config from lenovo
#loop.create_task(ConfigManager().loop())

# Handles sleep state when site is closed
sleep_manager = SleepManager()
loop.create_task(sleep_manager.loop())

sensors: List[Sensor] = []

long_distance_sensors = []

for long_dist_sensor in Config.get().longDistanceSensors:
    s = LongDistanceSensor(
        long_dist_sensor,
        event_queue
    )
    
    long_distance_sensors.append(s)
    sensors.append(s)

    loop.create_task(s.loop())

sensor_manager = SensorManager(sensors, event_queue)
loop.create_task(sensor_manager.loop())

# Sends out requests for alarm events when duration is exceeded
loop.create_task(AlarmManager(sensor_manager, event_queue).loop())

print("Starting web server on port 80")
# Web server that displays current status of sensors to web
server = ServerManager(long_distance_sensors, sensor_manager, event_manager, sleep_manager)
loop.create_task(server.loop())

print("Finished starting web server")

status_updater = HealthManager()
loop.create_task(status_updater.loop())

# Start our event loop
loop.run_forever()
