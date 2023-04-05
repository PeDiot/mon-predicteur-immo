# Business Data Challenge - Outil de Prédiction des Prix des Biens Immobiliers 

## Objectif

Constuire un outil de prédiction des prix des biens immobiliers en France à partir de modèles de Machine Learning. L'approche choisie consiste à séparer les maisons des appartements ainsi que les zones géographiques. L'outil est donc une collection de modèles de régression par type de bien et zone géographique. 

## Données

La base de données [`dvf+`](https://drive.google.com/drive/folders/106JJF6v_Z3dLZpjdX3Qr_FXqwBcMmA-j?usp=share_link) est constuite à partir des base de données Demandes de Valeurs Foncières (`dvf`) et Base Nationale des Bâtiments (`bnb`). Elle se compose de plusieurs tables ayant pour nom `[geo_area]_[property_type].csv`.

Les zones géographiques contenues dans `dvf+` sont les suivantes : 

- `Paris` 
- `Marseille` 
- `Lyon` 
- `Toulouse` 
- `Nice` 
- `Nantes` 
- `Montpellier` 
- `Bordeaux` 
- `Lille` 
- `Rennes`
- `urban_areas` (toutes les zones urbaines différentes des villes ci-dessus)
- `rural_areas` (toutes les zones rurales). 

Les types de propriété contenus dans `dvf+` sont :

- `flats`
- `houses`

Pour importer une table de la base de données `dvf+`: 

```python
df = load_dvfplus(zip_dir="./data/", zip_name="dvf+", property_type="flats", geo_area="Paris")
```

La base de données `dvf+` est téléchargeable [ici](https://drive.google.com/drive/folders/106JJF6v_Z3dLZpjdX3Qr_FXqwBcMmA-j?usp=share_link).

## `lib`

La librairie `lib` a été implémentée en python pour constuire l'outil de prédicition des prix de l'immobilier. 

### Architecture

```
lib/
├── __init__.py
├── enums.py
├── preprocessing/
├── model/
└── dataset/
```

### Description des modules

| Fichier/Module  | Description  |
|---|---|
| `__init__.py`  | Initialise la librairie  |
|  [`enums.py`](./lib/enums.py) | Variables prenant des valeurs pré-définies |
| [`preprocessing/`](./lib/preprocessing/)  | Pré-traitement des bases de données `dvf` et `bnb`  |
| [`dataset/`](./lib/dataset/)  | Création dataset pour modèles, feature selection, train/test split |
| [`model/`](./lib/model/) |  Régresseurs `sklearn` & `pytorch`, optimisation, évaluation résultats |

### Exemples d'utilisation 

- [`sk_regressors`](./analysis/sk_regressors.ipynb) : entrainement de modèles de régressions `sklearn` pour une zone géographique et un type de bien données
- [`bnb_cleaning`](./cleaning/bnb_cleaning.ipynb) : pré-traitement de la base de données `bnb` avant la création de `dvf+`

## Résultats 

### Sélection des variables

Le module [`dataset/`](./lib/dataset/) contient des méthodes pour identifier les features les plus intéressantes pour prédire la variable cible choisie: 
- l'information mutuelle (MI) : mesure la dépendance entre les variables. Elle est égale à zéro si et seulement si deux variables aléatoires sont indépendantes, et des valeurs plus élevées signifient une plus grande dépendance.
- la *mean decrease gini* (MDG): diminution de l'indice de Gini que l'on obtient en supprimant une variable du modèle. L'indice de Gini mesure la pureté d'un ensemble de donnée. Plus la MDG est élevée, plus la variable est importante dans le modèle. 

```python
# import required libraries
from lib.dataset import (
    compute_mutual_info, 
    compute_rf_importances, 
    select_important_features
)

# computance importances
mi_values = compute_mutual_info(X, y, features, n_neighbors=5)
mdg_values = compute_rf_importances(X, y, features)

# select important features
mi_threshold = "50%"
mdg_threshold = "75%"

important_features_mi = select_important_features(mi_values, threshold=mi_threshold)
important_features_mdg = select_important_features(mdg_values, threshold=mdg_threshold)
```

### Optimisation des modèles

Le module [`model`](./lib/model/) contient plusieurs méthodes pour optimiser les hyperparamètres des régresseurs `sklearn` à partir d'[`optuna`](https://optuna.org/).`optuna` est un framework python permerttant de trouver les paramètres maximisant (ou minimisant) une fonction objectif. 

```python 
# import required libraries
from lib.model import CustomRegressor
from lib.model.optimize import optuna_objective, OptimPruner

# prepare inputs to create study
pruner = OptimPruner(n_warmup_trials=5, n_trials_to_prune=10)

optuna_args = {
    "storage": f"sqlite:///./backup/__optuna/db.sqlite3", 
    "study_name": "optuna_study", 
    "pruner": pruner
}

study = optuna.create_study(direction="minimize", **optuna_args)

# prepare inputs for optimization function
regressor = CustomRegressor(estimator=XGBRegressor())

optim_args = {
    "regressor": regressor,
    "X_tr": X_tr_,
    "y_tr": y_tr,
    "X_te": X_te_,
    "y_te": y_te, 
    "to_prices": False
}

# launch optimization
study.optimize(
    func=lambda trial: optuna_objective(trial, **optim_args),
    n_trials=30,
    n_jobs=CPU_COUNT/2,
    show_progress_bar=True
)
```

## Sauvegarde & Chargement des modèles

Pour sauvegarder un modèle que l'on vient d'entrainer, le nom des features utilisées et les métriques obtenues, on peut utiliser la fonction  [`save_model`](./lib/model/loader.py). Voici un exemple pour sauvergarder un modèle de type `XGBRegressor` ayant été entrainé sur les appartements à Paris.

```python
from lib.model.loader import save_model

model_args = {
    "version": 0, 
    "geo_area": "Paris", 
    "property_type": "flats"
}

save_model(
    path=f"./backup/models",
    model=xgb_opt, 
    feature_names=feature_names, 
    metrics=xgb_opt_metrics, 
    **model_args)
```

Les modèles entrainées pour chaque couple `(geo_area, property_type)` sont contenus dans le dossier [`models/`](https://drive.google.com/drive/folders/1IHx-pWICxmMUAIB-oqP3EkCPhqI4fXYL?usp=share_link). Une fois le dossier téléchargé et placé dans [`backup`](./backup/), il est possible de charger le modèle pour le couple `(geo_area, property_type)`. Voici un exemple pour importer un modèle de type `XGBRegressor` ayant été entrainé sur les appartements à Paris.

```python
from lib.model.loader import load_model

model_args = {
    "version": 0, 
    "geo_area": "Paris", 
    "property_type": "flats"
}

model_loader = load_model(
    path="./backup/models",
    estimator_name="XGBRegressor", 
    **backup_args)
```
