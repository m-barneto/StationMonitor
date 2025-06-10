import asyncio
from datetime import datetime, timezone
from managers.sensor_manager import EventState, SensorContext, SensorManager
from sensors.reflective_sensor import ReflectiveSensor
from sensors.sensor import Sensor
from utils.config import Config, ReflectiveSensorConfig
from utils.utils import PixelStrip
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
                self.process_sensor(sensor.zone)
            
            # Sleep for a short interval to avoid busy waiting
            await asyncio.sleep(0.1)
    
    def process_sensor(self, sensor: str):
        current_time = datetime.now(timezone.utc)
        # get the "stage" of the sensor
        ctx: SensorContext = self.sensor_manager.get_sensor_ctx(sensor)
        duration = (current_time - ctx.occupied_start_time).seconds * 10
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
            elif duration >= 6 * 60:
                print("Stage three")
                # fill with yellow then remove some
                #led.fill(Color(255, 255, 0))
                blue_duration = duration - (4 * 60)
                led.fill(Color(0, 0, 255))

                to_fade = Config.get().leds.numLeds - 4

                fill_count = int(to_fade * (blue_duration / 120))  # 120 seconds is the max duration for yellow
                print(f"Filling {fill_count} pixels with below for {blue_duration} seconds")

                for i in range(fill_count):
                    led.setPixel(to_fade - i + 4, Color(0, 0, 0))

        led.show()
    
        