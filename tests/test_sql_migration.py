import pytest
from unittest.mock import patch, MagicMock
import psycopg2
import os

# Importar la variable create_table_sql del módulo de configuración de DB
from src.db_setup.create_db_table import create_table_sql

@pytest.fixture
def mock_db_connection():
    with patch('src.db_setup.create_db_table.psycopg2.connect') as mock_connect:
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

def test_migration_constraints(mock_env_vars, mock_db_connection):
    mock_conn, mock_cursor, mock_connect = mock_db_connection

    # Simular la ejecución del script de creación de tablas
    # Esto es para verificar que el SQL contiene las restricciones esperadas
    # No ejecutamos el create_properties_table real aquí para evitar dependencias de DB

    # Verificar que el SQL contiene las restricciones NOT NULL para campos críticos
    assert "id VARCHAR(255) PRIMARY KEY" in create_table_sql
    assert "precio DECIMAL(18, 2) NOT NULL" in create_table_sql
    assert "m2_construccion DECIMAL(10, 2) NOT NULL" in create_table_sql
    assert "m2_terreno DECIMAL(10, 2) NOT NULL" in create_table_sql
    assert "recamaras INTEGER NOT NULL" in create_table_sql
    assert "banos_totales DECIMAL(4, 1) NOT NULL" in create_table_sql
    assert "descripcion TEXT NOT NULL" in create_table_sql
    assert "status VARCHAR(50) NOT NULL" in create_table_sql
    assert "tipo_operacion VARCHAR(50) NOT NULL" in create_table_sql
    assert "tipo_contrato VARCHAR(50) NOT NULL" in create_table_sql
    assert "colonia VARCHAR(255) NOT NULL" in create_table_sql
    assert "municipio VARCHAR(255) NOT NULL" in create_table_sql
    assert "latitud DECIMAL(10, 8) NOT NULL" in create_table_sql
    assert "longitud DECIMAL(11, 8) NOT NULL" in create_table_sql

    # Verificar que el SQL contiene las restricciones CHECK para campos numéricos
    assert "precio >= 0" in create_table_sql
    assert "m2_construccion >= 0" in create_table_sql
    assert "m2_terreno >= 0" in create_table_sql
    assert "recamaras >= 0" in create_table_sql
    assert "banos_totales >= 0" in create_table_sql

    # Verificar que el SQL contiene las restricciones CHECK para campos de texto (ej. status, tipo_operacion, tipo_contrato)
    assert "status IN ('enPromocion', 'conIntencion', 'vendidas')" in create_table_sql
    assert "tipo_operacion IN ('venta', 'renta', 'traspaso', 'opcion')" in create_table_sql
    assert "tipo_contrato IN ('exclusiva', 'opcion', 'abierta')" in create_table_sql

    # Verificar que la tabla audit_log se crea
    assert "CREATE TABLE IF NOT EXISTS audit_log" in create_table_sql
    assert "property_id VARCHAR(255) NOT NULL REFERENCES properties(id)" in create_table_sql
    assert "field_name VARCHAR(255) NOT NULL" in create_table_sql
    assert "old_value TEXT" in create_table_sql
    assert "new_value TEXT" in create_table_sql
    assert "change_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP" in create_table_sql
    assert "changed_by VARCHAR(255)" in create_table_sql
    assert "change_source VARCHAR(50)" in create_table_sql
