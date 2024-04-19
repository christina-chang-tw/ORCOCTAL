from os import makedirs
from os.path import join
from sys import maxsize
import time

import numpy as np
from pyvisa import ResourceManager
from tqdm import tqdm
import pandas as pd

from pyoctal.instruments import AgilentE3640A, KeysightILME, Agilent8164B
from pyoctal.utils.file_operations import export_to_csv
from pyoctal.instruments.keysightPAS import export_to_omr

def run_ring_assisted_mzi(rm: ResourceManager, rpm_config: dict, hpm_config: dict, mm_config: dict, folder: str):
    """ 
    Try to see how the output power of a specific wavelength
    changes with the voltage of the MZI and the ring.
    """
    avg = 3
    tol = 5e-05

    heater_pm = AgilentE3640A(addr=hpm_config["addr"], rm=rm)
    ring_pm = AgilentE3640A(addr=rpm_config["addr"], rm=rm)
    mm = Agilent8164B(addr=mm_config["addr"], rm=rm)

    heater_voltages = np.arange(hpm_config["start"], hpm_config["stop"] + hpm_config["step"], hpm_config["step"])
    ring_voltages = np.arange(rpm_config["start"], rpm_config["stop"] + rpm_config["step"], rpm_config["step"])

    heater_pm.set_output_state(1)
    heater_pm.set_params(hpm_config["stop"], 0.5)
    ring_pm.set_output_state(1)
    ring_pm.set_params(rpm_config["stop"], 0.1)
    
    max_min_voltages = np.zeros(shape=(len(ring_voltages), 3))
    for i, ring_v in tqdm(enumerate(ring_voltages), total=len(ring_voltages)):
        powers = []
        currents = []
        
        ring_pm.set_volt(ring_v)

        mm.setup(0, 1550, 10, 0.2)

        for volt in heater_voltages:
            prev_curr = maxsize
            heater_pm.set_volt(volt)
            
            # wait until the current is stable
            while np.abs(heater_pm.get_curr() - prev_curr) > tol:
                prev_curr = heater_pm.get_curr()
                continue

            power = 0
            for _ in range(avg):
                power += mm.get_detect_pow()
            powers.append(power/avg)
            currents.append(prev_curr)

        export_to_csv(data=pd.DataFrame({"Voltage [V]": heater_voltages, "Power [W]": powers, "Current [A]": currents}), filename=join(folder, f"ring{ring_v}.csv"))
        
        
        max_v = heater_voltages[np.argmax(powers)]
        min_v = heater_voltages[np.argmin(powers)]
        max_min_voltages[i] = [ring_v, max_v, min_v]
    
    np.savetxt(join(folder, f"max_min_voltages.csv"), max_min_voltages, delimiter=",")
    heater_pm.set_volt(0)
    heater_pm.set_output_state(0)
    ring_pm.set_volt(0)
    ring_pm.set_output_state(0)


def main():
    rm = ResourceManager()
    folder = "data"

    rpm_config = {
        "addr": "GPIB0::5::INSTR",
        "start": 0, # [V]
        "stop": 2, # [V]
        "step": 0.01, # [V]
    }
    hpm_config = {
        "addr": "GPIB0::6::INSTR",
        "start": 0, # [V]
        "stop": 3, # [V]
        "step": 0.5, # [V]
    }
    mm_config = {
        "addr": "GPIB0::20::INSTR",
    }

    makedirs(folder, exist_ok=True)

    run_ring_assisted_mzi(rm, rpm_config, hpm_config, mm_config, folder)

if __name__ == "__main__":
    main()