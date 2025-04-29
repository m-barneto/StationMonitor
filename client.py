import asyncio
import RPi.GPIO as GPIO  # type: ignore

from managers.alarm_manager import AlarmManager
from managers.config_manager import ConfigManager
from managers.event_manager import EventManager
from managers.health_manager import HealthManager
from managers.sensor_manager import SensorManager
from managers.led_manager import LedManager

from managers.server_manager import ServerManager
from managers.sleep_manager import SleepManager
from sensors.distance_sensor import DistanceSensor, DistanceSensorConfig, get_port_from_serial
from utils.config import Config
from utils.utils import PixelStrip

try:
    get_port_from_serial("test")
    # Initialize our queues
    event_queue = asyncio.Queue()
    alarm_queue = asyncio.Queue()

    # Create main event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Manager that sends out requests containing event data
    event_manager = EventManager(event_queue)
    loop.create_task(event_manager.loop())

    # Sends out requests for alarm events when duration is exceeded
    loop.create_task(AlarmManager(alarm_queue).loop())

    # Syncs config from lenovo
    loop.create_task(ConfigManager().loop())

    # Handles sleep state when site is closed
    sleep_manager = SleepManager()
    loop.create_task(sleep_manager.loop())

    # List to store sensor managers in
    reflective_sensors = []

    # Initialize sensors from config entries
    for ref_sensor in Config.get()["reflectiveSensors"]:
        # Initialize our led strip
        leds = PixelStrip(Config.get()["leds"]["numLeds"],
                          ref_sensor["indicatorPin"],
                          ref_sensor["pwmChannel"],
                          Config.get()["leds"]["brightness"])
        print(leds)

        s = SensorManager(
            ref_sensor["gpioPin"],
            ref_sensor["zone"],
            ref_sensor["alarmDuration"],
            event_queue,
            alarm_queue
        )
        reflective_sensors.append(s)

        # Setup led manager for this sensor
        l = LedManager(s, leds)

        # Initialize our event loops for the sensor managers
        loop.create_task(s.loop())
        loop.create_task(l.loop())


    distance_sensors = []

    for dist_sensor in Config.get()["distanceSensors"]:
        config: DistanceSensorConfig = DistanceSensorConfig(**dist_sensor)
        print(config)
        s = DistanceSensor(
            config,
            event_queue,
            alarm_queue
        )
        
        distance_sensors.append(s)

        loop.create_task(s.loop())

    # Web server that displays current status of sensors to web
    server = ServerManager(reflective_sensors, distance_sensors, event_manager, sleep_manager)
    loop.create_task(server.loop())

    status_updater = HealthManager()
    loop.create_task(status_updater.loop())

    # Start our event loop
    loop.run_forever()
finally:
    # Cleanup GPIO pin
    GPIO.cleanup()
