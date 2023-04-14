import numpy as np
import pandas as pd 

import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.axes import Axes
from seaborn.palettes import _ColorPalette

from sklearn.metrics import (
    mean_absolute_error, 
    mean_absolute_percentage_error, 
    mean_squared_error, 
    r2_score
) 

import torch 
from torch import Tensor

from rich.table import Table
from rich.console import Console

from typing import (
    List, 
    Dict, 
    Optional, 
    Union
)

from .estimator import CustomRegressor, MLP
from .optimize import median_absolute_percentage_error

def compute_metrics(
    model: CustomRegressor, 
    X: np.ndarray, 
    y: np.ndarray, 
    to_prices: bool=True
) -> Dict:
    """Description: Compute MSE, MAE, MAPE and R² for train and test sets."""

    y_pred = model.predict(X)

    if to_prices:
        y_pred = np.exp(y_pred)
        y = np.exp(y)
    
    results = {}

    for metric in (
        mean_absolute_error, 
        mean_absolute_percentage_error, 
        median_absolute_percentage_error,
        mean_squared_error, 
        r2_score
    ): 
        metric_name = metric.__name__
        results[metric_name] = metric(y, y_pred)
    
    return results

def make_regression_report(metrics: Dict, title: Optional[str]=None) -> Table: 
    """Description. Make a rich table with the results of the regression models."""

    if title is None:
        title = "Regression report" 

    table = Table(title=title)

    table.add_column("Model", width=30)

    for col in ("MAE", "% MAPE", "%MDAPE", "MSE", "% R²"):
        table.add_column(col, width=15)

    for model, records in metrics.items(): 

        mae = round(records["mean_absolute_error"], 2)
        mape = round(100*records["mean_absolute_percentage_error"], 2)
        mdape = round(100*records["median_absolute_percentage_error"], 2)
        mse = round(records["mean_squared_error"], 2)
        r2 = round(100*records["r2_score"], 2)

        table.add_row(
            model, 
            str(mae),
            str(mape),
            str(mdape), 
            f"{mse:,.2e}",
            str(r2)
        )

    return table

def display_regression_report(results: Dict, title: Optional[str]=None) -> None:
    """Description. Display metrics of regression models in the console.
    
    Args:
        metrics (Dict): A dictionary with the metrics of each model.
        title (Optional[str], optional): The title of the table. Defaults to None.
        
    Returns:
        Table: A rich table with the results of the regression models.
        
    Example:
    >>> results = {
    ...     "model_1": {
    ...         "mean_absolute_error": 0.1,
    ...         "mean_absolute_percentage_error": 0.2,
    ...         "mean_squared_error": 0.3,
    ...         "r2_score": 0.4
    ...     },
    ...     "model_2": {
    ...         "mean_absolute_error": 0.5,
    ...         "mean_absolute_percentage_error": 0.6,
    ...         "mean_squared_error": 0.7,
    ...         "r2_score": 0.8
    ...     }
    ... }
    >>> make_regression_report(results)
    +-----------+---------------+---------------+---------------+---------------+
    |   Model   |      MAE      |     % MAPE    |      MSE      |      % R²     |
    +-----------+---------------+---------------+---------------+---------------+
    | model_1   | 0.1           | 20.0          | 3.00e-01      | 40.0          |
    | model_2   | 0.5           | 60.0          | 7.00e-01      | 80.0          |
    +-----------+---------------+---------------+---------------+---------------+
    """

    table = make_regression_report(results, title=title)
    console = Console()
    console.print(table)

def get_predictions(
    estimator: CustomRegressor, 
    X: np.ndarray, 
    y: np.ndarray, 
    target_var: str="l_valeur_fonciere"
) -> Dict: 
    """Description. Get predictions and true values for a given estimator and dataset.
        
    Args:
        estimator (CustomRegressor): The estimator to use.
        X (np.ndarray): The feature matrix.
        y (np.ndarray): The target vector
        target_var (str, optional): The target variable. Defaults to "l_valeur_fonciere".
        
    Returns:
        Dict: A dictionary containing the true and predicted values."""

    y_pred = estimator.predict(X)

    if target_var == "l_valeur_fonciere":
        results = {
            "l_valeur_fonciere": {
                "y_true": y,
                "y_pred": y_pred
            }, 
            "valeur_fonciere": {
                "y_true": np.exp(y),
                "y_pred": np.exp(y_pred)
            }
        }

    elif target_var == "valeur_fonciere":
        results = {
            "valeur_fonciere": {
                "y_true": y,
                "y_pred": y_pred
            }
        }

    else: 
        raise ValueError("Target variable must be either 'l_valeur_fonciere' or 'valeur_fonciere'.")
    
    return results 

def predict_mlp(model: MLP, X: Tensor, device: torch.device, to_prices: bool=True) -> np.ndarray:
    """Predicts the target values using a trained MLP.
    
    Args:
        model: the MLP model
        dataloader: the dataloader for the dataset
        device: the device on which the model is located
        to_prices: if True, the predicted values are exponentiated
        
    Returns:
        A numpy array containing the predicted values.
    """
    model.eval()

    with torch.no_grad():
        X = X.to(device)
        y_pred = model(X).cpu().numpy().reshape(-1)
        if to_prices:
            y_pred = np.exp(y_pred)

    return y_pred

def absolute_percentage_error(true: float, pred: float, return_pct: bool=True) -> float: 
    """Description. Compute the absolute percentage error."""
    ape = np.abs((true - pred) / pred) 

    if return_pct:  
        ape = 100 * ape 

    return ape

def plot_predictions(
    y_true: np.ndarray, 
    y_pred: np.ndarray, 
    add_line: bool=True,
    title: Optional[str]=None, 
    ax: Optional[Axes]=None
):
    """Description. Plot observed vs actual values.
    
    Args:
        y_true (np.ndarray): The true values.
        y_pred (np.ndarray): The predicted values.
        add_line (bool, optional): Whether to add a line y=x. Defaults to True.
        title (Optional[str], optional): The title of the plot. Defaults to None.
        ax (Optional[Axes], optional): The axes to plot on. Defaults to None."""

    if ax is None:  
        fig, ax = plt.subplots(figsize=(10, 5))

    mape = 100*mean_absolute_percentage_error(y_true, y_pred)
    
    tmp = pd.DataFrame(data={"obs": y_true, "pred": y_pred})
    tmp["ape"] = tmp.apply(lambda row: absolute_percentage_error(row.obs, row.pred), axis=1)

    min_x, max_x = tmp.obs.min(), tmp.obs.max()

    sns.scatterplot(
        x="obs", 
        y="pred", 
        data=tmp, 
        hue="ape", 
        palette="Reds", 
        ax=ax
    )

    if add_line:
        sns.lineplot(
            x=[min_x, max_x], 
            y=[min_x, max_x], 
            color="black", 
            linestyle="dotted", 
            ax=ax)

    ax.legend(loc="best", title="Absolute error (%)")

    if title is not None:
        ax.set_title(f"{title} - MAPE: {mape:.2f}%") 