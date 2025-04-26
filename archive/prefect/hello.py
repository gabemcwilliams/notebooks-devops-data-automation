from prefect import flow, task
from prefect.filesystems import RemoteFileSystem
import hvac
import os

#
# def read_secret(mount_point, path):
#     ca_path = os.environ.get("SSL_CERT_FILE")
#     client = hvac.Client(verify=ca_path)
#     resp = client.kv.v2.read_secret(mount_point=mount_point, path=f'/{path}')
#     secret = resp['data']['data']
#
#     return secret
#
#
# # pull vault secret for minio backup user
# minio_secret = read_secret(
#     mount_point="localhost",
#     path="minio/prefect",
# )
#
# # define block for prefect deployment storage
# minio_block = RemoteFileSystem(
#     basepath=f"s3:/{minio_secret['bucket']}",
#     settings={
#         "key": f"{minio_secret['accessKey']}",
#         "secret": f"{minio_secret['secretKey']}",
#         "client_kwargs": {"endpoint_url": f"{minio_secret['url']}"},
#     },
# )
#
# # save block
# minio_block.save("minio")


@task
def create_msg():
    msg = "Hello from Prefect"
    return msg


@flow
def hello_world():
    task_message = create_msg()
    print(task_message)


if __name__ in "__main__":
    hello_world()
