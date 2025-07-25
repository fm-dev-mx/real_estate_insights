# Hoja de Ruta de Pruebas Unitarias

Este documento detalla el estado actual de las pruebas unitarias en el proyecto `real_estate_insights`, listando las funciones y módulos que ya cuentan con cobertura de pruebas, así como aquellos que aún requieren ser probados.

## 🧪 Pruebas Existentes

Las siguientes funciones y módulos ya cuentan con pruebas unitarias implementadas:

*   **`src/visualization/dashboard_logic.py`**
    *   `apply_dashboard_transformations`: Verifica que las transformaciones de datos para el dashboard (cálculo de días en mercado, redondeo de m2, unificación de baños, eliminación de columnas) se apliquen correctamente.

*   **`src/data_processing/data_validator.py`**
    *   `get_incomplete_properties`: Probar la identificación correcta de propiedades con campos faltantes.
    *   `validate_and_report_missing_data`: Probar la detección de datos faltantes según la matriz de prioridad y la generación de reportes.

*   **`src/data_processing/data_cleaner.py`**
    *   `clean_and_transform_data`: Probar la limpieza y transformación de datos desde un archivo Excel, incluyendo el renombrado de columnas, conversión de tipos y manejo de valores nulos.

*   **`src/data_access/property_repository.py`**
    *   `PropertyRepository.load_properties`: Probar la carga y actualización de propiedades en la base de datos, incluyendo manejo de duplicados y tipos de datos.
    *   `PropertyRepository.get_properties_from_db`: Probar la recuperación de propiedades con diferentes combinaciones de filtros.
    *   `PropertyRepository.get_property_details`: Probar la obtención de detalles de una propiedad específica.
    *   `PropertyRepository.update_property_field`: Probar la actualización de un campo específico de una propiedad.
    *   `PropertyRepository.log_audit_entry`: Probar el registro de entradas en la tabla de auditoría.

*   **`src/data_processing/excel_converter.py`**
    *   `convert_xls_to_xlsx`: Probar la conversión de archivos XLS a XLSX (simulando el entorno con MS Excel).

*   **`src/db_setup/create_db_table.py`**
    *   `create_properties_table`: Probar la creación de la tabla `properties` en la base de datos, incluyendo el manejo de errores y la verificación de la conexión.

*   **`src/data_collection/download_pdf.py`**
    *   `download_property_pdf`: Probar la descarga exitosa de un PDF, el manejo de errores (ej. 404 Not Found) y la omisión de descarga si el archivo ya existe.

*   **`src/scripts/pdf_autofill.py`**
    *   `autofill_from_pdf`: Probar el auto-llenado de datos desde PDF, incluyendo casos de éxito, no coincidencia y manejo de errores de OCR.

*   **`src/scripts/apply_manual_fixes.py`**
    *   `apply_manual_fixes`: Probar la aplicación de correcciones manuales, el registro en el log de auditoría y el manejo de errores.

## 📝 Pruebas Pendientes

Las siguientes funciones y módulos requieren la implementación de pruebas unitarias para asegurar su correcto funcionamiento y robustez:

*   **`src/data_collection/download_inventory.py`**
    *   Funciones de descarga y automatización web: Probar el proceso de login y descarga de archivos (estas pruebas pueden ser más complejas debido a la interacción con la UI).

### Nuevas Pruebas Requeridas

| Nuevo Módulo | Pruebas a Añadir | Propósito |
| --- | --- | --- |
| **Lógica de Pausa** | `test_pipeline_pauses_on_critical_gaps`, `test_pipeline_resumes_after_fixes` | Asegurar que la regla del 5% se comporte según la especificación. |
| **Migración SQL** | `test_migration_constraints` | Confirmar restricciones NOT NULL y CHECKs. |
| **End-to-end** | `test_full_pipeline_success` | Proteger contra regresiones. |

## 🚀 Cómo Ejecutar las Pruebas

Para ejecutar todas las pruebas unitarias del proyecto, navega a la raíz del proyecto en tu terminal y ejecuta:

```bash
python -m pytest tests/
```

Para ejecutar una prueba específica, puedes especificar la ruta al archivo de prueba:

```bash
python -m pytest tests/test_dashboard_logic.py
```
