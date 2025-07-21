# Propuesta de Esquema de Datos para la Base de Datos de Propiedades

Este documento detalla el análisis de las columnas del archivo `inventario.xls` (ahora `inventario.xlsx`) y propone un esquema inicial para la tabla `properties` en la base de datos PostgreSQL. Se justifica la inclusión o exclusión de cada columna basándose en su relevancia para el análisis de propiedades y la calidad de los datos observada en la inspección inicial.

---

## Análisis de Columnas y Propuesta de Esquema

| Nombre de Columna | Tipo de Dato (Original) | Descripción Breve | ¿Incluir en DB? | Justificación |
| :---------------- | :---------------------- | :---------------- | :-------------- | :------------ |
| `id` | `int64` | Identificador único de la propiedad. | Sí | Clave primaria, esencial para identificar y relacionar propiedades. |
| `fechaAlta` | `object` | Fecha y hora de alta de la propiedad en el sistema. | Sí | Importante para análisis de antigüedad de listados y tendencias. Necesitará conversión a tipo `TIMESTAMP`. |
| `status` | `object` | Estado actual de la propiedad (ej. enPromocion). | Sí | Crucial para filtrar propiedades activas. |
| `tipoOperacion` | `object` | Tipo de operación (ej. Venta, Renta). | Sí | Fundamental para clasificar las propiedades. |
| `tipoDeContrato` | `object` | Tipo de contrato asociado a la propiedad. | Sí | Información relevante para el contexto legal/comercial. |
| `enInternet` | `float64` | Indicador si la propiedad está publicada en internet. | Sí | Útil para filtrar propiedades visibles al público. Muchos nulos (108/263), pero puede ser un `boolean` o `int` (0/1). |
| `clave` | `object` | Clave interna de la propiedad. | Sí | Identificador secundario o de referencia interna. |
| `claveOficina` | `object` | Clave de la oficina asociada a la propiedad. | Sí | Útil para segmentación por oficina. Muchos nulos (194/263), pero puede ser relevante si se completa. |
| `subtipoPropiedad` | `object` | Subtipo de propiedad (ej. Casa, Departamento, Terreno). | Sí | Clasificación detallada de la propiedad. |
| `numeroLlaves` | `object` | Número de llaves. | No | Muchos nulos (199/263) y probablemente no es un dato crítico para el análisis de inversión. |
| `calle` | `object` | Nombre de la calle de la propiedad. | Sí | Parte de la dirección, esencial para la ubicación. |
| `numero` | `object` | Número exterior de la propiedad. | Sí | Parte de la dirección. Pocos nulos (2/263), se pueden imputar o manejar. |
| `colonia` | `object` | Colonia o barrio de la propiedad. | Sí | Parte de la dirección, importante para la ubicación geográfica. |
| `municipio` | `object` | Municipio de la propiedad. | Sí | Parte de la dirección, importante para la ubicación geográfica. |
| `latitud` | `float64` | Latitud de la propiedad. | Sí | Crucial para análisis geoespacial. Pocos nulos (2/263), se pueden imputar o manejar. |
| `longitud` | `float64` | Longitud de la propiedad. | Sí | Crucial para análisis geoespacial. Pocos nulos (2/263), se pueden imputar o manejar. |
| `codigoPostal` | `int64` | Código postal de la propiedad. | Sí | Parte de la dirección, útil para segmentación geográfica. |
| `precio` | `float64` | Precio de la propiedad. | Sí | Dato fundamental para el análisis de inversión. Pocos nulos (2/263), se pueden imputar o manejar. |
| `comision` | `float64` | Comisión de la propiedad. | Sí | Relevante para el análisis financiero. Pocos nulos (2/263), se pueden imputar o manejar. |
| `comisionACompartirInmobiliariasExternas` | `float64` | Comisión a compartir con inmobiliarias externas. | Sí | Relevante para el análisis financiero. Muchos nulos (111/263), pero puede ser importante si se completa. |
| `m2C` | `float64` | Metros cuadrados de construcción. | Sí | Dato clave para el análisis de valor por metro cuadrado. Algunos nulos (25/263), se pueden imputar o manejar. |
| `m2T` | `float64` | Metros cuadrados de terreno. | Sí | Dato clave para el análisis de valor por metro cuadrado. Pocos nulos (2/263), se pueden imputar o manejar. |
| `recamaras` | `float64` | Número de recámaras. | Sí | Característica importante de la propiedad. Muchos nulos (163/263), pero esencial para el análisis. Se necesitará estrategia de imputación o manejo de nulos. |
| `banios` | `float64` | Número de baños. | Sí | Característica importante de la propiedad. Muchos nulos (148/263), pero esencial para el análisis. Se necesitará estrategia de imputación o manejo de nulos. |
| `mediosBanios` | `float64` | Número de medios baños. | Sí | Característica importante de la propiedad. Muchos nulos (187/263), pero puede ser relevante. Se necesitará estrategia de imputación o manejo de nulos. |
| `cuotaMantenimiento` | `float64` | Cuota de mantenimiento. | No | Todos nulos (263/263). No aporta valor si no hay datos. |
| `cocina` | `object` | Indicador de si tiene cocina. | Sí | Característica relevante. Muchos nulos (200/263), pero puede ser un `boolean` o `int` (0/1). |
| `nivelesConstruidos` | `float64` | Número de niveles construidos. | Sí | Característica importante. Muchos nulos (160/263), pero esencial para el análisis. Se necesitará estrategia de imputación o manejo de nulos. |
| `edad` | `float64` | Edad de la propiedad. | Sí | Relevante para el análisis de depreciación y estado. Algunos nulos (27/263), se pueden imputar o manejar. |
| `estacionamientos` | `float64` | Número de estacionamientos. | Sí | Característica importante. Muchos nulos (199/263), pero esencial para el análisis. Se necesitará estrategia de imputación o manejo de nulos. |
| `institucionHipotecaria` | `object` | Institución hipotecaria. | No | Casi todos nulos (262/263). No aporta valor si no hay datos. |
| `descripcion` | `object` | Descripción de la propiedad. | Sí | Texto libre importante para análisis cualitativo. Pocos nulos (2/263), se pueden manejar. |
| `nombre` | `object` | Nombre del agente/contacto. | Sí | Útil para atribución y contacto. |
| `apellidoP` | `object` | Apellido paterno del agente/contacto. | Sí | Útil para atribución y contacto. |
| `apellidoM` | `object` | Apellido materno del agente/contacto. | Sí | Útil para atribución y contacto. |

