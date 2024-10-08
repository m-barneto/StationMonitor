import asyncio
from managers.event_manager import EventManager
from managers.sensor_manager import SensorManager
from managers.led_manager import LedManager
from rpi_ws281x import Adafruit_NeoPixel

import RPi.GPIO as GPIO

# Setup GPIO
PES_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(PES_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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

try:
    q = asyncio.Queue()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(LedManager(leds).loop())
    loop.create_task(EventManager(q).loop())

    loop.create_task(SensorManager(PES_PIN, q).loop())
    # sensor #2 here
    # loop.create_task(SensorManager(PES_PIN, q).loop())

    loop.run_forever()
finally:
    # Cleanup GPIO pin
    GPIO.cleanup()