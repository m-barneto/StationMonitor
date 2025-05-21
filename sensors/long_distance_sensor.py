import asyncio
from dataclasses import dataclass
import serial
from sensors.sensor import Sensor, SensorState
from utils.config import Config, LongDistanceSensor
import time

def parse_sensor_data(packet):
    if len(packet) == 9 and packet[0] == 0x59 and packet[1] == 0x59:
        checksum = sum(packet[:8]) & 0xFF
        if checksum != packet[8]:
            return {
                'type': 'checksum_error',
                'expected': packet[8],
                'actual': checksum,
                'timestamp': time.time()
            }
        distance = int.from_bytes(packet[2:4], byteorder='little')
        strength = int.from_bytes(packet[4:6], byteorder='little')
        temp_raw = int.from_bytes(packet[6:8], byteorder='little')
        temperature = temp_raw / 8.0 - 256.0
        strength_percent = (strength / 65535.0) * 100.0
        # Filter out invalid distance values (per manual: 65535 = invalid)
        if distance in (4500, 65534, 65535):
            return {
                'error': 'invalid_measure', #DO SOMETHING WITH THIS TO DISREGARD AN EVENT
                'distance': distance,                                  #PLS
                'strength': strength,
                'temperature': temperature,
                'timestamp': time.time()
            }
#FORMATTING FOR OUTPUT HERE:
        return {
            'error': 'none',
            'distance': distance,
            'strength': strength,
            'strength_percent': strength_percent,
            'temperature': temperature,
            'timestamp': time.time()
        }

    return {
        'type': 'unknown_frame',
        'data': packet,
        'timestamp': time.time()
    }

def get_port_from_serial(serial_number: str):
    """Get the port of the sensor based on its serial number."""

    import serial.tools.list_ports

    ports = serial.tools.list_ports.comports()

    for port in ports:
        if port.serial_number == serial_number:
            return port.device
    return None

class LongDistanceSensor(Sensor):
    def __init__(self, config: LongDistanceSensor, event_queue: asyncio.Queue):
        """Initialize the distance sensor with the given configuration."""
        Sensor.__init__(self, config.zone, event_queue)
        if "ttyUSB" in config.serialNumber:
            self.port = config.serialNumber
        else:
            self.port = get_port_from_serial(config.serialNumber)
        self.occupied_distance = config.occupiedDistance
        self.current_distance = -1
        self.stable_distance = -1
        self.reflection_strength = -1
        self.temperature = -1
        if not self.port:
            print("Failed to find port for serial number: ", config.serialNumber)

    def is_occupied(self):
        return self.current_distance < self.occupied_distance

    async def loop(self) -> None:
        while True:
            print("Opening serial port: ", self.port)
            try:
                with serial.Serial(
                    port=self.port,  # e.g., '/dev/ttyUSB1' for linux (depends but yea)
                    baudrate=115200,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE
                ) as ser:
                    while True:
                        header1 = ser.read(1)
                        header2 = ser.read(1)
                        if header1 != b'\x59':
                            continue
                        if header2 != b'\x59':
                            continue
                        # Read the remaining 14 bytes to complete the 15-byte packet
                        packet = header1 + header2 + ser.read(7)
                        if len(packet) != 9:
                            continue  # Skip incomplete packets
                        result = parse_sensor_data(packet)
                        self.current_distance = result['distance']
                        self.reflection_strength = result['strength']
                        self.temperature = result['temperature']
                        self.state = SensorState.OCCUPIED if self.is_occupied() else SensorState.EMPTY
                        ser.flushInput()
                        await asyncio.sleep(float(1 / Config.get().sensorPollRate))
            except serial.SerialException as e:
                print(f"Serial error: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)