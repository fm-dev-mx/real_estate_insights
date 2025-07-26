import psycopg2
import logging
import os
from src.utils.logging_config import setup_logging
from src.data_access.database_connection import get_db_connection

setup_logging(log_file_prefix="create_db_table_log")
logger = logging.getLogger(__name__)

# --- SQL para crear la tabla properties ---
create_table_sql = """
CREATE TABLE IF NOT EXISTS properties (
    id VARCHAR(255) PRIMARY KEY,
    fecha_alta DATE,
    status VARCHAR(50) NOT NULL CHECK (status IN ('enPromocion', 'conIntencion', 'vendidas')),
    tipo_operacion VARCHAR(50) NOT NULL CHECK (tipo_operacion IN ('venta', 'renta', 'traspaso', 'opcion')),
    tipo_contrato VARCHAR(50) NOT NULL CHECK (tipo_contrato IN ('exclusiva', 'opcion', 'abierta')),
    en_internet BOOLEAN,
    clave VARCHAR(255),
    clave_oficina VARCHAR(255),
    subtipo_propiedad VARCHAR(255),
    calle VARCHAR(255),
    numero VARCHAR(50),
    colonia VARCHAR(255) NOT NULL,
    municipio VARCHAR(255) NOT NULL,
    latitud DECIMAL(10, 8) NOT NULL,
    longitud DECIMAL(11, 8) NOT NULL,
    codigo_postal VARCHAR(10),
    precio DECIMAL(18, 2) NOT NULL CHECK (precio >= 0),
    comision DECIMAL(5, 2),
    comision_compartir_externas DECIMAL(5, 2),
    m2_construccion DECIMAL(10, 2) NOT NULL CHECK (m2_construccion >= 0),
    m2_terreno DECIMAL(10, 2) NOT NULL CHECK (m2_terreno >= 0),
    recamaras INTEGER NOT NULL CHECK (recamaras >= 0),
    banos_totales DECIMAL(4, 1) NOT NULL CHECK (banos_totales >= 0),
    cocina BOOLEAN,
    niveles_construidos INTEGER,
    edad INTEGER,
    estacionamientos INTEGER,
    descripcion TEXT NOT NULL,
    nombre_agente VARCHAR(255),
    apellido_paterno_agente VARCHAR(255),
    apellido_materno_agente VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_log (
    log_id SERIAL PRIMARY KEY,
    property_id VARCHAR(255) NOT NULL REFERENCES properties(id),
    field_name VARCHAR(255) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    change_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(255),
    change_source VARCHAR(50) -- e.g., 'autofill', 'manual', 'system'
);
"""

def create_properties_table():
    conn = None
    try:
        # Get database connection parameters from environment
        db_name = os.environ.get('REI_DB_NAME')
        db_user = os.environ.get('REI_DB_USER')
        db_password = os.environ.get('REI_DB_PASSWORD')
        db_host = os.environ.get('REI_DB_HOST')
        db_port = os.environ.get('REI_DB_PORT')
        
        # Validate we have all required parameters
        if not all([db_name, db_user, db_password, db_host, db_port]):
            logger.error("Missing required database connection parameters")
            return
            
        conn = get_db_connection(db_name, db_user, db_password, db_host, db_port)
        cur = conn.cursor()
        logger.info("Conexión a la base de datos exitosa.")

        logger.info("Ejecutando sentencia CREATE TABLE...")
        cur.execute(create_table_sql)
        conn.commit()
        logger.info("Tabla 'properties' y 'audit_log' creadas o ya existentes en la base de datos.")

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
