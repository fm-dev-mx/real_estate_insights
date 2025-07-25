import pandas as pd
import logging
import os
from src.data_access.property_repository import PropertyRepository
from src.data_access.database_connection import get_db_connection # Assuming this is how you get connection details

logger = logging.getLogger(__name__)

def apply_manual_fixes(property_id: str, field_name: str, old_value, new_value, changed_by: str, change_reason: str) -> bool:
    """
    Applies a single manual fix to the database and logs the change.

    Args:
        property_id (str): The ID of the property to fix.
        field_name (str): The name of the field to update.
        old_value: The old value of the field (for audit log).
        new_value: The new value to set for the field.
        changed_by (str): The user who made the change.
        change_reason (str): The reason for the change.

    Returns:
        bool: True if the fix was applied successfully, False otherwise.
    """
    logger.info(f"[MANUAL_FIX] Iniciando aplicación de corrección manual para propiedad {property_id}, campo {field_name}.")

    db_name = os.environ.get('REI_DB_NAME', 'real_estate_db')
    db_user = os.environ.get('REI_DB_USER', 'fm_asesor')
    db_password = os.environ.get('REI_DB_PASSWORD')
    db_host = os.environ.get('REI_DB_HOST', '127.0.0.1')
    db_port = os.environ.get('REI_DB_PORT', '5432')

    if not db_password:
        logger.error("DB_PASSWORD environment variable not set. Cannot connect to database.")
        return False

    try:
        repo = PropertyRepository(db_name, db_user, db_password, db_host, db_port)
        repo.update_property_field(property_id, field_name, new_value)
        repo.log_audit_entry(property_id, field_name, old_value, new_value, changed_by, change_reason)
        logger.info(f"[MANUAL_FIX] Corrección manual aplicada y auditada para {property_id}, campo {field_name}.")
        return True
    except Exception as e:
        logger.error(f"[MANUAL_FIX] Error al aplicar corrección manual para {property_id}, campo {field_name}: {e}")
        return False

if __name__ == "__main__":
    # Example usage for testing in isolation
    test_property_id = "prop1"
    test_field_name = "precio"
    test_old_value = 1000000.0
    test_new_value = 1200000.0
    test_changed_by = "test_user_cli"
    test_change_reason = "CLI test correction"

    success = apply_manual_fixes(test_property_id, test_field_name, test_old_value, test_new_value, test_changed_by, test_change_reason)
    if success:
        print(f"Manual fix applied successfully for {test_property_id} - {test_field_name}.")
    else:
        print(f"Failed to apply manual fix for {test_property_id} - {test_field_name}.")
