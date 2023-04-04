import pandas as pd 
import numpy as np 
import geopy.distance
from pandas import DataFrame

def format_geo_loc(df: DataFrame, latitude: str, longitude: str,*arg) -> DataFrame:
    """
    format the column 'Geo loc' of df_dvf
    example: format_geo_loc(df_dvf, df_dvf['latitude'], df_dvf['longitude'])
    """
    if 'Geo loc' in df.columns:
        df['Geo loc'] = '42.00, 2.00'
        df['Geo loc'] = df['latitude'].astype(str) + ', ' + df['longitude'].astype(str)
    else:
        print('Error: column Geo loc not found')

    return df_dvf

def geo_to_tuple(df: DataFrame, latitude : str, longitude: str, *arg):
    """
    return a tuple of the format (latitude, longitude) from the columns 'latitude' and 'longitude' of df
    ex. geo_to_tuple(df_dvf, 'latitude', 'longitude')

    """
    if latitude in df.columns and longitude in df.columns:
        df['Geo loc'] = list(zip(df[latitude].astype(str), df[longitude].astype(str)))
    else: 
        print('Error: column latitude or longitude not found')

    return df

def distance(coord1: tuple, coord2: tuple) -> int:
    """
    Computes the distance in meter between two location with the format'42.00, 2.00'
    example : distance(df_dvf['Geo loc'][0], df_transport['Geo Point'][0]) # 3102 m 
    """
    df_dvf['Geo loc'] = df_dvf['latitude'].astype(str) + ', ' + df_dvf['longitude'].astype(str)

    try: 
        distance=  geopy.distance.geodesic(coord1, coord2).m
    except: 
        raise ValueError('Error: distance not computed \n Check the format of the coordinates')
    return distance 


def get_distance_metro(loc : tuple, df: DataFrame)-> DataFrame:
    """
    Compute the distance between the flat and the nearest transport station
    
    loc: (48.856079, 2.386354) 
    df['Geo Point'] is necessary
    """
    tmp = []
    
    for i in range(1, len(df)):
        tmp.insert(1,distance(loc, df['Geo Point'][i]))

    return min(tmp)

def get_distance_park(loc : tuple, df: DataFrame)-> DataFrame:
    """
    Compute the distance between the flat and the nearest transport station
    
    loc: (48.856079, 2.386354) 
    df[Location'] is necessary
    """
    tmp = []
    
    for i in range(1, len(df)):
        tmp.insert(1,distance(loc, df['Location'][i]))

    return min(tmp)

def get_distance_park_metro(coord, df_dvf, df_transport, df_ev):

    distance_metro = get_distance_metro(coord, df_transport)
    distance_park = get_distance_park(coord, df_ev)

    return distance_metro, distance_park

#import zipfile
#path = r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge'
#zf = zipfile.ZipFile(path + '\\dvf+.zip')
#df_dvf = pd.read_csv(zf.open('dvf+/Paris_flats.csv'))
#df_transport = pd.read_csv(path + '\\TransportIDF.csv')
#df_ev = pd.read_csv(path+'\\all_distances_parcs.csv')

#coord = (48.856079, 2.386354)
#get_distance_metro(coord, df_transport)
#get_distance_park(coord, df_ev)
#get_distance_park_metro(coord, df_dvf, df_transport, df_ev)






