# Automatización de Descarga de Inventario de Propiedades (Century 21 México)

Este script de Python automatiza el proceso de inicio de sesión en el portal de Century 21 México y la descarga del inventario de propiedades.

## 📊 Diagramas del Sistema

Estos diagramas proporcionan una hoja de ruta visual del proyecto Real Estate Insights, detallando tanto el estado actual de la implementación como los pasos de desarrollo futuros.

### 🗺️ Arquitectura General del Sistema

Este diagrama ilustra los componentes de alto nivel de todo el sistema, desde la adquisición de datos hasta la salida final.

```mermaid
%%{init: {'theme':'neutral'}}
%% This diagram provides a high-level overview of the entire Real Estate Insights system.
%% It shows the main components and their interactions, from data collection to analysis.

    subgraph Data Collection
        DC[download_inventory.py]
    end

    subgraph Data Processing
        DP[clean_data.py]
    end

    subgraph Data Storage
        DB[(PostgreSQL Database)]
    end

    subgraph Future Modules
        PS[Property Selection]
        PA[PDF Analysis]
        AI[AI Image Analysis]
        FO[Final Output Generation]
    end

    User --> DC
    DC --> RawExcel[Raw Excel Files]
    RawExcel --> DP
    DP --> DB
    DB --> PS
    PS --> PA
    PA --> AI
    AI --> FO
    FO --> User
```

### 🚀 Estado Actual del Proceso ETL

Este diagrama detalla las partes actualmente implementadas de la tubería ETL (Extraer, Transformar, Cargar), mostrando los scripts y sus interacciones.

```mermaid
%%{init: {'theme':'neutral'}}
%% This diagram details the current implementation of the ETL process.
%% It highlights the specific scripts and files involved in data collection, cleaning, and loading into the database.

    subgraph Implemented Modules
        A[User/Agent] --> B(src/data_collection/download_inventory.py)
        B --> C{Raw Excel Files<br>src/data_collection/downloads/}
        C --> D(src/data_processing/clean_data.py)
        D -- Cleans & Transforms --> E(PostgreSQL Database)
        E -- Credentials via --> F[.env file]
        F -- Verified by --> G(src/data_processing/verify_db_setup.py)
    end

    subgraph Key Interactions
        B -- Downloads --> C
        D -- Loads Data --> E
        E -- Reads Config --> F
        G -- Tests Connection --> E
    end
```

### ➡️ Pasos de Desarrollo Futuros

Este diagrama describe los módulos futuros planificados y su secuencia en la hoja de ruta del proyecto.

```mermaid
%%{init: {'theme':'neutral'}}
%% This diagram outlines the planned future modules and their sequence in the project roadmap.

    subgraph Future Development Steps
        DB[(PostgreSQL Database)] --> PS[Step 4: Top Property Selection]
        PS --> PA[Step 5: PDF Analysis]
        PA --> AI[Step 6: AI Image Analysis (Optional)]
        AI --> FO[Step 7: Final Output Generation]
        FO --> User[User/Agent]
    end

    subgraph Details
        PS -- Criteria --> Config[Configuration Files]
        PA -- Extracts Data --> PDF[Property Brochures (PDF)]
        AI -- Analyzes --> Images[Property Images]
        FO -- Generates --> Reports[Reports/CSV/Dashboards]
    end
```

## 🎯 Qué hace el script

1.  Navega a la página de inicio de sesión de Century 21 Online (`https://plus.21onlinemx.com/login2`).
2.  Rellena el formulario de inicio de sesión con las credenciales proporcionadas.
3.  Una vez autenticado, navega a la página de propiedades (`https://plus.21onlinemx.com/propiedades`).
4.  Hace clic en el botón "Descargar o Imprimir Inventario".
5.  Descarga el archivo `inventario.xls` directamente a una carpeta `descargas` dentro del directorio del script.

## ⚙️ Dependencias y Cómo Instalarlas

El script requiere las siguientes librerías de Python:

*   `selenium`: Para la automatización del navegador.
*   `requests`: Para realizar solicitudes HTTP (aunque actualmente no se usa para la descarga final, es una dependencia común).
*   `beautifulsoup4`: Para el análisis de HTML (actualmente no se usa directamente, pero es una dependencia común).

Para instalarlas, ejecuta el siguiente comando en tu terminal:

