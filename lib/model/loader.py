from typing import List, Dict
import pickle as pkl
import os

from .estimator import CustomRegressor

def save_model(
    path: str,
    model: CustomRegressor, 
    feature_names: List[str],
    metrics: Dict, 
    version: int, 
    geo_area: str, 
    property_type: str
) -> None:
    """Description. 
    Save CustomRegressor model and names of features used to train model.
    
    Args:
        path (str): path to directory where model will be saved.
        model (CustomRegressor): model to save.
        feature_names (List[str]): list of feature names.
        metrics (Dict): dictionary of metrics.
        version (int): model version.
        geo_area (str): geo area on which model was trained.
        property_type (str): property type for which model was trained."""

    estimator = model.estimator.__class__.__name__
    file_name = f"{estimator}-{geo_area}-{property_type}-v{version}.pkl".lower()
    file_path = f"{path}/{file_name}"

    to_save = {
        "model": model,
        "feature_names": feature_names, 
        "metrics": metrics, 
    }

    with open(file_path, "wb") as f: 
        pkl.dump(to_save, f)

    print(f"{estimator} and feature names saved at {file_path}")

def load_model(
    path: str,
    estimator_name: str, 
    version: int, 
    geo_area: str, 
    property_type: str
) -> Dict:
    """Description. Load CustomRegressor model and names of features used to train model.
    
    Args:
        path (str): path to directory where model is saved.
        estimator_name (str): name of estimator passed as argument of CustomRegressor model.
        version (int): model version.
        geo_area (str): geo area on which model was trained.
        property_type (str): property type for which model was trained.
        
    Returns:
        Dict: loaded model, feature names and metrics."""

    file_name = f"{estimator_name}-{geo_area}-{property_type}-v{version}.pkl".lower()
    file_path = f"{path}{file_name}"

    if not os.path.exists(file_path):
        to_load = None

    else:
        with open(file_path, "rb") as f: 
            to_load = pkl.load(f)

        print(f"Succesfully loaded {estimator_name}, feature names and metrics from {file_path}.")

    return to_load