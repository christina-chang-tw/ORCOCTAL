""" 
Functions related to CSV or Excel operations 
"""

from lib.util.util import get_result_dirpath
from lib.error import *

import pandas as pd
import logging
from typing import Union
import os.path


logger = logging.getLogger(__name__)


def get_dataframe_from_csv(path: str, fname: str,) -> pd.DataFrame:
    try:
        path_to_file = f'{path}/{fname}.csv'
        if not os.path.isfile(path_to_file):
            raise FileExistsError(f"Error code {FILE_NOT_EXIST_ERR}: {error_message[FILE_NOT_EXIST_ERR]}")
        elif os.stat(path_to_file).st_size == 0:
            raise ImportError(f"Error code {FILE_EMPTY_ERR}: {error_message[FILE_EMPTY_ERR]}")
        return pd.read_csv(path_to_file, encoding='utf-8')
    except FileExistsError as error:
        raise error
    except ImportError as error:
        raise error  


def get_dataframe_from_excel(path: str, fname: str, sheet_names: Union[tuple, list]) -> pd.DataFrame:

    try:
        path_to_file = f'{path}/{fname}.xlsx'
        if not os.path.isfile(path_to_file):
            raise FileExistsError(f"Error code {FILE_NOT_EXIST_ERR}: {error_message[FILE_NOT_EXIST_ERR]}")
        elif os.stat(path_to_file).st_size == 0:
            raise ImportError(f"Error code {FILE_EMPTY_ERR}: {error_message[FILE_EMPTY_ERR]}")

        xl = pd.ExcelFile(path_to_file)
        # make a dictionary of {sheet: sheetdata}
        data = {name: xl.parse(sheet_name=name) for name in sheet_names if name != "Overview"}
        return data
    except Exception as error:
        raise error



def export_to_csv(data: pd.DataFrame, path: str=get_result_dirpath("XXX"), fname: str="XXX"):
    path_to_file = f"{path}/{fname}.csv"

    with open(path_to_file, 'w', encoding='utf-8') as f:
        data.to_csv(f, index=False)


def export_to_excel(data: Union[pd.DataFrame, list, tuple], sheet_names: Union[tuple, list]=["sheet"], path: str=get_result_dirpath("XXX"), fname: str="XXX"):
    path_to_file = f"{path}/{fname}.xlsx"

    with pd.ExcelWriter(path_to_file) as writer:
        if isinstance(data, pd.DataFrame):
            data.to_excel(writer, sheet_name=f"{sheet_names[0]}", index=False)
        elif isinstance(data, Union[list, tuple]):
            [df.to_excel(writer, sheet_name=f"{sheet_names[i]}", index=False) for i, df in enumerate(data)]

