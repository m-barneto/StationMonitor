import asyncio
from datetime import datetime, timezone
import math
from queue import Queue

from Monitor.sensors.sensor import Sensor
from managers.sensor_manager import EventState, SensorContext, SensorManager
from managers.sleep_manager import SleepManager
from utils.config import Config
from utils.utils import PixelStrip, Color, clamp, hex_to_rgb, inv_lerp
from utils.sensor_event import SensorState
import serial

led_config = {
    "numLeds": 15,
    "brightness": 255,
    "stages": [
        {
            "color": "#FFFFFF",
            "duration": 3.0
        },
        {
            "color": "#FFFF00",
            "duration": 3.0
        },
        {
            "color": "#0000FF",
            "duration": 2.0
        }
    ],
    "flashing": {
        "shouldFlash": True,
        "flashFrequency": 3.0,
        "primaryColor": "#00FF00",
        "secondaryColor": "#0000FF"
    }
}


class LedManager:
    def __init__(self, sensors: list[Sensor], sensor_manager: SensorManager) -> None:
        self.sensors = sensors
        self.sensor_manager = sensor_manager
        self.command_queue = Queue()
        # map led strip from config to sensor zone
        self.leds = {}
        for ledStripConfig in Config.get().ledStrips:
            self.leds[ledStripConfig.zone] = PixelStrip(15, ledStripConfig.ledStrip)

    async def loop(self) -> None:
        while True:
            # Keep serial communication to leds open here
            print("Opening serial port for leds")
            try:
                with serial.Serial(
                    port="/dev/ttyS5",
                    baudrate=9600,
                    timeout=1
                ) as ser:
                    print("Serial port opened successfully.")
                    while True:
                        # If we're closed, sleep for configured amount of time and skip this led iteration
                        if not SleepManager.is_open:
                            # Clear led strip
                            for sensor in self.sensors:
                                self.leds[sensor.zone].clear()
                                self.leds[sensor.zone].show()

                            await asyncio.sleep(Config.get().sleep.sleepInterval)
                            continue
                        # Get the current time
                        current_time = datetime.now(timezone.utc)

                        # Loop through all sensors and call their loop method
                        for sensor in self.sensors:
                            if not SleepManager.is_open:
                                is_empty = self.get_sensor_ctx(sensor.zone).current_event_state == EventState.EMPTY
                                if not is_empty:
                                    await self.process_event(self.leds[sensor.zone])
                            else:
                                await self.process_event(self.leds[sensor.zone])
                        
                        # Send our commands over serial to the led controller
                        while self.command_queue.qsize() != 0:
                            packet = self.command_queue.get()
                            ser.write(packet)
                        # controls the update rate of our leds
                        await asyncio.sleep(.05)
            except serial.SerialException as e:
                print(f"Serial error: {e}. Trying to open LED serial in 5 seconds...")
                await asyncio.sleep(5)

    async def process_event(self, strip: PixelStrip) -> None:
        # Clear led strip
        strip.clear()

        ctx: SensorContext = self.sensor_manager.get_sensor_ctx(self.sensor)
        if ctx == None:
            print(f"LedManager: No context found for sensor {self.sensor}")
            return

        # If event is empty, show cleared led strip and return early
        if ctx != None and ctx.previous_sensor_state == SensorState.EMPTY:
            self.command_queue.put(strip.show())
            return

        event_duration = datetime.now(timezone.utc).timestamp(
        ) - ctx.occupied_start_time.timestamp()

        # Calculate what stage we're on based on duration
        stage_index = self.get_led_stage_index(event_duration)
        # Get stage info from config
        stage = led_config["stages"][stage_index]
        # If we aren't at the end/flashing stage
        if stage_index != -1:
            # Get amount of time we're into the stage
            time_into_stage = event_duration - \
                self.get_time_before_stage(stage_index)
            # Get % of led bar to fill
            val = time_into_stage / (stage.duration * 60)
            # convert that to numpixels
            pixelsToHighlight = val * strip.ledsCount

            # Fill led strip to the %
            pixelsFloored = int(pixelsToHighlight)
            for i in range(pixelsFloored):
                strip.setPixel(i, hex_to_rgb(stage.color))

            # Take the last led and modulate the brightness for a smooth animation
            if pixelsToHighlight > pixelsFloored:
                strip.setPixel(pixelsToHighlight,
                                   hex_to_rgb(stage.color, pixelsToHighlight % 1))
        else:
            # We're in the flashing stage
            # If should flash
            if led_config["flashing"]["shouldFlash"]:
                # get time sine wave
                # map from -1 to 1
                v = math.sin(datetime.now(timezone.utc).timestamp(
                ) * led_config["flashing"]["flashFrequency"])

                # Get amount of color to be used for both colors based on time
                t = inv_lerp(1, -1, v)
                y = inv_lerp(1, -1, -v)

                # Get primary and secondary colors
                primary = hex_to_rgb(
                    led_config["flashing"]["primaryColor"], t)
                secondary = hex_to_rgb(
                    led_config["flashing"]["secondaryColor"], y)

                # Interpolate between the two
                output = Color(clamp(primary.r + secondary.r, 0, 255), clamp(primary.g +
                               secondary.g, 0, 255), clamp(primary.b + secondary.b, 0, 255))

                # Display final color
                strip.fill(output)
            else:
                # Fill with color of final stage
                strip.fill(hex_to_rgb(stage.color))
        # Display our led strip data
        self.command_queue.put(strip.show())

    def get_led_stage_index(self, time: float) -> int:
        index = 0
        # Iterate over all stages
        for stage in led_config["stages"]:
            # Subtract the stages duration from our current time
            time -= (stage.duration * 60)
            # If we have time to spare
            if time > 0:
                # Try the next stage
                index += 1
                # If we're on the last stage already return -1 since we've now gone over and should flash
                if stage == led_config["stages"][-1]:
                    return -1
        return index

    def get_time_before_stage(self, stage: int):
        time_before_stage = 0
        # Go through each stage before the input stage
        for i in range(stage):
            # Add up time from previous stages
            time_before_stage += (led_config["stages"][i]["duration"] * 60)
        return time_before_stage