# Automated Real Estate Property Insights

This project aims to build a comprehensive n8n automation to identify real estate properties with high investment potential. The process involves automated data extraction, processing, analysis, and generating a final output with the most relevant properties.

## 🎯 Automation Flow (n8n)

The complete automation flow consists of the following steps:

### Step 1: Inventory Data Collection (Complete)

This Python script automates the login process to a real estate portal and the download of property inventory in XLS format. It includes interaction with download submenus. The script now also handles automatic conversion of `.xls` files to `.xlsx` for improved data processing compatibility.

**Script location:** `src/data_collection/download_inventory.py`

### Step 2: Data Cleaning, Validation, and Normalization (In Progress)

We have defined a detailed PostgreSQL database schema for property data and are now focusing on implementing the data cleaning, validation, and normalization logic. This involves processing the downloaded Excel files, cleaning inconsistencies, normalizing data formats, and preparing data for storage.

**Script location:** `src/data_processing/clean_data.py`

### Step 3: Data Storage (In Progress)

This step involves persisting processed data into a PostgreSQL database. The database schema has been designed to support complex queries and future scalability. The `clean_data.py` script now includes functionality to load the cleaned data directly into the `properties` table, handling updates for existing records.

### Future Steps:

*   **Step 4: Top Property Selection:** Filtering and selecting high-potential properties based on configurable criteria.
*   **Step 5: PDF Analysis:** Extracting key data from property brochures in PDF format.
*   **Step 6 (Optional): AI Image Analysis:** Exploring the feasibility of using AI for extracting features from property images.
*   **Step 7: Final Output Generation:** Creating a consolidated ranking, detailed reports, or CSV files with selected properties.

## ⚙️ Dependencies and Installation (Step 1: Data Collection)

The data collection script (`src/data_collection/download_inventory.py`) requires the following Python library:

*   `selenium`: For browser automation.

To install it, run the following command from the project root:

```bash
pip install -r src/data_collection/requirements.txt
```

### WebDriver

You will need the browser driver (`chromedriver.exe` for Google Chrome) that matches your Chrome browser version.

1.  **Check your Chrome version:** Open Chrome, go to `chrome://version`, and note the major version (e.g., `126`).
2.  **Download ChromeDriver:** Go to [https://googlechromelabs.github.io/chrome-for-testing/#stable](https://googlechromelabs.github.io/chrome-for-testing/#stable).
3.  Find the ChromeDriver version that matches your Chrome and download the `win64` file (`chromedriver.exe`).
4.  **Place `chromedriver.exe`:** Unzip the downloaded file and place `chromedriver.exe` in the project's `src/data_collection/` directory (`C:\Code\curl\src\data_collection\`).

## ⚙️ Database Configuration

For data processing and storage, the project connects to a PostgreSQL database. The connection details are read from environment variables for security and flexibility. You must configure the following environment variables before running the data processing scripts:

*   `REI_DB_NAME`: Name of your PostgreSQL database (e.g., `real_estate_db`)
*   `REI_DB_USER`: Username for connecting to the database (e.g., `fm_asesor`)
*   `REI_DB_PASSWORD`: Password for the database user.
*   `REI_DB_HOST`: Host where your PostgreSQL database is running (e.g., `127.0.0.1` for local).
*   `REI_DB_PORT`: Port number for the database connection (e.g., `5432`).

Refer to `docs/next_steps_data_processing.md` for detailed instructions on setting up PostgreSQL and configuring these environment variables.

## 🚀 How to Configure and Run the Script (Step 1: Data Collection)

1.  **Configure Your Credentials:**
    The script reads the username and password from environment variables for security. You must configure them in your terminal **before running the script**.

    *   **If using CMD:**
        ```cmd
        set C21_USERNAME=YOUR_REAL_USERNAME
        set C21_PSW=YOUR_REAL_PASSWORD
        ```
    *   **If using PowerShell:**
        ```powershell
        $env:C21_USERNAME="YOUR_REAL_USERNAME"
        $env:C21_PSW="YOUR_REAL_PASSWORD"
        ```
    **Ensure you replace `YOUR_REAL_USERNAME` and `YOUR_REAL_PASSWORD` with your actual credentials.**

2.  **Run the Script:**
    Open your terminal, navigate to the script's directory (`C:\Code\curl\src\data_collection\`) and run:

    ```bash
    python download_inventory.py
    ```

    The script will create a `downloads` folder in the same directory and save `inventario.xls` there. It will also create a `logs` folder for execution records and a `screenshots` folder for debugging screenshots.

## ⚠️ Considerations and Common Errors

*   **Environment Variables Not Configured:** If the script does not find `C21_USERNAME` or `C21_PSW`.
    *   **Solution:** Ensure you configure the environment variables in the same terminal session from which you run the script.

*   **WebDriver Error:** Issues with `chromedriver.exe` (not found, incorrect version, etc.).
    *   **Solution:** Verify that `chromedriver.exe` is in `src/data_collection/` and its version matches your Chrome.

*   **Web Portal Changes:** The real estate portal may change its HTML structure or navigation flow, which might require adjustments to the script.
    *   **Solution:** Review detailed logs in `src/data_collection/logs/` and screenshots in `src/data_collection/screenshots/` to identify the exact point of failure. You might need to adjust XPath selectors in `src/data_collection/download_inventory.py`.

## 💡 Usage Recommendations

*   **Credentials:** Use environment variables for enhanced security.
*   **Maintenance:** The script may require periodic updates due to changes in the web portal.
*   **Responsible Use:** Use this script in accordance with the portal's terms of service.
*   **Debugging:** Logs and screenshots are key tools for troubleshooting.
