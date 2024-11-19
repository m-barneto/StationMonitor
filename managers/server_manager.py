import asyncio
import json
from aiohttp import web

from managers.event_manager import EventManager
from managers.sensor_manager import SensorManager
from managers.sleep_manager import SleepManager


class ServerManager:
    def __init__(self, sensors: list[SensorManager], event_manager: EventManager, sleep_manager: SleepManager):
        self.sensors = sensors
        self.event_manager = event_manager
        self.sleep_manager = sleep_manager

    async def get_status(self, request) -> web.Response:
        status = {}
        status["currentEvent"] = self.event_manager.current_event
        status["isSleeping"] = not self.sleep_manager.is_open

        sensor_data = {}
        for s in self.sensors:
            sensor_data[s.zone] = {"sensorState": s.sensor_state.name}

        status["sensorData"] = sensor_data

        return web.Response(text=json.dumps(status, default=str, indent=4))

    async def loop(self) -> None:
        app = web.Application()
        app.router.add_get('/', self.get_status)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()

        print("Web server started on http://localhost:8080")

        await asyncio.Event().wait()
