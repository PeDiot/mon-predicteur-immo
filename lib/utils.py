"""Description. Helpful functions."""

from pandas.core.frame import DataFrame 
from typing import List

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