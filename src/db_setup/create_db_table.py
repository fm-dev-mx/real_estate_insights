import psycopg2
import getpass
import logging
import os
from datetime import datetime
from src.utils.constants import DB_COLUMNS # Import DB_COLUMNS

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOG_DIR = os.path.join(BASE_DIR, 'src', 'data_collection', 'logs') # Usar el mismo directorio de logs

# --- LOGGING CONFIGURATION ---
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, f"db_table_creation_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log")

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

# --- SQL para crear la tabla properties ---
create_table_sql = """
CREATE TABLE IF NOT EXISTS properties (
    id VARCHAR(255) PRIMARY KEY,
    fecha_alta DATE,
    status VARCHAR(50),
    tipo_operacion VARCHAR(50),
    tipo_contrato VARCHAR(50),
    en_internet BOOLEAN,
    clave VARCHAR(255),
    clave_oficina VARCHAR(255),
    subtipo_propiedad VARCHAR(255),
    calle VARCHAR(255),
    numero VARCHAR(50),
    colonia VARCHAR(255),
    municipio VARCHAR(255),
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    codigo_postal VARCHAR(10),
    precio DECIMAL(18, 2),
    comision DECIMAL(5, 2),
    comision_compartir_externas DECIMAL(5, 2),
    m2_construccion DECIMAL(10, 2),
    m2_terreno DECIMAL(10, 2),
    recamaras INTEGER,
    banos_totales DECIMAL(4, 1),
    cocina BOOLEAN,
    niveles_construidos INTEGER,
    edad INTEGER,
    estacionamientos INTEGER,
    descripcion TEXT,
    nombre_agente VARCHAR(255),
    apellido_paterno_agente VARCHAR(255),
    apellido_materno_agente VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

def create_properties_table():
    db_name = os.environ.get('REI_DB_NAME', 'real_estate_db')
    db_user = os.environ.get('REI_DB_USER', 'fm_asesor')
    db_password = os.environ.get('REI_DB_PASSWORD')
    db_host = os.environ.get('REI_DB_HOST', '127.0.0.1')
    db_port = os.environ.get('REI_DB_PORT', '5432')

    if not db_password:
        logger.error("Error: La variable de entorno DB_PASSWORD no está configurada. No se puede crear la tabla.")
        return # Salir si no hay contraseña

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
        logger.info("Conexión a la base de datos exitosa.")

        logger.info("Ejecutando sentencia CREATE TABLE...")
        cur.execute(create_table_sql)
        conn.commit()
        logger.info("✅ Tabla 'properties' creada o ya existente en la base de datos.")

        # --- Migración: Asegurar que la columna banos_totales exista ---
        logger.info("Verificando/Añadiendo columna 'banos_totales' para compatibilidad...")
        cur.execute("ALTER TABLE properties ADD COLUMN IF NOT EXISTS banos_totales DECIMAL(4, 1);")
        conn.commit()
        logger.info("✅ Columna 'banos_totales' verificada/añadida.")

        cur.close()

    except psycopg2.Error as e:
        logger.error(f"Error al crear la tabla en la base de datos: {e}")
        logger.error("Por favor, verifica lo siguiente:")
        logger.error("  - Que el servidor PostgreSQL esté en ejecución.")
        logger.error("  - Que la base de datos 'real_estate_db' exista.")
        logger.error("  - Que el usuario 'fm_asesor' tenga permisos para crear tablas.")
        logger.error("  - Que la contraseña sea correcta.")
    finally:
        if conn:
            conn.close()
            logger.info("Conexión a la base de datos cerrada.")
    logger.info("--- Script create_db_table.py finalizado ---")

if __name__ == "__main__":
    create_properties_table()
