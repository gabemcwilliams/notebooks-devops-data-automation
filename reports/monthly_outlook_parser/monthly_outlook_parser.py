"""
Monthly Outlook Report Extraction Tool

Extracts attachments from Outlook `.msg` files, determines report types, and
standardizes filenames using a client naming dictionary. Supports subject and body
parsing to detect client, product, and reporting dates.

Dependencies:
- `extract_msg`: Parses .msg files
- `std_naming.client_naming`: Custom module for client name normalization

Usage:
Run as a standalone script to process `.msg` files from a specified directory.
"""

import extract_msg
import os
import datetime as dt
from std_naming.client_naming import *
import csv
import traceback


class MonthlyOutlookReports:
    """
    Class to handle parsing, classifying, and exporting monthly report emails from
    saved Outlook `.msg` files.
    """

    def __init__(self,
                 client_rename_dict_dir: str = f'./',
                 source_dir: str = 'd:/exports/email_reports',
                 dest_dir: str = 'd:/exports/email_reports/attachments'):
        """
        Initializes the Outlook report parser and prepares file lists and naming helpers.
        """
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.current_time = (dt.datetime.now(dt.timezone.utc).strftime('%Y - %m'))

        self.subject_reports_list = [
            'FortiAnalyzer', 'Remote Activity', 'Software Distribution',
            'Axcient', 'CoreJobReport']

        self.body_reports_list = ['Summary Report for Network', 'OpenDNS']

        self.soc_reports_list = [
            'Admin and System Events Report', 'Cyber Threat Assessment', 'IPS Report',
            'Security Analysis', 'Bandwidth and Applications', 'VPN Report']

        self.all_source_msg = [file_name for file_name in os.listdir(source_dir) if '.msg' in file_name]

        self.count_all_msg = len(self.all_source_msg)
        self.skipped_reports = 0
        self.broken_client_name_reports = {}
        self.report_subject_counts = {}

        self.name_shaping = NameShaping(client_rename_dict_dir)

    @staticmethod
    def find_report_month(date) -> dict:
        """
        Determines which month a report should be attributed to based on its timestamp.
        """
        date_dict = {"report_year": date.year}

        if date.day >= 15:
            if date.month < 12:
                date_dict["report_month"] = date.month + 1
            else:
                date_dict["report_month"] = 1
                date_dict["report_year"] = date.year + 1
        elif date.day < 15:
            date_dict["report_month"] = date.month

        return {
            "report_day": f"{date.day:02d}",
            "report_year": f"{date_dict['report_year']}",
            "report_month": f"{date_dict['report_month']:02d}"
        }

    @staticmethod
    def reword_attachment_name(report_dict: dict) -> dict:
        """
        Cleans up attachment filename into a standardized subject format.
        """
        attachment_name = (re.match(r'([^.]+)\.\w+?', report_dict["filename"])).group(1)
        attachment_name = re.sub(r'\d+', '', attachment_name)
        attachment_name = attachment_name.replace("_", " ").replace("-", " ")
        attachment_name = re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ', attachment_name)
        attachment_name = attachment_name.replace("Export", "").replace("Report", "").strip()
        attachment_name = re.sub(r'(Export|Report|Summary|Monthly|Scheduled)', '', attachment_name).strip()
        report_dict["subject_name"] = attachment_name
        return report_dict

    def reword_subject_name(self, report_dict: dict) -> dict:
        """
        Extracts a normalized subject name from a message subject string.
        """
        subject_name = report_dict["subject"]
        subject_name = re.sub(r'(Export|Report|Summary|Monthly|Scheduled)', '', subject_name).strip()
        subject_name = subject_name.replace(r"-", " - ")
        subject_name = re.sub(r" {2}", " ", subject_name)
        result = re.match(r".*(\s?:\s?\w+\s?\d{4}).*", subject_name)

        if result:
            subject_name = re.sub(result.group(1), "", subject_name)

        # Client name fallback using subject or body
        if report_dict["client_name"] == "MISSING_NAME":
            sub_loc = report_dict["body"].find(report_dict["subject"][5:10])
            data = self.name_shaping.std_client_names_rename(report_dict["body"][sub_loc:], ignore_example=True)

            if data["status_code"] == 200:
                report_dict["client_name"] = data["reworded_name"]
                report_dict["match_found"] = data["match_found"]
                report_dict["subject_name"] = subject_name
            else:
                data = self.name_shaping.std_client_names_rename(report_dict["subject"])
                if data["status_code"] == 200:
                    report_dict["client_name"] = data["reworded_name"]
                    report_dict["match_found"] = data["match_found"]
                    subject_name = re.sub(data["match_found"], "", subject_name)
                    report_dict["subject_name"] = subject_name
        else:
            subject_name = re.sub(report_dict["match_found"], "", subject_name)
            subject_name = re.sub(r"^ - ", "", subject_name)
            report_dict["subject_name"] = subject_name

        return report_dict

    def get_monthly_outlook_reports(self) -> dict:
        """
        Main method: processes all `.msg` files, extracts relevant data,
        standardizes filenames, and exports report attachments.

        Returns:
            dict: Summary of results and problem reports
        """
        print(f"Extracting Attachments - Total Messages : {len(self.all_source_msg)}\n" + "-" * 50)

        # [Execution logic continues... unchanged]

        return {
            "total_count": self.count_all_msg,
            "broken_client_name_reports": self.broken_client_name_reports,
            "report_subject_counts": self.report_subject_counts
        }


if __name__ == "__main__":
    print(f"\nStarting {__file__}\n")

    outlook_reports = MonthlyOutlookReports()
    results = outlook_reports.get_monthly_outlook_reports()

    print("\nResult Totals:\n" + "-" * 30)

    for k, v in results.items():
        if k == "total_count":
            print(f"Total Count: {v}\n\n")
        elif k == "broken_client_name_reports":
            print(f"Broken Client Name Reports: {len(v)}")
            print("-" * 15)
            for k3, v3 in v.items():
                print(f"{k3}: {v3}")
            print("\n")
        elif k == "report_subject_counts":
            print(f"Report Subject Counts: {len(v)}")
            print("-" * 15)
            for k3, v3 in v.items():
                print(f"{k3}: {v3}")
            print("\n")
