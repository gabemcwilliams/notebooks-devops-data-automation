import pandas as pd
import re
import requests
import json
import gql
import dotenv

"""
Microsoft Graph API - Sign-In Activity Export Script

Description:
------------
This script authenticates using client credentials and queries the Microsoft Graph API
for user sign-in activity logs from the `/auditLogs/signIns` endpoint.

Steps:
- Reads credentials from a `.env` file (TENANT_ID, CLIENT_ID, CLIENT_SECRET)
- Requests an OAuth2 access token
- Fetches up to 365 sign-in audit log entries (first page only)
- Converts the JSON response to a pandas DataFrame
- Exports the data to `.csv`

Limitations:
------------
- Does not paginate beyond the first 365 entries (pagination logic is commented out)
- Filtering by date or app ID is not currently active
- No retry/backoff logic for API rate limiting
- Only handles client credentials (no delegated/user token support)

Use this as a base template for building more advanced Graph integrations.
"""

# Load the environment variables from the .env file
secrets = dotenv.dotenv_values()

# Get the tenant ID and client ID from the environment variables
tenant_id = secrets['TENANT_ID']
client_id = secrets['CLIENT_ID']
client_secret = secrets['CLIENT_SECRET']

token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
token_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'https://graph.microsoft.com/.default'
}

token_response = requests.post(token_url, data=token_data)
json_data = json.loads(token_response.content)
access_token = json_data['access_token']

# existing_data = pd.DataFrame()
first_date = pd.to_datetime('2024-01-01')
last_date = pd.to_datetime('2025-01-01')

# start_time = f'{first_date}T00:00:00Z'
# end_time = f'{last_date}T23:59:59Z'
all_sign_ins = []
endpoint = f'https://graph.microsoft.com/v1.0/auditLogs/signIns?$top=365'
# endpoint = f'https://graph.microsoft.com/v1.0/auditLogs/signIns?$filter=createdDateTime ge {first_date} and createdDateTime lt {last_date} and appId eq \'{app_id}\''
headers = {
    'Authorization': 'Bearer ' + access_token,
    'Content-Type': 'application/json'
}
resp = requests.get(endpoint, headers=headers)

content = resp.content.decode('utf-8')
c_dict = json.loads(content)

for c in c_dict['value']:
    print(c)

df = pd.DataFrame(c_dict['value'])

df.head()

df.to_csv('.csv', index=False)
