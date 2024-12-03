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

# from rpi_ws281x import Color
from rpi_ws281x import Adafruit_NeoPixel, Color, ws  # type: ignore

NUMLEDS = 15

leds = Adafruit_NeoPixel(NUMLEDS, 18, 800000, 10, False, 255, 0)
leds.begin()

pink = Color(255, 0, 255)
blue = Color(0, 0, 255)
white = Color(150, 150, 150)


while True:
    for i in range(int(NUMLEDS)):
        leds.setPixelColor(i, blue)
        # leds.setPixelColor(index + 4, blue)
    leds.show()


try:
    event_queue = asyncio.Queue()
    alarm_queue = asyncio.Queue()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    event_manager = EventManager(event_queue)
    loop.create_task(event_manager.loop())
    loop.create_task(AlarmManager(alarm_queue).loop())
    loop.create_task(ConfigManager().loop())
    sleep_manager = SleepManager()
    loop.create_task(sleep_manager.loop())

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

        led = PixelStrip(Config.get()["leds"]["numLedPerIndicator"],
                         sensor["indicatorGpio"],
                         Config.get()["leds"]["brightness"])
        print("setting up", sensor["gpioPin"], "at", sensor["indicatorGpio"])
        sensors.append(s)
        l = LedManager(s, led)
        loop.create_task(s.loop())
        loop.create_task(l.loop())
        break

    server = ServerManager(sensors, event_manager, sleep_manager)
    loop.create_task(server.loop())
    loop.run_forever()
finally:
    # Cleanup GPIO pin
    GPIO.cleanup()
