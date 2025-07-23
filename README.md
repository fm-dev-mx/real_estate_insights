# Automated Real Estate Property Insights

This project aims to build a comprehensive automation to identify real estate properties with high investment potential. The process involves automated data extraction, processing, analysis, and generating a final output with the most relevant properties.

## 🚀 How to Run the Application

To run the main dashboard application, execute the following command from the project root directory:

```bash
python run_dashboard.py
```

This script handles all necessary setup, including configuring the Python path, and launches the Streamlit interactive dashboard.

## 🎯 Project Workflow

The complete automation flow consists of the following steps:

### Step 1: Inventory Data Collection
Automates the login to a real estate portal and downloads the property inventory.

**Script:** `src/data_collection/download_inventory.py`

### Step 2: Data Cleaning, Validation, and Storage
Cleans, transforms, and loads property data into the PostgreSQL database. This logic is now modularized for clarity and maintenance.

**Modules:**
- `src/data_processing/data_cleaner.py`
- `src/data_processing/excel_converter.py`
- `src/data_access/property_repository.py`

### Step 3: Interactive Property Visualization
An interactive Streamlit dashboard to filter and visualize properties based on various criteria.

**Main App:** `src/visualization/dashboard_app.py`

For a detailed discussion on the project's future roadmap, please refer to [docs/next_steps_project_roadmap.md](docs/next_steps_project_roadmap.md).

## 📊 System Diagrams

### 🗺️ Overall System Architecture

```mermaid
graph TD
    subgraph User Interaction
        User[Usuario] --> Runner(run_dashboard.py)
    end

    subgraph Application Execution
        Runner -- Sets PYTHONPATH & Executes --> Streamlit(Streamlit Engine)
        Streamlit -- Runs --> DashboardApp(visualization/dashboard_app.py)
    end

    subgraph Core Modules
        DashboardApp -- Uses --> Logic(visualization/dashboard_logic.py)
        DashboardApp -- Uses --> UI(visualization/ui_components.py)
        DashboardApp -- Interacts with --> Repo(data_access/property_repository.py)
        Repo -- Manages --> DB[(PostgreSQL Database)]
    end

    subgraph Data Flow
        RawExcel[Archivos Excel Crudos] --> Cleaner(data_processing/data_cleaner.py)
        Cleaner -- Uses --> Converter(data_processing/excel_converter.py)
        Cleaner -- Uses --> Validator(data_processing/data_validator.py)
        Cleaner -- Loads Data --> Repo
    end

    subgraph Configuration
        EnvFile[.env] -- Provides Credentials --> Repo
        EnvFile -- Provides Settings --> DashboardApp
    end

    style Runner fill:#cde4f7,stroke:#333,stroke-width:2px
    style Streamlit fill:#ff4b4b,stroke:#333,stroke-width:2px
```

### 🚀 Current ETL Process State

```mermaid
graph TD
    subgraph Execution Flow
        A[Usuario] --> B(run_dashboard.py)
        B -- Launches --> C(streamlit run src/visualization/dashboard_app.py)
    end

    subgraph Data Initialization
        D[Agente] --> E(src/data_collection/download_inventory.py)
        E -- Downloads --> F{Archivos Excel Crudos}
        F --> G(src/data_processing/data_cleaner.py)
        G -- Cleans & Transforms --> H(data_access/property_repository.py)
        H -- Loads Data --> I[(PostgreSQL Database)]
    end

    subgraph Dashboard Interaction
        C -- Displays Interactive --> J[Dashboard UI]
        J -- Filters Data via --> H
        I -- Credentials via --> K[.env file]
    end

    subgraph Setup
        L[src/db_setup/create_db_table.py] -- Creates Table --> I
    end
```

### ➡️ Future Development Steps

```mermaid
graph TD
    subgraph Current Foundation
        A[(PostgreSQL Database)]
        B[Modular Codebase]
    end

    subgraph Next Development Steps
        A --> C{Step 1: Unit & Integration Testing}
        B --> C
        C -- Ensures Reliability --> D{Step 2: Advanced Visualizations}
        D -- e.g., Maps, Charts --> E{Step 3: PDF & Image Analysis}
        E -- Extracts Data --> F{Step 4: Reporting Engine}
        F -- Generates --> G[PDF/CSV Reports]
        G --> H[User/Agent]
    end

    subgraph Details
        C -- Validates --> Modules[data_cleaner, property_repository, etc.]
        D -- Enhances --> Dashboard[Dashboard UI]
        E -- Processes --> Files[Property Brochures, Images]
    end
```

## ⚙️ Dependencies and Installation

Install the required Python libraries by running:

```bash
pip install -r src/data_collection/requirements.txt
```

### WebDriver
Ensure `chromedriver.exe` (for Google Chrome) matches your browser version and is placed in the `src/data_collection/` directory.

### Database Configuration
Create a `.env` file in the project root with your PostgreSQL credentials. Refer to `.env.example` for the required variables.

To set up the database table, run:
```bash
python src/db_setup/create_db_table.py
```

## ⚠️ Considerations
- **Environment Variables:** Ensure all required variables are set in your `.env` file.
- **WebDriver:** Keep `chromedriver.exe` updated and correctly placed.
- **Web Portal Changes:** The real estate portal's structure may change, requiring script adjustments.