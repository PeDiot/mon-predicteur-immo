"""Description. 
Script which merges departments and regions and save a dataset with identification number of each region/dpt."""

import pandas as pd

DATA_DIR = "../../data/"
ZIP_DIR = f"{DATA_DIR}dvf.zip"

GEOGRAPHY_DIR = f"{DATA_DIR}geography/"
DENSITY_DIR = f"{DATA_DIR}densite/"

dpts = pd.read_csv(f"{GEOGRAPHY_DIR}departments.csv").\
    rename(columns={
        "code": "code_departement", 
        "name": "nom_departement", 
        "region_code": "code_region"
    }).\
    drop(labels=["id", "slug"], axis=1)

regions = pd.read_csv(f"{GEOGRAPHY_DIR}regions.csv").\
    rename(columns={
        "code": "code_region", 
        "name": "nom_region"
    }).\
    drop(labels=["id", "slug"], axis=1)

regions_dpts = pd.merge(dpts, regions, on="code_region")

def encode_dpt_code(code: str) -> int: 
    if str.startswith(code, "0"): 
        code = code[1:]

    return code

regions_dpts["code_departement"] = regions_dpts["code_departement"].apply(encode_dpt_code)

regions_dpts.to_csv(f"{GEOGRAPHY_DIR}regions_departments.csv", index=False)