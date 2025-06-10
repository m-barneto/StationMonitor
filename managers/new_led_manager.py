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
        duration = (current_time - ctx.occupied_start_time).seconds
        state: EventState = ctx.current_event_state

        current_time = datetime.now().second

        led = self.leds[sensor]

        led.clear()

        if state == EventState.EMPTY or True:
            # blink for a second every 10 seconds
            if current_time % 10 == 0:
                # Blink logic here
                led.setPixel(0, Color(40, 255, 40))  # Set first pixel to white
                pass
            pass
        elif state == EventState.OCCUPIED_PENDING:
            pass
        elif state == EventState.OCCUPIED_STARTED:
            pass

        led.show()
    
        