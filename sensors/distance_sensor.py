
import asyncio

import serial

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



class DistanceSensor:
    def __init__(self, zone: str, port: str, empty_distance: int):
        self.zone: str = zone
        self.port: str = port
        self.empty_distance: int = empty_distance
        self.current_distance: int = -1

    def is_occupied(self):
        return self.current_distance + self.threshold < self.empty_distance

    async def loop(self) -> None:
        while True:
            print("Opening serial port: ", self.port)
            with serial.Serial(self.port, 9600, timeout=1) as ser:
                buffer = bytearray()

                while True:
                    buffer.extend(ser.read(ser.in_waiting))
                    read_distance: str = ""
                    # Process complete packets (14 bytes)
                    while len(buffer) >= 14:
                        # Find packet start (AA 0F 10)
                        start_idx = next((i for i in range(len(buffer)-2)
                                        if buffer[i] == 0xAA
                                        and buffer[i+1] == 0x0F
                                        and buffer[i+2] == 0x10), -1)

                        if start_idx == -1:
                            buffer.clear()
                            break

                        if len(buffer) - start_idx >= 14:
                            packet = buffer[start_idx:start_idx+14]
                            decoded = decode_distance_packet(packet)
                            if not decoded:
                                continue
                            
                            read_distance = decoded["distance_mm"]

                            buffer = buffer[start_idx+14:]
                        else:
                            break

                    self.current_distance = read_distance
                    await asyncio.sleep(.5)
