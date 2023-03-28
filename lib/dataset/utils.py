"""Description. 
Data  filtering transformation techniques before regression model training."""

import numpy as np 
import pandas as pd

import re

from pandas.core.frame import DataFrame
from typing import (
    Tuple, 
    Optional, 
    List, 
    Dict, 
)

DIGIT = r"[0-9]+"

def get_na_proportion(df: DataFrame, col: str) -> float:
    """Description. Returns the proportion of missing values in pandas column."""
    
    return df[col].isna().sum() / df.shape[0]

def remove_na_cols(df: DataFrame, threshold: float) -> Tuple:
    """Description. Removes columns with missing values above threshold."""
    
    na_cols = [col for col in df.columns if get_na_proportion(df, col) > threshold]
    df = df.drop(na_cols, axis=1)
    
    return df, na_cols

def filter_df_with_quant_var(df: DataFrame, var_name: str, interval: Tuple) -> DataFrame:
        """Description. Select values inside interval for column of pandas DataFrame.
        
        Args:
            df (DataFrame): pandas DataFrame.
            var_name (str): name of column to filter.
            interval (Tuple): interval of values to select."""

        min_val, max_val = interval
        
        if min_val >= max_val: 
            raise ValueError("min_val must be lower than max_val.")
        
        if min_val == None: 
            min_val = df[var_name].min()
        
        if max_val == None: 
            max_val = df[var_name].max()

        mask = (df[var_name] >= min_val) & (df[var_name] <= max_val)
        return df[mask]

def transform_price(price: float, log:bool, area: Optional[float]=None) -> float: 
    """Description. Transforms price by dividing by area and taking log if needed."""

    y = price

    if area != None: 
        y = y / area

    if log: 
        y = np.log(y)
    
    return y 

def extract_int_from_string(string: str) -> int: 
    """Description. Extracts integer from string ."""

    integer = re.findall(DIGIT, string)

    if len(integer) > 1: 
        raise ValueError("Multiple integers found.")
    
    return integer[0]

def calc_movav_prices(
    df: DataFrame, 
    window_size: int, 
    lag: int=1, 
    price_var: str="valeur_fonciere", 
    date_var: str="date_mutation", 
    neighborhood_var: Optional[str]="arrondissement"
) -> DataFrame: 
    """Description. Compute moving average prices per neighborhood.
    
    Args:
        df (DataFrame): pandas DataFrame with price column.
        window_size (int): size of moving average window.
        lag (int): lag to apply before moving average.
        price_var (str): name of price column.
        date_var (str): name of date column.
        neighborhood_var (Optional[str]): name of neighborhood column.
    
    Returns:
        DataFrame: pandas DataFrame with moving average lagged prices.""" 

    if neighborhood_var != None: 
        by = [neighborhood_var, date_var]
    else:
        by = date_var

    avg_prices = df\
        .groupby(by)\
        [price_var]\
        .mean()\
        .shift(lag)

    if neighborhood_var != None: 
        avg_prices = avg_prices.groupby(neighborhood_var)

    mov_avg_prices = avg_prices\
        .apply(lambda x: x.rolling(window_size).mean())\
        .reset_index()\
        .rename(columns={price_var: f"{price_var}_ma{window_size}"})

    return mov_avg_prices

def add_movav_prices(
    df: DataFrame, 
    mov_av_prices: DataFrame, 
    date_var: str="date_mutation", 
    neighborhood_var: Optional[str]="arrondissement"
) -> DataFrame: 
    """Description. Merge moving average prices and DVF dataset.
    
    Args:
        df (DataFrame): pandas DataFrame with price column.
        mov_av_prices (DataFrame): pandas DataFrame with moving average lagged prices.
        date_var (str): name of date column.
        neighborhood_var (Optional[str]): name of neighborhood column.
        
    Returns:
        DataFrame: DVF dataset with moving average lagged prices."""

    keys = []
    if neighborhood_var != None: 
        keys.append(neighborhood_var) 
        
    keys.append(date_var)

    new_df = pd.merge(
        left=df, 
        right=mov_av_prices, 
        how="left", 
        left_on=keys, 
        right_on=keys)
    
    return new_df

def get_unique_values(df: DataFrame, col: str) -> List: 
    """Description. Returns unique values of a column in a pandas DataFrame."""

    unique_values = [
        val 
        for val in df[col].unique().tolist()
        if val == val 
    ]

    return unique_values

def get_cols_with_one_value(df: DataFrame, cols: list) -> DataFrame: 
    """Description. Returns columns with only one value in a pandas DataFrame."""

    unique_cols = [
        col for col in cols
        if len(get_unique_values(df, col)) == 1
    ]

    return unique_cols

def remove_cols_with_one_value(df: DataFrame, vars: List) -> DataFrame:
    """Description. Removes columns with only one value in a pandas DataFrame."""

    unique_cols = get_cols_with_one_value(df, vars)
    df = df.drop(unique_cols, axis=1)

    return df

def process_window_feature(df: DataFrame) -> DataFrame:   
    """Description. 
    Convert entries with all 0 in dummies related to `baie_orientation` to 1 in 'baie_orientation_indertemine'.""" 

    dummies = [
        "baie_orientation_indetermine",
        "baie_orientation_nord",
        "baie_orientation_ouest",
        "baie_orientation_est",
        "baie_orientation_horizontale",
        "baie_orientation_est_ou_ouest",
        "baie_orientation_sud"
    ]

    for var in dummies: 
        if var not in df.columns: 
            raise ValueError(f"Variable {var} not found in DataFrame.")

    new_df = df.copy() 
    new_df.loc[ 
        (df.baie_orientation_indetermine==0) &
        (df.baie_orientation_nord==0) &
        (df.baie_orientation_ouest==0) &
        (df.baie_orientation_est==0) &
        (df.baie_orientation_horizontale==0) &
        (df.baie_orientation_est_ou_ouest==0) &
        (df.baie_orientation_sud==0),
        "baie_orientation_indetermine"
    ] = 1

    return new_df

def get_categorical_vars(df: DataFrame) -> List: 
    """Description. Returns list of categorical variables in a pandas DataFrame.""" 
    
    categorical_vars = [
        col for col in df.columns
        if df[col].dtype == "object"
    ]

    return categorical_vars

def remove_nan_dummy_entries(df: DataFrame, nan_dummy: str) -> DataFrame: 
    """Description. Removes entries with dummy variable set to 0 in a pandas DataFrame."""

    mask = df[nan_dummy] == 0
    df = df.loc[mask, :]

    df = df.drop(labels=[nan_dummy], axis=1)

    return df

def to_dummies(df: DataFrame, categorical_vars: List) -> DataFrame: 
    """Description. Converts categorical variables to dummies in a pandas DataFrame."""

    df = pd.get_dummies(
        df, 
        columns=categorical_vars, 
        dummy_na=True, 
        drop_first=False) 
    
    for var in categorical_vars: 
        nan_dummy = var+"_nan"
        df = remove_nan_dummy_entries(df, nan_dummy)

    return df

def remove_reference_levels(df: DataFrame, reference_levels: Dict) -> DataFrame: 
    """Description. Remove reference columns from dataset."""

    for var, lvl in reference_levels.items(): 
        var_name = f"{var}_{lvl}"
        if var_name in df.columns: 
            df = df.drop([var_name], axis=1) 

    return df  