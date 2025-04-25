"""
Patch Compliance Summary Report Generator

Scans a report archive directory for matching client reports,
extracts patching and reboot stats, and writes two summarized CSV
output files:
- General summary by month
- Device-level snapshot of critical servers

This script uses:
- Filename parsing via regex for metadata extraction
- Data aggregation with pandas
- Hostname filtering for critical infrastructure assets

Refactored and obfuscated from internal infrastructure tooling.
"""

import pandas as pd
import os
import re
from pathlib import Path

# --- Configuration ---
archive_dir = Path(r"C:/data/report_archive")
output_dir = Path("d:/exports/summary")

client_match = "ABC Org"
report_types = ["Patch Summary"]
years = [2024]
months = [10, 11, 12]

critical_hosts = [
    "abc-util", "abc-fs-01", "abc-dc-01",
    "abc-dc-02", "abc-backup-02", "abc-automation-1"
]

# --- Timestamp Helpers ---
current_time = pd.Timestamp.utcnow().strftime('%Y_%m_%d_%H%M%S')
years_str = str(years[0]) if len(years) == 1 else '_'.join(map(str, years))
months_str = str(months[0]) if len(months) == 1 else '_'.join(map(str, months))

# --- Step 1: Discover Matching Reports ---
report_files = []
pattern = re.compile(r"([\w\s]+)\s-\s(\d{4})\s-\s(\d{2})\s-\s([\w\s]+)[REDACTED]/.csv")

for root, _, files in os.walk(archive_dir):
    for file in files:
        match = pattern.match(file)
        if not match:
            continue

        site, year, month, report = match.groups()
        if site != client_match:
            continue
        if int(year) not in years:
            continue
        if int(month) not in months:
            continue
        if report not in report_types:
            continue

        report_files.append({
            "client_name": site,
            "year": year,
            "month": month,
            "report_name": report,
            "file_name": file,
            "file_path": os.path.join(root, file)
        })

# --- Step 2: Aggregate Summary and Critical Info ---
summary = []
critical_snapshot = []

for report in report_files:
    df = pd.read_csv(report["file_path"])
    df["hostname_lower"] = df["hostname"].str.lower()
    critical_df = df[df["hostname_lower"].isin(critical_hosts)]

    for _, row in critical_df.iterrows():
        critical_snapshot.append({
            "client_name": report["client_name"],
            "year": report["year"],
            "month": report["month"],
            "hostname": row.get("hostname"),
            "os": row.get("operatingSystem"),
            "agent_status": "Online" if row.get("online") == 1 else "Offline",
            "last_audit": row.get("lastAuditDate"),
            "last_reboot": row.get("lastReboot"),
            "needs_reboot": row.get("rebootRequired"),
            "patch_percentage": round(row.get("patchStatusPercent", 0), 2)
        })

    try:
        needs_reboot = df.value_counts("rebootRequired")[True]
    except Exception:
        needs_reboot = 0

    try:
        patch_percent = round(df["patchStatusPercent"].mean(), 2)
    except Exception:
        patch_percent = None

    summary.append({
        "client_name": report["client_name"],
        "year": report["year"],
        "month": report["month"],
        "report_name": report["report_name"],
        "total_devices": len(df),
        "needs_reboot": needs_reboot,
        "patch_percentage": patch_percent
    })

# --- Step 3: Write Summary CSVs ---
out_df = pd.DataFrame(summary)
out_path = output_dir / f"{years_str}_{months_str}_{client_match.strip().lower().replace(' ', '_')}[REDACTED]/.csv"
out_df.to_csv(out_path, index=False)
print(f"[SUMMARY SAVED] → {out_path}")

critical_df = pd.DataFrame(critical_snapshot).drop_duplicates(subset="hostname", keep="last")
out_crit = output_dir / f"{years_str}_{months_str}_{client_match.strip().lower().replace(' ', '_')}[REDACTED]/.csv"
critical_df.to_csv(out_crit, index=False)
print(f"[CRITICAL SERVERS SAVED] → {out_crit}")
