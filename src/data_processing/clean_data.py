

"""Este script ETL (Extract, Transform, Load) se encarga de procesar archivos de inventario de bienes raíces,
limpiar y transformar los datos, y cargarlos en una base de datos PostgreSQL.

Funcionalidades principales:
- Búsqueda y conversión automática de archivos .xls a .xlsx.
- Conexión segura a la base de datos usando variables de entorno (`.env`).
- Limpieza y normalización de datos (renombrado de columnas, conversión de tipos, etc.).
- Carga de datos en la base de datos con manejo de conflictos (actualización de registros existentes).
- Registro detallado de operaciones y errores en un archivo de log.

Uso:
1.  Asegurarse de que las variables de entorno de la base de datos (REI_DB_*) estén configuradas en un archivo `.env` en la raíz del proyecto.
2.  Colocar el archivo de inventario (.xls o .xlsx) en el directorio 'src/data_collection/downloads'.
3.  Ejecutar el script desde el directorio 'src/data_processing': 'py clean_data.py'
"""

import io
import pandas as pd
import os
import logging
from datetime import datetime

from dotenv import load_dotenv
from ..utils.constants import DB_COLUMNS
from .excel_converter import convert_xls_to_xlsx
from ..data_access.database_connection import get_db_connection
from ..data_access.property_repository import PropertyRepository

load_dotenv() # Cargar variables de entorno desde .env

# --- DB CONFIGURATION (from environment variables) ---
DB_NAME = os.environ.get('REI_DB_NAME', 'real_estate_db')
DB_USER = os.environ.get('REI_DB_USER', 'fm_asesor')
DB_PASSWORD = os.environ.get('REI_DB_PASSWORD')
DB_HOST = os.environ.get('REI_DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('REI_DB_PORT', '5432')

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'src', 'data_collection', 'downloads')
LOG_DIR = os.path.join(BASE_DIR, 'src', 'data_collection', 'logs') # Usar el mismo directorio de logs

# --- LOGGING CONFIGURATION ---
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, f"data_processing_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
    ]
)

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)









def find_target_excel_file(directory):
    """
    Busca el archivo Excel a procesar en el directorio especificado.
    Prioriza los archivos .xlsx sobre los .xls y convierte el primer .xls si no hay .xlsx.
    """
    excel_files = [f for f in os.listdir(directory) if f.endswith('.xlsx') or f.endswith('.xls')]
    
    if not excel_files:
        logger.warning(f"[MAIN] No se encontraron archivos Excel (.xls o .xlsx) en {directory}.")
        return None

    # Priorizar .xlsx
    for f in excel_files:
        if f.endswith('.xlsx'):
            target_file = os.path.join(directory, f)
            logger.info(f"[MAIN] Encontrado archivo XLSX: {target_file}")
            return target_file

    # Si no hay .xlsx, convertir el primer .xls
    for f in excel_files:
        if f.endswith('.xls'):
            xls_file_path = os.path.join(directory, f)
            xlsx_file_name = os.path.splitext(os.path.basename(xls_file_path))[0] + '.xlsx'
            xlsx_file_path = os.path.join(directory, xlsx_file_name)
            logger.info(f"[MAIN] Encontrado archivo XLS: {xls_file_path}. Intentando convertir a {xlsx_file_path}...")
            if convert_xls_to_xlsx(xls_file_path, xlsx_file_path):
                logger.info(f"[MAIN] Conversión exitosa. El archivo a analizar es: {xlsx_file_path}")
                return xlsx_file_path
            else:
                logger.error(f"[MAIN] Falló la conversión de {xls_file_path}. No se puede proceder con el análisis.")
                return None
    
    return None

def main():
    logger.info("--- Script clean_data.py iniciado ---")

    # --- Verificación inicial de la conexión a la base de datos ---
    logger.info("[MAIN] Realizando verificación inicial de la conexión a la base de datos...")
    conn_check = None
    try:
        if not DB_PASSWORD:
            logger.error("Error: La variable de entorno REI_DB_PASSWORD no está configurada.")
            raise ValueError("La variable de entorno REI_DB_PASSWORD no está configurada.")
        
        conn_check = get_db_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
        logger.info("[MAIN] Verificación de conexión a la base de datos exitosa.")
        conn_check.close()
    except (psycopg2.Error, ValueError) as e:
        logger.error(f"[MAIN] No se pudo establecer conexión con la base de datos: {e}")
        logger.error("[MAIN] El script no continuará. Por favor, verifique la configuración de la base de datos y las variables de entorno.")
        return # Salir del script si la conexión falla

    target_file = find_target_excel_file(DOWNLOAD_DIR)
    
    if target_file:
        cleaned_df = clean_and_transform_data(target_file)
        if cleaned_df is not None:
            logger.info("\n--- Primeras 5 filas del DataFrame limpio ---")
            logger.info(cleaned_df.head().to_string())
            logger.info("\n--- Información general del DataFrame limpio ---")
            buffer = io.StringIO()
            cleaned_df.info(buf=buffer)
            logger.info(buffer.getvalue())
            logger.info("\n--- Conteo de valores nulos del DataFrame limpio ---")
            logger.info(cleaned_df.isnull().sum().to_string())

            # --- Cargar datos a PostgreSQL ---
            property_repo = PropertyRepository(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
            property_repo.load_properties(cleaned_df, DB_COLUMNS)

        else:
            logger.error("[MAIN] No se pudo obtener un DataFrame limpio.")
    else:
        logger.info("[MAIN] No se encontró un archivo Excel para procesar.")

    logger.info("--- Script clean_data.py finalizado ---")

if __name__ == "__main__":
    main()
