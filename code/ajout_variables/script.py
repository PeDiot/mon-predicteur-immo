import pandas as pd 
import numpy as np 
import zipfile
import os
import matplotlib.pyplot as plt
import geopy.distance
from lib.preprocessing import dvf
import zipfile
pd.set_option("display.max_columns", None)
import geopy.distance

path = r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge'

df_bpe = pd.read_csv(path+'\\bpe.csv')
df_transport = pd.read_csv(path + '\\TransportIDF.csv')
df_espaces_verts = pd.read_csv(path + '\\espaces_verts_IDF.csv')

zf = zipfile.ZipFile(path + '\\dvf+.zip')
df_dvf = pd.read_csv(zf.open('dvf+/Paris_flats.csv'))


# traitement code iris
df_dvf['code_iris'] # 751031102
df_bpe['DCIRIS']    # 956070113

type(df_dvf['code_iris'][0])
type(df_bpe['DCIRIS'][0])

df_bpe['DCIRIS'] = df_bpe['DCIRIS'].str.replace(r'[a-zA-Z]', '', regex=True)
df_bpe.shape

df_dvf['code_iris'] = df_dvf['code_iris'].astype(float)
df_bpe['DCIRIS'] = df_bpe['DCIRIS'].astype(float)

df_bpe.groupby('DCIRIS').sum() # on évite tout doublons sur les code IRIS

# création de la variable annnée 
df_bpe['AN'] = df_bpe['AN'].astype(str)
df_dvf['annee'] = df_dvf['date_mutation'].str[:4]

type(df_dvf['annee'][0])
type(df_bpe['AN'][0])

type(df_dvf['code_iris'][0])
type(df_bpe['DCIRIS'][0])

df_merged_bpe2 = pd.merge(df_dvf, df_bpe, left_on=['annee', 'code_iris'], right_on=['AN', 'DCIRIS'], how='left')
# prb d'allocation de mémoire 

n = df_dvf.shape[0]
m = df_merged_bpe2.shape[0]

print(f'on a {n} lignes dans df_dvf et {m} lignes dans df_merged_bpe soit {diff} lignes de différence')

# count nb of NaN per column
nb_nan = df_merged_bpe.isna().sum() / df_merged_bpe.shape[0]
nb_nan = nb_nan.to_frame()
nb_nan.sort_values(by=0, ascending=False) # 43% de NaN sur les variables ajoutées


