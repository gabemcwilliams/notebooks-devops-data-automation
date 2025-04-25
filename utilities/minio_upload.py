
"""
MinIO File Upload Utility (MinioExtract)
----------------------------------------

Uploads a DataFrame to a MinIO bucket in one of several supported formats (CSV, JSON, or Parquet).
This class integrates with HashiCorp Vault for credential retrieval and builds structured paths
based on metadata provided in a config dictionary.

Main Capabilities:
------------------
- Retrieves MinIO access credentials securely from Vault
- Supports dynamic file naming based on ETL context (source, product, timestamp, etc.)
- Uploads data as:
    - CSV
    - JSON (records format)
    - Parquet (uncompressed)
- Constructs structured object paths for versioning and partitioning in object storage
- Returns structured success or error payloads for auditability

Config Schema:
--------------
- DETAILS: metadata (task name, source method, product, subject)
- DATA:
    - destination:
        - file_type: ['csv', 'json', 'parquet']
        - bucket: name of the target MinIO bucket
- TIMESTAMPS: dictionary of standard datetime strings for naming
- SECRETS: includes Vault mount and path to retrieve MinIO credentials

Use Cases:
----------
- Staging raw or cleaned data for analytics workflows
- Archiving ETL outputs in S3-compatible storage
- Building cloud-agnostic pipelines using open tools

Dependencies:
-------------
- `pandas`
- `minio`
- `hvac`
- `io.BytesIO`, `traceback`, `re`, `os`

Author: Gabe McWilliams
"""



import os
from minio import Minio
from io import BytesIO
import re
import traceback
import hvac


class MinioExtract:

    def __init__(self, df_input, config):
        self.__df_input = df_input
        self.__details = config["DETAILS"]
        self.__data = config["DATA"]
        self.__timestamps = config["TIMESTAMPS"]
        self.__secrets = config["SECRETS"]
        self.__secrets.update(self.read_secret(mount_point=config["SECRETS"]["mount_point"],
                                               path=config["SECRETS"]["path"]))

    @staticmethod
    def read_secret(mount_point: str, path: str) -> dict:
        ca_path = os.environ.get("SSL_CERT_FILE")
        client = hvac.Client(verify=ca_path)
        print(f"client is authenticated: {client.is_authenticated}")
        resp = client.secrets.kv.read_secret(mount_point=mount_point, path=f'/{path}')
        secret = resp['data']['data']

        return secret

    def __create_minio_client__(self):
        try:
            minio_client = Minio(
                endpoint=re.sub("https?://", "", self.__secrets["url"]),
                secure=True,
                access_key=self.__secrets["accessKey"],
                secret_key=self.__secrets["secretKey"]
            )

            return {
                "data": minio_client,
                "result": {
                    "job_title": self.__details["task_title"],
                    "status_code": 200,
                    "message": "minio client created"
                }
            }
        except Exception as e:
            return {
                "result": {
                    "job_title": self.__details["task_title"],
                    "status_code": 500,
                    "message": traceback.format_exc()
                }
            }

    def __create_upload_details__(self):
        filename_details = [
            self.__details["source_method"],
            self.__timestamps["_OUT_DATA_TIMESTAMP"],
            self.__details["product"],
            self.__details["subject"],
        ]

        filename = ("_".join(filename_details)) + f'.{self.__data["destination"]["file_type"]}'

        bucket_location_details = [
            self.__details["product"],
            self.__details["subject"],
            self.__details["source_method"],
            self.__timestamps["_YEAR_DATA_TIMESTAMP"],
            self.__timestamps["_MONTH_DATA_TIMESTAMP"],
            self.__timestamps["_DAY_DATA_TIMESTAMP"],
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
            if self.__data["destination"]["file_type"] == "parquet":
                flat_file = self.__df_input.to_parquet(index=False)
            elif self.__data["destination"]["file_type"] == "csv":
                flat_file = self.__df_input.to_csv(index=False)
            elif self.__data["destination"]["file_type"] == "json":
                flat_file = str.encode(self.__df_input.to_json(orient="records"))

            minio_client.put_object(
                bucket_name=self.__data["destination"]["bucket"],
                object_name=minio_object,
                data=BytesIO(flat_file),
                length=len(flat_file),
                content_type=f'application/{self.__data["destination"]["file_type"]}')

            return {
                "data": minio_object,
                "result": {
                    "job_title": self.__details["task_title"],
                    "status_code": 200,
                    "file_format": self.__data["destination"]["file_type"],
                    "message": "File uploaded to minio",
                }
            }

        except:
            return {
                "result": {
                    "job_title": self.__details["task_title"],
                    "status_code": 500,
                    "file_format": self.__data["destination"]["file_type"],
                    "message": traceback.format_exc()
                }
            }

if __name__ == "__main__":


    # Load config and data
    with open(".yaml", "r") as f:
        config = yaml.safe_load(f)

    df = pd.read_parquet("./data/output/example.parquet")  # Or CSV/JSON

    uploader = MinioExtract(df_input=df, config=config)
    result = uploader.upload_to_minio()

    print(result)
