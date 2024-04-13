from os.path import join
from os import makedirs
import pyvisa
import argparse

from datetime import datetime
import logging
from typing import Union
import pandas as pd

from pyoctal.sweeps import (
    ILossSweep, 
    DCSweeps,
    IVSweeps,
    AMPSweeps,
    PulseSweeps
)
from pyoctal.utils.formatter import Colours, CustomArgparseFormatter
from pyoctal.utils.util import (
    setup_rootlogger,
    load_config,
)
from pyoctal.utils.file_operations import export_to_csv

LOG_FNAME = "./logging.log"
root_logger = logging.getLogger()
setup_rootlogger(root_logger, LOG_FNAME)
logger = logging.getLogger(__name__)


TEST_TYPES = ("passive", "dc", "ac", "iv", "amp", "pulse")


class SweepTestInfo:
    """
    Sweep Test Information
    """
    def __init__(self, folder, fname):
        self.folder = folder
        self.fname = fname

    def passive(self, configs):
        """ Information about passive testing """
        self.fname = self.fname + "_passive_info.csv"
        info = {
            "Power [dBm]" : configs.power,
            "Start wavelength [nm]" : configs.w_start,
            "Stop wavelength [nm]" : configs.w_stop,
            "Wavelength step [pm]" : configs.w_step,
            "Lengths [um]" : [", ".join(map(str, configs.lengths) if configs.lengths is not None else "")],
        }
        return info

    def dc(self, configs):
        """ Information about dc testing """
        self.fname = self.fname + "_dc_info.csv"
        info = {
            "Power [dBm]" : configs.power,
            "Start voltage [V]" : configs.v_start,
            "Stop voltage [V]" : configs.v_stop,
            "Step voltage [V]" : configs.v_step,
            "Cycle" : configs.cycle,
            "Wavelength start [nm]" : configs.w_start,
            "Wavelength stop [nm]" : configs.w_stop,
            "Wavelength step [nm]" : configs.w_step,
            "Scan speed [nm/s]" : configs.w_speed,
        }
        return info

    def iv(self, configs):
        """ Information about iv testing """
        self.fname = self.fname + "_iv_info.csv"
        info = {
            "Start voltage [V]" : configs.v_start,
            "Stop voltage [V]" : configs.v_stop,
            "Step voltage [V]" : configs.v_step,
            "Time step [s]" : configs.t_step,
        }
        return info
    
    def amp(self, configs):
        """ Information about amp testing. """
        self.fname = self.fname + "_amp_info.csv"
        info = {
            "Mode" : configs.mode,
            "Start Value" : configs.start,
            "Stop Value" : configs.stop,
            "Step Value" : configs.step,
        }
        return info

    def pulse(self, configs):
        """ Information about pulse testing. """
        self.fname = self.fname + "_pulse_info.csv"
        info = {
            "Wavelength" : configs.wavelength,
            "Start voltage [V]" : configs.v_start,
            "Stop voltage [V]" : configs.v_stoop,
            "Cycle" : configs.cycle,
            "Average transmission at quad": configs.avg_transmission_at_quad,
            "Current filename": configs.current_filename,
            "Power filename": configs.power_filename,
            "Phase filename": configs.phase_filename,
        }
        return info

    @staticmethod
    def print(info):
        for key, value in info.items():
            if isinstance(value, Union[tuple, list]):
                if value is not None:
                    logger.info(f'{key:<25} : {", ".join(value)}')
                else:
                    logger.info(f'{key:<25} :')
            elif isinstance(value, Union[str, float, int]):
                logger.info(f'{key:<25} : {value:}')
            else:
                raise ValueError("Values invalid.")
            
        


