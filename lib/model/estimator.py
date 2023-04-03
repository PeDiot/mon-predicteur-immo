import numpy as np 

from sklearn.base import BaseEstimator
from sklearn.linear_model import LinearRegression

from sklearn.metrics import (
    mean_absolute_error, 
    mean_absolute_percentage_error, 
    mean_squared_error
) 


from torch import Tensor
import torch.nn as nn

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

import torch.nn as nn
import torch.nn.functional as F

from typing import List

class MLP(nn.Module):
    """Description: A simple multi-layer perceptron (MLP) with a variable number of hidden layers.
    
    Args:
        input_size (int): The number of features in the input.
        output_size (int): The number of features in the output.
        hidden_sizes (List): A list of integers representing the number of nodes in each hidden layer.
        activation_funcs (List): A list of activation functions to be applied to the output of each hidden layer.
        """

    def __init__(
        self, 
        input_size: int, 
        output_size: int, 
        hidden_sizes: List, 
        activation_funcs: List, 
        dropout_probs: List
    ):
        super(MLP, self).__init__()
        
        # Define the input and output layers
        self.input_layer = nn.Linear(input_size, hidden_sizes[0])
        self.output_layer = nn.Linear(hidden_sizes[-1], output_size)

         # Define the dropout layers
        self.dropout_layers = nn.ModuleList()
        for i in range(len(hidden_sizes)-1):
            p = dropout_probs[i]
            self.dropout_layers.append(nn.Dropout(p=p))
        
        # Define the hidden layers and activation functions
        self.hidden_layers = nn.ModuleList()
        for i in range(len(hidden_sizes)-1):
            self.hidden_layers.append(nn.Linear(hidden_sizes[i], hidden_sizes[i+1]))
        self.activation_funcs = activation_funcs
        
    def forward(self, x):
        # Pass the input through the input layer and the first activation function
        x = self.activation_funcs[0](self.input_layer(x))
        
        # Pass the input through each hidden layer and activation function
        for i in range(len(self.hidden_layers)):
            x = self.activation_funcs[i+1](self.hidden_layers[i](x))
            
        # Pass the input through the output layer
        x = self.output_layer(x)
        return x