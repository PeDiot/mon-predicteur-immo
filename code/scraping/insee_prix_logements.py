import numpy as np 
import pandas as pd 
import zipfile
import 

os.chdir('C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge')

zf = zipfile.ZipFile('C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge/insee_data_logements.zip')
df = pd.read_excel(zf.open('data.xlsx'))
df.rename(columns={"Indice des prix des logements anciens - Paris - Appartements - Base 100 en moyenne annuelle 2015 - Série brute": "Prix", 'Data': 'Date'})

mean()
