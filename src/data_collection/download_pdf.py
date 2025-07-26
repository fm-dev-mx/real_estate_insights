import os
import logging
import requests

from src.utils.logging_config import setup_logging
from src.utils.constants import PDF_BASE_URL, PDF_SUFFIX, PDF_DOWNLOAD_BASE_DIR

setup_logging(log_file_prefix="download_pdf_log")
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
# Asegurarse de que el directorio base de descarga de PDFs exista
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FULL_PDF_DOWNLOAD_DIR = os.path.join(BASE_DIR, PDF_DOWNLOAD_BASE_DIR)
os.makedirs(FULL_PDF_DOWNLOAD_DIR, exist_ok=True)

def download_property_pdf(property_id: str) -> str or None:
    """
    Descarga el PDF de una propiedad dado su ID utilizando requests.
    Guarda el PDF en data/pdfs/[property_id].pdf.

    Args:
        property_id (str): El ID de la propiedad.

    Returns:
        str: La ruta absoluta al PDF descargado si la descarga fue exitosa, None en caso contrario.
    """
    logger.info(f"[PDF_DOWNLOAD] Iniciando descarga para property_id: {property_id}")
    pdf_url = f"{PDF_BASE_URL}{property_id}{PDF_SUFFIX}"
    logger.info(f"[PDF_DOWNLOAD] URL del PDF construida: {pdf_url}")
    pdf_local_path = os.path.join(BASE_DIR, PDF_DOWNLOAD_BASE_DIR, f"{property_id}.pdf")

    if os.path.exists(pdf_local_path):
        logger.info(f"[PDF_DOWNLOAD] PDF para la propiedad {property_id} ya existe en {pdf_local_path}. Saltando descarga.")
        return os.path.join(PDF_DOWNLOAD_BASE_DIR, f"{property_id}.pdf")

    try:
        logger.info(f"[PDF_DOWNLOAD] Intentando descargar PDF desde: {pdf_url}")
        response = requests.get(pdf_url, stream=True) # Usar stream para manejar archivos grandes
        response.raise_for_status() # Lanza una excepción para códigos de estado HTTP erróneos

        with open(pdf_local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"[PDF_DOWNLOAD] PDF de la propiedad {property_id} descargado exitosamente en {pdf_local_path}.")
        return os.path.join(PDF_DOWNLOAD_BASE_DIR, f"{property_id}.pdf")

    except requests.exceptions.RequestException as e:
        logger.error(f"[PDF_DOWNLOAD] Error de red o HTTP al descargar PDF para {property_id}. Error: {e}")
        return None
    except Exception as e:
        logger.error(f"[PDF_DOWNLOAD] Error inesperado al descargar PDF para {property_id}. Tipo: {type(e).__name__}, Mensaje: {e}")
        return None