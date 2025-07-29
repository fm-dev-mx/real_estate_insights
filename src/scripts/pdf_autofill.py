import logging
import os
from src.utils.constants import PDF_DOWNLOAD_BASE_DIR

from src.utils.logging_config import setup_logging

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

setup_logging(log_file_prefix="pdf_autofill_log")
logger = logging.getLogger(__name__)

def _extract_data_from_pdf_placeholder(pdf_path: str, missing_columns: list) -> dict:
    """
    Internal placeholder for data extraction from a PDF.
    This should be replaced with actual OCR/regex logic.
    In its current state, it returns no data, forcing mocks in tests.
    """
    # NOTE: This is a placeholder. The actual implementation will involve
    # using a library like PyMuPDF to extract and parse text.
    # Returning an empty dict makes the placeholder inert, which is better for testing,
    # as it forces tests to mock this function's return value explicitly.
    logger.info("Using placeholder for PDF data extraction. No real data will be extracted.")
    return {}

def autofill_from_pdf(property_id: str, missing_columns: list) -> dict:
    """
    Attempts to autofill specific missing data for a given property_id from its PDF.

    Args:
        property_id (str): The ID of the property.
        missing_columns (list): A list of column names that are missing for this property.

    Returns:
        dict: A dictionary where keys are column names and values are the autofilled data.
              Returns an empty dictionary if no data could be autofilled.
    """
    logger.info(f"[PDF_AUTOFILL] Iniciando auto-llenado para propiedad {property_id} y columnas: {missing_columns}")

    pdf_local_path = os.path.join(BASE_DIR, PDF_DOWNLOAD_BASE_DIR, f"{property_id}.pdf")

    if not os.path.exists(pdf_local_path):
        logger.warning(f"[PDF_AUTOFILL] PDF no encontrado para la propiedad {property_id} en {pdf_local_path}. No se puede auto-llenar.")
        return {}

    try:
        autofilled_data = _extract_data_from_pdf_placeholder(pdf_local_path, missing_columns)
        if autofilled_data:
            logger.info(f"[PDF_AUTOFILL] Proceso de auto-llenado completado para {property_id}. Datos encontrados: {autofilled_data}")
        else:
            logger.info(f"[PDF_AUTOFILL] Proceso de auto-llenado completado para {property_id}. No se encontraron datos para las columnas solicitadas.")
        return autofilled_data
    except Exception as e:
        # Catching generic Exception to make the function resilient.
        # It logs the full error but returns {} to avoid crashing the calling process.
        logger.error(f"[PDF_AUTOFILL] Error irrecuperable durante el proceso de auto-llenado para {property_id}: {e}", exc_info=True)
        return {}

if __name__ == "__main__":
    # Example usage for testing in isolation
    test_property_id = "574358" # Replace with an actual ID from your DB/PDFs
    test_missing_columns = ['precio', 'm2_construccion', 'descripcion']

    # Ensure a dummy PDF exists for testing purposes
    dummy_pdf_path = os.path.join(BASE_DIR, PDF_DOWNLOAD_BASE_DIR, f"{test_property_id}.pdf")
    if not os.path.exists(dummy_pdf_path):
        logger.warning(f"Dummy PDF not found at {dummy_pdf_path}. Creating a placeholder file for testing.")
        # Create a dummy empty file if it doesn't exist for the script to run without error
        os.makedirs(os.path.dirname(dummy_pdf_path), exist_ok=True)
        with open(dummy_pdf_path, 'w') as f:
            f.write("dummy pdf content")

    autofilled_results = autofill_from_pdf(test_property_id, test_missing_columns)
    logger.info(f"Autofilled Results for {test_property_id}: {autofilled_results}")
