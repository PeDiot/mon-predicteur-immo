"""Description. 
Build dataset from DVF+ using methods from utils.py."""

import rich 

from pandas.core.frame import DataFrame
from typing import (
    Dict, 
    List, 
    Tuple, 
    Optional,
)

from lib.enums import (
    DVF_SELECTED_VARS, 
    BNB_SELECTED_VARS, 
    DISCRETE_VARS, 
    CATEGORICAL_VARS,
)

from .utils import (
    flatten_list, 
    float_to_string, 
    filter_df_with_quant_var, 
    transform_price, 
    replace_inf_with_nan, 
    extract_int_from_string, 
    calc_movav_prices, 
    add_movav_prices, 
    is_quantitative, 
    to_object, 
    get_cols_with_one_value, 
    process_window_feature, 
    to_dummies, 
    get_dummie_names, 
    remove_reference_levels, 
)

from lib.preprocessing.utils import remove_na_cols

def prepare_dataset(
        df: DataFrame,
        target_var: str,
        quant_filters: Dict,
        na_threshold: float=.2, 
        date_var: str="date_mutation",
        mov_av_windows: Optional[List]=None, 
        neighborhood_var: Optional[str]=None
) -> Tuple:
    """Description. Dataset preparation from DVF+ raw data using methods from utils.py.
    
    Args:
        df (DataFrame): pandas DataFrame with DVF+ data.
        target_var (str): name of target variable.
        quant_filters (Dict): dictionary with quantitative variables and their intervals.
        na_threshold (float): threshold for removing columns with too many missing values.
        date_var (str): name of date column.
        mov_av_winddows (Optional[List]): list of moving average windows.
        neighborhood_var (Optional[str]): name of neighborhood column.
        
    Returns:
        Tuple: DVF dataset with moving average lagged prices, list of variables from DVF, list of variables from BNB."""

    # Instantiate objects to keep track of changes in dataset columns
    dvf_vars_updated = [col for col in df.columns if col in DVF_SELECTED_VARS]
    bnb_vars_updated = [col for col in df.columns if col in BNB_SELECTED_VARS]

    summary = {
        "created": [],
        "removed": []
    }

    df = df[dvf_vars_updated+bnb_vars_updated]

    # Remove columns with too many missing values
    df, na_cols = remove_na_cols(df, threshold=na_threshold)

    for col in na_cols:   
        if col in dvf_vars_updated: 
            dvf_vars_updated.remove(col)
        elif col in bnb_vars_updated: 
            bnb_vars_updated.remove(col)

    summary["removed"].extend(na_cols)

    # Check if target variable is in dataset
    if "valeur_fonciere" not in df.columns: 
        raise ValueError("valeur_fonciere not in df.columns")

    # Get quantitative variables
    quant_vars = [
        var
        for var in df.columns
        if is_quantitative(df[var])
        and var not in CATEGORICAL_VARS
    ]

    # Apply log transformation to quantitative variables
    if target_var == "l_valeur_fonciere": 
        df[target_var] = df.apply(lambda row: transform_price(row.valeur_fonciere, True), axis=1) 

        for var in quant_vars: 
            if var not in DISCRETE_VARS: 

                var_name = f"l_{var}"
                df[var_name] = df[var].apply(transform_price, log=True)
                df = replace_inf_with_nan(df, var_name) 

                if var in dvf_vars_updated:
                    dvf_vars_updated.append(var_name)
                elif var in bnb_vars_updated: 
                    bnb_vars_updated.append(var_name)

                summary["created"].append(var_name)

    # Create price per square meter variable
    df["valeur_fonciere_m2"] = df.apply(lambda row: transform_price(row.valeur_fonciere, False, row.surface_reelle_bati), axis=1) 
    dvf_vars_updated.append("valeur_fonciere_m2")
    summary["created"].append("valeur_fonciere_m2")

    # Apply filters on dvf variables 
    
    for var_name, interval in quant_filters.items(): 

        if var_name not in df.columns: 
            raise ValueError(f"{var_name} not in df.columns")
        
        df = filter_df_with_quant_var(df, var_name, interval)

    # Convert categorical variables to object type
    for var in CATEGORICAL_VARS: 
        if var in df.columns: 
            df[var] = df[var].apply(float_to_string) 

    # Extract neighborhood from nom_commune
    if neighborhood_var != None: 
        if "nom_commune" not in df.columns: 
            raise ValueError("nom_commune not in df.columns")
        
        df[neighborhood_var] = df.nom_commune.apply(extract_int_from_string)

        dvf_vars_updated.append(neighborhood_var)
        summary["created"].append(neighborhood_var)

        df.drop(labels=["nom_commune"], axis=1, inplace=True)
        dvf_vars_updated.remove("nom_commune")
        summary["removed"].append("nom_commune")

    # Create moving average lagged prices
    if mov_av_windows != None: 

        for window in mov_av_windows: 
            tmp = calc_movav_prices(df, window, 1, "valeur_fonciere", date_var, neighborhood_var)
            df = add_movav_prices(df, tmp, date_var, neighborhood_var) 

            ma_var = f"valeur_fonciere_ma{window}"

            if target_var == "l_valeur_fonciere": 
                l_ma_var = f"l_{ma_var}"
                df[l_ma_var] = df[ma_var].apply(transform_price, log=True)

                df.drop(labels=[ma_var], axis=1, inplace=True)

                dvf_vars_updated.append(l_ma_var)
                summary["created"].append(l_ma_var)

            else: 
                dvf_vars_updated.append(ma_var)
                summary["created"].append(ma_var)

        del tmp 

    # Preprocess dummies related to baie_orientation
    baie_orientation_cols = [col for col in df.columns if "baie_orientation" in col]
    if len(baie_orientation_cols) > 0: 
        df = process_window_feature(df) 

    # Print summary and return objects 

    rich.print("Preprocessing summary:")
    rich.print(summary) 

    return df, dvf_vars_updated, bnb_vars_updated

