# End of Life OS Report Generator

import os
import datetime as dt
import pandas as pd
import pdfkit
from jinja2 import Environment, FileSystemLoader

# Configuration
TEMPLATE_DIR = './templates'
EXPORT_DIR = './exports'
DATA_FILE = './data/devices.xlsx'
TEMPLATE_FILE = 'end_of_life_report.html'
WKHTMLTOPDF_PATH = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'

# Ensure export directory exists
os.makedirs(EXPORT_DIR, exist_ok=True)

# Load DataFrame
print("Loading device data...")
df_devices = pd.read_excel(DATA_FILE)

# Filter Data
ventura_mask = df_devices['siteName'] == 'Example CU'
end_of_life_mask = (df_devices['isEndOfSupport'] == 1) | (df_devices['isNearEndOfSupport'] == 1)
filtered_df = df_devices[ventura_mask & end_of_life_mask]

# Prepare HTML Table
df_columns = ['hostname', 'intIpAddress', 'operatingSystem', 'osEndOfSupportDate', 'lastLoggedInUser']
rename_map = {
    'hostname': 'hostname',
    'intIpAddress': 'ip address',
    'operatingSystem': 'operating system',
    'osEndOfSupportDate': 'last day of support',
    'lastLoggedInUser': 'last logged in user'
}

df_html = (filtered_df[df_columns]
           .rename(rename_map, axis=1)
           .fillna("Unknown")
           .to_html(index=False, justify='unset', border=0))

# Jinja Environment Setup
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template(TEMPLATE_FILE)

# Render HTML
print("Rendering HTML report...")
rendered_html = template.render(
    title='OS End of Life Report',
    site_name=filtered_df['siteName'].unique()[0],
    current_time=dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
    category_counts=filtered_df.value_counts('category').to_dict(),
    df=df_html
)

html_output_path = os.path.join(EXPORT_DIR, 'end_of_life_report.html')
with open(html_output_path, 'w', encoding='utf-8') as f:
    f.write(rendered_html)

# Generate PDF
print("Generating PDF report...")
pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
pdf_output_path = os.path.join(EXPORT_DIR, 'end_of_life_report.pdf')
pdfkit.from_file(html_output_path, pdf_output_path, configuration=pdfkit_config)

print(f"Reports generated successfully:\n- HTML: {html_output_path}\n- PDF: {pdf_output_path}")
