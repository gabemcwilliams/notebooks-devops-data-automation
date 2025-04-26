# End of Life OS Report Generator

## Overview

This utility generates a clean, professional report of devices reaching end of support (End of Life) based on device inventory data. It loads an inventory dataset, filters for devices nearing or past end of support dates, and outputs a formatted HTML report that can optionally be exported to PDF.

It is **not** a web application, but simply uses **Jinja2** templating for offline report generation.

---

## Features

- **Input:** Reads from a Datto RMM device inventory exported to Excel (`.xlsx`).
- **Processing:**
  - Filters devices based on "end of support" flags.
  - Supports site-specific filtering (e.g., reports per client).
  - Summarizes device categories.
- **Output:**
  - Generates a clean, stylized **HTML** report using a Jinja2 template.
  - Optionally exports to **PDF** using `pdfkit` and `wkhtmltopdf`.


---

## Folder Structure

```bash
/root/
    notebooks/
        end_of_life_os_report_generator.ipynb
    reports_templates/
        end_of_life_report.html
    exports/
        (Generated HTML and PDF reports will be saved here)
```

> 💡 If "exports/" does not exist, it will be created automatically.


---

## Prerequisites

- Python 3.10+
- Python Packages:
  - pandas
  - jinja2
  - matplotlib
  - seaborn
  - pdfkit (optional, for PDF generation)
- wkhtmltopdf installed and accessible (for PDF output)


---

## Setup

Install Python dependencies:

```bash
pip install pandas jinja2 matplotlib seaborn pdfkit
```

Install `wkhtmltopdf` separately:
- [https://wkhtmltopdf.org/downloads.html](https://wkhtmltopdf.org/downloads.html)
- Confirm its path after installation.


---

## Usage

1. **Update Paths** at the top of the notebook/script:
   - Input Excel file path
   - Template folder path
   - Export/output folder

2. **Run Script**:
   - Load device data
   - Filter for a specific site (optional)
   - Create an HTML report using the Jinja2 template
   - (Optional) Export to PDF using pdfkit


---

## Example Output

- **HTML Report:** A styled webpage summarizing end-of-life devices.
- **PDF Report:** A downloadable, printable version of the report.

---

## Notes

- This script can be adapted easily for any device inventory source (not just Datto RMM).
- To customize styling, simply modify the included Jinja2 template (`end_of_life_report.html`) and any referenced CSS.


---

## Author

**Gabe McWilliams**

_Professional-grade reporting built with classic design principles in mind._

