import os
import pytest
import requests
from src.data_collection.download_pdf import download_property_pdf
from src.utils.constants import PDF_BASE_URL, PDF_SUFFIX, PDF_DOWNLOAD_BASE_DIR

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

@pytest.fixture
def mock_requests_get(monkeypatch):
    """Fixture to mock requests.get."""
    def mock_get(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass
            def iter_content(self, chunk_size=1):
                return [b'pdf-content-chunk-1', b'pdf-content-chunk-2']
        return MockResponse()
    monkeypatch.setattr(requests, "get", mock_get)

@pytest.fixture
def mock_os_path_exists(monkeypatch):
    """Fixture to mock os.path.exists."""
    monkeypatch.setattr(os.path, "exists", lambda x: False)

@pytest.fixture
def mock_open(monkeypatch):
    """Fixture to mock the built-in open function."""
    class MockFile:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def write(self, data):
            pass
    monkeypatch.setattr("builtins.open", lambda x, y: MockFile())

def test_download_property_pdf_success(mock_requests_get, mock_os_path_exists, mock_open):
    """
    Tests successful download of a PDF when the file does not exist locally.
    """
    # Arrange
    property_id = "12345"
    expected_url = f"{PDF_BASE_URL}{property_id}{PDF_SUFFIX}"
    expected_path = os.path.join(PDF_DOWNLOAD_BASE_DIR, f"{property_id}.pdf")

    # Act
    result_path = download_property_pdf(property_id)

    # Assert
    assert result_path == expected_path

def test_download_property_pdf_already_exists(monkeypatch):
    """
    Tests that the download is skipped if the PDF file already exists.
    """
    # Arrange
    property_id = "67890"
    expected_path = os.path.join(PDF_DOWNLOAD_BASE_DIR, f"{property_id}.pdf")
    monkeypatch.setattr(os.path, "exists", lambda x: True)

    # Act
    result_path = download_property_pdf(property_id)

    # Assert
    assert result_path == expected_path

def test_download_property_pdf_http_error(monkeypatch, caplog):
    """
    Tests the handling of an HTTP error (e.g., 404 Not Found) during download.
    """
    # Arrange
    property_id = "failed-id"
    monkeypatch.setattr(os.path, "exists", lambda x: False)
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: (_ for _ in ()).throw(requests.exceptions.RequestException("HTTP 404 Error")))

    # Act
    result = download_property_pdf(property_id)

    # Assert
    assert result is None
    assert "Error de red o HTTP al descargar PDF" in caplog.text
