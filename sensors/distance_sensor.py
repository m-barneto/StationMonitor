
import asyncio
from dataclasses import dataclass

import serial

from sensors.sensor import Sensor, SensorState
from utils.config import Config, DistanceSensorConfig

def parse_sensor_data(packet):
    # Dynamic Distance (Dis1): 2 bytes (5-6)
    dis1 = int.from_bytes(packet[5:7], byteorder='big')
    # Stable Distance (Dis2): 2 bytes (7-8)
    dis2 = int.from_bytes(packet[7:9], byteorder='big')
    # Signal Strength? idek..: 2 bytes (9-10) This is only described as 'Strength'
    strength = int.from_bytes(packet[9:11], byteorder='big')
    # temp: 2 bytes (11-12) (NOT DIVIDED BY 10)
    temp = int.from_bytes(packet[11:13], byteorder='big')
    return dis1, dis2, strength, temp

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

class DistanceSensor(Sensor):
    def __init__(self, config: DistanceSensorConfig, event_queue: asyncio.Queue):
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
        return self.stable_distance < self.occupied_distance

    async def loop(self) -> None:
        while True:
            print("Opening serial port: ", self.port)
            try:
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
                        
                        current_distance, stable_distance, reflection_strength, temperature = parse_sensor_data(packet)
                        self.current_distance = current_distance
                        self.stable_distance = stable_distance
                        self.reflection_strength = reflection_strength
                        self.temperature = temperature
                        self.state = SensorState.OCCUPIED if self.is_occupied() else SensorState.EMPTY
                        ser.flushInput()
                        await asyncio.sleep(float(1 / Config.get().sensorPollRate))
            except serial.SerialException as e:
                print(f"Serial error: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)
