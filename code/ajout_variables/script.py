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

#1/
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

#2/
df_transport = pd.read_csv(path + '\\TransportIDF.csv')
df_dvf['Geo loc'] = list(zip(df_dvf['latitude'].astype(str), df_dvf['longitude'].astype(str)))

df_transport.loc[df_transport['mode'] == 'METRO']
df_transport.shape # On réduit la complexité des calculs ; (647, 5)

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
    try: 
        distance=  geopy.distance.geodesic(coord1, coord2).m
    except: 
        distance = float(123456789)
    return distance 

df_dvf['Distance'] = 123456789
c= 0 
tmp = []
a= distance(df_dvf['Geo loc'][3], df_transport['Geo Point'][10])
tmp.insert(1, a)
min(tmp)
df_dvf['Distance'][3] = min(tmp) 

# 10% en environ 45min ... 
for i in range (1, len(df_dvf)):
    c += 1
    for j in range (1,len(df_transport)): 
        tmp.insert(1, distance(df_dvf['Geo loc'][i], df_transport['Geo Point'][j]))
        df_dvf['Distance'][i] = min(tmp)
    tmp = []
    print(f'{c / df_dvf.shape[0]} done') 

df_dvf.colmuns
df_dvf.Distance.describe()
df.rename(columns={"Distance": "Distance_transport"})

# Sinon, en passant ça en fonction, histoire d'être plus rapide

import geopy.distance

def calculate_distances(df_dvf, df_transport):
    # Define a function to calculate the distance between two points using Geopy
    def distance(loc1, loc2):
        return geopy.distance.distance(loc1, loc2).meters
        
    df_dvf = df_dvf.dropna(subset=['Geo loc'])
    df_transport = df_transport.dropna(subset=['Geo Point'])

    # Initialize the distance column with NaN values
    df_dvf['Distance'] = np.nan

    # Initialize the tmp list
    tmp = []

    # Loop through each row in df_transport
    for j in range(len(df_transport)):
        # Append the jth point in df_transport to the tmp list
        tmp.append(df_transport['Geo Point'][j])

    # Loop through each row in df_dvf
    for i in range(len(df_dvf)):
        # Calculate the distances between the ith point in df_dvf and all points in tmp
        distances = [distance(df_dvf['Geo loc'][i], point) for point in tmp]
        
        # Update the distance column in df_dvf with the minimum distance
        df_dvf.at[i, 'Distance'] = min(distances)
        
        # Clear the tmp list
        tmp.clear()

        # Append all points in df_transport to the tmp list
        for j in range(len(df_transport)):
            tmp.append(df_transport['Geo Point'][j])
        
        # Print progress
        if i % 100 == 0:
            print(f'{i} rows processed.')
    
    return df_dvf


df_dvf = calculate_distances(df_dvf, df_transport)

# OR: 

import geopy.distance

def calculate_distances(df_dvf, df_transport):

    def distance(loc1, loc2):
        try:
            return geopy.distance.distance(loc1, loc2).meters
        except: 
            return 123456789
    
    df_dvf = df_dvf.dropna(subset=['Geo loc'])
    df_transport = df_transport.dropna(subset=['Geo Point'])

    loc1 = np.array(df_dvf['Geo loc'].values.tolist())
    loc2 = np.array(df_transport['Geo Point'].values.tolist())
    total_rows = len(df_dvf)

    distances = np.apply_along_axis(lambda x: np.min([distance(x, y) for y in loc2]), 1, loc1)
    df_dvf['Distance'] = distances

    for i, row in df_dvf.iterrows():
        if i % 10 == 0:
            print(f'{i/total_rows*100:.2f}% of rows processed.')

    return df_dvf


df_dvf = calculate_distances(df_dvf, df_transport)


#3/
df_ev = pd.read_csv(path+'\\all_distances_parcs.csv')

for i in range(0, len(df_ev)):
     df_ev['Location'][i] = df_ev['Location'][i].split(",")
df_ev['Location']

# check : 
df_dvf['Geo loc'] = list(zip(df_dvf['latitude'].astype(str), df_dvf['longitude'].astype(str)))
distance(df_dvf['Geo loc'][0], df_ev['Location'][0])

def calculate_distances_Parks(df):
    """
    Compute distance between df_dvf & df
    """
    df_dvf['Distance_Park'] = 0.0

    def distance(loc1, loc2):
        try:
            return geopy.distance.distance(loc1, loc2).meters
        except: 
            return 123456789
    
    loc1 = np.array(df_dvf['Geo loc'].values.tolist())
    loc2 = np.array(df['Location'].values.tolist())

    distances = np.apply_along_axis(lambda x: np.min([distance(x, y) for y in loc2]), 1, loc1)
    df_dvf['Distance_Park'] = distances

    return df_dvf

t = calculate_distances_Parks(df_ev)
df_dvf
