from pandas.core.frame import DataFrame

from rich.table import Table
import rich 

import matplotlib.pyplot as plt
import seaborn as sns

from .utils import transform_price
from lib.preprocessing.utils import get_na_proportion

def summarize_dataset(df: DataFrame): 

    selected = ["valeur_fonciere", "nombre_pieces_principales", "surface_reelle_bati", "surface_terrain"]
    tmp = df[selected]

    tmp["valeur_fonciere_m2"] = tmp.apply(
        lambda row: transform_price(row.valeur_fonciere, log=False, area=row.surface_reelle_bati), 
        axis=1
    )

    tmp.drop(columns=["valeur_fonciere"], inplace=True)

    numeric_vars = ["valeur_fonciere_m2", "surface_reelle_bati", "surface_terrain"]

    print(f"Dataset summary for {tmp.shape[0]:,} observations") 

    print("*" * 80)

    na_table = Table(title="Missing values")

    na_table.add_column("Variable")
    na_table.add_column("Missing values (%)")

    for var in tmp.columns: 
        na_prop = get_na_proportion(tmp, var)
        na_table.add_row(var, f"{round(100 * na_prop, 2)}%")

    rich.print(na_table)

    print("*" * 80)

    print("Numeric variables")

    summary_numeric_vars = tmp[numeric_vars].describe(percentiles=[.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    rich.print(summary_numeric_vars)
     
    fig, axes = plt.subplots(ncols=2, nrows=2, figsize=(12, 8))

    for var, ax in zip(numeric_vars, axes.flatten()): 
        thresold = summary_numeric_vars[var]["99%"]

        x = tmp.loc[tmp[var] < thresold, var].dropna()
        sns.histplot(x, ax=ax, bins=50)

    axes[-1, -1].set_axis_off()

    plt.show()

    print("*" * 80)

    print("Number of rooms")

    num_rooms_distrib = tmp\
        .nombre_pieces_principales\
        .value_counts(dropna=False, normalize=True)\
        .reset_index()\
        .rename(columns={"index": "nombre_pieces_principales", "nombre_pieces_principales": "proportion"})

    rich.print(num_rooms_distrib)