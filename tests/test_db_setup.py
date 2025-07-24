import pytest
from unittest.mock import MagicMock, patch
import psycopg2
import os

# Importar la función a probar
from src.db_setup.create_db_table import create_properties_table

# Mock de las variables de entorno
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

# Mock de la conexión a la base de datos
@pytest.fixture
def mock_db_connection():
    with patch('src.db_setup.create_db_table.psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_conn, mock_cursor, mock_connect

# Mock de la sentencia SQL de creación de tabla
@pytest.fixture
def mock_create_table_sql():
    with patch('src.db_setup.create_db_table.create_table_sql', "CREATE TABLE properties (id INT);") as mock_sql:
        yield mock_sql

def test_create_properties_table_success(mock_env_vars, mock_db_connection, mock_create_table_sql):
    mock_conn, mock_cursor, mock_connect = mock_db_connection

    # Act
    create_properties_table()

    # Assert
    mock_connect.assert_called_once_with(
        dbname='test_db', user='test_user', password='test_pass', host='test_host', port='5432'
    )
    mock_cursor.execute.assert_any_call("CREATE TABLE properties (id INT);")
    mock_cursor.execute.assert_any_call("ALTER TABLE properties ADD COLUMN IF NOT EXISTS banos_totales DECIMAL(4, 1);")
    assert mock_cursor.execute.call_count == 2
    mock_cursor.execute.assert_any_call("ALTER TABLE properties ADD COLUMN IF NOT EXISTS banos_totales DECIMAL(4, 1);")
    assert mock_conn.commit.call_count == 2
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

def test_create_properties_table_no_password(mock_env_vars, mock_db_connection, mock_create_table_sql):
    mock_conn, mock_cursor, mock_connect = mock_db_connection
    
    # Arrange: Eliminar la contraseña del entorno mockeado
    with patch.dict(os.environ, {'REI_DB_PASSWORD': ''}):
        # Act
        create_properties_table()

        # Assert
        mock_connect.assert_not_called()
        mock_cursor.execute.assert_not_called()
        mock_conn.commit.assert_not_called()
        mock_cursor.close.assert_not_called()
        mock_conn.close.assert_not_called()

def test_create_properties_table_db_error(mock_env_vars, mock_db_connection, mock_create_table_sql):
    mock_conn, mock_cursor, mock_connect = mock_db_connection
    mock_connect.side_effect = psycopg2.Error("Simulated DB Error")

    # Act
    create_properties_table()

    # Assert
    mock_connect.assert_called_once()
    mock_cursor.execute.assert_not_called() # No se llega a ejecutar si la conexión falla
    mock_conn.commit.assert_not_called()
    mock_conn.close.assert_not_called() # La conexión no se establece, por lo tanto no se cierra