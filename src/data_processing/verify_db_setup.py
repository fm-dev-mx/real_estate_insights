import psycopg2
import getpass
import logging
import os
from datetime import datetime

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOG_DIR = os.path.join(BASE_DIR, 'src', 'data_collection', 'logs') # Usar el mismo directorio de logs

# --- LOGGING CONFIGURATION ---
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, f"db_verify_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log")

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

def verify_db_connection():
    logger.info("--- Script verify_db_setup.py iniciado ---")
    db_name = "real_estate_db"
    db_user = "fm_asesor"
    db_host = "127.0.0.1" # Usar 127.0.0.1 para mayor compatibilidad en Windows
    db_port = "5432"

    logger.info(f"Intentando conectar a la base de datos PostgreSQL:")
    logger.info(f"  Base de Datos: {db_name}")
    logger.info(f"  Usuario: {db_user}")
    logger.info(f"  Host: {db_host}")
    logger.info(f"  Puerto: {db_port}")

    db_password = getpass.getpass("Por favor, introduce la contraseña para el usuario 'fm_asesor': ")

    conn = None
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        logger.info("Conexión a la base de datos exitosa! El usuario 'fm_asesor' puede acceder a 'real_estate_db'.")
        cur.close()

    except psycopg2.Error as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        logger.error("Por favor, verifica lo siguiente:")
        logger.error("  - Que el servidor PostgreSQL esté en ejecución.")
        logger.error("  - Que la base de datos 'real_estate_db' exista.")
        logger.error("  - Que el usuario 'fm_asesor' exista y tenga los permisos correctos.")
        logger.error("  - Que la contraseña sea correcta.")
        logger.error("  - Que el archivo pg_hba.conf de PostgreSQL permita conexiones desde 127.0.0.1 para este usuario/base de datos.")
    finally:
        if conn:
            conn.close()
    logger.info("--- Script verify_db_setup.py finalizado ---")

if __name__ == "__main__":
    verify_db_connection()