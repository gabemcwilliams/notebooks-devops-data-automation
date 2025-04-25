"""
Module: s3_parser_dict_upload.py

Purpose:
--------
Utility class for uploading local configuration and environment files 
(e.g., `.env`, `.ini`) to a specified S3 bucket. Typically used for 
storing secure automation configs for remote access or archival.

Author: Gabe McWilliams
"""

import os
import re
import boto3
import logging
import datetime as dt
from configparser import ConfigParser
from botocore.exceptions import ClientError


class AwsUploadConfigs:
    """
    Uploads all files in a specified local directory to an S3 bucket.
    Loads AWS credentials from a local `.ini` file.
    """

    def __init__(
        self,
        logging_directory: str = "d:/logging",
        upload_file_path: str = "D:/Git/data_parsing",
        secrets_ini: str = "d:/git/config/env.ini",
        bucket_name: str = "robotic-process-automation"
    ):
        self.logging_directory = logging_directory
        self.upload_file_path = upload_file_path
        self.secrets_ini = secrets_ini
        self.bucket_name = bucket_name
        self.logger = self._create_logger()

    def _create_logger(self) -> logging.Logger:
        """
        Sets up a file-based logger with timestamps.
        """
        log_time = dt.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S')
        filename_time = dt.datetime.utcnow().strftime('%Y_%m_%d')
        log_filename = os.path.join(self.logging_directory, f"{filename_time}_upload_to_s3.log")

        logger = logging.getLogger('aws_config_uploader')
        logger.setLevel(logging.INFO)

        fh = logging.FileHandler(log_filename)
        formatter = logging.Formatter(f'{log_time} - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        return logger

    def _load_aws_credentials(self) -> dict:
        """
        Loads AWS credentials from an INI file.

        Returns:
            dict: Dictionary containing AWS keys
        """
        config = ConfigParser()
        config.read(self.secrets_ini)

        try:
            creds = {
                "aws_access_key_id": config["data_dev_notebook_workstation"]["api_key"],
                "aws_secret_access_key": config["data_dev_notebook_workstation"]["api_secret"],
                "region_name": "us-west-2"
            }
        except KeyError as e:
            self.logger.error(f"Missing credential key in INI: {e}")
            raise

        return creds

    def _get_s3_client(self):
        """
        Initializes a boto3 S3 client using credentials from the .ini file.
        """
        creds = self._load_aws_credentials()
        return boto3.session.Session(**creds).client("s3")

    def upload_directory_to_s3(self):
        """
        Walks through the upload_file_path and uploads each file to the given S3 bucket.
        Maintains relative folder structure.
        """
        s3_client = self._get_s3_client()

        for root, _, files in os.walk(self.upload_file_path):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = re.sub(self.upload_file_path, "", local_path)[1:].replace("\\", "/")

                try:
                    s3_client.upload_file(local_path, self.bucket_name, relative_path)
                    self.logger.info(f"Uploaded: {relative_path}")
                except ClientError as e:
                    self.logger.error(f"Failed to upload {relative_path}: {e}")
