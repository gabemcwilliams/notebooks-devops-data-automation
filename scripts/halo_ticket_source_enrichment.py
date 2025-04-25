"""
[REDACTED]/.py

This script extracts ticket data from PostgreSQL using AutoJobs configuration,
applies entity-level parsing to infer source domains (email, vendor, URL), and
exports structured results and filtered subsets for service auditing or triage.

Phases:
1. Load configuration via AutoJobs
2. Extract ticket data using PostgresToPandas
3. Parse details field using ParseSource (regex + dictionary + domain extraction)
4. Output unique root domains and optionally filtered subsets (e.g., UPS incidents)

Author: Gabe McWilliams
Date: 2023-05-01
"""

import os
import re
import pandas as pd
from autojobs import AutoJobs
from postgres_extract import PostgresToPandas  # Update to your actual import path


class ParseSource:
    def __init__(self, dict_file='D:/Git/data_parsing/dictionaries/halopsa_regex_ticket_source.parquet'):
        self.__dict_file = dict_file
        self.__create_details_parse_list__()
        self.parse_functions_list = [
            self.__parse_source_url__,
            self.__parse_from_dictionary__,
            self.__parse_source_email_domain__
        ]

    def __create_details_parse_list__(self):
        details_parse_list = []
        df = pd.read_parquet(self.__dict_file)
        for _, row in df.iterrows():
            details_parse_list.append({row['keyPhrase']: row['emailSource']})
        self.details_parse_list = details_parse_list

    def __parse_source_url__(self, string):
        prog = re.compile(r'.*urldefense.proofpoint.com[^_]+[_.]+([^_\s/]{2,20}\.[^_.\s/]{3,20}\.[^_\s\d/&\-]*)_?')
        return [e.lower() for e in set(prog.findall(string))] or None

    def __parse_source_email_domain__(self, string):
        prog = re.compile(r'(@[^.]+\.[^\s\r\n!]+)')
        return [e.lower() for e in set(prog.findall(string))] or None

    def __parse_from_dictionary__(self, string):
        for mapping in self.details_parse_list:
            for key_phrase, source in mapping.items():
                if re.search(key_phrase, string):
                    return [e.strip().lower() for e in source.split(',') if e.strip()] or None
        return None

    def __root_domain_parse__(self, string_list):
        if not string_list or not isinstance(string_list, list):
            return "['COULD NOT PARSE']"
        prog = re.compile(r'([^@.]+)[.@][\w\d]{2,10}$')
        result = prog.findall(string_list[0])
        return result[0] if result else "['COULD NOT PARSE']"

    def __return_email_parse_details__(self, details):
        for func in self.parse_functions_list:
            try:
                result = func(details)
                if result:
                    return result
            except Exception:
                continue
        return None

    def add_parsed_info(self, df):
        df['sourceParseResults'] = df['details'].apply(self.__return_email_parse_details__)
        df['sourceParseResults'].fillna("['COULD NOT PARSE']", inplace=True)
        df['rootParse'] = df['sourceParseResults'].apply(self.__root_domain_parse__)
        df['rootParse'].fillna("['COULD NOT PARSE']", inplace=True)
        return df


if __name__ == '__main__':
    root_path = "d:/exports/"
    job_title = "products_halo_psa_api_assets"

    jobs = AutoJobs(root_path=root_path, job_title=job_title)
    job_data = jobs.run()["data"]

    for i, config in enumerate(job_data):
        print(f"\n--- Processing Job Block {i + 1}: {config['DETAILS']['TITLE']} ---")

        postgres = PostgresToPandas(config=config, root_path=root_path)
        df = postgres.postgresql_to_dataframe()["data"]

        parser = ParseSource()
        df_parsed = parser.add_parsed_info(df)

        # Export unparseable entries
        df_cnp = df_parsed[df_parsed["rootParse"] == "['COULD NOT PARSE']"]
        if not df_cnp.empty:
            df_cnp.to_csv(f"{root_path}/unparseable_records_{i + 1}[REDACTED]/.csv", index=False)

        # Export root domains
        root_domains = df_parsed["rootParse"].dropna().unique()
        with open(f"{root_path}/parsed_domains_{i + 1}[REDACTED]/.txt", "w") as f:
            for root in root_domains:
                f.write(root + "\n")

        # Save enriched DataFrame
        df_parsed.to_csv(f"{root_path}/enriched_tickets_{i + 1}[REDACTED]/.csv", index=False)

        print(f"Finished block {i + 1}, parsed {len(df_parsed)} records.\n")
