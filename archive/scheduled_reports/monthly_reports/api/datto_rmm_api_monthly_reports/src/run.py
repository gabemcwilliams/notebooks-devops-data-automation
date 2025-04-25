import pathlib
from autojobs import AutoJobs

root_path = pathlib.Path(__file__).parent.resolve(),
job_title = "datto_rmm_api_monthly_reports_ms_patching"


if __name__ == '__main__':
    jobs = AutoJobs(
        root_path=root_path,
        job_title=job_title)
    jobs.run()
