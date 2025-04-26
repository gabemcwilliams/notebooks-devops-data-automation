"""
NameShaping - Standard Naming Utilities Module
------------------------------------------------

This module provides the `NameShaping` class, which is used to standardize
column names and client names in tabular datasets, typically used in ETL
pipelines at Example Co. It supports mapping legacy or inconsistent naming
conventions to clean, analysis-ready formats using CSV-based dictionaries.

Features:
---------
- Rename columns based on a standard naming map (`.csv`)
- Standardize client names using a client mapping file (`.csv`)
- Apply common rewording for Credit Unions (e.g., "Federal Credit Union" → "FCU")
- Handle edge case normalization such as “Example CU” style adjustments

Intended Use:
-------------
Import this module in data shaping or ETL scripts to enforce consistent naming
before downstream analysis, reporting, or database ingestion.

Author: Gabe McWilliams  
Created: 2022-11-08  
Version: 1.0
"""


import re
import pandas as pd


class NameShaping:
    def __init__(self, dictionary_source=""):
        print('initializing Reshape')

        self.dictionary_source = dictionary_source

        # create column_rename_dict
        def __create_column_rename_dict__():
            print('Starting _create_column_rename_dict')
            df = pd.read_csv(f'{self.dictionary_source}.csv')
            column_rename_dict = {}
            for index, row in df.iterrows():
                current_column = row['currentColumn']
                standard_column = row['standardColumn']
                column_rename_dict[current_column] = standard_column
            return column_rename_dict

        # create client_rename_dict
        def __create_client_rename_dict__():
            print('Starting _create_client_rename_dict')
            df = pd.read_csv(f'{self.dictionary_source}.csv')
            client_rename_dict = {}
            for index, row in df.iterrows():
                previous_name = row['previousName']
                current_name = row['currentName']
                client_rename_dict[previous_name] = current_name
            return client_rename_dict

        self.column_rename_dict = __create_column_rename_dict__()
        self.client_rename_dict = __create_client_rename_dict__()

    def std_col_names_rename(self, string):
        for k, v in self.column_rename_dict.items():
            try:
                result = re.sub(k.lower(), v, string.lower())
                # print(f'comparing {k.lower()} with {string.lower()}')
                if result != string.lower():
                    print(f'Keyword found: {k}')
                    print(f'Replacement value: {v}')
                    print('\n')
                    return v
                    break
                elif k.lower() == string.lower():
                    print(f'Keyword found: {k}')
                    print(f'Replacement value: {v}')
                    print('\n')
                    return v
                    break
            except Exception as e:
                print(e)
                break
        return string

    def std_client_names_rename(self, string=""):
        for k, v in self.client_rename_dict.items():
            try:
                result = re.sub(k.lower(), v, string.lower())
                # print(f'comparing {k.lower()} with {string.lower()}')
                if result != string.lower():
                    print(f'Keyword found: {k}')
                    print(f'Replacement value: {v}')
                    print('\n')
                    return v
                    break
                elif k.lower() == string.lower():
                    print(f'Keyword found: {k}')
                    print(f'Replacement value: {v}')
                    print('\n')
                    return v
                    break
            except Exception as e:
                print(e)
                break
        return string

    @staticmethod
    def reword_credit_union(string=''):
        cu_reword_dict = {'Federal Credit Union': 'FCU', 'Credit Union': 'CU'}
        for k, v in cu_reword_dict.items():
            result = re.sub(k, v, string)
            if result != string:
                return result
                break
        return string

    @staticmethod
    def rename_members_first_cu(string):
        if string == 'Example CU':
            return 'Example 1st CU'
        else:
            return string
