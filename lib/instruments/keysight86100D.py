from lib.base import BaseInstrument
from lib.error import *

from typing import Union
class Keysight86100D(BaseInstrument):
    """
    Keysight 86100D Wide-Bandwidth Oscilloscope VISA Library

    Parameters
    ----------
    addr: str
        The address of the instrument
    chan: int, default = 1
        The input channel
    clk_num: int, default = 1
        The clock recovery number
    """

    def __init__(self, addr: str, chan: int=1, clk_num: int=1):
        super().__init__(rsc_addr=addr)
        self.chan = chan
        self.clk_num = clk_num
        self.channel = f"channel {chan}"
        self.clock = f"crecovery {self.clk_num}"

    # Acquire commands
    def set_acq_avg_state(self, state: Union[str, bool]):
        self.write(f"acquire:average {state}")

    def set_acq_best(self, opt: str):
        self.value_check(opt.lower(), ("thr", "flat"))
        self.write(f"acquire:best {opt}")
        
    def set_acq_count(self, cnt: int):
        self.value_check(cnt, (1, 4096))
        self.write(f"acquire:count {cnt}")

    # Channel commands
    def set_chan_bandwidth(self, setting: str):
        self.value_check(setting.lower(), ("high", "mid", "low"))
        self.write(f"{self.channel}:bandwidth {setting}")

    def set_chan_connector(self, connector: str):
        self.value_check(connector.lower(), ("a", "b"))
        self.write(f"{self.channel}:connector {connector}")

    def set_chan_wavelength(self, wavelength: Union[str, float]):
        # Factory wavelengths: 
        # - wavelength1: 8.50E-007, wavelength2: 1.31E-006, wavelength3: 1.55E-006
        # - user-defined: in nm
        wavelength = wavelength*1e-09
        self.write(f"{self.channel}:wavelength {wavelength}")

    # Clock recovery
    def set_clk_arelock(self, state: Union[bool, str]):
        self.write(f"{self.clock}:arelock {state}")

    def set_clk_arelock_cancel(self):
        self.write(f"{self.clock}:arelock:cancel")

    def set_clk_lbwmode(self, mode: str):
        self.value_check(mode.lower(), ("fixed", "fix", "rdependent", "rdep"))
        self.write(f"{self.clock}:lbwmode {mode}")

    def set_clk_clbandwidth(self, bandwidth):
        # need to set LBWMode to fixed before running this cmd
        self.value_check(bandwidth, (30e+3, 20e+6))
        self.write(f"{self.clock}:clbandwidth {bandwidth}")

    def set_clk_crate(self, rate):
        self.write(f"{self.clock}:crate {rate}")

    def set_clk_input_type(self, typ):
        types = ("electrical", "elec", "optical", "opt", "differential", "diff", "einverted", "einv", "auxiliary", "aux")
        self.value_check(typ.lower(), types)
        self.write(f"{self.clock}:input {typ}")

    def set_clk_odratio(self, rdiv):
        self.write(f"{self.clock}:odratio {rdiv}")

    def set_clk_autoodratio_state(self, state: bool):
        self.write(f"{self.clock}:odratio:auto {state}")

    def get_clk_arelock_state(self):
        return self.query(f"{self.clock}:state?")
    
    def get_clk_freq(self):
        return self.query_float(f"{self.clock}:cfrequency?")
    
    def get_clk_clbandwidth(self):
        return self.query_float(f"{self.clock}:clbandwidth?")   

    def get_clk_spresent(self, num: int):
        return bool(self.query(f"{self.clock}:spresent? receiver{num}")) 
