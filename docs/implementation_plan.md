# Plan de Implementación: Nuevas Funcionalidades para Real Estate Insights

## 1. Hoja de Ruta (Roadmap)

1.  **Gestión de PDFs (Descarga y Visualización):** Implementar la descarga de PDFs por propiedad y la interfaz de usuario para verlos localmente. Esto es fundamental para las siguientes etapas. **(IMPLEMENTADO)**
2.  **Extracción y Comparación de Datos de PDFs:** Desarrollar la lógica para leer los PDFs descargados, extraer campos clave y compararlos con los datos existentes en la base de datos, mostrando las diferencias.
3.  **Análisis Visual y Calificación de Imágenes:** Integrar la extracción de imágenes de los PDFs, su visualización en una galería y la implementación de un algoritmo de calificación visual.
4.  **Control de Versiones de Registros:** Diseñar e implementar el sistema de auditoría para registrar todas las modificaciones realizadas sobre los datos de las propiedades.
5.  **Integración y Refinamiento de UI/UX:** Unificar todas las nuevas funcionalidades en el dashboard de Streamlit, asegurando una una experiencia de usuario fluida y robusta.

## 2. Gestión de PDFs (Descarga y Visualización)

**Implementación Técnica:**

*   **Botón Dinámico:** En el dashboard de Streamlit, cada registro de propiedad tendrá un `st.button` que cambiará su etiqueta y acción.
    *   **Estado Inicial:** `[Descargar PDF]` si el PDF no existe localmente. Al hacer clic, llamará a una función `download_property_pdf(property_id, pdf_url)`.
    *   **Estado Posterior:** `[Ver PDF]` si el PDF ya está descargado. Al hacer clic, abrirá el PDF localmente (usando `os.startfile` en Windows o `subprocess.run` con el comando adecuado en otros OS).
*   **Descarga desde Century21:**
    *   Se creará `src/data_collection/download_pdf.py`.
    *   La URL del PDF se construirá usando el ID de la propiedad: `https://plus.21onlinemx.com/ft/[id]/DTF/273/40120`.
    *   La descarga se realizará utilizando la sesión de Selenium ya autenticada (reutilizando la lógica de `download_inventory.py` o adaptándola).
    *   Almacenamiento local: `PDF_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'data', 'pdfs')` (configurable en `.env`). Los archivos se guardarán como `data/pdfs/[property_id].pdf`.
*   **Manejo de Errores y Feedback:**
    *   **Conexión/Descarga Fallida:** Usar bloques `try-except` para `requests` o `selenium` (si la descarga requiere interacción web). Mostrar `st.error("Error al descargar el PDF.")` y un `st.exception(e)` para depuración.
    *   **Archivo Inexistente:** Verificar `os.path.exists(pdf_path)` antes de mostrar `[Ver PDF]`. Si no existe, mantener `[Descargar PDF]` o mostrar `[PDF no disponible]`.
    *   **Feedback Visual:** Usar `st.spinner("Descargando PDF...")` durante la operación de descarga. Mostrar `st.success("PDF descargado!")` o `st.warning("PDF ya existe.")` como tooltips o alertas temporales.

## 3. Comparación de Datos

**Flujo:**

1.  **Leer PDFs:** Al hacer clic en `[Ver PDF]`, además de abrirlo, se iniciará un proceso en segundo plano para extraer texto.
2.  **Extracción de Campos Clave:**
    *   **Campos Prioritarios:** `precio`, `m2_construccion`, `m2_terreno`, `recamaras`, `banios`, `edad`, `descripcion`.
    *   **Librería:** `PyMuPDF` (fitz) es excelente para extracción de texto e imágenes. Para texto no seleccionable (imágenes), se puede integrar `Tesseract` (vía `Pytesseract`).
    *   **Proceso:** Se definirá un conjunto de reglas (regex, búsqueda de palabras clave cercanas a valores numéricos) para identificar los campos prioritarios.
    *   **Validación:** Los datos extraídos se validarán contra patrones esperados (ej. números para precios, fechas para antigüedad).
3.  **Comparación y Diff Visual:**
    *   Los datos extraídos del PDF se compararán con los campos correspondientes en la base de datos para esa `property_id`.
    *   Se mostrará una tabla editable en Streamlit (`st.data_editor` o `st.dataframe` con `st.column_config.TextColumn` para edición) con tres columnas: `Campo`, `Valor BD`, `Valor PDF`.
    *   Las filas donde `Valor BD` y `Valor PDF` difieran se resaltarán (ej. color de fondo).
