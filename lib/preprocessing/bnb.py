"""Description. Data preprocessing methods for "Base Nationale des Batiments" dataset."""

import pandas as pd 
import numpy as np 

import ast
from tqdm import tqdm 
import os 

from pandas.core.frame import DataFrame
from typing import List, Tuple 

from lib.enums import (
    REL_BATIMENT_GROUPE_PARCELLE, 
    BATIMENT_GROUPE, 
    BATIMENT_GROUPE_ARGILES, 
    BATIMENT_GROUPE_BDTOPO_BAT, 
    BATIMENT_GROUPE_DPE, 
    BATIMENT_GROUPE_DPE_LOGTYPE, 
    BATIMENT_GROUPE_MERIMEE, 
    BATIMENT_GROUPE_QPV, 
    BATIMENT_GROUPE_RADON, 
    BATIMENT_GROUPE_RNC, 
    VARS_WITH_LIST_VALUES, 
    BNB_SELECTED_VARS, 
    BNB_PARCELLE_KEY, 
    DVF_PARCELLE_KEY, 
)

from .utils import remove_na_cols

VARS = {
    "rel_batiment_groupe_parcelle" : REL_BATIMENT_GROUPE_PARCELLE,
    "batiment_groupe": BATIMENT_GROUPE,
    "batiment_groupe_argiles": BATIMENT_GROUPE_ARGILES,
    "batiment_groupe_bdtopo_bat": BATIMENT_GROUPE_BDTOPO_BAT,
    "batiment_groupe_dpe": BATIMENT_GROUPE_DPE,
    "batiment_groupe_dpe_logtype": BATIMENT_GROUPE_DPE_LOGTYPE, 
    "batiment_groupe_merimee": BATIMENT_GROUPE_MERIMEE, 
    "batiment_groupe_qpv": BATIMENT_GROUPE_QPV, 
    "batiment_groupe_radon":  BATIMENT_GROUPE_RADON, 
    "batiment_groupe_rnc": BATIMENT_GROUPE_RNC
}

KEY = "batiment_groupe_id"

def object_to_string(df: pd.DataFrame) -> pd.DataFrame: 
    """Description. Convert object columns to string to avoid conversion error."""

    stringcols = df.select_dtypes(include="object").columns
    df[stringcols] = df[stringcols].fillna("").astype("string")

    return df 

def make_dataset(root: str, fnames: List[str], backup_fname: str): 
    """Description. 
    Build Base Nationale des Batiments dataset from selected file names.""" 

    if backup_fname.split(".")[-1] != "parquet": 
        raise ValueError("backup_fname must have .parquet extension.")

    backup_fpath = f"{root}{backup_fname}"
    existing = os.path.exists(backup_fpath)

    if existing: 
        print(f"Load {backup_fpath}...")
        df = pd.read_parquet(backup_fpath)

    loop = tqdm(fnames)
    for i, f in enumerate(loop): 

        if f not in list(VARS.keys()): 
            raise ValueError(f"{f} is not in {list(VARS.keys())}.")

        loop.set_description(f"Process {f}...")

        chunks = pd.read_csv(f"{root}{f}.csv", chunksize=10000)
        vars_ = VARS[f]

        if existing or i != 0:  
            tmp = pd.concat(chunks)[vars_]
            
            if f == "batiment_groupe_radon":
                tmp = tmp.rename(columns={"alea": "alea_radon"})

            df = pd.merge(left=df, right=tmp, how="left", on=KEY)

        else: 
            df = pd.concat(chunks)[vars_]

        df = object_to_string(df)

        print(f"Save updated {backup_fpath}...")
        df.to_parquet(backup_fpath, index=False) 

def load_bnb(data_dir: str, file_name: str) -> DataFrame: 

    file_path = data_dir + file_name
    df = pd.read_parquet(file_path)

    return df

def select_dvf_parcelle_ids(dvf: DataFrame) -> List:
    """Description. Select parcelle ids from DVF dataset."""

    idxs = dvf[DVF_PARCELLE_KEY].unique().tolist()
    return idxs 

