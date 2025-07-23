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
