import pandas as pd 
from pandas import DataFrame
import zipfile
from scipy.spatial.distance import pdist, squareform
import numpy as pd 

zf = zipfile.ZipFile(r'C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge/dbf21.zip') 
df = pd.read_csv(zf.open('dbf21/datadvf2021.csv'))
df.head()

def select_sales(df: DataFrame) -> DataFrame: 
    if "nature_mutation" not in df.columns: 
        raise ValueError("nature_mutation not in columns.")
    
    return df.loc[df.nature_mutation == "Vente", :] 

df_sales = select_sales(df)
df_sales.head()

print(f"{df_sales.shape[0]} transactions associées à des ventes \n{df_sales.id_mutation.unique().shape[0]} identifiants uniques de mutation")

def remove_industrial_facilities(df: DataFrame) -> DataFrame: 
    if "code_type_local" not in df.columns: 
        raise ValueError("code_type_local not in columns.")
    
    return df.loc[
        (df.code_type_local >= 1) & 
        (df.code_type_local < 4), 
        :
    ] 
df_sales = remove_industrial_facilities(df_sales)
print(f"{df_sales.shape[0]} ventes d'appartements/maisons/dépendances")

pd.crosstab(df_sales["type_local"], df_sales["code_type_local"], margins=True)

temp = df_sales.groupby("id_mutation").size()
not_duplicated = temp[temp==1].index.tolist()
mutations_simples = df_sales.loc[df_sales.id_mutation.isin(not_duplicated), :]

temp = df_sales.groupby("id_mutation").size()
duplica = temp[temp>1].index.tolist()
mutations_complexes = df_sales.loc[df_sales.id_mutation.isin(duplica), :]

df2 = mutations_complexes

# vérifs : 
def variables_by_format(dataframe: DataFrame, data_type: str):
    """
    Renvoie une liste de nom de variables d'un pd dataframe qui match avec un format donnée 
    """
    return [col for col in dataframe.columns if dataframe[col].dtype == data_type]

list_var_float = variables_by_format(df2, 'float64')
list_var_object = variables_by_format(df2, 'object')
list_var_int64 = variables_by_format(df2, 'int64')
df2.columns

# Approche : aggrégation des variables caractéristiques puis aggrégation des prix 
var_caracteristiques = ['type_local', 'nature_mutation']
for var in var_caracteristiques: 
  df_clean = mutations_complexes.groupby(['id_mutation', 'valeur_fonciere'])[f'{var}'].apply(lambda x: ','.join(x)).reset_index()

var_caracteristiques = ['type_local', 'nature_mutation']

def traitement_multilignes(df: DataFrame, var_varacateristiques: list):
    for var in var_varacateristiques:
        df_clean = df.groupby(['id_mutation', 'valeur_fonciere'])[f'{var}'].apply(lambda x: ','.join(x)).reset_index()

# on a traité le cas des observations en les aggrégeants 
# on a un prb avec les dispositions : il faut les aggréger si y'a num dispo == 1 & une var quanti qui est diff 
# pour ça on a besoin de créer un id_unique par disposition

#Il convient ensuite de reconstituer un identifiant unique pour chaque disposition. Pour
#cela, il convient de concaténer l’identifiant unique des actes avec le champ « Numéro
#de disposition ».
#Il convient d’abord de reconstituer un identifiant unique pour chaque acte. Il est
#possible de le faire en concaténant les champs « Code Service » et « Référence
#document ».




    if df_clean['numero_disposition'] == 1 & 


        return 
    else: pass 

