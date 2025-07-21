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
        psql -U postgres -d postgres

        -- Crea una nueva base de datos para tu proyecto
        CREATE DATABASE real_estate_db;

        -- Crea un nuevo usuario (opcional, pero buena práctica)
        CREATE USER fm_asesor WITH PASSWORD 'your_strong_password';

        -- Otorga todos los privilegios al nuevo usuario sobre la base de datos
        GRANT ALL PRIVILEGES ON DATABASE real_estate_db TO fm_asesor;

        -- Otorga permisos para crear tablas en el esquema public
        GRANT CREATE ON SCHEMA public TO fm_asesor;
        GRANT USAGE ON SCHEMA public TO fm_asesor;

        -- Sal de psql
        \q
        ```
    *   **Nota:** Reemplaza `'your_strong_password'` con una contraseña segura.

3.  **Definición del Esquema Inicial (Tabla `properties`):**
    *   El esquema final para la tabla `properties` se encuentra detallado en `docs/data_schema_proposal.md`.

4.  **Configuración de Variables de Entorno para la Base de Datos:**
    Para que los scripts de Python puedan conectarse a la base de datos sin requerir interacción manual, es necesario configurar las siguientes variables de entorno:

    *   `REI_DB_NAME`: Nombre de la base de datos (ej. `real_estate_db`)
    *   `REI_DB_USER`: Nombre de usuario de la base de datos (ej. `fm_asesor`)
    *   `REI_DB_PASSWORD`: Contraseña del usuario de la base de datos.
    *   `REI_DB_HOST`: Host de la base de datos (ej. `127.0.0.1`)
    *   `REI_DB_PORT`: Puerto de la base de datos (ej. `5432`)

    **Cómo configurar las variables de entorno (en Windows):**

    **Opción A: Para la sesión actual de la terminal (temporal)**

    *   **Si usas CMD (Símbolo del sistema):**
        ```cmd
        set REI_DB_NAME=real_estate_db
        set REI_DB_USER=fm_asesor
        set REI_DB_PASSWORD=Tu_Contraseña_Real_Aqui
        set REI_DB_HOST=127.0.0.1
        set REI_DB_PORT=5432
        ```

    *   **Si usas PowerShell:**
        ```powershell
        $env:REI_DB_NAME="real_estate_db"
        $env:REI_DB_USER="fm_asesor"
        $env:REI_DB_PASSWORD="Tu_Contraseña_Real_Aqui"
        $env:REI_DB_HOST="127.0.0.1"
        $env:REI_DB_PORT="5432"
        ```
        (Recuerda que estas variables solo durarán mientras la ventana de la terminal esté abierta).

    **Opción B: Configuración permanente (requiere reiniciar la terminal)**

    1.  Busca "Editar las variables de entorno del sistema" en el menú de inicio de Windows y ábrelo.
    2.  Haz clic en "Variables de entorno...".
    3.  En la sección "Variables de usuario" (para tu usuario) o "Variables del sistema" (para todos los usuarios), haz clic en "Nueva..." para añadir cada variable con su nombre y valor correspondientes.

---

## 🚀 Siguientes Pasos Propuestos (Resumen):

1.  **Instalar y configurar PostgreSQL localmente** (si aún no lo has hecho), incluyendo la creación de la base de datos `real_estate_db` y un usuario `fm_asesor` con los permisos adecuados.
2.  **Configurar las variables de entorno** `REI_DB_NAME`, `REI_DB_USER`, `REI_DB_PASSWORD`, `REI_DB_HOST`, `REI_DB_PORT`.
3.  **Ejecutar `src/data_processing/create_db_table.py`** para crear la tabla `properties` en PostgreSQL.
4.  **Ejecutar `src/data_processing/clean_data.py`** para limpiar, transformar y cargar los datos del inventario en la base de datos.
5.  **Verificar la integridad de los datos** en la base de datos PostgreSQL.
