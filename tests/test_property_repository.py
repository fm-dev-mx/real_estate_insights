import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
import psycopg2 # Importar psycopg2 para poder lanzar sus errores

# Importar la clase PropertyRepository y la función get_db_connection
from src.data_access.property_repository import PropertyRepository
from src.utils.constants import DB_COLUMNS

# Mock de la conexión a la base de datos
@pytest.fixture
def mock_db_connection():
    with patch('src.data_access.database_connection.psycopg2') as mock_psycopg2_conn_module, \
         patch('src.data_access.property_repository.psycopg2.extras') as mock_extras_module:

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.encoding = 'UTF8' # Añadir el atributo encoding a la conexión
        mock_cursor.connection = mock_conn # Asegurar que el cursor tenga una conexión mockeada
        mock_psycopg2_conn_module.connect.return_value = mock_conn

        # Mockear execute_values directamente en el módulo donde se usa
        with patch('src.data_access.property_repository.extras.execute_values') as mock_execute_values:
            yield mock_conn, mock_cursor, mock_psycopg2_conn_module, mock_extras_module, mock_execute_values

@pytest.fixture
def property_repo(mock_db_connection):
    # No necesitamos usar mock_db_connection directamente aquí, solo para asegurar que el patch está activo
    return PropertyRepository('test_db', 'test_user', 'test_pass', 'test_host', 'test_port')

def test_load_properties_insert(property_repo, mock_db_connection):
    mock_conn, mock_cursor, mock_psycopg2_conn_module, mock_extras_module, mock_execute_values = mock_db_connection

    # Arrange
    df_to_load = pd.DataFrame({
        'id': [1, 2],
        'fecha_alta': [pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-02')],
        'status': ['enPromocion', 'vendidas'],
        'tipo_operacion': ['venta', 'renta'],
        'tipo_contrato': ['exclusiva', 'abierta'],
        'en_internet': [True, False],
        'clave': ['CLAVE001', 'CLAVE002'],
        'clave_oficina': ['OF01', 'OF02'],
        'subtipo_propiedad': ['casa', 'departamento'],
        'calle': ['Calle A', 'Calle B'],
        'numero': ['10', '20'],
        'colonia': ['Colonia X', 'Colonia Y'],
        'municipio': ['Municipio 1', 'Municipio 2'],
        'latitud': [1.0, 2.0],
        'longitud': [1.0, 2.0],
        'codigo_postal': ['12345', '67890'],
        'precio': [100000.0, 200000.0],
        'comision': [3.0, 4.0],
        'comision_compartir_externas': [1.0, 1.5],
        'm2_construccion': [100.0, 150.0],
        'm2_terreno': [200.0, 250.0],
        'recamaras': [3, 2],
            'banos_totales': [2.5, 1.0],
            'cocina': [True, False],
        'niveles_construidos': [2, 1],
        'edad': [5, 10],
        'estacionamientos': [1, 0],
        'descripcion': ['Descripción 1', 'Descripción 2'],
        'nombre_agente': ['Agente A', 'Agente B'],
        'apellido_paterno_agente': ['Paterno A', 'Paterno B'],
        'apellido_materno_agente': ['Materno A', 'Materno B']
    })

    # Act
    property_repo.load_properties(df_to_load, DB_COLUMNS)

    # Assert
    mock_psycopg2_conn_module.connect.assert_called_once_with(
        dbname='test_db', user='test_user', password='test_pass', host='test_host', port='test_port'
    )
    mock_cursor.execute.assert_not_called() # execute_values should be used
    mock_execute_values.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_get_properties_from_db(property_repo, mock_db_connection):
    mock_conn, mock_cursor, mock_psycopg2_conn_module, mock_extras_module, mock_execute_values = mock_db_connection

    # Arrange
    # Simular el retorno de pd.read_sql
    expected_df = pd.DataFrame({
        'id': [1],
        'precio': [150000.0],
        'status': ['enPromocion']
    })
    # Mockear pd.read_sql para que devuelva nuestro DataFrame esperado
    with patch('pandas.read_sql', return_value=expected_df) as mock_read_sql:
        # Act
        result_df = property_repo.get_properties_from_db(min_price=100000, property_status='enPromocion')

        # Assert
        mock_psycopg2_conn_module.connect.assert_called_once()
        mock_read_sql.assert_called_once()
        # Verificar que la consulta y los parámetros se pasaron correctamente a read_sql
        args, kwargs = mock_read_sql.call_args
        assert 'SELECT * FROM properties WHERE 1=1 AND precio >= %(min_price)s AND status IN %(status_types)s' in args[0]
        assert kwargs['params']['min_price'] == 100000.0
        assert kwargs['params']['status_types'] == ('enPromocion',)

        pd.testing.assert_frame_equal(result_df, expected_df)
        mock_conn.close.assert_called_once()

def test_get_properties_from_db_no_filters(property_repo, mock_db_connection):
    mock_conn, mock_cursor, mock_psycopg2_conn_module, mock_extras_module, mock_execute_values = mock_db_connection

    # Arrange
    expected_df = pd.DataFrame({
        'id': [1, 2],
        'precio': [150000.0, 250000.0]
    })
    with patch('pandas.read_sql', return_value=expected_df) as mock_read_sql:
        # Act
        result_df = property_repo.get_properties_from_db()

        # Assert
        mock_psycopg2_conn_module.connect.assert_called_once()
        mock_read_sql.assert_called_once()
        args, kwargs = mock_read_sql.call_args
        assert 'SELECT * FROM properties WHERE 1=1' in args[0]
        assert kwargs['params'] == {}
        pd.testing.assert_frame_equal(result_df, expected_df)
        mock_conn.close.assert_called_once()


def test_load_properties_error_handling(property_repo, mock_db_connection):
    mock_conn, mock_cursor, mock_psycopg2_conn_module, mock_extras_module, mock_execute_values = mock_db_connection

    # Configurar el mock de execute_values para que lance un psycopg2.Error
    mock_execute_values.side_effect = psycopg2.Error("Error de carga simulado")

    df_to_load = pd.DataFrame({
        'id': [1],
        'fecha_alta': [pd.Timestamp('2023-01-01')],
        'status': ['enPromocion'],
        'tipo_operacion': ['venta'],
        'tipo_contrato': ['exclusiva'],
        'en_internet': [True],
        'clave': ['CLAVE001'],
        'clave_oficina': ['OF01'],
        'subtipo_propiedad': ['casa'],
        'calle': ['Calle A'],
        'numero': ['10'],
        'colonia': ['Colonia X'],
        'municipio': ['Municipio 1'],
        'latitud': [1.0],
        'longitud': [1.0],
        'codigo_postal': ['12345'],
        'precio': [100000.0],
        'comision': [3.0],
        'comision_compartir_externas': [1.0],
        'm2_construccion': [100.0],
        'm2_terreno': [200.0],
        'recamaras': [3],
            'banos_totales': [2.5],
            'cocina': [True],
        'niveles_construidos': [2],
        'edad': [5],
        'estacionamientos': [1],
        'descripcion': ['Descripción 1'],
        'nombre_agente': ['Agente A'],
        'apellido_paterno_agente': ['Paterno A'],
        'apellido_materno_agente': ['Materno A']
    })

    property_repo.load_properties(df_to_load, DB_COLUMNS)

    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()
