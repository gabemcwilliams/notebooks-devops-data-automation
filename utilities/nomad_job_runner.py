"""
Nomad Job Runner & Metadata Extractor

- Walks a directory and finds `.hcl` Nomad job files
- Extracts metadata from jobs
- Runs Nomad jobs via subprocess
- Optionally registers jobs via Python Nomad API

Usage:
[REDACTED]/.py --job-dir "./jobs" --run

Dependencies:
    - python-hcl2
    - python-nomad
    - python-hvac (optional, for Vault usage)
"""

import os
import subprocess
import argparse
import hcl2
import json
from nomad import Nomad


def find_job_files(root_dir):
    """Find all .hcl files under root_dir."""
    job_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".hcl"):
                job_files.append(os.path.join(root, file))
    return job_files


def run_nomad_job(job_path):
    """Run a Nomad job using subprocess."""
    print(f"Running Nomad job: {job_path}")
    subprocess.run(f"nomad job run {job_path}", shell=True, check=True)


def parse_job_file(file_path):
    """Parse HCL file into Python dictionary."""
    with open(file_path, 'r') as f:
        return hcl2.load(f)


def extract_metadata(job_dict):
    """Extract useful metadata from job definition."""
    jobs_info_list = []

    for job in job_dict.get("job", []):
        job_info = {}
        job_title = list(job.keys())[0]
        job_data = job[job_title]

        job_info["job_title"] = job_title
        job_info["job_type"] = job_data.get("type", "")
        periodic = job_data.get("periodic", [{}])[0]
        job_info["cron"] = periodic.get("cron", "")
        job_info["prohibit_overlap"] = periodic.get("prohibit_overlap", "")
        job_group = job_data.get("group", [{}])[0]
        group_title = list(job_group.keys())[0]
        group_data = job_group[group_title]
        job_info["group_count"] = group_data.get("count", "")
        task = group_data.get("task", [{}])[0]
        task_title = list(task.keys())[0]
        task_data = task[task_title]
        job_info["driver"] = task_data.get("driver", "")
        job_info["command"] = task_data.get("config", [{}])[0].get("command", "")
        job_info["args"] = task_data.get("config", [{}])[0].get("args", [])

        jobs_info_list.append(job_info)

    return jobs_info_list


def main(job_dir, run_jobs):
    nomad_client = Nomad()
    job_files = find_job_files(job_dir)

    if not job_files:
        print(f"No job files found in {job_dir}")
        return

    for job_file in job_files:
        print(f"\nProcessing: {job_file}")
        job_dict = parse_job_file(job_file)
        metadata = extract_metadata(job_dict)

        print("Metadata:")
        print(json.dumps(metadata, indent=2))

        if run_jobs:
            run_nomad_job(job_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nomad job runner and metadata inspector")
    parser.add_argument("--job-dir", type=str, required=True, help="Path to Nomad job files")
    parser.add_argument("--run", action="store_true", help="Run the job via Nomad CLI")

    args = parser.parse_args()
    main(args.job_dir, args.run)
