# dattormm_alerts_open_parser/main.py

import os
import re
import json
import datetime as dt
import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict
from configparser import ConfigParser


def get_api_credentials(config_path: str = "d:/git/example_infrastructure_data_dev/config/env.ini"):
    config = ConfigParser()
    config.read(config_path)
    base_uri = config['dattormm']['base_uri']
    api_key = config['dattormm']['api_key']
    api_secret = config['dattormm']['api_secret']
    return base_uri, api_key, api_secret


def authenticate(base_uri: str, api_key: str, api_secret: str) -> str:
    token_uri = f'{base_uri}/auth/oauth/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'password', 'username': api_key, 'password': api_secret}

    resp = requests.post(token_uri, headers=headers, data=data, auth=('public-client', 'public'))
    resp.raise_for_status()
    content = resp.json()
    return content['access_token']


def fetch_alerts(base_uri: str, token: str) -> pd.DataFrame:
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    request_url = f'{base_uri}/api/v2/account/alerts/open'

    all_alerts = []
    while request_url:
        resp = requests.get(request_url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        alerts = data.get('alerts', [])
        all_alerts.extend(alerts)
        request_url = data['pageDetails'].get('nextPageUrl')

    return pd.DataFrame(all_alerts)


def parse_alerts(df_alerts: pd.DataFrame) -> pd.DataFrame:
    def safe_get(d, key):
        return d.get(key) if isinstance(d, dict) else None

    if 'alertMonitorInfo' in df_alerts.columns:
        df_alerts['sendsEmails'] = df_alerts['alertMonitorInfo'].apply(lambda x: safe_get(x, 'sendsEmails'))
        df_alerts['createsTicket'] = df_alerts['alertMonitorInfo'].apply(lambda x: safe_get(x, 'createsTicket'))
        df_alerts.drop(columns=['alertMonitorInfo'], inplace=True)

    if 'alertContext' in df_alerts.columns:
        df_alerts['alertClass'] = df_alerts['alertContext'].apply(lambda x: safe_get(x, '@class'))
        df_alerts['samples'] = df_alerts['alertContext'].apply(lambda x: safe_get(x, 'samples'))
        df_alerts.drop(columns=['alertContext'], inplace=True)

        status_prog = re.compile(r'\{\'([^\'\"]*)[\s\"\':]+([\s\w\d\.\-]*)')
        df_alerts['statusType'] = df_alerts['samples'].apply(lambda x: status_prog.findall(str(x))[0][0] if x else None)
        df_alerts['statusMessage'] = df_alerts['samples'].apply(lambda x: status_prog.findall(str(x))[0][1] if x else None)
        df_alerts.drop(columns=['samples'], inplace=True)

    if 'diagnostics' in df_alerts.columns:
        diagnostics_prog = re.compile(r'([\w\d\/\\\:\#\=\.\-\s]+)*')
        df_alerts['diagnosticsMessage'] = df_alerts['diagnostics'].apply(lambda x: ''.join(diagnostics_prog.findall(str(x))) if x else None)
        df_alerts.drop(columns=['diagnostics'], inplace=True)

    if 'alertSourceInfo' in df_alerts.columns:
        df_alerts['deviceUid'] = df_alerts['alertSourceInfo'].apply(lambda x: safe_get(x, 'deviceUid'))
        df_alerts['deviceName'] = df_alerts['alertSourceInfo'].apply(lambda x: safe_get(x, 'deviceName'))
        df_alerts['siteUid'] = df_alerts['alertSourceInfo'].apply(lambda x: safe_get(x, 'siteUid'))
        df_alerts['siteName'] = df_alerts['alertSourceInfo'].apply(lambda x: safe_get(x, 'siteName'))
        df_alerts.drop(columns=['alertSourceInfo'], inplace=True)

    # responseActions could be handled similarly if desired
    if 'responseActions' in df_alerts.columns:
        df_alerts.drop(columns=['responseActions'], inplace=True)

    return df_alerts


def main():
    current_time = dt.datetime.utcnow().strftime('%Y_%m_%d_%H%M%S')
    export_folder = 'd:/exports/'

    os.makedirs(export_folder, exist_ok=True)

    base_uri, api_key, api_secret = get_api_credentials()
    token = authenticate(base_uri, api_key, api_secret)
    df_alerts = fetch_alerts(base_uri, token)

    print(f"Fetched {len(df_alerts)} raw alerts.")

    df_parsed = parse_alerts(df_alerts)

    output_path = os.path.join(export_folder, f'dattormm_alerts_open_{current_time}.csv')
    df_parsed.to_csv(output_path, index=False)

    print(f"Parsed and exported {len(df_parsed)} alerts to {output_path}")


if __name__ == "__main__":
    main()
