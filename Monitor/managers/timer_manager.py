import asyncio
from sensors.sensor import Sensor
from periphery import GPIO

class TimerManager:
    def __init__(self, sensors: list[Sensor]):
        # Find the bay sensor.
        for sensor in sensors:
            if "BAY" in sensor.zone:
                TimerManager.bay_sensor_zone = sensor.zone
                print(TimerManager.bay_sensor_zone)
        
        TimerManager.start_io = GPIO(145, "out")
        TimerManager.reset_io = GPIO(144, "out")

        # True = not grounded
        TimerManager.start_io.write(True)
        TimerManager.reset_io.write(True)

    @staticmethod
    def is_bay(sensor_zone: str) -> bool:
        return TimerManager.bay_sensor_zone == sensor_zone

    @staticmethod
    async def start() -> None:
        # to press the button
        # set state to true for non grounded
        # set to false for .25 seconds
        print("Writing false start")
        TimerManager.start_io.write(False)
        await asyncio.sleep(.25)
        TimerManager.start_io.write(True)

    @staticmethod
    async def reset() -> None:
        print("Writing false reset")
        TimerManager.reset_io.write(False)
        await asyncio.sleep(.25)
        TimerManager.reset_io.write(True)
    
