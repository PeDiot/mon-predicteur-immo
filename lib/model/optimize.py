import sqlalchemy
from optuna import Trial
from optuna.pruners import BasePruner
from optuna.study.study import Study

import numpy as np 
from tqdm import tqdm

from .estimator import CustomRegressor
from sklearn.metrics import mean_absolute_percentage_error

from torch.utils.data import DataLoader
import torch 
from torch.optim.lr_scheduler import ExponentialLR

from typing import Dict, Tuple, Optional

from .estimator import MLP

def generate_param_grid(trial: Trial, regressor: CustomRegressor) -> Dict: 
    """Description. Generate parameter grid for CustomRegressor model.
    
    Args:
        trial (Trial): optuna trial
        regressor (CustomRegressor): CustomRegressor model
        
    Returns:
        Dict: parameter grid for CustomRegressor model."""
    
    estimator_name = regressor.estimator.__class__.__name__
    
    if estimator_name == "XGBRegressor": 
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "learning_rate": trial.suggest_loguniform("learning_rate", 1e-3, 1e-1),
            "subsample": trial.suggest_loguniform("subsample", 0.5, 1.0),
            "reg_alpha": trial.suggest_loguniform("reg_alpha", 1e-3, 1e3),
            "reg_lambda": trial.suggest_loguniform("reg_lambda", 1e-3, 1e3),
            "random_state": 42
        }

    elif estimator_name == "RandomForestRegressor": 
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
            "random_state": 42, 
            "oob_score": True
        }
    
    else: 
        raise NotImplementedError(f"{estimator_name} not implemented.")

    return params 

def median_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Description. Compute the median absolute percentage error (MAPE) between y_true and y_pred.
    
    Args:
        y_true (np.ndarray): true values
        y_pred (np.ndarray): predicted values
        
    Returns:
        float: median absolute percentage error (MAPE) between y_true and y_pred."""
    
    mdape = np.median(np.abs((y_true - y_pred) / y_true))
    return mdape

def optuna_objective(
    trial: Trial,
    regressor: CustomRegressor, 
    X_tr: np.ndarray, 
    y_tr: np.ndarray, 
    X_te: np.ndarray, 
    y_te: np.ndarray,
    metric: str="mdape", 
    to_prices: bool = True
) -> float:
    """Description.
    Objective function to optimize hyperparams of CustomRegressor model using optuna.

    Args:
        trial (Trial): optuna trial
        X_tr (np.ndarray): training features
        y_tr (np.ndarray): training target
        X_te (np.ndarray): test features
        y_te (np.ndarray): test target
        metric (str): metric to optimize (default: "mdape")
        to_prices (bool): convert target to prices (default: True)

    Returns:
        float: median absolute percentage error between true and predicted values 
            ('valeur_fonciere' or 'l_valeur_fonciere') depending on to_prices."""

    if metric not in ["mdape", "mape"]:
        raise ValueError(f"metric must be 'mdape' or 'mape', got {metric}.")

    elif metric == "mape":
        metric_fun = mean_absolute_percentage_error
    
    else: 
        metric_fun = median_absolute_percentage_error


    params = generate_param_grid(trial, regressor)

    regressor.estimator.set_params(**params)
    regressor.fit(X_tr, y_tr)

    y_pred = regressor.predict(X_te)

    if to_prices:
        y_te = np.exp(y_te)
        y_pred = np.exp(y_pred)

    result = metric_fun(y_te, y_pred)
    return result

class OptimPruner(BasePruner):
    """Description. Stop optuna optimisation process if no improvement after n trials.
    
    Args:
        n_warmup_trials (int): number of trials to warm up the process
        n_trials_to_prune (int): number of trials to stop the process if no improvement"""

    def __init__(self, n_warmup_trials: int, n_trials_to_prune: int):
        self.n_warmup_trials = n_warmup_trials
        self.n_trials_to_prune = n_trials_to_prune

    def __repr__(self) -> str:
        return f"OptimPruner(n_warmup_trials={self.n_warmup_trials}, n_trials_to_prune={self.n_trials_to_prune})"

    def prune(self, study: Study, trial: Trial) -> bool:
        """Description. Stop optuna optimisation process if no improvement after n trials.
        
        Args:
            study (Study): optuna study with history of all trials
            trial (Trial): optuna trial."""
        
        if study.best_trial.number > trial.number - self.n_trials_to_prune:
            return False

        if trial.number < self.n_warmup_trials:
            return False

        best_value = study.best_trial.intermediate_values.get("mape")
        if best_value is None:
            return False

        value = trial.intermediate_values.get("mape")
        if value is None:
            return False

        return value >= best_value

def optimize_mlp(
    model: MLP, 
    train_loader: DataLoader, 
    val_loader: DataLoader, 
    optimizer, 
    criterion, 
    n_epochs: int, 
    device: torch.device, 
    loss_threshold: float = 1e-4, 
    n_warmup_epochs: int=10, 
    lr_scheduler: Optional[ExponentialLR] = None
) -> Tuple:
    """Description. Training/validation loop for a pytorch model.
    
    Args:
        model (MLP): pytorch model
        train_loader (DataLoader): training data loader
        val_loader (DataLoader): validation data loader
        optimizer (torch.optim): optimizer
        criterion (torch.nn): loss function
        n_epochs (int): number of epochs
        device (torch.device): device to use for training
        loss_threshold (float, optional): threshold to stop training (default: 1e-4)
        lr_scheduler (Optional[ExponentialLR], optional): learning rate scheduler (default: None)

    Returns:
        Tuple: train MSE losses, validation MSE losses"""

    train_losses, val_losses = [], []
    model.to(device)
    loop = tqdm(range(n_epochs), leave=True)

    for epoch in loop:
        train_loss = 0.0
        val_loss = 0.0

        # train
        model.train()
        for X, y in train_loader:
            X, y = X.to(device), y.to(device)

            optimizer.zero_grad()
            y_pred = model(X).reshape(-1)

            loss = criterion(y_pred, y)
            loss.backward()

            optimizer.step()

            train_loss += loss.item() * X.size(0)

        if lr_scheduler is not None:
            lr_scheduler.step()

        train_loss = train_loss / len(train_loader.dataset)

        # validate
        with torch.no_grad():
            model.eval()

            for X, y in val_loader:
                X, y = X.to(device), y.to(device)

                y_pred = model(X).reshape(-1)
                loss = criterion(y_pred, y)

                val_loss += loss.item() * X.size(0)

        val_loss = val_loss / len(val_loader.dataset)


        if epoch > n_warmup_epochs and np.abs(val_loss - val_losses[-1]) < loss_threshold:
            break

        train_losses.append(train_loss)
        val_losses.append(val_loss)

        msg = f"Epoch: {epoch + 1}/{n_epochs} \tTraining Loss: {train_loss:.6f} \tValidation Loss: {val_loss:.6f}"

        if lr_scheduler is not None:
            last_lr = lr_scheduler.get_last_lr()[0]
            msg += f"\tLearning Rate: {last_lr:.6f}"
        
        loop.set_description(msg) 

    return train_losses, val_losses