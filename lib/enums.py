# geo enums

GOOGLE_API_KEY = "AIzaSyCv3ofdclYDumBh63XHe0IkFG4_fjhZrIs"

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

IDF = [
    "Seine-et-Marne", 
    "Yvelines", 
    "Essonne", 
    "Hauts-de-Seine",
    "Seine-Saint-Denis", 
    "Val-de-Marne", 
    "Val-d'Oise"
]

YEARS = [
    2017, 
    2018, 
    2019, 
    2020, 
    2021, 
    2022
]

AVAILABLE_GEO_AREAS = {
    "flats": [
        "bordeaux",
        "hauts-de-seine",
        "lille",
        "lyon",
        "marseille",
        "montpellier",
        "nantes",
        "nice",
        "paris",
        "rennes",
        "seine-saint-denis",
        "toulouse",
        "val-d'oise",
        "val-de-marne", 
        "essonne", 
        "yvelines", 
        "seine-et-marne"
    ],
    "houses": [
        "bordeaux",
        "lille",
        "lyon",
        "marseille",
        "montpellier",
        "nantes",
        "nice",
        "rennes",
        "toulouse",
        "val-d'oise",
        "val-de-marne", 
        "essonne", 
        "seine-saint-denis",
        "seine-et-marne", 
        "yvelines"
    ]
}

AVAILABLE_GEO_AREAS_COORDS = {
    "bordeaux": [44.837789, -0.57918],
    "hauts-de-seine": [48.815573, 2.224199],
    "lille": [50.62925, 3.057256],
    "lyon": [45.764043, 4.835659],
    "marseille": [43.296482, 5.36978],
    "montpellier": [43.610769, 3.876716],
    "nantes": [47.218371, -1.553621],
    "nice": [43.710173, 7.261953],
    "paris": [48.856614, 2.352222],
    "rennes": [48.117266, -1.677793],
    "seine-saint-denis": [48.941, 2.3959],
    "toulouse": [43.604652, 1.444209],
    "val-d'oise": [49.0138, 2.0708],
    "val-de-marne": [48.8, 2.4], 
    "essonne": [48.485294, 2.197863], 
    "yvelines": [48.794997, 1.870641], 
    "seine-et-marne": [48.631633, 2.961794]
}

AVAILABLE_DEPARTMENTS = {
    91: "essonne",
    92: "hauts-de-seine",
    93: "seine-saint-denis",
    95: "val-d'oise",
    94: "val-de-marne",
    78: "yvelines", 
    77: "seine-et-marne", 
}

# DVF enums

DVF_PARCELLE_KEY = "id_parcelle"

DVF_SELECTED_VARS = [
    "id_mutation",
    "date_mutation",
    "valeur_fonciere",
    "nom_commune",
    "nom_departement", 
    "surface_reelle_bati",
    "nombre_pieces_principales",
    "surface_terrain",
    "dependance",
    "trimestre",
    "mois",
]

DVF_LOCATION_VARS = ["adresse_numero", "adresse_nom_voie", "code_postal", "longitude", "latitude"]

# BNB enums

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

VARS_WITH_LIST_VALUES = {
    "l_etat": ["En projet", "En construction", "En service"],
    "baie_orientation": [
        "indetermine",
        "nord",
        "ouest",
        "est",
        "horizontale",
        "est ou ouest",
        "sud", 
    ], 
    "enr": [
        "solaire photovoltaique", 
        "solaire thermique (chauffage)"
        "solaire thermique (ecs)", 
        "solaire thermique (ecs+chauffage)"
    ]
}

