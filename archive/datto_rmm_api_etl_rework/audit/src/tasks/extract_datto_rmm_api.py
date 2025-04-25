


# Data Shaping
import pandas as pd
import datetime as dt

# API Calls
import requests
from requests.structures import CaseInsensitiveDict

# File Handling and Export
import json
import os
import hvac
import traceback


class DattoRMM:

    def __init__(self, config):
        self.__details = config["DETAILS"]
        self.__origin = config["ORIGIN"]
        self.__destination = config["DESTINATION"]
        self.__data = config["DATA"]
        self.__logging = config["LOGGING"]
        self.__timestamps = config["TIMESTAMPS"]
        self.__secrets = self.read_secret(self.__origin["TYPE"], self.__origin["VARS"])
        data = self.__create_token()
        self.__access_token = data["access_token"]

    @staticmethod
    def read_secret(mount_point, path):

        client = hvac.Client()
        resp = client.kv.v2.read_secret(mount_point=mount_point, path=f'/{path}')
        secret = resp['data']['data']

        return secret

    def __create_token(self):
        try:
            # call token api url
            token_uri = f'{self.__secrets["base_uri"]}/auth/oauth/token'

            # construct header
            headers = CaseInsensitiveDict()
            headers["Content-Type"] = "application/x-www-form-urlencoded"

            # construct req body
            data = CaseInsensitiveDict()
            data["grant_type"] = "password"
            data["username"] = self.__secrets["api_key"]
            data["password"] = self.__secrets["api_secret"]

            # request content response
            resp = requests.post(token_uri, headers=headers, data=data, auth=("public-client", "public"))
            content = resp.content.decode("utf-8")
            c_dict = json.loads(content)

            return {
                "access_token": c_dict["access_token"],
                "result": {
                    "job_title": self.__details["TITLE"],
                    "status_code": 200,
                    "message": "Success"
                }
            }

        except Exception as e:
            return {
                "access_token": "error",
                "result": {
                    "job_title": self.__details["TITLE"],
                    "status_code": 500,
                    "message": traceback.format_exc()
                }
            }

    def __api_pagination(self, url):
        try:
            # construct header
            headers = CaseInsensitiveDict()
            headers["Authorization"] = f'Bearer {self.__access_token}'
            headers["Content-Type"] = "application/json"

            # construct req body
            data = ''

            print(f'Request URL: {url}')

            resp = requests.get(url, headers=headers, data=data)
            content = resp.content.decode('utf-8')
            print(content)
            c_dict = json.loads(content)

            return {
                "data": c_dict,
                "result": {
                    "status_code": 200,
                    "task_title": self.__details["TITLE"],
                    "message": "Success"
                }
            }

        except Exception as e:
            return {
                "result": {
                    "job_title": self.__details["TITLE"],
                    "status_code": 500,
                    "message": traceback.format_exc()
                }
            }

    def create_devices_dataframe(self):
        try:
            # Create Devices DataFrame
            request_url = f'{self.__secrets["base_uri"]}/api/v2/account/devices'
            data = self.__api_pagination(request_url)
            c_dict = data["data"]

            # iterate and combine remaining pages
            df = pd.DataFrame(c_dict["devices"])
            while c_dict["pageDetails"]["nextPageUrl"]:
                next_page = c_dict["pageDetails"]["nextPageUrl"]
                data = self.__api_pagination(next_page)
                c_dict = data["data"]
                print(c_dict["pageDetails"]["nextPageUrl"])
                df_current_page = pd.DataFrame(c_dict["devices"])
                df = pd.concat([df, df_current_page], ignore_index=False)

            df['lastAuditDate'] = pd.to_datetime(df['lastAuditDate'], unit='ms', errors='coerce')

            df['lastSeen'] = pd.to_datetime(df['lastSeen'], unit='ms', errors='coerce')

            df['creationDate'] = pd.to_datetime(df['creationDate'], unit='ms', errors='coerce')

            df['lastReboot'] = pd.to_datetime(df['lastReboot'], unit='ms', errors='coerce')

            return {
                "data": df,
                "result": {
                    "job_title": self.__details["TITLE"],
                    "status_code": 200,
                    "message": "DataFrame created successfully"
                }
            }

        except Exception as e:
            return {
                "result": {
                    "job_title": self.__details["TITLE"],
                    "status_code": 500,
                    "message": traceback.format_exc()
                }
            }

    def create_open_monitors_dataframe(self):
        request_url = f'{self.__secrets["base_uri"]}/api/v2/account/alerts/open'
        data = self.__api_pagination(request_url)
        c_dict = data["data"]
        # iterate and combine remaining pages
        df_open_alerts = pd.DataFrame(c_dict['alerts'])

        df_open_alerts['timestamp'] = pd.to_datetime(df_open_alerts['timestamp'], unit='ms', errors='coerce')
        print(
            f"Open Monitors DataFrame Timespan: {df_open_alerts['timestamp'].max()} : {df_open_alerts['timestamp'].min()}")

        while c_dict['pageDetails']['nextPageUrl'] is not None:
            try:
                next_page = c_dict["pageDetails"]["nextPageUrl"]
                current_page = next_page
                try:
                    if next_page is None:
                        break
                except:
                    if next_page == 'https://concord-api.centrastage.net/api/v2/account/alerts/open?max=250&page=1':
                        break
                print(next_page)
                data = self.__api_pagination(next_page)
                c_dict = data["data"]
                try:
                    if c_dict["pageDetails"]["nextPageUrl"] == current_page:
                        break
                except:
                    continue

                df_current_page = pd.DataFrame(c_dict['alerts'])

                df_open_alerts = pd.concat([df_open_alerts, df_current_page], ignore_index=False)

                df_open_alerts['timestamp'] = pd.to_datetime(df_open_alerts['timestamp'], unit='ms', errors='coerce')
                df_open_alerts['timestamp'] = df_open_alerts['timestamp'].dt.strftime("%Y-%m-%d %H:%M:%S")

                df_open_alerts['resolvedOn'] = pd.to_datetime(df_open_alerts['resolvedOn'], unit='ms', errors='coerce')
                df_open_alerts['resolvedOn'] = df_open_alerts['resolvedOn'].dt.strftime("%Y-%m-%d %H:%M:%S")

                return {
                    "data": df_open_alerts,
                    "result": {
                        "job_title": self.__details["TITLE"],
                        "status_code": 200,
                        "message": "Success",
                    }}

            except Exception as e:
                return {
                    "result": {
                        "status_code": 500,
                        "message": traceback.format_exc(),
                    }
                }

    def create_resolved_monitors_dataframe(self, monitor_history_age=7):
        delta = 1 - monitor_history_age
        request_url = f'{self.__secrets["base_uri"]}/api/v2/account/alerts/resolved'
        data = self.__api_pagination(request_url)
        c_dict = data["data"]
        # iterate and combine remaining pages
        df_resolved_alerts = pd.DataFrame(c_dict['alerts'])
        df_resolved_alerts['timestamp'] = pd.to_datetime(df_resolved_alerts['timestamp'], unit='ms', errors='coerce')
        print(
            f"""
                        
            Resolved Monitors DataFrame Timespan: 
            
            {df_resolved_alerts['timestamp'].max()} : {df_resolved_alerts['timestamp'].min()}
            
            """
        )

        days_delta = False
        try:
            while not days_delta:
                request_url = c_dict["pageDetails"]["nextPageUrl"]
                print(request_url)
                data = self.__api_pagination(request_url)
                c_dict = data["data"]
                df_current_page = pd.DataFrame(c_dict["alerts"])

                df_current_page['timestamp'] = pd.to_datetime(df_current_page['timestamp'], unit='ms', errors='coerce')
                df_current_page['timestamp'] = df_current_page['timestamp'].dt.strftime("%Y-%m-%d %H:%M:%S")

                # prepare dictionary for time delta creation
                end_date = df_current_page["timestamp"].max()
                time_delta = dt.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S") - dt.datetime.strptime(
                    self.__timestamps["_IN_DATA_TIMESTAMP"], "%Y-%m-%d %H:%M:%S")

                print(f'Time.Delta.Days: {time_delta.days}')

                days_delta = (time_delta.days <= delta)

                print(f'Timeframe Reached: {days_delta}')

                if days_delta:
                    break

                df_resolved_alerts = pd.concat([df_resolved_alerts, df_current_page], ignore_index=False)

                df_resolved_alerts['resolvedOn'] = (
                    pd.to_datetime(df_resolved_alerts['resolvedOn'], unit='ms', errors='coerce'))
                df_resolved_alerts['resolvedOn'] = df_resolved_alerts['resolvedOn'].dt.strftime("%Y-%m-%d %H:%M:%S")

            return {
                "data": df_resolved_alerts,
                "result": {
                    "job_title": self.__details["TITLE"],
                    "status_code": 200,
                    "message": "Success",
                }
            }

        except Exception as e:
            return {
                "result":
                    {
                        "status_code": 500,
                        "message": traceback.format_exc(),
                    }
            }
