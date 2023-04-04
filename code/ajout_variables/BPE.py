
import pandas as pd 
import numpy as np 
import zipfile
import os
import matplotlib.pyplot as plt
import geopy.distance

os.chdir('C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge')
df_zip = zipfile.ZipFile(r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge\bpe21.zip')
df = pd.read_csv(df_zip.open('bpe21_ensemble_xy.csv'), sep = ";")

VARS = ['AN','DCIRIS','DEP','QUALI_IRIS','LAMBERT_X','LAMBERT_Y','TYPEQU']
df2 = df.loc[:, df.columns.isin(VARS)]

def nb_type_by_IRIS(df, type):
    """
    Returns the number of type per IRIS

    example: nb_type(df, 'A501') returns the number of A501 per IRIS
    """
    return df.groupby(["DCIRIS"])['TYPEQU'].apply(lambda x: (x==type).sum()).reset_index(name='count').sort_values(by='count', ascending=True)

dict = {'A501': 'COIFFURE', 'A502': 'VÉTÉRINAIRE',  'A506': 'PRESSING-LAVERIE AUTOMATIQUE',
        'B101':  'HYPERMARCHÉ','B102': 'SUPERMARCHÉ','B201' : 'SUPÉRETTE', 'B202': 'ÉPICERIE', 
        'B203': 'BOULANGERIE', 'B204': 'BOUCHERIE CHARCUTERIE','C101': 'ÉCOLE MATERNELLE', 
        'C102': 'ÉCOLE MATERNELLE DE REGROUPEMENT PÉDAGOGIQUE INTERCOMMUNAL (RPI) DISPERSÉ',
        'C104': 'ÉCOLE ÉLÉMENTAIRE', 'C201' : 'COLLÈGE' ,'C301': 'LYCÉE D’ENSEIGNEMENT GÉNÉRAL ET/OU TECHNOLOGIQUE',
        'C302': 'LYCÉE D’ENSEIGNEMENT PROFESSIONNEL', 'C303': 'LYCÉE D’ENSEIGNEMENT TECHNIQUE ET/OU PROFESSIONNEL AGRICOLE',
        'D201': 'MÉDECIN GÉNÉRALISTE', 'D307': 'PHARMACIE', 'E107': 'GARE DE VOYAGEURS D’INTÉRÊT NATIONAL',
        'E108': 'GARE DE VOYAGEURS D’INTÉRÊT RÉGIONAL', 'E109': 'GARE DE VOYAGEURS D’INTÉRÊT LOCAL'}

for k in dict.keys():
    tmp  = nb_type_by_IRIS(df2, k)
    df2 = df2.merge(tmp, left_on = 'DCIRIS', right_on = 'DCIRIS', how='left')
    df2.rename(columns={'count': 'nb_'+dict[k]}, inplace=True)
    print(f'nb_{dict[k]} ajouté')

k = df2.shape[1] - len(VARS)
size = df2.shape
print(f'on a ajouté {k} variables\n la base fait maintenant {size}') 

# regroupement 
df2['nb_Alimentaire'] = df2['nb_HYPERMARCHÉ'] + df2['nb_SUPERMARCHÉ'] + df2['nb_SUPÉRETTE'] + df2['nb_ÉPICERIE']
df2['nb_lycee'] = df2['nb_LYCÉE D’ENSEIGNEMENT GÉNÉRAL ET/OU TECHNOLOGIQUE'] + df2['nb_LYCÉE D’ENSEIGNEMENT PROFESSIONNEL'] + df2['nb_LYCÉE D’ENSEIGNEMENT TECHNIQUE ET/OU PROFESSIONNEL AGRICOLE']
df2['nb_ECOLE_MARTERNELLE'] = df2['nb_ÉCOLE MATERNELLE'] + df2['nb_ÉCOLE MATERNELLE DE REGROUPEMENT PÉDAGOGIQUE INTERCOMMUNAL (RPI) DISPERSÉ']

df2.drop(['nb_GARE DE VOYAGEURS DINTÉRÊT LOCAL',
        'nb_LYCÉE D’ENSEIGNEMENT GÉNÉRAL ET/OU TECHNOLOGIQUE', 
        'nb_LYCÉE D’ENSEIGNEMENT PROFESSIONNEL',
        'nb_LYCÉE D’ENSEIGNEMENT TECHNIQUE ET/OU PROFESSIONNEL AGRICOLE',
        'nb_HYPERMARCHÉ', 'nb_SUPERMARCHÉ', 'nb_SUPÉRETTE', 'nb_ÉPICERIE', 
        'nb_ÉCOLE MATERNELLE', 'nb_ÉCOLE MATERNELLE DE REGROUPEMENT PÉDAGOGIQUE INTERCOMMUNAL (RPI) DISPERSÉ'],axis=1)

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

# on importe la base dvf_v2 & on vient ajouter les variables, puis on sauvergarde en dvf_v3 :
df4.columns
df4.drop(['LAMBERT_X', 'LAMBERT_Y'], axis=1)
df4['DCIRIS'] = df4['DCIRIS'].astype(float)

path = r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge'
df_dvf3 = pd.read_csv(path+'\\Paris_flats_v2.csv')
Paris_flats_v3  = pd.merge(df_dvf3, df4, left_on=['code_iris'], right_on=['DCIRIS'], how='left')

Paris_flats_v3.to_csv(r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge\Paris_flats_v3.csv', index=False)
