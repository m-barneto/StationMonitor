import asyncio
from datetime import datetime, timezone
import math
from rpi_ws281x import Adafruit_NeoPixel, Color  # type: ignore

from managers.sensor_manager import SensorManager
from utils.config import Config
from utils.utils import PixelStrip, inv_lerp, lerp
from utils.sensor_event import SensorState


class LedManager:
    def __init__(self, sensor: SensorManager, leds: PixelStrip, indicatorIndex: int) -> None:
        self.sensor = sensor
        self.leds = leds
        self.index = indicatorIndex

    async def loop(self) -> None:
        while True:
            await self.process_event()
            # controls the update rate of our leds
            await asyncio.sleep(.01)

    async def process_event(self) -> None:
        event = self.sensor.last_sensor_event
        if event.state == SensorState.EMPTY.value:
            self.leds.fill(self.index, Color(0, 255, 0))
            return

        event_duration = datetime.now(
            timezone.utc).timestamp() - self.sensor.last_empty_event.rpi_time

        timer_duration = 1000
        stage_index = self.get_led_stage_index(event_duration)
        print(stage_index)
        stage = Config.get()["leds"]["stages"][stage_index]
        print(stage["color"])
        await asyncio.sleep(2)
        if event_duration <= timer_duration:
            # figure out how far into timer we are
            val = event_duration / timer_duration
            # convert that to numpixels
            pixelsToHighlight = val * self.leds.indicatorNumPixels
            pixelsFloored = int(pixelsToHighlight)
            for i in range(pixelsFloored):
                self.leds.setPixel(self.index, i, Color(255, 255, 255))

            if pixelsToHighlight > pixelsFloored:
                v = int(255 * (pixelsToHighlight % 1))
                self.leds.setPixel(self.index, pixelsToHighlight,
                                   Color(v, v, v))

            self.leds.show()
        else:
            # get time sine wave
            # map from -1 to 1
            v = math.sin(datetime.now(timezone.utc).timestamp())
            t = int(inv_lerp(1, -1, v) * 255)
            col = Color(255 - t, 255 - t, t)
            self.leds.fill(self.index, col)

    def get_led_stage_index(self, time: float) -> int:
        index = len(Config.get()["leds"]["stages"]) - 1
        for stage in reversed(Config.get()["leds"]["stages"]):
            if time <= float(stage["duration"]):
                index -= 1
            else:
                break
        return index
