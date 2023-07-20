from lib.base import BaseInstrument

from typing import Union
import numpy as np

class TTiTGF3162(BaseInstrument):
    def __init__(self, addr):
        super().__init__(rsc_addr=addr)

    def set_freq(self, freq: float):
        self.write(f"frequency {freq}") # Hz

    def set_ampl(self, ampl: float):
        self.write(f"ampl {ampl}")

    def set_ampl_lolvl(self, lolvl: float):
        # set amplitude low level
        self.write(f"lolvl {lolvl}")

    def set_ampl_hilvl(self, hilvl: float):
        # set amplitude high level
        self.write(f"hilvl {hilvl}")

    def set_dc_offset(self, offset: float):
        self.write(f"dcoffs {offset}")

    def set_zload(self, zload: Union[str, float]):
        self.write(f"zload {zload}")

    def set_output_state(self, state: str):
        if state.lower() not in ("on", "off", "normal", "invert"):
            raise RuntimeError("Bad value")
        self.write(f"output {state}")

    def select_channel(self, channel: int):
        # set the channel as the destination of the
        # subsequent cmds
        if channel not in (1, 2):
            raise RuntimeError("Bad value")
        self.write(f"chn {channel}")

    def set_arb_waveform(self, array, memchan):
        # the array of values should be between -1 and 1
        # max length = 1024
        values = np.int16(array*pow(2, 15))
        self.write_binary_values(f"arb{memchan} ", values, is_big_endian=True, datatype='h')
    
    def load_arb(self, memchan):
        self.write(f"arbload arb{memchan}")

    def set_arb_output(self):
        self.write("wave arb")

    def set_arb_dc(self, memchan):
        y = 0.999*np.ones(2)
        self.set_arb_waveform(y, memchan)

    def get_arb_waveform(self, memchan):
        return self.query_binary_values(f"arb{memchan}?")