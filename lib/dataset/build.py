"""Description. 
Build dataset from DVF+ using methods from utils.py."""

import rich 

from pandas.core.frame import DataFrame
from pandas.core.series import Series

from typing import (
    Dict, 
    List, 
    Tuple, 
    Optional,
)

from lib.enums import (
    DVF_SELECTED_VARS, 
    DVF_LOCATION_VARS,
    BNB_SELECTED_VARS, 
    OTHER_VARS, 
    DISCRETE_VARS, 
    CATEGORICAL_VARS,
)

from .utils import (
    flatten_list, 
    float_to_string, 
    filter_numeric_var, 
    transform_price, 
    replace_inf_with_nan, 
    extract_int_from_string, 
    calc_movav_prices, 
    add_movav_prices, 
    is_numeric, 
    get_cols_with_one_value, 
    process_window_feature, 
    to_dummies, 
    get_dummie_names, 
    remove_reference_levels, 
    impute_missing_values
)

from lib.preprocessing.utils import remove_na_cols, get_na_proportion

def prepare_dataset(
    df: DataFrame,
    target_var: str,
    numeric_filters: Optional[Dict]=None,
    na_threshold: float=.2, 
    ma_lag: int=1, 
    date_var: str="date_mutation",
    mov_av_windows: Optional[List]=None, 
    neighborhood_var: Optional[str]=None, 
    keep_location_vars: bool=False,
    print_summary: bool=True, 
    return_var_names: bool=True
) -> Tuple:
    """Description. Dataset preparation from DVF+ raw data using methods from utils.py.
    
    Args:
        df (DataFrame): pandas DataFrame with DVF+ data.
        target_var (str): name of target variable.
        numeric_filters (Dict): dictionary with quantitative variables and their intervals.
        na_threshold (float): threshold for removing columns with too many missing values.
        ma_lag (int): lag for moving average calculation.
        date_var (str): name of date column.
        mov_av_winddows (Optional[List]): list of moving average windows.
        neighborhood_var (Optional[str]): name of neighborhood column.
        keep_location_vars (bool): whether to keep location variables.
        print_summary (bool): whether to print summary of dataset preparation.
        return_var_names (bool): whether to return list of variables from DVF, BNB and other variables.
        
    Returns:
        Tuple: 
            DVF dataset with moving average lagged prices, 
            list of variables from DVF, 
            list of variables from BNB, 
            list of other variables.
    """

    # Instantiate objects to keep track of changes in dataset columns
    dvf_vars_updated = [col for col in df.columns if col in DVF_SELECTED_VARS]
    if keep_location_vars:
        dvf_vars_updated.extend(DVF_LOCATION_VARS)

    bnb_vars_updated = [col for col in df.columns if col in BNB_SELECTED_VARS]
    other_vars_updated = [col for col in df.columns if col in OTHER_VARS]

    summary = {
        "created": [],
        "removed": []
    }

    if len(other_vars_updated) > 0:
        to_select = dvf_vars_updated + bnb_vars_updated + other_vars_updated
    else: 
        to_select = dvf_vars_updated + bnb_vars_updated
    
    df = df[to_select] 

    # Get quantitative variables
    numeric_vars = [
        var
        for var in df.columns
        if is_numeric(df[var])
        and var not in CATEGORICAL_VARS
    ]    

    # Missing values preprocessing
    for var in df.columns:
        
        if get_na_proportion(df, var) <= na_threshold:

            # Impute numeric variables with median
            if var in numeric_vars:
                df.loc[:, var] = impute_missing_values(df[var], dtype="numeric")

            # Impute numeric variables with most frequent value
            else: 
                df.loc[:, var] = impute_missing_values(df[var], dtype="category")

        else: 
            df.drop(var, axis=1, inplace=True)

            if var in dvf_vars_updated: 
                dvf_vars_updated.remove(var)

            elif var in bnb_vars_updated:
                bnb_vars_updated.remove(var)

            elif var in other_vars_updated: 
                other_vars_updated.remove(var)

            summary["removed"].append(var)

    # Check if target variable is in dataset
    if "valeur_fonciere" not in df.columns: 
        raise ValueError("valeur_fonciere not in df.columns")

    # Apply log transformation to quantitative variables
    if target_var == "l_valeur_fonciere": 
        df.loc[:, target_var] = df.apply(lambda row: transform_price(row.valeur_fonciere, True), axis=1) 

        for var in numeric_vars: 
            if var not in DISCRETE_VARS and var in df.columns: 

                var_name = f"l_{var}"
                df.loc[:, var_name] = df[var].apply(transform_price, log=True)
                df = replace_inf_with_nan(df, var_name) 

                if var in dvf_vars_updated:
                    dvf_vars_updated.append(var_name)

                elif var in bnb_vars_updated: 
                    bnb_vars_updated.append(var_name)

                elif var in other_vars_updated: 
                    other_vars_updated.append(var_name)

                summary["created"].append(var_name)

    # Create price per square meter variable
    df.loc[:, "valeur_fonciere_m2"] = df.apply(lambda row: transform_price(row.valeur_fonciere, False, row.surface_reelle_bati), axis=1) 
    
    dvf_vars_updated.append("valeur_fonciere_m2")
    summary["created"].append("valeur_fonciere_m2")

    # Apply filters on dvf variables 
    if numeric_filters is not None: 
        for var_name, interval in numeric_filters.items(): 

            if var_name not in df.columns: 
                print(f"{var_name} has been removed. Filter cannot be applied.")
                continue 
            
            df = filter_numeric_var(df, var_name, interval)

    # Convert categorical variables to object type
    for var in CATEGORICAL_VARS: 
        if var in df.columns: 
            df.loc[:, var] = df[var].apply(float_to_string) 

    # Extract neighborhood_var from nom_commune if neighborhood_var is arrondissement
    if neighborhood_var == "arrondissement": 
        if "nom_commune" not in df.columns: 
            raise ValueError("nom_commune not in df.columns")
        
        df.loc[:, neighborhood_var] = df.nom_commune.apply(extract_int_from_string)

        dvf_vars_updated.append(neighborhood_var)
        summary["created"].append(neighborhood_var)

        df.drop(labels=["nom_commune"], axis=1, inplace=True)
        dvf_vars_updated.remove("nom_commune")
        summary["removed"].append("nom_commune")

    # Create moving average lagged prices
    if mov_av_windows != None: 

        for window in mov_av_windows: 
            tmp = calc_movav_prices(df, window, ma_lag, "valeur_fonciere", date_var, neighborhood_var)
            df = add_movav_prices(df, tmp, date_var, neighborhood_var) 

            ma_var = f"valeur_fonciere_ma{window}"

            if target_var == "l_valeur_fonciere": 
                l_ma_var = f"l_{ma_var}"
                df.loc[:, l_ma_var] = df[ma_var].apply(transform_price, log=True)

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
    if print_summary:
        rich.print("Preprocessing summary:")
        rich.print(summary) 

    if return_var_names:
        return df, dvf_vars_updated, bnb_vars_updated, other_vars_updated
    else: 
        return df 

