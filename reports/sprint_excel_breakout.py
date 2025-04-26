"""
Sprint, Teamwork, and Financial Data Shaping & Alignment Script

Description:
------------
Processes and aligns data from multiple sources—Sprint Planning, Teamwork logs, and Unearned Revenue reports—into a unified format for downstream analysis or reporting.

Key Capabilities:
-----------------
- Parses client/project naming patterns using a renaming dictionary.
- Identifies and classifies structured actions and services from descriptions.
- Transforms wide weekly sprint data into normalized row-based format.
- Aligns Sprint and Teamwork logs by shared columns.
- Exports resource-specific and client-specific views for analysis.

Limitations:
------------
- Assumes consistent column naming across all source files.
- Regex-based name matching may fail on edge cases.
- Columns like 'Tags', 'Estimated' are dropped without preservation.
- Type coercion or validation on fields is not enforced.
- Focused on 2-week sprint structures with hardcoded timeframe assumptions.

Usage:
------
Intended for internal analytics and delivery reporting. Use as a pre-analytics step to prepare clean CSV outputs for visualization, finance review, or project management insight.
"""

import json

from ts_standard_naming import std_naming

# data conditioning

import pandas as pd
import re
import datetime as dt

### Base Variables for I/O


# add current timestamp to filename for reference
current_time = (dt.datetime.now(dt.timezone.utc).strftime('%Y_%m_%d_%H%M%S'))

# git repo folder
git_dir = 'd:/git'

# dictionary location
dict_dir = f'{git_dir}/data_parsing/dictionaries'

# export folder will contain all csv exported DataFrames for Ticket Creation
export_folder = 'd:/exports/'

data_set_dir = "d:/data_sets/sprint_financial_reports"

### File Locations

sprint_file = f'{data_set_dir}/master_sprint_planning_test_data.xlsx'
teamwork_file = f'{data_set_dir}.csv'
unearned_rev_file = f'{data_set_dir}/Unearned Project Rev 10.31.22.xlsx'


# Shaping Functions

## Client Renaming

# This is a module I made for adjusting names, but I've put it in this manually so it wont need to be installed or imported for now

class NameShaping:
    def __init__(self, dictionary_source=""):
        # print('initializing Reshape')

        self.dictionary_source = dictionary_source

        # create client_rename_dict
        def __create_client_rename_dict__():
            # print('Starting _create_client_rename_dict')
            df = pd.read_parquet(f'{self.dictionary_source}/standard_client_names.parquet')
            client_rename_dict = {}
            for index, row in df.iterrows():
                previous_name = row['previousName']
                current_name = row['currentName']
                client_rename_dict[previous_name] = current_name
            return client_rename_dict

        self.client_rename_dict = __create_client_rename_dict__()

    def std_client_names_rename(self, string=""):
        for k, v in self.client_rename_dict.items():
            try:
                if k.lower() == string.lower():
                    return v
                elif k.lower() == string[:len(k)].lower():
                    return v

                result = re.sub(k.lower(), v, string.lower())

                if (result != string.lower()) & (len(k) <= 4):
                    if (len(string) == len(k)) | (k == string[:len(k)]):
                        return v

                elif (result != string.lower()) & (len(k) > 4):
                    return v

            except Exception as e:
                break
        return string

    @staticmethod
    def reword_credit_union(string=''):
        cu_reword_dict = {'Federal Credit Union': 'FCU', 'Credit Union': 'CU'}
        for k, v in cu_reword_dict.items():
            result = re.sub(k, v, string)
            if result != string:
                return result

        return string

    @staticmethod
    def rename_members_first_cu(string):
        if string == 'Example CU':
            return '[REDACTED]'
        else:
            return string


## Parse and Categorize by Client Name

def parse_sprint_client_name(string, col_name):
    try:
        result = re.match(r'^((\w+)\s?-\s?)?([\w\s|]+)', string)
        if not result:
            return ""

        if col_name == 'scope':
            if result.group(3).lower() in ['all clients', 'all client']:
                return 'All Client'
            elif result.group(3).lower() == 'Example Co.':
                return 'Internal'
            else:
                return "Client"

        elif col_name == 'department':
            if result.group(2) == "360":
                return "360"
            elif result.group(3).lower() == 'Example Co.':
                return "Internal"
            else:
                return "Example Co."

        elif col_name == 'client':
            return result.group(3)

        return ""  # <-- fallthrough return if col_name is invalid

    except Exception:
        return ""  # fallback in case of failure


