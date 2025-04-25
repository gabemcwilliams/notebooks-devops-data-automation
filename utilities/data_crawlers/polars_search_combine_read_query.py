"""
[REDACTED]/.py

This module defines a `MinioLookUp` class for securely querying and retrieving Parquet objects
from a MinIO bucket using credentials pulled from HashiCorp Vault. It supports object listing
and lazy loading via PyArrow and Polars for downstream processing.

Features:
---------
- Vault integration via `hvac` to retrieve MinIO credentials securely
- MinIO client instantiation for S3-compatible storage
- Object path resolution (bucket existence + prefix-based search)
- Download of up to 3 objects from MinIO, wrapped as PyArrow datasets
- Lazy loading of remote Parquet objects into Polars

Dependencies:
-------------
- polars
- pyarrow
- minio
- hvac
- re, os, traceback, uuid, io

Example:
--------
>>> minio = MinioLookUp()
>>> query = {"bucket": "products", "path": "datto_rmm/devices/api/2023/08"}
>>> result = minio.resolve_query(query)
>>> dataset_query = {"bucket": "products", "object_list": result["data"]["object_list"]}
>>> objects = minio.get_objects(dataset_query)
>>> lazy_df = pl.scan_pyarrow_dataset(objects["data"])
"""

import os
import re
import uuid
import traceback
from io import BytesIO

import polars as pl
import pyarrow.dataset as ds
from minio import Minio
import hvac


class MinioLookUp:
    def __init__(self, query=None):
        if query is None:
            query = {}
        self.query = query
        self.__mountpoint = "localhost"
        self.__path = "MINIO"
        self.__secrets = self.__read_secret__()
        self.__minio = self.__create_minio_client__()["data"]

    def __read_secret__(self):
        client = hvac.Client(url=os.environ.get("VAULT_ADDR"))
        resp = client.kv.v2.read_secret(mount_point=self.__mountpoint, path=f"/{self.__path}")
        return resp['data']['data']

    def __create_minio_client__(self):
        try:
            minio_client = Minio(
                endpoint=re.sub("https?://", "", self.__secrets["url"]),
                secure=False,
                access_key=self.__secrets["accessKey"],
                secret_key=self.__secrets["secretKey"]
            )
            return {
                "data": minio_client,
                "result": {"status_code": 200, "message": "MinIO client created"}
            }
        except Exception:
            return {
                "result": {
                    "status_code": 500,
                    "message": traceback.format_exc()
                }
            }

    def resolve_query(self, query, max_results=100):
        try:
            path_exists = self.__minio.bucket_exists(query["bucket"])
            result = self.__minio.list_objects(query["bucket"], recursive=True, prefix=query["path"])
            object_list = []

            for i, obj in enumerate(result):
                if i >= max_results:
                    break
                object_list.append(obj.object_name)

            return {
                "data": {
                    "path_exists": path_exists,
                    "object_list": object_list
                },
                "result": {
                    "status_code": 200,
                    "message": "Query resolved"
                }
            }
        except Exception:
            return {
                "result": {
                    "status_code": 500,
                    "message": traceback.format_exc()
                }
            }

    def get_objects(self, query):
        ds_list = []
        try:
            for obj_name in query["object_list"][:3]:
                response = self.__minio.get_object(query["bucket"], obj_name)
                buffer = BytesIO(response.read())
                response.close()
                response.release_conn()

                # Load into Arrow Dataset wrapper
                dataset = ds.dataset(buffer, format="parquet")
                ds_list.append(dataset)

            return {
                "data": ds_list,
                "result": {
                    "status_code": 200,
                    "message": "Objects consumed"
                }
            }
        except Exception:
            return {
                "result": {
                    "status_code": 500,
                    "message": traceback.format_exc()
                }
            }

# Optional test code (can move to a notebook or test module)
if __name__ == "__main__":
    minio = MinioLookUp()
    query = {
        "bucket": "products",
        "path": "datto_rmm/devices/api/2023/08"
    }
    result = minio.resolve_query(query)
    print(result)

    if result["result"]["status_code"] == 200:
        object_query = {
            "bucket": query["bucket"],
            "object_list": result["data"]["object_list"]
        }
        obj_result = minio.get_objects(object_query)
        print(obj_result)

        if obj_result["result"]["status_code"] == 200:
            lazy_df = pl.scan_pyarrow_dataset(obj_result["data"])
            print(lazy_df.schema)
