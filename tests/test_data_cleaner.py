import pandas as pd
import os
from src.data_processing.data_cleaner import clean_and_transform_data
from src.utils.constants import DB_COLUMNS # Import DB_COLUMNS

def test_clean_and_transform_data(tmp_path):
    # Arrange
    # Usar tmp_path para crear un archivo Excel temporal para la prueba
    test_excel_path = tmp_path / "test_data.xlsx"
    
    # Crear un DataFrame de pandas que simule los datos de entrada de un Excel
    data = {
        'fechaAlta': ['2024-01-01', '2024-02-01', '2024-03-01'],
        'tipoOperacion': ['Venta', 'Renta', 'Venta'],
        'tipoDeContrato': ['Exclusiva', 'Abierta', 'Exclusiva'],
        'enInternet': ['Si', 'No', 'Si'],
        'claveOficina': ['OF1', 'OF2', 'OF3'],
        'subtipoPropiedad': ['Casa', 'Departamento', 'Terreno'],
        'codigoPostal': [12345, 67890, 11223],
        'comisionACompartirInmobiliariasExternas': [1.5, 2.0, 0.0],
        'm2C': [100.5, 50.0, 0.0],
        'm2T': [200.5, 70.0, 300.0],
        'mediosBanios': [1, 0, 0],
        'nivelesConstruidos': [2, 1, 0],
        'apellidoP': ['Perez', 'Lopez', 'Garcia'],
        'apellidoM': ['Gomez', 'Ruiz', 'Diaz'],
        'nombre': ['Juan', 'Maria', 'Pedro'],
        'id': [1, 2, 3],
        'precio': [1000000, 500000, 2000000],
        'comision': [3.0, 2.0, 4.0],
        'recamaras': [3, 2, 0],
        'banios': [2.5, 1.0, 0.0],
        'edad': [10, 5, 0],
        'estacionamientos': [1, 0, 0],
        'descripcion': ['Casa con jardin', 'Departamento centrico', 'Terreno amplio'],
        'latitud': [19.0, 20.0, 21.0],
        'longitud': [-99.0, -100.0, -101.0],
        'cocina': ['Si', 'No', 'Si'],
        'numero': ['100', '200', '300'] # Added 'numero' column
    }
    df_input = pd.DataFrame(data)
    df_input.to_excel(test_excel_path, index=False) # Guardar como Excel

    # Act
    cleaned_df = clean_and_transform_data(test_excel_path)

    # Assert
    assert cleaned_df is not None
    assert not cleaned_df.empty

    # Verificar renombrado de columnas
    # Usar DB_COLUMNS del módulo constants para la verificación
    assert all(col in cleaned_df.columns for col in DB_COLUMNS if col in cleaned_df.columns)

    # Verificar tipos de datos y valores transformados
    assert pd.api.types.is_datetime64_any_dtype(cleaned_df['fecha_alta'])
    assert cleaned_df['en_internet'].dtype == 'bool'
    assert cleaned_df['cocina'].dtype == 'bool'
    assert cleaned_df['m2_construccion'].iloc[0] == 100.5
    assert cleaned_df['m2_terreno'].iloc[0] == 200.5
    assert cleaned_df['recamaras'].dtype == 'Int64' # Pandas nullable integer
    assert cleaned_df['edad'].dtype == 'Int64'

    # Verificar que las columnas eliminadas no están presentes
    # Asegurarse de que las columnas que se eliminan en clean_and_transform_data no estén en el df final
    columns_to_be_dropped = ['numeroLlaves', 'cuotaMantenimiento', 'institucionHipotecaria']
    for col in columns_to_be_dropped:
        assert col not in cleaned_df.columns


def test_clean_and_transform_data_file_not_found():
    # Arrange
    non_existent_path = "/path/to/non_existent_file.xlsx"

    # Act
    cleaned_df = clean_and_transform_data(non_existent_path)

    # Assert
    assert cleaned_df is None