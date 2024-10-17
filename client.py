import asyncio
import RPi.GPIO as GPIO  # type: ignore

from managers.alarm_manager import AlarmManager
from managers.event_manager import EventManager
from managers.sensor_manager import SensorManager
from managers.led_manager import LedManager

from utils.config import Config
from utils.utils import PixelStrip


leds = PixelStrip(Config.get()["leds"]["numLeds"],
                  Config.get()["leds"]["numIndicators"],
                  Config.get()["leds"]["gpioPin"],
                  Config.get()["leds"]["brightness"])

try:
    event_queue = asyncio.Queue()
    alarm_queue = asyncio.Queue()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(EventManager(event_queue).loop())
    loop.create_task(AlarmManager(alarm_queue).loop())

    # Initialize sensors from config entries
    for sensor in Config.get()["sensors"]:
        s = SensorManager(
            sensor["gpioPin"],
            sensor["zone"],
            sensor["alarmDuration"]
            event_queue,
            alarm_queue
        )
        loop.create_task(s.loop())
        loop.create_task(LedManager(s, leds, sensor["indicatorIndex"]).loop())

    loop.run_forever()
finally:
    # Cleanup GPIO pin
    GPIO.cleanup()
