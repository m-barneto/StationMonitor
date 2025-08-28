import asyncio
from datetime import datetime, timezone
import json
from aiohttp import web

from managers.config_manager import ConfigManager
from managers.event_manager import EventManager
from managers.sensor_manager import SensorManager
from managers.sleep_manager import SleepManager
from sensors.distance_sensor import DistanceSensor
from sensors.long_distance_sensor import LongDistanceSensor
from sensors.reflective_sensor import ReflectiveSensor
from utils.config import Config, StationMonitorConfig
from utils.sensor_event import SensorState


class ServerManager:
    def __init__(self, reflective_sensors: list[ReflectiveSensor], distance_sensors: list[DistanceSensor], long_distance_sensors: list[LongDistanceSensor], sensor_manager: SensorManager, event_manager: EventManager, sleep_manager: SleepManager):
        ServerManager.reflective_sensors = reflective_sensors
        ServerManager.distance_sensors = distance_sensors
        ServerManager.long_distance_sensors = long_distance_sensors
        ServerManager.sensor_manager = sensor_manager
        ServerManager.event_manager = event_manager
        ServerManager.sleep_manager = sleep_manager

    @staticmethod
    def status_dict(include_queue: bool = False) -> dict:
        # Create dict containing info we want to include in response
        status = {}
        # Add data that pertains to the rpi system
        status["rpiTime"] = ServerManager.sleep_manager.get_local_time()
        status["eventsQueued"] = str(
            ServerManager.event_manager.event_queue.qsize() + ServerManager.event_manager.processing)
        status["isSleeping"] = not ServerManager.sleep_manager.is_open

        # Add data for individual sensors
        ref_sensor_data = {}
        for s in ServerManager.reflective_sensors:
            start_event_time = ServerManager.sensor_manager.get_sensor_occupied_time(s.zone)
            if start_event_time is not None:
                # Calculate the duration of the event in seconds
                duration = (datetime.now(timezone.utc) - start_event_time).total_seconds()
            # Add data to dict using zone id as key
            ref_sensor_data[s.zone] = {
                "isOccupied": s.get_state().name,
                "eventState": ServerManager.sensor_manager.sensor_ctx[s.zone].current_event_state.name,
                "duration": round(duration, 2) if start_event_time is not None else 0.0,
            }
        # Add our sensor data to the response dict
        status["reflectiveSensors"] = ref_sensor_data

        dist_sensor_data = {}

        for dist_sensor in ServerManager.distance_sensors:
            start_event_time = ServerManager.sensor_manager.get_sensor_occupied_time(dist_sensor.zone)
            if start_event_time is not None:
                # Calculate the duration of the event in seconds
                duration = (datetime.now(timezone.utc) - start_event_time).total_seconds()

            dist_sensor_data[dist_sensor.zone] = {
                "currentDistance": dist_sensor.current_distance,
                "stableDistance": dist_sensor.stable_distance,
                "reflectionStrength": dist_sensor.reflection_strength,
                "temperature": dist_sensor.temperature,
                "occupiedDistance": dist_sensor.occupied_distance,
                "reflectionStrength": dist_sensor.reflection_strength,
                "isOccupied": str(dist_sensor.get_state().name),
                "duration": round(duration, 2) if start_event_time is not None else 0.0,
            }

        status["distanceSensors"] = dist_sensor_data

        long_dist_sensor_data = {}
        for long_dist_sensor in ServerManager.long_distance_sensors:
            start_event_time = ServerManager.sensor_manager.get_sensor_occupied_time(long_dist_sensor.zone)
            if start_event_time is not None:
                # Calculate the duration of the event in seconds
                duration = (datetime.now(timezone.utc) - start_event_time).total_seconds()

            long_dist_sensor_data[long_dist_sensor.zone] = {
                "currentDistance": long_dist_sensor.current_distance,
                "stableDistance": long_dist_sensor.stable_distance,
                "readingCount": len(long_dist_sensor.readings),
                "reflectionStrength": long_dist_sensor.reflection_strength,
                "temperature": long_dist_sensor.temperature,
                "occupiedDistance": long_dist_sensor.occupied_distance,
                "reflectionStrength": long_dist_sensor.reflection_strength,
                "isOccupied": str(long_dist_sensor.get_state().name),
                "duration": round(duration, 2) if start_event_time is not None else 0.0,
            }

        status["longDistanceSensors"] = long_dist_sensor_data

        if not include_queue:
            return status

        events = list()
        i = 0
        for event in ServerManager.event_manager.event_queue._queue:
            # Add event to list
            events.append(event.to_dict())
            i += 1
            # Limit the number of events to 10
            if i >= 10:
                break


        # Add the current event to the list of events
        if ServerManager.event_manager.current_event is not None:
            # Add the current event to the list of events
            events.insert(0, ServerManager.event_manager.current_event.to_dict())

        status["events"] = events
        
        return status

    async def get_interface(self, request) -> web.Response:
        # Return the interface html page
        with open("./public/index.html", "r") as f:
            html = f.read()
        return web.Response(text=html, content_type="text/html")

    async def get_style(self, request) -> web.Response:
        # Return the style css page
        with open("./public/style.css", "r") as f:
            css = f.read()
        return web.Response(text=css, content_type="text/css")

    async def get_status(self, request) -> web.Response:
        status = ServerManager.status_dict(True)

        # Return dict as formatted json
        return web.Response(text=json.dumps(status, default=str, indent=4))
    
    async def get_config(self, request) -> web.Response:
        # Return dict as formatted json
        return web.Response(text=json.dumps(StationMonitorConfig.to_dict(Config.conf), default=str, indent=4), content_type="application/json")

    async def loop(self) -> None:
        # Setup our web application
        app = web.Application()
        # Add index route for status
        app.router.add_get('/', self.get_interface)

        app.router.add_get("/style.css", self.get_style)

        app.router.add_get("/status", self.get_status)

        app.router.add_get("/config", self.get_config)

        # Setup the web app runner
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 80)
        # Start web server
        await site.start()

        print("Web server started.")
        while True:
            # Keep web server alive here
            await asyncio.sleep(60)