def log_setup_info(ttype, configs, ttype_configs):
    """
    Print the setup information for each test
    """
    
    logger.info("")
    logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    logger.info("##############################################")
    logger.info("## TEST INFORMATION:                        ##")
    logger.info("##############################################")
    logger.info("")
    logger.info(Colours.underline + Colours.bold + Colours.italic + "General Variables" + Colours.end)
    logger.info(f'{"Folder":<10} : {configs.folder:<12}')
    logger.info(f'{"Filename":<10} : {configs.fname:<12}')
    logger.info(f'{"Test Type":<10} : {ttype:<12}')
    logger.info(f'{"Funcion":<10} : {configs.func:<12}')
    logger.info(f'{"Address":<10} :')
    for instr_type in configs.instr_addrs.keys():
        addr = configs.instr_addrs[instr_type]
        if isinstance(addr, list):
            addr_str = ", ".join(addr)
            no = len(addr)
        else:
            addr_str = addr
            no = 1
        logger.info(f'  {instr_type:<6} - {no} - {addr_str}')
    logger.info("")

    logger.info(Colours.underline + Colours.bold + Colours.italic + "Test-Specific Variables" + Colours.end)
    testinfo = SweepTestInfo(configs.folder, configs.fname)
    info = []
    if ttype == "passive":
        info = testinfo.passive(ttype_configs)
    elif ttype == "ac":
        pass
    elif ttype == "dc":
        info = testinfo.dc(ttype_configs)
    elif ttype == "iv":
        info = testinfo.iv(ttype_configs)
    elif ttype == "amp":
        info = testinfo.amp(ttype_configs)
    elif ttype == "pulse":
        info = testinfo.pulse(ttype_configs)

    testinfo.print(info)
    if not ttype == "amp": # don't export for amp info file for sweeps
        export_to_csv(data=pd.DataFrame(info.items(), columns=['Params', 'Value']), filename=join(configs.folder, f"{configs.fname}_info.csv"))
    logger.info("")


def test_distribution(ttype, configs, ttype_configs):
    """ 
    Distribute tests 
        type: test type,
        configs: containing all input arguments
    """
    folder = configs.folder
    # create a folder for the test chip if this has not been done so
    makedirs(folder, exist_ok=True)
    log_setup_info(ttype, configs, ttype_configs)
    rm = pyvisa.ResourceManager()
    
    if ttype == "passive":
        cls = ILossSweep
    elif ttype == "ac":
        pass
    elif ttype == "dc":
        cls = DCSweeps
    elif ttype == "iv":
        cls = IVSweeps
    elif ttype == "amp":
        cls = AMPSweeps
    elif ttype == "pulse":
        cls = PulseSweeps
    

    sweep = cls(
        rm=rm,
        ttype_configs=ttype_configs, 
        instr_addrs=configs.instr_addrs,
        folder=configs.folder,
        fname=configs.fname,
    )
    
    # run the sweep function
    func = getattr(sweep, configs.func)
    if configs.func == "run_ilme":
        func(configs.passive.lengths)
    else:
        func()
        

def main():
    """ Run this when this file is called. """

    desc = """
Automated Sweep Testing for Optical Chips

Example:
Run a dc sweep test with logging level as DEBUG and specify a path for a config file
    
    > python -m sweep_main -t dc --log-lvl DEBUG --config ./config/<fname>.yaml
    """

    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=CustomArgparseFormatter)
    parser.add_argument(
        "-t",
        "--test",
        dest="test",
        metavar="",
        nargs=1,
        type=str,
        help="Tests: " + ", ".join(TEST_TYPES),
        required=True,
    )

    config_path = "./configs/sweep_config.yaml"
    parser.add_argument(
        "-f",
        "--filepath",
        dest="filepath",
        metavar="",
        nargs=1,
        type=str,
        default=(config_path,),
        help=f'Path to a config file.',
        required=False,
    )

    args = parser.parse_args()
    ttype = args.test[0]

    configs = load_config(args.filepath[0])
    ttype_configs = configs[ttype]
    test_distribution(ttype, configs, ttype_configs)
    

if __name__ == "__main__":
    main()
    