def prepare_dummies(
    df: DataFrame, 
    categorical_vars: List,
    reference_levels: Dict, 
    remove_cols_with_one_value: bool=True,
    dvf_vars: Optional[List]=None,    
    bnb_vars: Optional[List]=None, 
    other_vars: Optional[List]=None
) -> Tuple: 
    """Description. Prepare dummies for categorical variables.
    
    Args:
        df (DataFrame): pandas DataFrame with DVF+ data.
        categorical_vars (List): list of categorical variables.
        reference_levels (Dict): dictionary with categorical variables and their reference levels.
        remove_cols_with_one_value (bool): whether to remove columns with only one value.
        dvf_vars (Optional[List]): list of variables from DVF.
        bnb_vars (Optional[List]): list of variables from BNB.
        other_vars (Optional[List]): list of other variables.
        
    Returns:
        Tuple: DVF dataset with dummies, list of variables from DVF, list of variables from BNB, list of other variables."""

    summary = {
        "created": [],
        "removed": []
    }

    if len(categorical_vars) > 0: 

        df = to_dummies(df, categorical_vars)
        
        if dvf_vars is not None:
            dummies_added_dvf = [
                get_dummie_names(df, prefix) 
                for prefix in categorical_vars
                if prefix in dvf_vars
            ]
            dummies_added_dvf = flatten_list(dummies_added_dvf)
            dummies_added_dvf = list(set(dummies_added_dvf))
            dvf_vars.extend(dummies_added_dvf)

            summary["created"].extend(dummies_added_dvf)

        if bnb_vars is not None:
            dummies_added_bnb = [
                get_dummie_names(df, prefix) 
                for prefix in categorical_vars
                if prefix in bnb_vars
            ]
            dummies_added_bnb = flatten_list(dummies_added_bnb)
            dummies_added_bnb = list(set(dummies_added_bnb))
            bnb_vars.extend(dummies_added_bnb)

            summary["created"].extend(dummies_added_bnb)

        if other_vars is not None: 
            dummies_added_other = [
                get_dummie_names(df, prefix) 
                for prefix in categorical_vars
                if prefix in other_vars
            ]
            dummies_added_other = flatten_list(dummies_added_other)
            dummies_added_other = list(set(dummies_added_other))
            other_vars.extend(dummies_added_other)

            summary["created"].extend(dummies_added_other)

        df, dummies_removed = remove_reference_levels(df, reference_levels)

        if dvf_vars is not None and bnb_vars is not None:
            for dum in dummies_removed: 

                if dum in dvf_vars: 
                    dvf_vars.remove(dum)

                elif dum in bnb_vars:
                    bnb_vars.remove(dum) 

                elif other_vars is not None and dum in other_vars: 
                    other_vars.remove(dum)

                summary["removed"].append(dum)

    if remove_cols_with_one_value:
        cols = [col for col in df.columns if col not in DVF_LOCATION_VARS]
        to_remove = get_cols_with_one_value(df, cols)

        if len(to_remove) > 0:
            df = df.drop(labels=to_remove, axis=1)

            if dvf_vars is not None and bnb_vars is not None: 
                summary["removed"].extend(to_remove)

                for col in to_remove:

                    if col in bnb_vars:
                        bnb_vars.remove(col)
                    elif col in dvf_vars:
                        dvf_vars.remove(col)
                    elif other_vars is not None and col in other_vars: 
                        other_vars.remove(col)

    if dvf_vars is not None and bnb_vars is not None: 

        rich.print("Preprocessing summary:")
        rich.print(summary) 

        if other_vars is not None: 
            return df, dvf_vars, bnb_vars, other_vars
        else: 
            return df, dvf_vars, bnb_vars

    return df
        
def add_distance_to_transportation(df: DataFrame, transportation: DataFrame) -> DataFrame:
    """Description. Add column which computes distance between properties to closest metro station.
    
    Details: only avaiblable for Paris."""

    if "id_mutation" not in df.columns and "id_mutation" not in transportation.columns:
        raise ValueError("id_mutation must be in both datasets.")

    new_df = df.merge(transportation, on="id_mutation", how="left")
    return new_df

def add_distance_to_parks(df: DataFrame, parks: DataFrame) -> DataFrame:
    """Description. Add column which computes distance between properties to closest park.
    
    Details: only avaiblable for Paris."""

    if "id_mutation" not in df.columns and "id_mutation" not in parks.columns:
        raise ValueError("id_mutation must be in both datasets.")

    new_df = df.merge(parks, on="id_mutation", how="left")
    return new_df

def add_public_facilities(df: DataFrame, facilities: DataFrame) -> DataFrame:
    """Description. Add columns which count the number of several public facilities.
    
    Details: only avaiblable for Paris."""

    if "id_mutation" not in df.columns and "id_mutation" not in facilities.columns:
        raise ValueError("id_mutation must be in both datasets.")    

    new_df = df.merge(facilities, on="id_mutation", how="left")
    return new_df