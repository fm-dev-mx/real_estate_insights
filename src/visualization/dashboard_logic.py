# src/visualization/dashboard_logic.py

import pandas as pd
import os
from src.data_collection.download_pdf import PDF_DOWNLOAD_BASE_DIR

def apply_dashboard_transformations(properties_df):
    """
    Aplica transformaciones específicas al DataFrame de propiedades para el dashboard.

    Args:
        properties_df (pd.DataFrame): DataFrame original de propiedades.

    Returns:
        pd.DataFrame: DataFrame de propiedades transformado.
    """
    if properties_df.empty:
        return properties_df

    # Calcular 'días en mercado'
    if 'fecha_alta' in properties_df.columns:
        properties_df['fecha_alta'] = pd.to_datetime(properties_df['fecha_alta'])
        properties_df['dias_en_mercado'] = (pd.to_datetime('today') - properties_df['fecha_alta']).dt.days
    else:
        properties_df['dias_en_mercado'] = pd.NA # Usar pd.NA para valores faltantes

    # Redondear metros de construcción y terreno
    if 'm2_construccion' in properties_df.columns:
        properties_df['m2_construccion'] = properties_df['m2_construccion'].round()
    else:
        properties_df['m2_construccion'] = pd.NA # Usar pd.NA para valores faltantes

    if 'm2_terreno' in properties_df.columns:
        properties_df['m2_terreno'] = properties_df['m2_terreno'].round()
    else:
        properties_df['m2_terreno'] = pd.NA # Usar pd.NA para valores faltantes

    # Añadir columna para indicar si el PDF está disponible localmente
    if 'id' in properties_df.columns:
        properties_df['pdf_available'] = properties_df['id'].apply(
            lambda x: os.path.exists(os.path.join(PDF_DOWNLOAD_BASE_DIR, f"{x}.pdf"))
        )
    else:
        properties_df['pdf_available'] = False

    # Eliminar columnas de fechas y cocina
    columns_to_drop = [
        'fecha_alta', 'fecha_creacion', 'fecha_modificacion', 'cocina',
        'apellido_paterno_agente', 'apellido_materno_agente', 'created_at', 'updated_at',
        'latitud', 'longitud', 'codigo_postal', 'comision_compartir_externas'
    ]
    properties_df = properties_df.drop(columns=[col for col in columns_to_drop if col in properties_df.columns], errors='ignore')

    return properties_df
