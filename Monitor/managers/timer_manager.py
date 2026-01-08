import asyncio
from sensors.sensor import Sensor
from periphery import GPIO

class TimerManager:
    has_started = False
    start_io = None
    reset_io = None
    bay_sensor_zone = None

    def __init__(self, sensors: list[Sensor]):
        # Find the bay sensor.
        for sensor in sensors:
            if "BAY" in sensor.zone:
                TimerManager.bay_sensor_zone = sensor.zone
                print(TimerManager.bay_sensor_zone)
        
        TimerManager.start_io = GPIO(70, "out")
        TimerManager.reset_io = GPIO(71, "out")

        # True = not grounded
        TimerManager.start_io.write(True)
        TimerManager.reset_io.write(True)

        TimerManager.has_started = False

    async def loop(self) -> None:
        await TimerManager.reset()
        await asyncio.sleep(1)
        await TimerManager.reset()

    @staticmethod
    def is_bay(sensor_zone: str) -> bool:
        if TimerManager.bay_sensor_zone:
            return TimerManager.bay_sensor_zone == sensor_zone
        return False

    @staticmethod
    async def start() -> None:
        # to press the button
        # set state to true for non grounded
        # set to false for .25 seconds
        TimerManager.start_io.write(False)
        await asyncio.sleep(.25)
        TimerManager.start_io.write(True)

    @staticmethod
    async def reset() -> None:
        TimerManager.reset_io.write(False)
        await asyncio.sleep(.25)
        TimerManager.reset_io.write(True)
    
