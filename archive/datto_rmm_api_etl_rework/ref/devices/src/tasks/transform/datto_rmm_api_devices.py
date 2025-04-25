# -------------------------------------------------------------------
#
#     Title: Postgres [TRANSFORM] - DattoRMM [API] - Devices
#     Created by: Gabe McWilliams
#     Date: 2023/04/19
#
# -------------------------------------------------------------------


import datetime as dt
import traceback

import pandas as pd


def transform_devices_dataframe(df):
    try:
        # Create Devices DataFrame
        def device_category(device):
            try:
                return device["category"]
            except:
                return None

        def device_type(device):
            try:
                return device["type"]
            except:
                return None

        df["category"] = df["deviceType"].apply(device_category)
        df["type"] = df["deviceType"].apply(device_type)

        df.drop(columns='deviceType', inplace=True)


        df["hostname"] = df["hostname"].str.upper()

        # Patch Management Breakdown
        # patchStatus | patchesApprovedPending | patchesNotApproved | patchesInstalled

        # patchStatus
        def patch_status(patch_management):
            try:
                return patch_management["patchStatus"]
            except:
                return None

        df["patchStatus"] = df["patchManagement"].apply(patch_status)

        # patchesApprovedPending
        def patches_approved_pending(patch_management):
            try:
                return patch_management["patchesApprovedPending"]
            except:
                return None

        df["patchesApprovedPending"] = df["patchManagement"].apply(patches_approved_pending)

        # patchesNotApproved
        def patches_not_approved(patch_management):
            try:
                return patch_management["patchesNotApproved"]
            except:
                return None

        df["patchesNotApproved"] = df["patchManagement"].apply(patches_not_approved)

        # patchesInstalled
        def patches_installed(patch_management):
            try:
                return patch_management["patchesInstalled"]
            except:
                return None

        df["patchStatus"] = df["patchManagement"].apply(patch_status)
        df["patchesApprovedPending"] = df["patchManagement"].apply(patches_approved_pending)
        df["patchesNotApproved"] = df["patchManagement"].apply(patches_not_approved)
        df["patchesInstalled"] = df["patchManagement"].apply(patches_installed)

        # drop patchManagement
        df.drop('patchManagement', axis=1, inplace=True)

        def antivirus_product(antivirus):
            try:
                return antivirus["antivirusProduct"]
            except:
                return None

        def antivirus_status(antivirus):
            try:
                return antivirus["antivirusStatus"]
            except:
                return None

        df["antivirusProduct"] = df["antivirus"].apply(antivirus_product)
        df["antivirusStatus"] = df["antivirus"].apply(antivirus_status)

        # drop antivirus
        df.drop('antivirus', axis=1, inplace=True)

        # Create Time Columns and Timedate Shaping

        # Add Timezone Column from UDF
        # Timezone
        def local_timezone(udf):
            try:
                return udf['udf10']
            except:
                return None

        df['localTimezone'] = df['udf'].apply(local_timezone)

        # drop udf {inplace=True}
        df.drop('udf', axis=1, inplace=True)

        # Create Date Correlation Columns

        # Convert Epoch to UTC
        df['lastAuditDate'] = pd.to_datetime(df['lastAuditDate'], unit='ms', errors='coerce')

        df['lastSeen'] = pd.to_datetime(df['lastSeen'], unit='ms', errors='coerce')

        df['creationDate'] = pd.to_datetime(df['creationDate'], unit='ms', errors='coerce')

        df['lastReboot'] = pd.to_datetime(df['lastReboot'], unit='ms', errors='coerce')

        # Define and apply functions to create correlation columns
        def no_audit_7_days(last_audit):
            if last_audit < dt.datetime.now() - dt.timedelta(days=7):
                return 1
            else:
                return 0

        def no_audit_30_days(last_audit):
            if last_audit < dt.datetime.now() - dt.timedelta(days=30):
                return 1
            else:
                return 0

        def offline_30_days(last_seen):
            if last_seen < dt.datetime.now() - dt.timedelta(days=30):
                return 1
            else:
                return 0

        def no_reboot_30_days(last_reboot):
            if last_reboot < dt.datetime.now() - dt.timedelta(days=30):
                return 1
            else:
                return 0

        # Create Column - Devices Last Audit > 7 days
        df['noAudit7Days'] = df['lastAuditDate'].apply(no_audit_7_days)
        # Create Column - Devices Last Audit > 7 days
        df['noAudit30Days'] = df['lastAuditDate'].apply(no_audit_30_days)
        # Create Column - Devices Offline 30 Days
        df['offline30Days'] = df['lastSeen'].apply(offline_30_days)
        # Create Column - Last Reboot Extended Duration and Online without Reboot Extended Duration
        df['noReboot30Days'] = df['lastReboot'].apply(no_reboot_30_days)

        def patch_percentage(pap, pi):
            try:
                return round(100 - pap / (pap + pi) * 100, 2)
            except:
                return None

        df['patchStatusPercent'] = df[["patchesApprovedPending", "patchesInstalled"]].apply(
            lambda x: patch_percentage(x.patchesApprovedPending, x.patchesInstalled), axis=1)

        # Hostname to_upper()
        df['hostname'] = df['hostname'].str.upper()

        # Replace Dtypes with Int64
        convert_to_int_mask = ((df.dtypes == 'float') | (df.dtypes == 'bool') | (
                df.dtypes == 'uint8')) & (df.columns != 'patchStatusPercent')
        convert_to_int = df.dtypes[convert_to_int_mask].index.tolist()
        df[convert_to_int] = df[convert_to_int].astype('Int64')

        return {
            "data": df,
            "result": {
                "status_message": "Success",
                "status_code": 200
            }
        }

    except Exception as e:
        return {
            "result": {
                "status_message": traceback.format_exc(),
                "status_code": 500
            }
        }
