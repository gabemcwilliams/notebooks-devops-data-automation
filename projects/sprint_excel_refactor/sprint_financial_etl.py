# sprint_financial_etl.py

import os
import re
import pandas as pd
import datetime as dt
import json
from configparser import ConfigParser

# Constants
CURRENT_TIME = dt.datetime.utcnow().strftime('%Y_%m_%d_%H%M%S')
GIT_DIR = 'd:/git'
EXPORT_FOLDER = 'd:/exports/'
DICT_DIR = f'{GIT_DIR}/data_parsing/dictionaries'
DATA_SET_DIR = "d:/data_sets/sprint_financial_reports"

TEAMWORK_FILE = f'{DATA_SET_DIR}/teamwork_data.csv'  # Example path
SPRINT_FILE = f'{DATA_SET_DIR}/master_sprint_planning_test_data.xlsx'
UNEARNED_REV_FILE = f'{DATA_SET_DIR}/Unearned Project Rev 10.31.22.xlsx'

# Load lookup dictionaries
client_rename_dict = pd.read_parquet(f'{DICT_DIR}/standard_client_names.parquet').to_dict(orient='records')
user_dict = pd.read_parquet(f"{DICT_DIR}/ts_user_info.parquet").to_dict(orient="records")
project_names_dict = pd.read_parquet(f'{DICT_DIR}/project_names.parquet').to_dict(orient='records')


# Helper Classes
class NameShaping:
    def __init__(self, dictionary_source=DICT_DIR):
        df = pd.read_parquet(f'{dictionary_source}/standard_client_names.parquet')
        self.client_rename_dict = {row['previousName']: row['currentName'] for _, row in df.iterrows()}

    def std_client_names_rename(self, string=""):
        for k, v in self.client_rename_dict.items():
            if k.lower() == string.lower() or string.lower().startswith(k.lower()):
                return v
        return string

    @staticmethod
    def reword_credit_union(string=''):
        cu_reword_dict = {'Federal Credit Union': 'FCU', 'Credit Union': 'CU'}
        for k, v in cu_reword_dict.items():
            string = string.replace(k, v)
        return string


# Helper Functions
def parse_sprint_client_name(string, col_name):
    match = re.match(r'^((\w+)\s?-\s?)?([\w\s|]+)', str(string))
    if not match:
        return None
    if col_name == 'scope':
        return 'All Client' if match.group(3).lower() in ['all clients', 'all client'] else 'Client'
    if col_name == 'department':
        return "360" if match.group(2) == "360" else "Example Co."
    if col_name == 'client':
        return match.group(3)


def std_user_names_rename(string=""):
    for user in user_dict:
        if any(string.lower() == user.get(field, "").lower() for field in
               ['currentName', 'firstName', 'lastName', 'fullName']):
            return user['fullName']
    return string


def parse_action(string=""):
    for proj in project_names_dict:
        if proj['keyword'].lower() in string.lower():
            return proj['stdAction']
    return ""


def breakup_pod_goals(string):
    parts = re.findall(r'([^\n]+)\n?', str(string).replace('\n\n', '\n'))
    return {
        'Week 1 - Goals': parts[0] if parts else "",
        'Week 2 - Goals': parts[1] if len(parts) > 1 else parts[0] if parts else ""
    }


# Loaders
def load_teamwork():
    shaper = NameShaping()
    df = pd.read_csv(TEAMWORK_FILE, encoding='latin1')

    df['Company'] = df['Company'].apply(shaper.reword_credit_union)
    df['clientName'] = df['Company'].apply(parse_sprint_client_name, args=['client'])
    df['scope'] = df['Company'].apply(parse_sprint_client_name, args=['scope'])
    df['department'] = df['Company'].apply(parse_sprint_client_name, args=['department'])
    df['Client Name'] = df['clientName'].apply(shaper.std_client_names_rename)
    df['Resource Name'] = df['Who'].apply(std_user_names_rename)
    df['Objective'] = df['Company']
    df['Action'] = df['Objective'].apply(parse_action)
    df['Service'] = df['Action'] + " service"

    df['Date'] = pd.to_datetime(df['Date/Time'], errors='coerce')
    df['Day of Week'] = df['Date'].dt.day_name()

    columns_order = ['Client Name', 'Scope', 'Department', 'Resource Name', 'Objective', 'Action', 'Service', 'Date',
                     'Day of Week']
    return df[columns_order]


def load_sprint_log():
    shaper = NameShaping()
    df = pd.read_excel(SPRINT_FILE, sheet_name="Sprint Pods")
    df = df.dropna(thresh=5)
    df = df[df['Client Name'] != "Total"]

    df['clientName'] = df['Client Name'].apply(parse_sprint_client_name, args=['client'])
    df['scope'] = df['Client Name'].apply(parse_sprint_client_name, args=['scope'])
    df['department'] = df['Client Name'].apply(parse_sprint_client_name, args=['department'])
    df['Client Name'] = df['clientName'].apply(shaper.std_client_names_rename)
    df['Resource Name'] = df['Resource'].apply(std_user_names_rename)

    df['Action'] = df['Objective'].apply(parse_action)
    df['Service'] = df['Action'] + " service"

    # Pod Goals
    goals = df['POD Goals'].apply(breakup_pod_goals).apply(pd.Series)
    df = pd.concat([df, goals], axis=1)

    return df


def load_unearned_rev():
    df = pd.read_excel(UNEARNED_REV_FILE, sheet_name='Sheet1')
    df.drop(df.columns[0], axis=1, inplace=True)
    return df


def merge_dataframes(df_sprint, df_teamwork):
    merge_keys = ['Client Name', 'Scope', 'Department', 'Resource Name', 'Objective', 'Action']
    return pd.merge(df_sprint, df_teamwork, on=merge_keys, how='inner')


# ETL Flow
def main():
    print("Loading teamwork...")
    df_teamwork = load_teamwork()

    print("Loading sprint planning...")
    df_sprint = load_sprint_log()

    print("Loading unearned revenue...")
    df_unearned_rev = load_unearned_rev()

    print("Merging datasets...")
    df_merged = merge_dataframes(df_sprint, df_teamwork)

    # Save
    teamwork_export = os.path.join(EXPORT_FOLDER, f'teamwork_export_{CURRENT_TIME}.csv')
    sprint_export = os.path.join(EXPORT_FOLDER, f'sprint_log_export_{CURRENT_TIME}.csv')
    merged_export = os.path.join(EXPORT_FOLDER, f'merged_sprint_teamwork_{CURRENT_TIME}.csv')

    df_teamwork.to_csv(teamwork_export, index=False)
    df_sprint.to_csv(sprint_export, index=False)
    df_merged.to_csv(merged_export, index=False)

    print(f"Exported to {EXPORT_FOLDER}")


if __name__ == "__main__":
    main()