## Users Rename

df = pd.read_parquet(f"{dict_dir}/ts_user_info.parquet")
user_dict = df.to_dict(orient="records")


def std_user_names_rename(string=""):
    def std_user_names_rename(string=""):
        if not string:
            return ""

        string_lower = string.lower()
        for e in user_dict:
            try:
                if e['currentName'].lower() == string_lower:
                    return e['fullName']
                elif e['firstName'].lower() == string_lower:
                    return e['fullName']
                elif e['lastName'].lower() == string_lower:
                    return e['fullName']
                elif e['fullName'].lower() == string_lower:
                    return e['fullName']
            except Exception:
                continue

        return string  # fallback if nothing matched


## Strip out Client name from Description or Title

def strip_client_name(row):
    string = row['Project']

    print(f'Original String: {string.lower()}')

    replacement = (re.sub('[:|,\s\t]', " ", string)).rstrip()
    print(f'First Replacement value: {replacement}')

    for e in client_rename_dict:
        try:
            if len(e['[REDACTED]']) >= 5:
                if e['[REDACTED]'].lower() in replacement.lower():
                    # print(f"key found: {e['[REDACTED]'].lower()}")
                    replacement = re.sub(e['[REDACTED]'].lower(), e['currentName'].lower(), replacement.lower())
                    print(f'Second Replacement value: {replacement}')
                    break
        except Exception as e:
            print(e)

    replacement = re.sub("(360|[NnSs][[Oo]cC])", "", replacement.lower())
    print(f'Third Replacement value: {replacement}')

    client = row['clientName'].lower()
    print(f"Client Name: {client}")

    print(replacement.find(' - '))

    if replacement.find(' - ') >= 0:
        replacement = replacement[replacement.find(' - '):]

    client_name_list = re.findall(r"(\w+)\s?", client)
    print(f"Client Name: {client_name_list}")

    for word in client_name_list:
        replacement = re.sub(word.lower(), "", replacement.lower())

    print(f'Fourth Replacement value: {replacement}')

    replacement = re.sub(r"\w+\s+?-\s+?", "", replacement.lower())
    print(f'Fifth Replacement value: {replacement}')

    replacement = re.sub("\s{2,}", " ", replacement.lower())
    replacement = re.sub("\s+?-?\s+?", " ", replacement.lower())
    replacement = re.sub("-", " ", replacement.lower())
    replacement = replacement.lstrip().rstrip()
    print(f'Sixth Replacement value: {replacement}')

    replacement = replacement.title()
    print(f'Final Replacement value: {replacement}')
    print("*" * 50 + "\n")

    return replacement


## Parse Action

project_names_dict = pd.read_parquet(f'{dict_dir}/project_names.parquet').to_dict(orient='records')


def parse_action(string=""):
    string_lower = string.lower()

    for entry in project_names_dict:
        keyword = entry.get('keyword', '').lower()
        std_action = entry.get('stdAction')

        if not keyword or std_action is None:
            continue  # Skip malformed entries

        if keyword == string_lower or keyword in string_lower:
            return std_action

    return None  # Explicit return if no match found


## Parse Service


def parse_service(row):
    # service
    service = ""

    try:
        service = re.sub(row['Action'].lower(), "", row['Objective'].lower())
    except Exception as e:
        pass

    if service == "":
        service = str(row['department']) + " " + str(row['Action'])

        service = re.sub(r'(noc|soc)', "", service)
        service = re.sub(r'\s?-\s?', "", service)
        service = re.sub(r'\s{2,}', " ", service)

    return service.lower()


## Break up POD Goals

i = 0


def breakup_pod_goals(string):
    string = re.sub(r'\n{2,}', '\n', string)
    results = re.findall(r'([^\n]+)\n?', str(string))

    # Create returnable row
    row = {}

    if len(results) == 2:
        row['Week 1 - Goals'] = re.sub(r'Week\s\d:\s', "", results[0])
        row['Week 2 - Goals'] = re.sub(r'Week\s\d:\s', "", results[1])
    elif len(results) == 1:
        row['Week 1 - Goals'] = re.sub(r'Week\s\d:\s', "", results[0])
        row['Week 2 - Goals'] = re.sub(r'Week\s\d:\s', "", results[0])
    else:
        row['Week 1 - Goals'] = ""
        row['Week 2 - Goals'] = ""

    return row


