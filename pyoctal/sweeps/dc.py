import time
from os.path import join

import pandas as pd
from tqdm import tqdm

from pyoctal.instruments import AgilentE3640A, Agilent8163B, KeysightILME
from pyoctal.instruments.keysightPAS import export_to_omr
from pyoctal.instruments.base import BaseSweeps
from pyoctal.utils.file_operations import export_to_csv

class DCSweeps(BaseSweeps):
    """
    DC Sweeps

    This sweeps through the voltage range and obtains the information
    about the insertion loss against wavelength 

    Parameters
    ----------
    ttype_configs: dict
        Test type specific configuration parameters
    instr_addrs: map
        All instrument addresses
    rm:
        Pyvisa resource manager
    folder: str
        Path to the folder
    fname: str
        Filename
    """
    def __init__(self, ttype_configs: dict, instr_addrs: dict, rm, folder: str, fname: str):
        super().__init__(instr_addrs=instr_addrs, rm=rm, folder=folder, fname=fname)
        self.v_start = ttype_configs.v_start
        self.v_stop = ttype_configs.v_stop
        self.v_step = ttype_configs.v_step
        self.cycles = ttype_configs.cycles
        self.w_start = ttype_configs.lambda_start,
        self.w_stop = ttype_configs.lambda_stop,
        self.w_step = ttype_configs.lambda_step*pow(10, 3)
        self.w_speed = ttype_configs.lambda_speed
        self.power = ttype_configs.power
        self.omr_save = ttype_configs.omr_save
        self.currents = []
        self.df = pd.DataFrame()


    def run_ilme(self):
        """ Run with ILME engine """
        self.instrment_check("pm", self._addrs.keys())

        pm = AgilentE3640A(addr=self._addrs.pm, rm=self._rm)
        ilme = KeysightILME()
        ilme.activate()

        for volt in tqdm(range(self.v_start, self.v_stop+self.v_step, self.v_step)):
            pm.set_volt(volt)
            time.sleep(0.1)
            self.currents.append(pm.get_curr()) # get the current value

            ilme.start_meas()
            wavelength, loss, omr_data = ilme.get_result()
            self.df["Wavelength"] = wavelength
            self.df["Loss [dB]"] = loss

            export_to_csv(data=self.df, filename=join(self.folder, f"{volt}V.csv"))

            if self.omr_save:
                export_to_omr(omr_data, join(self.folder, f"{volt}V.omr"))

        pm.set_volt(0)


    def run_one_source(self):
        """ Run only with instrument. Require one voltage source """
        self.instrment_check(("pm", "mm"), self._addrs.keys())
        pm = AgilentE3640A(addr=self._addrs.pm, rm=self._rm)
        mm = Agilent8163B(addr=self._addrs.mm, rm=self._rm)

        for volt in tqdm(range(self.v_start, self.v_stop+self.v_step, self.v_step)):
            pm.set_volt(volt)
            time.sleep(0.1)
            self.currents.append(pm.get_curr()) # get the current value

            pm.set_volt(0)

            # get the loss v.s. wavelength
            self.df[f"{volt}V"] = mm.run_laser_sweep_auto(
                power=self.power, 
                lambda_start=self.w_start,
                lambda_stop=self.w_stop,
                lambda_step=self.w_step,
                lambda_speed=self.w_speed,
                cycles=self.cycles,
                )
            
            export_to_csv(data=self.df, filename=join(self.folder, f"{self.fname}.csv"))
        
        pm.set_volt(0)
        pm.set_output_state(0)

        
        

        
