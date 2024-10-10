import asyncio
import RPi.GPIO as GPIO  # type: ignore

from managers.event_manager import EventManager
from managers.sensor_manager import SensorManager
from managers.led_manager import LedManager

from utils.config import Config


try:
    q = asyncio.Queue()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(LedManager().loop())
    loop.create_task(EventManager(q).loop())

    # Initialize sensors from config entries
    for sensor in Config.get()["sensors"]:
        loop.create_task(SensorManager(
            int(sensor["pin"]), sensor["zone"], q).loop())

    loop.run_forever()
finally:
    # Cleanup GPIO pin
    GPIO.cleanup()
