import numpy as np 

from sklearn.base import BaseEstimator
from sklearn.linear_model import LinearRegression

from sklearn.metrics import (
    mean_absolute_error, 
    mean_absolute_percentage_error, 
    mean_squared_error
) 

from typing import Dict, Optional

class CustomRegressor(BaseEstimator):
    """Description. A Custom BaseEstimator that can switch between regressors.
    
    Args:
        estimator (BaseEstimator): The estimator to use. Defaults to LinearRegression().""" 

    def __init__(self, estimator=LinearRegression()):
        self.estimator = estimator

    def fit(self, X: np.ndarray, y: Optional[np.ndarray]=None, **kwargs: Dict):
        """Description. Fits the estimator to the data.
        
        Args:
            X (np.ndarray): The features.
            y (np.ndarray): The target. Defaults to None.
            **kwargs (Dict): Additional arguments to pass to the estimator."""
        
        self.estimator.fit(X, y)
        return self

    def predict(self, X: np.ndarray, y: Optional[np.ndarray]=None) -> np.ndarray:
        """Description. Predicts the target given the features.
        
        Args:
            X (np.ndarray): The features.
            y (np.ndarray): The target. Defaults to None.
        
        Returns:
            np.ndarray: The predicted target."""
        return self.estimator.predict(X) 

    def score(self, X: np.ndarray, y: np.ndarray, scoring: str="r2") -> float:
        """Description. Scores the estimator given scoring method.
        Args:
            X (np.ndarray): The features.
            y (np.ndarray): The target.
            scoring (str): The scoring metric to use. Defaults to "r2".
        
        Returns:
            float: The score."""
        
        if scoring == "r2": 
            return self.estimator.score(X, y)
        elif scoring == "mae": 
            y_pred = self.predict(X)
            return mean_absolute_error(y, y_pred)
        elif scoring == "mape":
            y_pred = self.predict(X)
            return mean_absolute_percentage_error(y, y_pred)
        elif scoring == "mse": 
            y_pred = self.predict(X)
            return mean_squared_error(y, y_pred)
        else: 
            return NotImplementedError