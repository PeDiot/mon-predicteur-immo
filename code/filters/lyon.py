import numpy as np
import os 
os.chdir('C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge')
from lib.preprocessing import dvf
import matplotlib.pyplot as plt 
from typing import Optional
from IPython.display import display
import re


pd.set_option("display.max_columns", None)

# DATA
zf = 'C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge/dvf_cleaned.zip'
df_flats = dvf.concat_datasets_per_year(zf, geo_area="Lyon", property_type="flats")
df_houses = dvf.concat_datasets_per_year(zf, geo_area="Lyon", property_type="houses")

df_flats.shape
df_houses.shape

n_unique_ids_flats = df_flats.id_mutation.unique().shape[0]
n_unique_ids_houses = df_houses.id_mutation.unique().shape[0]

assert n_unique_ids_flats == df_flats.shape[0]
assert n_unique_ids_houses == df_houses.shape[0]

print(f"{n_unique_ids_flats} transactions uniques pour les appartements à Lyon")
print(f"{n_unique_ids_houses} transactions uniques pour les maisons à Lyon")


# SELECTION DES VARIABLES 

VARS = [
    "id_mutation", "date_mutation", "valeur_fonciere","nom_commune","longitude","latitude", "pop", 
    "annee", "trimestre", "mois", "jour", "dependance", "surface_terrain", "surface_reelle_bati", 
    "nombre_pieces_principales"]

df2_flats = df_flats.loc[:, df_flats.columns.isin(VARS)]
df2_houses = df_houses.loc[:, df_houses.columns.isin(VARS)]

# FILTRES STATIQUES 

df2_flats.describe()
df2_houses.describe()

## nb de pièces principales 

df2_flats = df2_flats.loc[
    (df2_flats.nombre_pieces_principales > 0) &
    (df2_flats.nombre_pieces_principales <= 8),
    :]

df2_houses = df2_houses.loc[
    (df2_houses.nombre_pieces_principales > 0) &
    (df2_houses.nombre_pieces_principales <= 8),
    :]


def encode_num_rooms(n: int) -> str: 
    """Description. Group properties with 6+ rooms into '6-8' category."""
    if n < 6: 
        return str(int(n))
    else: 
        return "6-8"

# convert to integer
df2_flats["nombre_pieces_principales"] = df2_flats["nombre_pieces_principales"].apply(encode_num_rooms)
df2_houses["nombre_pieces_principales"] = df2_houses["nombre_pieces_principales"].apply(encode_num_rooms)

# Plot: 
df2_flats.nombre_pieces_principales.value_counts().hist()
plt.show()

df2_houses.nombre_pieces_principales.value_counts().hist()
plt.show()

df2_flats.loc[df2_flats.nombre_pieces_principales == "6-8",: ].describe()
df2_houses.loc[df2_houses.nombre_pieces_principales == "6-8",: ].describe()

## Surface du bien
df2_flats.surface_reelle_bati.describe()
df2_houses.surface_reelle_bati.describe()

# On a des maisons relativement petites à Lyon 

fig, axes = plt.subplots(ncols=2, figsize=(14, 5))
fig.suptitle("Avant application du filtre, maisons à Lyon")
sns.histplot(data=df2_houses, x="surface_reelle_bati", bins=100, ax=axes[0])
sns.boxplot(data=df2_houses, x="surface_reelle_bati", ax=axes[1]);  
plt.show()

# Filtre: 
df3_houses = df2_houses.loc[
    (df2_houses.surface_reelle_bati >= 9) & 
    (df2_houses.surface_reelle_bati <= 275), 
    :
]

fig, axes = plt.subplots(ncols=2, figsize=(14, 5))
fig.suptitle("Après application du filtre")

sns.histplot(data=df3_houses, x="surface_reelle_bati", color="orange", bins=100, ax=axes[0])
sns.boxplot(data=df3_houses, x="surface_reelle_bati", color="orange", ax=axes[1]); 
plt.show()

# Même chose avec les appartements 

fig, axes = plt.subplots(ncols=2, figsize=(14, 5))
fig.suptitle("Avant application du filtre, appartements à Lyon")
sns.histplot(data=df2_flats, x="surface_reelle_bati", bins=100, ax=axes[0])
sns.boxplot(data=df2_flats, x="surface_reelle_bati", ax=axes[1]);  
plt.show()

# filtre: 
df3_flats = df2_flats.loc[
    (df2_flats.surface_reelle_bati >= 9) & 
    (df2_flats.surface_reelle_bati <= 200), 
    :
]

fig, axes = plt.subplots(ncols=2, figsize=(14, 5))
fig.suptitle("Avant application du filtre, appartements à Lyon")
sns.histplot(data=df3_flats, x="surface_reelle_bati", bins=100, ax=axes[0])
sns.boxplot(data=df3_flats, x="surface_reelle_bati", ax=axes[1]);  
plt.show()

