import os
import logging
import psycopg2
import pandas as pd
from psycopg2 import extras
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# --- CONFIGURACIÓN DE LOGGING ---
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_collection', 'logs'))
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, "select_properties_log.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN DE LA BASE DE DATOS (desde variables de entorno) ---
DB_NAME = os.environ.get('REI_DB_NAME')
DB_USER = os.environ.get('REI_DB_USER')
DB_PASSWORD = os.environ.get('REI_DB_PASSWORD')
DB_HOST = os.environ.get('REI_DB_HOST')
DB_PORT = os.environ.get('REI_DB_PORT')

# --- PARÁMETROS DE SELECCIÓN DE PROPIEDADES (desde variables de entorno) ---
MIN_PRICE = os.environ.get('MIN_PRICE')
MAX_PRICE = os.environ.get('MAX_PRICE')
PROPERTY_OPERATION_TYPE = os.environ.get('PROPERTY_OPERATION_TYPE')
PROPERTY_TYPE = os.environ.get('PROPERTY_TYPE')
MIN_BEDROOMS = os.environ.get('MIN_BEDROOMS')
MIN_BATHROOMS = os.environ.get('MIN_BATHROOMS')
MAX_AGE_YEARS = os.environ.get('MAX_AGE_YEARS')
MIN_CONSTRUCTION_M2 = os.environ.get('MIN_CONSTRUCTION_M2')
MIN_LAND_M2 = os.environ.get('MIN_LAND_M2')
HAS_PARKING = os.environ.get('HAS_PARKING')
KEYWORDS_DESCRIPTION = os.environ.get('KEYWORDS_DESCRIPTION')

def get_selected_properties():
    logger.info("--- Script select_properties.py iniciado ---")
    conn = None
    try:
        if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
            logger.error("Error: Faltan variables de entorno de la base de datos. Asegúrese de que REI_DB_NAME, REI_DB_USER, REI_DB_PASSWORD, REI_DB_HOST, REI_DB_PORT estén configuradas en el archivo .env")
            return pd.DataFrame()

        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        logger.info("Conexión a la base de datos PostgreSQL exitosa.")

        query = "SELECT * FROM properties WHERE 1=1"
        params = {}

        if MIN_PRICE:
            query += " AND precio >= %(min_price)s"
            params['min_price'] = float(MIN_PRICE)
        if MAX_PRICE:
            query += " AND precio <= %(max_price)s"
            params['max_price'] = float(MAX_PRICE)
        if PROPERTY_OPERATION_TYPE:
            op_types = [op.strip() for op in PROPERTY_OPERATION_TYPE.split(',')]
            query += " AND tipo_operacion IN %(op_types)s"
            params['op_types'] = tuple(op_types)
        if PROPERTY_TYPE:
            prop_types = [pt.strip() for pt in PROPERTY_TYPE.split(',')]
            query += " AND subtipo_propiedad IN %(prop_types)s"
            params['prop_types'] = tuple(prop_types)
        if MIN_BEDROOMS:
            query += " AND recamaras >= %(min_bedrooms)s"
            params['min_bedrooms'] = int(MIN_BEDROOMS)
        if MIN_BATHROOMS:
            query += " AND banios >= %(min_bathrooms)s"
            params['min_bathrooms'] = float(MIN_BATHROOMS)
        if MAX_AGE_YEARS:
            query += " AND edad <= %(max_age_years)s"
            params['max_age_years'] = int(MAX_AGE_YEARS)
        if MIN_CONSTRUCTION_M2:
            query += " AND m2_construccion >= %(min_construction_m2)s"
            params['min_construction_m2'] = float(MIN_CONSTRUCTION_M2)
        if MIN_LAND_M2:
            query += " AND m2_terreno >= %(min_land_m2)s"
            params['min_land_m2'] = float(MIN_LAND_M2)
        if HAS_PARKING and HAS_PARKING.lower() == 'true':
            query += " AND estacionamientos > 0"
        elif HAS_PARKING and HAS_PARKING.lower() == 'false':
            query += " AND (estacionamientos IS NULL OR estacionamientos = 0)"
        if KEYWORDS_DESCRIPTION:
            keywords = [k.strip() for k in KEYWORDS_DESCRIPTION.split(',')]
            keyword_conditions = [f"descripcion ILIKE '%%{k}%%'" for k in keywords]
            query += f" AND ({' OR '.join(keyword_conditions)})"

        logger.info(f"Ejecutando consulta: {query}")
        logger.info(f"Con parámetros: {params}")

        df = pd.read_sql(query, conn, params=params)
        logger.info(f"Se encontraron {len(df)} propiedades que cumplen con los criterios.")
        return df

    except psycopg2.Error as e:
        logger.error(f"Error de PostgreSQL al seleccionar propiedades: {e}")
    except Exception as e:
        logger.error(f"Un error inesperado ocurrió al seleccionar propiedades: {e}")
    finally:
        if conn:
            conn.close()
            logger.info("Conexión a la base de datos cerrada.")
    return pd.DataFrame()

if __name__ == "__main__":
    selected_properties_df = get_selected_properties()
    if not selected_properties_df.empty:
        logger.info("\n--- Primeras 5 filas de las propiedades seleccionadas ---")
        logger.info(selected_properties_df.head().to_string())
        logger.info(f"\nTotal de propiedades seleccionadas: {len(selected_properties_df)}")
    else:
        logger.info("No se encontraron propiedades que cumplan con los criterios de selección.")
    logger.info("--- Script select_properties.py finalizado ---")