# Shaping Algorithms
## Teamwork

# Create shaper class
shaper = NameShaping("D:\Git\data_parsing\dictionaries")

# Import teamwork portal export
df_teamwork = pd.read_csv(teamwork_file, encoding='latin1', index_col=False)

df_teamwork['reword_cn'] = df_teamwork['Company'].apply(shaper.reword_credit_union)

# Parse Client Names column identifying data and create columns
df_teamwork['clientName'] = df_teamwork['reword_cn'].apply(parse_sprint_client_name, args=['client'])
df_teamwork['scope'] = df_teamwork['reword_cn'].apply(parse_sprint_client_name, args=['scope'])
df_teamwork['department'] = df_teamwork['reword_cn'].apply(parse_sprint_client_name, args=['department'])

df_teamwork['shaped_cn'] = df_teamwork['clientName'].apply(shaper.std_client_names_rename)

df_teamwork['fullName'] = df_teamwork['Who'].apply(std_user_names_rename)

client_rename_dict = pd.read_parquet(f'{dict_dir}/standard_client_names.parquet').to_dict(orient='records')

df_teamwork['Objective'] = ""

client_rename_dict = sorted(client_rename_dict, key=lambda d: len(d['[REDACTED]']), reverse=True)

for index, row in df_teamwork.iterrows():
    stripped_project = strip_client_name(row)
    df_teamwork['Objective'].iloc[index] = stripped_project

df_teamwork['Action'] = df_teamwork['Objective'].apply(parse_action)

df_teamwork['Service'] = ""
for index, row in df_teamwork.iterrows():
    service = parse_service(row)
    df_teamwork['Service'].iloc[index] = service

# Drop original columns and replace with shapped and parsed columns
df_teamwork.drop(
    ['Company', 'clientName', 'Who', 'Tags', 'Invoice Number', 'Estimated', 'Estimated Minutes', 'Estimated Hours', ],
    axis=1, inplace=True)
client_name = df_teamwork.pop('shaped_cn')
df_teamwork.insert(0, 'Client Name', client_name)
scope = df_teamwork.pop('scope')
df_teamwork.insert(1, 'Scope', scope)
department = df_teamwork.pop('department')
df_teamwork.insert(2, 'Department', department)
department = df_teamwork.pop('fullName')
df_teamwork.insert(3, 'Resource Name', department)
objective = df_teamwork.pop('Objective')
df_teamwork.insert(4, 'Objective', objective)
action = df_teamwork.pop('Action')
df_teamwork.insert(5, 'Action', action)
service = df_teamwork.pop('Service')
df_teamwork.insert(6, 'Service', service)
df_teamwork.drop('reword_cn', axis=1, inplace=True)

### Break Up Time into Weeks and Filter

### Time Frame

week_1_start = dt.datetime.strptime("2022/12/18", "%Y/%m/%d")
week_2_end = dt.datetime.strptime("2023/01/01", "%Y/%m/%d")

#### Find First Day of Sprint

df_teamwork['Date'].min()
today = dt.date.today()
monday = today + dt.timedelta(days=-today.weekday())
dt.date.strftime(monday, "%Y/%m/%d")

first_entry = df_teamwork['Date'].min()
previous_monday = today + dt.timedelta(days=-today.weekday())
dt.date.strftime(monday, "%Y/%m/%d")


def sprint_week_from_monday(datetime):
    pass


#### Filter by Time Window

df_teamwork[['Date/Time', 'End Date/Time']] = df_teamwork[['Date/Time', 'End Date/Time']].apply(pd.to_datetime)

sprint_start = df_teamwork['Date/Time'] > week_1_start
sprint_end = df_teamwork['End Date/Time'] > week_1_start

df_teamwork = df_teamwork[sprint_start & sprint_end]

df_teamwork_client = df_teamwork[df_teamwork['Scope'] == 'Client']


#### Seperate out days of the week

def day_of_week(datetime):
    return dt.datetime.strftime(datetime, '%A')


df_teamwork['Date'] = df_teamwork['Date'].apply(pd.to_datetime)

df_teamwork['Day of Week'] = df_teamwork['Date'].apply(day_of_week)

df_teamwork['Day of Week'] = df_teamwork['Date'].apply(lambda x: dt.datetime.strftime(x, '%A'))

