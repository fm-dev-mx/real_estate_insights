import pandas as pd
import numpy as np
from src.data_processing.data_cleaner import clean_and_transform_data

def create_test_excel(tmp_path, data):
    """Helper function to create an Excel file for testing."""
    test_excel_path = tmp_path / "test_data.xlsx"
    df_input = pd.DataFrame(data)
    # Asegurar que todas las columnas esperadas por el cleaner existan, llenando con NaN si no están en `data`
    base_columns = {
        'fechaAlta': None, 'tipoOperacion': None, 'tipoDeContrato': None, 'enInternet': None,
        'claveOficina': None, 'subtipoPropiedad': None, 'codigoPostal': None,
        'comisionACompartirInmobiliariasExternas': None, 'm2C': None, 'm2T': None,
        'mediosbanos': None, 'nivelesConstruidos': None, 'apellidoP': None, 'apellidoM': None,
        'nombre': None, 'id': None, 'precio': None, 'comision': None, 'recamaras': None,
        'banos': None, 'edad': None, 'estacionamientos': None, 'descripcion': None,
        'latitud': None, 'longitud': None, 'cocina': None, 'numero': None
    }
    for col, default_val in base_columns.items():
        if col not in df_input.columns:
            df_input[col] = default_val

    df_input.to_excel(test_excel_path, index=False)
    return test_excel_path

def test_clean_and_transform_data(tmp_path):
    # Arrange
    data = {
        'id': [1, 2, 3],
        'fechaAlta': ['2024-01-01', '2024-02-01', '2024-03-01'],
        'enInternet': ['Si', 'No', 'Si'],
        'm2C': [100.5, 50.0, 0.0],
        'm2T': [200.5, 70.0, 300.0],
        'recamaras': [3, 2, 0],
        'edad': [10, 5, 0],
        'cocina': ['Si', 'No', 'Si'],
        'banos': [2, 1, 0],
        'mediosbanos': [1, 0, 1]
    }
    test_excel_path = create_test_excel(tmp_path, data)

    # Act
    cleaned_df = clean_and_transform_data(test_excel_path)

    # Assert
    assert cleaned_df is not None
    assert not cleaned_df.empty
    assert 'banos_totales' in cleaned_df.columns
    assert 'banos' not in cleaned_df.columns
    assert 'medios_banos' not in cleaned_df.columns

    expected_banos_totales = pd.Series([2.5, 1.0, 0.5], name='banos_totales')
    pd.testing.assert_series_equal(cleaned_df['banos_totales'], expected_banos_totales, check_names=False)

def test_banos_totales_with_nans(tmp_path):
    # Arrange
    data = {
        'id': [1, 2, 3, 4],
        'banos': [2, np.nan, 3, np.nan],
        'mediosbanos': [1, 1, np.nan, np.nan]
    }
    test_excel_path = create_test_excel(tmp_path, data)

    # Act
    cleaned_df = clean_and_transform_data(test_excel_path)

    # Assert
    assert 'banos_totales' in cleaned_df.columns
    expected_banos_totales = pd.Series([2.5, 0.5, 3.0, 0.0], name='banos_totales')
    pd.testing.assert_series_equal(cleaned_df['banos_totales'], expected_banos_totales, check_names=False)

def test_banos_totales_with_non_numeric(tmp_path):
    # Arrange
    data = {
        'id': [1, 2, 3],
        'banos': [2, 'uno', ' '],
        'mediosbanos': ['1', 0, '1.5']
    }
    test_excel_path = create_test_excel(tmp_path, data)

    # Act
    cleaned_df = clean_and_transform_data(test_excel_path)

    # Assert
    assert 'banos_totales' in cleaned_df.columns
    expected_banos_totales = pd.Series([2.5, 0.0, 0.75], name='banos_totales')
    pd.testing.assert_series_equal(cleaned_df['banos_totales'], expected_banos_totales, check_names=False)

def test_clean_and_transform_data_file_not_found():
    # Arrange
    non_existent_path = "/path/to/non_existent_file.xlsx"

    # Act
    cleaned_df = clean_and_transform_data(non_existent_path)

    # Assert
    assert cleaned_df is None
