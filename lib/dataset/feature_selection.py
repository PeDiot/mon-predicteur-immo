import numpy as np 
import pandas as pd 

from sklearn.feature_selection import mutual_info_regression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error

from typing import (
    Optional, 
    Dict, 
    List,
    Union
)

def compute_mutual_info(X: np.ndarray, y: np.ndarray, feature_names: List, n_neighbors: int=10) -> pd.Series: 
    """Description. Compute mutual information for each feature.
    
    Args:
        X (np.ndarray): Feature vector.
        y (np.ndarray): Target vector.
        feature_names (List): List of feature names.
        n_neighbors (int): Number of neighbors to use for MI estimation.
        
    Returns:
        pd.Series: Mutual information for each feature sorted in descending order."""

    mi = mutual_info_regression(
        X, 
        y, 
        discrete_features="auto", 
        n_neighbors=n_neighbors, 
        copy=True) 

    mi = pd.Series(mi, index=feature_names).sort_values(ascending=False)
    return mi

def compute_rf_importances(
        X: np.ndarray, 
        y: np.ndarray, 
        feature_names: List, 
        rf: Optional[RandomForestRegressor]=None, 
        kwargs: Optional[Dict]=None
    ) -> pd.Series: 
    """Description. Compute mean decrease Ginin for each feature from random forest.
    
    Args:
        X (np.ndarray): Feature vector.
        y (np.ndarray): Target vector.
        feature_names (List): List of feature names.
        kwargs (Optional[Dict]): arguments to pass to RandomForestRegressor.
        
    Returns:
        pd.Series: Random forest importances for each feature sorted in descending order."""

    if rf == None: 

        if kwargs == None:
            rf = RandomForestRegressor()
        else:
            rf = RandomForestRegressor(**kwargs)
        rf.fit(X, y)
        print("RandomForestRegressor fitted.")

        mape = 100 * mean_absolute_percentage_error(y, rf.predict(X))
        print(f"Train MAPE: {round(mape, 2)}%")

    importances = pd.Series(rf.feature_importances_, index=feature_names).sort_values(ascending=False)
    return importances

def select_important_features(importances: pd.Series, threshold: Union[str, float]="mean") -> List: 
    """Description. Select features for which MI is above threshold.
    
    Args:
        importances (Series): Feature Importance values.
        threshold (Union[str, float]): threshold for feature selection.
    
    Returns:
        List: List of selected features."""

    if threshold == "mean": 
        threshold = importances.mean()
    elif threshold == "25%": 
        threshold = importances.quantile(.25)
    elif threshold == "50%": 
        threshold = importances.quantile(.5)
    elif threshold == "75%":
        threshold = importances.quantile(.75)
    elif threshold == "90%": 
        threshold = importances.quantile(.90)
    elif threshold == "95%":
        threshold = importances.quantile(.95)
    elif threshold == "99%":
        threshold = importances.quantile(.99)
    elif type(threshold) == float:
        threshold = float(threshold)
    else: 
        raise ValueError(f"{threshold} is not a valid thresholding method.")

    selected_features = importances[importances > threshold].index.tolist()

    return selected_features