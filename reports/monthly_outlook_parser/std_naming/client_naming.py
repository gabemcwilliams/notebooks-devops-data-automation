"""
Standardized Client Naming Utility

This module provides helper methods to rename client names using a consistent naming convention.
It is designed to support downstream file and report normalization processes (e.g., from email attachments).

Originally created for Example Co., but the naming logic has been obfuscated for generalized use.
"""

import re
import pandas as pd


class ClientNameNormalizer:
    def __init__(self, dictionary_source="./", dictionary_file: str = ".csv") -> None:
        print('\n[Initializing Name Normalizer]\n' + '-' * 20)

        self.__dictionary_source = dictionary_source
        self.dictionary_file = dictionary_file
        self.__client_rename_dict = self.create_client_rename_dict()

    @staticmethod
    def reword_credit_union(string: str = '') -> str:
        """
        Converts verbose credit union phrases to short codes (e.g., 'Federal Credit Union' → 'FCU').
        """
        cu_reword_dict = {'Federal Credit Union': 'FCU', 'Credit Union': 'CU'}
        for k, v in cu_reword_dict.items():
            result = re.sub(k, v, string)
            if result != string:
                return result

        return string

    @staticmethod
    def rename_members_first_cu(string: str = '') -> str:
        """
        Specific rename logic for known special case.
        """
        if string == 'Example CU':
            return 'Example 1st CU'
        else:
            return string

    def create_client_rename_dict(self):
        """
        Loads the client name mapping dictionary from CSV.
        """
        print('Starting create_client_rename_dict...\n')
        df = pd.read_csv(f'{self.__dictionary_source}/{self.dictionary_file}', dtype_backend="pyarrow")
        client_rename_dict = {}
        for index, row in df.iterrows():
            previous_name = row['previousName']
            current_name = row['currentName']
            client_rename_dict[previous_name] = current_name
        return client_rename_dict

    def std_client_names_rename(self, string: str = "", ignore_example: bool = False) -> dict:
        """
        Attempts to match and standardize client names found in a string.

        Args:
            string (str): The source text to analyze
            ignore_example (bool): Optionally skip matches to 'example'

        Returns:
            dict: Information about any match found and the standardized name
        """
        parse_results = {
            "previous_name": string,
            "reworded_name": None,
            "status_code": 500
        }

        for k, v in self.__client_rename_dict.items():
            try:
                if (ignore_example is True) and (v == "example"):
                    continue

                result = re.sub(k.lower(), v, string.lower().strip())
                if re.search(f'.*[^a-zA-Z]{k}[^a-zA-Z].*', string):
                    parse_results.update({"reworded_name": v, "match_found": k, "status_code": 200})
                elif result != string.lower().strip():
                    parse_results.update({"reworded_name": v, "match_found": k, "status_code": 200})
                elif k.lower() == string.lower().strip():
                    parse_results.update({"reworded_name": v, "match_found": k, "status_code": 200})

            except Exception as e:
                print(e)
                print(k)
                print(v)
                parse_results["status_code"] = 500

        return parse_results
