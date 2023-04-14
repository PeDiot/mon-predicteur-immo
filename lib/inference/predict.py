from lib.enums import (
    CITIES, 
    AVAILABLE_GEO_AREAS, 
    GOOGLE_API_KEY, 
) 

from lib.dataset.loader import load_dvfplus
from lib.model.loader import load_model

from lib.dataset.build import (
    add_distance_to_parks, 
    add_distance_to_transportation, 
    add_public_facilities, 
    prepare_dataset, 
    prepare_dummies
)

from lib.dataset.utils import (
    get_categorical_vars, 
    get_most_frequent_levels, 
)

from .utils import (
    find_department, 
    extract_department_code, 
    get_movav_windows, 
    get_numeric_filters, 
    select_features, 
    fetch_last_trend_prices, 
    get_user_location, 
    return_close_properties, 
    find_closest, 
    prepare_feature_vector,
    get_predicted_price, 
)

from typing import Dict 

import pandas as pd 
from tqdm import tqdm
import googlemaps

import warnings
warnings.filterwarnings("ignore")

def activate_gmaps() -> googlemaps.Client: 
    """Description. Activate connection to Google Maps API."""

    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
    return gmaps

class Prediction:
    """Description. Class to predict real estate prices based on user's attributes using trained model.
    
    Example:
    
    >>> from lib.inference import Prediction
    >>> user_args = {
    ...:     "property_type": "flats",
    ...:     "street_number": 11,
    ...:     "street_name": "Rue des Halles",
    ...:     "zip_code": 75001,
    ...:     "city" : "Paris",
    ...:     "num_rooms": 2,
    ...:     "surface": 30,
    ...:     "field_surface": 0,
    ...:     "dependance": 0
    ...: }
    >>> prediction = Prediction(user_args)
    >>> prediction
    >>> Prediction(user_args={'property_type': 'flats', 'street_number': 11, 'street_name': 'Rue des Halles', 'zip_code': 75001, 'city': 'Paris', 'num_rooms': 2, 'surface': 30, 'field_surface': 0, 'dependance': 0})
    >>> prediction.load_data(data_dir="./data/")
    >>> prediction.load_model(model_dir="./backup/models/")
    Succesfully loaded XGBRegressor, feature names and metrics from ./backup/models//xgbregressor-paris-flats-v0.pkl.
    >>> pred_price = prediction.predict()
    100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 4/4 [00:00<00:00,  5.91it/s] 
    >>> print(f"Predicted price: {pred_price:,}€" )
    Predicted price: 388,950.0€"""

    def __init__(self, user_args: Dict):
        self.user_args = user_args

        if user_args["city"] in CITIES: 
            self.geo_area = user_args["city"]

        else:
            dpt = find_department(user_args["zip_code"])

            if dpt in AVAILABLE_GEO_AREAS[user_args["property_type"]]:
                self.geo_area = dpt
            else: 
                self.geo_area = None 

        self._last_trend_prices = None
        self.close_properties = None
        self._closest_property = None

    def __repr__(self) -> str:
        return f"Prediction(user_args={self.user_args})"

    def load_data(self, data_dir: str): 
        """Description. Load data from DVF+ dataset based on user's attributes."""

        df = load_dvfplus(
            zip_dir=data_dir, 
            zip_name="dvf+", 
            geo_area=self.geo_area,
            property_type=self.user_args["property_type"]
        )

        # encode street number and zip code to correct format 
        df["code_postal"] = df.code_postal.astype("Int32")
        df["adresse_numero"] = df.adresse_numero.astype("Int32")

        # add external data 
        if self.geo_area == "Paris":

            transportation = pd.read_csv(f"{data_dir}other/transportation.csv")
            parks = pd.read_csv(f"{data_dir}other/parks.csv")
            facilities = pd.read_csv(f"{data_dir}other/facilities.csv") 

            df = add_distance_to_transportation(df, transportation)
            del transportation

            df = add_distance_to_parks(df, parks)
            del parks 

            df = add_public_facilities(df, facilities)
            del facilities

        department_code = extract_department_code(self.user_args["zip_code"])
    
        if department_code == 75:
            self.df = df.loc[df["code_postal"]==self.user_args["zip_code"], :]
        else: 
            self.df = df.loc[df["code_departement"]==department_code, :]

    def load_model(self, model_dir: str): 
        """Description. Load model from backup directory.
        
        Details: model contains CustomRegressor, feature names and metrics."""

        self.model_loader = load_model(
            path=model_dir, 
            estimator_name="XGBRegressor", 
            version=0, 
            property_type=self.user_args["property_type"],
            geo_area=self.geo_area
        )

    def __preprocess(self): 
        """Description. Apply preprocessing steps to loaded dataframe."""
    
        mov_av_windows = get_movav_windows(self.model_loader["feature_names"])

        if len(mov_av_windows) == 0:
            mov_av_windows = None

        preproc_args = {
            "target_var": "l_valeur_fonciere", 
            "numeric_filters": get_numeric_filters(self.df, self.user_args["property_type"]),  
            "na_threshold": 0.5,
            "ma_lag": 0, 
            "mov_av_windows": mov_av_windows, 
            "print_summary": False, 
            "return_var_names": False, 
            "keep_location_vars": True
        }

        df = prepare_dataset(self.df, **preproc_args)

        categorical_vars = get_categorical_vars(df, n_levels_max=30)   
        categorical_vars.append("baie_orientation") 
        dummy_ref_levels = get_most_frequent_levels(df, categorical_vars)
        df = prepare_dummies(df, categorical_vars, dummy_ref_levels, remove_cols_with_one_value=False)

        self.df = select_features(df, self.model_loader)

        trend_prices_vars = [var for var in self.df.columns if var.startswith("l_valeur_fonciere_ma")]

        if len(trend_prices_vars) > 0:
            self._last_trend_prices = fetch_last_trend_prices(self.df, trend_prices_vars)

    def __fetch_close_properties(self): 
        """Description. Fetch close properties based on user's location.
        
        Details: only if user's real estate is a flat."""

        gmaps = activate_gmaps() 
        lng, lat = get_user_location(gmaps, self.user_args)        

        self.user_args["longitude"] = lng
        self.user_args["latitude"] = lat

        self.close_properties = return_close_properties(self.df, self.user_args)

        if self.close_properties is not None:
            self._closest_property = find_closest(self.close_properties, self.user_args)

    def predict(self) -> float:
        """Description. Predict price based on user's attributes."""

        funs = [
            self.__preprocess, 
            self.__fetch_close_properties, 
            prepare_feature_vector, 
            get_predicted_price
        ]

        model = self.model_loader["model"]

        loop = tqdm(funs) 

        for i, fun in enumerate(loop):
            print(self.df.shape)

            if i == len(funs) - 2: 
                self._features, self._X = fun(
                    self.df, 
                    self.model_loader, 
                    self.user_args, 
                    self._last_trend_prices, 
                    self._closest_property)
                
            elif i == len(funs) - 1: 
                price_pred = get_predicted_price(model, self._X)
            else: 
                fun()
        
        return price_pred

    def fecth_mape(self) -> float:
        """Description. Fetch MAPE of the model."""

        estimator_name = self.model_loader["model"].estimator.__class__.__name__
        metrics = self.model_loader["metrics"]["all"]
        mape = metrics[estimator_name]["mean_absolute_percentage_error"]      

        return mape
        