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
zf = zipfile.ZipFile(path + '\\dvf+.zip')
df_dvf = pd.read_csv(zf.open('dvf+/Paris_flats.csv'))

df_merged_bpe2 = pd.merge(df_dvf, df_bpe, left_on=['code_iris'], right_on=['DCIRIS'], how='left')

n = df_dvf.shape[0]
m = df_merged_bpe2.shape[0]
diff2 = n - m 
k = df_bpe4.shape[0] - df_dvf.shape[0]
print(f'on a {n} lignes dans df_dvf et {m} lignes dans df_merged_bpe soit {diff2} lignes de différence ')

df_merged_bpe2.head(100)

# count nb of NaN per column
nb_nan = df_merged_bpe2.isna().sum() / df_merged_bpe2.shape[0]
nb_nan = nb_nan.to_frame()
nb_nan.sort_values(by=0, ascending=False)

alldfs = [var for var in dir() if isinstance(eval(var), pd.core.frame.DataFrame)]
for df in alldfs: 
    print(df)

del df_bpe, df_dvf, nb_nan

df_transport = pd.read_csv(path + '\\TransportIDF.csv')
df_transport.head()

c = 0
df_transport['Latitude'] = 'NaN'
df_transport['Latitude'] = 'NaN'

for i in range(0, len(df_transport)):
    df_transport['Latitude'][i] = df_transport['Geo Point'][i].split(',')[0]
    df_transport['Latitude'][i] = df_transport['Geo Point'][i].split(',')[1]
    c += 1 
c == df_transport.shape[0]

def distance(coord1: str, coord2: str) -> int:
    """
    Computes the distance between two location 

    exemple : 
    coord = '42.00, 2.00'
    distance(df_transport['Geo Point'][0], coord)
    """
    return geopy.distance.geodesic(coord1, coord2).m

df_dvf['Geo loc'] = df_dvf['longitude'].astype(str) + ', ' + df_dvf['latitude'].astype(str)
df_dvf['Distance'] = '42.00, 2.00'
c= 0 

for i in range (1, len(df_dvf)):
    c += 1
    for j in range (1,len(df_transport)): 
        tmp.insert(1, distance(df_dvf['Geo loc'][i], df_transport['Geo Point'][j]))
    df_dvf['Distance'][i] = min(tmp)
    tmp = []

df_dvf.colmuns
df_dvf.Distance.describe()


# checker si on a des valeurs bizarres de distance en m 
