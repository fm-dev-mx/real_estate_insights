# Preguntas Clave para el Cliente: Nuevas Funcionalidades

Para continuar con la implementación de las nuevas funcionalidades, necesito tu dirección en los siguientes puntos. Por favor, selecciona la opción que mejor se ajuste a tus necesidades o proporciona una respuesta específica.

---

## 1. Gestión de PDFs: Acceso y Almacenamiento

*   **¿Cómo se accede a los PDFs de las propiedades?**
    a) La URL del PDF está directamente disponible en el inventario descargado.
    b) La URL del PDF se construye a partir del ID de la propiedad (ej. `https://portal.com/pdf/[ID].pdf`).
    c) Se requiere una navegación adicional o autenticación específica para acceder a los PDFs.

*   **¿Existe alguna autenticación adicional para descargar PDFs, diferente a la del login principal?**
    a) No, la sesión de login principal es suficiente.
    b) Sí, se requiere un token o credenciales adicionales.
    c) No estoy seguro.

*   **¿Cuál es la estructura deseada para almacenar los PDFs localmente?**
    a) `data/pdfs/[property_id].pdf`
    b) `data/pdfs/[año]/[mes]/[property_id].pdf`
    c) Otra (especificar).

---

## 2. Extracción y Comparación de Datos: Prioridad de Campos

*   **¿Cuáles son los 3-5 campos clave más importantes a extraer y comparar de los PDFs inicialmente?** (Ej. Precio, M2 Construcción, Recámaras, Baños, Antigüedad)
    a) Precio, M2 Construcción, Recámaras, Baños, Antigüedad.
    b) Precio, Dirección Completa, Tipo de Propiedad, Estatus.
    c) Otros (especificar).

---

## 3. Análisis Visual: Enfoque Inicial

*   **Para el análisis visual, ¿preferimos empezar con una heurística simple (ej. contar imágenes, verificar resolución) o intentar un modelo de ML básico (ej. clasificar calidad de imagen)?**
    a) Heurística simple para un prototipo rápido.
    b) Modelo de ML básico (requerirá más tiempo y datos de entrenamiento).

---

## 4. Control de Versiones: Identificación de Usuario

*   **¿Cómo identificamos al "usuario" que realiza un cambio en el sistema?**
    a) Un campo de texto libre donde el usuario introduce su nombre/ID.
    b) Se asume un usuario genérico ("Sistema", "Usuario Manual").
    c) Se integrará con un sistema de autenticación de usuarios existente (especificar).

---

**Tus Respuestas:**

*   **1. Gestión de PDFs:**
    *   Acceso: [ ] a) [x] b) [ ] c) `https://plus.21onlinemx.com/ft/[id]/DTF/273/40120`
    *   Autenticación adicional: [x] a) [ ] b) [ ] c)
    *   Estructura de almacenamiento: [x] a) [ ] b) [ ] c)

*   **2. Extracción y Comparación de Datos:**
    *   Campos clave: [ ] a) [ ] b) [x] c) `precio, m2_construccion, m2_terreno, recamaras, banios, edad, descripcion`

*   **3. Análisis Visual:**
    *   Enfoque: [x] a) [ ] b)

*   **4. Control de Versiones:**
    *   Identificación de usuario: [ ] a) [x] b) [ ] c)