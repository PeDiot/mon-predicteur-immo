
import pandas as pd 
import numpy as np 

path = r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge'
df = pd.read_csv(path + '/espaces_verts.csv', sep =';')

pd.set_option("display.max_columns", None)
df.columns
df.dtypes
df.head(100)

VARS = ["Nom de l'espace vert", 
        "Typologie d'espace vert", 
        "Catégorie",
        "Code postal"
        "Geo point",
        "Geo Shape", 

        ]
df2 = df.loc[:, df.columns.isin(VARS)]

# convert Geo Shape to geoloc since geo point has a lot of NaN 

df2.to_csv(r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge\espaces_verts_IDF.csv', index=False)
