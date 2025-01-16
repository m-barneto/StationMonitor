import logging
from ina219 import INA219

class BatteryManager:

    def __init__(self):
        self.ina = INA219(shunt_ohms=0.1, max_expected_amps=1.0, address=0x40, busnum=1, log_level=logging.INFO)
        self.ina.configure(gain=self.ina.GAIN_AUTO, bus_adc=self.ina.ADC_128SAMP, shunt_adc=self.ina.ADC_128SAMP, voltage_range=self.ina.RANGE_16V)

    async def loop(self) -> None:
        while True:
            # Get battery status and send it to event server, no need to deal with queues

            # sleep for configurable time
            pass
