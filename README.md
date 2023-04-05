# Business Data Challenge - Outil de Prédiction des Prix des Biens Immobiliers 

## `lib`

```
lib/
├── __init__.py
├── enums.py
├── preprocessing/
├── model/
└── dataset/
```

| File/Directory  | Description  |
|---|---|
| `__init__.py`  | Initialise la librairie  |
|  `enums.py` | Variables prenant des valeurs pré-définies |
| `preprocessing/`  | Pré-traitement des bases de données `DVF` et `BNB`  |
| `dataset/`  | Création dataset pour modèles, feature selection, train/test split |
| `model/` |  Régresseurs `sklearn` & `pytorch`, optimisation, évaluation résultats |