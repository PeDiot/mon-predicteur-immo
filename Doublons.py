import pandas as pd 
import zipfile
from scipy.spatial.distance import pdist, squareform

zf = zipfile.ZipFile(r'C:/Users/flore/OneDrive/Bureau/2023/Drive/Business Data Challenge/dbf21.zip') 
df = pd.read_csv(zf.open('dbf21/datadvf2021.csv'))

df.drop(columns = ['nature_culture_speciale', 'code_nature_culture', 'nature_culture', 'code_nature_culture_speciale', 'ancien_code_commune', 'ancien_id_parcelle'
])

df_sell = df[df['nature_mutation'] == 'Vente']
pd.set_option('display.max_columns', None)
df_sell.head(2)

Keep  = ['Appartement', 'Maison', 'Dépendance']
df_sell = df_sell[df_sell['type_local'] in Keep]

df_flat = df_sell[df_sell['type_local'] == 'Appartement']
df_house = df_sell[df_sell['type_local'] == 'Maison']
df_dep = df_sell[df_sell['type_local'] == 'Dépendance']

# Traitement Appartements
temp = df_flat.groupby("id_mutation").size()
duplica = temp[temp>1].index.tolist()
len(duplica) # nb d'id_mutation générant des duplica
flat_duplicated = df_flat.loc[df_flat.id_mutation.isin(duplica),:]

no_duplica = temp[temp==1].index.tolist()
len(no_duplica) # nb d'id_mutation n'étant pas des duplica
flat_no_duplicated = df_flat.loc[df_flat.id_mutation.isin(no_duplica),:]

# Vérifs 
len(df_flat) == len(flat_no_duplicated) + len(flat_duplicated) # value needs to be True 
len(flat_duplicated) # 190822
len(flat_no_duplicated) # 414343
len(df_flat) # 605165

dropout_rate = len(flat_duplicated) / (len(flat_no_duplicated) + len(flat_duplicated))
dropout_rate # 0.31

# ini
cleaned_flat_duplicated = []
c = 0.6

for d in duplica:
    subdf_flat_duplicated = flat_duplicated[flat_duplicated['id_mutation'] == '{d}']
    temp = pd.DataFrame(1 - squareform(pdist(flat_duplicated.set_index('id_mutation'), lambda u,v: (u != v).mean())))
    temp.values[np.tril_indices_from(temp)] = np.nan
    if (temp.unstack().mean() >= c ): 
        random_row = subdf_flat_duplicated.sample(n = 1)
        cleaned_flat_duplicated.append(random_row)
    else: 
        print('for {d} similarity between rows is not high enough')
    temp.drop()
    random_row.drop()
    subdf_flat_duplicated.drop()

cleaned_flat_duplicated = pd.DataFrame(cleaned_flat_duplicated)
cleaned_flat_duplicated.head(100)

dropout_rate_clean = len(cleaned_flat_duplicated) / (len(flat_no_duplicated) + len(cleaned_flat_duplicated))
dropout_rate_clean
