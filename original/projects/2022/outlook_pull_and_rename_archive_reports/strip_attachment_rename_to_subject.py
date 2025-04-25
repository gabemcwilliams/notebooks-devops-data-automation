

# =============================================================================
#
#   Title: Monthly Reports - Strip emails of attachments and rename to email subject (client) + string
#
#   Author: Gabe McWilliams
#
#   Creation_Date: 2022/05/09
#
#   Version: 1.0
# 
# =============================================================================



import extract_msg
import os
import datetime



report_name = 'Remote Activity Report'

current_time = (datetime.datetime.utcnow().strftime('%Y - %m'))

source_dir = 'd:/data_sets/data_pool/emails_export_data/'

dest_dir = 'd:/data_sets/data_pool/emails_export_data/email_reports'



all_source_msg = [file_name for file_name in os.listdir(
    source_dir) if '.msg' in file_name]


for eml in all_source_msg:
    
    msg = extract_msg.Message(source_dir + eml)
 
    msg_sender = msg.sender
    msg_date = msg.date
    msg_subj = msg.subject
    msg_message = msg.body

    #print('Sender: {}'.format(msg_sender))
    #print('Sent On: {}'.format(msg_date))
    #print('Subject: {}'.format(msg_subj))
    #print('Body: {}'.format(msg_message))
    
    #print(msg.attachments)
    site_name = (msg_subj[37:]).replace('|','').replace('.','').replace("'",'')
    #print(site_name)
    


    attachments = msg.attachments
    
    for attachment in attachments:
        attachment_name = (f'{site_name} - {str(current_time)} - {report_name}[REDACTED]/.csv')
        print(attachment_name)
        params = {'customFilename':attachment_name}
        save_location = attachment.save(customPath=dest_dir,customFilename=attachment_name)      

#%%
