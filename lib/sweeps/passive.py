from lib.instruments.pas import AgilentILME
from lib.instruments.agilent8163B import Agilent8163B
from lib.util.file_operations import export_to_csv
from lib.util.util import get_func_name, wait_for_next_meas
from lib.base import BaseSweeps

import sys
from typing import Union
import pandas as pd
from tqdm import tqdm 
import logging
import time


logger = logging.getLogger(__name__)

class PASILossSweep(BaseSweeps):
    """ This uses the ILME to sweep through the data """
    def __init__(self, dev: Union[AgilentILME, Agilent8163B], instr: Agilent8163B):
        super().__init__(instrument=instr)
        self.dev = dev
        self.dev.activate()

    def iloss_ilme(self, chip_name: str, args):
        df = pd.DataFrame()
        lf = pd.DataFrame()
        
        self.dev.sweep_params(
                start=args.range[0],
                stop=args.range[1],
                step=args.step[0],
                power=args.power[0],
            )

        for i, length in tqdm(enumerate(args.lengths), total=len(args.lengths), desc="ILOSS Sweeps"):
            self.instr.setup()
            wait_for_next_meas(i, len(args.lengths)) # this takes an input to continue to next measurement
            self.dev.start_meas()
            lf[i], temp = self.dev.get_result(length)
            df = pd.concat([df, temp], axis=1)
            export_to_csv(df, chip_name, f'{args.structure[0]}_{get_func_name()}_data')

        
        if not lf.eq(lf.iloc[:,0], axis=0).all(axis=1).all(axis=0):
            logger.warning("Discrepancy in wavelengths")
        
        export_to_csv(pd.concat([lf.iloc[:,0], df]), chip_name, f'{args.structure[0]}_{get_func_name()}_data')
        # df_coeff = iloss.iloss(df, np.array(lf.iloc[:,0]), self.dev.get_no_channels())
        # export_to_csv(df_coeff, chip_name, f'{args.structure[0]}_{get_func_name()}_coeffs')


class InstrILossSweep(BaseSweeps):
    """ This directly uses 8163B to sweep the data """
    def __init__(self, instr: Agilent8163B):
        super().__init__(instrument=instr)

    def run_sweep_manual(self, power: float=10.0, start_lambda: float=1535.0, stop_lambda: float=1575.0, step: float=5.0):
        if start_lambda <= float(instr.get_laser_wav_min()) and stop_lambda >= float(instr.get_laser_wav_min()):
            sys.exit("Wavelength out of range")
        
        instr = self.instr
        wavelengths = []
        powers = []
        instr.set_detect_autorange(1)
        instr.set_detect_avgtime(200e-03)
        instr.set_laser_pow(power)

        #### Loop through wavelengths:
        for wavelength in range(start_lambda, stop_lambda + step, step):
            tolerance = 0.001 # detector stability tolerance
            diff = prev_power = sys.maxsize # initiation
            LOOP_MAX = 20

            instr.set_wavelength(wavelength)
            
            # Make sure that the laser power is stabalised
            for _ in range(LOOP_MAX):
                time.sleep(0.5)
                detected_power = float(instr.get_detect_pow())
                diff = (detected_power - prev_power)/detected_power
                prev_power = detected_power
                if abs(diff) <= tolerance:
                    break

            wavelengths.append(wavelength)
            powers.append(detected_power)

            return wavelengths, powers
        

    def run_laser_sweep_auto(self, power: float=10.0, start_lambda: float=1535.0, stop_lambda: float=1575.0, step: float=5.0, cycles: int=1, tavg: float=100):

        instr = self.instr
        instr.set_unit(source="dBm", sensor="Watt")

        instr.set_laser_pow(power=power)
        instr.set_laser_wav(wavelength=start_lambda)
        instr.set_laser_state(status=1)
        

        instr.set_detect_wav(wavelength=1550)
        instr.set_detect_avgtime(period=1e-04)
        instr.set_detect_calibration_val(value=0)
        instr.set_detect_autorange(auto=0)
        instr.set_detect_prange(range=10)

        instr.set_trig_config(config=3)
        instr.set_laser_trig_response(in_rsp="ignored", out_rsp="stfinished")
        instr.set_detect_trig_response(in_rsp="smeasure", out_rsp="disabled")
        
        instr.set_sweep_mode(mode="continuous")
        instr.set_sweep_repeat_mode(mode="oneway")
        instr.set_sweep_cycles(cycles=cycles)
        instr.set_sweep_tdwell(time=0)
        instr.set_sweep_start_stop(start=start_lambda, stop=stop_lambda)
        instr.set_sweep_step(step=step)
        
        instr.set_detect_func_mode(mode=("logging", "stop"))
        trigno = instr.get_detect_trigno()
        instr.set_detect_func_params(mode="logging", params=(trigno, tavg*1e-06))
        instr.set_detect_func_mode(mode=("logging", "start"))
        
        instr.set_sweep_state(state="start")

        # wait for the sweep to stop
        while instr.get_sweep_state(): 
            pass

        # retrieve data
        llog_data = instr.get_laser_data()

        # Wait until the detector data acquisition is completed
        while instr.get_detect_func_status().endswith("progress"): 
            time.sleep(0.1)

        results = instr.get_detect_func_result()
        instr.set_detect_func_mode(mode=("logging","stop"))

        return llog_data, results


    
        