# src/data_processing/data_validator.py

import pandas as pd

def get_incomplete_properties(properties_df):
    """
    Identifica propiedades con campos clave faltantes en el DataFrame.

    Args:
        properties_df (pd.DataFrame): DataFrame de propiedades.

    Returns:
        pd.DataFrame: DataFrame con propiedades que tienen campos faltantes.
    """
    if properties_df.empty:
        return pd.DataFrame()

    missing_check_columns = ['banos', 'medios_banos', 'm2_construccion', 'm2_terreno', 'descripcion']

    incomplete_properties_mask = pd.Series([False] * len(properties_df))
    for col in missing_check_columns:
        if col in properties_df.columns:
            if properties_df[col].dtype == 'object':
                incomplete_properties_mask = incomplete_properties_mask | properties_df[col].isnull() | (properties_df[col] == '')
            else:
                incomplete_properties_mask = incomplete_properties_mask | properties_df[col].isnull()

    return properties_df[incomplete_properties_mask]
