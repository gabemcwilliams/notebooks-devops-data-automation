# DattoRMM Data Ingestion and Transformation Pipelines

## Project Overview

This project contains a series of production-grade scripts designed to extract, transform, and load (ETL) device data,
filters, and patch policies from the DattoRMM platform. Data is ingested either into structured CSVs or directly into a
MongoDB database for further processing and analysis.

It demonstrates end-to-end data engineering workflows, including API tokenization, pagination handling, CSV ingestion
and merging, data standardization, and auditability enhancements. The pipelines also support feature engineering steps
necessary for machine learning readiness.

---

## Features

- **API Data Ingestion**
    - Extracts device and filter data via authenticated DattoRMM API calls.
    - Handles pagination and dynamic schema ingestion.

- **MongoDB Integration**
    - Loads structured device and audit records into MongoDB collections.
    - Supports upsert operations and incremental enrichment of device documents.

- **CSV Data Processing**
    - Merges and aligns multiple device exports, managing non-standard column schemas.
    - Appends critical metadata such as file creation timestamps and policy mappings.

- **PowerShell Automation Scripts**
    - Adds missing creation date fields and patch policy relationships to exported datasets.
    - Automates CSV restructuring to ensure daily deltas are accurate and traceable.

- **Feature Engineering Preparation**
    - Normalizes fields for downstream machine learning workflows.
    - Generates new analytical columns such as device online duration, last reboot delta, and offline status over time.

---

## Repository Structure

```
/api_ingestion/
    pull_dattormm_devices.py
    pull_dattormm_filters.py
    pull_dattormm_audit_info.py

/mongo_ingestion/
    seed_devices.py
    seed_audit_info.py

/csv_processing/
    add_creation_date.ps1
    add_patch_policy.ps1
    merge_device_csvs.py

/ml_preparation/
    device_feature_engineering.py

/config/
    env.ini.example

/exports/
    (generated files stored here)

README.md
requirements.txt
```

---

## Technologies Used

- Python 3.x
- Pandas
- NumPy
- Requests
- PyMongo
- PowerShell
- MongoDB (local and remote)
- Matplotlib and Seaborn (for data inspection)

---

## Key Highlights

- **Real-world SaaS API handling** with authentication and pagination.
- **Production-grade ingestion pipelines** targeting structured databases.
- **Metadata-first design** supporting compliance and audit tracking.
- **Data cleaning and standardization** for multi-source CSV datasets.
- **Modular PowerShell scripting** integrated into ingestion workflows.
- **Feature engineering** focused on operational device metrics.

---

## Setup Instructions

1. Clone this repository.
2. Populate `config/env.ini` with your API credentials and MongoDB connection settings.
3. Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Execute scripts as needed based on ingestion target (CSV or MongoDB).

---

## Future Improvements

- Integrate robust logging with Loguru.
- Add retry logic and better error handling for API instability.
- Expand feature engineering for patch compliance trend analysis.

---

**This project is intended as a portfolio demonstration of real-world ETL, database integration, and operational data
engineering practices.**
