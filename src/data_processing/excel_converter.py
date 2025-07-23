import win32com.client as win32
import pythoncom
import logging

logger = logging.getLogger(__name__)

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
