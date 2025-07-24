import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.visualization.dashboard_logic import apply_dashboard_transformations

def test_apply_dashboard_transformations():
    # 1. Preparación (Arrange)
    # Crear un DataFrame de ejemplo con datos realistas
    start_date = datetime(2024, 7, 1)
    data = {
        'fecha_alta': [start_date, start_date - timedelta(days=30)],
        'm2_construccion': [150.56, 200.12],
        'm2_terreno': [300.78, 400.99],
        'banos': [2, 3],
        'medios_banos': [1, 0],
        'cocina': ['si', 'no'],
        'latitud': [19.4326, 20.6597],
        'longitud': [-99.1332, -103.3496]
    }
    test_df = pd.DataFrame(data)

    # 2. Actuación (Act)
    transformed_df = apply_dashboard_transformations(test_df.copy())

    # 3. Afirmación (Assert)
    # Verificar que las nuevas columnas se crearon correctamente
    assert 'dias_en_mercado' in transformed_df.columns
    assert 'banos_totales' in transformed_df.columns
    assert transformed_df['dias_en_mercado'].iloc[0] == (datetime.today() - start_date).days
    assert transformed_df['banos_totales'].iloc[0] == 2.5
    assert transformed_df['banos_totales'].iloc[1] == 3.0

    # Verificar que los valores se redondearon
    assert transformed_df['m2_construccion'].iloc[0] == 151
    assert transformed_df['m2_terreno'].iloc[0] == 301

    # Verificar que las columnas innecesarias fueron eliminadas
    assert 'fecha_alta' not in transformed_df.columns
    assert 'cocina' not in transformed_df.columns
    assert 'latitud' not in transformed_df.columns

def test_banos_totales_calculation():
    # Arrange
    data = {
        'banos': [2, 1, 0, np.nan, 3],
        'medios_banos': [1, 0, 1, 0.5, np.nan]
    }
    test_df = pd.DataFrame(data)

    # Act
    transformed_df = apply_dashboard_transformations(test_df.copy())

    # Assert
    # Expected banos_totales: [2 + 0.5 = 2.5, 1 + 0 = 1.0, 0 + 0.5 = 0.5, 0 + 0.25 = 0.25, 3 + 0 = 3.0]
    pd.testing.assert_series_equal(
        transformed_df['banos_totales'],
        pd.Series([2.5, 1.0, 0.5, 0.25, 3.0], name='banos_totales')
    )

def test_banos_totales_missing_columns():
    # Arrange
    data = {
        'col_random': [1, 2, 3]
    }
    test_df = pd.DataFrame(data)

    # Act
    transformed_df = apply_dashboard_transformations(test_df.copy())

    # Assert
    assert 'banos_totales' in transformed_df.columns
    pd.testing.assert_series_equal(
        transformed_df['banos_totales'],
        pd.Series([0.0, 0.0, 0.0], name='banos_totales')
    )