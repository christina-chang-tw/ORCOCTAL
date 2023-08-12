from pyoctal.base import BaseInstrument

class ThorlabsPM100(BaseInstrument):
    """
    Thorlabs Power Monitor PM100 VISA Library

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm: str
        Argument for resource manager (for simualated device only)
    """

    def __init__(self, addr: str, rm: str=""):
        super().__init__(rsc_addr=addr, rm=rm)
        self.write("data:encd asci")

    def read(self):
        """ Read the PM power (as shown on the display). """
        return self.query("read?")
    
    def meas_power(self) -> float:
        """ Measure the PM power (as shown on the display). """
        self.write("measure:power")
        return self.query_float("fetch?")

    def set_wavelength(self, wavelength: float):
        """ Set the power monitor wavelength [nm] """
        self.write(f"sense:correction:wavelength {wavelength}")

    def set_avg_count(self, count: float):
        """ Set the average count. """
        self.write(f"sense:average:count {count}")

    def set_curr_autorange_state(self, state: bool):
        """ Set the current autoranging state. """
        self.write(f"current:range:auto {state}")

    def set_curr_reference(self, ref: float):
        """ Set the current reference value [A]. """
        self.write(f"current:reference {ref}")

    def set_pow_autorange_state(self, state: bool):
        """ Set the power autoranging state. """
        self.write(f"power:range:auto {state}")

    def set_pow_reference(self, ref: float):
        """ Set the power reference [W]. """
        self.write(f"power:reference {ref}")

    def set_volt_autorange_state(self, state: bool):
        """ Set the voltage autoranging state. """
        self.write(f"voltage:range:auto {state}")

    def set_volt_reference(self, ref: float):
        """ Set the voltage reference [V]. """
        self.write(f"voltage:reference {ref}")
