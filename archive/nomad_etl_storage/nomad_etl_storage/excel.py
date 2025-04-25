"""

Title: Excel [LOAD]
Created by: Gabe McWilliams
Date: 2023/09/15

Description: Save DataFrame to Excel


"""

import os
import xlrd
import hvac
import traceback
import yaml
import logging


class LoadExcel:

    def __init__(self, df, config_dir=""):
        self.__df = df

        self.__config = self.read_config(yaml_dir=config_dir)

        self.__direction = self.__config["DIRECTION"]
        self.__vault = self.__config["VAULT"]
        self.__database = self.__config["DATABASE"]
        self.__schema = self.__config["SCHEMA"]
        self.__table = self.__config["TABLE"]
        self.__region = self.__config["REGION"]
        self.__logging = self.__config["LOGGING"]

        self.__title = '[{}] - {}.{}.{}'.format(
            self.__direction,
            self.__database,
            self.__schema,
            self.__table
        )

        self.__logger = self.create_logger()

        self.__secrets = self.read_secret(
            mount_point=self.__vault["MOUNT_POINT"],
            path=self.__vault["PATH"])

    @staticmethod
    def read_secret(mount_point, path):
        client = hvac.Client()
        resp = client.kv.v2.read_secret(mount_point=mount_point, path=f'/{path}')
        secret = resp['data']['data']

        return secret

    @staticmethod
    def read_config(yaml_dir):
        for root, dirs, files in os.walk(yaml_dir):
            for file in files:
                if file.startswith("postgres") & file.endswith(".yaml"):
                    with open(os.path.join(root, file), 'r') as f:
                        config = yaml.safe_load(f)

        return config

    def create_logger(self):
        logger = logging.getLogger(__name__)

        # create file handler which logs even debug messages
        fh = logging.FileHandler('postgres_{}_{}_{}_{}.log'.format(
            self.__direction,
            self.__database,
            self.__schema,
            self.__table
        ))
        fh.setLevel(logging.INFO)

        # create console handler with a higher log level
        ch = logging.StreamHandler(
        )
        ch.setLevel(logging.INFO)

        # TODO: add syslog server
        # # create syslog handler
        # syslog = logging.handlers.SysLogHandler(address='/dev/log')
        # syslog.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # syslog.setFormatter(formatter)

        # add the handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)
        # logger.addHandler(syslog)

        return logger

    def load_excel(self):
        self.__df.to_excel()











































