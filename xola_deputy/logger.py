"""Init logger parameters"""
import configparser

import logging
from logging.config import dictConfig
from . import config


class LoggerClient():
    """Create logger object"""
    logger = logging.getLogger()

    def __init__(self):
        config_console = configparser.ConfigParser()
        config_console.read('Settings.ini')
        self.logmode = config_console["LOG"]["log_mode"]

    def logger_settings(self):
        """create logger object and do some configuration with them"""
        config.LOG_CONFIG['root']['handlers'].append(self.logmode)
        flask_log = logging.getLogger('werkzeug')
        flask_log.setLevel(logging.ERROR)
        dictConfig(config.LOG_CONFIG)
        self.logger = logging.getLogger()

    def get_logger(self):
        """init logfer setting
        :return:logger object
        """
        self.logger_settings()
        return self.logger
