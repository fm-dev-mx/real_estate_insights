# Plan de Siguientes Pasos: Normalización y Almacenamiento de Datos

Este documento detalla las recomendaciones y el plan para avanzar en la automatización, específicamente en las etapas de **Limpieza, Validación y Normalización de Datos** (Paso 2) y **Almacenamiento de Datos** (Paso 3).

---

## 📊 Fase 1: Normalización y Limpieza de Datos (`src/data_processing/`)

**Objetivo:** Transformar los datos crudos obtenidos del archivo XLS en un formato limpio, consistente y estructurado, listo para el análisis y almacenamiento.

**Herramienta Principal:** Python con la librería `pandas`. Pandas es la herramienta estándar para manipulación y análisis de datos en Python, ideal para trabajar con datos tabulares como los de un archivo XLS.

### Mejores Prácticas Sugeridas:

1.  **Inspección Inicial del XLS:** Antes de cualquier limpieza, es crucial entender la estructura del archivo XLS descargado. Esto incluye identificar:
    *   Nombres de columnas (¿son consistentes? ¿necesitan ser renombrados?).
    *   Tipos de datos (números, texto, fechas).
    *   Valores faltantes (NaN, celdas vacías).
    *   Valores atípicos o inconsistentes.
    *   Filas o columnas irrelevantes.

2.  **Manejo de Valores Faltantes:**
    *   **Identificación:** Detectar celdas vacías o con valores nulos.
    *   **Estrategias:** Decidir si imputar (rellenar con un valor promedio, mediana, etc.) o eliminar filas/columnas completas, dependiendo del contexto y la cantidad de datos faltantes.

3.  **Estandarización de Formatos:**
    *   **Fechas:** Convertir todas las columnas de fecha a un formato uniforme (ej. `YYYY-MM-DD`).
    *   **Números:** Asegurar que los valores numéricos (precios, áreas) sean tratados como números y no como texto, manejando separadores de miles o decimales.
    *   **Texto:** Convertir texto a minúsculas, eliminar espacios extra, estandarizar abreviaturas.

4.  **Eliminación de Duplicados:** Identificar y remover filas completamente duplicadas o duplicados basados en columnas clave (ej. ID de propiedad).

5.  **Validación de Datos:** Implementar reglas de negocio para asegurar la calidad de los datos (ej. los precios deben ser positivos, las áreas deben estar dentro de un rango razonable).

6.  **Normalización de Texto:** Para campos de texto libre (ej. descripción de propiedad), aplicar técnicas como la eliminación de caracteres especiales, tokenización o lematización si se planea un análisis de texto más avanzado.

7.  **Modularidad:** Encapsular la lógica de limpieza en funciones o clases reutilizables dentro de un nuevo módulo, por ejemplo, `src/data_processing/clean_data.py`. Esto facilita el mantenimiento y las pruebas.

8.  **Registro de Cambios:** Implementar un sistema de logging para registrar las transformaciones realizadas, los errores encontrados y los datos descartados durante el proceso de limpieza.

### Primeros Pasos Concretos:

1.  **Crear el directorio:** `src/data_processing/`
2.  **Crear el archivo:** `src/data_processing/clean_data.py`
3.  **Implementar la lectura del XLS:** En `clean_data.py`, cargar un archivo XLS de ejemplo (uno descargado por `download_inventory.py`).
4.  **Realizar una inspección básica:** Usar `df.head()`, `df.info()`, `df.describe()` y `df.isnull().sum()` para entender el dataset.

---

## 🗄️ Fase 2: Almacenamiento de Datos

**Objetivo:** Persistir los datos limpios y normalizados en una base de datos para su posterior consulta, análisis y uso en etapas futuras de la automatización.

### Decisión de Base de Datos: PostgreSQL

Basado en tus requerimientos de volumen de datos, uso futuro (potencial multiusuario y escalabilidad), necesidad de consultas complejas y preferencia por bases de datos relacionales, hemos decidido utilizar **PostgreSQL**.

**Ventajas de PostgreSQL para este proyecto:**
*   **Robustez y Escalabilidad:** Maneja eficientemente volúmenes de datos crecientes y cargas de trabajo complejas.
*   **Consultas Complejas:** Excelente soporte para SQL avanzado, ideal para análisis de mercado y tendencias.
*   **Relacional:** Permite modelar y manejar relaciones complejas entre las propiedades y sus atributos.
*   **Compatibilidad con Supabase:** Facilita una futura migración o integración con Supabase, ya que este último utiliza PostgreSQL como su base de datos subyacente.

### Pasos para la Configuración de PostgreSQL (Local):

1.  **Instalación de PostgreSQL:**
    *   Si no lo tienes instalado, descarga e instala PostgreSQL desde el sitio oficial: [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
    *   Durante la instalación, asegúrate de recordar la contraseña del usuario `postgres` (el superusuario por defecto).

2.  **Creación de la Base de Datos y Usuario:**
    *   Puedes usar `psql` (la terminal interactiva de PostgreSQL) o una herramienta gráfica como `pgAdmin`.
    *   **Ejemplo usando `psql`:**
        ```sql
        -- Conéctate como superusuario (postgres)
        psql -U postgres

        -- Crea una nueva base de datos para tu proyecto
        CREATE DATABASE real_estate_db;

        -- Crea un nuevo usuario (opcional, pero buena práctica)
        CREATE USER fm_asesor WITH PASSWORD 'your_strong_password';

        -- Otorga todos los privilegios al nuevo usuario sobre la base de datos
        GRANT ALL PRIVILEGES ON DATABASE real_estate_db TO fm_asesor;

        -- Sal de psql
        \q
        ```
    *   **Nota:** Reemplaza `'your_strong_password'` con una contraseña segura.

3.  **Definición del Esquema Inicial (Tabla `properties`):**
    *   Necesitaremos una tabla para almacenar la información de las propiedades. Un esquema inicial podría ser:
        ```sql
        CREATE TABLE properties (
            id SERIAL PRIMARY KEY,
            address VARCHAR(255) NOT NULL,
            city VARCHAR(100),
            state VARCHAR(100),
            zip_code VARCHAR(20),
            price DECIMAL(15, 2),
            bedrooms INTEGER,
            bathrooms DECIMAL(4, 2),
            area_sqft DECIMAL(10, 2),
            property_type VARCHAR(50),
            listing_url TEXT,
            -- Agrega más columnas según los datos disponibles en el XLS
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        ```
    *   Este esquema es un punto de partida y se ajustará a medida que analicemos el contenido exacto del archivo XLS.

4.  **Conexión desde Python:**
    *   Utilizaremos la librería `psycopg2` para conectar Python con PostgreSQL.
    *   Deberás instalarla: `pip install psycopg2-binary`

---

## 🚀 Siguientes Pasos Propuestos (Resumen):

1.  **Crear la estructura de directorios:** `src/data_processing/`.
2.  **Instalar y configurar PostgreSQL localmente** (si aún no lo has hecho), incluyendo la creación de la base de datos `real_estate_db` y un usuario.
3.  **Implementar la lógica de limpieza inicial** en `src/data_processing/clean_data.py`, enfocándose en la lectura del XLS y la inspección básica.
4.  **Instalar `psycopg2-binary`** para la conexión a PostgreSQL.
5.  **Definir el esquema exacto de la tabla `properties`** una vez que hayamos inspeccionado el XLS.
