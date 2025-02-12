import asyncio
from datetime import datetime, timezone
import json
from aiohttp import web

from managers.config_manager import ConfigManager
from managers.event_manager import EventManager
from managers.sensor_manager import SensorManager
from managers.sleep_manager import SleepManager
from utils.config import Config
from utils.sensor_event import SensorState


class ServerManager:
    def __init__(self, sensors: list[SensorManager], event_manager: EventManager, sleep_manager: SleepManager):
        ServerManager.sensors = sensors
        ServerManager.event_manager = event_manager
        ServerManager.sleep_manager = sleep_manager

    @staticmethod
    def status_dict():
        # Create dict containing info we want to include in response
        status = {}
        # Add data that pertains to the rpi system
        status["rpiTime"] = ServerManager.sleep_manager.get_local_time()
        status["eventsQueued"] = str(
            ServerManager.event_manager.event_queue.qsize() + ServerManager.event_manager.processing)
        status["isSleeping"] = not ServerManager.sleep_manager.is_open

        # Add data for individual sensors
        sensor_data = {}
        for s in ServerManager.sensors:
            # Current sensor event duration
            duration = datetime.now(timezone.utc).timestamp(
            ) - s.last_empty_event.rpi_time.timestamp()
            # If sensor is empty, set duration to 0
            if s.sensor_state == SensorState.EMPTY:
                duration = 0.0

            # Add data to dict using zone id as key
            sensor_data[s.zone] = {
                "sensorState": s.sensor_state.name,
                "duration": duration
            }
        # Add our sensor data to the response dict
        status["sensorData"] = sensor_data

        # Add our loaded config to response

        status["config"] = Config.conf
        
        return status

    async def get_status(self, request) -> web.Response:
        status = ServerManager.status_dict()

        # Return dict as formatted json
        return web.Response(text=json.dumps(status, default=str, indent=4))

    async def loop(self) -> None:
        # Setup our web application
        app = web.Application()
        # Add index route for status
        app.router.add_get('/', self.get_status)

        app.router.add_get("/status", self.get_status)

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
