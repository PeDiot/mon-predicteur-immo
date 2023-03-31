"""Description. Helpful functions."""

from pandas.core.frame import DataFrame 
from typing import List, Tuple

import pandas as pd 

def get_unique_entries(df: DataFrame, var_name: str) -> List: 
    """Description. Extract not-duplicated values related from one variable."""
    unique = df\
        .groupby(var_name)\
        .size()[lambda x: x == 1]\
        .index\
        .tolist()
    
    return unique 

def add_date_components(df: DataFrame, date_var: str) -> DataFrame: 
    """Description. Add year, quarter, month and day to dataframe."""

    new_df = df.copy()
    new_df[date_var] = pd.to_datetime(df[date_var])

    new_df["annee"] = new_df[date_var].dt.year
    new_df["trimestre"] = new_df[date_var].dt.quarter
    new_df["mois"] = new_df[date_var].dt.month
    new_df["jour"] = new_df[date_var].dt.day
    
    return new_df

def get_na_proportion(df: DataFrame, col: str) -> float:
    """Description. Returns the proportion of missing values in pandas column."""
    
    return df[col].isna().sum() / df.shape[0]

def remove_na_cols(df: DataFrame, threshold: float) -> Tuple:
    """Description. Removes columns with missing values above threshold."""
    
    na_cols = [col for col in df.columns if get_na_proportion(df, col) > threshold]
    df = df.drop(na_cols, axis=1)
    
    return df, na_cols