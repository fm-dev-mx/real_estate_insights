# src/data_access/database_connection.py

import psycopg2
import logging
from dotenv import load_dotenv

from src.utils.logging_config import setup_logging

setup_logging(log_file_prefix="database_connection_log")
logger = logging.getLogger(__name__)

load_dotenv()

def get_db_connection(db: str, user: str, pwd: str, host: str, port: str | int) -> psycopg2.extensions.connection:
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL.
    Requiere parámetros explícitos para la conexión.
    
    Args:
        db: Database name
        user: Database username
        pwd: Database password
        host: Database host
        port: Database port (string or integer)
    
    Returns:
        psycopg2.extensions.connection object
    """
    if not all([db, user, pwd, host, port]):
        raise ValueError("All database connection parameters are required")
    
    # Convert port to string if needed
    port_str = str(port) if isinstance(port, int) else port
    
    try:
        conn = psycopg2.connect(
            dbname=db,
            user=user,
            password=pwd,
            host=host,
            port=port_str
        )
        logger.info("Conexión a la base de datos exitosa.")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        raise
