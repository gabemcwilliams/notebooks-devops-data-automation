"""
Microsoft Graph API Shared Mailbox Downloader
---------------------------------------------

This module provides the `DownloadSharedEmail` class, which uses a valid OAuth session
(access token) to download messages and attachments from a shared Microsoft 365 mailbox.

Features:
---------
- Fetch paginated email messages via Microsoft Graph API
- Identify and filter messages with attachments
- Download metadata of each attachment and structure it in a DataFrame
- Optionally save attachment files to disk with organized directory structure

Dependencies:
-------------
- requests
- pandas
- json
- re
- os
- time
- base64
- io
- pathlib

Author: Gabe McWilliams
"""
import pandas as pd
import re
import requests
import json
import time
import base64
from pathlib import Path
from io import BytesIO


class DownloadSharedEmail:
    """
    Downloads email metadata and attachments from a Microsoft 365 shared mailbox
    using the Microsoft Graph API and an OAuth2 access token.

    Attributes:
    -----------
    session : dict
        OAuth session containing 'access_token'
    user_email_address : str
        The email address of the shared mailbox
    resource : str
        Graph API resource endpoint (default: 'messages')
    pages : int
        Number of pages to paginate through (default: 1)
    page_size : int
        Number of messages per page

    Public DataFrames:
    ------------------
    df_shared_emails : pd.DataFrame
        All downloaded emails
    df_emails_with_attachments : pd.DataFrame
        Subset of emails with attachments
    df_email_attachments : pd.DataFrame
        Metadata for attachments in those emails
    """

    def __init__(self, session: dict, user_email_address: str, resource: str = 'messages',
                 pages: int = 1, page_size: int = 10) -> None:
        self.__session = session
        self.user_email_address = user_email_address
        self.resource = resource
        self.pages = pages
        self.page_size = page_size

        self.df_shared_emails = self.__create_shared_emails_dataframe__()
        self.df_emails_with_attachments = self.df_shared_emails[self.df_shared_emails['hasAttachments'] == True]
        self.df_email_attachments = self.__create_email_attachments_dataframe(self.df_emails_with_attachments)

    def __create_shared_emails_dataframe__(self) -> pd.DataFrame:
        """
        Fetch paginated emails from a Microsoft 365 mailbox using Graph API.
        Writes output to a CSV file for reference.

        Returns:
            pd.DataFrame: Combined dataframe of all retrieved email messages.
        """
        df = pd.DataFrame()
        page = 1

        request_url = f"https://graph.microsoft.com/v1.0/users/{self.user_email_address}/{self.resource}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.__session['access_token']}",
        }
        params = { "top": self.page_size }

        while page <= self.pages:
            print(f"Page: {page}")
            print(f"Request URL: {request_url}")

            if page == 1:
                resp = requests.get(request_url, headers=headers, params=params)
            else:
                resp = requests.get(request_url, headers=headers)

            content = resp.content.decode('utf-8')
            c_dict = json.loads(content)

            request_url = c_dict.get('@odata.nextLink', None)
            new_data = pd.DataFrame(c_dict.get('value', []))

            df = pd.concat([df, new_data], ignore_index=True)
            page += 1

            if not request_url:
                break

            time.sleep(1)  # Respect API throttling

        df.to_csv(f'./{self.user_email_address}_{self.resource}.csv', index=False)
        return df

    def __create_email_attachments_dataframe(self, df_source: pd.DataFrame = pd.DataFrame()) -> pd.DataFrame:
        """
        For all messages with attachments, fetch attachment metadata using Graph API.

        Args:
            df_source (pd.DataFrame): DataFrame with email rows containing attachments.

        Returns:
            pd.DataFrame: Metadata for each attachment.
        """
        df = pd.DataFrame()

        for index, row in df_source.iterrows():
            request_url = f"https://graph.microsoft.com/v1.0/users/{self.user_email_address}/{self.resource}/{row['id']}/attachments"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.__session['access_token']}",
            }

            print(f"Request URL: {request_url}")
            resp = requests.get(request_url, headers=headers)
            content = resp.content.decode('utf-8')
            c_dict = json.loads(content)

            if not c_dict.get('value'):
                continue

            attachment = c_dict['value'][0]
            attachment.update({
                'to_address': re.sub(r'[@\.:+]+', "_", row['from']['emailAddress']['address']),
                'from_address': re.sub(r'[@\.:+]+', "_", row['from']['emailAddress']['address']),
                'date_received': row['receivedDateTime'],
                'orig_email_id': row['id']
            })

            df = pd.concat([df, pd.DataFrame([attachment])], ignore_index=True)

        return df

    @staticmethod
    def download_attachments(df_source: pd.DataFrame, target_dir: str = "d:/cache") -> None:
        """
        Save base64-encoded attachments from dataframe to the local file system.

        Args:
            df_source (pd.DataFrame): DataFrame containing attachment metadata.
            target_dir (str): Base directory to store downloaded files.
        """
        for _, row in df_source.iterrows():
            dest_dir = os.path.join(target_dir, row['to_address'], row['from_address'], row['date_received'])
            Path(dest_dir).mkdir(parents=True, exist_ok=True)

            bytesio_object = BytesIO(base64.b64decode(row['contentBytes']))
            file_path = os.path.join(dest_dir, row['name'])

            with open(file_path, "wb") as f:
                f.write(bytesio_object.getbuffer())
