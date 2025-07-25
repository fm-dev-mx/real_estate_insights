import pandas as pd
import logging
import os # Added this import
from src.utils.constants import DB_COLUMNS

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
        # Check for common variations of 'banos' column name
        banos_variations = ['banos', 'Banos', 'Banio', 'Banios', 'banios']
        medios_banos_variations = ['medios_banos', 'mediosbanos', 'MediosBanos', 'mediosBanios']

        for col_name_raw in banos_variations + medios_banos_variations:
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
            'mediosbanos': 'medios_banos',
            'MediosBanios': 'medios_banos',
            'nivelesConstruidos': 'niveles_construidos',
            'apellidoP': 'apellido_paterno_agente',
            'apellidoM': 'apellido_materno_agente',
            'nombre': 'nombre_agente',
            'Banio': 'banos',
            'Banios': 'banos',
            'banios': 'banos',
            'banos': 'banos' # Asegurar que 'banos' se renombra a sí mismo si ya está en minúsculas
        }, inplace=True)
        logger.info("[CLEANING] Columnas renombradas.")

        # 2. Manejar fechaAlta: convertir a datetime
        if 'fecha_alta' in df.columns:
            df['fecha_alta'] = pd.to_datetime(df['fecha_alta'], errors='coerce')
            logger.info("[CLEANING] Columna 'fecha_alta' convertida a datetime.")
        else:
            logger.warning("[CLEANING] Columna 'fecha_alta' no encontrada en el DataFrame.")

        # 3. Manejar en_internet y cocina: convertir a booleano, imputando NaN a False
        if 'en_internet' in df.columns:
            df['en_internet'] = df['en_internet'].fillna(0).astype(bool)
        else:
            df['en_internet'] = False # Default to False if column does not exist
            logger.warning("[CLEANING] Columna 'en_internet' no encontrada. Inicializando a False.")

        if 'cocina' in df.columns:
            df['cocina'] = df['cocina'].apply(lambda x: True if pd.notna(x) and str(x).lower() == 'si' else False) # Asumiendo 'si' indica True
        else:
            df['cocina'] = False # Default to False if column does not exist
            logger.warning("[CLEANING] Columna 'cocina' no encontrada. Inicializando a False.")
        logger.info("[CLEANING] Columnas 'en_internet' y 'cocina' convertidas a booleano.")

        # 4. Manejar codigo_postal y numero: convertir a string
        if 'codigo_postal' in df.columns:
            df['codigo_postal'] = df['codigo_postal'].fillna('').astype(str)
        else:
            df['codigo_postal'] = "" # Default to empty string if column does not exist
            logger.warning("[CLEANING] Columna 'codigo_postal' no encontrada. Inicializando a cadena vacía.")

        if 'numero' in df.columns:
            df['numero'] = df['numero'].fillna('').astype(str) # Mantener como string para flexibilidad
        else:
            df['numero'] = "" # Default to empty string if column does not exist
            logger.warning("[CLEANING] Columna 'numero' no encontrada. Inicializando a cadena vacía.")
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

        # --- Manejo específico para banos y medios_banos: convertir a numérico y rellenar NaN con 0 ---
        for col in ['banos', 'medios_banos']:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.strip().str.replace(',', ''),
                    errors='coerce'
                ).fillna(0.0)
            else:
                df[col] = 0.0

        # --- Calcular banos_totales ---
        df['banos_totales'] = df['banos'] + (df['medios_banos'] * 0.5)
        logger.info("[CLEANING] Columna 'banos_totales' calculada.")
        logger.info(f"Estadísticas de 'banos_totales':\n{df['banos_totales'].describe().to_string()}")
        logger.info(f"Propiedades con baños totales > 0: {len(df[df['banos_totales'] > 0])}")

        # Eliminar las columnas originales de baños
        df.drop(columns=['banos', 'medios_banos'], inplace=True)
        logger.info("[CLEANING] Columnas 'banos' y 'medios_banos' eliminadas.")

        # --- DEBUGGING BAÑOS EN DATA_CLEANER (after calculation) ---
        logger.info("[CLEANING] Debugging banos_totales after calculation:")
        if 'banos_totales' in df.columns:
            logger.info(f"'banos_totales' Dtype: {df['banos_totales'].dtype}")
            logger.info(f"'banos_totales' head:\n{df['banos_totales'].head().to_string()}")
            logger.info(f"'banos_totales' null count: {df['banos_totales'].isnull().sum()}")
        else:
            logger.info("'banos_totales' column does NOT exist in DataFrame after calculation.")
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
        return pd.DataFrame()
