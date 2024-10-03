from rpi_ws281x import Adafruit_NeoPixel, Color
import time
import colorsys
import requests

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
LED_BRIGHTNESS = 25
LED_INVERT = False
LED_CHANNEL = 0

# LED helper function
def wipe(strip, col):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, col)
    strip.show()

# Finish setting up LED strip
leds = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
leds.begin()




try:
    # Store previous state to compare to
    state = 0

    # Start reading state constantly
    while True:
        # state is 0 or 1
        current_state = GPIO.input(PES_PIN)

        if current_state != state:
            print("State changed!")
            #r = requests.post('http://httpbin.org/post', json={"key": "value"})
            # send post request to server
            state = current_state

        if state == 0:
            wipe(leds, Color(0, 0, 50))
        else:
            wipe(leds, Color(50, 50, 0))
        
        
        
        time.sleep(.001)
finally:
    # Cleanup GPIO pin
    GPIO.cleanup()
