import pytest
import os
from unittest.mock import patch
from src.scripts.pdf_autofill import autofill_from_pdf

# Fix: Remove unnecessary src prefix in tests
# Now we can directly use autofill_from_pdf since we imported it directly

# Fix all test cases to use direct function call


# Fixture para crear un PDF dummy para pruebas
@pytest.fixture
def dummy_pdf_file(tmp_path):
    pdf_dir = tmp_path / "data" / "pdfs"
    os.makedirs(pdf_dir, exist_ok=True)
    dummy_id = "test_prop_123"
    pdf_path = pdf_dir / f"{dummy_id}.pdf"

    with open(pdf_path, "w") as f:
        f.write("This is a dummy PDF content.")

    with patch('src.scripts.pdf_autofill.PDF_DOWNLOAD_BASE_DIR', str(pdf_dir)):
        yield dummy_id, str(pdf_path)

# Alias for the function to fix tests
autofill_from_pdf = autofill_from_pdf

# Test para auto-llenado exitoso
@patch('src.scripts.pdf_autofill._extract_data_from_pdf_placeholder')
def test_pdf_autofill_success(mock_extract, dummy_pdf_file):
    property_id, pdf_path = dummy_pdf_file
    missing_columns = ['precio', 'm2_construccion']
    mock_extract.return_value = {
        'precio': 1234567.0,
        'm2_construccion': 250.0
    }

    with patch('src.scripts.pdf_autofill.logger') as mock_logger:
        autofilled_data = autofill_from_pdf(property_id, missing_columns)

        assert 'precio' in autofilled_data
        assert autofilled_data['precio'] == 1234567.0
        assert 'm2_construccion' in autofilled_data
        assert autofilled_data['m2_construccion'] == 250.0
        mock_logger.info.assert_called()

# Test para cuando no se encuentra el PDF
def test_pdf_autofill_no_pdf():
    property_id = "non_existent_prop"
    missing_columns = ['precio']

    with patch('src.scripts.pdf_autofill.PDF_DOWNLOAD_BASE_DIR', '/tmp/non_existent_dir'):
        with patch('src.scripts.pdf_autofill.logger') as mock_logger:
            autofilled_data = autofill_from_pdf(property_id, missing_columns)
            assert autofilled_data == {}
            # Check for substring instead of exact path to handle platform differences
            mock_logger.warning.assert_called_once()
            args, _ = mock_logger.warning.call_args
            assert f"[PDF_AUTOFILL] PDF no encontrado para la propiedad {property_id}" in args[0]

# Test para cuando no hay coincidencia de datos en el PDF (simulado)
@patch('src.scripts.pdf_autofill._extract_data_from_pdf_placeholder')
def test_pdf_autofill_no_match(mock_extract, dummy_pdf_file):
    property_id, pdf_path = dummy_pdf_file
    missing_columns = ['precio', 'm2_terreno']
    mock_extract.return_value = {}

    with patch('src.scripts.pdf_autofill.logger') as mock_logger:
        autofilled_data = autofill_from_pdf(property_id, missing_columns)
        assert autofilled_data == {}
        mock_logger.info.assert_called()

# Test para manejo de errores de OCR (simulado)
@patch('src.scripts.pdf_autofill._extract_data_from_pdf_placeholder')
def test_ocr_error_handling(mock_extract, dummy_pdf_file):
    property_id, pdf_path = dummy_pdf_file
    missing_columns = ['precio']
    mock_extract.side_effect = ValueError("Simulated OCR error")

    with patch('src.scripts.pdf_autofill.logger') as mock_logger:
        with pytest.raises(ValueError, match="Simulated OCR error"):
            autofill_from_pdf(property_id, missing_columns)
        mock_logger.error.assert_called()
