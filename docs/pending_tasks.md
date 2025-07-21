# Pending Tasks and Blockers

This document details the pending tasks and challenges for advancing the automation of identifying real estate properties with high investment potential.

---

## 🚧 Pending Tasks by Automation Stage

Currently, the **Inventory Data Collection** stage is complete and functional. We have also made significant progress in defining the schema for data storage. The following stages require development:

### Step 2: Data Cleaning, Validation, and Normalization
*   **Task:** Implement data processing (e.g., with Pandas) based on the defined schema.
*   **Task:** Define and apply cleaning and validation rules for the extracted data.

### Step 3: Data Storage
*   **Task:** Create the `properties` table in the PostgreSQL database based on the finalized schema.
*   **Task:** Implement data loading from cleaned DataFrames into the PostgreSQL database.

### Step 4: Top Property Selection
*   **Task:** Establish investment criteria and their weighting.
*   **Task:** Implement a scoring or ranking system.

### Step 5: PDF Analysis
*   **Task:** Research tools for text and structured data extraction from PDFs.
*   **Task:** Define specific data to extract from brochures.

### Step 6 (Optional): AI Image Analysis
*   **Task:** Evaluate technical and economic feasibility of AI image analysis.
*   **Task:** Define objectives for image analysis.

### Step 7: Final Output Generation
*   **Task:** Decide on the format and content of the final output.
*   **Task:** Explore visualization or integration options.

---

## ✅ Suggested Next Steps

1.  **Create the `properties` table in PostgreSQL** using the finalized schema.
2.  **Implement data cleaning and normalization logic** in `src/data_processing/clean_data.py` to transform raw XLS data into the defined schema.
3.  **Implement data loading** from the cleaned data into the PostgreSQL database.
