import asyncio
import colorsys
from datetime import datetime, timezone
import math
from rpi_ws281x import Adafruit_NeoPixel, Color  # type: ignore

from managers.sensor_manager import SensorContext, SensorManager
from managers.sleep_manager import SleepManager
from utils.config import Config
from utils.utils import PixelStrip, clamp, hex_to_rgb, inv_lerp, lerp
from utils.sensor_event import SensorState


class LedManager:
    def __init__(self, sensor: str, sensor_manager: SensorManager, leds: PixelStrip) -> None:
        self.sensor = sensor
        self.sensor_manager = sensor_manager
        self.leds = leds

    async def loop(self) -> None:
        while True:
            # If we're closed, sleep for configured amount of time and skip this led iteration
            if not SleepManager.is_open:
                # Clear led strip
                self.leds.clear()
                self.leds.show()
                await asyncio.sleep(Config.get().sleep.sleepInterval)
                continue
            await self.process_event()
            # controls the update rate of our leds
            await asyncio.sleep(.05)

    async def process_event(self) -> None:
        # Clear led strip
        self.leds.clear()

        ctx: SensorContext = self.sensor_manager.get_sensor_ctx(self.sensor)
        if ctx == None:
            print(f"LedManager: No context found for sensor {self.sensor}")
            return

        # If event is empty, show cleared led strip and return early
        if ctx != None and ctx.current_event_state == SensorState.EMPTY:
            self.leds.show()
            return

        event_duration = datetime.now(timezone.utc).timestamp(
        ) - ctx.occupied_start_time.timestamp()

        # Calculate what stage we're on based on duration
        stage_index = self.get_led_stage_index(event_duration)
        # Get stage info from config
        stage = Config.get().leds.stages[stage_index]
        # If we aren't at the end/flashing stage
        if stage_index != -1:
            # Get amount of time we're into the stage
            time_into_stage = event_duration - \
                self.get_time_before_stage(stage_index)
            # Get % of led bar to fill
            val = time_into_stage / (stage.duration * 60)
            # convert that to numpixels
            pixelsToHighlight = val * self.leds.ledsCount

            # Fill led strip to the %
            pixelsFloored = int(pixelsToHighlight)
            for i in range(pixelsFloored):
                self.leds.setPixel(i, hex_to_rgb(stage.color))

            # Take the last led and modulate the brightness for a smooth animation
            if pixelsToHighlight > pixelsFloored:
                self.leds.setPixel(pixelsToHighlight,
                                   hex_to_rgb(stage.color, pixelsToHighlight % 1))
        else:
            # We're in the flashing stage
            # If should flash
            if Config.get().leds.flashing.shouldFlash:
                # get time sine wave
                # map from -1 to 1
                v = math.sin(datetime.now(timezone.utc).timestamp(
                ) * Config.get().leds.flashing.flashFrequency)

                # Get amount of color to be used for both colors based on time
                t = inv_lerp(1, -1, v)
                y = inv_lerp(1, -1, -v)

                # Get primary and secondary colors
                primary = hex_to_rgb(
                    Config.get().leds.flashing.primaryColor, t)
                secondary = hex_to_rgb(
                    Config.get().leds.flashing.secondaryColor, y)

                # Interpolate between the two
                output = Color(clamp(primary.r + secondary.r, 0, 255), clamp(primary.g +
                               secondary.g, 0, 255), clamp(primary.b + secondary.b, 0, 255))

                # Display final color
                self.leds.fill(output)
            else:
                # Fill with color of final stage
                self.leds.fill(hex_to_rgb(stage.color))
        # Display our led strip data
        self.leds.show()

    def get_led_stage_index(self, time: float) -> int:
        index = 0
        # Iterate over all stages
        for stage in Config.get().leds.stages:
            # Subtract the stages duration from our current time
            time -= (stage.duration * 60)
            # If we have time to spare
            if time > 0:
                # Try the next stage
                index += 1
                # If we're on the last stage already return -1 since we've now gone over and should flash
                if stage == Config.get().leds.stages[-1]:
                    return -1
        return index

    def get_time_before_stage(self, stage: int):
        time_before_stage = 0
        # Go through each stage before the input stage
        for i in range(stage):
            # Add up time from previous stages
            time_before_stage += (Config.get()
                                  .leds.stages[i].duration * 60)
        return time_before_stage
