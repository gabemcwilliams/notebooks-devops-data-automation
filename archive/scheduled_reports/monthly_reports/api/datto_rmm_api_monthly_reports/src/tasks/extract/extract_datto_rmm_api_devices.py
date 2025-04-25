########################################################
#
#     Title: API [EXTRACT] - DattoRMM [API] - Devices
#     Created by: Gabe McWilliams
#     Date: 2023/04/19
#
########################################################


# Data Shaping
import pandas as pd

# API Calls
import requests
from requests.structures import CaseInsensitiveDict

# File Handling and Export
import json
import os

import traceback


class ExtractAPI:

    def __init__(self, config):
        self.__details = config["DETAILS"]
        self.__origin = config["ORIGIN"]
        self.__destination = config["DESTINATION"]
        self.__data = config["DATA"]
        self.__logging = config["LOGGING"]
        self.__timestamps = config["TIMESTAMPS"]
        print(f'origin: {self.__origin}')
        print(os.environ.get(self.__origin["VARS"]))
        self.__secrets = json.loads(os.environ.get(self.__origin["VARS"]))
        data = self.__create_token()
        self.__access_token = data["access_token"]

    def create_dataframe(self):
        return self.__create_devices_dataframe__()

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
            print(f'data: {data}')

            # request content response
            resp = requests.post(token_uri, headers=headers, data=data, auth=("public-client", "public"))
            content = resp.content.decode("utf-8")
            print(content)
            c_dict = json.loads(content)

            return {
                "access_token": c_dict["access_token"],
                "result": {
                    "job_title": self.__details["TITLE"],
                    "status_code": 200,
                    "message": "Success"
                }
            }

        except:
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

        except:
            return {
                "result": {
                    "job_title": self.__details["TITLE"],
                    "status_code": 500,
                    "message": traceback.format_exc()
                }
            }

    def __create_devices_dataframe__(self):
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

        except:
            return {
                "result": {
                    "job_title": self.__details["TITLE"],
                    "status_code": 500,
                    "message": traceback.format_exc()
                }
            }
