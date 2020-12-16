"""Init logger parameters"""
import configparser

import logging
from logging.config import dictConfig
from config_logger import LOG_CONFIG

from setup import CONFIG_FILE_NAME

DEFAULT_NAME_FLASK_LOGGER = 'werkzeug'


class LoggerClient():
    """Create logger object"""
    logger = logging.getLogger()

    def __init__(self):
        config_console = configparser.ConfigParser()
        config_console.read(CONFIG_FILE_NAME)
        self.logmode = config_console["LOG"]["log_mode"]

    def logger_settings(self):
        """create logger object and do some configuration with them"""
        LOG_CONFIG['root']['handlers'].append(self.logmode)
        flask_log = logging.getLogger(DEFAULT_NAME_FLASK_LOGGER)
        flask_log.setLevel(logging.ERROR)
        dictConfig(LOG_CONFIG)
        self.logger = logging.getLogger()

    def get_logger(self):
        """init logfer setting
        :return:logger object
        """
        self.logger_settings()
        return self.logger
