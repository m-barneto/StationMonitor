import asyncio
from datetime import datetime, timezone
import math
from rpi_ws281x import Adafruit_NeoPixel, Color  # type: ignore

from managers.sensor_manager import SensorManager
from utils.config import Config
from utils.utils import PixelStrip, clamp, hex_to_rgb, inv_lerp, lerp
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
        event = self.sensor.last_empty_event
        event_duration = datetime.now(timezone.utc).timestamp(
        ) - event.rpi_time
        print("Event Duration: " + "{:.2f}".format(event_duration))
        stage_index = self.get_led_stage_index(event_duration)
        stage = Config.get()["leds"]["stages"][stage_index]

        if stage_index != -1:
            time_into_stage = event_duration - \
                self.get_time_before_stage(stage_index)
            val = time_into_stage / stage["duration"]
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
                v = math.sin(datetime.now(timezone.utc).timestamp(
                ) * Config.get()["leds"]["flashing"]["flashFrequency"])

                t = inv_lerp(1, -1, v)
                y = inv_lerp(1, -1, -v)

                primary = hex_to_rgb(
                    Config.get()["leds"]["flashing"]["primaryColor"], t)
                secondary = hex_to_rgb(
                    Config.get()["leds"]["flashing"]["secondaryColor"], y)

                output = Color(clamp(primary.r + secondary.r, 0, 255), clamp(primary.g +
                               secondary.g, 0, 255), clamp(primary.b + secondary.b, 0, 255))

                self.leds.fill(self.index, output)
            else:
                self.leds.fill(self.index, hex_to_rgb(stage["color"]))

    def get_led_stage_index(self, time: float) -> int:
        index = 0

        for stage in Config.get()["leds"]["stages"]:
            time -= stage["duration"]
            if time > 0:
                index += 1
                if stage == Config.get()["leds"]["stages"][-1]:
                    return -1
        return index

    def get_time_before_stage(self, stage: int):
        time_before_stage = 0
        for i in range(stage):
            time_before_stage += Config.get()["leds"]["stages"][i]["duration"]
        return time_before_stage
