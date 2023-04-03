"""Description. 
Data  filtering transformation techniques before regression model training."""

import numpy as np 
import pandas as pd

from itertools import chain

import re

from sklearn.preprocessing import StandardScaler, MinMaxScaler

from pandas.core.frame import DataFrame
from pandas.core.series import Series

from typing import (
    Tuple, 
    Optional, 
    List, 
    Dict, 
    Union,
)

DIGIT = r"[0-9]+"

def flatten_list(list_of_lists: List) -> List: 
    """Description. Flattens list of lists to list."""

    return list(chain(*list_of_lists))

def float_to_string(x: float) -> str:
    """Description. Convert float string object to string."""

    x = str(x)
    x = x.split(".")[0]
    return x

def filter_numeric_var(df: DataFrame, var_name: str, interval: Tuple) -> DataFrame:
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

def to_object(x: Series) -> Series: 
    """Description. Transforms float column to object column."""

    if x.dtype != "object":
        x = x.astype("object")
    
    return x

def replace_inf_with_nan(df: DataFrame, var_name: Optional[str]=None) -> DataFrame: 
    """Description. Transforms infinite values to NaN in pandas DataFrame column."""

    if var_name == None:
        df = df.replace([np.inf, -np.inf], np.nan)
    else: 
        df.loc[:, var_name] = df.loc[:, var_name].replace([np.inf, -np.inf], np.nan)

    return df

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
        neighborhood_var (Optional[str]): name of neighborhood column to calculate average prices by group.
    
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
        neighborhood_var (Optional[str]): name of neighborhood column to calculate average prices by group. 
        
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

def get_dummie_names(df: DataFrame, prefix: str) -> List: 
    """Description. Get dummie names from pandas DataFrame."""

    return [col for col in df.columns if col.startswith(prefix)]

def process_window_feature(df: DataFrame) -> DataFrame:   
    """Description. 
    Convert entries with all 0 in dummies related to `baie_orientation` to 1 in 'baie_orientation_indertemine'.""" 

    dummies = get_dummie_names(df, "baie_orientation")
    new_df = df.copy() 

    if "baie_indetermine" not in dummies:
        return new_df

    else: 
        mask = (df[dummies] == 0).all(axis=1)
        new_df.loc[ 
            mask, 
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

def is_dummy(x: Union[Series, np.ndarray]) -> bool:
    """Description. Checks if a numpy array is a dummy variable."""

    if isinstance(x, Series):
        x = x.values

    x = x.astype(float)
    x = x[~np.isnan(x)]

    return np.all(np.isin(x, [0., 1.]))  

def is_numeric(x: Series) -> bool:
    """Description. Checks if a numpy array is numeric."""

    if x.dtype == "float64" and not is_dummy(x):  
        return True
    
    return False

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

def remove_reference_levels(df: DataFrame, reference_levels: Dict) -> Tuple: 
    """Description. Remove reference columns related to dummy variables."""

    removed = []

    for var, lvl in reference_levels.items(): 
        var_name = f"{var}_{lvl}"

        if var_name in df.columns: 
            df = df.drop([var_name], axis=1) 
            removed.append(var_name)

    return df, removed

def get_unique_values(df: DataFrame, col: str) -> List: 
    """Description. Returns unique values of a column in a pandas DataFrame."""

    unique_values = [
        val 
        for val in df[col].unique().tolist()
        if val == val 
    ]
    return unique_values

def get_cols_with_one_value(df: DataFrame, cols: Optional[List]=None) -> List: 
    """Description. Returns columns with only one value in a pandas DataFrame."""

    if cols == None:
        cols = df.columns.tolist()

    unique_cols = [
        col for col in cols
        if len(get_unique_values(df, col)) == 1
    ]
    return unique_cols

def get_categorical_vars(df: DataFrame, n_levels_max: int) -> List: 
    """Description. 
    Returns list of categorical variables with less than `n_levels_max` levels."""
    
    categorical_vars = [
        col for col in df.columns
        if df[col].dtype == "object"
        and len(df[col].unique()) < n_levels_max
    ]

    return categorical_vars

def get_most_frequent_levels(df: DataFrame, categorical_vars: List) -> Dict: 

    most_frequent = {}

    if "baie_orientation" in categorical_vars: 

        categorical_vars.remove("baie_orientation")

        baie_orientation_dummies = get_dummie_names(df, "baie_orientation")

        arg_max = np.argmax([
            df[var].mean()
            for var in baie_orientation_dummies
        ]) 
        ref_level = baie_orientation_dummies[arg_max]

        most_frequent["baie_orientation"] = ref_level.replace("baie_orientation_", "")

    for var in categorical_vars: 
        most_frequent[var] = df[var].value_counts().index[0]

    return most_frequent

def impute_missing_values(x: Series, dtype: str): 
    """Description. Impute missing values in pandas Series."""

    if dtype == "numeric": 
        med = x.median()
        return x.fillna(value=med)
    
    elif dtype == "category": 
        most_frequent = x.mode()[0]
        return x.fillna(value=most_frequent)
    
    else:
        raise ValueError("dtype must be 'numeric' or 'category'.")
        

def scale_features(scaler: Union[StandardScaler, MinMaxScaler], X: np.ndarray, fit: bool=False) -> Tuple:
    """Description. Scale features using a scaler.
    
    Args:
        scaler: Scaler to use.
        X: Features to scale.
        fit: Whether to fit the scaler or not.

    Returns: Scaled features and scaler."""

    if fit:
        scaler.fit(X)
        X_scaled = scaler.transform(X)

        return X_scaled, scaler

    else: 
        X_scaled = scaler.transform(X)

        return X_scaled