"""Description. 
Script which creates a dataset with density level, number of inhabitants per municipality."""

import pandas as pd

DATA_DIR = "../../data/"
ZIP_DIR = f"{DATA_DIR}dvf.zip"

ZIP_CODE_DIR = f"{DATA_DIR}french-zip-code/"
DENSITY_DIR = f"{DATA_DIR}densite/"

density = pd.read_excel(f"{DENSITY_DIR}grille_densite_7_niveaux_detaille_2022.xlsx").\
    rename(columns={
        "Code commune": "code_commune", 
        "Libellé degré densité": "degre_densite", 
        "Population \nmunicipale \n2019": "pop"
    }).\
    loc[:, ["code_commune", "degre_densite", "pop"]]

# add paris neighborhoods 
# source: https://94.citoyens.com/2019/population-2019-a-paris-par-arrondissement,07-01-2019.html
paris_codes = {
    "Paris 1er Arrondissement": 75101,
    "Paris 2e Arrondissement": 75102,
    "Paris 3e Arrondissement": 75103,
    "Paris 4e Arrondissement": 75104,
    "Paris 5e Arrondissement": 75105,
    "Paris 6e Arrondissement": 75106,
    "Paris 7e Arrondissement": 75107,
    "Paris 8e Arrondissement": 75108,
    "Paris 9e Arrondissement": 75109,
    "Paris 10e Arrondissement": 75110,
    "Paris 11e Arrondissement": 75111,
    "Paris 12e Arrondissement": 75112,
    "Paris 13e Arrondissement": 75113,
    "Paris 14e Arrondissement": 75114,
    "Paris 15e Arrondissement": 75115,
    "Paris 16e Arrondissement": 75116,
    "Paris 17e Arrondissement": 75117,
    "Paris 18e Arrondissement": 75118,
    "Paris 19e Arrondissement": 75119,
    "Paris 20e Arrondissement": 75120
}

density_paris = pd.read_csv(f"{DENSITY_DIR}population_paris.csv").\
    rename(columns={
        "Nom de la commune": "nom_commune", 
        "Population municipale 2019 (Pop légale 2016)": "pop"
    })
density_paris = density_paris.\
    loc[density_paris.nom_commune != "Total", :].\
    loc[:, ["nom_commune", "pop"]]
density_paris.loc[:, "code_commune"] = density_paris["nom_commune"].apply(lambda x: paris_codes[x])
density_paris.loc[:, "degre_densite"] = ["Paris" for _ in range(density_paris.shape[0])]
density_paris = density_paris.drop(labels=["nom_commune"], axis=1)

# add marseille neighborhoods (wiki)
density_marseille = pd.read_csv(f"{DENSITY_DIR}population_marseille.csv").\
    loc[:, ["code_commune", "pop"]] 
density_marseille.loc[:, "degre_densite"] = ["Marseille" for _ in range(density_marseille.shape[0])]

# add lyon neighborhoods (wiki)
density_lyon = pd.read_csv(f"{DENSITY_DIR}population_lyon.csv").\
    loc[:, ["code_commune", "pop"]] 
density_lyon.loc[:, "degre_densite"] = ["Lyon" for _ in range(density_lyon.shape[0])]

# concatenate the 4 datasets
density = pd.concat(
    [
        density, 
        density_paris, 
        density_marseille, 
        density_lyon
    ], 
    axis=0
)

# remove leaging zeroes from municipality ids 
def recode_municipality_id(id: str) -> str: 
    try: 
        return str(int(id))
    except ValueError: 
        return id 

density["code_commune"] = density["code_commune"].apply(recode_municipality_id)

print(density.head())

# save as csv file
file_path = f"{DENSITY_DIR}municipality_density_levels.csv"
density.to_csv(file_path, index=False)
print(f"File successfully saved at {file_path}")