---

## Resumen del Esquema Propuesto para `properties` (PostgreSQL)

Basado en el análisis anterior, el esquema inicial para la tabla `properties` en PostgreSQL podría ser el siguiente. Los tipos de datos son una propuesta y pueden ajustarse durante la implementación.

```sql
CREATE TABLE properties (
    id INTEGER PRIMARY KEY,
    fecha_alta TIMESTAMP,
    status VARCHAR(50),
    tipo_operacion VARCHAR(50),
    tipo_contrato VARCHAR(50),
    en_internet BOOLEAN,
    clave VARCHAR(100),
    clave_oficina VARCHAR(100),
    subtipo_propiedad VARCHAR(100),
    calle VARCHAR(255),
    numero VARCHAR(50),
    colonia VARCHAR(255),
    municipio VARCHAR(255),
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    codigo_postal VARCHAR(10),
    precio DECIMAL(15, 2),
    comision DECIMAL(15, 2),
    comision_compartir DECIMAL(15, 2),
    m2_construccion DECIMAL(10, 2),
    m2_terreno DECIMAL(10, 2),
    recamaras INTEGER,
    banios DECIMAL(4, 2),
    medios_banios DECIMAL(4, 2),
    cocina BOOLEAN,
    niveles_construidos INTEGER,
    edad INTEGER,
    estacionamientos INTEGER,
    descripcion TEXT,
    nombre_agente VARCHAR(100),
    apellido_p_agente VARCHAR(100),
    apellido_m_agente VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Consideraciones Adicionales y Soluciones Propuestas:**

1.  **Manejo de Nulos en Columnas Clave (`recamaras`, `banios`, `estacionamientos`, `nivelesConstruidos`, `cocina`, `enInternet`, `claveOficina`):**
    *   **Problema:** Estas columnas son importantes para el análisis, pero presentan un alto porcentaje de valores nulos.
    *   **Soluciones Propuestas:**
        *   **a) Imputación por Valor Cero:** Para características como `recamaras`, `banios`, `estacionamientos`, `nivelesConstruidos`, si un valor nulo significa "no tiene" (ej. 0 recámaras, 0 baños), podemos imputar los nulos con `0`. Esto es común y mantiene la integridad del tipo numérico.
        *   **b) Imputación por Moda/Mediana:** Para `edad` (si el nulo significa desconocido o no aplica), se podría imputar con la mediana o moda si hay una distribución clara.
        *   **c) Valores Booleanos por Defecto:** Para `enInternet` y `cocina`, si el nulo implica "no" o "desconocido", se pueden imputar como `FALSE` o `0`.
        *   **d) Mantener Nulos y Manejar en Consultas:** Permitir `NULL` en la base de datos y manejar los casos nulos durante las consultas o el análisis. Esto es más flexible pero requiere cuidado en cada uso.
        *   **e) Eliminar Filas con Nulos Críticos:** Si el porcentaje de nulos es muy alto y el dato es indispensable, se podría considerar eliminar las filas con nulos en esas columnas, aunque esto puede reducir el tamaño del dataset. (Menos recomendable para este caso).
    *  **Respuesta:** c y d.
2.  **Normalización de Nombres de Columnas:**
    *   **Problema:** Los nombres de columna originales (`fechaAlta`, `tipoDeContrato`, `comisionACompartirInmobiliariasExternas`, `m2C`, `m2T`, `apellidoP`, `apellidoM`) no siguen una convención uniforme (`camelCase` mezclado con `PascalCase`) y algunos son muy largos.
    *   **Soluciones Propuestas:**
        *   **a) `snake_case` Consistente:** Convertir todos los nombres de columna a `snake_case` (ej. `fecha_alta`, `tipo_de_contrato`, `comision_a_compartir_inmobiliarias_externas`, `m2_construccion`, `m2_terreno`, `apellido_paterno_agente`, `apellido_materno_agente`). Esto mejora la legibilidad y es una práctica común en bases de datos relacionales.
        *   **b) Acortar Nombres Largos:** Para nombres excesivamente largos como `comisionACompartirInmobiliariasExternas`, se puede usar una abreviatura clara como `comision_compartir_externas` o `comision_externa`.
        *   **c) Renombrar Agente:** Consolidar `nombre`, `apellidoP`, `apellidoM` en una tabla `agentes` separada si se espera que los agentes tengan más atributos o si la relación es de muchos a muchos. Por ahora, mantenerlos en la tabla `properties` como `nombre_agente`, `apellido_paterno_agente`, `apellido_materno_agente` es aceptable para simplificar.
    *  **Respuesta:** a, b y c.
3.  **Tipos de Datos y Precisión:**
    *   **Problema:** Asegurar que los tipos de datos en PostgreSQL sean los más adecuados para el almacenamiento y las operaciones.
    *   **Soluciones Propuestas:**
        *   **a) `TIMESTAMP` para Fechas:** Confirmar `fechaAlta` como `TIMESTAMP` o `TIMESTAMP WITH TIME ZONE` si la zona horaria es relevante.
        *   **b) `DECIMAL` para Moneda y Medidas:** Usar `DECIMAL(precision, scale)` para `precio`, `comision`, `m2C`, `m2T`, `latitud`, `longitud` para evitar problemas de precisión con `FLOAT`. La precisión actual (`DECIMAL(15, 2)`, `DECIMAL(10, 8)`, `DECIMAL(11, 8)`) parece adecuada.
        *   **c) `INTEGER` para Conteo:** Usar `INTEGER` para `recamaras`, `niveles_construidos`, `edad`, `estacionamientos`. Para `banios` y `mediosBanios`, si pueden ser fraccionarios (ej. 1.5 baños), `DECIMAL(4,2)` es apropiado; de lo contrario, `INTEGER`.
        *   **d) `BOOLEAN` para Indicadores:** Usar `BOOLEAN` para `enInternet` y `cocina` (mapeando 0/1 o texto a `TRUE`/`FALSE`).
        *   **e) `TEXT` para Descripciones Largas:** `descripcion` como `TEXT` es adecuado para contenido variable y potencialmente largo.
    *  **Respuesta:** a, b, c, d y e.
    *   **Nota:** Los tipos de datos propuestos son una guía inicial y pueden ajustarse según las necesidades específicas de la aplicación y el análisis posterior.
4.  **Columnas con Datos Casi Nulos (`numeroLlaves`, `cuotaMantenimiento`, `institucionHipotecaria`):**
    *   **Problema:** Estas columnas tienen casi todos sus valores nulos.
    *   **Soluciones Propuestas:**
        *   **a) Excluir Definitivamente:** Si no se espera que estos datos se completen en el futuro o no son críticos para el análisis actual, la mejor práctica es excluirlos del esquema para mantener la base de datos limpia y eficiente. (Esta es la recomendación actual y la más fuerte).
        *   **b) Tabla Separada (si la información es valiosa pero escasa):** Si en el futuro se espera que `institucionHipotecaria` o `cuotaMantenimiento` sean relevantes para un subconjunto de propiedades, se podría considerar una tabla separada (`property_details` o `financial_details`) con una relación uno a uno o uno a muchos con `properties`. Por ahora, la exclusión es más simple.
    *  **Respuesta:** a.
5.  **Auditoría de Registros (`created_at`, `updated_at`):**
    *   **Problema:** Necesidad de rastrear cuándo se insertó o modificó un registro.
    *   **Soluciones Propuestas:**
        *   **a) Usar `TIMESTAMP WITH TIME ZONE` y `DEFAULT CURRENT_TIMESTAMP`:** Esto ya está propuesto y es una excelente práctica. Asegura que las marcas de tiempo se almacenen con información de zona horaria y se actualicen automáticamente.
    *  **Respuesta:** a.

---

## Próximos Pasos

1.  **Tu Decisión sobre las Soluciones:** Por favor, revisa las "Soluciones Propuestas" para cada consideración (a, b, c, etc.) e indica cuál prefieres para cada punto.
2.  **Creación de la Tabla:** Una vez que tengamos el esquema finalizado, procederemos a crear esta tabla en la base de datos PostgreSQL.
3.  **Implementación de la Limpieza y Carga:** Con el esquema definido, podemos empezar a escribir la lógica en `clean_data.py` para transformar los datos del XLS a este formato, manejando nulos, tipos de datos y estandarización.
