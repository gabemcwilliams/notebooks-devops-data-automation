# Datto RMM – Software Compliance Report

This script authenticates against the Datto RMM API, extracts all installed software from enrolled devices, and compares key application versions to the latest available online.

## Features

- Authenticates using OAuth and Vault-stored secrets
- Queries the Datto RMM API for all device software
- Standardizes software names and extracts installed versions
- Scrapes official vendor sites for the latest known versions:
  - Adobe Air
  - Adobe Acrobat DC Reader
  - 7-Zip
  - Google Chrome
  - Mozilla Firefox
  - Microsoft Teams
  - Microsoft Office 365
- Produces a compliance matrix indicating which devices are current or outdated
- Exports results to CSV (`[REDACTED]/.csv`)

## Dependencies

- Python 3.10+
- `requests`
- `pandas`, `numpy`
- `beautifulsoup4`, `lxml`
- `hvac` (HashiCorp Vault client)
- Optional: `requests-html` (for JavaScript-rendered pages like Adobe Air)

## 📁 File Structure

```text
datto_rmm_software_report/
│
├──[REDACTED]/.py    # Main script
├── README.md                           # This file
└── dictionaries/
    └── datto_rmm_software_management_report.dict  # Software mapping config
