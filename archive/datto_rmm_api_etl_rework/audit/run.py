import pathlib


root_path = pathlib.Path(__file__).parent.resolve(),
job_title = "products_datto_rmm_api_devices"


if __name__ == '__main__':
    jobs = AutoJobs(
        root_path=root_path,
        job_title=job_title)
    jobs.run()
