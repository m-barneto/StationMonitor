import asyncio
from datetime import datetime, timezone
from time import time
import math
from managers.sensor_manager import EventState, SensorContext, SensorManager
from sensors.reflective_sensor import ReflectiveSensor
from sensors.sensor import Sensor
from utils.config import Config, ReflectiveSensorConfig
from utils.utils import PixelStrip, clamp, hex_to_rgb, inv_lerp
from rpi_ws281x import Color


class LedManager:
    def __init__(self, reflective_sensors: list[ReflectiveSensor], sensor_manager: SensorManager) -> None:
        self.sensors = reflective_sensors
        self.sensor_manager = sensor_manager
        self.leds: dict[str, PixelStrip] = {}
        for cfg in Config.get().reflectiveSensors:
            # Initialize the LED strip for this sensor
            self.leds[cfg.zone] = PixelStrip(Config.get().leds.numLeds, cfg.indicatorPin, cfg.pwmChannel)
            

    async def loop(self) -> None:
        while True:
            # Loop through all sensors and update their LEDs
            for sensor in self.sensors:
                self.process_sensor_new(sensor.zone)
            
            # Sleep for a short interval to avoid busy waiting
            await asyncio.sleep(0.1)
    
    def process_sensor(self, sensor: str):
        current_time = datetime.now(timezone.utc)
        # get the "stage" of the sensor
        ctx: SensorContext = self.sensor_manager.get_sensor_ctx(sensor)
        duration = (current_time - ctx.occupied_start_time).total_seconds() * 10
        state: EventState = ctx.current_event_state

        current_time = datetime.now().second

        led = self.leds[sensor]

        led.clear()
        print(state)
        if state == EventState.EMPTY:
            # blink for a second every 10 seconds
            if current_time % 10 == 0:
                # Blink logic here
                led.setPixel(0, Color(40, 255, 40))  # Set first pixel to green
        
        elif state == EventState.OCCUPIED_PENDING:
            # blink for a second every 30 seconds
            if current_time % 30 == 0:
                # Blink logic here
                led.setPixel(0, Color(255, 255, 255))  # Set first pixel to white
        
        elif state == EventState.OCCUPIED_STARTED:
            if duration < 4 * 60:
                print("Stage one")
                fill_count = int(duration / 60) + 1
                for i in range(fill_count):
                    led.setPixel(i, Color(255, 255, 255))
            if duration >= 4 * 60 and duration < 6 * 60:
                print("Stage two")
                # fill with yellow then remove some
                #led.fill(Color(255, 255, 0))
                yellow_duration = duration - (4 * 60)
                led.fill(Color(255, 255, 0))

                to_fade = Config.get().leds.numLeds - 4

                fill_count = int(to_fade * (yellow_duration / 120))  # 120 seconds is the max duration for yellow
                print(f"Filling {fill_count} pixels with yellow for {yellow_duration} seconds")

                for i in range(fill_count):
                    led.setPixel(to_fade - i + 4, Color(0, 0, 0))
            elif duration >= 6 * 60 and duration < 8 * 60:
                print("Stage three")
                # fill with yellow then remove some
                #led.fill(Color(255, 255, 0))
                blue_duration = duration - (6 * 60)
                led.fill(Color(0, 0, 255))

                to_fade = Config.get().leds.numLeds - 4

                fill_count = int(to_fade * (blue_duration / 120))  # 120 seconds is the max duration for yellow
                print(f"Filling {fill_count} pixels with below for {blue_duration} seconds")

                for i in range(fill_count):
                    led.setPixel(to_fade - i + 4, Color(0, 0, 0))
            elif duration >= 8 * 60:
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
                led.fill(output)

        led.show()
    
    def process_sensor_new(self, sensor: str):
        current_time = datetime.now(timezone.utc)
        # get the "stage" of the sensor
        ctx: SensorContext = self.sensor_manager.get_sensor_ctx(sensor)
        duration = (current_time - ctx.occupied_start_time).total_seconds()
        state: EventState = ctx.current_event_state

        current_time = time()
        led = self.leds[sensor]

        pulse_duration = 1
        pulse_period = 3

        led.clear()
        if state == EventState.EMPTY:
            time_in_cycle = current_time % pulse_period
            # Only pulse if within the pulse duration
            if time_in_cycle < pulse_duration:
                # Map time_in_cycle from [0, pulse_duration] to [0, π]
                x = math.sin(math.pi * (time_in_cycle / pulse_duration))
                # Sine wave goes from 0 → 1 → 0
                forty = int(x * 40)
                maxed = int(x * 255)
                led.setPixel(Config.get().leds.numLeds - 1, Color(forty, maxed, forty))
            else:
                led.setPixel(Config.get().leds.numLeds - 1, Color(0, 0, 0))

        elif state == EventState.OCCUPIED_PENDING:
            led.setPixel(Config.get().leds.numLeds - 1, Color(255, 255, 0))  # Set first pixel to yellow
        
        elif state == EventState.OCCUPIED_STARTED:
            if duration < 4 * 60:
                print("Stage one")

                fill_count = int(duration / 60.0)
                for i in range(fill_count):
                    led.setPixel(i, Color(255, 255, 255))
            if duration >= 4 * 60 and duration < 6 * 60:
                print("Stage two")
                for i in range(4):
                    led.setPixel(i, Color(255, 255, 0))

                yellow_duration = duration - (4 * 60)
                to_fade = Config.get().leds.numLeds - 4

                fill_count = int(to_fade * (yellow_duration / 120))  # 120 seconds is the max duration for yellow
                print(f"Filling {fill_count} pixels with yellow for {yellow_duration} seconds")

                for i in range(fill_count):
                    led.setPixel(i + 4, Color(255, 255, 255))
            elif duration >= 6 * 60 and duration < 8 * 60:
                print("Stage three")
                # fill with yellow then remove some
                #led.fill(Color(255, 255, 0))
                blue_duration = duration - (6 * 60)
                led.fill(Color(0, 0, 255))

                to_fade = Config.get().leds.numLeds - 4

                fill_count = int(to_fade * (blue_duration / 120))  # 120 seconds is the max duration for yellow
                print(f"Filling {fill_count} pixels with below for {blue_duration} seconds")

                for i in range(fill_count):
                    led.setPixel(to_fade - i + 4, Color(0, 0, 0))
            elif duration >= 8 * 60:
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
                led.fill(output)

        led.show()
        