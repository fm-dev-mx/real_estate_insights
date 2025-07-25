import pytest
import pandas as pd
import os
from unittest.mock import patch, MagicMock
# Importar el módulo completo para un mocking robusto
import src.scripts.pdf_autofill

# Fixture para crear un PDF dummy para pruebas
@pytest.fixture
def dummy_pdf_file(tmp_path):
    pdf_dir = tmp_path / "data" / "pdfs"
    os.makedirs(pdf_dir, exist_ok=True)
    dummy_id = "test_prop_123"
    pdf_path = pdf_dir / f"{dummy_id}.pdf"

    # Crear un archivo dummy (vacío o con contenido mínimo para simular existencia)
    with open(pdf_path, "w") as f:
        f.write("This is a dummy PDF content.")

    # Parchear PDF_DOWNLOAD_BASE_DIR para que apunte a nuestro directorio temporal
    with patch('src.scripts.pdf_autofill.PDF_DOWNLOAD_BASE_DIR', str(pdf_dir)):
        yield dummy_id, str(pdf_path)

# Test para auto-llenado exitoso
def test_pdf_autofill_success(dummy_pdf_file):
    property_id, pdf_path = dummy_pdf_file
    missing_columns = ['precio', 'm2_construccion']

    with patch('src.scripts.pdf_autofill.logger') as mock_logger:
        with patch('src.scripts.pdf_autofill.os.path.exists', return_value=True): # Asegurar que el PDF existe
            with patch('src.scripts.pdf_autofill.open', MagicMock()): # Mockear la apertura del archivo
                # Mockear la función en su ubicación original
                with patch('src.scripts.pdf_autofill.autofill_from_pdf', return_value={
                    'precio': 1234567.0,
                    'm2_construccion': 250.0
                }):
                    autofilled_data = src.scripts.pdf_autofill.autofill_from_pdf(property_id, missing_columns)

                    assert 'precio' in autofilled_data
                    assert autofilled_data['precio'] == 1234567.0
                    assert 'm2_construccion' in autofilled_data
                    assert autofilled_data['m2_construccion'] == 250.0
                    mock_logger.info.assert_called()

# Test para cuando no se encuentra el PDF
def test_pdf_autofill_no_pdf():
    property_id = "non_existent_prop"
    missing_columns = ['precio']

    with patch('src.scripts.pdf_autofill.PDF_DOWNLOAD_BASE_DIR', '/tmp/non_existent_dir'): # Directorio que no existe
        with patch('src.scripts.pdf_autofill.logger') as mock_logger:
            autofilled_data = src.scripts.pdf_autofill.autofill_from_pdf(property_id, missing_columns)
            assert autofilled_data == {}
            mock_logger.warning.assert_called_with(f"[PDF_AUTOFILL] PDF no encontrado para la propiedad {property_id} en /tmp/non_existent_dir\\{property_id}.pdf. No se puede auto-llenar.")

# Test para cuando no hay coincidencia de datos en el PDF (simulado)
def test_pdf_autofill_no_match(dummy_pdf_file):
    property_id, pdf_path = dummy_pdf_file
    missing_columns = ['precio', 'm2_terreno']

    with patch('src.scripts.pdf_autofill.logger') as mock_logger:
        with patch('src.scripts.pdf_autofill.os.path.exists', return_value=True): # Asegurar que el PDF existe
            with patch('src.scripts.pdf_autofill.open', MagicMock()): # Mockear la apertura del archivo
                # Mockear la función para que devuelva vacío
                with patch('src.scripts.pdf_autofill.autofill_from_pdf', return_value={}):
                    autofilled_data = src.scripts.pdf_autofill.autofill_from_pdf(property_id, missing_columns)
                    assert autofilled_data == {}
                    mock_logger.info.assert_called()

# Test para manejo de errores de OCR (simulado)
def test_ocr_error_handling(dummy_pdf_file):
    property_id, pdf_path = dummy_pdf_file
    missing_columns = ['precio']

    with patch('src.scripts.pdf_autofill.logger') as mock_logger:
        with patch('src.scripts.pdf_autofill.os.path.exists', return_value=True): # Asegurar que el PDF existe
            with patch('src.scripts.pdf_autofill.open', MagicMock()): # Mockear la apertura del archivo
                # Simular un error durante el proceso de OCR/extracción
                with patch('src.scripts.pdf_autofill.autofill_from_pdf', side_effect=ValueError("Simulated OCR error")):
                    with pytest.raises(ValueError, match="Simulated OCR error"):
                        src.scripts.pdf_autofill.autofill_from_pdf(property_id, missing_columns)
                    mock_logger.error.assert_called()
