# Monthly Reports Automation

All reports automation will pull configurations from the postgres db "client_config.services"
All configurations will be stored in sharepoint
 - infrastructure > database folder pulled from the db as backup in case of data loss and local review

 - Automation is broken into job modules per report.
 - Jobs will be completely independent and redundant of normal pipelines as these are service deliverables
 - Root folders are named after initial producer sources

Folder Tree:

    monthly reports:
         api:
            report_job_name:
                src:
                    config:
                    jobs:
                    tasks:
                        extract:
                        load:
                        transform:

