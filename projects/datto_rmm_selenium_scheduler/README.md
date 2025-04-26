# Datto RMM Monthly Report Scheduler

This project automates the configuration of monthly reports inside the Datto RMM web console using Selenium.

## What it Does
- Logs into the Datto RMM portal using username, password, and MFA (manual input).
- Navigates to the Reports section and finds all existing Monthly Reports.
- Configures each report to:
  - Set schedule to "Monthly"
  - Select all months
  - Set the correct report day based on client mapping
- Verifies if the standard reporting email address is already configured.
- Saves changes and validates completion.

## Purpose
This automation ensures consistent, compliant scheduling across all client reports, saving manual admin effort and reducing human error.

## Technologies Used
- Python 3
- Selenium WebDriver
- Chrome (headless mode)
