
# Create reports and save to CSV

## Pull year month to add to csv file title

# add current timestamp to filename for reference
current_time = (dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
year_month = (dt.datetime.utcnow().strftime('%Y - %m'))
year_month

## Import Client Service Files

def load_yaml(source_file=f'{dict_dir}.yaml'):
    with open(source_file, "r") as y:
        yaml_contents = yaml.load(y, Loader=SafeLoader)

        return yaml_contents

report_configs = load_yaml()

## Create report dataframes based on site and column filtering and export

def columns(report,yaml_configs=report_configs):

    try:
        yaml_columns = (yaml_configs['reports'][report]['standard_columns']) + (yaml_configs['reports'][report]['additional_columns'])
    except:
        yaml_columns = yaml_configs['reports'][report]['standard_columns']

    return yaml_columns

def site_names(report,yaml_configs=report_configs):

    yaml_sites = []

    for yaml_site in yaml_configs['site_names']:

        if report in yaml_site['reports']:

            yaml_sites.append(yaml_site['name'])

    return yaml_sites

def create_reports(report_list,source_df=df_devices,yaml_configs=report_configs):
    for report in report_list:

        df = source_df[columns(report)]
        df['reportCreationDate'] = current_time

        for yaml_site in site_names(report):

            df[df['siteName'] == yaml_site].to_csv(f'{export_folder}/reports/{yaml_site} - {year_month} - {yaml_configs["reports"][report]["report_name"]}.csv',index=False)

reports_list = ['ms_patching','software_management','sophos_av']

create_reports(reports_list)