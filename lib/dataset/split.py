from pandas.core.frame import DataFrame
from pandas.core.series import Series 
from typing import List, Optional, Tuple, Union

import numpy as np 

def sort_transaction_dates(df: DataFrame, date_var: str) -> Series: 
    """Description. Store id_mutation and date_mutation."""

    transaction_dates = df[date_var].sort_values(ascending=True)
    return transaction_dates 

def temporal_train_test_split(df: DataFrame, date_var: str, train_prop: float) -> Tuple: 
    """Description. Temporal train/test split. 
    
    Args:
        df (DataFrame): DataFrame to split.
        date_var (str): Date variable.
        train_prop (float): Proportion of training set.

    Returns:
        Tuple containing:
            df_train (DataFrame): Training set.
            df_test (DataFrame): Test set.
    """

    transaction_dates = sort_transaction_dates(df, date_var)

    train_size = int(transaction_dates.shape[0] * train_prop)
    training_idxs = transaction_dates[:train_size].index

    df_train = df.loc[df.index.isin(training_idxs), :].sort_values(by=date_var)
    df_test = df.loc[~df.index.isin(training_idxs), :].sort_values(by=date_var)

    train_dates = sort_transaction_dates(df_train, date_var)
    test_dates = sort_transaction_dates(df_test, date_var)

    df_train.drop(columns=date_var, inplace=True), 
    df_test.drop(columns=date_var, inplace=True)

    df_train.dropna(axis=0, inplace=True)
    df_test.dropna(axis=0, inplace=True)

    return (
        df_train,
        df_test, 
        train_dates, 
        test_dates 
    )  

def get_feature_vector(
    df: DataFrame, 
    return_features: bool=False, 
    return_df: bool=True, 
    target: Optional[str]=None, 
    features: Optional[List]=None
) -> Union[Tuple, DataFrame, np.ndarray]:
    """Description. Get feature vector.
    
    Args:
        df (DataFrame): DataFrame to extract features from.
        return_features (bool): Whether to return features.
        return_df (bool): Whether to return DataFrame.
        target (Optional[str]): Name of target variable.
        features (Optional[List]): List of features.
    
    Returns: 
        Union[Tuple, DataFrame, np.ndarray]: Feature vector, features."""

    if target is not None: 
        X = df.drop([target], axis=1)
        features = list(X.columns)

    elif features is not None: 
        X = df[features]

    else: 
        raise ValueError("No target or features provided.")

    if not return_df:
        X = X.values

    if return_features:
        return X, features

    return X

def get_target_vector(df: DataFrame, target: str, return_series: bool=True) -> Union[Series, np.ndarray]: 
    """Description. Get target vector.
    
    Args:
        df (DataFrame): DataFrame to extract target from.
        target (str): Name of target variable.
        return_series (bool): Whether to return Series.
        
    Returns:
        Union[Series, np.ndarray]: Target vector."""

    y = df[target]
    
    if return_series: 
        return y
    
    return y.values