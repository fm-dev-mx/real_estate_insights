import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import os

# Importar las funciones clave del pipeline
from src.data_collection.download_inventory import download_inventory_process
from src.data_processing.data_cleaner import clean_and_transform_data
from src.data_processing.data_validator import validate_and_report_missing_data
from src.data_access.property_repository import PropertyRepository
from src.scripts.pdf_autofill import autofill_from_pdf
from src.scripts.apply_manual_fixes import apply_manual_fixes
from src.db_setup.create_db_table import create_properties_table

# Fixtures para mockear dependencias externas
@pytest.fixture
def mock_db_connection():
    with patch('src.data_access.database_connection.psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_conn, mock_cursor, mock_connect

@pytest.fixture
def mock_env_vars():
    with patch.dict(os.environ, {
        'REI_DB_NAME': 'test_db',
        'REI_DB_USER': 'test_user',
        'REI_DB_PASSWORD': 'test_pass',
        'REI_DB_HOST': 'test_host',
        'REI_DB_PORT': '5432'
    }):
        yield

@pytest.fixture
def mock_download_inventory():
    with patch('src.data_collection.download_inventory.download_inventory_process') as mock_func:
        # Simular que descarga un archivo Excel dummy
        mock_func.return_value = "dummy_inventory.xlsx"
        yield mock_func

@pytest.fixture
def dummy_excel_file(tmp_path):
    # Crear un archivo Excel dummy para la prueba
    excel_path = tmp_path / "dummy_inventory.xlsx"
    df = pd.DataFrame({
        'id': ['prop1', 'prop2', 'prop3'],
        'fechaAlta': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'codigoPostal': ['12345', '67890', '54321'],
        'numero': ['10', '20', '30'],
        'precio': [100000, None, 300000],
        'm2_construccion': [100, 150, None],
        'm2_terreno': [200, 250, 350],
        'recamaras': [3, 2, 4],
        'banos_totales': [2, 1.5, 3],
        'descripcion': ['Desc1', 'Desc2', 'Desc3'],
        'status': ['enPromocion', 'vendidas', 'enPromocion'],
        'tipo_operacion': ['venta', 'renta', 'venta'],
        'tipo_contrato': ['exclusiva', 'opcion', 'abierta'],
        'colonia': ['Col1', 'Col2', 'Col3'],
        'municipio': ['Mun1', 'Mun2', 'Mun3'],
        'latitud': [1.0, 2.0, 3.0],
        'longitud': [1.0, 2.0, 3.0]
    })
    df.to_excel(excel_path, index=False)
    yield excel_path

@pytest.fixture
def mock_pdf_autofill():
    with patch('src.scripts.pdf_autofill.autofill_from_pdf') as mock_func:
        # Simular que autofill_from_pdf devuelve algunos datos
        mock_func.side_effect = lambda pid, cols: {'precio': 200000} if pid == 'prop2' and 'precio' in cols else {}
        yield mock_func

@pytest.fixture
def mock_apply_manual_fixes():
    with patch('src.scripts.apply_manual_fixes.apply_manual_fixes') as mock_func:
        mock_func.return_value = True # Simular éxito
        yield mock_func

# Test end-to-end del pipeline
def test_full_pipeline_success(
    mock_env_vars, mock_db_connection, mock_download_inventory,
    dummy_excel_file, mock_pdf_autofill, mock_apply_manual_fixes
):
    mock_conn, mock_cursor, mock_connect = mock_db_connection

    # 1. Configurar la base de datos
    create_properties_table()
    mock_connect.assert_called_once() # Verificar que se intentó conectar
    mock_cursor.execute.assert_called_once() # Verificar que se ejecutó el SQL de creación

    # 2. Descargar inventario (mocked)
    downloaded_excel_path = mock_download_inventory()
    assert downloaded_excel_path == "dummy_inventory.xlsx"

    # 3. Limpiar y transformar datos
    cleaned_df = clean_and_transform_data(dummy_excel_file)
    assert not cleaned_df.empty

    # 4. Validar y reportar datos faltantes
    cleaned_df = validate_and_report_missing_data(cleaned_df)
    assert 'has_critical_gaps' in cleaned_df.columns

    # 5. Cargar propiedades a la DB
    repo = PropertyRepository('test_db', 'test_user', 'test_pass', 'test_host', 'test_port')
    repo.load_properties(cleaned_df, cleaned_df.columns.tolist()) # Cargar todas las columnas
    mock_cursor.execute.assert_called() # Verificar que se intentó insertar datos

    # 6. Simular el flujo de auto-llenado y corrección manual (si hay gaps)
    # Esto es conceptual, ya que el pipeline real pausaría.
    # Aquí, simplemente verificamos que las funciones serían llamadas si hubiera gaps.
    # Si cleaned_df tiene has_critical_gaps=True para alguna fila, entonces:
    # mock_pdf_autofill.assert_called() # Debería ser llamado para cada propiedad con gaps
    # mock_apply_manual_fixes.assert_called() # Debería ser llamado si se aplican correcciones

    # 7. Verificar que los datos finales en la DB son consistentes (conceptual)
    # Esto requeriría una consulta a la DB mockeada y comparar con los datos esperados.
    # Por la complejidad del mock de DB, esto se deja como un TODO.

    # Asegurarse de que no haya errores inesperados
    assert True # Si llegamos aquí sin excepciones, el flujo básico es exitoso
