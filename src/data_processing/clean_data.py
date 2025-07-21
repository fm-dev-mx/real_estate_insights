Este script ETL (Extract, Transform, Load) se encarga de procesar archivos de inventario de bienes raíces,
limpiar y transformar los datos, y cargarlos en una base de datos PostgreSQL.

Funcionalidades principales:
- Búsqueda y conversión automática de archivos .xls a .xlsx.
- Conexión segura a la base de datos usando variables de entorno.
- Limpieza y normalización de datos (renombrado de columnas, conversión de tipos, etc.).
- Carga de datos en la base de datos con manejo de conflictos (actualización de registros existentes).
- Registro detallado de operaciones y errores en un archivo de log.

Uso:
1.  Asegurarse de que las variables de entorno de la base de datos (REI_DB_*) estén configuradas.
2.  Colocar el archivo de inventario (.xls o .xlsx) en el directorio 'src/data_collection/downloads'.
3.  Ejecutar el script desde el directorio 'src/data_processing': `py clean_data.py`
"""

import io
import pandas as pd
import os
import win32com.client as win32
import pythoncom
import logging
from datetime import datetime
import psycopg2
from psycopg2 import extras

# --- CONSTANTS ---
DB_COLUMNS = [
    'id', 'fecha_alta', 'status', 'tipo_operacion', 'tipo_contrato', 'en_internet',
    'clave', 'clave_oficina', 'subtipo_propiedad', 'calle', 'numero',
    'colonia', 'municipio', 'latitud', 'longitud', 'codigo_postal',
    'precio', 'comision', 'comision_compartir_externas', 'm2_construccion',
    'm2_terreno', 'recamaras', 'banios', 'medios_banios', 'cocina',
    'niveles_construidos', 'edad', 'estacionamientos', 'descripcion',
    'nombre_agente', 'apellido_paterno_agente', 'apellido_materno_agente'
]

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



def convert_xls_to_xlsx(xls_path, xlsx_path):
    """
    Convierte un archivo .xls a .xlsx usando pywin32 y Microsoft Excel.
    Requiere que Microsoft Excel esté instalado en el sistema.
    """
    excel = None
    workbook = None
    com_initialized = False
    try:
        logger.info(f"[CONVERSION] Iniciando conversión de {xls_path} a {xlsx_path}")
        pythoncom.CoInitialize() # Inicializa COM para este hilo
        com_initialized = True
        logger.info("[CONVERSION] COM inicializado.")

        excel = win32.Dispatch("Excel.Application")
        excel.Visible = False  # No mostrar Excel
        excel.DisplayAlerts = False # Suprimir alertas de Excel
        logger.info("[CONVERSION] Instancia de Excel creada.")

        logger.info("[CONVERSION] Abriendo workbook: {xls_path}")
        workbook = excel.Workbooks.Open(xls_path)
        logger.info("[CONVERSION] Workbook abierto. Guardando como XLSX...")
        workbook.SaveAs(xlsx_path, FileFormat=51)  # FileFormat=51 para .xlsx
        logger.info(f"[CONVERSION] Workbook guardado como {xlsx_path}.")
        return True
    except Exception as e:
        logger.error(f"[CONVERSION] Error al convertir el archivo XLS a XLSX: {e}")
        return False
    finally:
        if workbook:
            try:
                workbook.Close(SaveChanges=False) # Cerrar sin guardar cambios adicionales
                logger.info("[CONVERSION] Workbook cerrado.")
            except Exception as e: # Capturar cualquier error al cerrar
                logger.error(f"[CONVERSION] Error al cerrar el workbook: {e}")
        if excel:
            try:
                excel.Quit()
                logger.info("[CONVERSION] Excel.Application cerrado.")
            except Exception as e: # Capturar cualquier error al salir de Excel
                logger.error(f"[CONVERSION] Error al salir de Excel.Application: {e}")
        if com_initialized:
            pythoncom.CoUninitialize() # Desinicializa COM
            logger.info("[CONVERSION] COM desinicializado.")

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
            'nombre': 'nombre_agente' # Renombrar para consistencia con apellidos
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
        
        # Para baños, que es DECIMAL(4,2), se mantiene como float y se manejará la precisión al insertar en DB
        for col in ['precio', 'comision', 'comision_compartir_externas', 'm2_construccion', 'm2_terreno', 'latitud', 'longitud', 'banios', 'medios_banios']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce') # Convertir a numérico, nulos si hay error

        logger.info("[CLEANING] Columnas numéricas procesadas.")

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

def load_data_to_postgresql(df, db_name, db_user, db_host, db_port, db_password):
    """
    Carga un DataFrame de pandas a la tabla 'properties' en PostgreSQL.
    Utiliza INSERT ... ON CONFLICT (id) DO UPDATE para manejar duplicados.
    """
    logger.info("[LOAD] Iniciando carga de datos a PostgreSQL.")
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
        logger.info("[LOAD] Conexión a la base de datos PostgreSQL exitosa.")

        # Asegurarse de que los nombres de las columnas del DataFrame coincidan con los de la DB
        # y estén en el orden correcto para la inserción.
        # Las columnas created_at y updated_at se manejan automáticamente por la DB.
        columns = DB_COLUMNS

        # Convertir DataFrame a lista de tuplas, manejando los tipos de datos para PostgreSQL
        # Convertir Int64 (pandas nullable integer) a int o None para psycopg2
        # Convertir bool a True/False
        data_to_insert = []
        for index, row in df[columns].iterrows():
            # Manejar Int64 (pandas nullable integer) a int o None
            processed_row = []
            for col_name in columns:
                value = row[col_name]
                if pd.isna(value):
                    processed_row.append(None)
                elif isinstance(value, pd.Int64Dtype.type):
                    processed_row.append(int(value))
                elif isinstance(value, bool):
                    processed_row.append(bool(value))
                else:
                    processed_row.append(value)
            data_to_insert.append(tuple(processed_row))

        # Construir la sentencia SQL de inserción/actualización
        # Usamos ON CONFLICT (id) DO UPDATE para actualizar registros existentes
        # y SET para especificar qué columnas actualizar.
        # Excluimos 'id', 'fecha_alta', 'created_at' de la actualización si ya existen.
        update_columns = [col for col in columns if col not in ['id', 'fecha_alta']]
        update_set_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])
        update_set_clause += ", updated_at = CURRENT_TIMESTAMP"

        insert_sql = f"""
        INSERT INTO properties ({', '.join(columns)})
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET
            {update_set_clause}
        """

        logger.info(f"[LOAD] Insertando/actualizando {len(data_to_insert)} registros en la tabla 'properties'.")
        extras.execute_values(cur, insert_sql, data_to_insert, page_size=1000)
        conn.commit()
        logger.info(f"[LOAD] Carga de datos a PostgreSQL completada exitosamente. {len(data_to_insert)} registros procesados.")

    except psycopg2.Error as e:
        logger.error(f"[LOAD] Error al cargar datos a PostgreSQL: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        logger.error(f"[LOAD] Un error inesperado ocurrió durante la carga de datos: {e}")
    finally:
        if conn:
            conn.close()
            logger.info("[LOAD] Conexión a la base de datos cerrada.")

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

def main():    logger.info("--- Script clean_data.py iniciado ---")    # --- Verificación inicial de la conexión a la base de datos ---    logger.info("[MAIN] Realizando verificación inicial de la conexión a la base de datos...")    conn_check = None    try:        if not DB_PASSWORD:            raise ValueError("La variable de entorno REI_DB_PASSWORD no está configurada.")                conn_check = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )        logger.info("[MAIN] Verificación de conexión a la base de datos exitosa.")        conn_check.close()    except (psycopg2.Error, ValueError) as e:        logger.error(f"[MAIN] No se pudo establecer conexión con la base de datos: {e}")        logger.error("[MAIN] El script no continuará. Por favor, verifique la configuración de la base de datos y las variables de entorno.")        return # Salir del script si la conexión falla

    target_file = find_target_excel_file(DOWNLOAD_DIR)    
    if target_file:        cleaned_df = clean_and_transform_data(target_file)        if cleaned_df is not None:            logger.info("\n--- Primeras 5 filas del DataFrame limpio ---")            logger.info(cleaned_df.head().to_string())            logger.info("\n--- Información general del DataFrame limpio ---")            buffer = io.StringIO()            cleaned_df.info(buf=buffer)            logger.info(buffer.getvalue())            logger.info("\n--- Conteo de valores nulos del DataFrame limpio ---")            logger.info(cleaned_df.isnull().sum().to_string())            # --- Cargar datos a PostgreSQL ---            load_data_to_postgresql(cleaned_df, DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD)        else:            logger.error("[MAIN] No se pudo obtener un DataFrame limpio.")    else:        logger.info("[MAIN] No se encontró un archivo Excel para procesar.")

    logger.info("--- Script clean_data.py finalizado ---")

if __name__ == "__main__":
    main()
