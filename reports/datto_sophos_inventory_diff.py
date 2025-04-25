"""
[REDACTED]/.py

Compares device inventory data between Datto RMM and Sophos Central platforms
by querying their APIs, standardizing key fields, and exporting differences.

Features:
---------
- Pulls device data from both Datto RMM and Sophos Central APIs
- Harmonizes fields like 'device type', 'last seen', and 'site name'
- Applies site name normalization using `NameShaping`
- Identifies device mismatches across both platforms (based on site + hostname)
- Exports CSV showing unmatched devices

Requirements:
-------------
- `ts_api_connections.datto_rmm_api`
- `ts_api_connections.sophos_central_api`
- `ts_standard_naming.std_naming`

Suggested Usage:
----------------
Can be run as a standalone script for periodic audits. If you plan to
frequently inspect or test data, a notebook version may be appropriate.
"""

import json
import re
import datetime as dt
from pathlib import Path

import pandas as pd

from ts_api_connections import datto_rmm_api
from ts_api_connections import sophos_central_api
from ts_standard_naming.std_naming import NameShaping

# Timestamp for versioning output
current_time = dt.datetime.utcnow().strftime('%Y_%m_%d_%H%M%S')

# Directory setup
git_folder = 'd:/git/example_infrastructure_data_dev'
dictionary_dir = f'{git_folder}/dictionaries'
export_folder = 'd:/exports/'

# Instantiate API clients and naming resolver
datto = datto_rmm_api.DattoRMM()
sophos = sophos_central_api.SophosCentral()
rs = NameShaping(dictionary_dir)

# Fetch and process Datto RMM data
df_datto = datto.create_devices_dataframe()
df_datto['type'].replace({'Desktop': 'computer', 'Laptop': 'computer', 'Server': 'server'}, inplace=True)

# Fetch and process Sophos Central data
df_sophos_av = sophos.create_sophos_dataframe()
df_sophos_av['siteName'] = df_sophos_av['siteName'].apply(rs.client_names)

# Convert Sophos timestamps from nanoseconds
df_sophos_av['lastSeen'] = pd.to_datetime(df_sophos_av['lastSeenAt'], unit='ns').astype('datetime64[s]')
df_sophos_av.drop('lastSeenAt', axis=1, inplace=True)

# Columns to compare
compare_cols = ['siteName', 'hostname', 'type', 'lastSeen', 'system']
df_sophos_shaped = df_sophos_av[compare_cols]
df_datto_shaped = df_datto[compare_cols]

# Convert Datto timestamps from milliseconds
df_datto_shaped['lastSeen'] = pd.to_datetime(df_datto_shaped['lastSeen'], unit='ms')

# Restrict Datto records to sites present in Sophos
df_datto_shaped = df_datto_shaped[df_datto_shaped['siteName'].isin(df_sophos_shaped['siteName'].unique())]

# Perform diff
# Concatenate both and remove duplicates based on siteName + hostname
diff = pd.concat([df_datto_shaped, df_sophos_shaped])\
         .drop_duplicates(subset=['siteName', 'hostname'], keep=False, ignore_index=True)

# Export diff CSV
diff_path = f"{export_folder}datto_sophos_diff_{current_time}[REDACTED]/.csv"
diff.to_csv(diff_path, index=False)
print(f"Exported diff to {diff_path}")

# Debug/test block — hostname cleaning for a specific site (optional)
def tell_me_about(s):
    uv = s.encode("utf-8")
    return str(uv).replace("b'", "").replace("'", "").replace("\\xe2\\x80\\x99", "'").replace("\\xe2\\x80\\xb2", "'")

# Apply to test site (e.g., 'example')
test_site = 'example'
df_test = df_sophos_shaped[df_sophos_shaped['siteName'] == test_site].copy()
df_test['shapedHostname'] = df_test['hostname'].apply(tell_me_about)

# Export cleaned test site data
test_export_path = f"{export_folder}[REDACTED]/.csv"
df_test.to_csv(test_export_path, index=False)
print(f"Exported test site data to {test_export_path}")