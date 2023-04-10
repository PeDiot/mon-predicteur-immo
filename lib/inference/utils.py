from lib.enums import (
    AVAILABLE_DEPARTMENTS,
    DVF_LOCATION_VARS, 
    BNB_SELECTED_VARS, 
    OTHER_VARS
)

from lib.dataset.utils import (
    extract_int_from_string, 
    is_dummy, 
    get_most_frequent_levels    
)

from lib.model.estimator import CustomRegressor

from typing import (
    Tuple, 
    List, 
    Dict, 
    Optional, 
    Union,
)

from pandas.core.frame import DataFrame
from pandas.core.series import Series

import pandas as pd 
import numpy as np
from datetime import datetime

from googlemaps.client import Client
from geopy.distance import geodesic

TODAY = datetime.today().strftime("%Y-%m-%d")

def extract_department_code(zip_code: int) -> int: 
    """Description. Extract department code from zip code."""

    zip_code_str = str(zip_code)
    
    if len(zip_code_str) == 4:
        dpt_code = int(zip_code_str[0])
    else:
        dpt_code = int(zip_code_str[:2])
        
    return dpt_code 

def find_department(zip_code: int) -> str: 
    """Description. Find department from zip code."""
    
    dpt_code = extract_department_code(zip_code)

    if dpt_code in AVAILABLE_DEPARTMENTS.keys(): 
        return AVAILABLE_DEPARTMENTS[dpt_code]
    
    return None

def get_user_location(gmaps: Client, user_args: dict) -> Tuple: 
    """Description. Return longitude and latitude of user address.
    
    Args:
        gmaps (Client): Google Maps client.
        user_args (dict): User arguments.
        
    Returns:
        Tuple: Longitude and latitude."""

    address = f"{user_args['street_number']} {user_args['street_name']} {user_args['zip_code']} {user_args['city']}"

    geocode_result = gmaps.geocode(address)
    geocode = geocode_result[0]["geometry"]["location"]

    lng, lat = geocode["lng"], geocode["lat"]

    return lng, lat

def get_movav_windows(feature_names: List) -> List:
    """Description. Get moving average windows from the names of features used in model."""
    
    mov_av_windows = [
        int(extract_int_from_string(feature))            
        for feature in feature_names
        if feature.startswith("l_valeur_fonciere_ma") 
    ]
    
    return mov_av_windows

def get_interval(df: DataFrame, var_name: str, quantiles: Tuple=(.05, .99)) -> Tuple: 

    lower, upper = quantiles
    if lower > upper: 
        raise ValueError("Lower bound must be lower than upper bound.")
    
    interval = tuple(df[var_name].quantile([lower, upper]).values) 
    return interval

def get_numeric_filters(df: DataFrame, user_args: Dict) -> Dict: 
    """Description. Get numeric filters for data preprocessing from user arguments.
    
    Args:
        df (DataFrame): Dataframe to filter. 
        user_args (Dict): User arguments.
        
    Returns:
        Dict: Numeric filters to apply on df"""

    filters = {}

    for var in ("nombre_pieces_principales", "surface_reelle_bati", "valeur_fonciere"):
        filters[var] = get_interval(df, var)

    if user_args["property_type"] == "houses": 
        filters["surface_terrain"] = get_interval(df, "surface_terrain")

    return filters

def select_features(df: DataFrame, model_loader: Dict) -> DataFrame:
    """Description. Select features used in model and useful features.
    
    Args:
        df (DataFrame): Dataframe to select features from.
        model_loader (Dict): Model loader with feature names.
        
    Returns:
        DataFrame: Dataframe with selected features."""
    
    to_select = ["id_mutation", "date_mutation", "valeur_fonciere", "type_local"]
    to_select.extend(DVF_LOCATION_VARS)
    to_select.extend(model_loader["feature_names"])

    to_select = [var for var in to_select if var in df.columns]
    
    return df.loc[:, to_select]

def fetch_last_trend_prices(df: DataFrame, trend_price_vars: List[str]) -> Dict: 
    """Description. Return last trend prices from dataframe using moving averages."""
    
    result = df[trend_price_vars].iloc[-1]
    return dict(result)


def return_close_properties(df: DataFrame, user_args: Dict) -> Optional[Union[Series, DataFrame]]:
    """Description. Return properties (flats or houses) close to user's property.
    
    Args:
        df (DataFrame): Dataframe with all properties.
        user_args (Dict): features of user's property.
        
    Returns:
        Optional[Union[Series, DataFrame]]: close properties or None if no properties found."""

    mask_street_name = (
        df.adresse_nom_voie.str.lower().replace(",", "") == 
        user_args["street_name"].lower().replace(",", "")
    )
    mask = (
        (df.adresse_numero == user_args["street_number"]) &
        mask_street_name &
        (df.code_postal == user_args["zip_code"])
    )
    result = df[mask]

    if len(result) == 0: 
        mask = (
            mask_street_name &
            (df.code_postal == user_args["zip_code"])
        )
        result = df[mask]

        if len(result) == 0: 
            mask = (df.code_postal == user_args["zip_code"])
            result = df[mask]

            if len(result) == 0:
                return None

    return result

