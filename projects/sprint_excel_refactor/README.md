# Sprint Financial ETL

This project standardizes, merges, and analyzes Sprint Planning, Teamwork Time Logs, and Unearned Revenue financial
data.

It loads, parses, cleans, and aligns multiple messy real-world data sources into unified, exportable datasets —
supporting financial reporting and sprint planning reviews.

---

## 📄 Project Structure

| File                                  | Description                                                                                  |
|:--------------------------------------|:---------------------------------------------------------------------------------------------|
| `sprint_financial_etl.py`             | Main ETL script to load, shape, and merge datasets                                           |
| `data_parsing/dictionaries/`          | Lookup dictionaries (`.parquet`) for standardizing client names, users, and project keywords |
| `data_sets/sprint_financial_reports/` | Input datasets (Sprint Planning Excel, Teamwork CSV, Unearned Revenue Excel)                 |
| `exports/`                            | Output folder for cleaned and merged CSV files                                               |

---

## 📦 Requirements

- Python 3.8+
- pandas
- pyarrow
- openpyxl
- configparser

Install requirements if needed:

```bash
pip install pandas pyarrow openpyxl
```

---

## ⚙️ How to Run

```bash
python sprint_financial_etl.py
```

Exports cleaned CSVs into `d:/exports/`:

- `teamwork_export_<timestamp>.csv`
- `sprint_log_export_<timestamp>.csv`
- `merged_sprint_teamwork_<timestamp>.csv`

---

## 📊 Datasets Used

| Dataset                     | Description                                                   |
|:----------------------------|:--------------------------------------------------------------|
| **Sprint Planning Log**     | Sprint pod planning, project goals, time allocations          |
| **Teamwork Time Logs**      | User timesheets and project hours                             |
| **Unearned Revenue Report** | Financials for ongoing projects not yet recognized as revenue |

---

## 🧹 Data Processing

- **Client Name Standardization:** Aligns naming inconsistencies across datasets (internal vs external names).
- **User Name Standardization:** Matches user names across different platforms.
- **Sprint Parsing:** Breaks sprint pod goals by week.
- **Objective Parsing:** Identifies actions and services based on project naming patterns.
- **Data Merging:** Links Sprint Planning and Teamwork logs by matched project information.

---

## ✨ Features

- Handles missing and inconsistent values gracefully.
- Modular design: easy to swap in new datasets.
- Exports ready-to-use CSVs for reporting, dashboards, or finance review.

---

## 🛠 Future Improvements (Stretch Goals)

- Add CLI arguments for file paths and date ranges.
- Add validation checks for missing columns or malformed files.
- Create dashboard visualizations from merged data.

---

## 🏗 Example Use Cases

- Sprint time reconciliation against billing data.
- Financial projections based on sprint allocations.
- Analyzing project delivery efficiency across teams.
- Preparing reports for leadership or finance teams.

