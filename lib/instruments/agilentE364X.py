from lib.base import BaseInstrument

class AgilentE3640A(BaseInstrument):
    """
    Agilent E3640A Power Meter VISA Library

    Parameters
    ----------
    addr: str
        The address of the instrument
    """

    def __init__(self, addr: str="GPIB0::4::INSTR"):
        super().__init__(rsc_addr=addr) 

    def setup(self):
        self.reset()
        self.set_output_status(status=1)

    def set_output_status(self, status: bool=1):
        self.write(f"output {status}")

    def set_volt(self, volt: float=0):
        self.write(f"voltage {volt}")
    
    def set_curr(self, curr: float=0):
        self.write(f"current {curr}")

    def set_params(self, volt: float=0, curr: float=0):
        self.write(f"apply {volt}, {curr}")

    def read_params(self) -> list:
        return self.query("apply?")

    def read_curr(self) -> float:
        return self.query_float("measure:current?")
    
    def read_volt(self) -> float:
        return self.query_float("measure:voltage?")
    


class AgilentE3645(BaseInstrument):
    pass