```bash
pip install -r requirements.txt
```

### WebDriver

Necesitarás el controlador del navegador (`chromedriver.exe` para Google Chrome) que coincida con la versión de tu navegador Chrome.

1.  **Verifica la versión de tu Chrome:** Abre Chrome, ve a `chrome://version` en la barra de direcciones y anota la versión principal (ej. `126`).
2.  **Descarga ChromeDriver:** Ve a [https://googlechromelabs.github.io/chrome-for-testing/#stable](https://googlechromelabs.github.io/chrome-for-testing/#stable).
3.  Busca la versión de ChromeDriver que coincida con la de tu Chrome y descarga el archivo `win64` (`chromedriver.exe`).
4.  **Coloca `chromedriver.exe`:** Descomprime el archivo descargado y coloca `chromedriver.exe` directamente en el mismo directorio que este script (`C:\Code\curl\`).

## 🚀 Cómo Configurar y Ejecutar el Script

1.  **Configura tus Credenciales:**
    El script lee el usuario y la contraseña de variables de entorno por seguridad. Debes configurarlas en tu terminal **antes de ejecutar el script**.

    *   **Si usas CMD:**
        ```cmd
        set C21_USUARIO=TU_USUARIO_REAL
        set C21_PSW=TU_PASSWORD_REAL
        ```
    *   **Si usas PowerShell:**
        ```powershell
        $env:C21_USUARIO="TU_USUARIO_REAL"
        $env:C21_PSW="TU_PASSWORD_REAL"
        ```
    **Asegúrate de reemplazar `TU_USUARIO_REAL` y `TU_PASSWORD_REAL` con tus credenciales reales.**

2.  **Ejecuta el Script:**
    Abre tu terminal, navega al directorio del script (`C:\Code\curl\`) y ejecuta:

    ```bash
    python descargar_inventario.py
    ```

    El script creará una carpeta `descargas` en el mismo directorio y guardará `inventario.xls` allí.

## ⚠️ Posibles Errores Comunes y Cómo Resolverlos

*   **`X Error: Las variables de entorno C21_USUARIO y C21_PSW no están configuradas.`**
    *   **Causa:** No configuraste las variables de entorno en tu terminal, o las configuraste incorrectamente, o las configuraste en una sesión de terminal diferente.
    *   **Solución:** Asegúrate de configurar `C21_USUARIO` y `C21_PSW` en la misma sesión de terminal desde la que ejecutas el script, usando los comandos `set` o `$env:` como se describe arriba.

*   **`X Error de WebDriver: ...` o `WebDriverException`**
    *   **Causa:** `chromedriver.exe` no está en el lugar correcto, o su versión no coincide con la de tu Chrome, o no se pudo iniciar el navegador.
    *   **Solución:** Verifica que `chromedriver.exe` esté en `C:\Code\curl\` y que su versión coincida con la de tu Chrome. Reinicia tu terminal y vuelve a intentarlo.

*   **`X Error: Tiempo de espera excedido al cargar la página o encontrar elementos.`**
    *   **Causa:** El script no pudo encontrar un elemento web (como un campo de texto o un botón) dentro del tiempo especificado (30 segundos). Esto puede deberse a cambios en el sitio web, problemas de carga de la página, o que el elemento no es visible/interactuable.
    *   **Solución:** Revisa el sitio web manualmente para ver si ha cambiado. Si el problema persiste, puede que necesitemos ajustar los selectores de Selenium o añadir esperas adicionales.

*   **`X Login fallido con Selenium. URL actual: ...`**
    *   **Causa:** Las credenciales son incorrectas, o el sitio web ha cambiado su proceso de inicio de sesión.
    *   **Solución:** Verifica tus credenciales. Si son correctas, el sitio web podría haber implementado nuevas validaciones o campos ocultos. Necesitaríamos una depuración más profunda.

## 💡 Recomendaciones de Uso

*   **No compartas tus credenciales:** Las variables de entorno son más seguras que el código, pero aún así, mantén tus credenciales privadas.
*   **Monitoreo:** Los sitios web pueden cambiar. Si el script deja de funcionar, es probable que el HTML o el flujo de navegación hayan sido modificados y necesite una actualización.
*   **Uso Responsable:** Utiliza este script de manera responsable y de acuerdo con los términos de servicio del sitio web.
