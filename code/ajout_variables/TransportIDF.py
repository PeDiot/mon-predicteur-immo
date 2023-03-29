
# Gares et stations du réseau ferré d'Île-de-France (par ligne)

import pandas as pd 
import numpy as np 

path = r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge'
df = pd.read_csv(path + '/emplacement-des-gares-idf.csv', sep =';')
df.columns
df.head(10)

pd.set_option("display.max_columns", None)

VARS = [
    "Geo Point", 
    "nom", 
    "mode", 
    "ligne", 
    "exploitant"
]

df2 = df.loc[:, df.columns.isin(VARS)]

df2.to_csv(r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge\TransportIDF.csv', index=False)