def calc_distance(x1: Tuple, x2: Tuple, unit: str="m") -> float: 
    """Description. Calculate distance between two points.
    
    Args:
        x1 (Tuple): Coordinates of first point.
        x2 (Tuple): Coordinates of second point.
        unit (str, optional): Unit of distance. Defaults to "m".
        
    Returns:
        float: Distance between x1 and x2."""

    d = geodesic(x1, x2)
    
    if unit == "m":
        return d.m

    return d

def get_row_with_less_na(df: DataFrame) -> Series:
    """Description. Return row with less missing values."""

    return df.loc[df.isna().sum(axis=1) == df.isna().sum(axis=1).min(), :]

def find_closest(df: DataFrame, user_args: Dict) -> Series:
    """Description. Find closest property from user's property.
    
    Args:
        df (DataFrame): Dataframe with all properties.
        user_args (Dict): features of user's property.
        
    Returns:
        Series: Closest property."""

    user_coords = (user_args["latitude"], user_args["longitude"])

    df["distance"] = df.apply(lambda row: calc_distance(user_coords, (row.latitude, row.longitude)), axis=1) 
    closest = df.loc[df.distance == df.distance.min(), :]

    if isinstance(closest, DataFrame): 
        closest = get_row_with_less_na(closest)
        
    return closest.iloc[0, :]

def remove_l_prefix(string: str) -> str:
    """Description. Remove 'l_' prefix from string."""

    if string.startswith("l_"):
        string = string[2:]

    return string

def get_imputed_values(df: DataFrame, model_loader: Dict) -> DataFrame:
    """Description. Get imputed values for missing values in dataframe.
    
    Args:
        df (DataFrame): Dataframe to impute.
        model_loader (Dict): Model loader with feature names to impute.
        
    Returns:
        DataFrame: Dataframe with imputed values.
        
    Details:
        - If variable is a dummy variable, impute with most frequent level.
        - If variable is a continuous variable, impute with median."""
    
    to_impute = []

    for var in model_loader["feature_names"]:
        
        if not var.startswith("l_"):
            to_impute.append(var)
        elif var.startswith("l_") and remove_l_prefix(var) in BNB_SELECTED_VARS + OTHER_VARS:
            to_impute.append(var)
       
    imputed_values = {}
    
    for var in to_impute:
        x = df[var]

        if is_dummy(x):
            val = get_most_frequent_levels(df, [var])[var]

        else: 
            val = x.median()

        imputed_values[var] = val

    return imputed_values

def check_num_rooms(num_rooms: int, var: str) -> float: 
    """Description. Return 1 if number of rooms is in variable name, 0 otherwise."""

    if str(num_rooms) in var:
        return 1.
    else: 
        return 0.
    
def get_quarter(date: str) -> str:
    """Description. Return quarter from date."""
    
    date = pd.to_datetime(date)
    quarter = (date.month - 1) // 3 + 1 
    return str(quarter)

def get_month(date: str) -> str:
    """Description. Return month from date."""
    
    date = pd.to_datetime(date)
    return str(date.month)

def prepare_feature_vector(
    df: DataFrame, 
    model_loader: Dict, 
    user_args: Dict, 
    last_trend_prices: Optional[Dict]=None, 
    closest: Optional[Series]=None 
) -> Tuple: 
    """Description. Prepare feature vector for prediction.
    
    Args:
        df (DataFrame): Dataframe used for data imputation. 
        model_loader (Dict): Model loader with feature names used for prediction.
        user_args (Dict): Features of user's property.
        last_trend_prices (Dict): Last trend prices.
        closest (Optional[Series], optional): Closest property to user's. Defaults to None.
        
    Returns:
        Tuple: Feature vector and selected features."""
    
    selected_features = model_loader["feature_names"]
    X = pd.Series(index=selected_features, dtype="float64")

    if closest is None or closest.distance > 0:
        imputed_values = get_imputed_values(df, model_loader) 
    else: 
        imputed_values = closest 

    for var in selected_features: 

        if var not in closest.index:
            X[var] = 0

        elif "nombre_pieces_principales" in var:
                X[var] = check_num_rooms(user_args["num_rooms"], var)

        elif var == "surface_reelle_bati":
            X[var] = user_args["surface"]

        elif var == "l_surface_reelle_bati":
            X[var] = np.log(user_args["surface"])

        elif var == "surface_terrain":
            X[var] = user_args["field_surface"]

        elif var == "l_surface_terrain":
            X[var] = np.log(user_args["field_surface"])

        elif var == "dependance": 
            X[var] = user_args["dependance"]

        elif last_trend_prices is not None and var in last_trend_prices.keys():
            X[var] = last_trend_prices[var]

        elif "trimestre" in var:
            quarter = get_quarter(TODAY)
            X[var] = 1 if quarter in var else 0

        elif "mois" in var:
            month = get_month(TODAY)
            X[var] = 1 if month in var else 0

        else: 
            X[var] = imputed_values[var]

    features, X = X.index.tolist(), X.values.reshape(1, -1)

    return features, X

def get_predicted_price(model: CustomRegressor, X: np.ndarray) -> float: 
    """Description. Predict real estate's price from model.
    
    Args:
        - model (CustomRegressor): Model used for prediction.
        - X (np.ndarray): Feature vector.
        
    Returns:
        float: Predicted price."""

    y_pred = model.predict(X)
    price_pred = np.round(np.exp(y_pred)[0]) 
    return price_pred