# Standard library imports
import io
import os
import logging

# Third-party imports
import psycopg2
from dotenv import load_dotenv

# Local application imports
from src.utils.constants import DB_COLUMNS
from src.data_processing.excel_converter import convert_xls_to_xlsx
from src.data_access.database_connection import get_db_connection
from src.data_access.property_repository import PropertyRepository
from src.data_processing.data_cleaner import clean_and_transform_data
from src.utils.logging_config import setup_logging

# --- INITIALIZATION & CONFIGURATION ---
load_dotenv()  # Cargar variables de entorno desde .env
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'src', 'data_collection', 'downloads')
setup_logging(log_file_prefix="process_inventory_log") # Log prefix for the inventory processing pipeline
logger = logging.getLogger(__name__)

def _get_excel_files_in_directory(directory):
    """Lists all .xlsx and .xls files in the specified directory."""
    return [f for f in os.listdir(directory) if f.endswith('.xlsx') or f.endswith('.xls')]

def _find_xlsx_file(directory, excel_files):
    """Prioritizes and returns the first .xlsx file found."""
    for f in excel_files:
        if f.endswith('.xlsx'):
            target_file = os.path.join(directory, f)
            logger.info(f"[MAIN] Encontrado archivo XLSX: {target_file}")
            return target_file
    return None

def _convert_xls_to_xlsx_if_exists(directory, excel_files):
    """Converts the first .xls file to .xlsx if no .xlsx file is found."""
    for f in excel_files:
        if f.endswith('.xls'):
            xls_file_path = os.path.join(directory, f)
            xlsx_file_name = os.path.splitext(os.path.basename(xls_file_path))[0] + '.xlsx'
            xlsx_file_path = os.path.join(directory, xls_file_name)
            logger.info(f"[MAIN] Encontrado archivo XLS: {xls_file_path}. Intentando convertir a {xlsx_file_path}...")
            # Convert the found .xls file to a .xlsx file for processing.
            if convert_xls_to_xlsx(xls_file_path, xlsx_file_path):
                logger.info(f"[MAIN] Conversión exitosa. El archivo a analizar es: {xlsx_file_path}")
                return xlsx_file_path
            else:
                logger.error(f"[MAIN] Falló la conversión de {xls_file_path}. No se puede proceder con el análisis.")
                return None
    return None

def find_target_excel_file(directory):
    """
    Busca el archivo Excel a procesar en el directorio especificado.
    Prioriza los archivos .xlsx sobre los .xls y convierte el primer .xls si no hay .xlsx.
    """
    excel_files = _get_excel_files_in_directory(directory)

    if not excel_files:
        logger.warning(f"[MAIN] No se encontraron archivos Excel (.xls o .xlsx) en {directory}.")
        return None

    xlsx_file = _find_xlsx_file(directory, excel_files)
    if xlsx_file:
        return xlsx_file

    return _convert_xls_to_xlsx_if_exists(directory, excel_files)

def main():
    logger.info("--- Script clean_data.py iniciado ---")

    # --- Verificación inicial de la conexión a la base de datos ---
    logger.info("[MAIN] Realizando verificación inicial de la conexión a la base de datos...")
    conn_check = None
    try:
        conn_check = get_db_connection()
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
            property_repo = PropertyRepository()
            property_repo.load_properties(cleaned_df, DB_COLUMNS)

        else:
            logger.error("[MAIN] No se pudo obtener un DataFrame limpio.")
    else:
        logger.info("[MAIN] No se encontró un archivo Excel para procesar.")

    logger.info("--- Script clean_data.py finalizado ---")

if __name__ == "__main__":
    main()
