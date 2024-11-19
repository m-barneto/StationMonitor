import asyncio
from datetime import datetime, timezone
import json
from aiohttp import web

from managers.event_manager import EventManager
from managers.sensor_manager import SensorManager
from managers.sleep_manager import SleepManager
from utils.sensor_event import SensorState


class ServerManager:
    def __init__(self, sensors: list[SensorManager], event_manager: EventManager, sleep_manager: SleepManager):
        self.sensors = sensors
        self.event_manager = event_manager
        self.sleep_manager = sleep_manager

    async def get_status(self, request) -> web.Response:
        status = {}
        status["rpiTime"] = self.sleep_manager.get_local_time()
        if self.event_manager.current_event:
            status["lastSendEvent"] = self.event_manager.current_event.body
        else:
            status["lastSendEvent"] = None
        status["isSleeping"] = not self.sleep_manager.is_open

        sensor_data = {}
        for s in self.sensors:
            print(s.zone, s.sensor_state.name)
            duration = datetime.now(timezone.utc).timestamp(
            ) - s.last_empty_event.rpi_time.timestamp()
            if s.sensor_state == SensorState.EMPTY:
                duration = 0.0
            sensor_data[s.zone] = {
                "sensorState": s.sensor_state.name,
                "duration": duration
            }

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
        while True:
            await asyncio.sleep(1)

        await asyncio.Event().wait()
