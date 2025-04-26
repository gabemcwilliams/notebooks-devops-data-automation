# Datto RMM - Daily Patch Metrics and Visualizations

This project extracts device patch compliance data from the Datto RMM platform using its public v2 API. It analyzes and exports patching metrics at the device and site level, producing CSV outputs and visualizations to support daily operational monitoring.

## Key Features
- Authenticates against Datto RMM API (OAuth password flow)
- Pulls device inventory and patch management statuses
- Calculates compliance metrics:
  - Patch compliance percentage
  - Devices missing audits
  - Devices requiring reboots
  - Devices offline >30 days
- Outputs structured CSV reports for use in ticket creation and service delivery
- Generates barplots of patch compliance by site for visual reporting

## Technologies Used
- Python 3
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Requests
- ConfigParser for environment handling

## Usage
1. Configure your Datto RMM API credentials in `config/env.ini`.
2. Update `export_folder` and `git_folder` paths if needed.
3. Run the notebook to export CSVs and plots to the local `exports/` directory.

## Notes
- Assumes the Datto RMM API provides device-level patch management data.
- Requires functional OAuth authentication using Datto RMM API key and secret.
- Exports multiple CSVs focused on specific operational needs (e.g., devices missing audits, devices needing reboots).

---
