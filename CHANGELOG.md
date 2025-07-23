# Changelog

## [2025-07-22]

### Corregido (Fixed)

*   **`ImportError` al iniciar la aplicación del dashboard.**
    *   **Causa Raíz:** La aplicación se intentaba ejecutar como un script directo (`python src/visualization/dashboard_app.py`), lo que impedía que Python resolviera las importaciones relativas (`from ..utils import ...`) al no reconocer el directorio `src` como un paquete.
    *   **Solución:** Se ha introducido un script lanzador, `run_dashboard.py`, en el directorio raíz. Este script utiliza `python -m streamlit run ...` para invocar la aplicación, asegurando que la ruta del proyecto se cargue correctamente y que la estructura de paquetes de `src` sea reconocida por Python.
    *   **Archivos Involucrados:**
        *   `run_dashboard.py` (Añadido)
        *   `src/data_collection/__init__.py` (Añadido para consistencia de paquetes)
        *   `src/db_setup/__init__.py` (Añadido para consistencia de paquetes)

## [2025-07-22]

### Añadido (Added)

*   **Cobertura completa de pruebas unitarias.**
    *   **Descripción:** Se han implementado pruebas unitarias exhaustivas para los módulos clave del proyecto, incluyendo:
        *   `src/visualization/dashboard_logic.py`
        *   `src/data_processing/data_validator.py`
        *   `src/data_processing/data_cleaner.py`
        *   `src/data_access/property_repository.py`
        *   `src/data_processing/excel_converter.py`
        *   `src/db_setup/create_db_table.py`
        *   `src/data_collection/download_inventory.py`
    *   **Archivos Involucrados:**
        *   `tests/` (Nuevo directorio con todos los archivos de prueba)
        *   `docs/testing_roadmap.md` (Nuevo documento de seguimiento de pruebas)
        *   `README.md` (Actualizado con instrucciones de ejecución de pruebas)
        *   `src/db_setup/create_db_table.py` (Actualizado con la definición de `create_table_sql`)
        *   `src/data_collection/download_inventory.py` (Refactorizado para ser testeable)