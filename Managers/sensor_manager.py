import asyncio
import RPi.GPIO as GPIO

from sensor_event import SensorEvent, SensorState



class SensorManager:
    def __init__(self, SENSOR_PIN: int, q: asyncio.Queue) -> None:
        self.SENSOR_PIN = SENSOR_PIN
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.event_queue = q
        self.sensor_state: SensorState = SensorState.EMPTY
    
    async def loop(self) -> None:
        while True:
            # Get sensor state
            await self.process_sensor()
            # Sleep for configured interval
            await asyncio.sleep(.01)
    
    async def process_sensor(self) -> None:
        current_state: SensorState = GPIO.input(self.SENSOR_PIN)

        if current_state != self.sensor_state:
            # Create our event
            event = SensorEvent(current_state)

            print(f"Produced event {event.id} {event.rpi_time} {SensorState(event.state)}")
            # Enqueue the event
            await self.event_queue.put(event)

            # update our sensor_state
            self.sensor_state = current_state