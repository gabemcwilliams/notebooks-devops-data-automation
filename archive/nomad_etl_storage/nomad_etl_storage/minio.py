"""

Title: Minio [LOAD]
Created by: Gabe McWilliams
Date: 2023/04/19
Modified: 2023/09/15

Description:
    Load data from Dataframe to MinIO.

"""

import os
import yaml
from minio import Minio
from io import BytesIO
import re
import traceback
import hvac
import logging
import datetime as dt


class MinioLoad:

    def __init__(self, df, config_dir, logger):

        utc_now = dt.datetime.utcnow()  # datetime for cataloging

        self.__data_timestamps = {
            "_OUT_DATA_TIMESTAMP": utc_now.strftime('%Y_%m_%d_%H%M%S'),  # timestamp found in file
            "_YEAR_DATA_TIMESTAMP": f'{utc_now.year}',  # folder and path dates
            "_MONTH_DATA_TIMESTAMP": f'{utc_now.month:02d}',  # folder and path dates
            "_DAY_DATA_TIMESTAMP": f'{utc_now.day:02d}',  # folder and path dates

        }

        self.__df = df

        self.__config = self.read_config(yaml_dir=config_dir)

        self.__direction = self.__config["DIRECTION"]
        self.__vault = self.__config["VAULT"]
        self.__bucket = self.__config["BUCKET"]
        self.__source_method = self.__config["SOURCE_METHOD"]
        self.__product = self.__config["PRODUCT"]
        self.__route = self.__config["ROUTE"]
        self.__file_type = self.__config["FILE_TYPE"]
        self.__region = self.__config["REGION"]
        self.__logging = self.__config["LOGGING"]

        self.__title = '[{}] - {}.{}.{}'.format(
            self.__direction,
            self.__bucket,
            self.__source_method,
            self.__product,
            self.__route
        )

        self.__logger = self.create_logger()

        self.__secrets = self.read_secret(
            mount_point=self.__vault["MOUNT_POINT"],
            path=self.__vault["PATH"])

    @staticmethod
    def read_secret(mount_point, path):
        client = hvac.Client()
        resp = client.kv.v2.read_secret(mount_point=mount_point, path=f'/{path}')
        secret = resp['data']['data']

        return secret

    @staticmethod
    def read_config(yaml_dir):
        for root, dirs, files in os.walk(yaml_dir):
            for file in files:
                if file.startswith("minio") & file.endswith(".yaml"):
                    with open(os.path.join(root, file), 'r') as f:
                        config = yaml.safe_load(f)

        return config

    def create_logger(self):
        logger = logging.getLogger(__name__)

        # create file handler which logs even debug messages
        fh = logging.FileHandler('minio_{}_{}_{}_{}.log'.format(
            self.__direction,
            self.__bucket,
            self.__source_method,
            self.__product,
        ))
        fh.setLevel(logging.INFO)

        # create console handler with a higher log level
        ch = logging.StreamHandler(
        )
        ch.setLevel(logging.INFO)

        # TODO: add syslog server
        # # create syslog handler
        # syslog = logging.handlers.SysLogHandler(address='/dev/log')
        # syslog.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # syslog.setFormatter(formatter)

        # add the handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)
        # logger.addHandler(syslog)

        return logger

    def __create_minio_client__(self):
        try:
            minio_client = Minio(
                endpoint=re.sub("https?://", "", self.__secrets["url"]),
                secure=True,
                access_key=self.__secrets["accessKey"],
                secret_key=self.__secrets["secretKey"]
            )

            self.__logger.info("minio client created")

            return {
                "data": minio_client,
                "result": {
                    "job_title": self.__title,
                    "status_code": 200,
                    "message": "minio client created"
                }
            }
        except Exception as e:

            self.__logger.error(traceback.format_exc())

            return {
                "result": {
                    "job_title": self.__title,
                    "status_code": 500,
                    "message": traceback.format_exc()
                }
            }

    def __create_upload_details__(self):
        filename_details = [
            self.__source_method,
            self.__data_timestamps["_OUT_DATA_TIMESTAMP"],
            self.__product,
            self.__route,
        ]

        filename = "_".join(filename_details) + f'.{self.__file_type}'

        bucket_location_details = [

            self.__product,
            self.__route,
            self.__data_timestamps["_YEAR_DATA_TIMESTAMP"],
            self.__data_timestamps["_MONTH_DATA_TIMESTAMP"],
            self.__data_timestamps["_DAY_DATA_TIMESTAMP"],
            filename
        ]

        bucket_location = "/".join(bucket_location_details)

        return bucket_location

    def upload_to_minio(self):
        flat_file = None
        try:
            data = self.__create_minio_client__()
            minio_client = data["data"]
            minio_object = self.__create_upload_details__()

            # Create buffer with dataframe
            if self.__file_type == "parquet":
                flat_file = self.__df.to_parquet(index=False)
            elif self.__file_type == "csv":
                flat_file = self.__df.to_csv(index=False)
            elif self.__file_type == "json":
                flat_file = str.encode(self.__df.to_json(orient="records"))

            minio_client.put_object(
                bucket_name=self.__bucket,
                object_name=minio_object,
                data=BytesIO(flat_file),
                length=len(flat_file),
                content_type=f'application/{self.__file_type}')

            self.__logger.info("File uploaded to minio")

            return {
                "data": minio_object,
                "result": {
                    "job_title": self.__title,
                    "status_code": 200,
                    "file_format": self.__file_type,
                    "message": "File uploaded to minio",
                }
            }

        except:

            self.__logger.error(traceback.format_exc())

            return {
                "result": {
                    "job_title": self.__title,
                    "status_code": 500,
                    "file_format": self.__file_type,
                    "message": traceback.format_exc()
                }
            }