# Quantification des éléments filtrers: 
nb_appart_filtered =  df2_flats.shape[0] - df3_flats.shape[0]
print(f"On a filtrer {nb_appart_filtered} appartements à Lyon")

nb_houses_filtered =  df2_houses.shape[0] - df3_houses.shape[0]
print(f"On a filtrer {nb_houses_filtered} maisons à Lyon")

## surface terrain: 

def encode_field_area(area: float) -> float: 

    if pd.isna(area): 
        area = 0
    return area 

assert encode_field_area(float("nan")) == 0
assert encode_field_area(102.) == 102.

df3_flats["surface_terrain"] = df3_flats["surface_terrain"].apply(encode_field_area) 
df3_houses["surface_terrain"] = df3_houses["surface_terrain"].apply(encode_field_area) 

# Appartements : 

fig, axes = plt.subplots(ncols=2, figsize=(14, 5))
fig.suptitle("Avant application du filtre")
sns.histplot(data=df3_flats, x="surface_terrain", bins=100, ax=axes[0])
sns.boxplot(data=df3_flats, x="surface_terrain", ax=axes[1]);  
plt.show()

df3_flats.loc[df3_flats.surface_terrain == 0].shape[0] / df3_flats.shape[0]
# 99% de valeurs nulles, on décide donc de supprimer cette variable du jeu de données utilisé pour la modélisation.

# Maisons:
fig, axes = plt.subplots(ncols=2, figsize=(14, 5))
fig.suptitle("Avant application du filtre")
sns.histplot(data=df3_houses, x="surface_terrain", bins=100, ax=axes[0])
sns.boxplot(data=df3_houses, x="surface_terrain", ax=axes[1]);  
plt.show()

# filtre: 
df3_houses = df3_houses.loc[
    (df3_houses.surface_terrain >= 0) & 
    (df3_houses.surface_terrain <= 1200), 
    :
]

# Quantification des éléments filtrers: 
nb_houses_filtered = df2_houses.shape[0] -  df3_houses.shape[0]
print(f"On a filtré {round((nb_houses_filtered / df2_houses.shape[0]) * 100, 1)} % des maisons à Lyon")



## Valeur foncière :

df3_houses["valeur_fonciere"].describe()

fig, axes = plt.subplots(ncols=2, figsize=(14, 5))
fig.suptitle("Valeurs foncières des Maisons")
sns.histplot(data=df3_houses, x="valeur_fonciere", bins=100, ax=axes[0])
sns.boxplot(data=df3_houses, x="valeur_fonciere", ax=axes[1]);
plt.show()

df3_flats["valeur_fonciere"].describe()

fig, axes = plt.subplots(ncols=2, figsize=(14, 5))
fig.suptitle("Valeurs foncières des Appartements")
sns.histplot(data=df3_flats, x="valeur_fonciere", bins=100, ax=axes[0])
sns.boxplot(data=df3_flats, x="valeur_fonciere", ax=axes[1]);
plt.show()

# création des nouvelles variables cibles:
 
def transform_target_variable(price: float, log:bool, area: Optional[float]=None) -> float: 
    y = price
    if area != None: 
        y = y / area
    if log: 
        y = np.log(y)
    return y 


df3_houses["valeur_fonciere_m2"] = df3_houses.apply(lambda row: transform_target_variable(row.valeur_fonciere, False, row.surface_reelle_bati), axis=1) 
df3_houses["l_valeur_fonciere_m2"] = df3_houses.apply(lambda row: transform_target_variable(row.valeur_fonciere_m2, True), axis=1) 
df3_houses["l_valeur_fonciere"] = df3_houses.apply(lambda row: transform_target_variable(row.valeur_fonciere, True), axis=1) 

df3_flats["valeur_fonciere_m2"] = df3_flats.apply(lambda row: transform_target_variable(row.valeur_fonciere, False, row.surface_reelle_bati), axis=1) 
df3_flats["l_valeur_fonciere_m2"] = df3_flats.apply(lambda row: transform_target_variable(row.valeur_fonciere_m2, True), axis=1) 
df3_flats["l_valeur_fonciere"] = df3_flats.apply(lambda row: transform_target_variable(row.valeur_fonciere, True), axis=1) 

# vérifs: 
for target in ("valeur_fonciere_m2", "l_valeur_fonciere", "l_valeur_fonciere_m2"): 
    target
    display(df3_houses[target].describe())

for target in ("valeur_fonciere_m2", "l_valeur_fonciere", "l_valeur_fonciere_m2"): 
    target
    display(df3_flats[target].describe())

# Plot: 
colors = sns.color_palette(n_colors=3)
fig, axes = plt.subplots(ncols=2, nrows=3, figsize=(14,14))

