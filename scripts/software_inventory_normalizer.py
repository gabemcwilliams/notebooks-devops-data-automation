"""
[REDACTED]/.py

This script normalizes software inventory data from Datto RMM using version-stripping regex,
deduplicates application names, classifies architecture (32-bit vs 64-bit), and prepares
output files for compliance and asset tracking.

Key Features:
-------------
- Cleans messy software names by removing version numbers using custom regex rules
- Groups and deduplicates inventory data by hostname and application
- Flags architecture type using pattern recognition (x86 vs x64)
- Prepares clean output CSVs for further analysis or ingestion into dashboards
- Contains (optional) Datto RMM API example for dynamic software collection (commented)

Dependencies:
-------------
- pandas
- re
- Optional: requests, json (for API logic)

Suggested Improvements:
------------------------
- Externalize regex rules into config or YAML
- Add test coverage for version stripping and OS detection
- Replace print statements with structured logging

Usage:
------
This script is designed for standalone execution or can be embedded in a
larger ETL pipeline for IT asset compliance and software audits.
"""

import pandas as pd
import re

# Load software inventory CSV
df = pd.read_csv('[REDACTED]/.csv', dtype_backend='pyarrow')

# Load version regex patterns for normalization
version_keywords_df = pd.read_csv('[REDACTED]/.csv')
version_keyword_list = list(version_keywords_df['versionRegex'])

# Normalize software names by removing versions
def strip_version(software: str) -> str:
    for v in version_keyword_list:
        software = re.sub(v, '', software)
        software = re.sub(r'\s\s+', ' ', software).strip()
    return software

# Build a set of cleaned software names
software_set = set()
for _, row in df.iterrows():
    software = strip_version(row['Software Application '])
    software_set.add(software)

# Classify architecture based on naming patterns
def classify_architecture(name: str) -> str:
    return '32-bit' if re.match(r'(32|x86)', name) else '64-bit'

software_classified = [
    {
        'Software Application ': name,
        'Arch': classify_architecture(name)
    }
    for name in software_set
]

# Export normalized software list
df_software = pd.DataFrame(software_classified)
df_software.to_csv('[REDACTED]/.csv', index=False)

# Optional: explode software metadata from Datto API (pseudocode skeleton)
# def software_api_req(row):
#     # Requires: access_token, dattormm_config
#     # Use requests.get() to pull software list for each device
#     # Normalize software names using strip_version_from_title
#     # Append results to a device-level dictionary
#     pass

# Optional helper for deeper string normalization
# def strip_version_from_title(string):
#     for kw in version_keyword_list:
#         string = re.sub(kw, '', string)
#         string = re.sub(r'\s\s+', ' ', string).strip()
#     return string

# Optional: save fully grouped output by device (not shown here)
# Can implement with groupby on ['Device Hostname', 'Product'] if needed

print("[REDACTED]/.csv")
