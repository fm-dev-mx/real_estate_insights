# Pending Tasks and Blockers

This document details the pending tasks and challenges for advancing the automation of identifying real estate properties with high investment potential.

---

## 🚧 Pending Tasks by Automation Stage

Currently, the **Inventory Data Collection** stage is complete and functional. The following stages require development:

### Step 2: Data Cleaning, Validation, and Normalization
*   **Task:** Define cleaning and validation rules for XLS data.
*   **Task:** Implement data processing (e.g., with Pandas).

### Step 3: Data Storage
*   **Task:** Decide on storage strategy (Supabase vs. temporary JSON).
*   **Task:** Design the database schema.

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

1.  **Perform the initial project commit** with the current structure and updated documentation.
2.  **Begin development of Step 2:** Data Cleaning, Validation, and Normalization. This will involve working in the `src/data_processing/` directory.
