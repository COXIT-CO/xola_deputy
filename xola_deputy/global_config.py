"""Configuration module for logging"""
import logging
from os import mkdir
import csv

LOG_DIR = "./logs/"
FILE_NAME_MAPPING = "mapping.csv"
DELIMITER = ","
CONFIG_FILE_NAME = 'Settings.ini'


try:
    mkdir(LOG_DIR)
except OSError:
    print("Logs directory exists.")
else:
    print("Successfully created the logs directory")


LOG_CONFIG = dict(
    version=1,
    formatters={
        'simple':
            {
                'format': '[%(asctime)s] [%(levelname)s] - : %(message)s.',
                'datefmt': '%H:%M:%S',
            },
        'detailed':
            {
                'format': '[%(asctime)s] [%(levelname)s] - Line: %(lineno)d '
                          '- %(name)s - : %(message)s.',
                'datefmt': '%d/%m/%y - %H:%M:%S',
            },
    },
    handlers={
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': logging.INFO,
        },
        'file':
            {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'detailed',
                'level': logging.INFO,
                'filename': LOG_DIR + 'logfile',
                'when': 'midnight',
        },
    },
    root={
        'handlers': ['file', ],
        'level': logging.INFO,
    },
)


def compare_mapping(compare_value, key):
    """
    :param compare_value: value we want to cmpare in mapping csv
    :return: mapping dict in all data
    """
    key_value = {
        'title': "Possible Area Nicknames in Production",
        'experience': "experience_id",
        'area': "Area"
    }
    heading = key_value.get(key, False)
    if heading is False:
        return False
    with open(FILE_NAME_MAPPING) as r_file:
        file_reader = csv.DictReader(r_file, delimiter=DELIMITER)
        for exp_dict in file_reader:
            if exp_dict[heading] == compare_value:
                return exp_dict
    return False
