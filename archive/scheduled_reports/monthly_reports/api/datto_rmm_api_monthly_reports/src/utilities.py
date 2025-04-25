import json
import traceback


def logs_schema(results):
    pass


def store_logs(logs_list):
    pass


def announce_start(config):
    try:
        message = {
            "job_title": config["DETAILS"]["TITLE"],
            "status": "Job Started!",
            "configuration": config
        }

        return json.dumps(message, indent=4)

    except Exception as e:
        return {
            "result": {
                "status_code": 500,
                "message": traceback.format_exc()
            }
        }


def announce_end(config, start, end, result):
    try:
        message = {
            "job_title": config["DETAILS"]["TITLE"],
            "status": "Job Finished!",
            "scripts": config["DETAILS"]["SCRIPTS"],
            "time_in_seconds": f"{end - start:0.4f}",
            "results": result
        }

        return json.dumps(message, indent=4)

    except Exception as e:
        return {
            "result": {
                "status_code": 500,
                "message": traceback.format_exc()
            }
        }
