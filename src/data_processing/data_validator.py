# src/data_processing/data_validator.py

import pandas as pd
import os
import logging
from datetime import datetime  # Added missing import

from src.utils.logging_config import setup_logging

setup_logging(log_file_prefix="data_validator_log")
logger = logging.getLogger(__name__)

# 1. Column-Priority Matrix (authoritative)
COLUMN_PRIORITY = {
    "critical": [
        'id', 'precio', 'm2_construccion', 'm2_terreno', 'recamaras', 'banos_totales',
        'descripcion', 'status', 'tipo_operacion', 'tipo_contrato', 'colonia',
        'municipio', 'latitud', 'longitud'
    ],
    "recommended": [
        'codigo_postal', 'calle', 'numero', 'subtipo_propiedad', 'edad',
        'estacionamientos', 'comision', 'nombre_agente', 'apellido_paterno_agente'
    ],
    "optional": [
        'en_internet', 'clave', 'clave_oficina', 'cocina', 'niveles_construidos',
        'apellido_materno_agente', 'comision_compartir_externas', 'fecha_alta'
    ]
}

# Directorio para los reportes generados
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

def validate_and_report_missing_data(properties_df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida el DataFrame de propiedades, detecta datos faltantes según la matriz de prioridad,
    genera missing_critical.csv y errors_and_fixes.md.

    Args:
        properties_df (pd.DataFrame): DataFrame de propiedades.

    Returns:
        pd.DataFrame: DataFrame original con una columna adicional 'has_critical_gaps' si aplica.
    """
    if properties_df.empty:
        logger.info("DataFrame de propiedades vacío. No hay datos para validar.")
        return properties_df

    # Inicializar el log de errores
    errors_log_path = os.path.join(REPORTS_DIR, 'errors_and_fixes.md')
    with open(errors_log_path, 'w', encoding='utf-8') as f:
        f.write(f"# Log de Errores y Correcciones - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n")
        f.write("Este documento registra los datos faltantes detectados y las acciones sugeridas.\n\n")

    missing_critical_ids = []
    all_gaps_report = []

    for index, row in properties_df.iterrows():
        property_id = row['id']
        has_critical_gaps = False
        property_gaps = {'id': property_id}

        for priority, columns in COLUMN_PRIORITY.items():
            for col in columns:
                if col in row and (pd.isna(row[col]) or (isinstance(row[col], str) and row[col].strip() == '')):
                    gap_info = {
                        'property_id': property_id,
                        'column': col,
                        'priority': priority,
                        'status': 'missing'
                    }
                    all_gaps_report.append(gap_info)
                    property_gaps[col] = 'missing'

                    if priority == "critical":
                        has_critical_gaps = True
                        logger.warning(f"[VALIDATION] Critical missing data for property {property_id} in column: {col}")

        if has_critical_gaps:
            missing_critical_ids.append({'id': property_id})

        # Añadir una columna al DataFrame original para indicar si tiene gaps críticos
        properties_df.loc[index, 'has_critical_gaps'] = has_critical_gaps

    # Generar missing_critical.csv
    missing_critical_df = pd.DataFrame(missing_critical_ids)
    missing_critical_csv_path = os.path.join(REPORTS_DIR, 'missing_critical.csv')
    missing_critical_df.to_csv(missing_critical_csv_path, index=False)
    logger.info(f"Reporte de IDs con gaps críticos guardado en: {missing_critical_csv_path}")

    # Generar errors_and_fixes.md
    with open(errors_log_path, 'a', encoding='utf-8') as f:
        f.write("## Gaps Detectados\n\n")
        if not all_gaps_report:
            f.write("No se detectaron datos faltantes en ninguna columna.\n\n")
        else:
            for gap in all_gaps_report:
                f.write(f"- **Propiedad ID**: {gap['property_id']}, **Columna**: {gap['column']}, **Prioridad**: {gap['priority']}, **Estado**: {gap['status']}\n")
            f.write("\n")

    logger.info(f"Log de errores y correcciones guardado en: {errors_log_path}")

    return properties_df

def get_incomplete_properties(properties_df):
    """
    Identifica propiedades con campos clave faltantes en el DataFrame.
    (Esta función se mantiene para compatibilidad con el dashboard actual, pero la lógica
    principal de validación se mueve a validate_and_report_missing_data).

    Args:
        properties_df (pd.DataFrame): DataFrame de propiedades.

    Returns:
        pd.DataFrame: DataFrame con propiedades que tienen campos faltantes.
    """
    if properties_df.empty:
        return pd.DataFrame()

    # Usar solo las columnas críticas para esta función de compatibilidad
    missing_check_columns = COLUMN_PRIORITY["critical"]

    incomplete_properties_mask = pd.Series([False] * len(properties_df))
    for col in missing_check_columns:
        if col in properties_df.columns:
            if properties_df[col].dtype == 'object':
                incomplete_properties_mask = incomplete_properties_mask | properties_df[col].isnull() | (properties_df[col] == '')
            else:
                incomplete_properties_mask = incomplete_properties_mask | properties_df[col].isnull()

    return properties_df[incomplete_properties_mask]

