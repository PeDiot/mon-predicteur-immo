CITIES = [
    "Paris", 
    "Marseille", 
    "Lyon", 
    "Toulouse", 
    "Nice", 
    "Nantes", 
    "Montpellier", 
    "Bordeaux", 
    "Lille", 
    "Rennes"
]

URBAN_AREAS = [
    "Grands centres urbains",
    "Centres urbains intermédiaires",
    "Ceintures urbaines"
]

RURAL_AREAS = [
    "Petites villes",
    "Bourgs ruraux", 
    "Rural à habitat dispersé", 
    "Rural à habitat très dispersé"
]

YEARS = [
    2017, 
    2018, 
    2019, 
    2020, 
    2021, 
    2022
]

REL_BATIMENT_GROUPE_PARCELLE = [
    "batiment_groupe_id", 
    "parcelle_id"
]

BATIMENT_GROUPE = [
    "batiment_groupe_id", 
    "code_iris"
]

BATIMENT_GROUPE_ARGILES = ["batiment_groupe_id","alea"]

BATIMENT_GROUPE_BDTOPO_BAT = [
    "batiment_groupe_id", 
    "l_etat", 
    "hauteur_mean", 
    "altitude_sol_mean"
]

BATIMENT_GROUPE_DPE = [
    "batiment_groupe_id",
    "nb_classe_ener_a", 
    "nb_classe_ener_b", 
    "nb_classe_ener_c", 
    "nb_classe_ener_d", 
    "nb_classe_ener_e", 
    "nb_classe_ener_f", 
    "nb_classe_ener_g", 
    "nb_classe_ener_nc", 
    "nb_classe_ges_a", 
    "nb_classe_ges_b", 
    "nb_classe_ges_c", 
    "nb_classe_ges_d", 
    "nb_classe_ges_e", 
    "nb_classe_ges_f", 
    "nb_classe_ges_g", 
    "nb_classe_ges_nc",
    "conso_ener_mean", 
    "estim_ges_mean", 
    "conso_ener_std", 
    "estim_ges_std", 
    "conso_ener_min", 
    "estim_ges_min", 
    "conso_ener_max",
    "estim_ges_max"
]

BATIMENT_GROUPE_DPE_LOGTYPE = [
    "batiment_groupe_id", 
    "baie_orientation", 
    "baie_type_vitrage", 
    "baie_u", 
    "ch_solaire", 
    "ch_type_ener_corr",
    "enr", 
    "mur_pos_isol_ext", 
    "mur_u_ext", 
    "pb_u", 
    "prc_s_vitree_ext",
    "periode_construction", 
    "ph_pos_isol", 
    "ph_u", 
    "presence_balcon", 
    "presence_climatisation", 
    "type_batiment", 
    "type_ventilation", 
    "ratio_ges_conso"
]

BATIMENT_GROUPE_MERIMEE = [
    "batiment_groupe_id", 
    "distance_batiment_historique_plus_proche", 
    "nom_batiment_historique_plus_proche"
]

BATIMENT_GROUPE_QPV = ["batiment_groupe_id", "nom_quartier"]

BATIMENT_GROUPE_RADON = ["batiment_groupe_id", "alea"]

BATIMENT_GROUPE_RNC = [
    "batiment_groupe_id", 
    "periode_construction_max", 
    "l_annee_construction", 
    "nb_lot_garpark", 
    "nb_lot_tot",
    "nb_log",
    "nb_lot_tertiaire"
]