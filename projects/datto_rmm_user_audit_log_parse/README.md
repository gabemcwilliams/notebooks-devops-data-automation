

# Datto RMM User Audit - Parsing, Ingestion, and Scraping

This project collects, parses, ingests, and analyzes **Datto RMM User Audit** logs using a combination of notebooks and scripts.

## Project Structure

```
datto_rmm_user_audit/
├── notebooks/
│   ├── datto_mongodb_ingest.ipynb
│   ├── datto_useraudit_csv_repair.ipynb
│   ├── datto_useraudit_parse_dataframe.ipynb
│   ├── datto_useraudit_scrape_selenium.ipynb
├── README.md
```

## Files

### /notebooks/

**datto_mongodb_ingest.ipynb**  
- Parses user audit data from text exports
- Prepares structured records
- Inserts into MongoDB `datto_rmm.user_audit`

**datto_useraudit_csv_repair.ipynb**  
- Repairs broken CSV export formats from Datto RMM
- Fixes newline issues
- Outputs clean CSVs

**datto_useraudit_parse_dataframe.ipynb**  
- Parses and inspects Datto user audit logs into Pandas DataFrames
- Supports direct username, timestamp, or action filtering

**datto_useraudit_scrape_selenium.ipynb**  
- Logs into Datto RMM web portal using Selenium
- Navigates to activity pages
- Downloads CSV files for audit logs

---

## Setup Requirements

- Python 3.8+
- Packages:
  - `pandas`
  - `re`
  - `datetime`
  - `selenium`
  - `pymongo`
  - `requests`
  - `configparser`
- Web Drivers:
  - Geckodriver (for Firefox)
  - Chromedriver (optional)

## Environment Configuration

A `config/env.ini` file must exist with credentials:

```ini
[mongodb]
username = your_mongo_user
password = your_mongo_password
connection_ip = localhost

[dattormm]
username = your_datto_username
password = your_datto_password
```

## Usage Flow

1. Scrape or export Datto RMM user audit logs
2. Repair broken CSVs if needed using `datto_useraudit_csv_repair.ipynb`
3. Parse logs into DataFrames with `datto_useraudit_parse_dataframe.ipynb`
4. Ingest records into MongoDB using `datto_mongodb_ingest.ipynb`
