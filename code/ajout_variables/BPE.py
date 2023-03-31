
import pandas as pd 
import numpy as np 
import zipfile
import os
import matplotlib.pyplot as plt
import geopy.distance

os.chdir('C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge')
df_zip = zipfile.ZipFile(r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge\bpe21.zip')
df = pd.read_csv(df_zip.open('bpe21_ensemble_xy.csv'), sep = ";")

df.columns
VARS = ['AN','DCIRIS','DEP','QUALI_IRIS','LAMBERT_X','LAMBERT_Y','TYPEQU']
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

for k in dict.keys():
    tmp  = nb_type_by_IRIS(df2, k)
    df2 = df2.merge(tmp, left_on = 'DCIRIS', right_on = 'DCIRIS', how='left')
    df2.rename(columns={'count': 'nb_'+dict[k]}, inplace=True)
    print(f'nb_{dict[k]} ajouté')

k = df2.shape[1] - len(VARS)
size = df2.shape
print(f'on a ajouté {k} variables\n la base fait maintenant {size}') 

# traitement code IRIS
df2['DCIRIS']
type(df2['DCIRIS'][0])

df3 = df2[df2["DCIRIS"].str.contains("_IND|0000") == False]
df3 = df3[df3["DCIRIS"].str.contains("2A|2B") == False] 

n = df3.shape[0] - df2.shape[0]
prop = (1 - (df3.shape[0] / df2.shape[0])) *100
print(f'on a supp {n} lignes, soit {round(prop,0)} %') 

# mise au format
df3['AN'] = df3['AN'].astype(str) 
df3.drop('AN', inplace=True, axis=1)
df3['DCIRIS'] = df3['DCIRIS'].astype(str) 

df4 = df3.groupby('DCIRIS').sum().reset_index() # on évite tout doublons sur les code IRIS
print(f"une fois que l'on a sommé par IRIS , on passe de ce format {df3.shape} à {df4.shape}")

df4.to_csv(r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge\bpe.csv', index=False)
