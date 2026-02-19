import asyncio
from datetime import datetime, timezone
import json
import subprocess
from aiohttp import web
import aiohttp_cors

from managers.config_manager import ConfigManager
from managers.event_manager import EventManager
from managers.sensor_manager import SensorManager
from managers.sleep_manager import SleepManager
from managers.cache_manager import CacheManager
from sensors.long_distance_sensor import LongDistanceSensor
from utils.config import Config, StationMonitorConfig
from utils.sensor_event import SensorState


class ServerManager:
    def __init__(self, long_distance_sensors: list[LongDistanceSensor], sensor_manager: SensorManager, event_manager: EventManager, sleep_manager: SleepManager):
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
        status["realTime"] = datetime.now(timezone.utc).isoformat()
        status["eventsQueued"] = str(
            ServerManager.event_manager.event_queue.qsize() + ServerManager.event_manager.processing)
        status["isSleeping"] = not ServerManager.sleep_manager.is_open

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
        return web.FileResponse("../Interface/build/index.html")

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
    
    async def get_events(self, request) -> web.Response:
        # Return dict as formatted json
        return web.Response(text=json.dumps(list(CacheManager.event_cache), default=str, indent=4), content_type="application/json")
    
    async def post_config(self, request) -> web.Response:
        try:
            data = await request.json()
            # Validate and update config
            new_config = StationMonitorConfig.from_dict(data)
            # Modify the current config object
            Config.get().longDistanceSensors = new_config.longDistanceSensors
            Config.get().sleep.timezone = new_config.sleep.timezone
            Config.get().sleep.openTime = new_config.sleep.openTime
            Config.get().sleep.closeTime = new_config.sleep.closeTime
            Config.get().alarmDuration = new_config.alarmDuration
            Config.get().minOccupiedDuration = new_config.minOccupiedDuration
            # Save to file
            Config.save_config()

            # Save cache to file
            CacheManager.save_cache()
            # Get the asyncio event loop and schedule a restart in 5 seconds
            asyncio.get_event_loop().call_later(0.2, subprocess.run, ["sudo", "systemctl", "restart", "stationmonitor.service"])
            #Config.reload_config()
            return web.Response(text="Configuration updated successfully.", status=200)
        except Exception as e:
            return web.Response(text=f"Error updating configuration: {str(e)}", status=400)
    
    async def ping(self, ip, timeout=1):
        process = await asyncio.create_subprocess_exec(
            "ping",
            "-c", "1",
            "-W", str(timeout),
            ip,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )

        await process.communicate()

        return process.returncode == 0
    
    def set_static_ip(self, con_name, ip, gateway):
        cmds = [
            ["nmcli", "connection", "modify", con_name, "ipv4.addresses", ip],
            ["nmcli", "connection", "modify", con_name, "ipv4.gateway", gateway],
            ["nmcli", "connection", "modify", con_name, "ipv4.method", "manual"],
            ["nmcli", "connection", "down", con_name],
            ["nmcli", "connection", "up", con_name]
        ]

        for cmd in cmds:
            subprocess.run(cmd, check=True)

    async def post_set_ip(self, request) -> web.Response:
        try:
            data = await request.json()
            ip = data["ip"]

            if "192.168.17." not in ip or int(str.split(ip, '.')[-1]) <= 1 or int(str.split(ip, '.')[-1]) >= 255:
                return web.Response(text="IP out of range.", status=400)

            is_occupied = await self.ping(ip)

            if is_occupied:
                return web.Response(text="IP is occupied.", status=409)

            asyncio.get_event_loop().call_later(0.2, self.set_static_ip, "Wired connection 1", ip, "192.168.17.1")
            return web.Response(text="Updated IP successfully.", status=200)
        except Exception as e:
            return web.Response(text=f"Error setting ip: {str(e)}", status=500)

    async def loop(self) -> None:
        # Setup our web application
        app = web.Application()
        # Add index route for status
        app.router.add_get('/', self.get_interface)

        #app.router.add_get("/style.css", self.get_style)

        app.router.add_get("/status", self.get_status)

        app.router.add_get("/events", self.get_events)

        app.router.add_get("/config", self.get_config)

        app.router.add_post("/config", self.post_config)

        app.router.add_post("/ip", self.post_set_ip)

        # Static file serving (css, js, images, etc.)
        app.router.add_static("/", path="../Interface/build", name="public", show_index=True)

        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })

        # Apply CORS to all routes
        for route in list(app.router.routes()):
            cors.add(route)

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
