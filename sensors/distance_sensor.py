
import asyncio
from dataclasses import dataclass

import serial

from sensors.sensor import Sensor, SensorState

def parse_sensor_data(packet):
    #Dis1 = 3 bytes at positions 5,6 as 24-bit integer
    dis1 = int.from_bytes(packet[5:7], byteorder='big')
    #Dis2 = 2 bytes at positions 7,8 as 16-bit integer
    dis2 = int.from_bytes(packet[7:9], byteorder='big')
    return dis1, dis2

def decode_distance_packet(packet):
    """Decode distance measurement packet"""
    if len(packet) < 14:
        return None

    # Distance is typically in the first 16-bit value (little-endian)
    distance_mm = (packet[5] << 8) | packet[6]

    # Checksum verification
    calculated_csum = sum(packet[:-1]) & 0xFF
    valid = packet[-1] == calculated_csum

    return {
        'distance_mm': distance_mm,
        'raw_values': [
            (packet[5] << 8) | packet[6],  # Primary distance
            (packet[7] << 8) | packet[8],  # Often secondary/confirmation
            (packet[9] << 8) | packet[10]  # Usually diagnostic
        ],
        'checksum': f"{packet[-1]:02X}",
        'valid': valid
    }

def get_port_from_serial(serial_number: str):
    """Get the port of the sensor based on its serial number."""

    import serial.tools.list_ports

    ports = serial.tools.list_ports.comports()

    for port in ports:
        if port.serial_number == serial_number:
            return port.device
    return None

@dataclass
class DistanceSensorConfig:
    zone: str
    serialNumber: str
    port: str
    occupiedDistance: int


class DistanceSensor(Sensor):
    def __init__(self, config: DistanceSensorConfig, event_queue: asyncio.Queue, alarm_queue: asyncio.Queue):
        """Initialize the distance sensor with the given configuration."""
        Sensor.__init__(self, config.zone, event_queue, alarm_queue)
        self.port = config.port
        self.occupied_distance = config.occupiedDistance
        self.current_distance = -1
        if not self.port:
            print("Failed to find port for serial number: ", config.serial_number)

    def is_occupied(self):
        return self.current_distance < self.occupied_distance

    async def loop(self) -> None:
        while True:
            print("Opening serial port: ", self.port)
            with serial.Serial(
                port=self.port,  # e.g., '/dev/ttyUSB0' for linux (depends but yea)
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            ) as ser:
                while True:
                    # Find the start of the packet (0xAA)
                    header = ser.read(1)
                    if header != b'\xaa':
                        continue
                    
                    # Read the remaining 14 bytes to complete the 15-byte packet
                    packet = header + ser.read(14)
                    if len(packet) != 15:
                        continue  # Skip incomplete packets
                    
                    dis1, dis2 = parse_sensor_data(packet)
                    self.current_distance = dis1
                    self.state = SensorState.OCCUPIED if self.is_occupied() else SensorState.EMPTY
                    print(f"Dynamic Distance: {dis1} mm")
                    ser.flushInput()
                    await asyncio.sleep(.25)
