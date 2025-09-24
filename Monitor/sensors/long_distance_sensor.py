import asyncio
from dataclasses import dataclass
import serial
from sensors.sensor import Sensor, SensorState
from utils.config import Config, LongDistanceSensorConfig
import time

def parse_sensor_data(packet):
    ret = {
        'error': None,
        'details': None,
        'distance': -1,
        'strength': -1,
        'strength_percent': -1,
        'temperature': -1,
        'timestamp': time.time()
    }
    if len(packet) == 9 and packet[0] == 0x59 and packet[1] == 0x59:
        checksum = sum(packet[:8]) & 0xFF
        if checksum != packet[8]:
            ret['error'] = 'checksum_error'
            ret['details'] = {
                'expected': packet[8],
                'actual': checksum
            }
            return ret
        distance = int.from_bytes(packet[2:4], byteorder='little') * 10  # Convert to mm
        strength = int.from_bytes(packet[4:6], byteorder='little')
        temp_raw = int.from_bytes(packet[6:8], byteorder='little')
        temperature = temp_raw / 8.0 - 256.0
        strength_percent = (strength / 65535.0) * 100.0
        # Filter out invalid distance values (per manual: 65535 = invalid)
        # if distance in (4500, 65534, 65535):
        #     ret['error'] = 'invalid_measure'
        #     ret['distance'] = distance
        #     ret['strength'] = strength
        #     ret['temperature'] = temperature
        #     return ret
#FORMATTING FOR OUTPUT HERE:
        ret['distance'] = distance
        ret['strength'] = strength
        ret['strength_percent'] = strength_percent
        ret['temperature'] = temperature
        return ret

    ret['error'] = 'unknown_frame'
    ret['details'] = {
        'data': packet
    }
    return ret

def get_port_from_serial(serial_number: str):
    """Get the port of the sensor based on its serial number."""

    import serial.tools.list_ports

    ports = serial.tools.list_ports.comports()

    for port in ports:
        if port.serial_number == serial_number:
            return port.device
    return None

class LongDistanceSensor(Sensor):
    def __init__(self, config: LongDistanceSensorConfig, event_queue: asyncio.Queue):
        """Initialize the distance sensor with the given configuration."""
        Sensor.__init__(self, config.zone, event_queue)
        if "tty" in config.serialNumber:
            self.port = config.serialNumber
        else:
            print("Using serial number to find port: ", config.serialNumber)
            self.port = get_port_from_serial(config.serialNumber)
            print("Found port: ", self.port)
        self.occupied_distance = config.occupiedDistance
        self.empty_reflection_strength = config.emptyReflectionStrength
        self.current_distance = -1
        self.stable_distance = -1
        self.reflection_strength = -1
        self.temperature = -1
        self.readings = []
        if not self.port:
            print("Failed to find port for serial number: ", config.serialNumber)

    def is_occupied(self):
        return self.stable_distance < self.occupied_distance or self.reflection_strength < self.empty_reflection_strength

    async def loop(self) -> None:
        while True:
            print("Opening serial port: ", self.port)
            try:
                with serial.Serial(
                    port=self.port,  # e.g., '/dev/ttyUSB1' for linux (depends but yea)
                    baudrate=115200,
                    #bytesize=serial.EIGHTBITS,
                    #parity=serial.PARITY_NONE,
                    #stopbits=serial.STOPBITS_ONE,
                    timeout=1  # Set a timeout for read operations
                ) as ser:
                    print("Serial port opened successfully.")
                    while True:
                        header1 = ser.read(1)
                        header2 = ser.read(1)
                        if header1 != b'\x59':
                            print("Invalid header byte, skipping...")
                            continue
                        if header2 != b'\x59':
                            print("Invalid header byte, skipping...")
                            continue
                        # Read the remaining 14 bytes to complete the 15-byte packet
                        packet = header1 + header2 + ser.read(7)
                        if len(packet) != 9:
                            continue  # Skip incomplete packets
                        result = parse_sensor_data(packet)

                        if result['error']:
                            continue

                        if result['strength'] <= self.empty_reflection_strength:
                            result['distance'] = 0
                        self.readings.insert(0, int(result['distance']))
                        if len(self.readings) > 20:
                            self.readings.pop()
                        sorted_readings = sorted(self.readings)
                        # Set stable distance as the median of the last 20 readings
                        self.stable_distance = sorted_readings[len(sorted_readings) // 2]
                        #self.stable_distance = int(sum(self.readings) / len(self.readings))
                        self.current_distance = result['distance']
                        self.reflection_strength = result['strength']
                        self.temperature = result['temperature']
                        self.state = SensorState.OCCUPIED if self.is_occupied() else SensorState.EMPTY
                        ser.flushInput()
                        await asyncio.sleep(float(1 / Config.get().sensorPollRate))
            except serial.SerialException as e:
                print(f"Serial error: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)