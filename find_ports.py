import serial
import serial.tools.list_ports as list_ports

ports = list_ports.comports()

for port in ports:

    print(port.device)
    continue

    if port.manufacturer and "FTDI" in port.manufacturer:
        print(f"Serial: {port.serial_number}", end='')
        with serial.Serial(port.device, 115200, timeout=1) as ser:
            b = ser.read(5)
            if len(b) == 0:
                print(" XXXXXX")
            else:
                print(f" ✓✓✓✓✓✓", len(b), b)