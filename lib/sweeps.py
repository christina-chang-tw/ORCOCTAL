from lib.instruments.pas import ILME
from lib.csv_operations import export_csv
from lib.util import get_func_name, wait_for_next_meas

import lib.analysis as analysis
import pandas as pd
import numpy as np
from tqdm import tqdm 

class Sweeps:
    def __init__(self, dev: ILME):
        self.dev = dev
        dev.activate()

    def iloss(self, chip_name, args):
        df = pd.DataFrame()
        lf = pd.DataFrame()
        
        self.dev.sweep_params(
                start=args.range[0],
                stop=args.range[1],
                step=args.step[0],
                power=args.power[0],
            )

        for i, length in tqdm(iterable=enumerate(args.lengths), ncols=10, desc="iloss sweep", colour="1eb6cd"):
            wait_for_next_meas()
            self.dev.start_meas()
            lf[i], temp = self.dev.get_result(length)
            pd.concat([df, temp], axis = 1)
            
        
        if not lf.eq(lf.iloc[:, 0], axis=0).all(axis=1).all(axis=0):
            raise Exception("Descrepancy in wavelengths")
        
        analysis.iloss(df, np.array(lf.iloc[:,1]), self.dev.get_no_channels(), chip_name)
        export_csv(lf, chip_name, f'{get_func_name()}_lambda')
        export_csv(df, chip_name, f'{get_func_name()}_data')

        
