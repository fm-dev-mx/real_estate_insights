import pandas as pd
from datetime import datetime, timedelta
from src.visualization.dashboard_logic import apply_dashboard_transformations

def test_apply_dashboard_transformations_happy_path():
    # 1. Preparación (Arrange)
    start_date = datetime(2024, 7, 1)
    data = {
        'id': ['P1', 'P2'],
        'fecha_alta': [start_date, start_date - timedelta(days=30)],
        'm2_construccion': [150.56, 200.12],
        'm2_terreno': [300.78, 400.99],
        'banos_totales': [2.5, 3.0],
        'cocina': [True, False],
        'latitud': [19.4326, 20.6597],
        'longitud': [-99.1332, -103.3496]
    }
    test_df = pd.DataFrame(data)

    # 2. Actuación (Act)
    transformed_df = apply_dashboard_transformations(test_df.copy())

    # 3. Afirmación (Assert)
    assert 'dias_en_mercado' in transformed_df.columns
    assert transformed_df['dias_en_mercado'].iloc[0] == (datetime.today() - start_date).days
    assert transformed_df['m2_construccion'].iloc[0] == 151
    assert transformed_df['m2_terreno'].iloc[0] == 301
    assert 'cocina' not in transformed_df.columns
    assert 'latitud' not in transformed_df.columns

def test_empty_dataframe():
    # Arrange
    test_df = pd.DataFrame()

    # Act
    transformed_df = apply_dashboard_transformations(test_df.copy())

    # Assert
    assert transformed_df.empty

def test_dias_en_mercado_missing_column():
    # Arrange
    data = {
        'm2_construccion': [100, 200]
    }
    test_df = pd.DataFrame(data)

    # Act
    transformed_df = apply_dashboard_transformations(test_df.copy())

    # Assert
    assert 'dias_en_mercado' in transformed_df.columns
    assert transformed_df['dias_en_mercado'].isnull().all()
