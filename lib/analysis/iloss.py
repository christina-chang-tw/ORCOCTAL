import numpy as np
import pandas as pd


def iloss_coeffs(df, wavelengths, lengths, no_channels: int=1, unit: str="um"):
    """ 
    Extract the waveguide loss coefficient and insertion loss related to each wavelength to iloss_coeffs.csv file

    Variables
        df: data dataframe 
        wavelengths: the wavelengths that are stepped through
        chip_name: the name of the chip (must be distinguishable)
    """

    df = df.transpose()

    df_coeff = pd.DataFrame()
    df_coeff["Wavelength"] = wavelengths

    for i in range(0, len(df.columns)):
        for j in range(no_channels):
            fit = np.polyfit(lengths, df.iloc[:, i].to_numpy(), deg=1)
            df_coeff.loc[i, f"CH{j} - loss [db/{unit}]"] = round(fit[0],5)
            df_coeff.loc[i, f"CH{j} - insertion loss [dB]"] = round(fit[1], 5)
    return df_coeff
   

