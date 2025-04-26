"""
Parquet File Downloader and Aggregator from MinIO (Vault Authenticated)

This script securely connects to a Vault-authenticated MinIO instance to locate and
download Parquet files for a specified date range. Files are selected using a prefix
pattern composed of the product, subject, and source defined in a `.yaml` file.

Main Capabilities:
- Vault-based secret retrieval to configure a secure MinIO client
- Time-windowed prefix scanning of MinIO objects
- Local caching and optional clearing of old Parquet files
- Concatenation of all downloaded Parquet files into a single DataFrame
- Final CSV export with a timestamped filename

Limitations:
- This script is memory-bound: loading many large Parquet files will crash or stall
  on machines with limited RAM.
- The time range must be explicitly set and accurate in the YAML or it will default to the last 7 days.
- Query logic assumes a very specific S3 prefix structure.
- Error handling is minimal for invalid Parquet schema merges or partial downloads.

Suggested Use:
- Run with manageable date ranges (e.g., 1–3 days) for production-sized data.
- Consider moving to a streaming or chunked reader if hitting memory limits.

"""


import pandas as pd
import minio
import re
import requests
import os
import datetime as dt
import hvac
import yaml
from colorama import Style, Fore
from pathlib import Path


class ParquetFileObjectsDownload:
    def __init__(self, cache_dir="d:/cache/", clear_cache=False):
        if clear_cache:
            print("-" * 50)
            print(f"Clearing cache: {cache_dir}")

            for root, dirs, files in os.walk(cache_dir):
                for file in files:
                    if file.endswith(".parquet"):
                        os.remove(f"{root}/{file}")
                        print(f"Removed {root}/{file}")

            print("-" * 50 + "\n")

        self.__cache_dir = cache_dir
        self.__secrets = self.__read_secrets__(mount_point="db", path="minio/jetbrains")
        self.__minio_client = self.__create_minio_client__()
        self.__objects_list = self.create_object_list()
        self.download_objects(self.__objects_list, self.__cache_dir)

    @staticmethod
    def __read_secrets__(mount_point, path):
        ca_path = os.environ.get("SSL_CERT_FILE")
        client = hvac.Client(verify=ca_path)
        print(f"client is authenticated: {client.is_authenticated}")
        resp = client.secrets.kv.read_secret(mount_point=mount_point, path=f'/{path}')
        return resp['data']['data']

    @staticmethod
    def __read_yaml_query__(yaml_path=Path(".yaml")):
        try:
            with open(yaml_path, "r") as f:
                return yaml.safe_load(f)["QUERY"]
        except Exception as e:
            print(e)
            return None

    def __create_minio_client__(self):
        return minio.Minio(
            endpoint=re.sub(r"https?://", "", self.__secrets["url"]),
            access_key=self.__secrets["accessKey"],
            secret_key=self.__secrets["secretKey"],
            secure=True
        )

    def create_object_list(self, days=7):
        query = self.__read_yaml_query__()
        print("\n" + "-" * 50)
        print("QUERY:\n")
        for k, v in query.items():
            print(f"{k}: {v}")
        print("-" * 50 + "\n")

        bucket_name = query["bucket_name"].lower()
        product = query["product"].lower()
        subject = query["subject"].lower()
        source = query["source"].lower()
        start_date = pd.to_datetime(query["start_date"])
        end_date = pd.to_datetime(query["end_date"])

        if start_date is None or end_date is None:
            start_date = dt.datetime.now() - dt.timedelta(days=days)
            end_date = dt.datetime.now()

        if not self.__minio_client.bucket_exists(bucket_name):
            print(f'{Fore.YELLOW}Bucket [ {bucket_name.upper()} ] Does Not Exist!{Fore.RESET}\n')
            return []
        else:
            print(f'{Fore.GREEN}Bucket [ {bucket_name.upper()} ] Exists!{Fore.RESET}\n')

        if end_date < start_date:
            print(f'{Fore.RED}[start_date] must be before [end_date]!{Fore.RESET}')
            print(f'{Fore.YELLOW}[SWAPPING DATES]{Fore.RESET}')
            start_date, end_date = end_date, start_date

        date_list = []
        while start_date <= end_date:
            date_list.append({
                "year": start_date.strftime('%Y'),
                "month": start_date.strftime('%m'),
                "day": start_date.strftime('%d')
            })
            start_date += dt.timedelta(days=1)

        objects_list = []
        for date in date_list:
            prefix = f'{product}/{subject}/{source}/{date["year"]}/{date["month"]}/{date["day"]}/'
            objects = self.__minio_client.list_objects(bucket_name=bucket_name, prefix=prefix, recursive=True)
            for obj in objects:
                objects_list.append({
                    "bucket_name": bucket_name,
                    "year": date["year"],
                    "month": date["month"],
                    "day": date["day"],
                    "prefix": prefix,
                    "filename": re.sub(prefix, "", obj.object_name),
                    "object_name": obj.object_name
                })

        return objects_list

    def download_objects(self, objects_list, export_path):
        print("-" * 50)
        print('Attempting File DOWNLOAD:\n')
        for i, obj in enumerate(objects_list, 1):
            print(f'{i:03d}: {obj["object_name"]}')
            response = None
            try:
                response = self.__minio_client.get_object(
                    bucket_name=obj["bucket_name"],
                    object_name=obj["object_name"]
                )
                with open(f"{export_path}/{obj['filename']}", "wb") as f:
                    f.write(response.data)
            finally:
                if response:
                    response.close()
                    response.release_conn()
        print("-" * 50 + "\n")


if __name__ == "__main__":
    downloader = ParquetFileObjectsDownload(clear_cache=False)

    parquet_files = [
        os.path.join(root, file)
        for root, _, files in os.walk("d:/cache")
        for file in files if file.endswith(".parquet")
    ]

    dfs = [pd.read_parquet(f, dtype_backend="pyarrow") for f in parquet_files]
    df_combined = pd.concat(dfs)

    query = downloader._ParquetFileObjectsDownload__read_yaml_query__()

    filename = f"d:/exports/{dt.datetime.utcnow().strftime('%Y_%m_%d_%H%M%S')}_{query['product']}_{query['subject']}_{query['source']}.csv"
    df_combined.to_csv(filename, index=False)
    print(f"Exported combined DataFrame to {filename}")