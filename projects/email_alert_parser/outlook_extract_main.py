import traceback
import win32com.client
import pandas as pd
import numpy as np
from pathlib import Path

export_folder = 'D:/cache/mystery_emails'

# Connect to Outlook Worker

import win32com.client

outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

account_alerts = outlook.Folders['Alerts']
account_support = outlook.Folders['Example Co. Support']
account_soc = outlook.Folders['Example Co. Security']
account_reports = outlook.Folders['Reports Manager']
account_gmcwilliams = outlook.Folders['gmcwilliams@example.co']

email_accounts_list = [
    {
        'name': 'account_alerts',
        'root_folder': account_alerts,
        'target_folder': account_alerts.Folders['Deleted Items'],
        'export_folder': f"{export_folder}/alerts_example_co/suspicious_msgs"
    },
    {
        'name': 'account_support',
        'root_folder': account_support,
        'target_folder': account_support.Folders['Deleted Items'],
        'export_folder': f"{export_folder}/support_example_co/suspicious_msgs"
    },
    {
        'name': 'account_soc',
        'root_folder': account_soc,
        'target_folder': account_soc.Folders['Deleted Items'],
        'export_folder': f"{export_folder}/soc_example_co/suspicious_msgs"
    }
]


def test_to_address(email_str: str | None) -> bool:
    acceptable_destinations_list = [
        'alerts',
        'alerts@example.co',
        'licenses@abc.com',
        'alerts@abc.com',
        '@abc.com',
        '@example.co'
    ]

    if email_str == '':
        return True

    for dest in acceptable_destinations_list:
        if dest in email_str.lower():
            return False

    if email_str.lower() in acceptable_destinations_list:
        return False
    else:
        return True


df = pd.DataFrame()

for index, account in enumerate(email_accounts_list[2:]):
    Path(account["export_folder"]).mkdir(parents=True, exist_ok=True)

    emails_list = []

    messages = account["target_folder"].Items
    messages.Sort('[ReceivedTime]', True)

    i = 0

    for message in messages:
        i = i + 1
        if i % 1000 == 0:
            print(f"MILESTONE MESSAGE: {i}")
        try:

            # store To address for eval
            try:
                to_address = str(message.To)
            except:
                to_address = ''

            if test_to_address(to_address):

                message_dict = {}
                try:
                    message_dict['from'] = message.SenderEmailAddress
                except:
                    pass
                try:
                    message_dict['to'] = message.To
                except Exception as e:
                    message_dict['to'] = "[CANNOT PARSE]"
                    print(f"account: {account['name']} - message_no: {i} - [CANNOT PARSE]")
                try:
                    message_dict['date'] = message.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
                try:
                    message_dict['subject'] = message.Subject
                except:
                    pass
                try:
                    message_dict['body'] = message.Body
                except:
                    pass
                attachments_list = []
                for attachment in message.Attachments:
                    try:
                        attachment_name = str(attachment).lower()
                        attachments_list.append(attachment_name)

                    except Exception as e:
                        print(f"account: {account['name']} - message_no: {i} - {e[:50]}")

                message_dict['attachments'] = attachments_list
                message_dict['messageObject'] = message

                emails_list.append(message_dict)

                to_address_to_save = (message_dict['to']).lower().replace(" ", "_")
                try:
                    date_to_save = message.ReceivedTime.strftime("%Y_%m_%d_%H%M%S")
                except:
                    date_to_save = f"could_not_parse_date{np.abs(np.random.randn() * 1000)}"

                message.SaveAs(f"{account['export_folder']}/{date_to_save}_{to_address_to_save}.msg")


        except:
            print(f"account: {account['name']} - message_no: {i} - {(str(traceback.format_exc()))[:50]}")
            pass

        if i >= 100000:
            break

    print(f'FINAL COUNT: {i}')

    if index == 0:
        df = pd.DataFrame(emails_list)
        df.to_csv(f"{export_folder}/{account['name']}[REDACTED]/.csv", index=False)
    else:
        df_current = pd.DataFrame(emails_list)
        df_current.to_csv(f"{export_folder}/{account['name']}[REDACTED]/.csv", index=False)
        df = pd.concat([df_current, df], ignore_index=True)

df.to_csv(f"{export_folder}[REDACTED]/.csv", index=False)
