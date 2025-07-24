import os
import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PDF_DOWNLOAD_BASE_DIR = os.path.join(BASE_DIR, 'data', 'pdfs')

# Asegurarse de que el directorio base de descarga de PDFs exista
os.makedirs(PDF_DOWNLOAD_BASE_DIR, exist_ok=True)

# URL base para la descarga de PDFs
PDF_BASE_URL = "https://plus.21onlinemx.com/ft/"
PDF_SUFFIX = "/DTF/273/40120"

# --- AUXILIARY FUNCTIONS (Copied from download_inventory.py) ---
def setup_webdriver(download_dir):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Run in headless mode (no GUI)
    options.add_argument('--start-maximized') # Start browser maximized
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Configure download preferences for Chrome
    prefs = {"download.default_directory" : download_dir,
             "download.prompt_for_download": False,
             "download.directory_upgrade": True,
             "plugins.always_open_pdf_externally": True # To prevent Chrome from opening PDFs in the browser
            }
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

def download_property_pdf(property_id: str) -> str or None:
    """
    Descarga el PDF de una propiedad dado su ID.
    Guarda el PDF en data/pdfs/[property_id].pdf.

    Args:
        property_id (str): El ID de la propiedad.

    Returns:
        str: La ruta absoluta al PDF descargado si la descarga fue exitosa, None en caso contrario.
    """
    pdf_url = f"{PDF_BASE_URL}{property_id}{PDF_SUFFIX}"
    pdf_local_path = os.path.join(PDF_DOWNLOAD_BASE_DIR, f"{property_id}.pdf")

    if os.path.exists(pdf_local_path):
        logger.info(f"[PDF] PDF para la propiedad {property_id} ya existe en {pdf_local_path}.")
        return pdf_local_path

    driver = None
    try:
        driver = setup_webdriver(PDF_DOWNLOAD_BASE_DIR)
        
        logger.info(f"[PDF] Intentando descargar PDF para la propiedad {property_id} desde {pdf_url}...")
        driver.get(pdf_url)

        # Esperar un tiempo prudencial para que la descarga se complete
        start_time = time.time()
        download_timeout = 60 # segundos
        while not os.path.exists(pdf_local_path) and (time.time() - start_time) < download_timeout:
            time.sleep(1) # Esperar 1 segundo antes de re-verificar
        
        if os.path.exists(pdf_local_path):
            logger.info(f"[PDF] PDF de la propiedad {property_id} descargado exitosamente en {pdf_local_path}.")
            return pdf_local_path
        else:
            logger.error(f"[PDF] Falló la descarga del PDF para la propiedad {property_id}. Archivo no encontrado después de {download_timeout}s.")
            return None

    except TimeoutException as e:
        logger.error(f"[PDF] Timeout al intentar descargar PDF para {property_id}: {e}")
        return None
    except WebDriverException as e:
        logger.error(f"[PDF] WebDriver error al descargar PDF para {property_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"[PDF] Error inesperado al descargar PDF para {property_id}: {e}")
        return None
    finally:
        if driver:
            driver.quit()