4.  **Elección y Registro de Cambios:**
    *   El usuario podrá editar el `Valor BD` directamente en la tabla o seleccionar cuál valor conservar (BD o PDF) mediante botones de radio/checkboxes por fila.
    *   Al confirmar, se registrará el cambio en el sistema de control de versiones (ver sección 5) y se actualizará la base de datos.

**Librerías Sugeridas:**

*   `PyMuPDF` (fitz): Extracción de texto, imágenes, metadatos.
*   `Pillow` (PIL): Procesamiento básico de imágenes (si se usa Tesseract).
*   `Pytesseract`: Interfaz Python para Tesseract OCR (si es necesario para texto en imágenes).

## 4. Análisis Visual y Calificación

**Implementación Técnica:**

1.  **Extracción de Imágenes:** Usando `PyMuPDF`, se iterará sobre las páginas del PDF para identificar y extraer imágenes (ej. `page.get_images()`). Se filtrarán por tamaño para evitar logos o imágenes pequeñas irrelevantes.
2.  **Galería de Imágenes:** Las imágenes extraídas se mostrarán en una galería interactiva en Streamlit (`st.image` en columnas o un componente personalizado si es necesario).
3.  **Algoritmo de Calificación (Heurística Simple - Enfoque Inicial):**
    *   **Parámetros:**
        *   **Número de imágenes:** Más imágenes = mayor puntuación.
        *   **Resolución:** Imágenes con mayor resolución (ej. >1000px en un lado) = mayor puntuación.
        *   **Tamaño de archivo:** Imágenes más grandes (en KB/MB) = mayor puntuación (proxy de calidad).
        *   **Nitidez (básico):** Se puede usar un algoritmo simple de detección de bordes (ej. Laplaciano de OpenCV o Pillow) para estimar la nitidez.
        *   **Iluminación (básico):** Calcular el brillo promedio de la imagen.
    *   **Escala:** Cada parámetro contribuirá a una puntuación total de 1 a 10.
    *   **Almacenamiento:** Se añadirán columnas a la tabla `properties` (ej. `calificacion_visual_auto`, `calificacion_visual_manual`) o se creará una nueva tabla `property_visual_analysis` (`property_id`, `image_path`, `auto_score`, `manual_score`).
4.  **Ajuste Manual:** Un `st.slider` o `st.number_input` permitirá al usuario ajustar la calificación automática. Este ajuste manual también se registrará en el control de versiones.

**Consideraciones:**

*   **Heurística vs. ML:** Se comenzará con heurísticas simples para un prototipo rápido. Los modelos de ML serán una fase futura.
*   **Almacenamiento:** La elección de almacenar en `properties` o una tabla separada dependerá de la frecuencia de actualización y la granularidad deseada. Para un prototipo, añadir a `properties` es más rápido.

## 5. Control de Versiones (para Registros)

**Esquema de Historial de Cambios:**

Se creará una nueva tabla en la base de datos: `property_audit_log`.

```sql
CREATE TABLE IF NOT EXISTS property_audit_log (
    log_id SERIAL PRIMARY KEY,
    property_id VARCHAR(255) NOT NULL,
    field_name VARCHAR(255) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    change_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(255), -- Usuario que realizó el cambio
    change_reason TEXT,     -- Motivo del cambio (ej. "Corrección manual", "Actualización por PDF")
    FOREIGN KEY (property_id) REFERENCES properties(id)
);
```

*   **Registro de Modificaciones:** Cada vez que un usuario modifique un campo de una propiedad (ya sea por comparación de PDF o ajuste manual), la lógica de actualización en `PropertyRepository` (o una nueva capa de servicio) registrará una entrada en `property_audit_log`. El campo `changed_by` se establecerá como "Sistema" o "Usuario Manual" según corresponda.
*   **Rollback Parcial:**
    *   Se implementará una función en Streamlit que muestre el historial de cambios para un `property_id` y `field_name` específico.
    *   El usuario podrá seleccionar una entrada del historial y hacer clic en `[Revertir]`.
    *   La función de reversión leerá el `old_value` de la entrada seleccionada y actualizará el `new_value` en la tabla `properties` con ese `old_value`. Se registrará una nueva entrada en `property_audit_log` indicando la reversión.
