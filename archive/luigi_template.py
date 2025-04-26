"""
.py

This script was an early experiment with Luigi as an orchestration tool.

It defines:
- A task to fetch data from the Star Wars API (SWAPI) and write it to a local JSON file
- A simple print-based test task (not used in the DAG run)

This script was part of initial DAG exploration before transitioning to Prefect.

Author: Gabe McWilliams
Date: 2023-04
"""

import luigi
import json
import pandas as pd
import requests


class StarWars(luigi.Task):
    """
    Task: Fetch Star Wars character data and save to a JSON file.
    """
    def output(self):
        return luigi.LocalTarget(".json")

    def run(self):
        url = "https://swapi.tech/api/people/1"  # Fetching Luke Skywalker data
        response = requests.get(url)
        content = response.json()

        with self.output().open("w") as f:
            json.dump(content, f, indent=2)


class TestPrint(luigi.Task):
    """
    Task: Dummy print task (not used in pipeline execution).
    """
    def output(self):
        return luigi.LocalTarget(".txt")

    def run(self):
        with self.output().open("w") as f:
            f.write("Test Successful")


if __name__ == "__main__":
    luigi.build([StarWars()], workers=1, local_scheduler=True)
