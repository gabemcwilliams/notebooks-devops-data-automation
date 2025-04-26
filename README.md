# Notebook-Lab

This repository showcases real-world, production-style Jupyter Notebooks and Python modules created between 2021–2024.

It includes early API ingestion work, ETL pipelines, CSV and database shaping, asset management scripts, SaaS API integrations, and backend service testing.  
The focus is on real data movement, data cleaning, workflow automation, and practical DevOps/data engineering patterns — not tutorial examples.

---

## Repository Highlights

- **API Data Extraction and Comparison:**  
  Early API work with platforms like Datto RMM, Auvik, HaloPSA, Sophos Central, AWS, and Veeam.  
  Includes OAuth2 authentication, paginated data ingestion, endpoint mapping, and historical asset reconciliation.

- **Data Engineering and ETL Pipelines:**  
  Postgres and MinIO data lake ingestion scripts, CSV normalization, timeseries shaping, and basic Luigi orchestration examples.

- **Asset Management and Automation:**  
  Scripts and notebooks for SaaS inventory reporting, compliance checking, patch management data parsing, and monthly report generation.

- **Development Utilities:**  
  Includes internal modules for standardizing client names, manipulating Parquet files, managing object storage, and scheduling Nomad jobs.

- **Prefect.io and Luigi Experimentation:**  
  Early exploration of orchestration tools to automate ETL jobs across on-prem and cloud storage.

---

## Folder Structure

- `notebooks/` – Jupyter notebooks organized by early API work, ETL ingestion, and CSV manipulation.
- `projects/` – Focused project directories with service-specific pipelines and parsers.
- `scripts/` – Standalone Python and PowerShell scripts for data cleaning, migration, and monitoring.
- `compliance/` – Small utilities for system auditing and patch management validation.
- `utils/` – Reusable modules for storage, token caching, and data aggregation.
- `reports/` – Final report generation scripts and dashboards.
- `modules/` – Internal shared libraries (packaged with minimal setup).

---

## Notes

- All work was performed manually — no templates, code generators, or low-code tools were used.
- Early notebooks have been output-cleared and staged, but retain authentic, working history for educational purposes.
- This repository reflects live infrastructure, SaaS API, and ETL handling developed in a real production environment.

---

## About

Author: Gabe McWilliams  
Focus Areas: Data Engineering, MLOps, Edge AI, DevOps Integration  