for c, target in enumerate(["valeur_fonciere_m2", "l_valeur_fonciere", "l_valeur_fonciere_m2"]): 
    sns.histplot(data=df3_houses, x=target, bins=100, ax=axes[c, 0], color = colors[c])
    sns.boxplot(data=df3_houses, x=target, ax=axes[c, 1], color=colors[c]);
plt.show()

# Filtre + viz

fig, axes = plt.subplots(ncols=2, nrows=3, figsize=(14, 14))

                                        # filtre à changer + temp à enlever ! # 
tmp_houses = df3_houses.loc[
    (df3_houses.valeur_fonciere_m2 >= 5000) & 
    (df3_houses.valeur_fonciere_m2 <= 20000), 
    :]
prop = tmp_houses.shape[0] / df2_houses.shape[0]

fig.suptitle(f"Après application du filtre ({round(100 *prop, 2)}% de txs conservées)")

for c, target in enumerate(["valeur_fonciere_m2", "l_valeur_fonciere", "l_valeur_fonciere_m2"]): 
    sns.histplot(data=tmp_houses, x=target, bins=100, ax=axes[c, 0], color = colors[c])
    sns.boxplot(data=tmp_houses, x=target, ax=axes[c, 1], color=colors[c]);
plt.show()

del tmp; 

# On refait la même chose pour les appartements: 

colors = sns.color_palette(n_colors=3)
fig, axes = plt.subplots(ncols=2, nrows=3, figsize=(14,14))

for c, target in enumerate(["valeur_fonciere_m2", "l_valeur_fonciere", "l_valeur_fonciere_m2"]): 
    sns.histplot(data=df3_flats, x=target, bins=100, ax=axes[c, 0], color = colors[c])
    sns.boxplot(data=df3_flats, x=target, ax=axes[c, 1], color=colors[c]);
plt.show()

# Filtre + viz

fig, axes = plt.subplots(ncols=2, nrows=3, figsize=(14, 14))

                                             # filtre à changer + temp à enlever! # 
tmp_flats = df3_flats.loc[
    (df3_flats.valeur_fonciere_m2 >= 5000) & 
    (df3_flats.valeur_fonciere_m2 <= 20000), 
    :]
prop = tmp_flats.shape[0] / df2_flats.shape[0]

fig.suptitle(f"Après application du filtre ({round(100 *prop, 2)}% de txs conservées)")

for c, target in enumerate(["valeur_fonciere_m2", "l_valeur_fonciere", "l_valeur_fonciere_m2"]): 
    sns.histplot(data=tmp_flats, x=target, bins=100, ax=axes[c, 0], color = colors[c])
    sns.boxplot(data=tmp_flats, x=target, ax=axes[c, 1], color=colors[c]);
plt.show()
 


## Création de la variable arrondissement
# 
DIGIT = r"[0-9]+"
def extract_int_from_string(string: str) -> int: 
    integer = re.findall(DIGIT, string)
    if len(integer) > 1: 
        raise ValueError("Multiple integers found.")
    return integer[0] 

df3_flats["arrondissement"] = df3_flats.nom_commune.apply(extract_int_from_string)
df3_houses["arrondissement"] = df3_houses.nom_commune.apply(extract_int_from_string)

# Répartitions des arrondissements 
df3_flats.arrondissement.value_counts() / df2_flats.shape[0]
df3_houses.arrondissement.value_counts() / df2_houses.shape[0]
# Presque aucune donnnée dans le 1er arr. 

## Variables temporelles

def get_quarter_year(quarter: int, year: int) -> str: 
    return f"{year}Q{quarter}"

df3_houses["trimestre_annee"] = df3_houses.apply(lambda row: get_quarter_year(row.trimestre, row.annee), axis=1)
df3_flats["trimestre_annee"] = df3_flats.apply(lambda row: get_quarter_year(row.trimestre, row.annee), axis=1)

## Encodage du type de variable 

CAT_VARS = [
    "nombre_pieces_principales", 
    "dependance", 
    "arrondissement", 
    "trimestre_annee" 
]

QUANT_VARS = [
    "valeur_fonciere", 
    "valeur_fonciere_m2", 
    "l_valeur_fonciere", 
    "l_valeur_fonciere_m2", 
    "surface_reelle_bati", 
]

ID_VARS = ["id_mutation", "date_mutation"]

df4_houses = df3_houses.loc[:, ID_VARS+QUANT_VARS+CAT_VARS]
df4_houses.loc[:, CAT_VARS] = df3_houses.loc[:, CAT_VARS].astype(object)
df4_houses.loc[:, QUANT_VARS] = df4_houses.loc[:, QUANT_VARS].astype(float)

df4_flats = df3_flats.loc[:, ID_VARS+QUANT_VARS+CAT_VARS]
df4_flats.loc[:, CAT_VARS] = df3_flats.loc[:, CAT_VARS].astype(object)
df4_flats.loc[:, QUANT_VARS] = df4_flats.loc[:, QUANT_VARS].astype(float)

# Visualisation



# Sélection des variables
