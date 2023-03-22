import pickle 
import pandas as pd 
import os 
from pandas import DataFrame
import numpy as np
from typing import Optional
import re
from sklearn.linear_model import (
    LinearRegression, 
    Ridge, 
    Lasso, 
    ElasticNet) 

import statsmodels.api as sm

from lib.preprocessing import dvf

# changement du directory 
dir_path = os.getcwd()
os.listdir(dir_path)
os.chdir('C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge')
os.listdir()

# chargement des données 
zf = 'C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge/dvf_cleaned.zip'
df_flats = dvf.concat_datasets_per_year(zf, geo_area="Paris", property_type="flats")

# Début Preprocessing #  

## ID_mutation unique 
n_unique_ids = df_flats.id_mutation.unique().shape[0]
assert n_unique_ids == df_flats.shape[0]
print(f"{n_unique_ids} transactions uniques pour les appartements à Paris")

## Sélection des variables 
VARS = [
    "id_mutation", 
    "date_mutation", 
    "valeur_fonciere",
    "nom_commune",
    "longitude",
    "latitude", 
    "pop", 
    "annee", 
    "trimestre", 
    "mois", 
    "jour", 
    "dependance", 
    "surface_terrain", 
    "surface_reelle_bati", 
    "nombre_pieces_principales" 
]

df2 = df_flats.loc[:, df.columns.isin(VARS)]

## Correction nb de pièces & surface du bien
df2 = df2.loc[
    (df2.nombre_pieces_principales > 0) &
    (df2.nombre_pieces_principales <= 8),
    :
]

def encode_num_rooms(n: int) -> str: 
    """Description. Group properties with 6+ rooms into '6-8' category."""
    if n < 6: 
        return str(n)
    else: 
        return "6-8"

df2["nombre_pieces_principales"] = df2["nombre_pieces_principales"].apply(encode_num_rooms)

df2 = df2.loc[
    (df2.surface_reelle_bati >= 9) & 
    (df2.surface_reelle_bati <= 250), 
    :
]

def encode_field_area(area: float) -> float: 

    if pd.isna(area): 
        area = 0
    return area 

assert encode_field_area(float("nan")) == 0
assert encode_field_area(102.) == 102.
 
df2["surface_terrain"] = df2["surface_terrain"].apply(encode_field_area) 

## Valeur_foncière 
def transform_target_variable(price: float, log:bool, area: Optional[float]=None) -> float: 

    y = price

    if area != None: 
        y = y / area

    if log: 
        y = np.log(y)
    
    return y 

df2["valeur_fonciere_m2"] = df2.apply(lambda row: transform_target_variable(row.valeur_fonciere, False, row.surface_reelle_bati), axis=1) 
df2["l_valeur_fonciere_m2"] = df2.apply(lambda row: transform_target_variable(row.valeur_fonciere_m2, True), axis=1) 
df2["l_valeur_fonciere"] = df2.apply(lambda row: transform_target_variable(row.valeur_fonciere, True), axis=1) 

## arrondissement 
DIGIT = r"[0-9]+"
def extract_int_from_string(string: str) -> int: 
    integer = re.findall(DIGIT, string)

    if len(integer) > 1: 
        raise ValueError("Multiple integers found.")
    return integer[0]
df2["arrondissement"] = df2.nom_commune.apply(extract_int_from_string)

## trimestre_annee 
def get_quarter_year(quarter: int, year: int) -> str: 
    return f"{year}Q{quarter}"

df2["trimestre_annee"] = df2.apply(lambda row: get_quarter_year(row.trimestre, row.annee), axis=1)

## encodage type de variable 
CAT_VARS = [
    "nombre_pieces_principales", 
    "dependance", 
    "arrondissement", 
    "trimestre_annee" 
]

QUANT_VARS = [
    "valeur_fonciere", 
    "valeur_fonciere_m2", 
    "l_valeur_fonciere", 
    "l_valeur_fonciere_m2", 
    "surface_reelle_bati", 
]

ID_VARS = ["id_mutation", "date_mutation"]

df3 = df2.loc[:, ID_VARS+QUANT_VARS+CAT_VARS]
df3.loc[:, CAT_VARS] = df2.loc[:, CAT_VARS].astype(object)
df3.loc[:, QUANT_VARS] = df3.loc[:, QUANT_VARS].astype(float)

# Fin du Preprocessing #

# Etape 1 : split temporel
from datetime import datetime
df3.dtypes # datetime64[ns]

def split_temporelle(df: DataFrame, train_percentage: int) -> DataFrame :
    ''''
    description
    '''
    
    df_train = []
    df_test = []
    dates_train = []
    dates_test = []

    df.sort_values(by='date_mutation', ascending = True, inplace = True) 
    
    size = df.shape[0] 
    train_size = int(train_percentage*size)
    
    df_train  = df.iloc[0:train_size]
    df_test = df.iloc[train_size+1:size]
    
    # dates_train =  df_train['id_mutation','date_mutation']
    # dates_test = df_test['id_mutation','date_mutation']

    return df_train, df_test #, dates_train, dates_test

split_temporelle(df3, 0.8)
df_train.columns

# Etape 2 : création du bien de référence 
y_tr = df_train['l_valeur_fonciere']
x_tr = df_train[['trimestre_annee', 'arrondissement']]

x_tr2 = pd.get_dummies(data=x_tr, drop_first=False)

pd.set_option("display.max_columns", None)
x_tr2 = x_tr2.dropna()

model = LinearRegression()
model.fit(x_tr2, y_tr)

## sélection des var catégorielles de référence à faire 


