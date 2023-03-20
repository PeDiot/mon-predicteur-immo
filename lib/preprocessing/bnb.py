"""Description. Data preprocessing methods for "Base Nationale des Batiments" dataset."""

import pandas as pd 
from typing import List
from tqdm import tqdm 
import os 

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
)

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