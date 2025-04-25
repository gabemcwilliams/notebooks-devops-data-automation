########################################################
#
#     Title: Main Function Convertible to AWS Lambda
#     Created by: Gabe McWilliams
#     Date: 2023/04/19
#
########################################################


from tasks.extract.extract_datto_rmm_api_devices import *
from tasks.transform.datto_rmm_api_devices import *
from tasks.load.load_minio import *
from tasks.load.load_postgres import *


from utilities import *
import time


def lambda_handler(event, context):
    results_list = []
    task_config = {}

    #####################  API [EXTRACT] - datto_rmm - devices #########################################################

    try:
        task_config = context[0]
        start = time.perf_counter()
        print(announce_start(task_config))

        # create DataFrame from API
        datto = ExtractAPI(task_config)

        data = datto.create_dataframe()
        result = data["result"]
        results_list.append(result)
        df = data["data"]

        # # add marker columns
        df['_SOURCE_PRODUCT'] = task_config["DETAILS"]["PRODUCT"]
        df['_SOURCE_SUBJECT'] = task_config["DETAILS"]["SUBJECT"]
        df['_SOURCE_ORIGIN'] = task_config["ORIGIN"]["TYPE"]
        df['_UTC_EXTRACTION_DATETIME'] = task_config["TIMESTAMPS"]["_IN_DATA_TIMESTAMP"]

    except Exception as e:
        result = {
            "task_name": task_config["DETAILS"]['TITLE'],
            "status_code": 500,
            "message": f"Error: {e}",
        }
        print(result)
        exit(1)

    end = time.perf_counter()
    print(announce_end(task_config, start, end, result))
    print("*" * 150)


    #####################  DataFrame [TRANSFORM] - datto_rmm - devices  ################################################

    try:

        task_config = context[2]
        start = time.perf_counter()
        print(announce_start(task_config))

        data = transform_devices_dataframe(df)
        result = data["result"]
        df = data["data"]

    except Exception as e:
        result = {
            "task_name": task_config["DETAILS"]['TITLE'],
            "status_code": 500,
            "message": f"Error: {e}",
        }

        print(result)
        exit(1)
    end = time.perf_counter()
    print(announce_end(task_config, start, end, result))
    print("*" * 150)


    #####################  API [LOAD] - datto_rmm - devices  #########################################################


    #####################  ********** FINAL RESULTS ************   #####################################################

    print("#" * 75)
    print("\nFINAL RESULTS\n")
    print("--------------------------------")

    for result in results_list:
        print("\n")
        print(json.dumps(result, indent=4))
        print("---------")


    print("\n")
    print("#" * 75)

    exit(0)
