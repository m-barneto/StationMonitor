from rpi_ws281x import Adafruit_NeoPixel, Color
from sensor_event import SensorEvent, SensorState

class LedManager:
    def __init__(self, strip: Adafruit_NeoPixel) -> None:
        self.strip = strip
        self.sensor_state = SensorState.EMPTY
    
    def update_event(self, event: SensorEvent) -> None:
        self.event = event
    
    # LED helper function
    def wipe(self, color: Color) -> None:
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    async def loop(self) -> None:
        while True:
            await self.process_event()