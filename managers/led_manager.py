import asyncio
from datetime import datetime, timezone
import math
from rpi_ws281x import Adafruit_NeoPixel, Color  # type: ignore

from managers.sensor_manager import SensorManager
from utils.config import Config
from utils.utils import PixelStrip, hex_to_rgb, inv_lerp, lerp
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

        last_stage = Config.get()["leds"]["stages"][-1]
        if event_duration >= last_stage["duration"]:
            stage = last_stage
        else:
            stage_index = self.get_led_stage_index(event_duration)
            stage = Config.get()["leds"]["stages"][stage_index]

        timer_duration = stage["duration"]
        # await asyncio.sleep(2)
        if event_duration <= timer_duration:
            # figure out how far into timer we are
            val = event_duration / timer_duration
            # convert that to numpixels
            pixelsToHighlight = val * self.leds.indicatorNumPixels
            pixelsFloored = int(pixelsToHighlight)
            for i in range(pixelsFloored):
                self.leds.setPixel(self.index, i, hex_to_rgb(stage["color"]))

            if pixelsToHighlight > pixelsFloored:
                self.leds.setPixel(self.index, pixelsToHighlight,
                                   hex_to_rgb(stage["color"], pixelsToHighlight % 1))

            self.leds.show()
        else:
            if Config.get()["leds"]["flashing"]["shouldFlash"]:
                # get time sine wave
                # map from -1 to 1
                v = math.sin(datetime.now(timezone.utc).timestamp())
                t = int(inv_lerp(1, -1, v) * 255)
                col = Color(255 - t, 255 - t, t)
                self.leds.fill(self.index, col)
            else:
                self.leds.fill(self.index, hex_to_rgb(stage["color"]))

    def get_led_stage_index(self, time: float) -> int:
        index = len(Config.get()["leds"]["stages"]) - 1
        print("start index " + str(index))
        for stage in reversed(Config.get()["leds"]["stages"]):
            if time <= float(stage["duration"]) and index > 0:
                index -= 1
            else:
                break
        return index
