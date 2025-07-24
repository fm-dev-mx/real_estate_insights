# Import Errors and Fixes in Pytest

This document describes the import errors encountered when running `pytest` and the solutions applied to resolve them.

## 1. Original Error: `ModuleNotFoundError`

When running `pytest`, the following `ModuleNotFoundError` errors were encountered:

```
ERROR collecting tests/test_dashboard_logic.py ... ModuleNotFoundError: No module named 'data_collection'
ERROR collecting tests/test_data_cleaner.py ... ModuleNotFoundError: No module named 'utils'
ERROR collecting tests/test_property_repository.py ... ModuleNotFoundError: No module named 'data_access'
```

## 2. Fixes Applied

### a) Absolute Import Paths

The import paths in the `src` files were modified to be absolute from the project root (`src`).

**Before:**
```python
# src/visualization/dashboard_logic.py
from data_collection.download_pdf import PDF_DOWNLOAD_BASE_DIR

# src/data_processing/data_cleaner.py
from ..utils.constants import DB_COLUMNS

# src/data_access/property_repository.py
from .database_connection import get_db_connection
```

**After:**
```python
# src/visualization/dashboard_logic.py
from src.data_collection.download_pdf import PDF_DOWNLOAD_BASE_DIR

# src/data_processing/data_cleaner.py
from src.utils.constants import DB_COLUMNS

# src/data_access/property_repository.py
from src.data_access.database_connection import get_db_connection
```

### b) `pytest.ini` Configuration

The `pytest.ini` file was created in the project root with the following configuration to tell `pytest` where to find the `src` modules:

```ini
[pytest]
pythonpath = src
```

## 3. Final Result

After applying these fixes, all tests are collected and pass successfully.

```
============================= 25 passed in 16.00s =============================
```