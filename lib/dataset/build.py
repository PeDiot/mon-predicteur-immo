"""Description. 
Build dataset from DVF+ using methods from utils.py."""

from pandas.core.frame import DataFrame
from typing import (
    Dict, 
    Tuple, 
    Optional,
)

from lib.enums import (
    DVF_SELECTED_VARS, 
    BNB_SELECTED_VARS
)

from .utils import (
    remove_na_cols, 
    filter_df_with_quant_var, 
    transform_price, 
    extract_int_from_string
)

def prepare_dataset(
        df: DataFrame,
        quant_filters: Dict, 
        neighborhood_var: Optional[str]=None,
        na_threshold: float=.2, 

) -> Tuple:
    
    dvf_vars_updated = DVF_SELECTED_VARS
    bnb_vars_updated = BNB_SELECTED_VARS

    df = df[DVF_SELECTED_VARS + BNB_SELECTED_VARS]
    df, na_cols = remove_na_cols(df, threshold=.2)

    for col in na_cols:   
        if col in dvf_vars_updated: 
            dvf_vars_updated.remove(col)
        elif col in bnb_vars_updated: 
            bnb_vars_updated.remove(col)

    print(f"{na_cols} removed due to missing values above {na_threshold}")

    if "valeur_fonciere" not in df.columns: 
        raise ValueError("valeur_fonciere not in df.columns")

    df["valeur_fonciere_m2"] = df.apply(lambda row: transform_price(row.valeur_fonciere, False, row.surface_reelle_bati), axis=1) 
    df["l_valeur_fonciere"] = df.apply(lambda row: transform_price(row.valeur_fonciere, True), axis=1) 

    dvf_vars_updated.append("valeur_fonciere_m2")
    dvf_vars_updated.append("l_valeur_fonciere")

    for var_name, interval in quant_filters.items(): 
        if var_name not in df.columns: 
            raise ValueError(f"{var_name} not in df.columns")
        
        df = filter_df_with_quant_var(df, var_name, interval)

    if neighborhood_var != None: 
        if "nom_commune" not in df.columns: 
            raise ValueError("nom_commune not in df.columns")
        
        df[neighborhood_var] = df.nom_commune.apply(extract_int_from_string)
        dvf_vars_updated.append(neighborhood_var)

    ... 

    return df, dvf_vars_updated, bnb_vars_updated