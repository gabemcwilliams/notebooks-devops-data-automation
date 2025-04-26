# Infrastructure Data Migration and ETL - DattoRMM and N-Able

## Project Overview

This project consolidates, cleans, and compares infrastructure asset data between two major RMM platforms: DattoRMM and
N-Able.  
It includes ETL (Extract, Transform, Load) processes, data shaping scripts, audit log analysis, OCR-based extraction,
and export management for device inventory, patch policy compliance, and client onboarding tracking.

The goal was to automate the migration and validation of device and software inventory across platforms, ensuring
accuracy, compliance tracking, and operational reporting during infrastructure transitions.

## Contents

| Notebook                        | Description                                                                                                                                                      |
|:--------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 01_nable_device_shaping.ipynb   | Ingests and reshapes N-Able device exports, merges warranty information, and standardizes column naming for later comparison with DattoRMM devices.              |
| 02_nable_login_trends.ipynb     | Combines N-Able system audit logs for login/logout tracking, standardizes client information, and visualizes user activity trends.                               |
| 03_datto_nable_comparison.ipynb | Compares DattoRMM and N-Able device inventories, highlighting discrepancies for onboarding validation. Includes migration progress tracking with visualizations. |
| 04_ocr_patch_scrape.ipynb       | Automates scraping of patch management policies from web interfaces using OCR techniques and Selenium for difficult-to-export data.                              |
| 05_script_repo_scraper.ipynb    | Automates scraping and downloading of internal automation scripts and software packages from the N-Able platform repository.                                     |
| 06_unzip_policy_exports.ipynb   | Automates extraction, renaming, and organization of zipped service template exports for N-Able patch policies and scripts.                                       |

## Key Features

- Full ETL workflows from API, CSV, web scraping, and OCR sources.
- Client, site, and hostname standardization across different platforms.
- Warranty status and patch policy coverage tracking.
- Cross-platform device and software inventory validation.
- Automated compliance trend tracking for device onboarding.
- Script repository scraping and structured download automation.
- Preparation of clean, analysis-ready exports for downstream reporting.

## Stack and Tools Used

- Python 3.x
- pandas, numpy
- re (regex), datetime
- requests, selenium, BeautifulSoup, lxml
- pytesseract, OpenCV
- matplotlib, seaborn
- zeep (SOAP API handling)

## Context

These notebooks were developed as part of an internal infrastructure migration project focused on replacing an N-Able
RMM platform with DattoRMM while maintaining operational coverage, patch compliance, and audit trails during the
transition.  
The code emphasizes automation, data consistency, and auditability of client infrastructure across a distributed
environment.

## Notes

- All client identifiers, sensitive URLs, API keys, and environment configurations have been redacted or generalized.
- No real customer data is contained within this repository.
- This project is intended for demonstration of infrastructure automation, ETL design, and migration process management
  capabilities.

