########################################################
#
#     Title: Postgres [TRANSFORM] - DattoRMM [API] - Devices
#     Created by: Gabe McWilliams
#     Date: 2023/04/19
#
########################################################


import datetime as dt
import pandas as pd


def transform_devices_dataframe(df_devices):
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

        df_devices["category"] = df_devices["deviceType"].apply(device_category)
        df_devices["type"] = df_devices["deviceType"].apply(device_type)

        df_devices.drop(columns='deviceType', inplace=True)

        df_devices["system"] = 'dattormm'
        df_devices["hostname"] = df_devices["hostname"].str.upper()

        # Patch Management Breakdown
        # patchStatus | patchesApprovedPending | patchesNotApproved | patchesInstalled

        # patchStatus
        def patch_status(patch_management):
            try:
                return patch_management["patchStatus"]
            except:
                return None

        df_devices["patchStatus"] = df_devices["patchManagement"].apply(patch_status)

        # patchesApprovedPending
        def patches_approved_pending(patch_management):
            try:
                return patch_management["patchesApprovedPending"]
            except:
                return None

        df_devices["patchesApprovedPending"] = df_devices["patchManagement"].apply(patches_approved_pending)

        # patchesNotApproved
        def patches_not_approved(patch_management):
            try:
                return patch_management["patchesNotApproved"]
            except:
                return None

        df_devices["patchesNotApproved"] = df_devices["patchManagement"].apply(patches_not_approved)

        # patchesInstalled
        def patches_installed(patch_management):
            try:
                return patch_management["patchesInstalled"]
            except:
                return None

        df_devices["patchStatus"] = df_devices["patchManagement"].apply(patch_status)
        df_devices["patchesApprovedPending"] = df_devices["patchManagement"].apply(patches_approved_pending)
        df_devices["patchesNotApproved"] = df_devices["patchManagement"].apply(patches_not_approved)
        df_devices["patchesInstalled"] = df_devices["patchManagement"].apply(patches_installed)

        # drop patchManagement
        df_devices.drop('patchManagement', axis=1, inplace=True)

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

        df_devices["antivirusProduct"] = df_devices["antivirus"].apply(antivirus_product)
        df_devices["antivirusStatus"] = df_devices["antivirus"].apply(antivirus_status)

        # drop antivirus
        df_devices.drop('antivirus', axis=1, inplace=True)

        ## Create Time Columns and Timedate Shaping

        ### Add Timezone Column from UDF
        # Timezone
        def local_timezone(udf):
            try:
                return udf['udf10']
            except:
                return None

        df_devices['localTimezone'] = df_devices['udf'].apply(local_timezone)

        # drop udf {inplace=True}
        df_devices.drop('udf', axis=1, inplace=True)

        ## Create Date Correlation Columns

        ### Convert Epoch to UTC
        df_devices['lastAuditDate'] = pd.to_datetime(df_devices['lastAuditDate'], unit='ms', errors='coerce')

        df_devices['lastSeen'] = pd.to_datetime(df_devices['lastSeen'], unit='ms', errors='coerce')

        df_devices['creationDate'] = pd.to_datetime(df_devices['creationDate'], unit='ms', errors='coerce')

        df_devices['lastReboot'] = pd.to_datetime(df_devices['lastReboot'], unit='ms', errors='coerce')

        ### Define and apply functions to create correlation columns
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
        df_devices['noAudit7Days'] = df_devices['lastAuditDate'].apply(no_audit_7_days)
        # Create Column - Devices Last Audit > 7 days
        df_devices['noAudit30Days'] = df_devices['lastAuditDate'].apply(no_audit_30_days)
        # Create Column - Devices Offline 30 Days
        df_devices['offline30Days'] = df_devices['lastSeen'].apply(offline_30_days)
        # Create Column - Last Reboot Extended Duration and Online without Reboot Extended Duration
        df_devices['noReboot30Days'] = df_devices['lastReboot'].apply(no_reboot_30_days)

        def patch_percentage(pap, pi):
            try:
                return round(100 - pap / (pap + pi) * 100, 2)
            except:
                return None

        df_devices['patchStatusPercent'] = df_devices[["patchesApprovedPending", "patchesInstalled"]].apply(
            lambda x: patch_percentage(x.patchesApprovedPending, x.patchesInstalled), axis=1)

        ### Hostname to_upper()
        df_devices['hostname'] = df_devices['hostname'].str.upper()

        ### Replace Dtypes with Int64
        convert_to_int_mask = ((df_devices.dtypes == 'float') | (df_devices.dtypes == 'bool') | (
                df_devices.dtypes == 'uint8')) & (df_devices.columns != 'patchStatusPercent')
        convert_to_int = df_devices.dtypes[convert_to_int_mask].index.tolist()
        df_devices[convert_to_int] = df_devices[convert_to_int].astype('Int64')

    except Exception as e:
        return {
            "result": {
                "status_message": str(e),
                "status_code": 500
            }
        }

    return {
        "data": df_devices,
        "result": {
            "status_message": "Success",
            "status_code": 200
        }
    }
