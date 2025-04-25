"""
Active Directory vs DattoRMM Device Diff Tool

- Loads a PowerShell-exported AD device report.
- Pulls DattoRMM device data via API.
- Compares hostname/IP mappings.
- Outputs differences and disabled AD records.

Dependencies:
- pandas
- ts_api_connections.datto_rmm_api (local module)

Usage:
.py --ad-file "<csv_path>" --client "Example CU"
"""

import pandas as pd
import datetime as dt
import argparse
from ts_api_connections import datto_rmm_api


def load_ad_csv(path):
    """Load and preprocess AD CSV export."""
    df = pd.read_csv(path, encoding='utf-8')
    df.dropna(axis=1, how='all', inplace=True)
    df['source'] = 'activeDir'
    df.rename(columns={'Name': 'hostname', 'IPv4Address': 'intIpAddress'}, inplace=True)
    return df[['hostname', 'intIpAddress', 'source']], df


def load_dattormm(client_name):
    """Load DattoRMM data filtered by siteName."""
    datto = datto_rmm_api.DattoRMM()
    df_devices = datto.create_devices_dataframe()
    df_devices['source'] = 'dattoRMM'
    df_filtered = df_devices[df_devices['siteName'] == client_name]
    return df_filtered[['hostname', 'intIpAddress', 'source']]


def write_diff_and_disabled(df_ad, df_client, export_folder):
    """Write CSV reports."""
    diff = pd.concat([df_client, df_ad]).drop_duplicates(subset=['hostname'], keep=False)
    diff.to_csv(f'{export_folder}.csv', index=False)

    df_ad[df_ad['Enabled'] == False].to_csv(f'{export_folder}.csv', index=False)

    print("Exported:")
    print(f" - Hostname/IP diffs to {export_folder}.csv")
    print(f" - Disabled AD devices to {export_folder}.csv")


def main(ad_file_path, client_name, export_dir):
    df_ad_compare, df_ad_full = load_ad_csv(ad_file_path)
    df_client = load_dattormm(client_name)
    write_diff_and_disabled(df_ad_full, df_client, export_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare AD vs DattoRMM device lists.")
    parser.add_argument("--ad-file", required=True, help="Path to AD audit CSV")
    parser.add_argument("--client", required=True, help="Client siteName in DattoRMM")
    parser.add_argument("--export-dir", default="d:/exports", help="Directory for export files")

    args = parser.parse_args()
    main(args.ad_file, args.client, args.export_dir)
