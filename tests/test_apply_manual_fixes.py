import pytest
from unittest.mock import patch
import os
from src.scripts.apply_manual_fixes import apply_manual_fixes

# Fixture para mockear las variables de entorno de la DB
@pytest.fixture
def mock_db_env_vars():
    with patch.dict(os.environ, {
        'REI_DB_NAME': 'test_db',
        'REI_DB_USER': 'test_user',
        'REI_DB_PASSWORD': 'test_pass',
        'REI_DB_HOST': 'test_host',
        'REI_DB_PORT': '5432'
    }):
        yield

# Fixture para mockear PropertyRepository
@pytest.fixture
def mock_property_repo():
    with patch('src.scripts.apply_manual_fixes.PropertyRepository') as MockRepo:
        mock_repo_instance = MockRepo.return_value
        yield mock_repo_instance

# Test para aplicar una única corrección manual exitosamente
def test_apply_manual_single_success(mock_db_env_vars, mock_property_repo):
    property_id = "prop123"
    field_name = "precio"
    old_value = 100000.0
    new_value = 120000.0
    changed_by = "test_user"
    change_reason = "Corrección de precio"

    success = apply_manual_fixes(property_id, field_name, old_value, new_value, changed_by, change_reason)

    assert success is True
    mock_property_repo.update_property_field.assert_called_once_with(property_id, field_name, new_value)
    mock_property_repo.log_audit_entry.assert_called_once_with(property_id, field_name, old_value, new_value, changed_by, change_reason)

# Test para verificar que se escribe en el log de auditoría
def test_audit_log_written(mock_db_env_vars, mock_property_repo):
    property_id = "prop456"
    field_name = "m2_construccion"
    old_value = 150.0
    new_value = 160.0
    changed_by = "another_user"
    change_reason = "Actualización de m2"

    apply_manual_fixes(property_id, field_name, old_value, new_value, changed_by, change_reason)

    mock_property_repo.log_audit_entry.assert_called_once()
    args, kwargs = mock_property_repo.log_audit_entry.call_args
    assert args[0] == property_id
    assert args[1] == field_name
    assert args[2] == old_value
    assert args[3] == new_value
    assert args[4] == changed_by
    assert args[5] == change_reason

# Test para manejo de errores (ej. error de DB al actualizar)
def test_apply_manual_db_error(mock_db_env_vars, mock_property_repo):
    mock_property_repo.update_property_field.side_effect = Exception("DB Error")

    property_id = "prop789"
    field_name = "descripcion"
    old_value = "old desc"
    new_value = "new desc"
    changed_by = "error_user"
    change_reason = "Error test"

    success = apply_manual_fixes(property_id, field_name, old_value, new_value, changed_by, change_reason)

    assert success is False
    mock_property_repo.update_property_field.assert_called_once()
    mock_property_repo.log_audit_entry.assert_not_called() # No se debe loguear si la actualización falla

# Test para manejo de DB_PASSWORD no configurada
def test_apply_manual_no_db_password():
    with patch.dict(os.environ, {'REI_DB_PASSWORD': ''}):
        success = apply_manual_fixes("prop1", "field", "old", "new", "user", "reason")
        assert success is False

# TODO: Implement test_duplicate_fix_handling if needed (depends on how duplicate fixes are defined/handled in apply_manual_fixes)
