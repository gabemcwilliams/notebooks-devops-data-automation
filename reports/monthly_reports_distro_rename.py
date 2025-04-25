"""
Monthly Report File Sorter

Scans a source directory recursively for files matching the pattern:
    <Client Name> - <YYYY> - <MM> - <Report Name>

For each match:
- Extracts year, month, and client name
- Removes redundant text like "Monthly   Scheduled" from the report name
- Copies the file into a new structure:
    target_dir/YYYY/MM/Client Name/<cleaned report name>

Limitations:
- Assumes all relevant files follow a consistent naming convention
- No validation on file content or report type
- Duplicates will silently overwrite in the target directory
"""

import pandas as pd  # Not used but likely intended for future extension
import numpy  # Not used, can be removed
import re
import os
from pathlib import Path
from shutil import copy

source_dir = r'D:\monthly_reports_rework\source'
target_dir = r'D:\monthly_reports_rework\test'

for root, dirs, files in os.walk(source_dir):
    for file in files:
        print(f'\nProcessing: {file}')
        orig_path = os.path.join(root, file)
        print(f'Original path: {orig_path}')

        result = re.match(r'^(.*)\s-\s(\d{4})\s-\s(\d{2})\s-\s(.*)', file)
        if result:
            site = result.group(1).strip()
            year = result.group(2)
            month = int(result.group(3))
            raw_report_name = result.group(4).strip()

            # Clean report name (e.g., remove duplicate keywords or padding)
            report_name = re.sub(r'Monthly\s+Scheduled\s+', '', raw_report_name)

            destination_dir = Path(target_dir) / year / f'{month:02d}' / site
            destination_dir.mkdir(parents=True, exist_ok=True)

            destination_path = destination_dir / report_name
            print(f'Destination: {destination_path}')
            print('*' * 80)

            copy(orig_path, destination_path)
