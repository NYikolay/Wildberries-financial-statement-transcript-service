import pandas as pd
import numpy as np


def get_sorted_unique_report_ids(data_frame: pd.DataFrame) -> np.ndarray:
    """
    Receives Pandas DataFrame as input and forms unique values in the realizationreport_id column,
    also sorts them in ascending order
    :param data_frame: Pandas DataFrame
    :return: Numpy Array
    """

    # Getting the unique realizationreport_id as an array
    unique_ids: np.ndarray = data_frame['realizationreport_id'].unique()

    # Sorting from lesser to greater
    unique_ids_sorted: np.ndarray = pd.Series(unique_ids).sort_values().values

    return unique_ids_sorted


def get_unique_nm_ids(data_frame: pd.DataFrame) -> np.ndarray:
    """
    Get unique nm_ids from a DataFrame excluding None and 99866376 values.
    :param data_frame: Pandas DataFrame object
    :return: Array of unique nm_ids
    """

    # Excluding None and nm_id == 99866376
    df: pd.DataFrame = data_frame.query("~(nm_id == 99866376)").dropna(subset=['nm_id'])

    # Getting the unique_nm_ids as an array
    unique_nm_ids: np.ndarray = df['nm_id'].unique()

    unique_nm_ids = unique_nm_ids.astype(int)

    return unique_nm_ids
