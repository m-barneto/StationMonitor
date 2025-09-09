import json
import serial.tools.list_ports as list_ports

from utils.config import Config, LongDistanceSensorConfig

ports = list_ports.comports()

for p in ports:
    print (p)

usb_ports = [port for port in ports if port.manufacturer and ("FTDI" in port.manufacturer or "Prolific" in port.manufacturer)]
print(f"Found {len(usb_ports)} USB serial ports")
for port in usb_ports:
    print(f"Port: {port.device}, Serial Number: {port.serial_number}, Manufacturer: {port.manufacturer}")
# load config.jsonc file into a json object while retaining comments

config = Config.get()

config.reflectiveSensors = []
config.distanceSensors = []
config.longDistanceSensors = []
i = 1
for port in usb_ports:
    sensor_config = LongDistanceSensorConfig(str(i), port.serial_number, 5000, 100, 18 if i == 2 else 13, 0 if i == 2 else 1)
    config.longDistanceSensors.append(sensor_config)
    i += 1

with open("./config.jsonc", "w") as f:
    json.dump(config.to_dict(config), f, indent=4)