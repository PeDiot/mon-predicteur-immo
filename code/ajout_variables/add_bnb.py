import numpy as np
import pandas as pd
import os 
from lib.preprocessing import dvf

dir = 'C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge/'
bnb  = pd.read_parquet(dir+'base_nat_bat.parquet')

zf = 'C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge/dvf_cleaned.zip'
dvf = dvf.concat_datasets_per_year(zf, geo_area="Paris", property_type="flats")


n, p = bnb.shape
m, k = dvf.shape

print(f" la base bnb contient {n} x {p} éléments")
print(f" la base dvf contient {m} x {k} éléments")

# on merge avec un inner les deux bdd sur id_parcelle 
merged_df = pd.merge(bnb, dvf, on=['id_parcelle'], how='inner')
l, h  = merged_df.shape
print(f" la base dvf contient {l} x {h} éléments")

