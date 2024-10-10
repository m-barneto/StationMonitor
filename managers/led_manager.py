import asyncio
from datetime import datetime, timezone
import math
from rpi_ws281x import Adafruit_NeoPixel, Color  # type: ignore
from managers.sensor_manager import SensorManager
from utils.utils import PixelStrip, inv_lerp, lerp
from utils.sensor_event import SensorState


class LedManager:
    def __init__(self) -> None:
        # Setup LEDs
        LED_PIN = 18

        self.strip = PixelStrip(48, 2, 255, LED_PIN)

    async def loop(self) -> None:
        while True:
            await self.process_event()
            # controls the update rate of our leds
            await asyncio.sleep(.05)

    async def process_event(self) -> None:
        event = SensorManager.last_sensor_event
        if event.state == SensorState.EMPTY.value:
            self.strip.fill(Color(0, 255, 0))
            return

        event_duration = datetime.now(
            timezone.utc).timestamp() - event.rpi_time

        print(event_duration)

        first_stage_mins = .1
        if event_duration <= first_stage_mins * 60:
            # figure out how far into first stage we are 0-1
            end = inv_lerp(0, first_stage_mins * 60, event_duration)
            start = 1 - end

            # print(start, end)
            col = Color(int(lerp(0, 255, end)), int(lerp(0, 255, start)), 0)
            self.strip.fill(col)
            print("before")
        else:
            # get time sine wave
            # map from -1 to 1
            v = math.sin(datetime.now(timezone.utc).timestamp() * 1000)
            t = int(inv_lerp(1, -1, v) * 255)
            col = Color(255, 255 - t, 255 - t)
            print("After")
            self.strip.fill(col)
