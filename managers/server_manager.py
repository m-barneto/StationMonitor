import asyncio
import json
from aiohttp import web

from managers.event_manager import EventManager
from managers.sensor_manager import SensorManager


class ServerManager:
    def __init__(self, sensors: list[SensorManager], event_manager: EventManager):
        self.sensors = sensors
        self.event_manager = event_manager

    async def get_status(self, request) -> web.Response:
        status = {}
        status["currentEvent"] = self.event_manager.current_event
        return web.Response(text=json.dumps(status, default=str))

    async def loop(self) -> None:
        app = web.Application()
        app.router.add_get('/', self.get_status)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()

        print("Web server started on http://localhost:8080")

        await asyncio.Event().wait()
