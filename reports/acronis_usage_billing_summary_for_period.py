"""
Acronis Usage Report Formatter and Summary Generator

This script parses an Acronis billing export CSV, performs field normalization,
filters and enriches tenant usage data, and writes a cleaned CSV summary for
monthly billing. This is used to support internal cost reviews and allocation.

- Normalizes tenant name format
- Filters by service, cost > 0, and optionally partner/org flags
- Maps service type using an external tenant/service mapping file
- Writes a cleaned output CSV sorted by tenant name

Originally part of internal usage cost analysis workflow.
"""

import pandas as pd
import numpy as np
import re
import datetime as dt
from pathlib import Path

# --- Configuration ---
source_file = Path("[REDACTED]/.csv")
service_map_file = Path("[REDACTED]/.csv")
output_path = Path("[REDACTED]/.csv")

include_internal = True  # Set to False to exclude internal/partner records

# --- Load Source CSV ---
df = pd.read_csv(source_file, dtype_backend='pyarrow')

# --- Transformation Logic ---
def model(data_dict: dict) -> dict:
    tenant = data_dict.get('Tenant name', '') or ''
    cleaned_tenant = re.sub(r'^/[^/]+/?', '', tenant).strip() or 'example'

    return {
        'Tenant Name': cleaned_tenant,
        'Type': data_dict.get('Type'),
        'SKU': data_dict.get('SKU', pd.NA),
        'Status': data_dict.get('Status'),
        'Mode': data_dict.get('Mode', pd.NA),
        'Service Name': data_dict.get('Service name'),
        'Metric Name': data_dict.get('Metric name'),
        'metric_unit': data_dict.get('Metric unit', pd.NA),
        'Usage': float(data_dict.get('ProductionUsageFormatted', 0.0))
                 if isinstance(data_dict.get('ProductionUsageFormatted'), float) else 0.0,
        'Unit Cost': data_dict.get('Commitment'),
        'Total Cost': round(data_dict.get('TotalProductionPricingBasedOnTierPerItem', 0.0), 2)
                     if data_dict.get('TotalProductionPricingBasedOnTierPerItem') is not None else None
    }

# Apply transformation
df = pd.DataFrame([model(row) for row in df.to_dict(orient='records')])

# --- Filtering ---
df = df[df['Service Name'] == 'Cyber Protection']
df = df[df['Total Cost'] > 0]
#if not include_internal:
#    df = df[df['Type'] != 'Partner']

# --- Map Enriched Service Types ---
service_map = pd.read_csv(service_map_file)
map_dict = service_map.set_index('tenant_name')['service_name'].to_dict()
df['Service'] = df['Tenant Name'].map(map_dict)
df.insert(loc=1, column='Service', value=df.pop('Service'))

# --- Output ---
df.sort_values('Tenant Name').to_csv(output_path, index=False)
print(f"[ACRONIS USAGE EXPORT SAVED] → {output_path}")
