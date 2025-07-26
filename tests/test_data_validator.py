import pandas as pd
from src.data_processing.data_validator import get_incomplete_properties

def test_get_incomplete_properties_with_missing_values():
    # Arrange
    data = {
        'banos': [2, None, 1, 3],
        'medios_banos': [1, 0, None, 0],
        'm2_construccion': [100.0, 150.0, 200.0, None],
        'm2_terreno': [200.0, None, 300.0, 400.0],
        'descripcion': ['Casa bonita', '', 'Amplio jardín', 'Descripción completa']
    }
    df = pd.DataFrame(data)

    # Act
    incomplete_df = get_incomplete_properties(df)

    # Assert
    # Se esperan 2 propiedades incompletas (índices 1 y 3).
    # La lógica actual de la prueba parece verificar solo ciertas columnas (ej. m2_construccion, m2_terreno).
    assert len(incomplete_df) == 2
    assert incomplete_df.index.tolist() == [1, 3]

def test_get_incomplete_properties_with_no_missing_values():
    # Arrange
    data = {
        'banos': [2, 3, 1],
        'medios_banos': [1, 0, 0],
        'm2_construccion': [100.0, 150.0, 200.0],
        'm2_terreno': [200.0, 250.0, 300.0],
        'descripcion': ['Casa bonita', 'Amplio jardín', 'Descripción completa']
    }
    df = pd.DataFrame(data)

    # Act
    incomplete_df = get_incomplete_properties(df)

    # Assert
    assert incomplete_df.empty

def test_get_incomplete_properties_with_empty_dataframe():
    # Arrange
    df = pd.DataFrame()

    # Act
    incomplete_df = get_incomplete_properties(df)

    # Assert
    assert incomplete_df.empty
