import asyncio
from managers.event_manager import EventManager
from managers.sensor_manager import SensorManager
from managers.led_manager import LedManager
from rpi_ws281x import Adafruit_NeoPixel, Color

from utils.config import Config

import RPi.GPIO as GPIO
GPIO.setwarnings(False)

# Setup LEDs
LED_COUNT = 16
LED_PIN = 18
LED_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 10
LED_INVERT = False
LED_CHANNEL = 0

# Finish setting up LED strip
leds = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
leds.begin()
for i in range(leds.numPixels()):
    leds.setPixelColor(i, Color(100, 0, 100))
leds.show()

try:
    q = asyncio.Queue()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    #loop.create_task(LedManager(leds).loop())
    loop.create_task(EventManager(q).loop())

    # Initialize sensors from config entries
    for sensor in Config.get()["sensors"]:
        loop.create_task(SensorManager(int(sensor["pin"]), sensor["zone"], q).loop())

    loop.run_forever()
finally:
    # Cleanup GPIO pin
    GPIO.cleanup()