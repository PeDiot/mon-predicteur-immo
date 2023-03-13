import pandas as pd 
from pandas import DataFrame
import zipfile
import numpy as np 
import os 


def open_zip_in_folder(zip_folder_path, inner_zip_filename):
    with zipfile.ZipFile(zip_folder_path, 'r') as zip_folder:
        with zip_folder.open(inner_zip_filename, 'r') as inner_zip:
            inner_zip_file = zipfile.ZipFile(inner_zip)
            filename = inner_zip_file.namelist()[0]
            chunks = pd.read_csv(inner_zip_file.open(filename), chunksize=10000)
            df = pd.concat(chunks)

zip_folder_path = 'C:/Users/flore/OneDrive/Bureau/2023/Drive/_Projects/Business Data Challenge/BaseNatBat.zip'
inner_zip_filename = 'batiment_groupe.zip'
temp = open_zip_in_folder(zip_folder_path, inner_zip_filename)
print(temp)


            with zipfile.ZipFile(inner_zip, 'r') as inner_zip_file:
                # do something with the contents of the inner zip file
                # for example, print the names of all files in the inner zip:
                filename = inner_zip_file.namelist()[0]

                chunks = pd.read_csv(inner_zip_file.open(filename), chunksize=10000)
                df = pd.concat(chunks)
    return df



vars = {
    'batiment_groupe': ['batiment_groupe_id', 'code_iris'],
    'reel_batiment_groupe_parcelle' : ['batiment_groupe_id', 'parcelle_id'],
    'batiment_groupe_argile' : ['batiment_groupe_id','alea'],
    'batiment_groupe_bdtopo_bat' : ['batiment_groupe_id', 'l_etat','hauteur_mean', 'altitude_sol_mean'],
    'batiment_groupe_dpe' : ['batinement_groupe_id',
    'nb_classe_ener_a', 'nb_classe_ener_b', 'nb_classe_ener_c', 'nb_classe_ener_d', 'nb_classe_ener_e', 
    'nb_classe_ener_f', 'nb_classe_ener_g', 'nb_classe_ener_nc', 'nb_classe_ges_a', 'nb_classe_ges_b', 
    'nb_classe_ges_c', 'nb_classe_ges_d', 'nb_classe_ges_e', 'nb_classe_ges_f', 'nb_classe_ges_g', 'nb_classe_ges_nc',
    'conso_ener_mean', 'estim_ges_mean', 'conso_ener_std', 'estim_ges_std', 'conso_ener_min', 'estim_ges_min', 'conso_ener_max',' estim_ges_max'
    ],
    'batiment_groupe_dpe_loctype' : ['baie_orientation', 'baie_type_vitrage', 'baie_u', 'ch_solaire', 'ch_type_ener_corr',
                                     'enr', 'mur_pos_isol_ext', 'mur_u_ext', 'pb_u', 'periode_construction', 'prc_s_vitree_ext',
                                     'periode_construction', 'ph_pos_isol', 'ph_u', 'presence_balcon', 'presence_climatisation'
                                     'type_batiment', 'type_ventilation', 'ratio_ges_conso'], 
    'batiment_groupe_merimee' : ['batiment_groupe_id', 'distance_batiment_historique_plus_proche', 'nom_batiment_historique_plus_proche'], 
    'batiment_groupe_qpv' : ['batiment_groupe_id', 'nom_quartier'], 
    'batiment_groupe_radon' : ['batiment_groupe_id', 'alea'], 
    'batiment_groupe_rnc' : ['batiment_groupe_id', 'periode_construction_max', 'l_annee_construction', 'nb_lot_garpark', 'nb_lot_tot','nb_log','nb_lot_tertiaire'], 
}


# baie_u = coefficient d'isolation thermique d'une baie vitrée 

list_variables_batiment_groupe_bdtopo_bat = [


]


# filtre
df = df[list_variables]
df.head()
df.save()