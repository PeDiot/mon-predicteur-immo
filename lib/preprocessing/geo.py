"""Description. Methods for geographical data."""

from pandas.core.frame import DataFrame
from typing import Dict

from lib.enums import (
    CITIES, 
    URBAN_AREAS, 
    RURAL_AREAS
)

def split_by_city(df: DataFrame) -> Dict:
    """Description. Split dataframe per 10 biggest french cities."""

    if "nom_commune" not in df.columns: 
        raise ValueError("'nom_commune' not in columns.")
    if "degre_densite" not in df.columns: 
        raise ValueError("'degre_densite' not in columns.")

    dict_cities = {}

    for city in  CITIES: 
        if city in ("Paris", "Marseille", "Lyon"): 
            tmp = df.loc[df.degre_densite==city, :]
        else: 
            tmp = df.loc[df.nom_commune==city, :]

        dict_cities[city] = tmp 
    
    return dict_cities

def get_urban_areas(df: DataFrame) -> DataFrame: 
    """Description. Return transactions for urban areas which are not in big cities."""

    if "degre_densite" not in df.columns: 
        raise ValueError("'degre_densite' not in columns.")
    
    df_urban = df.loc[
        (df.degre_densite.isin(URBAN_AREAS)) &
        (~df.nom_commune.isin(CITIES)), 
        :
    ]

    return df_urban

def get_rural_areas(df: DataFrame) -> DataFrame: 
    """Description. Return transactions for rural areas."""

    if "degre_densite" not in df.columns: 
        raise ValueError("'degre_densite' not in columns.")
    
    df_rural = df.loc[df.degre_densite.isin(RURAL_AREAS), :]

    return df_rural