## Sprint Doc

import os
import datetime


def AddTime(source_file):
    source_mfdate = 'Source Modified Date'
    source_crdate = 'Source Creation Date'
    source_fn = 'Source Filename'

    # Both the variables would contain time
    # elapsed since EPOCH in float
    ti_c = os.path.getctime(source_file)
    ti_m = os.path.getmtime(source_file)
    fi_n = os.path.basename(source_file)

    # Converting the time in seconds to UTC datetime
    c_ti = datetime.datetime.utcfromtimestamp(ti_c).strftime('%Y/%m/%d %H:%M:%S')
    m_ti = datetime.datetime.utcfromtimestamp(ti_m).strftime('%Y/%m/%d %H:%M:%S')

    return {source_crdate: c_ti, source_mfdate: m_ti, source_fn: fi_n}


AddTime(sprint_file)

# Import Sprint Log
df_sprint_log = pd.read_excel(sprint_file, sheet_name="Sprint Pods")

# Rename Sprint Pods to 'Objective' to use function for parsing parts
df_sprint_log.rename({"Pod Name": "Objective"}, axis=1, inplace=True)

# Drop Rows with no Allocated Hours
df_sprint_log = df_sprint_log[~((df_sprint_log['Week 1 - Hours'] == 0) & (df_sprint_log['Week 2 - Hours'] == 0))]

# Drop NaN rows threshold of 5 blank cells and drop 'Total' client Row
df_sprint_log = df_sprint_log.dropna(thresh=5)
df_sprint_log = df_sprint_log[df_sprint_log['Client Name'] != "Total"]

# Parse Client Names column identifying data and create columns
df_sprint_log['clientName'] = df_sprint_log['Client Name'].apply(parse_sprint_client_name, args=['client'])
df_sprint_log['scope'] = df_sprint_log['Client Name'].apply(parse_sprint_client_name, args=['scope'])
df_sprint_log['department'] = df_sprint_log['Client Name'].apply(parse_sprint_client_name, args=['department'])

# Shape all client names to standard
df_sprint_log['shaped_cn'] = df_sprint_log['clientName'].apply(shaper.std_client_names_rename)

df_sprint_log['fullName'] = df_sprint_log['Resource'].apply(std_user_names_rename)
df_sprint_log['shaped_leader'] = df_sprint_log['Leader'].apply(std_user_names_rename)
df_sprint_log['shaped_pm'] = df_sprint_log['PM'].apply(std_user_names_rename)

df_sprint_log['Action'] = df_sprint_log['Objective'].apply(parse_action)

df_sprint_log['Service'] = ""
for index, row in df_sprint_log.iterrows():
    service = parse_service(row)

    df_sprint_log['Service'].loc[index] = service

df_sprint_log['Client Name'].rename({"All Client": "All Clients"}, inplace=True)

df_sprint_log.dropna(subset=['Week 1 - Hours', 'Week 2 - Hours'], how='all', inplace=True)

df_sprint_log = df_sprint_log.drop(
    ['Week 1 - Priority', 'Week 1- On Track?', 'Week 2 - Priority', 'Week 2- On Track?', 'Total Hours',
     'Sprint Update Notes'], axis=1)

df_sprint_log[['Week 1 - Goals', 'Week 2 - Goals']] = ""
for index, row in df_sprint_log.iterrows():
    for k, v in breakup_pod_goals(row['POD Goals']).items():
        df_sprint_log[k].loc[index] = v

### Re-Order / Re-Name Columns

# Drop original columns and replace with shapped and parsed columns

df_sprint_log.drop(['Client Name', 'clientName', 'Resource', 'Leader', 'PM'], axis=1, inplace=True)

client_name = df_sprint_log.pop('shaped_cn')
df_sprint_log.insert(0, 'Client Name', client_name)
scope = df_sprint_log.pop('scope')
df_sprint_log.insert(1, 'Scope', scope)
department = df_sprint_log.pop('department')
df_sprint_log.insert(2, 'Department', department)
full_name = df_sprint_log.pop('fullName')
df_sprint_log.insert(3, 'Resource Name', full_name)
objective = df_sprint_log.pop('Objective')
df_sprint_log.insert(4, 'Objective', objective)
action = df_sprint_log.pop('Action')
df_sprint_log.insert(5, 'Action', action)
service = df_sprint_log.pop('Service')
df_sprint_log.insert(6, 'Service', service)
wk1_goals = df_sprint_log.pop('Week 1 - Goals')
df_sprint_log.insert(8, 'Week 1 - Goals', wk1_goals)
wk2_goals = df_sprint_log.pop('Week 2 - Goals')
df_sprint_log.insert(10, 'Week 2 - Goals', wk2_goals)
leader = df_sprint_log.pop('shaped_leader')
df_sprint_log.insert(11, 'Leader', leader)
pm = df_sprint_log.pop('shaped_pm')
df_sprint_log.insert(12, 'PM', pm)

