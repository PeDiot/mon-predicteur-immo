
import pandas as pd 
import numpy as np 
import zipfile
import os
import matplotlib.pyplot as plt
import geopy.distance

os.chdir('C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge')
df_zip = zipfile.ZipFile(r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge\bpe21.zip')
df = pd.read_csv(df_zip.open('bpe21_ensemble_xy.csv'), sep = ";")

VARS = ['AN','DCIRIS','QUALI_IRIS','LAMBERT_X','LAMBERT_Y','TYPEQU']
df2 = df.loc[:, df.columns.isin(VARS)]

def nb_type_by_IRIS(df, type):
    """
    Returns the number of type per IRIS

    example: nb_type(df, 'A501') returns the number of A501 per IRIS
    """
    return df.groupby(["DCIRIS"])['TYPEQU'].apply(lambda x: (x==type).sum()).reset_index(name='count').sort_values(by='count', ascending=True)

dict = {'A501': 'COIFFURE', 'C101' : 'ÉCOLE MATERNELLE', 
        'C201' : 'COLLÈGE', 'C301' : 'LYCÉE D’ENSEIGNEMENT GÉNÉRAL ET/OU TECHNOLOGIQUE',
        'D201' : 'MÉDECIN GÉNÉRALISTE', 'D307' : 'PHARMACIE', 'C502' : 'INSTITUT UNIVERSITAIRE',
        'C503' : 'ÉCOLE D’INGÉNIEURS', 'B101' : 'HYPERMARCHÉ', 'B102' : 'SUPERMARCHÉ',
        'B103' : 'GRANDE SURFACE DE BRICOLAGE', 'B201' : 'SUPÉRETTE', 'B202' : 'ÉPICERIE'}

print(type(dict)) 

for k in dict.keys():
    tmp  = nb_type_by_IRIS(df2, k)
    df2 = df2.merge(tmp, left_on = 'DCIRIS', right_on = 'DCIRIS', how='left')
    df2.rename(columns={'count': 'nb_'+dict[k]}, inplace=True)
    print(f'nb_{dict[k]} ajouté')

df2.columns
df2.head(10)


# groupby iris mais aussi par année 

df2.to_csv(r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge\bpe.csv', index=False)








# Calcul de la distance entre les biens immobiliers et le commerce le plus proche - still wip ! 
from pyproj import Transformer
transformer = Transformer.from_crs("EPSG:2154", "EPSG:4326")
df2['coords'] = [transformer.transform(x, y) for x, y in zip(df2.LAMBERT_X, df2.LAMBERT_Y)]

> utiliser re pour change re format ici ! 

def distance_to_commerce(df, commerce: str, loc_immo) -> float:
    """
    Returns the distance to the closest commerce

    example: distance_to_commerce(df, 'HYPERMARCHÉ') returns the distance to the closest hypermarché
    """
    df.loc[df.TYPEQU == commerce]
    tmp = df.apply(lambda x: geopy.distance.geodesic(x['coords'], [loc_immo]).m, axis=1)
    return min(tmp)



# filtre par commerce choist dans l'input 
# calcul de la distance entre l'appart et coords 
# return la distance la plus petite

def find_nearest(lat, long):
    distances = hotels.apply(
        lambda row: dist(lat, long, row['lat'], row['lon']), 
        axis=1)
    return hotels.loc[distances.idxmin(), 'name']

members['DCIRIS'] = members.apply(lambda row: find_nearest(row['lat'], row['lon']), axis=1)


from math import radians, cos, sin, asin, sqrt

# on filtre par type de commerce 
commerce= 'A501'
df2.loc[df.TYPEQU == commerce]

# on calcule les distances 
def dist(lat1, long1, lat2, long2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])
    # haversine formula 
    dlon = long2 - long1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km

bien1 = 48.856614
bien2 = 2.3522219
dist(bien1, bien2, df2['coords'][0][0], df2['coords'][0][1])


def distance_to_commerce(df, commerce: str, loc_immo) -> float:
    """
    Returns the distance to the closest commerce for a given location

    example: 
    loc_immo = (48.856614, 2.3522219)
    distance_to_commerce(df, 'HYPERMARCHÉ', loc_immo) returns the distance to the closest hypermarché
    """
    df.loc[df.TYPEQU == commerce]
    df.apply(lambda x: dist(loc_immo[0], loc_immo[1], df2['coords'][x][0], df2['coords'][x][1], axis=1))

loc_immo = [48.856614,2.3522219]
test = df2.loc[df.TYPEQU == 'A501']
dist(loc_immo[0], loc_immo[1], test['coords'][10][0], test['coords'][10][1])


test = test.apply(dist(loc_immo[0], loc_immo[1], test['coords'][10][0], test['coords'][10][1]), axis=1)

test['coords'][x][0]
test

d = distance_to_commerce(df2, 'A501', loc_immo)


    # dist(loc_immo[0], loc_immo[1], df2['coords'][0][0], df2['coords'][0][1])



