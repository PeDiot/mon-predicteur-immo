"""Description. Data preprocessing methods for 'Demandes de Valeurs Foncières' dataset."""

import pandas as pd 
from tqdm import tqdm

from zipfile import ZipFile
import pickle as pkl

from pandas.core.frame import DataFrame 
from typing import Dict

from lib.enums import CITIES, YEARS, URBAN_AREAS,RURAL_AREAS

def load_zip_csv(zip_dir: str, year: int, chunk_size: int=10000) -> DataFrame: 
    """Description. Load zip DVF dataset in chunks."""

    if zip_dir.split(".")[-1] != "zip": 
        raise ValueError("Extension of zip_dir must be .zip.")
    
    zip_folder = ZipFile(zip_dir)
    file_name = f"dvf/{year}.csv"

    chunks = pd.read_csv(zip_folder.open(file_name), chunksize=chunk_size)
    df = pd.concat(chunks)

    return df 

def load_zip_pkl(zip_dir: str, year: int) -> Dict: 
    """Description. Load serialized (Dict) object from zip folder."""

    if zip_dir.split(".")[-1] != "zip": 
        raise ValueError("Extension of zip_dir must be .zip.")
    
    zip_folder = ZipFile(zip_dir)
    file_name = f"cleaned/dvf_splitted_{year}.pkl"

    d = pkl.load(zip_folder.open(file_name))
    return d 

def select_sales(df: DataFrame) -> DataFrame: 
    """Description. 
    Select entries related to sales such that nature_mutation='Vente'."""

    if "nature_mutation" not in df.columns: 
        raise ValueError("'nature_mutation' not in columns.")
    
    return df.loc[df.nature_mutation == "Vente", :] 


property_type_mapping = {
    1: "Maison", 
    2: "Appartement", 
    3: "Dépendance", 
    4: "Local industriel. commercial ou assimilé"
}

def encode_property_type(code: float) -> str:
    """Description. Map code_type_local to type_local."""
    
    if not pd.isna(code): 
      property_type = property_type_mapping[code] 
      return property_type
  
    return code

def remove_industrial_facilities(df: DataFrame) -> DataFrame: 
    """Description. Select entries which are not industrial facilities."""
    
    if "code_type_local" not in df.columns: 
        raise ValueError("'code_type_local' not in columns.")
    
    return df.loc[
        (df.code_type_local >= 1) & 
        (df.code_type_local < 4), 
        :
    ] 

def add_dependency_dummy(df: DataFrame, dependency_df: DataFrame) -> DataFrame: 
    """Description. Add dummy variable indicating whether property has dependency."""

    if "id_mutation" not in df.columns or "id_mutation" not in dependency_df.columns: 
        raise ValueError("'id_mutation' must be in columns of df and dependency_df.")

    dependencies_count = dependency_df\
        .loc[dependency_df.id_mutation.isin(df.id_mutation), :]\
        .groupby("id_mutation")\
        .size()
    
    df.loc[:, "dependance"] = 0
    df.loc[
        df.id_mutation.isin(dependencies_count.index), 
        "dependance"
    ] = 1

    return df 

def concat_datasets_per_year(zip_dir: str, geo_area: str , property_type: str) -> DataFrame: 
    """Description. Concatenate datasets for given geographical area over years."""

    dfs_list = []
    loop = tqdm(YEARS)

    for year in loop:
        loop.set_description(f"Processing {year}")
        tmp = load_zip_pkl(zip_dir, year)

        if geo_area in CITIES:
            tmp = tmp[property_type]["cities"][geo_area]
        else: 
            tmp = tmp[property_type][geo_area]

        dfs_list.append(tmp)

    df = pd.concat(dfs_list, axis=0).reset_index(drop=True)

    return df  

def concat_datasets(zip_dir: str, enums: str , property_type: str) -> DataFrame: 
    """Description. Concatenate datasets for a given area over years.

    enums : an element within CITIES, URBAN_AREAS, OR RURAL_AREAS
    """

    dfs_list = []
    loop = tqdm(YEARS)

    for year in loop:
        loop.set_description(f"Processing {year}")
        tmp = load_zip_pkl(zip_dir, year)

        if enums in CITIES:
            tmp = tmp[property_type]["cities"][enums]

        elif enums in URBAN_AREAS : 
            tmp = tmp[property_type][enums]
        
        elif enums in RURAL_AREAS:
            tmp = tmp[property_type][enums]
            
        dfs_list.append(tmp)

    df = pd.concat(dfs_list, axis=0).reset_index(drop=True)

    return df  
