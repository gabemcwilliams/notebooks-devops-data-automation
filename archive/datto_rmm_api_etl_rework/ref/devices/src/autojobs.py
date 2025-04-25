########################################################
#
#     Title: Main Application Class
#     Created by: Gabe McWilliams
#     Date: 2023/04/24
#
########################################################

import yaml
import os
import re
import datetime as dt
import time
import hcl2

from playbook import lambda_handler


class AutoJobs:

    def __init__(self, job_title, root_path):
        self.__root_path = root_path
        self.__user_job_title = job_title
        self.__config_docs = self.__find_config_docs__()
        self.__yaml_jobs = (self.__yaml_jobs__())["data"]
        self.__nomad_jobs = (self.__nomad_jobs__())["data"]

    def run(self):
        try:
            print("*" * 75)
            print(f"Searching for {self.__user_job_title} config...")

            data = self.__validate_before_create__()
            tasks = data["data"]
            result = data["result"]

            data = self.__add_data_timestamp__(tasks)
            stamped_tasks = data["data"]
            result = data["result"]

            lambda_handler(self.__user_job_title, stamped_tasks)

            return {
                "data": stamped_tasks,
                "result": {
                    "status_message": "Success",
                    "status_code": 200

                }
            }

        except Exception as e:
            return {
                "result": {
                    "status_message": str(e),
                    "status_code": 500
                }
            }

    def __find_config_docs__(self):
        nomad_docs = []
        yaml_docs = []

        if isinstance(self.__root_path, tuple):
            path = self.__root_path[0]
        else:
            path = self.__root_path

        print(f'Path: {path}')
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".hcl"):
                    nomad_docs.append(os.path.join(root, file))
                elif file.endswith(".yaml"):
                    yaml_docs.append(os.path.join(root, file))

        return {
            "data": {
                "yaml_docs": yaml_docs,
                "nomad_docs": nomad_docs
            },
            "result": {
                "status_message": "Success",
                "status_code": 200
            }
        }

    def __nomad_jobs__(self):
        nomad_jobs = []
        try:
            for doc in self.__config_docs["data"]["nomad_docs"]:
                with open(doc, 'r') as file:
                    nomad_jobs.append(hcl2.load(file))

            return {
                "data": nomad_jobs,
                "result": {
                    "status_message": "Success",
                    "status_code": 200,
                    "job_title": self.__user_job_title},
            }

        except Exception as e:
            return {
                "result": {
                    "job_title": self.__user_job_title,
                    "status_code": 400,
                    "error": str(e)
                }
            }

    def __yaml_jobs__(self):
        yaml_jobs = []
        try:
            for doc in self.__config_docs["data"]["yaml_docs"]:
                with open(doc, "r") as stream:
                    yaml_jobs.append(yaml.safe_load(stream))

            return {
                "data": yaml_jobs,
                "result": {
                    "status_message": "Success",
                    "status_code": 200,
                    "job_title": self.__user_job_title},
            }

        except Exception as e:
            return {
                "result": {
                    "job_title": self.__user_job_title,
                    "status_code": 400,
                    "error": str(e)
                }
            }

    def __validate_before_create__(self):
        try:
            yaml_title = self.__yaml_jobs[0]["JOB_TITLE"]
            environment = self.__yaml_jobs[0]['ENVIRONMENT']
            yaml_tasks = self.__yaml_jobs[0]["TASKS"]
            nomad_title = (re.match(r".*\'job\'\:\s\[\{\'([\w\_]+)\'", str(self.__nomad_jobs[0]))).group(1)
            if (yaml_title == self.__user_job_title) & (nomad_title == self.__user_job_title):
                print("*" * 75)
                message = f"""
                STARTING JOB: {self.__user_job_title} in 10 seconds!

                Stop this job IMMEDIATELY! if this is not the job you are looking for.

                ENVIRONTMENT: {environment}
                """
                print(message)
                print("*" * 75)
                time.sleep(0)

            return {
                "data": yaml_tasks,
                "result": {
                    "status_message": "Success",
                    "status_code": 200
                }
            }


        except Exception as e:
            return {
                "result": {
                    "job_title": self.__user_job_title,
                    "status_code": 400,
                    "error": e
                }
            }

    @staticmethod
    def __add_data_timestamp__(tasks):
        try:
            stamped_tasks = []

            utc_now = dt.datetime.utcnow()  # datetime for cataloging

            data_timestamps = {

                "_IN_DATA_TIMESTAMP": utc_now.strftime('%Y-%m-%d %H:%M:%S'),  # timestamp found inside data
                "_OUT_DATA_TIMESTAMP": utc_now.strftime('%Y_%m_%d_%H%M%S'),  # timestamp found in file
                "_YEAR_DATA_TIMESTAMP": f'{utc_now.year}',  # folder and path dates
                "_MONTH_DATA_TIMESTAMP": f'{utc_now.month:02d}',  # folder and path dates
                "_DAY_DATA_TIMESTAMP": f'{utc_now.day:02d}',  # folder and path dates

            }

            for task in tasks:
                updated_task = task.copy()
                updated_task["TIMESTAMPS"] = data_timestamps
                stamped_tasks.append(updated_task)

            return {
                "data": stamped_tasks,
                "result": {
                    "status_message": "Success",
                    "status_code": 200
                }
            }

        except Exception as e:
            return {
                "result": {
                    "status_message": str(e),
                    "status_code": 500
                }
            }


