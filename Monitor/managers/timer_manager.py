import asyncio
from periphery import GPIO
from Monitor.managers.sensor_manager import EventState, SensorManager


class TimerManager:
    def __init__(self, sensor_manager: SensorManager):
        self.sensor_manager = sensor_manager
        # Find the bay sensor.
        for sensor in sensor_manager.sensors:
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
        TimerManager.start_io.write(False)
        await asyncio.sleep(.25)
        TimerManager.start_io.write(True)

    @staticmethod
    async def reset() -> None:
        TimerManager.reset_io.write(False)
        await asyncio.sleep(.25)
        TimerManager.reset_io.write(True)
    
