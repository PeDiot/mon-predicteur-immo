"""Description. Automated script to preprocess DVF dataset for one year.

Example: 
~\business-data-challenge\cleaning> dvf_unique_transactions.py -year 2017
File successfully loaded.
394243 transactions uniques pour l'année 2017
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Zone géographique ┃ Maisons ┃ Appartements ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Paris             │ 92      │ 16,771       │
│ Marseille         │ 874     │ 5,076        │
│ Lyon              │ 103     │ 3,941        │
│ Toulouse          │ 679     │ 3,585        │
│ Nice              │ 136     │ 3,753        │
│ Nantes            │ 713     │ 2,314        │
│ Montpellier       │ 332     │ 2,355        │
│ Bordeaux          │ 723     │ 2,119        │
│ Lille             │ 568     │ 1,466        │
│ Rennes            │ 297     │ 1,825        │
│ urban_areas       │ 95,095  │ 115,530      │
│ rural_areas       │ 114,071 │ 21,693       │
│ Total             │ 213,683 │ 180,428      │
└───────────────────┴─────────┴──────────────┘
File sucessefully saved at ../data/cleaned/dvf_splitted_2017.pkl.
"""

# required libraries
import sys
sys.path.append("../")

from lib.preprocessing import dvf, geo
from lib.preprocessing.utils import get_unique_entries, add_date_components

import pandas as pd 
import numpy as np 

from rich import print 
from rich.console import Console
from rich.table import Table

import sys
import pickle as pkl 

# enums
DATA_DIR = "../data/"
ZIP_DIR = f"{DATA_DIR}dvf.zip"
GEOGRAPHY_DIR = f"{DATA_DIR}geography/"
DENSITY_DIR = f"{DATA_DIR}densite/"

# load data for input year
def extract_info(flag: str):
    """Description. Extract information from command line."""
    i = sys.argv.index(flag) + 1
    return sys.argv[i]

if "-year" not in sys.argv:
    print ("You must provide year using the -year flag")
    sys.exit(1)

year = extract_info(flag="-year")
df = dvf.load_zip_csv(zip_dir=ZIP_DIR, year=year)

print(f"File successfully loaded.")

# select sales
df_sales = dvf.select_sales(df) 
del df 

# remove industrial facilities
df_sales = dvf.remove_industrial_facilities(df_sales)

# split houses/flats and dependencies
dict_sales = {
    "houses_flats": df_sales.loc[df_sales.code_type_local != 3], 
    "dependencies": df_sales.loc[df_sales.code_type_local == 3]
}

del df_sales

# get id_mutation related to one row
unique_ids = get_unique_entries(dict_sales["houses_flats"], "id_mutation")
n_unique_ids = len(unique_ids)
print(f"{n_unique_ids} transactions uniques pour l'année {year}")

dict_sales = {
    k: df.loc[df.id_mutation.isin(unique_ids), :]
    for k, df in dict_sales.items()
}

# split houses and flats
dict_sales["houses"] = dict_sales["houses_flats"]\
    .loc[dict_sales["houses_flats"].code_type_local==1, :]

dict_sales["flats"] = dict_sales["houses_flats"]\
    .loc[dict_sales["houses_flats"].code_type_local==2, :]

del dict_sales["houses_flats"]

# add dependency dummy 
dependencies = dict_sales["dependencies"]
del dict_sales["dependencies"]

dict_sales = {
    property_type: dvf.add_dependency_dummy(df, dependencies)
    for property_type, df in dict_sales.items()
}

# convert department id to character
for property_type, df in dict_sales.items(): 
    df["code_departement"] = df["code_departement"].astype(str)
    dict_sales[property_type] = df

del df 

# add regions 
regions_dpts = pd.read_csv(f"{GEOGRAPHY_DIR}regions_departments.csv")

dict_sales = {
    property_type: pd.merge(left=df, right=regions_dpts, how="left", on="code_departement")
    for property_type, df in dict_sales.items()
} 

# convert code_commune to character
for property_type, df in dict_sales.items(): 
    df["code_commune"] = df["code_commune"].astype(str)
    dict_sales[property_type] = df

del df 

# add density level and population
density = pd.read_csv(f"{DENSITY_DIR}municipality_density_levels.csv")

dict_sales = {
    property_type: pd.merge(left=df, right=density, how="left", on="code_commune")
    for property_type, df in dict_sales.items()
}

# add year, quarter, month and day
dict_sales = {
    property_type: add_date_components(df, date_var="date_mutation") 
    for property_type, df in dict_sales.items()
}

# split by geo area
dict_sales_splitted = {

    property_type: {
        "cities": geo.split_by_city(df), 
        "urban_areas": geo.get_urban_areas(df), 
        "rural_areas": geo.get_rural_areas(df)
    } 

    for property_type, df in dict_sales.items()
    
}

# check coherence of transactions number per property type

for property_type, dfs_splitted in dict_sales_splitted.items(): 

    n1 = dict_sales[property_type].shape[0] 
    n1 -= dict_sales[property_type]\
        .degre_densite\
        .isna()\
        .sum()
        
    n2 = 0    
    for key, dfs in dfs_splitted.items(): 
        if key == "cities": 
            n2 += sum(df.shape[0] for df in dfs.values()) 
        else:
            n2 += dfs.shape[0] 
    
    assert n1 == n2

# build summary table 
table = Table()

table.add_column("Zone géographique")
table.add_column("Maisons")
table.add_column("Appartements")

n_houses_tot, n_flats_tot = 0, 0

for city in geo.CITIES:         
    n_houses = dict_sales_splitted["houses"]["cities"][city].shape[0]
    n_flats = dict_sales_splitted["flats"]["cities"][city].shape[0]
    table.add_row(city, f"{n_houses:,}", f"{n_flats:,}")

    n_houses_tot += n_houses
    n_flats_tot += n_flats 

for area in ("urban_areas", "rural_areas"): 
    n_houses = dict_sales_splitted["houses"][area].shape[0]
    n_flats = dict_sales_splitted["flats"][area].shape[0]
    table.add_row(area, f"{n_houses:,}", f"{n_flats:,}")

    n_houses_tot += n_houses
    n_flats_tot += n_flats 

table.add_row("Total", f"{n_houses_tot:,}", f"{n_flats_tot:,}")

console = Console()
console.print(table)

# save as pickle file

file_path = f"{DATA_DIR}cleaned/dvf_splitted_{year}.pkl"

with open(file_path, "wb") as file: 
    pkl.dump(dict_sales_splitted, file)

print(f"File sucessefully saved at {file_path}.")