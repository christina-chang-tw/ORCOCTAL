from lib.base import BaseInstrument
import time

class ThorlabsPM100(BaseInstrument):
    """Class to control a Thorlabs Power Monitor PM100"""
    def __init__(self, addr):
        super().__init__(rsc_addr=addr)
        self.write("data:encd asci")

    def read(self):
        # Read the PM power (as shown on the display)
        return self.query("read?")
    
    def meas_power(self):
        # Measure the PM power (as shown on the display)
        self.write("measure:power")
        return self.query("fetch?")

    def set_wav(self, wavelength):
        # Set the power monitor wavelength [nm]
        self.write(f"sense:correction:wavelength {wavelength}")

    def set_avg_count(self, count):
        self.write(f"sense:average:count {count}")

    def set_curr_autorange_state(self, state: bool=1):
        self.write(f"current:range:auto {state}")

    def set_curr_reference(self, ref: float):
        self.write(f"current:reference {ref}")

    def set_pow_autorange_state(self, state: bool=1):
        self.write(f"power:range:auto {state}")

    def set_pow_reference(self, ref: float):
        self.write(f"power:reference {ref}")

    def set_volt_autorange_state(self, state: bool=1):
        self.write(f"voltage:range:auto {state}")

    def set_volt_reference(self, ref: float):
        self.write(f"voltage:reference {ref}")