### Move Side-by-Side Sprint Data to Stacked by Row

common_cols = \
    ['Client Name', 'Scope', 'Department',
     'Resource Name', 'Objective', 'Action',
     'Service', 'Leader', 'PM',
     'Responsibilities', 'RACI', 'Reason for off track'
     ]


def reorg_week_1(row):
    week_1_row = {}

    for k, v in row[common_cols].items():
        week_1_row[k] = v
    week_1_row['Sprint Week'] = 1
    week_1_row['Sprint Hours'] = row['Week 1 - Hours']
    week_1_row['Sprint Goals'] = row['Week 1 - Goals']

    return week_1_row


def reorg_week_2(row):
    week_2_row = row[common_cols]
    week_2_row['Sprint Week'] = 2
    week_2_row['Sprint Hours'] = row['Week 2 - Hours']
    week_2_row['Sprint Goals'] = row['Week 2 - Goals']

    return week_2_row


wk1_row_list = []
for index, row in df_sprint_log.iterrows():
    wk1_row_list.append(reorg_week_1(row))

df_wk1 = pd.DataFrame(wk1_row_list)

wk2_row_list = []
for index, row in df_sprint_log.iterrows():
    wk2_row_list.append(reorg_week_2(row))

df_wk2 = pd.DataFrame(wk2_row_list)

df_sprint_log_reorg = pd.concat([df_wk1, df_wk2], ignore_index=True)


#### Define Timeframe


#### Separate out days of the week

def day_of_week(datetime):
    return dt.datetime.strftime(datetime, '%A')


df_teamwork['Date'] = df_teamwork['Date'].apply(pd.to_datetime)

df_teamwork['Day of Week'] = df_teamwork['Date'].apply(day_of_week)

df_teamwork['Day of Week'] = df_teamwork['Date'].apply(lambda x: dt.datetime.strftime(x, '%A'))

## Unearned Project Rev

df_unearned_rev = pd.read_excel(unearned_rev_file, sheet_name='Sheet1')

df_unearned_rev.drop(df_unearned_rev.columns[0], axis=1, inplace=True)

# Split , Apply, Combine


set(df_teamwork.columns).intersection(set(df_sprint_log_reorg.columns))

set(df_sprint_log['Service'].unique()).intersection(set(df_teamwork['Service'].unique()))

merge_key_cols = ['Client Name', 'Scope', 'Department', 'Resource Name', 'Objective', 'Action']

df_merged = pd.merge(df_sprint_log_reorg, df_teamwork, on=merge_key_cols)

df_teamwork['Client Name'].unique()

import datetime

today = datetime.date.today()
today + datetime.timedelta(days=-today.weekday(), weeks=1)
datetime.date(2009, 10, 26)

"""
Some words of explanation:

Take today's date. Subtract the number of days which already passed this week (this gets you 'last' monday). Add one week.

Edit: The above is for 'next monday', but since you were looking for 'last monday' you could use

today - datetime.timedelta(days=today.weekday())
"""

## Models

# Filter and Export

df_client_sprint_log = \
    df_sprint_log_reorg[df_sprint_log_reorg['Scope'] == 'Client']

df_teamwork_client[
    df_teamwork_client['Resource Name'] == "John Doe"
    ].to_csv(f'{export_folder}.csv', index=False)

df_client_sprint_log[
    df_client_sprint_log['Resource Name'] == "John Doe"
    ].to_csv(f'{export_folder}.csv', index=False)

df_teamwork_client.to_csv(f"{export_folder}.csv", index=False)
df_teamwork.to_csv(f"{export_folder}.csv", index=False)

df_client_sprint_log.to_csv(f"{export_folder}.csv", index=False)
df_sprint_log.to_csv(f"{export_folder}.csv", index=False)
