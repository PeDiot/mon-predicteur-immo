from zipfile import ZipFile

import pandas as pd
import numpy as np
import torch

from pandas.core.frame import DataFrame

from torch.utils.data import TensorDataset, DataLoader

def load_dvfplus(
    zip_dir: str, 
    zip_name: str, 
    geo_area: str, 
    property_type: str, 
    augmented: bool=False,
) -> DataFrame: 
    """Description. Load DVF+ table from zip folder.

    Args:
        zip_dir (str): path to zip folder containing DVF+.
        zip_name (str): name of zip folder containing DVF+.
        geo_area (str): name of geographical area.
        property_type (str): name of property type.
        augmented (bool): whether to load augmented data or not.

    Returns:
        DataFrame: DVF+ pandas DataFrame.
        
    Example:
        >>> from lib.dataset import load_dvfplus
        >>> df = load_dvfplus(zip_dir="./data", zip_name="dvf+",  geo_area="Marseille", property_type="flats")
        >>> df
            id_mutation date_mutation  numero_disposition nature_mutation  valeur_fonciere  ...  l_etat_en_projet l_etat_en_construction l_etat_en_service alea_argiles  alea_radon 
        0      2017-61434    2017-07-04                   1           Vente          38000.0  ...               0.0                    0.0               1.0         Fort       Moyen 
        1      2017-61437    2017-07-05                   1           Vente         125000.0  ...               0.0                    0.0               1.0         Fort      Faible 
        2      2017-61438    2017-07-04                   1           Vente         185000.0  ...               0.0                    0.0               1.0         Fort      Faible 
        3      2017-61439    2017-07-05                   1           Vente          60000.0  ...               0.0                    0.0               1.0         Fort       Moyen 
        4      2017-61440    2017-07-10                   1           Vente          33000.0  ...               0.0                    0.0               1.0         Fort       Moyen 
        ...           ...           ...                 ...             ...              ...  ...               ...                    ...               ...          ...         ... 
        48183  2022-44904    2022-06-23                   1           Vente          87000.0  ...               0.0                    0.0               1.0         Fort      Faible 
        48184  2022-44905    2022-06-20                   1           Vente         208100.0  ...               0.0                    0.0               1.0         Fort      Faible 
        48185  2022-44906    2022-06-10                   1           Vente         135000.0  ...               0.0                    0.0               1.0         Fort      Faible 
        48186  2022-44908    2022-06-23                   1           Vente          40000.0  ...               0.0                    0.0               1.0         Fort       Moyen 
        48187  2022-44909    2022-06-23                   1           Vente          45000.0  ...               0.0                    0.0               1.0         Fort      Faible 

        [48188 rows x 74 columns]"""

    zip_dirpath = f"{zip_dir}/{zip_name}.zip"
    zip_folder = ZipFile(zip_dirpath)

    file_name = f"{zip_name}/{geo_area}_{property_type}"

    if augmented:
        file_name += "_augmented"

    df = pd.read_csv(zip_folder.open(file_name + ".csv"))

    return df

def to_dataloader(X: np.ndarray, y: np.ndarray, batch_size: int=32, shuffle: bool=True) -> DataLoader:
    """Description. Converts (X, y) numpy arrays to pytorch data loader."""
    X = torch.from_numpy(X).float()
    y = torch.from_numpy(y).float()

    dataset = TensorDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

    return dataloader