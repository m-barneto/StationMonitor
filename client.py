import asyncio
import RPi.GPIO as GPIO  # type: ignore

from managers.alarm_manager import AlarmManager
from managers.config_manager import ConfigManager
from managers.event_manager import EventManager
from managers.sensor_manager import SensorManager
from managers.led_manager import LedManager

from managers.server_manager import ServerManager
from managers.sleep_manager import SleepManager
from utils.config import Config
from utils.utils import PixelStrip

from rpi_ws281x import Color

leds = PixelStrip(Config.get()["leds"]["numLeds"],
                  Config.get()["leds"]["numIndicators"],
                  Config.get()["leds"]["gpioPin"],
                  Config.get()["leds"]["brightness"])


try:
    # Initialize our queues
    event_queue = asyncio.Queue()
    alarm_queue = asyncio.Queue()

    # Create main event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Manager that sends out requests containing event data
    event_manager = EventManager(event_queue)
    loop.create_task(event_manager.loop())

    # Sends out requests for alarm events when duration is exceeded
    loop.create_task(AlarmManager(alarm_queue).loop())

    # Syncs config from lenovo
    loop.create_task(ConfigManager().loop())

    # Handles sleep state when site is closed
    sleep_manager = SleepManager()
    loop.create_task(sleep_manager.loop())

    # List to store sensor managers in
    sensors = []

    # Initialize sensors from config entries
    for sensor in Config.get()["sensors"]:
        s = SensorManager(
            sensor["gpioPin"],
            sensor["zone"],
            sensor["alarmDuration"],
            event_queue,
            alarm_queue
        )
        sensors.append(s)

        # Setup led manager for this sensor
        l = LedManager(s, leds, sensor["indicatorIndex"])

        # Initialize our event loops for the sensor managers
        loop.create_task(s.loop())
        loop.create_task(l.loop())

    # Web server that displays current status of sensors to web
    server = ServerManager(sensors, event_manager, sleep_manager)
    loop.create_task(server.loop())

    # Start our event loop
    loop.run_forever()
finally:
    # Cleanup GPIO pin
    GPIO.cleanup()
