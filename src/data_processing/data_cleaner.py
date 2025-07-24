import pandas as pd
import logging
import os # Added this import
from ..utils.constants import DB_COLUMNS

logger = logging.getLogger(__name__)

def clean_and_transform_data(file_path):
    """
    Lee un archivo Excel, limpia y transforma los datos según el esquema definido.
    """
    logger.info(f"[CLEANING] Iniciando limpieza y transformación de datos para: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"[CLEANING] Error: El archivo {file_path} no existe.")
        return None

    try:
        df = pd.read_excel(file_path)
        logger.info(f"[CLEANING] Datos cargados exitosamente desde: {file_path}")

        # --- DEBUGGING BAÑOS - RAW DATA FROM EXCEL (before rename) ---
        logger.info("[CLEANING] Debugging banos/medios_banos RAW from Excel (before rename):")
        # Check for common variations of 'banios' column name
        for col_name_raw in ['banios', 'Banios']:
            if col_name_raw in df.columns:
                logger.info(f"'{col_name_raw}' RAW Dtype: {df[col_name_raw].dtype}")
                logger.info(f"'{col_name_raw}' RAW head:\n{df[col_name_raw].head().to_string()}")
                logger.info(f"'{col_name_raw}' RAW null count: {df[col_name_raw].isnull().sum()}")
            else:
                logger.info(f"'{col_name_raw}' column does NOT exist RAW from Excel.")

        # Check for common variations of 'mediosBanios' column name
        for col_name_raw in ['medios_banios', 'mediosBanios']:
            if col_name_raw in df.columns:
                logger.info(f"'{col_name_raw}' RAW Dtype: {df[col_name_raw].dtype}")
                logger.info(f"'{col_name_raw}' RAW head:\n{df[col_name_raw].head().to_string()}")
                logger.info(f"'{col_name_raw}' RAW null count: {df[col_name_raw].isnull().sum()}")
            else:
                logger.info(f"'{col_name_raw}' column does NOT exist RAW from Excel.")
        logger.info("--------------------------------------------------")

        # 1. Renombrar columnas a snake_case y acortar nombres largos
        df.rename(columns={
            'fechaAlta': 'fecha_alta',
            'tipoOperacion': 'tipo_operacion',
            'tipoDeContrato': 'tipo_contrato',
            'enInternet': 'en_internet',
            'claveOficina': 'clave_oficina',
            'subtipoPropiedad': 'subtipo_propiedad',
            'codigoPostal': 'codigo_postal',
            'comisionACompartirInmobiliariasExternas': 'comision_compartir_externas',
            'm2C': 'm2_construccion',
            'm2T': 'm2_terreno',
            'mediosBanios': 'medios_banios',
            'nivelesConstruidos': 'niveles_construidos',
            'apellidoP': 'apellido_paterno_agente',
            'apellidoM': 'apellido_materno_agente',
            'nombre': 'nombre_agente',
            'banios': 'banios' # Asegurar que 'banios' se renombra a sí mismo si ya está en minúsculas
        }, inplace=True)
        logger.info("[CLEANING] Columnas renombradas.")

        # 2. Manejar fechaAlta: convertir a datetime
        df['fecha_alta'] = pd.to_datetime(df['fecha_alta'])
        logger.info("[CLEANING] Columna 'fecha_alta' convertida a datetime.")

        # 3. Manejar en_internet y cocina: convertir a booleano, imputando NaN a False
        df['en_internet'] = df['en_internet'].fillna(0).astype(bool)
        df['cocina'] = df['cocina'].apply(lambda x: True if pd.notna(x) and str(x).lower() == 'si' else False) # Asumiendo 'si' indica True
        logger.info("[CLEANING] Columnas 'en_internet' y 'cocina' convertidas a booleano.")

        # 4. Manejar codigo_postal y numero: convertir a string
        df['codigo_postal'] = df['codigo_postal'].astype(str)
        df['numero'] = df['numero'].astype(str) # Mantener como string para flexibilidad
        logger.info("[CLEANING] Columnas 'codigo_postal' y 'numero' convertidas a string.")

        # 5. Manejar otras columnas numéricas: asegurar tipo correcto, mantener nulos
        # Las columnas que eran float64 y ahora son INTEGER en el esquema, se convertirán a Int64 (con mayúscula) para permitir nulos.
        # Pandas 1.0+ soporta Integer arrays con NaN usando Int64.
        for col in ['recamaras', 'niveles_construidos', 'edad', 'estacionamientos']:
            if col in df.columns:
                df[col] = df[col].astype('Int64') # Permite nulos
        
        # Para precio, comision, m2_construccion, m2_terreno, latitud, longitud
        for col in ['precio', 'comision', 'comision_compartir_externas', 'm2_construccion', 'm2_terreno', 'latitud', 'longitud']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce') # Convertir a numérico, nulos si hay error

        # --- Manejo específico para banios y medios_banios: convertir a numérico y rellenar NaN con 0 ---
        for col in ['banios', 'medios_banios']:
            if col in df.columns:
                # Convertir a string primero para manejar valores no numéricos como texto o espacios
                # Luego limpiar espacios, comas, etc., convertir a numérico, forzando errores a NaN, y finalmente rellenar NaN con 0.0
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.strip().str.replace(',', ''), 
                    errors='coerce'
                ).fillna(0.0)
            else:
                df[col] = 0.0 # Asegurar que la columna exista y sea 0.0 si no estaba presente

        logger.info("[CLEANING] Columnas numéricas procesadas.")

        # --- DEBUGGING BAÑOS EN DATA_CLEANER (after fillna) ---
        logger.info("[CLEANING] Debugging banos/medios_banos after numeric conversion and fillna(0):")
        if 'banios' in df.columns:
            logger.info(f"'banios' Dtype: {df['banios'].dtype}")
            logger.info(f"'banios' head:\n{df['banios'].head().to_string()}")
            logger.info(f"'banios' null count: {df['banios'].isnull().sum()}")
        else:
            logger.info("'banios' column does NOT exist in DataFrame after rename.")

        if 'medios_banios' in df.columns:
            logger.info(f"'medios_banios' Dtype: {df['medios_banios'].dtype}")
            logger.info(f"'medios_banios' head:\n{df['medios_banios'].head().to_string()}")
            logger.info(f"'medios_banios' null count: {df['medios_banios'].isnull().sum()}")
        else:
            logger.info("'medios_banios' column does NOT exist in DataFrame after rename.")
        logger.info("--------------------------------------------------")

        # 6. Eliminar columnas excluidas
        columns_to_drop = ['numeroLlaves', 'cuotaMantenimiento', 'institucionHipotecaria']
        df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)
        logger.info("[CLEANING] Columnas excluidas eliminadas.")

        # Asegurar que todas las columnas del esquema final estén presentes y en el orden correcto (opcional, pero buena práctica)
        # y que los nombres finales coincidan exactamente con el esquema de la DB.
        df = df[[col for col in DB_COLUMNS if col in df.columns]]
        logger.info("[CLEANING] DataFrame finalizado con columnas seleccionadas y reordenadas.")

        logger.info("[CLEANING] Limpieza y transformación de datos completada.")
        return df
    except Exception as e:
        logger.error(f"[CLEANING] Error durante la limpieza y transformación de datos: {e}")
        return None
