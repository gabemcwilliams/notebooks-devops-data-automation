import extract_msg
import os
import datetime as dt
import re
import traceback
import pandas as pd

from pathlib import Path
from shutil import copy2

source_root_dir = 'D:/cache/mystery_emails'
dest_root_dir = 'D:/cache/parsed_emails/'

email_accounts_list = [
    'alerts_example_co',
    'soc_example_co',
    'support_example_co'
]


def verify_to_address(email_str: str | None) -> bool:
    acceptable_destinations_list = [
        'alerts',
        'alerts@example.co',
        'licenses@abc.com',
        'alerts@abc.com',
        '@abc.com',
        '@example.co',
        'abc.com'
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


index = 0
current_time = (dt.datetime.utcnow().strftime('%Y_%m_%d_%H%M%S'))
df = pd.DataFrame()

for email_account in email_accounts_list[:]:

    source_root_dir = 'D:/cache/mystery_emails'
    source_dir = f'{source_root_dir}/{email_account}/suspicious_msgs'

    dest_dir = f'{dest_root_dir}/{email_account}/parsed_info'
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    ## Traverse Directory for all Emails and add to List
    all_source_msg = [file_name for file_name in os.listdir(
        source_dir) if '.msg' in file_name]

    email_info_list = []

    for eml in all_source_msg[:]:
        header = "[MISSING]"

        try:

            msg = extract_msg.Message(source_dir + "/" + eml)
            msg_dict = {}
            for k, v in msg.__dict__.items():
                # print(k)

                if k.lower().replace(": ", "") in ["filename", "body", "attachments", "sender"]:
                    if isinstance(v, str):
                        msg_dict[k.lower()] = v.lower()[:1000]
                    else:
                        msg_dict[k.lower()] = v
                if k.lower() == "header":
                    header = v

                    for i, j in v.items():
                        # print(i)
                        if i.lower() in ["to", "from", "subject", "date", "return-path"]:
                            msg_dict[i.lower()] = j.lower()[:1000]
                # else:
                #     continue
            try:
                if (msg_dict['to'] is None) | (msg_dict['to'] == "") | (msg_dict['to'] == " "):
                    str_msg = '[TO ADDRESS MISSING]'
            except:
                msg_dict['to'] = '[TO ADDRESS MISSING]'

            if verify_to_address(msg_dict["to"]):
                str_msg = (msg_dict['to'])[:20]

                formatted_to = re.sub(r'[<>\-@\s.;:\"\',()\[\]_]+', '_', str_msg)
                formatted_to = f"{formatted_to}_{current_time}".replace('__', '_')
                formatted_to = re.sub(r'^_', '', formatted_to)

                save_path = f"{dest_dir}/{formatted_to}"
                Path(save_path).mkdir(parents=True, exist_ok=True)
                with open(f"{save_path}/{formatted_to}.json", "w") as f:
                    f.write(str(msg_dict))

                with open(f"{save_path}/{formatted_to}.txt", "w") as f:
                    f.write(str(header))

                copy2(f"{source_dir}/{eml}", f"{save_path}/{formatted_to}_info.msg")

                msg_dict["save_path"] = save_path

                email_info_list.append(msg_dict)

        except Exception as e:
            print(f"Error with {source_root_dir}/{email_account}/suspicious_msgs/{eml}")
            print(traceback.format_exc())
            continue

    if index == 0:
        df = pd.DataFrame(email_info_list)
        df.to_csv(f"{dest_root_dir}/{email_account}_{current_time}.csv", index=False)
        index += 1
    else:
        df_current = pd.DataFrame(email_info_list)
        df_current.to_csv(f"{dest_root_dir}/{email_account}_{current_time}.csv", index=False)
        df = pd.concat([df_current, df], ignore_index=True)
        index += 1

df.to_csv(
    f"{dest_root_dir}/combined_{current_time}.csv", index=False
)