def prepare_dummies(
    df: DataFrame, 
    categorical_vars: List,
    reference_levels: Dict, 
    dvf_vars: List,    
    bnb_vars: List
) -> Tuple: 
    """Description. Prepare dummies for categorical variables.
    
    Args:
        df (DataFrame): pandas DataFrame with DVF+ data.
        categorical_vars (List): list of categorical variables.
        reference_levels (Dict): dictionary with categorical variables and their reference levels.
        dvf_vars (List): list of variables from DVF.
        bnb_vars (List): list of variables from BNB.
        
    Returns:
        Tuple: DVF dataset with dummies, list of variables from DVF, list of variables from BNB."""

    summary = {
        "created": [],
        "removed": []
    }

    if len(categorical_vars) > 0: 

        df = to_dummies(df, categorical_vars)
        
        dummies_added_dvf = [
            get_dummie_names(df, prefix) 
            for prefix in categorical_vars
            if prefix in dvf_vars
        ]
        dummies_added_dvf = flatten_list(dummies_added_dvf)
        dummies_added_dvf = list(set(dummies_added_dvf))
        dvf_vars.extend(dummies_added_dvf)

        summary["created"].extend(dummies_added_dvf)

        dummies_added_bnb = [
            get_dummie_names(df, prefix) 
            for prefix in categorical_vars
            if prefix in bnb_vars
        ]
        dummies_added_bnb = flatten_list(dummies_added_bnb)
        dummies_added_bnb = list(set(dummies_added_bnb))
        bnb_vars.extend(dummies_added_bnb)

        summary["created"].extend(dummies_added_bnb)

        df, dummies_removed = remove_reference_levels(df, reference_levels)

        for dum in dummies_removed: 
            if dum in dvf_vars: 
                dvf_vars.remove(dum)
            elif dum in bnb_vars:
                bnb_vars.remove(dum) 

            summary["removed"].append(dum)

    to_remove = get_cols_with_one_value(df)

    if len(to_remove) > 0:
        df = df.drop(labels=to_remove, axis=1)

        summary["removed"].extend(to_remove)

        for col in to_remove:
            bnb_vars.remove(col)

    rich.print("Preprocessing summary:")
    rich.print(summary) 

    return df, dvf_vars, bnb_vars
        
