"""
Monthly Patch Report Exporter

Description:
------------
- Scans a directory for parquet-formatted patch reports.
- Filters for the most recent file per (year, month).
- For each unique site in the report:
    - Creates an archived CSV in `exports/archive/YYYY/MM/`
    - Creates a clean distribution copy in `exports/distro/YYYY/MM/{site}/`

Limitations:
------------
- Assumes file names follow the pattern: <source>_YYYY_MM_DD_HHMMSS_<subject>.parquet
- Year/months are currently hardcoded unless adapted for argparse
- No MinIO or S3 integration — files must already exist locally
"""

import pandas as pd
import re
import os
from pathlib import Path

# ------------------------------------------
# CONFIGURATION
# ------------------------------------------
data_dir = './data'
exports_dir = r"D:/monthly_reports"
years = [2025]
months = [1, 2]

std_cols = [
    'site_name', 'uid', 'category', 'type', 'hostname', 'int_ip_address',
    'operating_system', 'last_logged_in_user', 'domain', 'reboot_required',
    'online', 'last_seen', 'last_reboot', 'last_audit_date', 'creation_date',
    'local_timezone', 'snmp_enabled', 'patch_status', 'patches_approved_pending',
    'patches_not_approved', 'patches_installed', 'patch_status_percentage',
    'no_audit_last_30_days', 'offline_last_30_days', 'no_reboot_last_30_days'
]

# ------------------------------------------
# SCAN FILES
# ------------------------------------------
def get_source_files(data_dir):
    source_files = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            result = re.match(r'(\w+)_(\d{4})_(\d{2})_(\d{2})_(\d{2})(\d{2})(\d{2})_(.*).parquet', file)
            if result:
                source_files.append({
                    'file_name': file,
                    'path': f'{root}/{file}',
                    'source_type': result.group(1),
                    'subject': result.group(8),
                    'year': int(result.group(2)),
                    'month': int(result.group(3)),
                    'day': int(result.group(4)),
                    'hour_min_sec': result.group(5) + result.group(6) + result.group(7),
                })
    return source_files

# ------------------------------------------
# EXPORT LOGIC
# ------------------------------------------
def export_reports(df_sources):
    for _, source in df_sources.iterrows():
        df = pd.read_parquet(source['path'])
        site_names = df['site_name'].unique()

        for site in site_names:
            df_client = df[df['site_name'] == site]

            archive_path = f'{exports_dir}/archive/{source["year"]}/{source["month"]:02d}'
            Path(archive_path).mkdir(parents=True, exist_ok=True)
            archive_file = f"{archive_path}/{site} - {source['year']} - {source['month']:02d}.csv"
            df_client.to_csv(archive_file, index=False)

            distro_path = f'{exports_dir}/distro/{source["year"]}/{source["month"]:02d}/{site}'
            Path(distro_path).mkdir(parents=True, exist_ok=True)
            df_client.to_csv(f'{distro_path}.csv', index=False)

# ------------------------------------------
# MAIN EXECUTION
# ------------------------------------------
if __name__ == '__main__':
    source_files = get_source_files(data_dir)
    df_sources = pd.DataFrame(source_files)
    df_sources = df_sources.sort_values(['year', 'month', 'hour_min_sec'], ascending=False)
    df_sources = df_sources.drop_duplicates(subset=['year', 'month'], keep='first')
    df_sources = df_sources[(df_sources['year'].isin(years)) & (df_sources['month'].isin(months))]

    export_reports(df_sources)
    print("[REDACTED] exported successfully.")