BNB_SELECTED_VARS = [
    "periode_construction",
    "periode_construction_max",
    "hauteur_mean",
    "altitude_sol_mean",
    "conso_ener_mean",
    "estim_ges_mean",
    "conso_ener_std",
    "estim_ges_std",
    "conso_ener_min",
    "estim_ges_min",
    "conso_ener_max",
    "estim_ges_max",
    "ratio_ges_conso",
    "enr_solaire_photovoltaique",
    "enr_solaire_thermique_(chauffage)solaire_thermique_(ecs)",
    "enr_solaire_thermique_(ecs+chauffage)",
    "baie_u",
    "mur_u_ext", 
    "pb_u",
    "ph_u",
    "mur_pos_isol_ext",
    "prc_s_vitree_ext",
    "presence_balcon",
    "presence_climatisation",
    "baie_orientation_indetermine",
    "baie_orientation_nord",
    "baie_orientation_ouest",
    "baie_orientation_est",
    "baie_orientation_horizontale",
    "baie_orientation_est_ou_ouest",
    "baie_orientation_sud", 
    "distance_batiment_historique_plus_proche",
    "qpv", 
    "nb_lot_garpark",
    "nb_lot_tot",
    "nb_log",
    "nb_lot_tertiaire",
    "alea_argiles",
    "alea_radon",
]

BNB_PARCELLE_KEY = "parcelle_id"

# Variables from other data sources

## Transportation in Île-de-France: https://data.iledefrance-mobilites.fr/explore/dataset/emplacement-des-gares-idf/table/
## Facilities in Paris: https://www.insee.fr/fr/statistiques/3568638?sommaire=3568656
## Parks in Paris: https://opendata.paris.fr/explore/dataset/espaces_verts/api/?disjunctive.type_ev&disjunctive.categorie&disjunctive.adresse_codepostal&disjunctive.presence_cloture&basemap=jawg.dark&location=11,48.83239,2.34692

OTHER_VARS = [
    "distance_transport",
    "distance_park", 
    "nb_coiffure",
    "nb_veterinaire",
    "nb_pressing-laverie_automatique",
    "nb_hypermarche",
    "nb_supermarche",
    "nb_superette",
    "nb_epicerie",
    "nb_boulangerie",
    "nb_boucherie_charcuterie",
    "nb_ecole_maternelle",
    "nb_ecole_maternelle_de_regroupement_pedagogique_intercommunal_(rpi)_disperse",
    "nb_ecole_elementaire",
    "nb_college",
    "nb_lycee_denseignement_general_et_ou_technologique",
    "nb_lycee_denseignement_professionnel",
    "nb_lycee_denseignement_technique_et_ou_professionnel_agricole",
    "nb_medecin_generaliste",
    "nb_pharmacie",
    "nb_gare_de_voyageurs_dinteret_national",
    "nb_gare_de_voyageurs_dinteret_regional",
    "nb_gare_de_voyageurs_dinteret_local",
    "nb_alimentaire"
]

# Variable types

DISCRETE_VARS = [
    "nombre_pieces_principales",
    "nb_lot_garpark",                          
    "nb_lot_tot",
    "nb_log",
    "nb_lot_tertiaire", 
    "nb_coiffure",
    "nb_veterinaire",
    "nb_pressing-laverie_automatique",
    "nb_hypermarche",
    "nb_supermarche",
    "nb_superette",
    "nb_epicerie",
    "nb_boulangerie",
    "nb_boucherie_charcuterie",
    "nb_ecole_maternelle",
    "nb_ecole_maternelle_de_regroupement_pedagogique_intercommunal_(rpi)_disperse",
    "nb_ecole_elementaire",
    "nb_college",
    "nb_lycee_denseignement_general_et_ou_technologique",
    "nb_lycee_denseignement_professionnel",
    "nb_lycee_denseignement_technique_et_ou_professionnel_agricole",
    "nb_medecin_generaliste",
    "nb_pharmacie",
    "nb_gare_de_voyageurs_dinteret_national",
    "nb_gare_de_voyageurs_dinteret_regional",
    "nb_gare_de_voyageurs_dinteret_local",
    "nb_alimentaire"
]

CATEGORICAL_VARS = ["trimestre", "mois", "nombre_pieces_principales", "code_iris"]