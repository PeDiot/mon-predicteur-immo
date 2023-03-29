import numpy as np
import pandas as pd
import os 
from lib.preprocessing import dvf
import matplotlib.pyplot as plt 
from typing import Optional
from IPython.display import display
import re

os.chdir('C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge')
pd.set_option("display.max_columns", None)


# DATA
zf = 'C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge/dvf_cleaned.zip'
df = dvf.concat_datasets_per_year(zf, geo_area= "Ceintures urbaines", property_type="flats")

"Grands centres urbains",
"Centres urbains intermédiaires",
"Ceintures urbaines"

DIGIT = r"[0-9]+"
def extract_int_from_string(string: str) -> int: 
    integer = re.findall(DIGIT, string)
    if len(integer) > 1: 
        raise ValueError("Multiple integers found.")
    return integer[0] 

#df["département"] = df.nom_commune.apply(extract_int_from_string)
#deps = ['91','92', '...']
#df.loc[df['département'] isin(deps)]

