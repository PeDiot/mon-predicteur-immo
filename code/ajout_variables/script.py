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

#1/ BPE
df_bpe = pd.read_csv(path+'\\bpe.csv')
zf = zipfile.ZipFile(path + '\\dvf+.zip')
df_dvf = pd.read_csv(zf.open('dvf+/Paris_flats.csv'))
df_merged_bpe2 = pd.merge(df_dvf, df_bpe, left_on=['code_iris'], right_on=['DCIRIS'], how='left')

n = df_dvf.shape[0]
m = df_merged_bpe2.shape[0]
diff2 = n - m 
print(f'on a {n} lignes dans df_dvf et {m} lignes dans df_merged_bpe soit {diff2} lignes de différence ')

# count nb of NaN per column
nb_nan = df_merged_bpe2.isna().sum() / df_merged_bpe2.shape[0]
nb_nan = nb_nan.to_frame()
nb_nan.sort_values(by=0, ascending=False)

alldfs = [var for var in dir() if isinstance(eval(var), pd.core.frame.DataFrame)]
for df in alldfs: 
    print(df)

del df_bpe, nb_nan

#2/ TRANSPORT
df_transport = pd.read_csv(path + '\\TransportIDF.csv')
df_dvf['Geo loc'] = list(zip(df_dvf['latitude'].astype(str), df_dvf['longitude'].astype(str)))

df_transport.loc[df_transport['mode'] == 'METRO']
df_transport.shape # On réduit la complexité des calculs ; (647, 5)

c = 0
df_transport['Latitude'] = 'NaN'
df_transport['Latitude'] = 'NaN'

for i in range(0, len(df_transport)):
    df_transport['Latitude'][i] = df_transport['Geo Point'][i].split(',')[0]
    df_transport['Longitude'][i] = df_transport['Geo Point'][i].split(',')[1]
    c += 1 
c == df_transport.shape[0]

def distance(coord1: str, coord2: str) -> int:
    """
    Computes the distance between two location 

    exemple : 
    coord = '42.00, 2.00'
    distance(df_transport['Geo Point'][0], coord)
    """
    try: 
        distance=  geopy.distance.geodesic(coord1, coord2).m
    except: 
        distance = float(123456789)
    return distance 

df_dvf['Distance'] = 123456789
c= 0 
tmp = []

 
for i in range (1, len(df_dvf)):
    c += 1
    for j in range (1,len(df_transport)): 
        tmp.insert(1, distance(df_dvf['Geo loc'][i], df_transport['Geo Point'][j]))
        df_dvf['Distance'][i] = min(tmp)
    tmp = []
    print(f'{c / df_dvf.shape[0]} done') 

df_dvf['Distance']
df_dvf2 = df_dvf[df_dvf.Distance != 123456789]
df_dvf2.Distance.describe()

# sauvergarde intermédiaire 
path = r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge'
filename = '\Paris_flats_v2'
df_dvf2.to_csv(f'{path}{filename}.csv')
df_dvf2.Distance.describe()
df_dvf2.rename(columns={"Distance": "Distance_transport"})

#3/ ESPACES VERTS
df_ev = pd.read_csv(path+'\\all_distances_parcs.csv')
df_dvf3 = pd.read_csv(path+'\\Paris_flats_v2.csv')
df_dvf3 = df_dvf3.rename(columns={"Distance": "Distance_transport"})

# Préparing data: 
df_ev['long'] = 'NaN'
df_ev['lat'] = 'NaN'
for i in (range(0, len(df_ev))):
    # df_ev['Location'][i] = df_ev['Location'][i].split(",")
    df_ev['long'][i] = df_ev['Location'][i].split(",")[0]
    df_ev['lat'][i] = df_ev['Location'][i].split(",")[1]
df_ev['Location'] = list(zip(df_ev['lat'].astype(str), df_ev['long'].astype(str)))

# check : 
distance(df_dvf3['Geo loc'][0], df_ev['Location'][0])

df_dvf3['Distance_Park'] = 123456789
c = 0
tmp = []

# compute distances: 
for i in range (1, len(df_dvf3)):
    c += 1
    for j in range (1,len(df_ev)): 
        tmp.insert(1, distance(df_dvf3['Geo loc'][i], df_ev['Location'][j]))
        df_dvf3['Distance_Park'][i] = min(tmp)
    tmp = []
    print(f'{c / df_dvf3.shape[0]} done') 




###

df_dvf4 = df_dvf3[df_dvf3.Distance != 123456789]
df_dvf4 = df_dvf4.rename(columns={"Distance": "Distance_park"})

VARS = ['id_mutation', 'Distance_park']
df_dvf5 = df_dvf4.loc[:, df_dvf4.columns.isin(VARS)]

dvf = pd.read_csv(path+'\\Paris_flats_v2.csv')
dvf_v2 = pd.merge(dvf, df_dvf5, left_on=['id_mutation'], right_on=['id_mutation'], how='left')

dvf_v2