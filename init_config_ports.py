import json
import serial.tools.list_ports as list_ports
import pyjson5

from utils.config import Config, LongDistanceSensorConfig

ports = list_ports.comports()

usb_ports = [port for port in ports if port.manufacturer and ("FTDI" in port.manufacturer or "Prolific" in port.manufacturer)]

# load config.jsonc file into a json object while retaining comments

config = Config.get()

config.reflectiveSensors = []
config.distanceSensors = []
config.longDistanceSensors = []
i = 1
for port in usb_ports:
    sensor_config = LongDistanceSensorConfig(i, port.device, 5000, 100)
    config.longDistanceSensors.append(sensor_config)
    i += 1

with open("./config.jsonc", "w") as f:
    json.dump(config.to_dict(config), f, indent=4)