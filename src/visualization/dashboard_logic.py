# src/visualization/dashboard_logic.py

import pandas as pd

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

    # Unificar baños totales (sumando medios baños)
    # Convertir a float para asegurar compatibilidad con NaN y luego a pd.NA para enteros nulos
    banos_series = properties_df['banos'].astype(float) if 'banos' in properties_df.columns else pd.Series([pd.NA] * len(properties_df))
    medios_banos_series = properties_df['medios_banos'].astype(float) if 'medios_banos' in properties_df.columns else pd.Series([pd.NA] * len(properties_df))

    properties_df['banos_totales'] = banos_series.fillna(0) + (medios_banos_series.fillna(0) * 0.5)
    # Convertir a Int64 si no hay decimales y no es NaN, o dejar como float si hay decimales o NaN
    properties_df['banos_totales'] = properties_df['banos_totales'].apply(lambda x: int(x) if pd.notna(x) and x == int(x) else x)

    # Eliminar columnas de fechas y cocina
    columns_to_drop = [
        'fecha_alta', 'fecha_creacion', 'fecha_modificacion', 'cocina', 'banos', 'medios_banos',
        'apellido_paterno_agente', 'apellido_materno_agente', 'created_at', 'updated_at',
        'latitud', 'longitud', 'codigo_postal', 'comision_compartir_externas'
    ]
    properties_df = properties_df.drop(columns=[col for col in columns_to_drop if col in properties_df.columns], errors='ignore')

    return properties_df
