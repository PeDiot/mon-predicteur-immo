import sqlalchemy
from optuna import Trial, create_study
from optuna.pruners import BasePruner
from optuna.study.study import Study

import numpy as np 
from .estimator import CustomRegressor
from sklearn.metrics import mean_absolute_percentage_error

from typing import Dict

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

def optuna_objective(
    trial: Trial,
    regressor: CustomRegressor, 
    X_tr: np.ndarray, 
    y_tr: np.ndarray, 
    X_te: np.ndarray, 
    y_te: np.ndarray
) -> float:
    """Description.
    Objective function to optimize hyperparams of CustomRegressor model using optuna.

    Args:
        trial (Trial): optuna trial
        X_tr (np.ndarray): training features
        y_tr (np.ndarray): training target
        X_te (np.ndarray): test features
        y_te (np.ndarray): test target

    Returns: MAPE between predicted prices and real prices on test set.
    
    Details: target variable is the logarithm of the price (l_valeur_fonciere)."""

    params = generate_param_grid(trial, regressor)

    regressor.estimator.set_params(**params)
    regressor.fit(X_tr, y_tr)

    y_pred = regressor.predict(X_te)

    prices = np.exp(y_te)
    pred_prices = np.exp(y_pred)

    mape = mean_absolute_percentage_error(prices, pred_prices)

    return mape

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