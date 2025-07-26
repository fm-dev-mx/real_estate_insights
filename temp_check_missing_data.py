import os
import psycopg2
import logging

# Configuración de logging (para este script temporal)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Credenciales de la base de datos (se asume que están en variables de entorno)
DB_NAME = os.environ.get('REI_DB_NAME', 'real_estate_db')
DB_USER = os.environ.get('REI_DB_USER', 'fm_asesor')
DB_PASSWORD = os.environ.get('REI_DB_PASSWORD')
DB_HOST = os.environ.get('REI_DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('REI_DB_PORT', '5432')

# Campos críticos (copia de data_validator.py para este análisis)
CRITICAL_COLUMNS = [
    'id', 'precio', 'm2_construccion', 'm2_terreno', 'recamaras', 'banos_totales',
    'descripcion', 'status', 'tipo_operacion', 'tipo_contrato', 'colonia',
    'municipio', 'latitud', 'longitud'
]

def check_missing_critical_data():
    conn = None
    missing_report = []
    total_properties = 0

    if not DB_PASSWORD:
        logger.error("DB_PASSWORD environment variable not set. Cannot connect to database.")
        return

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        logger.info("Successfully connected to the database.")

        # Get total number of properties
        cur.execute("SELECT COUNT(*) FROM properties;")
        total_properties = cur.fetchone()[0]
        logger.info(f"Total properties in DB: {total_properties}")

        if total_properties == 0:
            logger.info("No properties found in the database. No missing data to check.")
            return

        for col in CRITICAL_COLUMNS:
            # Check for NULLs
            query_null = f"SELECT id FROM properties WHERE {col} IS NULL;"
            cur.execute(query_null)
            null_ids = [row[0] for row in cur.fetchall()]

            # Check for empty strings (only for text/varchar columns)
            empty_string_ids = []
            # Determine if column is text type (simplified check, could be more robust)
            cur.execute(f"SELECT data_type FROM information_schema.columns WHERE table_name = 'properties' AND column_name = '{col}';")
            col_type = cur.fetchone()
            if col_type and ('char' in col_type[0] or 'text' in col_type[0]):
                query_empty = f"SELECT id FROM properties WHERE {col} = '';"
                cur.execute(query_empty)
                empty_string_ids = [row[0] for row in cur.fetchall()]
            
            all_missing_ids = list(set(null_ids + empty_string_ids))
            
            if all_missing_ids:
                missing_report.append({
                    'column': col,
                    'missing_count': len(all_missing_ids),
                    'property_ids': all_missing_ids
                })
                logger.warning(f"Column '{col}' has {len(all_missing_ids)} missing values.")
            else:
                logger.info(f"Column '{col}' has no missing values.")

    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")

    # Generate final report
    if not missing_report:
        print("\n--- Validation Report ---")
        print("✅ All critical columns are complete in all properties.")
        print(f"Total properties checked: {total_properties}")
    else:
        print("\n--- Validation Report ---")
        print(f"Total properties checked: {total_properties}")
        print("❌ Missing critical data found in the following columns:")
        for item in missing_report:
            print(f"- Column: {item['column']}")
            print(f"  Missing Count: {item['missing_count']}")
            print(f"  Property IDs: {item['property_ids']}")
            print("-" * 30)

if __name__ == "__main__":
    check_missing_critical_data()
