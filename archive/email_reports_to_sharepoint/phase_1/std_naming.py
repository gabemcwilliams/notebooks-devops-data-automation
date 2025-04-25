# -----------------------------------------------------------------------------------------------
# Title: Module - example Standard Naming
# Author: Gabe McWilliams
# Purpose: Renaming Class Module for DataShaping at Example Co.
# Date of Creation: 2022/11/08
# Version 1.0
# -----------------------------------------------------------------------------------------------


import re
import pandas as pd


class NameShaping:
    def __init__(self, dictionary_source=""):
        print('initializing Reshape')

        self.dictionary_source = dictionary_source

        # create column_rename_dict
        def __create_column_rename_dict__():
            print('Starting _create_column_rename_dict')
            df = pd.read_csv(f'{self.dictionary_source}[REDACTED]/.csv')
            column_rename_dict = {}
            for index, row in df.iterrows():
                current_column = row['currentColumn']
                standard_column = row['standardColumn']
                column_rename_dict[current_column] = standard_column
            return column_rename_dict

        # create client_rename_dict
        def __create_client_rename_dict__():
            print('Starting _create_client_rename_dict')
            df = pd.read_csv(f'{self.dictionary_source}[REDACTED]/.csv')
            client_rename_dict = {}
            for index, row in df.iterrows():
                previous_name = row['[REDACTED]']
                current_name = row['currentName']
                client_rename_dict[previous_name] = current_name
            return client_rename_dict


        self.client_rename_dict = __create_client_rename_dict__()


    def std_client_names_rename(self, string=""):
        for k, v in self.client_rename_dict.items():
            try:
                result = re.sub(k.lower(), v, string.lower())
                # print(f'comparing {k.lower()} with {string.lower()}')
                if result != string.lower():
                    print(f'Keyword found: {k}')
                    print(f'Replacement value: {v}')
                    # print('\n')
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
