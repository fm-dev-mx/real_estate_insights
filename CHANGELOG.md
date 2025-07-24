# Changelog

## [Unreleased]

### Añadido (Added)

*   **Módulo de descarga de PDFs de propiedades.**
    *   Se ha creado `src/data_collection/download_pdf.py` para descargar los archivos PDF asociados a cada propiedad. Esta funcionalidad es clave para las próximas etapas de extracción de datos.
    *   **Archivos Involucrados:** `src/data_collection/download_pdf.py` (Añadido).

### Cambiado (Changed)

*   **Refactorización del proceso de limpieza de datos.**
    *   **Descripción:** La lógica de limpieza y transformación de datos se ha movido de `clean_data.py` a una función dedicada `clean_and_transform_data` en `data_cleaner.py`, mejorando la modularidad y la testeabilidad.
    *   Se ha mejorado la limpieza de datos de baños, creando una nueva columna `banos_totales`.
    *   **Archivos Involucrados:** `src/data_processing/clean_data.py`, `src/data_processing/data_cleaner.py`.

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