def recode_enr(x: str) -> List: 
    x = x.replace(" + ", "+")
    items = x.split("+")

    return items

def string_tolist(s: str) -> List: 
    """Description. Convert string object to List."""

    try: 
        l = ast.literal_eval(s)
        if type(l) == list: 
            return l
        return 
    
    except: 
        return 

def check_list(s: str) -> bool: 
    """Description. Return True if a string contains a list."""

    s = string_tolist(s)
    if s != None: 
        return True
    
    return False 

def format_var_name(var: str) -> str: 
    return var.lower().replace(" ", "_")

def add_empty_dummies(df: DataFrame, var_name: str) -> DataFrame: 
    """Description. 
    Add as many columns as unique levels for variable with list as values."""

    if var_name not in list(VARS_WITH_LIST_VALUES.keys()):
        raise ValueError(f"{var_name} cannot be encoded.")

    to_add = VARS_WITH_LIST_VALUES[var_name]
    for var in to_add: 
        new_var_name = var_name + "_" + format_var_name(var)  
        df.loc[:, new_var_name] = np.nan 

    return df 

def fill_dummy_vars(df: DataFrame, var_name: str) -> DataFrame: 
    """Description. Fill dummies based on var_name values."""

    def _parse_list(x: List, item: str) -> int:
        if x != None:
            return 1 if item in x else 0
        return 0

    for level in VARS_WITH_LIST_VALUES[var_name]:  
        dummy = var_name + "_" + format_var_name(level)  
        df[dummy] = df[var_name].apply(_parse_list, item=level)

    return df 

def preprocess(df: DataFrame, parcelle_ids: List[str]) -> DataFrame:
    """Description. Preprocess Base Nationale des Batiments dataset.
    
    Args:
        df (DataFrame): Base Nationale des Batiments dataset.
        parcelle_ids (List[str]): List of parcelle ids from DVF dataset.
        
    Returns:
        DataFrame: Preprocessed Base Nationale des Batiments dataset."""
     
    bnb = df\
        .loc[df[BNB_PARCELLE_KEY].isin(parcelle_ids)]\
        .drop_duplicates(subset=BNB_PARCELLE_KEY)
    
    if "enr" not in list(bnb.columns):
        raise ValueError("enr column is missing.")
    
    bnb["enr"] = bnb.enr.apply(recode_enr) 

    for var in ["l_etat", "baie_orientation"]: 
        if var not in list(bnb.columns): 
            raise ValueError(f"{var} column is missing.")
        
        bnb[var] = bnb[var].apply(string_tolist)

    for var in list(VARS_WITH_LIST_VALUES.keys()): 
        bnb = add_empty_dummies(bnb, var)
        bnb = fill_dummy_vars(bnb, var)

    if "nom_quartier" not in list(bnb.columns): 
        raise ValueError("nom_quartier column is missing.")
    
    bnb["qpv"] = bnb["nom_quartier"].apply(lambda x: 1 if x != "" else 0)

    if "alea" not in list(bnb.columns): 
        raise ValueError("alea column is missing.")
    
    bnb = bnb.rename(columns={"alea": "alea_argiles"})

    to_select = ["parcelle_id"] + BNB_SELECTED_VARS
    bnb = bnb[to_select]
   
    return bnb

def create_dvfplus(dvf: DataFrame, bnb: DataFrame) -> DataFrame: 
    """Description. Create DVF+ dataset.
    
    Args:
        dvf (DataFrame): DVF dataset.
        bnb (DataFrame): Base Nationale des Batiments dataset.
        
    Returns:
        DataFrame: DVF+ dataset which consists of DVF features augmented with BNB features."""

    parcelle_ids = select_dvf_parcelle_ids(dvf)

    bnb = preprocess(bnb, parcelle_ids) 

    dvfplus = pd.merge(
        dvf,
        bnb, 
        how="left", 
        left_on=DVF_PARCELLE_KEY, 
        right_on=BNB_PARCELLE_KEY)
    
    return dvfplus
    


