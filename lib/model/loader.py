from typing import List, Dict
import pickle as pkl

from .estimator import CustomRegressor

def save_model(
    model: CustomRegressor, 
    feature_names: List[str],
    version: int, 
    geo_area: str, 
    property_type: str
) -> None:
    """Description. 
    Save CustomRegressor model and names of features used to train model.
    
    Args:
        model (CustomRegressor): model to save.
        feature_names (List[str]): list of feature names.
        version (int): model version.
        geo_area (str): geo area on which model was trained.
        property_type (str): property type for which model was trained."""

    estimator = model.estimator.__class__.__name__
    file_name = f"{estimator}-{geo_area}-{property_type}-v{version}.pkl".lower()
    file_path = f"{BACKUP_DIR}models/{file_name}"

    to_save = {
        "model": model,
        "feature_names": feature_names
    }

    with open(file_path, "wb") as f: 
        pkl.dump(to_save, f)

    print(f"{estimator} and feature names saved at {file_path}")

def load_model(
    estimator_name: str, 
    version: int, 
    geo_area: str, 
    property_type: str
) -> Dict:
    """Description. Load CustomRegressor model and names of features used to train model.
    
    Args:
        estimator_name (str): name of estimator passed as argument of CustomRegressor model.
        version (int): model version.
        geo_area (str): geo area on which model was trained.
        property_type (str): property type for which model was trained.
        
    Returns:
        Dict: loaded model and feature names."""

    file_name = f"{estimator_name}-{geo_area}-{property_type}-v{version}.pkl".lower()
    file_path = f"{BACKUP_DIR}models/{file_name}"

    with open(file_path, "rb") as f: 
        to_load = pkl.load(f)

    return to_load