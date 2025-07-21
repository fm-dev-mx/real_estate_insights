import pandas as pd
import os
import win32com.client as win32
import pythoncom
import logging
from datetime import datetime

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'src', 'data_collection', 'downloads')
LOG_DIR = os.path.join(BASE_DIR, 'src', 'data_collection', 'logs')

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
    try:
        logger.info(f"[CONVERSION] Iniciando conversión de {xls_path} a {xlsx_path}")
        pythoncom.CoInitialize() # Inicializa COM para este hilo
        logger.info("[CONVERSION] COM inicializado.")

        excel = win32.Dispatch("Excel.Application")
        excel.Visible = False  # No mostrar Excel
        excel.DisplayAlerts = False # Suprimir alertas de Excel
        logger.info("[CONVERSION] Instancia de Excel creada.")

        logger.info(f"[CONVERSION] Abriendo workbook: {xls_path}")
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
        pythoncom.CoUninitialize() # Desinicializa COM
        logger.info("[CONVERSION] COM desinicializado.")

def inspect_excel_data(file_path):
    """
    Lee un archivo Excel (.xls o .xlsx) y realiza una inspección básica de sus datos.
    """
    logger.info(f"[INSPECTION] Iniciando inspección de datos para: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"[INSPECTION] Error: El archivo {file_path} no existe.")
        return None

    try:
        df = pd.read_excel(file_path)
        logger.info(f"[INSPECTION] Datos cargados exitosamente desde: {file_path}")
        logger.info("--- Primeras 5 filas ---")
        logger.info(df.head())
        logger.info("--- Información general del DataFrame ---")
        df.info(buf=logger.info)
        logger.info("--- Estadísticas descriptivas ---")
        logger.info(df.describe(include='all'))
        logger.info("--- Conteo de valores nulos por columna ---")
        logger.info(df.isnull().sum())
        logger.info("[INSPECTION] Inspección de datos completada.")
        return df
    except Exception as e:
        logger.error(f"[INSPECTION] Error al leer el archivo Excel con pandas: {e}")
        return None

if __name__ == "__main__":
    logger.info("--- Script clean_data.py iniciado ---")
    
    # Asegúrate de que la ruta de descargas sea correcta
    # downloads_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\', 'data_collection\', 'downloads\')
    
    # Buscar archivos Excel, priorizando .xlsx
    excel_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.xlsx') or f.endswith('.xls')]
    
    if excel_files:
        target_file = None
        # Intentar encontrar un archivo .xlsx primero
        for f in excel_files:
            if f.endswith('.xlsx'):
                target_file = os.path.join(DOWNLOAD_DIR, f)
                logger.info(f"[MAIN] Encontrado archivo XLSX: {target_file}")
                break
        
        # Si no se encontró un .xlsx, buscar un .xls y convertirlo
        if not target_file:
            for f in excel_files:
                if f.endswith('.xls'):
                    xls_file_path = os.path.join(DOWNLOAD_DIR, f)
                    xlsx_file_name = os.path.splitext(os.path.basename(xls_file_path))[0] + '.xlsx'
                    xlsx_file_path = os.path.join(DOWNLOAD_DIR, xlsx_file_name)
                    logger.info(f"[MAIN] Encontrado archivo XLS: {xls_file_path}. Intentando convertir a {xlsx_file_path}...")
                    if convert_xls_to_xlsx(xls_file_path, xlsx_file_path):
                        target_file = xlsx_file_path
                        logger.info(f"[MAIN] Conversión exitosa. El archivo a analizar es: {target_file}")
                        # Opcional: eliminar el archivo .xls original después de la conversión exitosa
                        # try:
                        #     os.remove(xls_file_path)
                        #     logger.info(f"[MAIN] Archivo original .xls eliminado: {xls_file_path}")
                        # except Exception as e:
                        #     logger.warning(f"[MAIN] No se pudo eliminar el archivo .xls original: {e}")
                    else:
                        logger.error(f"[MAIN] Falló la conversión de {xls_file_path}. No se puede proceder con el análisis.")
                    break # Solo procesar el primer XLS encontrado
        
        if target_file:
            inspect_excel_data(target_file)
        else:
            logger.error(f"[MAIN] No se encontraron archivos Excel válidos en {DOWNLOAD_DIR} para analizar después de intentar la conversión.")
    else:
        logger.warning(f"[MAIN] No se encontraron archivos Excel (.xls o .xlsx) en {DOWNLOAD_DIR}.")
        logger.info("[MAIN] Por favor, asegúrate de que el script de descarga haya generado uno o coloca uno manualmente.")

    logger.info("--- Script clean_data.py finalizado ---")